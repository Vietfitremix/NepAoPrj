"""Spring supplies its catalog; shared scoring configuration stays in ai-service/data."""
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture
def backend_client(monkeypatch):
    monkeypatch.setenv("BACKEND_COMPAT_ONLY", "true")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        yield client
    get_settings.cache_clear()


@pytest.fixture
def payload():
    acc = {"code": "NON_LA", "name": "Nón lá", "type": "HEADWEAR"}
    return {"prompt": "Màu đỏ", "city": "Hanoi", "eventCode": "TET", "styleCode": "GEN_Z",
            "weather": {"temperature": 30, "condition": "CLEAR", "humidity": 80, "city": "Hanoi"},
            "culturalContext": {}, "referenceData": {
                "outfits": [{"outfit": {"code": code, "name": code}, "accessories": [acc]}
                            for code in ("AO_DAI", "AO_NGU_THAN", "NHAT_BINH")],
                "colors": [{"code": "RED", "name": "Đỏ", "hexCode": "#D32F2F"},
                           {"code": "WHITE", "name": "Trắng", "hexCode": "#FFFFFF"}],
                "styles": [{"code": "GEN_Z", "name": "Gen Z"}],
                "events": [{"code": "TET", "name": "Tết"}], "accessories": [acc]}}


def test_recommendations_use_backend_codes_without_native_data(backend_client, payload):
    response = backend_client.post("/ai/recommendations", json=payload)
    assert response.status_code == 200, response.text
    concepts = response.json()["concepts"]
    assert len(concepts) == 3
    assert len({c["outfitCode"] for c in concepts}) == 3
    assert all(c["colorCode"] == "RED" and c["styleCode"] == "GEN_Z" for c in concepts)
    assert all(0 <= c["matchScore"] <= 100 and c["reason"] for c in concepts)


def test_remix_applies_explicit_accessory_removal(backend_client, payload):
    payload["prompt"] = "Bỏ nón lá, đổi màu trắng"
    payload["currentLook"] = {"outfitCode": "AO_DAI", "colorCode": "RED", "styleCode": "GEN_Z",
                              "eventCode": "TET", "accessories": ["NON_LA"]}
    response = backend_client.post("/ai/remix", json=payload)
    assert response.status_code == 200, response.text
    changes = response.json()["changes"]
    assert changes["removeAccessories"] == ["NON_LA"]
    assert changes["colorCode"] == "WHITE"
    assert changes["addAccessories"] == []


def test_invalid_selection_rejected(backend_client, payload):
    payload["currentLook"] = {"outfitCode": "UNKNOWN", "colorCode": "RED", "styleCode": "GEN_Z",
                              "eventCode": "TET", "accessories": []}
    assert backend_client.post("/ai/remix", json=payload).status_code == 422


def test_request_catalogs_are_isolated(backend_client, payload):
    assert backend_client.post("/ai/recommendations", json=payload).status_code == 200
    payload["referenceData"]["styles"] = [{"code": "MINIMAL", "name": "Tối giản"}]
    assert backend_client.post("/ai/recommendations", json=payload).status_code == 422


def test_native_routes_report_missing_catalog(backend_client):
    assert backend_client.get("/ai/health").json()["catalogSource"] == "backend-request"
    assert backend_client.post("/ai/stylist", json={"text": "Tết"}).status_code == 503


def test_gemini_schema_has_no_unsupported_keys():
    from app.api.routers.backend import RemixOutput, gemini_schema
    text = str(gemini_schema(RemixOutput))
    assert "additionalProperties" not in text and "$ref" not in text and "$defs" not in text


def expanded_payload(payload):
    from app.catalog.sources import load_from_json
    from app.catalog.backend_bridge import EVENTS, STYLES, ACCESSORIES
    native = load_from_json(get_settings().data_dir)
    ref = payload['referenceData']
    accs = [{'code': next((k for k, v in ACCESSORIES.items() if v == a), a.upper()),
             'name': r['name'], 'type': r['slot']} for a, r in native.accessories.items()]
    ref['accessories'] = accs
    ref['outfits'] = [{'outfit': {'code': g.upper(), 'name': r['name']}, 'accessories': accs}
                      for g, r in native.garments.items()]
    ref['events'] = [{'code': code, 'name': native.occasions[value]['name']} for code, value in EVENTS.items()]
    ref['styles'] = [{'code': code, 'name': native.styles[value]['name']} for code, value in STYLES.items()]
    ref['colors'] += [{'code': 'BLUE', 'name': 'Xanh', 'hexCode': '#32679e'},
                      {'code': 'YELLOW', 'name': 'Vàng', 'hexCode': '#e2b44b'},
                      {'code': 'CREAM', 'name': 'Kem', 'hexCode': '#fff4db'},
                      {'code': 'BLACK', 'name': 'Đen', 'hexCode': '#24242a'}]
    payload.update(prompt='Gợi ý trang phục phù hợp', character='female', styleCode='TRADITIONAL')
    return payload


def test_event_changes_actual_outfits_colors_and_accessories(backend_client, payload):
    payload = expanded_payload(payload)
    signatures = []
    for event in ('TET', 'GRADUATION', 'FESTIVAL', 'PHOTOSHOOT', 'CULTURAL_EVENT'):
        payload['eventCode'] = event
        response = backend_client.post('/ai/recommendations', json=payload)
        assert response.status_code == 200, response.text
        concepts = response.json()['concepts']
        assert len(concepts) == 3
        signatures.append(tuple((c['outfitCode'], c['colorCode'], tuple(c['accessories'])) for c in concepts))
        if event == 'GRADUATION':
            assert all(c['outfitCode'] != 'NHAT_BINH' for c in concepts)
    assert len(set(signatures)) == 5


def test_explicit_male_character_overrides_ambiguous_quiz_labels(backend_client, payload):
    payload = expanded_payload(payload)
    payload.update(character='male', prompt='Người mặc là nam hay nữ? Nam')
    response = backend_client.post('/ai/recommendations', json=payload)
    assert response.status_code == 200, response.text
    assert all(c['outfitCode'] not in ('NHAT_BINH', 'AO_TU_THAN') for c in response.json()['concepts'])


def wardrobe_payload():
    return dict(outfitCode='AO_DAI', colorCode='RED', styleCode='TRADITIONAL', eventCode='TET', accessories=[],
                wardrobe=dict(character='female', selection=dict(shirt='jade', pants='ivory', shoes=None,
                              accessories={}, styles={'shirt': {'color': '#b52838'}})))


def test_culture_check_tracks_custom_colors_and_modern_accessories(backend_client):
    payload = wardrobe_payload()
    base = backend_client.post('/ai/wardrobe-score', json=payload).json()
    payload['wardrobe']['selection']['styles']['shirt']['color'] = '#eee9dc'
    recolored = backend_client.post('/ai/wardrobe-score', json=payload).json()
    assert base['breakdown'] != recolored['breakdown']
    assert '#eee9dc' in recolored['explanation']
    payload['wardrobe']['selection']['accessories'] = {'headphones': 'tai-nghe'}
    modern = backend_client.post('/ai/wardrobe-score', json=payload).json()
    assert modern['breakdown']['modernRemix'] < recolored['breakdown']['modernRemix']
    assert 'tai nghe' in modern['explanation']
    payload['wardrobe']['selection']['accessories'] = {}
    assert backend_client.post('/ai/wardrobe-score', json=payload).json() == recolored


def test_culture_check_invalid_color_and_missing_shirt(backend_client):
    payload = wardrobe_payload()
    payload['wardrobe']['selection']['styles']['shirt']['color'] = 'bad'
    assert backend_client.post('/ai/wardrobe-score', json=payload).status_code == 422
    payload['wardrobe']['selection']['styles'] = {}
    payload['wardrobe']['selection']['shirt'] = None
    result = backend_client.post('/ai/wardrobe-score', json=payload).json()
    assert result['score'] is None and result['level'] == 'INSUFFICIENT_DATA'

def test_wardrobe_review_returns_comment_tip_and_score_card(backend_client):
    payload = wardrobe_payload()
    payload['context'] = {'weather': 'mat_me', 'setting': 'ngoai_troi'}
    res = backend_client.post('/ai/wardrobe-review', json=payload)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body['verdict'] in ('hop', 'nen_chinh')
    current = body['current']
    assert current['comment'] and current['tip']
    assert 0 <= current['scoreCard']['total'] <= 100 and len(current['scoreCard']['criteria']) == 5
    payload['wardrobe']['selection']['shirt'] = None
    assert backend_client.post('/ai/wardrobe-review', json=payload).status_code == 422


import pytest


def score_of(client, character='female', shirt='jade', pants='ivory', shoes=None, event='TET', style='TRADITIONAL', acc=None):
    payload = dict(outfitCode='AO_DAI', colorCode='RED', styleCode=style, eventCode=event, accessories=[],
                   wardrobe=dict(character=character, selection=dict(shirt=shirt, pants=pants, shoes=shoes,
                                 accessories=acc or {}, styles={})))
    res = client.post('/ai/wardrobe-score', json=payload)
    assert res.status_code == 200, res.text
    return res.json()


@pytest.mark.parametrize('character,pants', [('female', 'shorts-denim'), ('female', 'skirt-short-navy'), ('male', 'shorts-khaki')])
def test_short_bottoms_with_traditional_shirt_are_scored_low(backend_client, character, pants):
    shirt = 'jade' if character == 'female' else 'teal'
    res = score_of(backend_client, character, shirt, pants)
    assert res['score'] <= 40, res
    assert res['level'] == 'HIGH_RISK' and any(w['severity'] == 'HIGH' for w in res['warnings'])


def test_missing_bottom_is_scored_low(backend_client):
    assert score_of(backend_client, pants=None)['score'] <= 40


def test_wide_or_straight_trousers_stay_suitable(backend_client):
    assert score_of(backend_client, pants='ivory')['score'] >= 70
    assert score_of(backend_client, 'male', 'teal', 'wide-charcoal')['score'] >= 70
    assert score_of(backend_client, 'male', 'teal', 'slim-black')['score'] < score_of(backend_client, 'male', 'teal', 'wide-charcoal')['score']


def test_sandals_are_penalised_by_occasion(backend_client):
    base = score_of(backend_client, shoes='guoc')['score']
    formal = score_of(backend_client, shoes='dep-crocs')
    street = score_of(backend_client, shoes='dep-crocs', event='PHOTOSHOOT', style='GEN_Z')
    assert formal['score'] <= 45 and formal['score'] < base
    assert street['score'] < base and street['score'] > formal['score']


def remix_payload(prompt, character='female', shirt='jade', pants='ivory'):
    import json
    from pathlib import Path
    cat = json.loads((Path(__file__).resolve().parents[2] / f'frontend/public/figure/{character}-layers/catalog.json').read_text(encoding='utf-8'))
    items = lambda key: [dict(id=i['id'], name=i['name'], slot=i.get('slot')) for i in cat[key]]       # noqa: E731
    return dict(outfitCode='AO_DAI', colorCode='RED', styleCode='TRADITIONAL', eventCode='TET', accessories=[], prompt=prompt,
                wardrobe=dict(character=character, selection=dict(shirt=shirt, pants=pants, shoes='hai-theu', accessories={}, styles={})),
                options=dict(outfits=items('outfits'), pants=items('pants'), shoes=items('shoes'), accessories=items('accessories')))


def test_remix_applies_a_suitable_request(backend_client):
    res = backend_client.post('/ai/wardrobe-remix', json=remix_payload('Đổi sang váy dài')).json()
    assert res['status'] == 'hop' and res['applied'] and res['selection']['pants'] == 'skirt-long-ivory'
    assert res['analysis'] and res['explanation'] and res['scoreAfter'] >= res['scoreBefore'] - 5


def test_remix_does_not_blindly_follow_an_unsuitable_request(backend_client):
    res = backend_client.post('/ai/wardrobe-remix', json=remix_payload('Mình muốn mặc váy ngắn')).json()
    assert res['scoreRequested'] <= 40                      # yêu cầu bị chấm thấp
    assert res['status'] in ('dieu_chinh', 'khong_hop')
    assert res['selection']['pants'] != 'skirt-short-navy'  # không áp dụng nguyên văn
    if res['status'] == 'dieu_chinh':
        assert res['scoreAfter'] > res['scoreRequested']
    assert res['analysis'] and res['explanation']


def test_remix_asks_when_request_is_unclear(backend_client):
    res = backend_client.post('/ai/wardrobe-remix', json=remix_payload('làm đẹp hơn đi')).json()
    assert res['status'] == 'chua_ro' and not res['applied']


def test_review_accepts_modern_items_missing_from_catalog(backend_client):
    payload = wardrobe_payload()
    payload['wardrobe']['selection'].update(shoes='dep-crocs', accessories={'headphones': 'tai-nghe', 'headwear': 'mu-luoi-trai'})
    payload['names'] = {'dep-crocs': 'Dép Crocs', 'tai-nghe': 'Tai nghe', 'mu-luoi-trai': 'Mũ lưỡi trai'}
    res = backend_client.post('/ai/wardrobe-review', json=payload)
    assert res.status_code == 200, res.text
    assert res.json()['verdict'] == 'chua_hop' and res.json()['current']['scoreCard']['total'] <= 45


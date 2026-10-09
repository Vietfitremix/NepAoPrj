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

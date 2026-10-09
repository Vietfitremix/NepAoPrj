"""Regressions for detailed assessment, unknown evidence and shared route scoring."""
from copy import deepcopy

import pytest

from app.engine.color import color_metrics, score_colors
from app.engine.matcher import score_outfit
from app.engine.rules import evaluate, matches
from app.models import Colors, Intent, OutfitState


def outfit(**kw):
    return OutfitState(garment='ao_dai', gender='nu', occasion='tet', style='truyen_thong',
                       colors=Colors(main='do_do', bottom='trang_nga'), bottom='quan_dai_suong',
                       shoes='giay_bet', **kw)


def test_missing_context_does_not_become_true_under_negation():
    state = outfit()
    condition = {'not': {'weather': ['mua']}}
    assert not matches(condition, state)
    assert not matches({'all': [{'garment': ['ao_dai']}, condition]}, state, Intent())
    assert matches(condition, state, Intent(weather='mat_me'))


def test_missing_bottom_and_unknown_bottom_are_different():
    state = outfit()
    state.bottom = None
    assert not matches({'not': {'bottom': ['quan_ngan']}}, state)
    state.bottom = 'khong'
    assert matches({'bottom': ['khong']}, state)


def test_specific_rule_contributes_only_once_per_issue(catalog):
    state = outfit(accessories=['guoc'])
    hits = evaluate(state, catalog.rules, Intent(weather='mua', setting='ngoai_troi'))
    assert 'R61' in {e.id for e in hits}
    assert 'R20' not in {e.id for e in hits}
    state.bottom = 'quan_ngan'
    state.style = 'duong_pho'
    hits = evaluate(state, catalog.rules)
    assert 'R40' in {e.id for e in hits} and 'R50' not in {e.id for e in hits}


def test_rule_points_change_only_the_corresponding_criterion(catalog):
    from app.engine.scoring import score_card
    state = outfit()
    local = deepcopy(catalog)
    local.rules = [dict(id='detail', criterion='cau_truc', level='consider', points=-7,
                        when={'garment':['ao_dai']}, reason='Fit detail', suggestion={'text':'Adjust'})]
    base = score_card(state, [], 75, local)
    changed = score_card(state, evaluate(state, local.rules), 75, local)
    assert changed.criteria[0].score == base.criteria[0].score - 7
    assert changed.criteria[1:] == base.criteria[1:]


def test_exact_rgb_changes_color_rules_and_absent_bottom_has_no_metrics(catalog):
    state = outfit(colorHex={'main':'#ff0000','bottom':'#ff0000'})
    color = score_colors(state, catalog)
    metrics = color_metrics(state, catalog, color.score)
    ids = {e.id for e in evaluate(state, catalog.rules, metrics=metrics)}
    assert {'R74','R76'} <= ids
    state.colorHex['bottom'] = '#ffffff'
    metrics = color_metrics(state, catalog, score_colors(state, catalog).score)
    ids = {e.id for e in evaluate(state, catalog.rules, metrics=metrics)}
    assert {'R75','R77'} <= ids and not {'R74','R76'} & ids
    state.bottom = 'khong'
    assert color_metrics(state, catalog, color.score) == {}


@pytest.mark.parametrize('accessories,ctx,expected', [
    (['tai_nghe'], Intent(), set()),
    (['tai_nghe'], Intent(role='be_trap'), set()),
    (['ba_lo','tui','quat_giay'], Intent(role='be_trap'), {'R66','R67'}),
    (['bong_tai','vong_tay','kieng_bac'], Intent(), {'R82'}),
    (['moc_khoa_bong'], Intent(), {'R85'}),
    (['moc_khoa_bong','tui'], Intent(), set()),
])
def test_accessory_advice_uses_selected_evidence(catalog, accessories, ctx, expected):
    state = outfit(accessories=accessories)
    ids = {e.id for e in evaluate(state, catalog.rules, ctx)} & {'R66','R67','R82','R85'}
    assert ids == expected


def test_photo_role_does_not_trigger_old_nhat_binh_street_warning(catalog):
    state = outfit()
    state.garment = 'nhat_binh'
    state.occasion = 'dao_pho'
    assert 'R15' not in {e.id for e in evaluate(state, catalog.rules)}
    ids = {e.id for e in evaluate(state, catalog.rules, Intent(role='chup_anh'))}
    assert 'R71' in ids and 'R15' not in ids


def test_all_white_is_styling_advice_not_a_claim_of_mourning(catalog):
    state = outfit(accessories=['khan_van'])
    state.colors.main = 'trang_nga'
    hits = evaluate(state, catalog.rules)
    rule = next(e for e in hits if e.id == 'R12')
    assert rule.level == 'consider'
    assert 'Không thể kết luận tang phục' in rule.suggestion.text


def test_color_patch_clears_old_exact_rgb():
    from app.engine.outfit_check import apply_patch
    state = outfit(colorHex={'main':'#ff0000','bottom':'#ffffff'})
    changed = apply_patch(state, {'colors': {'main':'xanh_cham'}})
    assert changed.colorHex == {'bottom':'#ffffff'}
    assert state.colorHex['main'] == '#ff0000'


@pytest.mark.parametrize('character,shirt,pants', [('male','teal','wide-charcoal'),('female','jade','ivory')])
def test_quick_review_and_remix_share_exact_rgb_context_and_accessories(client, character, shirt, pants):
    payload = dict(outfitCode='AO_DAI',colorCode='RED',styleCode='TRADITIONAL',eventCode='CULTURAL_EVENT',accessories=[],
                   context={'weather':'mua','setting':'ngoai_troi','role':'be_trap','timeOfDay':'buoi_toi'},
                   wardrobe={'character':character,'selection':{'shirt':shirt,'pants':pants,'shoes':'guoc',
                             'accessories':{'headphones':'tai-nghe','backpack':'ba-lo','bag':'tui-coi','fan':'quat-giay'},
                             'styles':{'shirt':{'color':'#ff0000'},'pants':{'color':'#ffffff'}}}})
    quick = client.post('/ai/wardrobe-score',json=payload)
    review = client.post('/ai/wardrobe-review',json=payload)
    assert quick.status_code == review.status_code == 200, review.text
    q, r = quick.json(), review.json()['current']
    assert q['score'] == r['scoreCard']['total']
    assert {e['ruleId'] for e in q['checks']} == {e['id'] for e in r['evaluations']}
    assert {'R61','R65','R66','R67'} <= {e['ruleId'] for e in q['checks']}
    assert q['assessment']['contextUsed'] == payload['context']
    assert not q['assessment']['missingContext']
    from app.api.routers.wardrobe_remix import RemixBody, _score
    # The remix scorer shares the exact same deterministic engine, without calling Gemini.
    from types import SimpleNamespace
    from app.catalog import load_from_json
    from app.core.config import get_settings
    svc = SimpleNamespace(catalog=load_from_json(get_settings().data_dir))
    remix = RemixBody(**payload,prompt='Giữ bộ hiện tại',options={'outfits':[],'pants':[],'shoes':[],'accessories':[]})
    assert _score(remix, remix.wardrobe.selection, svc)[1].total == q['score']
    assert 'tai_nghe' not in svc.catalog.accessories  # request-local additions stay isolated


def test_quick_score_reports_unknown_context_without_penalty(client):
    payload = dict(outfitCode='AO_DAI',colorCode='RED',styleCode='TRADITIONAL',eventCode='TET',accessories=[],
                   wardrobe={'character':'female','selection':{'shirt':'jade','pants':'ivory','shoes':'hai-theu'}})
    result = client.post('/ai/wardrobe-score',json=payload).json()
    assert result['assessment']['ruleCount'] == 80
    assert set(result['assessment']['missingContext']) == {'weather','setting','timeOfDay','role'}
    assert not result['assessment']['contextUsed']
    assert all(not e['ruleId'] in {'R58','R60','R61','R63','R64','R66','R67','R80'} for e in result['checks'])

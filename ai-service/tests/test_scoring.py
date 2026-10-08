"""Thang chấm 5 tiêu chí (engine/scoring.py + data/scoring.json)."""
from app.engine import score_outfit
from app.models import Colors, Intent, OutfitState

CRITERIA = {"cau_truc", "dac_trung", "phu_kien", "boi_canh", "cach_tan"}


def outfit(**kw):
    base = dict(garment="ao_ngu_than", gender="nam", occasion="dao_pho", style="truyen_thong",
                colors=Colors(main="xanh_lam", bottom="den_tuyen"))
    return OutfitState(**{**base, **kw})


def test_config_weights_and_rule_tags(catalog):
    crit = catalog.scoring["criteria"]
    assert {c["id"] for c in crit} == CRITERIA
    assert sum(c["weight"] for c in crit) == 100
    assert all(r.get("criterion") in CRITERIA for r in catalog.rules)


def test_card_shape_and_range(catalog):
    _, _, _, card = score_outfit(outfit(), catalog)
    assert [c.id for c in card.criteria] and {c.id for c in card.criteria} == CRITERIA
    assert 0 <= card.total <= 100 and all(0 <= c.score <= 100 for c in card.criteria)
    assert card.band in {"chuan_bo", "hop_dip", "can_chinh"}


def test_risk_caps_total(catalog):
    o = OutfitState(garment="ao_dai", gender="nu", occasion="tet", style="toi_gian",
                    colors=Colors(main="trang_nga", bottom="trang_nga", accent="trang_nga"), accessories=["khan_van"])
    _, evals, _, card = score_outfit(o, catalog)
    assert any(e.level == "risk" for e in evals)
    assert card.total <= catalog.scoring["riskCap"] and card.band == "can_chinh"


def test_remix_depends_on_chosen_style(catalog):
    remix = lambda style: next(c.score for c in score_outfit(outfit(style=style, accessories=["sneaker"]), catalog)[3]
                               .criteria if c.id == "cach_tan")
    assert remix("duong_pho") > remix("truyen_thong")


def test_rules_move_their_own_criterion(catalog):
    guest = Intent(role="khach")
    o = outfit(garment="nhat_binh", gender="nu", occasion="dam_cuoi", colors=Colors(main="do_son", bottom="den_tuyen"))
    _, _, _, card = score_outfit(o, catalog, guest)
    ctx = next(c for c in card.criteria if c.id == "boi_canh")
    assert {"R25", "R26"} <= set(ctx.ruleIds) and ctx.score < 75


def test_full_set_scores_higher(catalog):
    bare = OutfitState(garment="ao_tu_than", gender="nu", occasion="le_hoi_chua", style="truyen_thong",
                       colors=Colors(main="nau_dat", bottom="den_tuyen"))
    full = bare.model_copy(update={"accessories": ["non_quai_thao", "khan_mo_qua", "kieng_bac"]})
    assert score_outfit(full, catalog)[3].total > score_outfit(bare, catalog)[3].total


def test_api_returns_score_card(client):
    state = outfit().model_dump()
    r = client.post("/ai/evaluate", json={"state": state}).json()
    assert r["scoreCard"]["total"] >= 0 and len(r["scoreCard"]["criteria"]) == 5

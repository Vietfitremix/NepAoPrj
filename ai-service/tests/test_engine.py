from app.engine import evaluate, match_outfits, score_pair, suggest_alternatives
from app.engine.color import hex_to_oklch
from app.models import Colors, Intent, OutfitState


def outfit(**kw):
    base = dict(garment="ao_ngu_than", gender="nu", occasion="ky_yeu", style="pastel",
                colors=Colors(main="hong_dao", bottom="trang_nga"), accessories=[])
    base.update(kw)
    return OutfitState(**base)


def ids(evals):
    return {e.id: e.level for e in evals}


# ---------- 4 luật mẫu trong doc gốc ----------
def test_tu_than_with_non_quai_thao_is_ok(catalog):
    o = outfit(garment="ao_tu_than", occasion="le_hoi_chua", accessories=["non_quai_thao"])
    assert ids(evaluate(o, catalog.rules)).get("R01") == "ok"


def test_ngu_than_with_sneaker_is_consider(catalog):
    o = outfit(accessories=["sneaker"])
    assert ids(evaluate(o, catalog.rules)).get("R07") == "consider"


def test_all_white_with_khan_at_wedding_is_styling_advice(catalog):
    o = outfit(occasion="dam_cuoi", colors=Colors(main="trang_nga", bottom="trang_nga", accent="trang_tinh"),
               accessories=["khan_van"])
    evals = evaluate(o, catalog.rules)
    assert ids(evals).get("R12") == "consider"
    assert not any(e.level == "risk" for e in evals)


def test_white_outfit_with_colored_khan_is_not_risk(catalog):
    o = outfit(occasion="dam_cuoi", colors=Colors(main="trang_nga", bottom="trang_nga", accent="do_son"),
               accessories=["khan_van"])
    assert "R12" not in ids(evaluate(o, catalog.rules))


def test_nhat_binh_dao_pho_is_consider(catalog):
    o = outfit(garment="nhat_binh", occasion="dao_pho", style="truyen_thong")
    assert ids(evaluate(o, catalog.rules, Intent(role="khach"))).get("R15") == "consider"
    assert "R15" not in ids(evaluate(o, catalog.rules, Intent(role="chup_anh")))


# ---------- chấm màu ----------
def test_oklch_white_and_black():
    assert hex_to_oklch("#FFFFFF")[0] > 0.99
    assert hex_to_oklch("#000000")[0] < 0.01


def test_color_score_range_and_contrast():
    high = score_pair("#B3261E", "#F5F0E1")              # đỏ son + trắng ngà: tương phản sáng tối tốt
    flat = score_pair("#F5F0E1", "#FFFFFF")              # trắng + trắng: phẳng
    assert 0 <= flat.score <= 100 and 0 <= high.score <= 100
    assert high.score > flat.score
    assert "low_contrast" in flat.noteKey


# ---------- bộ ghép trang phục ----------
def test_match_returns_three_valid_outfits(catalog):
    res = match_outfits(Intent(occasion="ky_yeu", style="pastel", gender="nu", mustHave=["sneaker"]), catalog)
    assert len(res) == 3
    for o in res:
        assert catalog.garments[o.garment]["hasSvg"]
        assert "sneaker" in o.accessories
        slots = [catalog.accessories[a]["slot"] for a in o.accessories]
        assert len(slots) == len(set(slots))


def test_match_respects_gender_and_avoid(catalog):
    res = match_outfits(Intent(occasion="dam_cuoi", gender="nam", avoidAccessories=["khan_van"]), catalog)
    assert res and all(o.gender == "nam" and "khan_van" not in o.accessories for o in res)
    assert all("nam" in catalog.garments[o.garment]["genders"] for o in res)


def test_alternatives_fix_risk(catalog):
    o = outfit(occasion="dam_cuoi", colors=Colors(main="trang_nga", bottom="trang_nga", accent="trang_tinh"),
               accessories=["khan_van"])
    alts = suggest_alternatives(o, catalog)
    assert alts
    assert all("R12" not in ids(evaluate(a, catalog.rules)) for a, _ in alts[:1])

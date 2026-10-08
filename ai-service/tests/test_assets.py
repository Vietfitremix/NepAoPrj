"""Mọi món trong catalog đều có đủ hình SVG ở 4 hướng nhìn (trước, trái, phải, sau)."""
from pathlib import Path

from app.ai.fallback import parse_by_keywords
from app.engine.rules import evaluate
from app.models.outfit import OutfitState

FIG = Path(__file__).resolve().parents[2] / "frontend/src/assets/figure"
VIEWS = ["", "_trai", "_phai", "_sau"]


def test_accessories_have_4_views(catalog):
    missing = []
    for a in catalog.accessories.values():
        names = [f"{a['id']}_{g}" for g in a["genders"]] if a.get("byGender") else [a["id"]]
        missing += [f"{n}{v}" for n in names for v in VIEWS if not (FIG / f"accessory/{n}{v}.svg").exists()]
    assert not missing, missing


def test_garments_have_4_views(catalog):
    missing = [f"{g['id']}_{s}{v}" for g in catalog.garments.values() if g.get("hasSvg")
               for s in g["genders"] for v in VIEWS if not (FIG / f"garment/{g['id']}_{s}{v}.svg").exists()]
    assert not missing, missing


def test_hat_and_headwrap_can_be_worn_together(catalog):
    slots = {catalog.accessories[a]["slot"] for a in ("non_quai_thao", "khan_mo_qua")}
    assert len(slots) == 2


def test_tu_than_with_quan_ho_accessories_is_ok(catalog):
    o = OutfitState(garment="ao_tu_than", gender="nu", occasion="le_hoi_chua", style="truyen_thong",
                    colors={"main": "nau_dat", "bottom": "den_tuyen"}, accessories=["non_quai_thao", "khan_mo_qua"])
    ids = {r.id: r.level for r in evaluate(o, catalog.rules)}
    assert ids.get("R34") == "ok" and ids.get("R01") == "ok"


def test_new_accessory_keywords(catalog):
    it = parse_by_keywords("đám cưới, nam, mặc ngũ thân đội khăn xếp, đi hài thêu nhưng không cầm quạt giấy", catalog)
    assert "khan_xep" in it.mustHave and "hai_theu" in it.mustHave
    assert "quat_giay" in it.avoidAccessories


def test_placement_patterns_have_motif_and_garments(catalog):
    for p in catalog.patterns.values():
        if p.get("kind") == "placement":
            assert (FIG / f"motif/{p['id']}.svg").exists(), p["id"]
            assert p.get("garments"), p["id"]


def test_placement_pattern_rejected_on_wrong_garment(catalog):
    import pytest

    from app.engine.outfit_check import InvalidOutfit, validate_outfit
    o = OutfitState(garment="ao_tu_than", gender="nu", occasion="tet", style="truyen_thong",
                    colors={"main": "nau_dat", "bottom": "den_tuyen"}, pattern="phuong_hoang")
    with pytest.raises(InvalidOutfit, match="phuong_hoang"):
        validate_outfit(o, catalog)


def test_guest_with_phoenix_is_consider(catalog):
    from app.models.intent import Intent
    o = OutfitState(garment="ao_dai", gender="nu", occasion="dam_cuoi", style="truyen_thong",
                    colors={"main": "hong_dao", "bottom": "trang_nga"}, pattern="phuong_hoang")
    ids = {r.id: r.level for r in evaluate(o, catalog.rules, Intent(role="khach", occasion="dam_cuoi"))}
    assert ids.get("R36") == "consider"


def test_enough_placement_patterns_per_gender(catalog):
    place = [p for p in catalog.patterns.values() if p.get("kind") == "placement"]
    for g in ("nu", "nam"):
        assert len([p for p in place if g in p.get("genders", ["nu", "nam"])]) >= 10, g


def test_gender_rule_accepts_list(catalog):
    o = OutfitState(garment="ao_ngu_than", gender="nam", occasion="tet", style="truyen_thong",
                    colors={"main": "xanh_lam", "bottom": "trang_nga"}, pattern="rong_may", accessories=["khan_xep"])
    ids = {r.id: r.level for r in evaluate(o, catalog.rules)}
    assert ids.get("R30") == "ok" and ids.get("R38") == "ok"


def test_checklist_covers_catalog(catalog):
    """Checklist 'soi và mặc theo': mọi áo, phụ kiện đều có gợi ý món tương đương ngoài đời."""
    ck = catalog.checklist
    assert set(catalog.garments) <= set(ck["garments"]), set(catalog.garments) - set(ck["garments"])
    assert set(catalog.accessories) <= set(ck["accessories"]), set(catalog.accessories) - set(ck["accessories"])
    assert {"quan", "vay"} <= set(ck["bottoms"])
    assert "checklist" in catalog.public_view()

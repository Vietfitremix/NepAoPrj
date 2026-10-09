"""Validate the existing raster wardrobes without restoring retired SVG assets."""
from pathlib import Path
import json

from app.ai.fallback import parse_by_keywords
from app.engine.rules import evaluate
from app.models.outfit import OutfitState

FIG = Path(__file__).resolve().parents[2] / "frontend/public/figure"
VIEWS = ["front", "left", "right", "back"]
CHARACTERS = {"nu": "female", "nam": "male"}


def wardrobe(gender):
    root = FIG / f"{CHARACTERS[gender]}-layers"
    return root, json.loads((root / "catalog.json").read_text(encoding="utf-8"))


def assert_views(root, item):
    folder = Path(item["file"]).parent
    assert (root / item["thumbnail"]).is_file(), item["id"]
    for view in VIEWS:
        assert (root / folder / f"{view}.png").is_file(), (item["id"], view)


def test_accessories_have_4_views(catalog):
    ids = {"tui": ["tui-coi"], "quat_giay": ["quat-giay"],
           "trang_suc": ["bong-tai", "vong-tay"], "sneaker": ["sneakers"]}
    for a in catalog.accessories.values():
        for gender in a["genders"]:
            root, data = wardrobe(gender)
            items = {item["id"]: item for item in data["accessories"] + data["shoes"]}
            for name in ids.get(a["id"], [a["id"].replace("_", "-")]):
                assert name in items, (gender, name)
                assert_views(root, items[name])


def test_garments_have_4_views(catalog):
    ids = {"ao_tu_than": "tu-than", "ao_ngu_than": "ngu-than", "nhat_binh": "nhat-binh", "ao_ba_ba": "ba-ba"}
    for garment in catalog.wearable_garments.values():
        for gender in garment["genders"]:
            root, data = wardrobe(gender)
            for view in VIEWS:
                assert (root / "body" / f"{view}.png").is_file()
            name = ("jade" if gender == "nu" else "navy") if garment["id"] == "ao_dai" else ids[garment["id"]]
            item = next(item for item in data["outfits"] if item["id"] == name)
            assert_views(root, item)


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


def test_current_pattern_assets_and_native_pattern_constraints(catalog):
    patterns = json.loads((FIG / "patterns/catalog.json").read_text(encoding="utf-8"))
    assert patterns
    for pattern in patterns:
        assert (FIG / pattern["file"]).is_file(), pattern["id"]
        assert (FIG / pattern["thumbnail"]).is_file(), pattern["id"]
    for p in catalog.patterns.values():
        if p.get("kind") == "placement":
            assert p.get("garments"), p["id"]
            assert set(p["garments"]) <= set(catalog.garments), p["id"]


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

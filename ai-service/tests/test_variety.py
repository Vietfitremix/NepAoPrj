"""Gợi ý phải đa dạng: nhiều bộ quần/giày/phụ kiện cho mỗi kiểu áo, danh sách ngắn không trùng lặp."""
from types import SimpleNamespace

from app.engine.variety import accessory_sets, bottom_and_shoes, diverse_shortlist

ACC = {
    "QUAN_LUA": {"type": "BOTTOM", "slot": "BOTTOM"}, "QUAN_DAI_DEN": {"type": "BOTTOM", "slot": "BOTTOM"},
    "QUAN_ONG_RONG": {"type": "BOTTOM", "slot": "BOTTOM"}, "VAY_DUP": {"type": "BOTTOM", "slot": "BOTTOM"},
    "VAY_XEP_LY": {"type": "BOTTOM", "slot": "BOTTOM"},
    "GUOC": {"type": "FOOTWEAR", "slot": "feet"}, "HAI_THEU": {"type": "FOOTWEAR", "slot": "feet"},
    "WHITE_SNEAKERS": {"type": "FOOTWEAR", "slot": "feet"},
    "NON_LA": {"type": "HEADWEAR", "slot": "head"}, "KHAN_VAN": {"type": "HEADWEAR", "slot": "hair", "genders": ["nu", "nam"]},
    "KIENG_BAC": {"type": "JEWELRY", "slot": "neck", "genders": ["nu"]},
    "MINIMAL_BAG": {"type": "BAG", "slot": "hand"}, "FAN": {"type": "HANDHELD", "slot": "hand2"},
}
CAT = SimpleNamespace(accessories=ACC)
ROW = {"allowedAccessories": list(ACC)}


def test_each_set_has_bottom_and_footwear_and_sets_differ():
    sets = accessory_sets(CAT, ROW, ["NON_LA", "KIENG_BAC"], [], set(), "nu")
    assert len(sets) == 3 and len({tuple(s) for s in sets}) == 3
    for s in sets:
        kinds = bottom_and_shoes(s)
        assert kinds[0] != "khong" and kinds[1] != "khong", s
    assert len({bottom_and_shoes(s) for s in sets}) >= 2         # quần/giày không giống hệt nhau ở cả ba bộ


def test_first_set_keeps_occasion_defaults():
    first = accessory_sets(CAT, ROW, ["NON_LA", "KIENG_BAC"], [], set(), "nu")[0]
    assert "NON_LA" in first and "KIENG_BAC" in first


def test_gender_and_unsuitable_items_are_filtered():
    male = [item for s in accessory_sets(CAT, ROW, [], [], set(), "nam") for item in s]
    assert "KIENG_BAC" not in male and "QUAN_DAI_DEN" not in male and "VAY_DUP" not in male
    assert "VAY_XEP_LY" not in [item for s in accessory_sets(CAT, ROW, [], [], set(), "nu") for item in s]


def test_requested_accessory_is_in_every_set_and_avoided_one_never():
    sets = accessory_sets(CAT, ROW, ["NON_LA"], ["FAN"], {"WHITE_SNEAKERS", "NON_LA"}, "nu")
    assert all("FAN" in s for s in sets)
    assert all("WHITE_SNEAKERS" not in s and "NON_LA" not in s for s in sets)


def _outfit(i, garment, color, accessories):
    return SimpleNamespace(outfitId=f"c{i}", state=SimpleNamespace(
        garment=garment, colors=SimpleNamespace(main=color), accessories=accessories))


def test_shortlist_does_not_repeat_garment_or_colour_when_alternatives_exist():
    candidates = [_outfit(1, "A", "RED", ["QUAN_LUA", "GUOC"]), _outfit(2, "A", "RED", ["QUAN_LUA", "GUOC", "NON_LA"]),
                  _outfit(3, "A", "BLUE", ["QUAN_LUA", "GUOC"]), _outfit(4, "B", "RED", ["QUAN_LUA", "GUOC"]),
                  _outfit(5, "C", "BLUE", ["QUAN_ONG_RONG", "HAI_THEU"])]
    ranks = {"c1": 90, "c2": 89, "c3": 88, "c4": 80, "c5": 78}
    top = diverse_shortlist(candidates, ranks, n=3)
    assert sorted(c.state.garment for c in top) == ["A", "B", "C"]
    assert top[0].outfitId == "c1"                                 # bộ tốt nhất vẫn đứng đầu


def test_colour_locked_does_not_penalise_same_colour():
    candidates = [_outfit(1, "A", "RED", ["X"]), _outfit(2, "B", "RED", ["Y"]), _outfit(3, "C", "BLUE", ["Z"])]
    ranks = {"c1": 90, "c2": 85, "c3": 70}
    assert [c.outfitId for c in diverse_shortlist(candidates, ranks, n=2, colour_locked=True)] == ["c1", "c2"]
    assert [c.outfitId for c in diverse_shortlist(candidates, ranks, n=2, colour_locked=False)] == ["c1", "c2"]

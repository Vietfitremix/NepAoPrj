"""Đa dạng hoá gợi ý: nhiều bộ phối quần/giày/phụ kiện cho mỗi kiểu áo, và chọn danh sách ngắn không trùng lặp.

Trước đây mỗi kiểu áo chỉ có đúng một bộ phụ kiện mặc định theo dịp, nên 3 gợi ý luôn giống nhau ở quần, giày
và phụ kiện. Ở đây mỗi kiểu áo được ghép thành vài bộ khác nhau (đổi quần/váy, giày dép, nón/khăn, thêm trang sức
hoặc túi/quạt) rồi chấm điểm như thường: luật văn hoá vẫn quyết định bộ nào hợp, không có bộ nào được ưu ái.
"""
# Mã món trong danh mục tham chiếu của Spring -> loại quần/váy, giày dép mà bộ luật R40–R50 hiểu.
BOTTOM_CODE_KIND = {"QUAN_LUA": "quan_dai_suong", "QUAN_ONG_RONG": "quan_ong_rong", "QUAN_DAI_DEN": "quan_dai",
                    "QUAN_DAI_XANH": "quan_dai", "VAY_DUP": "vay_dai", "VAY_XEP_LY": "vay_ngan"}
SHOE_CODE_KIND = {"GUOC": "giay_truyen_thong", "HAI_THEU": "giay_truyen_thong", "GIAY_BUP_BE": "giay_bet",
                  "WHITE_SNEAKERS": "giay_the_thao"}
# Giới tính phù hợp của các món chỉ có ở một bên trong tủ đồ (khớp ảnh trong tủ đồ nam/nữ).
CODE_GENDERS = {"QUAN_ONG_RONG": ["nam"], "QUAN_DAI_XANH": ["nam"], "QUAN_DAI_DEN": ["nu"], "VAY_DUP": ["nu"], "VAY_XEP_LY": ["nu"]}
# Không đưa vào gợi ý: hình xem trước của món này là váy ngắn, bộ luật xếp vào nhóm "không hợp" với áo truyền thống.
NOT_RECOMMENDED = {"VAY_XEP_LY"}
GROUP_ORDER = ("BOTTOM", "FOOTWEAR", "HEADWEAR")
EXTRA_GROUPS = ("JEWELRY", "BAG", "HANDHELD")


def _group(cat, code):
    return cat.accessories.get(code, {}).get("type") or "OTHER"


def _genders(cat, code):
    return CODE_GENDERS.get(code) or cat.accessories.get(code, {}).get("genders", ["nu", "nam"])


def accessory_sets(cat, row, defaults, must, avoid, gender, n=3):
    """Trả về tối đa n bộ phụ kiện khác nhau cho một kiểu áo (bộ đầu là bộ mặc định theo dịp)."""
    allowed = [a for a in row["allowedAccessories"]
               if a in cat.accessories and a not in avoid and a not in NOT_RECOMMENDED and gender in _genders(cat, a)]
    must = [a for a in dict.fromkeys(must) if a in allowed]
    groups: dict[str, list[str]] = {}
    for a in allowed:
        groups.setdefault(_group(cat, a), []).append(a)
    for items in groups.values():                           # món mặc định theo dịp đứng trước, quần lụa suông là mốc truyền thống
        items.sort(key=lambda a: (a not in defaults, a != "QUAN_LUA"))
    sets: list[list[str]] = []
    for i in range(n):
        chosen = list(must)
        taken = {_group(cat, a) for a in chosen}
        slots = {cat.accessories[a].get("slot") for a in chosen}
        if i == 0:
            for a in defaults:
                slot = cat.accessories.get(a, {}).get("slot")
                if a in allowed and a not in chosen and slot not in slots:
                    chosen.append(a)
                    slots.add(slot)
            taken |= {_group(cat, a) for a in chosen}
        for group in GROUP_ORDER:
            options = groups.get(group)
            if options and group not in taken:
                chosen.append(options[i % len(options)])
                taken.add(group)
        if i > 0:                                           # mỗi bộ thêm một món phụ khác nhóm với các bộ trước
            for step in range(len(EXTRA_GROUPS)):
                group = EXTRA_GROUPS[(i + step - 1) % len(EXTRA_GROUPS)]
                options = groups.get(group)
                if options and group not in taken:
                    chosen.append(options[(i // len(EXTRA_GROUPS)) % len(options)])
                    break
        chosen = list(dict.fromkeys(chosen))[:10]
        if chosen not in sets:
            sets.append(chosen)
    return sets


def bottom_and_shoes(accessories):
    """Loại quần/váy và giày dép của bộ phối; thiếu món thì ghi 'khong' để luật nhắc người dùng."""
    bottom = next((BOTTOM_CODE_KIND[a] for a in accessories if a in BOTTOM_CODE_KIND), "khong")
    shoes = next((SHOE_CODE_KIND[a] for a in accessories if a in SHOE_CODE_KIND), "khong")
    return bottom, shoes


def _first(accessories, table):
    return next((a for a in accessories if a in table), None)


def _overlap(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def diverse_shortlist(candidates, ranks, n=9, colour_locked=False):
    """Chọn n ứng viên theo điểm nhưng phạt bộ trùng kiểu áo, trùng màu chính và trùng phụ kiện với bộ đã chọn.
    colour_locked: người dùng đã chỉ định màu thì không phạt việc trùng màu."""
    pool, chosen = list(candidates), []
    while pool and len(chosen) < n:
        def value(c):
            score = ranks[c.outfitId]
            for p in chosen:
                score -= 25 if p.state.garment == c.state.garment else 0
                score -= 8 if _first(p.state.accessories, BOTTOM_CODE_KIND) == _first(c.state.accessories, BOTTOM_CODE_KIND) else 0
                score -= 6 if _first(p.state.accessories, SHOE_CODE_KIND) == _first(c.state.accessories, SHOE_CODE_KIND) else 0
                score -= 0 if colour_locked else (8 if p.state.colors.main == c.state.colors.main else 0)
                score -= 14 * _overlap(p.state.accessories, c.state.accessories)
            return score
        best = max(pool, key=value)
        chosen.append(best)
        pool.remove(best)
    return chosen

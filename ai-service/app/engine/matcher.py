"""Bộ ghép trang phục (code thuần, không gọi AI).

- candidate_outfits(): từ bối cảnh sinh danh sách bộ đồ hợp lệ, xếp theo điểm (để Gemini chọn 3 bộ).
- match_outfits(): lấy 3 bộ điểm cao nhất, ưu tiên 3 kiểu áo khác nhau (dùng khi Gemini lỗi).
- suggest_alternatives(): từ bộ đồ người dùng tự phối, đề xuất 2 phương án nâng cấp (nút "Hỏi stylist").
Mọi hàm đều chấm luật kèm bối cảnh (thời tiết, nơi, buổi, vai trò) nếu có.
"""
from app.models import Colors, Intent, OutfitState

from .color import score_colors
from .outfit_check import apply_patch
from .rules import count_levels, evaluate

NEUTRALS = ["trang_nga", "den_tuyen", "be_kem"]
DEFAULT_STYLE = {"tet": "truyen_thong", "ky_yeu": "pastel", "dam_cuoi": "truyen_thong",
                 "le_hoi_chua": "truyen_thong", "dao_pho": "toi_gian"}


def _dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out


def score_outfit(o: OutfitState, catalog, intent: Intent | None = None):
    """(điểm, đánh giá luật, điểm màu). Điểm = điểm màu − phạt luật + thưởng khớp mong muốn."""
    evals = evaluate(o, catalog.rules, intent)
    color = score_colors(o, catalog)
    lv = count_levels(evals)
    score = color.score - 40 * lv["risk"] - 8 * lv["consider"] + 4 * lv["ok"]
    if intent:
        if intent.style and intent.style == o.style:
            score += 15
        if o.colors.main in intent.preferredColors:
            score += 10
        if intent.preferredGarment == o.garment:
            score += 20
    return score, evals, color


def _accessories(garment_id, occasion, gender, catalog, must=(), avoid=()):
    wanted = list(must) + catalog.occasions[occasion].get("defaultAccessories", {}).get(garment_id, [])
    chosen, slots = [], set()
    for a in _dedupe(wanted):
        acc = catalog.accessories.get(a)
        if not acc or a in avoid or gender not in acc.get("genders", []) or acc["slot"] in slots:
            continue
        chosen.append(a); slots.add(acc["slot"])
    return chosen


def _best_bottom(main, garment, catalog, avoid):
    options = _dedupe([garment.get("defaultColors", {}).get("bottom")] + NEUTRALS)
    options = [c for c in options if c in catalog.colors and c not in avoid and c != main] or ["trang_nga"]

    def sc(c):
        o = OutfitState(garment=garment["id"], gender="nu", occasion="tet", style="toi_gian",
                        colors=Colors(main=main, bottom=c))
        return score_colors(o, catalog).score
    return max(options, key=sc)


def candidate_outfits(intent: Intent, catalog, limit: int = 8) -> list[OutfitState]:
    """Sinh các bộ hợp lệ (mỗi kiểu áo 2 biến thể màu), sắp xếp theo điểm giảm dần."""
    occ = intent.occasion
    gender = intent.gender if intent.gender in ("nu", "nam") else "nu"
    style = intent.style or DEFAULT_STYLE.get(occ, "truyen_thong")
    avoid_c, avoid_a = set(intent.avoidColors), set(intent.avoidAccessories)

    garments = [g for g in catalog.wearable_garments.values() if gender in g["genders"]]
    fit = [g for g in garments if occ in g["occasions"]] or garments

    palette = catalog.occasions[occ]["palette"]
    style_colors = [c for c in catalog.styles[style]["preferColors"] if c in palette]
    mains = _dedupe(intent.preferredColors + style_colors + palette)
    mains = [c for c in mains if c in catalog.colors and c not in avoid_c]

    scored = []
    for g in fit:
        for main in _dedupe(mains + [g["defaultColors"].get("main")])[:2]:
            accent = next((c for c in intent.preferredColors[1:] + palette
                           if c != main and c not in avoid_c and c in catalog.colors), None)
            o = OutfitState(
                garment=g["id"], gender=gender, occasion=occ, style=style,
                colors=Colors(main=main, bottom=_best_bottom(main, g, catalog, avoid_c),
                              lining=g["defaultColors"].get("lining", "trang_nga"), accent=accent),
                accessories=_accessories(g["id"], occ, gender, catalog, intent.mustHave, avoid_a),
            )
            scored.append((score_outfit(o, catalog, intent)[0], o))
    scored.sort(key=lambda t: -t[0])
    return [o for _, o in scored[:limit]]


def pick_diverse(candidates: list[OutfitState], n: int = 3) -> list[OutfitState]:
    """Lấy n bộ theo thứ tự, ưu tiên mỗi bộ một kiểu áo khác nhau."""
    picked, used = [], set()
    for o in candidates:
        if o.garment not in used:
            picked.append(o); used.add(o.garment)
    for o in candidates:
        if len(picked) >= n:
            break
        if o not in picked:
            picked.append(o)
    return picked[:n]


def match_outfits(intent: Intent, catalog, n: int = 3) -> list[OutfitState]:
    return pick_diverse(candidate_outfits(intent, catalog), n)


def suggest_alternatives(o: OutfitState, catalog, ctx: Intent | None = None,
                         n: int = 2) -> list[tuple[OutfitState, list[str]]]:
    """Phương án nâng cấp quanh bộ đồ hiện tại: sửa theo luật nặng nhất, đổi màu chính, đổi hoạ tiết, đổi phụ kiện."""
    base_score, evals, _ = score_outfit(o, catalog, ctx)
    options: list[tuple[int, OutfitState, list[str]]] = []

    worst = next((e for e in evals if e.level != "ok" and e.suggestion.patch), None)
    if worst:
        alt = apply_patch(o, worst.suggestion.patch)
        options.append((score_outfit(alt, catalog, ctx)[0] + 20, alt, [worst.suggestion.text]))

    palette = catalog.occasions[o.occasion]["palette"]
    for c in palette:
        if c == o.colors.main:
            continue
        alt = o.model_copy(deep=True)
        alt.colors.main = c
        if alt.colors.bottom == c:
            alt.colors.bottom = "trang_nga" if c != "trang_nga" else "den_tuyen"
        s = score_outfit(alt, catalog, ctx)[0]
        if s > base_score:
            options.append((s, alt, [f"Đổi màu chính sang {catalog.name('colors', c)}"]))

    if o.pattern != "tron":
        alt = o.model_copy(update={"pattern": "tron"}, deep=True)
        s = score_outfit(alt, catalog, ctx)[0]
        if s > base_score:
            options.append((s, alt, ["Dùng vải trơn để tổng thể gọn hơn"]))

    defaults = _accessories(o.garment, o.occasion, o.gender, catalog)
    if set(defaults) != set(o.accessories):
        alt = o.model_copy(update={"accessories": defaults}, deep=True)
        names = ", ".join(catalog.name("accessories", a) for a in defaults) or "bỏ bớt phụ kiện"
        options.append((score_outfit(alt, catalog, ctx)[0], alt, [f"Dùng phụ kiện quen thuộc của dịp này: {names}"]))

    options.sort(key=lambda t: -t[0])
    out, seen = [], set()
    for _, alt, changes in options:
        key = alt.model_dump_json()
        if key not in seen and alt != o:
            seen.add(key); out.append((alt, changes))
    return out[:n]

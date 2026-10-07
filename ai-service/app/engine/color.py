"""Chấm điểm hài hòa màu trên không gian OKLCH (0–100) kèm một câu giải thích viết sẵn."""
import math

from app.models import ColorScore, OutfitState

NOTES = {
    "analogous": "Các màu cùng tông nên nhìn hài hòa, dịu mắt.",
    "complementary": "Hai màu tương phản bổ túc, tạo điểm nhấn rõ mà vẫn cân bằng.",
    "neutral": "Màu trung tính đi cùng giúp tổng thể gọn gàng, dễ phối.",
    "clash": "Hai màu chính hơi lệch tông, có thể làm tổng thể rối mắt.",
    "low_contrast": "Áo và quần gần độ sáng nhau nên trông hơi phẳng.",
    "too_saturated": "Các màu đều rực, nên thêm một màu trầm hoặc trung tính.",
}


def hex_to_oklch(hex_: str) -> tuple[float, float, float]:
    """Trả về (L 0–1, C, H độ)."""
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (v ** (1 / 3) for v in (l, m, s))
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def _hue_diff(h1: float, h2: float) -> float:
    d = abs(h1 - h2) % 360
    return 360 - d if d > 180 else d


NEUTRAL_CHROMA = 0.04


def score_pair(main_hex: str, bottom_hex: str, accent_hex: str | None = None) -> ColorScore:
    main, bottom = hex_to_oklch(main_hex), hex_to_oklch(bottom_hex)
    all_ = [main, bottom] + ([hex_to_oklch(accent_hex)] if accent_hex else [])
    score, keys = 50, []

    chromatic = [c for c in all_ if c[1] >= NEUTRAL_CHROMA]
    if len(chromatic) >= 2:
        dh = max(_hue_diff(a[2], b[2]) for i, a in enumerate(chromatic) for b in chromatic[i + 1:])
        if dh < 30:
            score += 25; keys.append("analogous")
        elif dh > 150:
            score += 20; keys.append("complementary")
        elif 60 < dh < 120:
            score -= 10; keys.append("clash")
    if any(c[1] < NEUTRAL_CHROMA for c in all_):
        score += 10
        if not keys:
            keys.append("neutral")

    if abs(main[0] - bottom[0]) >= 0.15:
        score += 15
    else:
        score -= 10; keys.append("low_contrast")

    if all(c[1] > 0.18 for c in all_):
        score -= 15; keys.append("too_saturated")

    score = max(0, min(100, round(score)))
    key = keys[0] if keys else "neutral"
    note = " ".join(NOTES[k] for k in keys[:2]) or NOTES["neutral"]
    return ColorScore(score=score, noteKey="+".join(keys) or key, note=note)


def score_colors(o: OutfitState, catalog) -> ColorScore:
    # màu điểm nhấn chỉ tính khi có phụ kiện dùng màu này (khăn, quai nón, hài, túi...)
    head_acc = any(catalog.accessories.get(a, {}).get("usesAccent", catalog.accessories.get(a, {}).get("slot") in ("head", "hair"))
                   for a in o.accessories)
    accent = catalog.color_hex(o.colors.accent) if (o.colors.accent and head_acc) else None
    return score_pair(catalog.color_hex(o.colors.main), catalog.color_hex(o.colors.bottom), accent)

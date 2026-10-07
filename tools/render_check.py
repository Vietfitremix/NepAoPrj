"""Ghép các lớp SVG người mẫu giấy thành ảnh PNG để soát (thay màu đánh dấu bằng màu thật).

Ví dụ:
  python tools/render_check.py out.png body/body_nu bottom/vay_nu garment/ao_tu_than_nu
  python tools/render_check.py out.png body/body_nu garment/ao_dai_nu --main "#B3261E" --clip 100,140,300,520
Nhiều bộ cạnh nhau: ngăn cách các bộ bằng dấu '+':
  python tools/render_check.py out.png body/body_nu garment/ao_dai_nu + body/body_nam garment/ao_dai_nam
Hoạ tiết đặt vị trí (motif/*.svg) lên thân áo: --pattern phuong_hoang cho mọi bộ, hoặc "@sen" trong từng bộ (ghép giống trang playground)
Ưu tiên render bằng resvg-py (hỗ trợ clipPath); không có thì dùng pymupdf (bỏ qua clipPath).
"""
import argparse
import json
import re
from pathlib import Path

from view_measure import path_poly

FIG = Path(__file__).resolve().parents[1] / "frontend/src/assets/figure"
PATTERNS = Path(__file__).resolve().parents[1] / "data/patterns.json"
DEFAULT = {"main": "#B3261E", "lining": "#F2A7A0", "bottom": "#1E1E1E", "accent": "#2F5D8A"}
MOTIF_SPAN = 62
MARK = {"main": "#FF0000", "lining": "#00FF00", "bottom": "#0000FF", "accent": "#FF00FF"}
_seq = [0]


def inner(rel: str) -> str:
    t = (FIG / f"{rel}.svg").read_text(encoding="utf-8")
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    return re.search(r"<svg[^>]*>(.*)</svg>", t, re.S).group(1)


def with_placement(markup: str, pat: str, back: bool) -> str:
    """Chèn hoạ tiết đặt vị trí ngay sau mảng thân áo cuối cùng, cắt gọn trong thân áo (tay áo không tính)."""
    no_sleeve = re.sub(r'<g id="tay_ao[^"]*">.*?</g>', lambda m: " " * len(m.group(0)), markup, flags=re.S)
    mains = [m for m in re.finditer(r'<path(?![^>]*id="tay)[^>]*fill="#FF0000"[^>]*/>', no_sleeve)]
    if not mains:
        return markup
    pts = [p for m in mains for p in path_poly(re.search(r'\sd="([^"]+)"', m.group(0)).group(1))]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = (x1 - x0) / MOTIF_SPAN                       # giống playground: khung 100 phủ ~1,6 lần bề ngang thân áo, căn giữa
    cx = (x0 + x1) / 2
    src = (FIG / f"motif/{pat}.svg").read_text(encoding="utf-8")
    part = lambda a: re.search(rf'<g data-anchor="{a}">(.*?)</g>\s*(?=<g data-anchor|</svg>)', src, re.S).group(1)
    short = 0.6 if (y1 - y0) < 3 * (x1 - x0) else 1     # áo ngắn (bà ba): thu cụm ở tà
    tf = ((lambda y, z=1: f"translate({cx + 50 * k * z} {y}) scale({-k * z} {k * z})") if back
          else (lambda y, z=1: f"translate({cx - 50 * k * z} {y}) scale({k * z})"))
    _seq[0] += 1
    cid = f"kep_hoa_tiet_{_seq[0]}"
    clip = "".join(re.sub(r'\sid="[^"]*"', "", m.group(0)) for m in mains)
    g = (f'<g id="hoa_tiet_dat"><clipPath id="{cid}">{clip}</clipPath><g clip-path="url(#{cid})" stroke="none" stroke-opacity="1" stroke-width="1" stroke-linejoin="round">'
         f'<g transform="{tf(y0)}">{part("top")}</g><g transform="{tf(y1, short)}">{part("bottom")}</g></g></g>')
    end = mains[-1].end()
    return markup[:end] + g + markup[end:]


def render(svg: str, out: str, dpi: int):
    try:
        import resvg_py
        png = resvg_py.svg_to_bytes(svg_string=svg, zoom=max(1, round(dpi / 72)))
        Path(out).write_bytes(bytes(png))
    except ImportError:
        import pymupdf
        pymupdf.open(stream=svg.encode(), filetype="svg")[0].get_pixmap(dpi=dpi).save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("layers", nargs="+")
    for k, v in DEFAULT.items():
        ap.add_argument(f"--{k}", default=v)
    ap.add_argument("--pattern", help="mã hoạ tiết đặt vị trí trong motif/ (vd. phuong_hoang)")
    ap.add_argument("--clip", help="x0,y0,x1,y1 trong khung 400x800 (áp cho từng bộ)")
    ap.add_argument("--dpi", type=int, default=72)
    a = ap.parse_intermixed_args()

    groups, cur = [], []
    for l in a.layers:
        if l == "+":
            groups.append(cur); cur = []
        else:
            cur.append(l)
    groups.append(cur)

    x0, y0, x1, y1 = (0, 0, 400, 800) if not a.clip else map(float, a.clip.split(","))
    w, h = x1 - x0, y1 - y0
    body = ""
    for i, g in enumerate(groups):
        parts, pat = [], a.pattern
        for l in g:
            if l.startswith("@"):                     # "@sen": hoạ tiết riêng cho bộ này
                pat = l[1:]; continue
            t = inner(l)
            if pat and l.startswith("garment/") and (FIG / f"motif/{pat}.svg").exists():
                t = with_placement(t, pat, l.endswith("_sau"))
            parts.append(t)
        layer = "".join(parts)
        n = int(a.main[1:], 16)
        if pat and (0.299 * (n >> 16) + 0.587 * (n >> 8 & 255) + 0.114 * (n & 255)) / 255 > 0.72:
            layer = layer.replace("#F3EDE4", "#7A6E62")    # giống playground: nét kem đổi sang nâu xám trên nền sáng
        defs = ""
        if pat and not (FIG / f"motif/{pat}.svg").exists():      # hoạ tiết in đều (ô lặp trong data/patterns.json)
            tile = next(t for t in json.loads(PATTERNS.read_text(encoding="utf-8")) if t["id"] == pat)
            pid = f"o_lap_{i}"
            defs = (f'<defs><pattern id="{pid}" patternUnits="userSpaceOnUse" width="{tile["tile"]}" height="{tile["tile"]}">'
                    f'<rect width="{tile["tile"]}" height="{tile["tile"]}" fill="{a.main}"/>{tile["motif"].replace(chr(39), chr(34))}</pattern></defs>')
            layer = re.sub("#FF0000", f"url(#{pid})", layer, flags=re.I)
        for k, mark in MARK.items():
            layer = re.sub(mark, getattr(a, k), layer, flags=re.I)
        layer = defs + layer
        body += f'<g transform="translate({i * w - x0} {-y0})">{layer}</g>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * len(groups)}" height="{h}" viewBox="0 0 {w * len(groups)} {h}">'
           f'<rect width="100%" height="100%" fill="#ffffff"/>{body}</svg>')
    render(svg, a.out, a.dpi)
    print("Đã tạo", a.out)


if __name__ == "__main__":
    main()

"""Cho quần áo có khối như người mẫu: lấy ảnh tô bóng của mô hình 3D (Blender) phủ lên phần vải, viền đậm hơn, thêm nếp khuỷu tay.

Vì sao: người mẫu MakeHuman có tô bóng mềm, còn quần áo là mảng màu phẳng với vài dải bóng thẳng → trông như tấm bìa dán lên
người, nhìn nhỏ thì không đọc ra dáng áo. Công cụ này:
  1. Vùng vải = các mảng tô màu chính #FF0000 của áo (kể cả tay áo).
  2. Ảnh tô bóng .tools/render/<g>_<view>_shade.png → làm mờ → 2 tầng tối (bóng vừa, bóng sâu) + 1 tầng sáng (ánh lụa),
     ngưỡng theo phân bố sáng tối ngay trong vùng vải; vẽ thành lớp "khoi_3d" (đen / trắng trong suốt), cắt gọn trong vải,
     chèn ngay sau mảng thân áo nên cổ áo, khuy, viền vẫn nằm trên.
  3. Bỏ các dải bóng vẽ tay cũ (bong_tay, bong_than) — đã được lớp khối thay thế.
  4. Viền vải đậm hơn (0,3 → 0,55), nét gấp rõ hơn; thêm 2 nếp cong ở khuỷu mỗi tay áo (đo vị trí khuỷu trên lớp tay render).

Chạy: python tools/garment_shade.py garment/ao_dai_nu [truoc|sau|trai] ...
"""
import io
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import resvg_py
import vtracer
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "frontend/src/assets/figure"
RENDER = ROOT / ".tools/render"
RES = 4
SFX = {"truoc": "", "trai": "_trai", "phai": "_phai", "sau": "_sau"}


def raster(svg_inner: str) -> np.ndarray:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">{svg_inner}</svg>'
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg, width=400 * RES, height=800 * RES))
    return np.array(Image.open(io.BytesIO(png)).getchannel("A")) > 127


def trace(mask: np.ndarray, speckle=60) -> str:
    img = Image.fromarray(np.where(mask, 0, 255).astype("uint8")).convert("RGB")
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "i.png", Path(td) / "o.svg"
        img.save(a)
        vtracer.convert_image_to_svg_py(str(a), str(b), colormode="binary", mode="spline", filter_speckle=speckle,
                                        corner_threshold=80, length_threshold=8.0, splice_threshold=45, path_precision=1)
        svg = b.read_text(encoding="utf-8")
    ds = []
    for tag in re.findall(r"<path[^>]*>", svg):
        d = re.search(r'\sd="([^"]+)"', tag).group(1)
        t = re.search(r"translate\(([-\d.]+),\s*([-\d.]+)\)", tag)
        tx, ty = (float(t.group(1)), float(t.group(2))) if t else (0.0, 0.0)
        toks, is_x, res = re.findall(r"[MLCQZ]|-?\d*\.?\d+", d), True, []
        for tk in toks:
            if tk.isalpha():
                res.append(tk); is_x = True
            else:
                res.append(f"{(float(tk) + (tx if is_x else ty)) / RES:.1f}"); is_x = not is_x
        ds.append(" ".join(res))
    return " ".join(ds)


def smooth(mask: np.ndarray, r=3.0) -> np.ndarray:
    return np.array(Image.fromarray((mask * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(r))) > 127


def fabric_pieces(svg: str):
    """Các phần tử tô màu chính (#FF0000) không phải lớp bóng: (thẻ gốc, d)."""
    out = []
    for m in re.finditer(r'<path\b[^>]*\sfill="#FF0000"[^>]*/>', svg):
        tag = m.group(0)
        d = re.search(r'\sd="([^"]+)"', tag)
        if d:
            out.append((tag, d.group(1)))
    return out


def crotch_y(body: np.ndarray) -> float:
    """Đáy chậu (đơn vị khung): hàng đầu tiên dưới nửa người mà trục giữa không còn là thân (góc trước/sau);
    góc nghiêng không có khe chân → lấy 56% chiều cao người."""
    rows = np.flatnonzero(body.any(axis=1))
    top, bot = rows[0], rows[-1]
    for r in range(int(top + 0.45 * (bot - top)), int(top + 0.65 * (bot - top))):
        if not body[r, 200 * RES]:
            return r / RES
    return (top + 0.56 * (bot - top)) / RES


def drape_folds(fabric: np.ndarray, hip: float):
    """Nếp rủ của tà áo: với mỗi mảng vải đủ rộng dưới hông, 3 dải tối + 2 dải sáng chạy dọc, loe dần xuống gấu."""
    dark, light = np.zeros_like(fabric), np.zeros_like(fabric)
    r0 = int((hip - 10) * RES)
    bands = ((0.2, dark, 0.07, 0), (0.5, dark, 0.06, 26), (0.8, dark, 0.07, 12),
             (0.36, light, 0.045, 38), (0.66, light, 0.045, 18))   # (vị trí, lớp, nửa bề rộng, độ trễ bắt đầu)
    for r in range(r0, fabric.shape[0]):
        row = fabric[r]
        if not row.any():
            continue
        xs = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(int), [0]])))
        for a, b in zip(xs[::2], xs[1::2]):
            w = b - a
            if w < 24 * RES:                                   # bỏ mảng hẹp (gấu tay, viền)
                continue
            for i, (f, tgt, k, lag) in enumerate(bands):
                t = (r - r0 - lag * RES) / (90 * RES)          # nếp mọc dần từ hông: thon ở đầu, đủ rộng sau ~90 đơn vị
                if t <= 0:
                    continue
                half = int(w * k * min(1.0, t))
                c = int(a + (f + 0.018 * np.sin(r / (55 * RES) + 1.7 * i)) * w)   # lượn nhẹ như vải rủ
                tgt[r, max(a, c - half):min(b, c + half)] = True
    return [("nep_ru", dark, "#000", 0.09), ("anh_ru", light, "#FFF", 0.14)]


def elbow_folds(g: str, view: str, svg: str) -> str:
    """Hai nếp cong ở khuỷu mỗi tay áo (góc trước/sau): khuỷu ≈ 45% từ đỉnh vai tới cổ tay trên lớp tay render."""
    arm = np.array(Image.open(RENDER / f"{g}_{view}_arm.png").getchannel("A")) > 127
    rows = np.flatnonzero(arm.any(axis=1))
    if not len(rows):
        return ""
    y_el = (rows[0] + 0.42 * (rows[-1] - rows[0])) / RES
    paths = []
    for sid in ("tay_ao_trai", "tay_ao_phai"):
        m = re.search(rf'<path id="{sid}"[^>]*\sd="([^"]+)"', svg)
        if not m:
            continue
        sl = raster(f'<path d="{m.group(1)}" fill="#000"/>')
        for k, dy in enumerate((-5, 4)):
            r = int((y_el + dy) * RES)
            xs = np.flatnonzero(sl[r])
            if len(xs) < 8:
                continue
            x0, x1 = xs[0] / RES + 2.5, xs[-1] / RES - 2.5
            sag = 3.2 if k == 0 else 2.2
            paths.append(f"M{x0:.1f} {y_el + dy:.1f} Q{(x0 + x1) / 2:.1f} {y_el + dy + sag:.1f} {x1:.1f} {y_el + dy - 0.6:.1f}")
    return (f'    <path id="nep_khuyu" d="{" ".join(paths)}" fill="none" stroke="#000" stroke-opacity="0.32" stroke-width="1.1"/>'
            if paths else "")


def shade(rel: str, view: str) -> None:
    g = "nam" if rel.endswith("_nam") else "nu"
    path = FIG / f"{rel}{SFX[view]}.svg"
    svg = path.read_text(encoding="utf-8")
    svg = re.sub(r'\s*<g id="khoi_3d".*?</g>\s*</g>', "", svg, flags=re.S)          # chạy lại không chồng lớp
    svg = re.sub(r'\s*<clipPath id="vai_clip[^"]*">.*?</clipPath>', "", svg, flags=re.S)
    svg = re.sub(r'\s*<path id="nep_khuyu"[^>]*/>', "", svg)
    pieces = fabric_pieces(svg)
    if not pieces:
        print("bỏ qua (không có vải màu chính):", path.name); return
    fabric = raster("".join(f'<path d="{d}" fill="#000"/>' for _, d in pieces))
    gray = np.array(Image.open(RENDER / f"{g}_{view}_shade.png").convert("L").filter(ImageFilter.GaussianBlur(10))).astype(float)
    body = np.array(Image.open(RENDER / f"{g}_{view}_mask.png").getchannel("A")) > 127
    hip = crotch_y(body)                                      # dưới đây vải (tà áo) buông rủ, không ôm theo chân
    zone = fabric & body
    zone[int((hip - 4) * RES):] = False
    inside = gray[zone]
    # bóng nhạt dần trong ~60 đơn vị trên hông (cộng sáng dần) thay vì cắt thẳng ngang
    ys = np.arange(gray.shape[0])[:, None] / RES
    fade = np.clip((ys - (hip - 64)) / 60, 0, 1)
    dim = gray + fade * 120                                     # bóng tối mờ dần về hông
    lit = gray - fade * 120                                     # ánh lụa cũng mờ dần (không thành dải sáng ngang)
    lo, mid, hi = np.percentile(inside, 14), np.percentile(inside, 38), np.percentile(inside, 90)
    layers = [("bong_vua", zone & (dim < mid), "#000", 0.10), ("bong_sau", zone & (dim < lo), "#000", 0.12),
              ("anh_lua", zone & (lit > hi), "#FFF", 0.16)]
    cid = f"vai_clip{SFX[view]}"
    group = [f'    <clipPath id="{cid}">' + "".join(f'<path d="{d}"/>' for _, d in pieces) + "</clipPath>",
             f'    <g id="khoi_3d" clip-path="url(#{cid})" stroke="none"><g>']
    for lid, m, col, op in layers:
        d = trace(smooth(m, 6), speckle=200)
        if d:
            group.append(f'      <path id="{lid}" d="{d}" fill="{col}" fill-opacity="{op}"/>')
    for lid, m, col, op in drape_folds(fabric, hip):          # tà buông: nếp rủ dọc thay cho bóng theo chân
        d = trace(smooth(m, 5), speckle=200)
        if d:
            group.append(f'      <path id="{lid}" d="{d}" fill="{col}" fill-opacity="{op}"/>')
    group.append("    </g></g>")
    if view in ("truoc", "sau"):
        group.append(elbow_folds(g, view, svg))
    # chèn ngay sau mảng vải chính cuối cùng (chi tiết cổ, khuy, viền vẫn nằm trên)
    last = max(svg.rfind(tag) + len(tag) for tag, _ in pieces)
    svg = svg[:last] + "\n" + "\n".join(x for x in group if x) + svg[last:]
    # bỏ dải bóng vẽ tay cũ, viền và nét gấp đậm hơn
    svg = re.sub(r'\s*<path id="(bong_tay|bong_than)"[^>]*/>', "", svg)
    svg = re.sub(r'(<g id="[^"]+" stroke="#000" stroke-opacity=")0\.3(" stroke-width=")1\.3"', r'\g<1>0.55\g<2>1.5"', svg, count=1)
    svg = re.sub(r'(<path id="nep_[^"]*"[^>]*stroke-opacity=")0\.1\d', r"\g<1>0.3", svg)
    path.write_text(svg, encoding="utf-8")
    print("Đã tạo khối cho", path.relative_to(FIG))


if __name__ == "__main__":
    rel, views = sys.argv[1], sys.argv[2:] or ["truoc"]
    for v in views:
        shade(rel, v)

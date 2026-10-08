"""Chuyển ảnh render của Blender (render_model.py) thành SVG người mẫu theo phong cách tranh minh hoạ của dự án.

- Hình bóng (mask) → khối da liền một mảng, viền nâu đậm.
- Ảnh tô bóng (shade) → 2 tầng bóng (vừa, đậm) trong suốt, đặt trong hình bóng.
- Toạ độ: ảnh render gấp RES lần khung 400x800 → thu về đúng khung bằng transform.
Chạy: ai-service/.venv/Scripts/python tools/blender/vectorize_model.py nu .tools/render out_dir
"""
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import vtracer
from PIL import Image

RES = 4
SKIN = {"nu": ("#F4D2B8", "#DEA585", "#6E4636"), "nam": ("#EFC8A6", "#D29A78", "#5E3A2C")}


def trace(mask: np.ndarray, **kw) -> list[str]:
    """Vector hoá ảnh nhị phân (True = phần cần lấy) → danh sách path d (toạ độ ảnh render)."""
    img = Image.fromarray(np.where(mask, 0, 255).astype("uint8")).convert("RGB")
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "in.png", Path(td) / "out.svg"
        img.save(src)
        vtracer.convert_image_to_svg_py(str(src), str(dst), colormode="binary", mode="spline",
                                        filter_speckle=kw.get("speckle", 8), corner_threshold=60,
                                        length_threshold=6.0, splice_threshold=45, path_precision=1)
        svg = dst.read_text(encoding="utf-8")
    out = []
    for tag in re.findall(r"<path[^>]*>", svg):                 # đọc d và transform riêng trong từng thẻ (thứ tự thuộc tính bất kỳ)
        d = re.search(r'\sd="([^"]+)"', tag).group(1)
        t = re.search(r'transform="translate\(([-\d.]+),\s*([-\d.]+)\)"', tag)
        out.append((d, float(t.group(1)) if t else 0.0, float(t.group(2)) if t else 0.0))
    return out


def paths_xml(paths, attrs):
    return "".join(f'<path d="{d}" transform="translate({tx:g} {ty:g})" {attrs}/>' for d, tx, ty in paths)


def build(gender: str, view: str, src: Path) -> str:
    skin, shade, line = SKIN[gender]
    mask = np.array(Image.open(src / f"{gender}_{view}_mask.png"))[..., 3] > 127
    gray = np.array(Image.open(src / f"{gender}_{view}_shade.png").convert("L")).astype(float) / 255
    inside = gray[mask]
    lo, hi = np.percentile(inside, 18), np.percentile(inside, 42)        # hai ngưỡng bóng theo phân bố sáng tối của chính cơ thể
    body = trace(mask, speckle=40)
    mid = trace(mask & (gray < hi), speckle=60)
    dark = trace(mask & (gray < lo), speckle=60)
    k = 1 / RES
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n'
            f'  <!-- Người mẫu {"nữ" if gender == "nu" else "nam"} – góc {view}. Dựng bằng MakeHuman (MPFB2, CC0) trong Blender, '
            f'render trực giao rồi vector hoá: tools/blender/render_model.py + vectorize_model.py. -->\n'
            f'  <g id="body_{gender}{"" if view == "truoc" else "_" + view}" transform="scale({k:g})" stroke-linejoin="round">\n'
            f'    <g id="than_lien_khoi" fill="{skin}" stroke="{line}" stroke-width="{1.4 * RES:g}">{paths_xml(body, "")}</g>\n'
            f'    <g id="bong_vua" fill="{shade}" fill-opacity="0.35" stroke="none">{paths_xml(mid, "")}</g>\n'
            f'    <g id="bong_dam" fill="{shade}" fill-opacity="0.45" stroke="none">{paths_xml(dark, "")}</g>\n'
            f'  </g>\n</svg>\n')


if __name__ == "__main__":
    g, src, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    for v in ("truoc", "trai", "phai", "sau"):
        p = out / f"body_{g}{'' if v == 'truoc' else '_' + v}.svg"
        p.write_text(build(g, v, src), encoding="utf-8")
        print("Đã tạo", p)

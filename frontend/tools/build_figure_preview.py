"""Ghép các lớp SVG người mẫu giấy thành trang xem thử preview.html.

Script làm đúng việc frontend sẽ làm: thay màu đánh dấu bằng biến CSS rồi xếp chồng các lớp.
Chạy:  python tools/build_figure_preview.py
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "public" / "figure"
OUT = FIG / "preview.html"

# Thứ tự lớp: thân (kèm đồ lót) → quần/váy → áo → giày → khăn/nón
LAYERS = [
    # (file, nhãn, bật sẵn?) — mặc định chỉ hiện người mẫu mặc đồ lót trắng
    ("body/body_nu", "Người mẫu nữ (đồ lót trắng)", True),
    ("body/body_nam", "Người mẫu nam (quần lót đùi trắng)", False),
    ("bottom/quan_nu", "Quần", False),
    ("garment/ao_ngu_than_nu", "Áo ngũ thân", False),
    ("accessory/guoc", "Guốc", False),
    ("accessory/khan_van", "Khăn vấn", False),
]

PLACEHOLDERS = {
    "#ff0000": "var(--c-main)",
    "#00ff00": "var(--c-lining)",
    "#0000ff": "var(--c-bottom)",
    "#ff00ff": "var(--c-accent)",
}


def inner_svg(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    try:
        ET.fromstring(text)  # mở được trong trình duyệt/Figma thì phải là XML hợp lệ
    except ET.ParseError as e:
        raise SystemExit(f"{path.name}: lỗi XML – {e}")
    vb = re.search(r'viewBox="([^"]+)"', text)
    if not vb or vb.group(1) != "0 0 400 800":
        raise SystemExit(f"{path.name}: viewBox phải là 0 0 400 800")
    body = re.search(r"<svg[^>]*>(.*)</svg>", text, re.S).group(1)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    for hex_, var in PLACEHOLDERS.items():
        body = re.sub(re.escape(hex_), var, body, flags=re.I)
    return body.strip()


def main():
    hidden = ' style="display:none"'
    layers_html = "\n".join(
        f'<g class="layer" data-layer="{key}"{"" if on else hidden}>\n'
        f'{inner_svg(FIG / (key + ".svg"))}\n</g>'
        for key, _, on in LAYERS
    )
    toggles = "\n".join(
        f'<label><input type="checkbox"{" checked" if on else ""} data-toggle="{key}"> {label}</label>'
        for key, label, on in LAYERS
    )
    palette = json.loads((ROOT.parent / "ai-service" / "data" / "palettes.json").read_text(encoding="utf-8"))
    template = (Path(__file__).parent / "figure_preview_template.html").read_text(encoding="utf-8")
    html = (template
            .replace("{{LAYERS}}", layers_html)
            .replace("{{TOGGLES}}", toggles)
            .replace("{{PALETTE}}", json.dumps(palette, ensure_ascii=False)))
    OUT.write_text(html, encoding="utf-8")
    print("Đã tạo", OUT)


if __name__ == "__main__":
    main()

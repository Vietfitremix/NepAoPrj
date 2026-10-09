"""Sinh hướng PHẢI bằng cách lật đối xứng hướng TRÁI cho mọi asset trong public/figure.

- Với mỗi file *_trai.svg, tạo *_phai.svg (lật qua trục x=200).
- File *_phai.svg có dòng "VE_TAY" ở đầu là bản vẽ tay (ví dụ áo có khuy chỉ thấy từ bên phải): không ghi đè.
- Nếu có *_phai_them.svg (chi tiết riêng của bên phải, vẽ ở toạ độ hướng phải), nội dung được ghép thêm sau bản lật.
Chạy: python tools/mirror_views.py
"""
import re
from pathlib import Path

FIG = Path(__file__).resolve().parents[1] / "public/figure"


def inner(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.search(r"<svg[^>]*>(.*)</svg>", text, re.S).group(1).strip()


def main():
    for src in sorted(FIG.rglob("*_trai.svg")):
        dst = src.with_name(src.name.replace("_trai.svg", "_phai.svg"))
        if dst.exists() and "VE_TAY" in dst.read_text(encoding="utf-8")[:300]:
            print("Giữ bản vẽ tay:", dst.relative_to(FIG))
            continue
        body = inner(src.read_text(encoding="utf-8"))
        body = re.sub(r'id="([^"]+)"', r'id="\1_phai"', body)                 # tránh trùng id với bản trái
        body = body.replace("url(#", "url(#").replace('clip-path="url(#', 'clip-path="url(#')
        body = re.sub(r'url\(#([^)]+)\)', r'url(#\1_phai)', body)
        extra_path = src.with_name(src.name.replace("_trai.svg", "_phai_them.svg"))
        extra = inner(extra_path.read_text(encoding="utf-8")) if extra_path.exists() else ""
        dst.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n'
            f'  <!-- Hướng PHẢI: sinh tự động bằng tools/mirror_views.py từ {src.name}. Không sửa tay file này. -->\n'
            f'  <g transform="matrix(-1 0 0 1 400 0)">\n{body}\n  </g>\n'
            + (f"  {extra}\n" if extra else "")
            + "</svg>\n", encoding="utf-8")
        print("Đã tạo", dst.relative_to(FIG))


if __name__ == "__main__":
    main()

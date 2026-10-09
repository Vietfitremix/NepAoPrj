"""Đo mép cơ thể người mẫu: ở mỗi độ cao y, các đoạn x mà thân người chiếm (tay, thân, chân).

Dùng khi vẽ quần áo để mép áo/quần bám đúng dáng người.
Chạy: python tools/body_measure.py [nu|nam]          -> in bảng số đo (mặc định: nu)
      python tools/body_measure.py [nu|nam] --md     -> in bảng Markdown (dán vào README)
"""
import sys

from figure_lib import outline, spans

LANDMARKS = {
    150: "cổ", 178: "vai", 200: "dưới vai", 222: "nách", 238: "ngực", 266: "chân ngực",
    300: "giữa sườn", 318: "eo / khuỷu tay", 350: "bụng", 388: "cạp quần lót",
    414: "hông", 430: "cổ tay", 440: "đáy chậu", 470: "gấu quần đùi",
    500: "giữa đùi / đầu ngón tay", 590: "gối", 660: "bắp chân", 748: "mắt cá",
}


def load(model):
    if model == "nam":
        import gen_body_nam as m
    else:
        import gen_body_nu as m
    return m.START, m.LEFT


if __name__ == "__main__":
    model = "nam" if "nam" in sys.argv[1:] else "nu"
    poly = outline(*load(model))
    md = "--md" in sys.argv
    if md:
        print("| y | Mốc | Các đoạn x thân người chiếm (trái → phải) |")
        print("| --- | --- | --- |")
    for y, name in LANDMARKS.items():
        s = "  ".join(f"{a}–{b}" for a, b in spans(y, poly))
        print(f"| {y} | {name} | {s} |" if md else f"y={y:<4} {name:<24} {s}")

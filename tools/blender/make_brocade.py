"""Vẽ ô hoạ tiết gấm (lặp liền) cho bản dựng 3D minh hoạ: huy hiệu tròn hoa văn hình học xen mây cuộn.
Nét trắng trên nền trong suốt — trong Blender trộn thành màu sáng hơn nền vải một chút (gấm cùng tông).
Hoạ tiết tự vẽ bằng hình học đơn giản, không chép mẫu nào.

Chạy: ai-service/.venv/Scripts/python tools/blender/make_brocade.py .tools/brocade.png
"""
import math
import sys

from PIL import Image, ImageDraw

S = 1024                        # vẽ gấp đôi rồi thu nhỏ → nét mịn
T = 512


def medallion(d: ImageDraw.ImageDraw, cx, cy, r, w):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="white", width=w)
    d.ellipse([cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82], outline="white", width=max(2, w // 2))
    # hoa văn hình học đối xứng 4 phía: thanh ngang/dọc gấp khúc (kiểu hồi văn) bên trong vòng tròn
    k = r * 0.62
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        pts = [(cx, cy - sy * k), (cx + sx * k * 0.55, cy - sy * k), (cx + sx * k * 0.55, cy - sy * k * 0.35),
               (cx + sx * k * 0.2, cy - sy * k * 0.35), (cx + sx * k * 0.2, cy)]
        d.line(pts, fill="white", width=w, joint="curve")
    d.line([(cx - k, cy), (cx + k, cy)], fill="white", width=w)
    d.line([(cx, cy - k * 0.35), (cx, cy + k * 0.35)], fill="white", width=w)


def cloud(d: ImageDraw.ImageDraw, cx, cy, s, w):
    """Mây cuộn: một đường lượn có hai đầu xoắn ốc, kèm dải đuôi."""
    def spiral(x0, y0, r0, turns, direction):
        pts = []
        for i in range(int(40 * turns)):
            a = direction * i / 40 * 2 * math.pi
            r = r0 * (1 - i / (40 * turns) * 0.85)
            pts.append((x0 + r * math.cos(a), y0 + r * math.sin(a)))
        d.line(pts, fill="white", width=w, joint="curve")
    spiral(cx - s, cy, s * 0.55, 1.4, 1)
    spiral(cx + s, cy, s * 0.55, 1.4, -1)
    arc = [(cx - s + s * 0.55 * math.cos(t), cy - s * 0.15 - s * 0.55 * math.sin(t) * 0.6) for t in [i / 30 * math.pi for i in range(31)]]
    d.line([(cx - s * 0.45, cy - s * 0.2)] + [(cx + (x - cx) * 0.9, y - s * 0.25) for x, y in arc[::-1]][:0] +
           [(cx - s * 0.45 + i / 30 * s * 0.9, cy - s * 0.55 * math.sin(i / 30 * math.pi) - s * 0.2) for i in range(31)],
           fill="white", width=w, joint="curve")
    d.line([(cx - s * 1.6, cy + s * 0.6), (cx - s * 0.4, cy + s * 0.55), (cx + s * 0.5, cy + s * 0.75), (cx + s * 1.7, cy + s * 0.6)],
           fill="white", width=w, joint="curve")


def main(out):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = 9
    for cx, cy in ((S * 0.25, S * 0.25), (S * 0.75, S * 0.75)):
        medallion(d, cx, cy, S * 0.11, w)
    for cx, cy in ((S * 0.75, S * 0.25), (S * 0.25, S * 0.75)):
        cloud(d, cx, cy, S * 0.07, w - 2)
    # lặp liền ở mép: vẽ thêm phần tràn của 4 huy hiệu ở góc (không có — bố cục đã cách mép đủ xa)
    im.resize((T, T), Image.LANCZOS).save(out)
    print("Đã tạo", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".tools/brocade.png")

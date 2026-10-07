"""Đo mép người mẫu ở một hướng nhìn bất kỳ (đọc thẳng file SVG đã sinh), dùng khi vẽ quần áo góc trái/sau.

In các đoạn x mà từng phần (thân liền khối, tay gần) chiếm ở mỗi độ cao y.
Chạy: python tools/view_measure.py nu trai      (hoặc: nam trai, nu sau, nam sau)
"""
import re
import sys
from pathlib import Path

from figure_lib import _bezier, spans

FIG = Path(__file__).resolve().parents[1] / "frontend/src/assets/figure/body"
YS = [126, 140, 150, 164, 178, 200, 222, 238, 266, 300, 318, 350, 388, 414, 430, 440, 470, 500, 540, 590, 620, 660, 700, 740, 748, 760, 770, 781]


def path_poly(d: str):
    """Đa giác xấp xỉ một path toạ độ tuyệt đối gồm M/L/C/Q/Z."""
    toks = re.findall(r"[MLCQZ]|-?\d*\.?\d+", d)
    pts, cur, i, cmd = [], None, 0, None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd == "Z":
                continue
        n = {"M": 2, "L": 2, "C": 6, "Q": 4}[cmd]
        v = [float(x) for x in toks[i:i + n]]; i += n
        if cmd in "ML":
            cur = (v[0], v[1]); pts.append(cur)
        elif cmd == "C":
            pts.extend(_bezier(cur, (v[0], v[1]), (v[2], v[3]), (v[4], v[5]))); cur = (v[4], v[5])
        else:                                              # Q -> C
            q, p = (v[0], v[1]), (v[2], v[3])
            c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            c2 = (p[0] + 2 / 3 * (q[0] - p[0]), p[1] + 2 / 3 * (q[1] - p[1]))
            pts.extend(_bezier(cur, c1, c2, p)); cur = p
    return pts


if __name__ == "__main__":
    g, view = (sys.argv[1:] + ["nu", "trai"])[:2] if len(sys.argv) > 2 else ("nu", "trai")
    svg = (FIG / f"body_{g}_{view}.svg").read_text(encoding="utf-8")
    parts = {pid: path_poly(d) for pid, d in re.findall(r'id="(than_lien_khoi|tay_gan)"[^>]*?d="([^"]+)"', svg)}
    for y in YS:
        row = "  ".join(f"{k}: " + " ".join(f"{a}–{b}" for a, b in spans(y, p)) for k, p in parts.items() if spans(y, p))
        print(f"y={y:<4} {row}")

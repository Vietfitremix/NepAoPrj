"""Sinh lại quần áo, quần/váy hướng TRÁI (và *_phai_them) theo người mẫu MakeHuman, đo thẳng trên ảnh render của Blender.

Dùng lại các hàm dựng áo trong tools/gen_garment_views.py (ao_dai, ngu_than, ba_ba, tu_than, nhat_binh, quan, vay),
chỉ thay lớp đo người mẫu:
  - mép trước/sau thân   = .tools/render/<g>_trai_mask.png trừ lớp tay gần (<g>_trai_arm.png), nên thân áo không
    phình theo bàn tay và lưng áo bám đúng lưng người mới;
  - mép trước/sau tay gần = <g>_trai_arm.png → tay áo bọc đúng cánh tay mới;
  - các mốc độ cao viết sẵn trong hàm dựng (vai 176, eo 316, hông 414, gấu ...) theo khung người mẫu cũ được quy đổi
    sang người mẫu mới bằng cùng phép nội suy mốc của tools/refit_to_body.py (đỉnh, cổ, đáy chậu, mắt cá, đáy chân).
Hàm dựng chạy trong hệ toạ độ dọc cũ; xong mới đổi mọi toạ độ y sang hệ mới (x giữ nguyên). Lớp "ban_tay" (tay gần vẽ
lại trên quần áo) lấy đúng path tay của body_<g>_trai.svg mới, cắt từ cổ tay áo / cạp quần trở xuống.

Chạy: python tools/gen_side_views.py   (cần .tools/render từ render_model.py và .tools/old_body = người mẫu cũ)
      rồi python tools/mirror_views.py
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import gen_garment_views as gv                      # noqa: E402
from refit_to_body import landmarks, silhouette, warp_svg   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "frontend/src/assets/figure"
RENDER = ROOT / ".tools/render"
OLD = ROOT / ".tools/old_body"
RES = 4


def load(png: Path, blur=1.5) -> np.ndarray:
    im = Image.open(png).getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    return np.array(im) > 127


def dilate(m: np.ndarray, r: int) -> np.ndarray:
    im = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(2 * r + 1))
    return np.array(im) > 127


class YMap:
    """Đổi độ cao: hệ người mẫu cũ ↔ mới (nội suy tuyến tính từng khúc giữa các mốc)."""

    def __init__(self, lo, ln):
        self.lo, self.ln = lo, ln

    def __call__(self, y):
        return float(np.interp(y, self.lo, self.ln, left=self.ln[0] + y - self.lo[0], right=self.ln[-1] + y - self.lo[-1]))

    def back(self, y):
        return float(np.interp(y, self.ln, self.lo))


class Warp:
    """Phép đổi toạ độ cho warp_svg: x giữ nguyên, y theo YMap."""

    def __init__(self, ym: YMap):
        self.ym = ym

    def __call__(self, pts):
        pts = np.atleast_2d(np.asarray(pts, float))
        return np.column_stack([pts[:, 0], [self.ym(y) for y in pts[:, 1]]])

    def jac(self, p):
        y = float(np.asarray(p)[1])
        return np.array([[1.0, 0.0], [0.0, (self.ym(y + 0.5) - self.ym(y - 0.5))]])


class NewSide:
    """Thay cho gen_garment_views.Side: đo người mẫu mới trên ảnh render, nhận/trả độ cao theo hệ CŨ."""

    def __init__(self, g: str, ym: YMap):
        self.g, self.ym = g, ym
        arm = load(RENDER / f"{g}_trai_arm.png")
        body = load(RENDER / f"{g}_trai_mask.png")
        self.arm = arm
        self.body = body & ~dilate(arm, 2 * RES)
        svg = (FIG / f"body/body_{g}_trai.svg").read_text(encoding="utf-8")
        self.svg = svg
        self.skin = re.search(r'id="than_lien_khoi" fill="([^"]+)"', svg).group(1)
        self.line = re.search(r'<g id="body_\w+" stroke="([^"]+)"', svg).group(1)

    def _row(self, m, y_old):
        yn = self.ym(y_old)
        r = int(round(yn * RES))
        for dr in range(0, 6 * RES):                      # hàng trống (vd. khe nách) → lấy hàng gần nhất có hình
            for rr in (r + dr, r - dr):
                if 0 <= rr < m.shape[0] and m[rr].any():
                    return np.flatnonzero(m[rr]) / RES
        raise ValueError(f"không đo được ở y={y_old}")

    def f(self, y):
        return float(self._row(self.body, y)[0])

    def b(self, y):
        return float(self._row(self.body, y)[-1] + 1 / RES)

    def af(self, y):
        return float(self._row(self.arm, y)[0])

    def ab(self, y):
        return float(self._row(self.arm, y)[-1] + 1 / RES)

    def hand(self, clip_y: float, uid: str) -> str:
        return f"<!--BAN_TAY:{clip_y}:{uid}-->"

    def hand_xml(self, clip_y_old: float, uid: str) -> str:
        y0 = self.ym(clip_y_old)
        arm_d = re.search(r'id="tay_gan"[^>]*\sd="([^"]+)"', self.svg).group(1)
        shade = re.sub(r'\sid="[^"]*"', "", re.search(r'<path id="bong_tay"[^>]*/>', self.svg).group(0))
        return (f'<clipPath id="cat_tay_{uid}"><rect x="0" y="{y0:.1f}" width="400" height="{800 - y0:.1f}"/></clipPath>\n'
                f'    <g id="ban_tay" clip-path="url(#cat_tay_{uid})" stroke="{self.line}" stroke-width="1.3" stroke-linejoin="round">\n'
                f'      <path d="{arm_d}" fill="{self.skin}"/>\n      {shade}\n    </g>')


def collar(S, y0, y1, m=1.6, lift=0):
    """Như gv.collar, nhưng mép trước ở đỉnh cổ không vượt quá mép cổ phía dưới (cằm nhô ra trước không kéo cổ áo theo)."""
    f0 = max(S.f(y0), S.f(y1) + 1)
    return gv.shape([(f0 - m, y0), (S.b(y0) + m, y0 - lift)],
                    [(S.b(y1) + m + 0.5, y1 - 2 - lift), (S.f(y1) - m - 0.5, y1 + 1)])


def vay(S, g="nu"):
    """Như gv.vay, nhưng mép trước/sau đo theo người suốt tới gấu rồi giữ dáng chữ A (đùi, gối người mới nhô hơn đường
    thẳng của bản cũ; váy không được bó theo chân như quần)."""
    waist = 314
    run = gv.ys(waist, 754, 12)
    flare = lambda y: 0 if y <= 430 else 0.07 * (y - 430)  # loe chữ A dưới hông, ~23 đơn vị ở gấu mỗi bên
    fr, bk, xf, xb = [], [], 1e9, -1e9
    for y in run:                                         # mép chỉ đi ra ngoài khi xuống dưới (không thụt vào theo gối)
        xf = min(xf, S.f(y) - 3)
        xb = max(xb, S.b(y) + 3.5)
        fr.append((xf - flare(y), y)); bk.append((xb + flare(y), y))
    d = gv.shape(fr, bk[::-1])
    body = "\n".join([
        gv.el("vai_vay", d, "#0000FF"),
        f'    <path id="bong" d="{gv.shape([(x - 10, y) for x, y in bk[9:]], bk[9:][::-1])}" {gv.SHADE}/>',
        f'    <path id="nep_vay" d="M{fr[10][0] + 14:.1f} {fr[10][1]} L{fr[-1][0] + 8:.1f} 752 '
        f'M{(fr[10][0] + bk[10][0]) / 2:.1f} {fr[10][1]} L{(fr[-1][0] + bk[-1][0]) / 2 + 2:.1f} 754" {gv.FOLD}/>',
        "    " + S.hand(waist - 2, "vay_nu"),
    ])
    return gv.svg_doc("vay_nu_trai", f"Váy dài nữ – hướng TRÁI. Cạp ở eo y={waist}, dáng chữ A phủ đùi, gối, loe tới gấu y=754; "
                      "vẽ lại tay gần nằm trên váy.", body)


gv.collar = collar                                         # các hàm dựng áo trong gen_garment_views gọi collar() qua module


def finish(svg: str, S: NewSide, warp: Warp) -> str:
    out = warp_svg(svg, warp)
    out = re.sub(r"<!--BAN_TAY:([\d.]+):(\w+)-->", lambda m: S.hand_xml(float(m.group(1)), m.group(2)), out)
    return out.replace("Sinh bằng tools/gen_garment_views.py.",
                       "Sinh bằng tools/gen_side_views.py (đo trên người mẫu MakeHuman).")


def main():
    out = {}
    for g in ("nu", "nam"):
        ym = YMap(landmarks(silhouette(OLD / f"body_{g}.svg")), landmarks(silhouette(FIG / f"body/body_{g}.svg")))
        S, W = NewSide(g, ym), Warp(ym)
        makers = [gv.ao_dai, gv.ngu_than, gv.ba_ba] + ([gv.tu_than, gv.nhat_binh] if g == "nu" else [])
        for mk in makers:
            svg, extra = mk(S, g)
            name = re.search(r'<g id="(\w+)_trai"', svg).group(1)
            out[f"garment/{name}_trai"] = finish(svg, S, W)
            if extra:                                     # khuy hướng phải: toạ độ đã lật → chỉ đổi y
                out[f"garment/{name}_phai_them"] = finish(extra, S, W)
        out[f"bottom/quan_{g}_trai"] = finish(gv.quan(S, g), S, W)
        if g == "nu":
            out["bottom/vay_nu_trai"] = finish(vay(S), S, W)
    for rel, svg in out.items():
        p = FIG / f"{rel}.svg"
        p.write_text(svg, encoding="utf-8")
        print("Đã tạo", p.relative_to(FIG))


if __name__ == "__main__":
    main()

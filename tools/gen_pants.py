"""Dựng quần ống suông hướng TRƯỚC và SAU theo người mẫu MakeHuman, đo thẳng trên ảnh render của Blender.

Lý do: quần uốn từ bản vẽ cho người mẫu cũ bị hẹp hơn hông người mới (nhất là nam: hông rộng, bàn tay buông sát hông),
lộ đồ lót và da ở hông. Ở đây mỗi hàng y:
  - thân (đã trừ lớp tay) cho mép eo, hông;  mép ngoài ống = mép hông/đùi + độ nới, kẻ thẳng từ hông xuống gấu
    sao cho vẫn phủ kín đùi, gối, bắp chân (ống suông);
  - mép ngoài không đè lên cánh tay, bàn tay (lớp tay nằm dưới quần trong thứ tự lớp);
  - mép trong ống: từ đáy chậu kẻ thẳng xuống gấu, phủ kín mép trong của chân.
Độ cao cạp (eo cũ y=316) và gấu (y=752) quy đổi sang người mẫu mới bằng YMap của tools/gen_side_views.py.

Chạy: python tools/gen_pants.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import gen_garment_views as gv                                  # noqa: E402
from gen_side_views import FIG, OLD, RENDER, RES, YMap, dilate, load   # noqa: E402
from refit_to_body import landmarks, silhouette                 # noqa: E402

NOTE = {"nu": "Quần nữ ống suông", "nam": "Quần nam ống suông (mặc cùng áo dài, ngũ thân, bà ba nam)"}


def edges(m: np.ndarray, y: float):
    r = m[int(round(y * RES))]
    xs = np.flatnonzero(r)
    return (xs[0] / RES, (xs[-1] + 1) / RES) if len(xs) else None


def center_edges(m: np.ndarray, y: float):
    """Mép trái/phải của đoạn thân chứa trục giữa x=200 (bỏ khuỷu tay, bàn tay nằm tách khỏi thân)."""
    r = m[int(round(y * RES))].astype(int)
    c = 200 * RES
    if not r[c]:
        return edges(m, y)
    left = c - np.argmin(r[c::-1]) if not r[:c + 1].all() else 0
    right = c + np.argmin(r[c:]) if not r[c:].all() else len(r)
    return left / RES, right / RES


def side_cover(ys, need, hip_x, hem_x, outward):
    """Mép thẳng từ (hip_x, ys[0]) tới gấu, đẩy ra ngoài đủ để phủ mọi điểm need(y). outward=-1: bên trái, +1: bên phải."""
    t = (ys - ys[0]) / (ys[-1] - ys[0])
    x = hip_x + (hem_x - hip_x) * t
    gap = (need - x) * outward                              # > 0: đường thẳng chưa phủ tới
    k = np.max(np.where(t > 0.05, gap / np.maximum(t, 0.05), 0))
    return x + outward * max(k, 0) * t


def build(g: str, view: str, ym: YMap, crotch: float) -> str:
    body = load(RENDER / f"{g}_{view}_mask.png")
    arm = load(RENDER / f"{g}_{view}_arm.png") & body
    torso = load(RENDER / f"{g}_{view}_noarm.png")        # thân không tay (render riêng trong Blender)
    yw, yhem = ym(316), ym(752)
    ease = 1.6 if g == "nu" else 2.0

    # --- eo → hông: theo mép thân, nới dần; không đè lên tay
    up = np.arange(yw, crotch + 0.1, 4.0)
    L = np.array([center_edges(torso, y)[0] - ease for y in up])
    R = np.array([center_edges(torso, y)[1] + ease for y in up])
    L, R = np.minimum.accumulate(L), np.maximum.accumulate(R)        # quần không thắt vào dưới hông
    hip_i = len(up) - 1

    # --- hông → gấu: hai ống thẳng phủ kín chân
    down = np.arange(crotch, yhem + 0.1, 4.0)
    legL = np.array([edges(torso[:, :200 * RES], y) or (np.nan, np.nan) for y in down])
    legR = np.array([edges(torso[:, 200 * RES:], y) or (np.nan, np.nan) for y in down]) + [200, 200]
    ank = -3                                                        # đo mắt cá cao hơn gấu một chút
    # mép ngoài: theo đùi với độ nới, chỉ được rộng ra khi xuống dưới → ống suông (không thót theo gối, không loe)
    oL = np.minimum.accumulate(np.concatenate([[L[hip_i]], np.nan_to_num(legL[:, 0] - ease, nan=1e9)]))[1:]
    oR = np.maximum.accumulate(np.concatenate([[R[hip_i]], np.nan_to_num(legR[:, 1] + ease, nan=-1e9)]))[1:]
    iL = side_cover(down, legL[:, 1] + ease, 199.0, legL[ank, 1] + 4, +1)
    iR = side_cover(down, legR[:, 0] - ease, 201.0, legR[ank, 0] - 4, -1)
    iL, iR = np.minimum(iL, 199.5), np.maximum(iR, 200.5)

    # --- không đè lên tay: kẹp mép ngoài vào trong mép trong của cánh tay; dưới bàn tay nở ra dần (không gấp khúc)
    def clamp(xs, ys, side, rate=0.35):
        out = []
        for x, y in zip(xs, ys):
            r = arm[int(round(y * RES))]
            half = np.flatnonzero(r[:200 * RES] if side < 0 else r[200 * RES:])
            if len(half):
                inner = (half[-1] + 1) / RES if side < 0 else 200 + half[0] / RES
                x = max(x, inner + 0.3) if side < 0 else min(x, inner - 0.3)
            if out:
                step = rate * (y - prev_y)
                x = max(x, out[-1] - step) if side < 0 else min(x, out[-1] + step)
            out.append(x); prev_y = y
        return np.array(out)
    ys_all = np.concatenate([up, down[1:]])
    outL = clamp(np.concatenate([L, oL[1:]]), ys_all, -1)
    outR = clamp(np.concatenate([R, oR[1:]]), ys_all, +1)
    L, oL = outL[:len(up)], np.concatenate([[outL[len(up) - 1]], outL[len(up):]])
    R, oR = outR[:len(up)], np.concatenate([[outR[len(up) - 1]], outR[len(up):]])

    left = list(zip(L, up)) + list(zip(oL[1:], down[1:]))
    right = list(zip(R, up)) + list(zip(oR[1:], down[1:]))
    pts_out = left[::-1]                                            # gấu trái → cạp trái
    # tách mép trái / mép phải thành hai đoạn để góc cạp là góc nhọn (đường cong mềm qua góc sẽ vọt ra thành gờ)
    d = gv.shape([(left[-1][0], yhem)] + pts_out[1:], right[:-1] + [(right[-1][0], yhem)],
                 [(iR[-1], yhem)] + list(zip(iR[::-1], down[::-1]))[1:-1] + [(200, crotch)]
                 + list(zip(iL, down))[1:-1] + [(iL[-1], yhem)])
    cL, cR = (oL[-1] + iL[-1]) / 2, (oR[-1] + iR[-1]) / 2
    yk = crotch + 0.12 * (yhem - crotch)
    shade = (f"M200 {crotch:.1f} L{iR[-1]:.1f} {yhem:.1f} L{iR[-1] + 12:.1f} {yhem:.1f} L{iR[0] + 2:.1f} {crotch - 6:.1f} Z "
             f"M{oL[0]:.1f} {crotch:.1f} L{oL[0] + 6:.1f} {crotch:.1f} L{oL[-1] + 6:.1f} {yhem:.1f} L{oL[-1]:.1f} {yhem:.1f} Z")
    nep = (f"M{np.interp(yk, down, (oL + iL) / 2):.1f} {yk:.1f} L{cL:.1f} {yhem - 4:.1f} "
           f"M{np.interp(yk, down, (oR + iR) / 2):.1f} {yk:.1f} L{cR:.1f} {yhem - 4:.1f} "
           f"M{L[2] + 3:.1f} {up[2]:.1f} L{R[2] - 3:.1f} {up[2]:.1f}")
    gid = f"quan_{g}" + ("" if view == "truoc" else "_sau")
    huong = "TRƯỚC" if view == "truoc" else "SAU"
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n'
            f'  <!-- {NOTE[g]} – hướng {huong}. Cạp ở eo y={yw:.0f}, gấu ở mắt cá y={yhem:.0f}. #0000FF = màu quần (c-bottom).\n'
            '       Dựng theo người mẫu MakeHuman bằng tools/gen_pants.py: mép ngoài phủ hông, đùi (không đè lên tay), ống thẳng. -->\n'
            f'  <g id="{gid}" stroke="#000" stroke-opacity="0.3" stroke-width="1.3" stroke-linejoin="round">\n'
            f'    <path id="vai_quan" d="{d}" fill="#0000FF"/>\n'
            f'    <path id="bong" d="{shade}" fill="#000" fill-opacity="0.12" stroke="none"/>\n'
            f'    <path id="nep" d="{nep}" fill="none" stroke="#000" stroke-opacity="0.18" stroke-width="1.4"/>\n'
            '  </g>\n</svg>\n')


def main():
    for g in ("nu", "nam"):
        lo = landmarks(silhouette(OLD / f"body_{g}.svg"))
        ln = landmarks(silhouette(FIG / f"body/body_{g}.svg"))
        ym = YMap(lo, ln)
        for view, sfx in (("truoc", ""), ("sau", "_sau")):
            p = FIG / f"bottom/quan_{g}{sfx}.svg"
            p.write_text(build(g, view, ym, ln[2]), encoding="utf-8")
            print("Đã tạo", p.relative_to(FIG))


if __name__ == "__main__":
    main()

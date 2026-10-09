"""Sinh quần áo, quần/váy và phụ kiện ở hướng TRÁI và SAU (hướng PHẢI do tools/mirror_views.py lật từ TRÁI).

Hướng TRÁI (nhìn nghiêng, mặt quay sang trái khung hình) dựng theo SỐ ĐO đọc thẳng từ body_*_trai.svg:
  - mép trước/sau của thân áo, quần = mép người ± khoảng nới, nên luôn phủ kín người (quy tắc 1–2 trong README);
  - tay áo bọc tay gần theo đúng đường bao tay;
  - lớp nào đè lên vùng tay gần (thân áo dài, quần, váy) thì vẽ lại phần bàn tay / cẳng tay lộ ra ở trên cùng,
    để bàn tay không bị quần áo che mất.
Chi tiết chỉ thấy từ bên phải (đường cài khuy chéo của áo dài, ngũ thân) ghi vào *_phai_them.svg.
Hướng SAU dựng từ bản hướng trước: bỏ khuy, túi, yếm, vạt trước; thêm đường may sống lưng.

Chạy: python tools/gen_garment_views.py   (tự gọi mirror_views.py ở cuối)
"""
import re
import subprocess
import sys
from pathlib import Path

from figure_lib import mirror_d, spans
from view_measure import path_poly

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "public/figure"
G = 'stroke="#000" stroke-opacity="0.3" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round"'
SHADE = 'fill="#000" fill-opacity="0.12" stroke="none"'
FOLD = 'fill="none" stroke="#000" stroke-opacity="0.18" stroke-width="1.1"'


# ---------------------------------------------------------------- số đo người mẫu hướng trái
class Side:
    def __init__(self, g: str):
        svg = (FIG / f"body/body_{g}_trai.svg").read_text(encoding="utf-8")
        get = lambda pid: re.search(rf'id="{pid}"[^>]*?d="([^"]+)"', svg).group(1)
        self.g = g
        self.body = path_poly(get("than_lien_khoi"))
        self.arm_d, self.thumb_d, self.arm_shade_d = get("tay_gan"), get("ngon_cai"), get("bong_tay")
        self.arm = path_poly(self.arm_d)
        self.skin = re.search(r'id="than_lien_khoi" fill="([^"]+)"', svg).group(1)
        self.line = re.search(r'<g id="body_\w+" stroke="([^"]+)"', svg).group(1)
        self.shade = re.search(r'id="bong_than" fill="([^"]+)"', svg).group(1)

    def f(self, y):                   # mép trước (x nhỏ) của thân
        return spans(y, self.body)[0][0]

    def b(self, y):                   # mép sau (x lớn) của thân
        return spans(y, self.body)[-1][1]

    def af(self, y):
        return spans(y, self.arm)[0][0]

    def ab(self, y):
        return spans(y, self.arm)[-1][1]

    def hand(self, clip_y: float, uid: str) -> str:
        """Vẽ lại phần tay gần nằm dưới clip_y (cẳng tay, bàn tay) để nằm trên lớp quần áo."""

        # cắt sẵn đa giác (không dùng clipPath để trình xem SVG nào cũng hiển thị đúng)
        lines = [f'<g id="ban_tay" stroke="{self.line}" stroke-width="1.3" stroke-linejoin="round">',
                 f'      <path d="{poly_d(clip_below(self.arm, clip_y))}" fill="{self.skin}"/>',
                 f'      <path d="{poly_d(clip_below(path_poly(self.arm_shade_d), clip_y))}" fill="{self.shade}" fill-opacity="0.45" stroke="none"/>',
                 f'      <path d="{self.thumb_d}" fill="{self.skin}"/>',
                 '    </g>']
        return "\n".join(lines)


def clip_below(poly, y0):
    """Phần đa giác nằm dưới đường y = y0 (Sutherland–Hodgman với một nửa mặt phẳng)."""
    out = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ina, inb = a[1] >= y0, b[1] >= y0
        if ina:
            out.append(a)
        if ina != inb:
            t = (y0 - a[1]) / (b[1] - a[1])
            out.append((a[0] + t * (b[0] - a[0]), y0))
    return out


def poly_d(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z" if pts else ""


# ---------------------------------------------------------------- đường cong mềm qua các điểm
def _p(p):
    return f"{p[0]:.1f} {p[1]:.1f}"


def smooth(pts, start=True) -> str:
    """Đường Catmull-Rom (đổi sang bezier bậc 3) đi qua mọi điểm. start=True: mở đầu bằng M, ngược lại nối bằng L."""
    out = [("M" if start else "L") + _p(pts[0])]
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{_p(c1)} {_p(c2)} {_p(p2)}")
    return " ".join(out)


def shape(*runs) -> str:
    """Hình kín ghép từ nhiều đoạn cong: góc nhọn giữa các đoạn, cong mềm trong mỗi đoạn."""
    return " ".join(smooth(r, i == 0) for i, r in enumerate(runs)) + " Z"


def lerp(a, b, t):
    return a + (b - a) * t


def ys(a, b, step=8):
    out = list(range(int(a), int(b), step))
    return out + [b] if out[-1] != b else out


def front_edge(S, y_list, m, ease=None):
    """Mép trước = mép người - m. ease: độ lùi tối đa mỗi đơn vị y (vải rủ từ ngực xuống, không ôm sát bụng)."""
    pts, prev = [], None
    for y in y_list:
        x = S.f(y) - (m(y) if callable(m) else m)
        if ease is not None and prev is not None:
            x = min(x, prev + ease * (y - pts[-1][1]))
        pts.append((x, y)); prev = x
    return pts


def back_edge(S, y_list, m, ease=None):
    pts, prev = [], None
    for y in y_list:
        x = S.b(y) + (m(y) if callable(m) else m)
        if ease is not None and prev is not None:
            x = max(x, prev - ease * (y - pts[-1][1]))
        pts.append((x, y)); prev = x
    return pts


def sleeve(S, m_top, m_bottom, cuff_y, flare=0.0):
    """Tay áo bọc tay gần: m_* là khoảng nới ở bắp tay / cổ tay, flare nới thêm về phía gấu (tay rộng)."""
    rows = ys(196, cuff_y - 6, 10)
    fr, bk = [], []
    for y in rows:
        t = (y - 196) / (cuff_y - 196)
        m = lerp(m_top, m_bottom, t) + flare * t * t
        fr.append((S.af(y) - m, y)); bk.append((S.ab(y) + m * 0.8, y))
    top = (S.af(186) + S.ab(186)) / 2
    cap = [(fr[0][0] + 1, 188), (top - 6, 176), (top + 6, 175), (bk[0][0] - 1, 186)]
    m_end = m_bottom + flare
    cuff_f = (S.af(cuff_y - 4) - m_end - 1, cuff_y + flare * 0.15)
    cuff_b = (S.ab(cuff_y - 4) + m_end * 0.8 + 1, cuff_y - 2)
    d = shape(cap + bk[1:] + [cuff_b], [cuff_f] + fr[::-1][:-1])
    sh = shape([(x - 5, y) for x, y in bk[1:]] + [(cuff_b[0] - 5, cuff_b[1])], [cuff_b] + bk[1:][::-1])
    return d, sh, cuff_b[1] + 1


def collar(S, y0, y1, m=1.6, lift=0):
    """Cổ đứng: dải bao quanh cổ từ y0 tới y1."""
    return shape([(S.f(y0) - m, y0), (S.b(y0) + m, y0 - lift)], [(S.b(y1) + m + 0.5, y1 - 2 - lift), (S.f(y1) - m - 0.5, y1 + 1)])


def svg_doc(gid: str, note: str, body: str, defs: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n  <!-- {note} Sinh bằng tools/gen_garment_views.py. -->\n'
            + (f"  <defs>{defs}</defs>\n" if defs else "")
            + f'  <g id="{gid}" {G}>\n{body}\n  </g>\n</svg>\n')


def el(id_, d, fill, extra=""):
    return f'    <path id="{id_}" d="{d}" fill="{fill}"{(" " + extra) if extra else ""}/>'


# ---------------------------------------------------------------- áo, hướng trái
def ao_dai(S, g):
    nu = g == "nu"
    slit, hem = (392, 738) if nu else (398, 612)
    fr = front_edge(S, ys(168, slit), 2 if nu else 3, ease=None if nu else 0.4)
    bk = back_edge(S, ys(168, slit), 2 if nu else 3, ease=None if nu else 0.4)
    upper = shape([(S.f(168) - 1, 168), (S.b(166) + 1.5, 164)] + bk[2:] + [(bk[-1][0] + 1, slit + 8)],
                  [(fr[-1][0] - 1, slit + 8)] + fr[::-1][:-2])
    fx, bx = S.f(414) - 3, S.b(414) + 3
    ta_truoc = shape([(fr[-1][0] - 1, slit), (S.f(slit + 22) - 3, slit + 22), (fx - 2, slit + 90), (fx - 4, hem)],
                     [(fx + 24, hem + 2), (fx + 26, slit + 6)])
    ta_sau = shape([(bx - 30, slit + 6), (bx - 28, hem + 2)],
                   [(bx + 3, hem), (bx + 1, slit + 90), (bx, 414), (S.b(slit) + 2, slit)])
    sl, sl_sh, cuff = sleeve(S, 2.4, 2.6, 432)
    body = "\n".join([
        el("ta_sau", ta_sau, "#FF0000"),
        el("ta_truoc", ta_truoc, "#FF0000"),
        el("than_ao", upper, "#FF0000"),
        f'    <path id="bong_than" d="M{bx - 8:.1f} {slit + 10} L{bx - 7:.1f} {hem} L{bx + 3:.1f} {hem} L{bx + 1:.1f} {slit + 10} Z '
        f'M{fx + 16:.1f} {slit + 10} L{fx + 16:.1f} {hem + 1} L{fx + 24:.1f} {hem + 2} L{fx + 26:.1f} {slit + 10} Z" {SHADE}/>',
        f'    <path id="nep_ta" d="M{fx + 8:.1f} {slit + 30} Q{fx + 6:.1f} {(slit + hem) / 2:.0f} {fx + 6:.1f} {hem - 4} '
        f'M{bx - 14:.1f} {slit + 30} Q{bx - 12:.1f} {(slit + hem) / 2:.0f} {bx - 13:.1f} {hem - 4}" {FOLD}/>',
        el("co_ao", collar(S, 143 if nu else 140, 166 if nu else 163), "#00FF00"),
        el("tay_ao", sl, "#FF0000"),
        f'    <path id="bong_tay" d="{sl_sh}" {SHADE}/>',
        f'    <path id="vien_co_tay" d="M{S.af(426) - 3.5:.1f} {cuff - 7} L{S.ab(426) + 3:.1f} {cuff - 9}" fill="none" stroke-opacity="0.35"/>',
        "    " + S.hand(cuff, f"ao_dai_{g}"),
    ])
    note = (f"Áo dài {'nữ' if nu else 'nam'} – hướng TRÁI. Cổ đứng, thân ôm theo mép người (nới {'2' if nu else '3'}), "
            f"xẻ tà từ y={slit}: thấy tà trước, tà sau và quần lộ ở khe xẻ; tà dài tới y={hem}.")
    return svg_doc(f"ao_dai_{g}_trai", note, body), closure(S, f"ao_dai_{g}", 166 if nu else 163, 3, "#FFFFFF" if nu else "#D9B44A")


def closure(S, name, y0, n, button):
    """Đường cài khuy chéo từ cổ xuống nách bên phải người mặc: chỉ thấy ở hướng PHẢI (toạ độ đã lật)."""
    x0 = S.f(y0 + 4) + 3
    x1, y1 = S.af(222) - 4, 222
    d = f"M{x0:.1f} {y0 + 2} Q{x0 + 2:.1f} {y0 + 30} {x1:.1f} {y1}"
    pts = [(lerp(x0, x1, t) - 3 * t * (1 - t), lerp(y0 + 6, y1 - 6, t)) for t in [i / (n - 1) for i in range(n)]] if n > 1 else []
    btn = "".join(f'<circle cx="{400 - x:.1f}" cy="{y:.1f}" r="2.4"/>' for x, y in pts)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n'
            f'  <!-- Chi tiết riêng hướng PHẢI của {name}: đường cài khuy chéo bên phải người mặc. Toạ độ hướng phải. '
            'Sinh bằng tools/gen_garment_views.py. -->\n'
            f'  <g id="{name}_khuy_phai" stroke="#000" stroke-linecap="round">\n'
            f'    <path d="{mirror_d(d)}" fill="none" stroke-opacity="0.35" stroke-width="1.3"/>\n'
            f'    <g fill="{button}" stroke-opacity="0.3" stroke-width="0.8">{btn}</g>\n  </g>\n</svg>\n')


def ngu_than(S, g):
    nu = g == "nu"
    hem = 650 if nu else 624
    top = ys(168, 414)
    fr = front_edge(S, top, 3, ease=0.25)
    bk = back_edge(S, top, 3, ease=0.3)
    fh, bh = (fr[-1][0] - 10, hem), (bk[-1][0] + 12, hem - 2)
    d = shape([(S.f(168) - 1, 168), (S.b(164) + 1.5, 162)] + bk[2:] + [(lerp(bk[-1][0], bh[0], 0.5), (414 + hem) / 2), bh],
              [(fh[0] + 8, hem + 4), fh, (lerp(fr[-1][0], fh[0], 0.5), (414 + hem) / 2)] + fr[::-1][:-2])
    sl, sl_sh, cuff = sleeve(S, 3.5, 4.5, 432, flare=2)
    mid = (fr[-1][0] + bk[-1][0]) / 2
    body = "\n".join([
        el("than_ao", d, "#FF0000"),
        f'    <path id="bong_than" d="M{bk[-1][0] - 8:.1f} 414 L{bh[0] - 10:.1f} {hem - 2} L{bh[0]:.1f} {hem - 2} L{bk[-1][0]:.1f} 414 Z" {SHADE}/>',
        f'    <path id="nep_than" d="M{mid - 14:.1f} 440 Q{mid - 18:.1f} 540 {mid - 22:.1f} {hem - 4} M{mid + 10:.1f} 450 Q{mid + 14:.1f} 550 {mid + 16:.1f} {hem - 4}" {FOLD}/>',
        el("co_dung", collar(S, 144 if nu else 138, 166 if nu else 162), "#00FF00"),
        el("tay_ao", sl, "#FF0000"),
        f'    <path id="bong_tay" d="{sl_sh}" {SHADE}/>',
        f'    <path id="nep_khuyu" d="M{S.af(312) - 4:.1f} 312 Q{(S.af(312) + S.ab(312)) / 2:.1f} 320 {S.ab(312) + 3:.1f} 314" {FOLD}/>',
        (f'    <path id="co_tay" d="M{S.af(426) - 6:.1f} {cuff - 10} L{S.ab(426) + 5:.1f} {cuff - 12} L{S.ab(426) + 5:.1f} {cuff - 2} '
         f'L{S.af(426) - 6.5:.1f} {cuff} Z" fill="#00FF00"/>' if nu else ""),
        "    " + S.hand(cuff, f"ngu_than_{g}"),
    ])
    note = f"Áo ngũ thân {'nữ' if g == 'nu' else 'nam'} – hướng TRÁI. Cổ đứng, thân suông rủ từ ngực, loe dần tới gấu y={hem}, tay dài hơi rộng."
    return svg_doc(f"ao_ngu_than_{g}_trai", note, body), closure(S, f"ao_ngu_than_{g}", 166 if nu else 162, 4, "#D9B44A")


def tu_than(S, g="nu"):
    top = ys(168, 336)
    fr = front_edge(S, top, 3, ease=0.35)
    bk = back_edge(S, top, 3)
    jacket = shape([(S.f(168) - 1, 168), (S.b(166) + 1.5, 164)] + bk[2:] + [(bk[-1][0], 340)], [(fr[-1][0] + 2, 340)] + fr[::-1][:-2])
    yem = shape([(S.f(170) + 1, 170)] + [(x + 1, y) for x, y in fr[2:-3]] + [(fr[-3][0] + 2, 322)],
                [(fr[-3][0] + 12, 322)] + [(x + 11 + 3 * ((y - 170) / 150), y) for x, y in fr[2:-3][::-1]] + [(S.f(172) + 9, 172)])
    bw = S.b(340) + 3
    than_sau = shape([(bw - 30, 338), (bw, 338), (S.b(414) + 4, 414), (S.b(414) + 9, 560), (S.b(414) + 12, 702)],
                     [(bw - 22, 706), (bw - 28, 520)])
    knot_x = fr[-1][0] + 1
    body = "\n".join([
        el("than_sau", than_sau, "#FF0000"),
        f'    <path id="bong_than_sau" d="M{bw - 30:.1f} 340 L{bw - 22:.1f} 340 L{bw - 14:.1f} 704 L{bw - 22:.1f} 706 Z" {SHADE}/>',
        el("than_ao", jacket, "#FF0000"),
        el("yem", yem, "#00FF00"),
        f'    <path id="nep_co" d="{smooth([(x + 12 + 3 * ((y - 170) / 150), y) for x, y in fr[2:-3]])}" fill="none" stroke="#000" stroke-opacity="0.16" stroke-width="5"/>',
        f'    <path id="that_lung" d="M{fr[-2][0]:.1f} 316 L{bk[-2][0] + 1:.1f} 316 L{bk[-1][0] + 1:.1f} 331 L{fr[-1][0]:.1f} 331 Z" fill="#FF00FF"/>',
        el("duoi_vat", f"M{knot_x + 2:.1f} 330 C{knot_x - 2:.1f} 400 {knot_x - 6:.1f} 480 {knot_x - 9:.1f} 560 "
           f"L{knot_x + 6:.1f} 566 C{knot_x + 8:.1f} 480 {knot_x + 11:.1f} 400 {knot_x + 14:.1f} 332 Z", "#FF0000"),
        el("dai_that_lung", f"M{knot_x + 4:.1f} 334 L{knot_x + 1:.1f} 410 L{knot_x + 7:.1f} 412 L{knot_x + 10:.1f} 336 Z", "#FF00FF"),
        f'    <ellipse id="nut_buoc" cx="{knot_x + 4:.1f}" cy="327" rx="7" ry="7" fill="#FF0000"/>',
    ])
    sl, sl_sh, cuff = sleeve(S, 3, 3.5, 432)
    body += "\n" + "\n".join([el("tay_ao", sl, "#FF0000"), f'    <path id="bong_tay" d="{sl_sh}" {SHADE}/>',
                              f'    <path id="nep_khuyu" d="M{S.af(312) - 3:.1f} 312 Q{(S.af(312) + S.ab(312)) / 2:.1f} 320 {S.ab(312) + 3:.1f} 314" {FOLD}/>',
                              "    " + S.hand(cuff, "tu_than_nu")])
    note = ("Áo tứ thân nữ – hướng TRÁI. Áo ngoài mở trước, thấy dải yếm ở mép ngực; thắt lưng buộc trước bụng, "
            "đuôi vạt thả xuống trước váy; thân sau dài tới y=702 rủ sau lưng.")
    return svg_doc("ao_tu_than_nu_trai", note, body), None


def nhat_binh(S, g="nu"):
    hem = 690
    top = ys(168, 414)
    fr = front_edge(S, top, 3, ease=0.2)
    bk = back_edge(S, top, 3, ease=0.25)
    fh, bh = (fr[-1][0] - 14, hem), (bk[-1][0] + 16, hem - 2)
    d = shape([(S.f(168) - 1, 168), (S.b(164) + 1.5, 162)] + bk[2:] + [(lerp(bk[-1][0], bh[0], 0.5), 550), bh],
              [(fh[0] + 10, hem + 5), fh, (lerp(fr[-1][0], fh[0], 0.5), 550)] + fr[::-1][:-2])
    band_f = shape([(x, y) for x, y in fr[1:18]], [(x + 15, y) for x, y in fr[1:18][::-1]])
    band_b = shape([(x - 15, y) for x, y in bk[1:18]], [(x, y) for x, y in bk[1:18][::-1]])
    sl, sl_sh, cuff = sleeve(S, 4, 6, 437, flare=26)
    dots = [(fr[-1][0] + 12, 380), (fr[-1][0] + 8, 470), (fr[-1][0] - 2, 560), (fr[-1][0] - 6, 640),
            (bk[-1][0] - 10, 470), (bk[-1][0] - 4, 580), (bk[-1][0] + 4, 660), ((fr[-1][0] + bk[-1][0]) / 2, 610)]
    body = "\n".join([
        f'    <path id="co_ao_trong" d="{collar(S, 140, 164, m=1.2)}" fill="#F5F0E1"/>',
        el("than_ao", d, "#FF0000"),
        f'    <path id="bong_than" d="M{bk[-1][0] - 8:.1f} 414 L{bh[0] - 12:.1f} {hem - 2} L{bh[0]:.1f} {hem - 2} L{bk[-1][0]:.1f} 414 Z" {SHADE}/>',
        '    <g id="hoa_van_tron" fill="#D9B44A" fill-opacity="0.75" stroke="#8A6A1E" stroke-opacity="0.5" stroke-width="0.8">'
        + "".join(f'<circle cx="{x:.1f}" cy="{y}" r="6"/>' for x, y in dots) + "</g>",
        el("dai_co_truoc", band_f, "#00FF00"),
        el("dai_co_sau", band_b, "#00FF00"),
        '    <g id="hoa_van_dai_co" fill="none" stroke="#D9B44A" stroke-opacity="0.9" stroke-width="1.4"><path d="'
        + " ".join(f"M{fr[i][0] + 4:.1f} {fr[i][1]:.0f} q3 -4 6 0" for i in range(3, 17, 3))
        + " " + " ".join(f"M{bk[i][0] - 11:.1f} {bk[i][1]:.0f} q3 -4 6 0" for i in range(3, 17, 3)) + '"/></g>',
        el("tay_ao", sl, "#FF0000"),
        f'    <path id="bong_tay" d="{sl_sh}" {SHADE}/>',
        f'    <path id="nep_tay" d="M{S.af(300) - 6:.1f} 300 Q{S.af(380) - 12:.1f} 380 {S.af(420) - 18:.1f} 426 '
        f'M{S.ab(320) + 2:.1f} 330 Q{S.ab(390) + 8:.1f} 390 {S.ab(420) + 12:.1f} 428" {FOLD}/>',
        '    <g fill="#D9B44A" fill-opacity="0.75" stroke="#8A6A1E" stroke-opacity="0.5" stroke-width="0.8">'
        f'<circle cx="{(S.af(300) + S.ab(300)) / 2:.1f}" cy="300" r="5"/><circle cx="{(S.af(390) + S.ab(390)) / 2:.1f}" cy="392" r="5"/></g>',
        "    " + S.hand(cuff, "nhat_binh_nu"),
    ])
    note = ("Áo nhật bình nữ – hướng TRÁI. Thân suông dài tới y=690, dải cổ bản rộng thấy ở mép ngực và mép lưng, "
            "tay áo rộng loe xuống gấu; hoa văn tròn giản lược.")
    return svg_doc("nhat_binh_nu_trai", note, body), None


def ba_ba(S, g):
    nu = g == "nu"
    slit, hem = (392, 440) if nu else (418, 456)
    top = ys(176, slit)
    fr = front_edge(S, top, 2.5, ease=0.3)
    bk = back_edge(S, ys(166, slit), 2.5, ease=0.35)
    upper = shape([fr[0], (S.f(176) + 14, 171), (S.b(162) + 1.5, 160)] + bk[2:] + [(bk[-1][0], slit + 6)],
                  [(fr[-1][0], slit + 6)] + fr[::-1][:-1])
    fx, bx = fr[-1][0], bk[-1][0]
    mid = (fx + bx) / 2
    vat_truoc = shape([(fx, slit - 2), (fx - 2, hem)], [(mid - 2, hem + 2), (mid - 3, slit)])
    vat_sau = shape([(mid + 3, slit), (mid + 2, hem + 2)], [(bx + 3, hem), (S.b(slit) + 2.5, slit - 2)])
    sl, sl_sh, cuff = sleeve(S, 2.6, 3, 432)
    body = "\n".join([
        el("vat_sau", vat_sau, "#FF0000"),
        el("vat_truoc", vat_truoc, "#FF0000"),
        el("than_ao", upper, "#FF0000"),
        f'    <path id="xe_ta" d="M{mid - 3:.1f} {slit} L{mid + 3:.1f} {slit}" fill="none" stroke-opacity="0.45"/>',
        f'    <path id="tui" d="M{fx + 4:.1f} {slit + 2} L{fx + 20:.1f} {slit + 2} L{fx + 20:.1f} {hem - 12} Q{fx + 12:.1f} {hem - 8} {fx + 3:.1f} {hem - 12} Z" fill="none" stroke-opacity="0.4"/>',
        f'    <path id="nep_ao" d="M{fx + 8:.1f} 330 Q{fx + 10:.1f} 360 {fx + 8:.1f} 388" {FOLD}/>',
        el("tay_ao", sl, "#FF0000"),
        f'    <path id="bong_tay" d="{sl_sh}" {SHADE}/>',
        "    " + S.hand(cuff, f"ba_ba_{g}"),
    ])
    note = f"Áo bà ba {'nữ' if nu else 'nam'} – hướng TRÁI. Cổ tròn không bâu, xẻ hai bên từ y={slit} (lộ quần ở khe xẻ), dài tới y={hem}, tay raglan dài."
    return svg_doc(f"ao_ba_ba_{g}_trai", note, body), None


# ---------------------------------------------------------------- quần, váy, hướng trái
def quan(S, g):
    waist = 316
    up = ys(waist, 470, 10)
    ease = lambda y: 1.2 if y <= 414 else lerp(1.2, 3.5, (y - 414) / 56)     # ôm sát dưới áo, không lộ mép quần ở eo
    fr = front_edge(S, up, ease)
    bk = back_edge(S, up, ease)
    d = shape(fr + [(S.f(748) - 13, 752)], [(S.b(748) + 14, 752)] + bk[::-1])
    body = "\n".join([
        el("vai_quan", d, "#0000FF"),
        f'    <path id="bong" d="M{bk[-1][0] - 7:.1f} 470 L{S.b(748) + 7:.1f} 752 L{S.b(748) + 14:.1f} 752 L{bk[-1][0]:.1f} 470 Z" {SHADE}/>',
        f'    <path id="nep" d="M{fr[0][0] + 2:.1f} 330 L{bk[0][0] - 1:.1f} 330 M{S.f(540) + 6:.1f} 480 L{S.f(748) - 2:.1f} 748" '
        'fill="none" stroke="#000" stroke-opacity="0.18" stroke-width="1.4"/>',
        "    " + S.hand(waist - 2, f"quan_{g}"),
    ])
    return svg_doc(f"quan_{g}_trai", f"Quần {'nữ' if g == 'nu' else 'nam'} ống suông – hướng TRÁI. Cạp ở eo y={waist}, gấu ở mắt cá y=752; vẽ lại tay gần nằm trên quần.", body)


def vay(S, g="nu"):
    waist = 314
    up = ys(waist, 430, 10)
    fr = front_edge(S, up, 3)
    bk = back_edge(S, up, 3.5)
    d = shape(fr + [(fr[-1][0] - 6, 600), (fr[-1][0] - 12, 754)], [(bk[-1][0] + 14, 754), (bk[-1][0] + 7, 600)] + bk[::-1])
    body = "\n".join([
        el("vai_vay", d, "#0000FF"),
        f'    <path id="bong" d="M{bk[-1][0] - 6:.1f} 430 L{bk[-1][0] + 6:.1f} 754 L{bk[-1][0] + 14:.1f} 754 L{bk[-1][0]:.1f} 430 Z" {SHADE}/>',
        f'    <path id="nep_vay" d="M{fr[-1][0] + 14:.1f} 440 L{fr[-1][0] + 6:.1f} 752 M{(fr[-1][0] + bk[-1][0]) / 2:.1f} 440 L{(fr[-1][0] + bk[-1][0]) / 2 + 2:.1f} 754" {FOLD}/>',
        "    " + S.hand(waist - 2, "vay_nu"),
    ])
    return svg_doc("vay_nu_trai", f"Váy dài nữ – hướng TRÁI. Cạp ở eo y={waist}, loe nhẹ tới gấu y=754; vẽ lại tay gần nằm trên váy.", body)


# ---------------------------------------------------------------- phụ kiện
ACC = {
    "guoc_trai": ("Guốc gỗ – hướng TRÁI: một đế dưới bàn chân (mũi quay sang trái), quai vắt qua mu bàn chân.",
                  '    <rect id="de" x="147" y="779" width="70" height="11" rx="4.5" fill="#9A6A3A"/>\n'
                  '    <path id="quai" d="M163 780 C163 771 168 764 178 760" fill="none" stroke="#7A2E22" stroke-width="5"/>'),
    "guoc_sau": ("Guốc gỗ – hướng SAU: thấy gót hai đế, quai khuất phía trước bàn chân.",
                 '    <rect id="de_trai" x="164" y="779" width="32" height="11" rx="4.5" fill="#9A6A3A"/>\n'
                 '    <rect id="de_phai" x="204" y="779" width="32" height="11" rx="4.5" fill="#9A6A3A"/>\n'
                 '    <path id="mep_quai" d="M166 776 L170 772 M234 776 L230 772" fill="none" stroke="#7A2E22" stroke-width="4"/>'),
    "khan_van_trai": ("Khăn vấn – hướng TRÁI: vành khăn ôm đầu, mép trước nằm trên lông mày, mép sau phủ gáy trên búi tóc.",
                      '    <path id="vanh_khan" d="M163 76 C155 50 172 26 204 24 C236 24 256 46 252 80 C251 92 246 100 239 104 '
                      'C232 98 229 90 224 84 C212 72 194 68 178 72 C172 74 168 80 163 76 Z" fill="#FF00FF"/>\n'
                      '    <path id="lop_quan" d="M166 66 C186 46 226 42 248 70 M172 72 C192 56 222 56 244 88 M168 50 C192 54 226 64 240 96" '
                      'fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="1.6"/>\n'
                      '    <path id="sang_khan" d="M180 36 C194 29 214 29 228 35" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="3.5"/>'),
    "khan_van_sau": ("Khăn vấn – hướng SAU: vành khăn phủ đỉnh và sau đầu, mép dưới ngang trên búi tóc.",
                     '    <path id="vanh_khan" d="M158 88 C152 50 172 26 200 26 C228 26 248 50 242 88 C232 98 216 102 200 102 '
                     'C184 102 168 98 158 88 Z" fill="#FF00FF"/>\n'
                     '    <path id="lop_quan" d="M160 74 C180 86 220 86 240 74 M164 58 C184 70 216 70 236 58 M176 40 C190 50 210 50 224 40" '
                     'fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="1.6"/>\n'
                     '    <path id="sang_khan" d="M178 38 C190 32 210 32 222 38" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="3.5"/>'),
}


# ---------------------------------------------------------------- hướng sau: dựng từ hướng trước
def strip(svg: str, ids) -> str:
    for i in ids:
        svg = re.sub(rf'\s*<g id="{i}"[^>]*>.*?</g>', "", svg, flags=re.S)
        svg = re.sub(rf'\s*<(path|ellipse|circle|rect) id="{i}"[^>]*/>', "", svg, flags=re.S)
    return svg


def seam(y0, y1):
    return f'\n    <path id="duong_song_lung" d="M200 {y0} L200 {y1}" fill="none" stroke-opacity="0.28"/>'


BACK = {
    "garment/ao_dai_nu": dict(drop=["duong_cai_khuy", "khuy", "nep_nguc_eo"],
                              add='\n    <path id="nep_lung" d="M184 262 Q186 300 188 328 M216 262 Q214 300 212 328" fill="none" stroke="#000" stroke-opacity="0.18" stroke-width="1.1"/>'),
    "garment/ao_dai_nam": dict(drop=["duong_cai_khuy", "khuy"], add=seam(166, 400)),
    "garment/ao_ngu_than_nu": dict(drop=["vat_truoc", "khuy"], add=seam(168, 650)),
    "garment/ao_ngu_than_nam": dict(drop=["vat_truoc", "khuy"], add=seam(164, 626)),
    "garment/ao_ba_ba_nu": dict(drop=["duong_cai", "khuy", "tui"], sub=[("Q200 186 220 169", "Q200 174 220 169")]),
    "garment/ao_ba_ba_nam": dict(drop=["duong_cai", "khuy", "tui"], sub=[("Q200 182 222 164", "Q200 170 222 164")]),
    "garment/ao_tu_than_nu": dict(
        drop=["yem", "vat_truoc_trai", "vat_truoc_phai", "nep_co", "bong_vat", "duoi_vat_trai", "duoi_vat_phai",
              "bong_duoi_vat", "dai_that_lung", "nut_buoc", "nep_nut"],
        sub=[(r'(<path id="than_sau" d=")[^"]+', r"\1M151 174 C168 167 186 164 200 164 C214 164 232 167 249 174 L242 224 "
              r"C243 300 247 360 251 400 L257 702 Q200 710 143 702 L149 400 C154 360 157 300 158 224 Z"),
             (r'(\s*<path id="that_lung")', seam(166, 706) + r"\1")]),
    "garment/nhat_binh_nu": dict(drop=["hoa_tron_nguc"],
                                 sub=[(" M185 172 Q200 168 215 172 L206 262 L194 262 Z", ""), (' fill-rule="evenodd"', ""),
                                      ("M180 280 L220 280", "M178 296 L222 296")]),
    "bottom/quan_nu": dict(), "bottom/quan_nam": dict(), "bottom/vay_nu": dict(),
}


def back_view(rel: str, spec: dict) -> str:
    svg = (FIG / f"{rel}.svg").read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->", "", svg, count=1, flags=re.S)
    svg = strip(svg, spec.get("drop", []))
    for a, b in spec.get("sub", []):
        svg = re.sub(a, b, svg) if a.startswith(("(", "\\")) else svg.replace(a, b)
    name = rel.split("/")[1]
    svg = re.sub(r'<g id="' + name + '"', f'<g id="{name}_sau"', svg, count=1)
    if spec.get("add"):
        svg = svg.replace("\n  </g>\n</svg>", spec["add"] + "\n  </g>\n</svg>")
    note = (f"  <!-- {name} – hướng SAU. Dựng từ bản hướng trước (cùng đường bao), bỏ chi tiết chỉ có ở mặt trước. "
            "Sinh bằng tools/gen_garment_views.py. -->")
    return svg.replace('viewBox="0 0 400 800">', 'viewBox="0 0 400 800">\n' + note, 1)


# ---------------------------------------------------------------- chạy
def main():
    out = {}
    for g in ("nu", "nam"):
        S = Side(g)
        makers = [ao_dai, ngu_than, ba_ba] + ([tu_than, nhat_binh] if g == "nu" else [])
        for mk in makers:
            svg, extra = mk(S, g)
            name = re.search(r'<g id="(\w+)_trai"', svg).group(1)
            out[f"garment/{name}_trai"] = svg
            if extra:
                out[f"garment/{name}_phai_them"] = extra
        out[f"bottom/quan_{g}_trai"] = quan(S, g)
        if g == "nu":
            out["bottom/vay_nu_trai"] = vay(S)
    for rel, spec in BACK.items():
        out[f"{rel}_sau"] = back_view(rel, spec)
    for key, (note, body) in ACC.items():
        out[f"accessory/{key}"] = svg_doc(key, note, body)
    for rel, svg in out.items():
        p = FIG / f"{rel}.svg"
        p.write_text(svg, encoding="utf-8")
        print("Đã tạo", p.relative_to(FIG))
    subprocess.run([sys.executable, str(Path(__file__).with_name("mirror_views.py"))], check=True)


if __name__ == "__main__":
    main()

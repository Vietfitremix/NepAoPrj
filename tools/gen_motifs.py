"""Sinh hoạ tiết ĐẶT VỊ TRÍ (vẽ / thêu theo bố cục) cho thân áo: frontend/src/assets/figure/motif/{id}.svg

Khác hoạ tiết in đều (lặp ô vuông khắp áo), mỗi mẫu ở đây là một bố cục: cụm điểm nhấn ở ngực/vai và cụm ở tà dưới,
chừa khoảng trống ở giữa, giống áo dài vẽ tay/thêu tay ("trải dọc thân áo, điểm nhấn ở ngực, eo hoặc tà").
Khung vẽ rộng 100 đơn vị, căn giữa thân áo, phủ ~1,6 lần bề ngang thân (MOTIF_SPAN = 62 trong playground):
  <g data-anchor="top">     y = 0 là mép trên thân áo (vai), vẽ xuống dưới
  <g data-anchor="bottom">  y = 0 là gấu áo, vẽ lên trên (y âm)
Trình duyệt co giãn khung theo khung bao thân áo của từng kiểu áo, từng góc nhìn, rồi cắt gọn trong thân áo.
Hình tự vẽ giản lược, không đồ lại ảnh tham khảo. Chạy: python tools/gen_motifs.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "frontend/src/assets/figure/motif"
BROWN, GOLD, GOLD_D, CREAM = "#3A2418", "#E6B54A", "#8A4B12", "#FFF6E0"


def f(v):
    return f"{v:.1f}"


def blossom(cx, cy, r, petal="#F4A6B8", center="#C8395A", rot=0):
    """Hoa 5 cánh (đào, mai) nhìn thẳng."""
    out = []
    for i in range(5):
        a = math.radians(rot + i * 72 - 90)
        px, py = cx + r * 0.55 * math.cos(a), cy + r * 0.55 * math.sin(a)
        out.append(f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(r * 0.5)}" ry="{f(r * 0.42)}" '
                   f'transform="rotate({f(math.degrees(a) + 90)} {f(px)} {f(py)})"/>')
    dots = "".join(f'<circle cx="{f(cx + r * 0.22 * math.cos(math.radians(i * 72)))}" cy="{f(cy + r * 0.22 * math.sin(math.radians(i * 72)))}" r="{f(r * 0.07)}"/>' for i in range(5))
    return (f'<g fill="{petal}" stroke="#000" stroke-opacity="0.18" stroke-width="0.5">{"".join(out)}</g>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * 0.18)}" fill="{center}"/><g fill="#E8B830">{dots}</g>')


def bud(cx, cy, r, color="#E98BA2"):
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(r * 0.45)}" ry="{f(r * 0.65)}" fill="{color}" stroke="#000" stroke-opacity="0.15" stroke-width="0.5"/>'


def petal_fall(cx, cy, r, rot, color="#F4A6B8"):
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(r * 0.5)}" ry="{f(r * 0.3)}" fill="{color}" transform="rotate({rot} {f(cx)} {f(cy)})"/>'


def branch(d, w, color=BROWN):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'


def doc(name, note, top, bottom):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -300 100 600">\n'
            f'  <!-- Hoạ tiết đặt vị trí: {name}. {note} Khung rộng 100 = bề ngang thân áo. Sinh bằng tools/gen_motifs.py. -->\n'
            f'  <g data-anchor="top">{top}</g>\n  <g data-anchor="bottom">{bottom}</g>\n</svg>\n')


# ---------------------------------------------------------------- 1. Cành đào xuân
def canh_dao():
    trunk = (branch("M6 4 C12 -30 8 -70 22 -110 C32 -138 36 -162 54 -196 C60 -208 66 -216 74 -226", 4.2) +
             branch("M20 -96 C32 -100 44 -96 60 -112 C66 -118 72 -120 80 -122", 2.4) +
             branch("M30 -138 C22 -156 18 -174 22 -196", 2) +
             branch("M46 -176 C56 -182 66 -178 76 -190", 1.8) +
             branch("M12 -52 C22 -56 30 -54 38 -62", 1.8))
    flowers = [(74, -228, 9, "#F4A6B8"), (80, -122, 8, "#FFFFFF"), (60, -112, 7, "#F4A6B8"), (22, -198, 8, "#FFFFFF"),
               (76, -190, 7.5, "#F4A6B8"), (38, -63, 7, "#FFFFFF"), (44, -96, 6, "#F4A6B8"), (54, -196, 6.5, "#FFFFFF"),
               (30, -140, 6, "#F4A6B8"), (16, -80, 5.5, "#F4A6B8"), (64, -212, 5, "#FFFFFF")]
    bot = trunk + "".join(blossom(x, y, r, p, rot=x * 7) for x, y, r, p in flowers)
    bot += bud(70, -104, 4) + bud(26, -178, 4) + bud(84, -200, 3.5) + bud(10, -36, 3.5)
    bot += "".join(petal_fall(x, y, 5, rot) for x, y, rot in [(86, -250, 30), (60, -262, -20), (90, -150, 60), (50, -140, 10)])
    top = (branch("M2 34 C12 30 20 28 30 18 M14 30 C16 22 20 18 24 14", 1.8) +
           blossom(30, 18, 7, "#FFFFFF") + blossom(16, 30, 6, "#F4A6B8") + bud(24, 12, 3.5) +
           "".join(petal_fall(x, y, 4.5, rot) for x, y, rot in [(40, 44, 20), (34, 62, -30), (46, 80, 50)]))
    return doc("cành đào xuân", "Cành đào mọc từ gấu tà lên quá hông, một nhành nhỏ ở vai trái, cánh hoa rơi.", top, bot)


# ---------------------------------------------------------------- 2. Phượng hoàng
def feather(cx, cy, length, angle, width=7, fill=GOLD):
    a = math.radians(angle)
    ex, ey = cx + length * math.cos(a), cy + length * math.sin(a)
    nx, ny = -math.sin(a) * width, math.cos(a) * width
    mx, my = (cx + ex) / 2, (cy + ey) / 2
    return (f'<path d="M{f(cx)} {f(cy)} Q{f(mx + nx)} {f(my + ny)} {f(ex)} {f(ey)} Q{f(mx - nx * 0.4)} {f(my - ny * 0.4)} {f(cx)} {f(cy)} Z" '
            f'fill="{fill}" stroke="{GOLD_D}" stroke-width="0.7"/>')


def phuong():
    wings = "".join(feather(50, 46, 20 + i * 5, 200 + i * 12, 6) for i in range(6))           # cánh trái xoè lên
    wings += "".join(feather(52, 46, 20 + i * 5, -20 - i * 12, 6) for i in range(6))           # cánh phải
    wings += "".join(feather(50, 48, 14 + i * 3, 196 + i * 12, 4, CREAM) for i in range(5))
    wings += "".join(feather(52, 48, 14 + i * 3, -16 - i * 12, 4, CREAM) for i in range(5))
    body = (f'<path d="M50 40 C44 50 44 66 50 78 C56 66 58 50 52 40 Z" fill="{GOLD}" stroke="{GOLD_D}" stroke-width="0.8"/>'
            f'<path d="M51 42 C50 32 54 24 60 20 C64 18 68 20 68 24 C64 24 60 26 58 32 C56 36 54 40 53 44 Z" fill="{GOLD}" stroke="{GOLD_D}" stroke-width="0.8"/>'
            f'<path d="M67 22 L74 24 L67 26 Z" fill="{GOLD_D}"/><circle cx="64" cy="22" r="1.1" fill="#3A1A0A"/>'
            f'<path d="M60 19 C58 12 62 8 66 6 M62 18 C62 12 66 10 70 10 M58 20 C54 14 54 10 56 6" fill="none" stroke="{GOLD_D}" stroke-width="1.2"/>'
            f'<g fill="#C0392B">' + "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="1.4"/>' for x, y in [(50, 54), (51, 62), (50, 70)]) + "</g>")
    fringe = "".join(f'<path d="M{f(44 + i * 2.4)} 74 Q{f(42 + i * 2.6)} 86 {f(40 + i * 3)} 96" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round"/>' for i in range(6))
    tail = ""
    for k, (dx, w) in enumerate([(-10, 3.2), (0, 4.2), (12, 3.2)]):
        d = (f"M{50 + dx * 0.2} 80 C{30 + dx} 130 {72 + dx} 180 {48 + dx} 230 C{34 + dx} 262 {62 + dx} 292 {50 + dx} 330")
        tail += f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="{w}" stroke-linecap="round"/>'
        # lông nhỏ hai bên dải đuôi: điểm lấy mẫu dọc đường cong
        pts = [(50 + dx * 0.2, 80), (30 + dx, 130), (72 + dx, 180), (48 + dx, 230), (34 + dx, 262), (62 + dx, 292), (50 + dx, 330)]
        for t in [i / 14 for i in range(1, 14)]:
            seg = 0 if t < 0.5 else 1
            u = t * 2 if seg == 0 else t * 2 - 1
            p0, c1, c2, p3 = pts[seg * 3: seg * 3 + 4]
            x = (1-u)**3*p0[0] + 3*(1-u)**2*u*c1[0] + 3*(1-u)*u**2*c2[0] + u**3*p3[0]
            y = (1-u)**3*p0[1] + 3*(1-u)**2*u*c1[1] + 3*(1-u)*u**2*c2[1] + u**3*p3[1]
            side = 1 if int(t * 14) % 2 else -1
            tail += feather(x, y, 7 + 4 * t, 90 + side * 55, 2.4, GOLD if side > 0 else CREAM)
    eyes = "".join(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="4" ry="6" fill="#C0392B" stroke="{GOLD}" stroke-width="1.5"/>'
                   for x, y in [(38, 330), (50, 330), (62, 330), (44, 236), (60, 232)])
    clouds = "".join(f'<path d="M{x} {y} q4 -6 8 0 q4 -6 8 0" fill="none" stroke="{GOLD_D}" stroke-width="1.2"/>' for x, y in [(14, 120), (74, 150), (20, 200), (70, 270)])
    top = tail + eyes + clouds + wings + fringe + body
    bot = "".join(f'<path d="M{x} -10 q6 -10 12 0 q6 -10 12 0" fill="none" stroke="{GOLD}" stroke-width="2"/>' for x in (6, 40, 70))
    bot += f'<path d="M0 -4 L100 -4" stroke="{GOLD}" stroke-width="2.5"/>'
    return doc("phượng hoàng", "Phượng xoè cánh ở ngực, ba dải đuôi uốn dọc thân trước, vân mây; viền vàng ở gấu.", top, bot)


# ---------------------------------------------------------------- 3. Hạc và mai
def crane(x, y, s, flip=False, wings_up=False):
    sx = -s if flip else s
    g = (f'<path d="M-14 0 C-6 -6 8 -6 14 -2 C10 4 -4 6 -14 0 Z" fill="#FFFFFF" stroke="#7A7A7A" stroke-width="0.7"/>'
         f'<path d="M12 -3 C18 -10 22 -18 28 -20 C30 -21 31 -19 30 -18 C26 -16 22 -10 15 -1 Z" fill="#FFFFFF" stroke="#7A7A7A" stroke-width="0.6"/>'
         f'<circle cx="29" cy="-20" r="1.6" fill="#C0392B"/><path d="M30 -19 L37 -17 L30 -17.5 Z" fill="#555"/>'
         f'<path d="M-12 1 L-26 8 M-12 2 L-25 11" stroke="#555" stroke-width="0.9"/>')
    if wings_up:
        g += (f'<path d="M-2 -3 C-8 -20 -4 -34 4 -42 C6 -30 8 -18 6 -4 Z" fill="#FFFFFF" stroke="#7A7A7A" stroke-width="0.6"/>'
              f'<path d="M2 -3 C6 -22 16 -32 24 -36 C20 -24 14 -12 8 -2 Z" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="0.6"/>'
              f'<path d="M4 -42 L1 -36 M24 -36 L19 -31" stroke="#333" stroke-width="2"/>')
    else:
        g += (f'<path d="M-4 -2 C-14 -16 -30 -22 -40 -20 C-30 -12 -18 -4 -6 2 Z" fill="#FFFFFF" stroke="#7A7A7A" stroke-width="0.6"/>'
              f'<path d="M-40 -20 L-33 -16 M-36 -21 L-30 -15" stroke="#333" stroke-width="1.6"/>'
              f'<path d="M0 -3 C-2 -16 6 -28 16 -32 C14 -20 10 -10 4 -1 Z" fill="#F2F2F2" stroke="#7A7A7A" stroke-width="0.6"/>')
    return f'<g transform="translate({x} {y}) scale({f(sx)} {f(s)})">{g}</g>'


def hac_mai():
    twig = lambda d, w=1.3: branch(d, w, "#F3EDE4")
    plum = lambda x, y, r=3.4: blossom(x, y, r, "#FFFFFF", "#E8B830")
    top = (twig("M100 4 C86 14 76 22 66 40 C60 52 58 64 60 80 M76 24 C70 18 64 16 56 16 M66 42 C74 46 80 52 84 62", 1.5) +
           "".join(plum(x, y) for x, y in [(56, 16), (84, 62), (60, 80), (70, 32), (62, 56), (78, 50)]) +
           crane(40, 34, 1.0, flip=True))
    bot = (twig("M8 0 C12 -40 10 -80 22 -120 C28 -140 30 -160 40 -186 M16 -60 C26 -70 34 -72 44 -86 M20 -110 C12 -126 10 -140 12 -160 "
                "M30 -150 C40 -152 48 -160 52 -176", 1.6) +
           "".join(plum(x, y) for x, y in [(40, -186), (44, -86), (12, -160), (52, -176), (22, -130), (30, -100), (14, -40), (36, -168)]) +
           crane(70, -120, 1.35, wings_up=True))
    return doc("hạc và mai", "Hạc bay ở ngực cạnh nhành mai từ vai phải; nhành mai mọc từ gấu tà, hạc xoè cánh ở tà.", top, bot)


# ---------------------------------------------------------------- 4. Sen
def lotus(x, y, s, open_=True):
    if open_:
        pet = [(-26, 1.0, "#F7B6C8"), (26, 1.0, "#F7B6C8"), (-12, 1.1, "#F29AB4"), (12, 1.1, "#F29AB4"), (0, 1.2, "#EE86A4")]
    else:
        pet = [(-8, 1.0, "#F29AB4"), (8, 1.0, "#F29AB4"), (0, 1.15, "#EE86A4")]
    g = "".join(f'<path d="M0 0 C-6 -8 -5 -{f(18 * k)} 0 -{f(24 * k)} C5 -{f(18 * k)} 6 -8 0 0 Z" fill="{c}" '
                f'stroke="#B0506E" stroke-width="0.6" transform="rotate({a})"/>' for a, k, c in pet)
    if open_:
        g += '<ellipse cx="0" cy="-3" rx="5" ry="2.4" fill="#E8C35A" stroke="#B0506E" stroke-width="0.5"/>'
    return f'<g transform="translate({x} {y}) scale({s})">{g}</g>'


def leaf(x, y, rx, ry, rot):
    return (f'<g transform="translate({x} {y}) rotate({rot})"><ellipse rx="{rx}" ry="{ry}" fill="#5E8C4A" stroke="#3E6232" stroke-width="0.8"/>'
            f'<ellipse rx="{rx * 0.7}" ry="{ry * 0.62}" fill="#79A863" fill-opacity="0.6"/>'
            + "".join(f'<path d="M0 0 L{f(rx * math.cos(math.radians(a)))} {f(ry * math.sin(math.radians(a)))}" stroke="#3E6232" stroke-width="0.5"/>'
                      for a in range(0, 360, 45)) + "</g>")


def sen():
    stem = lambda d: branch(d, 1.8, "#4F7A3C")
    bot = (stem("M30 -20 C32 -70 26 -110 34 -150") + stem("M62 -24 C60 -60 66 -86 62 -112") + stem("M80 -18 C82 -60 78 -170 70 -210") +
           leaf(22, -22, 22, 9, -8) + leaf(70, -18, 26, 10, 6) + leaf(46, -48, 16, 7, -20) +
           lotus(34, -150, 1.25) + lotus(62, -112, 1.0) + lotus(70, -210, 0.9, open_=False))
    top = (stem("M22 92 C24 76 22 62 26 50") + lotus(26, 50, 0.9) + leaf(16, 96, 12, 5, -12) +
           "".join(f'<path d="M{x} {y} q3 -3 6 0" fill="none" stroke="#B0506E" stroke-width="0.8"/>' for x, y in [(40, 70), (44, 86)]))
    return doc("sen", "Hai bông sen nở và một búp sen vươn từ lá ở gấu tà; một bông nhỏ ở ngực trái.", top, bot)


# ---------------------------------------------------------------- 5. Hồi văn + mặt trống đồng
def key_band(y0, h, color=GOLD):
    """Dải hồi văn (chữ 回 nối tiếp)."""
    out = [f'<rect x="-4" y="{y0}" width="108" height="{h}" fill="#3B2A1A" fill-opacity="0.85"/>']
    u = h - 6
    for x in range(-4, 104, int(u) + 4):
        out.append(f'<path d="M{x} {y0 + h - 3} L{x} {y0 + 3} L{x + u} {y0 + 3} L{x + u} {y0 + h - 3} L{x + u * 0.3} {y0 + h - 3} '
                   f'L{x + u * 0.3} {y0 + h * 0.45} L{x + u * 0.65} {y0 + h * 0.45}" fill="none" stroke="{color}" stroke-width="1.6"/>')
    return "".join(out)


def drum(cx, cy, R):
    rays = "".join(f'<path d="M{f(cx + 3 * math.cos(math.radians(a - 8)))} {f(cy + 3 * math.sin(math.radians(a - 8)))} '
                   f'L{f(cx + R * 0.34 * math.cos(math.radians(a)))} {f(cy + R * 0.34 * math.sin(math.radians(a)))} '
                   f'L{f(cx + 3 * math.cos(math.radians(a + 8)))} {f(cy + 3 * math.sin(math.radians(a + 8)))} Z"/>' for a in range(0, 360, 30))
    birds = "".join(f'<path transform="rotate({a} {cx} {cy})" d="M{f(cx + R * 0.66)} {f(cy)} l4 -3 l2 2 l4 -1 l-3 3 z"/>' for a in range(0, 360, 45))
    dots = "".join(f'<circle cx="{f(cx + R * 0.86 * math.cos(math.radians(a)))}" cy="{f(cy + R * 0.86 * math.sin(math.radians(a)))}" r="0.9"/>' for a in range(0, 360, 12))
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{f(R * k)}" fill="none" stroke="{GOLD}" stroke-width="{w}"/>' for k, w in [(1, 1.6), (0.94, 0.7), (0.5, 1), (0.4, 0.6), (0.78, 1)])
    return (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#3B2A1A" fill-opacity="0.18"/>{rings}'
            f'<g fill="{GOLD}">{rays}{birds}{dots}</g><circle cx="{cx}" cy="{cy}" r="3" fill="{GOLD}"/>')


def hoi_van():
    top = drum(50, 56, 24) + key_band(4, 8)
    bot = key_band(-34, 22) + key_band(-46, 7) + "".join(drum(x, -76, 9) for x in (18, 50, 82))
    return doc("hồi văn & trống đồng", "Mặt trời trống đồng Đông Sơn giản lược ở ngực; dải hồi văn ở cổ và gấu tà.", top, bot)


# ---------------------------------------------------------------- 6. Rồng mây
def cloud(x, y, s=1.0, fill="#FBF6EC", line=GOLD):            # nền mây không đổi màu theo nền áo
    """Vân mây cát tường: ba bướu tròn, đuôi xoắn."""
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M0 0 C-3 -8 6 -12 10 -5 C12 -14 26 -14 26 -4 C32 -8 38 -2 34 4 C38 8 32 12 28 9 L2 9 C-5 9 -6 1 0 0 Z" '
            f'fill="{fill}" stroke="{line}" stroke-width="1.4"/>'
            f'<path d="M12 4 C10 -2 18 -4 19 1 C20 4 16 5 15 3 M26 5 C26 0 31 0 31 4" fill="none" stroke="{line}" stroke-width="1.1"/>'
            f'<path d="M34 4 C42 6 46 2 52 4" fill="none" stroke="{line}" stroke-width="1.2" stroke-linecap="round"/></g>')


def rong():
    spine = "M58 50 C80 72 82 102 56 122 C30 142 24 172 46 198 C68 224 74 254 50 278 C38 290 36 306 44 322"
    body = (f'<path d="{spine}" fill="none" stroke="{GOLD_D}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="{spine}" fill="none" stroke="{GOLD}" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="{spine}" fill="none" stroke="{GOLD_D}" stroke-width="7" stroke-dasharray="2 3.5" stroke-opacity="0.45"/>'
            f'<path d="{spine}" fill="none" stroke="#F3D88A" stroke-width="2.2" stroke-dasharray="5 2.5" transform="translate(-2.5 1.5)"/>'
            f'<path d="M44 322 C48 334 42 344 34 348" fill="none" stroke="{GOLD}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M34 348 l-8 -10 l12 2 z M34 348 l-10 6 l12 -1 z" fill="#C0392B" stroke="{GOLD_D}" stroke-width="0.6"/>')
    fins = "".join(f'<path d="M{x} {y} l{dx} {dy} l3 2 z" fill="#C0392B" stroke="{GOLD_D}" stroke-width="0.5"/>'
                   for x, y, dx, dy in [(78, 84, 8, -4), (74, 110, 8, 2), (32, 150, -8, -2), (30, 176, -8, 3), (70, 230, 8, -3), (66, 258, 8, 3)])
    claws = "".join(f'<g transform="translate({x} {y}) rotate({r})"><path d="M0 0 L10 0 M6 0 l6 -5 M6 0 l7 0 M6 0 l6 5" stroke="{GOLD_D}" stroke-width="2" stroke-linecap="round"/></g>'
                    for x, y, r in [(70, 128, 20), (30, 186, 160), (66, 244, 10), (40, 292, 170)])
    mane = "".join(f'<path d="M{x} {y} l{dx} {dy} l{ex} {ey} z" fill="#C0392B" stroke="{GOLD_D}" stroke-width="0.6"/>'
                   for x, y, dx, dy, ex, ey in [(64, 20, 12, -6, -4, 8), (68, 28, 14, -2, -6, 8), (68, 36, 14, 4, -8, 6), (62, 42, 10, 10, -10, 0)])
    head = (mane +
            # đầu rồng quay sang trái: trán gồ, mõm dài, hàm dưới há
            f'<path d="M68 38 C72 26 66 16 56 15 C50 9 40 10 34 16 C28 16 20 18 18 23 C22 25 26 25 30 26 '
            f'C34 27 40 26 44 28 C40 31 32 32 26 34 C24 38 28 40 34 39 C42 38 48 40 54 44 C60 46 66 44 68 38 Z" fill="{GOLD}" stroke="{GOLD_D}" stroke-width="1"/>'
            f'<path d="M26 30 l2 3 l2 -3 l2 3 l2 -3" fill="#FFFFFF" stroke="{GOLD_D}" stroke-width="0.5"/>'
            f'<path d="M30 29 C26 29 22 30 20 31" fill="none" stroke="#C0392B" stroke-width="2"/>'
            # sừng phân nhánh, mày, mắt
            f'<path d="M58 15 C62 6 70 2 78 -2 M66 8 C70 8 74 10 76 14 M54 14 C54 6 58 0 62 -4" fill="none" stroke="{GOLD_D}" stroke-width="2.2" stroke-linecap="round"/>'
            f'<path d="M42 18 C46 14 52 14 56 18" fill="none" stroke="{GOLD_D}" stroke-width="2"/>'
            f'<circle cx="48" cy="21" r="3" fill="#FFFFFF" stroke="{GOLD_D}" stroke-width="0.6"/><circle cx="47" cy="21" r="1.5" fill="#1A1A1A"/>'
            f'<circle cx="22" cy="22" r="1" fill="{GOLD_D}"/>'
            # râu dài uốn lượn, ngọc
            f'<path d="M20 22 C12 18 8 26 2 22 C-2 20 -2 14 4 14 M24 34 C16 40 18 50 8 54" fill="none" stroke="{GOLD_D}" stroke-width="1.3" stroke-linecap="round"/>'
            f'<circle cx="14" cy="44" r="5.5" fill="#C0392B" stroke="{GOLD}" stroke-width="1.6"/><path d="M12 42 Q14 40 16 42" fill="none" stroke="#FFFFFF" stroke-width="1"/>')
    top = cloud(8, 80, 0.8) + cloud(64, 168, 0.7) + body + fins + claws + head
    bot = cloud(4, -40, 1.0) + cloud(56, -30, 0.9) + cloud(30, -70, 0.7) + f'<path d="M0 -6 L100 -6" stroke="{GOLD}" stroke-width="2.5"/>'
    return doc("rồng mây", "Rồng uốn khúc từ vai xuống tà, đầu rồng ngậm ngọc ở ngực, mây cát tường quanh thân và ở gấu.", top, bot)


# ---------------------------------------------------------------- 7. Trúc quân tử
def bamboo_leaf(x, y, ang, L=22, c="#2F5A2E"):
    a = math.radians(ang)
    ex, ey = x + L * math.cos(a), y + L * math.sin(a)
    nx, ny = -math.sin(a) * L * 0.14, math.cos(a) * L * 0.14
    return (f'<path d="M{f(x)} {f(y)} Q{f((x + ex) / 2 + nx)} {f((y + ey) / 2 + ny)} {f(ex)} {f(ey)} '
            f'Q{f((x + ex) / 2 - nx)} {f((y + ey) / 2 - ny)} {f(x)} {f(y)} Z" fill="{c}"/>')


def truc():
    out = ""
    for x0, h, w in [(30, 270, 5), (46, 210, 4), (70, 245, 4.5)]:
        lean = (x0 - 50) * 0.08
        out += f'<path d="M{x0} 2 L{f(x0 + lean * h / 40)} {-h}" stroke="#5E8A3E" stroke-width="{w}" stroke-linecap="round"/>'
        for yy in range(-24, -h, -28):
            xx = x0 + lean * (-yy) / 40
            out += f'<path d="M{f(xx - w / 2 - 1)} {yy} L{f(xx + w / 2 + 1)} {yy}" stroke="#2F5A2E" stroke-width="1.6"/>'
        tx, ty = x0 + lean * h / 40, -h
        out += "".join(bamboo_leaf(tx, ty + 20 + 10 * k, a) for k, a in enumerate([200, 330, 215, 310, 190]))
    top = "".join(bamboo_leaf(x, y, a, 20) for x, y, a in [(80, 10, 150), (80, 10, 175), (74, 22, 140), (74, 22, 205), (68, 34, 160)])
    top += '<path d="M100 0 C90 8 82 14 66 38" stroke="#5E8A3E" stroke-width="2" fill="none"/>'
    return doc("trúc quân tử", "Ba thân trúc có đốt mọc từ gấu tà, lá trúc ở ngọn; nhành lá từ vai phải.", top, out)


# ---------------------------------------------------------------- 8. Mây cát tường
def may():
    top = cloud(18, 30, 1.0) + cloud(58, 54, 0.8) + cloud(24, 90, 0.6) + cloud(70, 120, 0.55)
    bot = cloud(2, -24, 1.3) + cloud(48, -36, 1.1) + cloud(26, -76, 0.9) + cloud(66, -100, 0.7) + cloud(12, -130, 0.55)
    return doc("mây cát tường", "Cụm vân mây xoắn ở vai và ngực, tầng mây dày dần về gấu tà.", top, bot)


# ---------------------------------------------------------------- 9. Tùng
def needles(x, y, r=11, c="#2E5A3A"):
    lines = "".join(f'<path d="M{x} {y} L{f(x + r * math.cos(math.radians(a)))} {f(y + r * math.sin(math.radians(a)))}"/>'
                    for a in range(200, 341, 14))
    return (f'<g stroke="{c}" stroke-width="1.3" stroke-linecap="round">{lines}</g>'
            f'<ellipse cx="{x}" cy="{f(y - r * 0.45)}" rx="{f(r * 0.9)}" ry="{f(r * 0.38)}" fill="{c}" fill-opacity="0.35"/>')


def tung():
    top = (branch("M100 30 C80 34 64 30 46 44 C36 52 26 52 14 50 M64 32 C60 22 54 18 46 16 M38 50 C36 60 30 66 22 70", 3) +
           "".join(needles(x, y) for x, y in [(46, 16), (14, 50), (22, 70), (56, 38), (32, 50), (78, 30), (88, 32)]))
    bot = (branch("M50 0 C46 -40 56 -80 48 -120 C44 -140 50 -160 46 -180 M48 -90 C62 -96 70 -104 80 -116 "
                  "M50 -130 C38 -134 30 -142 22 -152 M47 -170 C56 -174 62 -180 66 -188", 4) +
           "".join(needles(x, y, 13) for x, y in [(80, -116), (22, -152), (66, -188), (46, -182), (64, -104), (34, -142)]) +
           '<path d="M20 0 C30 -14 44 -16 54 -8 C62 -18 76 -16 84 0 Z" fill="#6B6255" fill-opacity="0.6"/>')
    return doc("tùng", "Cành tùng ngang ngực từ vai phải; cây tùng nhỏ trên đá ở tà.", top, bot)


# ---------------------------------------------------------------- 10. Sóng nước (hải thuỷ)
def song():
    cols = ["#2F5D8A", GOLD, "#F3EDE4", "#2E7D6B"]
    stripes = "".join(f'<path d="M{x} 0 L{x + 22} -40 L{x + 30} -40 L{x + 8} 0 Z" fill="{cols[k % 4]}"/>'
                      for k, x in enumerate(range(-30, 110, 8)))
    waves = ""
    for row, y in enumerate([-44, -54, -64]):
        for x in range(-10 + (row % 2) * 8, 110, 16):
            waves += (f'<path d="M{x} {y} a8 8 0 0 1 16 0" fill="#2F5D8A" stroke="#F3EDE4" stroke-width="1.6"/>'
                      f'<path d="M{x + 4} {y} a4 4 0 0 1 8 0" fill="none" stroke="#F3EDE4" stroke-width="1"/>')
    peaks = (f'<path d="M36 -66 L44 -96 L50 -84 L56 -102 L64 -66 Z" fill="{GOLD}" stroke="{GOLD_D}" stroke-width="1"/>'
             f'<path d="M44 -96 L46 -76 M56 -102 L56 -76" stroke="{GOLD_D}" stroke-width="0.8"/>')
    spray = "".join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#F3EDE4"/>' for x, y in [(30, -78), (70, -80), (24, -70), (76, -72)])
    bot = stripes + waves + peaks + spray + cloud(10, -110, 0.6) + cloud(62, -120, 0.6)
    top = f'<circle cx="50" cy="60" r="14" fill="#E8A33A" stroke="{GOLD_D}" stroke-width="1.6"/>' + cloud(22, 72, 0.7) + cloud(52, 78, 0.6)
    return doc("sóng nước (hải thuỷ)", "Dải sọc lập thuỷ, sóng cuộn và núi ở gấu tà như áo triều phục; mặt trời và mây ở ngực.", top, bot)


# ---------------------------------------------------------------- 11. Hoa cúc
def chrysanthemum(x, y, r, c="#F2C14E", c2="#E09A2D"):
    def ring(rad, rx, ry, start, step):
        out = ""
        for a in range(start, 360, step):
            px, py = x + rad * math.cos(math.radians(a)), y + rad * math.sin(math.radians(a))
            out += f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="{f(rx)}" ry="{f(ry)}" transform="rotate({a} {f(px)} {f(py)})"/>'
        return out
    return (f'<g fill="{c}" stroke="{c2}" stroke-width="0.5">{ring(r * 0.6, r * 0.42, r * 0.12, 0, 18)}</g>'
            f'<g fill="{c2}">{ring(r * 0.3, r * 0.25, r * 0.1, 9, 24)}</g><circle cx="{x}" cy="{y}" r="{f(r * 0.14)}" fill="#B5651D"/>')


def cuc_leaf(x, y, rot, s=1.0):
    return (f'<path transform="translate({x} {y}) rotate({rot}) scale({s})" d="M0 0 C4 -4 8 -2 10 -6 C12 -2 16 -4 18 -8 '
            f'C20 -2 22 0 24 -2 C22 4 16 6 10 6 C6 6 2 4 0 0 Z" fill="#4F7A3C" stroke="#2F5A2E" stroke-width="0.6"/>')


def cuc():
    stems = branch("M30 0 C32 -40 28 -80 34 -120 M58 0 C56 -30 62 -60 60 -84 M74 0 C76 -50 70 -120 76 -160", 1.8, "#4F7A3C")
    leaves = "".join(cuc_leaf(x, y, r) for x, y, r in [(30, -40, 200), (32, -80, -20), (58, -40, -30), (74, -60, 190), (74, -110, -10), (20, -10, 190)])
    bot = stems + leaves + chrysanthemum(34, -124, 16) + chrysanthemum(60, -88, 12, "#FFFFFF", "#E0C27A") + chrysanthemum(76, -162, 13)
    top = (branch("M8 70 C14 56 18 44 26 34", 1.4, "#4F7A3C") + cuc_leaf(14, 58, -40, 0.8) + chrysanthemum(28, 32, 10) +
           '<ellipse cx="18" cy="46" rx="3" ry="4.5" fill="#F2C14E" stroke="#E09A2D" stroke-width="0.5"/>')
    return doc("hoa cúc", "Ba bông cúc vàng, trắng vươn từ lá ở gấu tà; một bông nhỏ và nụ ở vai trái.", top, bot)


# ---------------------------------------------------------------- 12. Mai vàng
def mai_vang():
    def yel(x, y, r):
        return blossom(x, y, r, "#F5C518", "#E07B1A", rot=x * 5)
    br = (branch("M94 4 C86 -30 92 -60 76 -96 C68 -114 70 -140 56 -168 C50 -180 40 -190 32 -210", 4) +
          branch("M80 -80 C66 -84 52 -80 40 -92 M70 -132 C80 -146 86 -160 84 -180 M58 -164 C46 -158 34 -160 24 -170", 2.2) +
          branch("M90 -40 C78 -44 70 -40 62 -48", 1.8))
    bot = br + "".join(yel(x, y, r) for x, y, r in [(32, -212, 8), (40, -92, 7.5), (84, -182, 8), (24, -170, 7), (62, -48, 7),
                                                     (56, -168, 6), (76, -98, 6.5), (66, -134, 6), (50, -82, 5.5), (88, -60, 5.5)])
    bot += bud(46, -196, 3.5, "#E8B320") + bud(30, -100, 3.5, "#E8B320") + bud(80, -160, 3.5, "#E8B320")
    top = (branch("M98 20 C88 26 80 30 70 42 M84 28 C82 20 78 16 72 14", 1.8) + yel(70, 42, 7) + yel(72, 14, 6) + bud(86, 22, 3.2, "#E8B320") +
           "".join(petal_fall(x, y, 4.5, r, "#F5C518") for x, y, r in [(60, 60, 20), (66, 80, -30), (54, 96, 40)]))
    return doc("mai vàng", "Cành mai vàng ngày Tết vươn từ gấu tà lên ngang hông, nhành nhỏ ở vai phải, cánh mai rơi.", top, bot)


# ---------------------------------------------------------------- 13. Chim Lạc
BRONZE = "#B8862B"


def lac(x, y, s=1.0, rot=-20):
    """Chim Lạc Đông Sơn giản lược: mỏ dài, mào, cánh xoè gãy góc, đuôi dài."""
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" fill="{BRONZE}" stroke="#3B2A1A" stroke-width="0.7">'
            '<path d="M-12 0 C-6 -3 6 -3 10 0 C6 3 -6 3 -12 0 Z"/>'
            '<path d="M9 -1 L24 -2 L9 1 Z"/><circle cx="7" cy="-0.5" r="2.4"/>'
            '<path d="M5 -2 L0 -10 L4 -9 L2 -14 L7 -6 Z"/>'
            '<path d="M-2 -2 L-8 -16 L2 -12 L4 -22 L6 -4 Z"/>'
            '<path d="M-12 0 L-30 -4 L-26 0 L-32 4 L-12 2 Z"/>'
            '<circle cx="7.6" cy="-0.8" r="0.8" fill="#3B2A1A"/></g>')


def circle_band(y, n=7, r=6):
    out = f'<path d="M-4 {y - r - 3} L104 {y - r - 3} M-4 {y + r + 3} L104 {y + r + 3}" stroke="{BRONZE}" stroke-width="1.4"/>'
    for i in range(n + 1):
        cx = i * 100 / n
        out += (f'<circle cx="{f(cx)}" cy="{y}" r="{r}" fill="none" stroke="{BRONZE}" stroke-width="1.3"/>'
                f'<circle cx="{f(cx)}" cy="{y}" r="1.6" fill="{BRONZE}"/>')
        if i < n:
            out += f'<path d="M{f(cx + r)} {y} L{f(cx + 100 / n - r)} {y}" stroke="{BRONZE}" stroke-width="1"/>'
    return out


def chim_lac():
    top = lac(66, 40, 1.15, -18) + lac(40, 74, 0.95, -14) + circle_band(8, 6, 4)
    bot = circle_band(-16, 7, 6) + lac(30, -70, 1.2, -24) + lac(60, -110, 1.0, -20) + lac(36, -150, 0.85, -16)
    return doc("chim Lạc", "Đàn chim Lạc Đông Sơn bay chéo lên ở tà và ngực; dải vòng tròn tiếp tuyến ở cổ và gấu.", top, bot)


# ---------------------------------------------------------------- 14. Bướm và hoa
def butterfly(x, y, s=1.0, rot=0, c1="#7FB8D9", c2="#F2A1C4"):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})" stroke="#3B3B5A" stroke-width="0.6">'
            f'<path d="M0 0 C-6 -14 -18 -16 -16 -4 C-15 2 -6 2 0 0 Z" fill="{c1}"/><path d="M0 0 C6 -14 18 -16 16 -4 C15 2 6 2 0 0 Z" fill="{c1}"/>'
            f'<path d="M0 1 C-4 8 -12 12 -12 6 C-12 3 -6 2 0 1 Z" fill="{c2}"/><path d="M0 1 C4 8 12 12 12 6 C12 3 6 2 0 1 Z" fill="{c2}"/>'
            '<circle cx="-9" cy="-7" r="1.6" fill="#FFFFFF"/><circle cx="9" cy="-7" r="1.6" fill="#FFFFFF"/>'
            '<path d="M0 -6 L0 6" stroke-width="1.6"/><path d="M0 -6 C-2 -10 -4 -12 -6 -13 M0 -6 C2 -10 4 -12 6 -13" fill="none"/></g>')


def buom():
    def small(x, y, c):
        return blossom(x, y, 5, c, "#E8B830", rot=x * 9)
    stems = branch("M24 0 C26 -20 22 -36 28 -52 M40 0 C38 -16 44 -30 40 -44 M62 0 C64 -22 58 -34 64 -60 M78 0 C76 -12 80 -24 76 -36", 1.3, "#4F7A3C")
    bot = stems + "".join(small(x, y, c) for x, y, c in [(28, -52, "#FFFFFF"), (40, -44, "#F2A1C4"), (64, -60, "#FFFFFF"), (76, -36, "#F2A1C4"),
                                                          (34, -30, "#F2A1C4"), (70, -20, "#FFFFFF"), (20, -20, "#FFFFFF")])
    bot += butterfly(52, -100, 1.1, -12) + butterfly(30, -140, 0.85, 14, "#F2A1C4", "#F5D46A") + butterfly(70, -170, 0.75, -20)
    top = (butterfly(30, 40, 0.9, 18, "#F5D46A", "#7FB8D9") + butterfly(70, 70, 0.7, -16) +
           "".join(f'<path d="M{x} {y} q3 -4 6 0" fill="none" stroke="#3B3B5A" stroke-width="0.7" stroke-dasharray="1.5 2"/>'
                   for x, y in [(42, 52), (52, 60), (60, 66)]))
    return doc("bướm và hoa", "Ba cánh bướm bay lên từ cụm hoa nhỏ ở gấu tà; hai cánh bướm ở vai.", top, bot)


MOTIFS = [("canh_dao", canh_dao), ("phuong_hoang", phuong), ("hac_mai", hac_mai), ("sen", sen), ("hoi_van", hoi_van),
          ("rong_may", rong), ("truc", truc), ("may", may), ("tung", tung), ("song_nuoc", song),
          ("cuc", cuc), ("mai_vang", mai_vang), ("chim_lac", chim_lac), ("buom", buom)]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in MOTIFS:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("Đã tạo motif/" + name + ".svg")

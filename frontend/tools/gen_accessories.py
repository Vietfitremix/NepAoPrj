"""Sinh phụ kiện (nón, khăn, giày, túi, quạt, trang sức) ở hướng TRƯỚC, TRÁI, SAU; hướng PHẢI do mirror_views.py lật từ TRÁI.

Mốc lấy từ số đo người mẫu (tools/view_measure.py, body_measure.py):
  đầu: đỉnh tóc 30, đỉnh sọ 42, chân mày ~80, tai (164/236, 96), cằm 140; nghiêng: tâm đầu x~204, mũi x~152, gáy x~248
  cổ y=160: nữ 186–214, nam 179–221; bàn tay (trước) nữ tâm 131/269, nam 124/276, y 430–500; nghiêng tâm ~202 (nam ~198)
  bàn chân (trước): trái 163–197, phải 203–237, y 752–781; nghiêng: mũi chân x~150, gót x~213
Màu: #FF00FF = màu điểm nhấn người dùng chọn; các màu khác cố định theo chất liệu (lá cọ, bạc, vải nhung đen...).
Chạy: python tools/gen_accessories.py   (tự gọi mirror_views.py ở cuối)
"""
import math
import subprocess
import sys
from pathlib import Path

FIG = Path(__file__).resolve().parents[1] / "public/figure/accessory"
G = 'stroke="#000" stroke-opacity="0.3" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round"'
LINE = 'fill="none" stroke="#000" stroke-opacity="0.22" stroke-width="1.1"'
STRAW, STRAW_D, STRAW_L = "#E3C98A", "#C4A15E", "#F0DDAA"
BLACK, SILVER, GOLD, WOOD = "#26211F", "#C9CED6", "#D9B44A", "#8A5A32"
VIEW_NAME = {"": "TRƯỚC", "_trai": "TRÁI (nhìn nghiêng, mặt quay sang trái)", "_sau": "SAU", "_phai": "PHẢI"}


def doc(name, view, note, body, ve_tay=False):
    head = "VE_TAY: " if ve_tay else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n'
            f'  <!-- {head}{note} – hướng {VIEW_NAME[view]}. Sinh bằng tools/gen_accessories.py. -->\n'
            f'  <g id="{name}{view}" {G}>\n{body}\n  </g>\n</svg>\n')


def P(x, y):
    return f"{x:.1f} {y:.1f}"


# ---------------------------------------------------------------- nón lá
def non_la(cx, quai):
    """Nón lá hình chóp: đỉnh y=0, vành y=66, rộng 172 (≈2,4 lần bề ngang đầu, nón thật đường kính ~41 cm)."""
    l, r = cx - 86, cx + 86
    rings = " ".join(f"M{P(cx - 86 * t, 66 * t)} Q{P(cx, 66 * t + 12 * t)} {P(cx + 86 * t, 66 * t)}" for t in (0.3, 0.55, 0.8))
    ribs = " ".join(f"M{P(cx, 2)} L{P(cx + dx, 70 + abs(dx) * -0.03)}" for dx in (-56, -28, 0, 28, 56))
    out = [
        f'    <path id="mat_duoi_vanh" d="M{P(l, 66)} Q{P(cx, 92)} {P(r, 66)} Q{P(cx, 80)} {P(l, 66)} Z" fill="{STRAW_D}"/>',
        f'    <path id="than_non" d="M{P(cx, 0)} L{P(r, 66)} Q{P(cx, 80)} {P(l, 66)} Z" fill="{STRAW}"/>',
        f'    <path id="bong_non" d="M{P(cx, 0)} L{P(r, 66)} Q{P(cx + 40, 76)} {P(cx + 6, 78)} Z" fill="#000" fill-opacity="0.1" stroke="none"/>',
        f'    <path id="vong_nan" d="{rings}" {LINE}/>',
        f'    <path id="gan_la" d="{ribs}" fill="none" stroke="#000" stroke-opacity="0.1" stroke-width="1"/>',
    ]
    if quai:
        out.append(f'    <path id="quai" d="{quai}" fill="none" stroke="#FF00FF" stroke-opacity="1" stroke-width="3"/>')
    return "\n".join(out)


# ---------------------------------------------------------------- nón quai thao (nón ba tầm)
def quai_thao(cx, quai, tua):
    """Nón quai thao (nón ba tầm): mặt nón bằng hơi vồng ở giữa, thành nón đứng cao và loe nhẹ; đội sụp tới trán (mép thành ở y≈68,
    trên chân mày). Quai thao men theo hai bên má, vòng dưới cằm, tua thả trước ngực."""
    R, ry, top, h, fl = 100, 13, 38, 17, 5        # bán kính mặt (~2,9 lần bề ngang đầu), độ dẹt elip, tâm mặt nón, cao thành, độ loe
    l, r, lb, rb = cx - R, cx + R, cx - R - fl, cx + R + fl
    yb = top + h
    rings = " ".join(f'<ellipse cx="{cx:.1f}" cy="{top}" rx="{R * k:.1f}" ry="{ry * k:.1f}"/>' for k in (0.86, 0.72))
    out = [
        f'    <path id="thanh_non" d="M{P(l, top)} L{P(lb, yb)} A{R + fl} {ry} 0 0 0 {P(rb, yb)} L{P(r, top)} '
        f'A{R} {ry} 0 0 1 {P(l, top)} Z" fill="{STRAW}"/>',
        f'    <path id="bong_thanh" d="M{P(l, top)} L{P(lb, yb)} A{R + fl} {ry} 0 0 0 {P(cx - 62, yb + ry * 0.79)} '
        f'L{P(cx - 60, top + ry * 0.79)} A{R} {ry} 0 0 1 {P(l, top)} Z M{P(r, top)} L{P(rb, yb)} '
        f'A{R + fl} {ry} 0 0 1 {P(cx + 62, yb + ry * 0.79)} L{P(cx + 60, top + ry * 0.79)} A{R} {ry} 0 0 0 {P(r, top)} Z" '
        'fill="#000" fill-opacity="0.14" stroke="none"/>',
        f'    <path id="duong_khau_thanh" d="M{P(l - 2.5, top + h / 2)} A{R + 2.5} {ry} 0 0 0 {P(r + 2.5, top + h / 2)}" '
        'fill="none" stroke="#000" stroke-opacity="0.22" stroke-width="1.1" stroke-dasharray="3 3"/>',
        f'    <ellipse id="mat_non" cx="{cx:.1f}" cy="{top}" rx="{R}" ry="{ry}" fill="{STRAW_L}"/>',
        f'    <g id="vong_khau" {LINE}>{rings}</g>',
        f'    <path id="vong_dinh" d="M{P(cx - R * 0.55, top)} Q{P(cx - R * 0.5, top - 13)} {P(cx, top - 13)} Q{P(cx + R * 0.5, top - 13)} {P(cx + R * 0.55, top)} '
        f'A{R * 0.55} {ry * 0.55} 0 0 1 {P(cx - R * 0.55, top)} Z" fill="{STRAW_L}"/>',
        f'    <path id="sang_dinh" d="M{P(cx - 34, top - 6)} Q{P(cx, top - 10)} {P(cx + 26, top - 7)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="2"/>',
    ]
    if quai:
        out.append(f'    <path id="quai_thao" d="{quai}" fill="none" stroke="#FF00FF" stroke-opacity="1" stroke-width="4"/>')
    if tua:
        out.append(f'    <path id="tua" d="{tua}" fill="none" stroke="#FF00FF" stroke-opacity="1" stroke-width="3"/>')
        ends = [tuple(map(float, s.split()[-2:])) for s in tua.split("M")[1:]]
        out.append('    <g id="dau_tua" fill="#FF00FF" stroke-opacity="0.35">' + "".join(
            f'<path d="M{P(x - 4, y)} L{P(x + 4, y)} L{P(x + 5, y + 16)} L{P(x - 5, y + 16)} Z"/>' for x, y in ends) + "</g>")
        out.append('    <g id="soi_tua" ' + LINE + ">" + "".join(
            f'<path d="M{P(x - 2, y + 3)} L{P(x - 2.5, y + 15)} M{P(x + 2, y + 3)} L{P(x + 2.5, y + 15)}"/>' for x, y in ends) + "</g>")
    return "\n".join(out)


# ---------------------------------------------------------------- khăn mỏ quạ, khăn xếp
MO_QUA = {
    "": f'''    <path id="khan" fill="{BLACK}" d="M168 132 C158 120 154 104 155 88 C154 50 174 26 200 24 C226 26 246 50 245 88 C246 104 242 120 232 132
      L230 100 C230 80 226 66 214 60 L200 44 L186 60 C174 66 170 80 170 100 Z"/>
    <path id="mo_qua" d="M186 60 L200 36 L214 60 L200 50 Z" fill="{BLACK}"/>
    <path id="day_buoc" d="M168 130 Q182 142 197 147 M232 130 Q218 142 203 147" fill="none" stroke="{BLACK}" stroke-opacity="1" stroke-width="4"/>
    <ellipse id="nut_buoc" cx="200" cy="148" rx="5" ry="3.5" fill="{BLACK}"/>
    <path id="sang_nhung" d="M174 40 Q190 30 208 30 M162 70 Q164 54 172 44 M238 70 Q236 54 228 44 M196 44 L200 40" fill="none" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="2.2"/>''',
    "_trai": f'''    <path id="khan" fill="{BLACK}" d="M148 58 C156 38 176 26 206 24 C236 24 254 44 258 70 C262 96 260 118 252 132 C244 140 230 140 220 136
      L198 136 C196 118 194 98 188 84 C182 74 172 68 160 64 Z"/>
    <path id="mo_qua" d="M160 64 L142 52 L166 50 Z" fill="{BLACK}"/>
    <path id="day_buoc" d="M198 134 Q190 142 182 145" fill="none" stroke="{BLACK}" stroke-opacity="1" stroke-width="4"/>
    <ellipse id="nut_buoc" cx="180" cy="145" rx="4.5" ry="3.5" fill="{BLACK}"/>
    <path id="sang_nhung" d="M168 40 Q190 28 214 30 M232 40 Q250 56 252 86 M200 60 Q228 64 244 100" fill="none" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="2.2"/>''',
    "_sau": f'''    <path id="khan" fill="{BLACK}" d="M156 96 C152 54 174 26 200 26 C226 26 248 54 244 96 C244 118 236 136 220 142 L180 142 C164 136 156 118 156 96 Z"/>
    <path id="nep_khan" d="M176 60 Q200 70 224 60 M168 96 Q200 108 232 96 M186 124 Q200 132 214 124" fill="none" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="2"/>''',
}

KHAN_XEP = {
    "": '''    <path id="vanh_khan" fill="#FF00FF" d="M160 80 C157 64 157 48 162 38 Q200 26 238 38 C243 48 243 64 240 80 Q200 70 160 80 Z"/>
    <ellipse id="dinh_khan" cx="200" cy="35" rx="38" ry="5" fill="#FF00FF"/>
    <path id="nep_ngang" d="M160 50 Q200 42 240 50 M159 62 Q200 54 241 62" fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="1.4"/>
    <path id="nep_chu_nhan" d="M184 40 L203 74 M216 40 L197 74 M174 42 L188 72 M226 42 L212 72" fill="none" stroke="#000" stroke-opacity="0.28" stroke-width="1.3"/>
    <path id="sang_khan" d="M170 44 Q200 36 230 44" fill="none" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="2.5"/>''',
    "_trai": '''    <path id="vanh_khan" fill="#FF00FF" d="M158 78 C155 62 157 46 165 36 Q204 22 244 34 C252 46 254 64 252 82 Q206 70 158 78 Z"/>
    <path id="dinh_khan" d="M165 36 Q204 22 244 34 Q204 30 165 36 Z" fill="#000" fill-opacity="0.15" stroke="none"/>
    <path id="nep_ngang" d="M157 50 Q204 40 251 50 M157 63 Q204 54 253 66" fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="1.4"/>
    <path id="nep_chu_nhan" d="M166 42 L178 74 M176 38 L190 72 M186 36 L200 70" fill="none" stroke="#000" stroke-opacity="0.28" stroke-width="1.3"/>
    <path id="sang_khan" d="M172 40 Q200 32 230 36" fill="none" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="2.5"/>''',
    "_sau": '''    <path id="vanh_khan" fill="#FF00FF" d="M160 82 C157 64 157 48 162 38 Q200 26 238 38 C243 48 243 64 240 82 Q200 90 160 82 Z"/>
    <ellipse id="dinh_khan" cx="200" cy="35" rx="38" ry="5" fill="#FF00FF"/>
    <path id="nep_ngang" d="M160 50 Q200 58 240 50 M159 64 Q200 72 241 64" fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="1.4"/>
    <path id="mui_khan" d="M200 40 L200 86" fill="none" stroke="#000" stroke-opacity="0.2" stroke-width="1.2"/>''',
}


# ---------------------------------------------------------------- hoa cài tóc
def flower(cx, cy, r):
    petals = "".join(
        f'<ellipse cx="{cx + r * 0.62 * math.cos(a):.1f}" cy="{cy + r * 0.62 * math.sin(a):.1f}" rx="{r * 0.5:.1f}" ry="{r * 0.36:.1f}" '
        f'transform="rotate({math.degrees(a):.0f} {cx + r * 0.62 * math.cos(a):.1f} {cy + r * 0.62 * math.sin(a):.1f})"/>'
        for a in [i * 2 * math.pi / 5 - math.pi / 2 for i in range(5)])
    return (f'    <path id="la" d="M{P(cx - r * 0.4, cy + r * 0.6)} Q{P(cx - r * 1.6, cy + r * 1.1)} {P(cx - r * 1.5, cy + r * 0.2)} Q{P(cx - r * 0.8, cy + r * 0.3)} {P(cx - r * 0.4, cy + r * 0.6)} Z" fill="#6B8F4E"/>\n'
            f'    <g id="canh_hoa" fill="#FF00FF">{petals}</g>\n'
            f'    <circle id="nhuy" cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.28:.1f}" fill="{GOLD}"/>')


# ---------------------------------------------------------------- giày dép
def pair(shape_fn):
    """Vẽ một chiếc cho bàn chân trái (tâm x=180) rồi chiếc phải (tâm x=220)."""
    return shape_fn(180) + "\n" + shape_fn(220)


def hai_front(c):
    return (f'    <path d="M{P(c - 16, 778)} C{P(c - 17, 769)} {P(c - 11, 763)} {P(c, 762)} C{P(c + 11, 763)} {P(c + 17, 769)} {P(c + 16, 778)} '
            f'Q{P(c + 16, 786)} {P(c + 10, 786)} L{P(c - 10, 786)} Q{P(c - 16, 786)} {P(c - 16, 778)} Z" fill="#FF00FF"/>\n'
            f'    <path d="M{P(c - 3, 763)} Q{P(c - 1, 753)} {P(c + 4, 757)}" fill="none" stroke="#FF00FF" stroke-opacity="1" stroke-width="3"/>\n'
            f'    <path d="M{P(c - 9, 772)} q3 -3 6 0 q3 3 6 0 q3 -3 6 0" fill="none" stroke="{GOLD}" stroke-opacity="1" stroke-width="1.3"/>\n'
            f'    <rect x="{c - 16:.1f}" y="784" width="32" height="4" rx="2" fill="#EFE6D2"/>')


def hai_back(c):
    return (f'    <path d="M{P(c - 13, 772)} Q{P(c, 768)} {P(c + 13, 772)} Q{P(c + 15, 780)} {P(c + 13, 786)} L{P(c - 13, 786)} Q{P(c - 15, 780)} {P(c - 13, 772)} Z" fill="#FF00FF"/>\n'
            f'    <path d="M{P(c - 8, 778)} q4 -3 8 0 q4 3 8 0" fill="none" stroke="{GOLD}" stroke-opacity="1" stroke-width="1.2"/>\n'
            f'    <rect x="{c - 14:.1f}" y="784" width="28" height="4" rx="2" fill="#EFE6D2"/>')


HAI = {
    "": pair(hai_front),
    "_trai": f'''    <path id="than_hai" d="M147 774 Q141 765 147 764 C156 768 166 765 176 762 C184 761 190 764 196 769 L214 770 Q219 779 215 786 L152 786 Q146 783 147 774 Z" fill="#FF00FF"/>
    <path id="mui_cong" d="M149 768 Q140 758 146 756" fill="none" stroke="#FF00FF" stroke-opacity="1" stroke-width="3"/>
    <path id="hoa_van_theu" d="M156 776 q4 -4 8 0 q4 4 8 0 q4 -4 8 0" fill="none" stroke="{GOLD}" stroke-opacity="1" stroke-width="1.3"/>
    <rect id="de" x="148" y="784" width="68" height="4" rx="2" fill="#EFE6D2"/>''',
    "_sau": pair(hai_back),
}


def sneaker_front(c):
    return (f'    <path d="M{P(c - 18, 783)} C{P(c - 20, 769)} {P(c - 12, 757)} {P(c, 755)} C{P(c + 12, 757)} {P(c + 20, 769)} {P(c + 18, 783)} Z" fill="#F7F7F5"/>\n'
            f'    <path d="M{P(c - 19, 782)} L{P(c + 19, 782)} L{P(c + 19, 789)} Q{P(c, 791)} {P(c - 19, 789)} Z" fill="#E2E2DC"/>\n'
            f'    <path d="M{P(c - 6, 763)} L{P(c + 6, 763)} M{P(c - 7, 769)} L{P(c + 7, 769)} M{P(c - 12, 778)} Q{P(c, 773)} {P(c + 12, 778)}" {LINE}/>')


def sneaker_back(c):
    return (f'    <path d="M{P(c - 15, 789)} L{P(c - 15, 764)} Q{P(c, 752)} {P(c + 15, 764)} L{P(c + 15, 789)} Z" fill="#F7F7F5"/>\n'
            f'    <path d="M{P(c - 16, 782)} L{P(c + 16, 782)} L{P(c + 16, 790)} L{P(c - 16, 790)} Z" fill="#E2E2DC"/>\n'
            f'    <path d="M{P(c - 4, 756)} L{P(c - 4, 772)} L{P(c + 4, 772)} L{P(c + 4, 756)}" fill="#FF00FF"/>')


SNEAKER = {
    "": pair(sneaker_front),
    "_trai": '''    <path id="than_giay" d="M143 781 C143 771 151 766 163 762 C173 758 181 751 187 746 L211 746 C215 755 219 768 219 781 Z" fill="#F7F7F5"/>
    <path id="de" d="M141 780 L221 780 L221 789 Q181 792 141 789 Z" fill="#E2E2DC"/>
    <path id="day_giay" d="M166 762 L172 766 M172 758 L178 762 M178 754 L184 758 M183 750 L189 754" fill="none" stroke="#000" stroke-opacity="0.3" stroke-width="1.3"/>
    <path id="vien_mui" d="M144 778 Q146 768 160 764" fill="none" stroke="#000" stroke-opacity="0.18" stroke-width="1.1"/>
    <path id="dai_got" d="M206 748 L214 748 L218 770 L210 770 Z" fill="#FF00FF"/>''',
    "_sau": pair(sneaker_back),
}


def bup_be_front(c):
    return (f'    <path d="M{P(c - 17, 781)} C{P(c - 17, 772)} {P(c - 10, 767)} {P(c, 767)} C{P(c + 10, 767)} {P(c + 17, 772)} {P(c + 17, 781)} '
            f'Q{P(c + 16, 787)} {P(c + 10, 787)} L{P(c - 10, 787)} Q{P(c - 16, 787)} {P(c - 17, 781)} Z" fill="#FF00FF"/>\n'
            f'    <path d="M{P(c - 6, 768)} L{P(c, 772)} L{P(c - 6, 776)} Z M{P(c + 6, 768)} L{P(c, 772)} L{P(c + 6, 776)} Z" fill="#FF00FF" stroke-opacity="0.45"/>\n'
            f'    <rect x="{c - 16:.1f}" y="785" width="32" height="3" rx="1.5" fill="#3A2E28"/>')


def bup_be_back(c):
    return (f'    <path d="M{P(c - 13, 776)} Q{P(c, 773)} {P(c + 13, 776)} Q{P(c + 15, 782)} {P(c + 13, 787)} L{P(c - 13, 787)} Q{P(c - 15, 782)} {P(c - 13, 776)} Z" fill="#FF00FF"/>\n'
            f'    <rect x="{c - 14:.1f}" y="785" width="28" height="3" rx="1.5" fill="#3A2E28"/>')


BUP_BE = {
    "": pair(bup_be_front),
    "_trai": '''    <path id="than_giay" d="M147 777 C147 770 153 768 161 768 C171 768 181 770 189 773 L213 772 Q218 780 214 787 L152 787 Q146 784 147 777 Z" fill="#FF00FF"/>
    <path id="no" d="M154 766 L160 770 L154 774 Z M166 766 L160 770 L166 774 Z" fill="#FF00FF" stroke-opacity="0.45"/>
    <rect id="de" x="148" y="785" width="68" height="3" rx="1.5" fill="#3A2E28"/>''',
    "_sau": pair(bup_be_back),
}


def giay_ta_front(c):
    return (f'    <path d="M{P(c - 18, 783)} C{P(c - 19, 770)} {P(c - 12, 760)} {P(c, 759)} C{P(c + 12, 760)} {P(c + 19, 770)} {P(c + 18, 783)} Z" fill="{BLACK}"/>\n'
            f'    <path d="M{P(c - 18, 782)} L{P(c + 18, 782)} L{P(c + 18, 788)} L{P(c - 18, 788)} Z" fill="#F2EEE3"/>\n'
            f'    <path d="M{P(c - 9, 764)} Q{P(c, 760)} {P(c + 9, 764)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="1.5"/>')


def giay_ta_back(c):
    return (f'    <path d="M{P(c - 14, 788)} L{P(c - 14, 766)} Q{P(c, 760)} {P(c + 14, 766)} L{P(c + 14, 788)} Z" fill="{BLACK}"/>\n'
            f'    <path d="M{P(c - 15, 782)} L{P(c + 15, 782)} L{P(c + 15, 789)} L{P(c - 15, 789)} Z" fill="#F2EEE3"/>')


GIAY_TA = {
    "": pair(giay_ta_front),
    "_trai": f'''    <path id="than_giay" d="M145 782 C145 772 153 767 164 763 C175 759 183 755 189 753 L210 753 Q216 766 216 782 Z" fill="{BLACK}"/>
    <path id="de" d="M143 781 L218 781 L218 789 L143 789 Z" fill="#F2EEE3"/>
    <path id="sang" d="M152 772 Q164 764 182 758" fill="none" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="1.5"/>''',
    "_sau": pair(giay_ta_back),
}


# ---------------------------------------------------------------- túi cói, quạt giấy (cầm ở tay trái người mẫu)
HAND = {"nu": dict(front=269, side=202, back=131), "nam": dict(front=276, side=198, back=124)}


def tui(c, k=1.0):
    w, top, bot = 24 * k, 486, 486 + 64 * k
    weave = " ".join(f"M{P(c - w - (y - top) * 0.1, y)} L{P(c + w + (y - top) * 0.1, y)}" for y in range(top + 16, int(bot) - 2, 8))
    return (f'    <path id="quai_tui" d="M{P(c - 15 * k, top)} C{P(c - 15 * k, 460)} {P(c + 15 * k, 460)} {P(c + 15 * k, top)}" fill="none" stroke="#FF00FF" stroke-opacity="1" stroke-width="3.5"/>\n'
            f'    <path id="than_tui" d="M{P(c - w, top)} L{P(c + w, top)} L{P(c + w + 6, bot)} Q{P(c, bot + 6)} {P(c - w - 6, bot)} Z" fill="{STRAW}"/>\n'
            f'    <path id="dan_coi" d="{weave}" fill="none" stroke="{STRAW_D}" stroke-width="1.4" stroke-opacity="1"/>\n'
            f'    <path id="vien_mieng" d="M{P(c - w, top)} L{P(c + w, top)} L{P(c + w + 0.8, top + 9)} L{P(c - w - 0.8, top + 9)} Z" fill="#FF00FF"/>')


def quat(cx, cy, a0, a1, R=62, r0=24):
    """Quạt giấy xoè: trục ở bàn tay (cx, cy), xoè từ góc a0 tới a1 (độ, 0 = sang phải, 90 = xuống dưới)."""
    pt = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    big = 1 if a1 - a0 > 180 else 0
    leaf = f"M{P(*pt(r0, a0))} L{P(*pt(R, a0))} A{R} {R} 0 {big} 1 {P(*pt(R, a1))} L{P(*pt(r0, a1))} A{r0} {r0} 0 {big} 0 {P(*pt(r0, a0))} Z"
    n = 9
    ribs = " ".join(f"M{P(cx, cy)} L{P(*pt(R - 2, a0 + (a1 - a0) * i / n))}" for i in range(n + 1))
    folds = " ".join(f"M{P(*pt(r0, a0 + (a1 - a0) * (i + .5) / n))} L{P(*pt(R, a0 + (a1 - a0) * (i + .5) / n))}" for i in range(n))
    deco = f"M{P(*pt(R - 10, a0 + 6))} A{R - 10} {R - 10} 0 0 1 {P(*pt(R - 10, a1 - 6))}"
    return (f'    <path id="nan_trong" d="{ribs}" fill="none" stroke="{WOOD}" stroke-opacity="1" stroke-width="1.6"/>\n'
            f'    <path id="mat_quat" d="{leaf}" fill="#FF00FF"/>\n'
            f'    <path id="nep_gap" d="{folds}" fill="none" stroke="#000" stroke-opacity="0.16" stroke-width="1"/>\n'
            f'    <path id="hoa_van" d="{deco}" fill="none" stroke="{GOLD}" stroke-opacity="1" stroke-width="1.6"/>\n'
            f'    <circle id="dinh_quat" cx="{cx:.1f}" cy="{cy:.1f}" r="2.6" fill="{WOOD}"/>')


# ---------------------------------------------------------------- kiềng bạc, bông tai + vòng tay
def ring(d, w=6):
    return (f'    <path id="vien_kieng" d="{d}" fill="none" stroke="#8A9099" stroke-opacity="1" stroke-width="{w + 1.6}"/>\n'
            f'    <path id="kieng" d="{d}" fill="none" stroke="{SILVER}" stroke-opacity="1" stroke-width="{w}"/>\n'
            f'    <path id="sang_kieng" d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="1.6"/>')


KIENG = {
    "": ring("M178 160 Q200 190 222 160"),
    "_trai": ring("M219 157 C212 170 192 179 176 175"),
    "_sau": ring("M184 158 Q200 168 216 158"),
}


def earring(x, y):
    return (f'<circle cx="{x}" cy="{y}" r="2" fill="{GOLD}"/><path d="M{x} {y + 2} L{x} {y + 6}" stroke="{GOLD}" stroke-opacity="1"/>'
            f'<circle cx="{x}" cy="{y + 9}" r="3.2" fill="#F4EFE6"/>')


def bracelet(x0, x1, y):
    return f'<path d="M{x0} {y} Q{(x0 + x1) / 2} {y + 5} {x1} {y}" fill="none" stroke="{GOLD}" stroke-opacity="1" stroke-width="3"/>'


TRANG_SUC = {
    "": f'    <g id="bong_tai">{earring(164, 106)}{earring(236, 106)}</g>\n    <g id="vong_tay">{bracelet(121, 140, 441)}{bracelet(260, 279, 441)}</g>',
    "_trai": f'    <g id="bong_tai">{earring(214, 108)}</g>\n    <g id="vong_tay">{bracelet(193, 212, 441)}</g>',
    "_sau": f'    <g id="bong_tai">{earring(163, 108)}{earring(237, 108)}</g>\n    <g id="vong_tay">{bracelet(121, 140, 441)}{bracelet(260, 279, 441)}</g>',
}


# ---------------------------------------------------------------- tổng hợp
def build():
    out = {}

    def put(name, note, views, ve_tay_phai=None):
        for v, body in views.items():
            out[f"{name}{v}"] = doc(name, v, note, body)
        if ve_tay_phai is not None:
            out[f"{name}_phai"] = doc(name, "_phai", note, ve_tay_phai, ve_tay=True)

    put("non_la", "Nón lá: chóp nón đỉnh y=0, vành y=66 (che tới trán), quai (màu điểm nhấn) vòng dưới cằm", {
        "": non_la(200, "M172 76 Q178 116 197 146 M228 76 Q222 116 203 146"),
        "_trai": non_la(204, "M196 76 Q190 110 176 140"),
        "_sau": non_la(200, None)})
    put("non_quai_thao", "Nón quai thao (nón ba tầm): mặt bằng rộng, vành đứng; quai thao (màu điểm nhấn) vòng dưới cằm, tua thả trước ngực", {
        # quai đi từ mép trong thành nón xuống sát hai bên má (ngoài mép mặt 165–235), ôm theo quai hàm rồi gặp nhau dưới cằm
        "": quai_thao(200, "M161 66 C158 96 162 120 178 136 Q190 146 199 149 M239 66 C242 96 238 120 222 136 Q210 146 201 149",
                      "M198 151 C195 190 192 220 190 240 M202 151 C205 190 208 220 210 240"),
        # nghiêng: quai chạy trước tai, men theo quai hàm xuống dưới cằm; không cắt qua mắt, má
        "_trai": quai_thao(204, "M208 66 C208 88 206 106 202 118 C196 132 186 142 174 147",
                           "M172 149 C168 186 166 216 164 240 M176 149 C176 186 176 216 176 240"),
        "_sau": quai_thao(200, "M161 66 C158 96 162 120 176 134 M239 66 C242 96 238 120 224 134", None)})
    put("khan_mo_qua", "Khăn mỏ quạ: vuông vải nhung đen trùm đầu, túm trước trán thành mỏ nhọn, hai góc buộc dưới cằm", MO_QUA)
    put("khan_xep", "Khăn xếp (khăn đóng) nam: vành khăn tròn cứng, nếp xếp chéo hình chữ nhân trước trán", KHAN_XEP)
    put("hoa_cai_toc", "Hoa cài tóc: cài bên trái người mẫu (phía có đường ngôi); nhìn từ bên phải thì bị đầu che", {
        "": flower(227, 60, 9), "_trai": flower(224, 58, 9), "_sau": flower(170, 62, 8)}, ve_tay_phai="")
    put("hai_theu", "Hài thêu: mũi cong, thân vải (màu điểm nhấn) thêu chỉ vàng, đế trắng", HAI)
    put("sneaker", "Sneaker trắng: thân trắng, đế xám nhạt, đai gót màu điểm nhấn", SNEAKER)
    put("giay_bup_be", "Giày búp bê nữ: mũi tròn, cổ thấp, nơ nhỏ ở mũi (màu điểm nhấn)", BUP_BE)
    put("giay_ta", "Giày ta nam: thân vải đen, đế trắng", GIAY_TA)
    put("kieng_bac", "Kiềng bạc: vòng cứng đeo ở chân cổ, phía trước trễ xuống", KIENG)
    put("trang_suc", "Trang sức: bông tai ngọc trai và vòng tay vàng ở cổ tay", TRANG_SUC)
    for g, h in HAND.items():
        k = 1.0 if g == "nu" else 1.1
        put(f"tui_{g}", "Túi cói xách tay (tay trái người mẫu), quai và viền miệng màu điểm nhấn", {
            "": tui(h["front"], k), "_trai": tui(h["side"], k), "_sau": tui(h["back"], k)})
        put(f"quat_giay_{g}", "Quạt giấy xoè cầm ở tay trái người mẫu, mặt quạt màu điểm nhấn, nan tre", {
            "": quat(h["front"], 472, 18, 112), "_trai": quat(h["side"], 472, 88, 172), "_sau": quat(h["back"], 472, 68, 162)})
    return out


def main():
    for name, svg in build().items():
        (FIG / f"{name}.svg").write_text(svg, encoding="utf-8")
        print("Đã tạo", f"accessory/{name}.svg")
    subprocess.run([sys.executable, str(Path(__file__).with_name("mirror_views.py"))], check=True)


if __name__ == "__main__":
    main()

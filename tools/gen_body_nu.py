"""Sinh body/body_nu.svg: thân người một khối liền, vẽ nửa trái rồi lật đối xứng sang phải.

Tỉ lệ khoảng 7,5 đầu. Mốc (khung 400x800, trục x=200):
  đỉnh đầu 42 · cằm 140 · vai 172–180 · ngực 238 · eo 318 · hông 414 · đáy chậu 440
  cổ tay 430 · đầu ngón tay 500 · gối 590 · mắt cá 748 · đáy chân 781
Chạy: python tools/gen_body_nu.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "frontend/src/assets/figure/body/body_nu.svg"

# Nửa trái, đi từ đỉnh cổ xuống tới đáy chậu (200, 440). ("C", c1, c2, p) hoặc ("L", p)
START = (189, 126)
LEFT = [
    ("L", (189, 158)),
    ("C", (180, 166), (160, 170), (150, 178)),     # cơ thang → đầu vai
    ("C", (141, 184), (138, 200), (138, 222)),     # cơ vai
    ("C", (137, 260), (131, 292), (129, 318)),     # bắp tay ngoài → khuỷu
    ("C", (127, 350), (124, 392), (123, 428)),     # cẳng tay ngoài → cổ tay
    ("C", (121, 440), (119, 452), (120, 464)),     # mu bàn tay
    ("C", (121, 474), (122, 486), (125, 494)),     # mép ngón út
    ("C", (126, 498), (129, 499), (130, 497)),     # đầu ngón út
    ("C", (131, 501), (134, 502), (135, 500)),     # đầu ngón áp út, ngón giữa
    ("C", (137, 502), (140, 500), (140, 496)),     # đầu ngón trỏ
    ("C", (141, 488), (140, 480), (141, 474)),     # mép trước ngón trỏ
    ("C", (142, 474), (144, 472), (144, 468)),     # đầu ngón cái
    ("C", (144, 460), (142, 450), (141, 444)),     # lưng ngón cái
    ("C", (140, 440), (139, 436), (138, 432)),     # cổ tay trong
    ("C", (139, 396), (143, 352), (145, 318)),     # cẳng tay trong → khuỷu trong
    ("C", (148, 290), (156, 250), (158, 222)),     # bắp tay trong → nách
    ("C", (159, 246), (167, 286), (168, 318)),     # sườn → eo
    ("C", (168, 350), (151, 380), (151, 414)),     # hông
    ("C", (151, 470), (160, 540), (164, 590)),     # đùi ngoài → gối
    ("C", (158, 630), (165, 700), (175, 748)),     # bắp chân ngoài → mắt cá
    ("C", (168, 758), (161, 768), (163, 776)),     # bàn chân
    ("C", (166, 782), (178, 782), (188, 781)),
    ("C", (195, 780), (198, 775), (196, 767)),
    ("L", (193, 748)),
    ("C", (192, 700), (190, 650), (190, 590)),     # bắp chân trong → gối trong
    ("C", (190, 540), (196, 480), (200, 440)),     # đùi trong → đáy chậu
]


# Bàn tay theo ảnh mẫu: ngắn lại còn HAND_K so với cổ tay (y=432), dài ≈0,6 chiều cao đầu
HAND_K = 0.86


def _hand(p):
    return (p[0], round(432 + (p[1] - 432) * HAND_K, 1)) if p[1] > 432 and p[0] < 150 else p


LEFT = [(seg[0],) + tuple(_hand(p) for p in seg[1:]) for seg in LEFT]
HAND_TF = f"matrix(1 0 0 {HAND_K} 0 {432 * (1 - HAND_K):g})"     # cho các nét kẻ ngón tay


def fmt(p):
    return f"{p[0]:g} {p[1]:g}"


def mirror(p):
    return (400 - p[0], p[1])


def body_path() -> str:
    parts = [f"M{fmt(START)}"]
    pts = [START]
    for seg in LEFT:
        parts.append(("L" + fmt(seg[1])) if seg[0] == "L" else
                     "C" + " ".join(fmt(x) for x in seg[1:]))
        pts.append(seg[-1])
    # Nửa phải: đi ngược lại từ đáy chậu lên đỉnh cổ, lật x
    for i in range(len(LEFT) - 1, -1, -1):
        seg, start = LEFT[i], pts[i]
        if seg[0] == "L":
            parts.append("L" + fmt(mirror(start)))
        else:
            c1, c2 = seg[1], seg[2]
            parts.append("C" + " ".join(fmt(mirror(x)) for x in (c2, c1, start)))
    parts.append("Z")
    return " ".join(parts)


SKIN = "#F4D2B8"
SKIN_SHADE = "#DEA585"      # bóng da (dùng với độ trong)
SKIN_LINE = "#6E4636"       # viền da mềm thay cho viền đen
HAIR = "#1C1714"
HAIR_LIGHT = "#4A3C34"
INK = "#1C1714"             # nét mắt, lông mày


def mirror_d(d: str) -> str:
    """Lật một chuỗi path chỉ gồm toạ độ tuyệt đối (M/L/C/Q/Z) qua trục x=200."""
    out, toks = [], d.replace(",", " ").split()
    is_x = True
    for t in toks:
        if t[0].isalpha():
            out.append(t[0]); t = t[1:]; is_x = True
            if not t:
                continue
        v = float(t)
        out.append(f"{(400 - v) if is_x else v:g}")
        is_x = not is_x
    return " ".join(out)


def both(d: str) -> str:
    return d + " " + mirror_d(d)


SHADES = [
    # sườn và hông
    "M160 232 C164 270 168 300 168 318 C168 342 160 372 155 404 L163 404 C168 372 175 342 175 318 C175 296 171 262 166 234 Z",
    # mặt trong cánh tay
    "M157 226 C153 262 146 300 145 318 C143 360 140 400 138 430 L133 430 C135 400 138 360 140 318 C142 296 149 258 153 228 Z",
    # mặt trong đùi và bắp chân
    "M199 446 C195 480 191 540 190 590 C190 650 192 700 193 747 L187 747 C186 700 184 650 184 590 C185 540 190 480 195 448 Z",
    # bóng gối
    "M168 596 Q177 604 186 596 Q177 600 168 596 Z",
    # bóng xương gò má và thái dương
    "M167 96 C168 108 172 118 178 124 C173 116 170 106 170 96 Z",
]

SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">
  <!-- Người mẫu nữ mặc định (đã mặc đồ lót trắng), tỉ lệ khoảng 7,5 đầu, phong cách bán tả thực: viền da mềm, đổ bóng bằng tông da đậm.
       File sinh tự động bằng tools/gen_body_nu.py, sửa trong script.
       Mốc: đỉnh đầu 42, cằm 140, vai 178, ngực 238, eo 318, hông 414, đáy chậu 440, gối 590, mắt cá 748, đáy chân 781 -->
  <defs>
    <clipPath id="clip_mat_trai"><path d="M176.5 92 Q185 84 194.5 90.5 Q186 97 176.5 92 Z"/></clipPath>
    <clipPath id="clip_mat_phai"><path d="M223.5 92 Q215 84 205.5 90.5 Q214 97 223.5 92 Z"/></clipPath>
  </defs>
  <g id="body_nu" stroke="{SKIN_LINE}" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round">

    <path id="toc_sau" transform="matrix(0.95 0 0 0.95 10 4.8)" d="M160 100 C154 66 170 34 200 34 C230 34 246 66 240 100 C238 106 234 110 228 112 L172 112 C166 110 162 106 160 100 Z" fill="{HAIR}" stroke="none"/>

    <path id="than_lien_khoi" fill="{SKIN}" d="{body_path()}"/>
    <path id="bong_than" fill="{SKIN_SHADE}" fill-opacity="0.45" stroke="none" d="{' '.join(both(d) for d in SHADES[:-1])}"/>

    <g id="chi_tiet_than" fill="none" stroke-opacity="0.7" stroke-width="1">
      <path id="xuong_quai_xanh" d="M178 177 Q188 181 196 179 M222 177 Q212 181 204 179"/>
      <path id="ron" d="M199 352 Q200 356 201 352"/>
      <path id="ke_ngon_chan" d="M170 774 Q173 771 177 774 M230 774 Q227 771 223 774"/>
    </g>
    <path id="ke_ngon_tay" transform="{HAND_TF}" fill="none" stroke-opacity="0.55" stroke-width="0.9" d="M130 497 Q129 488 127 480 M135 500 Q134 490 133 482 M141 474 Q140 465 141 457 M270 497 Q271 488 273 480 M265 500 Q266 490 267 482 M259 474 Q260 465 259 457"/>
    <!-- Đồ lót trắng mặc định: luôn đi kèm người mẫu, quần áo chọn thêm sẽ đè lên trên -->
    <g id="do_lot" stroke="#000" stroke-opacity="0.3" fill="#FFFFFF">
      <path id="day_ao" d="M178 176 L175 222 M222 176 L225 222" fill="none" stroke-width="5"/>
      <path id="day_ao_mau" d="M178 176 L175 222 M222 176 L225 222" fill="none" stroke="#FFFFFF" stroke-opacity="1" stroke-width="3"/>
      <path id="ao_lot" d="M160 232 C169 218 188 217 200 229 C212 217 231 218 240 232 C239.5 246 238 256 236.5 266 L163.5 266 C162 256 160.5 246 160 232 Z"/>
      <path id="vien_ao_lot" d="M162.5 258 L237.5 258" fill="none" stroke-opacity="0.2"/>
      <path id="quan_lot" d="M154.5 388 C178 394 222 394 245.5 388 C247.5 396 248.8 405 249 414 C236 422 214 432 204 445 L196 445 C186 432 164 422 151 414 C151.2 405 152.5 396 154.5 388 Z"/>
      <path id="cap_quan_lot" d="M153 397 C178 403 222 403 247 397" fill="none" stroke-opacity="0.2"/>
    </g>
    <path id="bong_co" d="M189 132 Q200 148 211 132 L211 150 Q200 158 189 150 Z" fill="{SKIN_SHADE}" fill-opacity="0.55" stroke="none"/>

    <g id="dau_nho" transform="matrix(0.95 0 0 0.95 10 4.8)">  <!-- đầu nhỏ 5% theo ảnh mẫu (≈7,9 đầu) -->
    <g id="tai" fill="{SKIN}">
      <path d="M166 86 C158 84 156 98 158 105 C159 111 163 114 167 112 Z"/>
      <path d="M234 86 C242 84 244 98 242 105 C241 111 237 114 233 112 Z"/>
      <path d="M163 92 Q161 99 164 106 M237 92 Q239 99 236 106" fill="none" stroke-opacity="0.6" stroke-width="0.9"/>
    </g>
    <path id="mat_ngoai" fill="{SKIN}" d="M166 86 C166 56 181 43 200 43 C219 43 234 56 234 86 C234 104 231 117 222 128 C215 136 207 140 200 140 C193 140 185 136 178 128 C169 117 166 104 166 86 Z"/>
    <path id="bong_mat" fill="{SKIN_SHADE}" fill-opacity="0.32" stroke="none" d="{both(SHADES[-1])} M197 108 Q200 111 203 108 Q200 109.5 197 108 Z"/>

    <g id="mat" stroke="{INK}">
      <path d="M176.5 92 Q185 84 194.5 90.5 Q186 97 176.5 92 Z" fill="#FFFFFF" stroke-width="0.7" stroke-opacity="0.6"/>
      <path d="M223.5 92 Q215 84 205.5 90.5 Q214 97 223.5 92 Z" fill="#FFFFFF" stroke-width="0.7" stroke-opacity="0.6"/>
      <g clip-path="url(#clip_mat_trai)" stroke="none">
        <circle cx="185.5" cy="90.6" r="4.4" fill="#3A2820"/><circle cx="185.5" cy="90.6" r="2" fill="#0E0B0A"/>
        <circle cx="187" cy="89" r="1.2" fill="#FFF"/>
      </g>
      <g clip-path="url(#clip_mat_phai)" stroke="none">
        <circle cx="214.5" cy="90.6" r="4.4" fill="#3A2820"/><circle cx="214.5" cy="90.6" r="2" fill="#0E0B0A"/>
        <circle cx="216" cy="89" r="1.2" fill="#FFF"/>
      </g>
      <path id="mi_tren" d="M175.5 92.5 Q185 83 195.5 90 M224.5 92.5 Q215 83 204.5 90" fill="none" stroke-width="2.3"/>
      <path id="duoi_mat" d="M178 93.5 Q186 96 192 93 M222 93.5 Q214 96 208 93" fill="none" stroke-width="0.7" stroke-opacity="0.4"/>
      <path id="nep_mi" d="M178 86.5 Q185.5 82 193 85.5 M222 86.5 Q214.5 82 207 85.5" fill="none" stroke-width="0.8" stroke-opacity="0.5"/>
      <path id="long_may" d="M174 80.5 Q183 75 195 78.5 Q184 77.5 174 82 Z M226 80.5 Q217 75 205 78.5 Q216 77.5 226 82 Z" fill="{HAIR}" stroke="{HAIR}" stroke-width="0.8"/>
    </g>
    <g id="mui" fill="none" stroke-width="1">
      <path d="M202.5 95 Q204 103 204.5 107.5" stroke-opacity="0.45"/>
      <path d="M195.5 110.5 Q197 113.5 199.5 112.5 M204.5 110.5 Q203 113.5 200.5 112.5"/>
    </g>
    <g id="moi" stroke="none">
      <path d="M191 123 Q195.5 119.5 200 121.5 Q204.5 119.5 209 123 Q200 125 191 123 Z" fill="#C9706C"/>
      <path d="M192 124 Q200 130.5 208 124 Q200 126 192 124 Z" fill="#D88A84"/>
      <path d="M191 123 Q200 125 209 123" fill="none" stroke="#8A4642" stroke-width="0.9"/>
      <path d="M197 128 Q200 129 203 128" fill="none" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="0.8"/>
    </g>
    <g id="ma_hong" fill="#E8998D" fill-opacity="0.22" stroke="none">
      <ellipse cx="178" cy="108" rx="7" ry="4"/><ellipse cx="222" cy="108" rx="7" ry="4"/>
    </g>

    <g id="toc" stroke="none">
      <!-- Tóc đen ôm sát đầu, rẽ ngôi giữa, vén ra sau tai (lộ tai), vấn búi thấp sau gáy -->
      <path d="M163 96 C156 70 167 38 200 34 C233 38 244 70 237 96 C236 90 234 85 232 80 C227 66 216 57 204 54 L200 50 L196 54 C184 57 173 66 168 80 C166 85 164 90 163 96 Z" fill="{HAIR}"/>
      <path id="lon_toc_sang" d="M196 40 Q176 46 168 70 M188 42 Q172 52 166 76 M204 40 Q224 46 232 70 M212 42 Q228 52 234 76" fill="none" stroke="{HAIR_LIGHT}" stroke-width="1.3"/>
      <path id="duong_ngoi" d="M200 36 L200 51" fill="none" stroke="#E2B89A" stroke-width="1.4"/>
    </g>
    </g>
  </g>
</svg>
"""

if __name__ == "__main__":
    OUT.write_text(SVG, encoding="utf-8")
    print("Đã tạo", OUT)

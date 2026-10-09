"""Sinh body/body_nam.svg: người mẫu nam một khối liền, vẽ nửa trái rồi lật đối xứng sang phải.

Cùng khung và cùng mốc đầu/chân với người mẫu nữ để dùng chung khăn, nón, giày:
  đỉnh đầu 42 · cằm 140 · vai 176 · ngực 238 · eo 318 · hông 414 · đáy chậu 440
  cổ tay 430 · đầu ngón tay ~503 · gối 590 · mắt cá 748 · đáy chân 781
Khác mẫu nữ: vai rộng, eo/hông thẳng, cổ và tay to hơn, hàm vuông, tóc ngắn.
Đồ lót mặc định: quần lót đùi (boxer) trắng, mép tính tự động theo số đo cơ thể.
Chạy: python tools/gen_body_nam.py
"""
from pathlib import Path

from figure_lib import body_path, both, outline, spans

OUT = Path(__file__).resolve().parents[1] / "public/figure/body/body_nam.svg"

START = (186, 126)
LEFT = [
    ("L", (186, 156)),
    ("C", (176, 164), (154, 166), (143, 174)),     # cơ thang → đầu vai
    ("C", (132, 180), (128, 198), (128, 222)),     # cơ vai
    ("C", (127, 262), (121, 292), (119, 318)),     # bắp tay ngoài → khuỷu
    ("C", (117, 352), (115, 392), (115, 428)),     # cẳng tay ngoài → cổ tay
    ("C", (113, 440), (111, 453), (112, 465)),     # mu bàn tay
    ("C", (113, 476), (114, 488), (117, 496)),     # mép ngón út
    ("C", (118, 500), (121, 501), (122, 499)),     # đầu ngón út
    ("C", (123, 503), (127, 504), (128, 502)),     # đầu ngón áp út, ngón giữa
    ("C", (130, 504), (134, 502), (134, 498)),     # đầu ngón trỏ
    ("C", (135, 490), (134, 482), (135, 476)),     # mép trước ngón trỏ
    ("C", (136, 476), (138, 474), (138, 470)),     # đầu ngón cái
    ("C", (138, 461), (136, 451), (135, 444)),     # lưng ngón cái
    ("C", (134, 440), (133, 436), (132, 432)),     # cổ tay trong
    ("C", (133, 396), (137, 352), (139, 318)),     # cẳng tay trong → khuỷu trong
    ("C", (142, 290), (150, 250), (152, 224)),     # bắp tay trong → nách
    ("C", (154, 250), (163, 288), (165, 318)),     # sườn → eo (thẳng hơn mẫu nữ)
    ("C", (165, 350), (157, 385), (156, 414)),     # hông
    ("C", (155, 470), (161, 540), (164, 590)),     # đùi ngoài → gối
    ("C", (157, 630), (165, 700), (175, 748)),     # bắp chân ngoài → mắt cá
    ("C", (168, 758), (161, 768), (163, 776)),     # bàn chân (giống mẫu nữ để dùng chung giày)
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

SKIN = "#EFC8A6"
SKIN_SHADE = "#D29A78"
SKIN_LINE = "#5E3A2C"
HAIR = "#161210"
HAIR_LIGHT = "#3E3530"
INK = "#161210"

SHADES = [
    "M154 232 C157 268 163 300 165 318 C165 344 159 376 157 404 L165 404 C167 376 172 344 172 318 C170 296 164 264 159 234 Z",  # sườn
    "M151 228 C147 262 140 300 139 318 C137 360 134 400 132 430 L127 430 C129 400 132 360 134 318 C136 296 143 258 147 230 Z",  # trong tay
    "M199 446 C195 480 191 540 190 590 C190 650 192 700 193 747 L187 747 C186 700 184 650 184 590 C185 540 190 480 195 448 Z",  # trong đùi
    "M168 596 Q177 604 186 596 Q177 600 168 596 Z",  # gối
]
FACE_SHADE = "M166 96 C167 110 172 122 180 130 C174 120 170 108 169 96 Z"


def boxer_path() -> str:
    """Quần lót đùi: mép ngoài bám hông/đùi (nới 0,8), gấu ở giữa đùi y=470, đáy ở y=446."""
    poly = outline(START, LEFT)
    top, hem, crotch, pad = 382, 470, 446, 0.8

    def outer_left(y):
        sp = spans(y, poly)
        body = [s for s in sp if s[0] > 145]        # bỏ đoạn tay
        return body[0][0] - pad

    def inner_left(y):
        sp = [s for s in spans(y, poly) if s[0] > 145]
        return sp[0][1] + pad if len(sp) > 1 else 200

    pts = [(outer_left(y), y) for y in range(top, hem + 1, 4)]
    pts.append((outer_left(hem), hem))
    pts += [(inner_left(y), y) for y in range(hem, crotch - 1, -4)]
    pts.append((200, crotch))
    left = " ".join(f"{x:.1f} {y}" for x, y in pts)
    right = " ".join(f"{400 - x:.1f} {y}" for x, y in reversed(pts[:-1]))
    return f"M{left} L{right} Q200 {top + 6} {pts[0][0]:.1f} {top} Z"


SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">
  <!-- Người mẫu nam mặc định (đã mặc quần lót đùi trắng), tỉ lệ khoảng 7,5 đầu, phong cách bán tả thực.
       File sinh tự động bằng tools/gen_body_nam.py, sửa trong script.
       Mốc: đỉnh đầu 42, cằm 140, vai 176, ngực 238, eo 318, hông 414, đáy chậu 440, gối 590, mắt cá 748, đáy chân 781 -->
  <defs>
    <clipPath id="clip_mat_trai_nam"><path d="M176.5 92 Q185 84 194.5 90.5 Q186 97 176.5 92 Z"/></clipPath>
    <clipPath id="clip_mat_phai_nam"><path d="M223.5 92 Q215 84 205.5 90.5 Q214 97 223.5 92 Z"/></clipPath>
  </defs>
  <g id="body_nam" stroke="{SKIN_LINE}" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round">

    <path id="toc_sau" d="M162 92 C158 58 176 30 204 28 C228 30 244 50 240 92 C240 100 236 104 234 104 L166 104 C164 104 162 100 162 92 Z" fill="{HAIR}" stroke="none"/>

    <path id="than_lien_khoi" fill="{SKIN}" d="{body_path(START, LEFT)}"/>
    <path id="bong_than" fill="{SKIN_SHADE}" fill-opacity="0.45" stroke="none" d="{' '.join(both(d) for d in SHADES)}"/>

    <g id="chi_tiet_than" fill="none" stroke-opacity="0.6" stroke-width="1">
      <path id="xuong_quai_xanh" d="M174 176 Q186 181 196 179 M226 176 Q214 181 204 179"/>
      <path id="co_nguc" d="M168 250 Q184 260 197 254 M232 250 Q216 260 203 254" stroke-opacity="0.4"/>
      <path id="ron" d="M199 352 Q200 356 201 352"/>
      <path id="ke_ngon_tay" transform="{HAND_TF}" stroke-opacity="0.55" stroke-width="0.9" d="M122 499 Q121 490 119 482 M128 502 Q127 492 126 484 M135 476 Q134 466 135 458 M278 499 Q279 490 281 482 M272 502 Q273 492 274 484 M265 476 Q266 466 265 458"/>
      <path id="ke_ngon_chan" d="M170 774 Q173 771 177 774 M230 774 Q227 771 223 774"/>
    </g>

    <!-- Đồ lót trắng mặc định: quần lót đùi, quần áo chọn thêm sẽ đè lên trên -->
    <g id="do_lot" stroke="#000" stroke-opacity="0.3" fill="#FFFFFF">
      <path id="quan_lot_dui" d="{boxer_path()}"/>
      <path id="cap_quan" d="M156 392 Q200 398 244 392" fill="none" stroke-opacity="0.25"/>
      <path id="duong_may" d="M200 400 L200 440" fill="none" stroke-opacity="0.2"/>
    </g>

    <path id="bong_co" d="M186 132 Q200 150 214 132 L214 150 Q200 158 186 150 Z" fill="{SKIN_SHADE}" fill-opacity="0.55" stroke="none"/>
    <path id="yet_hau" d="M198 150 Q200 154 202 150" fill="none" stroke-opacity="0.5" stroke-width="1"/>

    <g id="tai" fill="{SKIN}">
      <path d="M165 86 C156 83 154 98 156 106 C157 112 162 115 166 113 Z"/>
      <path d="M235 86 C244 83 246 98 244 106 C243 112 238 115 234 113 Z"/>
      <path d="M162 92 Q159 99 162 107 M238 92 Q241 99 238 107" fill="none" stroke-opacity="0.6" stroke-width="0.9"/>
    </g>
    <path id="mat_ngoai" fill="{SKIN}" d="M165 86 C165 56 181 42 200 42 C219 42 235 56 235 86 C235 101 234 113 230 122 C225 133 212 140 200 140 C188 140 175 133 170 122 C166 113 165 101 165 86 Z"/>
    <path id="bong_mat" fill="{SKIN_SHADE}" fill-opacity="0.32" stroke="none" d="{both(FACE_SHADE)} M196 108 Q200 112 204 108 Q200 110 196 108 Z"/>

    <g id="mat" stroke="{INK}">
      <path d="M176.5 92 Q185 84 194.5 90.5 Q186 97 176.5 92 Z" fill="#FFFFFF" stroke-width="0.7" stroke-opacity="0.6"/>
      <path d="M223.5 92 Q215 84 205.5 90.5 Q214 97 223.5 92 Z" fill="#FFFFFF" stroke-width="0.7" stroke-opacity="0.6"/>
      <g clip-path="url(#clip_mat_trai_nam)" stroke="none">
        <circle cx="185.5" cy="90.6" r="4.4" fill="#2E211B"/><circle cx="185.5" cy="90.6" r="2" fill="#0B0908"/>
        <circle cx="187" cy="89" r="1.2" fill="#FFF"/>
      </g>
      <g clip-path="url(#clip_mat_phai_nam)" stroke="none">
        <circle cx="214.5" cy="90.6" r="4.4" fill="#2E211B"/><circle cx="214.5" cy="90.6" r="2" fill="#0B0908"/>
        <circle cx="216" cy="89" r="1.2" fill="#FFF"/>
      </g>
      <path id="mi_tren" d="M175.5 92.5 Q185 83 195.5 90 M224.5 92.5 Q215 83 204.5 90" fill="none" stroke-width="2"/>
      <path id="nep_mi" d="M178 86.5 Q185.5 82 193 85.5 M222 86.5 Q214.5 82 207 85.5" fill="none" stroke-width="0.8" stroke-opacity="0.5"/>
      <path id="long_may" d="M171 81 Q183 75.5 196 78 L196 81.5 Q183 79.5 171 84.5 Z M229 81 Q217 75.5 204 78 L204 81.5 Q217 79.5 229 84.5 Z" fill="{HAIR}" stroke="none"/>
    </g>
    <g id="mui" fill="none" stroke-width="1.1">
      <path d="M203 94 Q205 103 205.5 108" stroke-opacity="0.45"/>
      <path d="M194.5 111 Q196.5 114.5 199.5 113 M205.5 111 Q203.5 114.5 200.5 113"/>
    </g>
    <g id="moi" stroke="none">
      <path d="M190 124 Q195 121.5 200 122.5 Q205 121.5 210 124 Q200 125.5 190 124 Z" fill="#B87A6C"/>
      <path d="M191.5 125 Q200 129.5 208.5 125 Q200 126.5 191.5 125 Z" fill="#C98E7E"/>
      <path d="M190 124 Q200 125.5 210 124" fill="none" stroke="#6E3E36" stroke-width="1"/>
    </g>
    <path id="cam" d="M195 134 Q200 136 205 134" fill="none" stroke-opacity="0.35" stroke-width="0.9"/>

    <g id="toc" stroke="none">
      <!-- Tóc nam ngắn: hai bên tỉa gọn sát thái dương, phần trên dày, mái vuốt lệch sang bên phải khung hình,
           chân tóc trán cong rõ; tóc mai ngắn trước tai -->
      <path d="M166 90 C163 74 163 58 169 47 C176 33 191 26 206 26 C223 27 237 35 240 51 C242 63 239 78 235 90
               C234 82 233 76 231 71 C229 66 226 63 222 62 C214 60 208 63 200 62 C193 61 186 58 180 60 C173 63 169 70 168 78 C167 82 166 86 166 90 Z" fill="{HAIR}"/>
      <path id="mai_vuot" d="M168 60 C176 44 196 38 214 42 C226 45 235 52 240 62 C232 56 222 54 212 56 C200 58 190 54 180 56 C175 57 171 59 168 60 Z" fill="{HAIR_LIGHT}" fill-opacity="0.35"/>
      <path id="lon_toc_sang" d="M174 48 Q196 34 224 40 M176 56 Q198 44 230 50 M206 30 Q226 32 236 44" fill="none" stroke="{HAIR_LIGHT}" stroke-width="1.3"/>
      <path id="toc_mai" d="M166.5 80 L166.5 95 M233.5 80 L233.5 95" fill="none" stroke="{HAIR}" stroke-width="2.6"/>
    </g>
  </g>
</svg>
"""

if __name__ == "__main__":
    OUT.write_text(SVG, encoding="utf-8")
    print("Đã tạo", OUT)

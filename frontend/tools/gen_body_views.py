"""Sinh người mẫu ở hướng nhìn TRÁI (nghiêng) và SAU cho cả nữ và nam. Hướng PHẢI do tools/mirror_views.py lật từ TRÁI.

Quy ước hướng nhìn (khung 400x800, cùng mốc y với hướng trước):
  _trai : nhìn từ phía bên trái người mẫu  -> người mẫu quay mặt sang TRÁI khung hình
  _phai : nhìn từ phía bên phải người mẫu  -> quay mặt sang PHẢI (ảnh lật của _trai)
  _sau  : nhìn từ sau lưng; đường bao giống hướng trước, chi tiết trong là lưng
Mốc chung: đỉnh đầu 42, cằm 140, vai 178, ngực 238, eo 318, hông 414, gối 590, mắt cá 748, đáy chân 781.
Tham khảo dáng nghiêng: "Profil du torse féminin et du torse masculin d'après Thomson" (Wikimedia Commons).
Chạy: python tools/gen_body_views.py
"""
from pathlib import Path

import gen_body_nam as NAM
import gen_body_nu as NU
from figure_lib import body_path, both

FIG = Path(__file__).resolve().parents[1] / "public/figure/body"
UW = 'stroke="#000" stroke-opacity="0.3" fill="#FFFFFF"'          # đồ lót trắng

# ---------------------------------------------------------------- hướng TRÁI (nghiêng, quay mặt sang trái)
PROFILE = {
    "nu": dict(
        body="M190 126 C188 140 186 152 184 164 C176 172 170 182 168 196 C164 212 158 226 158 240 "
             "C158 252 164 262 172 268 C176 288 178 304 180 318 C181 340 176 368 176 392 C176 410 177 428 178 444 "
             "C176 480 178 540 184 590 C186 610 186 630 188 660 C189 700 190 730 191 748 "
             "C186 756 168 764 156 772 C150 776 150 781 158 781 L208 781 C214 781 215 774 212 766 C210 758 208 752 207 746 "
             "C208 720 214 680 214 650 C214 626 210 604 207 590 C210 560 216 500 220 460 "
             "C226 440 230 420 228 404 C226 390 220 380 218 372 C214 352 214 334 216 318 "
             "C218 296 226 268 226 240 C226 214 222 196 216 182 C214 168 212 148 212 126 Z",
        arm="M216 182 C202 176 194 182 193 198 C192 240 194 290 196 318 C196 360 196 400 197 430 "
            "C194 446 192 466 194 482 C196 494 198 502 204 504 C208 500 210 490 210 478 "
            "C211 462 211 446 210 432 C211 400 214 360 214 318 C214 290 218 240 220 210 C220 196 220 188 216 182 Z",
        thumb="M197 444 C190 450 188 464 192 472 C194 468 196 460 197 454 Z",
        shade="M218 196 C224 214 225 236 224 254 L218 250 C219 232 218 214 214 200 Z "
              "M207 330 C210 350 212 372 216 384 L212 386 C208 372 206 352 205 332 Z "
              "M212 470 C210 520 206 560 205 590 L200 590 C201 560 205 520 208 472 Z "
              "M206 600 C210 620 211 640 210 660 L206 660 C206 640 205 620 203 602 Z",
        arm_shade="M214 210 C214 260 212 300 211 318 C211 360 209 400 208 430 L204 430 C205 400 207 360 208 318 C209 300 210 260 210 214 Z",
        head="M212 126 C232 122 244 106 244 86 C244 58 226 42 202 42 C182 42 168 54 164 72 C163 80 162 86 160 92 "
             "C158 96 156 100 154 106 C152 109 153 112 156 113 C158 114 159 116 158 119 C157 122 158 124 160 125 "
             "C158 127 158 129 160 131 C162 135 165 138 171 140 C180 141 192 136 200 126 Z",
        ear=(214, 98, 5.5, 10),
        eye=dict(white="M164.5 92 Q171 85.5 178.5 90.5 Q171 96.5 164.5 92 Z", iris=(168.8, 91, 3.4),
                 lid="M164 92.2 Q171 84.5 179 90.2", brow="M162.5 81.5 Q171 76.5 180.5 80"),
        nose="M156 112 Q159 113 162 111",
        lips=("M157 120 Q160 118.5 163.5 120.5 Q160 122 157 120.5 Z", "M158 124 Q161 127.5 165 125 Q161 125.5 158 124 Z",
              "M157.5 122 L165 122.5"),
        neck_shade="M190 130 C196 138 204 140 212 136 L212 150 C204 152 196 150 188 146 Z",
        hair="M164 74 C166 50 186 34 208 34 C234 34 250 56 248 86 C247 102 242 114 234 120 C230 112 228 104 226 96 "
             "C222 84 214 78 204 78 C196 78 190 74 182 72 C176 70 170 72 164 74 Z",
        hair_extra='<circle id="bui_toc" cx="249" cy="92" r="13"/>',
        hair_light="M176 46 Q196 36 220 42 M206 40 Q232 46 242 70 M243 86 Q251 82 256 92",
        underwear=f'''    <g id="do_lot" {UW}>
      <path id="day_ao" d="M199 180 L172 230" fill="none" stroke-width="5"/>
      <path id="day_ao_mau" d="M199 180 L172 230" fill="none" stroke="#FFFFFF" stroke-opacity="1" stroke-width="3"/>
      <path id="ao_lot" d="M162 226 C158 232 156 244 159 254 C162 262 168 266 174 268 L224 262 C226 250 226 238 225 228 Z"/>
      <path id="quan_lot" d="M177 392 L219 382 C225 392 229 402 229 414 C229 428 224 438 214 446 L180 444 C177 430 176 410 177 392 Z"/>
      <path id="cap_quan_lot" d="M177 400 L221 391" fill="none" stroke-opacity="0.2"/>
    </g>''',
        skin=NU.SKIN, shade_c=NU.SKIN_SHADE, line=NU.SKIN_LINE, hair_c=NU.HAIR, hair_l=NU.HAIR_LIGHT, ink=NU.INK,
        lip=("#C2706A", "#B5605A"),
    ),
    "nam": dict(
        body="M187 126 C186 140 185 152 183 164 C174 172 167 184 165 200 C163 216 163 232 164 248 "
             "C165 262 170 272 174 282 C176 296 177 308 178 318 C179 340 178 360 178 382 C177 404 176 424 176 444 "
             "C175 480 177 540 183 590 C185 610 186 630 188 660 C189 700 190 730 191 748 "
             "C186 756 168 764 156 772 C150 776 150 781 158 781 L208 781 C214 781 215 774 212 766 C210 758 208 752 207 746 "
             "C208 720 215 680 215 650 C215 626 211 604 207 590 C210 560 216 500 219 462 "
             "C224 444 227 424 226 406 C224 392 220 382 219 372 C218 352 218 334 219 318 "
             "C221 296 229 268 229 240 C229 214 225 194 218 180 C216 166 215 148 215 126 Z",
        arm="M219 180 C201 174 191 182 190 200 C189 240 191 290 193 318 C193 360 193 400 194 430 "
            "C190 446 188 468 190 484 C192 496 195 504 201 506 C206 502 208 492 208 480 "
            "C209 464 209 448 208 433 C209 400 212 360 213 318 C214 290 219 240 222 210 C223 196 223 186 219 180 Z",
        thumb="M194 444 C187 450 185 465 189 474 C191 470 193 462 194 455 Z",
        shade="M221 196 C227 214 228 236 227 254 L221 250 C222 232 221 214 217 200 Z "
              "M209 330 C212 350 214 372 218 384 L214 386 C210 372 208 352 207 332 Z "
              "M211 472 C209 520 206 560 205 590 L200 590 C201 560 204 520 207 474 Z "
              "M206 600 C210 620 212 640 211 660 L207 660 C207 640 205 620 203 602 Z",
        arm_shade="M216 210 C216 260 214 300 213 318 C213 360 211 400 210 430 L205 430 C206 400 208 360 209 318 C210 300 211 260 211 214 Z",
        head="M215 126 C234 122 244 106 244 86 C244 58 226 42 202 42 C182 42 168 54 164 72 C163 80 162 86 160 92 "
             "C158 97 155 102 152 107 C150 110 151 113 155 114 C157 115 158 117 157 120 C156 123 157 125 159 126 "
             "C157 128 157 130 159 132 C160 136 162 139 168 141 C178 143 192 140 204 128 Z",
        ear=(214, 97, 6, 11),
        eye=dict(white="M164.5 92 Q171 86 178.5 90.5 Q171 96 164.5 92 Z", iris=(168.8, 91, 3.2),
                 lid="M164 92.2 Q171 85 179 90.2", brow="M164.5 81 L182 79 L182 82.5 L164.5 84.5 Z"),
        nose="M155 113 Q158 114.5 162 112",
        lips=("M156 121 Q160 120 163 121 Q160 122 156 121.5 Z", "M157 124 Q160 126.5 164 125 Q160 125.3 157 124 Z",
              "M156.5 122.5 L164 123"),
        neck_shade="M188 130 C196 140 206 142 215 138 L215 152 C206 154 196 152 186 148 Z",
        hair="M162 82 C162 52 182 36 206 36 C232 36 248 56 246 86 C245 100 240 110 234 116 C230 108 227 100 225 94 "
             "C221 84 214 80 204 78 C192 76 180 68 170 72 C166 74 163 78 162 82 Z",
        hair_extra="",
        hair_light="M174 50 Q194 40 218 44 M206 42 Q230 48 240 68",
        underwear=f'''    <g id="do_lot" {UW}>
      <path id="quan_lot_dui" d="M178 382 L221 378 C225 392 228 404 228 418 C228 440 222 456 219 470 L176 470 C175 440 177 410 178 382 Z"/>
      <path id="cap_quan" d="M178 392 L222 388" fill="none" stroke-opacity="0.2"/>
    </g>''',
        skin=NAM.SKIN, shade_c=NAM.SKIN_SHADE, line=NAM.SKIN_LINE, hair_c=NAM.HAIR, hair_l=NAM.HAIR_LIGHT, ink=NAM.INK,
        lip=("#B97A6E", "#AD6E62"),
    ),
}


# ---------------------------------------------------------------- tóc theo từng góc nghiêng (rẽ ngôi bên TRÁI người mẫu)
# Toạ độ đều vẽ ở dáng quay mặt sang trái; góc "phai" được lật đối xứng sau khi ghép.
#   trai: thấy phía có đường ngôi -> tóc gọn, ôm đầu, lộ hết tai
#   phai: thấy phía tóc được vuốt sang -> tóc phồng hơn, che thái dương và mép trên tai
PART_LINE = "#E9BFA0"          # đường ngôi tóc nữ (lộ da đầu); tóc nam dùng rãnh tối
PART_LINE_NAM = "#5A463A"
HAIR_VIEWS = {
    "nu": {
        "trai": dict(
            hair="M166 72 C168 48 188 34 210 34 C234 34 250 56 248 86 C247 100 243 110 238 116 C232 112 228 104 224 98 "
                 "C222 88 216 82 208 80 C196 78 184 74 176 72 C172 72 168 72 166 72 Z",
            extra='<circle id="bui_toc" cx="241" cy="121" r="12.5"/>',
            light="M172 66 Q202 60 232 96 M186 54 Q216 52 238 88 M233 118 Q241 112 249 120",
            part=""),
        "phai": dict(                                            # rẽ ngôi giữa: hai bên đối xứng, giống góc trái
            hair="M166 72 C168 48 188 34 210 34 C234 34 250 56 248 86 C247 100 243 110 238 116 C232 112 228 104 224 98 "
                 "C222 88 216 82 208 80 C196 78 184 74 176 72 C172 72 168 72 166 72 Z",
            extra='<circle id="bui_toc" cx="241" cy="121" r="12.5"/>',
            light="M172 66 Q202 60 232 96 M186 54 Q216 52 238 88 M233 118 Q241 112 249 120",
            part=""),
    },
    "nam": {
        # Tóc nam ngắn cổ điển: hai bên cắt ngắn ôm đầu, tóc mai trước tai, gáy gọn lộ tai
        "trai": dict(
            hair="M168 66 C170 46 188 30 212 30 C236 30 250 50 247 82 C246 98 242 110 236 118 C232 116 230 110 229 104 "
                 "C227 96 225 90 222 86 C218 82 210 82 204 84 C200 86 198 92 196 98 L192 98 C192 90 192 82 190 76 "
                 "C184 70 176 66 168 66 Z",
            extra="",
            light="M190 66 Q206 70 224 84 M200 57 Q222 61 240 76 M184 49 Q208 39 236 42",
            part="M172 58 Q200 50 232 46"),
        "phai": dict(
            hair="M166 69 C164 46 184 27 212 27 C238 27 251 50 247 82 C246 98 242 110 236 118 C232 116 230 110 229 104 "
                 "C227 96 225 90 222 86 C218 82 210 82 204 84 C200 86 198 92 196 98 L192 98 C192 90 191 82 189 77 "
                 "C182 73 172 73 166 69 Z",
            extra="",
            light="M236 44 Q206 37 175 57 M240 60 Q210 52 182 67 M232 78 Q214 71 197 77",
            part=""),
    },
}


# ---------------------------------------------------------------- nới bề dày dáng nghiêng
import re as _re

WIDEN = {"nu": dict(body=(198, 1.25), arm=(205, 1.2)), "nam": dict(body=(200, 1.22), arm=(205, 1.2))}


def _scale_d(d: str, cx: float, k: float) -> str:
    """Nới toạ độ x quanh trục cx theo hệ số k; giảm dần về 1 từ y=736 tới y=762 để giữ cỡ bàn chân."""
    toks = _re.findall(r"[MLCQZmlcqz]|-?\d*\.?\d+", d)
    out, nums = [], []

    def flush():
        for i in range(0, len(nums) - 1, 2):
            x, y = nums[i], nums[i + 1]
            f = k if y <= 736 else (1 if y >= 762 else k + (1 - k) * (y - 736) / 26)
            out.append(f"{cx + (x - cx) * f:.1f} {y:g}")
        nums.clear()

    for t in toks:
        if t.isalpha():
            flush(); out.append(t)
        else:
            nums.append(float(t))
    flush()
    return " ".join(out)


def widen_block(svg: str, cx: float, k: float) -> str:
    """Áp _scale_d cho mọi thuộc tính d="..." trong một đoạn SVG."""
    return _re.sub(r'd="([^"]+)"', lambda m: f'd="{_scale_d(m.group(1), cx, k)}"', svg)


def _shorten_hand(d: str, k: float = 0.86) -> str:
    """Bàn tay theo ảnh mẫu: co các điểm dưới cổ tay (y>432) về phía cổ tay."""
    toks = _re.findall(r"[MLCQZmlcqz]|-?\d*\.?\d+", d)
    out, nums = [], []

    def flush():
        for i in range(0, len(nums) - 1, 2):
            x, y = nums[i], nums[i + 1]
            out.append(f"{x:g} {432 + (y - 432) * k if y > 432 else y:.1f}")
        nums.clear()

    for t in toks:
        if t.isalpha():
            flush(); out.append(t)
        else:
            nums.append(float(t))
    flush()
    return " ".join(out)


def profile_svg(g: str, view: str = "trai") -> str:
    p = dict(PROFILE[g])
    hv = HAIR_VIEWS[g][view]
    p["hair"], p["hair_extra"], p["hair_light"] = hv["hair"], hv["extra"], hv["light"]
    part_c = PART_LINE if g == "nu" else PART_LINE_NAM
    p["part"] = f'<path id="duong_ngoi" d="{hv["part"]}" fill="none" stroke="{part_c}" stroke-width="1.7"/>' if hv["part"] else ""
    (bcx, bk), (acx, ak) = WIDEN[g]["body"], WIDEN[g]["arm"]
    for key in ("body", "shade"):
        p[key] = _scale_d(p[key], bcx, bk)
    for key in ("arm", "arm_shade", "thumb"):
        p[key] = _shorten_hand(_scale_d(p[key], acx, ak))
    p["underwear"] = widen_block(p["underwear"], bcx, bk)
    e = p["eye"]
    cx, cy, rx, ry = p["ear"]
    ix, iy, ir = e["iris"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">
  <!-- Người mẫu {'nữ' if g == 'nu' else 'nam'} – hướng TRÁI (nhìn nghiêng, quay mặt sang trái khung hình). Sinh bằng tools/gen_body_views.py.
       Tay gần (tay trái người mẫu) vẽ đè lên thân; hai chân trùng nhau khi nhìn nghiêng. Đã mặc đồ lót trắng. -->
  <defs><clipPath id="clip_mat_nghieng_{g}"><path d="{e['white']}"/></clipPath></defs>
  <g id="body_{g}_trai" stroke="{p['line']}" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round">
    <path id="toc_sau" d="{p['hair']}" fill="{p['hair_c']}" stroke="none"/>
    <path id="than_lien_khoi" fill="{p['skin']}" d="{p['body']}"/>
    <path id="bong_than" fill="{p['shade_c']}" fill-opacity="0.45" stroke="none" d="{p['shade']}"/>
{p['underwear']}
    <path id="tay_gan" fill="{p['skin']}" d="{p['arm']}"/>
    <path id="bong_tay" fill="{p['shade_c']}" fill-opacity="0.45" stroke="none" d="{p['arm_shade']}"/>
    <path id="ngon_cai" fill="{p['skin']}" d="{p['thumb']}"/>
    <path id="bong_co" d="{p['neck_shade']}" fill="{p['shade_c']}" fill-opacity="0.55" stroke="none"/>
    <path id="dau" fill="{p['skin']}" d="{p['head']}"/>
    <ellipse id="tai" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{p['skin']}"/>
    <path id="vanh_tai" d="M{cx + 1} {cy - 5} Q{cx - 2} {cy} {cx + 1} {cy + 5}" fill="none" stroke-opacity="0.6" stroke-width="1"/>
    <g id="mat" stroke="{p['ink']}">
      <path d="{e['white']}" fill="#FFFFFF" stroke-width="0.8" stroke-opacity="0.6"/>
      <g clip-path="url(#clip_mat_nghieng_{g})" stroke="none">
        <circle cx="{ix}" cy="{iy}" r="{ir}" fill="#4A3426"/><circle cx="{ix - 0.6}" cy="{iy}" r="1.3" fill="#111"/>
      </g>
      <path d="{e['lid']}" fill="none" stroke-width="1.8"/>
      <path d="{e['brow']}" fill="{p['hair_c']}" stroke="{p['hair_c']}" stroke-width="2"/>
    </g>
    <path id="mui" d="{p['nose']}" fill="none" stroke-width="1"/>
    <g id="moi" stroke="none">
      <path d="{p['lips'][0]}" fill="{p['lip'][0]}"/><path d="{p['lips'][1]}" fill="{p['lip'][1]}"/>
      <path d="{p['lips'][2]}" fill="none" stroke="#7E4A42" stroke-width="0.8"/>
    </g>
    <g id="toc" stroke="none" fill="{p['hair_c']}">
      <path d="{p['hair']}"/>
      {p['hair_extra']}
      <path d="{p['hair_light']}" fill="none" stroke="{p['hair_l']}" stroke-width="1.4"/>
      {p['part']}
    </g>
  </g>
</svg>
"""


HEAD_SMALL = {"nu": 0.95, "nam": 1.0}         # đầu nữ nhỏ 5% theo ảnh mẫu (≈7,9 đầu), giống hướng trước


def shrink_head(svg: str, g: str, start_id: str, cx: float) -> str:
    """Co phần đầu (từ phần tử start_id tới hết nhóm tóc) và lớp tóc sau quanh tầm mắt (cx, 96)."""
    k = HEAD_SMALL[g]
    if k == 1:
        return svg
    tf = f'transform="matrix({k} 0 0 {k} {cx * (1 - k):g} {96 * (1 - k):g})"'
    a = svg.index(f'<path id="{start_id}"')
    a = svg.rfind("\n", 0, a) + 1
    b = svg.index("  </g>\n</svg>")
    svg = svg[:a] + f"    <g id=\"dau_nho\" {tf}>\n" + svg[a:b] + "    </g>\n" + svg[b:]
    return svg.replace('<path id="toc_sau" ', f'<path id="toc_sau" {tf} ', 1)


def mirror_to_right(svg: str, g: str) -> str:
    """Lật bản dáng nghiêng (đã ghép tóc phía vuốt) thành góc PHẢI. Đánh dấu VE_TAY để mirror_views.py không ghi đè."""
    import re
    body = re.search(r"<svg[^>]*>(.*)</svg>", re.sub(r"<!--.*?-->", "", svg, flags=re.S), re.S).group(1)
    body = re.sub(r'id="([^"]+)"', r'id="\1_phai"', body)
    body = re.sub(r"url\(#([^)]+)\)", r"url(#\1_phai)", body)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n'
            f'  <!-- VE_TAY: góc PHẢI người mẫu {"nữ" if g == "nu" else "nam"}, sinh bằng tools/gen_body_views.py '
            '(thân lật từ góc trái, tóc là phía được vuốt sang). mirror_views.py không ghi đè file này. -->\n'
            f'  <g transform="matrix(-1 0 0 1 400 0)">{body}</g>\n</svg>\n')


# ---------------------------------------------------------------- hướng SAU
BACK = {
    "nu": dict(
        hair="M158 96 C154 58 176 34 200 34 C224 34 246 58 242 96 C242 114 234 126 222 130 Q200 140 178 130 C166 126 158 114 158 96 Z",
        hair_extra='<ellipse id="bui_toc" cx="200" cy="124" rx="18" ry="12" stroke="#6A4E3E" stroke-width="1.4"/>',
        hair_light="M206 42 Q214 46 218 54 M176 60 Q186 96 190 118 M224 60 Q214 96 210 118 M200 48 Q196 88 198 114 M188 122 Q200 116 212 122 M188 128 Q200 132 212 128",
        ears=((163, 100), (237, 100)),
        details="M172 214 Q180 238 190 250 M228 214 Q220 238 210 250 M200 190 L200 380 "
                "M170 596 Q177 590 184 596 M230 596 Q223 590 216 596 M190 156 Q200 162 210 156",
        knuckles="M118 478 Q126 482 134 478 M282 478 Q274 482 266 478",
        underwear=f'''    <g id="do_lot" {UW}>
      <path id="day_ao" d="M178 177 L176 230 M222 177 L224 230" fill="none" stroke-width="5"/>
      <path id="day_ao_mau" d="M178 177 L176 230 M222 177 L224 230" fill="none" stroke="#FFFFFF" stroke-opacity="1" stroke-width="3"/>
      <path id="ao_lot" d="M160 230 L240 230 L240.5 248 L160 248 Z"/>
      <path id="quan_lot" d="M154.5 388 C178 393 222 393 245.5 388 C248 405 249 425 247 446 C230 452 214 452 200 446 C186 452 170 452 153 446 C151 425 152 405 154.5 388 Z"/>
      <path id="ke_mong" d="M200 404 L200 446 M153 397 C178 403 222 403 247 397" fill="none" stroke-opacity="0.22"/>
    </g>''',
        mod=NU, path=lambda: NU.body_path(),
    ),
    "nam": dict(
        hair="M162 92 C158 58 178 36 200 36 C222 36 242 58 238 92 C236 104 230 114 222 120 Q200 126 178 120 C170 114 164 104 162 92 Z",
        hair_extra="",
        hair_light="M194 46 Q206 42 212 52 M180 60 Q177 90 184 112 M220 60 Q223 90 216 112 M200 54 Q199 88 200 118",
        ears=((163, 97), (237, 97)),
        details="M166 212 Q176 240 190 254 M234 212 Q224 240 210 254 M200 190 L200 376 "
                "M170 596 Q177 590 184 596 M230 596 Q223 590 216 596 M188 156 Q200 162 212 156",
        knuckles="M110 478 Q118 482 127 478 M290 478 Q282 482 273 478",
        underwear=f'''    <g id="do_lot" {UW}>
      <path id="quan_lot_dui" d="{NAM.boxer_path()}"/>
      <path id="ke_mong" d="M200 400 L200 446 M156 392 Q200 398 244 392" fill="none" stroke-opacity="0.22"/>
    </g>''',
        mod=NAM, path=lambda: body_path(NAM.START, NAM.LEFT),
    ),
}


# Khối đầu nhìn từ sau (không viền, nằm dưới lớp tóc) để gáy nối liền với cổ
HEAD_BACK = {
    "nu": "M165 86 C165 56 180 42 200 42 C220 42 235 56 235 86 C235 104 232 118 222 128 C214 136 206 140 200 140 "
          "C194 140 186 136 178 128 C168 118 165 104 165 86 Z",
    "nam": "M164 86 C164 56 180 42 200 42 C220 42 236 56 236 86 C236 104 234 118 228 126 C220 136 208 140 200 140 "
           "C192 140 180 136 172 126 C166 118 164 104 164 86 Z",
}


def back_svg(g: str) -> str:
    b = BACK[g]
    m = b["mod"]
    shades = m.SHADES[:-1] if g == "nu" else m.SHADES          # bỏ bóng gò má (của mặt trước)
    (lx, ly), (rx, ry) = b["ears"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">
  <!-- Người mẫu {'nữ' if g == 'nu' else 'nam'} – hướng SAU. Đường bao giống hướng trước; chi tiết trong là lưng, gáy, khoeo chân.
       Sinh bằng tools/gen_body_views.py. Đã mặc đồ lót trắng. -->
  <g id="body_{g}_sau" stroke="{m.SKIN_LINE}" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round">
    <path id="than_lien_khoi" fill="{m.SKIN}" d="{b['path']()}"/>
    <path id="bong_than" fill="{m.SKIN_SHADE}" fill-opacity="0.45" stroke="none" d="{' '.join(both(d) for d in shades)}"/>
    <path id="chi_tiet_lung" d="{b['details']}" fill="none" stroke-opacity="0.45" stroke-width="1.1"/>
    <path id="mu_ban_tay" d="{b['knuckles']}" fill="none" stroke-opacity="0.5" stroke-width="0.9"/>
{b['underwear']}
    <path id="dau_sau" d="{HEAD_BACK[g]}" fill="{m.SKIN}" stroke="none"/>
    <ellipse cx="{lx}" cy="{ly}" rx="5" ry="10" fill="{m.SKIN}"/>
    <ellipse cx="{rx}" cy="{ry}" rx="5" ry="10" fill="{m.SKIN}"/>
    <g id="toc" stroke="none" fill="{m.HAIR}">
      <path d="{b['hair']}"/>
      {b['hair_extra']}
      <path d="{b['hair_light']}" fill="none" stroke="{m.HAIR_LIGHT}" stroke-width="1.4"/>
    </g>
  </g>
</svg>
"""


if __name__ == "__main__":
    for g in ("nu", "nam"):
        files = {
            "trai": shrink_head(profile_svg(g, "trai"), g, "bong_co", 204),
            "phai": mirror_to_right(shrink_head(profile_svg(g, "phai"), g, "bong_co", 204), g),
            "sau": shrink_head(back_svg(g), g, "dau_sau", 200),
        }
        for view, svg in files.items():
            out = FIG / f"body_{g}_{view}.svg"
            out.write_text(svg, encoding="utf-8")
            print("Đã tạo", out)

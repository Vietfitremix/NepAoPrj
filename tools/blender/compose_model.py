"""Ghép người mẫu SVG hoàn chỉnh từ ảnh render MakeHuman (render_model.py): thân, mặt, tóc đều từ cùng một mô hình 3D.

Mỗi góc nhìn gồm các lớp (giữ đúng id của người mẫu cũ để tools/gen_garment_views.py và view_measure.py dùng lại được):
  than_lien_khoi (hình bóng thân) → bong_than (2 tầng bóng đã làm mềm) → do_lot (đồ lót trắng tính theo mép thân thật)
  → [góc nghiêng] tay_gan + bong_tay + ngon_cai (tay gần, lớp riêng) → mat_toc: lòng trắng, tròng mắt, mi, lông mày, môi, nét mặt, tóc + ánh tóc
  (tách vùng từ lớp _id, lấy tròng mắt/môi/ánh tóc từ lớp _tex; tóc chỉ gồm phần nhìn thấy nên đè đúng lên mặt).
Toạ độ đường cong đã quy về khung 400x800 (không dùng transform), để các script đo đọc được trực tiếp.
Góc PHẢI: dựng như góc trái trên ảnh lật gương rồi lật lại (file đánh dấu VE_TAY để mirror_views.py không ghi đè).

Chạy: ai-service/.venv/Scripts/python tools/blender/compose_model.py nu .tools/render <thư_mục_ra>
"""
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import vtracer
from PIL import Image, ImageFilter

RES = 4
SKIN = {"nu": ("#F4D2B8", "#DEA585", "#6E4636"), "nam": ("#EFC8A6", "#D29A78", "#5E3A2C")}
HAIR = {"nu": "#1C1714", "nam": "#1A1512"}
UW = 'stroke="#000" stroke-opacity="0.3" stroke-width="1.3" fill="#FFFFFF"'


# ---------------------------------------------------------------- ảnh → đường cong
def load_alpha(path: Path, flip: bool) -> np.ndarray:
    im = Image.open(path)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return np.array(im)[..., 3] > 127


def smooth_mask(mask: np.ndarray, r: float = 2.0) -> np.ndarray:
    im = Image.fromarray((mask * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(r))
    return np.array(im) > 127


def trace(mask: np.ndarray, speckle=40) -> list[str]:
    """Vector hoá ảnh nhị phân → danh sách path d đã quy về toạ độ khung 400x800 (tuyệt đối, chỉ M/L/C/Z)."""
    img = Image.fromarray(np.where(mask, 0, 255).astype("uint8")).convert("RGB")
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "in.png", Path(td) / "out.svg"
        img.save(src)
        vtracer.convert_image_to_svg_py(str(src), str(dst), colormode="binary", mode="spline", filter_speckle=speckle,
                                        corner_threshold=70, length_threshold=8.0, splice_threshold=45, path_precision=1)
        svg = dst.read_text(encoding="utf-8")
    out = []
    for tag in re.findall(r"<path[^>]*>", svg):
        d = re.search(r'\sd="([^"]+)"', tag).group(1)
        t = re.search(r'transform="translate\(([-\d.]+),\s*([-\d.]+)\)"', tag)
        tx, ty = (float(t.group(1)), float(t.group(2))) if t else (0.0, 0.0)
        toks, is_x, res = re.findall(r"[MLCQZ]|-?\d*\.?\d+", d), True, []
        for tk in toks:
            if tk.isalpha():
                res.append(tk); is_x = True
            else:
                v = float(tk)
                res.append(f"{(v + tx) / RES:.1f}" if is_x else f"{(v + ty) / RES:.1f}")
                is_x = not is_x
        out.append(" ".join(res))
    return out


def shade_layers(gray: np.ndarray, mask: np.ndarray):
    """Hai tầng bóng mềm: làm mờ ảnh tô bóng rồi lấy ngưỡng theo phân bố sáng tối trong vùng cơ thể."""
    g = np.array(Image.fromarray((gray * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(9))).astype(float) / 255
    inside = g[mask]
    lo, hi = np.percentile(inside, 10), np.percentile(inside, 30)
    return (trace(smooth_mask(mask & (g < hi), 4), speckle=300), trace(smooth_mask(mask & (g < lo), 4), speckle=300))


# ---------------------------------------------------------------- đo mép thân ở toạ độ khung
class Spans:
    def __init__(self, mask: np.ndarray):
        self.m = mask[::RES, ::RES]                           # 400x800

    def row(self, y):
        r = self.m[int(round(y))]
        xs = np.flatnonzero(np.diff(np.concatenate([[0], r.astype(int), [0]])))
        return [(xs[i], xs[i + 1]) for i in range(0, len(xs), 2)]

    def around(self, y, x=200):
        """Đoạn chứa (hoặc gần nhất) cột x."""
        sp = self.row(y)
        if not sp:
            return None
        return min(sp, key=lambda s: 0 if s[0] <= x <= s[1] else min(abs(s[0] - x), abs(s[1] - x)))

    def outer(self, y):
        sp = self.row(y)
        return (sp[0][0], sp[-1][1]) if sp else None


def head_box(sp: Spans, side: bool):
    """Đỉnh sọ, cằm, bề ngang đầu (kể cả tai) hoặc mũi/gáy ở góc nghiêng, đo trên hình bóng đầu trọc của MakeHuman."""
    top = next(y for y in range(800) if sp.row(y))
    rows = range(top + 2, top + 150)
    if side:
        xs = [sp.outer(y) for y in rows]
        nose = min(x[0] for x in xs[:110] if x)
        back = max(x[1] for x in xs[:110] if x)
        return dict(top=top, nose=nose, back=back)
    widths = [(y, sp.around(y)) for y in rows]
    ymax, smax = max(widths[:100], key=lambda t: t[1][1] - t[1][0])
    wmax = smax[1] - smax[0]
    chin = next(y for y, s in widths if y > ymax and (s[1] - s[0]) < 0.62 * wmax)
    return dict(top=top, chin=chin, w=wmax, cx=(smax[0] + smax[1]) / 2)


# ---------------------------------------------------------------- mặt, tóc dựng từ MakeHuman (lớp id + lớp texture)
def load_rgb(path: Path, flip: bool) -> np.ndarray:
    im = Image.open(path).convert("RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return np.array(im).astype(int)


def id_regions(a: np.ndarray) -> dict:
    """Tách vùng theo màu phẳng của lớp id (màu đã qua quản lý màu nên so theo kênh trội, không so giá trị tuyệt đối)."""
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3] > 127
    return dict(hair=al & (g > r + 40) & (g > b + 40),
                eyes=al & (g > r + 40) & (b > r + 40) & (abs(g - b) < 60),
                brows=al & (b > r + 60) & (b > g + 60),
                lashes=al & (r > b + 60) & (g > b + 60) & (abs(r - g) < 60))


def face_hair(g: str, view: str, src: Path, flip: bool, body: np.ndarray) -> str:
    reg = id_regions(load_rgb(src / f"{g}_{view}_id.png", flip))
    tex = load_rgb(src / f"{g}_{view}_tex.png", flip)
    lum = tex[..., :3].mean(axis=2)
    out = []

    def add(pid, mask, attrs, speckle=4, blur=1.0):
        if mask.sum() < 4:
            return
        d = " ".join(trace(smooth_mask(mask, blur) if blur else mask, speckle=speckle))
        if d:
            out.append(f'<path id="{pid}" {attrs} d="{d}"/>')

    skin = body & ~reg["hair"] & ~reg["eyes"] & ~reg["brows"] & ~reg["lashes"]
    if view != "sau":
        eyes = reg["eyes"]
        add("long_trang", eyes, 'fill="#FBF8F4" stroke="none"', blur=0.8)
        if eyes.any():
            add("trong_mat", eyes & (lum < np.percentile(lum[eyes], 45)), 'fill="#3A2520" stroke="none"', blur=1.2)
        lash = (reg["lashes"] & (lum < 90)) | (dilate(eyes, 2) & ~eyes & reg["lashes"])
        add("mi_mat", lash, 'fill="#1E1612" stroke="none"', blur=1.0)
        add("long_may", dilate(reg["brows"], 3 if g == "nam" else 2), 'fill="#2B201B" fill-opacity="0.9" stroke="none"', blur=1.0)
        # môi: lớp riêng theo nhóm điểm "lips" (phần không bị tóc che), khe môi = nét tối nhất trong môi
        lips = load_alpha(src / f"{g}_{view}_lips.png", flip) & ~reg["hair"]
        lips = lips & ~dilate(~lips, 2 * RES)                    # nhóm "lips" ôm rộng hơn viền môi thật → thu vào ~1 đơn vị
        lip_col = '#D47F76" fill-opacity="0.85' if g == "nu" else '#C68C7C" fill-opacity="0.7'
        add("moi", lips, f'fill="{lip_col}" stroke="none"', speckle=20, blur=1.5)
        if lips.sum() > 40 * RES * RES:                          # khe môi: một nét liền theo hàng tối nhất của từng cột
            cols = np.flatnonzero(lips.any(axis=0))
            c0, c1 = cols[0] + RES, cols[-1] - RES
            pts = []
            for x in range(c0, c1 + 1, RES):
                ys = np.flatnonzero(lips[:, x])
                if len(ys) > 2 * RES:
                    pts.append((x, ys[np.argmin(lum[ys, x])]))
            if len(pts) > 2:
                yy = np.convolve([p[1] for p in pts], np.ones(5) / 5, mode="same")
                yy[:2], yy[-2:] = [p[1] for p in pts[:2]], [p[1] for p in pts[-2:]]
                d = "M" + " L".join(f"{x / RES:.1f} {y / RES:.1f}" for (x, _), y in zip(pts, yy))
                out.append(f'<path id="khe_moi" d="{d}" fill="none" stroke="#7A3E37" stroke-width="0.8" stroke-opacity="0.85"/>')
        # cánh mũi, lỗ mũi: điểm tối nhất trên da, giữa đáy mắt và môi
        rows, lrows = np.flatnonzero(eyes.any(axis=1)), np.flatnonzero(lips.any(axis=1))
        if len(rows) and len(lrows):
            zone = skin.copy()
            zone[:rows[-1] + 4 * RES] = False
            zone[lrows[0] - 1 * RES:] = False
            xs = np.flatnonzero(lips.any(axis=0))
            zone[:, :xs[0] - 4 * RES] = False
            zone[:, xs[-1] + 4 * RES:] = False
            if zone.any():
                add("net_mui", zone & (lum < np.percentile(lum[zone], 4)), 'fill="#8A5444" fill-opacity="0.7" stroke="none"',
                    speckle=12, blur=1.2)
    hair = reg["hair"]
    if hair.any():
        hl = lum[hair]
        add("toc", hair, f'fill="{HAIR[g]}" stroke="none"', speckle=30, blur=1.5)
        add("toc_toi", hair & (lum < np.percentile(hl, 18)), 'fill="#0B0807" fill-opacity="0.7" stroke="none"', speckle=30, blur=1.2)
        add("anh_toc", hair & (lum > np.percentile(hl, 65)), 'fill="#4A3E38" fill-opacity="0.55" stroke="none"', speckle=30, blur=1.5)
        add("anh_toc_sang", hair & (lum > np.percentile(hl, 90)), 'fill="#8C7D74" fill-opacity="0.5" stroke="none"', speckle=20, blur=1.2)
    return '    <g id="mat_toc">\n      ' + "\n      ".join(out) + "\n    </g>"


def landmarks(sp, hb):
    """Mốc dọc tính theo khoảng D = đỉnh đầu → đáy chậu (đo chắc chắn từ hình bóng), theo tỉ lệ cơ thể chuẩn:
    vai 0,35·D · đầu ngực 0,52·D · eo 0,73·D · cạp quần 0,86·D. hh = khoảng tương đương một chiều cao đầu (D/4)."""
    top = hb["top"]
    crotch = next(y for y in range(int(top + 300), 640) if not (sp.around(y)[0] <= 200 <= sp.around(y)[1]))
    D = crotch - top
    return dict(hh=D / 4, shoulder=top + 0.35 * D, bust=top + 0.52 * D, waist=top + 0.73 * D, pant=top + 0.86 * D, crotch=crotch)


# ---------------------------------------------------------------- đồ lót trắng theo mép thân thật
def P(x, y):
    return f"{x:.1f} {y:.1f}"


def underwear_front(g, sp, lm, back=False):
    L = lambda y: sp.around(y)[0] - 0.6
    R = lambda y: sp.around(y)[1] + 0.6
    crotch, hh = lm["crotch"], lm["hh"]
    out = []
    if g == "nu":
        t, b_ = lm["bust"] - 0.28 * hh, lm["bust"] + 0.26 * hh
        if back:
            band = f"M{P(L(t + 4), t + 4)} L{P(R(t + 4), t + 4)} L{P(R(t + 18), t + 18)} L{P(L(t + 18), t + 18)} Z"
        else:
            band = (f"M{P(L(t), t)} Q{P(L(t) + 16, t - 12)} {P(200, t + 2)} Q{P(R(t) - 16, t - 12)} {P(R(t), t)} "
                    f"L{P(R(b_), b_)} L{P(L(b_), b_)} Z")
        ys = lm["shoulder"]
        w = sp.around(ys)
        sx = 0.22 * (w[1] - w[0])
        ty = t + (4 if back else -2)
        k = 8 if back else 14
        straps = f"M{P(200 - sx, ys)} L{P(L(t) + k, ty)} M{P(200 + sx, ys)} L{P(R(t) - k, ty)}"
        out.append(f'<path id="day_ao" d="{straps}" fill="none" stroke-width="5"/>')
        out.append(f'<path id="day_ao_mau" d="{straps}" fill="none" stroke="#FFFFFF" stroke-opacity="1" stroke-width="3"/>')
        out.append(f'<path id="ao_lot" d="{band}"/>')
        top = lm["pant"]
        side_y = top + 0.22 * hh
        if back:
            s2 = side_y + 18
            pant = (f"M{P(L(top), top)} Q{P(200, top + 5)} {P(R(top), top)} L{P(R(s2), s2)} "
                    f"Q{P(R(s2) - 10, crotch + 6)} {P(200, crotch + 2)} Q{P(L(s2) + 10, crotch + 6)} {P(L(s2), s2)} Z")
        else:
            pant = (f"M{P(L(top), top)} Q{P(200, top + 6)} {P(R(top), top)} L{P(R(side_y), side_y)} "
                    f"Q{P(R(side_y) - 26, crotch - 6)} {P(208, crotch + 3)} L{P(192, crotch + 3)} "
                    f"Q{P(L(side_y) + 26, crotch - 6)} {P(L(side_y), side_y)} Z")
        out.append(f'<path id="quan_lot" d="{pant}"/>')
        out.append(f'<path id="cap_quan_lot" d="M{P(L(top + 8), top + 8)} Q{P(200, top + 14)} {P(R(top + 8), top + 8)}" fill="none" stroke-opacity="0.2"/>')
    else:
        top, hem = int(lm["pant"]), int(crotch + 0.32 * hh)
        left = [(L(y), y) for y in range(top, crotch, 4)]
        right = [(R(y), y) for y in range(crotch - 4, top - 1, -4)]
        legL = [(sp.around(y, 180)[0] - 0.8, y) for y in range(crotch, hem + 1, 4)]
        legR = [(sp.around(y, 220)[1] + 0.8, y) for y in range(hem, crotch - 1, -4)]
        inL, inR = sp.around(hem, 180)[1] + 0.8, sp.around(hem, 220)[0] - 0.8
        pts = left + legL + [(inL, hem), (200, crotch + 2), (inR, hem)] + legR + right
        out.append(f'<path id="quan_lot_dui" d="M{" L".join(P(x, y) for x, y in pts)} Z"/>')
        out.append(f'<path id="cap_quan" d="M{P(L(top + 8), top + 8)} Q{P(200, top + 13)} {P(R(top + 8), top + 8)}" fill="none" stroke-opacity="0.25"/>')
    if back:
        out.append(f'<path id="ke_mong" d="M200 {lm["pant"] + 14:.1f} L200 {crotch}" fill="none" stroke-opacity="0.22"/>')
    return f'    <g id="do_lot" {UW}>\n      ' + "\n      ".join(out) + "\n    </g>"


def underwear_side(g, body, lm):
    F = lambda y: body.outer(y)[0] - 0.6
    B = lambda y: body.outer(y)[1] + 0.6
    out = []
    if g == "nu":
        hh = lm["hh"]
        t, b_ = int(lm["bust"] - 0.28 * hh), int(lm["bust"] + 0.26 * hh)
        cup = [(F(y), y) for y in range(t, b_, 4)]
        back = [(B(y), y) for y in range(t + 24, t + 3, -4)]
        band = "M" + " L".join(P(x, y) for x, y in cup + back) + " Z"
        mid = (F(t + 6) + B(t + 6)) / 2
        strap = f"M{P(mid, lm['shoulder'])} L{P(F(t) + 10, t)}"
        out += [f'<path id="day_ao" d="{strap}" fill="none" stroke-width="5"/>',
                f'<path id="day_ao_mau" d="{strap}" fill="none" stroke="#FFFFFF" stroke-opacity="1" stroke-width="3"/>',
                f'<path id="ao_lot" d="{band}"/>']
        rng = (int(lm["pant"]), int(lm["crotch"] + 4))
    else:
        rng = (int(lm["pant"]), int(lm["crotch"] + 0.32 * lm["hh"]))
    front = [(F(y), y) for y in range(rng[0], rng[1] + 1, 4)]
    backe = [(B(y), y) for y in range(rng[1], rng[0] - 1, -4)]
    out.append(f'<path id="{"quan_lot" if g == "nu" else "quan_lot_dui"}" d="M{" L".join(P(x, y) for x, y in front + backe)} Z"/>')
    out.append(f'<path id="cap_quan" d="M{P(F(rng[0] + 8), rng[0] + 8)} L{P(B(rng[0] + 8), rng[0] + 8)}" fill="none" stroke-opacity="0.22"/>')
    return f'    <g id="do_lot" {UW}>\n      ' + "\n      ".join(out) + "\n    </g>"


def dilate(m, r=3 * RES):
    im = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(2 * (r // 2) + 1))
    return np.array(im) > 127


def arm_mask_capped(arm: np.ndarray) -> np.ndarray:
    """Bo tròn đỉnh vai của lớp tay gần (ảnh render cắt ngang vai thành răng cưa)."""
    m = arm.copy()
    rows = np.flatnonzero(m.any(axis=1))
    top = rows[0]
    cut = top + 14 * RES
    xs = np.flatnonzero(m[cut])
    cx, rx = (xs[0] + xs[-1]) / 2, (xs[-1] - xs[0]) / 2 + RES
    m[:cut] = False
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    cap = (((xx - cx) / rx) ** 2 + ((yy - cut) / (14 * RES)) ** 2 <= 1) & (yy < cut)
    return m | cap


# ---------------------------------------------------------------- dựng từng góc
def build(g: str, view: str, src: Path) -> str:
    skin, shade, line = SKIN[g]
    side = view in ("trai", "phai")
    flip = view == "phai"
    mask = smooth_mask(load_alpha(src / f"{g}_{view}_mask.png", flip))
    gim = Image.open(src / f"{g}_{view}_shade.png")
    if flip:
        gim = gim.transpose(Image.FLIP_LEFT_RIGHT)
    gray = np.array(gim.convert("L")).astype(float) / 255
    body = trace(mask, speckle=40)
    mid, dark = shade_layers(gray, mask)
    gid = f"body_{g}" + ("" if view == "truoc" else f"_{view}")
    parts = []
    front_mask = smooth_mask(load_alpha(src / f"{g}_truoc_mask.png", False))
    front_arms = load_alpha(src / f"{g}_truoc_arm.png", False)
    lm = landmarks(Spans(front_mask & ~dilate(front_arms)), head_box(Spans(front_mask), False))
    arms_raw = load_alpha(src / f"{g}_{view}_arm.png", flip)
    if not side:
        parts.append(underwear_front(g, Spans(mask & ~dilate(arms_raw)), lm, back=view == "sau"))
    arm_xml = ""
    if side:
        arm = smooth_mask(arm_mask_capped(arms_raw))
        parts.append(underwear_side(g, Spans(mask & ~arm), lm))
        arm_d = " ".join(trace(arm, speckle=40))
        a_mid, a_dark = shade_layers(gray, arm)
        cut = np.flatnonzero(arm.any(axis=1))[0] / RES + 9
        arm_xml = (f'    <clipPath id="duoi_vai"><rect x="0" y="{cut:.1f}" width="400" height="{800 - cut:.1f}"/></clipPath>\n'
                   f'    <path id="tay_gan" fill="{skin}" stroke="none" d="{arm_d}"/>\n'
                   f'    <path id="bong_tay" fill="{shade}" fill-opacity="0.4" stroke="none" d="{" ".join(a_mid + a_dark)}"/>\n'
                   f'    <path id="vien_tay" fill="none" clip-path="url(#duoi_vai)" d="{arm_d}"/>\n'
                   f'    <path id="ngon_cai" fill="none" stroke="none" d="M0 0"/>')
    head_xml = face_hair(g, view, src, flip, mask)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n'
           f'  <!-- {"VE_TAY: " if flip else ""}Người mẫu {"nữ" if g == "nu" else "nam"} – góc {view}. Thân dựng bằng MakeHuman (MPFB2, CC0) trong Blender, '
           f'render trực giao rồi vector hoá (tools/blender/render_model.py, compose_model.py); mặt, mắt, lông mày, tóc cũng từ MakeHuman. '
           f'Đã mặc đồ lót trắng. -->\n'
           f'  <g id="{gid}" stroke="{line}" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round">\n'
           f'    <path id="than_lien_khoi" fill="{skin}" d="{" ".join(body)}"/>\n'
           f'    <path id="bong_than" fill="{shade}" fill-opacity="0.32" stroke="none" d="{" ".join(mid)}"/>\n'
           f'    <path id="bong_than_dam" fill="{shade}" fill-opacity="0.4" stroke="none" d="{" ".join(dark)}"/>\n'
           + "\n".join(parts) + "\n" + arm_xml + "\n"
           + head_xml + "\n"
           f'  </g>\n</svg>\n')
    if flip:                                                  # lật lại thành góc phải
        inner = re.search(r"<svg[^>]*>\n(.*)</svg>", svg, re.S).group(1)
        inner = re.sub(r'id="([^"]+)"', r'id="\1_phai"', inner).replace(f'id="{gid}_phai"', f'id="{gid}"')
        inner = re.sub(r"url\(#([^)]+)\)", r"url(#\1_phai)", inner)
        head, rest = inner.split("\n", 1)
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 800">\n' + head + "\n"
               f'  <g transform="matrix(-1 0 0 1 400 0)">\n{rest}  </g>\n</svg>\n')
    return svg


if __name__ == "__main__":
    g, src, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    for v in ("truoc", "trai", "phai", "sau"):
        p = out / f"body_{g}{'' if v == 'truoc' else '_' + v}.svg"
        p.write_text(build(g, v, src), encoding="utf-8")
        print("Đã tạo", p, f"{p.stat().st_size // 1024} KB")

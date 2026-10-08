"""Chỉnh quần áo, quần/váy, phụ kiện cho vừa người mẫu MỚI bằng phép uốn thin-plate spline (TPS) theo từng hướng nhìn.

Ý tưởng: người mẫu cũ và mới cùng khung 400x800, cùng tư thế. Ở mỗi hướng nhìn, lấy hình bóng đầy đủ (thân + tay + đầu + tóc)
của hai người mẫu, ghép cặp mép hình bóng theo từng hàng (sau khi quy đổi độ cao theo các mốc đỉnh đầu, cổ, đáy chậu,
mắt cá, đáy chân) → tập điểm tương ứng cũ → mới. TPS nội suy trơn tập điểm đó thành phép uốn cả khung, rồi áp lên MỌI toạ độ
của asset (path, circle, ellipse, rect; phần tử nằm trong <g transform> được quy về khung trước khi uốn).
Chi tiết vẽ tay của quần áo được giữ nguyên, chỉ co giãn theo dáng người mới; mép áo đang ôm mép người cũ sẽ ôm mép người mới.

Hướng PHẢI không uốn trực tiếp: uốn *_trai.svg và *_phai_them.svg rồi chạy tools/mirror_views.py.

Chạy: python tools/refit_to_body.py <thư_mục_người_mẫu_cũ> <thư_mục_người_mẫu_mới> [file.svg ...]
      (không ghi file → uốn mọi asset trong garment/, bottom/, accessory/ trừ *_phai.svg)
"""
import io
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import resvg_py
from PIL import Image, ImageFilter

FIG = Path(__file__).resolve().parents[1] / "frontend/src/assets/figure"
DATA = Path(__file__).resolve().parents[1] / "data"
RENDER = Path(__file__).resolve().parents[1] / ".tools/render"            # lớp tay của người mẫu mới (render_model.py)
SC = 2                                                     # độ phân giải dựng hình bóng (điểm ảnh / đơn vị khung)
VIEW_SUFFIX = {"truoc": "", "trai": "_trai", "phai": "_phai", "sau": "_sau"}


# ---------------------------------------------------------------- hình bóng và mốc
def silhouette(svg_file: Path) -> np.ndarray:
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg_file.read_text(encoding="utf-8"), width=400 * SC, height=800 * SC))
    a = Image.open(io.BytesIO(png)).getchannel("A").filter(ImageFilter.GaussianBlur(1.5))
    return np.array(a) > 110


def segments(row: np.ndarray, min_len=2.0, min_gap=1.5):
    xs = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(int), [0]])))
    seg = [[xs[i] / SC, xs[i + 1] / SC] for i in range(0, len(xs), 2)]
    merged = []
    for s in seg:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [s for s in merged if s[1] - s[0] >= min_len]


def arm_mask(png: Path) -> np.ndarray:
    """Lớp tay render riêng của người mẫu mới (render_model.py, độ phân giải gấp 4) → cùng lưới với silhouette()."""
    im = Image.open(png).getchannel("A").resize((400 * SC, 800 * SC), Image.BILINEAR)
    return np.array(im) > 127


def row_segments(m: np.ndarray, arm, y: float):
    """Các đoạn hình bóng ở độ cao y. Có lớp tay thì tách tay khỏi thân kể cả chỗ tay áp sát thân (vùng nách),
    để mép trong tay áo cũ ứng đúng mép trong cánh tay mới và mép thân áo ứng đúng mép thân mới."""
    r = min(int(y * SC), m.shape[0] - 1)
    if arm is None:
        return segments(m[r])
    a = arm[r] & m[r]
    return sorted(segments(m[r] & ~a) + segments(a), key=lambda s: s[0])


def landmarks(m: np.ndarray) -> list[float]:
    """Mốc dọc (đơn vị khung): đỉnh, cổ, đáy chậu, mắt cá, đáy chân — đo trên hình bóng hướng trước.
    (Không dùng nách: tay ép sát thân thì khe nách lộ ra thấp hơn nách thật, làm lệch cả vùng ngực.)"""
    rows = np.flatnonzero(m.any(axis=1))
    top, sole = rows[0] / SC, rows[-1] / SC
    H = sole - top
    width = lambda y: sum(b - a for a, b in segments(m[int(y * SC)]))
    neck = min(np.arange(top + 0.09 * H, top + 0.2 * H, 0.5), key=width)
    crotch = next(y for y in np.arange(top + 0.45 * H, top + 0.62 * H, 0.5) if not m[int(y * SC), 200 * SC])
    ankle = min(np.arange(sole - 0.08 * H, sole - 0.02 * H, 0.5), key=width)
    return [top, neck, crotch, ankle, sole]


# ---------------------------------------------------------------- thin-plate spline
class TPS:
    def __init__(self, src: np.ndarray, dst: np.ndarray, lam=0.002):
        self.c = src
        n = len(src)
        K = self._U(np.linalg.norm(src[:, None] - src[None], axis=2))
        P = np.hstack([np.ones((n, 1)), src])
        A = np.zeros((n + 3, n + 3))
        A[:n, :n] = K + lam * np.mean(np.abs(K)) * np.eye(n)
        A[:n, n:], A[n:, :n] = P, P.T
        b = np.zeros((n + 3, 2))
        b[:n] = dst
        sol = np.linalg.solve(A, b)
        self.w, self.a = sol[:n], sol[n:]

    @staticmethod
    def _U(r):
        with np.errstate(divide="ignore", invalid="ignore"):
            u = r * r * np.log(r)
        return np.nan_to_num(u)

    def __call__(self, pts: np.ndarray) -> np.ndarray:
        pts = np.atleast_2d(pts)
        U = self._U(np.linalg.norm(pts[:, None] - self.c[None], axis=2))
        return self.a[0] + pts @ self.a[1:] + U @ self.w

    def jac(self, p, h=0.5):
        p = np.asarray(p, float)
        dx = (self(p + [h, 0]) - self(p - [h, 0]))[0] / (2 * h)
        dy = (self(p + [0, h]) - self(p - [0, h]))[0] / (2 * h)
        return np.column_stack([dx, dy])


class Affine:
    """Phép affine khớp bình phương nhỏ nhất (dùng cho đồ đội đầu: nón, khăn là vật cứng, không nên uốn cong)."""

    def __init__(self, src: np.ndarray, dst: np.ndarray):
        A = np.hstack([src, np.ones((len(src), 1))])
        self.T = np.linalg.lstsq(A, dst, rcond=None)[0]           # 3x2

    def __call__(self, pts):
        pts = np.atleast_2d(pts)
        return np.hstack([pts, np.ones((len(pts), 1))]) @ self.T

    def jac(self, p):
        return self.T[:2].T


def build_warp(old_m: np.ndarray, new_m: np.ndarray, lm_old, lm_new, new_arm=None, head_only=False):
    src, dst = [], []
    for y in np.arange(lm_old[0] - 1, lm_old[-1] + 0.5, 3.0):
        yn = float(np.interp(y, lm_old, lm_new))
        so = row_segments(old_m, None, y)
        sn = row_segments(new_m, new_arm, yn)
        if not so or not sn:
            continue
        if len(so) != len(sn):                           # cấu trúc khác nhau (vd. tay chạm thân ở một bên): chỉ ghép mép ngoài
            so, sn = [[so[0][0], so[-1][1]]], [[sn[0][0], sn[-1][1]]]
        for (a, b), (c, d) in zip(so, sn):
            src += [(a, y), (b, y)]
            dst += [(c, yn), (d, yn)]
    # neo ngoài khung: phần xa người mẫu chỉ co giãn dọc theo mốc, ngang giữ nguyên tâm
    for y in (lm_old[0] - 40, lm_old[-1] + 15):
        yn = float(np.interp(y, lm_old, lm_new, left=lm_new[0] + (y - lm_old[0]), right=lm_new[-1] + (y - lm_old[-1])))
        for x in (-150, 200, 550):
            src.append((x, y)); dst.append((x, yn))
    src, dst = np.array(src, float), np.array(dst, float)
    if head_only:                                         # chỉ các điểm vùng đầu (đỉnh → cổ) → affine
        keep = src[:, 1] <= lm_old[1] + 5
        return Affine(src[keep], dst[keep])
    if len(src) > 900:                                    # giới hạn số điểm cho hệ phương trình nhỏ gọn
        keep = np.linspace(0, len(src) - 1, 900).astype(int)
        src, dst = src[keep], dst[keep]
    return TPS(src, dst)


# ---------------------------------------------------------------- biến đổi affine của <g transform>
def parse_transform(t: str) -> np.ndarray:
    M = np.eye(3)
    for name, args in re.findall(r"(\w+)\(([^)]*)\)", t or ""):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "matrix":
            T = np.array([[v[0], v[2], v[4]], [v[1], v[3], v[5]], [0, 0, 1]])
        elif name == "translate":
            T = np.array([[1, 0, v[0]], [0, 1, v[1] if len(v) > 1 else 0], [0, 0, 1]])
        elif name == "scale":
            T = np.diag([v[0], v[1] if len(v) > 1 else v[0], 1])
        elif name == "rotate":
            a = math.radians(v[0]); cx, cy = (v[1], v[2]) if len(v) > 2 else (0, 0)
            R = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
            T = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]]) @ R @ np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]])
        else:
            raise ValueError(f"transform chưa hỗ trợ: {name}")
        M = M @ T
    return M


class LocalWarp:
    """Uốn trong hệ toạ độ cục bộ của phần tử: cục bộ → khung (M) → uốn → cục bộ (M⁻¹)."""

    def __init__(self, tps, M: np.ndarray):
        self.t, self.M, self.Mi = tps, M, np.linalg.inv(M)

    def pts(self, P):
        P = np.atleast_2d(np.asarray(P, float))
        Q = (self.M[:2, :2] @ P.T).T + self.M[:2, 2]
        W = self.t(Q)
        return (self.Mi[:2, :2] @ W.T).T + self.Mi[:2, 2]

    def jac(self, p):
        q = self.M[:2, :2] @ np.asarray(p, float) + self.M[:2, 2]
        return self.Mi[:2, :2] @ self.t.jac(q) @ self.M[:2, :2]


# ---------------------------------------------------------------- path
def fmt(v):
    s = f"{v:.1f}"
    return "0.0" if s == "-0.0" else s


def warp_path(d: str, W: LocalWarp) -> str:
    toks = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", d)
    out, i, cmd = [], 0, None
    cur, start = np.zeros(2), np.zeros(2)
    nums = lambda n: [float(x) for x in toks[i:i + n]]
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
            if cmd in "Zz":
                out.append("Z"); cur = start.copy()
                continue
        up, rel = cmd.upper(), cmd.islower()
        base = cur if rel else np.zeros(2)
        if up in "ML":
            x, y = nums(2); i += 2
            p = base + [x, y]
            q = W.pts(p)[0]
            out.append(f"{up} {fmt(q[0])} {fmt(q[1])}")
            cur = p
            if up == "M":
                start = p.copy(); cmd = "l" if rel else "L"
        elif up in "HV":
            v = nums(1)[0]; i += 1
            p = cur.copy()
            if up == "H":
                p[0] = (cur[0] if rel else 0) + v
            else:
                p[1] = (cur[1] if rel else 0) + v
            q = W.pts(p)[0]
            out.append(f"L {fmt(q[0])} {fmt(q[1])}"); cur = p
        elif up in "CSQT":
            n = {"C": 6, "S": 4, "Q": 4, "T": 2}[up]
            v = nums(n); i += n
            P = np.array(v).reshape(-1, 2) + base
            Q = W.pts(P)
            out.append(up + " " + " ".join(f"{fmt(a)} {fmt(b)}" for a, b in Q))
            cur = P[-1]
        elif up == "A":
            rx, ry, rot, la, sw, x, y = nums(7); i += 7
            p = base + [x, y]
            J = W.jac(cur)
            sx, sy = np.linalg.norm(J[:, 0]), np.linalg.norm(J[:, 1])
            if np.linalg.det(J) < 0:
                sw = 1 - sw
            q = W.pts(p)[0]
            out.append(f"A {fmt(rx * sx)} {fmt(ry * sy)} {fmt(rot)} {int(la)} {int(sw)} {fmt(q[0])} {fmt(q[1])}")
            cur = p
    return " ".join(out).replace(" Z M", " Z M")


# ---------------------------------------------------------------- file SVG
def attr(tag, name):
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def set_attr(tag, name, val):
    return re.sub(rf'(\s{name}=")[^"]*(")', lambda m: m.group(1) + val + m.group(2), tag, count=1)


def warp_svg(text: str, tps) -> str:
    stack = [np.eye(3)]
    out, pos = [], 0
    for m in re.finditer(r"<!--.*?-->|<(/?)([a-zA-Z]+)([^>]*?)(/?)>", text, re.S):
        out.append(text[pos:m.start()]); pos = m.end()
        tag = m.group(0)
        if tag.startswith("<!--") or m.group(2) == "svg":
            out.append(tag); continue
        closing, name, self_close = m.group(1), m.group(2), m.group(4)
        if closing:
            if name == "g":
                stack.pop()
            out.append(tag); continue
        M = stack[-1] @ parse_transform(attr(tag, "transform"))
        W = LocalWarp(tps, M)
        if name == "g":
            if not self_close:
                stack.append(M)
        elif name == "path" and attr(tag, "d"):
            tag = set_attr(tag, "d", warp_path(attr(tag, "d"), W))
        elif name in ("circle", "ellipse"):
            c = np.array([float(attr(tag, "cx") or 0), float(attr(tag, "cy") or 0)])
            J = W.jac(c)
            q = W.pts(c)[0]
            tag = set_attr(set_attr(tag, "cx", fmt(q[0])), "cy", fmt(q[1]))
            sx, sy = np.linalg.norm(J[:, 0]), np.linalg.norm(J[:, 1])
            if name == "circle":
                tag = set_attr(tag, "r", fmt(float(attr(tag, "r")) * math.sqrt(sx * sy)))
            else:
                tag = set_attr(set_attr(tag, "rx", fmt(float(attr(tag, "rx")) * sx)), "ry", fmt(float(attr(tag, "ry")) * sy))
        elif name == "rect":
            x, y, w, h = (float(attr(tag, k)) for k in ("x", "y", "width", "height"))
            d = warp_path(f"M{x} {y} L{x + w} {y} L{x + w} {y + h} L{x} {y + h} Z", W)
            rest = re.sub(r'\s(x|y|width|height|rx|ry)="[^"]*"', "", m.group(3))
            tag = f'<path{rest} d="{d}"{self_close}>'
        out.append(tag)
    out.append(text[pos:])
    return "".join(out)


# ---------------------------------------------------------------- vá khe da lộ ra sau khi uốn
def _dilate_h(m: np.ndarray, r: int) -> np.ndarray:
    out = m.copy()
    for k in range(1, r + 1):
        out[:, k:] |= m[:, :-k]
        out[:, :-k] |= m[:, k:]
    return out


def _trace(mask: np.ndarray) -> str:
    import tempfile
    import vtracer
    img = Image.fromarray(np.where(mask, 0, 255).astype("uint8")).convert("RGB")
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "i.png", Path(td) / "o.svg"
        img.save(a)
        vtracer.convert_image_to_svg_py(str(a), str(b), colormode="binary", mode="polygon", filter_speckle=2)
        svg = b.read_text(encoding="utf-8")
    ds = []
    for tag in re.findall(r"<path[^>]*>", svg):
        d = re.search(r'\sd="([^"]+)"', tag).group(1)
        t = re.search(r'translate\(([-\d.]+),\s*([-\d.]+)\)', tag)
        tx, ty = (float(t.group(1)), float(t.group(2))) if t else (0, 0)
        toks, is_x, res = re.findall(r"[MLZ]|-?\d*\.?\d+", d), True, []
        for tk in toks:
            if tk.isalpha():
                res.append(tk); is_x = True
            else:
                res.append(fmt(((float(tk) + (tx if is_x else ty)) / SC))); is_x = not is_x
        ds.append(" ".join(res))
    return " ".join(ds)


def patch_gaps(text: str, body: np.ndarray, arm, color: str, is_bottom: bool, y_min: float) -> str:
    """Lót một mảng màu vải DƯỚI các mảnh quần áo, phủ (1) khe da hẹp ≤ 8 đơn vị kẹp giữa hai mảnh vải trên cùng hàng
    (vd. giữa tay áo và thân áo ở nách) và (2) dải da ≤ 2,5 đơn vị sát mép vải (4 đơn vị phía trên). Quần/váy không lót lên tay."""
    png = bytes(resvg_py.svg_to_bytes(svg_string=re.sub(r'\sid="patch_khe"[^>]*/>', "", text), width=400 * SC, height=800 * SC))
    G = np.array(Image.open(io.BytesIO(png)).getchannel("A")) > 100
    if not G.any():
        return text
    left = np.maximum.accumulate(np.where(G, np.arange(G.shape[1]), -10 ** 6), axis=1)
    right = np.flip(np.minimum.accumulate(np.flip(np.where(G, np.arange(G.shape[1]), 10 ** 6), axis=1), axis=1), axis=1)
    cols = np.arange(G.shape[1])
    gap = (right - left <= 8 * SC) & (cols - left > 0) & (right - cols > 0)
    edge = _dilate_h(G, int(2.5 * SC))
    for k in range(1, 4 * SC + 1):                         # và dải 4 đơn vị ngay TRÊN mép vải (đỉnh vai, cạp quần)
        edge[:-k] |= G[k:]
    fill = body & ~G & (gap | edge)
    if is_bottom and arm is not None:
        fill &= ~arm
    fill[:int(y_min * SC)] = False                         # không lót vùng cổ, mặt (cổ áo giữ nguyên dáng)
    if fill.sum() < 4:
        return text
    d = _trace(fill)
    patch = f'<path id="patch_khe" d="{d}" fill="{color}" stroke="none"/>'
    return re.sub(r"(<g\b[^>]*>)", lambda m: m.group(1) + "\n    " + patch, text, count=1)


def new_hand(text: str, body_svg: str) -> str:
    """Góc nghiêng: lớp "ban_tay" (vẽ lại bàn tay, cẳng tay nằm trên quần áo) lấy tay gần của người mẫu MỚI,
    cắt từ độ cao cũ (đã uốn) trở xuống."""
    m = re.search(r'<g id="ban_tay"[^>]*>(.*?)</g>', text, re.S)
    if not m:
        return text
    ys = [float(v) for v in re.findall(r"[\d.]+ ([\d.]+)", re.search(r'\sd="([^"]+)"', m.group(1)).group(1))]
    y0 = min(ys)
    get = lambda pid: re.search(rf'<path id="{pid}"[^>]*/>', body_svg).group(0)
    skin = re.search(r'id="tay_gan" fill="([^"]+)"', body_svg).group(1)
    line = re.search(r'<g id="body_\w+" stroke="([^"]+)"', body_svg).group(1)
    arm_d = re.search(r'id="tay_gan"[^>]*\sd="([^"]+)"', body_svg).group(1)
    shade = re.sub(r'\sid="[^"]*"', "", get("bong_tay"))
    group = (f'<clipPath id="ban_tay_cat"><rect x="0" y="{y0:.1f}" width="400" height="{800 - y0:.1f}"/></clipPath>\n'
             f'    <g id="ban_tay" clip-path="url(#ban_tay_cat)" stroke="{line}" stroke-width="1.3" stroke-linejoin="round">\n'
             f'      <path d="{arm_d}" fill="{skin}"/>\n      {shade}\n    </g>')
    return text[:m.start()] + group + text[m.end():]


# ---------------------------------------------------------------- chạy
def view_of(name: str) -> str:
    for v in ("trai", "sau", "phai"):
        if name.endswith(f"_{v}.svg") or name.endswith(f"_{v}_them.svg"):
            return v
    return "truoc"


def main():
    old_dir, new_dir = Path(sys.argv[1]), Path(sys.argv[2])
    files = [Path(f) for f in sys.argv[3:]] or sorted(
        p for d in ("garment", "bottom", "accessory") for p in (FIG / d).glob("*.svg") if not p.name.endswith("_phai.svg"))
    warps, bodies, arms, necks = {}, {}, {}, {}
    for g in ("nu", "nam"):
        fo, fn = silhouette(old_dir / f"body_{g}.svg"), silhouette(new_dir / f"body_{g}.svg")
        lo, ln = landmarks(fo), landmarks(fn)
        necks[g] = ln[1]
        print(g, "mốc cũ", [round(v, 1) for v in lo], "mới", [round(v, 1) for v in ln])
        for v, suf in VIEW_SUFFIX.items():
            om = fo if v == "truoc" else silhouette(old_dir / f"body_{g}{suf}.svg")
            nm = fn if v == "truoc" else silhouette(new_dir / f"body_{g}{suf}.svg")
            arm_png = RENDER / f"{g}_{v}_arm.png"
            arm = arm_mask(arm_png) if v in ("truoc", "sau") and arm_png.exists() else None
            warps[g, v] = build_warp(om, nm, lo, ln, arm)
            warps[g, v, "dau"] = build_warp(om, nm, lo, ln, head_only=True)
            bodies[g, v], arms[g, v] = nm, arm
    acc = {a["id"]: a for a in json.loads((DATA / "accessories.json").read_text(encoding="utf-8"))}
    split = set()
    for f in files:
        view = view_of(f.name)
        stem = re.sub(r"_(trai|sau|phai_them|phai)$", "", f.stem)
        if re.search(r"_(nu|nam)$", stem):
            genders = [stem.rsplit("_", 1)[1]]
            targets = [f]
        else:                                           # phụ kiện dùng chung: tách thành bản _nu / _nam nếu cả hai giới dùng
            genders = acc[stem]["genders"] if stem in acc else ["nu"]
            if len(genders) > 1:
                targets = [f.with_name(f.name.replace(stem, f"{stem}_{g}", 1)) for g in genders]
                split.add(stem)
            else:
                targets = [f]
        text = f.read_text(encoding="utf-8")
        for g, dst in zip(genders, targets):
            head = acc.get(re.sub(r"_(nu|nam)$", "", stem), {}).get("slot") in ("head", "hair")
            out = warp_svg(text, warps[(g, view, "dau") if head else (g, view)])
            kind = "bottom" if re.match(r"(quan|vay)_", f.name) else "accessory" if stem in acc else "garment"
            if kind in ("garment", "bottom") and view in ("truoc", "sau") and not f.name.endswith("_them.svg"):
                out = patch_gaps(out, bodies[g, view], arms.get((g, view)), "#0000FF" if kind == "bottom" else "#FF0000",
                                 kind == "bottom", necks[g] + 12)
            if view == "trai":
                out = new_hand(out, (new_dir / f"body_{g}_trai.svg").read_text(encoding="utf-8"))
            dst.write_text(out, encoding="utf-8")
            print("Đã chỉnh", dst.relative_to(FIG) if FIG in dst.parents else dst, f"({g}, {view})")
        if targets != [f]:
            f.unlink()
    if split:                                           # ghi cờ byGender cho các phụ kiện vừa tách
        lines = (DATA / "accessories.json").read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            m = re.search(r'"id": "(\w+)"', line)
            if m and m.group(1) in split and '"byGender"' not in line:
                lines[i] = line.replace(', "usesAccent"', ', "byGender": true, "usesAccent"')
        (DATA / "accessories.json").write_text("\n".join(lines) + "\n", encoding="utf-8")
        for f in FIG.glob("accessory/*_phai.svg"):      # bản phải cũ của phụ kiện đã tách (mirror_views sẽ sinh lại)
            if re.sub(r"_phai$", "", f.stem) in split:
                f.unlink()
        print("Tách theo giới:", ", ".join(sorted(split)))


if __name__ == "__main__":
    main()

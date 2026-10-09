"""Hàm dùng chung để sinh và đo người mẫu giấy (khung 400x800, trục x=200).

Người mẫu được mô tả bằng nửa trái: điểm START (đỉnh cổ) và danh sách LEFT các đoạn
("L", p) hoặc ("C", c1, c2, p) đi xuống tới đáy chậu (200, 440). Nửa phải là ảnh lật.
"""


def fmt(p):
    return f"{p[0]:g} {p[1]:g}"


def mirror(p):
    return (400 - p[0], p[1])


def body_path(start, left) -> str:
    """Path SVG khép kín cho toàn thân: nửa trái rồi nửa phải lật, đi ngược lên."""
    parts, pts = [f"M{fmt(start)}"], [start]
    for seg in left:
        parts.append(("L" + fmt(seg[1])) if seg[0] == "L" else "C" + " ".join(fmt(x) for x in seg[1:]))
        pts.append(seg[-1])
    for i in range(len(left) - 1, -1, -1):
        seg, s = left[i], pts[i]
        if seg[0] == "L":
            parts.append("L" + fmt(mirror(s)))
        else:
            parts.append("C" + " ".join(fmt(mirror(x)) for x in (seg[2], seg[1], s)))
    return " ".join(parts + ["Z"])


def mirror_d(d: str) -> str:
    """Lật một chuỗi path toạ độ tuyệt đối (M/L/C/Q/Z) qua trục x=200."""
    out, is_x = [], True
    for t in d.replace(",", " ").split():
        if t[0].isalpha():
            out.append(t[0]); t = t[1:]; is_x = True
            if not t:
                continue
        v = float(t)
        out.append(f"{(400 - v) if is_x else v:g}")
        is_x = not is_x
    return " ".join(out)


def both(d: str) -> str:
    """Path bên trái kèm bản lật sang phải."""
    return d + " " + mirror_d(d)


def _bezier(p0, c1, c2, p1, n=40):
    for i in range(1, n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        yield (a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1])


def outline(start, left):
    """Đa giác xấp xỉ đường bao toàn thân, dùng để đo."""
    pts, cur = [start], start
    for seg in left:
        pts.extend([seg[1]] if seg[0] == "L" else _bezier(cur, seg[1], seg[2], seg[3]))
        cur = seg[-1]
    return pts + [(400 - x, y) for x, y in reversed(pts)]


def spans(y, poly):
    """Các đoạn x mà cơ thể chiếm ở độ cao y."""
    xs = []
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xs.sort()
    return [(round(xs[i], 1), round(xs[i + 1], 1)) for i in range(0, len(xs) - 1, 2)]

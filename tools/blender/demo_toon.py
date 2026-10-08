"""Bản dựng thử: hai người mẫu MakeHuman mặc Việt phục dựng 3D, render kiểu minh hoạ phẳng (màu phẳng 2 tầng, viền đậm).

Quần áo "may" thẳng trên thân 3D đã tạo dáng:
  - phần ôm (thân trên, tay áo, cổ đứng, giày): tách vùng lưới người theo trọng số xương rồi đẩy ra ngoài theo pháp tuyến;
  - phần buông (tà áo, váy, ống quần): ống loft qua các lát cắt ngang của thân + độ loe;
  - áo khoác nữ mở vạt trước (cắt hình chữ V, nẹp viền sẫm), áo nam cài khuy chéo bên phải.
Vải gấm: ô hoạ tiết .tools/brocade.png chiếu hộp (box projection), trộn cùng tông với màu vải.
Viền: kỹ thuật "vỏ lật" (inverted hull) — lớp vỏ dày vài mm, lật pháp tuyến, chỉ thấy mặt sau → nét viền đen quanh hình.

Chạy: .tools/blender/blender.exe -b --factory-startup --python tools/blender/demo_toon.py -- <thư_mục_ra>
"""
import math
import sys
from pathlib import Path

import addon_utils
import bmesh
import bpy
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).parent))
from face_presets import EYEBROWS, EYELASHES, FACE, HAIR, PRESETS, apply_face   # noqa: E402

OUT = Path(sys.argv[sys.argv.index("--") + 1])
OUT.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parents[2]
addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
from bl_ext.user_default.mpfb.services.humanservice import HumanService          # noqa: E402
from bl_ext.user_default.mpfb.services.locationservice import LocationService    # noqa: E402

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
DATA = Path(LocationService.get_user_data(""))
TARGETS = Path(LocationService.get_mpfb_data("targets"))


def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


# ---------------------------------------------------------------- vật liệu minh hoạ
BROCADE = bpy.data.images.load(str(ROOT / ".tools/brocade.png")); BROCADE.use_fake_user = True


def toon(name, hexcol, pattern=None, scale=7.0, alpha_tex=None):
    """Màu phẳng 2 tầng: Diffuse → Shader to RGB → ColorRamp (bậc) → nhân màu → Emission.
    pattern: màu nét gấm (trộn theo kênh alpha của ô hoạ tiết). alpha_tex: ảnh lấy kênh alpha (tóc, lông mày)."""
    m = bpy.data.materials.new(name); m.use_fake_user = True
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    base = nt.nodes.new("ShaderNodeRGB"); base.outputs[0].default_value = srgb(hexcol)
    col = base.outputs[0]
    if pattern:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = BROCADE; tx.projection = "BOX"; tx.projection_blend = 0.25
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], tx.inputs["Vector"])
        pc = nt.nodes.new("ShaderNodeRGB"); pc.outputs[0].default_value = srgb(pattern)
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
        nt.links.new(tx.outputs["Alpha"], mix.inputs[0]); nt.links.new(col, mix.inputs[6]); nt.links.new(pc.outputs[0], mix.inputs[7])
        col = mix.outputs[2]
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.74, 0.74, 0.74, 1)
    ramp.color_ramp.elements[1].position = 0.32; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(dif.outputs[0], s2r.inputs[0]); nt.links.new(s2r.outputs[0], bw.inputs[0]); nt.links.new(bw.outputs[0], ramp.inputs[0])
    nt.links.new(col, mul.inputs[6]); nt.links.new(ramp.outputs[0], mul.inputs[7]); nt.links.new(mul.outputs[2], em.inputs[0])
    shader = em.outputs[0]
    if alpha_tex is not None:
        tx2 = nt.nodes.new("ShaderNodeTexImage"); tx2.image = alpha_tex
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        th = nt.nodes.new("ShaderNodeMath"); th.operation = "GREATER_THAN"; th.inputs[1].default_value = 0.45   # sợi tóc mảnh → mảng đặc, mép sắc
        nt.links.new(tx2.outputs["Alpha"], th.inputs[0])
        nt.links.new(th.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(shader, mx.inputs[2])
        shader = mx.outputs[0]
    nt.links.new(shader, out.inputs[0])
    return m


def outline_mat():
    """Vật liệu viền (tạo lại nếu MPFB đã dọn vật liệu chưa dùng khi tạo người)."""
    m = bpy.data.materials.get("vien")
    if m:
        return m
    m = bpy.data.materials.new("vien"); m.use_nodes = True
    n = m.node_tree.nodes; n.clear()
    e = n.new("ShaderNodeEmission"); e.inputs[0].default_value = srgb("#1d1a17")
    o = n.new("ShaderNodeOutputMaterial"); m.node_tree.links.new(e.outputs[0], o.inputs[0])
    m.use_backface_culling = True
    m.use_fake_user = True
    return m


def outline(obj, thick=0.0035):
    obj.data.materials.append(outline_mat())
    md = obj.modifiers.new("vien", "SOLIDIFY")
    md.thickness = thick; md.offset = 1; md.use_flip_normals = True; md.use_rim = False
    md.material_offset = len(obj.data.materials) - 1


def shade_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True


# ---------------------------------------------------------------- người mẫu
MACRO = {
    "nu": dict(gender=0.0, age=0.5, muscle=0.45, weight=0.42, proportions=0.75, height=0.45, cupsize=0.45, firmness=0.6),
    "nam": dict(gender=1.0, age=0.5, muscle=0.55, weight=0.48, proportions=0.75, height=0.55, cupsize=0.5, firmness=0.5),
}
SKIN = {"nu": "#F2CDB0", "nam": "#E9C19E"}


def make_person(g):
    macro = dict(MACRO[g]); macro["race"] = {"asian": 1.0, "caucasian": 0.0, "african": 0.0}
    human = HumanService.create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True,
                                      feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    apply_face(human, TARGETS, PRESETS[g][FACE[g]])
    parts = {}
    for kind, name in (("eyes", "high-poly"), ("eyelashes", EYELASHES[g]), ("eyebrows", EYEBROWS[g]), ("hair", HAIR[g])):
        parts[kind] = HumanService.add_mhclo_asset(str(DATA / kind / name / f"{name}.mhclo"), human, asset_type=kind.capitalize(),
                                                   subdiv_levels=1, material_type="MAKESKIN")
    rig = HumanService.add_builtin_rig(human, "default")
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")

    def aim(pb, d):
        bpy.context.view_layer.update()
        cur = (pb.tail - pb.head).normalized()
        q = cur.rotation_difference((rig.matrix_world.to_3x3().inverted() @ Vector(d)).normalized())
        R = pb.matrix.to_3x3().normalized().to_quaternion()
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = pb.rotation_quaternion @ (R.inverted() @ q @ R)
        bpy.context.view_layer.update()
    out_ = {"nu": 0.2, "nam": 0.17}[g]
    for side, sx in (("L", 1), ("R", -1)):
        aim(rig.pose.bones[f"upperarm01.{side}"], (sx * out_, 0.03, -1.0))
        aim(rig.pose.bones[f"lowerarm01.{side}"], (sx * out_ * 0.5, -0.08, -1.0))
        for bn in (f"lowerarm02.{side}", f"wrist.{side}"):
            pb = rig.pose.bones[bn]; pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = pb.rotation_quaternion @ Quaternion((0, 1, 0), sx * math.radians(-25))
        li = {"nu": 0.03, "nam": 0.06}[g]
        aim(rig.pose.bones[f"upperleg02.{side}"], (-sx * li, 0.0, -1.0))
        aim(rig.pose.bones[f"lowerleg01.{side}"], (-sx * li * 0.6, 0.02, -1.0))
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()

    # vật liệu minh hoạ cho người
    human.data.materials.clear(); human.data.materials.append(toon(f"da_{g}", SKIN[g]))
    for kind in ("hair", "eyebrows", "eyelashes"):
        o = parts[kind]
        img = next((n.image for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
        o.data.materials.clear()
        o.data.materials.append(toon(f"{kind}_{g}", "#1E1916" if kind == "hair" else "#2A211C", alpha_tex=img))
    shade_smooth(human)
    return human, rig, parts


# ---------------------------------------------------------------- đo thân đã tạo dáng
REGION = {"torso": ("spine", "clavicle", "shoulder", "breast", "pelvis", "root"), "arm": ("upperarm", "lowerarm"),
          "hand": ("wrist", "metacarpal", "finger", "thumb"), "leg": ("upperleg", "lowerleg"), "foot": ("foot", "toe"),
          "neck": ("neck",), "head": ("head", "jaw", "eye", "tongue", "teeth", "ear", "levator", "oris", "temporalis",
                                      "risorius", "orbicularis", "nose", "cheek", "special")}


def posed(human):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = human.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    me.transform(human.matrix_world)
    names = [vg.name for vg in human.vertex_groups]
    region = []
    for v in me.vertices:
        acc = {}
        for gr in v.groups:
            nm = names[gr.group] if gr.group < len(names) else ""
            for rk, pre in REGION.items():
                if nm.startswith(pre):
                    acc[rk] = acc.get(rk, 0) + gr.weight
        region.append(max(acc, key=acc.get) if acc else "head")
    return me, region


class Body:
    def __init__(self, me, region, wrist_z=None):
        if wrist_z is not None:
            region = ["arm" if r == "hand" and v.co.z > wrist_z + 0.012 else r for r, v in zip(region, me.vertices)]
        self.me, self.region = me, region
        zs = [v.co.z for v in me.vertices]
        self.z0, self.H = min(zs), max(zs) - min(zs)
        self.co = [v.co.copy() for v in me.vertices]

    def z(self, f):                                   # độ cao theo tỉ lệ chiều cao người
        return self.z0 + f * self.H

    def slice(self, z, regions=("torso", "leg"), band=0.012, xside=None):
        pts = [c for c, r in zip(self.co, self.region) if r in regions and abs(c.z - z) < band
               and (xside is None or (c.x - 0) * xside > 0)]
        if not pts:
            return None
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2)


# ---------------------------------------------------------------- may quần áo
def new_obj(name, bm, mats):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    for m in mats:
        me.materials.append(m)
    shade_smooth(ob)
    return ob


def cage(body: Body, keep, offset, name, mats, face_ok=None, mat_fn=None, snap=None):
    """Lớp vải bám thân: giữ các mặt có đủ đỉnh thuộc vùng keep (và face_ok(tâm, vùng) đúng), đẩy ra theo pháp tuyến."""
    bm = bmesh.new(); bm.from_mesh(body.me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); bm.normal_update()
    nrm = {v: v.normal.copy() for v in bm.verts}
    reg = body.region
    drop = []
    for f in bm.faces:
        rs = [reg[v.index] for v in f.verts]
        if not all(r in keep for r in rs):
            drop.append(f); continue
        main = max(set(rs), key=rs.count)
        if face_ok and not face_ok(f.calc_center_median(), main):
            drop.append(f)
    bmesh.ops.delete(bm, geom=drop, context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    if snap:
        for v in bm.verts:
            if v.is_boundary:
                v.co = snap(v.co.copy())
    for v in bm.verts:
        v.co += nrm[v] * offset
    if mat_fn:
        for f in bm.faces:
            f.material_index = mat_fn(f.calc_center_median())
    return new_obj(name, bm, mats)


def ribbon(edge_pts, width_dir, width, name, mat):
    """Dải nẹp: các điểm mép + độ rộng theo hướng width_dir (vector) → dải quad."""
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in edge_pts]
    b = [bm.verts.new(p + width_dir * width) for p in edge_pts]
    for i in range(len(a) - 1):
        bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, [mat])


def loft(rings, name, mats, n=72, gap=None, mat_fn=None, cap_bottom=False):
    """rings: [(z, cx, cy, rx, ry)] từ trên xuống. a=0 là phía trước (−Y). gap(z) → nửa góc bỏ trống phía trước (độ)."""
    bm = bmesh.new()
    grid, angs = [], []
    for z, cx, cy, rx, ry in rings:
        g0 = gap(z) if gap else 0.0
        row, ar = [], []
        for i in range(n if not gap else n + 1):
            ad = (360 * i / n) if not gap else (g0 + (360 - 2 * g0) * i / n)
            a = math.radians(ad)
            row.append(bm.verts.new((cx + rx * math.sin(a), cy - ry * math.cos(a), z))); ar.append(ad)
        grid.append(row); angs.append(ar)
    m = n if not gap else n
    for j in range(len(rings) - 1):
        zc = (rings[j][0] + rings[j + 1][0]) / 2
        for i in range(m):
            i2 = (i + 1) % n if not gap else i + 1
            f = bm.faces.new((grid[j][i], grid[j][i2], grid[j + 1][i2], grid[j + 1][i]))
            if mat_fn:
                a = (angs[j][i] + angs[j][i2]) / 2
                f.material_index = mat_fn(zc, min(a, 360 - a))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, mats)


def flared(body: Body, z_top, z_hem, ease, flare, regions=("torso", "leg"), step=0.02, xside=None, min_r=0.0):
    """Lát cắt thân + độ nới; dưới chỗ rộng nhất chỉ loe ra (vải buông), không thót theo chân."""
    rings, best = [], None
    z = z_top
    while z >= z_hem - 1e-6:
        s = body.slice(z, regions, xside=xside)
        t = (z_top - z) / max(z_top - z_hem, 1e-6)
        if s:
            cx, cy, rx, ry = s
            rx, ry = max(rx + ease, min_r), max(ry + ease, min_r)
            if best is None or rx >= best[2]:
                best = (cx, cy, rx, ry)
            else:
                cx, cy = best[0], best[1]
                rx, ry = max(rx, best[2]), max(ry, best[3])
        else:
            cx, cy, rx, ry = best
        rings.append((z, cx, cy, rx + flare * t ** 1.4, ry + flare * 0.6 * t ** 1.4))
        z -= step
    return rings


def front_y(objs, x, z, r=0.012):
    best = None
    for ob in objs:
        for v in ob.data.vertices:
            c = ob.matrix_world @ v.co
            if abs(c.x - x) < r and abs(c.z - z) < r:
                best = c.y if best is None else min(best, c.y)
    return best


def buttons(pts, mat, name, rad=0.0065):
    obs = []
    for i, p in enumerate(pts):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, location=p, segments=16, ring_count=8)
        o = bpy.context.active_object; o.name = f"{name}{i}"
        o.data.materials.append(mat); shade_smooth(o); obs.append(o)
    return obs


TEAL, TEAL_PAT, TEAL_DARK = "#1F5B57", "#4A887D", "#163F3D"


def dress_man(body: Body):
    coat = toon("ao_nam", TEAL, TEAL_PAT, 7.0)
    coat_plain = toon("co_nam", TEAL)
    zw, zhem, zn = body.z(0.6), body.z(0.31), body.z(0.835)
    top = cage(body, ("torso", "arm"), 0.012, "ao_tren_nam", [coat],
               face_ok=lambda c, r: r == "arm" or c.z > zw - 0.03)
    tails = loft(flared(body, zw, zhem, 0.024, 0.05), "ta_ao_nam", [coat])
    nz = sorted(c.z for c, r in zip(body.co, body.region) if r == "neck")
    z0 = nz[int(len(nz) * 0.05)]                       # chân cổ (đo trên vùng cổ của lưới)
    rings, last = [], None
    for k in range(5):
        z = z0 + 0.009 * k
        t = body.slice(z, ("neck",), band=0.008) or last
        if t is None:
            continue
        last = t
        rings.append((z, t[0], t[1], t[2] + 0.005, t[3] + 0.005))
    collar = loft(rings[::-1], "co_dung_nam", [coat_plain])
    beige = toon("quan_nam", "#D8CDB6")
    legs = []
    for xs in (-1, 1):
        rings = flared(body, body.z(0.355), body.z(0.035), 0.03, 0.0, regions=("leg",), xside=xs, min_r=0.064)
        legs.append(loft(rings, f"ong_quan_{'phai' if xs < 0 else 'trai'}", [beige]))
    shoes = cage(body, ("foot",), 0.008, "giay_nam", [toon("giay_nam", "#1B1917")])
    # đường cài khuy chéo bên phải người mặc (−X): cổ → nách → dọc sườn
    path = [(-0.012, body.z(0.83)), (-0.05, body.z(0.80)), (-0.085, body.z(0.77)), (-0.105, body.z(0.73)),
            (-0.11, body.z(0.66)), (-0.11, body.z(0.58)), (-0.12, body.z(0.50))]
    pts = []
    for x, z in path:
        y = front_y([top, tails, collar], x, z)
        if y is not None:
            pts.append(Vector((x, y - 0.003, z)))
    brass = toon("khuy", "#C9A35A")
    btn = buttons(pts[:5] + [pts[-2]], brass, "khuy_nam")
    for o in (top, tails, collar, *legs, shoes):
        outline(o)
    return [top, tails, collar, *legs, shoes, *btn]


def dress_woman(body: Body):
    coat = toon("ao_nu", TEAL, TEAL_PAT, 7.0)
    trim = toon("nep_nu", TEAL_DARK)
    white = toon("trong_nu", "#F1EADA")
    zn, zb, zw, zhem = body.z(0.83), body.z(0.72), body.z(0.6), body.z(0.24)
    cx = 0.0

    def hw(z):                                         # nửa bề rộng chỗ mở vạt (cổ hẹp → ngực rộng dần)
        t = min(1, max(0, (zn - z) / (zn - zb)))
        return 0.02 + 0.045 * t
    front = lambda c: c.y < -0.01
    inner_top = cage(body, ("torso",), 0.004, "ao_trong_nu", [white], face_ok=lambda c, r: c.z > zw - 0.04)
    skirt = loft(flared(body, zw, body.z(0.025), 0.01, 0.13), "vay_trong_nu", [white])
    top = cage(body, ("torso", "arm"), 0.011, "ao_khoac_tren_nu", [coat],
               face_ok=lambda c, r: r == "arm" or (c.z > zw - 0.03 and not (front(c) and abs(c.x - cx) < hw(c.z))),
               snap=lambda c: Vector((cx + math.copysign(hw(c.z), c.x - cx), c.y, c.z))
               if front(c) and abs(c.x - cx) < hw(c.z) + 0.015 and zw - 0.03 < c.z < zn + 0.01 else c)
    s0 = body.slice(zw, ("torso", "leg"))
    rx0 = s0[2] + 0.02
    gap = lambda z: math.degrees(math.asin(min(0.9, hw(zw) / rx0))) + 5 * max(0, (zw - z) / (zw - zhem))
    tails = loft(flared(body, zw, zhem, 0.02, 0.09), "ta_ao_nu", [coat, trim], gap=gap,
                 mat_fn=lambda z, ad: 1 if ad < gap(z) + 6 else 0)
    # nẹp viền chạy dọc mép vạt chữ V (thân trên)
    trims = []
    for sg in (-1, 1):
        pts = []
        z = zn - 0.005
        while z > zw - 0.03:
            x = cx + sg * hw(z)
            y = front_y([top], x + sg * 0.006, z, 0.01)
            if y is not None:
                pts.append(Vector((x, y - 0.002, z)))
            z -= 0.01
        if len(pts) > 2:
            trims.append(ribbon(pts, Vector((sg, 0.25, 0)).normalized(), 0.02, f"nep_vat_{sg}", trim))
    shoes = cage(body, ("foot",), 0.007, "giay_nu", [toon("giay_nu", TEAL)])
    # 3 khuy trên nẹp vạt phía trái người mặc (+X) dưới ngực
    pts = []
    for z in (body.z(0.70), body.z(0.665), body.z(0.63)):
        x = hw(z) + 0.011
        y = front_y([top], x, z, 0.015)
        if y is not None:
            pts.append(Vector((x, y - 0.003, z)))
    btn = buttons(pts, toon("khuy_nu", "#C9A35A"), "khuy_nu", 0.006)
    for o in (inner_top, skirt, top, tails, shoes):
        outline(o)
    return [inner_top, skirt, top, tails, shoes, *trims, *btn]


# ---------------------------------------------------------------- dựng cảnh
def main():
    people = []
    for g, x in (("nam", -0.3), ("nu", 0.3)):
        human, rig, parts = make_person(g)
        me, region = posed(human)                      # lấy lưới TRƯỚC khi gắn lớp viền (viền không được tính vào thân)
        wz = min((rig.matrix_world @ rig.pose.bones[f"wrist.{s}"].head).z for s in "LR")
        body = Body(me, region, wz)
        outline(human, 0.0025)
        clothes = dress_man(body) if g == "nam" else dress_woman(body)
        rig.location.x += x
        for o in clothes:
            o.location.x += x
        people.append((g, body))
        print("XONG", g, f"cao {body.H:.3f} m")

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = True
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    ld = bpy.data.lights.new("sun", "SUN"); ld.energy = 4.0; ld.angle = math.radians(5)
    lo = bpy.data.objects.new("sun", ld); sc.collection.objects.link(lo)
    lo.rotation_euler = (math.radians(55), 0, math.radians(-30))
    Hmax = max(b.H for _, b in people)
    cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; cd.ortho_scale = Hmax * 1.12
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = 1500, 1900
    zc = Hmax * 0.5
    for name, ang in (("truoc", 0), ("nghieng", 35), ("sau", 180)):
        a = math.radians(ang)
        cam.location = (8 * math.sin(a), -8 * math.cos(a), zc)
        cam.rotation_euler = (math.radians(90), 0, a)
        lo.rotation_euler = (math.radians(55), 0, a + math.radians(-30))
        sc.render.filepath = str(OUT / f"demo_3d_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("ANH", name)



if __name__ == "__main__":
    main()

"""Bản thử phần NGƯỜI MẪU theo phong cách minh hoạ (dáng thon, bàn tay nhỏ, mặt giản lược), chỉ mặc đồ lót.

Chạy: .tools/blender/blender.exe -b --factory-startup --python tools/blender/demo_person.py -- <thư_mục_ra> [so_sanh|ba_goc]
  so_sanh: nam hiện tại | nam đề xuất | nữ đề xuất | nữ hiện tại (góc trước)
  ba_goc : cặp đề xuất ở 3 góc (trước, ¾, sau)
Dùng lại hàm dựng của demo_toon.py (vật liệu minh hoạ, viền, đo thân, "may" lớp vải bám da).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).parent))
import demo_toon as T                                                      # noqa: E402
from face_presets import EYEBROWS, EYELASHES, FACE, HAIR, PRESETS, apply_face   # noqa: E402

NET = []                                            # thân người (để Freestyle chỉ vẽ nét trên da, không vẽ tóc/mắt)
FS = float(__import__("os").environ.get("FS", "0"))
MODE = sys.argv[sys.argv.index("--") + 2] if len(sys.argv) > sys.argv.index("--") + 2 else "so_sanh"

# ---- thông số "đề xuất": thon hơn ảnh dựng cũ, theo tỉ lệ ảnh mẫu (vai vừa, tay chân thon, bàn tay nhỏ)
STYLE_MACRO = {
    "nu": dict(gender=0.0, age=0.5, muscle=0.35, weight=0.38, proportions=0.8, height=0.5, cupsize=0.4, firmness=0.6),
    "nam": dict(gender=1.0, age=0.5, muscle=0.28, weight=0.36, proportions=0.8, height=0.55, cupsize=0.5, firmness=0.5),
}
STYLE_TARGETS = {
    "nu": {"torso/measure-shoulder-dist-decr": 0.25, "hands/*-hand-scale-decr": 0.35, "hands/*-hand-fingers-length-decr": 0.15,
           "neck/neck-scale-horiz-decr": 0.15, "arms/*-upperarm-fat-decr": 0.3, "arms/*-lowerarm-fat-decr": 0.3,
           "legs/*-upperleg-fat-decr": 0.3, "legs/*-lowerleg-fat-decr": 0.2},
    "nam": {"torso/measure-shoulder-dist-decr": 0.45, "torso/torso-vshape-decr": 0.4, "torso/torso-muscle-pectoral-decr": 0.4,
            "hands/*-hand-scale-decr": 0.4, "hands/*-hand-fingers-length-decr": 0.15, "neck/neck-scale-horiz-decr": 0.3,
            "arms/*-upperarm-muscle-decr": 0.5, "arms/*-upperarm-shoulder-muscle-decr": 0.5, "arms/*-lowerarm-muscle-decr": 0.4,
            "legs/*-upperleg-muscle-decr": 0.4, "legs/*-lowerleg-muscle-decr": 0.3},
}
# mặt giản lược: gò má và cằm mềm, mắt vừa, mũi nhỏ (nhẹ hơn bộ mặt "đã chốt")
FACE_SIMPLE = {
    "nu": {"head/head-oval": 0.7, "chin/chin-width-decr": 0.35, "eyes/*-eye-scale-incr": 0.1, "nose/nose-scale-vert-decr": 0.2,
           "nose/nose-scale-horiz-decr": 0.3, "mouth/mouth-scale-horiz-decr": 0.15, "mouth/mouth-angles-up": 0.25,
           "cheek/*-cheek-volume-decr": 0.1},
    "nam": {"head/head-oval": 0.5, "chin/chin-width-decr": 0.15, "nose/nose-scale-horiz-decr": 0.25, "nose/nose-scale-vert-decr": 0.15,
            "mouth/mouth-scale-horiz-decr": 0.1, "mouth/mouth-angles-up": 0.15, "eyes/*-eye-scale-incr": 0.05},
}
# mặt theo ảnh mẫu minh hoạ (3 mức T1 nhẹ → T3 rõ):
#  nam: gò má → má thẳng đều, từ má xuống cằm thu thoải, cằm vuông tròn (không nhọn);  nữ: trái xoan, cằm tròn mềm
_FACE_BASE = {"eyes/*-eye-scale-incr": 0.25, "eyes/*-eye-height1-incr": 0.2, "eyes/*-eye-height2-incr": 0.2,
              "nose/nose-scale-vert-decr": 0.25, "nose/nose-scale-horiz-decr": 0.3, "mouth/mouth-scale-horiz-decr": 0.15,
              "mouth/mouth-angles-up": 0.2, "ears/*-ear-scale-decr": 0.2}
_THON = {
    "nam": dict(_FACE_BASE, **{"head/head-oval": 0.3, "head/head-rectangular": 0.5, "head/head-scale-horiz-decr": 0.3,
                               "cheek/*-cheek-volume-decr": 0.2, "chin/chin-width-decr": 0.3, "chin/chin-prominent-decr": 0.1,
                               "chin/chin-jaw-drop-decr": 0.15, "neck/neck-scale-horiz-decr": 0.25}),
    "nu": dict(_FACE_BASE, **{"head/head-oval": 1.0, "head/head-scale-horiz-decr": 0.2, "cheek/*-cheek-volume-decr": 0.35,
                              "cheek/*-cheek-bones-incr": 0.1, "chin/chin-width-decr": 0.5, "chin/chin-triangle": 0.1,
                              "chin/chin-jaw-drop-incr": 0.05}),
}
FACE_ROUND = {g: {k: {t: min(v * f, 1.0) for t, v in _THON[g].items()} for k, f in (("T1", 0.6), ("T2", 1.0), ("T3", 1.4))}
              for g in ("nu", "nam")}
# vòng 2: nam thon hơn + đường cằm/hàm rõ nét (kiểu mặt nam thon, hàm gọn); nữ giữ trái xoan T2, thêm đường cằm
_CAM_NAM = {"head/head-scale-horiz-decr": 0.18, "cheek/*-cheek-volume-decr": 0.2, "chin/chin-width-decr": 0.12,
            "chin/chin-bones-incr": 0.35, "chin/chin-prominent-incr": 0.25, "cheek/*-cheek-bones-incr": 0.15,
            "head/head-fat-decr": 0.35, "head/head-scale-vert-incr": 0.08, "eyes/*-eye-scale-incr": 0.1, "neck/neck-scale-horiz-decr": 0.1}
_CAM_NU = {"chin/chin-bones-incr": 0.35, "chin/chin-prominent-incr": 0.3, "chin/chin-height-incr": 0.08, "cheek/*-cheek-volume-decr": 0.1}
for _g, _inc, _ref in (("nam", _CAM_NAM, "T3"), ("nu", _CAM_NU, "T2")):
    FACE_ROUND[_g]["REF"] = dict(FACE_ROUND[_g][_ref])
    for _k, _f in (("S1", 0.8), ("S2", 1.2), ("S3", 1.7)):
        _d = dict(FACE_ROUND[_g][_ref]); _d.pop("chin/chin-prominent-decr", None)
        for _t, _v in _inc.items():
            _d[_t] = min(_d.get(_t, 0) + _v * _f, 1.0)
        FACE_ROUND[_g][_k] = _d
# nam theo khuôn mặt ảnh mẫu: mặt dài vừa, hai bên má–hàm gần thẳng và song song, cằm vuông tròn nhỏ, cổ mảnh
_NAM_V2 = dict(_FACE_BASE, **{"head/head-oval": 0.15, "head/head-rectangular": 0.7, "head/head-scale-horiz-decr": 0.5,
                              "head/head-scale-vert-incr": 0.2, "head/head-fat-decr": 0.5, "cheek/*-cheek-volume-decr": 0.5,
                              "cheek/*-cheek-bones-decr": 0.25, "chin/chin-width-decr": 0.35, "chin/chin-bones-incr": 0.3,
                              "chin/chin-prominent-incr": 0.15, "neck/neck-scale-horiz-decr": 0.4, "ears/*-ear-scale-decr": 0.3,
                              "eyes/*-eye-scale-incr": 0.2})
FACE_ROUND["nam"]["V2"] = {t: min(v, 1.0) for t, v in _NAM_V2.items()}
# B1–B3: bớt "bè" — hàm/gò má hẹp dần (mặt trên rộng hơn dưới), tai nhỏ, mặt cân với sọ
for _k, _it in (("B1", 0.35), ("B2", 0.6), ("B3", 0.85)):
    _d = dict(_NAM_V2); _d.update({"head/head-rectangular": 0.3, "head/head-invertedtriangular": _it, "head/head-scale-horiz-decr": 0.6,
                                   "cheek/*-cheek-volume-decr": 0.7, "cheek/*-cheek-bones-decr": 0.3, "chin/chin-width-decr": 0.7,
                                   "chin/chin-triangle": 0.25, "chin/chin-jaw-drop-decr": 0.2, "mouth/mouth-angles-up": 0.4,
                                   "eyes/*-eye-scale-incr": 0.3, "ears/*-ear-scale-decr": 0.5, "head/head-scale-vert-incr": 0.1})
    FACE_ROUND["nam"][_k] = {t: min(v, 1.0) for t, v in _d.items()}
# V3–V5: hàm thu dần xuống cằm (gò má giữ nguyên, góc hàm mềm, cằm nhỏ vuông tròn)
for _k, _w, _tri, _jd in (("V3", 0.5, 0.15, 0.1), ("V4", 0.7, 0.25, 0.2), ("V5", 0.9, 0.35, 0.3)):
    _d = dict(_NAM_V2); _d.update({"chin/chin-width-decr": _w, "chin/chin-triangle": _tri, "chin/chin-jaw-drop-decr": _jd,
                                   "mouth/mouth-angles-up": 0.4, "eyes/*-eye-scale-incr": 0.3})
    FACE_ROUND["nam"][_k] = {t: min(v, 1.0) for t, v in _d.items()}
HAIR_STYLE = {"nu": "rehmanpolanski_hair_bun_brown", "nam": "short02"}          # nam: tóc ngắn gọn như ảnh mẫu (short02 trong bộ có sẵn)


def eye_toon(o, g):
    img = bpy.data.images.load(str(T.DATA / "eyes" / "materials" / "brown_eye.png"))    # tròng mắt nâu (MakeHuman, CC0)
    m = bpy.data.materials.new(f"mat_{g}"); m.use_nodes = True; m.use_fake_user = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    if img:
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img
        nt.links.new(tx.outputs[0], em.inputs[0])
    else:
        em.inputs[0].default_value = (0.1, 0.07, 0.05, 1)
    nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.clear(); o.data.materials.append(m)


def band(body, keep, zlo, zhi, offset, name, mats):
    """Dải vải bám da, cắt bằng MẶT PHẲNG NGANG ở zlo/zhi → mép thẳng, không răng cưa theo ô lưới."""
    import bmesh
    bm = bmesh.new(); bm.from_mesh(body.me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not all(body.region[v.index] in keep for v in f.verts)], context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    for z, kw in ((zlo, {"clear_inner": True}), (zhi, {"clear_outer": True})):
        bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(0, 0, z), plane_no=(0, 0, 1), **kw)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * offset
    return T.new_obj(name, bm, mats)


# dáng nữ THON: hai mức (A nhẹ, B rõ) so với đề xuất đầu; giảm hông, đùi, eo, ngực, tay, cổ
SLIM_NU = {
    "A": ({"weight": 0.30, "cupsize": 0.3, "proportions": 0.85},
          {"hip/hip-scale-horiz-decr": 0.45, "torso/measure-hips-circ-decr": 0.4, "torso/measure-waist-circ-decr": 0.3,
           "legs/measure-thigh-circ-decr": 0.5, "legs/*-upperleg-fat-decr": 0.5, "legs/measure-calf-circ-decr": 0.3,
           "torso/measure-bust-circ-decr": 0.3, "arms/measure-upperarm-circ-decr": 0.3}),
    # C, D: thon nhưng đầy đặn đúng chỗ — ngực nở vừa, eo nhỏ, hông cân với vai, đùi và chân mảnh
    "C": ({"weight": 0.30, "cupsize": 0.55, "proportions": 0.85, "firmness": 0.7},
          {"torso/measure-waist-circ-decr": 0.5, "torso/measure-bust-circ-incr": 0.15, "torso/measure-underbust-circ-decr": 0.3,
           "hip/hip-scale-horiz-decr": 0.2, "torso/measure-hips-circ-decr": 0.15, "legs/measure-thigh-circ-decr": 0.4,
           "legs/*-upperleg-fat-decr": 0.4, "legs/measure-calf-circ-decr": 0.3, "arms/measure-upperarm-circ-decr": 0.3,
           "torso/measure-shoulder-dist-decr": 0.25, "neck/neck-scale-horiz-decr": 0.2}),
    "D": ({"weight": 0.30, "cupsize": 0.7, "proportions": 0.85, "firmness": 0.8},
          {"torso/measure-waist-circ-decr": 0.6, "torso/measure-bust-circ-incr": 0.3, "torso/measure-underbust-circ-decr": 0.3,
           "hip/hip-scale-horiz-decr": 0.1, "torso/measure-hips-circ-incr": 0.1, "legs/measure-thigh-circ-decr": 0.35,
           "legs/*-upperleg-fat-decr": 0.35, "legs/measure-calf-circ-decr": 0.3, "arms/measure-upperarm-circ-decr": 0.3,
           "torso/measure-shoulder-dist-decr": 0.25, "neck/neck-scale-horiz-decr": 0.2}),
    "E": ({"weight": 0.30, "cupsize": 0.85, "proportions": 0.85, "firmness": 0.85},
          {"torso/measure-waist-circ-decr": 0.6, "torso/measure-bust-circ-incr": 0.5, "torso/measure-underbust-circ-decr": 0.3,
           "hip/hip-scale-horiz-decr": 0.1, "torso/measure-hips-circ-incr": 0.1, "legs/measure-thigh-circ-decr": 0.35,
           "legs/*-upperleg-fat-decr": 0.35, "legs/measure-calf-circ-decr": 0.3, "arms/measure-upperarm-circ-decr": 0.3,
           "torso/measure-shoulder-dist-decr": 0.25, "neck/neck-scale-horiz-decr": 0.2}),
    "F": ({"weight": 0.30, "cupsize": 1.0, "proportions": 0.85, "firmness": 0.9},
          {"torso/measure-waist-circ-decr": 0.6, "torso/measure-bust-circ-incr": 0.8, "torso/measure-underbust-circ-decr": 0.3,
           "hip/hip-scale-horiz-decr": 0.1, "torso/measure-hips-circ-incr": 0.1, "legs/measure-thigh-circ-decr": 0.35,
           "legs/*-upperleg-fat-decr": 0.35, "legs/measure-calf-circ-decr": 0.3, "arms/measure-upperarm-circ-decr": 0.3,
           "torso/measure-shoulder-dist-decr": 0.25, "neck/neck-scale-horiz-decr": 0.2}),
    "B": ({"weight": 0.22, "cupsize": 0.2, "proportions": 0.9},
          {"hip/hip-scale-horiz-decr": 0.7, "torso/measure-hips-circ-decr": 0.65, "torso/measure-waist-circ-decr": 0.45,
           "legs/measure-thigh-circ-decr": 0.8, "legs/*-upperleg-fat-decr": 0.8, "legs/measure-calf-circ-decr": 0.5,
           "legs/*-lowerleg-fat-decr": 0.5, "torso/measure-bust-circ-decr": 0.5, "arms/measure-upperarm-circ-decr": 0.5,
           "torso/measure-shoulder-dist-decr": 0.4, "neck/neck-scale-horiz-decr": 0.3}),
}


def make(g, style: bool, slim=None, rnd=None, hair=None, jaw=False):
    macro = dict(STYLE_MACRO[g] if style else T.MACRO[g]); macro["race"] = {"asian": 1.0, "caucasian": 0.0, "african": 0.0}
    human = T.HumanService.create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True,
                                        feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    face = dict(FACE_SIMPLE[g]) if style else dict(PRESETS[g][FACE[g]])
    if style:
        face.update(STYLE_TARGETS[g])
    if rnd:
        face.update(FACE_ROUND[g][rnd])
    if slim:
        macro.update(SLIM_NU[slim][0]); face.update(SLIM_NU[slim][1])
    apply_face(human, T.TARGETS, face)
    parts = {}
    hair = hair or (HAIR_STYLE[g] if style and not rnd else HAIR[g])
    for kind, name in (("eyes", "high-poly"), ("eyelashes", EYELASHES[g]), ("eyebrows", EYEBROWS[g]), ("hair", hair)):
        parts[kind] = T.HumanService.add_mhclo_asset(str(T.DATA / kind / name / f"{name}.mhclo"), human, asset_type=kind.capitalize(),
                                                     subdiv_levels=1, material_type="MAKESKIN")
    rig = T.HumanService.add_builtin_rig(human, "default")
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

    human.data.materials.clear(); human.data.materials.append(T.toon(f"da_{g}", T.SKIN[g]))
    for kind in ("hair", "eyebrows", "eyelashes"):
        o = parts[kind]
        img = next((n.image for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image), None)
        o.data.materials.clear()
        o.data.materials.append(T.toon(f"{kind}_{g}", "#1E1916" if kind == "hair" else "#2A211C", alpha_tex=img))
    if style and not rnd:
        eye_toon(parts["eyes"], g)
    T.shade_smooth(human)
    NET.append(human)
    me, region = T.posed(human)
    wz = min((rig.matrix_world @ rig.pose.bones[f"wrist.{s}"].head).z for s in "LR")
    body = T.Body(me, region, wz)
    T.outline(human, 0.0025)
    white = T.toon(f"lot_{g}", "#F4F1EA")
    z = body.z
    under = []
    if g == "nam":
        under.append(band(body, ("torso", "leg"), z(0.448), z(0.545), 0.006, "quan_lot_nam", [white]))
    else:
        under.append(band(body, ("torso", "leg"), z(0.47), z(0.54), 0.005, "quan_lot_nu", [white]))
        under.append(band(body, ("torso",), z(0.70), z(0.79), 0.006, "ao_lot_nu", [white]))
    for o in under:
        T.outline(o, 0.002)
    if jaw:                                            # bản sao phần đầu (chỉ để dựng mặt nạ đầu; ẩn khi render thường)
        import bmesh
        bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
        yn = min(c.co.y for c, r in zip(me.vertices, region) if r == "neck")        # mặt trước cổ: chỉ lấy phần đầu nằm trước đó (mặt, cằm)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if not all(region[v.index] == "head" and v.co.y < yn - 0.015 for v in f.verts)], context="FACES_ONLY")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        wm = bpy.data.materials.new("trang"); wm.use_nodes = True; wm.use_fake_user = True
        wm.node_tree.nodes.clear()
        em = wm.node_tree.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (1, 1, 1, 1)
        oo = wm.node_tree.nodes.new("ShaderNodeOutputMaterial"); wm.node_tree.links.new(em.outputs[0], oo.inputs[0])
        jo = T.new_obj(f"dau_{g}", bm, [wm]); jo.hide_render = True
        under.append(jo)
    return human, rig, body, under


def scene(items, per_row_x, width, out_prefix, views, zc=0.84, aspect=1.85):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = True
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    ld = bpy.data.lights.new("sun", "SUN"); ld.energy = 4.0; ld.angle = math.radians(5)
    lo = bpy.data.objects.new("sun", ld); sc.collection.objects.link(lo)
    if FS:                                             # Freestyle: nét viền theo đường biên thật (cằm đè lên cổ, tai, mũi...)
        sc.render.use_freestyle = True; sc.render.line_thickness_mode = "ABSOLUTE"; sc.render.line_thickness = FS
        vl = bpy.context.view_layer; vl.use_freestyle = True
        ls = vl.freestyle_settings.linesets.new("net") if not vl.freestyle_settings.linesets else vl.freestyle_settings.linesets[0]
        ls.select_silhouette = True; ls.select_border = False; ls.select_crease = False
        ls.linestyle.color = (0.11, 0.1, 0.09); ls.linestyle.alpha = 1.0; ls.linestyle.thickness = 2.0
        col = bpy.data.collections.new("net"); sc.collection.children.link(col)
        for o in NET:
            col.objects.link(o)
        ls.select_by_collection = True; ls.collection = col
    cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; cd.ortho_scale = width
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = 1900, int(1900 * aspect / width)
    for name, ang in views:
        a = math.radians(ang)
        cam.location = (8 * math.sin(a), -8 * math.cos(a), zc)
        cam.rotation_euler = (math.radians(90), 0, a)
        lo.rotation_euler = (math.radians(55), 0, a + math.radians(-30))
        sc.render.filepath = str(T.OUT / f"{out_prefix}_{name}.png")
        bpy.ops.render.render(write_still=True)
        heads = [o for o in bpy.data.objects if o.name.startswith("dau_")]
        if heads:                                      # lượt phụ: chỉ phần đầu → mặt nạ để vẽ nét cằm (đường biên đầu đè lên cổ)
            vis = {o: o.hide_render for o in bpy.data.objects}
            for o in bpy.data.objects:
                o.hide_render = o not in heads
            sc.render.use_freestyle = False
            sc.render.filepath = str(T.OUT / f"{out_prefix}_{name}_dau.png")
            bpy.ops.render.render(write_still=True)
            for o, v in vis.items():
                o.hide_render = v
        print("ANH", name)


def main():
    if MODE == "so_sanh":
        plan = [("nam", False, -1.05), ("nam", True, -0.35), ("nu", True, 0.35), ("nu", False, 1.05)]
        width, views, prefix = 2.7, [("truoc", 0)], "nguoi_so_sanh"
    elif MODE == "nu_thon":
        plan = [("nu", False, -1.05, None), ("nu", True, -0.35, "D"), ("nu", True, 0.35, "E"), ("nu", True, 1.05, "F")]
        for gg, style, x, sl in plan:
            human, rig, body, under = make(gg, style, sl)
            rig.location.x += x
            for o in under:
                o.location.x += x
            print("XONG", gg, sl, f"cao {body.H:.3f} m")
        scene(plan, None, 2.7, "nguoi_nu_thon", [("truoc", 0)], zc=0.76, aspect=1.62)
        return
    elif MODE == "nu_ngang":                           # góc nghiêng: các người xếp dọc theo trục nhìn → dời theo trục y để không chồng nhau
        plan = [("nu", False, -0.9, None), ("nu", True, -0.3, "D"), ("nu", True, 0.3, "E"), ("nu", True, 0.9, "F")]
        for gg, style, y, sl in plan:
            human, rig, body, under = make(gg, style, sl)
            rig.location.y += y
            for o in under:
                o.location.y += y
        scene(plan, None, 2.7, "nguoi_nu_ngang", [("nghieng", 90)], zc=0.76, aspect=1.62)
        return
    elif MODE == "mat_thon":                           # mặt thon: hiện tại | T1 | T2 | T3 (cùng giới)
        g = sys.argv[sys.argv.index("--") + 3]
        sl = "E" if g == "nu" else None
        plan = [(g, False, -0.42, None), (g, True, -0.14, "T1"), (g, True, 0.14, "T2"), (g, True, 0.42, "T3")]
        for gg, style, x, r in plan:
            human, rig, body, under = make(gg, style, sl if style else None, r)
            rig.location.x += x
        scene(plan, None, 1.2, f"nguoi_mat_thon_{g}", [("truoc", 0), ("nghieng", 35)], zc=1.58 if g == "nam" else 1.38, aspect=0.36)
        return
    elif MODE == "mat_cam":                            # mặt thon + đường cằm: bản trước | S1 | S2 | S3
        g = sys.argv[sys.argv.index("--") + 3]
        sl = "E" if g == "nu" else None
        plan = [(g, True, -0.42, "REF"), (g, True, -0.14, "S1"), (g, True, 0.14, "S2"), (g, True, 0.42, "S3")]
        for gg, style, x, r in plan:
            human, rig, body, under = make(gg, style, sl, r)
            rig.location.x += x
        scene(plan, None, 1.2, f"nguoi_mat_cam_{g}", [("truoc", 0), ("nghieng", 35)], zc=1.58 if g == "nam" else 1.38, aspect=0.36)
        return
    elif MODE == "mat_nam2":                           # nam theo ảnh mẫu: 4 kiểu tóc gọn, cùng một khuôn mặt V2, có nét cằm
        plan = [("nam", True, -0.42 + 0.28 * i, k, "short01") for i, k in enumerate(["V4", "B1", "B2", "B3"])]
        for gg, style, x, r, h in plan:
            human, rig, body, under = make(gg, style, None, r, hair=h, jaw=0.0028)
            rig.location.x += x
            for o in under:
                o.location.x += x
        scene(plan, None, 1.2, "nguoi_mat_nam2", [("truoc", 0), ("nghieng", 35)], zc=1.58, aspect=0.36)
        return
    elif MODE in ("mat_nam", "mat_nu"):
        g = MODE[4:]
        plan = [(g, False, -0.2), (g, True, 0.2)]
        for gg, style, x in plan:
            human, rig, body, under = make(gg, style)
            rig.location.x += x
        scene(plan, None, 0.8, f"nguoi_{MODE}", [("truoc", 0), ("nghieng", 35)], zc=1.58 if g == "nam" else 1.4, aspect=0.8)
        return
    else:
        plan = [("nam", True, -0.3), ("nu", True, 0.3)]
        width, views, prefix = 1.5, [("truoc", 0), ("nghieng", 35), ("sau", 180)], "nguoi_de_xuat"
    for g, style, x in plan:
        human, rig, body, under = make(g, style)
        rig.location.x += x
        for o in under:
            o.location.x += x
        print("XONG", g, "de_xuat" if style else "hien_tai", f"cao {body.H:.3f} m")
    scene(plan, None, width, prefix, views)


main()

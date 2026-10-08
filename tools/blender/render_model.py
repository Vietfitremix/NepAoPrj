"""Dựng người mẫu bằng MakeHuman (MPFB2) trong Blender và render 4 góc nhìn trực giao vào khung 400x800 của dự án.

Chạy (Blender chạy nền, không mở giao diện):
  .tools/blender/blender.exe -b --factory-startup --python tools/blender/render_model.py -- nu .tools/render
Kết quả: <out>/<gioi>_<goc>_mask.png (hình bóng, nền trong suốt) và <gioi>_<goc>_shade.png (tô bóng xám) cho 4 góc truoc/trai/phai/sau.

Căn khung: đáy bàn chân ở y=781, đỉnh đầu ở y=781−chiều_cao (đơn vị khung), trục giữa x=200 — giống mốc người mẫu SVG cũ.
Ảnh render gấp RES lần khung (mặc định 4 → 1600x3200) để vector hoá chính xác.
"""
import math
import sys
from pathlib import Path

import addon_utils
import bpy
from mathutils import Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
GENDER = argv[0] if argv else "nu"
OUT = Path(argv[1] if len(argv) > 1 else ".tools/render")
OUT.mkdir(parents=True, exist_ok=True)
RES = 4
FEET_Y, FRAME_H = 781, 739            # đáy chân và chiều cao người (đơn vị khung 400x800), như người mẫu cũ

# ---------------------------------------------------------------- bật MPFB
for mod in ("bl_ext.user_default.mpfb", "mpfb"):
    try:
        addon_utils.enable(mod, default_set=True)
        if mod in bpy.context.preferences.addons:
            MPFB = mod
            break
    except Exception:
        pass
else:
    raise SystemExit("Không bật được MPFB")
HumanService = __import__(f"{MPFB}.services.humanservice", fromlist=["HumanService"]).HumanService
LocationService = __import__(f"{MPFB}.services.locationservice", fromlist=["LocationService"]).LocationService
sys.path.insert(0, str(Path(__file__).parent))
from face_presets import EYEBROWS, EYELASHES, FACE, HAIR, PRESETS, apply_face   # noqa: E402

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- thông số cơ thể (thang 0..1 của MakeHuman)
MACRO = {
    "nu": dict(gender=0.0, age=0.5, muscle=0.45, weight=0.42, proportions=0.75, height=0.45, cupsize=0.45, firmness=0.6),
    "nam": dict(gender=1.0, age=0.5, muscle=0.55, weight=0.48, proportions=0.75, height=0.55, cupsize=0.5, firmness=0.5),
}[GENDER]
MACRO["race"] = {"asian": 1.0, "caucasian": 0.0, "african": 0.0}

human = HumanService.create_human(mask_helpers=True, detailed_helpers=True,      # cần nhóm "joint-" để ướm khung xương đúng
                                  extra_vertex_groups=True,
                                  feet_on_ground=True, scale=0.1, macro_detail_dict=MACRO)
apply_face(human, Path(LocationService.get_mpfb_data("targets")), PRESETS[GENDER][FACE[GENDER]])

# ---------------------------------------------------------------- khung xương + hạ tay (tư thế đứng thẳng, tay buông sát người)
rig = HumanService.add_builtin_rig(human, "default")
# Tư thế nghỉ của MakeHuman: tay chếch xuống ~48° (chữ A). Theo file t-pose.json của MPFB, nâng tay là xoay upperarm01 quanh Z
# dấu dương (bên L). Ở đây xoay ngược lại để tay buông gần thẳng; duỗi cẳng tay (lowerarm01 quanh X âm) như t-pose.
ARM_OUT = float(argv[2]) if len(argv) > 2 else 0.16       # độ tách tay khỏi thân (ngang/dọc)
LEG_IN = {"nu": 0.05, "nam": 0.08}[GENDER]                   # độ chếch vào trong của đùi (nữ ít hơn để đùi không chạm nhau)
ELBOW = float(argv[3]) if len(argv) > 3 else 0.0          # độ duỗi khuỷu tay
if rig is not None:
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    from mathutils import Vector

    def aim(pb, world_dir):
        """Xoay xương sao cho hướng đầu→đuôi (trong không gian thực) trùng world_dir.
        Tính phép xoay trong không gian khung xương rồi quy đổi sang hệ trục riêng của xương (không phụ thuộc trục xương)."""
        bpy.context.view_layer.update()
        cur = (pb.tail - pb.head).normalized()
        target = (rig.matrix_world.to_3x3().inverted() @ Vector(world_dir)).normalized()
        q = cur.rotation_difference(target)
        R = pb.matrix.to_3x3().normalized().to_quaternion()
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = pb.rotation_quaternion @ (R.inverted() @ q @ R)
        bpy.context.view_layer.update()

    for side, sx in (("L", 1), ("R", -1)):              # L = bên trái người mẫu = +X; người mẫu nhìn về −Y
        aim(rig.pose.bones[f"upperarm01.{side}"], (sx * ARM_OUT, 0.03, -1.0))
        aim(rig.pose.bones[f"lowerarm01.{side}"], (sx * ARM_OUT * 0.5, -0.10, -1.0))
        # khép chân: đùi chếch vào trong, cẳng chân gần thẳng đứng → hai bàn chân cách nhau ~3 cm như người mẫu cũ
        aim(rig.pose.bones[f"upperleg02.{side}"], (-sx * LEG_IN, 0.0, -1.0))
        aim(rig.pose.bones[f"lowerleg01.{side}"], (-sx * LEG_IN * 0.6, 0.02, -1.0))
        u = rig.pose.bones[f"upperarm01.{side}"]
        print("TAY", side, "huong", tuple(round(x, 2) for x in (rig.matrix_world.to_3x3() @ (u.tail - u.head)).normalized()))
    bpy.ops.object.mode_set(mode="OBJECT")

# ---------------------------------------------------------------- mắt, lông mi, lông mày, tóc (MakeHuman CC0), có da để render texture
DATA = Path(LocationService.get_user_data(""))
_skin = f"young_asian_{'female' if GENDER == 'nu' else 'male'}"
HumanService.set_character_skin(str(DATA / "skins" / _skin / f"{_skin}.mhmat"), human, skin_type="MAKESKIN")
PARTS = {}
for kind, name in (("eyes", "high-poly"), ("eyelashes", EYELASHES[GENDER]), ("eyebrows", EYEBROWS[GENDER]), ("hair", HAIR[GENDER])):
    PARTS[kind] = HumanService.add_mhclo_asset(str(DATA / kind / name / f"{name}.mhclo"), human, asset_type=kind.capitalize(),
                                               subdiv_levels=1, material_type="MAKESKIN")
# màu phân vùng cho lớp "id" (tô phẳng, không khử răng cưa → tách vùng bằng màu gần nhất)
ID_COLORS = {"human": (1, 0, 0, 1), "eyes": (0, 1, 1, 1), "eyelashes": (1, 1, 0, 1), "eyebrows": (0, 0, 1, 1), "hair": (0, 1, 0, 1)}
human.color = ID_COLORS["human"]
for kind, o in PARTS.items():
    o.color = ID_COLORS[kind]

# Nhóm điểm "cánh tay" (theo trọng số khung xương) để render riêng tay gần ở góc nghiêng
ARM_BONES = ("upperarm01", "upperarm02", "lowerarm01", "lowerarm02", "wrist", "finger", "metacarpal")
arm_masks = {}
for side in ("L", "R"):
    idx = [g.index for g in human.vertex_groups if g.name.startswith(ARM_BONES) and g.name.endswith("." + side)]
    vg = human.vertex_groups.new(name=f"tay_{side}")
    members = [v.index for v in human.data.vertices if sum(g.weight for g in v.groups if g.group in idx) > 0.5]
    vg.add(members, 1.0, "REPLACE")
    m = human.modifiers.new(f"chi_tay_{side}", "MASK")
    m.vertex_group = vg.name
    m.show_render = m.show_viewport = False
    arm_masks[side] = m
vg = human.vertex_groups.new(name="tay_LR")                     # hai tay (dùng cho góc trước, sau)
both_idx = [human.vertex_groups[f"tay_{s}"].index for s in ("L", "R")]
vg.add([v.index for v in human.data.vertices if any(g.group in both_idx and g.weight > 0.5 for g in v.groups)], 1.0, "REPLACE")
m = human.modifiers.new("chi_hai_tay", "MASK")
m.vertex_group = "tay_LR"
m.show_render = m.show_viewport = False
arm_masks["LR"] = m
m = human.modifiers.new("chi_moi", "MASK")                     # lớp môi riêng (nhóm điểm "lips" của MakeHuman)
m.vertex_group = "lips"
m.show_render = m.show_viewport = False
lip_mask = m

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = human.evaluated_get(dg)
zs = [(ev.matrix_world @ v.co).z for v in ev.data.vertices]
H = max(zs) - min(zs)
k = H / FRAME_H                         # mét trên mỗi đơn vị khung

# ---------------------------------------------------------------- vật liệu và render
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x, scene.render.resolution_y = 400 * RES, 800 * RES
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
sh = scene.display.shading
sh.color_type = "SINGLE"

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 800 * k
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
zc = (FEET_Y - 400) * k + min(zs)       # tâm khung (y=400) ứng với độ cao này

VIEWS = {   # vị trí camera, góc quay: người mẫu MakeHuman nhìn về −Y
    "truoc": ((0, -10, zc), (math.radians(90), 0, 0)),
    "sau": ((0, 10, zc), (math.radians(90), 0, math.radians(180))),
    "trai": ((10, 0, zc), (math.radians(90), 0, math.radians(90))),     # thấy bên trái người mẫu, mặt quay sang trái khung
    "phai": ((-10, 0, zc), (math.radians(90), 0, math.radians(-90))),
}
def show_parts(on):
    for o in PARTS.values():
        o.hide_render = not on


for view, (loc, rot) in VIEWS.items():
    cam.location, cam.rotation_euler = loc, rot
    show_parts(False)
    sh.color_type = "SINGLE"
    # hình bóng: tô phẳng một màu
    sh.light, sh.single_color, sh.show_cavity, sh.show_object_outline = "FLAT", (1, 1, 1), False, False
    scene.render.filepath = str(OUT / f"{GENDER}_{view}_mask.png")
    bpy.ops.render.render(write_still=True)
    # tô bóng: đèn studio, có hốc tối (cavity) để lấy mảng sáng tối và nếp cơ
    sh.light, sh.studio_light = "STUDIO", "Default"
    sh.single_color, sh.show_cavity = (0.8, 0.8, 0.8), True
    scene.render.filepath = str(OUT / f"{GENDER}_{view}_shade.png")
    bpy.ops.render.render(write_still=True)
    if True:                                           # lớp tay: góc nghiêng chỉ tay gần (trái: L, phải: R), góc trước/sau cả hai tay
        m = arm_masks["L" if view == "trai" else "R" if view == "phai" else "LR"]
        m.show_render = m.show_viewport = True
        sh.light, sh.single_color, sh.show_cavity = "FLAT", (1, 1, 1), False
        scene.render.filepath = str(OUT / f"{GENDER}_{view}_arm.png")
        bpy.ops.render.render(write_still=True)
        m.show_render = m.show_viewport = False
    if view != "sau":
        lip_mask.show_render = lip_mask.show_viewport = True
        scene.render.filepath = str(OUT / f"{GENDER}_{view}_lips.png")
        bpy.ops.render.render(write_still=True)
        lip_mask.show_render = lip_mask.show_viewport = False
    # lớp phân vùng: da / mắt / lông mi / lông mày / tóc
    show_parts(True)
    sh.light, sh.color_type, sh.show_cavity = "FLAT", "OBJECT", False
    scene.display.render_aa = "OFF"
    scene.render.filepath = str(OUT / f"{GENDER}_{view}_id.png")
    bpy.ops.render.render(write_still=True)
    # lớp texture: tròng mắt, môi, vân tóc
    scene.display.render_aa = "8"
    sh.light, sh.studio_light, sh.color_type, sh.show_cavity = "STUDIO", "Default", "TEXTURE", True
    scene.render.filepath = str(OUT / f"{GENDER}_{view}_tex.png")
    bpy.ops.render.render(write_still=True)

print(f"XONG {GENDER}: cao {H:.3f} m, {k * 1000:.2f} mm/đơn vị khung")

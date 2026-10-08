"""Render chân dung cận mặt (EEVEE) người mẫu MakeHuman với da, mắt, lông mày, lông mi, tóc (CC0) để chọn khuôn mặt.

Mỗi bộ mặt trong face_presets.PRESETS được dựng lại từ đầu (target mặt nạp trước, rồi mới gắn tóc/lông mày cho khớp).
Chạy: .tools/blender/blender.exe -b --factory-startup --python tools/blender/face_preview.py -- nu D:/.../.tools/face_preview [preset ...]
"""
import math
import sys
from pathlib import Path

import addon_utils
import bpy

sys.path.insert(0, str(Path(__file__).parent))
from face_presets import EYEBROWS, EYELASHES, HAIR, PRESETS, apply_face   # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
GENDER, OUT = argv[0], Path(argv[1])
NAMES = argv[2:] or ["goc"] + list(PRESETS[GENDER])
OUT.mkdir(parents=True, exist_ok=True)
addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
from bl_ext.user_default.mpfb.services.humanservice import HumanService          # noqa: E402
from bl_ext.user_default.mpfb.services.locationservice import LocationService    # noqa: E402

data = Path(LocationService.get_user_data(""))
MACRO = {"gender": 0.0 if GENDER == "nu" else 1.0, "age": 0.5, "muscle": 0.5, "weight": 0.45, "proportions": 0.75,
         "height": 0.5, "cupsize": 0.45, "firmness": 0.6, "race": {"asian": 1.0, "caucasian": 0.0, "african": 0.0}}


def build(preset: dict):
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    human = HumanService.create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True,
                                      feet_on_ground=True, scale=0.1, macro_detail_dict=MACRO)
    apply_face(human, Path(LocationService.get_mpfb_data("targets")), preset)
    skin = f"young_asian_{'female' if GENDER == 'nu' else 'male'}"
    HumanService.set_character_skin(str(data / "skins" / skin / f"{skin}.mhmat"), human, skin_type="MAKESKIN")

    def add(kind, name):
        return HumanService.add_mhclo_asset(str(data / kind / name / f"{name}.mhclo"), human,
                                            asset_type=kind.capitalize(), subdiv_levels=1, material_type="MAKESKIN")

    eyes = add("eyes", "high-poly")
    add("eyelashes", EYELASHES[GENDER])
    add("eyebrows", EYEBROWS[GENDER])
    hair = add("hair", HAIR[GENDER])
    for m in hair.data.materials:                                  # nhuộm tóc nâu đen
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.outputs["Color"].links:
                mix = m.node_tree.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
                mix.inputs[0].default_value = 1.0; mix.inputs[7].default_value = (0.16, 0.12, 0.11, 1)
                for link in list(n.outputs["Color"].links):
                    to = link.to_socket
                    m.node_tree.links.remove(link)
                    m.node_tree.links.new(mix.outputs[2], to)
                hsv = m.node_tree.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 0.0
                m.node_tree.links.new(n.outputs["Color"], hsv.inputs["Color"])
                m.node_tree.links.new(hsv.outputs["Color"], mix.inputs[6])
    return sum((eyes.matrix_world @ v.co).z for v in eyes.data.vertices) / len(eyes.data.vertices)


def stage(eye_z):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.render.resolution_x = sc.render.resolution_y = 700
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.88, 0.86, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    for loc, e, col in (((-3, -4, eye_z + 1), 1.8, (1, 0.97, 0.92)), ((3, -3, eye_z + 0.5), 0.8, (0.92, 0.95, 1))):
        ld = bpy.data.lights.new("l", "SUN"); ld.energy = e; ld.color = col
        lo = bpy.data.objects.new("l", ld); sc.collection.objects.link(lo); lo.location = loc
        lo.rotation_euler = (math.radians(65), 0, math.atan2(loc[0], -loc[1]))
    cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 0.32
    cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
    return sc, cam


for name in NAMES:
    eye_z = build({} if name == "goc" else PRESETS[GENDER][name])
    sc, cam = stage(eye_z)
    for view, ang in (("truoc", 0), ("nghieng", 35), ("trai", 90), ("sau", 180)):
        a = math.radians(ang)
        cam.location = (5 * math.sin(a), -5 * math.cos(a), eye_z - 0.03)
        cam.rotation_euler = (math.radians(90), 0, a)
        sc.render.filepath = str(OUT / f"{GENDER}_{name}_{view}.png")
        bpy.ops.render.render(write_still=True)
    print("MAT", name)

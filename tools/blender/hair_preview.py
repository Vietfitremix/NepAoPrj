"""Render thử các kiểu tóc MakeHuman (CC0) trên người mẫu, góc trước và góc nghiêng, để chọn kiểu.

Chạy: .tools/blender/blender.exe -b --factory-startup --python tools/blender/hair_preview.py -- nu D:/.../.tools/hair_preview
"""
import math
import sys
from pathlib import Path

import addon_utils
import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
GENDER, OUT = argv[0], Path(argv[1])
OUT.mkdir(parents=True, exist_ok=True)
addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
from bl_ext.user_default.mpfb.services.humanservice import HumanService          # noqa: E402
from bl_ext.user_default.mpfb.services.locationservice import LocationService    # noqa: E402

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
macro = {"gender": 0.0 if GENDER == "nu" else 1.0, "age": 0.5, "muscle": 0.5, "weight": 0.45, "proportions": 0.75,
         "height": 0.5, "cupsize": 0.45, "firmness": 0.6, "race": {"asian": 1.0, "caucasian": 0.0, "african": 0.0}}
human = HumanService.create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True,
                                  feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
zs = [(human.matrix_world @ v.co).z for v in human.data.vertices]
top = max(zs)

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x = sc.render.resolution_y = 500
sc.render.film_transparent = True
sh = sc.display.shading
sh.light, sh.studio_light, sh.color_type, sh.show_cavity = "STUDIO", "Default", "MATERIAL", True
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 0.5
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam

hair_dir = Path(LocationService.get_user_data("hair"))
styles = argv[2:] or sorted(p.name for p in hair_dir.iterdir() if p.is_dir())
for name in styles:
    mhclo = hair_dir / name / f"{name}.mhclo"
    hair = HumanService.add_mhclo_asset(str(mhclo), human, asset_type="Hair", subdiv_levels=0, material_type="MAKESKIN")
    for view, loc, rot in (("truoc", (0, -5, top - 0.16), (90, 0, 0)), ("trai", (5, 0, top - 0.16), (90, 0, 90)),
                           ("sau", (0, 5, top - 0.16), (90, 0, 180))):
        cam.location = loc
        cam.rotation_euler = [math.radians(a) for a in rot]
        sc.render.filepath = str(OUT / f"{GENDER}_{name}_{view}.png")
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(hair, do_unlink=True)
    print("TOC", name)

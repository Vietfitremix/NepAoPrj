"""Create a stylized, editable ao dai character and a transparent PNG."""
from pathlib import Path
from mathutils import Vector
import bpy

ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT / 'assets/archive/blender/viet-fit-character.blend'
IMAGE = ROOT / 'frontend/public/figure/blender/viet-fit-character.png'
SCENE.parent.mkdir(parents=True, exist_ok=True)
IMAGE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def material(name, color, roughness=0.6):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


skin = material('Skin', (0.65, 0.38, 0.24))
hair = material('Hair', (0.025, 0.016, 0.025))
cloth = material('Ao dai - teal', (0.025, 0.32, 0.30))
trousers = material('Ivory trousers', (0.85, 0.79, 0.65))
gold = material('Gold trim', (0.8, 0.52, 0.12), 0.35)
white = material('Eyes', (0.95, 0.93, 0.88))
lip = material('Lips', (0.38, 0.075, 0.065))


def ellipsoid(name, position, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def limb(name, start, end, radius, mat):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=radius, radius2=radius * 0.85,
                                    depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Soft edges', 'BEVEL')
    bevel.width, bevel.segments = 0.045, 3
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


# Face looks toward negative Y. Parts remain separate for easy editing.
for side in (-1, 1):
    x = side * 0.15
    limb(f'Trouser leg {side}', (x, 0, 0.15), (x, 0, 0.97), 0.115, trousers)
    ellipsoid(f'Shoe {side}', (x, -0.07, 0.11), (0.12, 0.22, 0.10), hair)
    limb(f'Sleeve {side}', (side*0.23, 0, 1.52), (side*0.40, -0.02, 1.04), 0.105, cloth)
    ellipsoid(f'Hand {side}', (side*0.41, -0.02, 0.99), (0.068, 0.065, 0.105), skin)

ellipsoid('Tunic bodice', (0, 0, 1.29), (0.26, 0.145, 0.36), cloth)
# Two separated long panels suggest the side slits of an ao dai.
ellipsoid('Front tunic panel', (0, -0.105, 0.86), (0.275, 0.047, 0.48), cloth)
ellipsoid('Back tunic panel', (0, 0.105, 0.86), (0.275, 0.047, 0.48), cloth)
limb('Neck', (0, 0, 1.53), (0, 0, 1.72), 0.085, skin)
limb('Standing collar', (0, 0, 1.54), (0, 0, 1.62), 0.102, cloth)
ellipsoid('Head', (0, -0.015, 1.85), (0.185, 0.158, 0.235), skin)
ellipsoid('Hair cap', (0, 0.035, 1.98), (0.192, 0.155, 0.14), hair)
ellipsoid('Hair bun', (0, 0.18, 1.92), (0.115, 0.11, 0.13), hair)
for side in (-1, 1):
    ellipsoid(f'Ear {side}', (side*0.177, 0, 1.85), (0.03, 0.035, 0.058), skin)
    ellipsoid(f'Eye {side}', (side*0.067, -0.157, 1.89), (0.036, 0.013, 0.022), white)
    ellipsoid(f'Pupil {side}', (side*0.067, -0.169, 1.89), (0.014, 0.007, 0.016), hair)
    ellipsoid(f'Brow {side}', (side*0.067, -0.153, 1.93), (0.04, 0.012, 0.008), hair)
ellipsoid('Nose', (0, -0.171, 1.84), (0.025, 0.03, 0.04), skin)
ellipsoid('Mouth', (0, -0.163, 1.775), (0.035, 0.01, 0.009), lip)
for z in (1.48, 1.40, 1.32):
    ellipsoid(f'Tunic button {z}', (0.11, -0.135, z), (0.014, 0.014, 0.014), gold)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 768
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = str(IMAGE)
scene.world.color = (0.25, 0.25, 0.25)

target = Vector((0, 0, 1.1))
bpy.ops.object.camera_add(location=(2.2, -7, 2.5))
camera = bpy.context.object
camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.65
scene.camera = camera
for name, position, power, size in [
    ('Key light', (-3, -4, 5), 500, 4),
    ('Fill light', (3, -2, 3), 250, 3),
    ('Rim light', (1, 3, 4), 450, 3),
]:
    bpy.ops.object.light_add(type='AREA', location=position)
    light = bpy.context.object
    light.name = name
    light.data.energy, light.data.shape, light.data.size = power, 'DISK', size
    light.rotation_euler = (target-light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(SCENE))
bpy.ops.render.render(write_still=True)
print(f'Created {SCENE} and {IMAGE}')

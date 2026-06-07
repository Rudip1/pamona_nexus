# Extract plants, force each material's diffuse image -> Principled Base Color
# (Blender's exporters only emit map_Kd for a DIRECT image->base-color link),
# unpack textures, and export textured OBJ+MTL per plant + combined.
# Run with --disable-autoexec.
#   blender --background --disable-autoexec <in.blend> --python export_textured_obj.py -- <outdir>
import bpy, os, sys

outdir = sys.argv[sys.argv.index("--") + 1:][0]
texdir = os.path.join(outdir, "textures")
os.makedirs(texdir, exist_ok=True)
KEEP = "Strawberry_"

for o in list(bpy.data.objects):
    if not (o.type == 'MESH' and o.name.startswith(KEEP)):
        bpy.data.objects.remove(o, do_unlink=True)
plants = sorted([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda x: x.name)

# --- collect materials used by plants; wire diffuse image into Base Color ---
mats = set()
for o in plants:
    for s in o.material_slots:
        if s.material:
            mats.add(s.material)

def img_of(nt, kw):
    for n in nt.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            fp = (n.image.filepath or n.image.name).lower()
            if kw in fp:
                return n
    return None

for m in mats:
    if not m.use_nodes:
        continue
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf:
        continue
    diff = img_of(nt, 'diffuse')
    if diff:
        nt.links.new(diff.outputs['Color'], bsdf.inputs['Base Color'])
        print("BASE", m.name, "->", os.path.basename(diff.image.filepath))
    if m.name == 'Leaves':
        a = img_of(nt, 'alpha')
        if a:
            nt.links.new(a.outputs['Color'], bsdf.inputs['Alpha'])
            m.blend_method = 'CLIP'
            print("ALPHA", m.name)

# --- unpack textures to disk, repoint to relative path next to the obj ---
for img in bpy.data.images:
    if not img.packed_file:
        continue
    fn = os.path.basename(img.filepath.replace("\\", "/")) or img.name + ".png"
    fn = fn.replace(" ", "_").replace("#", "")
    img.filepath_raw = os.path.join(texdir, fn)
    try:
        img.save()
    except Exception as e:
        print("save fail", img.name, e); continue
    img.filepath = os.path.join(texdir, fn)   # abs; RELATIVE path_mode makes it textures/fn

def isolate(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    bpy.context.view_layer.objects.active = o

def obj_export(base):
    bpy.ops.wm.obj_export(filepath=base + ".obj", export_selected_objects=True,
                          export_materials=True, path_mode='RELATIVE',
                          export_uv=True, export_normals=True)

for i, p in enumerate(plants, 1):
    isolate(p)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    p.location = (0.0, 0.0, p.dimensions.z / 2.0)
    obj_export(os.path.join(outdir, f"strawberry_plant_{i:02d}"))
    print("WROTE", f"strawberry_plant_{i:02d}.obj")

bpy.ops.object.select_all(action='SELECT')
obj_export(os.path.join(outdir, "strawberry_plants_all"))
print("DONE")

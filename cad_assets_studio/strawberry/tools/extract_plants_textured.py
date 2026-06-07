# Extract only the strawberry plants, unpack & repoint their packed textures,
# and export self-contained textured per-plant DAE/STL + combined files.
# Run with --disable-autoexec so embedded scripts NEVER execute.
#   blender --background --disable-autoexec <in.blend> --python extract_plants_textured.py -- <outdir>
import bpy, os, sys

outdir = sys.argv[sys.argv.index("--") + 1:][0]
texdir = os.path.join(outdir, "textures")
os.makedirs(texdir, exist_ok=True)
KEEP_PREFIX = "Strawberry_"

# --- drop pot, soil, empties ---
for o in list(bpy.data.objects):
    if not (o.type == 'MESH' and o.name.startswith(KEEP_PREFIX)):
        bpy.data.objects.remove(o, do_unlink=True)
plants = sorted([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda x: x.name)

# --- find images actually used by the surviving plant materials ---
used = set()
for o in plants:
    for slot in o.material_slots:
        m = slot.material
        if not m or not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                used.add(n.image)

# --- unpack each used image to textures/<clean name>, repoint to relative path ---
for img in used:
    if not img.packed_file:
        continue
    fname = os.path.basename(img.filepath.replace("\\", "/")) or (img.name + ".png")
    fname = fname.replace(" ", "_").replace("#", "")
    dest = os.path.join(texdir, fname)
    img.filepath_raw = dest
    try:
        img.save()                       # write unpacked pixels to disk
    except Exception as e:
        print("save fail", img.name, e)
        continue
    img.filepath = os.path.join("textures", fname)   # relative to the .dae
    print("TEX", fname)

def isolate(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    bpy.context.view_layer.objects.active = o

def export_sel(base):
    try:
        bpy.ops.wm.collada_export(filepath=base + ".dae", selected=True,
                                  apply_modifiers=True, triangulate=True)
    except Exception as e: print("DAE fail", base, e)
    try:
        bpy.ops.wm.stl_export(filepath=base + ".stl",
                              export_selected_objects=True, apply_modifiers=True)
    except Exception as e: print("STL fail", base, e)

for i, p in enumerate(plants, 1):
    isolate(p)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    p.location = (0.0, 0.0, p.dimensions.z / 2.0)
    base = os.path.join(outdir, f"strawberry_plant_{i:02d}")
    export_sel(base)
    print("WROTE", base)

bpy.ops.object.select_all(action='SELECT')
export_sel(os.path.join(outdir, "strawberry_plants_all"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(outdir, "strawberry_plants_only.blend"))
print("DONE")

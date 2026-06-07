# Extract only the strawberry plants from the planter scene (drop pot + soil),
# center each with its base at z=0, and export per-plant + combined files.
# Run with --disable-autoexec so the .blend's embedded scripts NEVER execute.
#   blender --background --disable-autoexec <in.blend> --python extract_plants.py -- <outdir>
import bpy, os, sys

outdir = sys.argv[sys.argv.index("--") + 1:][0]
os.makedirs(outdir, exist_ok=True)

KEEP_PREFIX = "Strawberry_"   # the 8 plant meshes

# --- delete everything that isn't a plant mesh (pot, soil, empties) ---
for o in list(bpy.data.objects):
    if not (o.type == 'MESH' and o.name.startswith(KEEP_PREFIX)):
        bpy.data.objects.remove(o, do_unlink=True)

plants = sorted([o for o in bpy.data.objects if o.type == 'MESH'],
                key=lambda x: x.name)
print("PLANTS KEPT:", [o.name for o in plants])
print("MATERIALS:", [m.name for m in bpy.data.materials])
print("IMAGES:", [(i.name, i.filepath) for i in bpy.data.images])


def isolate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def center_base_z0(obj):
    # origin to geometry bounds center, then lift so the bbox bottom rests on z=0
    isolate(obj)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0.0, 0.0, obj.dimensions.z / 2.0)


def export_selected(base):
    try:
        bpy.ops.wm.collada_export(filepath=base + ".dae", selected=True,
                                  apply_modifiers=True, triangulate=True)
    except Exception as e:
        print("DAE fail", base, e)
    try:
        bpy.ops.wm.stl_export(filepath=base + ".stl",
                              export_selected_objects=True, apply_modifiers=True)
    except Exception as e:
        print("STL fail", base, e)


# --- per-plant exports (centered, base at z=0) ---
for i, p in enumerate(plants, 1):
    center_base_z0(p)
    base = os.path.join(outdir, f"strawberry_plant_{i:02d}")
    export_selected(base)
    print("WROTE", base + ".{dae,stl}")

# --- combined: all plants together ---
bpy.ops.object.select_all(action='SELECT')
combo = os.path.join(outdir, "strawberry_plants_all")
export_selected(combo)
try:
    bpy.ops.wm.obj_export(filepath=combo + ".obj", export_selected_objects=True)
except Exception as e:
    print("OBJ fail", e)
try:
    bpy.ops.export_scene.gltf(filepath=combo + ".glb", use_selection=True,
                              export_format='GLB')
except Exception as e:
    print("GLB fail", e)

# --- clean .blend with plants only ---
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(outdir, "strawberry_plants_only.blend"))
print("DONE")

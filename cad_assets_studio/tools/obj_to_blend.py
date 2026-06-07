# Build a CLEAN, editable .blend from OBJ files (geometry+materials only, no
# code lineage). Textures are packed so the .blend is self-contained.
# Imported objects are spaced along X so they're easy to edit side by side.
#   blender --background --python obj_to_blend.py -- <indir-with-objs> <out.blend> [glob]
import bpy, sys, os, glob

argv = sys.argv[sys.argv.index("--") + 1:]
indir, outblend = argv[0], argv[1]
pattern = argv[2] if len(argv) > 2 else "*.obj"

bpy.ops.wm.read_factory_settings(use_empty=True)

i = 0
for objfile in sorted(glob.glob(os.path.join(indir, pattern))):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=objfile)
    for o in [x for x in bpy.data.objects if x not in before]:
        o.location.x += i * 0.6
    i += 1
    print("IMPORTED", os.path.basename(objfile))

# pack textures into the blend so it's portable/editable anywhere
try:
    bpy.ops.file.pack_all()
    print("packed textures")
except Exception as e:
    print("pack warn:", e)

os.makedirs(os.path.dirname(outblend), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=outblend)
print("SAVED", outblend, "(", i, "objects )")

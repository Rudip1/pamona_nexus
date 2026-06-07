# Headless Blender exporter: .blend -> .dae + .stl
# Usage: blender --background --python blend_export.py -- <in.blend> <out_basepath>
import bpy, sys

argv = sys.argv[sys.argv.index("--") + 1:]
infile, outbase = argv[0], argv[1]

bpy.ops.wm.open_mainfile(filepath=infile)

# select everything so exporters that honor selection include the whole scene
try:
    bpy.ops.object.select_all(action='SELECT')
except Exception as e:
    print("select_all warn:", e)

# ---- COLLADA (.dae) — keeps materials/colors ----
try:
    bpy.ops.wm.collada_export(filepath=outbase + ".dae",
                              apply_modifiers=True, triangulate=True)
    print("WROTE", outbase + ".dae")
except Exception as e:
    print("DAE FAILED:", e)

# ---- STL (geometry only) — try new 4.x exporter, fall back to legacy addon ----
wrote = False
try:
    bpy.ops.wm.stl_export(filepath=outbase + ".stl", apply_modifiers=True)
    wrote = True
except Exception as e:
    print("new stl exporter unavailable:", e)
if not wrote:
    try:
        bpy.ops.preferences.addon_enable(module="io_mesh_stl")
        bpy.ops.export_mesh.stl(filepath=outbase + ".stl")
        wrote = True
    except Exception as e:
        print("legacy stl failed:", e)
print("WROTE" if wrote else "STL FAILED", outbase + ".stl")

# Convert one OBJ -> DAE + STL (geometry).  (DAE here is geometry-only; for
# textured Gazebo use the OBJ+MTL — Blender's collada export drops node textures.)
#   blender --background --python obj_to_dae_stl.py -- <in.obj> <out_basepath>
import bpy, sys
inobj, outbase = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=inobj)
bpy.ops.object.select_all(action='SELECT')
try:
    bpy.ops.wm.collada_export(filepath=outbase + ".dae", apply_modifiers=True, triangulate=True)
except Exception as e:
    print("DAE fail", e)
try:
    bpy.ops.wm.stl_export(filepath=outbase + ".stl", apply_modifiers=True)
except Exception as e:
    print("STL fail", e)
print("OK", outbase)

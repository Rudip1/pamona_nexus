# Import a textured OBJ and render a preview PNG (CPU Cycles, headless-safe).
#   blender --background --python render_preview.py -- <in.obj> <out.png>
import bpy, sys, math
from mathutils import Vector

inobj, outpng = sys.argv[sys.argv.index("--") + 1:][:2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=inobj)

objs = [o for o in bpy.data.objects if o.type == 'MESH']
# bounding box center + size
mn = Vector((1e9, 1e9, 1e9)); mx = -mn
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
ctr = (mn + mx) / 2
size = (mx - mn).length

# camera
cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = ctr + Vector((size, -size, size * 0.6))
d = ctr - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# light
sun = bpy.data.lights.new("sun", 'SUN'); sun.energy = 4
so = bpy.data.objects.new("sun", sun); bpy.context.scene.collection.objects.link(so)
so.rotation_euler = (math.radians(50), math.radians(20), math.radians(30))
# sky-ish world
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.75, 0.9, 1)

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 24
sc.render.resolution_x = 800
sc.render.resolution_y = 800
sc.render.film_transparent = False
sc.render.filepath = outpng
bpy.ops.render.render(write_still=True)
print("RENDERED", outpng)

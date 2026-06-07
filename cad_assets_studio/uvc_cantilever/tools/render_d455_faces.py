# Render the D455 STL from +Y and -Y to see which face has the lens.
#   blender --background --python render_d455_faces.py -- <stl> <outdir>
import bpy, sys, math, os
from mathutils import Vector
stl, outd = sys.argv[sys.argv.index("--")+1:][:2]
os.makedirs(outd, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
try:    bpy.ops.wm.stl_import(filepath=stl)
except: bpy.ops.import_mesh.stl(filepath=stl)
o=[x for x in bpy.data.objects if x.type=='MESH'][0]; o.scale=(0.001,)*3
bpy.context.view_layer.update()
sun=bpy.data.lights.new("s",'SUN'); sun.energy=3.5
so=bpy.data.objects.new("s",sun); bpy.context.scene.collection.objects.link(so)
so.rotation_euler=(math.radians(45),math.radians(15),math.radians(25))
w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.45,0.45,0.45,1)
cam_d=bpy.data.cameras.new("c"); cam=bpy.data.objects.new("c",cam_d)
bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera=cam
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16
sc.render.resolution_x=600; sc.render.resolution_y=400
for tag,loc in [("plusY",(0,0.22,0.02)),("minusY",(0,-0.22,0.02))]:
    cam.location=Vector(loc); d=Vector((0,0,0))-cam.location
    cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=os.path.join(outd,f"d455_{tag}.png")
    bpy.ops.render.render(write_still=True); print("RENDERED",tag)

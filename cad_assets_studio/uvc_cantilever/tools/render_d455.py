# Render the D455 STL from a 3/4 view with RGB world-axis arrows so we can see
# which way the lens faces.  blender --background --python render_d455.py -- <stl> <out.png>
import bpy, sys, math
from mathutils import Vector
stl, out = sys.argv[sys.argv.index("--")+1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
try:    bpy.ops.wm.stl_import(filepath=stl)
except: bpy.ops.import_mesh.stl(filepath=stl)
obj=[o for o in bpy.data.objects if o.type=='MESH'][0]
# scale mm->m
obj.scale=(0.001,0.001,0.001); bpy.context.view_layer.update()
# axis arrows: X=red,Y=green,Z=blue (each a thin long box)
def axis(name,vec,col):
    m=bpy.data.meshes.new(name);
    bpy.ops.mesh.primitive_cube_add(size=1)
    a=bpy.context.active_object; a.scale=vec
    mat=bpy.data.materials.new(name); mat.diffuse_color=col; a.data.materials.append(mat)
axis("X",(0.10,0.004,0.004),(1,0,0,1))
axis("Y",(0.004,0.10,0.004),(0,1,0,1))
axis("Z",(0.004,0.004,0.10),(0,0,1,1))
# camera 3/4
cam_d=bpy.data.cameras.new("c"); cam=bpy.data.objects.new("c",cam_d)
bpy.context.scene.collection.objects.link(cam)
cam.location=Vector((0.22,-0.22,0.18)); d=Vector((0,0,0))-cam.location
cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=cam
sun=bpy.data.lights.new("s",'SUN'); sun.energy=4
so=bpy.data.objects.new("s",sun); bpy.context.scene.collection.objects.link(so)
so.rotation_euler=(math.radians(50),math.radians(20),math.radians(30))
w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.5,0.5,0.5,1)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16
sc.render.resolution_x=700; sc.render.resolution_y=600; sc.render.filepath=out
bpy.ops.render.render(write_still=True); print("RENDERED",out)

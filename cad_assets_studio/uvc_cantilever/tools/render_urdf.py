# Crude URDF visual renderer: draws each link's <visual> (box/cylinder/mesh) at
# its world pose (fixed joints only) so we can eyeball the assembly.
#   blender --background --python render_urdf.py -- <urdf> <out.png> [name_filter]
import bpy, sys, math, os
import xml.etree.ElementTree as ET
from mathutils import Vector, Euler, Matrix

urdf, out = sys.argv[sys.argv.index("--")+1:][:2]
flt = sys.argv[sys.argv.index("--")+3] if len(sys.argv[sys.argv.index("--")+1:])>2 else None
root = ET.parse(urdf).getroot()
pkg_share = os.path.expanduser("~/pomona_nexus/src/pomona_description")

bpy.ops.wm.read_factory_settings(use_empty=True)

# build link world transforms from fixed joints (parent->child)
joints = {}
for j in root.findall('joint'):
    c = j.find('child').get('link'); p = j.find('parent').get('link')
    o = j.find('origin'); xyz = [float(v) for v in (o.get('xyz','0 0 0')).split()] if o is not None else [0,0,0]
    rpy = [float(v) for v in (o.get('rpy','0 0 0')).split()] if o is not None else [0,0,0]
    joints[c] = (p, Matrix.Translation(xyz) @ Euler(rpy).to_matrix().to_4x4())

def world(link):
    M = Matrix(); cur = link
    while cur in joints:
        p, T = joints[cur]; M = T @ M; cur = p
    return M

def addmat(obj, rgba):
    m = bpy.data.materials.new("m"); m.diffuse_color = rgba; obj.data.materials.append(m)

COL = {"grey":(0.5,0.5,0.5,1),"dark":(0.2,0.2,0.2,1),"blue":(0.1,0.3,0.9,1),
       "white":(0.9,0.9,0.9,1),"black":(0.05,0.05,0.05,1)}

for link in root.findall('link'):
    ln = link.get('name')
    if flt and (flt not in ln):
        continue
    W = world(ln)
    for vis in link.findall('visual'):
        o = vis.find('origin')
        vxyz = [float(v) for v in (o.get('xyz','0 0 0')).split()] if o is not None else [0,0,0]
        vrpy = [float(v) for v in (o.get('rpy','0 0 0')).split()] if o is not None else [0,0,0]
        L = W @ Matrix.Translation(vxyz) @ Euler(vrpy).to_matrix().to_4x4()
        g = vis.find('geometry'); obj=None; S=Matrix()
        if g.find('box') is not None:
            s=[float(v) for v in g.find('box').get('size').split()]
            bpy.ops.mesh.primitive_cube_add(size=1); obj=bpy.context.active_object   # 1m cube
            S=Matrix.Diagonal((s[0],s[1],s[2],1.0))
        elif g.find('cylinder') is not None:
            cy=g.find('cylinder'); r=float(cy.get('radius')); h=float(cy.get('length'))
            bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=h); obj=bpy.context.active_object
        elif g.find('mesh') is not None:
            mp=g.find('mesh').get('filename').replace('package://pomona_description',pkg_share)
            sc=[float(x) for x in g.find('mesh').get('scale','1 1 1').split()]
            try:
                if mp.lower().endswith('.stl'):
                    try: bpy.ops.wm.stl_import(filepath=mp)
                    except: bpy.ops.import_mesh.stl(filepath=mp)
                else:
                    try: bpy.ops.wm.obj_import(filepath=mp)
                    except: bpy.ops.import_scene.obj(filepath=mp)
                obj=bpy.context.selected_objects[0] if bpy.context.selected_objects else bpy.context.active_object
                S=Matrix.Diagonal((sc[0],sc[1],sc[2],1.0))
            except Exception as e: print("mesh fail",mp,e); continue
        if obj is None: continue
        obj.matrix_world = L @ S
        mat = vis.find('material')
        addmat(obj, COL.get(mat.get('name') if mat is not None else 'grey',(0.5,0.5,0.5,1)))

# camera + light (3/4 from front-left, looking at the boom head ~z 0.8)
cam_d=bpy.data.cameras.new("c"); cam_d.lens=42; cam=bpy.data.objects.new("c",cam_d)
bpy.context.scene.collection.objects.link(cam)
cam.location=Vector((0.95,1.35,0.55)); d=Vector((0.53,1.0,0.66))-cam.location
cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=cam
sun=bpy.data.lights.new("s",'SUN'); sun.energy=3.5
so=bpy.data.objects.new("s",sun); bpy.context.scene.collection.objects.link(so)
so.rotation_euler=(math.radians(50),math.radians(20),math.radians(35))
w=bpy.data.worlds.new("w"); bpy.context.scene.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.6,0.72,0.85,1)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=20
sc.render.resolution_x=900; sc.render.resolution_y=700; sc.render.filepath=out
bpy.ops.render.render(write_still=True); print("RENDERED",out)

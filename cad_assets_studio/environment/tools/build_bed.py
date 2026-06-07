# Build a realistic raised mulch bed mesh: trapezoidal cross-section with a
# gently crowned (slightly curvy) top, sloped (non-sharp) sides. Top = plastic
# mulch (with holes baked into the texture); sides/ends = soil. Tiled UVs.
#   blender --background --python build_bed.py -- <outdir> [length_m]
import bpy, bmesh, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
outdir = argv[0]
L  = float(argv[1]) if len(argv) > 1 else 200.0
Wb, Wt, H, CROWN = 1.0, 0.85, 0.4, 0.04
TEX = os.path.expanduser("~/pomona_nexus/cad_assets_studio/environment/textures")

# cross-section profile (Y,Z), CCW: bottom edge, right slope, crowned top arc, left slope
prof = [(-Wb/2, 0.0), (Wb/2, 0.0), (Wt/2, H)]
N = 12
for i in range(1, N):
    t = i / N
    prof.append((Wt/2 - t*Wt, H + CROWN*math.sin(math.pi*t)))
prof.append((-Wt/2, H))

bpy.ops.wm.read_factory_settings(use_empty=True)
bm = bmesh.new()
vs = [bm.verts.new((-L/2, y, z)) for (y, z) in prof]
f = bm.faces.new(vs)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
ret = bmesh.ops.extrude_face_region(bm, geom=[f])
nv = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
bmesh.ops.translate(bm, vec=(L, 0, 0), verts=nv)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
# slight chamfer/fillet on all edges for realism (rounded, ~2.5 cm)
bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.025, segments=2, profile=0.7, affect='EDGES')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("bed"); bm.to_mesh(me); bm.free()
obj = bpy.data.objects.new("bed", me)
bpy.context.scene.collection.objects.link(obj)

def mat(name, tex):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    n = m.node_tree.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(os.path.join(TEX, tex))
    m.node_tree.links.new(n.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.55
    return m
me.materials.append(mat("mulch", "mulch_plastic.jpg"))   # idx 0
me.materials.append(mat("soil",  "soil.jpg"))            # idx 1

me.uv_layers.new(name="UVMap")
bm2 = bmesh.new(); bm2.from_mesh(me); uv = bm2.loops.layers.uv.active
for face in bm2.faces:
    n = face.normal
    # plastic mulch wraps the ENTIRE bed (top, sides, AND both end caps); only
    # the buried BOTTOM (nz<0) is bare soil (invisible).
    is_bottom = n.z < -0.5
    is_endcap = abs(n.x) > 0.5
    face.material_index = 1 if is_bottom else 0   # 0 = mulch, 1 = soil(bottom only)
    for lp in face.loops:
        c = lp.vert.co
        if is_endcap:
            lp[uv].uv = (c.y, c.z*2.0)            # mulch on the end caps
        else:
            lp[uv].uv = (c.x, (c.y + Wb/2)/Wb)    # mulch top + sides (and bottom)
bm2.to_mesh(me); bm2.free()

# export OBJ; author MTL to point at ../textures (studio convention)
os.makedirs(outdir, exist_ok=True)
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
bpy.context.view_layer.objects.active = obj
base = os.path.join(outdir, "bed")
bpy.ops.wm.obj_export(filepath=base + ".obj", export_selected_objects=True,
                      export_materials=True, path_mode='STRIP', export_uv=True,
                      export_normals=True)  # default Y-up; model.sdf adds rpy=1.5708 0 0
with open(base + ".mtl", "w") as fh:
    for nm, tx in [("mulch", "mulch_plastic.jpg"), ("soil", "soil.jpg")]:
        fh.write(f"newmtl {nm}\nKa 1 1 1\nKd 1 1 1\nmap_Kd ../textures/{tx}\n\n")
print("EXPORTED", base + ".obj")

# ---- close-up preview render of one end ----
cam_d = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cam_d)
bpy.context.scene.collection.objects.link(cam)
cam.location = Vector((-L/2 + 1.5, -2.6, 1.7))
d = Vector((-L/2 + 3.0, 0, 0.45)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
sun = bpy.data.lights.new("s", 'SUN'); sun.energy = 4
so = bpy.data.objects.new("s", sun); bpy.context.scene.collection.objects.link(so)
so.rotation_euler = (math.radians(50), math.radians(15), math.radians(40))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.75, 0.9, 1)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = 24; sc.render.resolution_x = 900; sc.render.resolution_y = 600
prev = os.path.expanduser("~/pomona_nexus/cad_assets_studio/environment/previews/preview_bed.png")
os.makedirs(os.path.dirname(prev), exist_ok=True); sc.render.filepath = prev
bpy.ops.render.render(write_still=True)
print("RENDERED", prev)

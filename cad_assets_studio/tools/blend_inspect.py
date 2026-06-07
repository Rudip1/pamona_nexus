# List every object in a .blend: name, type, verts, world-size, location.
# Run with --disable-autoexec so embedded scripts never execute.
# Usage: blender --background --disable-autoexec <in.blend> --python blend_inspect.py
import bpy

print("==== OBJECT INVENTORY ====")
print(f"{'NAME':40s} {'TYPE':10s} {'VERTS':>8s}  {'DIM (x,y,z m)':>22s}  LOC")
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    verts = len(o.data.vertices) if (o.type == 'MESH' and o.data) else 0
    d = o.dimensions
    loc = o.location
    print(f"{o.name[:40]:40s} {o.type:10s} {verts:8d}  "
          f"({d.x:6.2f},{d.y:6.2f},{d.z:6.2f})  "
          f"({loc.x:5.1f},{loc.y:5.1f},{loc.z:5.1f})")

mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
total_v = sum(len(o.data.vertices) for o in mesh_objs if o.data)
print(f"\nMESH objects: {len(mesh_objs)}   total verts: {total_v}")
print("\n==== MATERIALS ====")
for m in sorted(bpy.data.materials, key=lambda x: x.name):
    print(" ", m.name)

#!/usr/bin/env python3
# Procedural bed textures (generated from scratch; harvester bed_plastic.jpg used
# only as a visual reference). Tileable 1 m x 1 m patches.
#   soil.jpg          - dark grey-brown grainy soil (bed sides + showing in holes)
#   mulch_plastic.jpg - dark plastic mulch (woven sheen) + planting holes (2
#                       staggered rows) that reveal the soil underneath
import os, numpy as np
from PIL import Image, ImageFilter

OUT = os.path.expanduser("~/pomona_nexus/cad_assets_studio/environment/textures")
os.makedirs(OUT, exist_ok=True)
S = 1024
rng = np.random.default_rng(3)

def save(arr, name):
    Image.fromarray((np.clip(arr,0,1)*255).astype(np.uint8)).save(os.path.join(OUT,name), quality=92)
    print("WROTE", name)

def smooth(a, r):
    im = Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=r))
    return np.asarray(im, dtype=np.float32)/255.0

# ---------------- SOIL ----------------
base = np.array([0.30, 0.26, 0.22], dtype=np.float32)        # dark grey-brown
grain = rng.random((S,S)).astype(np.float32)
fine = (grain - 0.5) * 0.22                                   # per-pixel grain
clump = (smooth(rng.random((S,S)).astype(np.float32), 6) - 0.5) * 0.18  # soft clumps
soilL = np.clip(1.0 + fine + clump, 0.6, 1.4)                 # luminance multiplier
soil = base[None,None,:] * soilL[...,None]
# a few darker pebbles / specks
for _ in range(500):
    y,x = rng.integers(0,S), rng.integers(0,S); rr = rng.integers(1,4)
    y0,y1 = max(0,y-rr), min(S,y+rr); x0,x1 = max(0,x-rr), min(S,x+rr)
    gy,gx = np.mgrid[y0:y1, x0:x1]
    m = (gy-y)**2+(gx-x)**2 < rr*rr
    soil[y0:y1, x0:x1][m] *= rng.uniform(0.6,1.3)
save(soil, "soil.jpg")

# ---------------- MULCH PLASTIC (+ holes) ----------------
# dark plastic base with faint diagonal weave + large-scale sheen
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
weave = (np.sin((xx+yy)*np.pi/6.0)*0.5+0.5) * 0.06 + (np.sin((xx-yy)*np.pi/6.0)*0.5+0.5)*0.04
sheen = smooth(rng.random((S,S)).astype(np.float32), 60)      # soft reflectance blobs
plastL = np.clip(0.55 + weave + 0.5*sheen, 0.35, 1.0)
plastic = np.array([0.06,0.06,0.07], dtype=np.float32)[None,None,:] * (plastL[...,None]*1.8)
plastic += 0.04*sheen[...,None]                              # specular-ish lift
plastic = np.clip(plastic, 0, 1)
# faint scratches
for _ in range(12):
    y0 = rng.integers(0,S); x0 = rng.integers(0,S); ln = rng.integers(40,200); ang = rng.uniform(0,np.pi)
    for t in range(ln):
        xx2 = int(x0+t*np.cos(ang))%S; yy2=int(y0+t*np.sin(ang))%S
        plastic[yy2, xx2] = np.clip(plastic[yy2,xx2]+0.10,0,1)

# Planting holes are added LATER, once plant positions are chosen (the farm
# generator punches holes at the real plant (x,y) spots). For now: plain plastic.
# Set HOLES=True to bake a default 2x3 staggered hole pattern instead.
HOLES = False
if HOLES:
    hole = np.zeros((S,S), dtype=np.float32)
    ring = np.zeros((S,S), dtype=np.float32)
    centers = [(0.28,0.17),(0.28,0.50),(0.28,0.83),(0.72,0.33),(0.72,0.67),(0.72,1.00)]
    R = 0.075*S
    for (v,u) in centers:
        cy, cx = v*S, (u%1.0)*S
        d = np.sqrt((yy-cy)**2 + (xx-cx)**2)
        hole = np.maximum(hole, (d < R).astype(np.float32))
        ring = np.maximum(ring, ((d<R*1.18)&(d>=R)).astype(np.float32))
    mulch = plastic*(1-hole[...,None]) + soil*hole[...,None]
    mulch = mulch*(1 - 0.5*ring[...,None])
else:
    mulch = plastic
save(mulch, "mulch_plastic.jpg")
print("DONE (holes:", HOLES, ")")

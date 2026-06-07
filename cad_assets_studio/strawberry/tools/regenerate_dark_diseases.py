#!/usr/bin/env python3
# Rebuild the two disease leaf textures from the (now dark) healthy leaf, so the
# diseased plants' underlying green matches the dark leaf everywhere.
#   leaf_healthy.jpg  ->  leaf_mildew.jpg (powdery mildew) + leaf_scorch.jpg (scorch)
import os, numpy as np
from PIL import Image, ImageFilter

TEX = os.path.expanduser("~/pomona_nexus/cad_assets_studio/strawberry/textures")
src = os.path.join(TEX, "leaf_healthy.jpg")
arr = np.asarray(Image.open(src).convert("RGB"), dtype=np.float32) / 255.0
h, w = arr.shape[:2]

def to_hsv(rgb):
    return np.asarray(Image.fromarray((rgb*255).astype(np.uint8)).convert("HSV"),
                      dtype=np.float32)/255.0
def to_rgb(hsv):
    return np.asarray(Image.fromarray((hsv*255).astype(np.uint8), "HSV").convert("RGB"),
                      dtype=np.float32)/255.0
def save(rgb, name):
    Image.fromarray((np.clip(rgb,0,1)*255).astype(np.uint8)).save(os.path.join(TEX,name), quality=92)
    print("WROTE", name)

# ---------- POWDERY MILDEW (white dusting ~55% + purple-red blotches) ----------
def blurred(seed, radius):
    n = np.random.default_rng(seed).random((h, w)).astype(np.float32)
    im = Image.fromarray((n*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=radius))
    a = np.asarray(im, dtype=np.float32)/255.0
    return (a-a.min())/(a.max()-a.min()+1e-6)
coarse = blurred(11, max(6, w//18)); fine = blurred(23, 1.2)
patch = (coarse > np.quantile(coarse, 0.45)).astype(np.float32)
speckle = np.clip((fine-0.35)/0.65, 0, 1)
alpha = patch*(0.45+0.55*speckle)*0.95
powder = np.array([0.95,0.96,0.92], dtype=np.float32)
mil = arr*(1-alpha[...,None]) + powder[None,None,:]*alpha[...,None]
rng = np.random.default_rng(11); yy,xx = np.mgrid[0:h,0:w]
for _ in range(28):
    cy,cx = rng.integers(0,h), rng.integers(0,w); r = rng.integers(3,10)
    m = (yy-cy)**2+(xx-cx)**2 < r*r
    mil[m] = mil[m]*0.45 + np.array([0.40,0.12,0.20])*0.55
save(mil, "leaf_mildew.jpg")

# ---------- LEAF SCORCH (green -> yellow, darker, + brown necrotic spots) ----------
hsv = to_hsv(arr); H,S,V = hsv[...,0],hsv[...,1],hsv[...,2]
green = (H>0.18)&(H<0.45)
out = hsv.copy()
out[...,0] = np.where(green, 0.12, H)          # -> yellow
out[...,1] = np.where(green, np.clip(S*1.1,0,1), S)
out[...,2] = np.where(green, V*0.9, V)
sc = to_rgb(out)
rng = np.random.default_rng(7)
for _ in range(40):
    cy,cx = rng.integers(0,h), rng.integers(0,w); r = rng.integers(4,14)
    m = (yy-cy)**2+(xx-cx)**2 < r*r
    sc[m] = sc[m]*0.35 + np.array([0.30,0.18,0.05])*0.65
save(sc, "leaf_scorch.jpg")
print("DONE")

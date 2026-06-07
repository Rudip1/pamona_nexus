#!/usr/bin/env python3
# High-res, sharp, tileable plastic-mulch texture (grey, subtle sheen + weave +
# faint scratches). Replaces a low-res import. -> mulch_plastic.png (1024px)
import os, numpy as np
from PIL import Image, ImageFilter

OUT = os.path.expanduser("~/pomona_nexus/cad_assets_studio/environment/textures")
S = 1024
rng = np.random.default_rng(5)

def smooth(a, r):
    return np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius=r)), dtype=np.float32)/255.0

base = np.array([0.26, 0.27, 0.29], dtype=np.float32)   # dark cool grey plastic

yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
# faint diagonal weave (periodic -> tiles seamlessly)
weave = (np.sin((xx+yy)*np.pi/8.0)*0.5+0.5)*0.05 + (np.sin((xx-yy)*np.pi/8.0)*0.5+0.5)*0.035
# fine speckle (tiles fine visually) + LOW-amplitude broad sheen (keep bands subtle)
fine = (rng.random((S, S)).astype(np.float32) - 0.5) * 0.05
sheen = (smooth(rng.random((S, S)).astype(np.float32), 70) - 0.5) * 0.12
L = np.clip(1.0 + weave + fine + sheen, 0.7, 1.5)
img = np.clip(base[None, None, :] * L[..., None], 0, 1)
# a couple of faint highlight scratches
for _ in range(10):
    y0, x0 = rng.integers(0, S), rng.integers(0, S); ln = rng.integers(60, 240); a = rng.uniform(0, np.pi)
    for t in range(ln):
        img[int(y0+t*np.sin(a)) % S, int(x0+t*np.cos(a)) % S] += 0.06
img = np.clip(img, 0, 1)

Image.fromarray((img*255).astype(np.uint8)).save(os.path.join(OUT, "mulch_plastic.jpg"), quality=92)
print("WROTE mulch_plastic.jpg  1024x1024  dark-grey plastic")

#!/usr/bin/env python3
# Tileable hedge foliage texture: dense green with leaf-clump light/dark
# variation, fine speckle, a few dark gaps and lighter tips.  -> hedge.jpg
import os, numpy as np
from PIL import Image, ImageFilter

OUT = os.path.expanduser("~/pomona_nexus/cad_assets_studio/environment/textures")
S = 1024
rng = np.random.default_rng(8)

def smooth(a, r):
    b = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius=r)), dtype=np.float32)/255.0
    return (b - b.min()) / (b.max() - b.min() + 1e-6)   # stretch back to 0..1

base = np.array([0.10, 0.26, 0.08], dtype=np.float32)      # dark leaf green
# two octaves of leaf detail (fine leaves + bigger clumps), high contrast
n1 = smooth(rng.random((S, S)).astype(np.float32), 1.5)    # fine leaves
n2 = smooth(rng.random((S, S)).astype(np.float32), 5)      # clumps
leaf = (n1 - 0.5) * 0.9 + (n2 - 0.5) * 0.7
L = np.clip(1.0 + leaf, 0.35, 1.8)
img = base[None, None, :] * L[..., None]
# dark shadow gaps between clumps
dark = n2 < 0.30
img[dark] *= 0.45
# bright sunlit leaf tips (slightly yellow-green)
tips = n1 > 0.72
img[tips] = img[tips] * 0.4 + np.array([0.28, 0.45, 0.16]) * 0.6
img = np.clip(img, 0, 1)

Image.fromarray((img*255).astype(np.uint8)).save(os.path.join(OUT, "hedge.jpg"), quality=92)
print("WROTE hedge.jpg  1024x1024  foliage green")

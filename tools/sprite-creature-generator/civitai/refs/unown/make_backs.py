#!/usr/bin/env python3
"""AUREBESH (unown) backs, free: the letter's front mirrored with the eye painted over in body
colour, on the same shared palette (vanilla Unown backs are the same glyph seen from behind).
The model-drawn backs (image to image from the mirrored front) wandered into creature shapes."""
import sys
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image

art = Path(sys.argv[1])  # wiki/art/graphics/pokemon/unown
for d in sorted(p for p in art.iterdir() if p.is_dir()):
    im = Image.open(d / "front.png")
    a = np.array(im)[:, ::-1].copy()
    op = a > 0
    inner = op.copy()
    inner[1:] &= op[:-1]; inner[:-1] &= op[1:]; inner[:, 1:] &= op[:, :-1]; inner[:, :-1] &= op[:, 1:]
    eye = a == 1
    for _ in range(1):
        e = eye.copy()
        e[1:] |= eye[:-1]; e[:-1] |= eye[1:]; e[:, 1:] |= eye[:, :-1]; e[:, :-1] |= eye[:, 1:]
        eye = e
    eye &= inner
    body = Counter(a[inner & ~eye].tolist()).most_common(1)[0][0]
    a[eye] = body
    out = Image.fromarray(a.astype(np.uint8), "P")
    out.putpalette(im.getpalette())
    out.save(d / "back.png", transparency=0)
    print(d.name, int(eye.sum()), "px painted with index", body)

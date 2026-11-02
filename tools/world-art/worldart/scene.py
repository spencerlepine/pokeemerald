"""Mockup scenes: rendered objects placed on a planet's ground at cell coordinates, drawn back to
front by foot row, so the tools can be judged together as a map and not as sheets of squares.

scenes/<name>.yaml:
    name: bright-tree-village
    planet: endor
    size: [24, 14]                 # cells
    ground: {base: [112, 152, 104], speck: [88, 128, 88]}
    paths:                         # rectangles of the walkable "signal" colour, cells [x0, y0, x1, y1]
      - {rect: [0, 8, 24, 10], colour: [192, 112, 88]}
    objects:                       # model path and the top-left cell of its image
      - {model: models/endor/redwood-trunk.yaml, at: [2, 1]}
      - {model: models/endor/fern-undergrowth.yaml, fill: [0, 12, 24, 14]}   # tile a 1x1 object over a rect
"""
import os

import numpy as np
import yaml
from PIL import Image, ImageDraw

from . import model as M, render as R

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "output", "scenes")


def _ground(w, h, spec, seed=7):
    rng = np.random.default_rng(seed)
    a = np.zeros((h * 16, w * 16, 3), np.uint8)
    a[:] = spec.get("base", [112, 152, 104])
    m = rng.random((h * 16, w * 16)) < float(spec.get("density", 0.06))
    a[m] = spec.get("speck", [88, 128, 88])
    return a


def _layout_ground(sc):
    """A real map rendered through a tile-generator recipe, with rectangles of cells reset to the
    map's most common metatile (grass) where the new objects go. Needs ../tile-generator."""
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "tile-generator"))
    from tilegen import gba, recolour
    from tilegen.__main__ import _build_pair
    L = gba.layouts()
    lay = L[sc["layout"]]
    rec = recolour.Recipe.load(os.path.join(HERE, sc["recipe"]))
    _, pair = _build_pair(rec, lay.primary, lay.secondary)
    cells = lay.cells()
    ids = cells & 0x3FF
    grass = int(np.bincount(ids.ravel()).argmax()) if "fill" not in sc else int(sc["fill"])
    edited = cells.copy()
    for x0, y0, x1, y1 in sc.get("clear", []):
        edited[y0:y1, x0:x1] = (edited[y0:y1, x0:x1] & ~np.uint16(0x3FF)) | np.uint16(grass)
    tmp = os.path.join(HERE, "output", "scenes", f"{lay.name}.edited.bin")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    edited.astype("<u2").tofile(tmp)
    import dataclasses
    from pathlib import Path
    lay2 = dataclasses.replace(lay, map_bin=Path(tmp))
    return gba.render_layout(lay2, pair=pair).convert("RGB"), (lay.width, lay.height)


def build(path):
    sc = yaml.safe_load(open(path))
    if "layout" in sc:
        img, (w, h) = _layout_ground(sc)
    else:
        w, h = sc["size"]
        img = Image.fromarray(_ground(w, h, sc.get("ground", {})))
    d = ImageDraw.Draw(img)
    for p in sc.get("paths", []):
        x0, y0, x1, y1 = p["rect"]
        d.rectangle([x0 * 16, y0 * 16, x1 * 16 - 1, y1 * 16 - 1], fill=tuple(p.get("colour", [192, 112, 88])))
    cache = {}
    placements = []
    for o in sc.get("objects", []):
        mp = os.path.join(HERE, o["model"])
        if mp not in cache:
            obj = M.Object(mp)
            sprite, ind, warnings = R.render_object(obj, float(o.get("yaw", 0)))
            for wmsg in warnings:
                print("WARNING", wmsg)
            cache[mp] = (obj, sprite)
        obj, sprite = cache[mp]
        if "fill" in o:
            x0, y0, x1, y1 = o["fill"]
            cw, ch = obj.cells
            for cy in range(y0, y1, ch):
                for cx in range(x0, x1, cw):
                    placements.append((cy + ch, cx, sprite))
        else:
            cx, cy = o["at"]
            placements.append((cy + obj.cells[1], cx, sprite))
    img = img.convert("RGBA")
    # draw north to south (smaller bottom row first), so southern objects overlap northern ones
    for bottom, cx, sprite in sorted(placements, key=lambda t: (t[0], t[1])):
        img.alpha_composite(sprite, (cx * 16, (bottom - sprite.height // 16) * 16))
    os.makedirs(OUT, exist_ok=True)
    name = sc.get("name") or os.path.basename(path).split(".")[0]
    out = os.path.join(OUT, f"{name}.png")
    img.convert("RGB").save(out)
    img.resize((img.width * 3, img.height * 3), Image.NEAREST).convert("RGB").save(os.path.join(OUT, f"{name}-3x.png"))
    print(f"scene {name}: {w}x{h} cells, {len(placements)} objects -> {os.path.relpath(out, HERE)}")
    return out

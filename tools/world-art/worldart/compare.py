"""Calibration: a rendered model next to the vanilla art it must be able to replace.

`python -m worldart compare models/calibration/hoenn-tree.yaml` reads the model's `vanilla:` block
(a layout and the cell rect where vanilla draws that object), renders both on the same ground,
and writes output/compare/<name>.png: vanilla | ours | ours dropped into the vanilla map in place
of the original, at 1x and 6x, plus a colour report. Needs ../tile-generator.

    vanilla: {layout: Route101_Layout, rect: [0, 0, 2, 2], context: [0, 0, 8, 6]}
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

from . import model as M, render as R

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "output", "compare")


def _vanilla_map(layout_name):
    sys.path.insert(0, os.path.join(HERE, "..", "tile-generator"))
    from tilegen import gba
    lay = gba.layouts()[layout_name]
    return np.array(gba.render_layout(lay).convert("RGB"))


def build(path):
    obj = M.Object(path)
    v = obj.raw.get("vanilla")
    if not v:
        raise SystemExit(f"{path}: no `vanilla:` block to compare against")
    sprite, ind, warnings = R.render_object(obj)
    for w in warnings:
        print("WARNING", w)
    full = _vanilla_map(v["layout"])
    x0, y0, x1, y1 = v["rect"]
    van = full[y0 * 16:y1 * 16, x0 * 16:x1 * 16]
    cx0, cy0, cx1, cy1 = v.get("context", [max(x0 - 3, 0), max(y0 - 2, 0), x1 + 3, y1 + 2])
    ctx = full[cy0 * 16:cy1 * 16, cx0 * 16:cx1 * 16].copy()
    ground = np.array(v.get("ground", [115, 197, 164]), np.uint8)

    # ours on flat ground, the size of the vanilla rect
    ours = np.zeros_like(van)
    ours[:] = ground
    o = Image.fromarray(ours).convert("RGBA")
    o.alpha_composite(sprite, (0, van.shape[0] - sprite.height))
    ours = np.array(o.convert("RGB"))

    # ours in the map: replace the vanilla object (ground first) and overlay ours
    swap = ctx.copy()
    rx, ry = (x0 - cx0) * 16, (y0 - cy0) * 16
    swap[ry:ry + van.shape[0], rx:rx + van.shape[1]] = ground
    s = Image.fromarray(swap).convert("RGBA")
    s.alpha_composite(sprite, (rx, ry + van.shape[0] - sprite.height))
    swap = np.array(s.convert("RGB"))

    def z(a, k):
        return Image.fromarray(a).resize((a.shape[1] * k, a.shape[0] * k), Image.NEAREST)
    k = 8
    pair = [z(van, k), z(ours, k)]
    ctx_pair = [z(ctx, 3), z(swap, 3)]
    W = max(pair[0].width * 2 + 24, ctx_pair[0].width * 2 + 24)
    H = pair[0].height + ctx_pair[0].height + 70
    sheet = Image.new("RGB", (W, H), (28, 28, 32))
    d = ImageDraw.Draw(sheet)
    d.text((4, 2), "vanilla", fill=(240, 240, 240))
    d.text((pair[0].width + 28, 2), f"world-art: {obj.name}", fill=(240, 240, 240))
    sheet.paste(pair[0], (0, 16))
    sheet.paste(pair[1], (pair[0].width + 24, 16))
    y = 16 + pair[0].height + 20
    d.text((4, y - 16), "vanilla map (3x)", fill=(240, 240, 240))
    d.text((ctx_pair[0].width + 28, y - 16), "same map, ours swapped in", fill=(240, 240, 240))
    sheet.paste(ctx_pair[0], (0, y))
    sheet.paste(ctx_pair[1], (ctx_pair[0].width + 24, y))
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"{obj.name}.png")
    sheet.save(out)

    vc = {tuple(c) for c in van.reshape(-1, 3)}
    oc = {tuple(c) for c in np.array(sprite)[..., :3][np.array(sprite)[..., 3] > 0]}
    print(f"{obj.name}: vanilla {len(vc)} colours, ours {len(oc)}; ours not in vanilla: "
          f"{sorted('#%02x%02x%02x' % c for c in oc - vc)}")
    print(f"-> {os.path.relpath(out, HERE)}")
    return out

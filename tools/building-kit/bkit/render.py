"""Render a composed building with the world-art camera, cropped to whole cells, and lay out review sheets."""
import os

import numpy as np
from PIL import Image, ImageDraw

from . import compose as C
from worldart import render as R, preview as P, tiles as T

GROUND = (176, 176, 168)


def render(raw):
    """(RGBA sprite cropped to whole cells, index array, warnings, unique tiles)."""
    obj = C.obj_from(raw)
    img, ind, warnings = R.render_object(obj)
    rows = np.nonzero((ind > 0).any(1))[0]
    top = 0 if len(rows) == 0 else (int(rows[0]) - 1) // 16 * 16          # keep a pixel clear above
    top = max(top, 0)
    img, ind = img.crop((0, top, img.width, img.height)), ind[top:]
    cols = (ind > 0).any(0)
    if cols[0] or cols[-1]:
        warnings.append(f"{raw['name']}: the art touches the {'left' if cols[0] else 'right'} edge")
    if top == 0 and (ind[0] > 0).any():
        warnings.append(f"{raw['name']}: taller than {C.TALL} cells, cut off")
    tiles = T.budget(ind, obj.palette)["unique_tiles"]
    return img, ind, warnings, tiles


def on_ground(img, scale=1, grid=False):
    bg = P.speckled(img.width, img.height, GROUND).convert("RGBA")
    bg.alpha_composite(img)
    out = bg.resize((img.width * scale, img.height * scale), Image.NEAREST)
    if grid and scale > 1:
        d = ImageDraw.Draw(out)
        for x in range(0, out.width, 16 * scale):
            d.line([(x, 0), (x, out.height)], fill=(150, 150, 142))
        for y in range(out.height, -1, -16 * scale):
            d.line([(0, y), (out.width, y)], fill=(150, 150, 142))
    return out


def sheet(title, shots, scale=3, max_w=1500, grid=True):
    """shots: [(label, sprite)] side by side at `scale`, wrapped, on ground."""
    cw = max(im.width for _, im in shots) * scale
    ch = max(im.height for _, im in shots) * scale
    cols = max(1, min(len(shots), (max_w - 12) // (cw + 12)))
    nrows = (len(shots) + cols - 1) // cols
    out = Image.new("RGB", (cols * (cw + 12) + 12, nrows * (ch + 30) + 28), (28, 28, 32))
    d = ImageDraw.Draw(out)
    d.text((10, 6), title, fill=(240, 240, 240))
    for k, (label, im) in enumerate(shots):
        x = 12 + (k % cols) * (cw + 12)
        y = 28 + (k // cols) * (ch + 30)
        g = on_ground(im, scale, grid)
        out.paste(g.convert("RGB"), (x + (cw - g.width) // 2, y + 14 + ch - g.height))
        d.text((x, y), label, fill=(215, 215, 215))
    return out


def player():
    im = Image.open(os.path.join(C.ROOT, "game/graphics/object_events/pics/people/brendan/walking.png")).convert("RGBA")
    a = np.array(im)
    a[..., 3] = np.where((a[..., :3] == a[0, 0, :3]).all(-1), 0, 255)
    g = Image.fromarray(a).crop((0, 0, 16, 32)).convert("LA")
    return Image.merge("RGBA", (g.getchannel(0),) * 3 + (g.getchannel(1),))


def vanilla_house():
    """Petalburg's red house (5x4), grey, for scale."""
    sys_path = os.path.join(C.ROOT, "tools", "tile-generator")
    import sys
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    from tilegen import gba
    pet = gba.render_layout(gba.layouts()["PetalburgCity_Layout"]).convert("LA")
    g = pet.crop((5 * 16, 2 * 16, 10 * 16, 6 * 16))
    return Image.merge("RGBA", (g.getchannel(0),) * 3 + (Image.new("L", g.size, 255),))


def street(buildings, cols=30, rows=16, scale=2, title=""):
    """Two rows of lots on a 30x16-cell patch (two GBA screens wide), each row on a path, a grey vanilla
    house first for scale and the player on the first path. The red frame is one GBA screen (15x10).
    buildings: [sprite]. Returns (image, how many were placed)."""
    W, H = cols * 16, rows * 16
    bg = P.speckled(W, H, GROUND).convert("RGBA")
    d = ImageDraw.Draw(bg)
    bases = [7 * 16, 14 * 16]                    # the foot of each row of lots
    for b in bases:
        d.rectangle([0, b, W, b + 16 - 1], fill=(196, 194, 184))
    lots = [vanilla_house()] + list(buildings)
    row, x, placed = 0, 16, 0
    for im in lots:
        if x + im.width > W - 16:
            row, x = row + 1, 16
            if row >= len(bases):
                break
        bg.alpha_composite(im, (x, bases[row] - im.height))
        x += im.width + 16
        placed += 1
    bg.alpha_composite(player(), (16 * 7, bases[0] - 12))
    big = bg.resize((W * scale, H * scale), Image.NEAREST).convert("RGB")
    d = ImageDraw.Draw(big)
    d.rectangle([0, (bases[0] + 32 - 160) * scale, 15 * 16 * scale - 1, (bases[0] + 32) * scale - 1], outline=(220, 60, 60), width=2)
    out = Image.new("RGB", (big.width + 16, big.height + 30), (28, 28, 32))
    ImageDraw.Draw(out).text((8, 6), title, fill=(240, 240, 240))
    out.paste(big, (8, 26))
    return out, placed - 1

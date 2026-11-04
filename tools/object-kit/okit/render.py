"""Render a composed object with the world-art camera, cropped to whole cells, measure its hit box,
and lay out the review sheets (variants, border, scene, collage)."""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

from . import compose as C
from worldart import render as R, preview as P, tiles as T

GROUND = (176, 176, 168)
PATH = (196, 194, 184)
GRID = (150, 150, 142)


def render(raw, info):
    """(RGBA sprite cropped to whole cells, index array, warnings, unique tiles)."""
    obj = C.obj_from(raw)
    img, ind, warnings = R.render_object(obj)
    if info.get("fixed_rows"):
        top = 0
    else:
        rows = np.nonzero((ind > 0).any(1))[0]
        top = 0 if len(rows) == 0 else max((int(rows[0]) - 1) // 16 * 16, 0)
    img, ind = img.crop((0, top, img.width, img.height)), ind[top:]
    cols = (ind > 0).any(0)
    if not info.get("fill") and (cols[0] or cols[-1]):
        warnings.append(f"{raw['name']}: the art touches the {'left' if cols[0] else 'right'} edge")
    if top == 0 and (ind[0] > 0).any() and not info.get("fixed_rows"):
        warnings.append(f"{raw['name']}: taller than {C.TALL} cells, cut off")
    tiles = T.budget(ind, obj.palette)["unique_tiles"]
    return img, ind, warnings, tiles


def hit_box(raw):
    """(depth cells, west cell, east cell) of ground the object stands on at knee height (0.1 m):
    the hit box the piece needs. Depth is counted north from y = 0."""
    obj = C.obj_from(raw)
    W = raw["cells"][0]
    xs = np.arange(-W / 2 + 1 / 32, W / 2, 1 / 16)
    ys = np.arange(-0.5 + 1 / 32, C.TALL, 1 / 16)
    X, Y = np.meshgrid(xs, ys)
    P_ = np.stack([X.ravel(), Y.ravel(), np.full(X.size, 0.1)], 1)
    inst = obj.instances[0]
    d = inst.sdf(P_, 0.0)
    d = d[0] if isinstance(d, tuple) else d
    inside = d < 0
    if not inside.any():
        return 0, 0, 0
    yy, xx = Y.ravel()[inside], X.ravel()[inside]
    depth = max(1, int(np.ceil(yy.max() - 0.05)))
    west = int(np.floor(xx.min() + W / 2))
    east = int(np.floor(xx.max() + W / 2))
    return depth, west, east


def on_ground(img, scale=1, grid=False, bg_color=GROUND):
    bg = P.speckled(img.width, img.height, bg_color).convert("RGBA")
    bg.alpha_composite(img)
    out = bg.resize((img.width * scale, img.height * scale), Image.NEAREST)
    if grid and scale > 1:
        d = ImageDraw.Draw(out)
        for x in range(0, out.width, 16 * scale):
            d.line([(x, 0), (x, out.height)], fill=GRID)
        for y in range(out.height, -1, -16 * scale):
            d.line([(0, y), (out.width, y)], fill=GRID)
    return out


def sheet(title, shots, scale=3, max_w=1500, grid=True):
    """shots: [(label, sprite, D)] side by side at `scale`, wrapped, on ground, the hit box (bottom D
    rows) framed in red."""
    cw = max(im.width for _, im, _ in shots) * scale
    ch = max(im.height for _, im, _ in shots) * scale
    cols = max(1, min(len(shots), (max_w - 12) // (cw + 12)))
    nrows = (len(shots) + cols - 1) // cols
    out = Image.new("RGB", (cols * (cw + 12) + 12, nrows * (ch + 30) + 28), (28, 28, 32))
    d = ImageDraw.Draw(out)
    d.text((10, 6), title, fill=(240, 240, 240))
    for k, (label, im, D) in enumerate(shots):
        x = 12 + (k % cols) * (cw + 12)
        y = 28 + (k // cols) * (ch + 30)
        g = on_ground(im, scale, grid)
        px, py = x + (cw - g.width) // 2, y + 14 + ch - g.height
        out.paste(g.convert("RGB"), (px, py))
        if D:
            d.rectangle([px, py + g.height - D * 16 * scale, px + g.width - 1, py + g.height - 1], outline=(255, 70, 70), width=1)
        d.text((x, y), label, fill=(215, 215, 215))
    return out


def player():
    im = Image.open(os.path.join(C.ROOT, "game/graphics/object_events/pics/people/brendan/walking.png")).convert("RGBA")
    a = np.array(im)
    a[..., 3] = np.where((a[..., :3] == a[0, 0, :3]).all(-1), 0, 255)
    g = Image.fromarray(a).crop((0, 0, 16, 32)).convert("LA")
    return Image.merge("RGBA", (g.getchannel(0),) * 3 + (g.getchannel(1),))


_refs = {}


def vanilla_refs():
    """Grey vanilla pieces for scale: the Route 101 tree (2x2), the Route 111 cone rock (2x2) and the
    Petalburg house (5x4)."""
    if _refs:
        return _refs
    sys_path = os.path.join(C.ROOT, "tools", "tile-generator")
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    from tilegen import gba
    L = gba.layouts()

    def grey(img):
        g = img.convert("LA")
        return Image.merge("RGBA", (g.getchannel(0),) * 3 + (g.getchannel(1),))

    def lift(img, keys):
        a = np.array(img.convert("RGBA"))
        for k in keys:
            a[(a[..., :3] == k).all(-1), 3] = 0
        return Image.fromarray(a)
    r101 = gba.render_layout(L["Route101_Layout"])
    tree = lift(r101.crop((0, 2 * 16, 2 * 16, 4 * 16)), [(115, 197, 164), (164, 213, 197), (65, 180, 131)])
    r111 = gba.render_layout(L["Route111_Layout"])
    rock = lift(r111.crop((16 * 16, 100 * 16, 18 * 16, 102 * 16)),
                [(222, 205, 131), (213, 180, 106), (238, 230, 164), (115, 197, 164), (164, 213, 197), (65, 180, 131)])
    pet = gba.render_layout(L["PetalburgCity_Layout"])
    house = pet.crop((5 * 16, 2 * 16, 10 * 16, 6 * 16)).convert("RGBA")
    _refs.update(tree=grey(tree), rock=grey(rock), house=grey(house))
    return _refs


def scene(sprite, D, title):
    """One GBA screen (15x10 cells): the piece in the middle on a path's edge, the player south of it,
    a vanilla tree and rock for scale, the hit box in red. 1x and 3x."""
    refs = vanilla_refs()
    W, H = 15 * 16, 10 * 16
    bg = P.speckled(W, H, GROUND).convert("RGBA")
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 7 * 16, W, 8 * 16 - 1], fill=PATH)
    sx = (W - sprite.width) // 2
    sy = 7 * 16 - sprite.height
    bg.alpha_composite(refs["tree"], (16, 7 * 16 - 32))
    bg.alpha_composite(refs["tree"], (48, 7 * 16 - 32))
    bg.alpha_composite(refs["rock"], (W - 48, 7 * 16 - 32))
    bg.alpha_composite(sprite, (sx, sy))
    bg.alpha_composite(player(), (sx + sprite.width // 2 - 8, 7 * 16 - 12))
    d = ImageDraw.Draw(bg)
    d.rectangle([sx, 7 * 16 - D * 16, sx + sprite.width - 1, 7 * 16 - 1], outline=(255, 60, 60, 190))
    big = bg.resize((W * 3, H * 3), Image.NEAREST)
    out = Image.new("RGB", (W + 12 + W * 3, H * 3 + 18), (28, 28, 32))
    ImageDraw.Draw(out).text((4, 2), title, fill=(240, 240, 240))
    out.paste(bg.convert("RGB"), (0, 18))
    out.paste(big.convert("RGB"), (W + 12, 18))
    return out


def border(sprites, title, cols=15, rows_deep=3, scale=3):
    """A map border made of the pieces: `rows_deep` rows of them, edge to edge, north of a path, drawn
    back to front so each row covers the base of the one behind. sprites: [(sprite, D)] cycled.
    Shows whether a family works as the thing that frames a route instead of vanilla's tree line."""
    W = cols * 16
    base_y = 8 * 16
    H = base_y + 2 * 16
    bg = P.speckled(W, H, GROUND).convert("RGBA")
    d = ImageDraw.Draw(bg)
    d.rectangle([0, base_y, W, base_y + 16 - 1], fill=PATH)
    k = 0
    step = 16 * max(max(D for _, D in sprites), 1)
    for r in range(rows_deep - 1, -1, -1):
        x = 0
        while x < W:
            im, D = sprites[k % len(sprites)]
            k += 1
            foot = base_y - r * step
            bg.alpha_composite(im, (x, foot - im.height))
            x += im.width
    bg.alpha_composite(player(), (7 * 16, base_y - 12))
    big = bg.resize((W * scale, H * scale), Image.NEAREST)
    out = Image.new("RGB", (big.width + 16, big.height + 30), (28, 28, 32))
    ImageDraw.Draw(out).text((8, 6), title, fill=(240, 240, 240))
    out.paste(big.convert("RGB"), (8, 26))
    return out


def collage(groups, title, scale=2, max_w=1800):
    """groups: [(label, [sprite, ...])]: one row of sprites per blueprint, labelled, on ground."""
    rows = []
    for label, sprites in groups:
        h = max(s.height for s in sprites) * scale
        w = sum(s.width * scale + 6 for s in sprites)
        rows.append((label, sprites, w, h))
    width = min(max_w, max(r[2] for r in rows) + 24)
    total = 30
    for _, sprites, w, h in rows:
        lines = max(1, -(-w // (width - 24)))
        total += lines * (h + 8) + 18
    out = Image.new("RGB", (width, total), (28, 28, 32))
    d = ImageDraw.Draw(out)
    d.text((10, 6), title, fill=(240, 240, 240))
    y = 28
    for label, sprites, w, h in rows:
        d.text((10, y), label, fill=(220, 220, 220))
        y += 14
        x = 12
        for s in sprites:
            g = on_ground(s, scale, False)
            if x + g.width > width - 12:
                x = 12
                y += h + 8
            out.paste(g.convert("RGB"), (x, y + h - g.height))
            x += g.width + 6
        y += h + 12
    return out.crop((0, 0, width, y))


def vanilla_forest(cols, rows):
    """Petalburg Woods' tree grid (cols x rows trees, 2x2 cells each), grey, with a strip of open
    ground below so the front row's trunks show."""
    sys_path = os.path.join(C.ROOT, "tools", "tile-generator")
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    from tilegen import gba
    pw = gba.render_layout(gba.layouts()["PetalburgWoods_Layout"])
    # the woods' north-west block is a solid tree grid; its south edge row (484/485) is at rows 7-8, cols 4-11
    g = pw.crop((0, 0, cols * 32, rows * 32)).convert("LA")
    return Image.merge("RGBA", (g.getchannel(0),) * 3 + (Image.new("L", g.size, 255),))


def forest(blocks, cols, rows, title, scale=2):
    """blocks(col, row, edge) -> sprite (W*16 wide, any height, its foot at the bottom). Trees on a
    plain grid like vanilla, north rows first, the south row drawn as the forest edge; a path below,
    the player on it, and the same patch of vanilla forest (grey) beside it."""
    bw, bh = None, None
    sprites = {}
    for r in range(rows):
        for c in range(cols):
            sprites[(c, r)] = blocks(c, r, r == rows - 1)
    bw = max(s.width for s in sprites.values())
    bh = 32
    W, H = cols * bw, rows * bh + 40
    bg = P.speckled(W, H, GROUND).convert("RGBA")
    d = ImageDraw.Draw(bg)
    d.rectangle([0, rows * bh + 8, W, rows * bh + 23], fill=PATH)
    for r in range(rows):
        for c in range(cols):
            s = sprites[(c, r)]
            bg.alpha_composite(s, (c * bw, (r + 1) * bh - s.height))
    bg.alpha_composite(player(), (W // 2 - 8, rows * bh + 23 - 28))
    van = vanilla_forest(min(cols, 6), rows)
    vb = P.speckled(van.width, H, GROUND).convert("RGBA")
    vb.alpha_composite(van, (0, 0))
    ImageDraw.Draw(vb).rectangle([0, rows * bh + 8, van.width, rows * bh + 23], fill=PATH)
    out = Image.new("RGB", ((W + van.width) * scale + 36, H * scale + 30), (28, 28, 32))
    dd = ImageDraw.Draw(out)
    dd.text((8, 6), title, fill=(240, 240, 240))
    dd.text((W * scale + 28, 6), "vanilla (Petalburg Woods), grey", fill=(200, 200, 200))
    out.paste(bg.resize((W * scale, H * scale), Image.NEAREST).convert("RGB"), (8, 26))
    out.paste(vb.resize((van.width * scale, H * scale), Image.NEAREST).convert("RGB"), (W * scale + 28, 26))
    return out

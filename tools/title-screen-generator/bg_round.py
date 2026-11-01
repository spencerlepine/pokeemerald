"""Background round: same three layers as Emerald, recoloured and redrawn in place.

BG0 = gradient + creature silhouette (one 16-colour palette, BG palette 14, shared with BG1)
BG1 = clouds / nebula, blended 6/16 over BG0.
The gradient is copied tile-for-tile from Emerald's rayquaza tiles (same bands and dither rows); only colours change.

Palette 14 layout used here:
  0 transparent   1 creature dark detail   2 cloud light   3 creature rim light
  4..10 gradient (4 = bottom band, 10 = top band)   11 creature body
  12 cloud mid    13 cloud third   14 star   15 left alone (the game pulses it for the legendary's markings)
"""
import math, os, random, struct
from PIL import Image, ImageDraw, ImageChops
import gba_title as g
from backdrop import worm_path, maw, reduce, canvas, S
from logo import hexc

W, H = 240, 160


# ---------- gradient ----------

def vanilla_gradient_indices():
    """240x160 index map of Emerald's sky gradient: the left-most (pure gradient) tile of each tile row."""
    d = open(os.path.join(g.TS, "rayquaza.bin"), "rb").read()
    tiles = g.tiles_of(Image.open(os.path.join(g.TS, "rayquaza.png")))
    out = Image.new("P", (W, H), 0)
    px = out.load()
    for row in range(H // 8):
        e = struct.unpack_from("<H", d, (row * 32) * 2)[0]
        t = tiles[e & 0x3FF]
        for y in range(8):
            for x in range(W):
                px[x, row * 8 + y] = t[y][x % 8]
    return out


GRADIENTS = {
    # top band (index 10) first, bottom band (index 4) last
    "void-charcoal": ["080808", "101010", "181818", "202028", "282830", "303038", "383840"],
    "deep-space":    ["080810", "101020", "101828", "182030", "202838", "283040", "303848"],
    "dusk-violet":   ["080808", "100c18", "181020", "201828", "282030", "302838", "383040"],
}

CREATURE = {"body": "505860", "rim": "687080", "dark": "384048"}


def palette(grad, clouds):
    p = [(0, 0, 0)] * 16
    for i, c in enumerate(grad):
        p[10 - i] = hexc(c)
    p[11], p[3], p[1] = hexc(CREATURE["body"]), hexc(CREATURE["rim"]), hexc(CREATURE["dark"])
    p[2], p[12], p[13] = (hexc(c) for c in clouds["cols"])
    p[14] = hexc(clouds.get("star", "f8f8f0"))
    p[15] = (248, 248, 96)
    return p


# ---------- creature ----------

def _worm(points, r0, r1, ring_every=13):
    path = worm_path(points, r0, r1)
    body, rings = canvas(), canvas()
    db, dr = ImageDraw.Draw(body), ImageDraw.Draw(rings)
    for x, y, r, a in path:
        db.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=255)
    for i, (x, y, r, a) in enumerate(path):
        if i % ring_every == 0 and i < len(path) - 25:
            nx, ny = -math.sin(a), math.cos(a)
            dr.line([((x - nx * r * .9) * S, (y - ny * r * .9) * S), ((x + nx * r * .9) * S, (y + ny * r * .9) * S)], fill=255, width=S)
    return body, rings


def creature(points, r0, r1, head, ring_every=13):
    """Index masks: body (11), rim (3), detail (1). head = (cx, cy, r, squash, facing)."""
    body, rings = _worm(points, r0, r1, ring_every)
    cx, cy, r, sq, fa = head
    lip, throat, tooth = maw(cx, cy, r, teeth=11, facing=fa, squash=sq)
    body = ImageChops.lighter(body, lip)
    body, rings, lip, throat, tooth = map(reduce, (body, rings, lip, throat, tooth))
    rings = ImageChops.subtract(ImageChops.multiply(rings, body), lip)
    mouth = ImageChops.subtract(throat, tooth)
    rim = ImageChops.subtract(body, g_shift(body, 1, 2))
    return body, rim, ImageChops.lighter(rings, mouth), ImageChops.multiply(tooth, throat)


def g_shift(m, dx, dy):
    o = Image.new("L", m.size, 0); o.paste(m, (dx, dy)); return o


CREATURES = {
    "ring": dict(points=[(262, 150), (190, 156), (100, 154), (36, 134), (20, 104), (52, 80), (118, 74), (186, 82), (218, 108), (204, 134), (168, 138)],
                 r0=6, r1=17, head=(150, 128, 21, 0.85, 0.3)),
    "rising-s": dict(points=[(-12, 170), (34, 146), (70, 116), (114, 108), (152, 126), (184, 146), (214, 130), (224, 100), (206, 82)],
                     r0=7, r1=16, head=(196, 82, 19, 0.75, -0.4)),
    "double-coil": dict(points=[(-14, 118), (34, 150), (84, 136), (82, 102), (44, 104), (56, 142), (124, 158), (188, 146), (220, 114), (198, 86), (166, 94)],
                        r0=5, r1=16, head=(164, 104, 19, 0.85, 0.1)),
}


def bg0(grad_name, creature_name):
    idx = vanilla_gradient_indices()
    if creature_name:
        c = CREATURES[creature_name]
        body, rim, detail, teeth = creature(c["points"], c["r0"], c["r1"], c["head"])
        for m, i in ((body, 11), (rim, 3), (detail, 1), (teeth, 3)):
            idx.paste(i, (0, 0), m)
    return idx


# ---------- clouds / nebula (256x256, wraps vertically) ----------

def vanilla_clouds_indices():
    d = open(os.path.join(g.TS, "clouds.bin"), "rb").read()
    tiles = g.tiles_of(Image.open(os.path.join(g.TS, "clouds.png")))
    out = Image.new("P", (256, 256), 0); px = out.load()
    for i in range(1024):
        e = struct.unpack_from("<H", d, i * 2)[0]
        t, hf, vf = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1
        if t >= len(tiles):
            continue
        for y in range(8):
            for x in range(8):
                px[(i % 32) * 8 + x, (i // 32) * 8 + y] = tiles[t][7 - y if vf else y][7 - x if hf else x]
    return out


def stamp_cloud(px, x0, y0, rnd, length, layers, light=2, mid=12):
    """Chunky horizontal-slab cloud like Emerald's: stacked bars, light on top, mid along the bottom."""
    w = length
    for k in range(layers):
        bar_w = max(8, int(w * (1 - abs(k - layers / 2) / layers) * rnd.uniform(0.8, 1.0)))
        off = rnd.randint(-6, 6)
        h = rnd.choice([2, 2, 3])
        y = y0 + k * 2
        for yy in range(h):
            for xx in range(bar_w):
                X, Y = (x0 + off + xx) % 256, (y + yy) % 256
                col = light if (k < layers - 1 and yy < h - 1) else mid
                if px[X, Y] != light:
                    px[X, Y] = col


def clouds_drawn(seed, count, lmin, lmax, layers=(3, 6), stars=0, star_dim=0):
    rnd = random.Random(seed)
    out = Image.new("P", (256, 256), 0); px = out.load()
    for _ in range(count):
        stamp_cloud(px, rnd.randrange(256), rnd.randrange(256), rnd, rnd.randint(lmin, lmax), rnd.randint(*layers))
    for _ in range(stars):
        x, y = rnd.randrange(256), rnd.randrange(256)
        if px[x, y] == 0:
            px[x, y] = 14
    for _ in range(star_dim):
        x, y = rnd.randrange(256), rnd.randrange(256)
        if px[x, y] == 0:
            px[x, y] = 13
    return out


def nebula(seed, threshold=(0.55, 0.40, 0.30), band=None, stars=30):
    rnd = random.Random(seed)
    out = Image.new("P", (256, 256), 0); px = out.load()
    ph = [rnd.random() * 6.28 for _ in range(6)]
    for y in range(256):
        for x in range(256):
            v = (math.sin(x * 0.045 + 2.5 * math.sin(y * 2 * math.pi / 256 * 2 + ph[0]) + ph[1]) * 0.5
                 + math.sin(y * 2 * math.pi / 256 * 3 + x * 0.02 + ph[2]) * 0.35
                 + math.sin(x * 0.11 + y * 2 * math.pi / 256 * 5 + ph[3]) * 0.15)
            if band is not None:
                v -= abs(math.sin(y * 2 * math.pi / 256 + ph[4]) * 1.0) - 0.2
            dither = 0.08 if (x + y) % 2 else 0.0
            if v + dither > threshold[0]:
                px[x, y] = 2
            elif v + dither > threshold[1]:
                px[x, y] = 12
            elif v > threshold[2] and (x % 2 == 0 and y % 2 == 0):
                px[x, y] = 13
    for _ in range(stars):
        x, y = rnd.randrange(256), rnd.randrange(256)
        if px[x, y] == 0:
            px[x, y] = 14
    return out


def stars_only(seed=5):
    rnd = random.Random(seed)
    out = Image.new("P", (256, 256), 0); px = out.load()
    for _ in range(110):
        px[rnd.randrange(256), rnd.randrange(256)] = 13
    for _ in range(40):
        px[rnd.randrange(256), rnd.randrange(256)] = 14
    return out


GREY = ("e0e0e8", "9098a8", "c0c0d0")
LAV = ("e8e0f8", "a898d0", "c8b8e8")
VIOLET = ("d0b8f8", "8070c0", "b0a0e0")
CLOUDS = {
    "1-emerald-shapes-grey":     dict(make=vanilla_clouds_indices, cols=GREY),
    "2-emerald-shapes-lavender": dict(make=vanilla_clouds_indices, cols=LAV),
    "3-slab-clouds-grey":        dict(make=lambda: clouds_drawn(4, 16, 30, 70), cols=GREY),
    "4-thin-wisps-lavender":     dict(make=lambda: clouds_drawn(8, 26, 20, 60, layers=(2, 3), stars=25), cols=LAV),
    "5-nebula-violet":           dict(make=lambda: nebula(3, (0.8, 0.68, 0.9)), cols=VIOLET),
    "6-nebula-band":             dict(make=lambda: nebula(9, (0.55, 0.4, 9), band=True, stars=40), cols=LAV),
    "7-sparse-clouds-stars":     dict(make=lambda: clouds_drawn(12, 8, 24, 50, stars=40, star_dim=60), cols=LAV),
    "8-stars-only":              dict(make=stars_only, cols=GREY),
}


# ---------- rendering + tile budget ----------

def to_rgba(idx, pal, transparent0=True):
    rgba = Image.new("RGBA", idx.size, (0, 0, 0, 0)); src, dst = idx.load(), rgba.load()
    for y in range(idx.size[1]):
        for x in range(idx.size[0]):
            c = src[x, y]
            if c or not transparent0:
                dst[x, y] = g.gba(pal[c]) + (255,)
    return rgba


def unique_tiles(idx):
    """Unique 8x8 tiles counting h/v flips as the same tile (what the tilemap can reuse)."""
    seen = set(); px = idx.load()
    for ty in range(idx.size[1] // 8):
        for tx in range(idx.size[0] // 8):
            t = tuple(tuple(px[tx * 8 + x, ty * 8 + y] for x in range(8)) for y in range(8))
            forms = [t, tuple(r[::-1] for r in t), t[::-1], tuple(r[::-1] for r in t[::-1])]
            seen.add(min(forms))
    return len(seen)

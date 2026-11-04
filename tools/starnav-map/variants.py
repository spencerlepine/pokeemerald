"""The five StarNAV map styles. Each one draws its static layers with PIL; the browser player
(player.html) moves the cursor, zooms and writes the text.

Layers per style, all GBA sizes:
- map    224x120: the zoomed-out map BG (space, lanes, planets, town marks). Zoom is 2x of this, like Emerald.
- chrome 240x160: the frame over everything; the map window (VIEW) is left clear.
- style  JSON: text colours and slots, cursor kind, info panel colours (read by the player).
The `galaxy` style instead has a galaxy map and one detail map per planet (zoom = open the planet).

Every colour is GBA-safe (channels in steps of 8).
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import font
from world import (CELL, CLASSES, LAYOUT, MAP_H, MAP_W, GRASS, GROUND, PATH, ROCK, SPACE, TOWN, TREE, WATER,
                   WILD, planet_detail)

VIEW = (8, 20, 224, 120)      # map window on the 240x160 screen
SCREEN = (240, 160)


def g(c):
    """Snap a colour to the GBA's 15-bit grid."""
    return tuple((v // 8) * 8 for v in c[:3]) + tuple(c[3:])


def mix(a, b, t):
    return g(tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))


# biome colours for the full-colour styles: wild, water, rock, tree, grass, ground, path
BIOMES = {
    "TATOOINE":       [(152, 104, 64), (72, 120, 160), (168, 120, 72), (128, 96, 56), (208, 168, 104), (224, 184, 120), (248, 224, 168)],
    "KASHYYYK":       [(32, 72, 40), (48, 96, 144), (104, 96, 80), (40, 104, 48), (104, 160, 72), (128, 168, 88), (184, 160, 112)],
    "SULLUST":        [(56, 48, 56), (64, 88, 120), (88, 80, 88), (88, 104, 88), (136, 128, 112), (120, 112, 112), (184, 176, 160)],
    "MUSTAFAR":       [(48, 24, 24), (248, 120, 32), (64, 40, 40), (80, 48, 40), (128, 72, 48), (104, 64, 56), (176, 120, 88)],
    "ENDOR":          [(24, 64, 40), (56, 104, 136), (96, 96, 80), (32, 88, 48), (96, 152, 72), (88, 136, 72), (168, 144, 96)],
    "FELUCIA":        [(104, 40, 96), (64, 152, 152), (112, 72, 104), (152, 64, 128), (232, 136, 176), (208, 112, 160), (248, 208, 184)],
    "BESPIN":         [(184, 104, 88), (232, 184, 160), (168, 120, 112), (200, 144, 128), (240, 192, 160), (224, 176, 144), (248, 232, 208)],
    "JEDHA":          [(88, 80, 72), (88, 112, 136), (120, 112, 104), (112, 112, 96), (168, 152, 128), (184, 168, 144), (224, 208, 184)],
    "YAVIN 4":        [(16, 64, 48), (48, 112, 120), (104, 112, 96), (24, 96, 56), (112, 160, 64), (96, 144, 72), (176, 160, 104)],
    "HOTH":           [(160, 176, 208), (112, 160, 208), (152, 168, 192), (184, 200, 224), (216, 224, 240), (232, 240, 248), (248, 248, 248)],
    "KAMINO":         [(24, 40, 80), (40, 72, 128), (96, 112, 136), (88, 104, 128), (152, 168, 184), (160, 176, 192), (216, 224, 232)],
    "DAGOBAH":        [(24, 48, 32), (56, 88, 72), (72, 80, 64), (32, 72, 48), (96, 120, 64), (80, 104, 64), (136, 128, 88)],
    "ASTEROID FIELD": [(56, 48, 40), (64, 72, 96), (88, 80, 72), (96, 88, 72), (136, 120, 104), (128, 112, 96), (184, 168, 144)],
    "ILUM":           [(152, 184, 224), (80, 168, 232), (128, 160, 200), (168, 192, 224), (200, 224, 248), (216, 232, 248), (248, 248, 248)],
    "GRAND ARENA":    [(104, 96, 72), (64, 120, 168), (128, 120, 96), (80, 120, 72), (144, 160, 96), (184, 168, 128), (232, 216, 176)],
    "TYTHON":         [(72, 104, 64), (72, 136, 168), (128, 120, 104), (64, 112, 64), (128, 168, 96), (152, 168, 112), (208, 200, 152)],
    "ATOLLON":        [(40, 48, 72), (64, 88, 128), (64, 72, 96), (72, 88, 104), (120, 136, 144), (104, 112, 136), (168, 176, 192)],
    "MORTIS":         [(64, 48, 112), (88, 120, 200), (104, 88, 152), (112, 88, 160), (168, 152, 216), (152, 136, 200), (224, 216, 248)],
    "DEATH STAR":     [(64, 72, 80), (48, 64, 80), (96, 104, 112), (96, 104, 112), (128, 136, 144), (120, 128, 136), (168, 176, 184)],
}
SLOT = {WILD: 0, WATER: 1, ROCK: 2, TREE: 3, GRASS: 4, GROUND: 5, PATH: 6}


# ---------------------------------------------------------------- shared drawing

def starfield(img, seed, cols, density=0.012, box=None):
    rnd = random.Random(seed)
    px = img.load()
    W, H = img.size
    for y in range(H):
        for x in range(W):
            if rnd.random() < density:
                px[x, y] = g(rnd.choice(cols))


def dotted(img, a, b, col, on=2, off=2, skip=None):
    px = img.load()
    (x0, y0), (x1, y1) = a, b
    n = int(max(abs(x1 - x0), abs(y1 - y0)))
    for i in range(n + 1):
        if i % (on + off) >= on:
            continue
        x = round(x0 + (x1 - x0) * i / max(n, 1))
        y = round(y0 + (y1 - y0) * i / max(n, 1))
        if 0 <= x < img.size[0] and 0 <= y < img.size[1] and not (skip and skip(x, y)):
            px[x, y] = col


def lane_ends(world, a, b):
    return world.centres[a], world.centres[b]


def land_image(world, colour, outline=None, shadow=None, highlight=None, cls=None, planet=None, size=None):
    """Colour a class map. colour(cls, planet, x, y) -> rgb or None. Adds a 1 px outline into space,
    a drop shadow under the land and a lit top edge."""
    W, H = size or (MAP_W, MAP_H)
    cls = cls or world.cls
    pl = planet or world.planet
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    def land(x, y):
        return 0 <= x < W and 0 <= y < H and cls[y][x] != SPACE

    for y in range(H):
        for x in range(W):
            c = cls[y][x]
            p = pl[y][x] if isinstance(pl, list) else pl
            if c != SPACE:
                col = colour(c, p, x, y)
                if highlight and not land(x, y - 1):
                    col = highlight(col)
                px[x, y] = g(col) + (255,)
            else:
                if shadow and land(x, y - 1) or shadow and land(x - 1, y - 1) and land(x - 1, y):
                    px[x, y] = g(shadow) + (255,)
                if outline and any(land(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    px[x, y] = g(outline) + (255,)
    return img


def texture(c, base, x, y):
    """A little pixel texture per class: tree checker, grass flecks, water stripes, path flat."""
    if c == TREE:
        return base if (x + y) % 2 else mix(base, (0, 0, 0), 0.25)
    if c == GRASS:
        return mix(base, (255, 255, 255), 0.18) if (x * 7 + y * 3) % 5 == 0 else base
    if c == WATER:
        return mix(base, (255, 255, 255), 0.2) if (y % 3 == 0 and (x + y // 3) % 4 < 2) else base
    if c == ROCK:
        return mix(base, (0, 0, 0), 0.2) if (x + 2 * y) % 4 == 0 else base
    if c == WILD:
        return mix(base, (0, 0, 0), 0.25) if (x + y) % 2 == 0 and (x // 2 + y) % 3 == 0 else base
    return base


def mono(ramp):
    """A one-hue ramp: class -> colour, for the hologram / tactical / amber styles."""
    def f(c, p, x, y):
        return texture(c, ramp[SLOT[c]], x, y)
    return f


def scanlines(img, amount=0.22, view_only=None):
    px = img.load()
    W, H = img.size
    for y in range(1, H, 2):
        for x in range(W):
            v = px[x, y]
            if len(v) == 4 and v[3] == 0:
                continue
            px[x, y] = g(tuple(int(c * (1 - amount)) for c in v[:3])) + tuple(v[3:])


def stamp(img, art, x, y, cols):
    """Draw ASCII art: each char indexes cols (a dict), '.' is clear."""
    px = img.load()
    for j, r in enumerate(art.strip("\n").splitlines()):
        for i, ch in enumerate(r):
            if ch in cols and 0 <= x + i < img.size[0] and 0 <= y + j < img.size[1]:
                px[x + i, y + j] = g(cols[ch]) + (255,)


PILL = """
.oooooo.
oHhhhhho
ohhhhhho
ohsssssо
.oooooo.
""".replace("о", "o")
DIAMOND = """
...o...
..oHo..
.oHhho.
oHhhhso
.ohhso.
..oso..
...o...
"""
SQUARE = """
oooooo
oHhhho
ohssho
ohssho
ohhhho
oooooo
"""
RING = """
.oooo.
oo..oo
o....o
o....o
oo..oo
.oooo.
"""


def town_marks(img, world, art, cols, towns=None, offset=(0, 0)):
    towns = towns if towns is not None else world.towns
    lines = art.strip("\n").splitlines()
    w, h = len(lines[0]), len(lines)
    for a, (cx, cy) in towns.items():
        stamp(img, art, offset[0] + cx * CELL + (CELL - w) // 2, offset[1] + cy * CELL + (CELL - h) // 2, cols)


def frame_box(d, x0, y0, x1, y1, fill=None, outline=None):
    d.rectangle((x0, y0, x1, y1), fill=fill, outline=outline)


def clear_view(img, inset=0):
    x, y, w, h = VIEW
    ImageDraw.Draw(img).rectangle((x + inset, y + inset, x + w - 1 - inset, y + h - 1 - inset), fill=(0, 0, 0, 0))


def corners(d, x0, y0, x1, y1, col, n=6):
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line((x, y, x + sx * n, y), fill=col)
        d.line((x, y, x, y + sy * n), fill=col)


# ---------------------------------------------------------------- the styles

def style_holo(world):
    """1 HOLOTABLE: a Rebel briefing hologram. Black, one cyan hue, scanlines, gold cursor."""
    ramp = [(16, 40, 64), (24, 64, 112), (40, 96, 136), (32, 80, 120), (56, 120, 160), (72, 144, 184), (160, 232, 248)]
    m = Image.new("RGBA", (MAP_W, MAP_H), g((8, 8, 16)) + (255,))
    starfield(m, 1, [(32, 48, 72), (48, 72, 104), (88, 120, 160)], 0.02)
    for a, b in world.lanes:
        dotted(m, *lane_ends(world, a, b), g((40, 120, 168)) + (255,), 1, 2)
    land = land_image(world, mono(ramp), outline=(88, 200, 248), highlight=lambda c: mix(c, (255, 255, 255), 0.25))
    m.alpha_composite(land)
    town_marks(m, world, DIAMOND, {"o": (24, 64, 112), "H": (248, 248, 248), "h": (184, 240, 248), "s": (88, 200, 248)})
    scanlines(m, 0.3)

    c = Image.new("RGBA", SCREEN, g((8, 8, 16)) + (255,))
    d = ImageDraw.Draw(c)
    cy = g((88, 200, 248))
    dim = g((32, 80, 120))
    d.line((0, 17, 239, 17), fill=dim)
    d.line((0, 143, 239, 143), fill=dim)
    clear_view(c)
    x, y, w, h = VIEW
    d.rectangle((x - 1, y - 1, x + w, y + h), outline=dim)
    corners(d, x - 2, y - 2, x + w + 1, y + h + 1, cy, 7)
    font.draw(c, 8, 145, "STARNAV", cy, None, "aurebesh")
    hint = "A ZOOM   B CLOSE"
    font.draw(c, 232 - font.text_width(hint, "small"), 146, hint, g((88, 200, 248)), g((16, 40, 64)), "small")
    scanlines(c, 0.25)
    return {"map": m, "chrome": c, "style": {
        "title": "Holotable", "zoom": "scale",
        "name": {"x": 8, "y": 1, "font": "normal", "ink": cy, "shadow": g((16, 48, 80))},
        "sub": {"x": 232, "y": 3, "font": "small", "ink": g((40, 120, 168)), "shadow": None, "align": "right"},
        "cursor": {"kind": "brackets", "col": g((248, 208, 0)), "col2": g((248, 240, 160))},
        "panel": {"fill": g((8, 16, 32)), "edge": cy, "ink": g((184, 240, 248)), "shadow": g((16, 48, 80)), "dim": g((40, 120, 168))},
        "empty": "",
    }}


def style_atlas(world):
    """2 STAR ATLAS: every planet in its own colours, floating in space, linked by gold hyperlanes."""
    m = Image.new("RGBA", (MAP_W, MAP_H), g((8, 8, 16)) + (255,))
    rnd = random.Random(7)
    px = m.load()
    # faint nebula: a few soft dithered blobs
    for (cx, cy, r, col) in ((40, 100, 60, (40, 16, 56)), (170, 20, 70, (16, 24, 56)), (200, 110, 50, (40, 16, 48))):
        for y in range(MAP_H):
            for x in range(MAP_W):
                dd = math.hypot(x - cx, y - cy) / r
                if dd < 1 and rnd.random() < (1 - dd) * 0.6 and (x + y) % 2 == 0:
                    px[x, y] = g(col) + (255,)
    starfield(m, 2, [(120, 128, 160), (248, 248, 240), (88, 200, 248), (248, 240, 160)], 0.01)
    for a, b in world.lanes:
        dotted(m, *lane_ends(world, a, b), g((184, 136, 0)) + (255,), 2, 2)

    def colour(c, p, x, y):
        return texture(c, BIOMES[p][SLOT[c]], x, y)
    land = land_image(world, colour, outline=(8, 8, 8), shadow=(0, 0, 0),
                      highlight=lambda c: mix(c, (255, 255, 255), 0.3))
    m.alpha_composite(land)
    town_marks(m, world, PILL, {"o": (96, 64, 0), "H": (248, 248, 240), "h": (248, 208, 0), "s": (184, 136, 0)})

    c = Image.new("RGBA", SCREEN, g((16, 24, 40)) + (255,))
    d = ImageDraw.Draw(c)
    gold, gold_d, gold_o = g((248, 208, 0)), g((184, 136, 0)), g((96, 64, 0))
    d.rectangle((0, 0, 239, 17), fill=g((8, 8, 8)))
    d.line((0, 18, 239, 18), fill=gold_d)
    d.rectangle((0, 142, 239, 159), fill=g((8, 8, 8)))
    d.line((0, 142, 239, 142), fill=gold_d)
    clear_view(c)
    x, y, w, h = VIEW
    d.rectangle((x - 2, y - 1, x + w + 1, y + h), outline=gold_o)
    d.rectangle((x - 1, y - 1, x + w, y + h), outline=gold_d)
    clear_view(c)
    font.draw(c, 8, 144, "STARNAV", gold, gold_o, "normal")
    hint = "A ZOOM  B CLOSE"
    font.draw(c, 232 - font.text_width(hint, "small"), 146, hint, g((248, 240, 160)), gold_o, "small")
    return {"map": m, "chrome": c, "style": {
        "title": "Star Atlas", "zoom": "scale",
        "name": {"x": 8, "y": 1, "font": "normal", "ink": g((248, 248, 240)), "shadow": g((96, 96, 112))},
        "sub": {"x": 232, "y": 3, "font": "small", "ink": gold, "shadow": gold_o, "align": "right"},
        "cursor": {"kind": "box", "col": g((248, 48, 48)), "col2": g((248, 248, 240))},
        "panel": {"fill": g((16, 24, 40)), "edge": gold_d, "ink": g((248, 248, 240)), "shadow": g((64, 64, 80)), "dim": gold},
        "empty": "",
    }}


def style_imperial(world):
    """3 IMPERIAL TACTICAL: a fleet display. Grey on black, the section grid shown, red marks and crosshair."""
    ramp = [(32, 36, 40), (40, 56, 72), (72, 80, 88), (80, 88, 96), (104, 112, 120), (128, 136, 144), (232, 232, 232)]
    m = Image.new("RGBA", (MAP_W, MAP_H), g((16, 16, 16)) + (255,))
    d = ImageDraw.Draw(m)
    for x in range(0, MAP_W, CELL):
        d.line((x, 0, x, MAP_H), fill=g((32, 32, 40)))
    for y in range(0, MAP_H, CELL):
        d.line((0, y, MAP_W, y), fill=g((32, 32, 40)))
    for x in range(0, MAP_W, CELL * 4):
        d.line((x, 0, x, MAP_H), fill=g((48, 48, 56)))
    for y in range(0, MAP_H, CELL * 4):
        d.line((0, y, MAP_W, y), fill=g((48, 48, 56)))
    for a, b in world.lanes:
        dotted(m, *lane_ends(world, a, b), g((136, 24, 24)) + (255,), 3, 2)
    land = land_image(world, mono(ramp), outline=(168, 176, 184), shadow=(8, 8, 8))
    m.alpha_composite(land)
    town_marks(m, world, SQUARE, {"o": (16, 16, 16), "H": (248, 248, 248), "h": (192, 32, 32), "s": (248, 48, 48)})

    c = Image.new("RGBA", SCREEN, g((8, 8, 8)) + (255,))
    d = ImageDraw.Draw(c)
    red, grey = g((192, 32, 32)), g((96, 104, 112))
    d.rectangle((0, 0, 239, 17), fill=g((16, 16, 16)))
    d.rectangle((0, 0, 3, 17), fill=red)
    d.line((0, 17, 239, 17), fill=red)
    d.rectangle((0, 142, 239, 159), fill=g((16, 16, 16)))
    d.line((0, 142, 239, 142), fill=g((48, 48, 56)))
    clear_view(c)
    x, y, w, h = VIEW
    d.rectangle((x - 1, y - 1, x + w, y + h), outline=grey)
    for i in range(0, w, 16):   # ruler ticks
        d.point((x + i, y - 2), fill=grey)
        d.point((x + i, y + h + 1), fill=grey)
    font.draw(c, 8, 147, "IMPERIAL NAV", grey, None, "aurebesh")
    hint = "A ZOOM  B CLOSE"
    font.draw(c, 232 - font.text_width(hint, "small"), 146, hint, g((240, 240, 240)), g((64, 64, 72)), "small")
    return {"map": m, "chrome": c, "style": {
        "title": "Imperial Tactical", "zoom": "scale",
        "name": {"x": 9, "y": 1, "font": "normal", "ink": g((240, 240, 240)), "shadow": g((64, 64, 72))},
        "sub": {"x": 232, "y": 3, "font": "small", "ink": g((248, 48, 48)), "shadow": None, "align": "right"},
        "cursor": {"kind": "crosshair", "col": g((248, 48, 48)), "col2": g((248, 248, 248))},
        "panel": {"fill": g((16, 16, 16)), "edge": red, "ink": g((240, 240, 240)), "shadow": g((64, 64, 72)), "dim": g((168, 176, 184))},
        "empty": "",
    }}


def style_amber(world):
    """4 TARGETING COMPUTER: the X-wing's amber CRT. Black glass, one amber hue, a reticle cursor."""
    ramp = [(56, 24, 0), (80, 32, 0), (120, 56, 8), (104, 48, 8), (152, 72, 8), (184, 96, 16), (248, 176, 56)]
    m = Image.new("RGBA", (MAP_W, MAP_H), g((16, 8, 0)) + (255,))
    starfield(m, 4, [(64, 32, 0), (104, 48, 8)], 0.015)
    for a, b in world.lanes:
        dotted(m, *lane_ends(world, a, b), g((136, 64, 8)) + (255,), 1, 1)
    land = land_image(world, mono(ramp), outline=(248, 136, 24))
    m.alpha_composite(land)
    town_marks(m, world, RING, {"o": (248, 216, 120)})
    scanlines(m, 0.35)

    c = Image.new("RGBA", SCREEN, g((24, 16, 8)) + (255,))
    d = ImageDraw.Draw(c)
    amber, amber_d = g((248, 160, 40)), g((136, 64, 8))
    # a rounded bezel around the glass
    x, y, w, h = VIEW
    d.rounded_rectangle((x - 5, y - 4, x + w + 4, y + h + 3), radius=6, fill=g((40, 24, 8)), outline=g((72, 48, 24)))
    d.rounded_rectangle((x - 2, y - 2, x + w + 1, y + h + 1), radius=4, fill=g((16, 8, 0)), outline=amber_d)
    clear_view(c)
    for i in range(4):   # bezel screws
        sx = (x - 4, x + w + 2)[i % 2]
        sy = (y - 3, y + h + 1)[i // 2]
        d.point((sx, sy), fill=g((112, 80, 40)))
    font.draw(c, 8, 145, "TARGETING", amber, g((72, 32, 0)), "small")
    font.draw(c, 64, 147, "STARNAV", amber_d, None, "aurebesh")
    hint = "A ZOOM  B CLOSE"
    font.draw(c, 232 - font.text_width(hint, "small"), 145, hint, amber, g((72, 32, 0)), "small")
    return {"map": m, "chrome": c, "style": {
        "title": "Targeting Computer", "zoom": "scale",
        "name": {"x": 8, "y": 0, "font": "normal", "ink": amber, "shadow": g((72, 32, 0))},
        "sub": {"x": 232, "y": 2, "font": "small", "ink": amber_d, "shadow": None, "align": "right"},
        "cursor": {"kind": "reticle", "col": g((248, 216, 120)), "col2": amber},
        "panel": {"fill": g((24, 8, 0)), "edge": amber, "ink": g((248, 200, 96)), "shadow": g((72, 32, 0)), "dim": amber_d},
        "empty": "",
    }}


GALAXY_POS = {   # planet -> centre on the 224x120 galaxy map, roughly along the spiral
    "TATOOINE": (34, 70), "KASHYYYK": (22, 34), "SULLUST": (62, 22), "MUSTAFAR": (60, 100),
    "GRAND ARENA": (12, 104), "ENDOR": (94, 54), "FELUCIA": (98, 92), "JEDHA": (118, 24),
    "BESPIN": (130, 74), "TYTHON": (116, 108), "ATOLLON": (144, 104), "MORTIS": (162, 96),
    "YAVIN 4": (158, 40), "HOTH": (152, 12), "DEATH STAR": (190, 18), "KAMINO": (206, 96),
    "DAGOBAH": (186, 66), "ASTEROID FIELD": (212, 48), "ILUM": (210, 16),
}
GLOBE_R = {"TATOOINE": 7, "BESPIN": 6, "YAVIN 4": 6, "ENDOR": 6, "DAGOBAH": 6, "KASHYYYK": 6}


def globe(img, cx, cy, r, base, dark, lite, ring=False):
    px = img.load()
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            dd = math.hypot(dx, dy)
            if dd <= r:
                light = (-dx - dy) / (r * 1.4)
                col = base
                if light > 0.45:
                    col = lite
                elif light < -0.35 or dd > r - 0.9 and light < 0.1:
                    col = dark
                if dd > r - 0.9 and light < -0.2:
                    col = mix(dark, (0, 0, 0), 0.4)
                px[x, y] = g(col) + (255,)
    if ring:
        for i in range(int(-r * 2), int(r * 2) + 1):
            x, y = int(cx + i), int(cy + i * 0.25)
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) > r - 0.5 or i > 0:
                px[x, y] = g(lite) + (255,)


def style_galaxy(world):
    """5 GALAXY CHART: zoomed out is the galaxy, each planet a globe; zoom opens that planet's own map."""
    m = Image.new("RGBA", (MAP_W, MAP_H), g((8, 8, 16)) + (255,))
    px = m.load()
    rnd = random.Random(5)
    cx, cy = 112, 62
    # two dithered spiral arms
    for t in [i / 400 for i in range(2400)]:
        for arm in (0, math.pi):
            a = t * 2.4 + arm
            rr = 6 + t * 26
            for _ in range(2):
                x = int(cx + math.cos(a) * rr * 1.7 + rnd.gauss(0, 3 + t))
                y = int(cy + math.sin(a) * rr * 0.9 + rnd.gauss(0, 2 + t * 0.6))
                if 0 <= x < MAP_W and 0 <= y < MAP_H:
                    col = mix((120, 80, 168), (24, 24, 64), min(1, t / 5))
                    if rnd.random() < 0.15:
                        col = (184, 168, 224)
                    px[x, y] = col + (255,)
    for y in range(cy - 4, cy + 5):
        for x in range(cx - 7, cx + 8):
            if ((x - cx) / 7) ** 2 + ((y - cy) / 4) ** 2 <= 1:
                px[x, y] = g((248, 240, 200) if ((x - cx) / 4) ** 2 + ((y - cy) / 2) ** 2 <= 1 else (200, 168, 224)) + (255,)
    starfield(m, 6, [(120, 128, 160), (248, 248, 240)], 0.008)
    for a, b in world.lanes:
        dotted(m, GALAXY_POS[a], GALAXY_POS[b], g((88, 200, 248)) + (255,), 1, 2)
    for p, (x, y) in GALAXY_POS.items():
        b = BIOMES[p]
        r = GLOBE_R.get(p, 5)
        if p == "DEATH STAR":
            globe(m, x, y, 5, (128, 136, 144), (72, 80, 88), (184, 192, 200))
            stamp(m, "oo\noo", x - 3, y - 3, {"o": (48, 56, 64)})
        else:
            globe(m, x, y, r, b[5], b[0], b[6], ring=(p == "BESPIN"))

    planets = {}
    for p in LAYOUT:
        det = planet_detail(world, p)
        if not det:
            continue
        d = Image.new("RGBA", (224, 120), g((8, 8, 16)) + (255,))
        starfield(d, hash(p) & 255, [(120, 128, 160), (64, 72, 96)], 0.01)

        def colour(c, _p, x, y, p=p):
            return texture(c, BIOMES[p][SLOT[c]], x, y)
        land = land_image(world, colour, outline=(8, 8, 8), shadow=(0, 0, 0),
                          highlight=lambda c: mix(c, (255, 255, 255), 0.3), cls=det["cls"], planet=p, size=(224, 120))
        d.alpha_composite(land)
        town_marks(d, world, PILL, {"o": (96, 64, 0), "H": (248, 248, 240), "h": (248, 208, 0), "s": (184, 136, 0)},
                   towns={a: tuple(v) for a, v in det["towns"].items()})
        planets[p] = {"img": d, "cells": det["cells"], "towns": det["towns"]}

    c = Image.new("RGBA", SCREEN, g((40, 56, 64)) + (255,))
    d = ImageDraw.Draw(c)
    gold, gold_o, steel = g((248, 208, 0)), g((96, 64, 0)), g((144, 176, 200))
    d.rectangle((0, 0, 239, 17), fill=g((16, 24, 40)))
    d.line((0, 17, 239, 17), fill=steel)
    d.rectangle((0, 143, 239, 159), fill=g((16, 24, 40)))
    d.line((0, 143, 239, 143), fill=steel)
    x, y, w, h = VIEW
    d.rounded_rectangle((x - 3, y - 2, x + w + 2, y + h + 1), radius=3, fill=g((8, 8, 16)), outline=steel)
    clear_view(c)
    font.draw(c, 8, 145, "STARNAV", gold, gold_o, "normal")
    hint = "A OPEN  B BACK"
    font.draw(c, 232 - font.text_width(hint, "small"), 147, hint, steel, g((16, 24, 40)), "small")
    return {"map": m, "chrome": c, "planets": planets, "style": {
        "title": "Galaxy Chart", "zoom": "planet",
        "galaxy": {p: list(v) for p, v in GALAXY_POS.items()},
        "radius": {p: GLOBE_R.get(p, 5) for p in GALAXY_POS},
        "name": {"x": 8, "y": 1, "font": "normal", "ink": g((248, 248, 240)), "shadow": g((64, 72, 96))},
        "sub": {"x": 232, "y": 3, "font": "small", "ink": gold, "shadow": gold_o, "align": "right"},
        "cursor": {"kind": "box", "col": gold, "col2": g((248, 248, 240)), "ring": g((88, 200, 248))},
        "panel": {"fill": g((16, 24, 40)), "edge": steel, "ink": g((248, 248, 240)), "shadow": g((64, 72, 96)), "dim": gold},
        "empty": "",
    }}


STYLES = [("holotable", style_holo), ("atlas", style_atlas), ("imperial", style_imperial),
          ("targeting", style_amber), ("galaxy", style_galaxy)]

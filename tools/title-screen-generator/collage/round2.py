"""Round 2: de-clutter the collage (owner, 2026-11-01: "the bottom is a little too cluttered ... each sprite by
itself is good but combined it's too detailed"). Three tactics, all baked into the sprite pixels so they stay
hardware-legal (a darker copy is just another 16-colour OBJ palette; the fade is ordered dither to transparent):

  depth  back rows are pulled toward the night backdrop (z1 most, front row untouched): aerial perspective, so the
         eye lands on the front row and the back row reads as one quieter mass
  fade   the bottom 24 rows dissolve into the backdrop with a 4x4 Bayer checker, in 8-row bands (STYLE.md 2),
         so feet and the pile-up at the screen edge go away
  ridge  a flat dark foreground dune on a BG above the OBJs hides feet and the bottom pile-up without dither
  fewer  two creatures, one per side, in the gaps between people instead of on top of them

    python3 round2.py OUT_DIR       -> v1..v6 + a contact sheet, each with layers/ + layers.json, and v3's slide-in
"""
import os, sys, json
from PIL import Image
import compose as C, blocking

BACKDROP = (8, 8, 16)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
DEPTH = {1: 0.55, 2: 0.35, 3: 0.12}
FADE_TOP = 136


def gba(c):
    return tuple(min(248, (int(round(v)) >> 3) << 3) for v in c)


def depth(s, t):
    if not t:
        return s
    px = s.load()
    for y in range(s.size[1]):
        for x in range(s.size[0]):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = gba((r + (BACKDROP[0] - r) * t, g + (BACKDROP[1] - g) * t, b + (BACKDROP[2] - b) * t)) + (255,)
    return s


def fade(s, top, start=FADE_TOP):
    """Dissolve rows below `start` (screen y): 8-row bands at 25 / 50 / 75 % gone."""
    px = s.load()
    for y in range(s.size[1]):
        sy = top + y
        if sy < start:
            continue
        band = min(3, (sy - start) // 8 + 1)
        for x in range(s.size[0]):
            if BAYER[sy % 4][x % 4] < band * 4:
                px[x, y] = (0, 0, 0, 0)
    return s


# people spread a little wider apart than round 1 so faces don't stack
PEOPLE = {
    "obiwan": dict(x=14, y=166), "kael": dict(x=40, y=170), "leia": dict(x=70, y=168), "mira": dict(x=94, y=172),
    "trooper": dict(x=166, y=170), "vader": dict(x=206, y=172), "boba": dict(x=234, y=166),
}
CORNERS = [  # one creature per side, out in front on the ridge, at the outer corners where nobody's face is
    dict(name="lothwolf", src=C.creature("absol", 1), x=62, y=160, z=5, side="L", flip=True),
    dict(name="fyrnalpha", src=C.creature("houndoom", 1), x=184, y=162, z=5, side="R"),
]
TWO = [
    dict(name="lothwolf", src=C.creature("absol", 1), x=118, y=162, z=5, side="L", flip=True),
    dict(name="fyrnalpha", src=C.creature("houndoom", 1), x=140, y=164, z=5, side="R"),
]


def cast(creatures):
    out = []
    for c in C.CAST:
        c = dict(c); c.update(PEOPLE.get(c["name"], {}))
        out.append(c)
    return out + creatures


RIDGE = (16, 16, 32)       # one step above the backdrop: reads as ground, not a hole
RIDGE_LIT = (48, 48, 72)   # 1 px lit lip (STYLE.md 1: BGs have no outline, the ground's top edge is the one line)


def ridge_y(x):
    """A low foreground dune: higher at the screen edges, dipping in the middle under the copyright line."""
    import math
    return int(150 - 8 * abs(x - 120) / 120 + 2 * math.sin(x / 9.0) + 1.5 * math.sin(x / 4.3 + 1))


def ridge():
    """Foreground silhouette drawn on a BG with priority above the OBJs: it covers feet and the pile-up at the
    bottom edge with one flat dark shape instead of dither."""
    r = Image.new("RGBA", (C.W, C.H))
    px = r.load()
    for x in range(C.W):
        top = ridge_y(x)
        for y in range(top, C.H):
            px[x, y] = (RIDGE_LIT if y == top else RIDGE) + (255,)
    return r


def build(cs, use_depth, use_fade, offsets=None, use_ridge=False):
    back, fg = LAYERS
    img = back.copy()
    layers = []
    for c in sorted(cs, key=lambda c: c["z"]):
        s = C.load(c["src"], c.get("flip", False))
        x = c["x"] - s.size[0] // 2 + (offsets or {}).get(c["name"], 0)
        y = c["y"] - s.size[1]
        if use_depth:
            s = depth(s, DEPTH.get(c["z"], 0))
        if use_fade:
            s = fade(s, y)
        tmp = Image.new("RGBA", (C.W, C.H)); tmp.paste(s, (x, y), s)
        img.alpha_composite(tmp)
        layers.append((c, s, x, y))
        if use_ridge and c["z"] == 4:
            img.alpha_composite(ridge())   # ridge sits in front of the people, behind the front creatures
    img.alpha_composite(fg)
    return img, layers


def save(name, cs, d, f, out, rg=False):
    img, layers = build(cs, d, f, use_ridge=rg)
    os.makedirs(os.path.join(out, name, "layers"), exist_ok=True)
    img.convert("RGB").save(os.path.join(out, name, "collage_1x.png"))
    img.convert("RGB").resize((720, 480), Image.NEAREST).save(os.path.join(out, name + ".png"))
    meta = []
    for c, s, x, y in layers:
        s.save(os.path.join(out, name, "layers", c["name"] + ".png"))
        meta.append(dict(name=c["name"], x=x, y=y, w=s.size[0], h=s.size[1], z=c["z"], side=c.get("side"),
                         colours=len({p for p in s.get_flattened_data() if p[3]})))
    json.dump(meta, open(os.path.join(out, name, "layers.json"), "w"), indent=1)
    return img


def gif(cs, d, f, path, frames=40, rg=False):
    ims = []
    for fr in range(frames):
        offs = {}
        for c in cs:
            t = min(1, max(0, (fr - c["z"] * 4) / 16)); t = 1 - (1 - t) ** 3
            offs[c["name"]] = int((1 - t) * 90) * (-1 if c.get("side") == "L" else 1)
        ims.append(build(cs, d, f, offs, rg)[0].convert("RGB").resize((480, 320), Image.NEAREST))
    ims[0].save(path, save_all=True, append_images=ims[1:] + [ims[-1]] * 30, duration=33, loop=0)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    LAYERS = blocking.layers()
    V = [("v1_two_creatures", cast(TWO), False, False),
         ("v2_two_creatures_depth", cast(TWO), True, False),
         ("v3_two_creatures_depth_fade", cast(TWO), True, True),
         ("v4_no_creatures_depth_fade", cast([]), True, True)]
    V += [("v5_ridge_two_creatures", cast(CORNERS), True, False, True),
          ("v6_ridge_no_creatures", cast([]), True, False, True)]
    V = [v if len(v) == 5 else v + (False,) for v in V]
    ims = [save(n, cs, d, f, out, rg) for n, cs, d, f, rg in V]
    sheet = Image.new("RGB", (480 * 2 + 8, 320 * 3 + 16), (255, 255, 255))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((480, 320), Image.NEAREST), ((i % 2) * 488, (i // 2) * 328))
    sheet.save(os.path.join(out, "round2_sheet.png"))
    gif(V[4][1], True, False, os.path.join(out, "v5_slide_in.gif"), rg=True)

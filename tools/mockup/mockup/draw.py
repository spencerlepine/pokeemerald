"""Draw one area as a flat shapes-and-colours mockup: planet-coloured terrain, simple 3/4-view buildings,
props as basic shapes, and pink-family figures for people. 16 px per map cell, like the game."""
import math
import zlib

from PIL import Image, ImageDraw, ImageFont

from .style import shade
from . import build as _build

C = 16
TERRAIN = {".": "ground", ":": "path", '"': "wild", "~": "water", "=": "bridge", "T": "nature", "#": "cliff",
           "v": "ledge", "^": "ledge", "<": "ledge", ">": "ledge", "H": "ladder", "x": "blocked", "_": "floor", "|": "wall"}


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


F_SMALL, F, F_BIG = _font(9), _font(11), _font(15)


def _h(*v):
    h = 2166136261
    for x in v:
        h = ((h ^ (x & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    return h


# ---------------------------------------------------------------------------------------------- terrain
def terrain(d, grid, pal, nature_kind, water_kind):
    H, W = len(grid), len(grid[0])

    def at(x, y):
        return grid[y][x] if 0 <= x < W and 0 <= y < H else None

    for y in range(H):
        for x in range(W):
            ch = grid[y][x]
            name = TERRAIN.get(ch, "blocked")
            x0, y0 = x * C, y * C
            box = [x0, y0, x0 + C - 1, y0 + C - 1]
            base = pal["ground"] if name in ("nature", "ledge") else pal.get(name, pal["ground"])
            d.rectangle(box, fill=base)
            r = _h(x, y)
            if name == "ground":
                for k in range(3):
                    rr = _h(x, y, k)
                    d.point((x0 + rr % 16, y0 + (rr >> 8) % 16), fill=shade(base, -0.08))
            elif name == "path":
                if at(x, y - 1) not in (":",):
                    d.line([x0, y0, x0 + 15, y0], fill=shade(base, -0.06))
                d.point((x0 + r % 16, y0 + (r >> 8) % 16), fill=shade(base, -0.05))
            elif name == "wild":
                dark = shade(base, -0.28)
                for tx, ty in ((1, 4), (8, 2), (4, 10), (11, 11)):
                    d.line([(x0 + tx, y0 + ty + 4), (x0 + tx + 1, y0 + ty), (x0 + tx + 2, y0 + ty + 4)], fill=dark)
                    d.line([(x0 + tx + 2, y0 + ty + 4), (x0 + tx + 3, y0 + ty + 1)], fill=dark)
            elif name == "water":
                if water_kind == "lava":
                    d.ellipse([x0 + r % 8, y0 + (r >> 4) % 8, x0 + r % 8 + 5, y0 + (r >> 4) % 8 + 3], fill=shade(base, 0.35))
                elif water_kind == "void":
                    if r % 7 == 0:
                        d.point((x0 + r % 16, y0 + (r >> 8) % 16), fill=(230, 230, 240))
                else:
                    light = shade(base, 0.25)
                    off = (y % 2) * 4
                    d.line([(x0 + 1 + off, y0 + 5), (x0 + 4 + off, y0 + 4), (x0 + 7 + off, y0 + 5)], fill=light)
                    d.line([(x0 + 6 - off, y0 + 12), (x0 + 9 - off, y0 + 11), (x0 + 12 - off, y0 + 12)], fill=light)
                    for nx, ny, side in ((x, y - 1, "n"), (x - 1, y, "w"), (x + 1, y, "e"), (x, y + 1, "s")):
                        if at(nx, ny) not in ("~", None):
                            edge = {"n": [x0, y0, x0 + 15, y0 + 1], "s": [x0, y0 + 14, x0 + 15, y0 + 15],
                                    "w": [x0, y0, x0 + 1, y0 + 15], "e": [x0 + 14, y0, x0 + 15, y0 + 15]}[side]
                            d.rectangle(edge, fill=shade(base, 0.45))
            elif name == "nature":
                _nature(d, x0, y0, pal["nature"], nature_kind, r, at(x, y - 1) == "T")
            elif name == "cliff":
                d.line([x0 + 4 + r % 6, y0 + 3, x0 + 3 + r % 6, y0 + 12], fill=shade(base, -0.18))
                if at(x, y - 1) != "#":
                    d.rectangle([x0, y0, x0 + 15, y0 + 3], fill=shade(base, 0.3))
                if at(x, y + 1) not in ("#", None):
                    d.rectangle([x0, y0 + 12, x0 + 15, y0 + 15], fill=shade(base, -0.3))
            elif name == "ledge":
                band = {"v": [x0, y0 + 10, x0 + 15, y0 + 15], "^": [x0, y0, x0 + 15, y0 + 5],
                        "<": [x0, y0, x0 + 5, y0 + 15], ">": [x0 + 10, y0, x0 + 15, y0 + 15]}[ch]
                d.rectangle(band, fill=pal["ledge"])
                d.rectangle(band, outline=shade(pal["ledge"], -0.3))
            elif name == "bridge":
                for k in range(0, 16, 4):
                    d.line([x0, y0 + k, x0 + 15, y0 + k], fill=shade(base, -0.2))
            elif name == "ladder":
                d.rectangle(box, fill=pal["ground"])
                d.line([x0 + 3, y0, x0 + 3, y0 + 15], fill=pal["ladder"], width=2)
                d.line([x0 + 12, y0, x0 + 12, y0 + 15], fill=pal["ladder"], width=2)
                for k in range(2, 16, 4):
                    d.line([x0 + 3, y0 + k, x0 + 12, y0 + k], fill=pal["ladder"], width=2)
            elif name == "floor":
                d.line([x0, y0 + 15, x0 + 15, y0 + 15], fill=shade(base, -0.06))
                d.line([x0 + 15, y0, x0 + 15, y0 + 15], fill=shade(base, -0.06))
            elif name == "wall":
                if at(x, y + 1) == "_":
                    d.rectangle([x0, y0 + 6, x0 + 15, y0 + 15], fill=shade(base, 0.25))
                    d.line([x0, y0 + 6, x0 + 15, y0 + 6], fill=shade(base, -0.3))
            elif name == "blocked":
                for k in range(-16, 16, 5):
                    d.line([x0 + k, y0 + 15, x0 + k + 15, y0], fill=shade(base, -0.2))


def _nature(d, x0, y0, col, kind, r, stacked):
    dark, light = shade(col, -0.35), shade(col, 0.25)
    if kind == "tree":
        d.ellipse([x0 - 2, y0 - 3, x0 + 17, y0 + 15], fill=col, outline=dark)
        d.ellipse([x0 + 3, y0, x0 + 9, y0 + 5], fill=light)
    elif kind == "rock":
        pts = [(x0 + 1, y0 + 12), (x0 + 3, y0 + 3 + r % 3), (x0 + 8, y0 + 1), (x0 + 13, y0 + 4), (x0 + 15, y0 + 13), (x0 + 8, y0 + 15)]
        d.polygon(pts, fill=col, outline=dark)
        d.line([(x0 + 4, y0 + 5), (x0 + 8, y0 + 3)], fill=light, width=2)
    elif kind == "ice":
        d.polygon([(x0 + 2, y0 + 15), (x0 + 5, y0 + 2), (x0 + 9, y0 + 8), (x0 + 12, y0 + 1), (x0 + 15, y0 + 15)], fill=col, outline=dark)
        d.line([(x0 + 5, y0 + 3), (x0 + 6, y0 + 10)], fill=(255, 255, 255))
    elif kind == "fungus":
        d.rectangle([x0 + 6, y0 + 7, x0 + 9, y0 + 15], fill=shade(col, 0.5))
        d.ellipse([x0 - 1, y0 - 1, x0 + 16, y0 + 9], fill=col, outline=dark)
        d.ellipse([x0 + 3, y0 + 1, x0 + 6, y0 + 3], fill=light)
    elif kind == "cloud":
        d.ellipse([x0 - 1, y0 + 2, x0 + 16, y0 + 15], fill=col)
        d.ellipse([x0 + 3, y0 + 3, x0 + 9, y0 + 7], fill=light)
    else:
        d.ellipse([x0, y0, x0 + 15, y0 + 15], fill=col, outline=dark)


# ---------------------------------------------------------------------------------------------- buildings
# Buildings live in build.py (the 3/4 top-down projection, footprints and building types).


# ---------------------------------------------------------------------------------------------- props
def prop(d, p, st):
    (cx, cy), (cw, ch) = p["at"], p.get("size", [1, 1])
    x0, y0, W, H = cx * C, cy * C, cw * C, ch * C
    x1, y1 = x0 + W - 1, y0 + H - 1
    f, t = st["fill"], st["trim"]
    out = shade(f, -0.45)
    k, form = st["kind"], st.get("form")
    if k == "tree":
        trunk = t
        g = 4 if st.get("big") else 0
        if form == "bare":
            mx = (x0 + x1) // 2
            d.line([mx, y1, mx, y0 + 4], fill=f, width=3)
            d.line([mx, y0 + H // 2, x0 + 2, y0 + 3], fill=f, width=2)
            d.line([mx, y0 + H // 3, x1 - 2, y0 + 1], fill=f, width=2)
        else:
            d.rectangle([(x0 + x1) // 2 - 2 - g // 2, y1 - H // 3, (x0 + x1) // 2 + 2 + g // 2, y1], fill=trunk)
            blobs = 3 if form == "gnarl" else 1
            for i in range(blobs):
                ox = (i - blobs // 2) * W // 3
                d.ellipse([x0 - g + ox // 2, y0 - g - 4 + i * 2, x1 + g + ox // 2, y1 - H // 4], fill=shade(f, -0.08 * i), outline=out)
            d.ellipse([x0 + W // 4, y0 - g, x0 + W // 2, y0 + H // 5], fill=shade(f, 0.25))
    elif k == "pine":
        mx = (x0 + x1) // 2
        for i in range(3):
            ty = y0 - 4 + i * H // 4
            hw = W // 2 - 1 - (2 - i) * 2
            d.polygon([(mx, ty), (mx - hw - 3, ty + H // 3), (mx + hw + 3, ty + H // 3)], fill=f, outline=out)
            d.line([(mx - 2, ty + 2), (mx, ty)], fill=t, width=2)
        d.rectangle([mx - 1, y1 - 3, mx + 1, y1], fill=(90, 60, 40))
    elif k == "rock":
        if st.get("tall"):
            d.polygon([(x0 + 2, y1), (x0 + W * 0.3, y0 - 6), (x0 + W * 0.6, y0 - 2), (x1 - 1, y1)], fill=f, outline=out)
            d.line([(x0 + W * 0.3, y0 - 4), (x0 + W * 0.25, y1 - 4)], fill=shade(f, 0.3), width=2)
        else:
            d.polygon([(x0 + 1, y1 - 2), (x0 + 3, y0 + 4), (x0 + W * 0.5, y0 + 1), (x1 - 2, y0 + 5), (x1, y1 - 3), (x0 + W * 0.5, y1)],
                      fill=f, outline=out)
            d.line([(x0 + 5, y0 + 6), (x0 + W * 0.5, y0 + 3)], fill=shade(f, 0.3), width=2)
    elif k == "pole":
        for i in range(cw):
            mx = x0 + i * C + C // 2
            d.rectangle([mx - 2, y0 + 3, mx + 1, y1], fill=f, outline=out)
            d.ellipse([mx - 4, y0, mx + 3, y0 + 6], fill=shade(f, 0.2), outline=t)
    elif k == "stack":
        n = st.get("count") or 2
        for i in range(cw * n):
            for j in range(ch * n):
                s = C // n
                bx, by = x0 + i * s + 1, y0 + j * s + 1
                d.rectangle([bx, by, bx + s - 3, by + s - 3], fill=f, outline=t)
                d.line([bx, by, bx + s - 3, by + s - 3], fill=shade(f, -0.2))
    elif k == "tank":
        for i in range(cw):
            for j in range(ch):
                bx, by = x0 + i * C, y0 + j * C
                d.rectangle([bx + 2, by + 4, bx + 13, by + 15], fill=f, outline=t)
                d.ellipse([bx + 2, by + 1, bx + 13, by + 7], fill=shade(f, 0.25), outline=t)
    elif k == "craft":
        _craft(d, x0, y0, x1, y1, f, t, form)
    elif k == "bones":
        mx = (x0 + x1) // 2
        d.line([x0 + 2, (y0 + y1) // 2, x1 - 2, (y0 + y1) // 2], fill=f, width=3)
        for i in range(x0 + 4, x1 - 2, 6):
            d.arc([i - 3, y0 + 2, i + 5, y1 - 2], 180, 360, fill=f, width=2)
        d.ellipse([x1 - 9, (y0 + y1) // 2 - 4, x1, (y0 + y1) // 2 + 4], fill=f, outline=shade(f, -0.3))
    elif k == "disc":
        # flat on the ground, so seen at the game's angle: an oval about 0.65 as deep as it is wide
        y0 = max(y0, y1 - int(W * 0.65))
        H = y1 - y0
        d.ellipse([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=f, outline=st["ring"], width=2)
        if st.get("mark") == "H":
            mx, my = (x0 + x1) // 2, (y0 + y1) // 2
            d.text((mx - 4, my - 7), "H", font=F_BIG, fill=st["ring"])
        elif st.get("mark") == "pit":
            d.ellipse([x0 + W // 4, y0 + H // 4, x1 - W // 4, y1 - H // 4], fill=shade(f, -0.6))
        else:
            d.arc([x0 + W // 5, y0 + H // 5, x1 - W // 5, y1 - H // 5], 200, 330, fill=shade(f, 0.35), width=2)
    elif k == "wreck":
        pts = [(x0 + 1, y1 - 3), (x0 + W * 0.2, y0 + 4), (x0 + W * 0.45, y0 + 8), (x0 + W * 0.6, y0 + 1), (x1 - 2, y0 + H * 0.5), (x1, y1 - 1)]
        d.polygon(pts, fill=f, outline=out)
        d.line([(x0 + W * 0.3, y0 + 6), (x0 + W * 0.55, y1 - 3)], fill=out, width=2)
        d.line([(x0 + W * 0.6, y0 + 3), (x1 - 4, y1 - 4)], fill=shade(f, 0.25))
    elif k == "plant":
        for i in range(max(3, cw * ch * 3)):
            rr = _h(cx, cy, i)
            px, py = x0 + rr % max(W - 4, 1), y0 + (rr >> 8) % max(H - 4, 1)
            d.ellipse([px, py, px + 5, py + 5], fill=shade(f, (rr % 3 - 1) * 0.15), outline=shade(f, -0.35))
    elif k == "fungus":
        g = 4 if st.get("big") else 0
        mx = (x0 + x1) // 2
        d.rectangle([mx - 2 - g // 2, y0 + H // 3, mx + 2 + g // 2, y1], fill=t)
        d.ellipse([x0 - g, y0 - g - 2, x1 + g, y0 + H // 2], fill=f, outline=out)
        d.ellipse([x0 + W // 4, y0 - g, x0 + W // 2, y0 + H // 6], fill=shade(f, 0.35))
    elif k == "stones":
        if form == "tents":
            for i in range(cw):
                bx = x0 + i * C
                d.polygon([(bx + 1, y1), (bx + C // 2, y0 + 2), (bx + C - 2, y1)], fill=f, outline=t)
        else:
            for i in range(cw * 2):
                bx = x0 + i * (C // 2)
                d.rectangle([bx + 1, y0 + 1, bx + C // 2 - 2, y1], fill=f, outline=shade(f, -0.4))
    else:   # slab and anything unknown
        d.rectangle([x0 + 1, y0 + 2, x1 - 1, y1 - 1], fill=f, outline=out)
        d.rectangle([x0 + 1, y0 + 2, x1 - 1, y0 + 5], fill=shade(f, 0.25))
        if form == "awning":
            for i in range(x0 + 1, x1, 6):
                d.rectangle([i, y0 + 2, i + 2, y0 + H // 2], fill=(240, 230, 210))
        elif form == "log":
            d.ellipse([x1 - 7, y0 + 2, x1 - 1, y1 - 1], fill=shade(f, 0.3), outline=out)
        elif form in ("dock", "steps", "grate"):
            step = 4 if form != "grate" else 3
            for i in range(y0 + 4, y1, step):
                d.line([x0 + 2, i, x1 - 2, i], fill=t)
        elif t != f:
            d.rectangle([x0 + 3, y0 + 7, x1 - 3, y0 + 9], fill=t)
    if st.get("unknown"):
        d.rectangle([x0, y0, x1, y1], outline=(255, 0, 255))


def _craft(d, x0, y0, x1, y1, f, t, form):
    W, H = x1 - x0, y1 - y0
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    out = shade(f, -0.45)
    if form == "xwing":
        d.rectangle([x0 + 1, my - 2, x1 - 1, my + 2], fill=f, outline=out)
        d.line([x0 + 3, y0 + 2, x1 - 3, y1 - 2], fill=t, width=3)
        d.line([x0 + 3, y1 - 2, x1 - 3, y0 + 2], fill=t, width=3)
        d.ellipse([mx - 4, y0 + 1, mx + 4, y1 - 1], fill=f, outline=out)
    elif form == "tie":
        for i in range(0, max(1, W // 24)):
            cx = x0 + 12 + i * 24
            d.rectangle([cx - 10, y0 + 2, cx - 7, y1 - 2], fill=t)
            d.rectangle([cx + 7, y0 + 2, cx + 10, y1 - 2], fill=t)
            d.ellipse([cx - 5, my - 5, cx + 5, my + 5], fill=f, outline=out)
    elif form == "shuttle":
        d.polygon([(mx, y0 + 1), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)], fill=f, outline=out)
        d.line([mx, y0 + 2, mx, y1 - 3], fill=t, width=2)
    elif form == "pod":
        d.ellipse([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=f, outline=out)
    elif form == "glider":
        d.polygon([(mx, y0 + 2), (x0 + 1, y1 - 2), (x1 - 1, y1 - 2)], fill=f, outline=t)
    elif form == "podracer":
        d.rectangle([x0 + 2, y0 + 3, x0 + W // 3, y0 + 7], fill=f, outline=out)
        d.rectangle([x0 + 2, y1 - 7, x0 + W // 3, y1 - 3], fill=f, outline=out)
        d.ellipse([x1 - W // 3, my - 4, x1 - 2, my + 4], fill=t, outline=out)
    else:   # speeder, freighter
        d.ellipse([x0 + 1, y0 + 2, x1 - 1, y1 - 2], fill=f, outline=out)
        d.ellipse([mx - W // 6, my - H // 4, mx + W // 6, my + H // 6], fill=shade(f, 0.25), outline=t)
        if form == "freighter":
            d.ellipse([x1 - W // 4, my - 3, x1 - W // 8, my + 3], fill=t)


# ---------------------------------------------------------------------------------------------- sprites
def person(d, p, roles):
    x, y = p["at"]
    x0, y0 = x * C, y * C
    role = p.get("role", "npc")
    r = roles.get(role) or roles.get("npc")
    if "ball" in r:
        col = tuple(int(r["ball"][i:i + 2], 16) for i in (1, 3, 5))
        d.ellipse([x0 + 4, y0 + 5, x0 + 11, y0 + 12], fill=col, outline=(40, 30, 30))
        d.line([x0 + 4, y0 + 8, x0 + 11, y0 + 8], fill=(40, 30, 30))
        return
    body = tuple(int(r["body"][i:i + 2], 16) for i in (1, 3, 5))
    ring = tuple(int(r["ring"][i:i + 2], 16) for i in (1, 3, 5))
    d.ellipse([x0 + 3, y0 + 13, x0 + 12, y0 + 16], fill=(0, 0, 0, 70))
    d.rectangle([x0 + 4, y0 + 7, x0 + 11, y0 + 14], fill=body, outline=ring)
    d.ellipse([x0 + 4, y0 + 0, x0 + 11, y0 + 7], fill=shade(body, 0.4), outline=ring)


def sign(d, s):
    x, y = s["at"]
    x0, y0 = x * C, y * C
    d.rectangle([x0 + 7, y0 + 8, x0 + 8, y0 + 15], fill=(110, 80, 50))
    d.rectangle([x0 + 2, y0 + 2, x0 + 13, y0 + 9], fill=(200, 160, 110), outline=(90, 60, 40))
    d.line([x0 + 4, y0 + 5, x0 + 11, y0 + 5], fill=(110, 80, 50))


def warp(d, w, grid):
    x, y = w["at"]
    x0, y0 = x * C, y * C
    ch = grid[y][x] if 0 <= y < len(grid) and 0 <= x < len(grid[0]) else "."
    above = grid[y - 1][x] if y > 0 else None
    if ch in "#|" or above in ("#", "|"):
        d.chord([x0 + 1, y0 + 1, x0 + 14, y0 + 22], 180, 360, fill=(26, 22, 22))
        d.rectangle([x0 + 1, y0 + 9, x0 + 14, y0 + 15], fill=(26, 22, 22))
    else:
        d.rectangle([x0 + 2, y0 + 3, x0 + 13, y0 + 13], fill=(40, 34, 34), outline=(255, 79, 191))


def exits(d, doc, W, H):
    for e in doc.get("exits") or []:
        for c in e.get("cells") or []:
            x, y = {"north": (c, 0), "south": (c, H - 1), "west": (0, c), "east": (W - 1, c)}[e["edge"]]
            x0, y0 = x * C + 8, y * C + 8
            a = {"north": [(x0, y0 - 6), (x0 - 4, y0), (x0 + 4, y0)], "south": [(x0, y0 + 6), (x0 - 4, y0), (x0 + 4, y0)],
                 "west": [(x0 - 6, y0), (x0, y0 - 4), (x0, y0 + 4)], "east": [(x0 + 6, y0), (x0, y0 - 4), (x0, y0 + 4)]}[e["edge"]]
            d.polygon(a, fill=(255, 255, 255, 170))


def label(d, text, cx, cy):
    tw = d.textlength(text, font=F)
    d.rectangle([cx - tw / 2 - 2, cy - 7, cx + tw / 2 + 2, cy + 7], fill=(0, 0, 0, 150))
    d.text((cx - tw / 2, cy - 6), text, font=F, fill=(255, 255, 255))


# ---------------------------------------------------------------------------------------------- an area
WATER_KIND = {"MUSTAFAR": "lava", "ASTEROID FIELD": "void"}


def area(doc, styles, labels=True, grey=False):
    grid = [r for r in (doc.get("grid") or "").splitlines() if r]
    W = max(len(r) for r in grid)
    grid = [r.ljust(W, "x") for r in grid]
    H = len(grid)
    planet = doc.get("planet", "")
    pal, nature_kind = styles.terrain(planet)
    img = Image.new("RGB", (W * C, H * C), pal["ground"])
    d = ImageDraw.Draw(img, "RGBA")
    terrain(d, grid, pal, nature_kind, WATER_KIND.get(planet, "water"))
    exits(d, doc, W, H)
    # draw back to front so lower pieces overlap higher ones, like the game
    pieces = [("building", b) for b in doc.get("buildings") or []] + [("prop", p) for p in doc.get("props") or []]
    pieces.sort(key=lambda kp: kp[1]["at"][1] + kp[1].get("size", [1, 1])[1])
    for kind, o in pieces:
        seed = _h(zlib.crc32(o.get("art", "").encode()), o["at"][0], o["at"][1])
        st = styles.shape(o.get("art", ""), planet, kind, seed)
        if kind == "building" or st.get("build"):      # props with a `build` are 3D models too
            st["ground"] = pal["ground"]
            st.setdefault("cliff", pal["cliff"])
            _build.building(img, o, st, seed, grey)
        else:
            prop(d, o, st)
    for w in doc.get("warps") or []:
        warp(d, w, grid)
    for s in doc.get("signs") or []:
        sign(d, s)
    for p in sorted(doc.get("people") or [], key=lambda p: p["at"][1]):
        person(d, p, styles.roles)
    if labels:
        for b in doc.get("buildings") or []:
            st = styles.shape(b.get("art", ""), planet, "building")
            name = b.get("name") or st.get("label") or ""
            if len(name) > 18:
                name = name[:17] + "."
            (cx, cy), (cw, ch) = b["at"], b["size"]
            label(d, name, (cx + cw / 2) * C, cy * C + ch * C * 0.35)
    return img

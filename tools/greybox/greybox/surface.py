"""Liquid and open surfaces in relief: what a `~` cell is on each planet, and how its banks look.

Phase 1 marks every liquid or open drop with `~`. The planet decides what it is (SURFACE), and a big
connected body of plain water becomes sea. Each kind has its own drop below the bank (how far below
the ground it sits, in px) and its own simple marks, all from the cell's base colour:
  - water: a 3 px bank, two light ripples per cell, a light edge where it meets land,
  - sea: as water, deeper colour, wave crests in rows and white foam along the shore,
  - swamp: a 2 px bank, murky, scum patches and reed stubs, no ripples,
  - lava: a 3 px dark crust bank, bright core with darker crust plates, a glow on the bank above,
  - ice: level with the ground (no bank), pale sheet, crack lines, a light rim,
  - cloud: a 10 px drop, soft puffs (Bespin's cloud sea),
  - void: a 12 px drop into black with stars (the asteroid field).
"""
from .style import shade

C = 16
SURFACE = {"MUSTAFAR": "lava", "ASTEROID FIELD": "void", "BESPIN": "cloud", "HOTH": "ice", "ILUM": "ice",
           "DAGOBAH": "swamp", "KAMINO": "sea"}
DROP = {"water": 3, "sea": 3, "swamp": 2, "lava": 3, "ice": 0, "cloud": 10, "void": 12}
SEA_CELLS = 200          # a connected body of water this big is sea


def _h(*v):
    x = 2166136261
    for n in v:
        x = ((x ^ (n & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    x ^= x >> 13
    return x


def bodies(grid):
    """Size of the connected `~` body each water cell belongs to."""
    H, W = len(grid), len(grid[0])
    size = {}
    seen = set()
    for y in range(H):
        for x in range(W):
            if grid[y][x] != "~" or (x, y) in seen:
                continue
            stack, cells = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                cells.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < W and 0 <= ny < H and grid[ny][nx] == "~" and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            for c in cells:
                size[c] = len(cells)
    return size


def kind_for(planet, body_size):
    k = SURFACE.get(planet, "water")
    if k == "water" and body_size >= SEA_CELLS:
        return "sea"
    return k


def draw(d, grid, pal, planet, grey=False):
    """Draw every `~` cell of a relief area as its surface, with banks. Call after the ground is drawn."""
    H, W = len(grid), len(grid[0])
    size = bodies(grid)
    base0 = (120, 132, 150) if grey else pal["water"]
    ground = (196, 196, 196) if grey else pal["ground"]

    def liquid(x, y):
        return 0 <= x < W and 0 <= y < H and grid[y][x] == "~"

    for (x, y), n in size.items():
        k = kind_for(planet, n)
        base = shade(base0, -0.12) if k == "sea" else base0
        x0, y0 = x * C, y * C
        d.rectangle([x0, y0, x0 + C - 1, y0 + C - 1], fill=base)
        r = _h(x, y)
        if k in ("water", "sea"):
            light = shade(base, 0.28)
            off = (y % 2) * 4
            d.line([(x0 + 1 + off, y0 + 6), (x0 + 4 + off, y0 + 5), (x0 + 7 + off, y0 + 6)], fill=light)
            if k == "sea" or r % 2:
                d.line([(x0 + 7 - off, y0 + 12), (x0 + 10 - off, y0 + 11), (x0 + 13 - off, y0 + 12)], fill=light)
        elif k == "swamp":
            if r % 3 == 0:
                d.ellipse([x0 + r % 8, y0 + (r >> 4) % 8, x0 + r % 8 + 6, y0 + (r >> 4) % 8 + 3], fill=shade(base, 0.18))
            if r % 5 == 0:
                for i in range(3):
                    xx = x0 + 3 + i * 3 + (r >> 8) % 3
                    d.line([xx, y0 + 9, xx, y0 + 13], fill=shade(pal.get("nature", base), -0.1))
        elif k == "lava":
            d.rectangle([x0, y0, x0 + C - 1, y0 + C - 1], fill=shade(base, 0.12))
            if r % 5 == 0:                       # a few dark crust plates drifting on the flow
                px, py = x0 + r % 5, y0 + (r >> 8) % 8
                d.rounded_rectangle([px, py, px + 10, py + 5], 2, fill=shade(base, -0.3))
            elif r % 5 == 1:                     # a bright bubble
                d.ellipse([x0 + 6, y0 + 6, x0 + 9, y0 + 8], fill=shade(base, 0.4))
        elif k == "ice":
            d.rectangle([x0, y0, x0 + C - 1, y0 + C - 1], fill=shade(base, 0.25))
            if r % 5 == 0:                       # an occasional long crack
                d.line([x0 + r % 6, y0 + (r >> 8) % 6, x0 + r % 6 + 10, y0 + (r >> 8) % 6 + 7], fill=shade(base, 0.05))
        elif k == "cloud":
            for i in range(2):
                rr = _h(x, y, i)
                d.ellipse([x0 + rr % 9 - 2, y0 + (rr >> 8) % 9 - 1, x0 + rr % 9 + 9, y0 + (rr >> 8) % 9 + 6],
                          fill=shade(base, 0.22))
        elif k == "void":
            d.rectangle([x0, y0, x0 + C - 1, y0 + C - 1], fill=(14, 14, 26))
            if r % 4 == 0:
                d.point((x0 + r % 16, y0 + (r >> 8) % 16), fill=(230, 230, 240))
        # banks: the drop face on the north edge, a rim on the other edges
        drop = DROP[k]
        if not liquid(x, y - 1) and y > 0 and drop:
            face = shade(ground, -0.3) if k != "lava" else shade(base0, -0.6)
            d.rectangle([x0, y0, x0 + C - 1, y0 + min(drop, C) - 1], fill=face)
            if k in ("cloud", "void"):
                d.rectangle([x0, y0 + drop, x0 + C - 1, y0 + drop + 2], fill=(0, 0, 0, 60))
        for nx, ny, edge in ((x - 1, y, "w"), (x + 1, y, "e"), (x, y + 1, "s"), (x, y - 1, "n")):
            if liquid(nx, ny) or not (0 <= nx < W and 0 <= ny < H):
                continue
            if edge == "n" and drop:
                continue
            box = {"w": [x0, y0, x0 + 1, y0 + C - 1], "e": [x0 + C - 2, y0, x0 + C - 1, y0 + C - 1],
                   "s": [x0, y0 + C - 2, x0 + C - 1, y0 + C - 1], "n": [x0, y0, x0 + C - 1, y0 + 1]}[edge]
            rim = {"sea": (240, 244, 246), "lava": shade(base0, -0.6), "ice": shade(base, 0.5),
                   "void": shade(ground, -0.4), "cloud": shade(ground, -0.25)}.get(k, shade(base, 0.45))
            d.rectangle(box, fill=rim)
        # lava lights the ground above it
        if k == "lava" and not liquid(x, y - 1) and y > 0:
            d.rectangle([x0, y0 - 5, x0 + C - 1, y0 - 1], fill=(255, 140, 40, 60))

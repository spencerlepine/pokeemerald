"""An interior as a greybox room: the vanilla layout's walls and floor, drawn the way the game shows a room.

The grid of an interior area keeps the vanilla shape: `#` is anything a player cannot walk on, `.` is floor.
The `#` cells joined to the top edge are the walls (the back wall and the side walls); every other `#` blob is
a block of furniture whose real shape is not decided yet, drawn as a low greybox box so the room reads in 3D.

Walls follow the game's rule: a wall shows its face on the two cells above the floor (a top band and a
panel), and a ceiling strip above that. The floor row under a face is in shadow. Doors on the wall are
arches, doors on the floor are mats; stairs and ladders are warps too.
"""
from PIL import Image, ImageDraw

from . import build as _build
from .draw import C, person, warp, label
from .style import shade


def _flood_walls(grid):
    H, W = len(grid), len(grid[0])
    seen = set()
    stack = [(x, 0) for x in range(W) if grid[0][x] == "#"]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < W and 0 <= y < H) or grid[y][x] != "#":
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return seen


def _blocks(grid, walls):
    """Greedy rectangles over the `#` cells that are not walls."""
    H, W = len(grid), len(grid[0])
    free = {(x, y) for y in range(H) for x in range(W) if grid[y][x] == "#" and (x, y) not in walls}
    out = []
    for y in range(H):
        for x in range(W):
            if (x, y) not in free:
                continue
            w = 1
            while (x + w, y) in free:
                w += 1
            h = 1
            while all((x + i, y + h) in free for i in range(w)):
                h += 1
            for j in range(h):
                for i in range(w):
                    free.discard((x + i, y + j))
            out.append((x, y, w, h))
    return out


def colours(styles, planet, grey):
    pal, _ = styles.terrain(planet)
    mat = styles.material(planet)
    if grey:
        wall, floor, trim = (150, 150, 150), (200, 200, 200), (104, 104, 104)
    else:
        wall = mat["wall"]
        floor = pal.get("floor") or shade(pal.get("path", pal["ground"]), -0.04)
        trim = mat["trim"]
    return {"wall": wall, "floor": floor, "trim": trim, "ceiling": shade(trim, -0.35), "band": shade(wall, -0.18),
            "line": shade(floor, -0.08), "shadow": shade(floor, -0.22), "ground": floor, "cliff": trim, "roof": wall}


def draw_room(d, grid, walls, col):
    H, W = len(grid), len(grid[0])

    def wall(x, y):
        return (x, y) in walls

    for y in range(H):
        for x in range(W):
            x0, y0 = x * C, y * C
            box = [x0, y0, x0 + C - 1, y0 + C - 1]
            if not wall(x, y):
                d.rectangle(box, fill=col["floor"])
                d.line([x0, y0, x0 + C - 1, y0], fill=col["line"])
                d.line([x0, y0, x0, y0 + C - 1], fill=col["line"])
                if wall(x, y - 1):
                    d.rectangle([x0, y0, x0 + C - 1, y0 + 3], fill=col["shadow"])
                continue
            s1, s2 = not wall(x, y + 1) and y + 1 < H, not wall(x, y + 2) and y + 2 < H
            if s1:                                   # lower panel
                d.rectangle(box, fill=col["wall"])
                d.rectangle([x0, y0 + 11, x0 + C - 1, y0 + C - 1], fill=col["band"])
                d.line([x0, y0, x0, y0 + C - 1], fill=col["band"])
            elif s2:                                 # top band of the face
                d.rectangle(box, fill=col["wall"])
                d.rectangle([x0, y0, x0 + C - 1, y0 + 2], fill=col["trim"])
                d.line([x0, y0, x0, y0 + C - 1], fill=col["band"])
            else:                                    # ceiling / wall top
                d.rectangle(box, fill=col["ceiling"])


def room(doc, styles, labels=True, grey=False):
    grid = [r for r in (doc.get("grid") or "").splitlines() if r]
    W = max(len(r) for r in grid)
    grid = [r.ljust(W, "#").replace("T", "#") for r in grid]     # plants and the like are furniture too
    H = len(grid)
    planet = doc.get("planet", "")
    col = colours(styles, planet, grey)
    img = Image.new("RGB", (W * C, H * C), col["floor"])
    d = ImageDraw.Draw(img, "RGBA")
    walls = _flood_walls(grid)
    draw_room(d, grid, walls, col)
    pieces = [("block", {"at": [x, y], "size": [w, h]}) for x, y, w, h in _blocks(grid, walls)]
    pieces += [("prop", p) for p in doc.get("props") or []]
    pieces.sort(key=lambda kp: kp[1]["at"][1] + kp[1].get("size", [1, 1])[1])
    for kind, o in pieces:
        if kind == "block":
            st = dict(col, build="r-block")
            _build.building(img, o, st, 1, grey)
        else:
            st = styles.shape(o.get("art", ""), planet, "prop", 1)
            st.update(ground=col["floor"], cliff=col["trim"])
            _build.building(img, o, st, 1, grey)
    for w in doc.get("warps") or []:
        warp(d, w, grid)
    for p in sorted(doc.get("people") or [], key=lambda p: p["at"][1]):
        person(d, p, styles.roles)
    if labels:
        label(d, doc.get("name", doc["id"]), W * C / 2, 8)
    return img

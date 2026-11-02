"""Dungeon areas (caves, mines, ship decks) drawn as enclosed spaces, the way the game shows a cave.

A cave grid is mostly rock. Outdoors, rock is a plateau the player can see the top of; in a cave the rock
is the cave itself, so:
  - every rock cell that does not touch the floor is the dark mass between chambers (no detail, a dark margin),
  - a rock run above a floor cell shows a tall wall: two cells of face (one if the run is a single cell),
    lit at the top, darker at the foot, with a shadow cast on the floor in front of it,
  - rock beside or below the floor gets a lit rim, so every chamber reads as a hole cut into the rock,
  - the floor is the planet's ground darkened, with pebbles; water is dark and still,
  - `T` cells in a cave are stalagmites (the kit's shard or boulder by planet), ledges drop one level.
Station decks (grids drawn with `|` walls and `_` floor, the Death Star) use the room shell instead.
`python3 -m greybox terrain <area-id>` picks this mode for every area of kind `dungeon`.
"""
from .style import shade

C = 16
ROCK = set("#x")


def _h(*v):
    x = 2166136261
    for n in v:
        x = ((x ^ (n & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return x


def colours(pal, grey):
    if grey:
        ground, cliff = (150, 150, 150), (120, 120, 120)
    else:
        ground, cliff = pal["ground"], pal["cliff"]
    return {"floor": shade(ground, -0.32), "pebble": shade(ground, -0.45), "face": shade(cliff, -0.08),
            "face_lo": shade(cliff, -0.3), "rim": shade(cliff, 0.25), "mass": shade(cliff, -0.72),
            "line": shade(cliff, -0.4), "water": shade(pal.get("water", (60, 80, 110)), -0.45)}


def faces(grid):
    """Per cell: k for the k-th face cell (0 = top) of n, as (k, n), or None for mass / floor."""
    H, W = len(grid), len(grid[0])
    out = [[None] * W for _ in range(H)]
    for x in range(W):
        for y in range(H):
            if grid[y][x] in ROCK and (y + 1 < H and grid[y + 1][x] not in ROCK):
                a = y
                while a - 1 >= 0 and grid[a - 1][x] in ROCK:
                    a -= 1
                n = min(2, y - a + 1)
                for k in range(n):
                    out[y - n + 1 + k][x] = (k, n)
    return out


def draw(d, grid, pal, grey=False, planet=""):
    """Draw a cave in relief on the game grid. Returns the `T` cells to model as stalagmites."""
    H, W = len(grid), len(grid[0])
    col = colours(pal, grey)
    fc = faces(grid)

    def rock(x, y):
        return not (0 <= x < W and 0 <= y < H) or grid[y][x] in ROCK

    for y in range(H):
        for x in range(W):
            x0, y0 = x * C, y * C
            box = [x0, y0, x0 + C - 1, y0 + C - 1]
            ch = grid[y][x]
            if not rock(x, y):
                d.rectangle(box, fill=col["floor"])
                r = _h(x, y)
                if ch != "~":
                    for k in range(2):
                        rr = _h(x, y, k)
                        d.point((x0 + rr % 16, y0 + (rr >> 8) % 16), fill=col["pebble"])
                else:
                    d.line([x0 + r % 8, y0 + 6, x0 + r % 8 + 5, y0 + 6], fill=shade(col["water"], 0.25))
                if ch in "v^<>":
                    d.rectangle([x0, y0 + C - 4, x0 + C - 1, y0 + C - 1], fill=col["face"])
                    d.line([x0, y0 + C - 4, x0 + C - 1, y0 + C - 4], fill=col["rim"])
                if rock(x, y - 1):                      # the wall's shadow on the floor in front of it
                    d.rectangle([x0, y0, x0 + C - 1, y0 + 4], fill=(0, 0, 0, 70))
                if rock(x - 1, y):
                    d.rectangle([x0, y0, x0 + 3, y0 + C - 1], fill=(0, 0, 0, 45))
                continue
            f = fc[y][x]
            if f is None:
                d.rectangle(box, fill=col["mass"])
            else:
                k, n = f
                d.rectangle(box, fill=col["face"] if k < n - 1 or n == 1 else col["face_lo"])
                for z in (5, 11):
                    j = _h(x, y, z) % 3
                    d.line([x0, y0 + z + j - 1, x0 + C - 1, y0 + z + _h(x + 1, y, z) % 3 - 1], fill=col["line"])
                if k == 0:
                    d.rectangle([x0, y0, x0 + C - 1, y0 + 1], fill=col["rim"])
            # a lit rim wherever the rock mass meets the floor on its north, east or west side
            if f is None or f[0] == 0:
                if not rock(x, y + 1) and f is None:
                    d.rectangle([x0, y0 + C - 3, x0 + C - 1, y0 + C - 1], fill=col["rim"])
            if not rock(x, y - 1):
                d.rectangle([x0, y0, x0 + C - 1, y0 + 2], fill=col["rim"])
            if not rock(x + 1, y):
                d.rectangle([x0 + C - 3, y0, x0 + C - 1, y0 + C - 1], fill=col["rim"])
            if not rock(x - 1, y):
                d.rectangle([x0, y0, x0 + 2, y0 + C - 1], fill=col["rim"])
    from . import surface
    surface.draw(d, grid, dict(pal, ground=col["floor"]), planet, grey)
    return [(x, y) for y in range(H) for x in range(W) if grid[y][x] == "T"]


def station(d, grid, styles, planet, grey=False):
    """A deck drawn with `|` walls and `_` floor: the room shell, walls joined to any edge."""
    from . import room
    g = [row.replace("|", "#").replace("_", ".") for row in grid]
    H, W = len(g), len(g[0])
    walls = {(x, y) for y in range(H) for x in range(W) if g[y][x] == "#"}
    room.draw_room(d, g, walls, room.colours(styles, planet, grey))

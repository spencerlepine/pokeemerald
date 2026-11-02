"""Heights for every phase-1 area, derived from its grid, and the area drawn in relief (greybox 3D).

Phase 1 only says which cells are rock (`#`, and `x` left over from imports), ledges (`v ^ < >`), water,
nature and walkable ground. This turns that into heights in the game's own tile convention (the map grid
stays the game grid, nothing is shifted):
  - a rock mass is a raised plateau. In each column, the southern cells of a run of rock are its cliff
    face and the rest is the rock top. The face is as many levels high as the run allows: a run of one or
    two cells is all face (a low wall), three to five gets one level of face, six or more gets two.
    A run that reaches the bottom edge of the map has no face (the mass goes on off the map).
  - where rock meets ground on its east or west side, the top gets a rock lip, and the ground east of
    rock gets the rock's shadow (the light comes from the south-west).
  - ledges are one level: a lit lip on the drop side.
  - water sits a little below its banks.
  - nature cells become kit models: pine for forest planets, boulders for rock, shards for ice, fungus.
`python3 -m mockup render ... --relief` draws areas this way. `heights(grid)` returns the derived levels.
"""
from .style import shade

C = 16
ROCK = set("#x")
NATURE_BUILD = {"tree": "pine", "rock": "boulder", "ice": "shard", "fungus": "fungus"}


def _h(*v):
    x = 2166136261
    for n in v:
        x = ((x ^ (n & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return x


def face_rows(n, at_bottom):
    """How many of the southern cells of a rock run of n cells are cliff face."""
    if at_bottom:
        return 0
    if n <= 2:
        return n
    return 1 if n <= 5 else 2


def analyse(grid):
    """Per cell: ('top', level) for rock tops, ('face', k, n) for the k-th of n face cells, or None."""
    H, W = len(grid), len(grid[0])
    info = [[None] * W for _ in range(H)]
    for x in range(W):
        y = 0
        while y < H:
            if grid[y][x] in ROCK:
                a = y
                while y < H and grid[y][x] in ROCK:
                    y += 1
                b = y - 1
                f = face_rows(b - a + 1, b == H - 1)
                lvl = max(f, 1)
                for yy in range(a, b + 1):
                    k = yy - (b - f + 1)
                    info[yy][x] = ("face", k, f) if k >= 0 else ("top", lvl)
            else:
                y += 1
    return info


def heights(grid):
    """The derived level of every cell: rock tops at their face height, faces stepping down, ground 0."""
    info = analyse(grid)
    out = []
    for y, row in enumerate(info):
        r = []
        for x, c in enumerate(row):
            if c is None:
                r.append(0)
            elif c[0] == "top":
                r.append(c[1])
            else:
                r.append(c[2] - c[1])
        out.append(r)
    return out


def draw(d, grid, pal, grey=False):
    """Draw the terrain of an area in relief, on the game grid. Returns the nature cells to model."""
    from .draw import terrain as flat
    H, W = len(grid), len(grid[0])
    info = analyse(grid)
    if grey:
        pal = dict(pal, ground=(196, 196, 196), path=(214, 214, 214), wild=(176, 176, 176),
                   water=(120, 132, 150), cliff=(150, 150, 150), ledge=(170, 170, 170), nature=(160, 160, 160))
    # everything that isn't rock or nature keeps the flat drawing (paths, grass, water, ledges, bridges)
    soft = ["".join("." if (ch in ROCK or ch == "T") else ch for ch in row) for row in grid]
    flat(d, soft, pal, "none", "water")
    rock_top = shade(pal["cliff"], 0.22)
    cliff = pal["cliff"]

    def rock(x, y):
        return 0 <= x < W and 0 <= y < H and grid[y][x] in ROCK

    for y in range(H):
        for x in range(W):
            c = info[y][x]
            x0, y0 = x * C, y * C
            if c is None:
                # shadow on open ground east of a rock mass
                if x > 0 and rock(x - 1, y) and grid[y][x] != "~":
                    d.rectangle([x0, y0, x0 + 8, y0 + C - 1], fill=(0, 0, 0, 45))
                # water sits below its banks: a bank face on its north edge
                if grid[y][x] == "~" and y > 0 and grid[y - 1][x] != "~":
                    d.rectangle([x0, y0, x0 + C - 1, y0 + 2], fill=shade(pal["ground"], -0.3))
                continue
            if c[0] == "top":
                d.rectangle([x0, y0, x0 + C - 1, y0 + C - 1], fill=rock_top)
                r = _h(x, y)
                d.point((x0 + r % 16, y0 + (r >> 8) % 16), fill=shade(rock_top, -0.1))
                d.line([x0 + (r >> 4) % 12, y0 + 4 + (r >> 12) % 8, x0 + (r >> 4) % 12 + 3, y0 + 4 + (r >> 12) % 8],
                       fill=shade(rock_top, -0.12))
                if not rock(x, y - 1) and y > 0:
                    d.line([x0, y0, x0 + C - 1, y0], fill=shade(rock_top, -0.35))
            else:
                _, k, n = c
                d.rectangle([x0, y0, x0 + C - 1, y0 + C - 1], fill=cliff)
                for z in (5, 11):
                    j = _h(x, y, z) % 3
                    d.line([x0, y0 + z + j - 1, x0 + C - 1, y0 + z + _h(x + 1, y, z) % 3 - 1], fill=shade(cliff, -0.16))
                xx = x0 + 3 + _h(x, y) % 10
                d.line([xx, y0, xx + 1, y0 + C - 1], fill=shade(cliff, -0.12))
                if k == 0:
                    d.line([x0, y0, x0 + C - 1, y0 + 1], fill=shade(cliff, 0.35))
                if k == n - 1:
                    d.line([x0, y0 + C - 1, x0 + C - 1, y0 + C - 1], fill=shade(cliff, -0.45))
            # a rock lip on a side that drops to open ground
            for nx, ex in ((x + 1, x0 + C - 3), (x - 1, x0)):
                if 0 <= nx < W and not rock(nx, y):
                    d.rectangle([ex, y0, ex + 2, y0 + C - 1], fill=cliff if c[0] == "top" else shade(cliff, -0.2))
                    d.line([ex + (2 if ex > x0 else 0), y0, ex + (2 if ex > x0 else 0), y0 + C - 1], fill=shade(cliff, -0.45))
    return [(x, y) for y in range(H) for x in range(W) if grid[y][x] == "T"]


def nature_pieces(cells, kind):
    """Kit models for nature cells: one piece per cell, its sprite box one cell taller for height."""
    b = NATURE_BUILD.get(kind)
    if not b:
        return []
    out = []
    for x, y in cells:
        if b == "boulder":
            out.append({"build": b, "at": [x, y], "size": [1, 1]})
        else:
            out.append({"build": b, "at": [x, y - 1], "size": [1, 2]})
    return out

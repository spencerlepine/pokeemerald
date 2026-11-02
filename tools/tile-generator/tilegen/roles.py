"""The tile vocabulary: every terrain kind is drawn from a fixed set of named roles.

A terrain item (water, cliff, wall, path, ledge...) is not one tile but a set. The set is the same for every
tileset and every planet, so the wiki can list every tile the game needs and mark the missing ones.

  - **Blob sets** (water, cliff, wall, path): a cell's role is read from which of its 4 cardinal neighbours
    are the same kind (out of bounds counts as the same), plus the diagonals for inner corners:
    `fill`, edges `n e s w`, outer corners `ne nw se sw`, inner corners `inner-ne inner-nw inner-se inner-sw`,
    one-cell strips `strip-h strip-v`, tips `tip-n tip-e tip-s tip-w`, and `single`.
    Walls add `top`: the row above a face (`s`), the way Emerald draws a wall as top + face.
  - **Ledges**: `fill`, `end-w`, `end-e` (south / north ledges), `end-n`, `end-s` (east / west ledges), `single`.
  - **Bridges**: `h` or `v`.
  - Everything else (grounds, wild grass, sand, ice, trees, structures): `fill`.
"""
from __future__ import annotations

BLOB = ["fill", "n", "e", "s", "w", "ne", "nw", "se", "sw", "inner-ne", "inner-nw", "inner-se", "inner-sw",
        "strip-h", "strip-v", "tip-n", "tip-e", "tip-s", "tip-w", "single"]
WALL = BLOB + ["top"]
LEDGE_H = ["fill", "end-w", "end-e", "single"]
LEDGE_V = ["fill", "end-n", "end-s", "single"]
BRIDGE = ["h", "v"]

# item name -> which role set it uses (prefix match for water-*, ground-path, ledge-*)
def role_set(item: str) -> list[str]:
    if item.startswith("water-") or item == "cliff" or item == "ground-path":
        return BLOB
    if item == "wall":
        return WALL
    if item in ("ledge-south", "ledge-north"):
        return LEDGE_H
    if item in ("ledge-east", "ledge-west"):
        return LEDGE_V
    if item == "bridge":
        return BRIDGE
    return ["fill"]


# the group a cell belongs to for "same neighbour" tests, by item
def group(item: str) -> str:
    if item.startswith("water-"):
        return "water"
    if item in ("cliff", "wall", "structure", "tree"):
        return "blocked"
    if item == "ground-path":
        return "path"
    if item.startswith("ledge-"):
        return item
    if item == "bridge":
        return "bridge"
    return "ground"


_BLOB_BY_MASK = {  # (n, e, s, w) same? -> role
    (1, 1, 1, 1): "fill",
    (0, 1, 1, 1): "n", (1, 0, 1, 1): "e", (1, 1, 0, 1): "s", (1, 1, 1, 0): "w",
    (0, 0, 1, 1): "ne", (0, 1, 1, 0): "nw", (1, 0, 0, 1): "se", (1, 1, 0, 0): "sw",
    (0, 1, 0, 1): "strip-h", (1, 0, 1, 0): "strip-v",
    (0, 0, 0, 1): "tip-e", (0, 1, 0, 0): "tip-w", (0, 0, 1, 0): "tip-n", (1, 0, 0, 0): "tip-s",
    (0, 0, 0, 0): "single",
}


def roles(items: list[list[str]]) -> list[list[str]]:
    """The role of every cell, from the item grid (one item name per cell)."""
    H, W = len(items), len(items[0])
    G = [[group(it) for it in row] for row in items]

    def same(y, x, g):
        return not (0 <= y < H and 0 <= x < W) or G[y][x] == g

    out = [["fill"] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            it = items[y][x]
            g = G[y][x]
            rs = role_set(it)
            if rs is BLOB or rs is WALL:
                m = (same(y - 1, x, g), same(y, x + 1, g), same(y + 1, x, g), same(y, x - 1, g))
                r = _BLOB_BY_MASK[tuple(int(v) for v in m)]
                if r == "fill":
                    if not same(y - 1, x + 1, g):
                        r = "inner-ne"
                    elif not same(y - 1, x - 1, g):
                        r = "inner-nw"
                    elif not same(y + 1, x + 1, g):
                        r = "inner-se"
                    elif not same(y + 1, x - 1, g):
                        r = "inner-sw"
                out[y][x] = r
            elif rs is LEDGE_H:
                l, rr = same(y, x - 1, g) and 0 <= x - 1, same(y, x + 1, g) and x + 1 < W
                out[y][x] = "fill" if l and rr else "end-w" if rr else "end-e" if l else "single"
            elif rs is LEDGE_V:
                u, d = same(y - 1, x, g) and 0 <= y - 1, same(y + 1, x, g) and y + 1 < H
                out[y][x] = "fill" if u and d else "end-n" if d else "end-s" if u else "single"
            elif rs is BRIDGE:
                out[y][x] = "h" if (0 <= x - 1 and G[y][x - 1] == g) or (x + 1 < W and G[y][x + 1] == g) else "v"
    # walls: the row above a face is the top
    for y in range(H):
        for x in range(W):
            if items[y][x] == "wall" and y + 1 < H and items[y + 1][x] == "wall" and out[y + 1][x] == "s" \
                    and out[y][x] in ("fill", "n", "inner-ne", "inner-nw", "strip-h"):
                out[y][x] = "top"
    return out

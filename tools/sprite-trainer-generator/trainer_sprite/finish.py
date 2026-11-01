"""Pixel-art finisher (D13): run after the rig layers, before `patches:`, so bold kitbashing
(erased hats, grafted heads, placed parts) still ends up as clean Emerald pixel art.

    front:
      repaint: {...}
      rig: {layers: [...]}
      finish:
        outline: K             # close the silhouette: light edge pixels -> the outline char
        selective: "hij"       # ...except these, which vanilla outlines with their own colour
        box: [x, y, w, h]      # optional: only here (default: the whole frame)
        pixel_perfect: true    # remove L-shaped corner doubles from outlines (1 px lines)
        strays: true           # delete floating single pixels, fill pinholes inside the figure

Every step is deterministic and only uses the spec's own palette.
"""
from __future__ import annotations

from . import palette as pal

N4 = ((0, -1), (1, 0), (0, 1), (-1, 0))


def _box(fin, w, h):
    b = fin.get("box")
    if not b:
        return 0, 0, w, h
    return int(b[0]), int(b[1]), int(b[2]), int(b[3])


def apply(g, fin: dict, legend: dict[str, int], colours, w: int, h: int) -> list[str]:
    """Clean `g` in place; returns a short log of what changed."""
    log = []
    bx, by, bw, bh = _box(fin, w, h)
    inside = lambda x, y: bx <= x < bx + bw and by <= y < by + bh  # noqa: E731
    K = legend.get(str(fin.get("outline", "K")))

    def dark(v):
        return v == K or pal.luma(colours[v]) <= 72

    if fin.get("strays", True):
        n = 0
        src = [list(r) for r in g]
        for y in range(h):
            for x in range(w):
                if not inside(x, y):
                    continue
                nb = [src[y + dy][x + dx] if 0 <= x + dx < w and 0 <= y + dy < h else 0 for dx, dy in N4]
                if src[y][x] and not any(nb):  # floating single pixel
                    diag = sum(1 for dx in (-1, 1) for dy in (-1, 1) if 0 <= x + dx < w and 0 <= y + dy < h and src[y + dy][x + dx])
                    if diag <= 1:
                        g[y][x] = 0
                        n += 1
                elif not src[y][x] and sum(1 for v in nb if v) >= 3 and y < h - 1:  # pinhole
                    vals = [v for v in nb if v]
                    g[y][x] = max(set(vals), key=vals.count)
                    n += 1
        if n:
            log.append(f"strays: {n} px")
    if K is not None and fin.get("outline"):
        sel = {legend[c] for c in str(fin.get("selective", "")) if c in legend}
        n = 0
        src = [list(r) for r in g]
        for y in range(h):
            for x in range(w):
                v = src[y][x]
                if not v or not inside(x, y) or dark(v) or v in sel:
                    continue
                # the frame bottom is a crop, not an edge (vanilla legs run off it)
                if any(0 <= x + dx < w and 0 <= y + dy < h and src[y + dy][x + dx] == 0 or not 0 <= x + dx < w or y + dy < 0
                       for dx, dy in N4):
                    g[y][x] = K
                    n += 1
        if n:
            log.append(f"outline: {n} px")
    if K is not None and fin.get("pixel_perfect"):
        n = 0
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if g[y][x] != K or not inside(x, y):
                    continue
                N, E, S, W = (g[y + dy][x + dx] == K for dx, dy in N4)
                for a, b, c, d, (ddx, ddy) in ((N, E, S, W, (1, -1)), (E, S, W, N, (1, 1)), (S, W, N, E, (-1, 1)), (W, N, E, S, (-1, -1))):
                    if a and b and not c and not d and g[y + ddy][x + ddx] != K:
                        # an L corner: the two neighbours already join diagonally
                        ox, oy = x - ddx, y - ddy  # the side away from the corner
                        g[y][x] = g[oy][ox] if g[oy][ox] != K else 0
                        n += 1
                        break
        if n:
            log.append(f"pixel-perfect: {n} corners")
    return log

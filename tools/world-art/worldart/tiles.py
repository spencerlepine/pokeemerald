"""What the GBA needs from a rendered object: 8x8 tiles, one 15-colour bank, and metatile layers.

An object image is a rectangle of 16x16 cells. Each cell becomes a metatile of two layers:
- rows inside the `footprint` (the bottom rows the player cannot enter) draw on the BOTTOM layer
  (the player is drawn over them; they are impassable);
- rows above it (crown, roof over open ground) draw on the TOP layer (the player walks behind), with
  the planet's ground under them (the ground is composited in at install, so here they stay transparent).

`budget()` counts the unique 8x8 tiles (after H/V flips) and the colours, the two numbers a tileset
runs out of: General has 512 tiles and 6 banks for the whole planet, a town secondary 512 more and 7
banks. Transparent pixels in a tile become index 0 and show the layer below.
"""
import numpy as np


def split_tiles(ind: np.ndarray):
    """ind: (H, W) palette indices, 0 = transparent. Returns the (n, 8, 8) tiles in metatile order:
    for each 16x16 cell row-major, its four 8x8 quarters top-left, top-right, bottom-left, bottom-right."""
    H, W = ind.shape
    out = []
    for cy in range(0, H, 16):
        for cx in range(0, W, 16):
            for qy in (0, 8):
                for qx in (0, 8):
                    out.append(ind[cy + qy:cy + qy + 8, cx + qx:cx + qx + 8])
    return np.array(out)


def _canon(t: np.ndarray):
    """Canonical form under horizontal/vertical flip (the GBA flips tiles for free)."""
    cands = [t, t[:, ::-1], t[::-1, :], t[::-1, ::-1]]
    return min(c.tobytes() for c in cands)


def budget(ind: np.ndarray, palette: np.ndarray):
    tiles = split_tiles(ind)
    blank = sum(1 for t in tiles if not t.any())
    uniq = {_canon(t) for t in tiles if t.any()}
    used = sorted(set(np.unique(ind)) - {0})
    colours = [tuple(int(v) for v in palette[i]) for i in used]
    return {"cells": int(len(tiles) // 4), "tiles_8x8": int(len(tiles)), "blank_tiles": blank,
            "unique_tiles": len(uniq), "colours": len(colours), "bank_ok": len(colours) <= 15}


def layers(ind: np.ndarray, footprint_rows: list[int]):
    """Split the index image into (bottom, top) layer images by cell row."""
    H, W = ind.shape
    bottom = np.zeros_like(ind)
    top = np.zeros_like(ind)
    for r in range(H // 16):
        sl = slice(r * 16, r * 16 + 16)
        if r in footprint_rows:
            bottom[sl] = ind[sl]
        else:
            top[sl] = ind[sl]
    return bottom, top

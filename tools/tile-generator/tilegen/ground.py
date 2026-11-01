"""Stage 2: 2D ground textures as index maps, in the vanilla idiom.

All generators return uint8 index arrays (values are palette indices inside one bank) so they drop
straight into a tileset's tiles. Measured idiom (General metatile 1, grass): a flat base tone, two 2x2
blobs of the lighter tone and ~4 single pixels of the darker tone per 8x8 tile, arranged so the two
tiles of a 16x16 cell differ and the cell tiles seamlessly in every direction.
"""
from __future__ import annotations

import numpy as np

Tones = dict  # {"base": idx, "light": idx, "dark": idx, ...}


def _rng(seed):
    return np.random.default_rng(seed)


def speckle(size: int, base: int, light: int | None, dark: int | None, seed: int = 0,
            light_blobs: int = 2, dark_dots: int = 4, blob: int = 2, margin: int = 0) -> np.ndarray:
    """A flat field with sparse marks. Counts are per 8x8; the whole array tiles seamlessly."""
    rng = _rng(seed)
    a = np.full((size, size), base, np.uint8)
    n8 = (size // 8) ** 2
    occupied = np.zeros((size, size), bool)

    def free(y, x, h, w):
        yy = (np.arange(y, y + h)) % size
        xx = (np.arange(x, x + w)) % size
        return not occupied[np.ix_(yy, xx)].any()

    def mark(y, x, h, w, v):
        yy = (np.arange(y, y + h)) % size
        xx = (np.arange(x, x + w)) % size
        a[np.ix_(yy, xx)] = v
        # keep a 1 px moat so marks never touch
        yy2 = (np.arange(y - 1, y + h + 1)) % size
        xx2 = (np.arange(x - 1, x + w + 1)) % size
        occupied[np.ix_(yy2, xx2)] = True

    if light is not None:
        for _ in range(light_blobs * n8):
            for _try in range(40):
                y, x = int(rng.integers(0, size)), int(rng.integers(0, size))
                if free(y, x, blob, blob):
                    mark(y, x, blob, blob, light); break
    if dark is not None:
        for _ in range(dark_dots * n8):
            for _try in range(40):
                y, x = int(rng.integers(0, size)), int(rng.integers(0, size))
                if free(y, x, 1, 1):
                    mark(y, x, 1, 1, dark); break
    return a


def blob_edge_set(size: int, outside: np.ndarray, inside_base: int, edge_dark: int, edge_light: int | None = None,
                  seed: int = 0, inset: int = 3) -> dict[str, np.ndarray]:
    """The 13-piece transition kit between a surrounding material (`outside`, a size x size index tile)
    and a patch of `inside_base`: n/s/e/w edges, 4 outer corners, 4 inner corners, plus the full inside.
    Vanilla sand edges: the patch boundary is a rounded shape and a 1 px ring of dots in the darker tone
    sits just outside the fill, every other pixel (see General metatiles 468-477)."""
    rng = _rng(seed)
    pieces = {}
    yy, xx = np.mgrid[0:size, 0:size]

    def make(mask_inside: np.ndarray) -> np.ndarray:
        a = outside.copy()
        a[mask_inside] = inside_base
        # dotted ring: outside pixels 4-adjacent to the inside, every other along the boundary
        ring = np.zeros_like(mask_inside)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ring |= np.roll(mask_inside, (dy, dx), axis=(0, 1))
        ring &= ~mask_inside
        dots = ring & (((xx + yy) % 2) == 0)
        a[dots] = edge_dark
        if edge_light is not None:
            # a lighter lip just inside the boundary on the top/left (lit) side
            inner = mask_inside & ~np.roll(mask_inside, (1, 0), axis=(0, 1))
            a[inner & (((xx + yy) % 2) == 1)] = edge_light
        return a

    i = inset
    r = size // 2  # corner radius for rounded corners
    full = np.ones((size, size), bool)
    pieces["c"] = make(full)
    pieces["n"] = make(yy >= i); pieces["s"] = make(yy < size - i)
    pieces["w"] = make(xx >= i); pieces["e"] = make(xx < size - i)

    def disc(cy, cx, rad):
        return (yy - cy) ** 2 + (xx - cx) ** 2 <= rad ** 2

    # outer corners: the patch is the quarter disc in the far corner
    pieces["nw"] = make(disc(size - 1 + r - i, size - 1 + r - i, r + size - 1 - i) & (yy >= i) & (xx >= i))
    pieces["ne"] = pieces["nw"][:, ::-1]
    pieces["sw"] = pieces["nw"][::-1, :]
    pieces["se"] = pieces["nw"][::-1, ::-1]
    # inner corners: everything except a small outside notch in one corner
    notch = ~(disc(-r + i, -r + i, r) ) | (yy >= i) | (xx >= i)
    inner_nw = full & ~((yy < i) & (xx < i))
    pieces["inw"] = make(inner_nw)
    pieces["ine"] = pieces["inw"][:, ::-1]
    pieces["isw"] = pieces["inw"][::-1, :]
    pieces["ise"] = pieces["inw"][::-1, ::-1]
    return pieces


def ledge(size: int, ground: np.ndarray, lip_light: int, face_mid: int, face_dark: int, shadow: int | None,
          rows: int = 6) -> np.ndarray:
    """A one-way ledge strip drawn in 2D: the ground on top, a lit 1 px lip, a `rows` px face in mid with a
    dark bottom edge, and a shadow row on the ground below (General metatile 135 family)."""
    a = ground.copy()
    top = size // 2 - 1
    a[top, :] = lip_light
    a[top + 1:top + rows, :] = face_mid
    a[top + rows, :] = face_dark
    if shadow is not None:
        a[top + rows + 1, ::2] = shadow
    return a


def tile_grid(pieces: dict[str, np.ndarray], order: list[str], cols: int) -> np.ndarray:
    size = next(iter(pieces.values())).shape[0]
    rows = (len(order) + cols - 1) // cols
    out = np.zeros((rows * size, cols * size), np.uint8)
    for k, name in enumerate(order):
        r, c = divmod(k, cols)
        out[r * size:(r + 1) * size, c * size:(c + 1) * size] = pieces[name]
    return out


# ----------------------------------------------------------------------------- metal floors (Death Star)
# Patterns return a 16x16 map of tone *levels* (0 = lightest); the recipe maps levels to bank indices, so the
# same pattern fills the lit and the shadowed floor tiles (vanilla Facility: shadow = every index + 1).

def deck_plate(bolts: bool = False) -> np.ndarray:
    """One square deck plate per metatile: dark seam on the top row and right column, a 1 px lit bevel inside
    it (light from the upper left), a flat glossy field, and a short reflection streak."""
    p = np.ones((16, 16), np.uint8)
    p[0, :] = 2; p[:, 15] = 2
    p[1, :15] = 0; p[1:, 0] = 0
    for i in range(4):                      # diagonal gloss streak, upper left of the plate
        p[4 + i, 9 - i] = 0
    if bolts:
        for y, x in ((3, 3), (3, 12), (12, 3), (12, 12)):
            p[y, x] = 2
    return p


def grate(period: int = 4) -> np.ndarray:
    """A floor grate: dark slots every `period` rows between lit bars, with a frame seam like deck_plate."""
    p = np.ones((16, 16), np.uint8)
    for y in range(2, 16, period):
        p[y, 2:14] = 2
        p[y - 1, 2:14] = 0
    p[0, :] = 2; p[:, 15] = 2; p[1:, 0] = 0
    return p


def grate_band() -> np.ndarray:
    """A 16x8 floor grate band that repeats vertically (for kits that stack one tile row twice): lit bars
    between dark slots, a slot break every 8 px so it reads as a grid, not stripes."""
    p = np.ones((8, 16), np.uint8)
    for y in (1, 5):
        p[y, :] = 2
        p[y + 1, :] = 0
    p[:, 7] = 2; p[:, 15] = 2
    p[:, 0] = np.where(p[:, 0] == 2, 2, 0); p[:, 8] = np.where(p[:, 8] == 2, 2, 0)
    return p


PATTERNS = {"deck_plate": deck_plate, "grate": grate, "grate_band": grate_band}

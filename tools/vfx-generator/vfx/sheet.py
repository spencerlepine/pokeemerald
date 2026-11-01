"""The GBA tile model: how a PNG becomes OBJ frames, and back.

gbagfx turns a PNG into 8x8 tiles left to right, top to bottom (or metatile by metatile with
-mwidth/-mheight). An OBJ frame of W x H pixels at tile offset `o` (ANIMCMD_FRAME's first argument,
or overworld_frame's index * W/8 * H/8) is tiles o .. o + W/8*H/8 - 1 laid out row-major, W/8 per row
(1D OBJ mapping, which Emerald uses everywhere).

So the PNG layout and the frame layout are not the same thing: a 16-wide sheet of 8x8 frames reads
across rows, a 32-wide sheet of 16x16 frames would interleave. Reading and writing through this
module makes every generated frame land exactly where the game reads it, whatever the PNG shape.
"""
from __future__ import annotations

import numpy as np
from PIL import Image


def to_tiles(pix: np.ndarray, mwidth: int = 1, mheight: int = 1) -> list[np.ndarray]:
    """Index array (H x W) -> list of 8x8 tiles in VRAM order."""
    h, w = pix.shape
    th, tw = h // 8, w // 8
    out = []
    for my in range(0, th, mheight):
        for mx in range(0, tw, mwidth):
            for ty in range(my, min(my + mheight, th)):
                for tx in range(mx, min(mx + mwidth, tw)):
                    out.append(pix[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8])
    return out


def from_tiles(tiles: list[np.ndarray], size: tuple[int, int], mwidth: int = 1, mheight: int = 1) -> np.ndarray:
    """Inverse of to_tiles: tiles in VRAM order -> index array of `size` (W, H)."""
    w, h = size
    pix = np.zeros((h, w), dtype=np.uint8)
    th, tw = h // 8, w // 8
    i = 0
    for my in range(0, th, mheight):
        for mx in range(0, tw, mwidth):
            for ty in range(my, min(my + mheight, th)):
                for tx in range(mx, min(mx + mwidth, tw)):
                    if i < len(tiles):
                        pix[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] = tiles[i]
                    i += 1
    return pix


def frame_from_tiles(tiles: list[np.ndarray], offset: int, fw: int, fh: int) -> np.ndarray:
    tw, th = fw // 8, fh // 8
    out = np.zeros((fh, fw), dtype=np.uint8)
    for k in range(tw * th):
        if offset + k < len(tiles):
            ty, tx = divmod(k, tw)
            out[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] = tiles[offset + k]
    return out


def frame_to_tiles(frame: np.ndarray) -> list[np.ndarray]:
    fh, fw = frame.shape
    return [frame[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] for ty in range(fh // 8) for tx in range(fw // 8)]


def read_indexed(path) -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    im = Image.open(path)
    if im.mode != "P":
        raise ValueError(f"{path}: not an indexed PNG (mode {im.mode})")
    pal = im.getpalette() or []
    cols = [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]
    return np.array(im, dtype=np.uint8), cols


def split_frames(pix: np.ndarray, fw: int, fh: int, mwidth: int = 1, mheight: int = 1, count: int | None = None) -> list[np.ndarray]:
    """Every frame slot of a sheet, in tile order."""
    tiles = to_tiles(pix, mwidth, mheight)
    per = (fw // 8) * (fh // 8)
    n = len(tiles) // per if count is None else count
    return [frame_from_tiles(tiles, k * per, fw, fh) for k in range(n)]


def join_frames(frames: list[np.ndarray], size: tuple[int, int], mwidth: int = 1, mheight: int = 1,
                base: np.ndarray | None = None) -> np.ndarray:
    """Frames (index arrays) -> sheet of `size`, through the tile order. Tiles past the last frame keep
    `base` (the vanilla sheet), so unused slack tiles stay byte-identical."""
    tiles = to_tiles(base, mwidth, mheight) if base is not None else []
    flat: list[np.ndarray] = []
    for f in frames:
        flat.extend(frame_to_tiles(f))
    total = (size[0] // 8) * (size[1] // 8)
    if len(tiles) < total:
        tiles = tiles + [np.zeros((8, 8), np.uint8)] * (total - len(tiles))
    for i, t in enumerate(flat[:total]):
        tiles[i] = t
    return from_tiles(tiles, size, mwidth, mheight)


def to_rgba(pix: np.ndarray, pal: list[tuple[int, int, int]], transparent0: bool = True) -> Image.Image:
    lut = np.zeros((256, 4), dtype=np.uint8)
    for i, c in enumerate(pal[:256]):
        lut[i, :3] = c[:3]
        lut[i, 3] = 255
    if transparent0:
        lut[0, 3] = 0
    return Image.fromarray(lut[pix], "RGBA")


def indexed_image(pix: np.ndarray, pal: list[tuple[int, int, int]]) -> Image.Image:
    im = Image.fromarray(pix.astype(np.uint8), "P")
    flat = []
    for c in pal:
        flat.extend(c[:3])
    flat += [0] * (768 - len(flat))
    im.putpalette(flat)
    return im

"""Edit a tileset in memory: replace the pixels of the tiles a metatile uses, allocate new tiles, and
write the result back in the game's format (stage 7's packer lives in pack.py)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import gba

TILE, META = gba.TILE, gba.METATILE


def copy_tileset(ts: gba.Tileset) -> gba.Tileset:
    return gba.Tileset(ts.name, ts.path, ts.secondary, ts.tiles.copy(), [list(p) for p in ts.palettes],
                       ts.metatiles.copy(), ts.attributes.copy())


def metatile_entries(ts: gba.Tileset, mid: int):
    """Yield (layer, quadrant, tile_id_local, hflip, vflip, bank) for a metatile."""
    for layer in range(2):
        for q in range(4):
            e = int(ts.metatiles[mid, layer, q])
            tid = e & 0x3FF
            if ts.secondary:
                tid -= gba.NUM_TILES_IN_PRIMARY
            yield layer, q, tid, (e >> 10) & 1, (e >> 11) & 1, (e >> 12) & 0xF


def set_metatile_layer(ts: gba.Tileset, mid: int, layer: int, idx16: np.ndarray) -> None:
    """Write a 16x16 index map into the four tiles of one layer of a metatile, honouring the flips the
    metatile applies (so the tile stores the un-flipped pixels). Other metatiles sharing those tiles change
    too: that is the point of a tile kit (use `clone_metatile_tiles` first to detach)."""
    assert idx16.shape == (META, META)
    for _, q, tid, hf, vf, _bank in [e for e in metatile_entries(ts, mid) if e[0] == layer]:
        if tid < 0 or (tid == 0 and not ts.secondary):
            continue
        y, x = (q // 2) * TILE, (q % 2) * TILE
        t = idx16[y:y + TILE, x:x + TILE]
        if hf:
            t = t[:, ::-1]
        if vf:
            t = t[::-1, :]
        ts.tiles[tid] = t


def used_tile_ids(ts: gba.Tileset) -> set[int]:
    s = set()
    for mid in range(ts.n_metatiles):
        for _, _, tid, _, _, _ in metatile_entries(ts, mid):
            s.add(tid)
    return s


def free_tile_ids(ts: gba.Tileset, limit: int = gba.NUM_TILES_IN_PRIMARY) -> list[int]:
    used = used_tile_ids(ts)
    return [t for t in range(1, min(limit, len(ts.tiles))) if t not in used]


def grow_tiles(ts: gba.Tileset, n: int) -> None:
    ts.tiles = np.concatenate([ts.tiles, np.zeros((n, TILE, TILE), np.uint8)])


def clone_metatile_tiles(ts: gba.Tileset, mid: int, layer: int, alloc: list[int]) -> None:
    """Give a metatile its own copies of the tiles it uses on a layer (ids popped from `alloc`)."""
    base = gba.NUM_TILES_IN_PRIMARY if ts.secondary else 0
    for layer_, q, tid, hf, vf, bank in list(metatile_entries(ts, mid)):
        if layer_ != layer or tid <= 0:
            continue
        new = alloc.pop(0)
        if new >= len(ts.tiles):
            grow_tiles(ts, new + 1 - len(ts.tiles))
        ts.tiles[new] = ts.tiles[tid]
        ts.metatiles[mid, layer, q] = (new + base) | (hf << 10) | (vf << 11) | (bank << 12)


def set_metatile_bank(ts: gba.Tileset, mid: int, bank: int, layer: int | None = None) -> None:
    for layer_ in range(2):
        if layer is not None and layer_ != layer:
            continue
        for q in range(4):
            e = int(ts.metatiles[mid, layer_, q])
            if (e & 0x3FF) == 0:
                continue
            ts.metatiles[mid, layer_, q] = (e & 0x0FFF) | (bank << 12)


def rgb_to_bank_indices(rgb: np.ndarray, bank: list[tuple[int, int, int]], alpha: np.ndarray | None = None) -> np.ndarray:
    """Nearest colour (CIELAB) in a 16-colour bank; alpha False -> 0."""
    from . import colour
    pal = colour.srgb_to_lab(np.array(bank[1:], float))
    lab = colour.srgb_to_lab(rgb.reshape(-1, 3).astype(float))
    d = ((lab[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    idx = (d.argmin(1) + 1).astype(np.uint8).reshape(rgb.shape[:2])
    if alpha is not None:
        idx[~alpha] = 0
    return idx


def rebank_metatiles(ts: gba.Tileset, mids, frm: int, to: int, idxmap: dict[int, int], alloc: list[int]) -> int:
    """Move the `frm`-bank entries of some metatiles to bank `to`, remapping colour indices with `idxmap`
    (indices not in the map stay). The affected tiles are cloned (once per source tile, ids popped from
    `alloc`), so other metatiles that share them keep their bank and look. Use it to give an effect its own
    colours (lava rocks) when its tiles share a bank with unrelated art. Returns the tiles cloned."""
    base = gba.NUM_TILES_IN_PRIMARY if ts.secondary else 0
    lut = np.arange(16, dtype=np.uint8)
    for k, v in idxmap.items():
        lut[int(k)] = int(v)
    clones: dict[int, int] = {}
    for mid in mids:
        for layer, q, tid, hf, vf, bank in list(metatile_entries(ts, mid)):
            if bank != frm or tid <= 0:
                continue
            if tid not in clones:
                new = alloc.pop(0)
                if new >= len(ts.tiles):
                    grow_tiles(ts, new + 1 - len(ts.tiles))
                ts.tiles[new] = lut[ts.tiles[tid]]
                clones[tid] = new
            ts.metatiles[mid, layer, q] = (clones[tid] + base) | (hf << 10) | (vf << 11) | (to << 12)
    return len(clones)


def metatiles_using_tiles(ts: gba.Tileset, lo: int, hi: int) -> list[int]:
    """Metatiles that draw any tile id in [lo, hi) (e.g. the animated water range 432-462)."""
    return [m for m in range(ts.n_metatiles)
            if any(lo <= (int(e) & 0x3FF) < hi for e in ts.metatiles[m].flatten())]

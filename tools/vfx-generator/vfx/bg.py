"""Battle-anim backdrops (fadetobg BG_X): a tileset PNG + 32x20 tilemap in the format of
graphics/battle_anims/backgrounds/psychic.{png,bin}.

The engine loads the tileset at BG_CHAR_ADDR(2) (room for 640 tiles before the map at screen base 26)
and the palette into BG palette 2, so every map entry carries palette nibble 2. Backdrops are drawn as
palette *indices*; `ripple` puts indices 1..11 in bands so AnimTask_SetPsychicBackground (which rotates
BG palette entries 1..11 every 4 frames) makes the bands flow outward. The picture is built from one
quadrant mirrored with tile flips, so unique tiles stay well under the limit.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 256, 160          # visible battle area (32x20 tiles)
PAL_NIBBLE = 2
MAX_TILES = 640


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def ripple(cx: int = 128, cy: int = 80, spacing: float = 7.0, wobble: float = 0.9, petals: int = 4,
           swirl: float = 0.0) -> np.ndarray:
    """Index image (H, W): concentric bands of indices 1..11, bent into `petals` lobes by `wobble`."""
    ys, xs = np.mgrid[0:H, 0:W]
    dx, dy = xs + 0.5 - cx, ys + 0.5 - cy
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    phase = r / spacing + wobble * np.cos(petals * th) * np.clip(r / 40.0, 0, 1) + swirl * th
    return (np.floor(phase).astype(int) % 11) + 1


def tilemap(img: np.ndarray) -> tuple[list[np.ndarray], list[int]]:
    """Dedupe 8x8 tiles, allowing h/v flips. Returns (tiles, 32x20 map entries)."""
    tiles: list[np.ndarray] = []
    index: dict[bytes, int] = {}
    entries = []
    for ty in range(H // 8):
        for tx in range(W // 8):
            t = img[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8]
            hit = None
            for flip, v in ((0, t), (1, t[:, ::-1]), (2, t[::-1, :]), (3, t[::-1, ::-1])):
                k = v.astype(np.uint8).tobytes()
                if k in index:
                    hit = (index[k], flip)
                    break
            if hit is None:
                index[t.astype(np.uint8).tobytes()] = len(tiles)
                tiles.append(t.copy())
                hit = (len(tiles) - 1, 0)
            n, flip = hit
            entries.append(n | ((flip & 1) << 10) | ((flip >> 1) << 11) | (PAL_NIBBLE << 12))
    # the game reads a 32x32 screen block; rows 20-31 are off screen
    entries += [entries[0]] * (32 * 32 - len(entries))
    return tiles, entries


def write(img: np.ndarray, colors: list[str], out_png: Path) -> dict:
    """Write <out>.png (128-wide tileset, indexed, 16 colours) and <out>.bin (tilemap)."""
    if len(colors) != 16:
        raise ValueError("a backdrop palette has 16 colours (index 0 = backdrop/transparent)")
    tiles, entries = tilemap(img)
    if len(tiles) > MAX_TILES:
        raise ValueError(f"{len(tiles)} unique tiles; the backdrop slot holds {MAX_TILES}")
    cols = 16
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.zeros((rows * 8, cols * 8), dtype=np.uint8)
    for i, t in enumerate(tiles):
        y, x = divmod(i, cols)
        sheet[y * 8:(y + 1) * 8, x * 8:(x + 1) * 8] = t
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(sheet, "P")
    flat = [v for c in colors for v in _hex(c)]
    im.putpalette(flat + [0] * (768 - len(flat)))
    im.save(out_png)
    out_png.with_suffix(".bin").write_bytes(np.array(entries, dtype="<u2").tobytes())
    # a preview of the backdrop as the game composes it
    prev = Image.fromarray(img.astype(np.uint8), "P")
    prev.putpalette(flat + [0] * (768 - len(flat)))
    prev.convert("RGB").resize((W * 2, H * 2), Image.NEAREST).save(out_png.with_name(out_png.stem + "_preview.png"))
    return {"tiles": len(tiles), "png": out_png, "bin": out_png.with_suffix(".bin")}


def build(spec: dict, out_png: Path) -> dict:
    """spec: {kind: ripple, colors: [16 hex], <ripple args>}"""
    kind = spec.get("kind", "ripple")
    if kind != "ripple":
        raise ValueError(f"unknown backdrop kind {kind!r}")
    args = {k: spec[k] for k in ("cx", "cy", "spacing", "wobble", "petals", "swirl") if k in spec}
    return write(ripple(**args), spec["colors"], out_png)

"""Post-processing: turn any RGB/RGBA image (a diffusion render, a downscale, a hand edit) into an
indexed PNG that obeys the hardware and, if asked, a theme or a locked shared palette.

Order of operations (tools/PALETTES.md, "The enforcement step"):
  1. transparency: alpha < 128, or a key colour, becomes index 0
  2. snap every opaque pixel to a GBA step (multiples of 8)
  3. pick the palette:
       --pal    a locked palette (shared NPC/icon/tileset bank): pixels map onto its 15 colours, indices kept
       --theme  quantise to <= N colours, then pull each colour onto the theme
                (within --tolerance always; beyond it, at most --free colours may stay off-theme)
       neither  quantise to <= N colours (N = 15 for 4bpp)
  4. map every pixel to the nearest palette colour (CIELAB), no dithering
  5. write an indexed PNG at the target bit depth (and optionally the .pal)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from . import core
from .core import Colour

# Index 0 of a new palette when nothing else sets it. Never shown (transparent / backdrop), so it
# is a loud colour that cannot be mistaken for art in a viewer.
DEFAULT_ZERO: Colour = (248, 0, 248)


def _quantise(colours: np.ndarray, weights: np.ndarray, k: int) -> list[Colour]:
    uniq = [tuple(int(v) for v in c) for c in colours]
    if len(uniq) <= k:
        return uniq
    # Median cut over the pixels (weighted by count), via Pillow on a 1-row image.
    reps = np.repeat(colours, np.minimum(weights, 4096), axis=0).astype(np.uint8)
    strip = Image.fromarray(reps.reshape(1, -1, 3), "RGB")
    q = strip.quantize(colors=k, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    flat = q.getpalette()[: 3 * k]
    out: list[Colour] = []
    for i in range(0, len(flat), 3):
        c = core.snap(tuple(flat[i : i + 3]))
        if c not in out:
            out.append(c)
    return out


def _pull_to_theme(centres: list[Colour], theme: list[Colour], tolerance: float, free: int) -> list[Colour]:
    j, d = core.nearest(centres, theme)
    order = np.argsort(-d)  # farthest from the theme first: those are the ones worth a free slot
    out = list(centres)
    kept = 0
    for i in order:
        if d[i] <= tolerance or kept >= free:
            out[i] = theme[j[i]]
        else:
            kept += 1
    dedup: list[Colour] = []
    for c in out:
        if c not in dedup:
            dedup.append(c)
    return dedup


def enforce(
    img: Image.Image,
    *,
    bpp: int = 4,
    pal: list[Colour] | None = None,
    theme: list[Colour] | None = None,
    tolerance: float = 12.0,
    free: int | None = None,
    colours: int | None = None,
    key: Colour | str | None = None,
    zero: Colour | None = None,
) -> tuple[Image.Image, list[Colour]]:
    """Return (indexed image, palette). The palette has 2**bpp entries; index 0 is transparent."""
    if bpp not in core.VISIBLE:
        raise ValueError(f"bpp must be one of {sorted(core.VISIBLE)}")
    rgba = np.asarray(img.convert("RGBA"))
    h, w = rgba.shape[:2]
    rgb = rgba[..., :3].astype(np.int32)
    clear = rgba[..., 3] < 128
    if key == "auto":
        key = tuple(int(v) for v in rgb[0, 0])
    if key is not None:
        clear |= np.all(rgb == np.array(key[:3]), axis=-1)

    snapped = np.minimum(np.round(rgb / 8.0) * 8, core.MAX_STEP).astype(np.int32)
    opaque = snapped[~clear]
    visible = core.VISIBLE[bpp]
    k = min(colours or visible, visible)

    if pal is not None:
        if len(pal) < 2:
            raise ValueError("locked palette needs index 0 plus at least one colour")
        # A locked palette is someone else's file (shared NPC/icon/tileset bank): keep it verbatim.
        palette = [tuple(c) for c in pal[: visible + 1]]
        targets = list(range(1, len(palette)))
    else:
        if len(opaque):
            uniq, inv_counts = np.unique(opaque, axis=0, return_counts=True)
            centres = _quantise(uniq, inv_counts, k)
            if theme:
                centres = _pull_to_theme(centres, [core.snap(c) for c in theme], tolerance, k if free is None else free)
            centres.sort(key=core.luma, reverse=True)
        else:
            centres = []
        z = zero or (core.snap(key) if isinstance(key, tuple) else DEFAULT_ZERO)
        palette = [z] + centres
        targets = list(range(1, len(palette)))

    idx = np.zeros((h, w), dtype=np.uint8)
    if len(opaque) and targets:
        uniq, inv = np.unique(opaque, axis=0, return_inverse=True)
        j, _ = core.nearest(uniq, [palette[t] for t in targets])
        idx[~clear] = np.array(targets, dtype=np.uint8)[j][inv.reshape(-1)]

    size = 1 << bpp
    palette = (palette + [(0, 0, 0)] * size)[:size]
    out = Image.fromarray(idx, "P")
    out.putpalette([v for c in palette for v in c])
    return out, palette


def save(img: Image.Image, path: str | Path, bpp: int) -> None:
    """Indexed PNG at the exact bit depth gbagfx expects."""
    img.save(path, bits=bpp, optimize=False)


def enforce_file(src: str | Path, dst: str | Path, *, write_pal: str | Path | None = None, **kw) -> list[Colour]:
    bpp = kw.get("bpp", 4)
    out, palette = enforce(Image.open(src), **kw)
    save(out, dst, bpp)
    if write_pal:
        core.write_jasc(write_pal, palette[:16] if bpp <= 4 else palette)
    return palette

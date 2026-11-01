"""Review sheets: vanilla vs generated, side by side, with labels and palette swatches."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import gba

_FONT = None


def font(size: int = 12):
    global _FONT
    if _FONT is None:
        for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"):
            if Path(p).exists():
                _FONT = ImageFont.truetype(p, size)
                break
        else:
            _FONT = ImageFont.load_default()
    return _FONT


def zoom(im: Image.Image, z: int) -> Image.Image:
    return im if z == 1 else im.resize((im.width * z, im.height * z), Image.NEAREST)


def side_by_side(panels: list[tuple[str, Image.Image]], zoom_factor: int = 2, gap: int = 16, bg=(24, 24, 28)) -> Image.Image:
    ims = [(t, zoom(im.convert("RGB"), zoom_factor)) for t, im in panels]
    label_h = 22
    W = sum(im.width for _, im in ims) + gap * (len(ims) + 1)
    H = max(im.height for _, im in ims) + label_h + gap * 2
    out = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(out)
    x = gap
    for t, im in ims:
        d.text((x, gap // 2), t, fill=(230, 230, 230), font=font())
        out.paste(im, (x, gap // 2 + label_h))
        x += im.width + gap
    return out


def stack(panels: list[Image.Image], gap: int = 16, bg=(24, 24, 28)) -> Image.Image:
    W = max(p.width for p in panels)
    H = sum(p.height for p in panels) + gap * (len(panels) - 1)
    out = Image.new("RGB", (W, H), bg)
    y = 0
    for p in panels:
        out.paste(p.convert("RGB"), (0, y))
        y += p.height + gap
    return out


def swatches(pairs: list[tuple[str, list, list]], cell: int = 14) -> Image.Image:
    """Rows of (label, old bank, new bank): old on top, new under, per bank."""
    rows = len(pairs)
    W = 160 + 16 * cell
    H = rows * (cell * 2 + 8)
    out = Image.new("RGB", (W, H), (24, 24, 28))
    d = ImageDraw.Draw(out)
    y = 0
    for label, old, new in pairs:
        d.text((4, y + cell // 2), label, fill=(230, 230, 230), font=font(11))
        for i in range(16):
            d.rectangle([160 + i * cell, y, 160 + (i + 1) * cell - 1, y + cell - 1], fill=tuple(old[i]))
            d.rectangle([160 + i * cell, y + cell, 160 + (i + 1) * cell - 1, y + 2 * cell - 1], fill=tuple(new[i]))
        y += cell * 2 + 8
    return out

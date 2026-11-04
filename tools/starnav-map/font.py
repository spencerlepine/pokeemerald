"""The game's own fonts, read straight from ../../game (read only), so the mockup text is the GBA's text.

Each latin font PNG is a grid of 16x16 glyph cells, 16 per row, indexed by the charmap byte. Pixel index 1 is
ink, 2 is shadow. Widths come from the glyph width tables in src/fonts.c. Aurebesh letters come from the
glyph-maker's ASCII art (8x9).
"""
from __future__ import annotations

import re
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "game"

FONTS = {"normal": ("latin_normal", "gFontNormalLatinGlyphWidths"),
         "small": ("latin_small", "gFontSmallLatinGlyphWidths"),
         "narrow": ("latin_narrow", "gFontNarrowLatinGlyphWidths")}


@lru_cache(None)
def charmap():
    out = {}
    for line in open(GAME / "charmap.txt", encoding="utf-8"):
        m = re.match(r"^'(.)'\s*=\s*([0-9A-F]{2})\s*$", line)
        if m and m.group(1) not in out:
            out[m.group(1)] = int(m.group(2), 16)
    out["'"] = out.get("’", 0xB4)
    return out


@lru_cache(None)
def widths(table):
    src = (GAME / "src" / "fonts.c").read_text()
    m = re.search(table + r"\[\] = \{(.*?)\};", src, re.S)
    return [int(v) for v in re.findall(r"\d+", m.group(1))]


@lru_cache(None)
def glyphs(font):
    """char -> (width, rows) where rows are strings of '0' clear, '1' ink, '2' shadow. Height 16."""
    png, table = FONTS[font]
    im = Image.open(GAME / "graphics" / "fonts" / f"{png}.png")
    px = im.load()
    ws = widths(table)
    out = {}
    for ch, ix in charmap().items():
        if ix >= len(ws):
            continue
        gx, gy = (ix % 16) * 16, (ix // 16) * 16
        w = ws[ix]
        rows = []
        for y in range(16):
            r = ""
            for x in range(w):
                v = px[gx + x, gy + y]
                r += "1" if v == 1 else "2" if v == 2 else "0"
            rows.append(r)
        out[ch] = (w, rows)
    return out


@lru_cache(None)
def aurebesh():
    sys.path.insert(0, str(ROOT / "tools" / "glyph-maker"))
    import aurebesh as ab  # noqa: E402
    out = {}
    for ch, art in ab.LETTERS.items():
        rows = [r for r in art.strip("\n").splitlines()]
        out[ch] = (len(rows[0]) + 1, ["".join("1" if c == "#" else "0" for c in r) for r in rows])
    out[" "] = (5, ["0"] * 9)
    return out


def text_width(text, font="normal"):
    g = aurebesh() if font == "aurebesh" else glyphs(font)
    return sum(g.get(c, (3, []))[0] for c in text)


def draw(img, x, y, text, ink, shadow=None, font="normal"):
    """Draw text on a PIL RGBA/RGB image at (x, y), top of the 16-row glyph cell."""
    g = aurebesh() if font == "aurebesh" else glyphs(font)
    px = img.load()
    W, H = img.size
    for c in text:
        w, rows = g.get(c, (3, []))
        for j, r in enumerate(rows):
            for i, v in enumerate(r):
                col = ink if v == "1" else shadow if v == "2" else None
                if col and 0 <= x + i < W and 0 <= y + j < H:
                    px[x + i, y + j] = col if len(col) == len(img.mode) else tuple(col)[:len(img.mode)]
        x += w
    return x


def export(fonts=("normal", "small", "narrow", "aurebesh")):
    """JSON-ready glyph tables for the browser player."""
    out = {}
    for f in fonts:
        g = aurebesh() if f == "aurebesh" else glyphs(f)
        out[f] = {c: [w, rows] for c, (w, rows) in g.items()
                  if c.isascii() and (c.isalnum() or c in " .'-/:!?&,·")}
    return out

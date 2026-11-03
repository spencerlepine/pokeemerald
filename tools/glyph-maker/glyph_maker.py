"""Draw the COMPANION ligature glyphs (the Star Wars version of Emerald's PkMn glyph) into the game fonts.

    python3 glyph_maker.py preview    # before/after sheets in out/ (nothing in ../../game changes)
    python3 glyph_maker.py install    # write the glyphs into ../../game fonts, widths and charmap

Emerald writes POKéMON's short form with two special glyphs, PK (0x53) and MN (0x54): a tall capital, then a
second capital set lower and to the right ("PkMn"). This tool draws COMPANION the same way, five glyphs
CO MP AN IO N (plural: ... IO NS), into font slots the English fonts leave empty. Text uses them with
{COMPANION} / {COMPANIONS} (charmap.txt).

Everything worth tweaking is at the top: the letters (ASCII art, '#' = ink), which letter pairs make each
glyph, the slots, and per font where the high and the low letter sit. The shadow is added automatically
(right, below and diagonal of every ink pixel), like every other glyph in the font.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
GAME = HERE.parent.parent / "game"
OUT = HERE / "out"

# ---- letters ----------------------------------------------------------------------------------------------
# TALL: 8 rows, for the normal, short and narrow fonts (same height as the P and K in Emerald's PK glyph).
TALL = {
    "C": [".##", "#..", "#..", "#..", "#..", "#..", "#..", ".##"],
    "O": [".#.", "#.#", "#.#", "#.#", "#.#", "#.#", "#.#", ".#."],
    "M": ["#..#", "####", "####", "#..#", "#..#", "#..#", "#..#", "#..#"],
    "P": ["###", "#.#", "#.#", "###", "#..", "#..", "#..", "#.."],
    "A": [".#.", "#.#", "#.#", "#.#", "###", "#.#", "#.#", "#.#"],
    "N": ["#..#", "##.#", "##.#", "#.##", "#.##", "#..#", "#..#", "#..#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "S": [".##", "#..", "#..", ".#.", ".#.", "..#", "..#", "##."],
}
# SMALL: 6 rows, for the small fonts (Emerald's small PK glyph is this height).
SMALL = {
    "C": [".##", "#..", "#..", "#..", "#..", ".##"],
    "O": [".#.", "#.#", "#.#", "#.#", "#.#", ".#."],
    "M": ["#..#", "####", "#..#", "#..#", "#..#", "#..#"],
    "P": ["##.", "#.#", "#.#", "##.", "#..", "#.."],
    "A": [".#.", "#.#", "#.#", "###", "#.#", "#.#"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#", "#..#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", "###"],
    "S": [".##", "#..", ".#.", "..#", "..#", "##."],
}

# ---- glyphs: slot -> (high letter, low letter or None) -----------------------------------------------------
# Slots 0x37-0x3C are hiragana codes that the English fonts leave blank.
GLYPHS = {
    0x37: ("C", "O"),
    0x38: ("M", "P"),
    0x39: ("A", "N"),
    0x3A: ("I", "O"),
    0x3B: ("N", None),
    0x3C: ("N", "S"),
}
CHARMAP = {"COMPANION": [0x37, 0x38, 0x39, 0x3A, 0x3B], "COMPANIONS": [0x37, 0x38, 0x39, 0x3A, 0x3C]}

# ---- fonts: file, widths table in src/fonts.c, letter set, (high top row, low top row, low x offset) --------
FONTS = {
    "latin_normal": ("gFontNormalLatinGlyphWidths", TALL, (1, 6, 4)),
    "latin_short": ("gFontShortLatinGlyphWidths", TALL, (0, 5, 4)),
    "latin_narrow": ("gFontNarrowLatinGlyphWidths", TALL, (1, 6, 4)),
    "latin_small": ("gFontSmallLatinGlyphWidths", SMALL, (3, 7, 4)),
    "latin_small_narrow": ("gFontSmallNarrowLatinGlyphWidths", SMALL, (3, 7, 4)),
}
INK, SHADOW, PAPER, CLEAR = 1, 2, 3, 0  # palette indices in the font PNGs


def draw_glyph(letters: dict, layout, high: str, low: str | None) -> tuple[list[list[int]], int]:
    """Return a 16x16 cell (palette indices) and the glyph width."""
    top_hi, top_lo, lo_x = layout
    ink = set()
    for y, row in enumerate(letters[high]):
        for x, c in enumerate(row):
            if c == "#":
                ink.add((x, top_hi + y))
    width = len(letters[high][0]) + 1
    if low:
        x0 = max(lo_x, len(letters[high][0]))
        for y, row in enumerate(letters[low]):
            for x, c in enumerate(row):
                if c == "#":
                    ink.add((x0 + x, top_lo + y))
        width = x0 + len(letters[low][0]) + 1
    width = max(width, 4)
    cell = [[CLEAR] * 16 for _ in range(16)]
    for y in range(15):
        for x in range(width):
            cell[y][x] = PAPER
    for x, y in ink:
        for dx, dy in ((1, 0), (0, 1), (1, 1)):
            if (x + dx, y + dy) not in ink and x + dx < width:
                cell[y + dy][x + dx] = SHADOW
    for x, y in ink:
        cell[y][x] = INK
    return cell, width


# ---- reading the game fonts ---------------------------------------------------------------------------------
def load_widths(table: str) -> list[int]:
    src = (GAME / "src" / "fonts.c").read_text(encoding="utf-8")
    m = re.search(rf"{table}\[\] = \{{(.*?)\}};", src, re.S)
    return [int(x) for x in re.findall(r"\d+", m.group(1))]


def load_charmap() -> dict[str, list[int]]:
    out = {}
    for line in (GAME / "charmap.txt").read_text(encoding="utf-8").split("\n"):
        line = line.split("@")[0]
        m = re.match(r"\s*('(?:\\'|[^'])+'|[A-Z_0-9]+)\s*=\s*((?:[0-9A-F]{2}\s*)+)$", line)
        if m:
            key = m.group(1).strip("'") if m.group(1).startswith("'") else "{" + m.group(1) + "}"
            out.setdefault(key, [int(b, 16) for b in m.group(2).split()])
    return out


def encode(text: str, cmap) -> list[int]:
    out, i = [], 0
    while i < len(text):
        if text[i] == "{":
            j = text.index("}", i)
            out += cmap[text[i:j + 1]]
            i = j + 1
        else:
            out += cmap[text[i]]
            i += 1
    return out


def render(text: str, font_img: Image.Image, widths: list[int], cmap, scale: int = 4) -> Image.Image:
    codes = encode(text, cmap)
    w = sum(widths[c] for c in codes)
    canvas = Image.new("RGB", (w + 4, 18), (255, 255, 255))
    pal = font_img.getpalette()[:12]
    colours = {0: (255, 255, 255), 1: tuple(pal[3:6]), 2: tuple(pal[6:9]), 3: (255, 255, 255)}
    px, x = font_img.load(), 2
    for c in codes:
        cx, cy = c % 16 * 16, c // 16 * 16
        for yy in range(16):
            for xx in range(widths[c]):
                v = px[cx + xx, cy + yy]
                if v in (1, 2):
                    canvas.putpixel((x + xx, 1 + yy), colours[v])
        x += widths[c]
    return canvas.resize((canvas.width * scale, canvas.height * scale), Image.NEAREST)


def patched(name: str) -> tuple[Image.Image, list[int]]:
    table, letters, layout = FONTS[name]
    img = Image.open(GAME / "graphics" / "fonts" / f"{name}.png").copy()
    widths = load_widths(table)
    for slot, (hi, lo) in GLYPHS.items():
        cell, width = draw_glyph(letters, layout, hi, lo)
        x0, y0 = slot % 16 * 16, slot // 16 * 16
        for y in range(16):
            for x in range(16):
                img.putpixel((x0 + x, y0 + y), cell[y][x])
        widths[slot] = width
    return img, widths


def stack(rows: list[tuple[str, Image.Image]], title: str) -> Image.Image:
    from PIL import ImageDraw
    w = max(im.width for _, im in rows) + 260
    h = sum(im.height + 10 for _, im in rows) + 40
    sheet = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), title, fill=(0, 0, 0))
    y = 36
    for label, im in rows:
        d.text((10, y + im.height // 2 - 6), label, fill=(80, 80, 80))
        sheet.paste(im, (250, y))
        y += im.height + 10
    return sheet


def preview() -> None:
    OUT.mkdir(exist_ok=True)
    cmap = load_charmap()
    cmap.update({"{" + k + "}": v for k, v in CHARMAP.items()})
    samples = [("{PKMN} TRAINER", "{COMPANION} TRAINER"),
               ("Your {PKMN} is healthy.", "Your {COMPANION} is healthy."),
               ("{PKMN} CENTER", "{COMPANIONS} CENTER")]
    rows = []
    for name in FONTS:
        img0 = Image.open(GAME / "graphics" / "fonts" / f"{name}.png")
        w0 = load_widths(FONTS[name][0])
        img1, w1 = patched(name)
        before, after = samples[0]
        rows.append((f"{name} before", render(before, img0, w0, cmap)))
        rows.append((f"{name} after", render(after, img1, w1, cmap)))
    stack(rows, "PkMn glyph (before) vs COMPANION glyphs (after), every font, 4x").save(OUT / "before_after_fonts.png")

    img0, w0 = Image.open(GAME / "graphics/fonts/latin_normal.png"), load_widths(FONTS["latin_normal"][0])
    img1, w1 = patched("latin_normal")
    rows = []
    for before, after in samples:
        rows.append(("before", render(before, img0, w0, cmap)))
        rows.append(("after", render(after, img1, w1, cmap)))
    rows.append(("plain word (what the game says now)", render("COMPANION TRAINER", img0, w0, cmap)))
    stack(rows, "Normal font, sample lines, 4x").save(OUT / "before_after_lines.png")

    # the glyph cells themselves, 12x, on the font's own colours
    cells = Image.new("RGB", (len(GLYPHS) * 16 + 2 * 16, 16), (144, 200, 255))
    for i, slot in enumerate([0x53, 0x54]):
        cells.paste(img0.convert("RGB").crop((slot % 16 * 16, slot // 16 * 16, slot % 16 * 16 + 16, slot // 16 * 16 + 16)), (i * 16, 0))
    for i, slot in enumerate(GLYPHS):
        cells.paste(img1.convert("RGB").crop((slot % 16 * 16, slot // 16 * 16, slot % 16 * 16 + 16, slot // 16 * 16 + 16)), ((i + 2) * 16, 0))
    cells.resize((cells.width * 12, cells.height * 12), Image.NEAREST).save(OUT / "glyph_cells.png")
    print("wrote", *sorted(p.name for p in OUT.glob("*.png")))


def install() -> None:
    src = (GAME / "src" / "fonts.c").read_text(encoding="utf-8")
    for name, (table, _, _) in FONTS.items():
        img, widths = patched(name)
        img.save(GAME / "graphics" / "fonts" / f"{name}.png")
        m = re.search(rf"({table}\[\] = \{{)(.*?)(\}};)", src, re.S)
        rows = [widths[i:i + 16] for i in range(0, len(widths), 16)]
        body = "\n" + "\n".join("    " + ", ".join([str(r[0])] + [f"{w:2d}" for w in r[1:]]) + "," for r in rows) + "\n"
        src = src[:m.start(2)] + body + src[m.end(2):]
    (GAME / "src" / "fonts.c").write_text(src, encoding="utf-8")
    cm = (GAME / "charmap.txt").read_text(encoding="utf-8")
    for key, codes in CHARMAP.items():
        line = f"{key:<11} = " + " ".join(f"{c:02X}" for c in codes)
        if re.search(rf"^{key}\s*=", cm, re.M):
            cm = re.sub(rf"^{key}\s*=.*$", line, cm, flags=re.M)
        else:
            cm = cm.replace("POKEBLOCK   =", line + "\nPOKEBLOCK   =", 1)
    (GAME / "charmap.txt").write_text(cm, encoding="utf-8")
    print("installed", len(GLYPHS), "glyphs into", len(FONTS), "fonts; charmap:", ", ".join(CHARMAP))


if __name__ == "__main__":
    {"preview": preview, "install": install}[sys.argv[1] if len(sys.argv) > 1 else "preview"]()

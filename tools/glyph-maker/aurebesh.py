"""Draw Aurebesh letters into the Braille font, so the ancient signs read as Aurebesh.

    python3 aurebesh.py preview    # before/after sheets in out/ (nothing in ../../game changes)
    python3 aurebesh.py install    # write ../../game/graphics/fonts/braille.png

Emerald's signs (the Sealed Chamber, the three titan tombs) print with FONT_BRAILLE. The text is still
plain letters in data/text/braille.inc (`.braille "DIG HERE.$"`); the preprocessor turns each letter into a
Braille cell number (BRAILLE_CHAR_A = 0x01 ...) and the font draws the cell at that number. This tool keeps
every number and redraws the cells: the cell for A gets the Aurebesh letter Aurek, and so on. Nothing else
changes, so the text, the puzzles and the window sizes work as before.

The letters are ASCII art below ('#' = ink), drawn after the Aurebesh chart already used for the AUREBESH
companion (../sprite-creature-generator/civitai/refs/unown/<letter>_glyph.png). Each is 8 wide and 9 tall,
set in the same 9x15 paper box the Braille dots used, with a light shadow added right and below.
Cells no letter uses (the number sign, unused dot patterns) are left blank.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "game"
FONT = GAME / "graphics" / "fonts" / "braille.png"
REFS = ROOT / "tools" / "sprite-creature-generator" / "civitai" / "refs" / "unown"
OUT = Path(__file__).resolve().parent / "out"

TOP = 3        # first cell row of a letter (the 9 letter rows sit in rows 3-11 of the 15-row paper box)
PAPER = (9, 15)  # the paper box every Braille cell has, top left of the 16x16 cell
INK, SHADOW, PAPER_IX, CLEAR = 1, 2, 3, 0

LETTERS = {
    "A": """
#.....##
#....##.
#...##..
#####...
#.......
#####...
#...##..
#....##.
#.....##""",
    "B": """
.######.
#......#
#......#
#......#
#.####.#
#......#
#......#
#......#
.######.""",
    "C": """
#.......
#.......
#.......
#..#..#.
#..#..#.
#..#..#.
......#.
......#.
......#.""",
    "D": """
########
......#.
.....#..
..####..
...#....
..#.....
..#.....
.#......
.#......""",
    "E": """
#....#.#
#....#.#
.#...#.#
.#..#..#
..#.#..#
..#.#..#
...#...#
...#...#
...#...#""",
    "F": """
....#..#
....#.#.
....##..
..###...
....#...
#...#...
#...#...
#...#...
########""",
    "G": """
#.######
#.#....#
#......#
#.....#.
#.....#.
#....#..
#....#..
#...#...
#####...""",
    "H": """
########
........
........
........
.######.
........
........
........
########""",
    "I": """
....#...
...##...
..#.#...
....#...
....#...
....#...
....#...
....#...
....#...""",
    "J": """
......#.
......#.
.....#..
#######.
#....#..
.....#..
....#...
#####...
........""",
    "K": """
########
.......#
.......#
.......#
.......#
.......#
.......#
.......#
########""",
    "L": """
.......#
.......#
.......#
.......#
#......#
.#.....#
..#....#
...#...#
....####""",
    "M": """
....####
....#...
...#....
...#....
..#.....
..#.....
.#......
.#......
########""",
    "N": """
.#..#...
#...#...
#...#...
#....#..
#....#..
#.....#.
#.....#.
#......#
#......#""",
    "O": """
..####..
.#....#.
.#....#.
.#....#.
#......#
#......#
#......#
#......#
########""",
    "P": """
.###...#
#......#
#......#
#......#
#......#
#......#
#......#
#......#
########""",
    "Q": """
########
#......#
#......#
#.......
#.......
#.......
#.......
#.......
#####...""",
    "R": """
########
.......#
......#.
.....#..
....#...
....#...
...#....
..#.....
.#......""",
    "S": """
#......#
.#.....#
..#....#
...#...#
....#..#
##...#.#
..##..##
....####
........""",
    "T": """
...#....
...#....
...#....
...#....
#..#..#.
.#.#.#..
..###...
...#....
........""",
    "U": """
#..#####
#..#...#
#......#
#......#
#......#
#......#
#......#
#......#
########""",
    "V": """
#.....#.
.#...#..
..#.#...
...#....
...#....
...#....
...#....
...#....
...#....""",
    "W": """
########
#......#
#......#
#......#
#......#
#......#
#......#
#......#
########""",
    "X": """
...##...
...##...
..#..#..
..#..#..
.#....#.
.#....#.
#......#
########
........""",
    "Y": """
##.....#
.#.....#
.##...#.
..#...#.
..##.#..
...#.#..
...###..
....#...
........""",
    "Z": """
.......#
.......#
..######
.#.....#
#......#
.......#
#......#
########
........""",
    ".": """
........
........
........
........
........
........
........
##......
##......""",
    ",": """
........
........
........
........
........
........
.##.....
.##.....
#.......""",
    "!": """
.#......
.#......
.#......
.#......
.#......
.#......
........
.#......
.#......""",
    "?": """
.####...
#....#..
.....#..
....#...
...#....
...#....
........
...#....
...#....""",
    ":": """
........
........
##......
##......
........
........
##......
##......
........""",
    ";": """
........
........
.##.....
.##.....
........
........
.##.....
.##.....
#.......""",
    "-": """
........
........
........
........
#####...
........
........
........
........""",
    "/": """
......#.
......#.
.....#..
....#...
...#....
..#.....
.#......
.#......
........""",
    "(": """
..#.....
.#......
#.......
#.......
#.......
#.......
#.......
.#......
..#.....""",
    "'": """
.#......
.#......
#.......
........
........
........
........
........
........""",
    '"': """
#.#.....
#.#.....
........
........
........
........
........
........
........""",
}

# letter -> cell number, from include/constants/characters.h (BRAILLE_CHAR_*)
NAMES = {".": "PERIOD", ",": "COMMA", "!": "EXCL_MARK", "?": "QUESTION_MARK", ":": "COLON", ";": "SEMICOLON",
         "-": "HYPHEN", "/": "SLASH", "(": "PAREN", "'": "APOSTROPHE", '"': "DBL_QUOTE_RIGHT"}


def cells() -> dict[str, int]:
    src = (GAME / "include" / "constants" / "characters.h").read_text(encoding="utf-8")
    ids = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"#define BRAILLE_CHAR_(\w+)\s+0x([0-9A-F]+)", src)}
    return {ch: ids[NAMES.get(ch, ch)] for ch in LETTERS}


def grid(art: str) -> list[str]:
    rows = art.strip("\n").splitlines()
    assert len(rows) == 9 and all(len(r) == 8 for r in rows), art
    return rows


def draw_aurebesh() -> Image.Image:
    base = Image.open(FONT)
    img = Image.new("P", base.size, CLEAR)
    img.putpalette(base.getpalette())
    for slot in range(base.width // 16 * (base.height // 16)):
        x0, y0 = slot % 16 * 16, slot // 16 * 16
        for y in range(PAPER[1]):
            for x in range(PAPER[0]):
                img.putpixel((x0 + x, y0 + y), PAPER_IX)
    for ch, slot in cells().items():
        x0, y0 = slot % 16 * 16, slot // 16 * 16 + TOP
        rows = grid(LETTERS[ch])
        ink = {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "#"}
        for x, y in ink:
            for dx, dy in ((1, 0), (0, 1), (1, 1)):
                if (x + dx, y + dy) not in ink:
                    img.putpixel((x0 + x + dx, y0 + y + dy), SHADOW)
        for x, y in ink:
            img.putpixel((x0 + x, y0 + y), INK)
    return img


def draw_braille() -> Image.Image:
    """Emerald's own Braille sheet, redrawn from the dot numbers (so 'before' works after install too)."""
    base = Image.open(FONT)
    img = Image.new("P", base.size, CLEAR)
    img.putpalette(base.getpalette())
    for slot in range(64):
        x0, y0 = slot % 16 * 16, slot // 16 * 16
        for y in range(15):
            for x in range(9):
                img.putpixel((x0 + x, y0 + y), PAPER_IX)
        if not slot:
            continue
        for bit in range(6):
            dx, dy = (bit % 2) * 6, (bit // 2) * 6
            for y in range(3):
                for x in range(3):
                    img.putpixel((x0 + dx + x, y0 + dy + y), INK if slot >> bit & 1 else SHADOW)
    return img


def encode(text: str) -> list[int]:
    ids = cells()
    ids[" "], ids[")"] = 0, ids["("]
    return [-1 if c == "\n" else ids[c] for c in text]


def render(text: str, font: Image.Image, scale: int = 3) -> Image.Image:
    lines = text.split("\n")
    w = max(len(l) for l in lines) * 16 + 8
    h = len(lines) * 24 + 8
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    colours = {1: (74, 74, 74), 2: (189, 189, 189)}
    px = font.load()
    for row, line in enumerate(lines):
        for col, slot in enumerate(encode(line)):
            for y in range(16):
                for x in range(16):
                    v = px[slot % 16 * 16 + x, slot // 16 * 16 + y]
                    if v in colours:
                        canvas.putpixel((4 + col * 16 + x, 4 + row * 24 + y), colours[v])
    return canvas.resize((w * scale, h * scale), Image.NEAREST)


def preview() -> None:
    from PIL import ImageDraw
    OUT.mkdir(exist_ok=True)
    before, after = draw_braille(), draw_aurebesh()
    samples = ["DIG HERE.", "OPEN A DOOR.\nAN ETERNAL\nCOMPANION\nWAITS.", "ABCDEFGHIJKLM\nNOPQRSTUVWXYZ\n.,!?:;-/('\""]
    blocks = [(render(s, before), render(s, after), s) for s in samples]
    w = max(b.width + a.width for b, a, _ in blocks) + 60
    h = sum(max(b.height, a.height) + 40 for b, a, _ in blocks) + 40
    sheet = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "Braille (before)  vs  Aurebesh (after), 3x", fill=(0, 0, 0))
    y = 36
    for b, a, s in blocks:
        d.text((10, y), s.replace("\n", " / "), fill=(90, 90, 90))
        sheet.paste(b, (10, y + 16))
        sheet.paste(a, (b.width + 40, y + 16))
        y += max(b.height, a.height) + 40
    sheet.save(OUT / "aurebesh_before_after.png")

    # every letter next to the chart glyph it was drawn from
    import string
    tiles = []
    for ch in string.ascii_uppercase:
        ref = Image.open(REFS / f"{ch.lower()}_glyph.png").convert("RGBA")
        bg = Image.new("RGBA", ref.size, (255, 255, 255, 255))
        ref = Image.alpha_composite(bg, ref).convert("RGB")
        ref = ref.crop(ref.convert("L").point(lambda v: 255 if v < 128 else 0).getbbox())
        ref.thumbnail((96, 72))
        tiles.append((ch, ref, render(ch, after, 6)))
    cw, chh = 230, 120
    chart = Image.new("RGB", (cw * 6, chh * 5), (255, 255, 255))
    d = ImageDraw.Draw(chart)
    for i, (ch, ref, glyph) in enumerate(tiles):
        x, y = i % 6 * cw, i // 6 * chh
        d.text((x + 6, y + 6), ch, fill=(0, 0, 0))
        chart.paste(ref, (x + 20, y + 20))
        chart.paste(glyph.crop((0, 0, 16 * 6 + 24, 22 * 6)), (x + 124, y))
    chart.save(OUT / "aurebesh_letters.png")
    print("wrote", OUT / "aurebesh_before_after.png", OUT / "aurebesh_letters.png")


def install() -> None:
    draw_aurebesh().save(FONT)
    print("installed", len(LETTERS), "Aurebesh letters into", FONT.relative_to(ROOT))


if __name__ == "__main__":
    {"preview": preview, "install": install}[sys.argv[1] if len(sys.argv) > 1 else "preview"]()

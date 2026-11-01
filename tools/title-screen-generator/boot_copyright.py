"""Boot copyright screen (graphics/intro/copyright.png + copyright.bin).

Keeps the vanilla "©2005 Pokémon." and "©1995-2005 Nintendo" rows, drops
Creatures and GAME FREAK, and adds a STAR WARS row and a Lucasfilm row drawn
in the same thin font the vanilla Creatures / GAME FREAK lines use (glyphs
below are copied pixel for pixel from those lines; S T W L f l m d & ™ 7 are
new glyphs drawn to match).

Idempotent: rows 6 and 8 are read back from the current png/bin, rows 10 and
12 are rebuilt from the glyphs here. Run from the repo root:
    python3 tools/title-screen-generator/boot_copyright.py
"""
import os
import struct
import sys

from PIL import Image

GAME = os.path.join(os.path.dirname(__file__), "..", "..", "game")
PNG = os.path.join(GAME, "graphics/intro/copyright.png")
BIN = os.path.join(GAME, "graphics/intro/copyright.bin")

LINE3_PREFIX = "©1977-2005"
LINE3_TEXT = "STAR WARS"
LINE4_PREFIX = "©&™2005"
LINE4_TEXT = "Lucasfilm Ltd."

# Palette indices of the vanilla strip: 1 = background, 9/10 = anti-alias
# greys, 13 = mid grey, 15 = white.
PIX = {".": 1, "a": 9, "b": 10, "D": 13, "F": 15}

# Uppercase/digits occupy rows 1-7 of the 8px strip, lowercase x-height rows 3-7.
G = {
    # --- copied from the vanilla strip ---
    "©": ["..DFFD..", ".F....F.", "D.aFFb.D", "F.F....F", "F.F....F", "D.aFFb.D", ".F....F.", "..DFFD.."],
    "1": ["", ".F", "FF", ".F", ".F", ".F", ".F", ".F"],
    "9": ["", "bFFb", "F..F", "F..F", "bFFF", "...F", "..bF", "FFFb"],
    "2": ["", "bFFb", "F..F", "...F", "..Fb", ".Fb.", "Fb..", "FFFF"],
    "0": ["", "bFFb", "F..F", "F..F", "F..F", "F..F", "F..F", "bFFb"],
    "5": ["", "FFFF", "F...", "F...", "FFFb", "...F", "...F", "FFFb"],
    "-": ["", "", "", "", "FFF", "", "", ""],
    "A": ["", "..FD..", "..FF..", ".F.aD.", ".F..F.", ".FFFFD", "Fa..aF", "F....F"],
    "R": ["", "FFFFa.", "F...F.", "F...F.", "FFFFa.", "F..F..", "F..aF.", "F...Fa"],
    "a": ["", "", "", "FFFa", "...F", "aFFF", "F..F", "aFFF"],
    "s": ["", "", "", "aFFF", "F...", "aFFa", "...F", "FFFa"],
    "c": ["", "", "", "aFFa", "F..F", "F...", "F..F", "aFFa"],
    "u": ["", "", "", "F..F", "F..F", "F..F", "F..F", "aFFF"],
    "t": ["", "", ".F.", "FFF", ".F.", ".F.", ".F.", ".F."],
    "i": ["", "F", "", "F", "F", "F", "F", "F"],
    ".": ["", "", "", "", "", "", "", "F"],
    # --- new, drawn to match ---
    "7": ["", "FFFF", "...F", "..Fb", "..F.", ".Fb.", ".F..", ".F.."],
    "S": ["", "aFFFa", "Fa..F", "F....", "aFFFa", "....F", "F..aF", "aFFFa"],
    "T": ["", "FFFFF", "..F..", "..F..", "..F..", "..F..", "..F..", "..F.."],
    "W": ["", "F....F", "F....F", "F....F", "F.DD.F", "FDFFDF", "FF..FF", "F....F"],
    "L": ["", "F...", "F...", "F...", "F...", "F...", "F...", "FFFF"],
    "f": ["", ".aF", ".F.", "FFF", ".F.", ".F.", ".F.", ".F."],
    "l": ["", "F", "F", "F", "F", "F", "F", "F"],
    "m": ["", "", "", "F.Fa.Fa", "FF.FF.F", "F..F..F", "F..F..F", "F..F..F"],
    "d": ["", "...F", "...F", "aFFF", "F..F", "F..F", "F..F", "aFFF"],
    "&": ["", ".aFa.", ".F.F.", ".aFa.", "aFa.F", "F.aFa", "F..F.", "aFFaF"],
    "™": ["", "FFF.F...F", ".F..FF.FF", ".F..F.F.F", ".F..F...F", "", "", ""],
}
SPACE = 3  # blank columns for a space, as between "Creatures" and "Inc."


def render(text):
    cols = []
    for i, ch in enumerate(text):
        if ch == " ":
            cols += [[1] * 8 for _ in range(SPACE)]
            continue
        g = G[ch]
        w = max(len(r) for r in g)
        for x in range(w):
            cols.append([PIX[g[y][x]] if x < len(g[y]) else 1 for y in range(8)])
        if i < len(text) - 1 and text[i + 1] != " ":
            cols.append([1] * 8)
            if ch == "-" or text[i + 1] == "-":  # vanilla puts 2 blank cols around the dash
                cols.append([1] * 8)
    return cols


def prefix_line(prefix):
    if prefix == "©&™2005":
        # © & ™ spaced out so "2005" sits in the same columns as the rows above
        cols = render("©") + [[1] * 8] + render("&") + [[1] * 8, [1] * 8] + render("™")
        cols += [[1] * 8] * (33 - len(cols)) + render("2005")
    else:
        cols = render(prefix[0]) + [[1] * 8] + render(prefix[1:])
    return cols


def build_line(prefix, text):
    cols = prefix_line(prefix)
    assert len(cols) <= 57, (prefix, len(cols))
    cols += [[1] * 8] * (57 - len(cols)) + render(text)
    W = 23 * 8
    assert len(cols) <= W, (text, len(cols))
    cols += [[1] * 8] * (W - len(cols))
    return [[cols[x][y] for x in range(W)] for y in range(8)]


def main():
    im = Image.open(PNG)
    pal = im.getpalette()
    tm = list(struct.unpack("<1024H", open(BIN, "rb").read()))
    tile = lambda t: tuple(im.getpixel((t * 8 + x, y)) for y in range(8) for x in range(8))

    rows = {}
    for r in (6, 8):  # Pokémon, Nintendo: keep vanilla pixels
        ts = [tm[r * 32 + c] & 0x3FF for c in range(7, 30)]
        rows[r] = [[tile(t)[y * 8 + x] for t in ts for x in range(8)] for y in range(8)]
    rows[10] = build_line(LINE3_PREFIX, LINE3_TEXT)
    rows[12] = build_line(LINE4_PREFIX, LINE4_TEXT)

    tiles = [tile(0), tile(1)]  # 0 = unused, 1 = blank background
    index = {t: i for i, t in enumerate(tiles)}
    new_tm = [(1 if (v & 0x3FF) else 0) for v in tm]  # blank everything, keep 0-columns
    for r, px in rows.items():
        for c in range(23):
            t = tuple(px[y][c * 8 + x] for y in range(8) for x in range(8))
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            new_tm[r * 32 + 7 + c] = index[t]

    out = Image.new("P", (len(tiles) * 8, 8))
    out.putpalette(pal[:48])
    for i, t in enumerate(tiles):
        for y in range(8):
            for x in range(8):
                out.putpixel((i * 8 + x, y), t[y * 8 + x])
    out.save(PNG, bits=4)
    open(BIN, "wb").write(struct.pack("<1024H", *new_tm))
    print(f"wrote {PNG} ({len(tiles)} tiles) and {BIN}")

    if "--preview" in sys.argv:
        prev = Image.new("P", (240, 160), 1)
        prev.putpalette(pal)
        for r in range(20):
            for c in range(30):
                t = tiles[new_tm[r * 32 + c] & 0x3FF]
                for y in range(8):
                    for x in range(8):
                        prev.putpixel((c * 8 + x, r * 8 + y), t[y * 8 + x])
        path = sys.argv[sys.argv.index("--preview") + 1]
        prev.convert("RGB").resize((480, 320), Image.NEAREST).save(path)
        print("preview", path)


if __name__ == "__main__":
    main()

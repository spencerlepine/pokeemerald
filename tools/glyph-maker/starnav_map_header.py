"""Redraw the StarNAV map's left header: HOENN MAP -> STAR MAP.

The label (graphics/pokenav/left_headers/hoenn_map.png) is an image: its letters are pixels, not font text.
This rebuilds it from Emerald's (read from git, commit b532c32e). A, M and P are the label's own letters; S, T
and R are drawn in the same 5x9 style, with the shadow to the right and below. FULL VIEW and ZOOM VIEW stay.
GALAXY MAP (the wiki's wish) is 10 letters and does not fit the 52 px label; STAR MAP does.

    python3 starnav_map_header.py preview   # out/starnav_map_header.png (before | after, 4x)
    python3 starnav_map_header.py install   # writes ../../game/graphics/pokenav/left_headers/hoenn_map.png
"""
import io
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
VANILLA_REV = 'b532c32e'
PATH = 'game/graphics/pokenav/left_headers/hoenn_map.png'
INK, SHADOW, FILL = 1, 2, 8
TOP, ROWS = 7, 9                      # the label's letters: rows 7-15, shadow on row 16
LEFT, RIGHT = 4, 54                   # where Emerald's label sits (x 4-53)
PITCH, SPACE = 6, 3

DRAWN = {
    'S': [".111.", "1...1", "1....", "1....", ".111.", "....1", "....1", "1...1", ".111."],
    'T': ["11111", "..1..", "..1..", "..1..", "..1..", "..1..", "..1..", "..1..", "..1.."],
    'R': ["1111.", "1...1", "1...1", "1...1", "1111.", "1.1..", "1..1.", "1...1", "1...1"],
}
EMERALD_X = {'M': 37, 'A': 43, 'P': 49}   # x of each letter in HOENN MAP


def vanilla():
    data = subprocess.run(['git', '-C', ROOT, 'show', f'{VANILLA_REV}:{PATH}'], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(data))


def glyph(im, ch):
    if ch in DRAWN:
        return [[c == '1' for c in row] for row in DRAWN[ch]]
    px, x0 = im.load(), EMERALD_X[ch]
    return [[px[x0 + x, TOP + y] == INK for x in range(5)] for y in range(ROWS)]


def build(text="STAR MAP"):
    im = vanilla()
    out = im.copy()
    px = out.load()
    for y in range(TOP, TOP + ROWS + 1):          # clear the old label
        for x in range(LEFT, RIGHT + 1):
            px[x, y] = FILL
    width = sum(SPACE if c == ' ' else PITCH for c in text) - 1
    x = LEFT + (RIGHT - LEFT - width) // 2
    ink = set()
    for c in text:
        if c == ' ':
            x += SPACE
            continue
        for gy, row in enumerate(glyph(im, c)):
            for gx, on in enumerate(row):
                if on:
                    ink.add((x + gx, TOP + gy))
        x += PITCH
    for (ix, iy) in ink:                          # shadow right, below and down-right, under the ink
        for sx, sy in ((ix + 1, iy), (ix, iy + 1), (ix + 1, iy + 1)):
            if (sx, sy) not in ink:
                px[sx, sy] = SHADOW
    for (ix, iy) in ink:
        px[ix, iy] = INK
    return im, out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    before, after = build()
    if cmd == 'install':
        after.save(os.path.join(ROOT, PATH))
        print('wrote', PATH)
    else:
        os.makedirs(os.path.join(os.path.dirname(__file__), 'out'), exist_ok=True)
        sheet = Image.new('RGB', (64 * 2 + 4, 96), (0, 0, 0))
        sheet.paste(before.convert('RGB'), (0, 0))
        sheet.paste(after.convert('RGB'), (68, 0))
        p = os.path.join(os.path.dirname(__file__), 'out', 'starnav_map_header.png')
        sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(p)
        print(p)

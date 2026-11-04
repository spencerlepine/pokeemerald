"""Redraw the Datapad's HOENN label: HOENN -> REGIONAL.

When the national Datapad is unlocked, the list screen shows two count labels, HOENN and NATIONAL. They are
32x8 sprite frames in graphics/pokedex/interface.png, so their letters are pixels. OUTER RIM does not fit in
32 px in this tiny font, so the label says REGIONAL, the partner of NATIONAL. IONAL is copied from NATIONAL
(same letters, same place); R, E and G are drawn in the same 3x7 style with the shadow right and below.
The base is Emerald's sheet (read from git, commit b532c32e).

    python3 datapad_dex_label.py preview   # out/datapad_dex_label.png (before above, after below, 4x)
    python3 datapad_dex_label.py install   # writes ../../game/graphics/pokedex/interface.png
"""
import io
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
VANILLA_REV = 'b532c32e'
PATH = 'game/graphics/pokedex/interface.png'
INK, SHADOW, CLEAR = 1, 15, 0
HOENN_Y, NATIONAL_Y = 324, 340        # top row of each label's letters (7 rows, shadow on the 8th)
ROWS = 7
KEEP_FROM = 13                        # NATIONAL's "IONAL" starts at x 13
DRAWN = {                             # x of the left column, 3x7 glyph
    'R': (1, ["##.", "#.#", "#.#", "##.", "#.#", "#.#", "#.#"]),
    'E': (5, ["###", "#..", "#..", "###", "#..", "#..", "###"]),
    'G': (9, [".##", "#..", "#..", "#.#", "#.#", "#.#", ".##"]),
}


def vanilla():
    data = subprocess.run(['git', '-C', ROOT, 'show', f'{VANILLA_REV}:{PATH}'], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(data))


def build():
    im = vanilla()
    out = im.copy()
    px = out.load()
    for y in range(HOENN_Y, HOENN_Y + ROWS + 1):  # clear HOENN
        for x in range(32):
            px[x, y] = CLEAR
    for y in range(ROWS + 1):                      # IONAL from NATIONAL
        for x in range(KEEP_FROM, 32):
            px[x, HOENN_Y + y] = px[x, NATIONAL_Y + y]
    ink = set()
    for x0, rows in DRAWN.values():
        for gy, row in enumerate(rows):
            for gx, c in enumerate(row):
                if c == '#':
                    ink.add((x0 + gx, HOENN_Y + gy))
    for (ix, iy) in ink:                           # shadow right, below and down-right
        for sx, sy in ((ix + 1, iy), (ix, iy + 1), (ix + 1, iy + 1)):
            if (sx, sy) not in ink and px[sx, sy] == CLEAR:
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
        sheet = Image.new('RGB', (32, 26), (0, 0, 0))
        sheet.paste(before.crop((0, HOENN_Y - 1, 32, HOENN_Y + 8)).convert('RGB'), (0, 0))
        sheet.paste(after.crop((0, HOENN_Y - 1, 32, HOENN_Y + 8)).convert('RGB'), (0, 9))
        sheet.paste(after.crop((0, NATIONAL_Y - 1, 32, NATIONAL_Y + 8)).convert('RGB'), (0, 18))
        p = os.path.join(os.path.dirname(__file__), 'out', 'datapad_dex_label.png')
        sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(p)
        print(p)

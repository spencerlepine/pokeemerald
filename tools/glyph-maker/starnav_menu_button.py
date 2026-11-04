"""Redraw the StarNAV main menu's map button: HOENN MAP -> STAR MAP.

The button (graphics/pokenav/options/hoenn_map.png) is four 32x16 sprite frames that sit side by side in the
game, so its label is pixels, not font text. This rebuilds it from Emerald's (read from git, commit b532c32e)
with the same letters as the map strip (starnav_map_header.py): M, A and P are the button's own, S, T and R
are drawn. The label stays left-aligned after the green light, like the other buttons.

    python3 starnav_menu_button.py preview   # out/starnav_menu_button.png (before above, after below, 4x)
    python3 starnav_menu_button.py install   # writes ../../game/graphics/pokenav/options/hoenn_map.png
"""
import io
import os
import subprocess
import sys

from PIL import Image

from starnav_map_header import DRAWN, PITCH, ROOT, SPACE, VANILLA_REV

PATH = 'game/graphics/pokenav/options/hoenn_map.png'
INK, SHADOW, FILL = 1, 2, 4
TOP, ROWS = 4, 9                      # letters on rows 4-12 of the strip, shadow on row 13
LEFT, RIGHT = 16, 126                 # the label area after the green light
EMERALD_X = {'M': 49, 'A': 55, 'P': 61}
FRAMES = 4                            # 32x16 frames stacked in the PNG, laid out left to right in the game


def vanilla():
    data = subprocess.run(['git', '-C', ROOT, 'show', f'{VANILLA_REV}:{PATH}'], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(data))


def to_strip(im):
    s = Image.new('P', (32 * FRAMES, 16))
    s.putpalette(im.getpalette())
    for f in range(FRAMES):
        s.paste(im.crop((0, f * 16, 32, f * 16 + 16)), (f * 32, 0))
    return s


def from_strip(s, like):
    im = like.copy()
    for f in range(FRAMES):
        im.paste(s.crop((f * 32, 0, f * 32 + 32, 16)), (0, f * 16))
    return im


def glyph(strip, ch):
    if ch in DRAWN:
        return [[c == '1' for c in row] for row in DRAWN[ch]]
    px, x0 = strip.load(), EMERALD_X[ch]
    return [[px[x0 + x, TOP + y] == INK for x in range(5)] for y in range(ROWS)]


def build(text="STAR MAP"):
    im = vanilla()
    src = to_strip(im)
    out = src.copy()
    px = out.load()
    for y in range(TOP, TOP + ROWS + 1):          # clear the old label
        for x in range(LEFT, RIGHT + 1):
            px[x, y] = FILL
    x, ink = LEFT, set()
    for c in text:
        if c == ' ':
            x += SPACE
            continue
        for gy, row in enumerate(glyph(src, c)):
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
    return src, out, from_strip(out, im)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    before, after, png = build()
    if cmd == 'install':
        png.save(os.path.join(ROOT, PATH))
        print('wrote', PATH)
    else:
        os.makedirs(os.path.join(os.path.dirname(__file__), 'out'), exist_ok=True)
        sheet = Image.new('RGB', (128, 36), (0, 0, 0))
        sheet.paste(before.convert('RGB'), (0, 0))
        sheet.paste(after.convert('RGB'), (0, 20))
        p = os.path.join(os.path.dirname(__file__), 'out', 'starnav_menu_button.png')
        sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(p)
        print(p)

"""Render the 20 option-menu window frames from game/graphics/text_window into one sheet (screen 00).
python3 frames_sheet.py OUT.png"""
import sys, pathlib
from PIL import Image, ImageDraw
SRC = pathlib.Path(__file__).resolve().parent / '../../game/graphics/text_window'
W, H = 12, 5
sheet = Image.new('RGB', (4*(W*8*2+16)+16, 5*(H*8*2+28)+16), (30, 32, 40))
d = ImageDraw.Draw(sheet)
for n in range(1, 21):
    im = Image.open(SRC / f'{n}.png').convert('RGBA')
    t = lambda c, r: im.crop((c*8, r*8, c*8+8, r*8+8))
    box = Image.new('RGBA', (W*8, H*8), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            c = 0 if x == 0 else 2 if x == W-1 else 1
            r = 0 if y == 0 else 2 if y == H-1 else 1
            box.paste(t(c, r), (x*8, y*8))
    box = box.resize((W*16, H*16), Image.NEAREST)
    i = n-1; X = 16+(i % 4)*(W*16+16); Y = 16+(i//4)*(H*16+28)
    d.text((X, Y), f'Frame type {n}', fill=(230, 230, 230))
    sheet.paste(box, (X, Y+14), box)
sheet.save(sys.argv[1])

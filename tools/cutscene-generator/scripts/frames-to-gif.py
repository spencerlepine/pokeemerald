#!/usr/bin/env python3
"""Turn a folder of 240x160 screenshots into a small GIF that plays at the game's real speed.

    frames-to-gif.py FRAMES_DIR OUT.gif [--fps 20] [--scale 1] [--sheet SHEET.png] [--sheet-every 30]

GIF delays are whole centiseconds, so 20 fps (every 3rd game frame, 5 cs) is exact; 30 fps is
stored as 3/4 cs alternating. Frames are kept at 1x by default (the GBA's own resolution, which
any viewer can zoom) and share one palette, which keeps a 15 s scene around 1-3 MB.
The contact sheet is every Nth kept frame at 2x with its game frame number, for a quick look.
"""
import argparse, os, re, sys
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("frames"); ap.add_argument("out")
ap.add_argument("--fps", type=float, default=20); ap.add_argument("--scale", type=int, default=1)
ap.add_argument("--sheet"); ap.add_argument("--sheet-every", type=int, default=30)
a = ap.parse_args()

names = sorted(n for n in os.listdir(a.frames) if n.endswith(".png"))
if not names:
    sys.exit(f"no frames in {a.frames}")
ims = [Image.open(os.path.join(a.frames, n)).convert("RGB") for n in names]
if a.scale != 1:
    ims = [im.resize((im.width * a.scale, im.height * a.scale), Image.NEAREST) for im in ims]

# one shared palette from a sample of frames (GBA scenes rarely exceed 256 colors on screen)
sample = Image.new("RGB", (ims[0].width, ims[0].height * min(len(ims), 16)))
for i, im in enumerate(ims[:: max(1, len(ims) // 16)][:16]):
    sample.paste(im, (0, i * im.height))
pal = sample.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in ims]

cs = 100 / a.fps
durs, acc = [], 0.0
for i in range(len(q)):  # spread rounding so the total time is right
    acc += cs; d = round(acc) - sum(durs); durs.append(max(2, d))
q[0].save(a.out, save_all=True, append_images=q[1:], duration=[d * 10 for d in durs], loop=0, optimize=False, disposal=1)
print(f"{a.out}: {len(q)} frames, {sum(durs) / 100:.1f} s, {os.path.getsize(a.out) / 1e6:.2f} MB")

if a.sheet:
    picks = list(range(0, len(ims), a.sheet_every))
    cols = 4; rows = (len(picks) + cols - 1) // cols
    w, h = 240 * 2, 160 * 2
    sheet = Image.new("RGB", (cols * (w + 4) + 4, rows * (h + 18) + 4), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    for k, i in enumerate(picks):
        x, y = 4 + (k % cols) * (w + 4), 4 + (k // cols) * (h + 18)
        sheet.paste(Image.open(os.path.join(a.frames, names[i])).convert("RGB").resize((w, h), Image.NEAREST), (x, y + 14))
        d.text((x, y), "frame " + re.sub(r"\D", "", names[i]).lstrip("0"), fill=(220, 220, 220))
    sheet.save(a.sheet)
    print(f"{a.sheet}: {len(picks)} stills")

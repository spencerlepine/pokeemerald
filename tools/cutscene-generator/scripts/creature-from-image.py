#!/usr/bin/env python3
"""Turn a generated creature picture into intro scene 3 art: a 16-color sheet with the three poses
Emerald's camera cuts between, plus a palette include for the scene's .px.js.

    creature-from-image.py IN.png OUT_DIR --name krayt [--height 90] [--width 176] [--colors 14]
        [--anchors 293,1 117,121 37,353] [--poses "0,0,0 0,-6,-4 0,4,3"] [--glow]

IN.png is any picture on a plain background (a generated 768x768 is fine). The background is knocked
out from the border, the figure is cropped, scaled to fit --width x --height (Groudon was 172x90 at the
game's 1x zoom), quantized to --colors colors on GBA steps (index 0 transparent, 1 the outline), and
given a 1 px dark outline. With --glow, the brightest saturated color becomes index 15, which the game
pulses between blue and red (Groudon's veins). Each pose is the figure shifted and tilted
(dx,dy,degrees), drawn at its anchor on a 512x512 sheet.

Writes OUT_DIR/<name>_sheet.png (indexed, 512x512), OUT_DIR/<name>_pal.px.js (const <NAME>_PAL = [...])
and OUT_DIR/<name>_preview.png (the figure at 3x). The .px.js then does:
    include("<name>_pal.px.js"); ref("<name>_src", "<abs path>/<name>_sheet.png"); use(KRAYT_PAL); scene(..., stamp("<name>_src"))
"""
import argparse, colorsys, os, sys
from collections import deque
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--name", default="krayt")
ap.add_argument("--height", type=int, default=90); ap.add_argument("--width", type=int, default=176)
ap.add_argument("--colors", type=int, default=14, help="colors for the figure (1..14), outline uses index 1")
ap.add_argument("--anchors", nargs="+", default=["293,1", "117,121", "37,353"])
ap.add_argument("--poses", default="0,0,0 0,-6,-4 0,4,3", help="dx,dy,deg per anchor")
ap.add_argument("--glow", action="store_true", help="brightest saturated color -> index 15 (the game pulses it)")
ap.add_argument("--tol", type=int, default=48, help="background knock-out tolerance")
ap.add_argument("--flip", action="store_true", help="mirror so the head faces left")
a = ap.parse_args()

im = Image.open(a.src).convert("RGBA")
w, h = im.size
px = im.load()

# 1. knock out the background: flood from every border pixel, within tol of the corner color
corner = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
bg = tuple(sum(c[i] for c in corner) // 4 for i in range(3))
near = lambda p: all(abs(p[i] - bg[i]) <= a.tol for i in range(3))
seen = bytearray(w * h); q = deque()
for x in range(w):
    for y in (0, h - 1):
        if near(px[x, y]) and not seen[y * w + x]: seen[y * w + x] = 1; q.append((x, y))
for y in range(h):
    for x in (0, w - 1):
        if near(px[x, y]) and not seen[y * w + x]: seen[y * w + x] = 1; q.append((x, y))
while q:
    x, y = q.popleft(); px[x, y] = (0, 0, 0, 0)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        xx, yy = x + dx, y + dy
        if 0 <= xx < w and 0 <= yy < h and not seen[yy * w + xx] and near(px[xx, yy]):
            seen[yy * w + xx] = 1; q.append((xx, yy))

# 2. crop and scale
box = im.getbbox()
if not box: sys.exit("nothing left after knocking out the background")
fig = im.crop(box)
if a.flip: fig = fig.transpose(Image.FLIP_LEFT_RIGHT)
s = min(a.width / fig.width, a.height / fig.height)
fig = fig.resize((max(1, round(fig.width * s)), max(1, round(fig.height * s))), Image.LANCZOS)
# hard alpha
fig = Image.composite(fig, Image.new("RGBA", fig.size, (0, 0, 0, 0)), fig.getchannel("A").point(lambda v: 255 if v > 127 else 0))

# 3. quantize the opaque pixels
opaque = fig.convert("RGB")
mask = fig.getchannel("A")
n = max(1, min(a.colors, 14 if a.glow else 14))
q = opaque.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
qpal = q.getpalette()[: n * 3]
cols = [tuple((qpal[i * 3 + k] >> 3) << 3 for k in range(3)) for i in range(n)]
# order: darkest first (index 1 doubles as the outline); the glow color, if any, goes to 15
lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
order = sorted(range(n), key=lambda i: lum(cols[i]))
glow = None
if a.glow:
    def sat(c):
        hh, ss, vv = colorsys.rgb_to_hsv(*(v / 255 for v in c)); return ss * vv
    glow = max(order, key=lambda i: sat(cols[i]))
    order = [i for i in order if i != glow]
pal = [(0, 0, 0)] * 16
remap = {}
for slot, i in enumerate(order, start=1): pal[slot] = cols[i]; remap[i] = slot
if glow is not None: pal[15] = cols[glow]; remap[glow] = 15
if lum(pal[1]) > 64:  # make sure the outline reads dark
    pal[1] = tuple(v // 3 for v in pal[1])

fw, fh = fig.size
out = Image.new("P", (fw + 2, fh + 2), 0)
flat = []
for c in pal: flat += list(c)
out.putpalette(flat + [0] * (768 - 48))
op = out.load(); qp = q.load(); mp = mask.load()
for y in range(fh):
    for x in range(fw):
        if mp[x, y]: op[x + 1, y + 1] = remap[qp[x, y]]
# 4. outline: index 1 around the figure
src = out.copy(); sp = src.load()
for y in range(fh + 2):
    for x in range(fw + 2):
        if sp[x, y]: continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < fw + 2 and 0 <= yy < fh + 2 and sp[xx, yy]: op[x, y] = 1; break

# 5. the sheet with the poses
sheet = Image.new("P", (512, 512), 0); sheet.putpalette(flat + [0] * (768 - 48))
poses = [tuple(float(v) for v in p.split(",")) for p in a.poses.split()]
for k, anc in enumerate(a.anchors):
    ax, ay = (int(v) for v in anc.split(","))
    dx, dy, deg = poses[k] if k < len(poses) else (0, 0, 0)
    pose = out.rotate(deg, resample=Image.NEAREST, expand=True, fillcolor=0) if deg else out
    sheet.paste(pose, (ax + int(dx), ay + int(dy)))

os.makedirs(a.out, exist_ok=True)
sheet.save(os.path.join(a.out, f"{a.name}_sheet.png"))
out.convert("RGBA").resize(((fw + 2) * 3, (fh + 2) * 3), Image.NEAREST).save(os.path.join(a.out, f"{a.name}_preview.png"))
with open(os.path.join(a.out, f"{a.name}_pal.px.js"), "w") as f:
    f.write(f"// written by scripts/creature-from-image.py from {os.path.basename(a.src)}\n")
    f.write(f"const {a.name.upper()}_PAL = [" + ", ".join('"#%02x%02x%02x"' % c for c in pal) + "]\n")
print(f"{a.name}: figure {fw + 2}x{fh + 2}, {n} colors" + (f", glow index 15 = #%02x%02x%02x" % pal[15] if glow is not None else ""))

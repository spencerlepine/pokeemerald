import sys, numpy as np
from PIL import Image
from pathlib import Path
# glyph (black on transparent) -> 96 native creature start: slate body, light top edge, dark outline, one eye
src, out, width = sys.argv[1], sys.argv[2], int(sys.argv[3])
g = Image.open(src).convert("RGBA"); g = g.crop(g.getbbox())
k = min(width / g.width, 52 / g.height)
g = g.resize((max(1, round(g.width * k)), max(1, round(g.height * k))), Image.LANCZOS)
m = np.array(g)[..., 3] > 100
h, w = m.shape
# eye at the deepest point (simple chamfer distance)
d = m.astype(int) * 99
for _ in range(2):
    for y in range(h):
        for x in range(w):
            if m[y, x]:
                n = [d[y-1, x] if y else 0, d[y, x-1] if x else 0]
                d[y, x] = min(d[y, x], min(n) + 1)
    for y in range(h-1, -1, -1):
        for x in range(w-1, -1, -1):
            if m[y, x]:
                n = [d[y+1, x] if y < h-1 else 0, d[y, x+1] if x < w-1 else 0]
                d[y, x] = min(d[y, x], min(n) + 1)
cy, cx = np.argwhere(m).mean(0)
cand = np.argwhere(d >= d.max() - 1)
ey, ex = cand[np.argmin(((cand - (cy, cx)) ** 2).sum(1))]
r = 4
pad=6
ey, ex = ey + pad - 1, ex + pad - 1
m = np.pad(m, pad - 1); h, w = m.shape; d = np.pad(d, pad - 1)
a = np.zeros((h + 2, w + 2, 3), np.uint8); a[:] = 255
mm = np.pad(m, 1)
body = np.array([60, 62, 78]); hi = np.array([110, 112, 132]); ol = np.array([20, 20, 28])
a[mm] = body
top = mm & ~np.roll(mm, 1, 0)
a[top] = hi
ring = ~mm & (np.roll(mm, 1, 0) | np.roll(mm, -1, 0) | np.roll(mm, 1, 1) | np.roll(mm, -1, 1))
a[ring] = ol
yy, xx = np.mgrid[:h + 2, :w + 2]
eye = (yy - ey - 1) ** 2 + (xx - ex - 1) ** 2 <= r * r
dd = (yy - ey - 1) ** 2 + (xx - ex - 1) ** 2
a[dd <= (r + 1) ** 2] = ol
a[dd <= r * r] = (240, 240, 240)
a[dd <= 2 ** 2] = (20, 20, 28)
canvas = np.full((96, 96, 3), 255, np.uint8)
oy, ox = (96 - a.shape[0]) // 2, (96 - a.shape[1]) // 2
canvas[oy:oy + a.shape[0], ox:ox + a.shape[1]] = a
Image.fromarray(canvas).resize((768, 768), Image.NEAREST).save(out)

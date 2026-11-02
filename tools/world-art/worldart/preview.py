"""Review images: the object at 1x on the planet's ground tones, at 3x, and at 6x with the cell
grid, the footprint rows (red) and each foot (blue). Judge it at 1x and 3x; that is what players see."""
import numpy as np
from PIL import Image, ImageDraw

GROUNDS = {"endor": [(112, 152, 104), (88, 128, 88), (192, 112, 88)],
           "common": [(112, 200, 160), (96, 176, 136), (216, 184, 128)]}


def speckled(w, h, base, seed=1):
    """A flat ground with sparse specks in a darker tone (STYLE 5), as a background for previews."""
    rng = np.random.default_rng(seed)
    a = np.zeros((h, w, 3), np.uint8)
    a[:] = base
    dark = tuple(max(c - 24, 0) for c in base)
    m = rng.random((h, w)) < 0.06
    a[m] = dark
    return Image.fromarray(a)


def grid_image(img, obj, scale=6):
    W, H = obj.size
    big = img.resize((W * scale, H * scale), Image.NEAREST).convert("RGBA")
    d = ImageDraw.Draw(big)
    for x in range(0, W + 1, 16):
        d.line([(x * scale, 0), (x * scale, H * scale)], fill=(255, 220, 0, 160))
    for y in range(0, H + 1, 16):
        d.line([(0, y * scale), (W * scale, y * scale)], fill=(255, 220, 0, 160))
    for x in range(0, W + 1, 8):
        d.line([(x * scale, 0), (x * scale, H * scale)], fill=(255, 220, 0, 60))
    for y in range(0, H + 1, 8):
        d.line([(0, y * scale), (W * scale, y * scale)], fill=(255, 220, 0, 60))
    fp = obj.footprint_rows()
    for r in fp:
        d.rectangle([(1, r * 16 * scale + 1), (W * scale - 2, (r + 1) * 16 * scale - 2)], outline=(255, 40, 40, 255), width=2)
    for inst in obj.instances:
        fx, fy = inst.foot
        d.ellipse([(fx * scale - 4, fy * scale - 4), (fx * scale + 4, fy * scale + 4)], fill=(40, 120, 255, 255))
    return big


def review_sheet(img, obj, ground_key):
    W, H = obj.size
    grounds = GROUNDS.get(ground_key, GROUNDS["common"])
    pad = 8
    row1_h = H + pad * 2
    tiles = []
    for base in grounds:
        g = speckled(W + pad * 2, row1_h, base)
        g.paste(img, (pad, pad), img)
        tiles.append(g)
    one = Image.new("RGB", (sum(t.width for t in tiles) + pad * (len(tiles) - 1), row1_h), (30, 30, 30))
    x = 0
    for t in tiles:
        one.paste(t, (x, 0))
        x += t.width + pad
    three = speckled((W + pad * 2) * 3, row1_h * 3, grounds[0]).resize(((W + pad * 2) * 3, row1_h * 3), Image.NEAREST)
    three.paste(img.resize((W * 3, H * 3), Image.NEAREST), (pad * 3, pad * 3), img.resize((W * 3, H * 3), Image.NEAREST))
    base = speckled(W, H, grounds[0]).convert("RGBA")
    base.alpha_composite(img)
    g6 = grid_image(base, obj, 6)
    width = max(one.width, three.width + 12 + g6.width)
    sheet = Image.new("RGB", (width, one.height + 12 + max(three.height, g6.height)), (30, 30, 30))
    sheet.paste(one, (0, 0))
    sheet.paste(three, (0, one.height + 12))
    sheet.paste(g6, (three.width + 12, one.height + 12), g6)
    return sheet

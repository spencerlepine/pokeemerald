"""Pixel-art effects on 1-bit masks: outlines, bevels, gradients, shadows, arches."""
from PIL import Image, ImageChops, ImageFilter


def dilate(m, r=1, diag=True):
    out = m
    for _ in range(r):
        if diag:
            out = out.filter(ImageFilter.MaxFilter(3))
        else:
            sh = [ImageChops.offset(out, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            for s in sh:
                out = ImageChops.lighter(out, s)
    return out


def shift(m, dx, dy):
    out = Image.new("L", m.size, 0)
    out.paste(m, (dx, dy))
    return out


def sub(a, b):
    return ImageChops.subtract(a, b)


def pad(m, p):
    out = Image.new("L", (m.size[0] + 2 * p, m.size[1] + 2 * p), 0)
    out.paste(m, (p, p))
    return out


def arch(m, rise):
    """Bend a wordmark into an arch: the middle columns rise by `rise` px (the Pokémon logo trick)."""
    w, h = m.size
    out = Image.new("L", (w, h + rise), 0)
    for x in range(w):
        t = (x - w / 2) / (w / 2)
        dy = round(rise * (t * t))
        out.paste(m.crop((x, 0, x + 1, h)), (x, dy))
    return out


def paint(canvas, mask, color):
    canvas.paste(Image.new("RGBA", canvas.size, color + (255,)), (0, 0), mask)


def gradient_fill(canvas, mask, stops, top=None, bottom=None):
    """Hard-banded vertical gradient over the mask's bounding rows. stops: list of colours top->bottom."""
    bb = mask.getbbox()
    if not bb:
        return
    y0 = bb[1] if top is None else top
    y1 = bb[3] if bottom is None else bottom
    n = len(stops)
    for i, c in enumerate(stops):
        a = y0 + (y1 - y0) * i // n
        b = y0 + (y1 - y0) * (i + 1) // n
        band = Image.new("L", mask.size, 0)
        band.paste(255, (0, a, mask.size[0], b))
        paint(canvas, ImageChops.multiply(mask, band), c)


def edge(mask, dx, dy):
    """Pixels of mask whose neighbour at (dx,dy) is outside the mask."""
    return sub(mask, shift(mask, -dx, -dy))

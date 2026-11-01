"""Three KYBER VERSION banners (128x32 sprite, 15 colours + transparent)."""
from PIL import Image, ImageDraw
from glyphs import big_mask, small_mask
from fx import *
from logo import hexc

W, H = 128, 32

def _place(img, layer, x, y):
    img.paste(layer, (x, y), layer)

def word(mask, outline, fill, hi, lo, glow=None, shadow=None):
    p = 2 if glow is None else 3
    m = pad(mask, p)
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    if shadow:
        paint(out, shift(dilate(m, 1), 1, 1), hexc(shadow))
    if glow:
        paint(out, dilate(m, 2), hexc(glow))
    paint(out, dilate(m, 1), hexc(outline))
    gradient_fill(out, m, [hexc(c) for c in fill])
    if hi:
        paint(out, edge(m, 0, -1), hexc(hi))
    if lo:
        paint(out, edge(m, 0, 1), hexc(lo))
    return out

def version_mask():
    m = small_mask("VERSION", 1)
    return m.resize((m.size[0] * 2, m.size[1]), Image.NEAREST)  # wide like Emerald's VERSION

def compose(kyber, version, vx_shift=0, icon=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kx = (W - kyber.size[0]) // 2 + (6 if icon else 0)
    _place(img, kyber, kx, 0)
    if icon:
        _place(img, icon, kx - icon.size[0] + 2, 1)
    _place(img, version, (W - version.size[0]) // 2 + vx_shift, H - version.size[1])
    return img

def crystal_icon():
    """A small kyber crystal: elongated hexagon, faceted."""
    m = Image.new("L", (10, 22), 0); d = ImageDraw.Draw(m)
    d.polygon([(5, 0), (9, 5), (9, 16), (5, 21), (1, 16), (1, 5)], fill=255)
    out = Image.new("RGBA", (12, 24), (0, 0, 0, 0))
    mm = pad(m, 1)
    paint(out, dilate(mm, 1), hexc("06200e"))
    paint(out, mm, hexc("30c060"))
    left = Image.new("L", mm.size, 0); ImageDraw.Draw(left).polygon([(6, 1), (2, 6), (2, 17), (6, 22)], fill=255)
    paint(out, ImageChops.multiply(mm, left), hexc("a0ffc0"))
    paint(out, ImageChops.multiply(mm, shift(left, 2, 0)), hexc("60e890"))
    return out

from PIL import ImageChops

def banner_crystal():
    k = word(big_mask("KYBER", 3, 3), "06200e", ("e0fff0", "a0f8c0", "60e090", "30b868", "189048"), "ffffff", "0c6030")
    v = word(version_mask(), "101820", ("ffffff", "d0d8e0"), None, None)
    return compose(k, v, 10)

def banner_chrome():
    k = word(big_mask("KYBER", 3, 3), "10141c", ("ffffff", "e0e8f0", "b8c4d4", "8898b0", "a8b8cc"), "ffffff", "485870", shadow="000000")
    v = word(version_mask(), "301404", ("fff0a0", "f8c030", "d08818"), None, None)
    return compose(k, v, 10)

def banner_icon():
    k = word(big_mask("KYBER", 3, 3), "06200e", ("ffffff", "c8ffd8", "70e8a0", "38c070"), "ffffff", "107038")
    v = word(version_mask(), "06200e", ("c8ffd8", "70e8a0"), None, None)
    return compose(k, v, 4, icon=crystal_icon())

VARIANTS = {"crystal": banner_crystal, "chrome": banner_chrome, "icon": banner_icon}

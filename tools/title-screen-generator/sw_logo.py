"""Round 2 logo: stacked STAR / WARS wordmark (own pixel lettering, film-logo layout) in the Pokémon logo's
art style: yellow banded fill, blue outline, blue 3D extrusion, navy rim. KYBER VERSION sits between the lines."""
from PIL import Image, ImageDraw, ImageChops
from fx import dilate, shift, sub, paint, gradient_fill, edge, pad
from glyphs import big_mask, small_mask
from logo import hexc

S = 4          # supersample
LH = 26        # letter height in px
ST = 7         # stroke


def poly(d, pts, ox, fill=255):
    d.polygon([((x + ox) * S, y * S) for x, y in pts], fill=fill)


def cut_rect(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0):
    return [(x0 + tl, y0), (x1 - tr, y0), (x1, y0 + tr), (x1, y1 - br), (x1 - br, y1), (x0 + bl, y1), (x0, y1 - bl), (x0, y0 + tl)]


H = LH
M0, M1 = (H - ST) // 2, (H - ST) // 2 + ST      # middle bar rows


def g_S(d, ox, tail_left=0, tail_right=0):
    w = 28
    poly(d, cut_rect(0, 0, w + tail_right, ST, tl=5), ox)
    poly(d, cut_rect(0, 0, ST + 1, M1), ox)
    poly(d, cut_rect(0, M0, w, M1, bl=0), ox)
    poly(d, cut_rect(w - ST - 1, M0, w, H), ox)
    poly(d, cut_rect(-tail_left, H - ST, w, H, br=5), ox)
    return w


def g_T(d, ox):
    w = 28
    poly(d, cut_rect(0, 0, w, ST), ox)
    poly(d, cut_rect((w - ST - 2) / 2, 0, (w + ST + 2) / 2, H), ox)
    return w


def g_A(d, ox):
    w = 32
    poly(d, [(12, 0), (20, 0), (w, H), (w - ST - 2, H), (16, 8), (ST + 2, H), (0, H)], ox)
    return w


def g_R(d, ox):
    w = 28
    poly(d, cut_rect(0, 0, ST + 1, H), ox)
    poly(d, cut_rect(0, 0, w, ST, tr=5), ox)
    poly(d, cut_rect(w - ST - 1, 0, w, M1 + 1, tr=5, br=5), ox)
    poly(d, cut_rect(0, M0 + 1, w - 3, M1 + 1), ox)
    poly(d, [(11, M1), (19, M1), (w + 2, H), (w + 2 - ST - 3, H)], ox)
    return w + 2


def g_W(d, ox):
    w = 40
    poly(d, [(0, 0), (ST + 1, 0), (12, 15), (16, 3), (24, 3), (28, 15), (w - ST - 1, 0), (w, 0),
             (w - 7, H), (w - 15, H), (20, 12), (15, H), (7, H)], ox)
    return w


def word(letters, gap=3, left_pad=12, right_pad=12):
    img = Image.new("L", (240 * S, (H + 2) * S), 0)
    d = ImageDraw.Draw(img)
    x = left_pad
    for f, kw in letters:
        x += f(d, x, **kw) + gap
    m = img.resize((240, H + 2), Image.BOX).point(lambda v: 255 if v >= 128 else 0)
    bb = m.getbbox()
    return m.crop((bb[0], 0, bb[2], H))


def star():
    return word([(g_S, dict(tail_left=10)), (g_T, {}), (g_A, {}), (g_R, {})])


def wars():
    return word([(g_W, {}), (g_A, {}), (g_R, {}), (g_S, dict(tail_right=10))])


def arch(m, rise, up=True):
    w, h = m.size
    out = Image.new("L", (w, h + rise), 0)
    for x in range(w):
        t = (x - w / 2) / (w / 2)
        dy = round(rise * t * t) if up else round(rise * (1 - t * t))
        out.paste(m.crop((x, 0, x + 1, h)), (x, dy))
    return out


POKE = dict(fill=("fff6a0", "ffe838", "ffd800", "f8c800", "f0b400", "e0a000"), hi="fffce0", lo="b07800",
            outline="3a64d8", extrude="2848a8", rim="0c1a50")


# Kyber Gold (wiki/bible/PALETTE.md): black and yellow
KYBER_GOLD = dict(fill=("f8f0a0", "f8e050", "f8d000", "f8d000", "e0b000", "b88800"), hi="f8f8f0", lo="b88800",
                  outline="080808", outline_top="383838", extrude="604000", rim="080808")
KYBER_GOLD_B = dict(fill=("f8f0a0", "f8e050", "f8d000", "f8d000", "e0b000", "b88800"), hi="f8f8f0", lo="b88800",
                    outline="604000", outline_top="b88800", extrude="080808", rim="080808")


def style(m, c=POKE, depth=3):
    """Pokémon-logo treatment: banded yellow fill, 2px blue outline, blue extrusion down-right, navy rim."""
    m = pad(m, 4 + depth)
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    o = dilate(m, 2)
    ext = o
    for k in range(1, depth + 1):
        ext = ImageChops.lighter(ext, shift(o, k // 2, k))
    paint(out, dilate(ext, 1), hexc(c["rim"]))
    paint(out, ext, hexc(c["extrude"]))
    paint(out, o, hexc(c["outline"]))
    paint(out, sub(o, shift(o, 0, 1)), hexc(c.get("outline_top", "7898f0")))  # light top edge on the outline
    gradient_fill(out, m, [hexc(v) for v in c["fill"]])
    paint(out, edge(m, 0, -1), hexc(c["hi"]))
    paint(out, edge(m, 0, 1), hexc(c["lo"]))
    return out


# ---- middle subtitle (the 128x32 banner sprite) ----

def _word(mask, outline, fill, hi=None, lo=None, p=2):
    m = pad(mask, p)
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    paint(out, shift(dilate(m, 1), 1, 1), (0, 0, 0))
    paint(out, dilate(m, 1), hexc(outline))
    gradient_fill(out, m, [hexc(v) for v in fill])
    if hi:
        paint(out, edge(m, 0, -1), hexc(hi))
    if lo:
        paint(out, edge(m, 0, 1), hexc(lo))
    return out


def version_mask(xs=2):
    m = small_mask("VERSION", 1)
    return m.resize((m.size[0] * xs, m.size[1]), Image.NEAREST)


def kyber_version_line():
    """One line, black and white like Emerald's EMERALD VERSION banner: white-to-grey fill, black outline and shadow."""
    m = big_mask("KYBER VERSION", 3, 4)
    m = m.resize((m.size[0] // 2, m.size[1] // 2), Image.BOX).point(lambda v: 255 if v >= 128 else 0)
    m = pad(m, 2)
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    paint(out, shift(dilate(m, 1), 1, 1), hexc("080808"))
    paint(out, dilate(m, 1), hexc("080808"))
    gradient_fill(out, m, [hexc(c) for c in ("f8f8f8", "f8f8f8", "d8d8d8", "a8a8a8")])
    paint(out, edge(m, 0, -1), hexc("ffffff"))
    out = out.crop(out.getbbox())
    img = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    img.paste(out, ((128 - out.size[0]) // 2, (32 - out.size[1]) // 2), out)
    return img


def subtitle(kind):
    img = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    if kind == "green":
        k = _word(big_mask("KYBER", 3, 2), "06200e", ("e0fff0", "90f0b0", "48d080", "20a050"), "ffffff", "0c6030")
        v = _word(version_mask(), "06200e", ("ffffff", "d0e8d8"))
    elif kind == "silver":
        k = _word(big_mask("KYBER", 3, 2), "182030", ("ffffff", "e8eef4", "c0ccd8", "98a8bc"), "ffffff", "5c6c84")
        v = _word(version_mask(), "182030", ("ffffff", "d8dee8"))
    else:  # white on a dark plate, like the film subtitle
        k = _word(big_mask("KYBER", 3, 2), "0c1a50", ("ffffff", "ffffff", "e0e8f8"), None, "a8b8e0")
        v = _word(version_mask(), "0c1a50", ("ffe838", "f0b400"))
    img.paste(k, ((128 - k.size[0]) // 2, 0), k)
    img.paste(v, ((128 - v.size[0]) // 2, k.size[1] - 2), v)
    return img


def layout(top, sub_img, bottom, y_top=5, gap=3):
    y_top = min(y_top, 104 - 2 - (top.size[1] + sub_img.getbbox()[3] - sub_img.getbbox()[1] + bottom.size[1] - 6))
    """Logo layer (240x160 RGBA) with STAR on top, the subtitle sprite and WARS below. Returns (bg2, banner_xy)."""
    bg = Image.new("RGBA", (240, 160), (0, 0, 0, 0))
    bg.paste(top, ((240 - top.size[0]) // 2, y_top), top)
    sb = sub_img.getbbox()
    sy = y_top + top.size[1] - 4 + gap
    by = sy + (sb[3] - sb[1]) - 2 + gap
    bg.paste(bottom, ((240 - bottom.size[0]) // 2, by), bottom)
    return bg, (56, sy - sb[1]), by + bottom.size[1]


VARIANTS_R2 = {
    "flat-green": lambda: (style(star()), subtitle("green"), style(wars())),
    "flat-silver": lambda: (style(star()), subtitle("silver"), style(wars())),
    "arched-white": lambda: (style(arch(star(), 3, up=True)), subtitle("white"), style(arch(wars(), 3, up=False))),
}


VARIANTS = {
    "black-outline": lambda: (style(star(), KYBER_GOLD), kyber_version_line(), style(wars(), KYBER_GOLD)),
    "gold-outline": lambda: (style(star(), KYBER_GOLD_B), kyber_version_line(), style(wars(), KYBER_GOLD_B)),
}

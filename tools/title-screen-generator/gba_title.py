"""Render the title screen the way the GBA composes it (final state, after the logo slides in).

Layers (from src/title_screen.c):
  BG0  rayquaza.png + rayquaza.bin  (4bpp, palette 14, priority 3)
  BG1  clouds.png   + clouds.bin    (4bpp, priority 2), alpha-blended 6/16 over BG0 and the backdrop at 15/16
  BG2  pokemon_logo.png + .bin      (8bpp affine, priority 1), shown at screen x+29, y+0
  OBJ  emerald_version.png: two 64x32 halves centred at (98,66) and (162,66) -> top-left (66,50)
  OBJ  press_start.png strips: PRESS START centred at (128,108), copyright centred at (128,148)
"""
from PIL import Image
import struct, os

GAME = os.path.join(os.path.dirname(__file__), "..", "..", "game")
TS = os.path.join(GAME, "graphics", "title_screen")
W, H = 240, 160
LOGO_X, LOGO_Y = 29, 0
BANNER_XY = (66, 50)
PRESS_START_Y, COPYRIGHT_Y = 104, 144


def gba(c):
    """Quantise an RGB colour to 15-bit like the hardware does."""
    return tuple((v >> 3) << 3 for v in c[:3])


def read_jasc(path):
    lines = open(path).read().split()
    n = int(lines[2])
    return [tuple(int(v) for v in lines[3 + i * 3:6 + i * 3]) for i in range(n)]


def tiles_of(img, bpp_tile=8):
    w, h = img.size
    px = img.load()
    out = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            out.append([[px[tx * 8 + x, ty * 8 + y] for x in range(8)] for y in range(8)])
    return out


def text_bg(png, binf, pal):
    img = Image.open(png)
    tiles = tiles_of(img)
    data = open(binf, "rb").read()
    out = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    px = out.load()
    for i in range(min(1024, len(data) // 2)):
        e = struct.unpack_from("<H", data, i * 2)[0]
        t, hf, vf, p = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        if t >= len(tiles):
            continue
        tile = tiles[t]
        bx, by = (i % 32) * 8, (i // 32) * 8
        for y in range(8):
            for x in range(8):
                c = tile[7 - y if vf else y][7 - x if hf else x]
                if c:
                    px[bx + x, by + y] = gba(pal[p * 16 + c]) + (255,)
    return out


def affine_bg(png, binf, pal):
    img = Image.open(png)
    tiles = tiles_of(img)
    data = open(binf, "rb").read()
    out = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    px = out.load()
    for i, t in enumerate(data[:1024]):
        if t >= len(tiles):
            continue
        bx, by = (i % 32) * 8, (i // 32) * 8
        for y in range(8):
            for x in range(8):
                c = tiles[t][y][x]
                if c:
                    px[bx + x, by + y] = gba(pal[c]) + (255,)
    return out


def sprite_rgba(img):
    """Indexed sprite -> RGBA with index 0 transparent."""
    img = img.convert("P") if img.mode != "P" else img
    pal = img.getpalette()
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            c = src[x, y]
            if c:
                dst[x, y] = gba(pal[c * 3:c * 3 + 3]) + (255,)
    return out


def press_start_strips(img):
    """press_start.png is read as 32x8 metatiles in row order; PRESS START is tiles 1-20, copyright 21-40."""
    rgba = sprite_rgba(img)
    seq = []
    for m in range(15):
        mx, my = (m % 5) * 32, (m // 5) * 8
        for k in range(4):
            seq.append(rgba.crop((mx + k * 8, my, mx + k * 8 + 8, my + 8)))
    def strip(a):
        s = Image.new("RGBA", (160, 8))
        for i in range(20):
            s.paste(seq[a + i], (i * 8, 0))
        return s
    return strip(1), strip(21)


def compose(backdrop, bg0=None, bg1=None, bg2=None, sprites=(), bg1_alpha=(6, 15)):
    """bg* are RGBA images already positioned in screen space (any size, cropped to 240x160)."""
    base = Image.new("RGB", (W, H), gba(backdrop))
    if bg0 is not None:
        base.paste(bg0.crop((0, 0, W, H)), (0, 0), bg0.crop((0, 0, W, H)))
    if bg1 is not None:
        a, b = bg1_alpha
        top = bg1.crop((0, 0, W, H))
        bp, tp = base.load(), top.load()
        for y in range(H):
            for x in range(W):
                t = tp[x, y]
                if t[3]:
                    u = bp[x, y]
                    bp[x, y] = tuple(min(248, ((t[i] >> 3) * a + (u[i] >> 3) * b) // 16 << 3) for i in range(3))
    if bg2 is not None:
        l = bg2.crop((0, 0, W, H))
        base.paste(l, (0, 0), l)
    for img, (x, y) in sprites:
        base.paste(img, (x, y), img)
    return base


def place(img, x, y, size=(W, H)):
    c = Image.new("RGBA", size, (0, 0, 0, 0))
    c.paste(img, (x, y), img if img.mode == "RGBA" else None)
    return c


def vanilla():
    logo_pal = read_jasc(os.path.join(TS, "pokemon_logo.pal"))
    rc_pal = read_jasc(os.path.join(TS, "rayquaza_and_clouds.pal"))
    bgpal = (logo_pal[:224] + [(0, 0, 0)] * 224)[:224] + rc_pal
    bgpal += [(0, 0, 0)] * (256 - len(bgpal))
    bg0 = text_bg(os.path.join(TS, "rayquaza.png"), os.path.join(TS, "rayquaza.bin"), bgpal)
    bg1 = text_bg(os.path.join(TS, "clouds.png"), os.path.join(TS, "clouds.bin"), bgpal)
    logo = affine_bg(os.path.join(TS, "pokemon_logo.png"), os.path.join(TS, "pokemon_logo.bin"), bgpal)
    banner = sprite_rgba(Image.open(os.path.join(TS, "emerald_version.png")))
    ps, cr = press_start_strips(Image.open(os.path.join(TS, "press_start.png")))
    return compose(bgpal[0], bg0, bg1, place(logo, LOGO_X, LOGO_Y),
                   [(banner, BANNER_XY), (ps, (48, PRESS_START_Y)), (cr, (48, COPYRIGHT_Y))])


if __name__ == "__main__":
    vanilla().resize((720, 480), Image.NEAREST).save(os.path.join(os.environ.get("OUT", "."), "vanilla_screen.png"))

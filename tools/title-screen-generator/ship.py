"""Write the approved title screen into ../../game (owner picks, 2026-11-01):
logo black-outline (Kyber Gold), one-line KYBER VERSION banner, deep-space gradient, double-coil Exogorth,
Emerald's own cloud shapes recoloured grey.
    python3 ship.py
"""
import os, re, struct
from PIL import Image
import gba_title as g, sw_logo, bg_round as b

LOGO, GRADIENT, CREATURE, CLOUDS = "black-outline", "deep-space", "double-coil", "1-emerald-shapes-grey"
TS = g.TS
SRC = os.path.join(g.GAME, "src", "title_screen.c")


def write_jasc(path, cols):
    with open(path, "w", newline="\r\n") as f:
        f.write("JASC-PAL\n0100\n%d\n" % len(cols))
        for c in cols:
            f.write("%d %d %d\n" % c)


def tiles(img):
    px = img.load()
    for ty in range(img.size[1] // 8):
        for tx in range(img.size[0] // 8):
            yield tx, ty, tuple(tuple(px[tx * 8 + x, ty * 8 + y] for x in range(8)) for y in range(8))


def sheet_png(tile_list, width_tiles, pal, path):
    rows = (len(tile_list) + width_tiles - 1) // width_tiles
    out = Image.new("P", (width_tiles * 8, rows * 8), 0)
    px = out.load()
    for i, t in enumerate(tile_list):
        ox, oy = (i % width_tiles) * 8, (i // width_tiles) * 8
        for y in range(8):
            for x in range(8):
                px[ox + x, oy + y] = t[y][x]
    flat = []
    for c in pal:
        flat += list(c)
    out.putpalette(flat)
    out.save(path)


def ship_logo(layer):
    """BG2: 8bpp affine. Texture x = screen x - 29 (BG2X is -29 in title_screen.c). Tilemap is 1 byte per tile, no flips."""
    tex = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    tex.paste(layer, (-g.LOGO_X, 0), layer)
    colors = [(8, 8, 16)]                       # index 0: transparent / backdrop (deep space)
    lut = {}
    idx = Image.new("P", (256, 256), 0)
    sp, ip = tex.load(), idx.load()
    for y in range(256):
        for x in range(256):
            c = sp[x, y]
            if c[3] < 128:
                continue
            q = g.gba(c)
            if q not in lut:
                lut[q] = len(colors); colors.append(q)
            ip[x, y] = lut[q]
    assert len(colors) <= 224, f"logo uses {len(colors)} colours, max 224"
    blank = tuple(tuple(0 for _ in range(8)) for _ in range(8))
    tl, seen, tmap = [blank], {blank: 0}, bytearray(1024)
    for tx, ty, t in tiles(idx):
        if t not in seen:
            seen[t] = len(tl); tl.append(t)
        tmap[ty * 32 + tx] = seen[t]
    assert len(tl) <= 256, f"logo needs {len(tl)} tiles, max 256"
    pal = colors + [(0, 0, 0)] * (256 - len(colors))
    sheet_png(tl, 32, pal, os.path.join(TS, "pokemon_logo.png"))
    open(os.path.join(TS, "pokemon_logo.bin"), "wb").write(bytes(tmap))
    write_jasc(os.path.join(TS, "pokemon_logo.pal"), pal)
    return len(colors), len(tl)


def ship_banner(img):
    """OBJ: 128x32, 8bpp tiles cut as two 64x32 halves (gbagfx -mwidth 8 -mheight 4), 16-colour palette."""
    colors, lut = [(0, 0, 0)], {}
    out = Image.new("P", img.size, 0)
    sp, op = img.load(), out.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            c = sp[x, y]
            if c[3] < 128:
                continue
            q = g.gba(c)
            if q not in lut:
                lut[q] = len(colors); colors.append(q)
            op[x, y] = lut[q]
    assert len(colors) <= 16, f"banner uses {len(colors)} colours"
    colors += [(0, 0, 0)] * (16 - len(colors))
    flat = []
    for c in colors:
        flat += list(c)
    out.putpalette(flat)
    out.save(os.path.join(TS, "emerald_version.png"), bits=8)
    return len(lut) + 1


def ship_bg0(idx, pal):
    """BG0: 4bpp text BG, palette 14, tiles deduplicated with h/v flips."""
    full = Image.new("P", (256, 256), 0)
    full.paste(idx, (0, 0))
    fp, ip = full.load(), idx.load()
    for y in range(256):                       # off-screen area: carry the gradient on
        for x in range(256):
            if x >= 240 or y >= 160:
                fp[x, y] = ip[x % 8, min(y, 159 - (7 - y % 8)) if y >= 160 else y]
    tl, seen, tmap = [], {}, []
    for tx, ty, t in tiles(full):
        forms = {(0, 0): t, (1, 0): tuple(r[::-1] for r in t), (0, 1): t[::-1], (1, 1): tuple(r[::-1] for r in t[::-1])}
        hit = None
        for (h, v), f in forms.items():
            if f in seen:
                hit = (seen[f], h, v); break
        if hit is None:
            seen[t] = len(tl); tl.append(t); hit = (seen[t], 0, 0)
        n, h, v = hit
        tmap.append(n | (h << 10) | (v << 11) | (14 << 12))
    assert len(tl) <= 512, f"BG0 needs {len(tl)} tiles"
    sheet_png(tl, 16, pal, os.path.join(TS, "rayquaza.png"))
    open(os.path.join(TS, "rayquaza.bin"), "wb").write(struct.pack("<1024H", *tmap))
    return len(tl)


def ship_code(bxy):
    src = open(SRC).read()
    left = bxy[0] + 32
    src = re.sub(r"#define VERSION_BANNER_LEFT_X -?\d+", f"#define VERSION_BANNER_LEFT_X {left}", src)
    src = re.sub(r"#define VERSION_BANNER_RIGHT_X -?\d+", f"#define VERSION_BANNER_RIGHT_X {left + 64}", src)
    src = re.sub(r"#define VERSION_BANNER_Y_GOAL -?\d+", f"#define VERSION_BANNER_Y_GOAL {bxy[1] + 16}", src)
    open(SRC, "w").write(src)


def main():
    top, banner, bottom = sw_logo.VARIANTS[LOGO]()
    layer, bxy, _ = sw_logo.layout(top, banner, bottom)
    pal = b.palette(b.GRADIENTS[GRADIENT], b.CLOUDS[CLOUDS])
    print("logo colours, tiles:", ship_logo(layer))
    print("banner colours:", ship_banner(banner))
    print("bg0 tiles:", ship_bg0(b.bg0(GRADIENT, CREATURE), pal))
    write_jasc(os.path.join(TS, "rayquaza_and_clouds.pal"), [g.gba(c) for c in pal])
    ship_code(bxy)
    print("banner top-left", bxy)


if __name__ == "__main__":
    main()

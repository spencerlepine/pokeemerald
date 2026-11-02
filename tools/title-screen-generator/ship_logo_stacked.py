"""Ship the round 3 logo layout (owner pick A, 2026-11-02): STAR / WARS stacked tight as one wordmark,
KYBER VERSION right below it, PRESS START unchanged.
    python3 ship_logo_stacked.py [PREVIEW.png]
Writes only the logo (pokemon_logo.png/.bin/.pal, face colours split into diagonal shine bands), the banner (emerald_version.png, art unchanged) and the
banner/logo position and LOGO_SHINE_* defines in src/title_screen.c. BG0 (the collage ridge) is not touched, unlike ship.py.
"""
import math, os, re, sys
from PIL import Image
import gba_title as g, ship, sw_logo
from logo import hexc
from ship import SRC, TS

LOGO = "black-outline"


def ship_positions(bxy, logo_bottom):
    src = open(SRC).read()
    # Point the crawl-out shrinks the wordmark towards: the middle of STAR WARS
    cy = (9 + logo_bottom) // 2
    src = re.sub(r"#define CRAWL_OUT_CENTER_Y\s+\d+", lambda m: m.group(0)[:-len(m.group(0).split()[-1])] + str(cy), src)
    # The logo shine (a 64x64 window sprite) sweeps across the middle of the wordmark
    # (plus 32: the shines play before the logo has slid up from 32px low)
    src = re.sub(r"#define LOGO_SHINE_Y \(\d+ \+ 32\)", f"#define LOGO_SHINE_Y ({cy} + 32)", src)
    open(SRC, "w").write(src)
    return cy


# Logo shine (src/title_screen.c, UpdateLogoShine). The shine only lights the gold letter faces, never the
# outline, extrusion or sky: every face pixel gets a palette entry for its diagonal band (u = 2x + y, the
# slope of the shine stripes in logo_shine.png), so the game brightens just the bands under the stripes.
PAL_LIMIT = 224                        # BG palettes 0-13 hold the logo


def ship_logo_banded(layer, style=sw_logo.KYBER_GOLD):
    face = []
    for c in list(style["fill"]) + [style["hi"], style["lo"]]:
        q = g.gba(hexc(c))
        if q not in face:
            face.append(q)
    px = layer.load()
    others, us = [], []
    for y in range(160):
        for x in range(240):
            c = px[x, y]
            if c[3] < 128:
                continue
            q = g.gba(c)
            if q in face:
                us.append(2 * x + y)
            elif q not in others:
                others.append(q)
    base = 1 + len(others)
    u0, u1 = min(us), max(us) + 1
    max_bands = (PAL_LIMIT - base) // len(face)
    width = math.ceil((u1 - u0) / max_bands)
    bands = math.ceil((u1 - u0) / width)
    colors = [(8, 8, 16)] + others
    for b in range(bands):
        colors += face
    assert len(colors) <= PAL_LIMIT

    tex = Image.new("P", (256, 256), 0)
    tp = tex.load()
    for y in range(160):
        for x in range(240):
            c = px[x, y]
            tx = x - g.LOGO_X
            if c[3] < 128 or not 0 <= tx < 256:
                continue
            q = g.gba(c)
            if q in face:
                tp[tx, y] = base + ((2 * x + y - u0) // width) * len(face) + face.index(q)
            else:
                tp[tx, y] = 1 + others.index(q)
    blank = tuple(tuple(0 for _ in range(8)) for _ in range(8))
    tl, seen, tmap = [blank], {blank: 0}, bytearray(1024)
    for tx, ty, t in ship.tiles(tex):
        if t not in seen:
            seen[t] = len(tl); tl.append(t)
        tmap[ty * 32 + tx] = seen[t]
    assert len(tl) <= 256, f"logo needs {len(tl)} tiles, max 256"
    pal = colors + [(0, 0, 0)] * (256 - len(colors))
    ship.sheet_png(tl, 32, pal, os.path.join(TS, "pokemon_logo.png"))
    open(os.path.join(TS, "pokemon_logo.bin"), "wb").write(bytes(tmap))
    ship.write_jasc(os.path.join(TS, "pokemon_logo.pal"), pal)
    return dict(LOGO_SHINE_FACE_BASE=base, LOGO_SHINE_FACE_COLORS=len(face), LOGO_SHINE_BANDS=bands,
                LOGO_SHINE_BAND_W=width, LOGO_SHINE_U0=u0), len(colors), len(tl)


def ship_shine_defines(d):
    src = open(SRC).read()
    for k, v in d.items():
        src, n = re.subn(r"#define %s\s+-?\d+" % k, lambda m: m.group(0)[:-len(m.group(0).split()[-1])] + str(v), src)
        assert n == 1, k
    open(SRC, "w").write(src)


def main():
    top, banner, bottom = sw_logo.VARIANTS[LOGO]()
    layer, bxy, logo_bottom = sw_logo.layout_stacked(top, banner, bottom)
    shine, ncol, ntiles = ship_logo_banded(layer)
    print("logo colours, tiles:", ncol, ntiles, shine)
    ship_shine_defines(shine)
    print("banner colours:", ship.ship_banner(banner))
    ship.ship_code(bxy)
    print("banner top-left", bxy, "logo bottom", logo_bottom, "centre y", ship_positions(bxy, logo_bottom))
    if len(sys.argv) > 1:
        layer.save(sys.argv[1])
    ship.gate()


if __name__ == "__main__":
    main()

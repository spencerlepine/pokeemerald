"""Ship the round 3 logo layout (owner pick A, 2026-11-02): STAR / WARS stacked tight as one wordmark,
KYBER VERSION right below it, PRESS START unchanged.
    python3 ship_logo_stacked.py [PREVIEW.png]
Writes only the logo (pokemon_logo.png/.bin/.pal), the banner (emerald_version.png, art unchanged) and the
banner/logo position defines in src/title_screen.c. BG0 (the collage ridge) is not touched, unlike ship.py.
"""
import re, sys
import ship, sw_logo
from ship import SRC

LOGO = "black-outline"


def ship_positions(bxy, logo_bottom):
    src = open(SRC).read()
    # Point the crawl-out shrinks the wordmark towards: the middle of STAR WARS
    cy = (9 + logo_bottom) // 2
    src = re.sub(r"#define CRAWL_OUT_CENTER_Y\s+\d+", lambda m: m.group(0)[:-len(m.group(0).split()[-1])] + str(cy), src)
    # The logo shine (a 64x64 window sprite) sweeps across the middle of the wordmark
    src = re.sub(r"#define LOGO_SHINE_Y\s+\d+", lambda m: m.group(0)[:-len(m.group(0).split()[-1])] + str(cy), src)
    open(SRC, "w").write(src)
    return cy


def main():
    top, banner, bottom = sw_logo.VARIANTS[LOGO]()
    layer, bxy, logo_bottom = sw_logo.layout_stacked(top, banner, bottom)
    print("logo colours, tiles:", ship.ship_logo(layer))
    print("banner colours:", ship.ship_banner(banner))
    ship.ship_code(bxy)
    print("banner top-left", bxy, "logo bottom", logo_bottom, "centre y", ship_positions(bxy, logo_bottom))
    if len(sys.argv) > 1:
        layer.save(sys.argv[1])
    ship.gate()


if __name__ == "__main__":
    main()

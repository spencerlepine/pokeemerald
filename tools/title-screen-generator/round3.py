"""Round 2 review: stacked logo variants on the default (vanilla) background."""
import os, sys
from PIL import Image
import gba_title as g, sw_logo
from mockups import sheet, big

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
V = g.TS
pal = g.read_jasc(os.path.join(V, "pokemon_logo.pal"))[:224] + g.read_jasc(os.path.join(V, "rayquaza_and_clouds.pal"))
bg0 = g.text_bg(os.path.join(V, "rayquaza.png"), os.path.join(V, "rayquaza.bin"), pal)
bg1 = g.text_bg(os.path.join(V, "clouds.png"), os.path.join(V, "clouds.bin"), pal)
ps, row = g.press_start_strips(Image.open(os.path.join(V, "press_start.png")))

cells = [("Current game (Pokémon logo still in)", g.vanilla())]
for i, (k, f) in enumerate(sw_logo.VARIANTS.items()):
    top, subimg, bottom = f()
    layer, bxy, bottom_y = sw_logo.layout(top, subimg, bottom)
    print(k, "bottom of WARS at y", bottom_y, "banner", bxy)
    s = g.compose(pal[0], bg0, bg1, layer, [(subimg, bxy), (ps, (48, g.PRESS_START_Y)), (row, (48, g.COPYRIGHT_Y))])
    s.save(os.path.join(OUT, f"logo3_{i+1}_{k}.png"))
    big(s, 3).save(os.path.join(OUT, f"logo3_{i+1}_{k}_3x.png"))
    cells.append((f"{i+1} · {k}", s))
sheet("Round 3: Kyber Gold logo, one-line KYBER VERSION, default background (2x)",
      [("", cells)], os.path.join(OUT, "review_logo_round3.png"), k=2)

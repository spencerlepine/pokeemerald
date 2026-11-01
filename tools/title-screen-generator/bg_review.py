import os, sys
from PIL import Image
import gba_title as g, sw_logo, bg_round as b
from mockups import sheet

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
top, subimg, bottom = sw_logo.VARIANTS["black-outline"]()
layer, bxy, _ = sw_logo.layout(top, subimg, bottom)
ps, row = g.press_start_strips(Image.open(os.path.join(g.TS, "press_start.png")))

def screen(grad, creature, cloud, logo=True):
    c = b.CLOUDS[cloud]
    pal = b.palette(b.GRADIENTS[grad], c)
    bg0 = b.to_rgba(b.bg0(grad, creature), pal, transparent0=False)
    cl = c["make"]()
    bg1 = b.to_rgba(cl, pal)
    spr = [(ps, (48, g.PRESS_START_Y)), (row, (48, g.COPYRIGHT_Y))]
    if logo:
        spr.insert(0, (subimg, bxy))
    return g.compose(pal[4], bg0, bg1, layer if logo else None, spr), cl

van = g.vanilla()
# 1) gradients x creatures, clouds fixed to the plain grey Emerald shapes
rows = []
for gr in b.GRADIENTS:
    cells = []
    for cr in b.CREATURES:
        s, _ = screen(gr, cr, "1-emerald-shapes-grey")
        s.save(os.path.join(OUT, f"bg_{gr}_{cr}.png"))
        cells.append((f"{gr} · {cr}", s))
    rows.append((f"Gradient: {gr}", cells))
sheet("Gradient (rows) x Exogorth silhouette (columns), grey Emerald-shape clouds (2x)", rows, os.path.join(OUT, "review_gradient_creature.png"), k=2)

# 2) silhouettes alone (no logo, no clouds) so the shapes read
cells = [(cr, screen("deep-space", cr, "8-stars-only", logo=False)[0]) for cr in b.CREATURES]
sheet("Exogorth silhouettes without the logo (2x)", [("", [("Original", van)] + cells[:1]), ("", cells[1:])],
      os.path.join(OUT, "review_creature_only.png"), k=2)

# 3) clouds: 8 variants on deep-space + ring
cells = []
for name in b.CLOUDS:
    s, cl = screen("deep-space", "ring", name)
    s.save(os.path.join(OUT, f"clouds_{name}.png"))
    cells.append((f"{name}  ({b.unique_tiles(cl)} tiles)", s))
sheet("Clouds / nebula variants on deep-space + ring (2x). Tile count must stay under ~190 to fit VRAM.",
      [("", cells[i:i + 3]) for i in range(0, len(cells), 3)], os.path.join(OUT, "review_clouds.png"), k=2)
print("creature tiles", {cr: b.unique_tiles(b.bg0("deep-space", cr)) for cr in b.CREATURES})

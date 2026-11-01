"""Build every title-screen mockup and the side-by-side review sheets.
    python3 mockups.py OUT_DIR
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
import gba_title as g
import logo, banner, backdrop, copyright as cr

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
os.makedirs(os.path.join(OUT, "screens"), exist_ok=True)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
SMALLF = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

THEMES = [
    dict(name="1-kyber", label="1 · Kyber", backdrop="145868", logo="steel", banner="crystal", exo="coil", sky="stars",
         row="fan-project", boot="name"),
    dict(name="2-imperial", label="2 · Imperial", backdrop="2a2050", logo="gold", banner="chrome", exo="asteroid", sky="nebula",
         row="not-for-sale", boot="disclaimer"),
    dict(name="3-hyperspace", label="3 · Hyperspace", backdrop="3c2814", logo="arch", banner="icon", exo="maw", sky="asteroids",
         row="name", boot="credit"),
]


def screen(t, logo_img=None, banner_img=None, exo=None, sky=None, row=None):
    logo_img = logo_img or logo.VARIANTS[t["logo"]]()
    banner_img = banner_img or banner.VARIANTS[t["banner"]]()
    exo = exo or backdrop.EXO[t["exo"]]()
    sky = sky or backdrop.SKY[t["sky"]]()
    row = row or cr.title_row(cr.TITLE_ROW[t["row"]])
    ps, _ = g.press_start_strips(Image.open(os.path.join(g.TS, "press_start.png")))
    lx = 120 - logo_img.size[0] // 2
    return g.compose(logo.hexc(t["backdrop"]), exo, sky, g.place(logo_img, lx, 3),
                     [(banner_img, g.BANNER_XY), (ps, (48, g.PRESS_START_Y)), (row, (40, g.COPYRIGHT_Y))])


def big(img, k=3):
    return img.resize((img.size[0] * k, img.size[1] * k), Image.NEAREST)


def on_bg(img, color=(24, 28, 44)):
    bg = Image.new("RGBA", img.size, color + (255,))
    bg.paste(img, (0, 0), img)
    return bg.convert("RGB")


def sheet(title, rows, path, k=3):
    """rows: [(row label, [(cell label, image)])] -> grid PNG."""
    pad, lab = 16, 30
    cw = max(i.size[0] for _, cells in rows for _, i in cells) * k
    ch = [max(i.size[1] for _, i in cells) * k for _, cells in rows]
    ncol = max(len(c) for _, c in rows)
    W = pad + ncol * (cw + pad)
    H = 50 + sum(h + lab * 2 + pad for h in ch)
    out = Image.new("RGB", (W, H), (16, 16, 22))
    d = ImageDraw.Draw(out)
    d.text((pad, 12), title, font=FONT, fill=(240, 240, 240))
    y = 50
    for (rl, cells), h in zip(rows, ch):
        d.text((pad, y), rl, font=FONT, fill=(150, 220, 170))
        y += lab
        for c, (cl, img) in enumerate(cells):
            x = pad + c * (cw + pad)
            d.text((x, y), cl, font=SMALLF, fill=(200, 200, 210))
            out.paste(big(img, k), (x, y + lab - 6))
        y += h + lab + pad
    out.save(path)


def save(img, name):
    img.save(os.path.join(OUT, "assets", name + ".png"))
    return img


def main():
    V = os.path.join(g.TS)
    van_logo = g.sprite_rgba(Image.open(os.path.join(V, "pokemon_logo.png")))
    van_banner = g.sprite_rgba(Image.open(os.path.join(V, "emerald_version.png")))
    vscreen = g.vanilla()
    vbg0 = g.compose((0, 0, 0), g.text_bg(os.path.join(V, "rayquaza.png"), os.path.join(V, "rayquaza.bin"),
                     (g.read_jasc(os.path.join(V, "pokemon_logo.pal"))[:224] + g.read_jasc(os.path.join(V, "rayquaza_and_clouds.pal")))))
    pal = g.read_jasc(os.path.join(V, "pokemon_logo.pal"))[:224] + g.read_jasc(os.path.join(V, "rayquaza_and_clouds.pal"))
    vbg1 = g.text_bg(os.path.join(V, "clouds.png"), os.path.join(V, "clouds.bin"), pal)
    _, vrow = g.press_start_strips(Image.open(os.path.join(V, "press_start.png")))
    vboot = g.sprite_rgba(Image.open(os.path.join(g.GAME, "graphics", "intro", "copyright.png")).convert("P"))
    vboot = Image.open(os.path.join(g.GAME, "graphics", "intro", "copyright.png")).convert("L").point(lambda v: 255 if v else 0)
    vboot_rgba = Image.new("RGBA", vboot.size, (0, 0, 0, 0)); vboot_rgba.paste((255, 255, 255, 255), (0, 0), vboot)

    logos = {k: save(f(), f"logo_{k}") for k, f in logo.VARIANTS.items()}
    banners = {k: save(f(), f"banner_{k}") for k, f in banner.VARIANTS.items()}
    exos = {k: save(f(), f"exogorth_{k}") for k, f in backdrop.EXO.items()}
    skies = {k: save(f(), f"sky_{k}") for k, f in backdrop.SKY.items()}
    rows = {k: save(cr.title_row(t), f"title_copyright_{k}") for k, t in cr.TITLE_ROW.items()}
    boots = {k: save(cr.boot_strip(t), f"boot_copyright_{k}") for k, t in cr.BOOT.items()}

    screens = []
    for t in THEMES:
        s = screen(t)
        s.save(os.path.join(OUT, "screens", f"title_{t['name']}.png"))
        big(s, 3).save(os.path.join(OUT, "screens", f"title_{t['name']}_3x.png"))
        screens.append((t["label"], s))

    sheet("Full title screens: original vs 3 new themes",
          [("Title screen", [("Original (Pokémon Emerald)", vscreen)] + screens[:1]),
           ("", screens[1:])], os.path.join(OUT, "review_screens.png"), k=2)

    # each asset swapped alone into theme 1, so it reads in context
    t1 = THEMES[0]
    def ctx(**kw):
        return screen(t1, **kw)
    rows_ = [
        ("A · Logo (256x64 BG, replaces POKéMON)", [("Original", on_bg(van_logo))] + [(f"A{i+1} · {k}", on_bg(v)) for i, (k, v) in enumerate(logos.items())]),
        ("B · Subtitle banner (128x32 sprite)", [("Original", on_bg(van_banner))] + [(f"B{i+1} · {k}", on_bg(v)) for i, (k, v) in enumerate(banners.items())]),
        ("C · Creature behind the logo (BG0, replaces Rayquaza)", [("Original", vbg0)] + [(f"C{i+1} · {k}", on_bg(v, (10, 42, 52))) for i, (k, v) in enumerate(exos.items())]),
        ("D · Sky layer (BG1, replaces the clouds; shown before blending)", [("Original", on_bg(vbg1.crop((0, 0, 240, 160)), (32, 160, 120)))] + [(f"D{i+1} · {k}", on_bg(v.crop((0, 0, 240, 160)), (10, 14, 30))) for i, (k, v) in enumerate(skies.items())]),
    ]
    sheet("Title screen pieces, side by side (2x)", rows_, os.path.join(OUT, "review_pieces.png"), k=2)

    rows2 = [
        ("Each logo in place", [(f"A{i+1} · {k}", ctx(logo_img=v)) for i, (k, v) in enumerate(logos.items())]),
        ("Each banner in place", [(f"B{i+1} · {k}", ctx(banner_img=v)) for i, (k, v) in enumerate(banners.items())]),
        ("Each creature in place", [(f"C{i+1} · {k}", ctx(exo=v)) for i, (k, v) in enumerate(exos.items())]),
        ("Each sky in place", [(f"D{i+1} · {k}", ctx(sky=v)) for i, (k, v) in enumerate(skies.items())]),
    ]
    sheet("Every variant dropped into theme 1, so you can compare in context (2x)", rows2, os.path.join(OUT, "review_in_place.png"), k=2)

    E = [("Original: ©2005 GAMEFREAK inc.", vrow)] + [(f"E{i+1} · {k}", v) for i, (k, v) in enumerate(rows.items())]
    F = [("Original", vboot_rgba)] + [(f"F{i+1} · {k}", v) for i, (k, v) in enumerate(boots.items())]
    rows3 = [(("E · Title screen copyright row, under PRESS START" if i == 0 else ""), [(l, on_bg(v, (10, 42, 52)))]) for i, (l, v) in enumerate(E)]
    rows3 += [(("F · Boot screen copyright strip (312x8)" if i == 0 else ""), [(l, on_bg(v, (0, 0, 0)))]) for i, (l, v) in enumerate(F)]
    sheet("Copyright lines (3x)", rows3, os.path.join(OUT, "review_copyright.png"), k=3)


if __name__ == "__main__":
    main()

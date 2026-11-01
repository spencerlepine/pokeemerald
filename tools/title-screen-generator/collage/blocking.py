"""Blocking pass for the title-screen collage: flat silhouettes cut from the existing wiki art (concept only,
nothing here ships) placed on the real background and logo, to settle cast, size and position before drawing.
    python3 blocking.py OUT_DIR
"""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import gba_title as g

WIKI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "wiki", "art", "graphics")
TR = os.path.join(WIKI, "trainers", "front_pics")
MON = os.path.join(WIKI, "pokemon")
REBEL, SITH, CREAT_R, CREAT_S = (232, 200, 144), (200, 56, 56), (120, 184, 216), (168, 104, 200)


def layers():
    TS = g.TS
    lp = g.read_jasc(os.path.join(TS, "pokemon_logo.pal")); rc = g.read_jasc(os.path.join(TS, "rayquaza_and_clouds.pal"))
    bgpal = (lp[:224] + [(0, 0, 0)] * 224)[:224] + rc
    bgpal += [(0, 0, 0)] * (256 - len(bgpal))
    bg1 = g.text_bg(os.path.join(TS, "clouds.png"), os.path.join(TS, "clouds.bin"), bgpal)
    logo = g.affine_bg(os.path.join(TS, "pokemon_logo.png"), os.path.join(TS, "pokemon_logo.bin"), bgpal)
    ban = g.sprite_rgba(Image.open(os.path.join(TS, "emerald_version.png")))
    ps, cr = g.press_start_strips(Image.open(os.path.join(TS, "press_start.png")))
    back = g.compose(bgpal[0], None, bg1, None, []).convert("RGBA")
    fg = Image.new("RGBA", (240, 160))
    lg = g.place(logo, g.LOGO_X, g.LOGO_Y)
    fg.alpha_composite(lg)
    for im, xy in [(ban, g.BANNER_XY), (ps, (48, g.PRESS_START_Y)), (cr, (48, g.COPYRIGHT_Y))]:
        fg.paste(im, xy, im)
    return back, fg


def cut(path, flip=False):
    im = Image.open(path).convert("RGBA")
    # wiki pics: index 0 / magenta background
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, gg, b, a = px[x, y]
            if (r, gg, b) in ((255, 0, 255), (248, 0, 248)):
                px[x, y] = (0, 0, 0, 0)
    pal_im = Image.open(path)
    if pal_im.mode == "P":
        idx = pal_im.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                if idx[x, y] == 0:
                    px[x, y] = (0, 0, 0, 0)
    if path.endswith("front.png") and im.size[1] > 64:
        im = im.crop((0, 0, 64, 64))
    im = im.crop(im.getbbox())
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


def silhouette(im, h, col):
    w = max(1, round(im.size[0] * h / im.size[1]))
    s = im.resize((w, h), Image.NEAREST)
    a = s.split()[3].point(lambda v: 255 if v > 0 else 0)
    flat = Image.new("RGBA", s.size, col + (255,))
    out = Image.new("RGBA", (w + 2, h + 2))
    dark = Image.new("RGBA", s.size, (24, 16, 24, 255))
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        out.paste(dark, (dx, dy), a)
    out.paste(flat, (1, 1), a)
    return out


SIL = False


def standin(im, h):
    """The concept art itself, scaled to the planned height (blocking only: the real figures get drawn new)."""
    w = max(1, round(im.size[0] * h / im.size[1]))
    s = im.resize((w, h), Image.NEAREST)
    a = s.split()[3].point(lambda v: 255 if v > 0 else 0)
    s.putalpha(a)
    return s


def render(cast, back, fg, behind_logo=True):
    img = back.copy()
    for c in sorted(cast, key=lambda c: c["z"]):
        src = os.path.join(TR, c["src"] + ".png") if c["kind"] == "t" else os.path.join(MON, c["src"], "front.png")
        im = cut(src, c.get("flip", False))
        s = silhouette(im, c["h"], c["col"]) if SIL else standin(im, c["h"])
        img.alpha_composite(s, (c["x"] - s.size[0] // 2, c["y"] - s.size[1]))
    img.alpha_composite(fg)
    return img


def label(img, cast, scale=3):
    big = img.resize((240 * scale, 160 * scale), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for c in cast:
        d.text((c["x"] * scale - 10, min(155, c["y"]) * scale - 12), c["name"], fill=(255, 255, 255))
    return big


def T(name, src, x, y, h, z, col, flip=False): return dict(name=name, src=src, kind="t", x=x, y=y, h=h, z=z, col=col, flip=flip)
def M(name, src, x, y, h, z, col, flip=False): return dict(name=name, src=src, kind="m", x=x, y=y, h=h, z=z, col=col, flip=flip)

LAYOUTS = {
    # A: V-frame. Tall figures at the screen edges rise beside the logo, the front row and the creatures
    # fill the open band under it (y 104-160) without touching PRESS START or the copyright line.
    "A_v_frame": [
        T("OBI-WAN", "champion_wallace", 20, 172, 150, 1, REBEL),
        T("LEIA", "steven", 50, 168, 100, 2, REBEL),
        T("KAEL", "brendan", 22, 170, 110, 3, REBEL),
        M("LOTHWOLF", "absol", 72, 162, 34, 4, CREAT_R),
        M("SUNCHICK", "torchic", 44, 162, 20, 5, CREAT_R),
        M("KATARNKIT", "treecko", 98, 161, 22, 5, CREAT_R),
        T("VADER", "magma_leader_maxie", 216, 176, 156, 1, SITH, True),
        T("BOBA", "dome_ace_tucker", 186, 170, 100, 2, SITH, True),
        T("TROOPER", "magma_grunt_m", 222, 170, 104, 3, SITH, True),
        M("FYRNALPHA", "houndoom", 160, 162, 34, 4, CREAT_S, True),
        M("SPIDROID", "aron", 140, 161, 18, 5, CREAT_S, True),
    ],
    # B: Two crowds. Every character is a mid-size full figure standing on the bottom edge, heads in the
    # gap beside WARS; creatures out in front. Calmer, more like the Unchained screen.
    "B_two_crowds": [
        T("OBI-WAN", "champion_wallace", 16, 166, 96, 1, REBEL),
        T("LEIA", "steven", 40, 162, 80, 2, REBEL),
        T("KAEL", "brendan", 26, 168, 78, 3, REBEL),
        T("MIRA", "may", 58, 168, 72, 3, REBEL),
        M("SUNCHICK", "torchic", 82, 160, 20, 5, CREAT_R),
        M("MARSHLET", "mudkip", 36, 160, 20, 5, CREAT_R),
        T("VADER", "magma_leader_maxie", 222, 166, 104, 1, SITH, True),
        T("BOBA", "dome_ace_tucker", 198, 164, 82, 2, SITH, True),
        T("TROOPER", "magma_grunt_m", 214, 168, 76, 3, SITH, True),
        T("TROOPER2", "magma_grunt_m", 180, 168, 70, 2, SITH, True),
        M("FYRNALPHA", "houndoom", 160, 161, 30, 5, CREAT_S, True),
    ],
}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    back, fg = layers()
    for k, cast in LAYOUTS.items():
        img = render(cast, back, fg)
        img.convert("RGB").resize((720, 480), Image.NEAREST).save(os.path.join(out, k + ".png"))
        label(img, cast).convert("RGB").save(os.path.join(out, k + "_labels.png"))

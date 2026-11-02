"""The creature sprites that are not a species: the Companion Egg, the question-mark placeholders and
Wobblekit's (Spinda's) spot masks.

The Egg and the placeholders keep vanilla's hand-drawn pixels (the hatch cracks and the shell shards
line up with code), and get new colours: the Egg becomes a Star Wars creature egg, the placeholders a
"no data" hologram. The spot masks are redrawn for Wobblekit's front. The Egg and placeholder icons are
recoloured the same way and snapped to the fitted shared icon banks.

    python3 extras.py --out out                  # everything, with the chosen egg scheme
    python3 extras.py --egg-options sheet.png    # every egg scheme side by side, for review
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools" / "palette-enforcer"))
sys.path.insert(0, str(REPO / "tools" / "sprite-creature-icon-generator"))
from gba_palette import check, core, enforce  # noqa: E402
import icongen  # noqa: E402

GAME = REPO / "game" / "graphics" / "pokemon"
ICON_BANKS = [core.load_jasc(REPO / f"tools/sprite-creature-icon-generator/palettes/icon_palette_{n}.pal") for n in range(3)]

# Egg palette: 0 key, 1-2 outline greys, 3-5 shell light->dark, 6-7 spots light->dark, 15 unused cyan.
EGG_SCHEMES = {
    "dune": {  # leathery desert reptile egg (krayt, dewback), rust mottling
        1: (72, 48, 40), 2: (152, 120, 96), 3: (240, 224, 184), 4: (224, 192, 136), 5: (184, 152, 104),
        6: (192, 96, 56), 7: (136, 64, 40),
    },
    "kyber": {  # pale stone egg with kyber-blue speckles
        1: (48, 56, 72), 2: (136, 144, 160), 3: (240, 240, 232), 4: (208, 208, 200), 5: (168, 168, 160),
        6: (96, 176, 240), 7: (40, 104, 192),
    },
    "jungle": {  # ivory egg with deep plum blotches (Kashyyyk, Felucia)
        1: (64, 40, 56), 2: (144, 120, 128), 3: (248, 240, 216), 4: (224, 216, 176), 5: (184, 176, 136),
        6: (152, 88, 136), 7: (96, 48, 96),
    },
}
EGG_DEFAULT = "dune"

# "No data" hologram for the placeholders.
HOLO = {"fill": (120, 200, 248), "mid": (64, 144, 216), "dark": (24, 64, 128), "line": (16, 32, 72), "hi": (216, 240, 255)}


def recolour_pal(pal, mapping):
    out = list(pal)
    for i, c in mapping.items():
        out[i] = core.snap(c)
    return out


def pal_of(im: Image.Image, n=16):
    p = im.getpalette()[: n * 3]
    return [tuple(p[i:i + 3]) for i in range(0, len(p), 3)]


def save_indexed(arr: np.ndarray, pal, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(arr.astype(np.uint8), "P")
    flat = [v for c in pal for v in c]
    im.putpalette(flat + [0] * (768 - len(flat)))
    enforce.save(im, dst, 4)
    rep = check.check_png(dst, pal=pal)
    if not rep.ok:
        raise SystemExit(f"{dst}: " + "\n".join(rep.lines()))


def icon_from(src: Path, colour_map, dst: Path):
    """Recolour a vanilla icon (RGB lookup) and snap it to the best fitted shared bank."""
    im = Image.open(src)
    a = np.array(im)
    pal = pal_of(im)
    rgba = np.zeros(a.shape + (4,))
    for i, c in enumerate(pal):
        m = a == i
        rgba[m, :3] = colour_map.get(i, c)
        rgba[m, 3] = 0 if i == 0 else 255
    out, bank = icongen.finish(rgba, ICON_BANKS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    enforce.save(out, dst, 4)
    rep = check.check_png(dst, pal=ICON_BANKS[bank])
    if not rep.ok:
        raise SystemExit(f"{dst}: " + "\n".join(rep.lines()))
    return bank


# --- the Egg ---------------------------------------------------------------------------------------

def egg(out: Path, scheme: str):
    base = core.load_jasc(GAME / "egg/normal.pal")
    pal = recolour_pal(base, EGG_SCHEMES[scheme])
    pal[15] = pal[1]  # the unused cyan slot
    for name in ("front.png", "anim_front.png", "hatch.png", "shard.png"):
        a = np.array(Image.open(GAME / "egg" / name))
        save_indexed(a, pal, out / "graphics/pokemon/egg" / name)
    core.write_jasc(out / "graphics/pokemon/egg/normal.pal", pal)
    # icon: vanilla egg icon indices in vanilla bank 1 -> egg roles
    ic = Image.open(GAME / "egg/icon.png")
    ipal = pal_of(ic)
    # match each used icon colour to the nearest vanilla egg colour, then take that slot's new colour
    egg_old = np.array(base[1:8], float)
    cmap = {}
    for i in np.unique(np.array(ic)):
        if i == 0:
            continue
        j, _ = core.nearest(np.array([ipal[i]], float), egg_old)
        cmap[int(i)] = pal[1 + int(j[0])]
    return icon_from(GAME / "egg/icon.png", cmap, out / "graphics/pokemon/egg/icon.png")


# --- the placeholders ---------------------------------------------------------------------------------

def question_marks(out: Path):
    # circled: 12 light grey, 13 mid grey, 14 white, 15 black outline; index 1-11 black
    c = core.load_jasc(GAME / "question_mark/circled/normal.pal")
    circ = list(c)
    for i in range(1, 12):
        circ[i] = core.snap(HOLO["line"])
    circ[12], circ[13], circ[14], circ[15] = (core.snap(HOLO[k]) for k in ("fill", "mid", "hi", "line"))
    circ_shiny = list(circ)
    circ_shiny[12], circ_shiny[13] = core.snap((248, 184, 96)), core.snap((216, 128, 48))  # amber holo
    # double: 1 white fill, 2 black outline
    dpal_src = pal_of(Image.open(GAME / "question_mark/double/front.png"))
    dbl = list(dpal_src)
    dbl[0] = core.snap(dbl[0])
    dbl[1], dbl[2] = core.snap(HOLO["fill"]), core.snap(HOLO["line"])
    for i in range(3, 16):
        dbl[i] = core.snap(HOLO["line"])
    dbl_shiny = list(dbl)
    dbl_shiny[1] = core.snap((248, 184, 96))
    for form, pal, shiny in (("circled", circ, circ_shiny), ("double", dbl, dbl_shiny)):
        for name in ("front.png", "anim_front.png", "back.png"):
            a = np.array(Image.open(GAME / "question_mark" / form / name))
            save_indexed(a, pal, out / "graphics/pokemon/question_mark" / form / name)
        core.write_jasc(out / f"graphics/pokemon/question_mark/{form}/normal.pal", pal)
        core.write_jasc(out / f"graphics/pokemon/question_mark/{form}/shiny.pal", shiny)
    # icon: grey "?" block on a grey shadow -> holo blue
    ic = Image.open(GAME / "question_mark/icon.png")
    ipal = pal_of(ic)
    cmap = {}
    for i in np.unique(np.array(ic)):
        if i == 0:
            continue
        L = core.luma(ipal[i])
        cmap[int(i)] = HOLO["hi"] if L > 220 else HOLO["fill"] if L > 170 else HOLO["mid"] if L > 120 else HOLO["line"]
    return icon_from(GAME / "question_mark/icon.png", cmap, out / "graphics/pokemon/question_mark/icon.png")


# --- Wobblekit's spots --------------------------------------------------------------------------------

SPOTS = [
    # spot 0 sits on the face (base 16,7 +-8): a big round patch
    """
......####......
....########....
...##########...
..############..
..############..
.##############.
.##############.
.##############.
.##############.
..############..
..############..
...##########...
....########....
......####......
""",
    # spot 1, the far ear/shoulder (base 40,8): a smaller patch
    """
......###.......
....#######.....
...#########....
...#########....
..###########...
..###########...
..###########...
...#########....
...#########....
....#######.....
......###.......
""",
    # spots 2 and 3, chest and hands (base 22,25 and 34,26): small ovals
    """
.....####.......
....######......
...########.....
...########.....
...########.....
...########.....
....######......
.....####.......
""",
    """
.......###......
......#####.....
.....#######....
.....#######....
.....#######....
......#####.....
.......###......
""",
]


def spot_mask(i):
    rows = SPOTS[i].strip().splitlines()
    m = np.zeros((16, 16), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "#":
                m[y, x] = 1
    return m


def spots(out: Path):
    for i in range(4):
        dst = out / f"graphics/pokemon/spinda/spots/spot_{i}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        im = Image.fromarray(spot_mask(i), "P")
        im.putpalette([255, 255, 255, 0, 0, 0])  # as vanilla: index 1 (black) = part of the spot
        im.save(dst, bits=1, optimize=False)
        rep = check.check_png(dst, bpp=1)
        if not rep.ok:
            raise SystemExit(f"{dst}: " + "\n".join(rep.lines()))


def egg_options(dst: Path, sc=3):
    tmp = HERE / "out" / "_options"
    panes = []
    for s in EGG_SCHEMES:
        egg(tmp / s, s)
        row = []
        for name, h in (("front.png", 64), ("hatch.png", 128), ("shard.png", 8), ("icon.png", 32)):
            im = Image.open(tmp / s / "graphics/pokemon/egg" / name)
            a = np.array(im)
            rgba = np.array(im.convert("RGBA"))
            rgba[..., 3] = np.where(a == 0, 0, 255)
            row.append(Image.fromarray(rgba).crop((0, 0, im.width, min(h, im.height))))
        panes.append(row)
    w = sum(i.width * sc + 10 for i in panes[0]) + 10
    h = 128 * sc + 20
    out = Image.new("RGB", (w, h * len(panes)), (236, 236, 228))
    for r, row in enumerate(panes):
        x = 10
        for im in row:
            t = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
            out.paste(t, (x, r * h + 10), t)
            x += t.width + 10
    out.save(dst)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--egg", default=EGG_DEFAULT, choices=list(EGG_SCHEMES))
    ap.add_argument("--egg-options")
    a = ap.parse_args(argv)
    if a.egg_options:
        return egg_options(Path(a.egg_options))
    out = Path(a.out)
    eb = egg(out, a.egg)
    qb = question_marks(out)
    spots(out)
    print(f"egg ({a.egg}) icon bank {eb}; question_mark icon bank {qb}; 4 spot masks -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])

"""Compose the title-screen collage from individually picked figure layers.

Figures are new-pose takes from the Civitai trainer/creature tools (runs/title_*/finished/*_native.png: 96-grid native
size, 15 colours, transparent background), never the in-game battle pics. Each figure stays its own layer
(written to OUT/layers/<name>.png with its screen position in OUT/layers.json) so it can be repositioned or become a
sliding OBJ later. Draw order: clouds, figures (back to front), logo + banner + text on top, so a figure can sit
partly behind the lettering and the logo's black outline keeps it readable.

    python3 compose.py OUT_DIR [--gif]
"""
import os, sys, json, glob
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import blocking

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "..", "..")
TR_RUNS = os.path.join(TOOLS, "sprite-trainer-generator", "civitai", "runs")
CR_RUNS = os.path.join(TOOLS, "sprite-creature-generator", "civitai", "runs")
W, H = 240, 160


def take(run, idx=None, narrowest=False, root=TR_RUNS, sub="finished"):
    files = sorted(glob.glob(os.path.join(root, run, sub, "*_native.png")))
    if not files:
        return None
    if narrowest:
        files.sort(key=lambda f: Image.open(f).size[0])
        return files[0]
    return files[idx or 0]


def load(path, flip=False):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


# name, source, screen x of the figure's centre, y of its feet, z (back to front), flip, side (slide-in direction)
CAST = [
    dict(name="obiwan", src=take("title_obiwan", 1), x=16, y=168, z=1, side="L"),
    dict(name="leia", src=take("title_leia", 1), x=66, y=170, z=2, side="L"),
    dict(name="mira", src=take("title_mira", 1), x=92, y=172, z=3, side="L"),
    dict(name="kael", src=take("title_kael", 1), x=42, y=172, z=4, side="L"),
    dict(name="trooper", src=take("title_trooper", 0), x=168, y=172, z=2, side="R"),
    dict(name="boba", src=take("title_boba", narrowest=True), x=224, y=168, z=1, side="R"),
    dict(name="vader", src=take("title_vader", 1), x=200, y=172, z=4, side="R"),
]
CREATURES = []  # filled in when the creature takes are picked


def render(cast, back, fg, offsets=None):
    img = back.copy()
    for c in sorted(cast, key=lambda c: c["z"]):
        if not c["src"]:
            continue
        s = load(c["src"], c.get("flip", False))
        dx = (offsets or {}).get(c["name"], 0)
        img.alpha_composite(s, (max(0, c["x"] - s.size[0] // 2 + dx), c["y"] - s.size[1]))if False else None
        tmp = Image.new("RGBA", (W, H))
        tmp.paste(s, (c["x"] - s.size[0] // 2 + dx, c["y"] - s.size[1]), s)
        img.alpha_composite(tmp)
    img.alpha_composite(fg)
    return img


def slide_gif(cast, back, fg, path, frames=28):
    """Figures ease in from their side; back row first, front row last."""
    ims = []
    for f in range(frames + 12):
        offs = {}
        for c in cast:
            start = c["z"] * 4  # staggered
            t = min(1, max(0, (f - start) / 16))
            t = 1 - (1 - t) ** 3
            d = int((1 - t) * 90)
            offs[c["name"]] = -d if c.get("side") == "L" else d
        ims.append(render(cast, back, fg, offs).convert("RGB").resize((480, 320), Image.NEAREST))
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=33, loop=0)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(os.path.join(out, "layers"), exist_ok=True)
    back, fg = blocking.layers()
    cast = CAST + CREATURES
    img = render(cast, back, fg)
    img.convert("RGB").save(os.path.join(out, "collage_1x.png"))
    img.convert("RGB").resize((720, 480), Image.NEAREST).save(os.path.join(out, "collage_3x.png"))
    meta = []
    for c in cast:
        if c["src"]:
            s = load(c["src"], c.get("flip", False))
            s.save(os.path.join(out, "layers", c["name"] + ".png"))
            meta.append(dict(name=c["name"], x=c["x"] - s.size[0] // 2, y=c["y"] - s.size[1], w=s.size[0], h=s.size[1], z=c["z"], src=os.path.relpath(c["src"], TOOLS)))
    json.dump(meta, open(os.path.join(out, "layers.json"), "w"), indent=1)
    if "--gif" in sys.argv:
        slide_gif(cast, back, fg, os.path.join(out, "slide_in.gif"))

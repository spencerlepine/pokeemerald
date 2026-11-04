"""Scenery models: the large static pieces of ../../wiki/mapping/world_art.csv (`category` scenery), as
low-poly greybox models rendered in the Emerald camera.

    python3 -m worldart scenery shared_crashed-tie-fighter        # one model (models/scenery/<name>.yaml)
    python3 -m worldart scenery --all                             # every model
    python3 -m worldart scenery --status                          # every scenery row and its model status

A model file names its wiki row (`art: art:shared:crashed-tie-fighter`); its `cells` must be the row's
`drawn` size and its `footprint` the row's footprint depth, or the render stops. Each render writes:

- output/scenery/<name>/sprite.png, review.png (1x on grounds, 3x, 6x with the cell grid and footprint);
- output/scenery/<name>/scene.png: a 15x10-cell game screen (the GBA view) in grey with the piece, the
  player, a vanilla cone rock and a vanilla house for scale, at 1x and 3x;
- wiki/world/models/<name>.png (the sprite) and <name>_scene.png, which the wiki row links.

The row's `model_status` goes TODO -> IN-PROGRESS (a model file exists) -> IN-REVIEW (rendered, waiting
for the owner) -> APPROVED (the owner's call, set with --set). `model_tiles` is the real count of unique
8x8 tiles after flips (the number a tileset runs out of)."""
import csv
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

from . import model as M, render as R, preview as P, tiles as T

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODELS = os.path.join(HERE, "models", "scenery")
OUT = os.path.join(HERE, "output", "scenery")
WIKI_OUT = os.path.join(ROOT, "wiki", "world", "models")
CSV = os.path.join(ROOT, "wiki", "mapping", "world_art.csv")
GAME = os.path.join(ROOT, "game")
STATUSES = ("TODO", "IN-PROGRESS", "IN-REVIEW", "APPROVED")


def _rows():
    rows = list(csv.DictReader(open(CSV)))
    for c in ("model", "model_status", "model_png", "model_tiles"):
        for r in rows:
            r.setdefault(c, "")
    return rows


def _save(rows):
    with open(CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def name_of(art_id):
    return art_id.replace("art:", "").replace(":", "_")


def _grey(img):
    g = img.convert("LA")
    return Image.merge("RGBA", (g.getchannel(0),) * 3 + (g.getchannel(1),))


def _player():
    im = Image.open(os.path.join(GAME, "graphics/object_events/pics/people/brendan/walking.png")).convert("RGBA")
    a = np.array(im)
    a[..., 3] = np.where((a[..., :3] == a[0, 0, :3]).all(-1), 0, 255)    # index 0 is the key colour
    return Image.fromarray(a).crop((0, 0, 16, 32))


def _vanilla_refs():
    """A vanilla cone rock (2x2) and a vanilla house (Petalburg, 5x4) for scale, grey."""
    sys.path.insert(0, os.environ.get("TILEGEN_DIR", os.path.join(ROOT, "tools", "tile-generator")))
    from tilegen import gba
    L = gba.layouts()
    r111 = gba.render_layout(L["Route111_Layout"]).convert("RGBA")
    rock = r111.crop((16 * 16, 100 * 16, 18 * 16, 102 * 16))
    a = np.array(rock)
    key = [(222, 205, 131), (213, 180, 106), (238, 230, 164), (115, 197, 164), (164, 213, 197), (65, 180, 131)]
    for k in key:                                   # lift the rock off its sand and grass
        a[(a[..., :3] == k).all(-1), 3] = 0
    rock = Image.fromarray(a)
    pet = gba.render_layout(L["PetalburgCity_Layout"]).convert("RGBA")
    house = pet.crop((5 * 16, 2 * 16, 10 * 16, 6 * 16))
    return _grey(rock), _grey(house)


def scene(sprite, obj, row):
    """The piece on a 15x10-cell screen, south of the middle, with the player in front of it."""
    rock, house = _vanilla_refs()
    W, H = 15 * 16, 10 * 16
    bg = P.speckled(W, H, (176, 176, 168)).convert("RGBA")       # plain grey ground with sparse specks
    sy = max(H - 16 * 2 - sprite.height, 0)
    # scale references: a vanilla house on the left when there is room, a vanilla rock on the right;
    # the piece between them, the player standing just south of it
    room = sprite.width <= W - 5 * 16 - 3 * 16
    sx = 5 * 16 + 16 if room else (W - sprite.width) // 2
    if room:
        bg.alpha_composite(house, (0, H - 16 * 5))
    bg.alpha_composite(rock, (W - 32, H - 48))
    bg.alpha_composite(sprite, (sx, sy))
    bg.alpha_composite(_player(), (sx + sprite.width // 2 - 8, sy + sprite.height - 8))
    d = ImageDraw.Draw(bg)
    fp = obj.footprint_rows()
    top = sy + fp[0] * 16
    d.rectangle([sx, top, sx + sprite.width - 1, sy + sprite.height - 1], outline=(255, 60, 60, 180))
    big = bg.resize((W * 3, H * 3), Image.NEAREST)
    sheet = Image.new("RGB", (W + 12 + W * 3, H * 3 + 18), (28, 28, 32))
    dd = ImageDraw.Draw(sheet)
    dd.text((4, 2), f"{row['name']}  hit box {row['footprint']}  drawn {row['drawn']}  (red = hit box)", fill=(240, 240, 240))
    sheet.paste(bg.convert("RGB"), (0, 18))
    sheet.paste(big.convert("RGB"), (W + 12, 18))
    return sheet


def render(name, rows):
    path = os.path.join(MODELS, f"{name}.yaml")
    obj = M.Object(path)
    art = obj.raw.get("art")
    row = next((r for r in rows if r["concept_id"] == art), None)
    if row is None:
        raise SystemExit(f"{path}: `art: {art}` is not a row in world_art.csv")
    dw, dh = (int(v) for v in row["drawn"].split("x"))
    fw, fd = (int(v) for v in row["footprint"].split("x"))
    if obj.cells != (dw, dh):
        raise SystemExit(f"{name}: cells {list(obj.cells)} but the wiki row is drawn {row['drawn']}")
    if len(obj.footprint_rows()) != fd:
        raise SystemExit(f"{name}: footprint {len(obj.footprint_rows())} rows but the wiki row's hit box is {fd} deep")
    img, ind, warnings = R.render_object(obj)
    for w in warnings:
        print("WARNING", w)
    out = os.path.join(OUT, name)
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, "sprite.png"))
    P.review_sheet(img, obj, "common").save(os.path.join(out, "review.png"))
    sc = scene(img, obj, row)
    sc.save(os.path.join(out, "scene.png"))
    os.makedirs(WIKI_OUT, exist_ok=True)
    img.save(os.path.join(WIKI_OUT, f"{name}.png"))
    sc.save(os.path.join(WIKI_OUT, f"{name}_scene.png"))
    b = T.budget(ind, obj.palette)
    row["model"] = os.path.relpath(path, ROOT)
    row["model_png"] = f"world/models/{name}.png"
    row["model_tiles"] = str(b["unique_tiles"])
    if row["model_status"] in ("", "TODO", "IN-PROGRESS"):
        row["model_status"] = "IN-REVIEW"
    print(f"{name}: {obj.cells[0]}x{obj.cells[1]} cells, {b['unique_tiles']} unique tiles, {b['colours']} colours "
          f"-> {os.path.relpath(os.path.join(out, 'scene.png'), HERE)}")


def main(args):
    rows = _rows()
    if args.set:
        ident, st = args.set
        if st not in STATUSES:
            raise SystemExit(f"status must be one of {STATUSES}")
        r = next(r for r in rows if r["concept_id"] == ident)
        r["model_status"] = st
        _save(rows)
        print(ident, st)
        return
    # every scenery row is tracked: TODO until a model file exists
    have = {f[:-5] for f in os.listdir(MODELS) if f.endswith(".yaml")} if os.path.isdir(MODELS) else set()
    for r in rows:
        if r["category"] == "scenery":
            n = name_of(r["concept_id"])
            if not r["model_status"]:
                r["model_status"] = "IN-PROGRESS" if n in have else "TODO"
            elif r["model_status"] == "TODO" and n in have:
                r["model_status"] = "IN-PROGRESS"
    names = sorted(have) if args.all else (args.names or [])
    for n in names:
        render(n, rows)
    _save(rows)
    if args.status or not names:
        from collections import Counter
        sc = [r for r in rows if r["category"] == "scenery"]
        for r in sc:
            if args.status:
                print(f"{r['model_status']:12} {r['concept_id']:44} {r['drawn']:6} {r['model_tiles']:>4}  {r['model']}")
        print(dict(Counter(r["model_status"] for r in sc)))

"""Scenery models: the large static pieces of ../../wiki/mapping/world_art.csv (`category` scenery), as
low-poly greybox models rendered in the Emerald camera.

    python3 -m worldart scenery shared_crashed-tie-fighter        # one model (models/scenery/<name>.yaml)
    python3 -m worldart scenery --all                             # every model
    python3 -m worldart scenery --status                          # every scenery row and its model status
    python3 -m worldart scenery NAME --variant V --try turn=10     # one variant, tweaked, output/ only
    python3 -m worldart scenery NAME --sweep "turn=-12,0,12"       # each value side by side (sweep.png)

A model with `variants:` makes one drawing per variant (`<name>--<variant>.png`, and every variant on
`<name>_variants.png`); the first is the one the wiki row shows.

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

import yaml

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
    for c in ("model", "model_status", "model_png", "model_tiles", "model_variants"):
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


def variants_of(path):
    """[(variant name, raw model)]: the model as written when it has no `variants`, else one per variant,
    each deep-merged over the model (params merge key by key; `drop` lists part-name patterns to leave
    out; any other key replaces the model's: tilt, turn, sink, scale, mirror, foot...)."""
    raw = yaml.safe_load(open(path)) or {}
    vs = raw.pop("variants", None)
    if not vs:
        return [("base", raw)]
    out = []
    for vname, over in vs.items():
        over = dict(over or {})
        out.append((str(vname), M.deep_merge(raw, over)))
    return out


def clipped(img):
    """Sides of the sprite the art runs into (so it may be cut off). Keep a pixel clear on every side."""
    a = np.array(img)[..., 3] > 0
    return [side for side, edge in (("top", a[0]), ("bottom", a[-1]), ("left", a[:, 0]), ("right", a[:, -1]))
            if edge.any()]


def variant_sheet(name, shots, row):
    """Every variant side by side at 3x on grey ground, with its name and tile count."""
    s = 3
    w = max(im.width for _, im, _ in shots) * s
    h = max(im.height for _, im, _ in shots) * s
    cols = min(len(shots), max(1, 1200 // (w + 12)))
    rows_n = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 12) + 12, rows_n * (h + 30) + 24), (28, 28, 32))
    d = ImageDraw.Draw(sheet)
    d.text((8, 4), f"{row['name']} ({row['concept_id']}): {len(shots)} variants, hit box {row['footprint']}, drawn {row['drawn']}",
           fill=(240, 240, 240))
    for k, (vn, im, tiles) in enumerate(shots):
        x, y = 12 + (k % cols) * (w + 12), 24 + (k // cols) * (h + 30)
        bg = P.speckled(im.width, im.height, (176, 176, 168)).convert("RGBA")
        bg.alpha_composite(im)
        sheet.paste(bg.resize((im.width * s, im.height * s), Image.NEAREST).convert("RGB"), (x, y + 14))
        if row.get("footprint"):                      # the hit box: the bottom rows, in red
            fd = int(row["footprint"].split("x")[1])
            d.rectangle([x, y + 14 + im.height * s - fd * 16 * s, x + im.width * s - 1, y + 14 + im.height * s - 1],
                        outline=(255, 70, 70))
        d.text((x, y), f"{vn}  ({tiles} tiles)", fill=(220, 220, 220))
    return sheet


def _override(raw, key, value):
    """raw with `key` (dotted: params.fknee) set to `value` (a yaml string: 12, [4, 90], true)."""
    raw = M.deep_merge(raw, {})
    d = raw
    ks = key.split(".")
    for k in ks[:-1]:
        d = d.setdefault(k, {})
    d[ks[-1]] = yaml.safe_load(value) if isinstance(value, str) else value
    return raw


def sweep(name, spec, only=None, tries=()):
    """One key over several values, every chosen variant: a contact sheet to pick from."""
    path = os.path.join(MODELS, f"{name}.yaml")
    key, vals = spec.split("=", 1)
    vals = [v.strip() for v in vals.split(",")]
    shots = []
    for vn, raw in variants_of(path):
        if only and vn not in only:
            continue
        for t in tries:
            raw = _override(raw, *t.split("=", 1))
        for v in vals:
            obj = M.Object(path, _override(raw, key, v))
            img, ind, _ = R.render_object(obj)
            cut = clipped(img)
            label = f"{vn} {key}={v}" + (f"  CUT {'/'.join(cut)}" if cut else "")
            shots.append((label, img, T.budget(ind, obj.palette)["unique_tiles"]))
    art = vs_art(path)
    row = next((r for r in _rows() if r["concept_id"] == art), {"name": name, "concept_id": art, "footprint": "", "drawn": ""})
    out = os.path.join(OUT, name, "sweep.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    variant_sheet(name, shots, row).save(out)
    print(f"{len(shots)} renders -> {os.path.relpath(out, HERE)}")


def vs_art(path):
    return (yaml.safe_load(open(path)) or {}).get("art", "")


def render(name, rows, only=None, tries=()):
    path = os.path.join(MODELS, f"{name}.yaml")
    vs = variants_of(path)
    if only:
        vs = [v for v in vs if v[0] in only]
        if not vs:
            raise SystemExit(f"{name}: no variant {only}")
    dry = bool(tries) or bool(only)          # a partial or tweaked render never touches the wiki
    for t in tries:
        vs = [(vn, _override(raw, *t.split("=", 1))) for vn, raw in vs]
    art = vs[0][1].get("art")
    row = next((r for r in rows if r["concept_id"] == art), None)
    if row is None:
        raise SystemExit(f"{path}: `art: {art}` is not a row in world_art.csv")
    dw, dh = (int(v) for v in row["drawn"].split("x"))
    fw, fd = (int(v) for v in row["footprint"].split("x"))
    shots = []
    for k, (vn, raw) in enumerate(vs):
        obj = M.Object(path, raw)
        tag = name if vn == "base" else f"{name}--{vn}"
        if obj.cells != (dw, dh):
            raise SystemExit(f"{tag}: cells {list(obj.cells)} but the wiki row is drawn {row['drawn']}")
        if len(obj.footprint_rows()) != fd:
            raise SystemExit(f"{tag}: footprint {len(obj.footprint_rows())} rows but the wiki row's hit box is {fd} deep")
        img, ind, warnings = R.render_object(obj)
        for w in warnings:
            print("WARNING", w)
        cut = clipped(img)
        if cut:
            print(f"WARNING {tag}: the art is cut off at the {', '.join(cut)} edge: move `foot`, `scale` it or turn it")
        out = os.path.join(OUT, name) if vn == "base" else os.path.join(OUT, name, vn)
        os.makedirs(out, exist_ok=True)
        img.save(os.path.join(out, "sprite.png"))
        P.review_sheet(img, obj, "common").save(os.path.join(out, "review.png"))
        sc = scene(img, obj, row)
        sc.save(os.path.join(out, "scene.png"))
        b = T.budget(ind, obj.palette)
        shots.append((vn, img, b["unique_tiles"]))
        print(f"{tag}: {obj.cells[0]}x{obj.cells[1]} cells, {b['unique_tiles']} unique tiles, {b['colours']} colours "
              f"-> {os.path.relpath(os.path.join(out, 'scene.png'), HERE)}")
        if dry:
            continue
        os.makedirs(WIKI_OUT, exist_ok=True)
        img.save(os.path.join(WIKI_OUT, f"{tag}.png"))
        if k == 0:                                   # the first variant is the one the row shows
            sc.save(os.path.join(WIKI_OUT, f"{name}_scene.png"))
            row["model_png"] = f"world/models/{tag}.png"
            row["model_tiles"] = str(b["unique_tiles"])
    if dry:
        print("(--variant / --try: output/ only, the wiki is not changed)")
        return
    if len(shots) > 1:
        variant_sheet(name, shots, row).save(os.path.join(WIKI_OUT, f"{name}_variants.png"))
    row["model"] = os.path.relpath(path, ROOT)
    row["model_variants"] = " ".join(v for v, _, _ in shots) if len(shots) > 1 else ""
    if row["model_status"] in ("", "TODO", "IN-PROGRESS"):
        row["model_status"] = "IN-REVIEW"


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
    if getattr(args, "sweep", None):
        for n in names:
            sweep(n, args.sweep, args.variant, args.tries)
        return
    for n in names:
        render(n, rows, getattr(args, "variant", None), getattr(args, "tries", ()))
    _save(rows)
    if args.status or not names:
        from collections import Counter
        sc = [r for r in rows if r["category"] == "scenery"]
        for r in sc:
            if args.status:
                print(f"{r['model_status']:12} {r['concept_id']:44} {r['drawn']:6} {r['model_tiles']:>4}  {r['model']}")
        print(dict(Counter(r["model_status"] for r in sc)))

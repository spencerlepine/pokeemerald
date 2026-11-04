"""building-kit: outdoor buildings from a kit of walls, roofs, doors, windows and decor.

    python3 -m bkit list                                   # every blueprint and its kit
    python3 -m bkit try block-house --seed 3 [--width 5] [--set roof=dome]
    python3 -m bkit variants block-house [-n 12] [--width 5]
    python3 -m bkit parts tatooine                         # the kit's pieces, one by one
    python3 -m bkit sheet [--style tatooine] [-n 4]        # every blueprint, n seeds each
    python3 -m bkit street [--style tatooine] [--seed 1]   # a random street in a game screen
    python3 -m bkit init                                   # catalog entries for every area building
    python3 -m bkit build [--planet tatooine] [--no-wiki]  # render the catalog (wiki: buildings.csv, pngs)
    python3 -m bkit collage                                # every built building on one image

Everything goes to output/ (not committed). Nothing here writes the wiki yet.
"""
import argparse
import os
import random

from . import compose as C
from . import render as R

OUT = os.path.join(C.HERE, "output")


def _label(info, tiles):
    bits = " ".join(f"{k}={C.fmt(v)}" for k, v in info["picked"].items() if not isinstance(v, float))
    return f"seed {info['seed']}  {info['W']}w  {tiles}t  {bits}"[:70]


def _one(path, seed, width=None, sets=None):
    raw, params, info = C.compose(path, seed, width, sets)
    img, ind, warns, tiles = R.render(raw)
    for w in warns:
        print("WARNING", w)
    return img, info, tiles


def cmd_list(a):
    for p in C.all_blueprints(a.style):
        bp = C.load(p)
        print(f"{bp['style']:10} {bp['name']:16} width {bp.get('width')}  {bp.get('about', '')}")


def cmd_try(a):
    path = C.blueprint_path(a.blueprint)
    sets = dict(s.split("=", 1) for s in a.set or [])
    img, info, tiles = _one(path, a.seed, a.width, sets)
    d = os.path.join(OUT, info["style"], info["name"])
    os.makedirs(d, exist_ok=True)
    img.save(os.path.join(d, f"seed{a.seed}.png"))
    R.sheet(f"{info['blueprint']} seed {a.seed}: {img.width // 16}x{img.height // 16} cells, {tiles} tiles",
            [(_label(info, tiles), img)], scale=6).save(os.path.join(d, f"seed{a.seed}_6x.png"))
    print(f"{info['blueprint']} seed {a.seed}: {img.width // 16}x{img.height // 16} cells, {tiles} unique tiles")
    for k, v in info["picked"].items():
        print(f"  {k} = {C.fmt(v)}")
    print("->", os.path.relpath(os.path.join(d, f"seed{a.seed}_6x.png"), C.HERE))


def cmd_variants(a):
    path = C.blueprint_path(a.blueprint)
    shots = []
    for s in range(a.start, a.start + a.n):
        img, info, tiles = _one(path, s, a.width)
        shots.append((_label(info, tiles), img))
    bp = C.load(path)
    d = os.path.join(OUT, bp["style"], bp["name"])
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "variants.png")
    R.sheet(f"{bp['style']} / {bp['name']}: {a.n} seeds. {bp.get('about', '')}", shots, scale=a.scale).save(out)
    print("->", os.path.relpath(out, C.HERE))


def cmd_parts(a):
    """Each template of the style's kits that has a `preview`, alone, at its defaults."""
    shots = []
    for k in C.kit_files(a.style):
        kit = C.load(os.path.join(C.KITS, f"{k}.yaml"))
        for name, t in (kit.get("templates") or {}).items():
            if "preview" not in t:
                continue
            pv = t["preview"] or {}
            raw = {"name": f"part-{name}", "style": a.style}
            bp = {"name": f"part-{name}", "style": a.style, "width": [4],
                  "parts": [dict({"use": name, "name": name}, **pv)]}
            tmp = os.path.join(OUT, "_parts", f"{name}.yaml")
            os.makedirs(os.path.dirname(tmp), exist_ok=True)
            import yaml
            with open(tmp, "w") as fh:
                yaml.safe_dump(bp, fh)
            img, info, tiles = _one(tmp, 0)
            shots.append((f"{name} ({os.path.basename(k)})", img))
    out = os.path.join(OUT, f"parts_{a.style}.png")
    R.sheet(f"{a.style} kit: every piece alone, at its defaults", shots, scale=4, grid=True).save(out)
    print("->", os.path.relpath(out, C.HERE))


def cmd_sheet(a):
    shots = []
    for p in C.all_blueprints(a.style):
        for s in range(a.start, a.start + a.n):
            img, info, tiles = _one(p, s)
            shots.append((f"{info['blueprint']} {info['seed']} ({tiles}t)", img))
    out = os.path.join(OUT, f"sheet_{a.style or 'all'}.png")
    R.sheet(f"{a.style or 'every style'}: every blueprint, {a.n} seeds each", shots, scale=a.scale).save(out)
    print("->", os.path.relpath(out, C.HERE))


def cmd_street(a):
    rng = random.Random(a.seed)
    bps = C.all_blueprints(a.style)
    ims = []
    for k in range(14):
        p = rng.choice(bps)
        img, info, tiles = _one(p, rng.randrange(1000), rng.choice([None]))
        ims.append(img)
    img, n = R.street(ims, title=f"{a.style or 'all'} street, seed {a.seed}: a vanilla house (grey) for scale, the player on the path")
    out = os.path.join(OUT, f"street_{a.style or 'all'}_{a.seed}.png")
    img.save(out)
    print(f"{n} buildings ->", os.path.relpath(out, C.HERE))


def cmd_init(a):
    from . import catalog
    catalog.init()


def cmd_build(a):
    from . import catalog
    catalog.build(a.planet, wiki=not a.no_wiki, only=a.only)


def cmd_collage(a):
    from . import catalog
    catalog.collage()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bkit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("--style")
    s.set_defaults(fn=cmd_list)
    s = sub.add_parser("try")
    s.add_argument("blueprint")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--width", type=int)
    s.add_argument("--set", action="append", help="param=value, over what the seed picked")
    s.set_defaults(fn=cmd_try)
    s = sub.add_parser("variants")
    s.add_argument("blueprint")
    s.add_argument("-n", type=int, default=12)
    s.add_argument("--start", type=int, default=0)
    s.add_argument("--width", type=int)
    s.add_argument("--scale", type=int, default=3)
    s.set_defaults(fn=cmd_variants)
    s = sub.add_parser("parts")
    s.add_argument("style")
    s.set_defaults(fn=cmd_parts)
    s = sub.add_parser("sheet")
    s.add_argument("--style")
    s.add_argument("-n", type=int, default=4)
    s.add_argument("--start", type=int, default=0)
    s.add_argument("--scale", type=int, default=3)
    s.set_defaults(fn=cmd_sheet)
    s = sub.add_parser("street")
    s.add_argument("--style")
    s.add_argument("--seed", type=int, default=1)
    s.set_defaults(fn=cmd_street)
    s = sub.add_parser("init", help="add a catalog entry for every area building that has none")
    s.set_defaults(fn=cmd_init)
    s = sub.add_parser("build", help="render the catalog into the wiki")
    s.add_argument("--planet", action="append")
    s.add_argument("--no-wiki", action="store_true", help="output/build only, for trying")
    s.add_argument("--only", action="append", help="only entries whose id contains this")
    s.set_defaults(fn=cmd_build)
    s = sub.add_parser("collage")
    s.set_defaults(fn=cmd_collage)
    a = ap.parse_args(argv)
    a.fn(a)

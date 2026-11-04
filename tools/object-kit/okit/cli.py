"""python3 -m okit <command>: see README.md."""
import argparse
import os

from PIL import Image

from . import compose as C
from . import render as R

OUT = os.path.join(C.HERE, "output")


def _save(img, *path):
    p = os.path.join(OUT, *path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    return os.path.relpath(p, C.HERE)


def _footprint(s):
    if not s:
        return None
    w, d = s.lower().split("x")
    return int(w), int(d)


def make(path, seed, footprint=None, overrides=None, quiet=False):
    """Compose, render and measure one seed. Returns (sprite, info)."""
    raw, params, info = C.compose(path, seed, footprint, overrides)
    img, ind, warnings, tiles = R.render(raw, info)
    depth, west, east = R.hit_box(raw)
    info.update(tiles=tiles, rows=img.height // 16, depth=depth, west=west, east=east,
                fits=(depth <= info["D"] and west >= 0 and east < info["W"]), warnings=warnings)
    if not quiet:
        picked = ", ".join(f"{k}={C.fmt(v)}" for k, v in info["picked"].items())
        fit = "" if info["fits"] else f"  HIT BOX OVERFLOW: stands on {depth} rows, cells {west}-{east}"
        print(f"{info['blueprint']} seed {seed}: hit box {info['W']}x{info['D']}, drawn {info['W']}x{info['rows']}, "
              f"{tiles} tiles{fit}  [{picked}]")
        for w in warnings:
            print("  WARNING", w)
    return img, info


def label(info):
    return f"s{info['seed']} {info['W']}x{info['D']} drawn {info['rows']} ({info['tiles']}t){'' if info['fits'] else ' !'}"


def cmd_list(a):
    for p in C.all_blueprints(a.style):
        bp = C.load(p)
        fps = " ".join(f"{w}x{d}" for w, d in C.footprint_options(bp))
        print(f"{bp['style']}/{bp['name']:22} {bp.get('role', 'noise'):9} {fps:14} {bp.get('about', '')}")


def cmd_try(a):
    path = C.blueprint_path(a.blueprint)
    over = dict(kv.split("=", 1) for kv in a.set or [])
    img, info = make(path, a.seed, _footprint(a.footprint), over)
    big = R.sheet(f"{info['blueprint']} seed {a.seed}: {label(info)}", [(label(info), img, info["D"])], scale=6)
    print("->", _save(big, "try", f"{info['name']}-{a.seed}.png"))


def family(path, n, footprint=None, start=1):
    shots = []
    for s in range(start, start + n):
        img, info = make(path, s, footprint)
        shots.append((img, info))
    return shots


def write_family(path, n, footprint=None):
    """variants.png, scene.png and (edge pieces) border.png for one blueprint. Returns the shots."""
    shots = family(path, n, footprint)
    bp = C.load(path)
    style, name = bp["style"], bp["name"]
    fps = " ".join(f"{w}x{d}" for w, d in C.footprint_options(bp))
    title = f"{style}/{name} ({bp.get('role', 'noise')}, hit box {fps}): {bp.get('about', '')}"
    sh = R.sheet(title, [(label(i), im, i["D"]) for im, i in shots])
    print("->", _save(sh, style, name, "variants.png"))
    im, info = shots[0]
    print("->", _save(R.scene(im, info["D"], f"{style}/{name} seed {info['seed']} in a screen; red = hit box {info['W']}x{info['D']}"),
                      style, name, "scene.png"))
    if bp.get("role") == "edge":
        print("->", _save(R.border([(im, i["D"]) for im, i in shots], f"{style}/{name} as a map border (seeds cycle)"),
                          style, name, "border.png"))
    return shots


def cmd_variants(a):
    write_family(C.blueprint_path(a.blueprint), a.n, _footprint(a.footprint))


def cmd_sheet(a):
    for p in C.all_blueprints(a.style):
        write_family(p, a.n)


def cmd_collage(a):
    groups = []
    for p in C.all_blueprints(a.style):
        bp = C.load(p)
        shots = family(p, a.n)
        groups.append((f"{bp['style']}/{bp['name']}  ({bp.get('role', 'noise')}, hit box {' '.join(f'{w}x{d}' for w, d in C.footprint_options(bp))}): {bp.get('about', '')}",
                       [im for im, _ in shots]))
    out = R.collage(groups, f"object-kit: {len(groups)} families, {a.n} seeds each (greybox)", scale=a.scale)
    print("->", _save(out, a.out or "_collage.png"))


def cmd_catalog(a):
    from . import catalog as K
    K.report(a.planet)


def cmd_build(a):
    from . import catalog as K
    K.build(a.planet, a.wiki)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="okit", description="small world objects (nature, rocks, props, small structures) in greybox, from seeded blueprints")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list", help="every blueprint"); p.add_argument("--style"); p.set_defaults(f=cmd_list)
    p = sub.add_parser("try", help="one seed of a blueprint, 6x, with its hit box")
    p.add_argument("blueprint"); p.add_argument("--seed", type=int, default=1); p.add_argument("--footprint", help="WxD")
    p.add_argument("--set", action="append", metavar="PARAM=VALUE"); p.set_defaults(f=cmd_try)
    p = sub.add_parser("variants", help="n seeds side by side, a screen scene, a border strip for edge pieces")
    p.add_argument("blueprint"); p.add_argument("-n", type=int, default=8); p.add_argument("--footprint", help="WxD"); p.set_defaults(f=cmd_variants)
    p = sub.add_parser("sheet", help="variants of every blueprint of a style"); p.add_argument("--style"); p.add_argument("-n", type=int, default=6); p.set_defaults(f=cmd_sheet)
    p = sub.add_parser("collage", help="every family on one image"); p.add_argument("--style"); p.add_argument("-n", type=int, default=6)
    p.add_argument("--scale", type=int, default=2); p.add_argument("--out"); p.set_defaults(f=cmd_collage)
    p = sub.add_parser("catalog", help="the object list per planet (catalog/<planet>.yaml)"); p.add_argument("--planet"); p.set_defaults(f=cmd_catalog)
    p = sub.add_parser("build", help="render every designed catalog entry (output/build/, or --wiki)"); p.add_argument("--planet"); p.add_argument("--wiki", action="store_true"); p.set_defaults(f=cmd_build)
    a = ap.parse_args(argv)
    a.f(a)

"""python3 -m mockup render [area-id ...] [--planet P] [--all]   -> wiki/mockup/<planet>/<area>.png
python3 -m mockup world                                        -> wiki/mockup/<planet>/_planet.png and _world.png
python3 -m mockup missing                                      -> art ids with no entry in styles.yaml

Phase 1 (wiki/world) is read, never written. Per-area tweaks go in wiki/mockup/overrides/<area>.yaml."""
import argparse
import glob
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from . import draw
from .style import MOCK, WORLD, Styles, apply_overrides, load_area

ORDER = ["TATOOINE", "KASHYYYK", "SULLUST", "MUSTAFAR", "ENDOR", "BESPIN", "JEDHA", "YAVIN 4", "HOTH", "DAGOBAH",
         "KAMINO", "ILUM", "GRAND ARENA", "FELUCIA", "TYTHON", "ATOLLON", "MORTIS", "ASTEROID FIELD", "DEATH STAR", "SHARED"]


def _areas():
    out = []
    for p in sorted(glob.glob(str(WORLD / "**" / "*.yaml"), recursive=True)):
        doc = load_area(p)
        doc["_path"] = p
        out.append(doc)
    return out


def _out(doc):
    rel = os.path.relpath(os.path.dirname(doc["_path"]), WORLD)
    return MOCK / rel / f"{doc['id']}.png"


def cmd_render(a):
    st = Styles()
    docs = _areas()
    if a.ids:
        docs = [x for x in docs if x["id"] in a.ids]
    elif a.planet:
        docs = [x for x in docs if x.get("planet") == a.planet.upper()]
    elif not a.all:
        sys.exit("name areas, --planet P or --all")
    for doc in docs:
        img = draw.area(apply_overrides(doc), st, labels=not a.no_labels, grey=a.grey)
        out = _out(doc)
        if a.out:
            out = Path(a.out) / out.name
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
    print(f"{len(docs)} areas rendered")


def cmd_world(a):
    st = Styles()
    docs = _areas()
    panels = []
    for pl in ORDER + sorted({x.get("planet") for x in docs} - set(ORDER)):
        mine = [x for x in docs if x.get("planet") == pl and x.get("kind") in ("town", "route", "landmark", "space")]
        if not mine:
            continue
        if all(x.get("pos") is None for x in mine):
            cx = 0
            for x in mine:
                w = max(len(r) for r in x["grid"].splitlines() if r)
                x["pos"], cx = [cx, 0], cx + w + 4
        placed = [x for x in mine if x.get("pos") is not None]
        imgs = {x["id"]: draw.area(apply_overrides(x), st, labels=False) for x in placed}
        x0 = min(x["pos"][0] for x in placed)
        y0 = min(x["pos"][1] for x in placed)
        x1 = max(x["pos"][0] + imgs[x["id"]].width // draw.C for x in placed)
        y1 = max(x["pos"][1] + imgs[x["id"]].height // draw.C for x in placed)
        k = a.cell
        pad, head = 12, 30
        sheet = Image.new("RGB", ((x1 - x0) * k + 2 * pad, (y1 - y0) * k + 2 * pad + head), (24, 24, 30))
        dd = ImageDraw.Draw(sheet)
        dd.text((pad, 8), pl, font=draw.F_BIG, fill=(255, 255, 255))
        for x in placed:
            im = imgs[x["id"]].resize((imgs[x["id"]].width * k // draw.C, imgs[x["id"]].height * k // draw.C), Image.LANCZOS)
            sheet.paste(im, (pad + (x["pos"][0] - x0) * k, head + pad + (x["pos"][1] - y0) * k))
        for x in placed:
            w, h = imgs[x["id"]].width * k // draw.C, imgs[x["id"]].height * k // draw.C
            cx, cy = pad + (x["pos"][0] - x0) * k + w / 2, head + pad + (x["pos"][1] - y0) * k + h / 2
            draw.label(dd, x.get("name", x["id"]), cx, cy)
        out = MOCK / pl.lower().replace(" ", "-") / "_planet.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
        panels.append(sheet)
        print(os.path.relpath(out, MOCK))
    cols, gap = 4, 16
    cw = max(p.width for p in panels)
    rows = [panels[i:i + cols] for i in range(0, len(panels), cols)]
    H = sum(max(p.height for p in r) for r in rows) + gap * (len(rows) + 1)
    world = Image.new("RGB", (cols * cw + gap * (cols + 1), H), (24, 24, 30))
    y = gap
    for r in rows:
        x = gap
        for p in r:
            world.paste(p, (x, y))
            x += cw + gap
        y += max(p.height for p in r) + gap
    world.save(MOCK / "_world.png")
    print("_world.png", world.size)


def cmd_builds(a):
    """One sheet with every building type at three sizes, in Tatooine colours: wiki/mockup/_buildings.png."""
    from . import build
    st = Styles()
    pal, _ = st.terrain("TATOOINE")
    mat = st.material("TATOOINE")
    from . import kit
    kitn = {n for c in kit.CATEGORIES.values() for n in c}
    names = [n for n in dict.fromkeys(build.BUILDS) if n != "box" and n not in build.GIANTS and n not in kitn]
    sizes, cols, CW, CH = [(4, 3), (5, 4), (7, 5)], 6, 9, 7
    if a.giants:
        names, sizes, cols, CW, CH = build.GIANTS, [(14, 7), (20, 9)], 2, 22, 11
    rows = (len(names) * len(sizes) + cols - 1) // cols
    img = Image.new("RGB", (cols * CW * draw.C, rows * CH * draw.C), pal["ground"])
    d = ImageDraw.Draw(img, "RGBA")
    for i, (n, (w, h)) in enumerate((n, s) for n in names for s in sizes):
        gx, gy = (i % cols) * CW + 1, (i // cols) * CH + 1
        b = {"at": [gx, gy + CH - 2 - h], "size": [w, h], "door": w // 2}
        style = dict(mat, fill=mat["wall"], ring=mat["trim"], ground=pal["ground"], cliff=pal["cliff"], build=n)
        build.building(img, b, style, 7919 * (i + 1), a.grey)
        d.text((gx * draw.C, (gy + CH - 2) * draw.C + 4), f"{n}  {w}x{h}", font=draw.F, fill=(40, 30, 20))
    name = ("_giants" if a.giants else "_buildings") + ("-grey" if a.grey else "") + ".png"
    img.save(MOCK / name)
    print(name, img.size)


def cmd_kit(a):
    """One category on plain ground (no trees): each piece at its sizes in three seeded variations, with a
    person and a 4x3 house at the start of every row for scale. -> wiki/mockup/kit/<category>.png"""
    from . import build, kit
    st = Styles()
    planet = a.planet.upper()
    pal, _ = st.terrain(planet)
    mat = st.material(planet)
    cat = kit.CATEGORIES[a.category]
    seeds = [11, 23, 37]
    rows = []
    for name, (_, sizes) in cat.items():
        rows.append((name, [(s, sd) for s in sizes for sd in seeds]))
    ref_w = 1 + 4 + 1
    gap = 1
    width = max(ref_w + sum(s[0] + gap for s, _ in r) for _, r in rows) + 1
    heights = [max(3, max(s[1] for s, _ in r)) + 2 for _, r in rows]
    img = Image.new("RGB", (width * draw.C, (sum(heights) + 1) * draw.C), pal["ground"])
    d = ImageDraw.Draw(img, "RGBA")
    roles = st.roles if hasattr(st, "roles") else {"npc": {"body": "#e86fa0", "ring": "#8a2a50"}}
    style = dict(mat, fill=mat["wall"], ring=mat["trim"], ground=pal["ground"], cliff=pal["cliff"])
    y = 1
    for (name, items), hh in zip(rows, heights):
        base = y + hh - 2
        draw.person(d, {"at": [1, base - 1]}, roles)
        build.building(img, {"at": [2, base - 3], "size": [4, 3], "door": 2}, dict(style, build="block"), 5, a.grey)
        x = ref_w + 1
        for (w, h), sd in items:
            build.building(img, {"at": [x, base - h], "size": [w, h]}, dict(style, build=name), sd, a.grey)
            x += w + gap
        d.text((draw.C, base * draw.C + 3), f"{name}   sizes " + ", ".join(f"{w}x{h}" for w, h in cat[name][1])
               + "   (3 seeded variations each)", font=draw.F, fill=(40, 30, 20))
        y += hh
    out = MOCK / "kit"
    out.mkdir(exist_ok=True)
    fn = out / f"{a.category}{'-grey' if a.grey else ''}.png"
    img.save(fn)
    print(fn.name, img.size)


def cmd_missing(a):
    st = Styles()
    seen = set()
    for doc in _areas():
        for k in ("buildings", "props"):
            for o in doc.get(k) or []:
                if o.get("art") and o["art"] not in st.shapes:
                    seen.add(o["art"])
    for s in sorted(seen):
        print(s)
    print(f"{len(seen)} art ids without a shape")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mockup")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("ids", nargs="*")
    r.add_argument("--planet")
    r.add_argument("--all", action="store_true")
    r.add_argument("--no-labels", action="store_true")
    r.add_argument("--grey", action="store_true", help="buildings in neutral grey (the greybox look)")
    r.add_argument("--out", help="write here instead of wiki/mockup/<planet>/")
    w = sub.add_parser("world")
    w.add_argument("--cell", type=int, default=4, help="px per cell on the planet sheets")
    sub.add_parser("missing")
    bl = sub.add_parser("builds", help="sheet of every building type")
    bl.add_argument("--grey", action="store_true")
    bl.add_argument("--giants", action="store_true", help="the huge border pieces instead")
    k = sub.add_parser("kit", help="one building category on plain ground, for review")
    k.add_argument("category")
    k.add_argument("--planet", default="TATOOINE")
    k.add_argument("--grey", action="store_true")
    a = ap.parse_args(argv)
    {"render": cmd_render, "world": cmd_world, "missing": cmd_missing, "builds": cmd_builds, "kit": cmd_kit}[a.cmd](a)

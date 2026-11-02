"""python3 -m greybox piece <art-id|build> [--size WxH] [--seed N] [--planet P] [--grey]  -> wiki/world/greybox/<id>.png
python3 -m greybox piece --all                 every art id in world_art.csv that has a build; fills its `greybox` column
python3 -m greybox kit <category> [--grey]     one category, pieces side by side for review -> wiki/world/greybox/_kit-<category>.png
python3 -m greybox sheet [--grey]              every building model at three sizes -> wiki/world/greybox/_sheet-buildings.png
python3 -m greybox terrain <area-id> [--grey]  one area's terrain in relief with its pieces -> wiki/world/greybox/areas/<area>.png
python3 -m greybox room <area-id> [--grey]     one interior as a greybox room (walls, floor, blocks) -> wiki/world/greybox/rooms/<area>.png

What to draw comes from the wiki: `python3 -m blockout todo --tool greybox` (in ../blockout). The model for an art
id is its `build` column in wiki/mapping/world_art.csv; colours come from palettes.yaml and styles.yaml here."""
import argparse
import csv
import glob
import sys

from PIL import Image, ImageDraw

from . import draw
from .style import ASSETS, OUT, WORLD, Styles, load_area


def _areas():
    out = []
    for p in sorted(glob.glob(str(WORLD / "**" / "*.yaml"), recursive=True)):
        doc = load_area(p)
        doc["_path"] = p
        out.append(doc)
    return out


def _style(st, planet, build, art=None, seed=1):
    pal, _ = st.terrain(planet)
    if art:
        s = st.shape(art, planet, "building", seed)
    else:
        mat = st.material(planet)
        s = dict(mat, fill=mat["wall"], ring=mat["trim"])
    s = dict(s, build=build or s.get("build"), ground=pal["ground"])
    s.setdefault("cliff", pal["cliff"])
    return s, pal


def _render_piece(st, name, planet, size, seed, grey):
    """One sprite on transparent ground. `name` is an art id (looked up in the wiki) or a build name."""
    from . import build
    art = name if name.startswith("art:") else None
    row = st.assets.get(art) if art else None
    if art and row is None:
        sys.exit(f"{art} is not in {ASSETS}")
    if art and not row.get("build"):
        sys.exit(f"{art} has no build in world_art.csv (status {row.get('status')}); add one or pick a kit model")
    if size is None:
        fp = (row or {}).get("footprint") or "4x3"
        size = tuple(int(v) for v in fp.lower().split("x"))
    if planet is None:
        planet = (row or {}).get("planet") or "TATOOINE"
        if planet in ("SHARED", "NEW"):
            planet = "TATOOINE"
    s, pal = _style(st, planet, None if art else name, art, seed)
    if s.get("build") not in build.BUILDS:
        sys.exit(f"no model named {s.get('build')!r}; see `python3 -m greybox sheet` and kit.CATEGORIES")
    b = {"at": [0, 0], "size": list(size), "door": size[0] // 2}
    return build.sprite(b, s, seed, grey), planet


def cmd_piece(a):
    st = Styles()
    OUT.mkdir(parents=True, exist_ok=True)
    names = a.names
    if a.all:
        names = [k for k, r in st.assets.items() if r.get("build")]
    done = []
    for name in names:
        size = tuple(int(v) for v in a.size.lower().split("x")) if a.size else None
        sp, planet = _render_piece(st, name, a.planet and a.planet.upper(), size, a.seed, a.grey)
        fn = name.replace("art:", "").replace(":", "_") + ("-grey" if a.grey else "") + ".png"
        out = OUT / fn
        sp.save(out)
        done.append((name, fn))
        if not a.all:
            print(out, sp.size, planet)
    if a.all:
        rows = list(csv.DictReader(open(ASSETS)))
        paths = dict(done)
        for r in rows:
            if r["concept_id"] in paths and not a.grey:
                r["greybox"] = f"world/greybox/{paths[r['concept_id']]}"
        with open(ASSETS, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"{len(done)} pieces -> {OUT}")


def cmd_sheet(a):
    """Every building model at three sizes, in Tatooine colours."""
    from . import build, kit
    st = Styles()
    pal, _ = st.terrain("TATOOINE")
    mat = st.material("TATOOINE")
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
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / (("_sheet-giants" if a.giants else "_sheet-buildings") + ("-grey" if a.grey else "") + ".png")
    img.save(out)
    print(out, img.size)


def cmd_kit(a):
    """One category on plain ground (no trees): each piece at its sizes in three seeded variations, with a
    person and a 4x3 house at the start of every row for scale."""
    from . import build, kit
    st = Styles()
    planet = a.planet.upper()
    pal, _ = st.terrain(planet)
    mat = dict(st.material(planet), **kit.MATERIAL.get(a.category, {}))
    cat = kit.CATEGORIES[a.category]
    if a.category == "interiors":                       # props sit on a room floor, not on ground
        from . import room as _room
        rc = _room.colours(st, planet, a.grey)
        pal = dict(pal, ground=rc["floor"], cliff=rc["trim"])
    seeds = [11, 23, 37]
    rows = []
    for name, (_, sizes) in cat.items():
        rows.append((name, [(s, sd) for s in sizes for sd in seeds]))
    ref_w = 1 + 4 + 1
    gap = 1
    width = max(ref_w + sum(s[0] + gap for s, _ in r) for _, r in rows) + 1
    heights = [max(3, max(s[1] for s, _ in r)) + 2 + (1 if a.category in kit.SIGNED else 0) for _, r in rows]
    img = Image.new("RGB", (width * draw.C, (sum(heights) + 1) * draw.C), pal["ground"])
    d = ImageDraw.Draw(img, "RGBA")
    style = dict(mat, fill=mat["wall"], ring=mat["trim"], ground=pal["ground"], cliff=pal["cliff"])
    y = 1
    for (name, items), hh in zip(rows, heights):
        base = y + hh - 2
        draw.person(d, {"at": [1, base - 1]}, st.roles)
        build.building(img, {"at": [2, base - 3], "size": [4, 3], "door": 2}, dict(style, build="block"), 5, a.grey)
        x = ref_w + 1
        for (w, h), sd in items:
            build.building(img, {"at": [x, base - h], "size": [w, h]}, dict(style, build=name), sd, a.grey)
            if a.category in kit.SIGNED:          # the game's sign out front
                draw.sign(d, {"at": [x + w // 2 + 2, base]})
            x += w + gap
        ly = base + (1 if a.category in kit.SIGNED else 0)
        d.text((draw.C, ly * draw.C + 3), f"{name}   sizes " + ", ".join(f"{w}x{h}" for w, h in cat[name][1])
               + "   (3 seeded variations each)", font=draw.F, fill=(40, 30, 20))
        y += hh
    OUT.mkdir(parents=True, exist_ok=True)
    fn = OUT / f"_kit-{a.category}{'-grey' if a.grey else ''}.png"
    img.save(fn)
    print(fn, img.size)


def cmd_terrain(a):
    """One area in relief: heights derived from its grid (rock runs become plateaus with cliff faces), 3D
    nature by planet, and its placed pieces drawn with their greybox models."""
    st = Styles()
    docs = [x for x in _areas() if x["id"] in a.ids]
    missing = set(a.ids) - {x["id"] for x in docs}
    if missing:
        sys.exit(f"unknown areas: {sorted(missing)}")
    out_dir = OUT / "areas"
    out_dir.mkdir(parents=True, exist_ok=True)
    for doc in docs:
        img = draw.area(doc, st, labels=not a.no_labels, grey=a.grey, relief=True)
        out = out_dir / f"{doc['id']}{'-grey' if a.grey else ''}.png"
        img.save(out)
        print(out, img.size)


def cmd_room(a):
    """One interior area as a room: its vanilla walls and floor in the planet's interior colours, blocked cells
    as low greybox slabs, doors, stairs and people."""
    from . import room as _room
    st = Styles()
    docs = [x for x in _areas() if x["id"] in a.ids]
    missing = set(a.ids) - {x["id"] for x in docs}
    if missing:
        sys.exit(f"unknown areas: {sorted(missing)}")
    out_dir = OUT / "rooms"
    out_dir.mkdir(parents=True, exist_ok=True)
    for doc in docs:
        if doc.get("kind") != "interior":
            sys.exit(f"{doc['id']} is a {doc.get('kind')}, not an interior; use `terrain`")
        img = _room.room(doc, st, labels=not a.no_labels, grey=a.grey)
        out = out_dir / f"{doc['id']}{'-grey' if a.grey else ''}.png"
        img.save(out)
        print(out, img.size)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="greybox", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("piece", help="one piece by art id or model name")
    p.add_argument("names", nargs="*")
    p.add_argument("--all", action="store_true", help="every art id with a build")
    p.add_argument("--size", help="WxH in cells (default: the wiki footprint)")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--planet", help="palette (default: the asset's planet)")
    p.add_argument("--grey", action="store_true", help="pure greybox colours")
    s = sub.add_parser("sheet", help="every building model at three sizes")
    s.add_argument("--grey", action="store_true")
    s.add_argument("--giants", action="store_true")
    k = sub.add_parser("kit", help="one category side by side for review")
    k.add_argument("category")
    k.add_argument("--planet", default="TATOOINE")
    k.add_argument("--grey", action="store_true")
    t = sub.add_parser("terrain", help="one area in relief")
    t.add_argument("ids", nargs="+")
    t.add_argument("--no-labels", action="store_true")
    t.add_argument("--grey", action="store_true")
    r = sub.add_parser("room", help="one interior as a greybox room")
    r.add_argument("ids", nargs="+")
    r.add_argument("--no-labels", action="store_true")
    r.add_argument("--grey", action="store_true")
    a = ap.parse_args(argv)
    {"piece": cmd_piece, "sheet": cmd_sheet, "kit": cmd_kit, "terrain": cmd_terrain, "room": cmd_room}[a.cmd](a)

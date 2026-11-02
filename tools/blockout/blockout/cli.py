"""python3 -m blockout new <area-id> --replaces <VanillaMap> --planet P --kind town --name NAME
       -> wiki/world/<planet>/<area-id>.yaml, its grid imported from the vanilla map's collision
python3 -m blockout render [area.yaml ...]   -> <area>.png next to each file (default: every area)
python3 -m blockout check  [area.yaml ...]   -> layout problems, exit 1 if any
python3 -m blockout index                    -> wiki/world/INDEX.csv: every area and every placed piece
python3 -m blockout guide                    -> wiki/world/GUIDE.md: planets, areas, connections, ship links"""
import argparse
import csv
import glob
import os
import sys

import yaml

from .area import Area
from . import vanilla as V

WORLD = V.ROOT / "wiki" / "world"


class _Dumper(yaml.SafeDumper):
    pass


_Dumper.add_representer(str, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|" if "\n" in s else None))


def _all():
    return sorted(glob.glob(str(WORLD / "**" / "*.yaml"), recursive=True))


def cmd_new(a):
    rows, (w, h) = V.terrain_grid(a.replaces) if a.replaces != "new" else (["." * a.size[0]] * a.size[1], a.size)
    ev = V.events(a.replaces) if a.replaces != "new" else {}
    exits = []
    for c in ev.get("connections", []):
        if c["edge"] in ("up", "down", "left", "right"):
            edge = {"up": "north", "down": "south", "left": "west", "right": "east"}[c["edge"]]
            line = {"north": rows[0], "south": rows[-1], "west": [r[0] for r in rows], "east": [r[-1] for r in rows]}[edge]
            cells = [i for i, ch in enumerate(line) if ch not in "x#T~"]
            exits.append({"edge": edge, "cells": cells, "to": c["to"]})
    doc = {"id": a.id, "name": a.name or a.id.upper(), "planet": a.planet, "kind": a.kind, "replaces": a.replaces,
           "status": "TODO", "story": "", "grid": "\n".join(rows) + "\n", "exits": exits,
           "buildings": [], "props": [], "people": [], "signs": [], "warps": [],
           "todo": [f"vanilla doors: {len(ev.get('warps', []))}, people: {len(ev.get('people', []))}, "
                    f"signs: {len(ev.get('signs', []))}"] if ev else []}
    out = WORLD / a.planet.lower().replace(" ", "-") / f"{a.id}.yaml"
    os.makedirs(out.parent, exist_ok=True)
    if out.exists() and not a.force:
        sys.exit(f"{out} exists (use --force)")
    with open(out, "w") as fh:
        yaml.dump(doc, fh, Dumper=_Dumper, sort_keys=False, width=140, allow_unicode=True, default_flow_style=None)
    print(out)


def import_map(name, cat, pos, const_to_name, force=False):
    """Write the area file for one vanilla map, from its collision, people and connections."""
    from . import catalog as K
    m = cat[name]
    out = K.path_for(m)
    if os.path.exists(out) and not force:
        return None
    rows, (w, h) = V.terrain_grid(name)
    ev = V.events(name)
    by_const = {c: cat[n]["area"] for c, n in const_to_name.items() if n in cat}
    exits = []
    for c in ev["connections"]:
        edge = {"up": "north", "down": "south", "left": "west", "right": "east"}.get(c["edge"])
        if not edge:
            continue
        nb = const_to_name.get(c["to"])
        lay = None
        line = {"north": rows[0], "south": rows[-1], "west": "".join(r[0] for r in rows), "east": "".join(r[-1] for r in rows)}[edge]
        lo = max(c["offset"], 0)
        hi = len(line)
        if nb and nb in pos and name in pos:
            # the neighbour's extent along this edge, in this map's cells
            from . import vanilla as _V
            bw, bh = _sizes(nb)
            hi = min(len(line), c["offset"] + (bw if edge in ("north", "south") else bh))
        cells = [i for i in range(lo, hi) if line[i] in ".:\"=Hv^<>~"]
        exits.append({"edge": edge, "cells": cells, "to": by_const.get(c["to"], c["to"])})
    people = [p for p in ev["people"]]
    doc = {"id": m["area"], "name": m["sw_name"] if m["kind"] in ("town", "route") else m["area"].replace("-", " ").upper(),
           "planet": m["planet"], "kind": m["kind"], "replaces": name, "status": "TODO", "story": "",
           "pos": list(pos[name]) if name in pos else None,
           "grid": "\n".join(rows) + "\n", "exits": exits, "buildings": [], "props": [],
           "people": people, "signs": ev["signs"],
           "warps": [{"name": "Door", "at": wp["at"], "to": by_const.get(wp["to"], wp["to"])} for wp in ev["warps"]],
           "todo": ["Imported from vanilla: '#' cells are vanilla buildings, cliffs and fences; replace them with this area's own buildings and props."]}
    if doc["pos"] is None:
        del doc["pos"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        yaml.dump(doc, fh, Dumper=_Dumper, sort_keys=False, width=160, allow_unicode=True, default_flow_style=None)
    return out


_SZ = {}


def _sizes(name):
    if name not in _SZ:
        lay = V._gba().layouts()[V.map_json(name)["layout"]]
        _SZ[name] = (lay.width, lay.height)
    return _SZ[name]


def cmd_import_all(a):
    from . import catalog as K
    cat = K.maps()
    pos, const_to_name = V.world_positions()
    n = 0
    for name in sorted(cat):
        if a.only and not any(name.startswith(o) for o in a.only):
            continue
        try:
            out = import_map(name, cat, pos, const_to_name, a.force)
        except Exception as e:  # noqa: BLE001 - report and carry on with the other maps
            print("FAILED", name, e)
            continue
        if out:
            n += 1
    print(f"{n} areas written")


def cmd_render(a):
    from .render import sheet
    paths = a.areas or [p for p in _all() if Area(p).status != "TODO"]   # TODO areas are rendered on request
    for p in paths:
        ar = Area(p)
        van = V.render(ar.replaces) if ar.replaces and ar.replaces != "new" else None
        out = os.path.splitext(p)[0] + ".png"
        sheet(ar, van).save(out)
        probs = ar.check()
        print(f"{os.path.relpath(out, V.ROOT)}  {ar.w}x{ar.h}  {len(ar.pieces())} pieces  {len(probs)} problems")
        for q in probs:
            print("   ", q)


def layout_planet(areas, root=None):
    """Set each overworld area's `pos` from its exits: a neighbour sits across the shared edge with
    the two exits' centres lined up. Returns (positions, problems)."""
    by_id = {x.id: x for x in areas}
    ext = {x.id: x for x in areas if x.exits}
    if not ext:
        return {}, []
    opposite = {"north": "south", "south": "north", "west": "east", "east": "west"}
    probs = []
    root = root if root in ext else sorted(ext, key=lambda i: (by_id[i].kind != "town", i))[0]
    pos = {}
    groups = []
    for start in [root] + sorted(ext):
        if start in pos:
            continue
        pos[start] = (0, 0)
        groups.append(_grow(start, by_id, pos, probs, opposite))
    # groups after the first (reached by doors, not by walking) go in a row below the main one
    if len(groups) > 1:
        def box(g):
            return (min(pos[i][0] for i in g), min(pos[i][1] for i in g),
                    max(pos[i][0] + by_id[i].w for i in g), max(pos[i][1] + by_id[i].h for i in g))
        _, _, _, by1 = box(groups[0])
        bx0, _, _, _ = box(groups[0])
        cx = bx0
        for g in groups[1:]:
            x0, y0, x1, y1 = box(g)
            for i in g:
                pos[i] = (pos[i][0] - x0 + cx, pos[i][1] - y0 + by1 + 12)
            cx += x1 - x0 + 12
    return _overlaps(pos, by_id, probs)


def _grow(root, by_id, pos, probs, opposite):
    group = [root]
    todo = [root]
    while todo:
        aid = todo.pop(0)
        a = by_id[aid]
        ax, ay = pos[aid]
        for e in a.exits:
            b = by_id.get(e.get("to"))
            if b is None:
                probs.append(f"{aid}: exit {e['edge']} goes to {e.get('to')}, which is not on this planet")
                continue
            back = [f for f in b.exits if f.get("to") == aid and f["edge"] == opposite[e["edge"]]]
            if not back:
                probs.append(f"{aid}: exit {e['edge']} to {b.id} has no matching {opposite[e['edge']]} exit back")
                continue
            ca = sum(e["cells"]) / len(e["cells"])
            cb = sum(back[0]["cells"]) / len(back[0]["cells"])
            if e["edge"] == "north":
                p = (round(ax + ca - cb), ay - b.h)
            elif e["edge"] == "south":
                p = (round(ax + ca - cb), ay + a.h)
            elif e["edge"] == "west":
                p = (ax - b.w, round(ay + ca - cb))
            else:
                p = (ax + a.w, round(ay + ca - cb))
            if b.id in pos:
                if pos[b.id] != p:
                    probs.append(f"{aid} -> {b.id}: loop does not close ({pos[b.id]} vs {p}); shift one of them")
                continue
            pos[b.id] = p
            todo.append(b.id)
            group.append(b.id)
    return group


def _overlaps(pos, by_id, probs):
    ids = list(pos)
    for i, m in enumerate(ids):
        for n in ids[i + 1:]:
            (mx, my), (nx, ny) = pos[m], pos[n]
            A, B = by_id[m], by_id[n]
            if mx < nx + B.w and nx < mx + A.w and my < ny + B.h and ny < my + A.h:
                ox = min(mx + A.w, nx + B.w) - max(mx, nx)
                oy = min(my + A.h, ny + B.h) - max(my, ny)
                probs.append(f"{m} and {n} overlap by {ox}x{oy} cells")
    return pos, probs


def _write_pos(path, p):
    import re as _re
    s = open(path).read()
    line = f"pos: [{p[0]}, {p[1]}]"
    if _re.search(r"^pos: .*$", s, _re.M):
        s = _re.sub(r"^pos: .*$", line, s, flags=_re.M)
    else:
        s = s.replace("\ngrid: |", f"\n{line}\ngrid: |", 1)
    open(path, "w").write(s)


def cmd_layout(a):
    areas = [Area(p) for p in _all()]
    for pl in a.planets:
        mine = [x for x in areas if x.planet == pl and x.kind in ("town", "route", "landmark")]
        pos, probs = layout_planet(mine, a.root)
        for x in mine:
            if x.id in pos:
                _write_pos(x.path, pos[x.id])
        print(f"{pl}: {len(pos)} areas placed")
        for q in probs:
            print("   ", q)


def cmd_world(a):
    from PIL import Image
    from . import overview as O
    areas = [Area(p) for p in _all()]
    planets = sorted({x.planet for x in areas})
    for pl in planets:
        mine = [x for x in areas if x.planet == pl]
        img = O.stitch(mine, f"{pl}: overworld blockout ({sum(1 for x in mine if x.status != 'TODO')}/{len(mine)} areas laid out)")
        side = O.side_list(mine, img.height if img else 400)
        if img is None:
            img = Image.new("RGB", (10, side.height), (28, 28, 32))
        out = Image.new("RGB", (img.width + side.width, max(img.height, side.height)), (28, 28, 32))
        out.paste(img, (0, 0))
        out.paste(side, (img.width, 0))
        path = WORLD / pl.lower().replace(" ", "-") / "_planet.png"
        out.save(path)
        print(os.path.relpath(path, V.ROOT))
    img = O.stitch(areas, "The whole world, overworld areas (orange label = not laid out yet)", tint=True)
    img.save(WORLD / "_world.png")
    print("wiki/world/_world.png", img.size)


def cmd_check(a):
    bad = 0
    for p in a.areas or _all():
        for q in Area(p).check():
            print(f"{p}: {q}")
            bad += 1
    sys.exit(1 if bad else 0)


def cmd_index(a):
    art = {}
    wa = V.ROOT / "wiki" / "mapping" / "world_art.csv"
    for r in csv.DictReader(open(wa)):
        art[r["concept_id"]] = r
    out = WORLD / "INDEX.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["area", "planet", "kind", "replaces", "layout_status", "piece_kind", "piece", "size", "art",
                    "art_known", "art_status"])
        for p in _all():
            ar = Area(p)
            w.writerow([ar.id, ar.planet, ar.kind, ar.replaces, ar.status, "area", ar.name, f"{ar.w}x{ar.h}", "", "", ""])
            for pc in ar.pieces():
                aid = pc.get("art", "")
                known = "yes" if aid in art else ("" if not aid else "NEW")
                st = "PLACEHOLDER" if pc["kind"] in ("person", "sign", "warp") else "TODO"
                w.writerow([ar.id, ar.planet, ar.kind, ar.replaces, ar.status, pc["kind"], pc.get("name", ""),
                            "x".join(str(v) for v in pc.get("size", [1, 1])), aid, known, st])
    print(out)


ORDER = ["TATOOINE", "KASHYYYK", "SULLUST", "MUSTAFAR", "ENDOR", "BESPIN", "JEDHA", "YAVIN 4", "HOTH", "DAGOBAH",
         "KAMINO", "ILUM", "GRAND ARENA", "FELUCIA", "TYTHON", "ATOLLON", "MORTIS", "ASTEROID FIELD", "SHARED"]


def cmd_guide(a):
    """wiki/world/GUIDE.md: every planet, its areas, how they connect and where ships land."""
    areas = [Area(p) for p in _all()]
    by_id = {x.id: x for x in areas}
    planets = ORDER + sorted({x.planet for x in areas} - set(ORDER))
    L = ["# World guide", "",
         "Generated by `python3 -m blockout guide` from the area files; do not edit by hand.", "",
         f"{len(areas)} areas: " + ", ".join(f"{sum(1 for x in areas if x.status == s)} {s}" for s in ("TODO", "BLOCKOUT", "APPROVED")) + ".",
         "Each planet is its own map; ships link them. Ship rooms use the StarNAV console to pick a planet.", ""]
    for pl in planets:
        mine = [x for x in areas if x.planet == pl]
        if not mine:
            continue
        slug = pl.lower().replace(" ", "-")
        over = [x for x in mine if x.kind in ("town", "route", "landmark", "space")]
        caves = [x for x in mine if x.kind == "dungeon"]
        rooms = [x for x in mine if x.kind == "interior"]
        L += [f"## {pl.title()}", "", f"Overview: [{slug}/_planet.png]({slug}/_planet.png). "
              f"{len(over)} overworld areas, {len(caves)} cave rooms, {len(rooms)} interiors.", ""]
        if over:
            L += ["| Area | Kind | Built from | Connects to | What it is |", "|---|---|---|---|---|"]
            for x in sorted(over, key=lambda x: (x.kind != "town", x.id)):
                links = sorted({e.get("to") for e in x.exits if e.get("to")})
                rel = os.path.relpath(x.path, WORLD)
                story = " ".join(str(x.story).split())
                L.append(f"| [{x.name}]({rel}) | {x.kind} | {x.replaces} | {', '.join(links) or '(doors only)'} | {story} |")
            L.append("")
        ships = []
        for x in mine:
            for o in x.buildings + x.warps:
                t = o.get("to") or ""
                if "hangar" in t or "(ships)" in o.get("name", "") or "berth" in o.get("name", "").lower():
                    ships.append(f"{o.get('name')} in {x.name} -> {t}")
        if ships:
            L += ["Ship links: " + "; ".join(sorted(set(ships))) + ".", ""]
        new = [x.name for x in mine if x.replaces == "new"]
        if new:
            L += ["New areas (not in vanilla): " + ", ".join(sorted(new)) + ".", ""]
        if caves:
            L += ["Caves: " + ", ".join(x.id for x in sorted(caves, key=lambda x: x.id)) + ".", ""]
    out = WORLD / "GUIDE.md"
    out.write_text("\n".join(L) + "\n")
    print(out)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="blockout")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("id")
    n.add_argument("--replaces", default="new")
    n.add_argument("--planet", required=True)
    n.add_argument("--kind", default="town")
    n.add_argument("--name")
    n.add_argument("--size", type=int, nargs=2, default=[20, 20])
    n.add_argument("--force", action="store_true")
    for name in ("render", "check"):
        s = sub.add_parser(name)
        s.add_argument("areas", nargs="*")
    sub.add_parser("index")
    sub.add_parser("world")
    sub.add_parser("guide")
    lo = sub.add_parser("layout")
    lo.add_argument("planets", nargs="+")
    lo.add_argument("--root")
    ia = sub.add_parser("import-all")
    ia.add_argument("--force", action="store_true")
    ia.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    {"new": cmd_new, "world": cmd_world, "layout": cmd_layout, "import-all": cmd_import_all, "render": cmd_render, "check": cmd_check, "index": cmd_index, "guide": cmd_guide}[a.cmd](a)

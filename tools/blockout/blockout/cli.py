"""python3 -m blockout new <area-id> --replaces <VanillaMap> --planet P --kind town --name NAME
       -> wiki/world/<planet>/<area-id>.yaml, its grid imported from the vanilla map's collision
python3 -m blockout render [area.yaml ...]   -> <area>.png next to each file (default: every area)
python3 -m blockout check  [area.yaml ...]   -> layout problems, exit 1 if any
python3 -m blockout index                    -> wiki/world/INDEX.csv: every area and every placed piece"""
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
        cells = [i for i in range(lo, hi) if line[i] in ".:\"=Hv^<>"]
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
    ia = sub.add_parser("import-all")
    ia.add_argument("--force", action="store_true")
    ia.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    {"new": cmd_new, "world": cmd_world, "import-all": cmd_import_all, "render": cmd_render, "check": cmd_check, "index": cmd_index}[a.cmd](a)

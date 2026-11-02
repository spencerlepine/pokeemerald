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
    return sorted(glob.glob(str(WORLD / "*" / "*.yaml")))


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


def cmd_render(a):
    from .render import sheet
    for p in a.areas or _all():
        ar = Area(p)
        van = V.render(ar.replaces) if ar.replaces and ar.replaces != "new" else None
        out = os.path.splitext(p)[0] + ".png"
        sheet(ar, van).save(out)
        probs = ar.check()
        print(f"{os.path.relpath(out, V.ROOT)}  {ar.w}x{ar.h}  {len(ar.pieces())} pieces  {len(probs)} problems")
        for q in probs:
            print("   ", q)


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
    a = ap.parse_args(argv)
    {"new": cmd_new, "render": cmd_render, "check": cmd_check, "index": cmd_index}[a.cmd](a)

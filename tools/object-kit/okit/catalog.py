"""The catalog: every small object each planet needs, one entry per object, in `catalog/<planet>.yaml`.

    planet: TATOOINE
    objects:
      - id: obj:tatooine:sandstone-boulder    # unique, never reused
        name: Sandstone boulder
        role: edge          # edge (blocks, frames paths) | noise (corners, dead space) | landmark | walkable
        footprint: [2, 1]   # the hit box, W x D cells (the drawn sprite is taller: rows above are walk-behind)
        art: art:tatooine:sandstone-boulder    # the wiki world_art.csv row it draws, or empty (new)
        blueprint: tatooine/sandstone-boulder  # the family that draws it; empty = still to design
        seeds: [1, 2, 3]    # optional: the picked variations (default: the first 6 seeds)
        about: one line on what it is

`catalog` prints the list and what is designed; `build` renders every designed entry at its footprint
to `output/build/<planet>/` with one sheet per planet. Nothing here writes the wiki yet.
"""
import glob
import os

import yaml

from . import compose as C

CATALOG = os.path.join(C.HERE, "catalog")


def planets():
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(CATALOG, "*.yaml")))


def load(planet):
    with open(os.path.join(CATALOG, f"{planet}.yaml")) as fh:
        return yaml.safe_load(fh) or {}


def report(only=None):
    total = done = 0
    for pl in planets():
        if only and pl != only:
            continue
        objs = load(pl).get("objects") or []
        d = sum(1 for o in objs if o.get("blueprint"))
        total, done = total + len(objs), done + d
        print(f"\n{pl}: {len(objs)} objects, {d} designed")
        for o in objs:
            fp = "x".join(str(v) for v in o["footprint"])
            mark = o["blueprint"] or "-"
            print(f"  {'*' if o.get('blueprint') else ' '} {o['name']:28} {o['role']:9} {fp:4} {mark:28} {o.get('art') or '(new)'}")
    print(f"\n{total} objects, {done} designed")


def build(only=None, wiki=False):
    from .cli import make, _save, label
    from . import render as R
    if wiki:
        raise SystemExit("--wiki is not wired yet: the owner approves the look first (README)")
    for pl in planets():
        if only and pl != only:
            continue
        shots = []
        for o in load(pl).get("objects") or []:
            if not o.get("blueprint"):
                continue
            path = C.blueprint_path(o["blueprint"])
            for s in o.get("seeds") or range(1, 7):
                img, info = make(path, s, tuple(o["footprint"]), quiet=True)
                slug = o["id"].split(":")[-1]
                _save(img, "build", pl, f"{slug}-{s}.png")
                shots.append((f"{o['name']} {label(info)}", img, info["D"]))
                if not info["fits"]:
                    print(f"  {o['id']} seed {s}: does not fit its {info['W']}x{info['D']} hit box")
        if shots:
            print("->", _save(R.sheet(f"{pl}: every designed object at its catalog footprint", shots, scale=2), "build", f"_sheet_{pl}.png"))

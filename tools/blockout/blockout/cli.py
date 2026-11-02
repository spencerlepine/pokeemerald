"""python3 -m blockout new <area-id> --replaces <VanillaMap> --planet P --kind town --name NAME
       -> wiki/world/<planet>/<area-id>.yaml, its grid imported from the vanilla map's collision
python3 -m blockout render [area.yaml ...]   -> <area>.png next to each file (default: every area)
python3 -m blockout check  [area.yaml ...]   -> layout problems, exit 1 if any
python3 -m blockout index                    -> wiki/world/INDEX.csv: every area and every placed piece
python3 -m blockout world-tiles              -> <planet>/_planet_tiles.png and _world_tiles.png from the greybox terrain renders
python3 -m blockout guide                    -> wiki/world/GUIDE.md and CONNECTIONS.csv (the area graph)
python3 -m blockout todo [--status S] [--planet P] [--kind K] [--tool T] [--csv]   -> what to draw next
python3 -m blockout todo --set <area-id or art id> <status>                           -> record progress"""
import argparse
import csv
import re
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
    if os.path.exists(out):   # hand-written travel links (ships, shuttles, dives) survive a re-import
        old = yaml.safe_load(open(out)) or {}
        if old.get("travel"):
            doc["travel"] = old["travel"]
        if old.get("pos") is not None:   # keep the planet layout (`blockout layout`) over vanilla's position
            doc["pos"] = old["pos"]
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
    # each planet is its own map, so the world sheet is one panel per planet, in story order
    panels = []
    for pl in [p for p in ORDER if p in planets] + [p for p in planets if p not in ORDER]:
        mine = [x for x in areas if x.planet == pl and x.kind in ("town", "route", "landmark", "space")]
        if mine and all(x.pos is None for x in mine):   # door-linked islands: show them side by side
            cx = 0
            for x in mine:
                x.pos, cx = [cx, 0], cx + x.w + 4
        im = O.stitch(mine, pl, tint=True)
        if im is not None:
            panels.append(im)
    cols, gap = 4, 16
    cw = max(i.width for i in panels)
    rows = [panels[k:k + cols] for k in range(0, len(panels), cols)]
    H = sum(max(i.height for i in r) for r in rows) + gap * (len(rows) + 1) + 30
    img = Image.new("RGB", (cols * cw + gap * (cols + 1), H), (28, 28, 32))
    from PIL import ImageDraw
    ImageDraw.Draw(img).text((gap, 8), "The whole world: one panel per planet (each planet is its own map; ships link them)",
                             font=O.F_BIG, fill=(255, 255, 255))
    y = 30 + gap
    for r in rows:
        x = gap
        for i in r:
            img.paste(i, (x, y))
            x += cw + gap
        y += max(i.height for i in r) + gap
    img.save(WORLD / "_world.png")
    print("wiki/world/_world.png", img.size)


def cmd_check(a):
    bad = 0
    for p in a.areas or _all():
        for q in Area(p).check():
            print(f"{p}: {q}")
            bad += 1
    sys.exit(1 if bad else 0)


def _assets():
    return {r["concept_id"]: r for r in csv.DictReader(open(V.ROOT / "wiki" / "mapping" / "world_art.csv"))}


def cmd_index(a):
    """wiki/world/INDEX.csv: every area and every placed piece, with the art status from world_art.csv."""
    art = _assets()
    out = WORLD / "INDEX.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["area", "planet", "kind", "replaces", "layout_status", "piece_kind", "piece", "size", "art",
                    "art_known", "art_status", "tool"])
        for p in _all():
            ar = Area(p)
            w.writerow([ar.id, ar.planet, ar.kind, ar.replaces, ar.status, "area", ar.name, f"{ar.w}x{ar.h}", "", "",
                        ar.raw.get("art_status", "pending-mockup"), "greybox room" if ar.kind == "interior" else "greybox terrain"])
            for pc in ar.pieces():
                aid = pc.get("art", "")
                known = "yes" if aid in art else ("" if not aid else "NEW")
                row = art.get(aid, {})
                st = "PLACEHOLDER" if pc["kind"] in ("person", "sign", "warp") else row.get("status", "pending-mockup")
                w.writerow([ar.id, ar.planet, ar.kind, ar.replaces, ar.status, pc["kind"], pc.get("name", ""),
                            "x".join(str(v) for v in pc.get("size", [1, 1])), aid, known, st, row.get("tool", "")])
    print(out)


STATUSES = ["pending-mockup", "pending-final-art", "art-complete", "imported-in-game"]


def cmd_todo(a):
    """What to draw next, from the wiki: areas (their yaml), assets (world_art.csv) and terrain items
    (terrain.csv), filtered by status, planet, kind or tool. --set ID STATUS writes a status back (an area id,
    an art id or a terrain id)."""
    if a.set:
        ident, status = a.set
        if status not in STATUSES:
            sys.exit(f"status must be one of {STATUSES}")
        if ident.startswith(("art:", "terrain:")):
            col = "concept_id" if ident.startswith("art:") else "terrain_id"
            path = V.ROOT / "wiki" / "mapping" / ("world_art.csv" if col == "concept_id" else "terrain.csv")
            rows = list(csv.DictReader(open(path)))
            hit = [r for r in rows if r[col] == ident]
            if not hit:
                sys.exit(f"{ident} is not in {path.name}")
            hit[0]["status"] = status
            with open(path, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        else:
            paths = [p for p in _all() if os.path.basename(p) == f"{ident}.yaml"]
            if not paths:
                sys.exit(f"{ident} is not an area")
            doc = yaml.safe_load(open(paths[0]))
            doc["art_status"] = status
            with open(paths[0], "w") as fh:
                yaml.dump(doc, fh, Dumper=_Dumper, sort_keys=False, width=160, allow_unicode=True, default_flow_style=None)
        print(f"{ident}: {status}")
        return
    rows = []
    for aid, r in _assets().items():
        rows.append({"id": aid, "kind": r["category"], "planet": r["planet"], "status": r["status"], "tool": r["tool"],
                     "build": r["build"], "used_in": r["used_in"], "notes": r["notes"] or r["description"][:90]})
    tpath = V.ROOT / "wiki" / "mapping" / "terrain.csv"
    if tpath.exists():                       # terrain items (tile-generator `terrain`): ground, water, ledges...
        for r in csv.DictReader(open(tpath)):
            rows.append({"id": r["terrain_id"], "kind": f"terrain:p{r['phase']}", "planet": r["planets"],
                         "status": r["status"], "tool": r["tool"], "build": "", "used_in": r["areas"],
                         "notes": r["notes"] or f"{r['metatiles']} metatiles, {r['areas']} areas"})
    for p in _all():
        d = yaml.safe_load(open(p))
        rows.append({"id": d["id"], "kind": "area:" + d["kind"], "planet": d["planet"],
                     "status": d.get("art_status", "pending-mockup"),
                     "tool": "greybox room" if d["kind"] == "interior" else "greybox terrain", "build": "",
                     "used_in": "", "notes": (d.get("notes") or "")[:90]})
    if a.status:
        rows = [r for r in rows if r["status"] == a.status]
    if a.planet:
        rows = [r for r in rows if a.planet.upper() in r["planet"].split(" | ")]
    if a.kind:
        rows = [r for r in rows if r["kind"] == a.kind or r["kind"].startswith(a.kind + ":")]
    if a.tool:
        rows = [r for r in rows if r["tool"].startswith(a.tool)]
    if a.csv:
        w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()) if rows else ["id"])
        w.writeheader()
        w.writerows(rows)
        return
    for r in rows:
        print(f"{r['status']:18} {r['kind']:14} {r['planet']:14} {r['id']:44} {r['tool']:16} {r['build']:14} {r['notes']}")
    print(f"{len(rows)} rows")


ORDER = ["TATOOINE", "KASHYYYK", "SULLUST", "MUSTAFAR", "ENDOR", "BESPIN", "JEDHA", "YAVIN 4", "HOTH", "DAGOBAH",
         "KAMINO", "ILUM", "GRAND ARENA", "FELUCIA", "TYTHON", "ATOLLON", "MORTIS", "ASTEROID FIELD", "DEATH STAR", "SHARED"]


def cmd_world_tiles(a):
    """wiki/world/<planet>/_planet_tiles.png (16 px per cell) and wiki/world/_world_tiles.png (8 px per cell):
    the overworld of every planet from the greybox tile renders, dungeons below each. Interiors are not on
    the map; see greybox/tiles/<area>.png."""
    from PIL import Image, ImageDraw
    from . import overview as O
    tiles = WORLD / "greybox" / "tiles"
    areas = [Area(p) for p in _all()]
    planets = [p for p in ORDER if p in {x.planet for x in areas}] + sorted({x.planet for x in areas} - set(ORDER))
    panels = []
    for pl in planets:
        mine = [x for x in areas if x.planet == pl and x.kind in ("town", "route", "landmark", "space", "dungeon")]
        outdoor = [x for x in mine if x.kind != "dungeon"]
        if outdoor and all(x.pos is None for x in outdoor):   # door-linked islands: side by side
            cx = 0
            for x in outdoor:
                x.pos, cx = [cx, 0], cx + x.w + 2
        img = O.stitch_tiles(mine, f"{pl}: greybox terrain", tiles)
        if img is None:
            continue
        path = WORLD / pl.lower().replace(" ", "-") / "_planet_tiles.png"
        img.save(path)
        print(os.path.relpath(path, V.ROOT), img.size)
        panels.append(img.resize((img.width // 2, img.height // 2), Image.LANCZOS))
    gap = 16
    W = max(i.width for i in panels) + 2 * gap
    H = sum(i.height for i in panels) + gap * (len(panels) + 1) + 30
    img = Image.new("RGB", (W, H), (28, 28, 32))
    ImageDraw.Draw(img).text((gap, 8), "The whole world in greybox terrain, half size (8 px per cell); one planet after another in story order",
                             font=O.F_BIG, fill=(255, 255, 255))
    y = 30 + gap
    for i in panels:
        img.paste(i, (gap, y))
        y += i.height + gap
    img.save(WORLD / "_world_tiles.png", optimize=True)
    print("wiki/world/_world_tiles.png", img.size)


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
    # the connection graph: one row per exit, door and warp, plus StarNAV flights between ship rooms
    edges = []
    for x in areas:
        for e in x.exits:
            edges.append((x, e.get("to"), f"exit {e['edge']}", ""))
        for b in x.buildings:
            if b.get("to"):
                edges.append((x, b["to"], "door", b.get("name", "")))
        for w in x.warps:
            if w.get("to"):
                edges.append((x, w["to"], "warp", w.get("name", "")))
        for t in x.travel:
            edges.append((x, t["to"], t.get("via", "travel"), t.get("name", "")))
    from . import catalog as K
    area_of = {n: m["area"] for n, m in K.maps().items()}
    for a_, b_, via in V.vanilla_links():
        fa, tb = area_of.get(a_), area_of.get(b_)
        if fa in by_id and tb in by_id:
            edges.append((by_id[fa], tb, f"vanilla {via}", ""))
    ship_rooms = sorted({x.id for x, t, _, _ in edges if t == "starnav"} |
                        {x.id for x in areas if x.kind == "interior" and "hangar" in x.id})
    links = {(x.id, t) for x, t, _, _ in edges}
    with open(WORLD / "CONNECTIONS.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["from", "from_planet", "from_kind", "to", "to_planet", "to_kind", "via", "name", "two_way", "crosses_planet"])
        for x, t, via, name in edges:
            y = by_id.get(t)
            w.writerow([x.id, x.planet, x.kind, t, y.planet if y else "", y.kind if y else "", via, name,
                        "yes" if (t, x.id) in links else "no",
                        "yes" if y and y.planet != x.planet and "SHARED" not in (x.planet, y.planet) else ""])
        for r in [r for r in ship_rooms if not any(e[0].id == r and e[1] == "starnav" for e in edges)]:
            w.writerow([r, by_id[r].planet, by_id[r].kind, "starnav", "", "", "StarNAV flight", "ship to any unlocked planet", "yes", "yes"])
    # what the player can reach on foot, by door and by ship, starting at Mos Pelgo
    adj = {}
    for x, t, _, _ in edges:
        adj.setdefault(x.id, set()).add(t)
        adj.setdefault(t, set())
    for r in ship_rooms:
        adj.setdefault(r, set()).add("starnav")
        adj.setdefault("starnav", set()).add(r)
    seen, todo = {"mos-pelgo"}, ["mos-pelgo"]
    while todo:
        for n in adj.get(todo.pop(), ()):
            if n not in seen:
                seen.add(n)
                todo.append(n)
    lost = sorted(x.id for x in areas if x.id not in seen)
    one_way = sum(1 for x, t, _, _ in edges if (t, x.id) not in links)
    L[4:4] = [f"Connections: [CONNECTIONS.csv](CONNECTIONS.csv) has {len(edges)} links (exits, doors, warps) plus a StarNAV flight "
              f"row for each of the {len(ship_rooms)} ship rooms; {one_way} links have no way straight back (ledges, holes, "
              f"one-way warps, or a back door still missing). From Mos Pelgo, {len(seen & set(by_id))} of {len(areas)} areas can be reached."
              + (f" Not reachable yet: {', '.join(lost)}." if lost else ""), ""]
    L += progression_section(areas, by_id, planets)
    out = WORLD / "GUIDE.md"
    out.write_text("\n".join(L) + "\n")
    print(out)


def _slug(camel: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", camel.replace("_", "-")).lower()


def progression_section(areas, by_id, planets):
    """Balance check (owner, 2026-11-02): every planet's badge and level band from Emerald's own table
    (`wiki/database/area_progression.csv`, unchanged by the hotswap), and every net-new area checked against
    it: it must name a gate (a flag or item in `net_new.csv` `depends_on`, matched by the `net:` id in its
    yaml) and a level band inside its planet's band. Anything missing is listed here as a problem."""
    prog = {r["map_id"]: r for r in csv.DictReader(open(V.ROOT / "wiki" / "database" / "area_progression.csv"))}
    net = {r["id"]: r for r in csv.DictReader(open(V.ROOT / "wiki" / "database" / "net_new.csv"))}
    L = ["", "## Progression and balance", "",
         "Emerald's progression table is kept as is (badges, wild and trainer levels per map; `wiki/database/area_progression.csv`). "
         "Each planet's band below is read from the vanilla maps its areas replace. A net-new area must name its gate "
         "(`depends_on` in `net_new.csv`, found through the `net:` id in the area's `todo`) and a level band inside the "
         "planet's band (`levels N-M` in its `story`). Problems are listed; an empty list means the new content fits.", "",
         "| Planet | Badges | Trainer levels | Wild levels | Gates seen |", "|---|---|---|---|---|"]
    band = {}
    for pl in planets:
        mine = [x for x in areas if x.planet == pl]
        if not mine:
            continue
        rows = [prog["map:" + _slug(x.replaces)] for x in mine if x.replaces != "new" and "map:" + _slug(x.replaces) in prog]
        def rng(key_lo, key_hi):
            lo = [int(r[key_lo]) for r in rows if r[key_lo]]
            hi = [int(r[key_hi]) for r in rows if r[key_hi]]
            return (min(lo), max(hi)) if lo and hi else None
        badges = sorted({int(r["badges_expected"]) for r in rows if r["badges_expected"]})
        tl, wl = rng("trainer_level_min", "trainer_level_max"), rng("wild_any_min", "wild_any_max")
        gates = sorted({g for r in rows for g in r["requires"].split("|") if g})
        band[pl] = (badges, tl, wl)
        L.append(f"| {pl} | {badges[0]}-{badges[-1] if badges else ''} | {tl[0]}-{tl[1]} | {wl[0]}-{wl[1]} | {', '.join(gates[:4])}{' ...' if len(gates) > 4 else ''} |"
                 if badges and tl and wl else f"| {pl} | {'-'.join(map(str, badges[:1] + badges[-1:])) or '?'} | {tl or '?'} | {wl or '?'} | {', '.join(gates[:4])} |")
    L += ["", "### Net-new areas", "", "| Area | Planet | Gate | Levels | Check |", "|---|---|---|---|---|"]
    problems = 0
    for x in sorted(areas, key=lambda a: (a.planet, a.id)):
        if x.replaces != "new":
            continue
        text = " ".join(str(t) for t in x.todo) + " " + (x.raw.get("story") or "") + " " + (x.raw.get("notes") or "")
        ids = re.findall(r"net:[a-z0-9-]+", text)
        gate = "; ".join(sorted({net[i]["depends_on"] for i in ids if i in net and net[i]["depends_on"]}))
        m = re.search(r"levels?\s+(\d+)\s*-\s*(\d+)", text)
        lv = (int(m.group(1)), int(m.group(2))) if m else None
        b = band.get(x.planet)
        issues = []
        if x.kind != "interior" or x.people:
            if not gate and not any(i in net for i in ids):
                issues.append("no gate: name its net: id and a depends_on flag")
            if lv is None and x.kind in ("dungeon", "route", "landmark", "town") and any(p.get("role") == "trainer" for p in x.people):
                issues.append("trainers but no level band in story")
            if lv and b and b[1] and not (b[1][0] - 5 <= lv[0] and lv[1] <= max(b[1][1] + 5, 70 if "sys-game-clear" in gate else 0)):
                issues.append(f"levels {lv[0]}-{lv[1]} outside the planet band {b[1][0]}-{b[1][1]}")
        if issues:
            problems += 1
        L.append(f"| [{x.name}]({os.path.relpath(x.path, WORLD)}) | {x.planet} | {gate or ids[0] if ids else gate} | "
                 f"{f'{lv[0]}-{lv[1]}' if lv else ''} | {'; '.join(issues) if issues else 'ok'} |")
    L += ["", f"{problems} net-new areas with a balance problem."]
    return L


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
    td = sub.add_parser("todo", help="what to draw next, from the wiki")
    td.add_argument("--status", choices=STATUSES)
    td.add_argument("--planet")
    td.add_argument("--kind", help="area, area:town, building, object, interior, nature, landmark")
    td.add_argument("--tool")
    td.add_argument("--csv", action="store_true")
    td.add_argument("--set", nargs=2, metavar=("ID", "STATUS"))
    sub.add_parser("world")
    sub.add_parser("world-tiles")
    sub.add_parser("guide")
    lo = sub.add_parser("layout")
    lo.add_argument("planets", nargs="+")
    lo.add_argument("--root")
    ia = sub.add_parser("import-all")
    ia.add_argument("--force", action="store_true")
    ia.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    {"new": cmd_new, "world": cmd_world, "layout": cmd_layout, "import-all": cmd_import_all, "render": cmd_render, "check": cmd_check, "index": cmd_index, "todo": cmd_todo, "guide": cmd_guide, "world-tiles": cmd_world_tiles}[a.cmd](a)

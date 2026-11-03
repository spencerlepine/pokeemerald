"""Step 11: large static scenery. Places every piece of scenery_spec.py in its areas and writes the
 `scenery` rows of wiki/mapping/world_art.csv. Dry run unless --write.

A piece only ever sits on cells that are already blocked (rock, trees, cliff) or on water, so no path changes.
Zones: n/e/s/w touch that map edge (border barriers and backdrops, partly off the map); edge is any blocked
run next to open ground; water is all water; shore mixes water and bank. The drawn rows above a hit box must
not hide a door, sign, person, warp, building or another piece; a water piece must never cut a surf route.
Re-running replaces earlier scenery placements (props whose art is a `scenery` row).

    python3 drafts/scenery.py            # dry run: where each piece would go
    python3 drafts/scenery.py --write    # write the yamls and the rows, then run `index` and `check`
"""
import csv, sys, glob, os, yaml
from collections import deque
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT + "/tools/blockout")
sys.path.insert(0, os.path.dirname(__file__))
from blockout.cli import _Dumper
from blockout.area import Area
from blockout.terrain import walkable
from scenery_spec import P

LAND = set("T#")
paths = {os.path.basename(p)[:-5]: p for p in glob.glob(ROOT + "/wiki/world/*/*.yaml")}

def comps(cells):
    lab, n = {}, 0
    for c in cells:
        if c in lab: continue
        n += 1; q = deque([c]); lab[c] = n
        while q:
            x, y = q.popleft()
            for d in ((1,0),(-1,0),(0,1),(0,-1)):
                m = (x+d[0], y+d[1])
                if m in cells and m not in lab:
                    lab[m] = n; q.append(m)
    return lab, n

def place_area(aid, reqs, log):
    ar = Area(paths[aid])
    ar.props = [p for p in ar.props if p.get("art") not in IDS]     # earlier scenery placements are redone
    doc = ar.raw
    solid = set(ar.solid_cells())
    mark = set()
    for k in ("people", "signs", "warps"):
        for o in doc.get(k) or []:
            mark.add(tuple(o["at"]))
    exitc = set()
    for e in ar.exits:
        for c in e["cells"]:
            exitc.add({"north": (c, 0), "south": (c, ar.h-1), "west": (0, c), "east": (ar.w-1, c)}[e["edge"]])
    bcells = set()
    for b in ar.buildings:
        (x, y), (w, h) = b["at"], b["size"]
        bcells |= {(xx, yy) for xx in range(x, x+w) for yy in range(y, y+h)}
        if "door" in b: mark.add((x + int(b["door"]), y + h))
    def open_(x, y):
        ch = ar.cell(x, y)
        return ch is not None and (x, y) not in solid and (walkable(ch) or ch == "~")
    placed_new = []
    out = []
    for piece, zones, count, shown, nm in reqs:
        w, d = piece["fp"]; rise = piece["rise"]
        for i in range(count):
            best = None
            tiers = [(z, st) for st in (True, False) for z in zones]
            tiers += [(z, "mixed") for z in zones + ([] if "edge" in zones else ["edge"])]
            tiers += [(z, "open") for z in zones + ([] if "edge" in zones else ["edge"]) if z != "water"]
            for zone, strict in tiers:
                cands = []
                for y in range(0, ar.h - d + 1):
                    for x in range(0, ar.w - w + 1):
                        cells = [(xx, yy) for yy in range(y, y+d) for xx in range(x, x+w)]
                        chs = [ar.cell(*c) for c in cells]
                        if any(c in solid or c in mark or c in exitc for c in cells): continue
                        nw = sum(ch == "~" for ch in chs); nl = sum(ch in LAND for ch in chs)
                        no = sum(ch == "." for ch in chs) if strict == "open" else 0
                        if nw + nl + no != len(cells): continue
                        if no and (nw or any((ar.cell(*q) or "") in list(":=H<>^v") for q in
                                             ((xx + dx, yy + dy) for (xx, yy) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                                             if q not in cells)):
                            continue                  # open ground only away from roads, stairs and ledges
                        if zone == "water" and nl: continue
                        if zone == "shore" and not nw: continue
                        if zone in ("n", "s", "e", "w", "edge") and nw: continue
                        if zone == "n" and y != 0: continue
                        if zone == "s" and y + d != ar.h: continue
                        if zone == "w" and x != 0: continue
                        if zone == "e" and x + w != ar.w: continue
                        # the drawn rows above the hit box must not hide a door, sign, person, building or another piece
                        risec = [(xx, yy) for yy in range(y - rise, y) for xx in range(x, x+w) if yy >= 0]
                        if any(c in mark or c in bcells or c in solid for c in risec): continue
                        ring = {(xx, yy) for yy in range(y-1, y+d+1) for xx in range(x-1, x+w+1)} - set(cells)
                        ring_open = sum(open_(*c) for c in ring)
                        front = sum(open_(xx, y+d) for xx in range(x, x+w))
                        land_open = sum(1 for c in ring if open_(*c) and ar.cell(*c) != "~")
                        # clean edges: a land piece stands on one kind of blocked ground (all rock or all trees, never across
                        # a cliff line) and its drawn rows never hang over water; a water piece keeps clear of the banks
                        if zone != "shore" and nl and len(set(chs)) > 1 and strict not in ("mixed", "open"): continue
                        if nl and any(ar.cell(*c) == "~" for c in risec): continue
                        if zone == "water":
                            wr = [ar.cell(*c) == "~" for c in ring if ar.cell(*c) is not None]
                            if strict and not all(wr): continue
                            if not strict and sum(wr) < 0.75 * len(wr): continue
                        elif strict is False:
                            continue
                        if strict == "mixed" and zone == "water": continue
                        if ring_open < 2: continue
                        if zone == "edge" and land_open < 2: continue     # seen from where the player walks, not only from the water
                        if zone == "shore" and not (nl or land_open): continue
                        if zone == "shore" and not land_open and nl == 0: continue
                        border = min(x, y, ar.w - (x+w), ar.h - (y+d))
                        crowd = 0
                        near = False
                        for (px, py, pw, pd) in placed_new:
                            gap = max(px - (x+w), x - (px+pw), py - (y+d), y - (py+pd))
                            near = near or gap < 2
                            if gap < 8: crowd += (8 - gap) * 3
                        if near: continue
                        score = min(ring_open, 10) + 2 * front - 0.4 * border - crowd
                        if zone == "shore": score += 2 * min(land_open, 4)
                        if zone in ("n", "s", "e", "w"): score += 2 * front
                        cands.append((score, -y, -x, x, y, cells, zone))
                cands.sort(reverse=True)
                for c in cands:
                    sc, _, _, x, y, cells, zone = c
                    if any(ar.cell(*q) in ("~", ".") for q in cells):     # a piece on water or open ground must not cut a route
                        free = {(xx, yy) for yy in range(ar.h) for xx in range(ar.w) if open_(xx, yy)}
                        lab, _ = comps(free); lab2, _ = comps(free - set(cells))
                        groups = {}
                        for q, l in lab2.items(): groups.setdefault(lab[q], set()).add(l)
                        if any(len(v) > 1 for v in groups.values()) or len(groups) < len(set(lab.values())):
                            continue
                    best = (sc, x, y, cells, zone if strict is True else f"{zone} ({strict or 'loose'})"); break
                if best: break
            if not best:
                log.append(f"FAIL {aid}: {piece['id']} {w}x{d} zones {zones}"); continue
            _, x, y, cells, zone = best
            zone = zone.split(" (")[0]
            solid |= set(cells)
            placed_new.append((x, y, w, d))
            fac = piece["facings"].split()
            facing = fac[0] if len(fac) == 1 else ("e" if x + w / 2 < ar.w / 2 else "w")
            if "e" not in fac: facing = fac[0]
            pr = {"name": nm or piece["name"], "art": piece["id"], "at": [x, y], "size": [w, d], "facing": facing}
            if shown != "always": pr["shown"] = shown
            kinds = {ar.cell(*c) for c in cells}
            if "." in kinds:
                pr["fit"] = "no blocked spot this big here: it takes open ground at the edge; adjust the terrain when placing for real"
            elif len(kinds) > 1 and "~" not in kinds:
                pr["fit"] = "stands across rock and trees: even out the terrain under it when placing for real"
            out.append(pr)
            log.append(f"ok   {aid}: {piece['id']} at {x},{y} zone {zone} facing {facing}")
    return doc, out

IDS = {p["id"] for p in P}


def main(write):
    by = {}
    for piece in P:
        for (aid, zones, count, shown, nm) in piece["place"]:
            by.setdefault(aid, []).append((piece, zones, count, shown, nm))
    log = []
    for aid, reqs in by.items():
        # big pieces first so they get the room they need
        reqs.sort(key=lambda r: -r[0]["fp"][0] * r[0]["fp"][1])
        doc, out = place_area(aid, reqs, log)
        if write and out:
            doc.setdefault("props", [])
            doc["props"] = [p for p in doc["props"] if p.get("art") not in IDS]
            doc["props"] += out
            with open(paths[aid], "w") as fh:
                yaml.dump(doc, fh, Dumper=_Dumper, sort_keys=False, width=160, allow_unicode=True, default_flow_style=None)
    if write:
        for aid, path in paths.items():      # areas no longer in the plan lose their old scenery
            if aid in by:
                continue
            doc = yaml.safe_load(open(path))
            kept = [p for p in doc.get("props") or [] if p.get("art") not in IDS]
            if len(kept) != len(doc.get("props") or []):
                doc["props"] = kept
                with open(path, "w") as fh:
                    yaml.dump(doc, fh, Dumper=_Dumper, sort_keys=False, width=160, allow_unicode=True, default_flow_style=None)
        write_rows()
    print("\n".join(log))
    print(sum(l.startswith("ok") for l in log), "placed,", sum(l.startswith("FAIL") for l in log), "failed")




def write_rows():
    path = ROOT + "/wiki/mapping/world_art.csv"
    rows = list(csv.DictReader(open(path)))
    fields = list(rows[0].keys())
    NEW = ["drawn", "facings", "metatiles", "tiles", "shown"]
    for c in NEW:
        if c not in fields: fields.append(c)
    # reference images already in the wiki, by starwars-db id
    refimg = {}
    for r in rows:
        for ref in (r["sw_refs"] or "").split("|"):
            if ref and r["reference_art"]:
                db = [p for p in r["reference_art"].split("|") if "__db_" in p]
                if db: refimg.setdefault(ref, db[0])
    known = set(refimg)
    old = {r["concept_id"]: r for r in rows if r["category"] == "scenery"}
    rows = [r for r in rows if r["category"] != "scenery"]
    for r in rows:
        for c in NEW: r.setdefault(c, "")
    for p in P:
        w, d = p["fp"]; h = d + p["rise"]
        f = p["facings"].split()
        drawings = (1 if ("e" in f or "w" in f) else 0) + ("n" in f) + ("s" in f)
        shown = sorted({pl[3] for pl in p["place"]})
        states = 2 if any(":" in s for s in shown) else 1
        mt = w * h * drawings * states * p.get("variants", 1)
        ref = p["refs"] if p["refs"] in known else ""
        planet = p["id"].split(":")[1].upper().replace("-", " ")
        if planet == "SHARED": planet = "SHARED"
        stand = p["build"]
        rows.append({**{k: "" for k in fields},
            "concept_id": p["id"], "planet": planet,
            "place": "every planet" if planet == "SHARED" else " ".join(pl[0] for pl in p["place"]),
            "category": "scenery", "name": p["name"], "footprint": f"{w}x{d}", "map_role": p["role"],
            "build": stand, "tool": "greybox piece", "status": "pending-mockup",
            "description": p["lore"], "vanilla_template": "none (new)", "sw_refs": ref,
            "reference_art": refimg.get(ref, ""),
            "notes": f"Greybox uses the {stand} model as a stand-in; needs its own shape. Drawn {w}x{h} cells "
                     f"({w*16}x{h*16} px): the top {p['rise']} row(s) overlap the cells behind it (walk-behind)."
                     + (" Partly off the map on purpose." if p["role"] == "backdrop" else ""),
            "drawn": f"{w}x{h}", "facings": " ".join(f), "metatiles": str(mt), "tiles": str(mt * 4),
            "shown": "; ".join(shown),
            **{k: old[p["id"]][k] for k in ("used_in", "areas", "greybox") if p["id"] in old}})
    with open(path, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields); wr.writeheader(); wr.writerows(rows)
    print(len(P), "scenery rows;", sum(1 for p in P if p["refs"] in known), "with a reference image")


if __name__ == "__main__":
    main("--write" in sys.argv)

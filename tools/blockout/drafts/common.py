import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from blockout.draft import Draft, place_near, auto_buildings, clean_people, cut_borders, open_exit, link_all
from blockout import catalog as K
CAT = K.maps()
PLANET = {m["area"]: m["planet"] for m in CAT.values()}
BY_AREA = {m["area"]: n for n, m in CAT.items()}
from blockout import vanilla as V, cli as C
POS, CONST = V.world_positions()

def reimport(area_id):
    C.import_map(BY_AREA[area_id], CAT, POS, CONST, force=True)

def retheme(area_id, story, props=(), people=(), todo=(), art_house=None, rename_exits=None, name=None, extra=None):
    reimport(area_id)
    d = Draft.load(area_id)
    d.doc["status"] = "BLOCKOUT"
    d.doc["story"] = story
    if name: d.doc["name"] = name
    if art_house: auto_buildings(d, art_house)
    clean_people(d)
    for e in d.doc["exits"]:
        if rename_exits and e.get("to") in rename_exits: e["to"] = rename_exits[e["to"]]
    cut = cut_borders(d, PLANET)
    d.doc["signs"] = [x for x in d.doc["signs"] if 0 <= x["at"][0] < d.w and 0 <= x["at"][1] < d.h]
    d.doc["warps"] = [x for x in d.doc["warps"] if 0 <= x["at"][0] < d.w and 0 <= x["at"][1] < d.h]
    for wp in list(d.doc["warps"]):
        if wp.get("to") in PLANET and PLANET[wp["to"]] != d.doc["planet"]:
            d.doc["warps"].remove(wp)
            cut.append(f"door at {wp['at']} to {wp['to']}")
    d.doc["todo"] = [t for t in d.doc.get("todo", []) if not t.startswith("Imported from vanilla")]
    if any(ch == "#" for row in d.g for ch in row):
        d.doc["todo"].append("'#' cells are cliffs and rock walls kept from vanilla.")
    for c in cut:
        d.doc["todo"].append(f"Planet border cut: {c}; reached by ship instead.")
    if extra: extra(d)
    missed = []
    for p in props:
        name_, art, w, h, near = p
        if not place_near(d, name_, art, w, h, near):
            missed.append(name_)
    for n, x, y, role in people:
        d.person(n, x, y, role)
    d.doc["todo"] += list(todo)
    if missed:
        d.doc["todo"].append("Could not fit: " + ", ".join(missed))
    unblock(d)
    d.save()
    return d

def drop_exit(d, to):
    for e in list(d.doc["exits"]):
        if e.get("to") == to:
            for c in e["cells"]:
                x, y = {"north": (c, 0), "south": (c, d.h - 1), "west": (0, c), "east": (d.w - 1, c)}[e["edge"]]
                if d.get(x, y) != "~":
                    d.set(x, y, "T")
            d.doc["exits"].remove(e)

def unblock(d):
    """Move people standing on blocked cells (walls, buildings, props) to the nearest open cell."""
    solid = set()
    for k in ("buildings", "props"):
        for o in d.doc[k]:
            (x, y), (w, h) = o["at"], o.get("size", [1, 1])
            solid |= {(x + i, y + j) for i in range(w) for j in range(h)}
    used = {tuple(p["at"]) for p in d.doc["people"]}
    ok = lambda x, y: d.get(x, y) in (".", ":", '"', "=", "_") and (x, y) not in solid and (x, y) not in used
    for p in d.doc["people"]:
        if p.get("role") in ("berry", "item", "object"):
            continue
        x, y = p["at"]
        if d.get(x, y) in (".", ":", '"', "=", "_", "~") and (x, y) not in solid:
            continue
        for r in range(1, 8):
            hit = next(((x + i, y + j) for j in range(-r, r + 1) for i in range(-r, r + 1)
                        if max(abs(i), abs(j)) == r and ok(x + i, y + j)), None)
            if hit:
                used.discard((x, y)); used.add(hit); p["at"] = list(hit)
                break

"""Buildings and props as solid map cells, drawn with their render from the wiki.

Every building (`buildings:`) and every sized prop (`props:`) of an area covers its cells with its own
metatiles: the building-kit render (`mapping/buildings.csv` png), else the greybox render (`world_art.csv`
`greybox`, then `model_png`), else the piece's pink placeholder. Each cell is solid (collision 1); a building's
door cell (bottom row, `door` column) is walkable and warps (MB_NON_ANIMATED_DOOR). In a vanilla or hybrid
map only the pieces set on ground vanilla has open are drawn; the vanilla buildings keep their own tiles.

The render is fitted to the piece's cells: scaled down if it is bigger, centred and standing on the bottom row
if smaller. `facing: w` mirrors the east-facing render. A redrawn or new map's signs are holo-sign posts. A prop `shown` only after a story flag is always drawn
for now (listed in the port report).
"""
from pathlib import Path

from . import base as B
from .model import read_csv

_B = None
_A = None
PLACEHOLDER = B.TOOLS / "tile-generator" / "tilegen" / "data" / "placeholder-16x16.png"


def _tables():
    global _B, _A
    if _B is None:
        _B = read_csv(B.MAPPING / "buildings.csv")
        _A = {r["concept_id"]: r for r in read_csv(B.MAPPING / "world_art.csv")}
    return _B, _A


def building_png(area, b):
    rows, _ = _tables()
    for r in rows:
        if area.id in r["areas"].split() and r["name"] == b["name"] and r["png"]:
            p = B.WIKI / r["png"]
            if p.exists():
                return p, r["id"]
    return art_png(b.get("art"))


def art_png(art):
    _, A = _tables()
    r = A.get(art or "")
    if r:
        for k in ("greybox", "model_png", "placeholder"):
            if r.get(k):
                p = B.WIKI / r[k]
                if p.exists():
                    return p, art
    return None, art


def pieces_of(area):
    """(kind, name, key, png, x, y, w, h, door_x or None, mirror, note) for every building and prop."""
    out = []
    for b in area.buildings:
        (x, y), (w, h) = b["at"], b["size"]
        png, key = building_png(area, b)
        door = x + int(b["door"]) if "door" in b else None
        out.append(dict(kind="building", name=b["name"], key=key or b.get("art") or b["name"], png=png, x=x, y=y,
                        w=w, h=h, door=door, mirror=False, shown=None))
    if area.mode == "redraw":
        # a redrawn map has no vanilla sign tiles: each sign is a holo-sign post (solid, read from below)
        for sg in area.signs:
            png, key = art_png("art:shared:holo-sign")
            out.append(dict(kind="sign", name=sg.get("name", "Sign"), key=key or "sign", png=png, x=sg["at"][0],
                            y=sg["at"][1], w=1, h=1, door=None, mirror=False, shown=None))
    for p in area.props:
        (x, y), (w, h) = p["at"], p.get("size", [1, 1])
        png, key = art_png(p.get("art"))
        out.append(dict(kind="prop", name=p["name"], key=key or p["name"], png=png, x=x, y=y, w=w, h=h, door=None,
                        mirror=p.get("facing") == "w", shown=p.get("shown")))
    return out


def add_pieces(C):
    """Overlay every piece of the area onto its Cells (symbols ("piece", ...)); returns the pieces."""
    area = C.area
    ps = pieces_of(area)
    if area.mode in ("vanilla", "hybrid"):
        # a vanilla map already draws its own buildings: a piece over cells vanilla has solid is one of them; only
        # a piece set on open vanilla ground is new (a hangar on a route)
        def is_new(p):
            under = [int(C.coll[yy, xx]) for yy in range(p["y"], p["y"] + p["h"]) for xx in range(p["x"], p["x"] + p["w"])
                     if 0 <= yy < area.h and 0 <= xx < area.w]
            return bool(under) and sum(c == 0 for c in under) > len(under) / 2
        ps = [p for p in ps if is_new(p)]
    for i, p in enumerate(ps):
        for yy in range(p["y"], p["y"] + p["h"]):
            for xx in range(p["x"], p["x"] + p["w"]):
                if not (0 <= xx < area.w and 0 <= yy < area.h):
                    continue
                under = int(C.meta[yy, xx])
                under = under if under >= 0 else C.symbol(under)
                is_door = p["door"] == xx and yy == p["y"] + p["h"] - 1
                png = str(p["png"]) if p["png"] else str(PLACEHOLDER)
                C.meta[yy, xx] = C.sym(("piece", png, p["w"], p["h"], p["mirror"], xx - p["x"], yy - p["y"], under, is_door))
                if is_door:
                    C.coll[yy, xx], C.elev[yy, xx] = 0, 3
                else:
                    C.coll[yy, xx], C.elev[yy, xx] = 1, 0
    return ps


def align_doors(areas):
    """Line up each building that replaces a vanilla one with the vanilla door (vanilla and hybrid maps).

    Map scripts open, close and walk people through a vanilla door by its cell. When the wiki redraws such a
    building a cell or two off, the building moves so its door sits on the vanilla door cell. Returns notes.
    """
    notes = []
    for a in areas.values():
        if a.mode not in ("vanilla", "hybrid"):
            continue
        vw = B.base_map(a.replaces).get("warp_events") or []
        for b in a.buildings:
            if "door" not in b or b.get("to") not in areas:
                continue
            dx, dy = b["at"][0] + int(b["door"]), b["at"][1] + b["size"][1] - 1
            const = areas[b["to"]].map_const
            near = sorted((abs(w["x"] - dx) + abs(w["y"] - dy), w["x"], w["y"]) for w in vw if w["dest_map"] == const)
            if near and 0 < near[0][0] <= 3:
                _, vx, vy = near[0]
                b["at"] = [b["at"][0] + vx - dx, b["at"][1] + vy - dy]
                notes.append(f"{a.id}: {b['name']} moved by ({vx - dx},{vy - dy}) so its door is vanilla's ({vx},{vy})")
    return notes

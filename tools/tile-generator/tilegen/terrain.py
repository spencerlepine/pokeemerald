"""Greybox terrain: every ground, water, ledge and cliff tile of every area, itemized in the wiki, tile by tile.

Phase 1 of the world art (owner, 2026-11-02): terrain only, in greybox. The game already has most of the
terrain shapes (grass, paths, shores, ledges, cliffs, caves, floors); this repaints them, keeps them, and lists
the ones it does not have.

  - **Vocabulary.** Every terrain item is a fixed set of named roles (`roles.py`): water, cliffs, walls and
    paths are blob sets (fill, 4 edges, 4 outer corners, 4 inner corners, strips, tips, single; walls add
    `top`), ledges have fill and end caps, bridges h / v, everything else is `fill`.
  - **Catalog.** Every vanilla layout an area replaces is read cell by cell. Each cell is classed the way
    blockout classes it (`.` ground, `"` wild grass, `~` water, `v ^ < >` ledges, `=` bridge, `#` blocked,
    `T` tree), named as an item of its tileset (`ground-path`, `water-pond`, `cliff`, `wall`, `floor`...) and
    given its role from its neighbours. The metatile is filed under `terrain:<tileset>:<item>:<role>`. Trees
    and structures are phase 2 and only listed. Written to `wiki/mapping/terrain.csv`.
  - **Autotile.** An area whose grid was redesigned (or is new) is drawn from the same vocabulary: each grid
    cell gets an item (the pair's usual ground, path, water, wild grass; wall or cliff for blocked cells) and
    its role, then the metatile vanilla uses for that item and role in that tileset pair. A role vanilla never
    drew in that pair has no tile: the cell shows the placeholder (the z-day 16x16 circle) and the row is added
    to the catalog as TODO (`pending-mockup`) with the areas that need it. A hand-set `use` metatile id in the
    csv row wins over the learned one, so a tile can be reassigned without code.
  - **Sheets.** Per tileset, a real-size sheet (128 px wide, 16x16 cells, one per catalog row, placeholder
    where the tile is missing) in `wiki/world/greybox/sheets/`, and a labelled sheet in
    `wiki/world/greybox/terrain/`. The csv row says which sheet cell it is.
  - **Greybox.** A planet's tilesets are recoloured with its approved planet recipe (if it has one) and then
    desaturated to grey (`GREY_CHROMA`), so shading, materials and shapes stay and colour waits. Area renders
    go to `wiki/world/greybox/tiles/<area>.png`.

`python -m tilegen terrain run|catalog|sheets|render [--area ID ...] [--planet P]|mark --status S|build --planet P`.
"""
from __future__ import annotations

import csv
import glob
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import gba, colour, roles as R

ROOT = Path(__file__).resolve().parents[3]
WIKI = ROOT / "wiki"
WORLD = WIKI / "world"
CSV_OUT = WIKI / "mapping" / "terrain.csv"
AREAS_OUT = WIKI / "mapping" / "terrain_areas.csv"
TILES_OUT = WORLD / "greybox" / "tiles"
SHEETS_OUT = WORLD / "greybox" / "terrain"
REAL_OUT = WORLD / "greybox" / "sheets"
PLACEHOLDER = Path(__file__).resolve().parent / "data" / "placeholder-16x16.png"   # from z-day/.dev/assets
MISSING = 0xFFFF            # cell value for a role with no tile
SHEET_COLS = 8               # 128 px wide, like tiles.png
RECIPES = Path(__file__).resolve().parents[1] / "recipes"

GREY_CHROMA = 0.22          # how much of the planet colour a greybox keeps
PLANET_RECIPE = {"TATOOINE": "tatooine", "HOTH": "hoth", "ILUM": "hoth", "SULLUST": "sullust",
                 "MUSTAFAR": "sullust-lava", "ENDOR": "endor", "YAVIN 4": "endor", "KASHYYYK": "endor",
                 "DAGOBAH": "dagobah", "KAMINO": "kamino", "DEATH STAR": "death-star"}
PHASE2 = {"tree", "structure"}
# the pair a redesigned area is autotiled with, when its planet has no vanilla layout of that kind to borrow
# from, or the layout it replaces has the wrong pair for the new design (NiJedha replaces Mt. Pyre's exterior:
# a town needs a town tileset, the stone city of Rustboro)
PAIR_OVERRIDE = {("DEATH STAR", "dungeon"): ("gTileset_General", "gTileset_Facility"),
                 ("JEDHA", "town"): ("gTileset_General", "gTileset_Rustboro")}

WATER = {"MB_POND_WATER", "MB_DEEP_WATER", "MB_OCEAN_WATER", "MB_SOOTOPOLIS_DEEP_WATER", "MB_WATERFALL",
         "MB_INTERIOR_DEEP_WATER", "MB_NO_SURFACING", "MB_EASTWARD_CURRENT", "MB_WESTWARD_CURRENT",
         "MB_NORTHWARD_CURRENT", "MB_SOUTHWARD_CURRENT"}
WILD = {"MB_TALL_GRASS", "MB_LONG_GRASS", "MB_ASHGRASS", "MB_DEEP_SAND"}
LEDGE = {"MB_JUMP_SOUTH": "v", "MB_JUMP_NORTH": "^", "MB_JUMP_WEST": "<", "MB_JUMP_EAST": ">"}
LEDGE_NAME = {"v": "ledge-south", "^": "ledge-north", "<": "ledge-west", ">": "ledge-east"}
BRIDGE = {"MB_FORTREE_BRIDGE", "MB_PACIFIDLOG_VERTICAL_LOG_TOP", "MB_PACIFIDLOG_VERTICAL_LOG_BOTTOM",
          "MB_PACIFIDLOG_HORIZONTAL_LOG_LEFT", "MB_PACIFIDLOG_HORIZONTAL_LOG_RIGHT", "MB_BRIDGE_OVER_POND_LOW",
          "MB_BRIDGE_OVER_OCEAN", "MB_BRIDGE_OVER_POND_MED", "MB_BRIDGE_OVER_POND_HIGH"}
WATER_KIND = {"MB_POND_WATER": "pond", "MB_DEEP_WATER": "deep", "MB_OCEAN_WATER": "ocean",
              "MB_SOOTOPOLIS_DEEP_WATER": "deep", "MB_WATERFALL": "waterfall", "MB_INTERIOR_DEEP_WATER": "deep",
              "MB_NO_SURFACING": "deep", "MB_EASTWARD_CURRENT": "current", "MB_WESTWARD_CURRENT": "current",
              "MB_NORTHWARD_CURRENT": "current", "MB_SOUTHWARD_CURRENT": "current"}
SPECIAL = {"MB_ICE": "ice", "MB_THIN_ICE": "ice-thin", "MB_CRACKED_ICE": "ice-cracked", "MB_SAND": "sand",
           "MB_PUDDLE": "puddle", "MB_SHALLOW_WATER": "shallow-water", "MB_MUDDY_SLOPE": "muddy-slope",
           "MB_CRACKED_FLOOR": "cracked-floor", "MB_CRACKED_FLOOR_HOLE": "cracked-floor", "MB_HOT_SPRINGS": "hot-spring",
           "MB_SEAWEED": "seaweed", "MB_SEAWEED_NO_SURFACING": "seaweed", "MB_MOUNTAIN_TOP": "mountain-top",
           "MB_SLIDE_EAST": "slide", "MB_SLIDE_WEST": "slide", "MB_SLIDE_NORTH": "slide", "MB_SLIDE_SOUTH": "slide",
           "MB_CAVE": "cave-floor", "MB_SHORT_GRASS": "short-grass", "MB_LONG_GRASS_SOUTH_EDGE": "long-grass-edge",
           "MB_STAIRS_OUTSIDE_ABANDONED_SHIP": "stairs"}


# --------------------------------------------------------------------------------------------- reading
def behaviours() -> dict[int, str]:
    text = (gba.game_dir() / "include/constants/metatile_behaviors.h").read_text()
    body = text[text.index("enum {") + 6:text.index("};")]
    out, v = {}, 0
    for line in body.splitlines():
        m = re.match(r"\s*(MB_\w+)\s*(?:=\s*(\w+))?\s*,", line)
        if m:
            if m.group(2):
                v = int(m.group(2), 0)
            out[v] = m.group(1)
            v += 1
    return out


_PAIRS: dict = {}
AREA_ITEMS: dict = {}
META_ITEM: dict = defaultdict(set)     # (tileset, metatile) -> the (item, role) keys it was filed under
PAIR_ITEMS: dict = defaultdict(Counter) # (primary, secondary) -> Counter(item) by cells, to pick an area's usual ground
LAYOUT_VOTES: dict = defaultdict(Counter)  # (primary, secondary|'*', item, role) -> Counter(meta) by layouts using it


def pair(primary: str, secondary: str) -> gba.TilesetPair:
    k = (primary, secondary)
    if k not in _PAIRS:
        _PAIRS[k] = gba.TilesetPair(gba.load_tileset_by_header(primary), gba.load_tileset_by_header(secondary))
    return _PAIRS[k]


def meta_ts(p: gba.TilesetPair, mid: int) -> tuple[gba.Tileset, int]:
    return (p.primary, mid) if mid < gba.NUM_METATILES_IN_PRIMARY else (p.secondary, mid - gba.NUM_METATILES_IN_PRIMARY)


def behaviour_of(p: gba.TilesetPair, mid: int) -> int:
    ts, i = meta_ts(p, mid)
    return ts.behaviour(i) if i < ts.n_metatiles else 0


def areas() -> list[dict]:
    """Every wiki area with its vanilla layout (if it replaces a map) and whether its grid is still that layout."""
    maps, types = {}, {}
    for p in glob.glob(str(gba.game_dir() / "data/maps/*/map.json")):
        j = json.loads(Path(p).read_text())
        maps[j["name"]] = j["layout"]
        types[j["layout"]] = j.get("map_type", "")
    L = gba.layouts()
    import yaml
    out = []
    for p in sorted(glob.glob(str(WORLD / "**" / "*.yaml"), recursive=True)):
        d = yaml.safe_load(open(p))
        if not isinstance(d, dict) or "grid" not in d:
            continue
        grid = [r for r in (d.get("grid") or "").splitlines() if r]
        W = max(len(r) for r in grid)
        grid = [r.ljust(W, "x") for r in grid]
        lay = L.get(maps.get(d.get("replaces") or "", ""))
        same = bool(lay) and (lay.width, lay.height) == (W, len(grid))
        indoor = (types.get(lay.id, "") in ("MAP_TYPE_INDOOR", "MAP_TYPE_SECRET_BASE")) if lay else \
            d.get("kind", "") == "interior"
        out.append({"id": d["id"], "planet": d.get("planet", ""), "kind": d.get("kind", ""), "path": p,
                    "grid": grid, "layout": lay, "same": same, "indoor": indoor})
    return out


# --------------------------------------------------------------------------------------------- classing
def material(rgb: np.ndarray) -> Counter:
    """Colour families of a rendered 16x16 metatile: grass, sand, rock, water, snow, grey, dark."""
    px = rgb.reshape(-1, 3).astype(int)
    r, g, b = px[:, 0], px[:, 1], px[:, 2]
    mx, mn = px.max(1), px.min(1)
    sat = (mx - mn) / np.maximum(mx, 1)
    fam = np.full(len(px), "grey", dtype=object)
    fam[(mx < 60)] = "dark"
    fam[(b > r + 25) & (b >= g) & (mx >= 60)] = "water"
    fam[(g > r + 10) & (g > b - 10) & (mx >= 60) & (fam != "water")] = "grass"
    fam[(r >= g) & (g > b + 20) & (mx > 170) & (sat > 0.2)] = "sand"
    fam[(r > g + 8) & (r > b + 15) & (mx <= 200) & (fam == "grey")] = "rock"
    fam[(mn > 205) & (sat < 0.12)] = "snow"
    return Counter(fam.tolist())


def cell_class(beh: str, coll: int, rgb_cell: np.ndarray) -> str:
    """The blockout character for a vanilla cell (same rules as tools/blockout vanilla.py)."""
    if beh in LEDGE:
        return LEDGE[beh]
    if beh in WATER:
        return "~"
    if beh in BRIDGE:
        return "="
    if beh in WILD:
        return '"'
    if coll:
        cell = rgb_cell.reshape(-1, 3).astype(float)
        green = ((cell[:, 1] > cell[:, 0] + 12) & (cell[:, 1] > cell[:, 2] - 10)).mean()
        return "T" if green > 0.45 else "#"
    return "."


def item_name(ch: str, beh: str, fam: Counter, indoor: bool) -> str:
    total = sum(fam.values()) or 1
    top = [k for k, v in fam.most_common() if v / total >= 0.2 and k not in ("dark",)]
    main = top[0] if top else fam.most_common(1)[0][0]
    if beh in SPECIAL and ch in ".\"~":
        return SPECIAL[beh]
    if ch in LEDGE_NAME:
        return LEDGE_NAME[ch]
    if ch == "~":
        kind = WATER_KIND.get(beh, "water")
        return f"water-{kind}"                   # shores are the edge roles of the water item
    if ch == "=":
        return "bridge"
    if ch == '"':
        return {"MB_TALL_GRASS": "tall-grass", "MB_LONG_GRASS": "long-grass", "MB_ASHGRASS": "ash-grass",
                "MB_DEEP_SAND": "deep-sand"}.get(beh, "wild-grass")
    if ch == "T":
        return "tree"
    if ch == "#":
        if indoor:
            return "wall" if main in ("grey", "rock", "snow", "sand") else "structure"
        return "cliff" if main in ("rock", "grey", "snow", "sand", "dark") and fam.get("rock", 0) / total > 0.25 else "structure"
    # walkable ground
    if indoor:
        return "floor"
    # Hoenn's dirt path is the tan ("sand") family: plain, or with another ground's border (a path role).
    # Grey walkable tiles are stairs, concrete and stone floors: `ground-stone`, fill only.
    if main == "sand" or (len(top) >= 2 and "sand" in top[:2]):
        return "ground-path"
    return "ground-" + {"grey": "stone", "dark": "stone"}.get(main, main)


def phase(item: str) -> int:
    return 2 if item in PHASE2 else 1





# --------------------------------------------------------------------------------------------- catalog + autotile stats
def scan(all_areas: list[dict] | None = None):
    """Walk every vanilla layout the areas replace. Returns (items, stats):
    items[(tileset, item, role)] = {metas, areas, planets, cells, phase}
    stats[(primary, secondary or '*', item, role)] = Counter(meta)"""
    beh_names = behaviours()
    all_areas = all_areas or areas()
    items: dict = defaultdict(lambda: {"metas": Counter(), "areas": set(), "planets": set(), "cells": 0})
    stats: dict = defaultdict(Counter)
    done_layouts = {}
    voted = set()
    for ar in all_areas:
        lay = ar["layout"]
        if lay is None:
            continue
        if lay.name in done_layouts:
            for key in done_layouts[lay.name]:
                items[key]["areas"].add(ar["id"])
                items[key]["planets"].add(ar["planet"])
            continue
        p = pair(lay.primary, lay.secondary)
        img = np.asarray(gba.render_layout(lay, pair=p))
        raw = lay.cells()
        H, W = raw.shape
        names = [[""] * W for _ in range(H)]
        metas = np.zeros((H, W), int)
        indoor = ar["indoor"]
        fam_cache = {}
        for y in range(H):
            for x in range(W):
                v = int(raw[y, x])
                mid, coll = v & 0x3FF, (v >> 10) & 3
                beh = beh_names.get(behaviour_of(p, mid), "")
                cell = img[y * 16:(y + 1) * 16, x * 16:(x + 1) * 16]
                ch = cell_class(beh, coll, cell)
                if mid not in fam_cache:
                    fam_cache[mid] = material(cell)
                names[y][x] = item_name(ch, beh, fam_cache[mid], indoor)
                metas[y, x] = mid
        role_grid = R.roles(names)
        keys, seen = set(), set()
        for y in range(H):
            for x in range(W):
                mid = int(metas[y, x])
                name, role = names[y][x], role_grid[y][x]
                ts, local = meta_ts(p, mid)
                key = (ts.name, name, role)
                it = items[key]
                it["metas"][local] += 1
                it.setdefault("votes", Counter())
                if (ts.name, local, lay.name) not in voted:
                    voted.add((ts.name, local, lay.name))
                    it["votes"][local] += 1
                it["cells"] += 1
                it["phase"] = phase(name)
                META_ITEM[(ts.name, local)].add(key)
                keys.add(key)
                PAIR_ITEMS[(lay.primary, lay.secondary)][name] += 1
                seen.add((lay.secondary, name, role, mid))
                stats[(lay.primary, lay.secondary, name, role)][mid] += 1
                if mid < gba.NUM_METATILES_IN_PRIMARY:
                    seen.add(("*", name, role, mid))
                    stats[(lay.primary, "*", name, role)][mid] += 1
        for sec, name, role, mid in seen:              # votes: one per layout, so one big map cannot win alone
            LAYOUT_VOTES[(lay.primary, sec, name, role)][mid] += 1
        for key in keys:
            items[key]["areas"].add(ar["id"])
            items[key]["planets"].add(ar["planet"])
        done_layouts[lay.name] = keys
        AREA_ITEMS[lay.name] = keys
    return items, stats


# --------------------------------------------------------------------------------------------- autotile
GRID_CLASS = {":": ":", "_": ".", "|": "#", "x": "#", "H": ".", "=": "="}
USE_OVERRIDE: dict = {}        # (tileset, item, role) -> metatile id, hand-set in terrain.csv `use`


def load_overrides():
    USE_OVERRIDE.clear()
    if CSV_OUT.exists():
        for r in csv.DictReader(open(CSV_OUT)):
            if r.get("use") and r.get("use_set") == "hand":
                USE_OVERRIDE[(r["tileset"], r["item"], r["role"])] = int(r["use"], 16)


def _usual(prim: str, sec: str, pred, default: str) -> str:
    """The item this pair uses most among those matching pred (cells counted over its vanilla layouts)."""
    c = Counter({k: v for k, v in PAIR_ITEMS.get((prim, sec), Counter()).items() if pred(k)})
    if not c:
        c = Counter()
        for (p2, s2), cnt in PAIR_ITEMS.items():
            if p2 == prim:
                c.update({k: v for k, v in cnt.items() if pred(k)})
    return c.most_common(1)[0][0] if c else default


def grid_items(grid: list[str], prim: str, sec: str, indoor: bool, kind: str) -> list[list[str]]:
    """Grid characters -> item names, with the pair's usual ground, path, water and wild grass."""
    plain = lambda k: R.group(k) == "ground" and k not in ("ground-path", "ground-stone", "bridge", "tree", "structure") \
        and not k.startswith("ledge-")           # not the path, not stairs and stone (ground-stone)
    ground = _usual(prim, sec, plain, "floor" if indoor else "ground-grass")
    path = _usual(prim, sec, lambda k: k == "ground-path", ground)
    water = _usual(prim, sec, lambda k: k.startswith("water-"), "water-pond")
    wild = _usual(prim, sec, lambda k: k in ("tall-grass", "long-grass", "ash-grass", "deep-sand", "wild-grass"), "tall-grass")
    blocked = _usual(prim, sec, lambda k: k in ("wall", "cliff"), "wall" if kind in ("interior", "dungeon") else "cliff")
    table = {".": ground, ":": path, "~": water, '"': wild, "#": blocked, "T": "tree", "=": "bridge",
             "v": "ledge-south", "^": "ledge-north", "<": "ledge-west", ">": "ledge-east"}
    out = []
    for row in grid:
        out.append([table.get(GRID_CLASS.get(c, c), ground) for c in row])
    return out


def lookup(prim: str, sec: str, item: str, role: str, stats: dict, p: gba.TilesetPair):
    """The metatile for an item role in this pair: hand-set `use` first, then the learned one. None if missing."""
    for ts in (p.secondary.name, p.primary.name):
        o = USE_OVERRIDE.get((ts, item, role))
        if o is not None:
            return o + (gba.NUM_METATILES_IN_PRIMARY if ts == p.secondary.name else 0)
    # grounds and paths: the primary's shared tiles first (the standard path, not one map's stairs);
    # cliffs, walls, water: the pair's own tiles first (cave walls, lava shores)
    order = ("*", sec) if item.startswith("ground-") else (sec, "*")
    for s in order:
        c = stats.get((prim, s, item, role))
        if c:
            votes = LAYOUT_VOTES.get((prim, s, item, role), Counter())
            return max(c, key=lambda m: (votes[m], c[m]))     # most layouts, then most cells
    return None


def autotile(grid: list[str], prim: str, sec: str, stats: dict, indoor: bool = False, kind: str = ""):
    """Grid characters -> metatile ids (MISSING where the pair has no tile for the role).
    Returns (cells, needs): needs[(item, role)] = metatile or None."""
    p = pair(prim, sec)
    names = grid_items(grid, prim, sec, indoor, kind)
    role_grid = R.roles(names)
    H, W = len(grid), len(grid[0])
    out = np.full((H, W), MISSING, np.uint16)
    needs: dict = {}
    for y in range(H):
        for x in range(W):
            key = (names[y][x], role_grid[y][x])
            if key not in needs:
                needs[key] = lookup(prim, sec, key[0], key[1], stats, p)
            if needs[key] is not None:
                out[y, x] = needs[key]
    return out, needs


def pair_for(ar: dict, all_areas: list[dict]) -> tuple[str, str]:
    """The tileset pair an area is drawn with: its vanilla layout's, else the one its planet uses most
    for the same kind of area."""
    if ar["same"]:
        return ar["layout"].primary, ar["layout"].secondary
    if (ar["planet"], ar["kind"]) in PAIR_OVERRIDE:
        return PAIR_OVERRIDE[(ar["planet"], ar["kind"])]
    if ar["layout"] is not None:
        return ar["layout"].primary, ar["layout"].secondary
    kinds = {"interior": ("interior",), "dungeon": ("dungeon",)}.get(ar["kind"], ("town", "route", "landmark"))
    c = Counter((a["layout"].primary, a["layout"].secondary) for a in all_areas
                if a["layout"] is not None and a["kind"] in kinds and a["planet"] == ar["planet"])
    if not c:
        c = Counter((a["layout"].primary, a["layout"].secondary) for a in all_areas
                    if a["layout"] is not None and a["kind"] in kinds)
    return c.most_common(1)[0][0]


_CELLS: dict = {}


def area_cells(ar: dict, all_areas: list[dict], stats: dict):
    """The metatile grid an area is drawn with (vanilla layout or autotiled) and its needs (autotiled only)."""
    if ar["id"] in _CELLS:
        return _CELLS[ar["id"]]
    if ar["same"]:
        r = (ar["layout"].cells() & 0x3FF, {})
    else:
        prim, sec = pair_for(ar, all_areas)
        r = autotile(ar["grid"], prim, sec, stats, ar["indoor"], ar["kind"])
    _CELLS[ar["id"]] = r
    return r


def render_area(ar: dict, all_areas: list[dict], stats: dict) -> tuple[Image.Image, str]:
    prim, sec = pair_for(ar, all_areas)
    p = greybox_pair(prim, sec, ar["planet"])
    cells, _ = area_cells(ar, all_areas, stats)
    return render_cells(cells, p), "vanilla layout" if ar["same"] else "autotiled from the grid"


# --------------------------------------------------------------------------------------------- catalog
def _row_key(r):
    return (r[0] != "general", r[0], phase(r[1]), r[1], R.role_set(r[1]).index(r[2]) if r[2] in R.role_set(r[1]) else 99)


def write_catalog(items: dict, needs_by_area: dict, all_areas: list[dict]) -> list[dict]:
    """terrain.csv: one row per tileset, item and role. Vanilla rows list their metatiles; a role an autotiled
    area needs that vanilla never drew in its pair is a TODO row with no tile. Keeps status, notes and a
    hand-set `use` already in the file."""
    old = {}
    if CSV_OUT.exists():
        old = {r["terrain_id"]: r for r in csv.DictReader(open(CSV_OUT))}
    rows_d: dict = {}
    for (ts, name, role), it in items.items():
        rows_d[(ts, name, role)] = {"metas": it["metas"], "votes": it.get("votes", Counter()), "areas": set(it["areas"]),
                                    "planets": set(it["planets"]), "cells": it["cells"], "needed_by": set()}
    by_id = {a["id"]: a for a in all_areas}
    for aid, (prim, sec, needs) in needs_by_area.items():
        p = pair(prim, sec)
        for (name, role), mid in needs.items():
            if mid is None:
                key = (p.secondary.name if p.secondary.name != "0" else p.primary.name, name, role)
                r = rows_d.setdefault(key, {"metas": Counter(), "areas": set(), "planets": set(), "cells": 0, "needed_by": set()})
            else:
                ts, local = meta_ts(p, mid)
                key = (ts.name, name, role)
                r = rows_d.setdefault(key, {"metas": Counter({local: 0}), "areas": set(), "planets": set(), "cells": 0, "needed_by": set()})
            r["needed_by"].add(aid)
            r["planets"].add(by_id[aid]["planet"])
    rows = []
    for (ts, name, role) in sorted(rows_d, key=_row_key):
        it = rows_d[(ts, name, role)]
        tid = f"terrain:{ts}:{name}:{role}"
        metas = [m for m, _ in it["metas"].most_common()]
        if metas and it.get("votes"):
            metas.sort(key=lambda m: (-it["votes"][m], -it["metas"][m]))
        o = old.get(tid, {})
        hand = o.get("use_set") == "hand" and o.get("use")
        use = o["use"] if hand else (f"{metas[0]:03x}" if metas else "")
        status = o.get("status") or ""
        if not use:                                   # no tile: TODO, whatever it said before
            status = "pending-mockup"
        elif status in ("", "pending-mockup"):        # a tile now exists: greybox done
            status = "pending-final-art"
        note = o.get("notes", "")
        if not note:
            if phase(name) == 2:
                note = "Phase 2 (structures and trees): listed only."
            elif not use:
                need = sorted(it["needed_by"])
                note = "No vanilla tile for this role: placeholder in the sheet. Needed by " + \
                       ", ".join(need[:6]) + (f" and {len(need) - 6} more" if len(need) > 6 else "") + "."
        rows.append({
            "terrain_id": tid, "tileset": ts, "item": name, "role": role, "phase": phase(name),
            "metatiles": len(metas), "metatile_ids": " ".join(f"{m:03x}" for m in sorted(metas)),
            "use": use, "use_set": "hand" if hand else ("learned" if use else ""),
            "cells": it["cells"], "planets": " | ".join(sorted(it["planets"])),
            "areas": len(it["areas"] | it["needed_by"]), "needed_by": len(it["needed_by"]),
            "tool": "tilegen terrain" if phase(name) == 1 else "",
            "status": status,
            "sheet": f"world/greybox/sheets/{ts}.png", "sheet_cell": "",
            "notes": note,
        })
    # sheet cells: csv order within each tileset, SHEET_COLS per row
    n_by_ts = Counter()
    for r in rows:
        i = n_by_ts[r["tileset"]]
        r["sheet_cell"] = f"{i % SHEET_COLS},{i // SHEET_COLS}"
        n_by_ts[r["tileset"]] += 1
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows


# --------------------------------------------------------------------------------------------- greybox
def _grey_recipe():
    from . import recolour
    return recolour.Recipe("greybox", [recolour.Rule("grey", None, set={"chroma_scale": GREY_CHROMA})])


_GREY: dict = {}


def greybox_pair(primary: str, secondary: str, planet: str = "") -> gba.TilesetPair:
    """The planet's recipe (if any), then greyed. Pixels and metatiles are the vanilla ones."""
    from . import recolour
    key = (primary, secondary, PLANET_RECIPE.get(planet, ""))
    if key in _GREY:
        return _GREY[key]
    p = pair(primary, secondary)
    rname = key[2]
    if rname and (RECIPES / f"{rname}.yaml").exists():
        rec = recolour.Recipe.load(RECIPES / f"{rname}.yaml")
        p = recolour.recolour_pair(p, rec)
    g = recolour.recolour_pair(p, _grey_recipe())
    _GREY[key] = g
    return g


_PH = None


def placeholder_cell(backdrop=(44, 44, 48)) -> np.ndarray:
    """The z-day 16x16 placeholder (magenta circle) on a dark backdrop."""
    global _PH
    if _PH is None:
        im = Image.new("RGBA", (16, 16), backdrop + (255,))
        im.alpha_composite(Image.open(PLACEHOLDER).convert("RGBA"))
        _PH = np.asarray(im.convert("RGB"))
    return _PH


def render_cells(cells: np.ndarray, p: gba.TilesetPair) -> Image.Image:
    H, W = cells.shape
    out = np.zeros((H * 16, W * 16, 3), np.uint8)
    cache = {}
    for y in range(H):
        for x in range(W):
            mid = int(cells[y, x])
            if mid == MISSING:
                out[y * 16:(y + 1) * 16, x * 16:(x + 1) * 16] = placeholder_cell()
                continue
            mid &= 0x3FF
            if mid not in cache:
                cache[mid] = p.render_metatile(mid, backdrop=(0, 0, 0))[..., :3]
            out[y * 16:(y + 1) * 16, x * 16:(x + 1) * 16] = cache[mid]
    return Image.fromarray(out, "RGB")


# --------------------------------------------------------------------------------------------- sheets
def _sample_pairs(all_areas: list[dict]) -> dict:
    """A pair to draw each tileset's metatiles with: any layout that uses it."""
    sample = {}
    for ar in all_areas:
        lay = ar["layout"]
        if lay is None:
            continue
        p = pair(lay.primary, lay.secondary)
        for tsname in (p.primary.name, p.secondary.name):
            sample.setdefault(tsname, (lay.primary, lay.secondary))
    return sample


def real_sheets(rows: list[dict], all_areas: list[dict]) -> list[Path]:
    """One real-size sheet per tileset: 128 px wide, 16x16 cells in csv order, the `use` tile in greybox or the
    placeholder where there is none."""
    REAL_OUT.mkdir(parents=True, exist_ok=True)
    sample = _sample_pairs(all_areas)
    by_ts = defaultdict(list)
    for r in rows:
        by_ts[r["tileset"]].append(r)
    out = []
    for ts, lst in by_ts.items():
        if ts not in sample:
            continue
        p = greybox_pair(*sample[ts])
        base = 0 if p.primary.name == ts else gba.NUM_METATILES_IN_PRIMARY
        n = len(lst)
        sheet = np.zeros((((n + SHEET_COLS - 1) // SHEET_COLS) * 16, SHEET_COLS * 16, 3), np.uint8)
        for i, r in enumerate(lst):
            cx, cy = (i % SHEET_COLS) * 16, (i // SHEET_COLS) * 16
            if r["use"]:
                sheet[cy:cy + 16, cx:cx + 16] = p.render_metatile(base + int(r["use"], 16), backdrop=(0, 0, 0))[..., :3]
            else:
                sheet[cy:cy + 16, cx:cx + 16] = placeholder_cell()
        f = REAL_OUT / f"{ts}.png"
        Image.fromarray(sheet, "RGB").save(f)
        out.append(f)
    return out


def item_sheets(rows: list[dict], all_areas: list[dict]) -> list[Path]:
    """One labelled sheet per tileset: every item as a strip of its roles at 2x, each cell named, the
    placeholder where the role has no tile."""
    SHEETS_OUT.mkdir(parents=True, exist_ok=True)
    sample = _sample_pairs(all_areas)
    by_ts = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_ts[r["tileset"]][r["item"]].append(r)
    out = []
    CW, CH = 58, 48
    for ts, items_ in by_ts.items():
        if ts not in sample:
            continue
        p = greybox_pair(*sample[ts])
        base = 0 if p.primary.name == ts else gba.NUM_METATILES_IN_PRIMARY
        strips = []
        for name, lst in items_.items():
            cols = min(len(lst), 10)
            h = ((len(lst) + cols - 1) // cols) * CH + 14
            strip = Image.new("RGB", (cols * CW + 4, h), (34, 34, 38))
            d = ImageDraw.Draw(strip)
            todo = sum(1 for r in lst if not r["use"])
            d.text((4, 1), f"{name}  ({len(lst)} roles, {todo} missing, phase {lst[0]['phase']})", fill=(230, 230, 230))
            for i, r in enumerate(lst):
                x, y = 2 + (i % cols) * CW, 14 + (i // cols) * CH
                cell = p.render_metatile(base + int(r["use"], 16), backdrop=(0, 0, 0))[..., :3] if r["use"] else placeholder_cell()
                strip.paste(Image.fromarray(cell, "RGB").resize((32, 32), Image.NEAREST), (x + 12, y))
                d.text((x + 2, y + 34), r["role"][:9], fill=(200, 200, 200) if r["use"] else (255, 120, 220))
            strips.append(strip)
        W = max(s.width for s in strips)
        sheet = Image.new("RGB", (W, sum(s.height for s in strips)), (34, 34, 38))
        y = 0
        for s in strips:
            sheet.paste(s, (0, y))
            y += s.height
        f = SHEETS_OUT / f"{ts}.png"
        sheet.save(f)
        out.append(f)
    return out


# --------------------------------------------------------------------------------------------- the whole run
def catalog(A: list[dict] | None = None):
    """Scan, autotile every redesigned area, write terrain.csv. Returns (areas, items, stats, rows)."""
    A = A or areas()
    load_overrides()
    _CELLS.clear()
    items, stats = scan(A)
    needs_by_area = {}
    for ar in A:
        if not ar["same"]:
            prim, sec = pair_for(ar, A)
            _, needs = area_cells(ar, A, stats)
            needs_by_area[ar["id"]] = (prim, sec, needs)
    rows = write_catalog(items, needs_by_area, A)
    return A, items, stats, rows


def run(ids: list[str] | None = None, planet: str | None = None, sheets: bool = True) -> dict:
    """Catalog, sheets and area renders in one go. Returns counts."""
    A, items, stats, rows = catalog()
    if sheets:
        real_sheets(rows, A)
        item_sheets(rows, A)
    TILES_OUT.mkdir(parents=True, exist_ok=True)
    how = Counter()
    links = []
    for ar in A:
        prim, sec = pair_for(ar, A)
        src = "vanilla layout" if ar["same"] else "autotiled from the grid"
        cells, needs = area_cells(ar, A, stats)
        if ar["same"]:
            its = sorted(f"terrain:{t}:{n}:{r}" for t, n, r in AREA_ITEMS.get(ar["layout"].name, ()))
            missing = 0
        else:
            pp = pair(prim, sec)
            its = set()
            for (n, r), mid in needs.items():
                if mid is None:
                    its.add(f"terrain:{pp.secondary.name}:{n}:{r}")
                else:
                    ts, _ = meta_ts(pp, mid)
                    its.add(f"terrain:{ts.name}:{n}:{r}")
            its = sorted(its)
            missing = sum(1 for v in needs.values() if v is None)
        links.append({"area_id": ar["id"], "planet": ar["planet"], "kind": ar["kind"], "primary": prim,
                      "secondary": sec, "source": src, "missing_roles": missing,
                      "render": f"world/greybox/tiles/{ar['id']}.png", "terrain_items": " ".join(its)})
        if ids and ar["id"] not in ids:
            continue
        if planet and ar["planet"] != planet:
            continue
        im, h = render_area(ar, A, stats)
        im.save(TILES_OUT / f"{ar['id']}.png")
        how[h] += 1
    with open(AREAS_OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(links[0].keys()))
        w.writeheader()
        w.writerows(links)
    return {"rows": len(rows), "phase1": sum(1 for r in rows if r["phase"] == 1),
            "missing": sum(1 for r in rows if not r["use"]), **how}


def mark(status: str, phase_: int = 1) -> int:
    """Set the status of every phase item that has a tile in terrain.csv (after a full greybox run)."""
    rows = list(csv.DictReader(open(CSV_OUT)))
    n = 0
    for r in rows:
        if int(r["phase"]) == phase_ and r["tool"] and r["use"]:
            r["status"] = status
            n += 1
    with open(CSV_OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return n


def build_planet(planet: str, out: Path) -> list[Path]:
    """Write the planet's greybox tilesets in game format (tiles.png, palettes, metatiles, attributes) for
    every pair its areas use, through the palette gate. Nothing is installed into game/."""
    from . import pack
    A = areas()
    pairs = {pair_for(a, A) for a in A if a["planet"] == planet}
    done = []
    for prim, sec in sorted(pairs):
        g = greybox_pair(prim, sec, planet)
        for ts in (g.primary, g.secondary):
            d = out / planet.lower().replace(" ", "-") / ts.name
            if d in done:
                continue
            pack.write_tileset(ts, d)
            ok, lines = pack.check_tileset(ts, d)
            (d / "check.txt").write_text("\n".join(lines) + "\n")
            done.append(d)
            print(f"{'OK  ' if ok else 'FAIL'} {d}")
    return done

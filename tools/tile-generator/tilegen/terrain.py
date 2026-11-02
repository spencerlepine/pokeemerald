"""Greybox terrain: every ground, water, ledge and cliff tile of every area, itemized in the wiki.

Phase 1 of the world art (owner, 2026-11-02): terrain only, in greybox. The game already has all the
terrain shapes (grass, paths, shores, ledges, cliffs, caves, floors); this repaints them and keeps them.

  - **Catalog.** Every vanilla layout an area replaces is read cell by cell. Each cell is classed the way
    blockout classes it (`.` ground, `"` wild grass, `~` water, `v ^ < >` ledges, `=` bridge, `#` blocked,
    `T` tree) and its metatile is filed under a terrain item of its tileset, e.g. `terrain:general:ledge-south`
    or `terrain:general:water-shore`. Items get the areas and planets that use them. Phase 1 items are ground,
    grass, water, shores, ledges, bridges, cliffs, cave and room floors and walls; trees and structures are
    phase 2 and only listed. Written to `wiki/mapping/terrain.csv`.
  - **Greybox.** A planet's tilesets are recoloured with its approved planet recipe (if it has one) and then
    desaturated to grey (`GREY_CHROMA`), so shading, materials and shapes stay and colour waits.
  - **Areas.** An area that keeps its vanilla layout is that layout drawn with the planet's greybox tiles.
    An area whose grid was redesigned (or is new) is **autotiled**: each grid cell takes the metatile that
    vanilla maps use most for the same cell class with the same neighbours (8, then 4, then none), so shores,
    cliff edges and ledge ends come out the way the game draws them. Renders go to
    `wiki/world/greybox/tiles/<area>.png`.

`python -m tilegen terrain catalog|sheets|render [--area ID ...] [--planet P]|build <planet>`.
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

from . import gba, colour

ROOT = Path(__file__).resolve().parents[3]
WIKI = ROOT / "wiki"
WORLD = WIKI / "world"
CSV_OUT = WIKI / "mapping" / "terrain.csv"
AREAS_OUT = WIKI / "mapping" / "terrain_areas.csv"
TILES_OUT = WORLD / "greybox" / "tiles"
SHEETS_OUT = WORLD / "greybox" / "terrain"
RECIPES = Path(__file__).resolve().parents[1] / "recipes"

GREY_CHROMA = 0.22          # how much of the planet colour a greybox keeps
PLANET_RECIPE = {"TATOOINE": "tatooine", "HOTH": "hoth", "ILUM": "hoth", "SULLUST": "sullust",
                 "MUSTAFAR": "sullust-lava", "ENDOR": "endor", "YAVIN 4": "endor", "KASHYYYK": "endor",
                 "DAGOBAH": "dagobah", "KAMINO": "kamino", "DEATH STAR": "death-star"}
PHASE2 = {"tree", "structure"}
# a planet whose areas have no vanilla layout of that kind to borrow a pair from
PAIR_OVERRIDE = {("DEATH STAR", "dungeon"): ("gTileset_General", "gTileset_Facility")}

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
META_ITEM: dict = defaultdict(set)     # (tileset, metatile) -> the items it was filed under       # layout name -> the terrain items its cells use (filled by scan)


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
    maps = {}
    for p in glob.glob(str(gba.game_dir() / "data/maps/*/map.json")):
        j = json.loads(Path(p).read_text())
        maps[j["name"]] = j["layout"]
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
        out.append({"id": d["id"], "planet": d.get("planet", ""), "kind": d.get("kind", ""), "path": p,
                    "grid": grid, "layout": lay, "same": same})
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
        land = sum(v for k, v in fam.items() if k not in ("water", "dark", "grey")) / total
        return "water-shore" if land >= 0.15 and kind in ("pond", "ocean") else f"water-{kind}"
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
    if len(top) >= 2 and set(top[:2]) != {"grey", "snow"}:
        return "ground-edge-" + "-".join(sorted(top[:2]))
    return "ground-" + {"grey": "path", "dark": "path"}.get(main, main)


def phase(item: str) -> int:
    return 2 if item in PHASE2 else 1


def is_indoor(lay: gba.Layout) -> bool:
    return lay.primary in ("gTileset_Building", "gTileset_SecretBase") or "Building" in lay.primary


# --------------------------------------------------------------------------------------------- catalog + autotile stats
def scan(all_areas: list[dict] | None = None):
    """Walk every vanilla layout the areas replace. Returns (items, stats):
    items[(tileset, item)] = {metas, areas, planets, cells, phase, pair}
    stats[(primary, secondary or '*', ch, sig)] = Counter(meta)"""
    beh_names = behaviours()
    all_areas = all_areas or areas()
    items: dict = defaultdict(lambda: {"metas": Counter(), "areas": set(), "planets": set(), "cells": 0})
    stats: dict = defaultdict(Counter)
    done_layouts = {}
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
        chars = [[""] * W for _ in range(H)]
        metas = np.zeros((H, W), int)
        indoor = is_indoor(lay)
        keys = set()
        fam_cache = {}
        for y in range(H):
            for x in range(W):
                v = int(raw[y, x])
                mid, coll = v & 0x3FF, (v >> 10) & 3
                beh = beh_names.get(behaviour_of(p, mid), "")
                cell = img[y * 16:(y + 1) * 16, x * 16:(x + 1) * 16]
                ch = cell_class(beh, coll, cell)
                chars[y][x] = ch
                metas[y, x] = mid
                if mid not in fam_cache:
                    fam_cache[mid] = material(cell)
                ts, _ = meta_ts(p, mid)
                name = item_name(ch, beh, fam_cache[mid], indoor)
                key = (ts.name, name)
                it = items[key]
                it["metas"][mid if mid < 512 else mid - 512] += 1
                META_ITEM[(ts.name, mid if mid < 512 else mid - 512)].add(key)
                it["cells"] += 1
                it["phase"] = phase(name)
                it["indoor"] = indoor
                keys.add(key)
        for key in keys:
            items[key]["areas"].add(ar["id"])
            items[key]["planets"].add(ar["planet"])
        done_layouts[lay.name] = keys
        AREA_ITEMS[lay.name] = keys
        # autotile statistics: what metatile a cell class takes, given its neighbours
        for y in range(H):
            for x in range(W):
                ch = chars[y][x]
                n8 = "".join(chars[y + dy][x + dx] if 0 <= y + dy < H and 0 <= x + dx < W else "_"
                             for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)))
                n4 = n8[1] + n8[3] + n8[5] + n8[7]
                mid = int(metas[y, x])
                for sec in (lay.secondary, "*"):
                    if sec == "*" and mid >= 512:
                        continue
                    stats[(lay.primary, sec, ch, n8)][mid] += 1
                    stats[(lay.primary, sec, ch, n4)][mid] += 1
                    stats[(lay.primary, sec, ch, "")][mid] += 1
    return items, stats


def write_catalog(items: dict) -> list[dict]:
    """terrain.csv: one row per terrain item per tileset. Keeps the status and notes already in the file."""
    old = {}
    if CSV_OUT.exists():
        old = {r["terrain_id"]: r for r in csv.DictReader(open(CSV_OUT))}
    rows = []
    for (ts, name), it in sorted(items.items(), key=lambda kv: (kv[0][0] != "general", kv[0][0], phase(kv[0][1]), kv[0][1])):
        tid = f"terrain:{ts}:{name}"
        metas = sorted(it["metas"])
        o = old.get(tid, {})
        rows.append({
            "terrain_id": tid, "tileset": ts, "item": name, "phase": phase(name),
            "metatiles": len(metas), "metatile_ids": " ".join(f"{m:03x}" for m in metas),
            "cells": it["cells"], "planets": " | ".join(sorted(it["planets"])), "areas": len(it["areas"]),
            "tool": "tilegen terrain" if phase(name) == 1 else "",
            "status": o.get("status") or "pending-mockup",
            "greybox": f"world/greybox/terrain/{ts}.png",
            "notes": o.get("notes") or ("Phase 2 (structures and trees): listed only." if phase(name) == 2 else ""),
        })
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


def render_cells(cells: np.ndarray, p: gba.TilesetPair) -> Image.Image:
    H, W = cells.shape
    out = np.zeros((H * 16, W * 16, 3), np.uint8)
    cache = {}
    for y in range(H):
        for x in range(W):
            mid = int(cells[y, x]) & 0x3FF
            if mid not in cache:
                cache[mid] = p.render_metatile(mid, backdrop=(0, 0, 0))[..., :3]
            out[y * 16:(y + 1) * 16, x * 16:(x + 1) * 16] = cache[mid]
    return Image.fromarray(out, "RGB")


# --------------------------------------------------------------------------------------------- autotile
GRID_CLASS = {":": ".", "_": ".", "|": "#", "x": "#", "H": ".", "=": "="}


def autotile(grid: list[str], primary: str, secondary: str, stats: dict) -> np.ndarray:
    """Grid characters -> metatile ids, by the most common vanilla choice for the same class and neighbours."""
    H, W = len(grid), len(grid[0])
    g = [[GRID_CLASS.get(c, c) for c in row] for row in grid]
    out = np.zeros((H, W), np.uint16)
    for y in range(H):
        for x in range(W):
            ch = g[y][x]
            n8 = "".join(g[y + dy][x + dx] if 0 <= y + dy < H and 0 <= x + dx < W else "_"
                         for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)))
            n4 = n8[1] + n8[3] + n8[5] + n8[7]
            pick = None
            for sec in (secondary, "*"):
                for sig in (n8, n4, ""):
                    c = stats.get((primary, sec, ch, sig))
                    if c:
                        pick = c.most_common(1)[0][0]
                        break
                if pick is not None:
                    break
            if pick is None:                      # a class this pair never uses: fall back to its ground
                for sec in (secondary, "*"):
                    c = stats.get((primary, sec, ".", ""))
                    if c:
                        pick = c.most_common(1)[0][0]
                        break
            out[y, x] = pick or 1
    return out


def pair_for(ar: dict, all_areas: list[dict]) -> tuple[str, str]:
    """The tileset pair an area is drawn with: its vanilla layout's, else the one its planet uses most
    for the same kind of area."""
    if ar["layout"] is not None:
        return ar["layout"].primary, ar["layout"].secondary
    if (ar["planet"], ar["kind"]) in PAIR_OVERRIDE:
        return PAIR_OVERRIDE[(ar["planet"], ar["kind"])]
    kinds = {"interior": ("interior",), "dungeon": ("dungeon",)}.get(ar["kind"], ("town", "route", "landmark"))
    c = Counter((a["layout"].primary, a["layout"].secondary) for a in all_areas
                if a["layout"] is not None and a["kind"] in kinds and a["planet"] == ar["planet"])
    if not c:
        c = Counter((a["layout"].primary, a["layout"].secondary) for a in all_areas
                    if a["layout"] is not None and a["kind"] in kinds)
    return c.most_common(1)[0][0]


def area_cells(ar: dict, all_areas: list[dict], stats: dict) -> np.ndarray:
    """The metatile grid an area is drawn with: its vanilla layout, or the grid autotiled."""
    if ar["same"]:
        return ar["layout"].cells() & 0x3FF
    prim, sec = pair_for(ar, all_areas)
    return autotile(ar["grid"], prim, sec, stats)


def render_area(ar: dict, all_areas: list[dict], stats: dict) -> tuple[Image.Image, str]:
    prim, sec = pair_for(ar, all_areas)
    p = greybox_pair(prim, sec, ar["planet"])
    cells = area_cells(ar, all_areas, stats)
    return render_cells(cells, p), "vanilla layout" if ar["same"] else "autotiled from the grid"


# --------------------------------------------------------------------------------------------- sheets
def item_sheets(items: dict, rows: list[dict]) -> list[Path]:
    """One sheet per tileset: every phase 1 item as a labelled strip of its metatiles, in plain greybox."""
    SHEETS_OUT.mkdir(parents=True, exist_ok=True)
    by_ts = defaultdict(list)
    for (ts, name), it in items.items():
        by_ts[ts].append((name, it))
    # a pair to draw each tileset's metatiles with: any layout that uses it
    sample_pair = {}
    for ar in areas():
        lay = ar["layout"]
        if lay is None:
            continue
        for tsname in (pair(lay.primary, lay.secondary).primary.name, pair(lay.primary, lay.secondary).secondary.name):
            sample_pair.setdefault(tsname, (lay.primary, lay.secondary))
    out = []
    for ts, lst in by_ts.items():
        if ts not in sample_pair:
            continue
        prim, sec = sample_pair[ts]
        p = greybox_pair(prim, sec)
        base = 0 if p.primary.name == ts else 512
        lst = sorted(lst, key=lambda t: (phase(t[0]), t[0]))
        cols = 24
        rows_px = []
        for name, it in lst:
            metas = [m for m, _ in it["metas"].most_common()][:cols * 3]
            n = len(metas)
            h = ((n + cols - 1) // cols) * 18 + 14
            strip = Image.new("RGB", (cols * 18 + 4, h), (34, 34, 38))
            d = ImageDraw.Draw(strip)
            d.text((4, 1), f"{name}  ({len(it['metas'])} metatiles, {it['cells']} cells, phase {phase(name)})",
                   fill=(230, 230, 230))
            for i, m in enumerate(metas):
                img = Image.fromarray(p.render_metatile(base + m, backdrop=(255, 0, 255))[..., :3], "RGB")
                strip.paste(img, (2 + (i % cols) * 18, 14 + (i // cols) * 18))
            rows_px.append(strip)
        W = max(s.width for s in rows_px)
        sheet = Image.new("RGB", (W, sum(s.height for s in rows_px)), (34, 34, 38))
        y = 0
        for s in rows_px:
            sheet.paste(s, (0, y))
            y += s.height
        f = SHEETS_OUT / f"{ts}.png"
        sheet.save(f)
        out.append(f)
    return out


# --------------------------------------------------------------------------------------------- the whole run
def run(ids: list[str] | None = None, planet: str | None = None, sheets: bool = True) -> dict:
    """Catalog, item sheets and area renders in one go. Returns counts."""
    A = areas()
    items, stats = scan(A)
    rows = write_catalog(items)
    if sheets:
        item_sheets(items, rows)
    TILES_OUT.mkdir(parents=True, exist_ok=True)
    how = Counter()
    links = []
    for ar in A:
        prim, sec = pair_for(ar, A)
        src = "vanilla layout" if ar["same"] else "autotiled from the grid"
        if ar["same"]:
            its = sorted(f"terrain:{t}:{n}" for t, n in AREA_ITEMS.get(ar["layout"].name, ()))
        else:                               # autotiled: the items of the metatiles it was given
            pp = pair(prim, sec)
            its = set()
            for mid in set(int(v) for v in area_cells(ar, A, stats).ravel()):
                ts, local = meta_ts(pp, mid)
                its |= {f"terrain:{t}:{n}" for (t, n) in META_ITEM.get((ts.name, local), ())}
            its = sorted(its)
        links.append({"area_id": ar["id"], "planet": ar["planet"], "kind": ar["kind"], "primary": prim,
                      "secondary": sec, "source": src, "render": f"world/greybox/tiles/{ar['id']}.png",
                      "terrain_items": " ".join(its)})
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
    return {"items": len(rows), "phase1": sum(1 for r in rows if r["phase"] == 1), **how}


def mark(status: str, phase_: int = 1) -> int:
    """Set the status of every item of a phase in terrain.csv (after a full greybox run)."""
    rows = list(csv.DictReader(open(CSV_OUT)))
    n = 0
    for r in rows:
        if int(r["phase"]) == phase_ and r["tool"]:
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

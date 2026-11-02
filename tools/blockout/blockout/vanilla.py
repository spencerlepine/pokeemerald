"""Read a vanilla Emerald map into blockout terms: a terrain grid from the collision bits and metatile
behaviours, plus its doors, people, signs and connections. Used to start an area from the map it
replaces (so the result can be built into that map later) and to draw vanilla next to the blockout."""
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
GAME = ROOT / "game"
TILEGEN = Path(os.environ.get("TILEGEN_DIR", ROOT / "tools" / "tile-generator"))


def _gba():
    sys.path.insert(0, str(TILEGEN))
    from tilegen import gba
    return gba


def behaviours():
    """MB_* name -> value, parsed from the enum in metatile_behaviors.h."""
    text = (GAME / "include/constants/metatile_behaviors.h").read_text()
    body = text[text.index("enum {") + 6:text.index("};")]
    out, v = {}, 0
    for line in body.splitlines():
        m = re.match(r"\s*(MB_\w+)\s*(?:=\s*(\w+))?\s*,", line)
        if m:
            if m.group(2):
                v = int(m.group(2), 0)
            out[m.group(1)] = v
            v += 1
    return out


def map_json(map_name):
    return json.loads((GAME / "data/maps" / map_name / "map.json").read_text())


def terrain_grid(map_name, layout=None):
    """Rows of terrain chars for a vanilla map (or one of its alternate layouts, by layout id)."""
    gba = _gba()
    mj = map_json(map_name)
    lay = gba.layouts()[layout or mj["layout"]]
    raw = lay.cells()
    mb = behaviours()
    inv = {v: k for k, v in mb.items()}
    water = {"MB_POND_WATER", "MB_DEEP_WATER", "MB_OCEAN_WATER", "MB_SOOTOPOLIS_DEEP_WATER", "MB_WATERFALL",
             "MB_INTERIOR_DEEP_WATER", "MB_NO_SURFACING", "MB_EASTWARD_CURRENT", "MB_WESTWARD_CURRENT",
             "MB_NORTHWARD_CURRENT", "MB_SOUTHWARD_CURRENT"}
    wild = {"MB_TALL_GRASS", "MB_LONG_GRASS", "MB_ASHGRASS", "MB_DEEP_SAND"}
    ledge = {"MB_JUMP_SOUTH": "v", "MB_JUMP_NORTH": "^", "MB_JUMP_WEST": "<", "MB_JUMP_EAST": ">"}
    bridge = {"MB_FORTREE_BRIDGE", "MB_PACIFIDLOG_VERTICAL_LOG_TOP", "MB_PACIFIDLOG_VERTICAL_LOG_BOTTOM",
              "MB_PACIFIDLOG_HORIZONTAL_LOG_LEFT", "MB_PACIFIDLOG_HORIZONTAL_LOG_RIGHT", "MB_BRIDGE_OVER_POND_LOW",
              "MB_BRIDGE_OVER_OCEAN", "MB_BRIDGE_OVER_POND_MED", "MB_BRIDGE_OVER_POND_HIGH"}
    img = np.asarray(gba.render_layout(lay).convert("RGB"), dtype=float)
    rows = []
    for r in range(lay.height):
        line = ""
        for c in range(lay.width):
            v = int(raw[r, c])
            meta, coll = v & 0x3FF, (v >> 10) & 3
            name = inv.get(_behaviour(gba, lay, meta), "")
            if name in ledge:
                ch = ledge[name]
            elif name in water:
                ch = "~"
            elif name in bridge:
                ch = "="
            elif name in wild:
                ch = '"'
            elif coll:
                cell = img[r * 16:(r + 1) * 16, c * 16:(c + 1) * 16].reshape(-1, 3)
                rr, gg, bb = cell.mean(0)
                green = ((cell[:, 1] > cell[:, 0] + 12) & (cell[:, 1] > cell[:, 2] - 10)).mean()
                ch = "T" if green > 0.45 else "#"
            else:
                ch = "."
            line += ch
        rows.append(line)
    return rows, (lay.width, lay.height)


_TS = {}


def _behaviour(gba, lay, meta):
    key = (lay.primary, lay.secondary)
    if key not in _TS:
        _TS[key] = (gba.load_tileset_by_header(lay.primary), gba.load_tileset_by_header(lay.secondary))
    p, s = _TS[key]
    if meta < p.n_metatiles and meta < 512:
        return p.behaviour(meta)
    return s.behaviour(meta - 512) if meta - 512 < s.n_metatiles else 0


def _trainer_names():
    import csv
    out = {}
    for r in csv.DictReader(open(ROOT / "wiki/mapping/trainers.csv")):
        out[r["emerald_name"].upper()] = r["sw_name"]
    return out


def events(map_name):
    """Doors, people, signs and connections of a vanilla map, in blockout terms."""
    mj = map_json(map_name)
    names = _trainer_names()
    people, items = [], []
    for o in mj.get("object_events") or []:
        gfx = o["graphics_id"].replace("OBJ_EVENT_GFX_", "")
        script = (o.get("script") or "").split("_EventScript_")[-1]
        if gfx == "ITEM_BALL":
            items.append({"name": "Item", "at": [o["x"], o["y"]], "role": "item"})
            continue
        if o.get("trainer_type", "TRAINER_TYPE_NONE") != "TRAINER_TYPE_NONE":
            base = re.sub(r"\d+$", "", script).upper()
            sw = names.get(base)
            people.append({"name": f"Trainer {sw.title() if sw else script}", "at": [o["x"], o["y"]], "role": "trainer"})
        else:
            if "BerryTree" in script:
                items.append({"name": "Berry tree", "at": [o["x"], o["y"]], "role": "berry"})
                continue
            label = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", script) if script and script != "0" else gfx.title().replace("_", " ")
            people.append({"name": label, "at": [o["x"], o["y"]], "role": "npc"})
    return {
        "warps": [{"at": [w["x"], w["y"]], "to": w["dest_map"]} for w in mj.get("warp_events") or []],
        "people": people + items,
        "signs": [{"name": "Sign", "at": [b["x"], b["y"]]} for b in mj.get("bg_events") or [] if b.get("type") == "sign"],
        "connections": [{"edge": c["direction"], "to": c["map"], "offset": int(c["offset"])}
                        for c in mj.get("connections") or []],
    }


def world_positions():
    """Vanilla overworld position (cells) of every map reachable by connections, per connected group."""
    import glob as _g
    sizes, conns = {}, {}
    lays = _gba().layouts()
    for f in _g.glob(str(GAME / "data/maps/*/map.json")):
        mj = json.loads(Path(f).read_text())
        name = Path(f).parent.name
        if not mj.get("connections"):
            continue
        lay = lays.get(mj["layout"])
        if lay is None:
            continue
        sizes[name] = (lay.width, lay.height)
        conns[name] = mj["connections"]
    const_to_name = {}
    for f in _g.glob(str(GAME / "data/maps/*/map.json")):
        mj = json.loads(Path(f).read_text())
        const_to_name[mj["id"]] = Path(f).parent.name
    pos = {}
    groups = []
    for start in ["LittlerootTown"] + sorted(sizes):
        if start in pos:
            continue
        pos[start] = (0, 0)
        groups.append([start])
        todo = [start]
        while todo:
            a = todo.pop()
            ax, ay = pos[a]
            aw, ah = sizes[a]
            for c in conns.get(a, []):
                b = const_to_name.get(c["map"])
                if b is None or b in pos or b not in sizes:
                    continue
                bw, bh = sizes[b]
                o = int(c["offset"])
                d = c["direction"]
                if d == "up":
                    pos[b] = (ax + o, ay - bh)
                elif d == "down":
                    pos[b] = (ax + o, ay + ah)
                elif d == "left":
                    pos[b] = (ax - bw, ay + o)
                elif d == "right":
                    pos[b] = (ax + aw, ay + o)
                else:
                    continue
                todo.append(b)
                groups[-1].append(b)
    # the main continent keeps its coordinates; every other connected group (islands, the frontier)
    # goes in a row below it, normalised to start at its own top-left
    def box(g):
        return (min(pos[n][0] for n in g), min(pos[n][1] for n in g),
                max(pos[n][0] + sizes[n][0] for n in g), max(pos[n][1] + sizes[n][1] for n in g))
    mx0, my0, mx1, my1 = box(groups[0])
    shift = {n: (pos[n][0] - mx0, pos[n][1] - my0) for n in groups[0]}
    cx, cy = 0, my1 - my0 + 20
    for g in groups[1:]:
        x0, y0, x1, y1 = box(g)
        for n in g:
            shift[n] = (pos[n][0] - x0 + cx, pos[n][1] - y0 + cy)
        cx += x1 - x0 + 10
    return shift, const_to_name


def render(map_name):
    gba = _gba()
    lay = gba.layouts()[map_json(map_name)["layout"]]
    return gba.render_layout(lay).convert("RGB")


def vanilla_links():
    """Links that are not doors or map edges: dive and emerge connections from each map.json, and
    `warp...` commands in each map's own scripts.inc (ferries, cable cars, facility rooms).
    Returns (from_map, to_map, via) with vanilla map folder names."""
    import glob as _g
    import re as _re
    const_to_name, out = {}, []
    for f in _g.glob(str(GAME / "data/maps/*/map.json")):
        const_to_name[json.loads(Path(f).read_text())["id"]] = Path(f).parent.name
    for f in _g.glob(str(GAME / "data/maps/*/map.json")):
        mj = json.loads(Path(f).read_text())
        name = Path(f).parent.name
        for c in mj.get("connections") or []:
            if c["direction"] in ("dive", "emerge") and c["map"] in const_to_name:
                out.append((name, const_to_name[c["map"]], c["direction"]))
        sc = Path(f).parent / "scripts.inc"
        if sc.exists():
            for m in sorted(set(_re.findall(r"^\s*warp\w*\s+(MAP_[A-Z0-9_]+)", sc.read_text(), _re.M))):
                if m in const_to_name and const_to_name[m] != name:
                    out.append((name, const_to_name[m], "script"))
    return out

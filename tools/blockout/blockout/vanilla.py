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


def terrain_grid(map_name):
    """Rows of terrain chars for a vanilla map."""
    gba = _gba()
    mj = map_json(map_name)
    lay = gba.layouts()[mj["layout"]]
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
                ch = "x"
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


def events(map_name):
    """Doors, people, signs and connections of a vanilla map, in blockout terms."""
    mj = map_json(map_name)
    return {
        "warps": [{"at": [w["x"], w["y"]], "to": w["dest_map"]} for w in mj.get("warp_events") or []],
        "people": [{"at": [o["x"], o["y"]], "gfx": o["graphics_id"].replace("OBJ_EVENT_GFX_", "")}
                   for o in mj.get("object_events") or []],
        "signs": [{"at": [b["x"], b["y"]], "type": b.get("type")} for b in mj.get("bg_events") or []],
        "triggers": [{"at": [t["x"], t["y"]]} for t in mj.get("coord_events") or []],
        "connections": [{"edge": c["direction"], "to": c["map"], "offset": c["offset"]} for c in mj.get("connections") or []],
    }


def render(map_name):
    gba = _gba()
    lay = gba.layouts()[map_json(map_name)["layout"]]
    return gba.render_layout(lay).convert("RGB")

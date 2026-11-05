"""Write the ported world into ../game: layouts, per-area tilesets, map headers, warps and connections.

Every run starts from the vanilla snapshot (base.py), so it can run again and gives the same files. Areas
outside the scope keep their vanilla maps; a warp or connection into a new area outside the scope is left out.

What it writes, per area in scope:
  - its layout (`data/layouts/<Layout>/map.bin`, `border.bin`): rewritten in place when the vanilla layout is
    the map's own, a new `LAYOUT_SW_<ID>` when the vanilla layout is shared with other maps or the area is new.
  - its tileset, when it needs new metatiles: `data/tilesets/secondary/sw/<area-id>/`, declared in
    `src/data/tilesets/sw_*.h` (included at the end of graphics.h, metatiles.h and headers.h).
  - its map (`data/maps/<Map>/map.json`): warps and connections from the wiki; new maps in gMapGroup_StarWars
    with an empty `scripts.inc` included from `data/event_scripts.s`.
Events (people, signs, triggers) are written by events.py.
"""
import json
import re
from collections import Counter, defaultdict

import numpy as np

from . import base as B, model as M, terrain as TR, pieces as PC, tiles as TL, warps as W

LAYOUTS_JSON = "data/layouts/layouts.json"
GROUPS_JSON = "data/maps/map_groups.json"
SW_H = {"graphics.h": "sw_graphics.h", "metatiles.h": "sw_metatiles.h", "headers.h": "sw_headers.h"}


def map_type(area):
    return {"interior": "MAP_TYPE_INDOOR", "dungeon": "MAP_TYPE_UNDERGROUND", "town": "MAP_TYPE_TOWN"}.get(
        area.kind, "MAP_TYPE_ROUTE")


class World:
    """Everything the port computes before it writes."""

    def __init__(self, scope=None, exclude=()):
        self.V = B.use_base_for_tools()
        self.areas = M.classify(M.load_areas(), self.V)
        self.align_notes = PC.align_doors(self.areas)
        self.scope = {a for a, x in self.areas.items() if (scope is None or x.planet in scope or a in scope) and a not in exclude}
        self.warps, self.warp_problems = W.build_warps(self.areas)
        self.connections, self.conn_problems = W.build_connections(self.areas)
        self.base_maps = {}
        layouts = B.base_json(LAYOUTS_JSON)["layouts"]
        self.base_layouts = {l["id"]: l for l in layouts if l}
        users = Counter()
        for a in self.areas.values():
            if not a.new:
                users[B.base_map(a.replaces)["layout"]] += 1
        import glob
        users = Counter(json.load(open(p))["layout"] for p in glob.glob(str(B.BASE_GAME / "data/maps/*/map.json")))
        self.layout_users = users
        self.by_const = {a.map_const: a for a in self.areas.values()}
        self.results = {}
        from . import events as E
        self.people_rows = E.people_rows()
        from . import lanes as L
        self.lanes = L.Lanes(self)

    def installed(self, area_id):
        """Whether the area exists in the game after this run (vanilla maps always do)."""
        a = self.areas[area_id]
        return not a.new or area_id in self.scope

    # ------------------------------------------------------------------ terrain and tilesets
    def build_area(self, a, foreign=()):
        from tilegen import gba
        C = TR.build(a)
        pieces = PC.add_pieces(C)
        if not a.new:
            # metatiles only a script-swapped layout of this map uses (layout_variants) keep their tiles
            C.extra_live = {int(v) & 0x3FF for lid in layout_variants().get(a.replaces, ())
                            for v in variant_cells(lid).ravel()}
        out = None
        if C.syms or foreign:
            P = gba.load_tileset_by_header(C.prim)
            S = gba.load_tileset_by_header(C.sec)
            mode = "compact" if a.new else "pinned"
            out = TL.Builder(C, P, S, mode, foreign).build()
            if out["n_approx"]:
                C.notes.append(f"{out['n_approx']} tiles of a neighbour's edge drawn in the nearest palette")
            cells = out["cells"]
        else:
            cells = C.meta.astype(np.uint16)
        raw = (cells.astype(np.uint32) & 0x3FF) | (C.coll.astype(np.uint32) << 10) | (C.elev.astype(np.uint32) << 12)
        piece_cells = {(x, y) for p in pieces for y in range(p["y"], p["y"] + p["h"]) for x in range(p["x"], p["x"] + p["w"])}
        r = dict(area=a, C=C, pieces=pieces, tileset=out, raw=raw.astype(np.uint16), piece_cells=piece_cells)
        self.results[a.id] = r
        return r

    def layout_for(self, a, r):
        """(layout dict, folder name, is new layout) or None when the vanilla layout stays as it is."""
        sec = f"gTileset_Sw{M.camel(a.id)}" if r["tileset"] else r["C"].sec
        prim = r["C"].prim
        if not a.new:
            lid = B.base_map(a.replaces)["layout"]
            bl = self.base_layouts[lid]
            vraw = r["C"].vanilla_raw
            same = (vraw is not None and vraw.shape == r["raw"].shape and np.array_equal(vraw, r["raw"])
                    and sec == bl["secondary_tileset"] and prim == bl["primary_tileset"])
            if same:
                return None
            if self.layout_users[lid] == 1:
                folder = bl["blockdata_filepath"].split("/")[2]
                lay = dict(bl, width=a.w, height=a.h, primary_tileset=prim, secondary_tileset=sec)
                return lay, folder, False
        name = f"Sw{M.camel(a.id)}"
        lay = {"id": f"LAYOUT_SW_{a.id.upper().replace('-', '_')}", "name": f"{name}_Layout", "width": a.w,
               "height": a.h, "primary_tileset": prim, "secondary_tileset": sec,
               "border_filepath": f"data/layouts/{name}/border.bin",
               "blockdata_filepath": f"data/layouts/{name}/map.bin"}
        return lay, name, True

    def border_for(self, a, r):
        C = r["C"]
        out = r["tileset"]
        if not a.new and a.mode != "redraw":
            lid = B.base_map(a.replaces)["layout"]
            border = np.frombuffer((B.BASE_GAME / self.base_layouts[lid]["border_filepath"]).read_bytes(), "<u2")
            mids = [int(v) & 0x3FF for v in border]
            if out is None or all(m < TL.N_PRIM_META + len(out["metatiles"]) for m in mids):
                return border.astype(np.uint16).tobytes()
        # a redrawn or new map: what lies beyond its edge is the inside of its own border mass (the most common
        # blocked metatile with blocked cells all round), else the most common blocked metatile on the edge
        cells = r["raw"] & 0x3FF
        coll = C.coll
        inner = [(y, x) for y in range(1, a.h - 1) for x in range(1, a.w - 1)
                 if all(coll[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
                 and (x, y) not in r["piece_cells"]]
        c = Counter(int(cells[y, x]) for y, x in inner)
        if not c and a.kind != "interior":
            # a thin border: the fill tile of its blocked terrain
            items = TR.autotile_items(a, C.prim, C.sec)
            c = Counter(mid for row in items for item, role, mid in row
                        if role == "fill" and mid is not None and item in ("cliff", "wall", "tree")
                        and (mid < TL.N_PRIM_META or not a.new))     # a new area renumbers secondary ids
        if not c:
            edge = [(y, x) for y in range(a.h) for x in range(a.w) if y in (0, a.h - 1) or x in (0, a.w - 1)]
            c = Counter(int(cells[y, x]) for y, x in edge if coll[y, x])
        if not c:
            c = Counter(int(v) for v in cells.ravel())
        m = c.most_common(1)[0][0] | (1 << 10)
        return np.array([m] * 4, "<u2").tobytes()

    # ------------------------------------------------------------------ maps
    def warp_events(self, a):
        out = []
        for w in self.warps[a.id]:
            if w.to and not self.installed(w.to):
                continue                    # a new area outside this run
            elev = 0
            if w.vanilla is not None and (w.x, w.y) == (w.vanilla["x"], w.vanilla["y"]):
                elev = w.vanilla["elevation"]
            dest_id = w.dest_id
            if w.to and not self.areas[w.to].new and w.to not in self.scope:
                # a vanilla map outside this run keeps its vanilla warps only
                n = len(B.base_map(self.areas[w.to].replaces).get("warp_events") or [])
                if int(dest_id) >= n:
                    dest_id = "0"
            out.append({"x": w.x, "y": w.y, "elevation": elev, "dest_map": w.dest_map, "dest_warp_id": str(dest_id)})
        return out

    def connections_for(self, a):
        out = []
        for c in self.connections[a.id]:
            b = self.by_const.get(c["map"])
            if b is not None and not self.installed(b.id):
                continue
            if b is not None and b.id not in self.scope and c["direction"] not in ("dive", "emerge"):
                # the other side is still vanilla: only a vanilla connection both sides agree on
                vc = B.base_map(b.replaces).get("connections") or []
                opp = {"up": "down", "down": "up", "left": "right", "right": "left"}[c["direction"]]
                if not any(x["map"] == a.map_const and x["direction"] == opp and int(x["offset"]) == -int(c["offset"])
                           for x in vc):
                    continue
            out.append(c)
        return out or None


_VARIANTS = {}


def layout_variants():
    """{map: [layout ids]}: the other layouts a map's script swaps in (`setmaplayoutindex`), such as Route 111
    without the Mirage Tower or the Sky Pillar floors once cracked."""
    if not _VARIANTS:
        for f in sorted((B.BASE_GAME / "data/maps").glob("*/scripts.inc")):
            own = B.base_map(f.parent.name)["layout"]
            ids = sorted(set(re.findall(r"setmaplayoutindex (LAYOUT_\w+)", f.read_text())) - {own})
            if ids:
                _VARIANTS[f.parent.name] = ids
    return _VARIANTS


def variant_cells(lid):
    l = {x["id"]: x for x in B.base_json(LAYOUTS_JSON)["layouts"] if x}[lid]
    raw = np.frombuffer((B.BASE_GAME / l["blockdata_filepath"]).read_bytes(), "<u2")
    return raw[:l["height"] * l["width"]].reshape(l["height"], l["width"])     # some vanilla map.bin files carry a spare cell


def write_variants(world, a, r, lay, layouts):
    """A ported map's script-swapped layouts: the port's cells, with the cells the variant changes from the
    vanilla map taken from the variant where the port left that cell vanilla; same tilesets as the map."""
    notes = []
    vmain = r["C"].vanilla_raw
    if vmain is None:
        lid = B.base_map(a.replaces)["layout"]
        vmain = variant_cells(lid)
    for vid in layout_variants().get(a.replaces, ()):
        vv = variant_cells(vid)
        out = r["raw"].copy()
        if vv.shape == out.shape and vmain.shape == out.shape:
            take = (vv != vmain) & (out == vmain)
            out[take] = vv[take]
            if ((vv != vmain) & ~take).any():
                notes.append(f"{vid}: {int(((vv != vmain) & ~take).sum())} cells the variant changes are redrawn by the port")
        else:
            notes.append(f"{vid}: the map was resized, so the variant is the ported map unchanged")
        for i, x in enumerate(layouts["layouts"]):
            if x and x["id"] == vid:
                layouts["layouts"][i] = dict(x, width=a.w, height=a.h, primary_tileset=lay["primary_tileset"],
                                             secondary_tileset=lay["secondary_tileset"])
                B.write_bytes(B.GAME / x["blockdata_filepath"], out.astype("<u2").tobytes())
                B.write_bytes(B.GAME / x["border_filepath"], world.border_for(a, r))
    return notes


def parent_of(world, a, seen=None):
    """The nearest vanilla map a new area is reached from (for its music and map section)."""
    seen = seen or set()
    seen.add(a.id)
    for w in world.warps[a.id]:
        if w.to and w.to in world.areas and w.to not in seen:
            b = world.areas[w.to]
            if not b.new:
                return b
            p = parent_of(world, b, seen)
            if p:
                return p
    for e in a.exits:
        b = world.areas.get(e.get("to"))
        if b and b.id not in seen:
            if not b.new:
                return b
            p = parent_of(world, b, seen)
            if p:
                return p
    return None


def music_overrides():
    """Map music the wiki sets by hand: the `maps` column of mapping/music.csv (a per-planet split of a song
    Emerald shares, or the song a new area plays). Keyed by vanilla map folder, or `map:<area>` for a new area;
    the value is the song's constant in ../game (the Emerald id for a hot-swap, the new id for a net-new song)."""
    import csv
    songs = {r["asset_id"]: r for r in csv.DictReader(open(B.DATABASE / "music.csv", encoding="utf-8"))}
    folders = {e["id"]: e["source_file"].split("/")[2] for e in csv.DictReader(open(B.DATABASE / "entities.csv",
               encoding="utf-8")) if e["entity_type"] == "map" and e["source_file"].startswith("data/maps/")}
    out = {}
    for r in csv.DictReader(open(B.MAPPING / "music.csv", encoding="utf-8")):
        s = songs.get(r["asset_id"])
        if not s or not r["maps"]:
            continue
        const = s["emerald_constant"] if s["swap_kind"] == "HOTSWAP" else s["sw_constant"]
        for m in r["maps"].split("|"):
            out[folders.get(m, m)] = const
    return out


def new_map_json(world, a):
    p = parent_of(world, a)
    pm = B.base_map(p.replaces) if p else {}
    indoor = a.kind == "interior"
    return {
        "id": a.map_const,
        "name": a.map_name,
        "layout": f"LAYOUT_SW_{a.id.upper().replace('-', '_')}",
        "music": pm.get("music", "MUS_NONE"),
        "region_map_section": pm.get("region_map_section", "MAPSEC_NONE"),
        "requires_flash": False,
        "weather": "WEATHER_NONE" if indoor or a.kind == "dungeon" else pm.get("weather", "WEATHER_SUNNY"),
        "map_type": map_type(a),
        "allow_cycling": not indoor,
        "allow_escaping": a.kind == "dungeon",
        "allow_running": True,
        "show_map_name": a.kind != "interior",
        "battle_scene": "MAP_BATTLE_SCENE_NORMAL",
        "connections": None,
        "object_events": [],
        "warp_events": [],
        "coord_events": [],
        "bg_events": [],
    }


def write_tileset_c(world, written):
    """src/data/tilesets/sw_*.h for every per-area tileset, and their includes."""
    g, m, h = [], [], []
    for aid in sorted(written):
        r = world.results[aid]
        out = r["tileset"]
        n = M.camel(aid)
        d = f"data/tilesets/secondary/sw/{aid}"
        g.append(f'const u32 gTilesetTiles_Sw{n}[] = INCGFX_U32("{d}/tiles.png", ".4bpp.lz", '
                 f'"-num_tiles {len(out["tiles"])} -Wnum_tiles");\n\nconst u16 gTilesetPalettes_Sw{n}[][16] =\n{{\n'
                 + "".join(f'\tINCGFX_U16("{d}/palettes/{i:02d}.pal", ".gbapal"),\n' for i in range(16)) + "};\n")
        m.append(f'const u16 gMetatiles_Sw{n}[] = INCBIN_U16("{d}/metatiles.bin");\n'
                 f'const u16 gMetatileAttributes_Sw{n}[] = INCBIN_U16("{d}/metatile_attributes.bin");\n')
        h.append(f"const struct Tileset gTileset_Sw{n} =\n{{\n    .isCompressed = TRUE,\n    .isSecondary = TRUE,\n"
                 f"    .tiles = gTilesetTiles_Sw{n},\n    .palettes = gTilesetPalettes_Sw{n},\n"
                 f"    .metatiles = gMetatiles_Sw{n},\n    .metatileAttributes = gMetatileAttributes_Sw{n},\n"
                 f"    .callback = {out['callback']},\n}};\n")
    head = "// Generated by wiki/tools/world_port (the ported world's per-area tilesets). Do not edit.\n\n"
    base = B.GAME / "src/data/tilesets"
    B.write_text(base / "sw_graphics.h", head + "\n".join(g))
    B.write_text(base / "sw_metatiles.h", head + "\n".join(m))
    B.write_text(base / "sw_headers.h", head + "\n".join(h))
    for f, inc in SW_H.items():
        p = base / f
        t = p.read_text()
        line = f"#include \"{inc}\"\n"
        if line not in t:
            p.write_text(t.rstrip("\n") + "\n\n" + line)


def port(scope=None, exclude=(), log=print, rounds=4):
    """Install, then fix the map seams: add the neighbours' edge metatiles each map is missing and install
    again until none is missing, then write the remap table and check every seam (seams.py)."""
    from . import seams as SM
    foreign = {}
    for _ in range(rounds):
        world, report = install(scope, exclude, foreign={k: list(v.values()) for k, v in foreign.items()})
        seams = SM.Seams(world, foreign)
        if not seams.missing:
            break
        for aid, defs in seams.missing.items():
            foreign.setdefault(aid, {}).update(defs)
    else:
        raise RuntimeError(f"map seams still missing metatiles after {rounds} rounds: {dict(seams.missing)}")
    SM.write_header(seams)
    world.seams = seams
    world.seam_problems = seams.check()
    return world, report


def install(scope=None, exclude=(), log=print, foreign=None):
    from . import events as E, towns as T
    foreign = foreign or {}
    world = World(scope, exclude)
    problems = []
    B.ensure_base()
    layouts = B.base_json(LAYOUTS_JSON)
    groups = B.base_json(GROUPS_JSON)
    new_layouts, tilesets, report = [], [], []
    maps_out = {}
    for aid in sorted(world.scope):
        a = world.areas[aid]
        r = world.build_area(a, foreign.get(aid, ()))
        lay = world.layout_for(a, r)
        if r["tileset"]:
            TL.write_tileset(r["tileset"], B.GAME / f"data/tilesets/secondary/sw/{aid}")
            tilesets.append(aid)
        layout_id = None
        if lay:
            l, folder, is_new = lay
            B.write_bytes(B.GAME / "data/layouts" / folder / "map.bin", r["raw"].astype("<u2").tobytes())
            B.write_bytes(B.GAME / "data/layouts" / folder / "border.bin", world.border_for(a, r))
            if is_new:
                new_layouts.append(l)
            else:
                for i, x in enumerate(layouts["layouts"]):
                    if x and x["id"] == l["id"]:
                        layouts["layouts"][i] = l
            layout_id = l["id"]
            if not a.new and a.replaces in layout_variants():
                r["C"].notes += write_variants(world, a, r, l, layouts)
        mj = new_map_json(world, a) if a.new else json.loads(json.dumps(B.base_map(a.replaces)))
        if layout_id:
            mj["layout"] = layout_id
        mj["warp_events"] = world.warp_events(a)
        mj["connections"] = world.connections_for(a)
        if a.new or a.mode in ("vanilla", "hybrid"):
            problems += E.events(world, a, r, mj)
        else:
            problems += T.town_events(world, a, r, mj)
        maps_out[aid] = mj
        report.append((aid, a.mode, len(r["C"].syms), r["tileset"]["n_new_meta"] if r["tileset"] else 0,
                       "; ".join(r["C"].notes)))
    # vanilla maps outside the run: drop connections into the run that the run no longer has
    for aid, a in world.areas.items():
        if aid in world.scope or a.new:
            continue
        vm = B.base_map(a.replaces)
        cons = vm.get("connections") or []
        keep = []
        for c in cons:
            b = world.by_const.get(c["map"])
            if b is not None and b.id in world.scope and c["direction"] not in ("dive", "emerge"):
                opp = {"up": "down", "down": "up", "left": "right", "right": "left"}[c["direction"]]
                back = maps_out[b.id].get("connections") or []
                if not any(x["map"] == a.map_const and x["direction"] == opp and int(x["offset"]) == -int(c["offset"])
                           for x in back):
                    continue
            keep.append(c)
        if len(keep) != len(cons):
            mj = json.loads(json.dumps(vm))
            mj["connections"] = keep or None
            maps_out[aid] = mj
    layouts["layouts"] += new_layouts
    B.write_json(B.GAME / LAYOUTS_JSON, layouts)
    # new maps: their group, folder and script file
    new_maps = [world.areas[a].map_name for a in sorted(world.scope) if world.areas[a].new]
    if new_maps:
        groups["group_order"].append(M.NEW_GROUP)
        groups[M.NEW_GROUP] = new_maps
    B.write_json(B.GAME / GROUPS_JSON, groups)
    music = music_overrides()
    for aid, mj in maps_out.items():
        a = world.areas[aid]
        mj["music"] = music.get(f"map:{a.id}" if a.new else a.replaces, mj.get("music"))
        B.write_json(B.GAME / "data/maps" / a.map_name / "map.json", mj)
        if a.new:
            sp = B.GAME / "data/maps" / a.map_name / "scripts.inc"
            if not sp.exists():
                sp.write_text(f"{a.map_name}_MapScripts::\n\t.byte 0\n")
    write_event_script_includes(new_maps)
    write_tileset_c(world, tilesets)
    T.heal_locations(world)
    world.event_problems = problems
    return world, report


def write_event_script_includes(new_maps):
    p = B.GAME / "data/event_scripts.s"
    t = p.read_text()
    begin, end = "@ world_port: new maps (begin)\n", "@ world_port: new maps (end)\n"
    block = begin + "".join(f'\t.include "data/maps/{m}/scripts.inc"\n' for m in new_maps) + end
    if begin in t:
        t = t[:t.index(begin)] + block + t[t.index(end) + len(end):]
    else:
        anchor = '\t.include "data/maps/LittlerootTown/scripts.inc"\n'
        i = t.index(anchor)
        # after the last vanilla map include
        last = max(m.end() for m in re.finditer(r'\t\.include "data/maps/[^"]+/scripts\.inc"\n', t))
        t = t[:last] + block + t[last:]
    B.write_text(p, t)

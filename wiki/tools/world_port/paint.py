"""Paint the ported world's terrain in its planet's colours (owner approved look A, 2026-11-05).

Runs after the install. Pixels and metatiles are untouched; only palettes change (tile-generator's
`tilegen/paint.py`: one world palette of material ramps, each planet's look picks from it; buildings stay grey).

- Each planet gets its own painted copy of every vanilla tileset its outdoor maps use: a header
  `gTileset_<Name>_<Planet>` that shares the vanilla tiles, metatiles and animation and points at painted
  palettes in `data/tilesets/sw_paint/<planet>/<name>/` (`src/data/tilesets/sw_paint.h`, included by
  graphics.h and headers.h). Their layouts in `layouts.json` point at the copies.
- A per-area tileset (`secondary/sw/<area>/`) has its palettes painted in place.
- A bank that draws a net-new item (the Dune Sea is the sea, mud the sand...), a grey vanilla ground or a
  walkway takes that item's colours (`paint.look(planet, "A", item)`); the banks are found from the cells.
Interiors are not painted.
"""
import json
import re
from collections import defaultdict

import numpy as np

from . import base as B, model as M, terrain as TR

LOOK = "A"
OUT = "data/tilesets/sw_paint"
HDR = "src/data/tilesets/sw_paint.h"


def _pt():
    TR._tilegen()
    from tilegen import paint as PT, gba
    return PT, gba


def slug(planet):
    return planet.lower().replace(" ", "-")


def camel(s):
    return "".join(w.capitalize() for w in re.split(r"[^A-Za-z0-9]+", s) if w)


def vanilla_headers():
    """gTileset_X -> {tiles, palettes, metatiles, metatileAttributes, callback, isSecondary} from headers.h."""
    out = {}
    text = (B.GAME / "src/data/tilesets/headers.h").read_text()
    for m in re.finditer(r"const struct Tileset (\w+) =\s*\{(.*?)\};", text, re.S):
        out[m.group(1)] = dict(re.findall(r"\.(\w+) = (\w+)", m.group(2)))
    return out


def palette_files():
    """gTilesetPalettes_X -> list of 16 .pal paths (from graphics.h)."""
    text = (B.GAME / "src/data/tilesets/graphics.h").read_text() + (B.GAME / "src/graphics.c").read_text()
    out = {}
    for m in re.finditer(r"const u16 (gTilesetPalettes_\w+)\[\]\[16\] =\s*\{(.*?)\};", text, re.S):
        out[m.group(1)] = re.findall(r'"([^"]+\.pal)"', m.group(2))
    return out


def item_cells(world, a):
    """(item, vanilla-pair metatile id) for the cells that need their own colours."""
    PT, gba = _pt()
    T, R, _ = TR._tilegen()
    C = cells_of(world, a)
    want = lambda n: PT.item_key(n) is not None
    if a.mode == "redraw":
        names = [[q[0] for q in row] for row in TR.autotile_items(a, C.prim, C.sec)]
    else:
        lay = TR.catalog()["A"][a.id]["layout"]
        names = [[T.kit_item(a.planet, n) for n in row] for row in T.LAYOUT_NAMES.get(lay.name, [])]
    out = []
    from .tiles import ph_source
    for y, row in enumerate(names):
        for x, n in enumerate(row):
            if not want(n) or y >= C.meta.shape[0] or x >= C.meta.shape[1]:
                continue
            v = int(C.meta[y, x])
            if v >= 0:
                out.append((n, v))
            else:
                s = C.syms[-1 - v]
                if s[0] == "ph":
                    m = ph_source(C, s[2], s[3])
                    if m is not None:
                        out.append((n, m))
    return out


def cells_of(world, a):
    r = getattr(world, "results", {}).get(a.id)
    if r is None:
        r = world.results[a.id] = {"C": TR.build(a)}
    return r["C"]


def _keep(aid, f):
    return B.CACHE / "paint" / aid / f.name


def unpainted(aid, f):
    """The area tileset's palette as the install wrote it: painting again starts from that, not from the paint."""
    k = _keep(aid, f)
    done = k.with_suffix(".painted")
    if k.exists() and done.exists() and done.read_bytes() == f.read_bytes():
        return __import__("tilegen.gba", fromlist=["x"]).read_pal(k)
    k.parent.mkdir(parents=True, exist_ok=True)
    k.write_bytes(f.read_bytes())
    return __import__("tilegen.gba", fromlist=["x"]).read_pal(f)


def remember(aid, f):
    _keep(aid, f).with_suffix(".painted").write_bytes(f.read_bytes())


def banks_of(p, mid):
    """Palette banks a vanilla-pair metatile draws with."""
    ts = p.primary if mid < 512 else p.secondary
    ent = ts.metatiles[mid if mid < 512 else mid - 512].reshape(-1)
    return {int(e) >> 12 for e in ent}


def paint(world, log=print):
    PT, gba = _pt()
    T, R, _ = TR._tilegen()
    layouts = json.loads((B.GAME / "data/layouts/layouts.json").read_text())
    by_id = {l["id"]: l for l in layouts["layouts"] if l}
    maps = {}
    for aid in world.scope:
        a = world.areas[aid]
        if a.kind == "interior" or not a.planet:
            continue
        mj = json.loads((B.GAME / "data/maps" / a.map_name / "map.json").read_text())
        if mj["layout"] in by_id:
            maps[aid] = by_id[mj["layout"]]
    # bank overrides: per (planet, vanilla tileset symbol) and per area tileset
    over = defaultdict(dict)        # (planet, tileset) -> bank -> assign updates
    area_over = defaultdict(dict)   # area id -> bank -> assign updates
    for aid in maps:
        a = world.areas[aid]
        planet = a.planet.upper()
        base = PT.look(planet, LOOK)
        C = cells_of(world, a)
        p = T.pair(C.prim, C.sec)
        sw_sec = maps[aid]["secondary_tileset"].startswith("gTileset_Sw")
        for item, mid in item_cells(world, a):
            diff = {k: v for k, v in PT.look(planet, LOOK, item).items() if base.get(k) != v}
            if not diff:
                continue
            for b in banks_of(p, mid):
                if b < 6 and item in PT.ITEM_ALL:
                    continue        # a walkway in a shared General bank: the bank keeps the planet's look
                if b < 6:
                    over[(planet, C.prim)].setdefault(b, {}).update(diff)
                elif sw_sec:
                    area_over[aid].setdefault(b, {}).update(diff)
                else:
                    over[(planet, C.sec)].setdefault(b, {}).update(diff)
    hdrs, pfiles = vanilla_headers(), palette_files()
    made = {}       # (planet, symbol) -> new symbol
    g_out, h_out = [], []

    def painted_pal(pal, planet, bank, upd):
        assign = dict(PT.look(planet, LOOK))
        assign.update(upd or {})
        return PT.paint_bank(pal, assign)

    def copy_of(planet, sym):
        key = (planet, sym)
        if key in made:
            return made[key]
        h = hdrs[sym]
        name = sym[len("gTileset_"):]
        new = f"gTileset_{name}_{camel(planet)}"
        folder = f"{OUT}/{slug(planet)}/{name.lower()}"
        files = pfiles[h["palettes"]]
        secondary = h.get("isSecondary") == "TRUE"
        banks = range(6, 13) if secondary else range(0, 6)
        lines = []
        for i, f in enumerate(files):
            pal = gba.read_pal(B.GAME / f)
            if i in banks:
                pal = painted_pal(pal, planet, i, over[key].get(i))
            (B.GAME / folder).mkdir(parents=True, exist_ok=True)
            gba.write_pal(B.GAME / folder / f"{i:02d}.pal", pal)
            lines.append(f'\tINCGFX_U16("{folder}/{i:02d}.pal", ".gbapal"),\n')
        g_out.append(f"const u16 gTilesetPalettes_{name}_{camel(planet)}[][16] =\n{{\n" + "".join(lines) + "};\n")
        h_out.append(f"const struct Tileset {new} =\n{{\n    .isCompressed = {h['isCompressed']},\n"
                     f"    .isSecondary = {h['isSecondary']},\n    .tiles = {h['tiles']},\n"
                     f"    .palettes = gTilesetPalettes_{name}_{camel(planet)},\n    .metatiles = {h['metatiles']},\n"
                     f"    .metatileAttributes = {h['metatileAttributes']},\n    .callback = {h['callback']},\n}};\n")
        made[key] = new
        return new

    n_area = 0
    for aid, lay in sorted(maps.items()):
        planet = world.areas[aid].planet.upper()
        for k in ("primary_tileset", "secondary_tileset"):       # painted before: start from the vanilla one
            suf = "_" + camel(planet)
            if lay[k] not in hdrs and lay[k].endswith(suf) and lay[k][:-len(suf)] in hdrs:
                lay[k] = lay[k][:-len(suf)]
        if lay["primary_tileset"] in hdrs:
            lay["primary_tileset"] = copy_of(planet, lay["primary_tileset"])
        sec = lay["secondary_tileset"]
        if sec.startswith("gTileset_Sw"):
            folder = B.GAME / f"data/tilesets/secondary/sw/{aid}/palettes"
            for i in range(6, 13):
                f = folder / f"{i:02d}.pal"
                gba.write_pal(f, painted_pal(unpainted(aid, f), planet, i, area_over[aid].get(i)))
                remember(aid, f)
            n_area += 1
        elif sec in hdrs:
            lay["secondary_tileset"] = copy_of(planet, sec)
    head = "// Generated by wiki/tools/world_port/paint.py (each planet's painted terrain palettes). Do not edit.\n\n"
    (B.GAME / HDR).write_text(head + "#ifdef SW_PAINT_GRAPHICS\n" + "\n".join(g_out) + "#else\n" + "\n".join(h_out)
                              + "#endif\n")
    for f, line in (("graphics.h", '#define SW_PAINT_GRAPHICS\n#include "sw_paint.h"\n#undef SW_PAINT_GRAPHICS\n'),
                    ("headers.h", '#include "sw_paint.h"\n')):
        p = B.GAME / "src/data/tilesets" / f
        t = p.read_text()
        if "sw_paint.h" not in t:
            p.write_text(t.rstrip("\n") + "\n\n" + line)
    B.write_json(B.GAME / "data/layouts/layouts.json", layouts)
    log(f"painted: {len(maps)} maps, {len(made)} planet tileset copies, {n_area} area tilesets")
    return made

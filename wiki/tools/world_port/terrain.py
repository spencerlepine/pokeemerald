"""The cells of every area: which metatile each map cell shows, and its collision and elevation bits.

A cell's metatile is either a vanilla metatile of the area's tileset pair (an int, in pair space: below 512 the
primary, from 512 the secondary) or a new metatile, named by a symbol the tileset builder turns into a real one:

  ("ph", sheet, item, role)              a terrain role the pair has no tile for (terrain.csv row with no `use`):
                                         the pink placeholder over a flat grey fill, its own metatile per role.
  ("room", style, part, sub, flip)       a room-kit part of a new interior (rooms.csv), placeholder art.
  ("piece", key, cx, cy, under, door)    one cell of a building or prop render (`under` is the cell below it).

Bits follow vanilla: walkable ground is collision 0 elevation 3, water collision 0 elevation 1, everything
blocked (walls, cliffs, trees, ledges) collision 1 elevation 0. Levels (`=` platforms, `H` ladders) are walked
at ground height, as blockout's reach check assumes.
"""
import numpy as np

from . import base as B

WALK = set('.:"=H_')
LEDGES = {"v": "ledge-south", "^": "ledge-north", "<": "ledge-west", ">": "ledge-east"}
BLOCKED = set("#T|x")


def bits_for(ch):
    if ch in WALK:
        return 0, 3
    if ch == "~":
        return 0, 1
    return 1, 0          # blocked and ledges


class Cells:
    def __init__(self, area, prim, sec, h, w):
        self.area = area
        self.prim, self.sec = prim, sec
        self.meta = np.zeros((h, w), np.int64)     # >= 0 vanilla pair metatile, < 0: -(1 + index into syms)
        self.coll = np.zeros((h, w), np.uint8)
        self.elev = np.zeros((h, w), np.uint8)
        self.syms = []
        self._sym_index = {}
        self.vanilla_raw = None                      # the vanilla map.bin cells (vanilla and hybrid areas)
        self.notes = []

    def sym(self, s):
        if s not in self._sym_index:
            self._sym_index[s] = len(self.syms)
            self.syms.append(s)
        return -(1 + self._sym_index[s])

    def symbol(self, v):
        return self.syms[-v - 1] if v < 0 else None


def _tilegen():
    from tilegen import terrain as T, roles as R, gba
    return T, R, gba


_CAT = {}


def catalog():
    """tile-generator's terrain catalog of the vanilla snapshot (areas, stats), once."""
    if not _CAT:
        T, R, gba = _tilegen()
        A, items, stats, rows = T.catalog()
        _CAT.update(A={a["id"]: a for a in A}, Alist=A, stats=stats, rows=rows)
    return _CAT


def pair_of(area):
    T, R, gba = _tilegen()
    c = catalog()
    ar = dict(c["A"][area.id])
    if area.mode == "redraw":
        ar["same"] = False
    return T.pair_for(ar, c["Alist"])


def autotile_items(area, prim, sec):
    """Item and role of every cell of the area's grid, and the vanilla metatile for it (None: missing)."""
    T, R, gba = _tilegen()
    c = catalog()
    ar = c["A"][area.id]
    p = T.pair(prim, sec)
    names = T.grid_items(area.grid, prim, sec, ar["indoor"], area.kind)
    names = [[T.kit_item(area.planet, n) for n in row] for row in names]
    roles = R.roles(names)
    out = []
    for y, row in enumerate(names):
        line = []
        for x, item in enumerate(row):
            role = roles[y][x]
            mid = None if item in T.NEW_ITEMS else T.lookup(prim, sec, item, role, c["stats"], p)
            line.append((item, role, mid))
        out.append(line)
    return out


def sheet_for(area, item, prim, sec):
    T, R, gba = _tilegen()
    if item in T.NEW_ITEMS:
        return "sw-" + area.planet.lower().replace(" ", "-")
    p = T.pair(prim, sec)
    return p.secondary.name if p.secondary.name != "0" else p.primary.name


def vanilla_cells(area):
    """The vanilla layout's raw u16 cells (from the snapshot) and its tilegen layout."""
    T, R, gba = _tilegen()
    lay = catalog()["A"][area.id]["layout"]
    return lay.cells().astype(np.uint16), lay


def kit_cells(area):
    """tile-generator's planet-kit pass over a vanilla layout: (cells with MISSING / placeholder codes, names)."""
    T, R, gba = _tilegen()
    c = catalog()
    ar = c["A"][area.id]
    cells, needs = T.kit_layout(ar, c["stats"])
    return cells


def build(area):
    """The Cells of one area (terrain only; pieces are added by pieces.add_pieces)."""
    T, R, gba = _tilegen()
    prim, sec = pair_of(area)
    C = Cells(area, prim, sec, area.h, area.w)
    if area.mode in ("vanilla", "hybrid"):
        raw, lay = vanilla_cells(area)
        C.vanilla_raw = raw
        kit = kit_cells(area)
        names = None
        for y in range(area.h):
            for x in range(area.w):
                v = int(raw[y, x])
                C.coll[y, x] = (v >> 10) & 3
                C.elev[y, x] = v >> 12
                k = int(kit[y, x])
                if k == T.MISSING or k >= T.PH_BASE:
                    # a kit item the pair has no tile for (the Dune Sea, wroshyr trunks...): its own placeholder
                    if names is None:
                        names = [[T.kit_item(area.planet, n) for n in row] for row in T.LAYOUT_NAMES[lay.name]]
                        roles = R.roles(names)
                    item, role = names[y][x], roles[y][x]
                    C.meta[y, x] = C.sym(("ph", sheet_for(area, item, prim, sec), item, role))
                else:
                    C.meta[y, x] = k
        if area.mode == "hybrid":
            items = autotile_items(area, prim, sec)
            for (x, y) in sorted(area.changed):
                ch = area.grid[y][x]
                item, role, mid = items[y][x]
                C.meta[y, x] = mid if mid is not None else C.sym(("ph", sheet_for(area, item, prim, sec), item, role))
                C.coll[y, x], C.elev[y, x] = bits_for(ch)
        return C
    if area.kind == "interior" and area.new:
        return build_room(area, C)
    items = autotile_items(area, prim, sec)
    for y in range(area.h):
        for x in range(area.w):
            ch = area.grid[y][x]
            item, role, mid = items[y][x]
            C.meta[y, x] = mid if mid is not None else C.sym(("ph", sheet_for(area, item, prim, sec), item, role))
            C.coll[y, x], C.elev[y, x] = bits_for(ch)
    return C


def room_part(area, x, y):
    """The room-kit part for a cell of a new interior's grid (`|` wall, `_` floor)."""
    g = area.cell
    ch = g(x, y)
    if ch == "_":
        edge = x in (0, area.w - 1) or y in (0, area.h - 1)
        if edge:
            return "exit-mat", 0, False
        return "floor", 0, False
    fl = lambda xx, yy: g(xx, yy) == "_"
    if fl(x, y + 1):
        return "wall-back", 2, False
    if fl(x, y + 2) and g(x, y + 1) == "|":
        return "wall-back", 1, False
    if fl(x, y - 1):
        return "wall-front", 0, False
    if fl(x + 1, y):
        return "wall-side", 0, False
    if fl(x - 1, y):
        return "wall-side", 0, True
    if fl(x + 1, y + 1) or fl(x - 1, y + 1):
        return "corner-out", 0, fl(x - 1, y + 1)
    if fl(x + 1, y - 1) or fl(x - 1, y - 1):
        return "corner-front", 0, fl(x - 1, y - 1)
    if any(fl(x + dx, y + dy) for dx, dy in ((1, 2), (-1, 2))) or (g(x, y + 1) == "|" and g(x, y + 2) == "|" and y + 2 < area.h and any(fl(x + d, y + 2) for d in (-1, 0, 1))):
        return "wall-back", 1, False
    return "wall-back", 0, False


def build_room(area, C):
    style = (area.room.get("style") or "room:generic").split(":", 1)[-1]
    for y in range(area.h):
        for x in range(area.w):
            ch = area.grid[y][x]
            part, sub, flip = room_part(area, x, y)
            C.meta[y, x] = C.sym(("room", style, part, sub, flip, edge_dir(area, x, y) if part == "exit-mat" else ""))
            C.coll[y, x], C.elev[y, x] = bits_for(ch)
    return C


def edge_dir(area, x, y):
    if y == area.h - 1:
        return "south"
    if y == 0:
        return "north"
    if x == 0:
        return "west"
    return "east"

"""Map seams: what a map shows of its neighbour across a connection.

When the player stands near a map edge, the game shows the connected map's cells there (7 rows or columns of
them, 8 to the east), but draws them with the *current* map's tilesets. Vanilla maps that meet share their
tilesets, or keep their edges to metatiles both sets have. The ported world gives many areas their own
tileset, so a neighbour's metatile id can mean another picture, or another behaviour, on this side.

For every connection this finds the neighbour's metatile ids that land in the current map's view (the same
rows and columns `fieldmap.c` copies) and renders each one in both tileset pairs:

  same      the id looks and behaves the same on both sides: nothing to do.
  remap     another metatile of this map looks and behaves the same: the game swaps the id when it copies the
            neighbour's cells (`src/data/sw_seam_remap.h`, read by `fieldmap.c`).
  foreign   nothing here matches: the neighbour's metatile is added to this map's tileset (`Builder.foreign`),
            then remapped. Its palette goes to a slot with the same colours, or a spare slot; only when there
            is none are its colours matched to the nearest slot ("approx", reported).

After crossing, the game also redraws the whole view when the two maps' tilesets differ (`field_camera.c`).
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import base as B

MAP_OFFSET = 7
HEADER = "src/data/sw_seam_remap.h"


class GameState:
    """The maps, layouts and tilesets as written in ../game."""

    def __init__(self, game=B.GAME):
        B.use_base_for_tools()           # puts the tile-generator on the path
        from tilegen import gba
        self.gba = gba
        self.game = Path(game)
        self.layouts = {l["id"]: l for l in json.loads((self.game / "data/layouts/layouts.json").read_text())["layouts"] if l}
        self.maps = {}
        for p in sorted((self.game / "data/maps").glob("*/map.json")):
            j = json.loads(p.read_text())
            self.maps[j["id"]] = j
        self.folders = self._folders()
        self._ts, self._pairs, self._render, self._index, self._cells = {}, {}, {}, {}, {}

    def _folders(self):
        d = self.game / "src/data/tilesets"
        text = "".join(p.read_text() for p in sorted(d.glob("*.h"))) + (self.game / "src/graphics.c").read_text()
        tp = dict(re.findall(r"gTilesetTiles_(\w+)\[\] = INCGFX_U32\(\"(data/tilesets/[^\"]+)/tiles\.png\"", text))
        out = {}
        for m in re.finditer(r"const struct Tileset gTileset_(\w+) =\s*\{(.*?)\};", text, re.S):
            t = re.search(r"\.tiles = gTilesetTiles_(\w+)", m.group(2))
            if t and t.group(1) in tp:
                out["gTileset_" + m.group(1)] = self.game / tp[t.group(1)]
        return out

    def tileset(self, header):
        if header not in self._ts:
            f = self.folders[header]
            self._ts[header] = self.gba.Tileset.load(f, "/secondary/" in f.as_posix())
        return self._ts[header]

    def pair_of(self, map_const):
        l = self.layouts[self.maps[map_const]["layout"]]
        return l["primary_tileset"], l["secondary_tileset"]

    def pair(self, key):
        if key not in self._pairs:
            self._pairs[key] = self.gba.TilesetPair(self.tileset(key[0]), self.tileset(key[1]))
        return self._pairs[key]

    def cells(self, map_const):
        if map_const not in self._cells:
            l = self.layouts[self.maps[map_const]["layout"]]
            raw = np.frombuffer((self.game / l["blockdata_filepath"]).read_bytes(), "<u2")
            self._cells[map_const] = raw.reshape(l["height"], l["width"])
        return self._cells[map_const]

    def size(self, map_const):
        l = self.layouts[self.maps[map_const]["layout"]]
        return l["width"], l["height"]

    def look(self, key, mid):
        """(16x16 picture at GBA colour depth, attributes) of a metatile id in a tileset pair; None past the end."""
        k = (key, mid)
        if k not in self._render:
            p = self.pair(key)
            ts, local = p.metatile(mid)
            if local >= ts.n_metatiles:
                self._render[k] = None
            else:
                img = p.render_metatile(mid, backdrop=(0, 0, 0))
                self._render[k] = ((img[..., :3] >> 3).tobytes(), int(ts.attributes[local]))
        return self._render[k]

    def index(self, key):
        """{look: lowest metatile id} for every metatile of a tileset pair."""
        if key not in self._index:
            p = self.pair(key)
            d = {}
            ids = list(range(p.primary.n_metatiles)) + [512 + i for i in range(p.secondary.n_metatiles)]
            for m in ids:
                lk = self.look(key, m)
                if lk is not None:
                    d.setdefault(lk, m)
            self._index[key] = d
        return self._index[key]

    def foreign_def(self, key, mid):
        """A metatile of a tileset pair as Builder.foreign wants it: ([(pixels, colours, hf, vf, primary id)] x 8,
        attributes)."""
        p = self.pair(key)
        ts, local = p.metatile(mid)
        tiles, pals = p.tiles, p.palettes
        refs = []
        for e in ts.metatiles[local].reshape(-1):
            e = int(e)
            t, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
            pix = tiles[t] if t < len(tiles) else np.zeros((8, 8), np.uint8)
            refs.append((pix, [tuple(c) for c in pals[pal]], hf, vf, t if t < 512 else None))
        return refs, int(ts.attributes[local])


def band(state, a, b, conn):
    """The cells (x, y) of map b that fieldmap.c copies into map a's view for connection `conn` of a."""
    aw, ah = state.size(a)
    bw, bh = state.size(b)
    W, H = aw + 2 * MAP_OFFSET + 1, ah + 2 * MAP_OFFSET
    off, d = int(conn["offset"]), conn["direction"]
    out = []
    if d in ("up", "down"):
        x = off + MAP_OFFSET
        if x < 0:
            x2, x = -x, x + bw
            width, x = min(x, W), 0
        else:
            x2 = 0
            width = bw if x + bw < W else W - x
        rows = range(bh - MAP_OFFSET, bh) if d == "up" else range(0, MAP_OFFSET)
        out = [(x2 + i, yy) for yy in rows for i in range(max(width, 0))]
    else:
        y = off + MAP_OFFSET
        if y < 0:
            y2 = -y
            height = y + bh if y + bh < H else H
        else:
            y2 = 0
            height = bh if y + bh < H else H - y
        cols = range(bw - MAP_OFFSET, bw) if d == "left" else range(0, MAP_OFFSET + 1)
        out = [(xx, y2 + i) for xx in cols for i in range(max(height, 0))]
    return out


class Seams:
    """Every seam of the game as written, against the foreign metatiles the last install added."""

    def __init__(self, world, foreign, state=None):
        self.world, self.foreign = world, foreign
        self.state = state or GameState()
        self.remaps = {}                 # (map, neighbour) -> {neighbour id: id here}
        self.missing = defaultdict(dict)  # area id -> {look: foreign def}
        self.approx = []                 # (map, neighbour, id): drawn with the nearest colours
        self.errors = []                 # seams the game would read outside a map
        self.counts = defaultdict(int)
        self._run()

    def _foreign_ids(self, area_id):
        """{look in the neighbour: id here} for the foreign metatiles the last install added to an area."""
        r = self.world.results.get(area_id)
        out = (r["tileset"] if r else None) or {}
        ids = out.get("foreign_ids") or []
        return {k: ids[i] for i, k in enumerate(self.foreign.get(area_id, {}))} if ids else {}

    def _run(self):
        st = self.state
        by_const = self.world.by_const
        for a, mj in sorted(st.maps.items()):
            for conn in mj.get("connections") or []:
                if conn["direction"] in ("dive", "emerge"):
                    continue
                b = conn["map"]
                bw, bh = st.size(b)
                if bw < MAP_OFFSET + 1 or bh < MAP_OFFSET:
                    self.errors.append(f"{a} -> {b}: the neighbour is smaller than the view band ({bw}x{bh})")
                pa, pb = st.pair_of(a), st.pair_of(b)
                if pa[0] != pb[0]:
                    self.errors.append(f"{a} -> {b}: different primary tilesets ({pa[0]}, {pb[0]})")
                cells = st.cells(b)
                ids = sorted({int(cells[y, x]) & 0x3FF for x, y in band(st, a, b, conn)})
                area = by_const.get(a)
                fids = self._foreign_ids(area.id) if area else {}
                remap = {}
                for m in ids:
                    want = st.look(pb, m)
                    if want is None:
                        self.errors.append(f"{a} -> {b}: metatile {m} is past the end of {b}'s tileset")
                        continue
                    if st.look(pa, m) == want:
                        self.counts["same"] += 1
                        continue
                    hit = st.index(pa).get(want)
                    if hit is not None:
                        remap[m] = hit
                        self.counts["remap"] += 1
                    elif want in fids:
                        hit = fids[want] if fids[want] is not None else self.nearest(pa, want)
                        if hit is None:
                            self.errors.append(f"{a} -> {b}: metatile {m} has no room and no metatile behaves the same")
                            continue
                        remap[m] = hit
                        self.approx.append((a, b, m))
                        self.counts["approx" if fids[want] is not None else "nearest"] += 1
                    elif area is None:
                        self.errors.append(f"{a} -> {b}: metatile {m} has no match and {a} is not a wiki area")
                    else:
                        self.missing[area.id][want] = st.foreign_def(pb, m)
                        self.counts["missing"] += 1
                if remap:
                    self.remaps[(a, b)] = dict(sorted(remap.items()))

    def nearest(self, key, want):
        """The metatile of a tileset pair with the same attributes that looks closest (when there is no room for
        a neighbour's own)."""
        pic = np.frombuffer(want[0], np.uint8).astype(int)
        best = None
        for lk, m in self.state.index(key).items():
            if lk[1] != want[1]:
                continue
            d = np.abs(np.frombuffer(lk[0], np.uint8).astype(int) - pic).sum()
            if best is None or d < best[0]:
                best = (d, m)
        return best[1] if best else None

    def check(self):
        """Every band cell of every seam, after the remap, against the neighbour's own picture. Returns problems."""
        st = self.state
        out = list(self.errors)
        approx = set(self.approx)
        for a, mj in sorted(st.maps.items()):
            for conn in mj.get("connections") or []:
                if conn["direction"] in ("dive", "emerge"):
                    continue
                b = conn["map"]
                pa, pb = st.pair_of(a), st.pair_of(b)
                remap = self.remaps.get((a, b), {})
                cells = st.cells(b)
                for m in sorted({int(cells[y, x]) & 0x3FF for x, y in band(st, a, b, conn)}):
                    want, got = st.look(pb, m), st.look(pa, remap.get(m, m))
                    if want is None or got is None:
                        out.append(f"{a} -> {b}: metatile {m} is past the end of a tileset")
                    elif want[1] != got[1]:
                        out.append(f"{a} -> {b}: metatile {m} behaves differently ({want[1]:#x} vs {got[1]:#x})")
                    elif want[0] != got[0] and (a, b, m) not in approx:
                        out.append(f"{a} -> {b}: metatile {m} looks different")
        return out


def write_header(seams):
    lines = ["// Generated by wiki/tools/world_port/seams.py. Do not edit.",
             "// For each connection whose two maps use different tilesets: the neighbour's metatile ids that show",
             "// in this map's view, and the id that draws the same here (pairs of from, to; sorted by from).",
             '#include "constants/maps.h"', ""]
    rows = []
    for i, ((a, b), remap) in enumerate(sorted(seams.remaps.items())):
        flat = ", ".join(f"{k}, {v}" for k, v in remap.items())
        lines.append(f"static const u16 sSeamRemap{i}[] = {{{flat}}};")
        rows.append(f"    {{MAP_GROUP({a}), MAP_NUM({a}), MAP_GROUP({b}), MAP_NUM({b}), {len(remap)}, sSeamRemap{i}}},")
    lines += ["", "static const struct SeamRemap sSeamRemaps[] =", "{"] + rows
    if not rows:
        lines.append("    {0xFF, 0xFF, 0xFF, 0xFF, 0, NULL},")
    lines += ["};", ""]
    B.write_text(B.GAME / HEADER, "\n".join(lines))


# ---------------------------------------------------------------------------------------------- in the game
# tools/play-tester/scripts/seam-check.sh walks across seams in mGBA and dumps what the game built; these write
# its spot list and compare the dumps.
STEP = {"up": (0, -1, "UP"), "down": (0, 1, "DOWN"), "left": (-1, 0, "LEFT"), "right": (1, 0, "RIGHT")}
# ground a walk may cross (seam-check.sh keeps wild battles away)
PLAIN = ("MB_NORMAL", "MB_TALL_GRASS", "MB_LONG_GRASS", "MB_SHORT_GRASS", "MB_DEEP_SAND", "MB_SAND", "MB_CAVE",
         "MB_ASHGRASS", "MB_FOOTPRINTS", "MB_PUDDLE", "MB_LONG_GRASS_SOUTH_EDGE")


def group_nums(state):
    groups = json.loads((state.game / "data/maps/map_groups.json").read_text())
    by_name = {m["name"]: c for c, m in state.maps.items()}
    return {by_name[name]: (g, n) for g, grp in enumerate(groups["group_order"])
            for n, name in enumerate(groups[grp]) if name in by_name}


def _blocked(state, const):
    """Cells of a map the walk must not cross: its people, signs, triggers and warps."""
    mj = state.maps[const]
    out = set()
    for k in ("object_events", "coord_events", "bg_events", "warp_events"):
        for e in mj.get(k) or []:
            if "x" in e and "y" in e:
                out.add((int(e["x"]), int(e["y"])))
    return out


def _plain():
    from . import tiles as TL
    return {TL.mb(n) for n in PLAIN}


def _walkable(state, const, cells_xy):
    w, h = state.size(const)
    raw = state.cells(const)
    key = state.pair_of(const)
    blocked = _blocked(state, const)
    elev = set()
    for x, y in cells_xy:
        if not (0 <= x < w and 0 <= y < h) or (x, y) in blocked:
            return None
        v = int(raw[y, x])
        if v & 0xC00:
            return None
        lk = state.look(key, v & 0x3FF)
        if lk is None or lk[1] & 0xFF not in _plain():
            return None
        elev.add(v >> 12)
    return elev


def spots(state=None):
    """One walk per connection: 4 steps to the edge and 3 beyond, on plain walkable cells with nobody about.
    Lines `name group num x y DIR steps`; connections with no such line are listed separately."""
    state = state or GameState()
    gn = group_nums(state)
    lines, none = [], []
    for a, mj in sorted(state.maps.items()):
        for conn in mj.get("connections") or []:
            d = conn["direction"]
            if d not in STEP:
                continue
            b, off = conn["map"], int(conn["offset"])
            aw, ah = state.size(a)
            bw, bh = state.size(b)
            dx, dy, key = STEP[d]
            cands = []
            if d in ("up", "down"):
                for x in range(max(0, off), min(aw, off + bw)):
                    ys_a = range(ah - 4, ah) if d == "down" else range(0, 4)
                    ys_b = range(0, 4) if d == "down" else range(bh - 4, bh)
                    ea = _walkable(state, a, [(x, y) for y in ys_a])
                    eb = _walkable(state, b, [(x - off, y) for y in ys_b])
                    if ea and eb and len(ea | eb - {0}) <= 1:
                        cands.append((abs(x - (max(0, off) + min(aw, off + bw)) / 2), x, ah - 4 if d == "down" else 3))
            else:
                for y in range(max(0, off), min(ah, off + bh)):
                    xs_a = range(aw - 4, aw) if d == "right" else range(0, 4)
                    xs_b = range(0, 4) if d == "right" else range(bw - 4, bw)
                    ea = _walkable(state, a, [(x, y) for x in xs_a])
                    eb = _walkable(state, b, [(x, y - off) for x in xs_b])
                    if ea and eb and len(ea | eb - {0}) <= 1:
                        cands.append((abs(y - (max(0, off) + min(ah, off + bh)) / 2), aw - 4 if d == "right" else 3, y))
            name = f"{state.maps[a]['name']}-{d}"
            g, n = gn[a]
            if not cands:
                # no walk (water, cliffs): still load the map there, to check the cells it copies
                none.append(f"{a} {d} {b}")
                if d in ("up", "down"):
                    x, y = (max(0, off) + min(aw, off + bw)) // 2, ah - 1 if d == "down" else 0
                else:
                    x, y = aw - 1 if d == "right" else 0, (max(0, off) + min(ah, off + bh)) // 2
                lines.append(f"{name} {g} {n} {x} {y} {key} 0")
                continue
            _, x, y = min(cands)
            lines.append(f"{name} {g} {n} {x} {y} {key} 7")
    return lines, none


def read_header(game=B.GAME):
    """The remap table as the game has it: {(map, neighbour): {neighbour id: id here}}."""
    text = (Path(game) / HEADER).read_text()
    arrays = {m.group(1): [int(v) for v in m.group(2).split(",") if v.strip()]
              for m in re.finditer(r"static const u16 (sSeamRemap\d+)\[\] = \{([^}]*)\};", text)}
    out = {}
    for m in re.finditer(r"\{MAP_GROUP\((\w+)\), MAP_NUM\(\w+\), MAP_GROUP\((\w+)\), MAP_NUM\(\w+\), (\d+), (\w+)\}", text):
        flat = arrays[m.group(4)]
        out[(m.group(1), m.group(2))] = dict(zip(flat[::2], flat[1::2]))
    return out


def expected_buffer(state, const, seams):
    """The cells of gBackupMapLayout fieldmap.c fills from the neighbours (after the remap): {(x, y): block}."""
    aw, ah = state.size(const)
    W, H = aw + 2 * MAP_OFFSET + 1, ah + 2 * MAP_OFFSET
    out = {}
    for conn in state.maps[const].get("connections") or []:
        d = conn["direction"]
        if d not in STEP:
            continue
        b, off = conn["map"], int(conn["offset"])
        remap = seams.get((const, b), {})
        cells = state.cells(b)
        for bx, by in band(state, const, b, conn):
            if d in ("up", "down"):
                x = bx + off + MAP_OFFSET
                y = by - (state.size(b)[1] - MAP_OFFSET) if d == "up" else ah + MAP_OFFSET + by
            else:
                y = by + off + MAP_OFFSET
                x = bx - (state.size(b)[0] - MAP_OFFSET) if d == "left" else aw + MAP_OFFSET + bx
            if 0 <= x < W and 0 <= y < H:
                v = int(cells[by, bx])
                m = remap.get(v & 0x3FF, v & 0x3FF)
                out[(x, y)] = (v & ~0x3FF) | m
    return out


def verify(outdir, seams, state=None):
    """Compare seam-check.sh's dumps: the neighbours' cells the game copied against what seams.py expects, and
    the field tilemaps after walking across against the same place loaded afresh. Returns (report, problems)."""
    state = state or GameState()
    outdir = Path(outdir)
    gn = {v: k for k, v in group_nums(state).items()}
    report, problems = [], []
    for line in (outdir / "log.txt").read_text().splitlines():
        name, src, pos, _, dst, dpos, _, cb2 = line.split()
        g, n = map(int, src.split("."))
        const = gn[(g, n)]
        if not all((outdir / f"{name}.{k}").exists() for k in ("load", "walk", "ref")):
            problems.append(f"{name}: no dump (the run stopped)")
            continue
        raw = (outdir / f"{name}.load").read_bytes()
        w, h = np.frombuffer(raw[:8], "<i4")
        buf = np.frombuffer(raw[8:], "<u2").reshape(h, w)
        exp = expected_buffer(state, const, seams)
        bad = [(x, y) for (x, y), v in exp.items() if int(buf[y, x]) != v]
        if bad:
            problems.append(f"{name}: {len(bad)} neighbour cells differ in the map buffer, e.g. {bad[:3]}")
        crossed = dst != src
        walk, ref = _tilemaps(outdir / f"{name}.walk"), _tilemaps(outdir / f"{name}.ref")
        diff = int((walk != ref).sum())
        if diff:
            problems.append(f"{name}: {diff} tilemap entries differ after walking into {dst} {dpos}")
        report.append(f"{name}: {len(exp)} neighbour cells ok, {'crossed into ' + gn[tuple(map(int, dst.split('.')))] if crossed else 'did not cross'}"
                      f", screen {'same as a fresh load' if not diff else 'DIFFERENT'}")
    return report, problems


def _tilemaps(path):
    """The three BG tilemaps, rotated by the camera's tile offset; the 15x15 metatiles the game keeps drawn."""
    raw = path.read_bytes()
    xo, yo = raw[2], raw[3]
    out = []
    for i in range(3):
        m = np.frombuffer(raw[4 + i * 0x800:4 + (i + 1) * 0x800], "<u2").reshape(32, 32)
        m = np.roll(np.roll(m, -yo, 0), -xo, 1)
        out.append(m[:30, :30])
    return np.stack(out)

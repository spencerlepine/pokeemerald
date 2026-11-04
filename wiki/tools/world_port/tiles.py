"""Per-area secondary tilesets: the vanilla tiles an area uses plus a metatile of its own for every new piece.

An area that needs anything vanilla does not have (a placeholder terrain role, a room-kit part, a building or
prop) gets its own secondary tileset `gTileset_Sw<Area>` in `data/tilesets/secondary/sw/<area-id>/`:

  append   (vanilla and hybrid areas) the vanilla secondary, unchanged, with the new metatiles and tiles after
           its own. Metatile ids and the tile animations stay vanilla, so map scripts that change metatiles
           still work.
  compact  (redrawn and new areas) only the vanilla secondary metatiles the area uses, renumbered, then the
           new ones. No tile animation (water there is still).

Every new graphic uses one palette, SW_PAL, in a secondary palette slot the vanilla metatiles leave free:
greys for the greybox renders and flat fills, magenta for the placeholder. Each new metatile is "covered"
(drawn below sprites), so a person standing in front of a building is drawn over it.

Placeholder cells: a flat grey fill on the bottom layer (the blockout legend's grey for that terrain) and the
pink placeholder circle on top. Each terrain role, room part and piece cell is its own metatile even when it
looks the same, so the final art can replace it without touching the maps.
"""
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

from . import base as B

N_PRIM_META = 512
N_PRIM_TILES = 512
N_SEC_META = 512
SEC_PALS = range(6, 13)
COVERED = 1

# SW_PAL: 0 transparent, 1 placeholder magenta, 2 outline, 3 water grey-blue, 4-15 greys
SW_PAL = [(0, 0, 0), (248, 0, 232), (40, 40, 48), (136, 144, 160)] + \
         [(v, v, v + 4 if v < 248 else v) for v in (48, 64, 80, 96, 112, 128, 144, 168, 184, 200, 216, 240)]
SW_PAL = [tuple((c >> 3) << 3 for c in col) for col in SW_PAL]
GREYS = list(range(4, 16))
LUM = np.array([sum(c) / 3 for c in SW_PAL])

FILL = {"ground": 13, "path": 15, "wild": 11, "water": 3, "blocked": 7, "wall": 6, "floor": 14, "bridge": 12,
        "ledge": 10}


def nearest_grey(lum):
    g = np.array(GREYS)
    return g[np.abs(LUM[g][None, :] - lum.reshape(-1, 1)).argmin(1)].reshape(lum.shape)


_PH = None


def placeholder_mask():
    global _PH
    if _PH is None:
        a = np.array(Image.open(B.TOOLS / "tile-generator/tilegen/data/placeholder-16x16.png").convert("RGBA"))
        _PH = a[..., 3] >= 128
    return _PH


def to_indices(img, w, h, mirror=False):
    """A render (any size, RGBA) fitted into w x h cells, as SW_PAL indices (0 = transparent)."""
    im = Image.open(img).convert("RGBA")
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    W, H = w * 16, h * 16
    if im.size[0] > W or im.size[1] > H:
        im.thumbnail((W, H), Image.NEAREST)
    canvas = Image.new("RGBA", (W, H))
    canvas.paste(im, ((W - im.size[0]) // 2, H - im.size[1]))
    a = np.array(canvas).astype(int)
    alpha = a[..., 3] >= 128
    rgb = a[..., :3]
    magenta = (rgb[..., 0] > 200) & (rgb[..., 1] < 80) & (rgb[..., 2] > 180)
    lum = rgb.mean(-1)
    out = nearest_grey(lum).astype(np.uint8)
    out[magenta] = 1
    out[~alpha] = 0
    return out


_RENDER = {}


def piece_pixels(png, w, h, mirror):
    k = (png, w, h, mirror)
    if k not in _RENDER:
        _RENDER[k] = to_indices(png, w, h, mirror)
    return _RENDER[k]


def flat_tile(idx):
    return np.full((8, 8), idx, np.uint8)


def split16(a16):
    """A 16x16 index array -> its four 8x8 tiles (tl, tr, bl, br)."""
    return [a16[0:8, 0:8], a16[0:8, 8:16], a16[8:16, 0:8], a16[8:16, 8:16]]


def ph_top():
    m = placeholder_mask()
    a = np.zeros((16, 16), np.uint8)
    a[m] = 1
    return split16(a)


def group_fill(item):
    from tilegen import roles as R
    g = R.group(item)
    if g.startswith("ledge"):
        return FILL["ledge"]
    if item in ("tall-grass", "long-grass", "ash-grass", "deep-sand"):
        return FILL["wild"]
    if g in ("path",):
        return FILL["path"]
    if item == "wall":
        return FILL["wall"]
    if item in ("floor",):
        return FILL["floor"]
    return FILL.get(g, FILL["ground"])


def behaviour_names():
    import re
    text = (B.BASE_GAME / "include/constants/metatile_behaviors.h").read_text()
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


MB = None


def mb(name):
    global MB
    if MB is None:
        MB = behaviour_names()
    return MB[name]


def ph_behaviour(item, role):
    from tilegen import roles as R
    g = R.group(item)
    if g == "water":
        if "pond" in item:
            return mb("MB_POND_WATER")
        return mb("MB_OCEAN_WATER")
    if item.startswith("ledge-"):
        return mb({"ledge-south": "MB_JUMP_SOUTH", "ledge-north": "MB_JUMP_NORTH", "ledge-east": "MB_JUMP_EAST",
                   "ledge-west": "MB_JUMP_WEST"}[item])
    if item in ("tall-grass", "long-grass"):
        return mb("MB_TALL_GRASS")
    return mb("MB_NORMAL")


ROOM_FILL = {"floor": FILL["floor"], "floor-alt": FILL["floor"], "exit-mat": FILL["path"]}


class Ref:
    """One tile of a metatile: ('P', id) primary tile, ('S', i) vanilla secondary tile i, ('N', bytes) new tile."""
    __slots__ = ("src", "key", "pal", "hf", "vf")

    def __init__(self, src, key, pal, hf=0, vf=0):
        self.src, self.key, self.pal, self.hf, self.vf = src, key, pal, hf, vf


def refs_of_vanilla(entries):
    out = []
    for e in entries:
        e = int(e)
        t, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        out.append(Ref("P", t, pal, hf, vf) if t < N_PRIM_TILES else Ref("S", t - N_PRIM_TILES, pal, hf, vf))
    return out


def new_ref(tile):
    return Ref("N", np.ascontiguousarray(tile, np.uint8).tobytes(), "SW")


class Builder:
    """Builds one area's secondary tileset and its final metatile ids."""

    def __init__(self, C, P, S, mode):
        self.C, self.P, self.S, self.mode = C, P, S, mode
        self.defs = []          # per symbol: (refs[8], attr)

    def vanilla_meta(self, mid):
        if mid < N_PRIM_META:
            return self.P.metatiles[mid].reshape(-1), int(self.P.attributes[mid])
        return self.S.metatiles[mid - N_PRIM_META].reshape(-1), int(self.S.attributes[mid - N_PRIM_META])

    def bottom_of(self, under):
        """Bottom-layer refs of what lies under a piece cell."""
        if isinstance(under, (int, np.integer)):
            ent, attr = self.vanilla_meta(int(under))
            return refs_of_vanilla(ent[:4])
        if under is None:
            return [new_ref(flat_tile(FILL["ground"]))] * 4
        return self.sym_def(under)[0][:4]

    def sym_def(self, s):
        kind = s[0]
        top_ph = ph_top()
        if kind == "ph":
            _, sheet, item, role = s
            fill = group_fill(item)
            refs = [new_ref(flat_tile(fill))] * 4 + [new_ref(t) for t in top_ph]
            return refs, ph_behaviour(item, role) | (COVERED << 12)
        if kind == "room":
            _, style, part, sub, flip, edge = s
            fill = ROOM_FILL.get(part, FILL["wall"])
            refs = [new_ref(flat_tile(fill))] * 4 + [new_ref(t) for t in top_ph]
            beh = mb("MB_NORMAL")
            if part == "exit-mat":
                beh = mb({"south": "MB_SOUTH_ARROW_WARP", "north": "MB_NORTH_ARROW_WARP", "east": "MB_EAST_ARROW_WARP",
                          "west": "MB_WEST_ARROW_WARP"}[edge])
            return refs, beh | (COVERED << 12)
        if kind == "piece":
            _, png, w, h, mirror, cx, cy, under, door = s
            pix = piece_pixels(png, w, h, mirror)[cy * 16:(cy + 1) * 16, cx * 16:(cx + 1) * 16]
            refs = self.bottom_of(under) + [new_ref(t) for t in split16(pix)]
            beh = mb(door) if isinstance(door, str) else mb("MB_NON_ANIMATED_DOOR") if door else mb("MB_NORMAL")
            return refs, beh | (COVERED << 12)
        raise ValueError(s)

    def build(self):
        """Lay out the area's secondary tileset. Returns tiles, palettes, metatiles, attributes and final cells."""
        from . import pins
        C, S = self.C, self.S
        used = sorted({int(v) for v in np.unique(C.meta) if v >= N_PRIM_META})
        self.defs = [self.sym_def(s) for s in C.syms]
        n_sec = S.n_metatiles
        if self.mode == "pinned":
            # every vanilla metatile keeps its id; only the tiles of the ones in use (or named by scripts) and
            # the animated slots keep their place, the other slots take the new tiles
            labelled = {m - N_PRIM_META for m in pins.labels().get(C.sec, set()) if N_PRIM_META <= m < N_PRIM_META + n_sec}
            live = sorted({m - N_PRIM_META for m in used} | labelled)
            meta_map = {N_PRIM_META + i: N_PRIM_META + i for i in range(n_sec)}
            kept_tiles = {(int(e) & 0x3FF) - N_PRIM_TILES for i in live for e in S.metatiles[i].reshape(-1)
                          if (int(e) & 0x3FF) >= N_PRIM_TILES}
            kept_tiles |= pins.reserved_slots(C.sec)
            tile_map = {t: t for t in range(N_PRIM_TILES)}
            free_slots = [t for t in range(N_PRIM_TILES) if t not in kept_tiles]
            base_entries = [S.metatiles[i].reshape(-1).astype(np.uint16) for i in range(n_sec)]
            base_attrs = [int(a) for a in S.attributes]
            live_entries = [S.metatiles[i].reshape(-1) for i in live]
            free_meta = list(range(n_sec, N_SEC_META)) + [i for i in range(n_sec) if i not in set(live)]
            self.callback = pins.callbacks().get(C.sec, "NULL")
        else:
            meta_map = {mid: N_PRIM_META + i for i, mid in enumerate(used)}
            live_entries = [S.metatiles[mid - N_PRIM_META].reshape(-1) for mid in used]
            sec = sorted({(int(e) & 0x3FF) - N_PRIM_TILES for ent in live_entries for e in ent
                          if (int(e) & 0x3FF) >= N_PRIM_TILES})
            tile_map = {t: i for i, t in enumerate(sec)}
            kept_tiles = set(tile_map.values())
            free_slots = list(range(len(sec), N_PRIM_TILES))
            base_entries, base_attrs = None, None
            free_meta = list(range(len(used), N_SEC_META))
            self.callback = "NULL"
        # --- palettes
        used_pals = {int(e) >> 12 for ent in live_entries for e in ent}
        free = [p for p in SEC_PALS if p not in used_pals]
        if not free:
            raise RuntimeError(f"{C.area.id}: no free secondary palette slot (used {sorted(used_pals)})")
        sw_pal = free[-1]

        # --- new tiles (dedup with flips), merged down to the free slots if needed
        def canon(key):
            a = np.frombuffer(key, np.uint8).reshape(8, 8)
            best = None
            for hf in (0, 1):
                for vf in (0, 1):
                    b = a[:, ::-1] if hf else a
                    b = b[::-1] if vf else b
                    k = b.tobytes()
                    if best is None or k < best[0]:
                        best = (k, hf, vf)
            return best

        counts = Counter()
        for refs, _ in self.defs:
            for r in refs:
                if r.src == "N":
                    counts[canon(r.key)[0]] += 1
        merge = reduce_tiles(list(counts), counts, len(free_slots))
        if merge:
            C.notes.append(f"{len(merge)} similar new tiles merged to fit the tile budget")
        new_slot = {}
        for k in sorted(counts, key=lambda k: -counts[k]):
            k2 = merge.get(k, k)
            if k2 not in new_slot:
                new_slot[k2] = free_slots[len(new_slot)]

        def entry(r):
            if r.src == "P":
                return r.key | (r.hf << 10) | (r.vf << 11) | (r.pal << 12)
            if r.src == "S":
                t = N_PRIM_TILES + tile_map[r.key]
                return t | (r.hf << 10) | (r.vf << 11) | (r.pal << 12)
            k, hf, vf = canon(r.key)
            k = merge.get(k, k)
            return (N_PRIM_TILES + new_slot[k]) | ((hf ^ r.hf) << 10) | ((vf ^ r.vf) << 11) | (sw_pal << 12)

        # --- metatiles
        if self.mode == "pinned":
            metas = {i: base_entries[i] for i in range(n_sec)}
            attrs = {i: base_attrs[i] for i in range(n_sec)}
        else:
            metas, attrs = {}, {}
            for mid in used:
                ent = S.metatiles[mid - N_PRIM_META].reshape(-1)
                metas[meta_map[mid] - N_PRIM_META] = np.array([entry(r) for r in refs_of_vanilla(ent)], np.uint16)
                attrs[meta_map[mid] - N_PRIM_META] = int(S.attributes[mid - N_PRIM_META])
        sym_ids, uniq = {}, {}
        for i, (refs, attr) in enumerate(self.defs):
            ent = tuple(entry(r) for r in refs)
            key = (ent, attr, C.syms[i] if C.syms[i][0] != "piece" else None)
            if key not in uniq:
                if not free_meta:
                    raise RuntimeError(f"{C.area.id}: no free secondary metatile slot")
                slot = free_meta.pop(0)
                uniq[key] = N_PRIM_META + slot
                metas[slot] = np.array(ent, np.uint16)
                attrs[slot] = attr
            sym_ids[i] = uniq[key]
        n_meta = max(metas) + 1
        meta_arr = np.zeros((n_meta, 8), np.uint16)
        attr_arr = np.zeros(n_meta, np.uint16)
        for i, e in metas.items():
            meta_arr[i] = e
            attr_arr[i] = attrs[i]
        # --- tiles
        n_tiles = max([max(kept_tiles, default=-1)] + [max(new_slot.values(), default=-1)]) + 1
        if self.mode == "pinned":
            n_tiles = max(n_tiles, len(S.tiles))
        tiles = np.zeros((n_tiles, 8, 8), np.uint8)
        if self.mode == "pinned":
            tiles[:len(S.tiles)] = S.tiles
        else:
            for t, i in tile_map.items():
                if t < len(S.tiles):
                    tiles[i] = S.tiles[t]
        for k, slot in new_slot.items():
            tiles[slot] = np.frombuffer(k, np.uint8).reshape(8, 8)
        pals = [list(p) for p in S.palettes]
        pals[sw_pal] = list(SW_PAL)
        # --- final cells
        final = np.zeros(C.meta.shape, np.uint16)
        for (y, x), v in np.ndenumerate(C.meta):
            v = int(v)
            if v < 0:
                final[y, x] = sym_ids[-v - 1]
            elif v < N_PRIM_META:
                final[y, x] = v
            else:
                final[y, x] = meta_map[v]
        return dict(tiles=tiles, palettes=pals, metatiles=meta_arr, attributes=attr_arr, cells=final,
                    sw_pal=sw_pal, n_new_tiles=len(new_slot), n_new_meta=len(uniq), callback=self.callback,
                    sym_ids=sym_ids)


def reduce_tiles(keys, counts, budget):
    """Merge the least used new tiles into their nearest neighbour until they fit the budget. {old: kept}."""
    if len(keys) <= budget:
        return {}
    if budget <= 0:
        raise RuntimeError("no room for new tiles")
    arr = {k: LUM[np.frombuffer(k, np.uint8)].reshape(8, 8) for k in keys}
    alive = sorted(keys, key=lambda k: -counts[k])
    merge = {}
    while len(alive) > budget:
        k = alive.pop()                       # least used
        a = arr[k]
        best = min(alive, key=lambda o: np.abs(arr[o] - a).sum())
        merge[k] = best
        counts[best] += counts[k]
        for kk, vv in list(merge.items()):
            if vv == k:
                merge[kk] = best
    return merge


def write_tileset(out, folder):
    """tiles.png (indexed), palettes/00-15.pal, metatiles.bin, metatile_attributes.bin. Returns tile count."""
    from tilegen import gba
    folder = Path(folder)
    tiles = out["tiles"]
    n = len(tiles)
    img = gba.tiles_to_image(tiles, 16)
    im = Image.fromarray(img.astype(np.uint8), "P")
    flat = [c for col in SW_PAL for c in col]
    im.putpalette(flat)
    folder.mkdir(parents=True, exist_ok=True)
    import io
    buf = io.BytesIO()
    im.save(buf, format="PNG", bits=4)
    B.write_bytes(folder / "tiles.png", buf.getvalue())
    for i, pal in enumerate(out["palettes"]):
        txt = "JASC-PAL\r\n0100\r\n16\r\n" + "".join(f"{r} {g} {b}\r\n" for r, g, b in pal)
        B.write_text(folder / "palettes" / f"{i:02d}.pal", txt)
    B.write_bytes(folder / "metatiles.bin", out["metatiles"].astype("<u2").tobytes())
    B.write_bytes(folder / "metatile_attributes.bin", out["attributes"].astype("<u2").tobytes())
    return n

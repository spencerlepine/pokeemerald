"""Tile a redrawn grid the way vanilla tiles it: by example, not by a fixed role table.

Every vanilla layout is read once. For each cell we know its item (cliff, path, grass...) and the items around
it, and which metatile vanilla put there. A new grid cell takes the metatile vanilla uses most for the same item
with the same surroundings: the 5x5 pattern first, then the 3x3 one, then the old role lookup. Then each cell is
checked against its four neighbours: a pair of metatiles vanilla never puts side by side is swapped for another
candidate that fits, a few sweeps over the grid. So cliff faces, corners and path edges join the way they do in
Hoenn.

Patterns are counted per tileset pair (the secondary's own tiles) and per primary (tiles below 512, shared by
every pair of that primary).
"""
from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np

from . import terrain as T
from . import roles as R
from . import gba

NP = gba.NUM_METATILES_IN_PRIMARY


def cls(item: str) -> str:
    """The class an item counts as in a neighbour pattern."""
    if item.startswith("water-") or item == "dune-sea":
        return "~"
    if item in ("cliff", "wall"):
        return "#"
    if item == "structure":
        return "."               # ground by a vanilla house is plain ground; a redrawn grid has ground under pieces
    if item in ("tree", "wroshyr"):
        return "T"
    if item == "ground-path":
        return ":"
    if item.startswith("ledge-"):
        return item
    if item == "bridge":
        return "="
    if item in ("tall-grass", "long-grass", "ash-grass", "deep-sand", "wild-grass"):
        return '"'
    return item                  # each ground by name: an edge tile has the ground beside it drawn in


R3 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
R5 = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3) if (dy, dx) != (0, 0)]


def _ctx(C, y, x, offs):
    H, W = len(C), len(C[0])
    return tuple(C[min(max(y + dy, 0), H - 1)][min(max(x + dx, 0), W - 1)] for dy, dx in offs)


class Model:
    def __init__(self):
        self.c5 = defaultdict(Counter)    # (prim, sec|'*', item, ctx5) -> Counter(meta)
        self.c3 = defaultdict(Counter)
        self.h = defaultdict(Counter)     # (prim, sec|'*') -> Counter((left, right))
        self.v = defaultdict(Counter)     # (prim, sec|'*') -> Counter((top, bottom))
        self.seen = set()
        self._idx = {}

    def nearest(self, prim, src, item, k5, slack=0.0):
        """Metatiles vanilla draws for this item where the 5x5 pattern is closest to k5, scored by count."""
        key = (prim, src, item)
        if key not in self._idx:
            ks = [(k, c) for (p_, s_, it, k), c in self.c5.items() if p_ == prim and s_ == src and it == item]
            if not ks:
                self._idx[key] = None
            else:
                codes = {}
                arr = np.array([[codes.setdefault(v, len(codes)) for v in k] for k, _ in ks], np.int32)
                tot = Counter()
                for _, c in ks:
                    tot.update(c)
                # a metatile vanilla filed under this item only a few times is a one-off (flowers by a path)
                common = {m for m, n in tot.items() if n >= MIN_CELLS} or set(tot)
                cs = [Counter({m: n for m, n in c.items() if m in common}) for _, c in ks]
                keep = [i for i, c in enumerate(cs) if c]
                self._idx[key] = (arr[keep], [cs[i] for i in keep], codes)
        ix = self._idx[key]
        if ix is None:
            return Counter(), 1e9
        arr, cs, codes = ix
        q = np.array([codes.get(v, -1) for v in k5], np.int32)
        d = ((arr != q) * WT).sum(1)
        dmin = d.min()
        out = Counter()
        for i in np.nonzero(d <= dmin + slack)[0]:
            tot = sum(cs[i].values())
            for m, n in cs[i].items():
                out[m] += n / tot * (1 + tot) ** 0.5 / (1 + d[i] - dmin)
        return out, dmin

    def learn(self, prim, sec, names, metas):
        H, W = metas.shape
        C = [[cls(n) for n in row] for row in names]
        for y in range(H):
            for x in range(W):
                it = names[y][x]
                if it == "structure":
                    continue
                m = int(metas[y, x])
                k5, k3 = _ctx(C, y, x, R5), _ctx(C, y, x, R3)
                self.c5[(prim, sec, it, k5)][m] += 1
                self.c3[(prim, sec, it, k3)][m] += 1
                if m < NP:
                    self.c5[(prim, "*", it, k5)][m] += 1
                    self.c3[(prim, "*", it, k3)][m] += 1
                if x + 1 < W:
                    a, b = m, int(metas[y, x + 1])
                    self.h[(prim, sec)][(a, b)] += 1
                    if a < NP and b < NP:
                        self.h[(prim, "*")][(a, b)] += 1
                if y + 1 < H:
                    a, b = m, int(metas[y + 1, x])
                    self.v[(prim, sec)][(a, b)] += 1
                    if a < NP and b < NP:
                        self.v[(prim, "*")][(a, b)] += 1


SANDY = {":", "sand", "deep-sand"}   # grounds a path meets with no edge
MIN_CELLS = 8                  # a metatile counts for an item from this many vanilla cells
WT = np.array([4 if max(abs(dy), abs(dx)) == 1 else 1 for dy, dx in R5], float)   # near ring counts more

_MODEL: dict = {}


def model() -> Model:
    """Learned from every vanilla layout tile-generator scanned (terrain.scan fills LAYOUT_NAMES)."""
    if "m" not in _MODEL:
        M = Model()
        done = set()
        for ar in T.areas():
            lay = ar["layout"]
            if lay is None or lay.name in done or lay.name not in T.LAYOUT_NAMES:
                continue
            done.add(lay.name)
            M.learn(lay.primary, lay.secondary, T.LAYOUT_NAMES[lay.name], lay.cells() & 0x3FF)
        _MODEL["m"] = M
    return _MODEL["m"]


# The General tileset's rock set, read off the tileset (rows 0x68-0xAF), one set per ground it stands on: each
# role from which of the 8 neighbours are open ground. Checked on test basins rendered from the tileset. A cliff
# drawn piece by piece from patterns can mix pieces of different vanilla mountains; this set always joins.
ROCK_KITS = {
    "grass": dict(fill=0x71, n=0x69, s=0x79, w=0x70, e=0x72, nw=0x68, ne=0x6A, sw=0x78, se=0x7A,
                  in_ne=0xBF, in_nw=0xBE, in_se=0x74, in_sw=0x89, tip=0xE0, strip_v=0xE0, strip_h=0x79),
    "sand": dict(fill=0x71, n=0x81, s=0x91, w=0x88, e=0x8A, nw=0x80, ne=0x82, sw=0x90, se=0x92,
                 in_ne=0x71, in_nw=0x71, in_se=0x93, in_sw=0x94, tip=0xE2, strip_v=0xE2, strip_h=0x91),
}
GRASSY = {"ground-grass", "tall-grass", "long-grass", "wild-grass", "ground-path", "ground-stone", "bridge",
          "ledge-south", "ledge-north", "ledge-east", "ledge-west"}
SANDS = {"sand", "deep-sand"}
BLOCKS = {"#", "T"}


def rock_role(open_):
    """open_(dy, dx): is that neighbour open ground. The rock piece for a blocked cell."""
    n, e, s, w = open_(-1, 0), open_(0, 1), open_(1, 0), open_(0, -1)
    if sum((n, e, s, w)) >= 3 or (n and s and not (e or w) and False):
        return "tip"
    if (n and s) or (e and w):
        return "strip_h" if n and s else "strip_v"
    if n and w: return "nw"
    if n and e: return "ne"
    if s and w: return "sw"
    if s and e: return "se"
    if n: return "n"
    if s: return "s"
    if w: return "w"
    if e: return "e"
    if open_(-1, 1): return "in_ne"
    if open_(-1, -1): return "in_nw"
    if open_(1, 1): return "in_se"
    if open_(1, -1): return "in_sw"
    return "fill"


def rock_kit(names, prim, cand, fixed=None):
    """Cliff cells on the General tileset take the fixed rock set (grass or sand by the ground beside them).
    A cliff by water or a pair's own ground (Lavaridge ash) keeps its pattern tile."""
    if prim != "gTileset_General":
        return
    H, W = len(names), len(names[0])
    C = [[cls(n) for n in row] for row in names]
    at = lambda y, x: C[min(max(y, 0), H - 1)][min(max(x, 0), W - 1)]
    is_open = lambda y, x: at(y, x) not in BLOCKS and not at(y, x).startswith("ph")
    grounds = Counter()
    kit_of = {}
    for y in range(H):
        for x in range(W):
            if names[y][x] != "cliff" or (fixed is not None and fixed[y, x] != T.MISSING):
                continue
            near = {names[min(max(y + dy, 0), H - 1)][min(max(x + dx, 0), W - 1)] for dy, dx in R3
                    if is_open(y + dy, x + dx)}
            if not near:
                continue
            k = "sand" if near & SANDS else "grass" if near <= GRASSY else None
            kit_of[(y, x)] = k
            grounds[k] += 1
    if not grounds:
        return
    area_kit = grounds.most_common(1)[0][0]
    if area_kit is None:
        return
    kitted = set()
    for y in range(H):
        for x in range(W):
            if names[y][x] != "cliff" or (fixed is not None and fixed[y, x] != T.MISSING):
                continue
            k = kit_of.get((y, x), area_kit)
            if k is None:
                continue
            r = rock_role(lambda dy, dx: is_open(y + dy, x + dx))
            cand[y][x] = [(ROCK_KITS[k][r], 1.0)]
            kitted.add((y, x))
    _repair(cand, kitted, H, W)


ROCK_SET = sorted({t for k in ROCK_KITS.values() for t in k.values()} | {0x73, 0x75, 0x7B, 0x7C, 0x7D, 0x6B, 0x6D, 0xA9})


def _repair(cand, kitted, H, W, sweeps=4):
    """Where two set pieces meet in a way vanilla never draws (a lit rim against a dark face, a ridge into a wall),
    try the other rock pieces for that cell: each choice is scored by how often vanilla puts it beside its four
    neighbours, the set's own piece first on a tie."""
    M = model()
    hh, vv = M.h[("gTileset_General", "*")], M.v[("gTileset_General", "*")]
    cur = lambda y, x: cand[y][x][0][0] if cand[y][x] else None

    def pair_score(t, y, x):
        sc, bad = 0.0, 0
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            yy, xx = y + dy, x + dx
            if not (0 <= yy < H and 0 <= xx < W) or cur(yy, xx) is None:
                continue
            u = cur(yy, xx)
            n = (hh if dy == 0 else vv)[(t, u) if dy + dx > 0 else (u, t)]
            if n < 2:
                bad += 1
            sc += np.log1p(n)
        return bad, sc

    for _ in range(sweeps):
        changed = 0
        for (y, x) in sorted(kitted):
            own = cand[y][x][0][0]
            b0, s0 = pair_score(own, y, x)
            if b0 == 0:
                continue
            best = min(ROCK_SET, key=lambda t: (pair_score(t, y, x)[0], -pair_score(t, y, x)[1] - (2 if t == own else 0)))
            if pair_score(best, y, x)[0] < b0:
                cand[y][x] = [(best, 1.0)]
                changed += 1
        if not changed:
            break


def tile(names, prim, sec, stats, p, ok=None, sweeps=4, fixed=None):
    """Item grid -> metatile grid (None where the pair has no tile). `ok(y, x, mid)` can veto a candidate.
    `fixed` (an array, MISSING where free) holds cells already set, such as the vanilla cells a planet kit keeps."""
    M = model()
    H, W = len(names), len(names[0])
    C = [[cls(n) for n in row] for row in names]
    role_grid = R.roles(names)
    cand = [[None] * W for _ in range(H)]
    near = {}
    dsum = defaultdict(lambda: [0.0, 0.0])         # item -> total distance with the primary's tiles, the pair's
    fbs = {}
    for y in range(H):
        for x in range(W):
            it = names[y][x]
            if fixed is not None and fixed[y, x] != T.MISSING:
                cand[y][x] = [(int(fixed[y, x]), 1.0)]
                continue
            if it in T.NEW_ITEMS:
                continue
            fb = fbs[(y, x)] = T.lookup(prim, sec, it, role_grid[y][x], stats, p)
            if (R.group(it) == "ground" and it not in ("ground-path", "bridge") and not it.startswith("ledge-")) \
                    or (it == "ground-path" and (role_grid[y][x] in T.THIN or all(
                        C[min(max(y + dy, 0), H - 1)][min(max(x + dx, 0), W - 1)] in SANDY for dy, dx in R3))):
                # grounds and wild grass: their fill tile (vanilla dots grass with flowers and stones where an
                # artist liked, which a pattern would copy at random); a one-cell path, or a path with only path or sand
                # around it (a plaza, a road through Tatooine sand: vanilla draws no edge there): the plain path
                if it == "ground-path":
                    fb = T.lookup(prim, sec, it, "fill", stats, p)
                if fb is not None and (not ok or ok(y, x, fb)):
                    cand[y][x] = [(fb, 1.0)]
                continue
            k5 = _ctx(C, y, x, R5)
            near[(y, x)] = n = (M.nearest(prim, "*", it, k5, 2), M.nearest(prim, sec, it, k5, 2))
            dsum[it][0] += min(n[0][1], 99)
            dsum[it][1] += min(n[1][1], 99)
    # one source per item for the whole area, so a cliff ring is one set: the primary's shared tiles (one look on
    # every planet) unless the pair's own match closer overall (a cliff on Lavaridge ash has the ash drawn in)
    use_sec = {it: d[1] < d[0] and R.group(it) != "ground" for it, d in dsum.items()}    # paths: always the shared set
    for (y, x), n in near.items():
        it = names[y][x]
        score, d = n[1] if use_sec[it] else n[0]
        if not score:
            score = (n[0] if use_sec[it] else n[1])[0]
        score = Counter(score)
        fb = fbs[(y, x)]
        if fb is not None:
            score[fb] = max(score[fb], 1e-3)
        if ok:
            score = Counter({m: v for m, v in score.items() if ok(y, x, m)})
        if score:
            cand[y][x] = score.most_common(12)
    rock_kit(names, prim, cand, fixed)
    pick = [[c[0][0] if c else None for c in row] for row in cand]
    hp, hs = M.h.get((prim, sec), Counter()), M.h.get((prim, "*"), Counter())
    vp, vs = M.v.get((prim, sec), Counter()), M.v.get((prim, "*"), Counter())

    def fits(a, b, P, S):
        return a is None or b is None or (a, b) in P or (a, b) in S

    def bad(y, x, m):
        n = 0
        if x > 0 and not fits(pick[y][x - 1], m, hp, hs): n += 1
        if x + 1 < W and not fits(m, pick[y][x + 1], hp, hs): n += 1
        if y > 0 and not fits(pick[y - 1][x], m, vp, vs): n += 1
        if y + 1 < H and not fits(m, pick[y + 1][x], vp, vs): n += 1
        return n

    for _ in range(sweeps):
        changed = 0
        for y in range(H):
            for x in range(W):
                cs = cand[y][x]
                if not cs or len(cs) < 2:
                    continue
                cur = pick[y][x]
                if bad(y, x, cur) == 0:
                    continue
                best = min(cs, key=lambda mv: (bad(y, x, mv[0]), -mv[1]))
                if best[0] != cur and bad(y, x, best[0]) < bad(y, x, cur):
                    pick[y][x] = best[0]
                    changed += 1
        if not changed:
            break
    return pick


def misfits(pick, prim, sec):
    """How many neighbour pairs vanilla never shows side by side (for reports)."""
    M = model()
    H, W = len(pick), len(pick[0])
    n = 0
    for y in range(H):
        for x in range(W):
            a = pick[y][x]
            if a is None:
                continue
            if x + 1 < W and pick[y][x + 1] is not None and (a, pick[y][x + 1]) not in M.h[(prim, sec)] \
                    and (a, pick[y][x + 1]) not in M.h[(prim, "*")]:
                n += 1
            if y + 1 < H and pick[y + 1][x] is not None and (a, pick[y + 1][x]) not in M.v[(prim, sec)] \
                    and (a, pick[y + 1][x]) not in M.v[(prim, "*")]:
                n += 1
    return n

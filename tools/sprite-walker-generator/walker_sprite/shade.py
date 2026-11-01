"""Form shading learned from Emerald (D13).

The LLM draws *regions* (which material covers which pixel: skin, cloth ramp a/b/c, white,
black) and this module picks the tone of every pixel the way the 90 vanilla walkers do: light on
top and on the lit side, mid in the middle, dark on the underside and at the edges, outline in
the darkest tone against transparency or another material.

It is a lookup table, not a rule of thumb: for every opaque vanilla pixel we record a local
geometric key (how far the pixel is from its region's edge up/down/left/right, capped at 3, and
what lies beyond each edge: transparency, another material, or black) and the tone the artist
used there. Shading a new sprite looks each pixel's key up, backing off to coarser keys when the
exact one was never seen. Re-shading the vanilla sheets themselves from their own regions gives
the tone back ~74% of the time (always-mid gets 30%); `python -m walker_sprite shader` rebuilds
the table and writes corpus/shader-check.png so the result can be judged by eye.

    regions_of(frames)      index grids -> material letters (s a b c w k, '.' transparent)
    shade(region_grid, ...) material letters -> palette indices

Materials: s = skin ramp (indices 1 2 3 4: light, base, shade, outline), a/b/c = the three
3-tone ramps (5-7, 8-10, 11-13), w = white (14), k = black (15). A spec may map several letters
to one material (e.g. A and a both -> ramp a) to shade two touching volumes separately.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "corpus"
TABLE_FILE = CORPUS / "shader.json"

INDEX_TO_MAT = {1: ("s", 0), 2: ("s", 1), 3: ("s", 2), 4: ("s", 3),
                5: ("a", 0), 6: ("a", 1), 7: ("a", 2), 8: ("b", 0), 9: ("b", 1), 10: ("b", 2),
                11: ("c", 0), 12: ("c", 1), 13: ("c", 2), 14: ("w", 0), 15: ("k", 0)}
MAT_TONES = {"s": (1, 2, 3, 4), "a": (5, 6, 7), "b": (8, 9, 10), "c": (11, 12, 13), "w": (14,), "k": (15,)}
SHADED = ("s", "a", "b", "c")
CAP = 3


def regions_of(frame: list[list[int]]) -> list[str]:
    """One frame of palette indices -> rows of material letters."""
    return ["".join("." if not v else INDEX_TO_MAT[v][0] for v in row) for row in frame]


def _features(mat: list[list[str]], x: int, y: int) -> tuple:
    h, w = len(mat), len(mat[0])
    m = mat[y][x]

    def run(dx, dy):
        n, X, Y = 0, x + dx, y + dy
        while 0 <= X < w and 0 <= Y < h and mat[Y][X] == m and n < CAP:
            n, X, Y = n + 1, X + dx, Y + dy
        return n

    def beyond(dx, dy):
        X, Y = x + dx, y + dy
        while 0 <= X < w and 0 <= Y < h and mat[Y][X] == m:
            X, Y = X + dx, Y + dy
        if not (0 <= X < w and 0 <= Y < h) or mat[Y][X] == ".":
            return "t"
        return "k" if mat[Y][X] == "k" else "o"

    skin = 1 if m == "s" else 0
    return (skin, run(0, -1), run(0, 1), run(-1, 0), run(1, 0), beyond(0, -1), beyond(0, 1), beyond(-1, 0), beyond(1, 0))


def _backoff(key: tuple):
    """Coarser and coarser versions of a key, most specific first."""
    skin, u, d, l, r, bu, bd, bl, br = key
    yield key
    yield (skin, u, d, l, r, bu, bd, "x", "x")
    yield (skin, u, d, l, r, "x", "x", "x", "x")
    yield (skin, min(u, 1), min(d, 1), min(l, 1), min(r, 1), bu, bd, bl, br)
    yield (skin, min(u, 1), min(d, 1), min(l, 1), min(r, 1), "x", "x", "x", "x")
    yield (skin, "x", "x", "x", "x", "x", "x", "x", "x")


def _k(key) -> str:
    return "|".join(str(v) for v in key)


def train(frames_by_sheet: dict[str, list]) -> dict:
    """Learn the tone table from vanilla stand frames; returns the table plus a self-check."""
    counts: dict[str, Counter] = defaultdict(Counter)
    samples = []
    for name, frames in frames_by_sheet.items():
        for fr in frames[:3]:
            mat = [list(r) for r in regions_of(fr)]
            for y, row in enumerate(fr):
                for x, v in enumerate(row):
                    if v and INDEX_TO_MAT[v][0] in SHADED:
                        key = _features(mat, x, y)
                        tone = INDEX_TO_MAT[v][1]
                        samples.append((name, key, tone))
                        for kk in _backoff(key):
                            counts[_k(kk)][tone] += 1
    table = {k: c.most_common(1)[0][0] for k, c in counts.items()}
    ok = sum(1 for _, key, tone in samples if _lookup(table, key) == tone)
    return {"table": table, "accuracy": round(ok / len(samples), 3), "samples": len(samples)}


def _lookup(table: dict, key: tuple) -> int:
    for kk in _backoff(key):
        t = table.get(_k(kk))
        if t is not None:
            return t
    return 1


def load_table() -> dict:
    if not TABLE_FILE.exists():
        raise FileNotFoundError("corpus/shader.json missing: run `python -m walker_sprite shader`")
    return json.loads(TABLE_FILE.read_text())["table"]


def shade(regions: list[str], materials: dict[str, str] | None = None, hard: dict[str, int] | None = None,
          table: dict | None = None, facing: str | None = None) -> list[list[int]]:
    """Material-letter rows -> palette indices.

    materials: letter -> material (s a b c w k); default: the letter is the material.
    hard: letter -> palette index placed as-is (eyes, buttons); these pixels shade their
    neighbours as 'black' when the index is 15 and as 'another material' otherwise.
    A white material may be written "w/c" (or w/s, w/a, w/b): white fill, and the pixels on the
    silhouette edge in that ramp's darkest tone, the way Emerald outlines white shirts.
    A ramp may be written "skin-b" (skin-a, skin-c): shaded with the face statistics (mostly the
    mid tone, light on top, dark only at the edge) instead of the cloth/hair statistics, for
    bald alien heads and bare hide. The 4 skin tones collapse onto the ramp's 3.
    Letters mapping to the same material but spelled differently are separate volumes.
    """
    table = table or load_table()
    materials = materials or {}
    hard = hard or {}
    h, w = len(regions), len(regions[0])
    # letters whose material ends in "!" are shaded by the volume rules (D14) instead of the
    # table: flat garments the corpus has no local match for (robes, aprons, droid plating)
    round_ = {ch for ch, m in materials.items() if m.rstrip("!").endswith(("@", "%"))}
    # "%" = a form: round shading bounded by its OWN volume (other letters count as outside), so
    # overlapping forms each get an outline and a lit top inside the silhouette (D17, big sprites)
    form_ = {ch for ch, m in materials.items() if m.rstrip("!").endswith("%")}
    materials = {ch: m.replace("@", "").replace("%", "") for ch, m in materials.items()}
    ruled = {ch for ch, m in materials.items() if m.endswith("!")}
    materials = {ch: m.rstrip("!") for ch, m in materials.items()}
    by_rules = shade_rules(regions, materials, hard) if ruled else None
    by_round = shade_round(regions, materials, hard, round_, facing, form_) if round_ else None
    # per-pixel volume id: the letter itself (so A and a are different volumes), with hard
    # pixels marked by what they look like to their neighbours
    vol = []
    for row in regions:
        r = []
        for ch in row:
            if ch == ".":
                r.append(".")
            elif ch in hard:
                r.append("k" if hard[ch] == 15 else "#" + ch)
            else:
                r.append(ch)
        vol.append(r)
    # skin-ness is a property of the material, which the feature extractor reads from the letter
    # 's'; map volumes onto a grid where every skin volume is spelled 's' + letter for the test
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            ch = regions[y][x]
            if ch == ".":
                continue
            if ch in hard:
                out[y][x] = hard[ch]
                continue
            if ch in round_:
                out[y][x] = by_round[y][x]
                continue
            if ch in ruled:
                out[y][x] = by_rules[y][x]
                continue
            m = materials.get(ch, ch)
            edge = None
            skinlike = m.startswith("skin-")  # "skin-b": ramp b lit like a face (bald alien heads)
            if skinlike:
                m = m[5:]
                if m not in ("a", "b", "c"):
                    raise ValueError(f"letter {ch!r}: skin-X needs X in a b c, not {m!r}")
            if "/" in m:  # "w/c": white fill, silhouette edge in ramp c's darkest tone
                m, edge_mat = m.split("/", 1)
                if m != "w" or edge_mat not in SHADED:
                    raise ValueError(f"letter {ch!r}: edged material must be w/s, w/a, w/b or w/c, not {m}/{edge_mat}")
                edge = MAT_TONES[edge_mat][-1]
            if m not in MAT_TONES:
                raise ValueError(f"letter {ch!r} maps to unknown material {m!r}")
            tones = MAT_TONES[m]
            if len(tones) == 1:
                at_edge = edge is not None and any(
                    not (0 <= x + dx < w and 0 <= y + dy < h) or vol[y + dy][x + dx] == "."
                    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
                out[y][x] = edge if at_edge else tones[0]
                continue
            key = _features(vol, x, y)
            key = (1 if (m == "s" or skinlike) else 0,) + key[1:]
            tone = _lookup(table, key)
            if skinlike:  # 4 face tones onto 3: light, base+shade -> mid, outline -> dark
                tone = {0: 0, 1: 1, 2: 1, 3: 2}[tone]
            out[y][x] = tones[min(tone, len(tones) - 1)]
    _despeckle(out, vol, keep=round_)
    return out


def _despeckle(out, vol, keep=()) -> None:
    """A pixel with 3+ same-volume neighbours whose tone differs from all of them takes the
    tone two of them agree on. Vanilla interiors are flat; the table's local keys can leave
    single odd pixels next to eyes and corners."""
    h, w = len(out), len(out[0])
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            v = vol[y][x]
            if v == "." or v.startswith("#") or v == "k" or v in keep:
                continue
            nb = [(j, i) for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if vol[j][i] == v]
            if len(nb) < 3:
                continue
            tones = [out[j][i] for j, i in nb]
            if out[y][x] in tones:
                continue
            common = Counter(tones).most_common(1)[0]
            if common[1] >= 2:
                out[y][x] = common[0]


# ---- Rule engine (D14) --------------------------------------------------------------------
# A deterministic alternative to the table: shade each *volume* (a 4-connected run of one
# letter) by the rules STYLE.md measured. Crisper on shapes the vanilla corpus never had
# (bald alien heads, droid cylinders), where the local-key table turns to mud.
#
#   outline   every pixel on the volume's edge against transparency, or against a volume that
#             is *under* it (starts lower on the sprite; on a tie, the bigger one), in the
#             ramp's darkest tone
#   interior  the top 40% of each column's interior rows light, the rest mid; the bottom
#             interior row dark when the column is 5+ deep (shadow under a belly or a hem)
#   skin      the same with the face statistics: light above, base below, shade on the bottom
#             interior row when the column is 3+ deep, outline in skin dark
#   thin      a volume with no interior (belts, straps, 1-px hands): dark against
#             transparency, light on its top row, mid elsewhere

def _volumes(vol):
    """Label 4-connected same-letter runs; returns (label grid, {label: info})."""
    h, w = len(vol), len(vol[0])
    lab = [[-1] * w for _ in range(h)]
    info = {}
    n = 0
    for y in range(h):
        for x in range(w):
            if vol[y][x] == "." or lab[y][x] >= 0:
                continue
            ch = vol[y][x]
            stack, cells = [(x, y)], []
            lab[y][x] = n
            while stack:
                cx, cy = stack.pop()
                cells.append((cx, cy))
                for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    X, Y = cx + dx, cy + dy
                    if 0 <= X < w and 0 <= Y < h and lab[Y][X] < 0 and vol[Y][X] == ch:
                        lab[Y][X] = n
                        stack.append((X, Y))
            info[n] = {"ch": ch, "top": min(c[1] for c in cells), "size": len(cells), "cells": cells}
            n += 1
    return lab, info


def _over(a, b, info) -> bool:
    """Is volume a drawn over volume b (so a owns the outline between them)?"""
    ia, ib = info[a], info[b]
    if ia["top"] != ib["top"]:
        return ia["top"] < ib["top"]
    return ia["size"] < ib["size"] or (ia["size"] == ib["size"] and a < b)


def shade_rules(regions: list[str], materials: dict[str, str] | None = None,
                hard: dict[str, int] | None = None) -> list[list[int]]:
    materials = materials or {}
    hard = hard or {}
    h, w = len(regions), len(regions[0])
    vol = [["." if ch == "." else ("#" + ch if ch in hard else ch) for ch in row] for row in regions]
    lab, info = _volumes(vol)
    out = [[0] * w for _ in range(h)]

    def mat_of(ch):
        m = materials.get(ch, ch)
        skinlike = m.startswith("skin-")
        edge = None
        if skinlike:
            m = m[5:]
        elif "/" in m:
            m, e = m.split("/", 1)
            edge = MAT_TONES[e][-1]
        if m not in MAT_TONES:
            raise ValueError(f"letter {ch!r} maps to unknown material {m!r}")
        return m, skinlike, edge

    for L, v in info.items():
        ch = v["ch"]
        if ch.startswith("#"):
            for x, y in v["cells"]:
                out[y][x] = hard[ch[1:]]
            continue
        m, skinlike, edge = mat_of(ch)
        tones = MAT_TONES[m]
        cells = set(v["cells"])
        ring = set()
        for x, y in cells:
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                X, Y = x + dx, y + dy
                if not (0 <= X < w and 0 <= Y < h) or vol[Y][X] == ".":
                    ring.add((x, y))
                    break
                other = lab[Y][X]
                if other != L and not vol[Y][X].startswith("#") and _over(L, other, info):
                    ring.add((x, y))
                    break
        interior = cells - ring
        if len(tones) == 1:  # white / black: flat, with an optional edged silhouette
            for x, y in cells:
                at_sil = any(not (0 <= x + dx < w and 0 <= y + dy < h) or vol[y + dy][x + dx] == "."
                             for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
                out[y][x] = edge if (edge is not None and at_sil) else tones[0]
            continue
        dark, light, mid = tones[-1], tones[0], tones[1]
        if not interior:  # thin volume
            top = v["top"]
            for x, y in cells:
                at_sil = any(not (0 <= x + dx < w and 0 <= y + dy < h) or vol[y + dy][x + dx] == "."
                             for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
                out[y][x] = dark if at_sil else (light if y == top and v["size"] > 1 else mid)
            continue
        for x, y in ring:
            out[y][x] = dark
        cols = defaultdict(list)
        for x, y in interior:
            cols[x].append(y)
        for x, ys in cols.items():
            ys.sort()
            n = len(ys)
            for i, y in enumerate(ys):
                frac = i / max(1, n - 1)
                if skinlike or m == "s":
                    if n >= 2 and frac < 0.4:
                        t = tones[0]
                    elif n >= 3 and i == n - 1:
                        t = tones[2]
                    else:
                        t = tones[1]
                else:
                    if n >= 2 and frac < 0.4:
                        t = light
                    elif n >= 5 and i == n - 1:
                        t = dark
                    else:
                        t = mid
                out[y][x] = t
    return out


# ---- Round volumes: cel shading for heads, domes and bellies (owner: "how come it's not using
# cel shading on rounded heads?") -----------------------------------------------------------
# Measured on vanilla bald heads (Spenser, Sidney, the Gentleman, the Fat Man): tones are
# concentric bands from the silhouette inwards, with the light core pushed up (light from above)
# and, in the side view, toward the face (light from the front):
#
#     ......4444......      d=1 against transparency: outline (skin 4 / ramp dark)
#     ....43211234....      d=2: base (2 / mid); in the lower half of the volume: shade (3 / dark)
#     ...4211EE1124...      inside: light core (1 / light) in the upper ~60%,
#     ..422211112224..             base below it, 1-px rim of base at d=3
#     ..43EEE33EEE34..
#     ..433311113334..      the row resting on another material (chin on collar): shade
#
# A material written with "@" (s@, skin-a@, c@, skin-b!@ ...) is shaded this way per 4-connected
# volume. Hard pixels (eyes, tattoos) count as part of the volume for distances, so eyes do not
# get outlined. `facing` = "left" shifts the core toward the front (left) and darkens the back.

def shade_round(regions, materials, hard, letters, facing=None, forms=frozenset()):
    h, w = len(regions), len(regions[0])
    out = [[0] * w for _ in range(h)]
    vol = [["." if ch == "." else ("#" + ch if ch in hard else ch) for ch in row] for row in regions]
    lab, info = _volumes(vol)
    if forms:
        # Forms measure their distance from anything that is not the same form. Hard detail pixels
        # (creases, scales, glints) inside a form count as part of it, so a 1 px stroke does not
        # grow a dark ring. Where two forms touch, the one declared LATER in `materials` is in front
        # and owns the outline; the one behind keeps its own tones up to the boundary.
        order = {ch: i for i, ch in enumerate(materials)}
        def owner(y, x):  # the form letter a pixel belongs to, seeing through hard pixels
            ch = vol[y][x]
            if ch.startswith("#"):
                near = [vol[y + dy][x + dx] for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
                        if 0 <= x + dx < w and 0 <= y + dy < h and not vol[y + dy][x + dx].startswith("#") and vol[y + dy][x + dx] != "."]
                near = [c for c in near if c in forms]
                return max(near, key=lambda c: order.get(c, 0)) if near else None
            return ch if ch in forms else None
        own = [[owner(y, x) for x in range(w)] for y in range(h)]
        fdist = [[99] * w for _ in range(h)]
        q = []
        for y in range(h):
            for x in range(w):
                me = own[y][x]
                if me is None or vol[y][x].startswith("#"):
                    continue
                edge = False
                for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    X, Y = x + dx, y + dy
                    if not (0 <= X < w and 0 <= Y < h) or vol[Y][X] == ".":
                        edge = True
                    elif own[Y][X] != me:
                        other = own[Y][X]
                        # a form behind another one does not outline itself against it
                        if other is None or order.get(other, 0) < order.get(me, 0):
                            edge = True
                if edge:
                    fdist[y][x] = 1
                    q.append((x, y))
        i = 0
        while i < len(q):
            x, y = q[i]; i += 1
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                X, Y = x + dx, y + dy
                if 0 <= X < w and 0 <= Y < h and own[Y][X] == own[y][x] and fdist[Y][X] > fdist[y][x] + 1:
                    fdist[Y][X] = fdist[y][x] + 1
                    q.append((X, Y))
    # distance from transparency / the frame edge, through every opaque pixel (4-connected BFS)
    INF = 99
    dist = [[INF] * w for _ in range(h)]
    q = []
    for y in range(h):
        for x in range(w):
            if vol[y][x] == ".":
                continue
            if any(not (0 <= x + dx < w and 0 <= y + dy < h) or vol[y + dy][x + dx] == "."
                   for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                dist[y][x] = 1
                q.append((x, y))
    i = 0
    while i < len(q):
        x, y = q[i]; i += 1
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            X, Y = x + dx, y + dy
            if 0 <= X < w and 0 <= Y < h and vol[Y][X] != "." and dist[Y][X] > dist[y][x] + 1:
                dist[Y][X] = dist[y][x] + 1
                q.append((X, Y))
    for L, v in info.items():
        ch = v["ch"]
        if ch.startswith("#") or ch not in letters:
            continue
        m = materials.get(ch, ch).rstrip("!")
        skinlike = m.startswith("skin-")
        if skinlike:
            m = m[5:]
        if m not in SHADED:
            raise ValueError(f"letter {ch!r}: round shading needs a ramp (s a b c), not {m!r}")
        tones = MAT_TONES[m]
        four = len(tones) == 4
        # light, base, shade, outline as indices into this ramp
        LIGHT, BASE = tones[0], tones[1]
        SHADE = tones[2] if four else tones[2]
        OUT = tones[3] if four else tones[2]
        if not four:  # a 3-tone ramp: light, mid, dark; the shade band uses mid, the outline dark
            SHADE = tones[1]
        cells = v["cells"]
        ys = [c[1] for c in cells]
        xs = [c[0] for c in cells]
        top, bot, lft, rgt = min(ys), max(ys), min(xs), max(xs)
        is_form = ch in forms
        for x, y in cells:
            d = fdist[y][x] if is_form else dist[y][x]
            f = (y - top) / max(1, bot - top)
            fx = (x - lft) / max(1, rgt - lft)
            # side view: the core leans toward the face (left); only the far back darkens
            back = facing == "left" and fx > 0.65
            far_back = facing == "left" and fx > 0.8
            below = vol[y + 1][x] if y + 1 < h else "."
            resting = below not in (".", ch) and not below.startswith("#") and lab[y + 1][x] != L
            if d <= 1:
                t = OUT
            elif is_form:
                tall = (bot - top) >= 6
                DARK = tones[2] if four else tones[2]   # 3-tone ramps: the bottom band uses the dark tone
                MID = tones[1]
                if d == 2:
                    t = DARK if (f > 0.6 or far_back) else (LIGHT if f < 0.2 else MID)
                elif f > 0.72 and tall:
                    t = DARK if d == 3 else MID
                elif f < 0.55 and not back:
                    t = LIGHT
                else:
                    t = MID
            elif resting:
                t = SHADE if four else OUT
            elif d == 2:
                t = SHADE if (f > 0.55 or far_back) else BASE
            elif f < 0.6 and not back:
                t = LIGHT
            elif d == 3:
                t = BASE
            else:
                t = BASE if back else LIGHT
            out[y][x] = t
        # specular: vanilla bald heads carry a 1-2 px white glint on the crown (Spenser, Sidney,
        # the Gentleman); faces and hides get one, cloth and fur do not
        if skinlike or m == "s":
            core = sorted((y, x) for x, y in cells if out[y][x] == LIGHT and dist[y][x] >= 3)
            if core and (bot - top) >= 5:
                y0 = core[0][0]
                row = sorted(x for y, x in core if y == y0 + 1) or sorted(x for y, x in core if y == y0)
                yy = y0 + 1 if any(y == y0 + 1 for y, _ in core) else y0
                if facing == "left":
                    xs_ = [row[0]]
                else:
                    mid = row[len(row) // 2]
                    xs_ = [x for x in (mid - 2, mid - 1) if x in row] or [mid]
                for x in xs_:
                    out[yy][x] = 14
    return out

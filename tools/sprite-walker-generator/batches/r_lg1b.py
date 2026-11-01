"""Large companions group 1, second iteration (BRIEF4): GREATKRAYT (groudon), SANDO (kyogre),
EXOGORTH (rayquaza, rayquaza_still), TIDEWING (lugia), DAWNWING (ho_oh).

Each frame is a stack of FORMS painted back to front on a letter canvas (Cv), then shaded by the
D17 form rules (formshade): every form gets a 1 px outline in its ramp's darkest tone, a lit top,
base in the middle and shade along its bottom; the form in front owns the outline where two forms
touch, and the form behind gets a crease (shade) row under an overhang. Detail strokes (scales,
plates, teeth, glints) are composited AFTER shading, because the tool's `%` flag outlines a form
against every hard pixel inside it (a 1 px stroke comes out as a 3 px cross, a glint gets a dark
ring), and on 3-tone ramps `%` has no bottom-shade tone. The yaml therefore carries index frames.

Run from the tool folder: python batches/r_lg1b.py [names...]
"""
import math
import sys

import yaml

sys.path.insert(0, "batches")
from helpers import PK, spec  # noqa: E402

RAMP = {"s": (1, 2, 3, 4), "a": (5, 6, 7, 7), "b": (8, 9, 10, 10), "c": (11, 12, 13, 13)}
HEX = "0123456789abcdef"
LEGEND = {HEX[i]: i for i in range(1, 16)}


def L(r):
    return RAMP[r][0]


def M(r):
    return RAMP[r][1]


def S(r):
    return RAMP[r][2]


def D(r):
    return RAMP[r][3]


class Cv:
    """A region canvas: '.' is transparent; shapes paint one letter. `hard` holds detail pixels
    (x, y) -> palette index, composited after shading."""

    def __init__(s, w=32, h=32, rows=None):
        s.w, s.h = w, h
        s.g = [list(r) for r in rows] if rows else [["."] * w for _ in range(h)]
        s.hard = {}

    def put(s, x, y, ch):
        if 0 <= x < s.w and 0 <= y < s.h:
            s.g[y][x] = ch

    def get(s, x, y):
        return s.g[y][x] if 0 <= x < s.w and 0 <= y < s.h else "."

    def ell(s, cx, cy, rx, ry, ch, over=None):
        for y in range(s.h):
            for x in range(s.w):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    if over is None or s.g[y][x] in over:
                        s.g[y][x] = ch

    def rect(s, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.put(x, y, ch)

    def poly(s, pts, ch, over=None):
        n = len(pts)
        for y in range(s.h):
            for x in range(s.w):
                px, py = x + 0.5, y + 0.5
                inside = False
                for i in range(n):
                    (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                    if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
                        inside = not inside
                if inside and (over is None or s.g[y][x] in over):
                    s.g[y][x] = ch

    def line(s, pts, ch, r=0.0, over=None):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            n = int(max(abs(x2 - x1), abs(y2 - y1)) * 2) + 1
            for i in range(n + 1):
                t = i / n
                x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                if r <= 0:
                    if over is None or s.get(round(x), round(y)) in over:
                        s.put(round(x), round(y), ch)
                else:
                    for yy in range(int(y - r) - 1, int(y + r) + 2):
                        for xx in range(int(x - r) - 1, int(x + r) + 2):
                            if (xx + 0.5 - x) ** 2 + (yy + 0.5 - y) ** 2 <= r * r:
                                if over is None or s.get(xx, yy) in over:
                                    s.put(xx, yy, ch)

    def text(s, x, y, txt, skip="_"):
        """Overlay rows of letters; `skip` keeps what is there, '.' clears."""
        for j, row in enumerate(txt.strip("\n").split("\n")):
            for i, ch in enumerate(row):
                if ch != skip:
                    s.put(x + i, y + j, ch)

    # ---- detail pixels (after shading) ----
    def dot(s, x, y, idx, only=None):
        """A hard pixel; `only` restricts it to cells holding one of those letters."""
        if 0 <= x < s.w and 0 <= y < s.h and (only is None or s.g[y][x] in only):
            s.hard[(x, y)] = idx

    def stroke(s, pts, idx, only=None):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            n = int(max(abs(x2 - x1), abs(y2 - y1))) + 1
            for i in range(n + 1):
                t = i / n
                s.dot(round(x1 + (x2 - x1) * t), round(y1 + (y2 - y1) * t), idx, only)

    def mirror(s):
        """Copy the left half onto the right half (front views are symmetric), hard pixels too."""
        for y in range(s.h):
            for x in range(s.w // 2):
                s.g[y][s.w - 1 - x] = s.g[y][x]
        for (x, y), v in list(s.hard.items()):
            if x < s.w // 2:
                s.hard[(s.w - 1 - x, y)] = v

    def shift(s, dy, keep_from=None):
        """Move every row down by dy; rows >= keep_from stay where they are (feet planted)."""
        old = [r[:] for r in s.g]
        for y in range(s.h):
            if keep_from is not None and y >= keep_from:
                continue
            src = y - dy
            s.g[y] = old[src][:] if 0 <= src < s.h else ["."] * s.w
        s.hard = {(x, y if (keep_from is not None and y >= keep_from) else y + dy): v
                  for (x, y), v in s.hard.items()}
        return s

    def copy(s):
        c = Cv(s.w, s.h, s.g)
        c.hard = dict(s.hard)
        return c


def _label(g, w, h):
    lab = [[-1] * w for _ in range(h)]
    info = []
    for y in range(h):
        for x in range(w):
            if g[y][x] == "." or lab[y][x] >= 0:
                continue
            ch = g[y][x]
            n = len(info)
            stack, cells = [(x, y)], []
            lab[y][x] = n
            while stack:
                cx, cy = stack.pop()
                cells.append((cx, cy))
                for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    X, Y = cx + dx, cy + dy
                    if 0 <= X < w and 0 <= Y < h and lab[Y][X] < 0 and g[Y][X] == ch:
                        lab[Y][X] = n
                        stack.append((X, Y))
            info.append({"ch": ch, "cells": cells})
    return lab, info


def formshade(cv, mats, z, facing=None):
    """D17 form shading in the batch. mats: letter -> ramp + flags ('s', 'a!', 'b@', 'cg'):
    '!' flat plate (lit top row only, no bottom band), '@' small round part (light core, no
    bottom band), 'g' white glint on the lit top. z: letters back to front (front owns the
    outline where forms touch). facing='left': the lit core leans to the front, the back darkens.
    Returns rows of palette-index characters."""
    w, h, g = cv.w, cv.h, cv.g
    zi = {ch: i for i, ch in enumerate(z)}
    for y in range(h):
        for x in range(w):
            if g[y][x] != "." and g[y][x] not in zi:
                raise ValueError(f"letter {g[y][x]!r} at {x},{y} not in z order")
    lab, info = _label(g, w, h)
    out = [[0] * w for _ in range(h)]
    N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))

    def nb(x, y, dx, dy):
        X, Y = x + dx, y + dy
        return g[Y][X] if 0 <= X < w and 0 <= Y < h else "."

    # distance from this volume's own outline: the silhouette, or a form BEHIND it
    dist = [[99] * w for _ in range(h)]
    q = []
    for y in range(h):
        for x in range(w):
            ch = g[y][x]
            if ch == ".":
                continue
            for dx, dy in N4:
                o = nb(x, y, dx, dy)
                if o == "." or (o != ch and zi[o] < zi[ch]):
                    dist[y][x] = 1
                    q.append((x, y))
                    break
    i = 0
    while i < len(q):
        x, y = q[i]
        i += 1
        for dx, dy in N4:
            X, Y = x + dx, y + dy
            if 0 <= X < w and 0 <= Y < h and lab[Y][X] == lab[y][x] and dist[Y][X] > dist[y][x] + 1:
                dist[Y][X] = dist[y][x] + 1
                q.append((X, Y))
    for v in info:
        ch = v["ch"]
        m = mats[ch]
        ramp, flags = m[0], m[1:]
        Lt, Bs, Sh, Ot = RAMP[ramp]
        flat, small, glint = "!" in flags, "@" in flags, "g" in flags
        cells = v["cells"]
        ys = [c[1] for c in cells]
        xs = [c[0] for c in cells]
        top, bot, lft, rgt = min(ys), max(ys), min(xs), max(xs)
        tall = (bot - top) >= 6
        for x, y in cells:
            d = dist[y][x]
            f = (y - top) / max(1, bot - top)
            fx = (x - lft) / max(1, rgt - lft)
            up = nb(x, y, 0, -1)
            over_up = up != "." and up != ch and zi[up] > zi[ch]  # a front form overhangs this pixel
            side_front = any(nb(x, y, dx, dy) not in (".", ch) and zi[nb(x, y, dx, dy)] > zi[ch]
                             for dx, dy in ((1, 0), (-1, 0), (0, 1)))
            back = facing == "left" and fx > 0.62
            far_back = facing == "left" and fx > 0.82
            if d <= 1:
                t = Ot
            elif over_up:
                t = Sh
            elif side_front:
                t = Bs
            elif not flat and not small and tall and f > 0.66 and d <= 3:
                t = Sh
            elif far_back:
                t = Sh if ramp == "s" else Bs
            elif flat:
                t = Lt if (d == 2 and f < 0.25 and not back) else Bs
            elif small:
                t = Lt if (f < 0.5 and not back and (d >= 2)) else Bs
            elif f < (0.36 if tall else 0.45) and not back:
                t = Lt
            else:
                t = Bs
            out[y][x] = t
        if glint:
            core = sorted((y, x) for x, y in cells if out[y][x] == Lt and dist[y][x] >= 3)
            if core:
                y0 = core[0][0]
                row = sorted(x for y, x in core if y == y0 + 1) or sorted(x for y, x in core if y == y0)
                yy = y0 + 1 if any(y == y0 + 1 for y, _ in core) else y0
                if facing == "left":
                    xs_ = row[:2]
                else:
                    mid = row[len(row) // 2]
                    xs_ = [x for x in (mid - 2, mid - 1) if x in row] or [mid]
                for x in xs_:
                    out[yy][x] = 14
    for (x, y), v in cv.hard.items():
        out[y][x] = v
    return ["".join(HEX[v] if v else "." for v in r) for r in out]


def write(name, gi, pal, tag, replaces, kit, desc, note, accept, frames):
    spec(name, gi, pal, replaces, desc, note, {}, LEGEND, accept, frames=frames, kit=kit, root=PK)
    d = yaml.safe_load(open(f"art/{name}.yaml"))
    d["palette_tag"] = tag  # sw_<stem>.pal replaces the creature's own palette file at install
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


ONLY = set(sys.argv[1:])


# ====================================================================== GREATKRAYT (groudon)
# Greater krayt dragon, sw_groudon: s = sand hide, a = brown back ridge and bands, b = bone horns,
# chest plates and claws, c = red mouth.
# Forms plan, front (back to front; camera 45 deg above, so we see the TOP of each):
#   N body/back      s   the big back is the lit area around the head and between the shoulders
#   R dorsal ridge   a   brown saddle along the top of the back, behind the skull
#   L shoulders x2   s   upper arms, tops lit, bottom shaded where the forearms overlap
#   P chest plate    b   bone plate between the legs, bottom third shaded, plate lines
#   F forearms x2    s   lowest and nearest, claws hang off the bottom edge
#   W horns          b   fan back from the skull; the skull sits in front of their roots
#   H skull          s   crown lit, glint; eyes at 60% of the head, brow strokes above
#   S snout          s   hangs down toward the camera below the eyes
#   J jaw            s   under the snout; the black mouth line and teeth sit between them
KR_MATS = {"N": "a", "L": "s", "P": "b!", "F": "s", "W": "b", "H": "sg", "S": "s", "J": "s", "T": "a",
           "E": "s", "G": "a", "K": "s", "U": "s"}
KR_Z = ["T", "N", "U", "G", "L", "P", "K", "F", "E", "W", "H", "S", "J"]


def horn(c, base, tip, bw, ch="W"):
    """A tapered bone spike: a quad from a base of width bw to a 1 px tip."""
    (bx, by), (tx, ty) = base, tip
    dx, dy = tx - bx, ty - by
    n = math.hypot(dx, dy) or 1
    px, py = -dy / n, dx / n
    c.poly([(bx + px * bw / 2, by + py * bw / 2), (bx - px * bw / 2, by - py * bw / 2),
            (tx - px * 0.7, ty - py * 0.7), (tx + px * 0.7, ty + py * 0.7)], ch)


def krayt_front(eyes=True):
    c = Cv()
    c.ell(16, 21, 15.5, 9.5, "N")
    c.ell(6.5, 21, 5.5, 6, "L")
    c.ell(16, 26, 6.5, 5, "P")
    c.ell(5.5, 28, 5, 3.5, "F")
    horn(c, (16, 8), (16, 0), 4.5)
    horn(c, (12, 8), (9, 0.5), 4)
    horn(c, (20, 8), (23, 0.5), 4)
    horn(c, (9, 11), (4, 4), 3.5)
    horn(c, (23, 11), (28, 4), 3.5)
    c.ell(16, 10.5, 8, 5.5, "H")
    c.poly([(10.5, 13), (21.5, 13), (21, 19), (11, 19)], "S")
    c.ell(16, 18.5, 5, 3.2, "S")
    c.ell(16, 22.5, 5.5, 2.4, "J")
    # details (left half; mirrored)
    if eyes:
        for x, y in ((11, 12), (12, 12), (11, 13), (12, 13)):
            c.dot(x, y, 15)
        c.dot(12, 12, 14)
    else:
        c.stroke([(11, 13), (12, 13)], 4)
    c.stroke([(10, 11), (13, 11)], 4)  # brow
    c.dot(13, 19, 15)  # nostril
    c.stroke([(11, 21), (15, 21)], 15)  # mouth line
    for x in (12, 14):
        c.dot(x, 22, 14)  # teeth
    for x in (13, 15):
        c.dot(x, 22, 12)  # red mouth between the teeth
    c.dot(11, 22, 13)
    for x in (2, 4, 6):  # claws
        c.dot(x, 30, 14)
        c.dot(x, 31, 10)
    c.stroke([(10, 24), (15, 24)], 10, only="P")  # chest plate lines
    c.stroke([(10, 27), (15, 27)], 10, only="P")
    c.stroke([(11, 29), (15, 29)], 10, only="P")
    c.stroke([(2, 19), (4, 17), (8, 16)], 4, only="L")  # scale creases over the shoulders
    c.stroke([(1, 22), (3, 20), (7, 19)], 4, only="L")
    c.stroke([(4, 26), (7, 27)], 4, only="F")  # knuckle crease
    for x in (3, 6):  # bone spines on the back ridge behind the skull
        c.dot(x, 13, 8, only="N")
        c.dot(x, 14, 10, only="N")
    c.stroke([(1, 16), (2, 15)], 7, only="N")  # scales on the back
    c.mirror()
    return c


def krayt_side():
    c = Cv()
    c.line([(25, 22), (29, 18)], "T", r=3.0)
    c.line([(29, 18), (31.5, 12), (31.5, 6)], "T", r=2.1)
    c.ell(19, 20, 12.5, 6.5, "N")
    c.ell(19, 24, 10, 3.6, "U")
    c.ell(26.5, 26, 3, 4, "G")  # far hind leg
    c.ell(13.5, 26, 3, 4, "G")  # far foreleg
    c.ell(23, 27.5, 4, 4, "K")  # near hind leg
    c.ell(10, 27.5, 3.5, 4, "F")  # near foreleg
    c.poly([(7, 12), (14, 13), (17, 20), (10, 20)], "E")  # neck
    horn(c, (9, 7), (9.5, 1), 4)
    horn(c, (11, 8), (15, 2), 3.6)
    horn(c, (13, 10), (18.5, 4.5), 3.4)
    horn(c, (6, 7), (4, 1.5), 3.4)
    c.ell(8.5, 10.5, 6.8, 4.8, "H")
    c.poly([(3, 8.5), (9, 9), (9, 16), (0, 16.5), (0, 12)], "S")
    c.ell(4, 17.5, 4, 1.9, "J")
    # details
    for x, y in ((5, 10), (6, 10), (5, 11), (6, 11)):
        c.dot(x, y, 15)
    c.dot(6, 10, 14)
    c.stroke([(4, 9), (7, 9)], 4)
    c.dot(1, 13, 15)  # nostril
    c.stroke([(0, 16), (7, 16)], 15)  # mouth line
    for x in (1, 3, 5):
        c.dot(x, 17, 14)
    for x in (2, 4, 6):
        c.dot(x, 17, 12)
    for x in (8, 10, 12):  # near foreleg claws
        c.dot(x, 31, 14)
    for x in (21, 23, 25):
        c.dot(x, 31, 14)
    for x in (14, 18, 22, 26):  # bone spines along the back ridge
        c.dot(x, 14, 8, only="N")
        c.dot(x, 15, 10, only="N")
    for x, y in ((29, 16), (31, 10)):
        c.dot(x, y, 8, only="T")
        c.dot(x, y + 1, 10, only="T")
    c.stroke([(13, 19), (17, 18), (21, 19)], 7, only="N")  # scale creases across the back
    c.stroke([(27, 20), (29, 21)], 7, only="N")
    c.stroke([(18, 23), (22, 23)], 4, only="U")
    return c


if not ONLY or "groudon" in ONLY:
    a = krayt_front()
    b = krayt_front(eyes=False)
    s = krayt_side()
    s2 = s.copy().shift(1, keep_from=26)
    write("groudon", "gObjectEventGraphicsInfo_GroudonFront", "sw_groudon", "OBJ_EVENT_PAL_TAG_GROUDON", "groudon.png",
          "frames32x32_4",
          "GREATKRAYT: the eldest greater krayt dragon (replaces Groudon).",
          "Mockup v2 (forms): front (eyes open / shut) and side (two breathing poses); sandy hide, brown ridge and bands, bone horn crown and chest plates, toothy snout.",
          accept={"hair_rows": "a creature: the horn crown, not hair, sits above the face"},
          frames={"down": formshade(a, KR_MATS, KR_Z), "f1": formshade(b, KR_MATS, KR_Z),
                  "f2": formshade(s, KR_MATS, KR_Z, "left"), "f3": formshade(s2, KR_MATS, KR_Z, "left")})


# ====================================================================== SANDO (kyogre)
# Sando aqua monster, sw_kyogre: s = blue-grey hide, a = dark blue back, b = pale belly and fangs,
# c = red mouth.
# Forms plan, front (back to front):
#   B back dome     a   the top-down camera sees mostly the dark back, lit on its crown
#   R ridge plates  a   a row of small plates along the top of the back
#   A flippers x2   s   paddle forelimbs at the sides, webbed claws off the bottom edge
#   P belly         b   pale strip under the jaw between the flippers
#   H head          s   broad flat head in front of the dome, eyes at 60%, brow ridges above
#   J jaw           s   huge underslung jaw; black mouth line, fangs jutting up and down
SA_MATS = {"B": "ag", "R": "a@", "A": "s", "P": "b!", "H": "sg", "J": "s", "E": "a@", "T": "a", "U": "s", "F": "a",
           "K": "s", "G": "a", "N": "s"}
SA_Z = ["T", "F", "B", "U", "R", "G", "A", "P", "K", "N", "H", "E", "J"]


def sando_front():
    c = Cv()
    c.ell(16, 14, 14.5, 9.5, "B")
    for x, y in ((16, 4.5), (11, 6), (21, 6), (6.5, 9), (25.5, 9)):
        c.ell(x, y, 2.2, 2.6, "R")
    c.ell(5, 24, 4.5, 6.5, "A")
    c.ell(16, 27.5, 7.5, 4, "P")
    c.ell(16, 17.5, 10.5, 6, "H")
    c.ell(16, 24.5, 9.5, 3.5, "J")
    c.stroke([(9, 14), (12, 13)], 4)  # heavy brow
    c.stroke([(7, 17), (9, 18)], 3, only="H")  # cheek scale creases
    c.stroke([(6, 20), (8, 21)], 3, only="H")
    c.stroke([(13, 13), (15, 13)], 1, only="H")  # lit snout ridge
    # details (left half; mirrored)
    for x in (10, 11, 12):  # eye 3x2 with glint
        c.dot(x, 15, 15)
        c.dot(x, 16, 15)
    c.dot(11, 15, 14)
    c.dot(12, 16, 14)
    c.dot(13, 19, 15)  # nostril
    c.stroke([(7, 22), (15, 22)], 15)  # mouth line
    for x in (8, 11, 14):  # fangs jutting up from the jaw over the lip
        c.dot(x, 21, 14)
        c.dot(x, 20, 14)
        c.dot(x, 22, 14)
    for x in (9, 12):  # upper fangs hanging down
        c.dot(x, 23, 14)
    for x in (10, 13):
        c.dot(x, 23, 12)
    c.dot(15, 23, 11)  # lit gum
    c.stroke([(2, 29), (3, 30)], 10)  # webbed claws
    c.dot(5, 30, 10)
    c.dot(7, 30, 10)
    c.stroke([(2, 20), (4, 18)], 4, only="A")  # flipper creases
    c.stroke([(1, 24), (3, 22)], 4, only="A")
    c.stroke([(11, 27), (14, 27)], 10, only="P")  # belly plates
    c.stroke([(12, 29), (15, 29)], 10, only="P")
    c.stroke([(3, 11), (5, 12)], 7, only="B")  # back scale creases
    c.stroke([(8, 8), (10, 9)], 7, only="B")
    c.mirror()
    return c


def sando_side():
    c = Cv()
    c.line([(24, 20), (29, 17), (31.5, 12)], "T", r=2.6)
    c.poly([(27, 14), (31.5, 7), (31.5, 15)], "F")  # tail fluke
    c.ell(18, 19, 12.5, 7, "B")
    c.ell(18, 24, 11, 3.8, "U")
    for x, y in ((11, 11), (16, 10.5), (21, 11.5), (25.5, 13.5)):
        c.ell(x, y, 2.0, 2.4, "R")
    c.ell(26, 25.5, 3.2, 3.6, "G")  # far hind flipper
    c.ell(13.5, 25.5, 3.2, 3.6, "G")  # far fore flipper
    c.ell(22.5, 27.5, 4.5, 3.4, "K")  # near hind flipper (paddle)
    c.ell(9.5, 27.5, 4.5, 3.4, "A")  # near fore flipper
    c.ell(8.5, 15, 9, 5.5, "H")
    c.ell(5.5, 21, 5.5, 2.8, "J")
    # details
    for x in (3, 4, 5):
        c.dot(x, 13, 15)
        c.dot(x, 14, 15)
    c.dot(4, 13, 14)
    c.dot(5, 14, 14)
    c.stroke([(2, 12), (6, 12)], 4)  # brow
    c.stroke([(8, 16), (11, 17)], 3, only="H")  # cheek scale crease
    c.dot(1, 17, 15)  # nostril
    c.stroke([(0, 19), (10, 19)], 15)  # mouth line
    for x in (1, 4, 7):
        c.dot(x, 18, 14)
        c.dot(x, 17, 14)
        c.dot(x, 19, 14)
    for x in (2, 5):
        c.dot(x, 20, 14)
    for x in (3, 6):
        c.dot(x, 20, 12)
    c.dot(8, 20, 11)
    for x in (7, 9, 11, 13):  # webbed claws
        c.dot(x, 31, 10)
    for x in (19, 21, 23, 25):
        c.dot(x, 31, 10)
    c.stroke([(13, 17), (17, 16), (21, 17)], 7, only="B")
    c.stroke([(15, 21), (20, 20), (25, 21)], 7, only="B")
    c.stroke([(16, 25), (21, 25)], 4, only="U")
    c.stroke([(28, 11), (30, 12)], 7, only="F")
    c.stroke([(10, 22), (13, 24)], 4, only="H")  # jowl crease
    return c


if not ONLY or "kyogre" in ONLY:
    a = sando_front()
    b = a.copy().shift(1, keep_from=30)
    s = sando_side()
    s2 = s.copy().shift(1, keep_from=29)
    write("kyogre", "gObjectEventGraphicsInfo_KyogreFront", "sw_kyogre", "OBJ_EVENT_PAL_TAG_KYOGRE", "kyogre.png",
          "frames32x32_4",
          "SANDO: the greatest of the sando aqua monsters (replaces Kyogre).",
          "Mockup v2 (forms): front and side, each with a breathing bob; dark ridged back over blue-grey hide, broad head, underslung jaw with fangs, webbed flippers, finned tail.",
          accept={"hair_rows": "a sea beast: its ridged back, not hair, sits above the face"},
          frames={"down": formshade(a, SA_MATS, SA_Z), "f1": formshade(b, SA_MATS, SA_Z),
                  "f2": formshade(s, SA_MATS, SA_Z, "left"), "f3": formshade(s2, SA_MATS, SA_Z, "left")})


# ====================================================================== TIDEWING (lugia)
# Mortis's sea guardian (original), sw_lugia: s = pale belly/face plates, a = deep blue hide,
# b = teal glow (ribs, eyes), c = dark teal sail membrane.
# Forms plan, wings raised (back to front):
#   W wings x2      c   sail fins rising from the shoulders, glowing ribs (b light) along them
#   F tail flukes   a   forked fluke peeking out below the body
#   B body          a   round back seen from above, lit crown
#   P belly         s   pale plate on the lower body, plate lines
#   T feet x2       a   small, lowest
#   N neck          a   joins head to body
#   H head          a   crown lit with glint; eyes at 60% glow teal; short beak below
#   K crest fins x2 c   swept back from the skull, a glowing rib each
#   S beak          s
TW_MATS = {"W": "c", "F": "a", "B": "ag", "P": "s!", "T": "a@", "N": "a", "H": "ag", "K": "c", "S": "s@", "G": "b@"}
TW_Z = ["W", "F", "B", "P", "T", "N", "G", "K", "H", "S"]


def tidewing(up):
    c = Cv()
    if up:
        c.poly([(12, 18), (6, 4), (2, 3), (0.5, 9), (2, 17), (10, 22)], "W")
        ribs = [[(10, 19), (6, 10), (3, 5)], [(10, 20), (4, 13), (1.5, 9)], [(10, 21), (4, 17), (2, 16)]]
    else:
        c.poly([(12, 18), (6, 14), (1, 17), (0.5, 24), (4, 29), (11, 25)], "W")
        ribs = [[(10, 20), (5, 17), (2, 18)], [(10, 22), (4, 22), (1.5, 24)], [(10, 24), (6, 27), (4, 28)]]
    c.poly([(11, 25), (8, 30), (12, 31), (16, 27), (20, 31), (24, 30), (21, 25)], "F")
    c.ell(16, 21.5, 7, 6.5, "B")
    c.ell(16, 24.5, 4.5, 4.2, "P")
    c.ell(11.5, 29, 2.3, 1.8, "T")
    c.ell(20.5, 29, 2.3, 1.8, "T")
    c.rect(13, 11, 18, 18, "N")
    c.ell(16, 19.5, 2.2, 1.8, "G")  # teal Force-glow gem on the throat
    horn(c, (12.5, 8), (8, 1), 4.5, "K")
    horn(c, (19.5, 8), (24, 1), 4.5, "K")
    c.ell(16, 10.5, 5.5, 4.8, "H")
    c.poly([(13.5, 14), (18.5, 14), (16, 17.5)], "S")
    # details (left half; mirrored)
    for r in ribs:
        c.stroke(r, 8, only="W")
        c.stroke(r[:2], 9, only="W")
        c.stroke([r[0], ((r[0][0] + r[1][0]) / 2, (r[0][1] + r[1][1]) / 2)], 10, only="W")
    c.stroke([(11, 6), (9, 3)], 8, only="K")  # crest rib
    c.dot(11, 7, 10, only="K")
    for x, y in ((12, 11), (13, 11), (12, 12), (13, 12)):
        c.dot(x, y, 15)
    c.dot(13, 11, 8)  # teal glow in the eye
    c.stroke([(11, 10), (13, 10)], 7)  # brow
    c.dot(15, 15, 4)  # beak line
    c.stroke([(12, 24), (14, 24)], 3, only="P")  # belly plate lines
    c.stroke([(12, 26), (14, 26)], 3, only="P")
    c.stroke([(10, 28), (11, 29)], 7, only="T")
    c.dot(10, 30, 15)
    c.dot(12, 30, 15)
    c.stroke([(9, 17), (11, 16)], 7, only="B")  # back scale creases
    c.stroke([(9, 27), (10, 29)], 7, only="F")  # fluke rib
    c.mirror()
    return c


if not ONLY or "lugia" in ONLY:
    write("lugia", "gObjectEventGraphicsInfo_Lugia", "sw_lugia", "OBJ_EVENT_PAL_TAG_LUGIA", "lugia.png",
          "frames32x32_2",
          "TIDEWING: guardian of Mortis's seas (replaces Lugia).",
          "Mockup v2 (forms): wings raised / wings lowered; deep-blue wyvern seen from above, pale belly plates, teal sail wings on glowing ribs, swept crest fins, glowing eyes, forked fluke.",
          accept={"hair_rows": "a winged beast: its crest fins, not hair, sit above the face"},
          frames={"down": formshade(tidewing(True), TW_MATS, TW_Z), "f1": formshade(tidewing(False), TW_MATS, TW_Z)})


# ====================================================================== DAWNWING (ho_oh)
# Mortis's sky guardian (original), sw_ho_oh: s = cream glowing plumage, a = flame orange,
# b = gold, c = rose.
# Forms plan, wings raised (back to front):
#   Y/A/C wing tiers x2  b/a/c   gold tips, orange middle, rose inner tier; each tier its own
#                                 form with feather strokes along its edge
#   T tail plumes        a       flame plumes fanning below the body
#   B body               s       round back from above, lit crown, glint
#   P chest              b       gold chest plate, flat, feather lines
#   F feet x2            b
#   N neck, H head       s       crown lit, eyes at 60%, gold beak below
#   R halo rays x3       b       golden light rays fanning up from the skull, white cores
DW_MATS = {"Y": "b", "A": "a", "C": "c", "T": "a", "B": "sg", "P": "b!", "F": "b@", "N": "s", "H": "sg", "R": "b",
           "K": "b@"}
DW_Z = ["Y", "A", "C", "T", "B", "P", "N", "R", "H", "K", "F"]


def dawnwing(up):
    c = Cv()
    if up:  # tiers as bands along the wing: gold outer, orange, rose inner
        c.poly([(12, 18), (7, 3), (2, 2), (0.5, 9), (2, 19), (10, 24)], "Y")
        c.poly([(12, 18), (8, 6), (4, 5.5), (3, 11), (4, 19), (10, 24)], "A")
        c.poly([(12, 18), (9, 9), (6, 9), (5.5, 13), (6, 19), (10, 24)], "C")
        feathers = ([(4, 5), (6, 7)], [(2, 9), (4, 11)], [(2, 14), (4, 15)], [(3, 18), (5, 18)])
    else:
        c.poly([(12, 18), (5, 14), (0.5, 18), (0.5, 25), (4, 30), (11, 26)], "Y")
        c.poly([(12, 18), (6, 16.5), (3, 19.5), (3, 24), (6, 28), (11, 26)], "A")
        c.poly([(12, 18), (7.5, 18.5), (5.5, 21), (5.5, 24), (8, 26.5), (11, 26)], "C")
        feathers = ([(2, 18), (4, 19)], [(1, 22), (4, 22)], [(2, 26), (4, 25)], [(4, 29), (6, 27)])
    c.poly([(9, 24), (14, 24), (7.5, 31.5), (2.5, 29.5)], "T")  # broad flame plumes fanning out
    c.poly([(12, 25), (17, 25), (13.5, 31.5), (8, 31.5)], "T")
    c.ell(16, 21.5, 6.5, 6, "B")
    c.ell(16, 24, 4, 4, "P")
    c.ell(12, 29.5, 2, 1.6, "F")
    c.ell(20, 29.5, 2, 1.6, "F")
    c.rect(13, 12, 18, 18, "N")
    horn(c, (16, 7), (16, 0), 3.5, "R")
    horn(c, (13, 7.5), (9.5, 1), 3.2, "R")
    horn(c, (19, 7.5), (22.5, 1), 3.2, "R")
    c.ell(16, 10.5, 5.5, 4.5, "H")
    c.poly([(13, 13.5), (19, 13.5), (16, 18)], "K")
    # details (left half; mirrored)
    for pts in feathers:
        c.stroke(pts, 10, only="Y")
    for pts in feathers:
        c.stroke([(x + 2, y + (0 if up else 1)) for x, y in pts], 7, only="A")
    c.stroke([(16, 1), (16, 5)], 14)  # white light cores in the halo rays
    c.stroke([(10, 2), (12, 5)], 14)
    for x, y in ((12, 11), (13, 11), (12, 12), (13, 12)):
        c.dot(x, y, 15)
    c.dot(13, 11, 14)
    c.stroke([(14, 15), (15, 15)], 10)  # beak line
    c.stroke([(13, 23), (15, 23)], 10, only="P")  # chest feather lines
    c.stroke([(13, 25), (15, 25)], 10, only="P")
    c.dot(11, 31, 10)
    c.dot(13, 31, 10)
    c.stroke([(10, 26), (5, 30)], 7, only="T")  # plume ribs
    c.stroke([(14, 27), (11, 31)], 7, only="T")
    c.stroke([(5, 28), (4, 29)], 11, only="T")  # rose heat along the plume tips
    c.stroke([(10, 29), (9, 30)], 11, only="T")
    c.mirror()
    return c


if not ONLY or "ho_oh" in ONLY:
    write("ho_oh", "gObjectEventGraphicsInfo_HoOh", "sw_ho_oh", "OBJ_EVENT_PAL_TAG_HO_OH", "ho_oh.png",
          "frames32x32_2",
          "DAWNWING: guardian of Mortis's skies (replaces Ho-Oh).",
          "Mockup v2 (forms): wings raised / wings lowered; glowing cream sun-bird from above, halo of three light rays, gold beak and chest, rose-orange-gold wing tiers, flame tail plumes.",
          accept={"hair_rows": "a bird: its halo crest, not hair, sits above the face"},
          frames={"down": formshade(dawnwing(True), DW_MATS, DW_Z), "f1": formshade(dawnwing(False), DW_MATS, DW_Z)})


# ====================================================================== EXOGORTH (rayquaza, rayquaza_still)
# Space slug, npc_4: c = grey hide, s = peach belly plates and lips, b = pink maw, a = navy throat
# and deep creases.
# Forms plan (back to front): the body is a chain of RING SEGMENTS, one form each (so every ring
# gets its own outline and lit top), painted tail first so each ring sits over the one behind it;
# peach belly plates run along the underside of every ring; then the blunt head (lit crown,
# glint), the eyes at 60% of the head, and the maw (pink form, navy throat, white fangs on the rim).
import string  # noqa: E402

POOL = [ch for ch in string.ascii_letters + string.digits]
EX_MATS = {}
EX_Z = []


def ring(c, x, y, r, mats, z):
    ch = POOL[len(z)]
    prev = z[-1] if z else None
    mats[ch] = "c"
    z.append(ch)
    c.ell(x, y, r, r * 0.92, ch)
    if prev:  # deepest crease: this ring's outline goes navy where it sits on the ring behind
        for yy in range(c.h):
            for xx in range(c.w):
                if c.g[yy][xx] == ch and c.get(xx, yy + 1) == prev and c.get(xx, yy - 1) == ch:
                    c.dot(xx, yy, 7)
    # peach belly plate along the underside of the ring
    yy = round(y + r * 0.92) - 2
    n = int(r * 0.5)
    for dx in range(-n, n + 1):
        c.dot(round(x) + dx, yy, 1 if dx == -n else (3 if dx == n else 2), only=ch)
    return ch


def worm(c, pts, r0, r1, mats, z, step=0.95):
    """Rings along a polyline, radius r0 at the tail end to r1 at the head end."""
    samples = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) * 4))
        for i in range(n):
            t = i / n
            samples.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
    samples.append(pts[-1])
    Ls = [0.0]
    for i in range(1, len(samples)):
        Ls.append(Ls[-1] + math.hypot(samples[i][0] - samples[i - 1][0], samples[i][1] - samples[i - 1][1]))
    total = Ls[-1]
    nxt = 0.0
    for i, (x, y) in enumerate(samples):
        if Ls[i] >= nxt:
            r = r0 + (r1 - r0) * Ls[i] / total
            ring(c, x, y, r, mats, z)
            nxt = Ls[i] + r * step
    return samples


def spiral(cx, cy, rx, ry, start, turns, n=80, shrink=0.2):
    pts = []
    for i in range(n + 1):
        a = start + 2 * math.pi * turns * i / n
        k = 1 - shrink * i / n
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


def slug_head(c, cx, cy, rx, ry, mode, mats, z):
    mats.update({"Q": "cg", "P": "s@", "M": "b", "X": "a"})
    z.extend(["Q", "P", "M", "X"])
    c.ell(cx, cy, rx, ry, "Q")
    if mode == "open":
        c.ell(cx, cy + ry * 0.3, rx * 0.72, ry * 0.6, "P")
        c.ell(cx, cy + ry * 0.3, rx * 0.56, ry * 0.46, "M")
        c.ell(cx, cy + ry * 0.4, rx * 0.26, ry * 0.2, "X")
        for i in range(10):  # fangs on the rim of the maw
            a = 2 * math.pi * i / 10
            x = round(cx + rx * 0.55 * math.cos(a))
            y = round(cy + ry * 0.3 + ry * 0.45 * math.sin(a))
            c.dot(x, y, 14)
            if math.sin(a) < 0:
                c.dot(x, y + 1, 14)  # upper fangs hang down
    else:
        y = round(cy + ry * 0.42)
        c.ell(cx, y, rx * 0.42, ry * 0.36, "P")  # puckered round maw, shut
        cx_ = round(cx)
        c.dot(cx_, y, 15)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            c.dot(cx_ + dx, y + dy, 10)
        for dx, dy in ((-2, -2), (2, -2), (-2, 2), (2, 2), (-3, 0), (3, 0)):  # radiating lip creases
            c.dot(cx_ + dx, y + dy, 4, only="P")
        c.dot(cx_ - 1, y - 1, 9)
        c.dot(cx_ + 1, y + 1, 9)
        c.dot(cx_ - 1, y + 1, 14)
        c.dot(cx_ + 1, y - 1, 14)
    if mode != "asleep":
        for sx in (-1, 1):
            ex = round(cx + sx * rx * 0.5)
            ey = round(cy - ry * 0.25)
            for x in (ex - 1, ex, ex + 1):
                c.dot(x, ey, 15)
                c.dot(x, ey + 1, 15)
            c.dot(ex - (1 if sx < 0 else 0), ey, 14)
            c.stroke([(ex - 1, ey - 1), (ex + 1, ey - 1)], 13)  # brow fold
            c.stroke([(ex - 1, ey + 2), (ex + 1, ey + 2)], 6)  # navy socket under the eye
    else:
        for sx in (-1, 1):
            ex = round(cx + sx * rx * 0.5)
            ey = round(cy - ry * 0.25)
            c.stroke([(ex - 1, ey + 1), (ex + 1, ey + 1)], 7)  # closed lids
            c.stroke([(ex - 1, ey + 2), (ex + 1, ey + 2)], 6)


def exo_coiled(mode):
    c = Cv(64, 64)
    mats, z = {}, []
    pts = spiral(31.5, 31, 14, 10.5, math.pi * 0.45, 1.2)
    worm(c, [(46, 47), (48, 44)] + pts[:1], 1.5, 2.5, mats, z)  # tail tip curling out
    worm(c, pts, 2.8, 5.2, mats, z)
    slug_head(c, 31.5, 34, 8, 7.5, mode, mats, z)
    return formshade(c, mats, z)


def exo_raised(dy=0):
    c = Cv(64, 64)
    mats, z = {}, []
    pts = spiral(31.5, 38 + dy, 13.5, 8, math.pi * 0.45, 1.05)
    worm(c, [(46, 52 + dy), (48, 49 + dy)] + pts[:1], 1.5, 2.5, mats, z)
    worm(c, pts, 3.0, 5.0, mats, z)
    worm(c, [(31.5, 40 + dy), (31.5, 32 + dy), (31.5, 24 + dy)], 5.0, 5.6, mats, z)
    slug_head(c, 31.5, 17 + dy, 9, 8.5, "open", mats, z)
    return formshade(c, mats, z)


def exo_flying():
    c = Cv(64, 64)
    mats, z = {}, []
    worm(c, [(22, 64), (19, 57), (22, 50), (30, 44), (32, 36), (28, 28), (26, 20), (28, 15)], 1.8, 5.6, mats, z)
    slug_head(c, 28.5, 9.5, 8, 7.8, "open", mats, z)
    return formshade(c, mats, z)


EXO_ACC = {"hair_rows": "a space slug: no hair", "skin_tones": "the peach ramp is only the belly plates and lips"}

if not ONLY or "rayquaza" in ONLY:
    fr = {"down": exo_coiled("asleep"), "f1": exo_coiled("awake"), "f2": exo_coiled("open"),
          "f3": exo_raised(), "f4": exo_flying()}
    write("rayquaza", "gObjectEventGraphicsInfo_Rayquaza", "npc_4", "OBJ_EVENT_PAL_TAG_NPC_4", "rayquaza.png",
          "frames64x64_5",
          "EXOGORTH: the space slug that calms the other two titans (replaces Rayquaza).",
          "Mockup v2 (forms): coiled asleep / awake / maw open, reared up, rising; grey ringed hide with every ring its own form, peach belly plates, pink maw with fangs and a navy throat. Stays on NPC_4.",
          accept=EXO_ACC, frames=fr)

if not ONLY or "rayquaza_still" in ONLY:
    write("rayquaza_still", "gObjectEventGraphicsInfo_RayquazaStill", "npc_4", "OBJ_EVENT_PAL_TAG_NPC_4", "rayquaza_still.png",
          "frames64x64_1",
          "EXOGORTH (still): the space slug reared up from its coil (replaces the still Rayquaza).",
          "Mockup v2 (forms): reared up from its coil, maw open; same rings and maw as the animated sheet. Stays on NPC_4.",
          accept=EXO_ACC, frames={"down": exo_raised(dy=14)})

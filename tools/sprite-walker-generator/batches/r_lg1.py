"""Large companions group 1 (mockups): GREATKRAYT (groudon), SANDO (kyogre), EXOGORTH (rayquaza,
rayquaza_still), TIDEWING (lugia), DAWNWING (ho_oh). Whole frames drawn as material regions with a
small canvas helper; the shader picks the tones. Run from the tool folder: python batches/r_lg1.py
"""
import sys

import yaml

sys.path.insert(0, "batches")
from helpers import PK, spec  # noqa: E402


class Cv:
    """A region canvas: '.' is transparent; shapes paint one letter."""

    def __init__(s, w=32, h=32, rows=None):
        s.w, s.h = w, h
        s.g = [list(r) for r in rows] if rows else [["."] * w for _ in range(h)]

    def put(s, x, y, ch):
        if 0 <= x < s.w and 0 <= y < s.h:
            s.g[y][x] = ch

    def ell(s, cx, cy, rx, ry, ch, over=None):
        for y in range(s.h):
            for x in range(s.w):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
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

    def line(s, pts, ch, r=0.0):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            n = int(max(abs(x2 - x1), abs(y2 - y1)) * 2) + 1
            for i in range(n + 1):
                t = i / n
                x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                if r <= 0:
                    s.put(round(x), round(y), ch)
                else:
                    for yy in range(int(y - r) - 1, int(y + r) + 2):
                        for xx in range(int(x - r) - 1, int(x + r) + 2):
                            if (xx - x) ** 2 + (yy - y) ** 2 <= r * r:
                                s.put(xx, yy, ch)

    def text(s, x, y, txt, skip="_"):
        """Overlay rows; `skip` keeps what is there, '.' clears."""
        for j, row in enumerate(txt.strip("\n").split("\n")):
            for i, ch in enumerate(row):
                if ch != skip:
                    s.put(x + i, y + j, ch)

    def mirror(s):
        """Copy the left half onto the right half (front views are symmetric)."""
        for y in range(s.h):
            for x in range(s.w // 2):
                s.g[y][s.w - 1 - x] = s.g[y][x]

    def shift(s, dy, keep_from=None):
        """Move every row down by dy; rows >= keep_from stay where they are."""
        old = [r[:] for r in s.g]
        for y in range(s.h):
            if keep_from is not None and y >= keep_from:
                continue
            src = y - dy
            s.g[y] = old[src][:] if 0 <= src < s.h else ["."] * s.w
        return s

    def copy(s):
        return Cv(s.w, s.h, s.g)

    def rows(s):
        return ["".join(r) for r in s.g]


def write(name, gi, pal, tag, replaces, kit, desc, note, materials, legend, accept, frames):
    spec(name, gi, pal, replaces, desc, note, materials, legend, accept, frames=frames, kit=kit, root=PK)
    d = yaml.safe_load(open(f"art/{name}.yaml"))
    d["palette_tag"] = tag  # sw_<stem>.pal replaces the creature's own palette file at install
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


ONLY = set(sys.argv[1:])

# ====================================================================== GREATKRAYT (groudon)
# Greater krayt dragon: a sand-coloured serpentine titan with a crown of bone horns fanning back
# from the skull, brown bands across the back, short clawed forelegs and a long toothy snout.
def half(text):
    """A symmetric front view from its left half (16 columns)."""
    rows = text.strip("\n").split("\n")
    assert all(len(r) == 16 for r in rows) and len(rows) == 32, [len(r) for r in rows]
    return Cv(rows=[r + r[::-1] for r in rows])


def shut(f, lid, line):
    """Eyes shut: the eye pixels (k, e) become the lid letter, the lowest eye row a dark line."""
    g = f.copy()
    cells = [(x, y) for y in range(g.h) for x in range(g.w) if g.g[y][x] in "ke"]
    low = max(y for _, y in cells)
    for x, y in cells:
        g.g[y][x] = line if y == low else lid
    return g


def krayt():
    return half("""
................
...........h....
.....h....hh....
.....hh...hhh...
......hh..hhh..p
......hhh.hhhKKp
..KKKKhhhhhhhKKK
.hhKKKKhhhhhhHHH
.hhhhKKKhhhhHHHH
KKhhhhhKhhhHHHHH
KKKKhhhhhoHHHHHH
KKKKKKKKoHHHHHHH
KKzKKKKKoBBBHHHH
KKKzKKKKkkBHHHyy
LKKKKKKKekHHHHHH
LLKKKKKKoHHHHHHH
LLLKKKKKKoHHHHyy
LLLLKKKKKoHHHHHH
LLLLLKKKKoMMMMMM
LLLLLLKKKKoMMMyy
LLLLLLLKKKoMMMMM
LyyLLLLLKKoMMMMM
LLLyyLLLKKoMMMyy
LLLLLLLLLKKoMMMM
.LLLLLLLLKKoMMnM
.LyyLLLLLLKoMMMM
.LLLyyLLLLKtRRRR
..LLLLLLLLLoRtRR
..LLLLLLLL..oMMM
..LLLLLLL....ooo
.cLcLcLc........
................""")


def krayt_side():
    return Cv(rows="""
................................
..............hh................
...........h...hh...............
...........hh...hhh....hh.......
............hh...hhh.hhh........
.............hh..hhhhhh.........
.............hhhhhhhhh..........
..........HHHHhhhhhhKKKKK.......
........HHHHHHHhhhKKKzKKKKK.....
.......HHHHHHHHhKKKKzKKKKzKKK...
......HHHHHHHHHoKKKKKzKKKKzKKK..
....BBBBHHHHHHHoKKKKKKzKKKKzKKK.
..MMMMBkkHHHHHHoKKKKKKKKKKKKKKK.
MMMMMMMekHHHHHoKKKKKKKKKKKKKKKKK
MnMMMMMMHHHHHHoKKKKKKKKKKKKKKKKK
MMMMMMMMMHHHHoKKKKKKKKKKKKKKKKKK
MMMMMMMMMMMHoKKKKKKKKKKKKKKKKKKK
tRtRtRtRMMMoKKKKKKKKKKKKKKKKKKKT
RRRRRRRRRooKKKKKKKKKKKKKKKKKKKTT
MMMMMMMMMoKKKKKKKKKKKKKKKKKKKKTT
.MMMMMMMoLLLLLKKKKKKKKKKKKKKKTTT
..ooooo.LLLLLLKKKKKKKKKKKKKKTTT.
.......LLLLLLLLKKKKKKKKKLLLLTTT.
.......LLLLLLLLKKKKKKKKLLLLLTT..
.......LLLLLLLL.....KKLLLLLLTT..
........LLLLLLL......LLLLLLLTTT.
........LLLLLL.......LLLLLLL.TTT
.......LLLLLLL.......LLLLLL...TT
.......LLLLLLL......LLLLLLL.TTTT
.......LLLLLLL......LLLLLLLTTT..
......cLcLcLc.......cLcLcLc.....
................................""".strip("\n").split("\n"))


if not ONLY or "groudon" in ONLY:
    a = krayt()
    b = shut(a, "B", "x")
    s = krayt_side()
    s2 = s.copy().shift(1, keep_from=24)
    write("groudon", "gObjectEventGraphicsInfo_GroudonFront", "sw_groudon", "OBJ_EVENT_PAL_TAG_GROUDON", "groudon.png",
          "frames32x32_4",
          "GREATKRAYT: the eldest greater krayt dragon (replaces Groudon).",
          "Mockup: front (eyes open / shut) and side (two breathing poses); sandy hide, brown bands, bone horn crown.",
          materials={"K": "a", "A": "a", "p": "b", "L": "s!", "H": "s@", "M": "s@", "B": "a", "h": "b", "R": "c", "c": "b", "T": "s!"},
          legend={"k": 15, "e": 14, "n": 15, "t": 14, "x": 4, "o": 4, "z": 7, "y": 3},
          accept={"hair_rows": "a creature: the horn crown, not hair, sits above the face"},
          frames={"down": a.rows(), "f1": b.rows(), "f2": s.rows(), "f3": s2.rows()})


# ====================================================================== SANDO (kyogre)
# Sando aqua monster: a whale-sized Naboo sea beast, blue-grey hide, a dark back with ridge plates,
# a huge underslung jaw whose white fangs jut up over the snout, tiny eyes, paddle flippers and a
# fluked tail.
def sando(flip=0):
    f = half("""
................
................
..........f.....
.........fff....
.........ffffTTT
..........ffTTTT
........KKKKKKdd
......KKKKKKKKKK
....KKKKKKKKKKdd
...KKKKKKKKKKKKK
..KKKKKKKKKKKKdd
.KKKKKKKKKKKKKKK
.KKKKKKKKHHHHHHH
KKKKKKKHHHHHHHHH
AAKKKKHHGGGHHHHH
AAAKKoHkkGHHHHHH
AAAAKoHekHHHHHHH
AAAAKoHHHHHHHHHH
AAAAAKoHHHHHHHHH
.AAAAKoHHHHHnHHH
.AAAAAKoHHHHHHHH
..AAAAKotHHHHHHH
..AAAAKotooooRRt
..AAAAAoJJJJJJJJ
..AAAAAoJJJJJJJJ
...AAAAoJJJJJJJJ
...AAAAAoJJJJJJJ
..AAAAAAoBBBBBBB
.AAAAAAA.oBBBBBB
.AcAcAcA..ooBBBB
..c.c.c.....oooo
................""")
    if flip:  # breathing bob: body one row lower, claws planted
        f.shift(1, keep_from=29)
    return f


def sando_side():
    return Cv(rows="""
................................
................................
................................
................................
................................
................................
..........dd.dd.................
........KKKKKKKdd...............
......KKKKKKKKKKKdd.............
....KKKKKKKKKKKKKKKdd...........
...HHHHKKKKKKKKKKKKKKKd.........
..HHHHHHHKKKKKKKKKKKKKKKK.......
.HHHGGGHHHKKKKKKKKKKKKKKKKK.....
.HHHkkGHHHHKKKKKKKKKKKKKKKKKK...
HHHHekHHHHHKKKKKKKKKKKKKKKKKKTff
HnHHHHHHHHHHKKKKKKKKKKKKKKKKTTff
HHHHHHHHHHHHKKKKKKKKKKKKKKKKTfff
RtRRtoHHHHHHKKKKKKKKKKKKKKKK.fff
otJJtoHHHHHHKKKKKKKKKKKKKKK...ff
JJJJJJoHHHHKKKKKKKKKKKKKKK......
JJJJJJJoKAAAAKKKKKKKKKKKKK......
BBBBBBBoAAAAAAoBBBBBBBBBB.......
.BBBBBBoAAAAAAoBBBBBBBBB........
..ooBBoAAAAAAoBBBBBBBBB.........
....oooAAAAAAooooooooo..........
.......AAAAAA...................
......AAAAAA....................
.....AAAAAA.....................
.....AAAAAA.....................
....AAAAAAA.....................
....AcAcAcA.....................
....c.c.c.......................""".strip("\n").split("\n"))


if not ONLY or "kyogre" in ONLY:
    a = sando()
    b = sando(flip=1)
    s = sando_side()
    s2 = s.copy().shift(1, keep_from=29)
    write("kyogre", "gObjectEventGraphicsInfo_KyogreFront", "sw_kyogre", "OBJ_EVENT_PAL_TAG_KYOGRE", "kyogre.png",
          "frames32x32_4",
          "SANDO: the greatest of the sando aqua monsters (replaces Kyogre).",
          "Mockup: front and side, each with a breathing bob; blue-grey hide, dark ridged back, webbed claws, white fangs jutting from the underbite.",
          materials={"K": "a", "d": "a", "H": "s@", "J": "s@", "B": "b", "A": "s!", "f": "a", "T": "a", "R": "c", "G": "a", "c": "b", "F": "s!"},
          legend={"k": 15, "e": 14, "t": 14, "o": 4, "n": 15},
          accept={"hair_rows": "a sea beast: its ridged back, not hair, sits above the face"},
          frames={"down": a.rows(), "f1": b.rows(), "f2": s.rows(), "f3": s2.rows()})


# ====================================================================== EXOGORTH (rayquaza, rayquaza_still)
# Space slug: a colossal grey ringed worm from the asteroid field, coiled on itself, its blunt head
# opening into a round pink maw ringed with jagged white teeth. NPC_4 (C greys for the hide, B pink
# for the maw, skin peach for the belly plates, A navy for the deep creases).
import math  # noqa: E402


def tube(cv, pts, r0, r1, letters="W", seg=4.0, belly=None, crease="z"):
    """Paint a ringed worm along a polyline, radius r0 at the tail end to r1 at the head end.
    Later samples paint over earlier ones (the head end is on top); each pixel then takes a
    crease (ring line) when the sample that painted it sits on a segment boundary."""
    samples = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) * 3))
        for i in range(n):
            t = i / n
            samples.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
    samples.append(pts[-1])
    L = 0.0
    owner = {}
    for i, (x, y) in enumerate(samples):
        if i:
            L += math.hypot(x - samples[i - 1][0], y - samples[i - 1][1])
        r = r0 + (r1 - r0) * i / max(1, len(samples) - 1)
        for yy in range(int(y - r) - 1, int(y + r) + 2):
            for xx in range(int(x - r) - 1, int(x + r) + 2):
                if (xx - x) ** 2 + (yy - y) ** 2 <= r * r:
                    cv.put(xx, yy, letters[0])
                    owner[(xx, yy)] = i
    if crease:
        Ls = [0.0]
        for i in range(1, len(samples)):
            Ls.append(Ls[-1] + math.hypot(samples[i][0] - samples[i - 1][0], samples[i][1] - samples[i - 1][1]))
        for (xx, yy), i in owner.items():
            if not (0 <= xx < cv.w and 0 <= yy < cv.h) or cv.g[yy][xx] != letters[0]:
                continue
            r = r0 + (r1 - r0) * i / max(1, len(samples) - 1)
            lo = max(0, i - int(r * 3) - 3)
            j = min(range(lo, i + 1), key=lambda j: (xx - samples[j][0]) ** 2 + (yy - samples[j][1]) ** 2)
            d2 = (xx - samples[j][0]) ** 2 + (yy - samples[j][1]) ** 2
            if (Ls[j] % seg) < 0.75 and d2 < (r - 1.4) ** 2:
                cv.g[yy][xx] = crease
    return samples


def coil(cv, cx, cy, rx, ry, thick, start=0.0, turns=1.0, letters="W", seg=5.0, r_end=None):
    """A spiral coil seen from above at 3/4: an ellipse path traced from angle `start`."""
    pts = []
    n = int(64 * turns)
    for i in range(n + 1):
        a = start + 2 * math.pi * turns * i / n
        k = 1 - 0.18 * i / n  # spiral inwards a little
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return tube(cv, pts, thick, r_end or thick, letters, seg)


def slug_head(cv, cx, cy, rx, ry, mode):
    """Blunt worm head facing the camera. mode: asleep, awake, open."""
    cv.ell(cx, cy, rx, ry, "H")
    if mode == "open":
        cv.ell(cx, cy + 1, rx * 0.72, ry * 0.68, "L")
        cv.ell(cx, cy + 1, rx * 0.55, ry * 0.5, "M")
        cv.ell(cx, cy + 1.5, rx * 0.22, ry * 0.2, "x")
        # jagged teeth around the rim of the maw
        for i in range(12):
            a = 2 * math.pi * i / 12
            cv.put(round(cx + rx * 0.55 * math.cos(a)), round(cy + 1 + ry * 0.5 * math.sin(a)), "t")
    else:
        y = round(cy + ry * 0.35)
        cv.ell(cx, y, rx * 0.66, 2.3, "L")  # puckered fleshy lips
        cv.ell(cx, y, rx * 0.42, 1.1, "M")  # the pink maw showing through
        for x in range(round(cx - rx * 0.3), round(cx + rx * 0.3) + 1):
            cv.put(x, y, "x")
        for x in (round(cx - rx * 0.3), round(cx), round(cx + rx * 0.3)):
            cv.put(x, y + 1, "t")
    if mode != "asleep":
        for dx in (-rx * 0.5, rx * 0.5):
            cv.put(round(cx + dx), round(cy - ry * 0.4), "k")
            cv.put(round(cx + dx), round(cy - ry * 0.4) - 1, "e")


def underside(cv, body="WT", hard="y"):
    """Shade from above: the lowest two rows of every body run go to the mid grey."""
    for y in range(cv.h - 1, -1, -1):
        for x in range(cv.w):
            if cv.g[y][x] in body:
                b1 = cv.g[y + 1][x] if y + 1 < cv.h else "."
                b2 = cv.g[y + 2][x] if y + 2 < cv.h else "."
                b3 = cv.g[y + 3][x] if y + 3 < cv.h else "."
                if b1 not in body + hard + "z" and b1 != ".":
                    cv.g[y][x] = hard
                elif b1 != "." and (b2 == "." or b3 == "."):
                    cv.g[y][x] = hard


def exo_coiled(mode):
    cv = Cv(64, 64)
    coil(cv, 31.5, 31, 13, 10, 5.0, start=math.pi * 0.5, turns=1.15, r_end=4.0)
    tube(cv, [(42, 41), (46, 44), (44, 46), (39, 45)], 3.0, 1.2, letters="T", seg=3.0)  # tail tip
    underside(cv)
    slug_head(cv, 31.5, 34, 7.5, 7, mode)
    return cv


def exo_raised(dy=0):
    cv = Cv(64, 64)
    coil(cv, 31.5, 37 + dy, 13, 7.5, 4.6, start=math.pi * 0.5, turns=1.0, r_end=4.2)
    tube(cv, [(44, 42 + dy), (47, 45 + dy), (43, 46 + dy)], 2.6, 1.2, letters="T", seg=3.0)
    tube(cv, [(31.5, 40 + dy), (31.5, 32 + dy), (31.5, 22 + dy)], 5.2, 5.6, seg=4.5)
    underside(cv)
    slug_head(cv, 31.5, 17 + dy, 8.5, 8, "open")
    return cv


def exo_flying():
    cv = Cv(64, 64)
    tube(cv, [(22, 63), (19, 57), (22, 50), (30, 44), (32, 36), (28, 28), (26, 20), (28, 14)], 2.0, 5.5, seg=4.5)
    underside(cv)
    slug_head(cv, 28.5, 9, 7.5, 7.5, "open")
    return cv


EXO_MAT = {"W": "c@", "T": "c@", "H": "a@", "L": "s", "M": "b"}
EXO_LEG = {"x": 7, "t": 14, "e": 1, "k": 15, "z": 13, "y": 12}
EXO_ACC = {"hair_rows": "a space slug: no hair", "skin_tones": "the peach ramp is only the belly plates"}

if not ONLY or "rayquaza" in ONLY:
    fr = {"down": exo_coiled("asleep").rows(), "f1": exo_coiled("awake").rows(), "f2": exo_coiled("open").rows(),
          "f3": exo_raised().rows(), "f4": exo_flying().rows()}
    write("rayquaza", "gObjectEventGraphicsInfo_Rayquaza", "npc_4", "OBJ_EVENT_PAL_TAG_NPC_4", "rayquaza.png",
          "frames64x64_5",
          "EXOGORTH: the space slug that calms the other two titans (replaces Rayquaza).",
          "Mockup: coiled asleep / awake / maw open, reared up, rising; grey ringed hide, peach belly plates, pink maw ringed with teeth.",
          materials=EXO_MAT, legend=EXO_LEG, accept=EXO_ACC, frames=fr)

if not ONLY or "rayquaza_still" in ONLY:
    write("rayquaza_still", "gObjectEventGraphicsInfo_RayquazaStill", "npc_4", "OBJ_EVENT_PAL_TAG_NPC_4", "rayquaza_still.png",
          "frames64x64_1",
          "EXOGORTH (still): the space slug reared up from its coil (replaces the still Rayquaza).",
          "Mockup: reared up from its coil, maw open; same hide and maw as the animated sheet.",
          materials=EXO_MAT, legend=EXO_LEG, accept=EXO_ACC, frames={"down": exo_raised(dy=14).rows()})


# ====================================================================== TIDEWING (lugia)
# Mortis's sea guardian (original): a deep-blue sea wyvern with a pale belly, broad sail-fin wings of
# dark teal membrane strung on glowing ribs, a swept-back finned crest, glowing teal eyes and a
# forked tail fluke. Psychic/flying: the glow is the Force light of Mortis, not Lugia's white.
TIDE_BODY = """
................
................
................
................
................
.........c......
.........cc..HHH
..........cHHHHH
..........cHHHHH
...........HgkHH
...........HkkHH
............HSSS
.............SSS
.............NNN
.............NNN
............BBNN
...........BBBPP
..........BBBBPP
.........BBBBPPP
........BBBBBPPP
........BBBBBPPP
........BBBBBBPP
........BBBBBBPP
.........BBBBBBB
.........BBBBBBB
..........BBBBBB
.......FF..BBBBB
......FFFF..BBBB
......FFFFF.FFFF
.......FFFF.FFF.
................
................"""

TIDE_UP = """
................
................
................
................
................
................
...WW...........
..WWWW..........
..WWWWW.........
..WWWWWW........
..WWWWWWW.......
..WWWWWWWW......
..GWWWWWWWW.....
..GWWWWWWWWW....
...GWWWWWWWW....
...GWWWWWWWW....
....GWWWWWW.....
....GGWWWW......
.....GGWW.......
.......G........"""

TIDE_DOWN = """
................
................
................
................
................
................
................
................
................
................
................
................
................
................
................
....WWW.........
.WWWWWWWW.......
WWWWWWWWWW......
WWWWWWWWWWW.....
.WWWWWWWWWW.....
.GWWWWWWWWW.....
..GGWWWWWW......
....GGGWW.......
.......G........"""


def tidewing(up):
    f = half(TIDE_BODY)
    f.text(0, 0, TIDE_UP if up else TIDE_DOWN, skip=".")
    ribs = ([[(10, 15), (7, 11), (4, 7)], [(10, 16), (6, 15), (3, 13)], [(10, 17), (7, 18)]] if up else
            [[(9, 18), (5, 17), (1, 17)], [(9, 19), (5, 20), (2, 20)], [(9, 20), (6, 22)]])
    for r in ribs:
        f.line(r, "r")
    f.mirror()
    return f


if not ONLY or "lugia" in ONLY:
    write("lugia", "gObjectEventGraphicsInfo_Lugia", "sw_lugia", "OBJ_EVENT_PAL_TAG_LUGIA", "lugia.png",
          "frames32x32_2",
          "TIDEWING: guardian of Mortis's seas (replaces Lugia).",
          "Mockup: wings raised / wings lowered; deep-blue wyvern, pale belly, teal sail-fin wings on glowing ribs, finned crest, glowing eyes, forked fluke.",
          materials={"W": "c@", "G": "b", "H": "a@", "S": "s@", "B": "a@", "N": "a", "P": "s", "c": "b", "F": "c"},
          legend={"r": 8, "g": 8, "k": 15, "n": 9},
          accept={"hair_rows": "a winged beast: its finned crest, not hair, sits above the face"},
          frames={"down": tidewing(True).rows(), "f1": tidewing(False).rows()})


# ====================================================================== DAWNWING (ho_oh)
# Mortis's sky guardian (original): a radiant sun-bird whose feathers shine with light. A glowing
# white-gold body, a halo crest of three golden light rays, a short gold beak, wings in tiers of
# rose, flame orange and shining gold tips, and a fan of flame tail plumes.
DAWN_BODY = """
................
...............y
.........y.....y
.........yy....y
..........yy...y
...........yy..y
............yyyy
............HHHH
...........HHHHH
...........HHeHH
...........HHkHH
...........HHHHK
............RRRK
...........RRRRR
..........RRRPPP
..........RRPPPP
.........RRRPPPP
.........RRRPPPP
.........RRRPPPP
.........RRRRPPP
..........RRRPPP
..........RRRRPP
...........RRRRR
..........TTRRRR
........TTTTTTTT
.......TTTTTTTTT
......TTTTTYYTTT
......TYYTYYYTYY
.......YY.YY..YY
................
................
................"""

DAWN_UP = """
................
................
................
................
...WW...........
.WWWWW..........
.WWWWWW.........
WWWWWWWW........
.WWWWWWWW.......
.WWWWWWWWW......
.WWWWWWWWWW.....
..WWWWWWWWW.....
..WWWWWWWWW.....
...WWWWWWWW.....
...WWWWWWWW.....
....WWWWWWW.....
....WWWWWW......
.....WWWW......."""

DAWN_DOWN = """
................
................
................
................
................
................
................
................
................
................
................
................
................
................
................
....WWWW........
.WWWWWWWW.......
WWWWWWWWWW......
WWWWWWWWWWW.....
WWWWWWWWWWW.....
.WWWWWWWWWW.....
..WWWWWWWW......
...WWWWWW.......
....WWW........."""


def dawnwing(up):
    f = half(DAWN_BODY)
    w = Cv(rows=[r + "." * 16 for r in (DAWN_UP if up else DAWN_DOWN).strip("\n").split("\n")] + ["." * 32] * 32)
    sx, sy = 10.5, 15.5  # shoulder
    for y in range(32):
        for x in range(16):
            if w.g[y][x] == "W":
                d = math.hypot(x - sx, (y - sy) * (1.0 if up else 1.4))
                f.g[y][x] = "C" if d < 3.5 else ("A" if d < 7.5 else "Y")
    f.mirror()
    return f


if not ONLY or "ho_oh" in ONLY:
    write("ho_oh", "gObjectEventGraphicsInfo_HoOh", "sw_ho_oh", "OBJ_EVENT_PAL_TAG_HO_OH", "ho_oh.png",
          "frames32x32_2",
          "DAWNWING: guardian of Mortis's skies (replaces Ho-Oh).",
          "Mockup: wings raised / wings lowered; glowing white-gold sun-bird, halo crest of light rays, gold beak, rose-orange-gold wing tiers, flame tail fan.",
          materials={"H": "s@", "P": "s@", "R": "a", "K": "b", "y": "b", "C": "c", "A": "a", "Y": "b@", "T": "a@"},
          legend={"k": 15, "e": 14},
          accept={"hair_rows": "a bird: its halo crest, not hair, sits above the face"},
          frames={"down": dawnwing(True).rows(), "f1": dawnwing(False).rows()})

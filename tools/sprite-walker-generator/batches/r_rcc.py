"""Recast group c: WOOKIEE CUB (tuber_f, tuber_m, tuber_m_swimming), MON CAL (swimmer_m) and
NAUTOLAN (swimmer_f) walkers (wiki/bible/RECAST.md). Vanilla size and pose kept: the cubs are
16x16 kids holding a float at the waist (the swimming cub sits in the water up to the float), the
swimmers show only head, shoulders and stroking arms above the surf.

Cubs: drawn as whole frames (a Wookiee head has no vanilla part), steps = stand bobbed 1 px with
new legs; the swimming cub's steps take the vanilla splash dots. Swimmers: a new head drawn per
facing, the vanilla arms and white surf of every frame kept as regions (arms -> suit sleeves).
Writes art/<name>.yaml. Run from the tool folder: python batches/r_rcc.py
"""
import sys

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P, spec  # noqa: E402
from walker_sprite import shade as shade_mod  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import game_dir  # noqa: E402

ORDER = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]


def g(text):
    return [r for r in text.strip("\n").split("\n") if r]


def vanilla(name, h):
    fr, _ = read_frames(game_dir() / (P + name + ".png"), (16, h))
    return dict(zip(ORDER, [shade_mod.regions_of(f) for f in fr]))


def shifted(rows, dy, h):
    out = ["." * 16] * dy + rows[: h - dy]
    return out


def put(rows, y, text):
    """Replace rows from y with text lines ('_' keeps the pixel)."""
    rows = list(rows)
    for i, ln in enumerate(g(text)):
        rows[y + i] = "".join(o if n == "_" else n for o, n in zip(rows[y + i], ln))
    return rows


NOFACE = {"skin_tones": "fur, not skin: the muzzle uses the skin ramp only where it shows",
          "hair_rows": "the whole head is fur", "eye_row": "eyes under a fur brow"}

# ====================================================================== WOOKIEE CUB (m)
# Child proportions (head is half the sprite), shaggy brown fur on ramp c: the head round-shaded
# (H, c@) with light fur strands, body F and arms A as separate volumes so the fur reads in
# several browns, a hand-shaded tan muzzle with a black nose and glints in the eyes. He hugs a carved log float (L, golden wood ramp a) across his belly: the
# cut ends E show pale end grain, and two red-painted glyph bands (r) are carved into it.
CUB_M_MAT = {"H": "c@", "F": "c", "A": "c", "L": "a"}
# hard pixels: eyes k with a white glint, the muzzle in all four skin tones (p q r o), nose N,
# fur highlight strands h (ramp c light), log end grain e/o, red glyph bands r/R
CUB_M_LEG = {"k": 15, "W": 14, "N": 15, "r": 9, "R": 8, "e": 1, "o": 4, "p": 1, "q": 2, "u": 3, "h": 11}

HEAD_DOWN = """
................
.....HHHHHH.....
...HHhHHHhHHH...
..HHHHhHHHHhHH..
.HHhHHHHHhHHHHH.
.HHHHHHHHHHHHHH.
HHHHkWHHHHkWHHHH
.HHHkqppppqkHHH.
.HHHHqpNNpqHHHH.
"""
HEAD_UP = """
................
.....HHHHHH.....
...HHhHHHhHHH...
..HHHHhHHHHhHH..
.HHhHHHHHhHHHHH.
.HHHHHhHHHHhHHH.
HHHHHHHHHHHHHHHH
.HHHHHHHHHHHHHH.
"""
HEAD_LEFT = """
................
......HHHHHH....
....HHHhHHHhHH..
...HHhHHHhHHHHH.
..HHHHHhHHHHhHH.
..HHHHHHHHHHHHHH
.HkWHHHHHHHHHHH.
qpqkHHHHHHHHHHH.
NppqHHHHHHHHHH..
"""
CUB_M = {
    "down": g(HEAD_DOWN + """
AAHHHouqquoHHHAA
oLLLLLLLLLLLLLLo
eLLrRLLLLLLRrLLe
oLLLLLLLLLLLLLLo
...FFFFFFFFFF...
....FFF..FFF....
................"""),
    "up": g(HEAD_UP + """
.AHHHHHHHHHHHHA.
AAAFFFFFFFFFFAAA
oLAFFFFFFFFFFALo
eLLFFFFFFFFFFLLe
oLLFFFFFFFFFFLLo
...FFFFFFFFFF...
....FFF..FFF....
................"""),
    "left": g(HEAD_LEFT + """
.ouqHAAAFFFFFF..
oLLLLLLLLLLLLLL.
eLLrRLLLLLLRrLL.
oLLLLLLLLLLLLLL.
....FFFFFFFFF...
....FFF..FFF....
................"""),
}
LEGS_M = {
    "down_a": ["....FFFFFFFFF...", "....FFF........."], "down_b": ["...FFFFFFFFF....", ".........FFF...."],
    "up_a": ["....FFFFFFFFF...", "....FFF........."], "up_b": ["...FFFFFFFFF....", ".........FFF...."],
    "left_a": ["...FFFFFFFFFF...", "...FFF....FFF..."], "left_b": ["....FFFFFFFFF...", ".....FFF.FFF...."],
}


def walk_frames(stand, legs):
    fr = {k: v for k, v in stand.items()}
    for k, lg in legs.items():
        fr[k] = put(shifted(stand[k.split("_")[0]], 1, 16), 14, "\n".join(lg))
    return fr


spec("tuber_m", "TuberM", "npc_2", "tuber_m.png",
     "WOOKIEE CUB (m) hugging a carved log float (replaces Tuber M).",
     "Recast c: whole frames on TuberM's 16x16 footprint; shaggy brown Wookiee cub (round-shaded fur head with highlight strands, body and arms as separate volumes, tan four-tone muzzle, black nose, eye glints) hugging a golden carved log "
     "float with pale end grain and two red-painted glyph bands.",
     CUB_M_MAT, CUB_M_LEG, NOFACE, kit="person16x16", frames=walk_frames(CUB_M, LEGS_M))

# ====================================================================== WOOKIEE CUB (m), swimming
# The same cub and log in the lagoon: everything below the log is under water (white surf w);
# the steps bob 1 px and take the vanilla sheet's splash dots.
SWIM_WATER = {
    "down": ("""
oLLLLLLLLLLLLLLo
eLLrRLLLLLLRrLLe
wwwLLLLLLLLLLwww
..wwwwwwwwwwww..
................
................"""),
    "up": ("""
oLLFFFFFFFFFFLLo
eLLFFFFFFFFFFLLe
wwwLLLLLLLLLLwww
..wwwwwwwwwwww..
................
................"""),
    "left": ("""
oLLLLLLLLLLLLLL.
eLLrRLLLLLLRrLLw
wwwLLLLLLLLLLww.
..wwwwwwwwwwww..
................
................"""),
}
VS = vanilla("tuber_m_swimming", 16)
SWIM = {k: put(CUB_M[k], 10, SWIM_WATER[k]) for k in CUB_M}
swim_fr = dict(SWIM)
for k in ORDER[3:]:
    base = shifted(SWIM[k.split("_")[0]], 1, 16)
    v = VS[k]
    swim_fr[k] = ["".join(b if b != "." or v[y][x] != "w" else "w" for x, b in enumerate(base[y])) for y in range(16)]
spec("tuber_m_swimming", "TuberMSwimming", "npc_2", "tuber_m_swimming.png",
     "WOOKIEE CUB (m) paddling on a carved log float (replaces Tuber M swimming).",
     "Recast c: the tuber_m cub (same head, fur and golden log with red glyph bands) sitting in the lagoon up to the log; white surf below it, the vanilla splash dots on the steps.",
     {**CUB_M_MAT, "w": "w"}, CUB_M_LEG, {**NOFACE, "legs": "swimming: no legs above the water (vanilla shares it)"},
     kit="person16x16", frames=swim_fr)

# ====================================================================== WOOKIEE CUB (f)
# The same cub head and fur (NPC_2, like her brother; NPC_3 was tried but its only wood tone is the
# skin ramp, which made the float read as bare skin) with two bead braids hanging beside her face
# (dark braid B, red g/y and white W beads, a red bead tuft on the crown) and a carved golden wood
# ring float (O, ramp a) instead of the log, with a zigzag of carved notches (n) and red inlay (j).
CUB_F_MAT = {"H": "c@", "F": "c", "A": "c", "O": "a"}
CUB_F_LEG = {**CUB_M_LEG, "n": 13, "B": 13, "g": 9, "y": 8, "j": 9}


def braids(rows, left=False):
    """Bead braids hang from rows 5-10 at both sides (left view: the far side is hidden, one
    braid hangs at the back of the head)."""
    rows = list(rows)
    beads = "BgBWBg"
    for i, ch in enumerate(beads):
        r = rows[5 + i]
        r = r[:15] + ch if left else ch + r[1:15] + ch
        rows[5 + i] = r
    rows[1] = rows[1][:7] + "yy" + rows[1][9:] if not left else rows[1][:8] + "yy" + rows[1][10:]
    return rows


CUB_F = {
    "down": braids(g(HEAD_DOWN + """
.AHHHouqquoHHHA.
.AOOOOOOOOOOOOA.
.OnOjOnOOnOjOnO.
..OOOOOOOOOOOO..
....OOOOOOOO....
.....FF..FF.....
................""")),
    "up": braids(g(HEAD_UP + """
.AHHHHHHHHHHHHA.
.AAFFFFFFFFFFAA.
.OOOOOOOOOOOOOO.
..OOOOOOOOOOOO..
....OOOOOOOO....
.....FF..FF.....
................""")),
    "left": braids(g(HEAD_LEFT + """
.ouqHAAAFFFFFF..
.OOOOOOAFFFOOOO.
.OnOjOnOOnOjOnO.
..OOOOOOOOOOOO..
....OOOOOOOO....
......FFF.......
................"""), left=True),
}
LEGS_F = {
    "down_a": ["....OOOOOOOO....", "....FF.........."], "down_b": ["....OOOOOOOO....", "..........FF...."],
    "up_a": ["....OOOOOOOO....", "....FF.........."], "up_b": ["....OOOOOOOO....", "..........FF...."],
    "left_a": ["...FFOOOOOOFF...", "....FFF...FF...."], "left_b": ["....OOOOOOOFF...", ".....FF...FF...."],
}
spec("tuber_f", "TuberF", "npc_2", "tuber_f.png",
     "WOOKIEE CUB (f) with bead braids and a carved wooden float (replaces Tuber F).",
     "Recast c: whole frames on TuberF's 16x16 footprint; brown Wookiee cub (round-shaded fur head with highlight strands, tan four-tone muzzle, eye glints) with two bead braids hanging beside "
     "her face (red and white beads) and a red bead tuft, holding a carved golden wood ring float with carved notches and red inlay.",
     CUB_F_MAT, CUB_F_LEG, NOFACE, kit="person16x16", frames=walk_frames(CUB_F, LEGS_F))


# ====================================================================== swimmers
def swimmer(van, heads, head_end, mat_arm="A"):
    """heads: facing -> 32-row grid (only the head and anything that should cover the vanilla).
    Every frame: the head shifted by that frame's bob; below head_end the vanilla arms (s -> arm)
    and surf (w) of that frame; in the head zone the vanilla surf dots and raised-arm pixels at the
    frame edge are kept where the new head leaves the pixel empty."""
    out = {}
    for k in ORDER:
        face = k.split("_")[0]
        dy = 0 if k == face else 1
        mine = shifted(heads[face], dy, 32)
        v = van[k]
        rows = []
        for y in range(32):
            r = ""
            for x in range(16):
                m, o = mine[y][x], v[y][x]
                if m != ".":
                    r += m
                elif y <= head_end + dy:
                    if o == "w":
                        r += "w"
                    elif o == "s" and (x <= 1 or x >= 14) and y >= head_end + dy - 3:
                        r += mat_arm
                    else:
                        r += "."
                else:
                    r += {"s": mat_arm, "w": "w"}.get(o, "." if o == "." else mat_arm)
            rows.append(r)
        out[k] = rows
    return out


def tall(text, top):
    rows = g(text)
    return ["." * 16] * top + rows + ["." * 16] * (32 - top - len(rows))


# MON CAL (swimmer_m): tall domed salmon-orange head (H, c@ on NPC_3, a few darker mottles d) with
# big glossy black eyes on pale bulges (E) set on the SIDES of the head, wider than the dome; the
# dome's bottom edge is the wide mouth line over a pale cream chin (J, skin ramp); a navy-grey dive suit collar (U, ramp a) with a green trim (t) and suit sleeves
# on the vanilla stroking arms.
MC = {
    "down": tall("""
......HHHH......
....HHHHHHHH....
...HHdHHHHdHH...
..HHHHHHdHHHHH..
.EEHHHHHHHHHHEE.
EkkEHHHHHHHHEkkE
EWkEHHHHHHHHEkWE
EkkEHHHHHHHHEkkE
.EEHHHHHHHHHHEE.
..HHHHHHHHHHHH..
..JJJJpJJpJJJJ..
...JJJJJJJJJJ...
..UUtUUUUUUtUU..""", 13),
    "up": tall("""
......HHHH......
....HHHHHHHH....
...HHdHHHHdHH...
..HHHHHHdHHHHH..
.EEHHHHHHHHHHEE.
EEEEHHHHHHHHEEEE
EEEEHHHHHHHHEEEE
EEEEHHHHHHHHEEEE
.EEHHHHHHHHHHEE.
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
...HHHHHHHHHH...
..UUUUUUUUUUUU..""", 13),
    "left": tall("""
.......HHHH.....
.....HHHHHHHH...
....HHHdHHHdHH..
...HHHHHHHHHHH..
.EEEHHHHHHdHHH..
EkkEHHHHHHHHHH..
EWkEHHHHHHHHHH..
EkkEHHHHHHHHHH..
.EEHHHHHHHHHHH..
.HHHHHHHHHHHHH..
JJpJJJJHHHHHH...
.JJJJJUUUUUU....
...JJUUUUUUt....""", 13),
}
VM = vanilla("swimmer_m", 32)
spec("swimmer_m", "SwimmerM", "npc_3", "swimmer_m.png",
     "MON CAL diver swimming: salmon fish head with big side eyes (replaces Swimmer M).",
     "Recast c: a new head on the swimmer's own stroking arms and surf (arms -> dive-suit sleeves): tall domed salmon-orange Mon Calamari head with mottles, big black eyes on pale bulges on the sides of the head, "
     "a wide mouth line over a pale cream chin, navy-grey suit collar with green trim.",
     {"H": "c@", "E": "s", "J": "s", "U": "a", "A": "a", "w": "w"},
     {"k": 15, "W": 14, "p": 1, "d": 12, "t": 9},
     {"hair_rows": "a bald domed fish head, no hair", "eye_row": "Mon Calamari eyes sit on the sides of the head",
      "height": "swimming: only the head and shoulders show above the surf (vanilla shares it)"},
     frames=swimmer(VM, MC, 25))

# NAUTOLAN (swimmer_f): smooth green head (H, skin-b@ on NPC_3), big black eyes, brass dive
# goggles (hard ramp c pixels, grey lenses) pushed up on the forehead, and head-tails hand-shaded in
# ramp b (h T t) that trail behind her in the water: hanging beside her face when she swims at you, a
# fan of tails lying on the water behind her head when she swims away, streaming back when side-on.
NA = {
    "down": tall("""
......HHHH......
....HHHHHHHH....
...dLlGqqGLld...
..HHHHHHHHHHHH..
.tHHHHHHHHHHHHt.
thHHkkHHHHkkHHht
tTHHkWHHHHkWHHTt
thHHHHHHHHHHHHht
tT.HHHHnnHHHH.Tt
.th..HHHHHH..ht.
.tT..UUUUUU..Tt.
..t..........t..""", 15),
    "up": tall("""
......HHHH......
....HHHHHHHH....
...dGGqqqqGGd...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.thHHHHHHHHHHTt.
.hTthTthTthTthT.
.hT.hT.hT.hT.hT.
.hT.hT.hT.hT.hT.
..t.hT.hT.hT.t..
....tT.hT.Tt....
.....t.hT.t.....
.......tt.......""", 15),
    "left": tall("""
......HHHH......
....HHHHHHHH....
...dLlGqqGGd....
..HHHHHHHHHHH...
..HHHHHHHHHHhhh.
.HkkHHHHHHHHTTTh
.HkWHHHHHHHHttTT
..HHHHHHHHHhhh.t
..nHHHHHHHHTTTTh
...UUUUUUUUttTTt
.............tt.""", 15),
}
VF = vanilla("swimmer_f", 32)
spec("swimmer_f", "SwimmerF", "npc_3", "swimmer_f.png",
     "NAUTOLAN diver (f) swimming, head-tails trailing in the water (replaces Swimmer F).",
     "Recast c: a new head on the swimmer's own stroking arms and surf (arms -> grey suit sleeves): smooth green Nautolan head, big black eyes, brass goggles pushed up on the forehead, "
     "green head-tails hanging beside her face, fanned out behind her when she swims away and streaming back side-on.",
     {"H": "skin-b@", "U": "a", "A": "a", "w": "w"},
     {"k": 15, "W": 14, "l": 6, "n": 4, "G": 12, "q": 11, "d": 13, "L": 5, "h": 8, "T": 9, "t": 10},
     {"hair_rows": "bald Nautolan head: the head-tails are the hair", "eye_row": "Nautolan eyes are big and black",
      "skin_tones": "green alien skin on ramp b",
      "height": "swimming: only the head and shoulders show above the surf (vanilla shares it)"},
     frames=swimmer(VF, NA, 25))
print("wrote art/tuber_m.yaml tuber_m_swimming.yaml tuber_f.yaml swimmer_m.yaml swimmer_f.yaml")

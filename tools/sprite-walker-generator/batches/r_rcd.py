"""Recast group d: NEW walkers (net:walker-*) with no vanilla sheet of their own: `replaces` names
the placeholder they are compared against.

- sw_ewok           Ewok scout (EWOK and SHAMAN trainers), 16x16 kit on Ninja Boy's body.
- sw_bith           Bith musician of the Modal Nodes (FIGRIN D'AN, DOIKK NA'TS), still kit, drawn whole.
- sw_ithorian       MOMAW NADON / Ithorian herbalists, Gentleman's body as regions, new hammer head.
- sw_protocol_droid C-3PO-build protocol droid, Devon Employee's body as regions, new droid head.

The walking sprites take every frame of a vanilla body as material regions (classified per letter
and position), so the vanilla walk cycle and bob stay, and lay a new head over each frame at that
frame's bob (as r_g7.py does for the player). Writes art/<name>.yaml.
Run from the tool folder: python batches/r_rcd.py
"""
import sys

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P, spec  # noqa: E402
from walker_sprite.shade import regions_of  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import game_dir  # noqa: E402

ORDER = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]


def rows(text):
    return text.strip("\n").split("\n")


def top(f):
    return next(y for y, r in enumerate(f) if r.strip("."))


def overlay(g, block, x0, y0):
    for dy, ln in enumerate(block):
        for dx, ch in enumerate(ln):
            x, y = x0 + dx, y0 + dy
            if ch == "_" or not (0 <= x < len(g[0]) and 0 <= y < len(g)):
                continue
            g[y][x] = ch


def compose(path, size, classify, body_y, heads, extra=None):
    """Every frame of a vanilla sheet as regions: pixels at or below body_y[facing] (stand
    coordinates) go through classify(letter, x, y, facing, frame); heads[facing] = (y, rows) is laid
    over at the frame's bob, then extra[facing] = [(x, y, rows)] (props)."""
    fr, _ = read_frames(game_dir() / (P + path), size)
    reg = {n: regions_of(f) for n, f in zip(ORDER, fr)}
    stand_top = {n: top(reg[n]) for n in ("down", "up", "left")}
    out = {}
    for name in ORDER:
        facing = name.split("_")[0]
        bob = top(reg[name]) - stand_top[facing]
        g = [["."] * size[0] for _ in range(size[1])]
        for y, r in enumerate(reg[name]):
            for x, ch in enumerate(r):
                if ch != "." and y - bob >= body_y[facing]:
                    g[y][x] = classify(ch, x, y - bob, facing, name)
        hy, hrows = heads[facing]
        overlay(g, rows(hrows), 0, hy + bob)
        ex = extra or {}
        for (px, py, prow) in ex.get(name, ex.get(facing, [])):
            overlay(g, rows(prow), px, py + bob)
        out[name] = ["".join(r) for r in g]
    return out


def g32(text):
    r = rows(text)
    return ["................"] * (32 - len(r)) + r


# ====================================================================== EWOK (net:walker-ewok)
# Small (16x16 kit, Ninja Boy's body). Cues: round brown fur face (F) with big black glinting eyes
# and a tan muzzle (M) with a black nose, an ochre leather hood (H) with the two round fur ears
# (hard f/g) poking through it, a red bead on the hood's crown, brown fur body (B) with a leather strap,
# and a small spear (shaft p, red binding r, white stone tip W) held upright at the side.
EW_DOWN = """
..gg........gg..
..gfHHHHHHHHfg..
.HHHHHHrrHHHHHH.
.HHHHHHHHHHHHHH.
.HHgffffffffgHH.
.HgWkffffffWkgH.
.HgkkfMMMMfkkgH.
..HggMMkkMMggH..
...gggMMMMggg..."""
EW_UP = """
..gg........gg..
..gfHHHHHHHHfg..
..HHHHHrrHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
...HHHHHHHHHH..."""
EW_LEFT = """
........gg......
......HHgfHH....
....HHHHHHrHH...
...HHHHHHHHHHH..
..HHfffHHHHHHH..
..fWkffgHHHHHH..
.MfkkffgHHHHHH..
kMMMffggHHHHH...
MMMMgggHHHHH...."""
SPEAR = """
W
W
r
p
p
p
p
p
p
p
p
p
p
p"""


def ewok_cls(ch, x, y, facing, name):
    if ch == "a":
        return "H"          # the ninja's hood drape -> leather hood
    if ch == "b":
        return "L"          # sash -> leather strap
    if ch == "s":
        return "E"          # hands -> fur paws
    return "B"              # suit -> fur body


EW = compose("ninja_boy.png", (16, 16), ewok_cls, {"down": 9, "up": 9, "left": 9},
             {"down": (0, EW_DOWN), "up": (0, EW_UP), "left": (0, EW_LEFT)},
             {"down": [(14, 0, SPEAR)], "up": [(1, 0, SPEAR)], "left": [(10, 0, SPEAR)],
              # the spear arm swings with the step
              "down_a": [(14, -1, SPEAR)], "down_b": [(15, 1, SPEAR)], "up_a": [(0, 1, SPEAR)], "up_b": [(1, -1, SPEAR)],
              "left_a": [(9, 0, SPEAR)], "left_b": [(11, 0, SPEAR)]})
spec("sw_ewok", "SwEwok", "npc_2", "ninja_boy.png",
     "NEW WALKER (net:walker-ewok): Ewok scout: brown fur, ochre leather hood with the ears poking through, "
     "big black eyes, tan muzzle, a small spear (placeholder: Ninja Boy). Used by the EWOK and SHAMAN trainers.",
     "Recast group d, shade mode, 16x16 kit on Ninja Boy's body as regions (suit -> fur B, sash -> leather strap L, "
     "hood drape -> hood H). New head: brown fur face, tan muzzle, big glinting eyes, ochre hood with the round fur ears "
     "through it and a red crown bead; spear with a red binding and a white stone tip. Brown, hornless and small, "
     "unlike grey horn-hooded Chirpa (winona).",
     materials={"H": "a", "E": "c", "B": "c@", "L": "a", "M": "s"},
     legend={"k": 15, "W": 14, "p": 7, "r": 9, "f": 11, "g": 12},
     accept={"skin_tones": "Ewok fur is the brown ramp; only the muzzle uses the skin ramp",
             "hair_rows": "a leather hood over fur",
             "eye_row": "big Ewok eyes inside the fur face"},
     kit="person16x16", frames=EW)


# ====================================================================== PROTOCOL DROID (net:walker-protocol-droid)
# C-3PO build on Devon Employee's body as regions: dull silver plating (ramp a; head H round-shaded
# with a crown glint, torso P, arm A, legs L, feet F), ONE RED ARM (R, ramp c: his left arm, so
# viewer's right facing down, viewer's left facing up, the near arm facing left), round glowing
# eyes (skin light/base), ear discs (E), a mouth slot and a dark neck joint (hard ramp-a dark),
# the exposed midriff wiring of the build (M, ramp b) where the tie was. Stiff, upright stance.
PD_DOWN = """
.....HHHHHH.....
....HHWWHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHkkHHHHkkHH..
.EHHeoHHHHeoHHE.
.EHHouHHHHouHHE.
..HHHHHHHHHHHH..
...HHHHnnHHHH...
....HHHHHHHH...."""
PD_UP = """
.....HHHHHH.....
....HHWWHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.EHHHHHHHHHHHHE.
.EHHHHHHHHHHHHE.
..HHHHHHHHHHHH..
...HHHHHHHHHH...
....HHHHHHHH...."""
PD_LEFT = """
......HHHHHH....
....HHWWHHHHH...
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..HkkHHHHHHHHH..
.HeoHHHHHEEHHH..
.HouHHHHHEEHHH..
..HHHHHHHHHHH...
.nnHHHHHHHHH....
...HHHHHHHH....."""


def droid_cls(ch, x, y, facing, name):
    # which side is the red (left) arm: viewer's right facing down, viewer's left facing up
    red = (lambda x: x >= 8) if facing == "down" else (lambda x: x <= 7)
    if facing == "left":
        if ch == "s" and y >= 24:
            return "Q" if y >= 27 else "R"  # near hand (dark red only at the fingers)
        if ch == "s":
            return "n"                      # chin -> neck joint
        if ch in "aw":
            return "R" if y >= 24 else "M"  # sleeve cuff / collar wiring
        if ch in "kc" and y >= 28:
            return "F"
        if ch == "b" and y <= 27 and x <= 5:
            return "R"                      # near sleeve
        return "L" if y >= 28 else "P"
    if ch == "s":
        if 4 <= x <= 11 and y <= 23:
            return "n"                      # chin -> neck joint
        return "Q" if red(x) else "A"       # hands
    if ch in "aw":
        return "M"                          # tie -> midriff wiring
    if ch in "kc":
        return "F" if y >= 28 else "D"
    if y <= 27 and (x <= 3 or x >= 12):
        return "R" if red(x) else "A"       # sleeves
    return "L" if y >= 27 else "P"


PD = compose("devon_employee.png", (16, 32), droid_cls, {"down": 21, "up": 21, "left": 21},
             {"down": (11, PD_DOWN), "up": (11, PD_UP), "left": (11, PD_LEFT)},
             # chest-plate glints and the back's power-pack seam: single hard pixels, as vanilla creases
             {"down": [(4, 22, "W______W")], "up": [(6, 22, "nWWn"), (6, 24, "nnnn")], "left": [(9, 22, "W")]})


def red_arm(fr):
    """The red arm is only 2 px wide, so the shader would outline it into a dark stripe: tone it by
    hand (lit red inside, mid red on the silhouette edge, dark red hand) like a vanilla sleeve."""
    out = {}
    for name, g in fr.items():
        rows_ = [list(r) for r in g]
        for y, r in enumerate(rows_):
            for x, ch in enumerate(r):
                if ch == "R":
                    edge = any(not (0 <= x + dx < 16) or g[y + dy][x + dx] == "." for dx, dy in ((-1, 0), (1, 0), (0, -1)))
                    r[x] = "r" if edge else "q"
                elif ch == "Q":
                    r[x] = "d"
        out[name] = ["".join(r) for r in rows_]
    return out


PD = red_arm(PD)
spec("sw_protocol_droid", "SwProtocolDroid", "npc_3", "devon_employee.png",
     "NEW WALKER (net:walker-protocol-droid): silver protocol droid of the C-3PO build: dull silver plating, "
     "one red arm, round glowing eyes (placeholder: Devon Employee). Waits outside the cantina; droids in houses and offices.",
     "Recast group d, shade mode: Devon Employee's body as regions (suit -> plating P/L, tie -> midriff wiring M on ramp b, "
     "one sleeve and hand -> red arm R on ramp c, shoes -> feet F), new round droid head with ear discs, round glowing "
     "eyes, a mouth slot and a dark neck joint. NPC_3: ramp a is the dull lavender silver, ramp c the red.",
     materials={"H": "a@", "E": "a", "P": "a", "A": "a", "L": "a", "F": "a", "M": "b"},
     legend={"k": 15, "W": 14, "e": 1, "o": 2, "u": 3, "n": 7, "D": 7, "q": 11, "r": 12, "d": 13},
     accept={"skin_tones": "droid: no skin; the eyes use the skin ramp's light tones",
             "hair_rows": "droid: a plated head, no hair",
             "eye_row": "round droid photoreceptors"},
     frames=PD)


# ====================================================================== ITHORIAN (net:walker-ithorian)
# MOMAW NADON on Gentleman's body as regions (coat -> earth robe). Cues: the HAMMER HEAD, a wide
# curved bar of brown hide (H, round-shaded, crown glint) with a black eye at each END, set on a tall
# neck of the same hide (hand-toned on ramp c: shadow under the hammer, lit throat, ridges) with a
# black mouth at each side; ochre earth robe (O, ramp a, flat-shaded) with dark creases, a tan linen
# inner robe at the collar (V, skin ramp), a red sash (S, ramp b), brown hands. Taller than a human
# (22 rows). Head and neck share one brown so it does not read as a hat over a face.
IT_DOWN = """
....HHHWWHHH....
..HHHHHHHHHHHH..
HHWHHHHHHHHHHWHH
WkHHHHHHHHHHHHkW
kkHHHHHHHHHHHHkk
.HHHHHHHHHHHHHH.
...HHuuuuuuHH...
....3uu22uu3....
....3u2u22u3....
....m322u23m....
.....322223.....
.....332233....."""
IT_UP = """
....HHHWWHHH....
..HHHHHHHHHHHH..
HHWHHHHHHHHHHWHH
HHHHHHHHHHHHHHHH
HHHHHHHHHHHHHHHH
.HHHHHHHHHHHHHH.
...HHHHHHHHHH...
....uuuuuuuu....
....33322333....
....332u2233....
.....322223.....
.....332233....."""
IT_LEFT = """
.....HHWWHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHWkHHHHHHHH..
.HHHkkHHHHHHHH..
HHHHHHHHHHHHH...
HHH..uuuuuuu....
.H...2223333....
.....2223333....
.....m223333....
......22333.....
.....222333....."""


def ith_cls(ch, x, y, facing, name):
    if facing == "left":
        if ch == "s":
            return "h" if y >= 24 else "2"          # near hand / throat
        if ch == "k":
            return "K" if y >= 29 else "S"          # belt -> sash, shoes -> feet
        if ch in "aw" and y <= 23:
            return "V"
        return "O"
    if ch == "s":
        if 4 <= x <= 11 and y <= 23:
            return "V"                              # collar opening -> inner robe
        return "h"                                  # hands
    if ch in "aw" and y <= 23:
        return "V"                                  # collar -> inner robe
    if ch == "k":
        return "S" if y == 28 else "K"              # belt -> sash, shoes -> feet
    return "O"                                      # coat and buttons -> robe


IT = compose("gentleman.png", (16, 32), ith_cls, {"down": 21, "up": 21, "left": 22},
             {"down": (9, IT_DOWN), "up": (9, IT_UP), "left": (10, IT_LEFT)},
             # robe folds: single dark creases, as vanilla coats have
             {"down": [(4, 23, "f______f"), (5, 25, "f____f"), (7, 29, "f")], "up": [(7, 23, "f"), (5, 25, "f____f"), (8, 27, "f")],
              "left": [(10, 24, "f"), (8, 26, "f_f")]})
spec("sw_ithorian", "SwIthorian", "npc_2", "gentleman.png",
     "NEW WALKER (net:walker-ithorian): MOMAW NADON, Ithorian 'hammerhead': wide curved hammer head with an eye "
     "at each end, long neck, earth-coloured robes (placeholder: Gentleman). Also Ithorian HERBALISTs.",
     "Recast group d, shade mode: Gentleman's body as regions (coat -> ochre robe O with creases, collar -> tan linen "
     "inner robe V, belt -> red sash S, hands and shoes -> brown), new hammer head (brown hide, round-shaded, an eye at "
     "each end, crown and end glints) on a tall hand-toned brown neck with a mouth at each side. NPC_2 for the earth "
     "browns (Gentleman's NPC_3 made the hide pale peach, too close to the Bith dome).",
     materials={"H": "c@", "h": "c", "O": "a!", "V": "s", "S": "b", "K": "c"},
     legend={"k": 15, "W": 14, "m": 15, "f": 7, "u": 13, "2": 11, "3": 12},
     accept={"skin_tones": "Ithorian hide is the brown ramp; only the linen collar uses the skin ramp",
             "hair_rows": "no hair: the top of the hammer head",
             "eye_row": "the eyes are at the two ends of the hammer",
             "height": "Ithorians tower over people: 22 rows"},
     frames=IT)


# ====================================================================== BITH (net:walker-bith)
# Still kit (the band stands on its stage), drawn whole. Cues: the HUGE pale domed cranium (h,
# skin ramp, round-shaded with a crown glint) tapering to a small chin, big black wide-set eyes,
# skin-shade folds round the small mouth (f); a dark suit (J jacket, V sleeves, T trousers, ramp a)
# with a white shirt front (w), black shoes; the KLOO HORN, a long silver reed horn (hand-toned
# ramp c: g light, G mid, d dark bell) running from the mouth down to the hands.
def g32(text):
    r = text.strip("\n").split("\n")
    return ["................"] * (32 - len(r)) + r


BI_DOWN = g32("""
.....hhWWhh.....
...hhhhhhhhhh...
..hhhhhhhhhhhh..
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
..hhhhhhhhhhhh..
..hkkhhhhhhkkh..
...kkhhhhhhkk...
...hhhffffhhh...
....hfhhhhfh....
.....hffgfh.....
...JJJwwwgJJJ...
..JJJJwwwgJJJJ..
.JJJJJJwwJgJJJJ.
.VVJJJJJJJngJVV.
.VVJJJJJJJJngGV.
.nVJJJJJJJJJgGg.
..nJJJJJJJJJddd.
...TTTTTTTTTT...
...TTTT..TTTT...
...KKK....KKK...
................""")
BI_UP = g32("""
.....hhWWhh.....
...hhhhhhhhhh...
..hhhhhhhhhhhh..
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
..hhhhhhhhhhhh..
..hhhhhhhhhhhh..
...hhhhhhhhhh...
....hhhhhhhh....
.....hhhhhh.....
......hhhh......
...JJJJJJJJJJ...
..JJJJJJJJJJJJ..
.JJJJJJJJJJJJJJ.
.VVJJJJJJJJJJVV.
.VVJJJJJJJJJJVV.
.nVJJJJJJJJJJVn.
..nJJJJJJJJJJn..
...TTTTTTTTTT...
...TTTT..TTTT...
...KKK....KKK...
................""")
BI_LEFT = g32("""
......hhWWhh....
....hhhhhhhhhh..
...hhhhhhhhhhhh.
..hhhhhhhhhhhhh.
..hhhhhhhhhhhhh.
..hhhhhhhhhhhhh.
..hhhhhhhhhhhh..
..hkkhhhhhhhhh..
..hkkhhhhhhhh...
..hhhhhhhhhhh...
.gffhhhhhhhh....
.Gfhhhhhhhh.....
.G...wJJJJJ.....
G...JwJJJJJJ....
G...JJJJJJJJ....
dd.nVVJJJJJJ....
ddnnVVJJJJJJ....
....VVJJJJJJ....
....nJJJJJJJ....
.....TTTTTT.....
.....TTTTT......
.....KKKK.......
................""")
spec("sw_bith", "SwBith", "npc_4", "psychic_m.png",
     "NEW WALKER (net:walker-bith): Bith musician of the Modal Nodes: huge bald pale domed cranium, big black eyes, "
     "dark suit, silver kloo horn (placeholder: Psychic M). One sprite for FIGRIN D'AN and DOIKK NA'TS.",
     "Recast group d, shade mode, drawn whole (still kit: the band stands on the cantina stage). Cues: the huge "
     "round-shaded skin-ramp dome tapering to a small chin with skin-shade mouth folds and big black eyes; dark "
     "slate suit on ramp a with a white shirt front; a hand-toned silver kloo horn (ramp c) from the mouth to the hands.",
     materials={"h": "s@", "n": "s", "J": "a", "V": "a", "T": "a", "w": "w/a"},
     legend={"k": 15, "W": 14, "f": 3, "g": 11, "G": 12, "d": 13, "K": 15},
     accept={"hair_rows": "Bith: a bald domed cranium, no hair",
             "height": "the Bith cranium is taller than a human head: 22 rows"},
     kit="person16x32_still", frames={"down": BI_DOWN, "up": BI_UP, "left": BI_LEFT})

"""Recast group b: walkers whose class was recast (wiki/bible/RECAST.md, 2026-11-01).
pokefan_m (RACE FAN m), pokefan_f (RACE FAN f, Twi'lek), twin (Twi'lek kid), youngster (SCRAP
KID), ninja_boy (small kid in a desert poncho). Each keeps the vanilla body it replaces as
material regions (base + remap, so the walk cycle stays) and patches in the new head and
costume cues; the learned shader picks the tones.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_rcb.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402


def lekku(b, light="l", mid="m", dark="o"):
    """Hand-tone 2 px Twi'lek head-tails (T): too thin for the shader, which gives them only the
    dark tone and lets them melt into the head. Outer edge and tip dark, inner column mid, first
    row light; the letters are hard pixels in the spec's legend."""
    g = [list(r) for r in b["rows"].split("\n")]
    tails = "T" + light + mid + dark
    for y, r in enumerate(g):
        for x, ch in enumerate(r):
            if ch != "T":
                continue
            up = y > 0 and g[y - 1][x] in tails
            down = y + 1 < len(g) and g[y + 1][x] == "T"
            side = [r[x + d] if 0 <= x + d < len(r) else "." for d in (-1, 1)]
            edge = ("." in side and not any(c in tails for c in side)) or x in (0, len(r) - 1)
            g[y][x] = light if not up else (dark if edge or not down else mid)
    return {**b, "rows": "\n".join("".join(r) for r in g)}

# ====================================================================== POKEFAN_M -> podrace fan
# Stout body kept. Brown hair with racing goggles pushed up on the forehead (black strap k, amber
# lenses L with a white glint W), a red team vest R with two yellow pinstripes y, yellow shorts.
PM_D = block(0, 11, """
......cccc......
....cccccccc....
...kWLkkkkLWk...
..ckLLksskLLkc..""")
PM_U = block(0, 11, """
......cccc......
....cccccccc....
...cccccccccc...
..kkkkkkkkkkkk..""")
PM_L = block(0, 11, """
.......cccc.....
.....ccccccc....
....kWLkkkkkk...
...kLLk_________""")
PM_VEST_D = block(0, 22, """
____y______y____
_____y____y_____
_____y____y_____
_____y____y_____""")
PM_VEST_U = PM_VEST_D
PM_VEST_L = block(0, 22, """
__________y_____
__________y_____
__________y_____
__________y_____""")
spec("pokefan_m", "PokefanM", "npc_2", "pokefan_m.png",
     "RACE FAN (m): stout podrace fan in a striped red-and-yellow team vest, racing goggles pushed up on his head (replaces Pokefan M).",
     "Recast b, B style: Pokefan M's own stout body as regions (shirt -> red team vest R, belt/shorts kept yellow), brown hair with black-strapped amber racing goggles pushed up on the forehead, two yellow pinstripes down the vest. Stays on NPC_2.",
     materials={"R": "b"}, legend={"k": 15, "W": 14, "L": 6, "y": 5},
     accept={},
     base="pokefan_m.png", remap={"b": "R"},
     patches={"down": [PM_D, PM_VEST_D], "up": [PM_U, PM_VEST_U], "left": [PM_L, PM_VEST_L]})

# ====================================================================== POKEFAN_F -> Twi'lek race fan
# Blue Twi'lek (skin on ramp a, round-shaded dome F, two long head-tails T hanging behind the
# shoulders / down the back), pink headwrap H, orange team scarf S on the skin ramp with a pink
# stripe p, grey top O and pink skirt Q, grey boots D.
TF_D = block(0, 11, """
......FFFF......
....FFFFFFFF....
...FFFWFFFFFF...
...FFFFFFFFFF...
..HHHHHHHHHHHH..
..FFFFFFFFFFFF..
.TFFFFFFFFFFFFT.
.TFFFFkFFkFFFFT.
TTFFFFkFFkFFFFTT
TT..FFFFFFFF..TT
_TT_SSSSSSSS_TT_
_TTSSSSSSSSSSTT_
__TT____________
__TT____________
___TT___________
___TT___________
____T___________""")
TF_U = block(0, 11, """
......FFFF......
....FFFFFFFF....
...FFFFWFFFFF...
...FFFFFFFFFF...
..HHHHHHHHHHHH..
..FFFFFFFFFFFF..
..FFFFFFFFFFFF..
..FFTTFFFFTTFF..
...FTTTFFTTTF...
....TTT..TTT....
...STTTSSTTTS...
__OOTTTOOTTTOO__
____TTT__TTT____
_____TT__TT_____
_____TT__TT_____
______T__T______""")
TF_L = block(0, 11, """
......FFFF......
....FFFFFFF.....
...FFFFWFFFF....
...FFFFFFFFF....
..HHHHHHHHHH....
..FFFHHHHHHHT...
.FFFFFFFFFFTT...
.FFkFFFFFFFTTT..
.FFkFFFFFFTTTT..
..FFFFFFFFTTTT..
...SSSSSSSTTT...
___WSS____TTT___
______S___TTT___
__________TT____
__________TT____
___________T____""")
TF_D, TF_U, TF_L = lekku(TF_D, "u", "v", "x"), lekku(TF_U, "u", "v", "x"), lekku(TF_L, "u", "v", "x")
spec("pokefan_f", "PokefanF", "npc_1", "pokefan_f.png",
     "RACE FAN (f): blue Twi'lek woman with two long head-tails (one draped over her shoulder), a pink headwrap and an orange racing-team scarf (replaces Pokefan F).",
     "Recast b, B style: the Pokefan F's own body as regions (top -> olive O, skirt and apron -> pink Q, shoes -> olive boots D, arms -> blue skin), new bald round Twi'lek head on ramp b (blue, as on the RACE FAN front pic) with a pink headwrap and two long hand-toned head-tails (one draped over the shoulder onto the chest, one behind), orange team scarf on the skin ramp. Moves to NPC_1 for the blue skin.",
     materials={"F": "skin-b@", "H": "a", "S": "s", "O": "c", "Q": "a", "D": "c"},
     legend={"k": 15, "W": 14, "u": 8, "v": 9, "x": 10},
     accept={"eye_row": "Twi'lek: the face is on ramp b (blue skin), so the eye finder, which looks for black inside the human skin ramp, sees no eyes; the eyes are on row 7-8 as usual",
             "skin_tones": "Twi'lek: no human skin; the skin ramp only carries the small orange scarf, which the shader gives three of its four tones"},
     base="pokefan_f.png", remap={"s": "F", "b": "O", "a": "Q", "w": "Q", "c": "D"},
     patches={"down": [TF_D], "up": [TF_U], "left": [TF_L]})

# ====================================================================== TWIN -> Twi'lek kid
# Small body kept. Blue Twi'lek kid (skin on ramp b), short head-tails T to the shoulders, pink
# headband P, simple orange tunic D on the skin ramp, olive belt C and boots B.
TW_D = block(0, 14, """
................
................
......FFFF......
....FFFFFFFF....
...FFFWFFFFFF...
..PPPPPPPPPPPP..
..FFFFFFFFFFFF..
.TFFFFFFFFFFFFT.
.TFFFFkFFkFFFFT.
TTFFFFkFFkFFFFTT
TT..FFFFFFFF..TT
TT____________TT
TT____________TT
.T____________T.""")
TW_U = block(0, 14, """
................
................
......FFFF......
....FFFFFFFF....
...FFFFWFFFFF...
..PPPPPPPPPPPP..
..FFFFFFFFFFFF..
.TFFFFFFFFFFFFT.
.TFFFFFFFFFFFFT.
TTFFFFFFFFFFFFTT
TT.FFFFFFFFFF.TT
TT_FFDDDDDDFF_TT
TT____________TT
.T____________T.""")
TW_L = block(0, 14, """
................
................
.......FFFF.....
.....FFWFFFF....
....FFFFFFFFF...
...PPPPPPPPPPP..
..FFFFFFFFFFFF..
..FFFFFFFFFFFFT.
.FFFkFFFFFFFFTT.
.FFFkFFFFFFFFTT.
..FFFFFFFFFF.TT.
.....FFFF....TT.
_____________TT_
______________T_""")


TW_D, TW_U, TW_L = lekku(TW_D), lekku(TW_U), lekku(TW_L)
TW_BELT = block(0, 28, "____CCCCCCCC____")
spec("twin", "Twin", "npc_1", "twin.png",
     "TWINS: blue Twi'lek kid with short pink head-tails, an olive headband and a simple orange tunic (replaces the Twins).",
     "Recast b, B style: the Twin's own small body as regions (dress -> orange tunic D on the skin ramp, bow/shoes -> olive boots B, arms -> blue skin), new bald round Twi'lek head on ramp b (blue, after the TWINS front pic) with an olive headband and two short hand-toned pink head-tails hanging to the shoulders like pigtails, olive belt. Moves to NPC_1 for the blue skin and pink.",
     materials={"F": "skin-b@", "P": "c", "D": "s", "C": "c", "B": "c"},
     legend={"k": 15, "W": 14, "l": 5, "m": 6, "o": 7},
     accept={"eye_row": "Twi'lek: the face is on ramp b (blue skin), so the eye finder, which looks for black inside the human skin ramp, sees no eyes; the eyes sit where the vanilla Twin's do"},
     base="twin.png", remap={"s": "F", "a": "D", "w": "D", "b": "B", "c": "F"},
     patches={"down": [TW_D, TW_BELT], "up": [TW_U, TW_BELT], "left": [TW_L]})

# ====================================================================== YOUNGSTER -> scrap kid
# Shaggy auburn hair H with racing goggles pushed up (steel strap g, green lenses L, glint W), the
# youngster's body as regions (shirt -> cream tunic T with a green patch, shorts -> steel-grey
# trousers S, shoes -> rust boots D) and a steel hydrospanner in one hand.
YG_D = block(0, 12, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..gLWggggggLWg..
..HHHHHHHHHHHH..
..HHHsHHsHHsHH..
.sHHssssssssHHs.
.ssHsskssksHHss.
..sHsksskssHss..""")
YG_U = block(0, 12, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..gggggggggggg..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.sHHHHHHHHHHHHs.
.ssHHHHHHHHHHss.
..sHHHHHHHHHHs..""")
YG_L = block(0, 12, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..WLggggggHHHH..
..LLHHHHHHHHHHH.
..sHsHHHHHHHHHH.
..sssssHHHHHHH..
..ssskssHHHHHH..
..sssksssHHHH...
...ssssssssHH...
....ssssssH.....
.....ssss.......""")
YG_TORSO_D = block(5, 22, "TTssTT\nTTTTTT\nTTTTTT\n_TTTT_")
YG_TORSO_U = block(3, 21, "TTTTTTTTTT\n_TTTTTTTT_\n_TTTTTTTT_\n_TTTTTTTT_")
YG_PATCH = block(6, 24, "pq\nqq")
YG_PATCH_U = block(8, 23, "pq\nqq")
YG_SPAN_D = block(0, 26, "dn.\ndn.\ndn.\nnnn\nd.d")
YG_SPAN_U = block(13, 26, ".nd\n.nd\n.nd\nnnn\nd.d")
YG_SPAN_L = block(2, 26, ".dn\n.dn\n.dn\nnnn\nd.d")
spec("youngster", "Youngster", "npc_3", "youngster.png",
     "SCRAP KID: Tatooine junkyard kid with shaggy hair, goggles pushed up, a patched dusty-grey tunic and a hydrospanner (replaces Youngster).",
     "Recast b, B style: the youngster's own body as regions (shirt -> dusty grey tunic T with a green patch, trim/shorts -> rust trousers S, shoes -> rust boots D), new shaggy auburn hair with steel-strapped green-lensed goggles pushed up, a steel hydrospanner hanging from one hand. Moves to NPC_3 for steel greys and rust hair.",
     materials={"H": "c@", "T": "a", "S": "c", "D": "c"},
     legend={"k": 15, "W": 14, "L": 8, "g": 7, "p": 9, "q": 10, "d": 7, "n": 5},
     accept={},
     base="youngster.png", remap={"w": "T", "b": "S", "c": "D"},
     patches={"down": [YG_D, YG_TORSO_D, YG_PATCH, YG_SPAN_D], "up": [YG_U, YG_TORSO_U, YG_PATCH_U, YG_SPAN_U], "left": [YG_L, YG_SPAN_L]})

# ====================================================================== NINJA_BOY -> desert poncho kid
# Small kid in a hooded brown desert poncho (hood H round-shaded, poncho P) with a woven yellow /
# red band (y, r) across it, face peeking out of the hood, dark trousers L.
NB_D = block(0, 0, """
................
.....HHHHHH.....
....HHHWHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHssssssHHH..
..HHssssssssHH..
..HHssksskssHH..
..HHHssssssHHH..
.PPPPPPPPPPPPPP.
.PPPPPPPPPPPPPP.
.PyrRryrRryrRrP.
..PPPPPPPPPPPP..""")
NB_U = block(0, 0, """
................
.....HHHHHH.....
....HHHWHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
...HHHHHHHHHH...
.PPPPPHHHHPPPPP.
.PPPPPPHHPPPPPP.
.PyrRryrRryrRrP.
..PPPPPPPPPPPP..""")
NB_L = block(0, 0, """
................
......HHHHH.....
.....HHWHHHH....
....HHHHHHHHH...
...HHHHHHHHHHH..
..HHsssHHHHHHH..
..HssssHHHHHHH..
..HskssHHHHHHH..
..HHsssHHHHHHH..
..PPPPPPPPPPPP..
..PPPPPPPPPPPP..
..PyrRryrRryrP..
...PPPPPPPPPP...""")
spec("ninja_boy", "NinjaBoy", "npc_2", "ninja_boy.png",
     "Small kid in a brown desert hood and a sand-coloured poncho with a woven red-and-yellow band (replaces Ninja Boy; the EWOK trainers move to their own walker).",
     "Recast b, B style: Ninja Boy's small body as regions (suit -> dark trousers L), new round brown hood framing the face and a wide sand-coloured poncho (on the skin ramp, the lightest sand tones NPC_2 has) over the arms with a woven red/yellow band, Tatooine market colours. Moves to NPC_2 for the browns.",
     materials={"H": "c@", "P": "s", "L": "c"},
     legend={"k": 15, "W": 14, "y": 5, "r": 9, "R": 10},
     accept={},
     kit="person16x16",
     base="ninja_boy.png", remap={"a": "H", "c": "L", "b": "L"},
     patches={"down": [NB_D], "up": [NB_U], "left": [NB_L]})

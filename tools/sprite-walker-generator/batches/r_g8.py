"""Group 8 of the B-style rollout: the 16x16 kids, the tubers, the infiltrator (ninja boy) and the
2-1B surgical droid (nurse). Kids keep the vanilla body as regions and patch only bold cues;
2-1B is a droid with no human silhouette, so its four frames are drawn whole.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_g8.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402

K16 = "person16x16"

# ====================================================================== LITTLE BOY -> Tatooine farm kid
# Navy hair (H), podracer goggles pushed up on the forehead (grey strap g, magenta lenses L with a
# white glint), a pale wrapped tunic (T, white edged in grey) and a grey wrap belt (B) with a
# magenta pouch (P).
LB_D = block(0, 2, """
....gLg__gLg....
...gMMggggMMg...""")
LB_U = block(0, 3, """
...gggggggggg...""")
LB_L = block(0, 2, """
....gLg_______..
....MMggggggg...""")
LB_BELT_D = block(0, 11, "...sBBBPBBBBs...")
LB_BELT_L = block(0, 11, "....BPBBBBBB....")
spec("little_boy", "LittleBoy", "npc_4", "little_boy.png",
     "Tatooine farm kid with podracer goggles and a wrapped tunic (replaces Little Boy).",
     "Group 8, B style: Little Boy's own body as regions (shirt -> pale wrapped tunic T, hair H), "
     "podracer goggles pushed up on the hair, grey wrap belt with a pouch.",
     materials={"H": "a", "T": "w/c", "B": "c", "P": "b"},
     legend={"k": 15, "W": 14, "L": 14, "M": 9, "g": 13},
     accept={},
     base="little_boy.png", remap={"a": "H", "c": "T", "b": "T"},
     patches={"down": [LB_D, LB_BELT_D], "up": [LB_U, block(0, 11, "...sBBBBBBBBs...")],
              "left": [LB_L, LB_BELT_L]}, kit=K16)

# ====================================================================== LITTLE GIRL -> Naboo girl
# Brown hair (H) with two round side buns (N), a gold circlet (Y), a red Naboo smock (D) with a
# gold collar (G) and hem (h).
LG_D = block(0, 1, """
________________
________________
___HYYYYYYYYH___
________________
.NN__________NN.
NNN__________NNN
.NN__________NN.
....________....""")
LG_U = block(0, 1, """
________________
________________
________________
________________
.NN__________NN.
NNN__________NNN
.NN__________NN.
....________....""")
LG_L = block(0, 1, """
......HHHHH.....
.....HHHHHHH....
....YYYHHHHHH...
...YHHHHHHHHHN..
______HHHHHHNNN.
_______HHHHHNNN.
________HHHHNNN.
_________HHHHN..
_________HHH....""")
spec("little_girl", "LittleGirl", "npc_2", "little_girl.png",
     "Naboo girl with Leia-style side buns and a red smock (replaces Little Girl).",
     "Group 8, B style: Little Girl's own body as regions (smock -> red Naboo dress D, collar -> gold G), "
     "her pigtails become two round side buns with a gold circlet.",
     materials={"H": "c@", "N": "c@", "Y": "a", "D": "b", "G": "a"},
     legend={"k": 15, "W": 14},
     accept={},
     base="little_girl.png", remap={"c": "H", "b": "D", "a": "G"},
     patches={"down": [LG_D, block(0, 13, "____GDDDDDDG____")], "up": [LG_U, block(0, 13, "____GDDDDDDG____")],
              "left": [LG_L]}, kit=K16)

# ====================================================================== RS LITTLE BOY -> X-wing pilot kid
# Toy Rebel pilot helmet: white shell (W, edged in brown) with a red crest stripe (R), a brown
# visor band (V) and cheek guards; orange flight suit (O) with a white chest box (X) and a brown
# harness belt (G).
RS_D = block(0, 1, """
.....WWWWWW.....
....WWWRRWWW....
...WWWWRRWWWW...
...WWWWRRWWWW...
..WWVVVVVVVVWW..
..WWssksskssWW..
...WssksskssW...
....ssssssss....
...sOOOXXOOOs...""")
RS_U = block(0, 1, """
.....WWWWWW.....
....WWWRRWWW....
...WWWWRRWWWW...
...WWWWRRWWWW...
..WWWWWRRWWWWW..
..WWWWWRRWWWWW..
...WWWWWWWWWW...
....WWWWWWWW....
...sOOOOOOOOs...""")
RS_L = block(0, 1, """
.....WWWWWW.....
....WWWWWRRW....
...WWWWWWWRRW...
...WWWWWWWWRW...
...VVVVWWWWWW...
...sksWWWWWWW...
...sksWWWWWW....
....ssssssW.....
.....OOssOO.....""")
spec("rs_little_boy", "RubySapphireLittleBoy", "npc_2", "rs_little_boy.png",
     "Kid in a toy X-wing pilot helmet and orange flight suit (replaces the R/S Little Boy).",
     "Group 8, B style: the R/S Little Boy's own body as regions (shirt and legs -> orange flight suit O, "
     "shorts -> brown harness G), new white Rebel pilot helmet with a red crest stripe, visor band and cheek guards, white chest box.",
     materials={"W": "w/c", "R": "b", "V": "c", "O": "a", "X": "w/c", "G": "c"},
     legend={"k": 15},
     accept={"hair_rows": "no hair: a pilot helmet"},
     base="rs_little_boy.png", remap={"b": "O", "c": "G", "w": "s"},
     patches={"down": [RS_D], "up": [RS_U], "left": [RS_L]}, kit=K16)

# ====================================================================== NINJA BOY -> infiltrator
# Navy hood and mantle (H) over a grey mask (M) with a glowing magenta visor slit (v/V), a grey
# bodysuit (S) with a magenta belt (B).
NB_D = block(0, 1, """
.....HHHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
...HHHMMMMHHH...
..HHHMMMMMMHHH..
..HHMvVWVvvMHH..
...HMMMMMMMMH...
....HMMMMMMH....
...HHSSSSSSHH...""")
NB_U = block(0, 1, """
.....HHHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
...HHHHHHHHHH...
....HHHHHHHH....
...HHHHHHHHHH...""")
NB_L = block(0, 1, """
......HHHHH.....
.....HHHHHHH....
....HHHHHHHHH...
...MMMHHHHHHHH..
...MMMMMHHHHHH..
...WVvMMHHHHHH..
...MMMMMHHHHHH..
....MMMMHHHHH...
.....MMMHHHH....""")
spec("ninja_boy", "NinjaBoy", "npc_4", "ninja_boy.png",
     "Infiltrator in a dark hooded suit with a glowing visor slit (replaces Ninja Boy).",
     "Group 8, B style: Ninja Boy's own body as regions (suit -> grey bodysuit S, sash -> magenta belt B), "
     "new navy hood and mantle over a grey mask with a glowing magenta visor slit.",
     materials={"H": "a@", "M": "c", "S": "c", "B": "b"},
     legend={"k": 15, "v": 9, "V": 8, "W": 14, "x": 15},
     accept={"hair_rows": "no hair: a hood", "eye_row": "a visor slit instead of eyes",
             "skin_tones": "face masked: only the small hands show skin"},
     base="ninja_boy.png", remap={"a": "H", "c": "S", "b": "B"},
     patches={"down": [NB_D, block(4, 11, "BBBxBBBB")], "up": [NB_U], "left": [NB_L]}, kit=K16)

# ====================================================================== TUBERS -> lake kids with float droids
# The ring (R) becomes an inflatable float droid: white panel (body w), a sensor eye (E) and
# lights (l) on the front; the kids wear swim goggles (G lenses, g strap) on the forehead.
TF_D = block(0, 3, """
.c.gGGggggGGg.c.""")
TF_L = block(0, 3, """
....GGgggggg.c..""")
TF_U = block(0, 3, """
.c.gggggggggg.c.""")
TF_RING_D = block(7, 12, "EW")
spec("tuber_f", "TuberF", "npc_1", "tuber_f.png",
     "Lake-country girl with swim goggles in a pink float-droid ring (replaces Tuber F).",
     "Group 8, B style: Tuber F's own body as regions (hair, bows and ring kept), blue swim goggles pushed up "
     "on the hair, the ring turned into an inflatable float droid with a blue sensor eye and a light.",
     materials={"R": "a"},
     legend={"k": 15, "E": 15, "W": 14, "G": 8, "g": 10},
     accept={},
     base="tuber_f.png", remap={"a": "R"},
     patches={"down": [TF_D, TF_RING_D], "up": [TF_U], "left": [TF_L, block(0, 11, ".EW_____________")]}, kit=K16)

TM_D = block(0, 3, """
...gGGggggGGg...""")
TM_L = block(0, 3, """
...GGgggggggg...""")
TM_U = block(0, 3, """
...gggggggggg...""")
TM_RING_D = block(7, 12, "EW")
for nm, gi, desc in (("tuber_m", "TuberM", "Lake-country boy with swim goggles in a yellow float-droid ring (replaces Tuber M)."),
                     ("tuber_m_swimming", "TuberMSwimming", "Lake-country boy paddling in a yellow float-droid ring (replaces Tuber M swimming).")):
    spec(nm, gi, "npc_2", f"{nm}.png", desc,
         f"Group 8, B style: {gi}'s own body as regions (hair and ring kept), red swim goggles pushed up "
         "on the hair, the ring turned into an inflatable float droid with a red sensor eye and a light.",
         materials={"R": "a", "g": "b"},
         legend={"k": 15, "E": 15, "W": 14, "G": 14},
         accept={},
         base=f"{nm}.png", remap={"a": "R"},
         patches={"down": [TM_D, TM_RING_D], "up": [TM_U], "left": [TM_L, block(0, 11, ".EW_____________")]}, kit=K16)

# ====================================================================== NURSE -> 2-1B surgical droid
# Navy bowl head (D, round) with a grey face-plate grille (F, slits g) and two amber sensors (e);
# grey neck and limbs (N, L, J), navy shoulder/hip plating (P), a transparent-looking abdomen
# (T, pale grey glass) with magenta tubes (t), dark grey feet (K). Bow: bent at the waist.
NURSE = {
    "down": [
        "................",
        ".....DDDDDD.....",
        "...DDDWDDDDDD...",
        "..DDDWDDDDDDDD..",
        ".DDDDDDDDDDDDDD.",
        ".DDDFFFFFFFFDDD.",
        "..DFFeFFFFeFFD..",
        "...FxFgFxFgFF...",
        "...FgFxFgFxFF...",
        "....FFFFFFFF....",
        "......NNNN......",
        "..PPPPPPPPPPPP..",
        ".LPPPoOPPPPPPPL.",
        ".LL.PTTTTTTP.LL.",
        ".LL.TtTTtTtT.LL.",
        ".LL.TTtTtTTT.LL.",
        ".LL.TtTTTtTT.LL.",
        ".JJ.PPPPPPPP.JJ.",
        "....PPP..PPP....",
        "....LLL..LLL....",
        "...KKKK..KKKK...",
        "...xxxx..xxxx...",
        "................",
    ],
    "up": [
        "................",
        ".....DDDDDD.....",
        "...DDDWDDDDDD...",
        "..DDDWDDDDDDDD..",
        ".DDDDDDDDDDDDDD.",
        ".DDDDDDDDDDDDDD.",
        "..DDDDDDDDDDDD..",
        "...DDDDDDDDDD...",
        "....DDDDDDDD....",
        ".....NNNNNN.....",
        "......NNNN......",
        "..PPPPPPPPPPPP..",
        ".LPPPPPPPPPPPPL.",
        ".LL.PPPPPPPP.LL.",
        ".LL.TTTNNTTT.LL.",
        ".LL.TtTNNTtT.LL.",
        ".LL.TTTNNTTT.LL.",
        ".JJ.PPPPPPPP.JJ.",
        "....PPP..PPP....",
        "....LLL..LLL....",
        "...KKKK..KKKK...",
        "...xxxx..xxxx...",
        "................",
    ],
    "left": [
        "................",
        "......DDDDD.....",
        "....DDDWDDDDD...",
        "...DDDWDDDDDDD..",
        "..DDDDDDDDDDDDD.",
        ".FFFFFDDDDDDDDD.",
        ".FeFFFFDDDDDDDD.",
        ".xFgFFFDDDDDDD..",
        ".FxFgFFDDDDDD...",
        "..FFFFFFDD......",
        "......NNNN......",
        ".....PPPPPPP....",
        "....PPPPPPPPP...",
        "....PPLLPPPPP...",
        "....TTLLtTTT....",
        "....TtLLTTtT....",
        "....TTLLTtTT....",
        "....PPJJPPPP....",
        ".....PPPPPP.....",
        ".....LLL.LL.....",
        "...KKKK..KKK....",
        "...xxxx..xxx....",
        "................",
    ],
    "bow": [
        "................",
        "................",
        "................",
        ".....DDDDDD.....",
        "...DDDWDDDDDD...",
        "..DDDWDDDDDDDD..",
        ".DDDDDDDDDDDDDD.",
        ".DDDDDDDDDDDDDD.",
        ".DDDFFFFFFFFDDD.",
        "..DFxFgFxFgFD...",
        "..PPFgFxFgFFPP..",
        ".LPPoOFFFFPPPPL.",
        ".LLPPPPPPPPPPLL.",
        ".LL.TTtTTtTT.LL.",
        ".LL.TtTTtTTT.LL.",
        "..JJPPPPPPPPJJ..",
        "....PPP..PPP....",
        "....LLL..LLL....",
        "...KKKK..KKKK...",
        "...xxxx..xxxx...",
        "................",
    ],
}
spec("nurse", "Nurse", "npc_4", "nurse.png",
     "2-1B surgical droid of the bacta centre (replaces the Pokemon Center nurse).",
     "Group 8: drawn whole (a droid has no human silhouette): navy bowl head with a grey face-plate grille "
     "and amber sensors, navy plating, thin grey limbs, a glass abdomen with magenta tubes; the bow frame bends at the waist.",
     materials={"D": "a@", "F": "c", "N": "c", "P": "a", "L": "c", "J": "c", "T": "w/c", "t": "b", "K": "c"},
     legend={"k": 15, "g": 13, "x": 15, "e": 2, "W": 14, "o": 3, "O": 1},
     accept={"skin_tones": "droid: no skin", "hair_rows": "droid: no hair, a bowl head", "eye_row": "droid: sensors in a grille"},
     frames={k: (["................"] * (32 - len(v))) + v for k, v in NURSE.items()},
     kit="person16x32_bow")
print("ok")

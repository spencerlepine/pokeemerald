"""Batch 4, in the style the owner picked from batch 3 ("B style is what we need"): the vanilla
sheet the row replaces is the body, used as material regions (its proportions, arms and walk
cycle stay); only the head and the costume cues are new; the learned shader picks every tone.
Writes art/<name>.yaml. Run from the tool folder: python batches/batch4.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402

# ====================================================================== TARFFUL (replaces Brawly)
# Wookiee: fur everywhere (head H, limbs F, torso G as three volumes of the orange-brown ramp),
# a tan muzzle (M, skin ramp) with a black nose and mouth, a steel bandolier (l) across the chest.
T_HEAD_D = block(0, 10, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHkHHHHkHHHH.
.HHHHkHHHHkHHHH.
.HHHHMMMMMMHHHH.
..HHHMMkkMMHHH..
..HHHMMMMMMHHH..
...HHHMkkMHHH...
...HHHHHHHHHH...""")
T_HEAD_U = block(0, 10, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
...HHHHHHHHHH...
...HHHHHHHHHH...""")
T_HEAD_L = block(0, 10, """
......HHHHH.....
....HHHHHHHHH...
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHkHHHHHHHHHH..
.HHkHHHHHHHHHH..
MMMMHHHHHHHHH...
MkMMHHHHHHHHH...
.MMMHHHHHHHH....
.kkHHHHHHHHH....
...HHHHHHHH.....""")
T_BAND_D = block(0, 22, """
____ll__________
_____ll_________
______ll________
_______ll_______
________ll______""")
T_BAND_U = block(0, 22, """
__________ll____
_________ll_____
________ll______
_______ll_______
______ll________""")
spec("tarfful", "Brawly", "npc_3", "gym_leaders/brawly.png",
     "TARFFUL: Wookiee chieftain with a bandolier (replaces Brawly).",
     "Batch 4, B style: Brawly's own body as regions (limbs -> fur F, torso -> fur G, shorts -> belt l), new Wookiee head with a tan muzzle, steel bandolier across the chest. Stays on NPC_3 (orange-brown fur = ramp c).",
     materials={"H": "c@", "F": "c", "G": "c", "l": "a"}, legend={"k": 15, "M": 3},
     accept={"skin_tones": "fur, not skin: the muzzle uses the skin ramp's mid tones only", "hair_rows": "the whole head is fur",
             "eye_row": "eyes under a fur brow"},
     base="gym_leaders/brawly.png", remap={"s": "F", "a": "G", "c": "l"},
     patches={"down": [T_HEAD_D, T_BAND_D], "up": [T_HEAD_U, T_BAND_U], "left": [T_HEAD_L, block(0, 22, "____________....")]},
     kit="person16x32_still")

# ====================================================================== MAUL (replaces Sidney)
# Bald red Zabrak head (R, red ramp b) with black tattoo bands (k) and a ring of short pale horns
# (h, hard yellow), yellow eyes (e) in a black mask; Sidney's body as regions turned into dark
# robes: shoulders and sleeves P, tunic O, boots D (three volumes of the dark brown ramp c).
M_HEAD_D = block(0, 10, """
....h.h..h.h....
...RRRRRRRRRR...
..RRRRkRRkRRRR..
..RRRRkRRkRRRR..
.RRRRRRRRRRRRRR.
.RkkkRRRRRRkkkR.
.RkekkRRRRkkekR.
..RkkRRRRRRkkR..
..RRRRkRRkRRRR..
...RRRkkkkRRR...
....RRRRRRRR....""")
M_HEAD_U = block(0, 10, """
....h.h..h.h....
...RRRRRRRRRR...
..RRRRkRRkRRRR..
..RRRRkRRkRRRR..
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
..RRRRRRRRRRRR..
..RRRRRRRRRRRR..
...RRRRRRRRRR...
....OOOOOOOO....""")
M_HEAD_L = block(0, 10, """
.....h.h.h.h....
....RRRRRRRRR...
...RRRkRRkRRRR..
..RRRRkRRkRRRR..
..RRRRRRRRRRRR..
.RkkRRRRRRRRRR..
.ekkRRRRRRRRRR..
..kRRRRRRRRRR...
..RRRRRRRRRRR...
..kkkRRRRRRR....
...RRRRRRRR.....""")
spec("maul", "Sidney", "npc_2", "elite_four/sidney.png",
     "MAUL (Force vision): black robes, red-and-black tattoos, horns (replaces Sidney).",
     "Batch 4, B style: Sidney's own body as regions (vest + arms -> robe P, shirt + trousers -> tunic O, shoes -> boots D), new bald Zabrak head on NPC_2's red ramp with black tattoo bands, a horn ring and yellow eyes.",
     materials={"R": "skin-b@", "P": "c", "O": "c", "D": "c"}, legend={"k": 15, "h": 3, "e": 5},
     accept={"skin_tones": "Zabrak skin is the red ramp", "hair_rows": "bald; a ring of horns instead of hair",
             "edge_black": "the tattoos are black by design", "inner_black": "the tattoos are black by design",
             "eye_row": "yellow eyes inside a black tattoo mask"},
     base="elite_four/sidney.png", remap={"b": "P", "s": "P", "k": "O", "a": "O", "c": "D"},
     patches={"down": [M_HEAD_D], "up": [M_HEAD_U], "left": [M_HEAD_L]},
     kit="person16x32_still")

# ====================================================================== ZUCKUSS (replaces Spenser)
# Gand: a grey domed insect head (G, ramp a lit like a face) with two huge compound eyes
# (E, dark green ramp b) with white glints, breathing tubes (T) from the jaw down to the chest;
# Spenser's own body as regions turned into a brown coat (C) with sleeves (S) and an inner
# tunic (V); his short cane stays.
Z_HEAD_D = block(0, 11, """
.....GGGGGG.....
...GGGGGGGGGG...
..GGGGGGGGGGGG..
..GGGGGGGGGGGG..
.EEEEGGGGGGEEEE.
EEWEEEGGGGEEWEEE
EEEEEEGGGGEEEEEE
.EEEEGGGGGGEEEE.
..GGGTTGGTTGGG..
..GGTTGGGGTTGG..
...TT.GGGG.TT...
..TT..GGGG..TT..""")
Z_HEAD_U = block(0, 11, """
.....GGGGGG.....
...GGGGGGGGGG...
..GGGGGGGGGGGG..
..GGGGGGGGGGGG..
.EGGGGGGGGGGGGE.
EEGGGGGGGGGGGGEE
EEGGGGGGGGGGGGEE
.GGGGGGGGGGGGGG.
..GGGGGGGGGGGG..
..TGGGGGGGGGGT..
...TGGGGGGGGT...
....CCCCCCCC....""")
Z_HEAD_L = block(0, 11, """
......GGGGG.....
....GGGGGGGGG...
...GGGGGGGGGGG..
..GGGGGGGGGGGG..
.EEEEGGGGGGGGG..
EEWEEEGGGGGGGG..
EEEEEEGGGGGGGG..
.EEEEGGGGGGGG...
.TTGGGGGGGGGG...
TT.GGGGGGGGG....
T...GGGGGGG.....
T....GGGGG......""")
spec("zuckuss", "Spenser", "npc_3", "frontier_brains/spenser.png",
     "ZUCKUSS: insectoid Gand findsman with breathing tubes (replaces Spenser).",
     "Batch 4, B style: Spenser's own body as regions (sleeves S, coat C, inner tunic V, cane kept), new Gand head: grey dome, two big compound eyes with glints, breathing tubes to the chest. Stays on NPC_3 (grey ramp a, dark green ramp b, brown ramp c).",
     materials={"G": "skin-a@", "E": "b", "T": "a", "S": "c", "C": "c", "V": "b", "a": "a"}, legend={"k": 15, "W": 14},
     accept={"skin_tones": "Gand carapace is the grey ramp", "hair_rows": "no hair: a domed carapace", "eye_row": "compound eyes, not eye bars",
             "head_w": "16 wide across the eyes"},
     base="frontier_brains/spenser.png", remap={"s": "S", "b": "C", "c": "C", "w": "V"},
     patches={"down": [Z_HEAD_D], "up": [Z_HEAD_U], "left": [Z_HEAD_L]})
print("ok")

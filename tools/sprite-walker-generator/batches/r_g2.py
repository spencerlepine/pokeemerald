"""Group 2 of the parallel B-style batch (STAR WARS: KYBER): 14 walkers, each on the vanilla sheet
it replaces as material regions, with new heads and costume cues patched in.
Run from the tool folder: python batches/r_g2.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402

# ====================================================================== GENTLEMAN -> Senate diplomat
# Bail-Organa-like: swept dark hair, trimmed beard; long crimson senate robe (R, b ruled) with a
# maroon mantle on the shoulders (M) and a gold stole down the front (T).
GE_HEAD_D = block(0, 10, """
................
.....HHHHHH.....
...HHhHHHhHHH...
..HHHhHHHhHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHFFFFFFFFHH..
.FHFFFFFFFFFFHF.
.FFFFkFFFFkFFFF.
..FFFkFFFFkFFF..
..BFFFFFFFFFFB..
...BBBFFFFBBB...""")
GE_BODY_D = block(0, 21, """
___MMMMTTMMMM___
__MMMMMTTMMMMM__
_MgMMRRTTRRMMgM_
___RRRRTTRRRR___
___RfRRTgRRfR___
___RRrRgTRrRR___
__RRfRRTgRRfRR__
__RrRRRgTRRRrR__
__RRRRRRRRRRRR__""")
GE_HEAD_U = block(0, 10, """
................
.....HHHHHH.....
...HHhHHHHhHH...
..HHHHHhHHHHHH..
..HhHHHHHHHhHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.FHHHHHHHHHHHHF.
.FHHHHHHHHHHHHF.
..HHHHHHHHHHHH..
...HHHHHHHHHH...
....HHHHHHHH....""")
GE_BODY_U = block(0, 21, """
___MMMMMMMMMM___
__MMMMMMMMMMMM__
_MMMMMMMMMMMMMM_
___RRRRRRRRRR___
___RRfRRRRfRR___
___RrRRRrRRrR___
__RRRfRRRRfRRR__
__RRrRRRRRRrRR__
__RRRRRRRRRRRR__""")
GE_HEAD_L = block(0, 10, """
................
......HHHHH.....
....HHHhHHHHH...
...HHhHHHHhHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..FFFFFHHHHHHH..
..FFFFFFHHHHHH..
..FkFFFFFHHHHH..
..FkFFFFFFHHH...
...BFFFFFFHH....
...BBBFFFBB.....""")
GE_BODY_L = block(0, 21, """
____MMMMMM______
____TTMMMMM_____
____Tg__________
____gT__________
________________
________________
_____RRRRRRR____
_____RrRfRRR____
_____RfRRrRR____""")
spec("gentleman", "Gentleman", "npc_2", "gentleman.png",
     "Senate diplomat in a crimson robe with a maroon mantle and gold stole (replaces the Gentleman).",
     "r_g2, B style: the Gentleman's body as regions (coat -> robe R, arms kept), new head with swept dark hair and a trimmed beard, maroon mantle M, gold stole T, robe lengthened to the ankles. Moves to NPC_2 for the red senate robe.",
     materials={"H": "c", "F": "s", "B": "c", "R": "b!", "M": "b", "T": "a"}, legend={"k": 15, "f": 10, "h": 11, "g": 5, "r": 8},
     accept={"step_change": "the floor-length robe hides the legs; the bob, arms and hem still move"},
     base="gentleman.png", remap={"c": "R", "b": "T", "a": "M", "w": "M"},
     patches={"down": [GE_HEAD_D, GE_BODY_D], "up": [GE_HEAD_U, GE_BODY_U], "left": [GE_HEAD_L, GE_BODY_L]})

# ====================================================================== DRAKE -> ANAKIN (Force vision)
# Shoulder-length brown hair parted in the middle (H with dark strands d), the scar over his
# right eye (x, skin outline), dark Jedi robe (O, ramp a with dark folds o: the vision's cold
# cast) open over a black tunic (T), leather belt (L) with a lightsaber hilt (h, l), blue-white
# rim light (W, g) on the shoulders and sleeves.
AN_HEAD_D = block(0, 10, """
................
.....HHHHHH.....
...HHHdHHdHHH...
..HHHdHHHHdHHH..
..HHdHHHHHHdHH..
.HHdHHHddHHHdHH.
.HHHHFFHHFFHHHH.
.HdFFFxFFFFFFdH.
.HdFFFkFFkFFFdH.
.HHFFFkFFkFFFHH.
..HFFxFFFFFFFH..
..HdFFFFFFFFdH..
...OOOFFFFOOO...""")
AN_BODY_D = block(0, 23, """
WgOOOOTkkTOOOOgW
FFoOoOTkkTOoOoFF
FFFooOLLLLOooFFF
.FFoOLlhLLOoFF..
..goOTTTTTTogo..
...ooTTTTTToo...
...ooTTkkTToo...
....kkk..kkk....""")
AN_HEAD_U = block(0, 10, """
................
.....HHHHHH.....
...HHHHdHHHHH...
..HHHHHdHHHHHH..
..HHdHHdHHHdHH..
.HHdHHHHdHHHdHH.
.HHHHdHHdHHHHHH.
.HdHHdHHHHdHHdH.
.HdHHHHdHHHdHdH.
.HHHdHHdHHdHHHH.
.HHHHHHHHHHHHHH.
..HdHHHHHHHHdH..
...HHHHHHHHHH...""")
AN_BODY_U = block(0, 23, """
WgOOOOOOOOOOOOgW
FFoOOOoOOoOOOoFF
FFFoOOoOOoOOoFFF
.FFooOoooooOoFF.
..ogoooOOooogo..
...oooooooooo...
...oooooooooo...
....kkk..kkk....""")
AN_HEAD_L = block(0, 10, """
................
......HHHHH.....
....HHHdHHHHH...
...HHdHHHHdHHH..
..HHdHHHdHHHdH..
..HdHHHHHHdHHHH.
..FFFHHHdHHHdHH.
..FxFFFHHHHdHHH.
..FkFFFFHHdHHHH.
..FkFFFFHHHHdHH.
..FFFFFFHHdHHH..
...FFFFFHdHHHH..
....FFFOHHHHH...""")
AN_BODY_L = block(0, 23, """
....TTOOOOOgW...
....TTOOOoOOo...
....LLOOOoOoo...
....lhOFFooOo...
....ooOFFoogo...
.....TTooooo....
......TToooo....
......kkkkk.....""")
spec("drake", "Drake", "npc_3", "elite_four/drake.png",
     "ANAKIN (Force vision): shoulder-length hair, scarred eye, dark Jedi robe over a black tunic, lightsaber hilt, blue-white rim light (replaces Drake).",
     "r_g2, B style: Drake's standing body as the frame (proportions, arms), new parted shoulder-length brown hair, the scar over his right eye, dark indigo robe (ramp a with dark folds, the vision's cold cast) open over a black tunic, belt with a lightsaber hilt, white and lavender rim light on the shoulders.",
     materials={"H": "c", "F": "s", "O": "a", "T": "k", "L": "c"}, legend={"k": 15, "x": 4, "W": 14, "g": 5, "d": 13, "o": 7, "h": 6, "l": 14},
     accept={"hair_rows": "parted hair falls to the jaw; the crown is short"},
     base="elite_four/drake.png", remap={"w": "O", "a": "O", "c": "O"},
     patches={"down": [AN_HEAD_D, AN_BODY_D], "up": [AN_HEAD_U, AN_BODY_U], "left": [AN_HEAD_L, AN_BODY_L]},
     kit="person16x32_still")

# ====================================================================== BEAUTY -> Core World socialite
# Auburn hair piled into a tall Coruscant updo (H) held by a silver diadem (D) with a green gem
# (e); side locks from the vanilla flips; a floor-length lavender gown (G, white panels W) with a
# green sash (S) and a pearl necklace (p).
BE_HEAD_D = block(0, 10, """
......HHHH......
.....HHhhHH.....
....DDDeeDDD....
...HHHHHHHHHH...
..HHHhHHHHhHHH..
..HHHFFFFFFHHH..
..HHFFFFFFFFHH..
.HHFFFFFFFFFFHH.
.HHFFFkFFkFFFHH.
_HHFFFkFFkFFFHH_
_HHFFFFFFFFFFHH_
__HHHFFFFFFHHH__""")
BE_BODY_D = block(0, 22, """
____FGpppGF_____
________________
____SSSSSSSS____
________________
________________
___GGGWGGWGGG___
__GGGfGGGGfGGG__
__GGfGGfGGGfGG__
...GGGGGGGGGG...""")
BE_HEAD_U = block(0, 10, """
......HHHH......
.....HHhhHH.....
....DDDDDDDD....
...HHHHHHHHHH...
..HHHhHHHHhHHH..
..HHHHHHHHHHHH..
..HHHHhHHhHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
_HHHHHHHHHHHHHH_
_HHHHHHHHHHHHHH_
__HHHHHHHHHHHH__""")
BE_BODY_U = block(0, 22, """
________________
________________
____SSSSSSSS____
________________
________________
___GGWGGGGWGG___
__GGGfGGGGfGGG__
__GGfGGfGGGfGG__
...GGGGGGGGGG...""")
BE_HEAD_L = block(0, 10, """
........HHHH....
.......HHhhHH...
.....DDDDDeD....
....HHHHHHHHHH..
...HHhHHHHhHHH..
..HHHHHHHHHHHH..
..FFFFHHHHHHHH..
..FFFFFHHHHHHH..
..FkFFFHHHHHHH..
..FkFFFFHHHHHH..
...FFFFFFHHHHH..
....FFFFFHHHH...""")
BE_BODY_L = block(0, 22, """
________________
________________
____SSSSSS______
________________
________________
____GGGGGGG_____
___GGfGGWGGG____
___GfGGGfGGG____
....GGGGGGGG....""")
spec("beauty", "Beauty", "npc_3", "beauty.png",
     "Core World socialite: tall auburn updo with a silver diadem, floor-length lavender gown with a green sash (replaces the Beauty).",
     "r_g2, B style: the Beauty's own body as regions (dress -> gown G, white panels W, hair flips kept as side locks), new tall Coruscant updo with a diadem and gem, pearl necklace, green sash, gown lengthened to the floor. Stays on NPC_3.",
     materials={"H": "c", "F": "s", "G": "a!", "S": "b", "D": "a"}, legend={"k": 15, "h": 11, "e": 8, "p": 14, "W": 5, "f": 6},
     accept={"step_change": "the floor-length gown hides the legs; the bob, arms and hem still move"},
     base="beauty.png", remap={"b": "H", "a": "G", "w": "G", "s": "F", "k": "H"},
     patches={"down": [BE_HEAD_D, BE_BODY_D], "up": [BE_HEAD_U, BE_BODY_U], "left": [BE_HEAD_L, BE_BODY_L]})

# ====================================================================== FISHERMAN -> angler
# A wide floppy brimmed hat (H) with a yellow band (Y), seen from above as a full-width ellipse;
# the red jacket kept, a brown tackle strap (T) with a pouch, a short rod held upright at the hip
# (r, dark; reel R) that stays below the hat; in the side view the rod points forward.
FI_HAT_D = block(0, 10, """
................
.....HHHHHH.....
....HHHHHHHH....
...HHhHHHHhHH...
...HYYYYYYYYH...
.HHHHHHHHHHHHHH.
HHHHHHHHHHHHHHHH
.HHHHHHHHHHHHHH.""")
FI_HAT_U = block(0, 10, """
................
.....HHHHHH.....
....HHHHHHHH....
...HHHhHHhHHH...
...HYYYYYYYYH...
.HHHHHHHHHHHHHH.
HHHHHHHHHHHHHHHH
.HHHHHHHHHHHHHH.
.FNNNNNNNNNNNNF.
..NNNNNNNNNNNN..
..NNNNNNNNNNNN..""")
FI_HAT_L = block(0, 10, """
................
......HHHHH.....
.....HHHHHHH....
....HHhHHhHHH...
....YYYYYYYYH...
.HHHHHHHHHHHHHH.
HHHHHHHHHHHHHHH.
.HHHHHHHHHHHHH..""")
FI_STRAP_D = block(0, 21, """
_____T__________
______T_________
_______T________
________TPP____r
_________PP____r
_______________R
_______________r""")
FI_STRAP_U = block(0, 18, """
r_______________
r_______________
r_______________
r______________T
r_____________T_
r____________T__
R___________T___
r__________T____
r__________PP___
r__________PP___""")
FI_ROD_L = block(0, 19, """
r_______________
.r______________
..r_____________
...rr___________
.....R__________""")
spec("fisherman", "Fisherman", "npc_2", "fisherman.png",
     "Angler: wide floppy brimmed hat with a yellow band, red jacket, tackle strap and pouch, a short rod at the hip (replaces the Fisherman).",
     "r_g2, B style: the Fisherman's own body as regions (jacket, trousers, boots kept), new wide floppy hat seen from above as a full-width ellipse with a yellow band, brown tackle strap and pouch, a rod held upright at the hip (no higher than the hat) that points forward in the side view. Stays on NPC_2.",
     materials={"H": "c", "Y": "a", "T": "c", "P": "c", "N": "c", "F": "s"}, legend={"k": 15, "h": 11, "r": 12, "R": 14},
     accept={},
     base="fisherman.png",
     patches={"down": [FI_HAT_D, FI_STRAP_D], "up": [FI_HAT_U, FI_STRAP_U], "left": [FI_HAT_L, FI_ROD_L]})

# ====================================================================== NORMAN -> DORAN
# The player's father as a Rebel-style pilot: Norman's own face, his hair re-lettered (H, dark
# brown) so the base ramp a can become an orange flight suit (U, trousers and front); flight
# goggles pushed up on the forehead (dark strap d, red lenses g with a white glint w); a brown
# leather pilot coat (C) with cream fleece lapels (L), a white squadron badge (p).
def hairify(y, rows, src="a", dst="H"):
    return block(0, y, "\n".join("".join(dst if c == src else "_" for c in r) for r in rows.strip().split("\n")))


NO_HAIR_D = hairify(11, """
......aaaa......
....aaaaaaaa....
...aaaaaaaaaa...
..aaasaaaasaaa..
..aassaaaassaa..
..sasssaasssas..
.ssassssssssass.
.ssassssssssass.
..sassksskssas..
...sassssssas...""")
NO_HAIR_U = hairify(11, """
......aaaa......
....aaaaaaaa....
...aaaaaaaaaa...
..aaaaaaaaaaaa..
..aaaaaaaaaaaa..
..saaaaaaaaaas..
.ssaaaaaaaaaass.
.ssaaaaaaaaaass.
..skaaaaaaaaks..
...skkaaaakks...""")
NO_HAIR_L = hairify(11, """
.....aaaaaa.....
....aaaaaaaa....
...aaaaaaaaaa...
..aaaassaaaaaa..
..aaasssaaaaaa..
..aassssaaaaaa..
..ssssssaaaaak..
..ssssssaaaakk..
..ssskssasskkk..
...ssssassssk...""")
NO_GOG_D = block(0, 13, """
___dggddddggd___
___dgwd__dgwd___""")
NO_COL_D = block(0, 21, """
__LLL______LLL__
__CCLLUUUULLCC__
____CCUUUUCp____
____CCUUUUCC____
____CCUUUUCC____""")
NO_GOG_U = block(0, 13, """
________________
__dddddddddddd__""")
NO_COL_U = block(0, 21, """
___LLLLLLLLLL___""")
NO_GOG_L = block(0, 13, """
___ddddddddd____
__gw____________""")
NO_COL_L = block(0, 21, """
________LL______
_______LL_______
____UUCCCCCC____
____UUCCCCCC____""")
spec("norman", "Norman", "npc_3", "gym_leaders/norman.png",
     "DORAN: the player's father, Mos Entha arena leader, as a veteran pilot: greying hair, flight goggles pushed up, rust-leather coat with fleece lapels over an olive flight suit (replaces Norman).",
     "r_g2, B style: Norman's own body as regions (face, hair, arms, trousers, walk kept), hair greyed on ramp a, flight goggles on the forehead, jacket -> rust-leather pilot coat C with cream fleece lapels L, shirt front -> olive flight suit U, white squadron badge. Moves to NPC_3 for the rust leather and olive suit.",
     materials={"H": "a", "L": "w/c", "C": "c", "U": "b"}, legend={"k": 15, "d": 13, "g": 11, "w": 14, "p": 14},
     accept={},
     base="gym_leaders/norman.png", remap={"c": "C"},
     patches={"down": [NO_HAIR_D, NO_GOG_D, NO_COL_D], "up": [NO_HAIR_U, NO_GOG_U, NO_COL_U], "left": [NO_HAIR_L, NO_GOG_L, NO_COL_L]})

# ====================================================================== HIKER -> prospector
# Tan mining helmet (H dome, B brim) with a headlamp (L, white; glow y), a bushy white beard (W),
# the blue work shirt and olive trousers kept; a rose canvas pack (P) with a rolled bedroll (Q)
# on the back, dark straps (S) over the shoulders, a short pickaxe at the hip (handle p, head K).
HI_HAT_D = block(0, 10, """
......HHHH......
....HHHHHHHH....
...HHHHLLHHHH...
..HHHHHLLHHHHH..
.HHHHHHyyHHHHHH.
.BBBBBBBBBBBBBB.
..BBBBBBBBBBBB..""")
HI_BEARD_D = block(0, 20, """
___cWWsssWWc____
____SWWWWWS_____
____S_WWW_S_____
____S_____S_____""")
HI_AXE_D = block(12, 21, """
KwKK
__p_
__p_""")
HI_HAT_U = block(0, 10, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.BBBBBBBBBBBBBB.
..BBBBBBBBBBBB..""")
HI_PACK_U = block(0, 20, """
___QQQQQQQQQQ___
__QQQQQQQQQQQQ__
__PPPPPPPPPPPP__
__PPPPPPPPPPPP__
__PPPPPPPPPPPP__
__PPPPPPPPPPPP__
___PPPPPPPPPP___""")
HI_HAT_L = block(0, 10, """
......HHHH......
....HHHHHHHH....
...LLHHHHHHHH...
..yLLHHHHHHHHH..
.HyHHHHHHHHHHHH.
BBBBBBBBBBBBBB..
..BBBBBBBBBBB...""")
HI_BEARD_L = block(0, 20, """
__WWW___________
__WWWW__________
___WW___________""")
HI_PACK_L = block(0, 20, """
__________QQQ___
_________QQQQQ__
__________PPPP__
__________PPPP__
__________PPPP__
__________PPP___""")
spec("hiker", "Hiker", "npc_1", "hiker.png",
     "Prospector: tan mining helmet with a headlamp, bushy white beard, blue work shirt, rose canvas pack with a bedroll, short pickaxe at the hip (replaces the Hiker).",
     "r_g2, B style: the Hiker's own body as regions (shirt, trousers, boots, arms kept), new domed mining helmet with a brim and a headlamp, white beard, pack straps, a canvas pack with a bedroll on the back, a short pickaxe at hip height. Stays on NPC_1.",
     materials={"H": "c", "B": "c", "W": "w/c", "P": "a", "Q": "c"}, legend={"k": 15, "L": 14, "y": 5, "S": 13, "p": 11, "K": 15, "w": 14},
     accept={},
     base="hiker.png", remap={"a": "H"},
     patches={"down": [HI_HAT_D, HI_BEARD_D, HI_AXE_D], "up": [HI_HAT_U, HI_PACK_U], "left": [HI_HAT_L, HI_BEARD_L, HI_PACK_L]})

# ====================================================================== MAN_3 -> trader
# Mos Eisley trader: a cream desert head wrap (W) with a hanging tail, dark sideburns (H) and a
# moustache (M); the jacket turned into a brown vest (V) over a mustard shirt (Y), a red sash (R)
# at the waist with a gold buckle (g).
M3_HEAD_D = block(0, 11, """
......WWWW......
....WWWWWWWW....
...ffWWWWWWff...
..WWWffffffWWW..
..WWWWWWWWWWWW..
.HffWWWWWWWWffH.
_sHssssssssssHs_""")
M3_FACE_D = block(0, 20, """
___sMMMMMMMMs___""")
M3_SASH_D = block(0, 26, """
__RRRRRgRRRRR___""")
M3_HEAD_U = block(0, 11, """
......WWWW......
....WWWWWWWW....
...ffWWWWWWff...
..WWWffffffWWW..
..WWWWWWWWWWWW..
.WffWWWWWWWWffW.
.sWWWffWWffWWWs.
.sHHHHWWWWHHHHs.
..HHHHHWWHHHHH..
...HHHHWWHHHH...""")
M3_SASH_U = block(0, 26, """
__RRRRRRRRRRR___""")
M3_HEAD_L = block(0, 11, """
......WWWWW.....
....WWWWWWWW....
...fWWWWWWffW...
..WWffffffWWWW..
..WWWWWWWWWWWW..
..WWWWWWWWWfWWWW
..ssssHWWWfWWW.W
..ssssHHHHHHHH.W""")
M3_FACE_L = block(0, 20, """
___MM___________""")
M3_SASH_L = block(0, 26, """
____RRRRRRR_____""")
spec("man_3", "Man3", "npc_2", "man_3.png",
     "Mos Eisley trader: cream desert head wrap, moustache, brown vest over a mustard shirt, red sash with a gold buckle (replaces Man 3).",
     "r_g2, B style: Man 3's own body as regions (jacket -> brown vest V, shirt -> mustard Y, arms and walk kept), new cream head wrap with a hanging tail, dark sideburns and a moustache, red sash with a buckle. Stays on NPC_2.",
     materials={"W": "w/c", "H": "c", "M": "c", "V": "c", "Y": "a", "R": "b"}, legend={"k": 15, "f": 11, "g": 5},
     accept={},
     base="man_3.png", remap={"a": "H", "b": "V", "w": "Y"},
     patches={"down": [M3_HEAD_D, M3_FACE_D, M3_SASH_D], "up": [M3_HEAD_U, M3_SASH_U], "left": [M3_HEAD_L, M3_FACE_L, M3_SASH_L]})

# ====================================================================== MAUVILLE_OLD_MAN_2 -> Mos Espa storyteller
# An old Tatooine storyteller: a tan desert hood (H) and cloak (R, the old man's coat), a long
# white beard (W) and bushy white brows (e), a blue-grey wrap tunic underneath (T) with a rose
# sash (P).
OS_HEAD_D = block(0, 10, """
................
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHFFFFFFHHH..
.HHHFFFFFFFFHHH.
.HHFFeeFFeeFFHH.
.HHFFFkFFkFFFHH.
.HHFFFkFFkFFFHH.
.HHFWWFFFFWWFHH.
..HHWWWWWWWWHH..
..RRHWWWWWWHRR..
..RRRRWWWWRRRR..
__RRRRRWWRRRRR__""")
OS_SASH_D = block(0, 25, """
___PPPPPPPPPP___""")
OS_HEAD_U = block(0, 10, """
................
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHdHHHHH..
.HHHHHHHdHHHHHH.
.HHHHHHHdHHHHHH.
.HHHHHHdHHHHHHH.
.HHHHHHdHHHHHHH.
.HHHHHHdHHHHHHH.
..HHHHHHdHHHHH..
..RRHHHHdHHHRR..
..RRRRHHdHRRRR..""")
OS_SASH_U = block(0, 25, """
___PPPP__PPPP___""")
OS_HEAD_L = block(0, 10, """
................
.......HHHH.....
.....HHHHHHHH...
....HHHHHHHHHH..
...HHHHHHHHHHH..
..HFFFFHHHHHHHH.
..FFFFFFHHHHHHH.
..eeFFFFHHHHHHH.
..FkFFFFHHHHHHH.
..FkFFFFHHHHHHH.
..WWFFFFHHHHHH..
..WWWWFHHHHHH...
...WWWWHHHHH....
...WWWRRRRR.....
____WW__________""")
OS_SASH_L = block(0, 25, """
___PPPPPPP______""")
spec("mauville_old_man_2", "Storyteller", "npc_1", "mauville_old_man_2.png",
     "Mos Espa storyteller: tan desert hood and cloak, long white beard, bushy white brows, blue-grey wrap tunic with a rose sash (replaces the Mauville old man).",
     "r_g2, B style: the old man's own body as regions (coat -> tan cloak R, shirt and trousers -> blue-grey tunic T, clasped hands kept), new desert hood framing the face, long white beard over the chest, white brows, rose sash. Stays on NPC_1.",
     materials={"H": "c@", "F": "s", "W": "w/c", "R": "c", "T": "b", "P": "a"}, legend={"k": 15, "e": 14, "d": 13},
     accept={},
     base="mauville_old_man_2.png", remap={"a": "R", "b": "T", "c": "T", "w": "W"},
     patches={"down": [OS_HEAD_D, OS_SASH_D], "up": [OS_HEAD_U, OS_SASH_U], "left": [OS_HEAD_L, OS_SASH_L]})

# ====================================================================== POKEFAN_F -> beast fan (f)
# A fan in Leia cosplay: brown hair parted in the middle with two round side buns (B, round),
# the red top and yellow skirt kept; she hugs a porg plush to her chest (brown cap O, white face
# W, black eyes, orange beak).
PF_HEAD_D = block(0, 11, """
......HHHH......
.....HHHHHH.....
....HHHHHHHH....
...HHHHddHHHH...
.BBHHHHddHHHHBB.
BBdBHHFFFFHHBdBB
BdBdHFFFFFFHdBdB
BBdBFFFFFFFFBdBB
.BBHFFkFFkFFHBB.
..HFFFkFFkFFFH..""")
PF_PORG_D = block(5, 22, """
.OOOO.
OWWWWO
WkWWkW
WWaaWW
.WWWW.""")
PF_HEAD_U = block(0, 11, """
......HHHH......
.....HHHHHH.....
....HHHHHHHH....
...HHHHddHHHH...
.BBHHHHddHHHHBB.
BBdBHHHddHHHBdBB
BdBdHHHddHHHdBdB
BBdBHHHHHHHHBdBB
.BBHHHHHHHHHHBB.
..HHHHHHHHHHHH..""")
PF_HEAD_L = block(0, 11, """
......HHHH......
....HHHHHHH.....
...HHHHHHHHH....
..HHHHHHHHHHH...
..HHHHHHHHHBB...
..FFFHHHHHBdBB..
..FFFFFHHBdBdB..
..FFFFFFHBBdBB..
..FkFFFFHHBBB...""")
PF_PORG_L = block(1, 23, """
.OOO.
OWWWO
kWWWW
aWWWW
.WWW.""")
spec("pokefan_f", "PokefanF", "npc_2", "pokefan_f.png",
     "Beast fan (f): Leia-style side buns, red top and yellow skirt, hugging a porg plush (replaces the Pokefan F).",
     "r_g2, B style: the Pokefan F's own body as regions (top, skirt, arms, walk kept), new hair parted in the middle with two round side buns in Leia cosplay, a porg plush hugged to the chest (brown cap, white face, black eyes, orange beak). Stays on NPC_2.",
     materials={"H": "c", "B": "c@", "F": "s", "O": "c", "W": "w/c", "Y": "a", "R": "b"}, legend={"k": 15, "d": 13, "a": 6},
     accept={},
     base="pokefan_f.png", remap={"c": "H", "a": "Y", "b": "R", "w": "Y"},
     patches={"down": [PF_HEAD_D, PF_PORG_D], "up": [PF_HEAD_U], "left": [PF_HEAD_L, PF_PORG_L]})

# ====================================================================== RICH_BOY -> young noble
# A young Alderaanian noble: the neat orange-brown hair kept, a silver circlet (D) with a white
# gem; the green tunic kept, with a high white collar (L), a short lavender-grey cape (K, ramp a) over
# the shoulders and down the back, and a dark belt (Y) with a silver clasp.
RB_CIRC_D = block(0, 14, """
__DDDDDeDDDDDD__""")
RB_BODY_D = block(0, 21, """
__KLLL____LLLK__
_KK__________KK_""")
RB_BELT_D = block(0, 26, """
___YYYYgYYYYY___""")
RB_CIRC_U = block(0, 14, """
__DDDDDDDDDDDD__""")
RB_BODY_U = block(0, 20, """
___LLLLLLLLLL___
__KKKKKKKKKKKK__
_KKKKKKKKKKKKKK_
_KKKKKKKKKKKKKK_
__KKKKKKKKKKKK__
__KKKKKKKKKKKK__
__KKKKKKKKKKKK__
___KKKKKKKKKK___""")
RB_CIRC_L = block(0, 14, """
__eDDDDDDDDDDD__""")
RB_BODY_L = block(0, 21, """
______LLKKK_____
_______KKKKK____
________KKKKK___
________KKKKK___
_________KKKK___
_________KKKK___""")
RB_BELT_L = block(0, 26, """
____YYYY________""")
spec("rich_boy", "RichBoy", "npc_3", "rich_boy.png",
     "Young noble: neat hair with a silver circlet, green tunic with a high white collar, short lavender-grey cape, dark belt with a silver clasp (replaces the Rich Boy).",
     "r_g2, B style: the Rich Boy's own body as regions (hair, green tunic, cravat, arms, walk kept), new silver circlet with a gem, high white collar, short lavender-grey cape over the shoulders and down the back, dark belt with a clasp. Stays on NPC_3.",
     materials={"D": "a", "L": "w/a", "K": "a!", "Y": "c"}, legend={"k": 15, "e": 14, "g": 5},
     accept={},
     base="rich_boy.png",
     patches={"down": [RB_CIRC_D, RB_BODY_D, RB_BELT_D], "up": [RB_CIRC_U, RB_BODY_U], "left": [RB_CIRC_L, RB_BODY_L, RB_BELT_L]})

# ====================================================================== SCIENTIST_1 -> researcher
# The Scientist's own hair kept; the glasses replaced by a scanner monocle over one eye (black
# frame, green lens g with a glint); a pale lavender-grey lab coat (C; the black hair outline re-lettered H onto the hair ramp) over a
# green shirt and tie; a datapad with a glowing green screen held at the hip.
SC_FACE_D = block(0, 17, """
_sskssssskkkkss_
_sskssksskggkss_
__sssskssgwksss_""")
SC_PAD_D = block(10, 24, """
kkkk
kggk
kkkk""")
SC_FACE_L = block(0, 17, """
__kkkss_________
__kgwss_________
__kkkss_________""")
SC_MONO_L = block(0, 16, """
____kkk_________""")
SC_PAD_L = block(2, 24, """
kkk
gkk
kkk""")
spec("scientist_1", "Scientist1", "npc_3", "scientist_1.png",
     "Researcher: scanner monocle over one eye, pale grey lab coat over a green shirt and tie, a glowing green datapad at the hip (replaces Scientist 1).",
     "r_g2, B style: the Scientist's own body as regions (hair, arms, walk kept; lab coat C on ramp a, black hair outline and shoes re-lettered onto the brown hair ramp), the round glasses replaced by a scanner monocle with a green lens, a datapad with a green screen at hip height. Stays on NPC_3.",
     materials={"C": "a", "W": "w/a", "H": "c"}, legend={"k": 15, "g": 8, "w": 14},
     accept={},
     base="scientist_1.png", remap={"a": "C", "w": "W", "k": "H"},
     patches={"down": [SC_FACE_D, SC_PAD_D], "up": [], "left": [SC_FACE_L, SC_PAD_L]})

# ====================================================================== TEALA -> HOLONET CLUB attendant
# Teala's long blue hair and pink uniform kept; a comlink headset (olive earcups E over the ears,
# a dark mic boom m to the mouth); a holo-projector puck (k) in her clasped hands throwing a
# small pale-blue hologram (h, glint W) in front of her uniform.
TE_MIC_D = block(0, 16, """
_EE_____________
EEE_____________
EEE_____________
_m______________
__mmm___________""")
TE_HOLO_D = block(0, 22, """
_______W________
______hhh_______
_____hhhhh______
______kkk_______""")
TE_MIC_U = block(0, 16, """
_EE__________EE_
EEE__________EEE
EEE__________EEE""")
TE_MIC_L = block(0, 16, """
______EEE_______
______EEE_______
______EEE_______
____mm__________
__mm____________""")
TE_HOLO_L = block(0, 22, """
__W_____________
_hhh____________
hhhhh___________
_kkk____________""")
spec("teala", "Teala", "npc_1", "teala.png",
     "TEALA, HOLONET CLUB attendant: long blue hair, comlink headset with a mic boom, pink uniform, a holo-projector showing a small hologram (replaces Teala).",
     "r_g2, B style: Teala's own body as regions (hair, pink uniform, clasped hands, walk kept), new comlink headset (olive earcups, dark mic boom), a projector puck in her hands throwing a small pale-blue hologram. Stays on NPC_1.",
     materials={"E": "c"}, legend={"k": 15, "h": 8, "W": 14, "m": 13},
     accept={},
     base="teala.png",
     patches={"down": [TE_MIC_D, TE_HOLO_D], "up": [TE_MIC_U], "left": [TE_MIC_L, TE_HOLO_L]})

# ====================================================================== TWIN -> twin kid
# A Tatooine kid (both twins share the sheet): the big bow replaced by a top-knot (H) tied with a
# red band (R); the dress turned into a cream wrap tunic (T, edged maroon) with a dark crossover
# fold (d), a brown belt (B) with a yellow buckle (y), brown boots (O).
TW_HEAD_D = block(0, 14, """
................
......HHHH......
.....HHhHHH.....
......RRRR......
....HHHHHHHH....""")
TW_BELT_D = block(0, 28, """
____BBByBBBB____""")
TW_HEAD_U = block(0, 14, """
................
......HHHH......
.....HHHhHH.....
......RRRR......
....HHHHHHHH....""")
TW_HEAD_L = block(0, 14, """
................
.........HHH....
........HHhHH...
.........RRR....
.....HHHHHHHH...""")
TW_BELT_L = block(0, 28, """
____BByBBBB_____""")
spec("twin", "Twin", "npc_2", "twin.png",
     "Twin kid (both twins): top-knot tied with a red band, cream wrap tunic with a crossover fold, brown belt and boots (replaces the Twins).",
     "r_g2, B style: the Twin's own small body as regions (face, hair, arms, walk kept), the big bow replaced by a top-knot with a red band, the dress turned into a cream Tatooine wrap tunic with a crossover fold, belt with a buckle, brown boots. Stays on NPC_2.",
     materials={"H": "c", "R": "b", "T": "w/c", "B": "c", "O": "c"}, legend={"k": 15, "h": 11, "d": 12, "y": 5},
     accept={},
     base="twin.png", remap={"a": "T", "w": "d", "b": "O"},
     patches={"down": [TW_HEAD_D, TW_BELT_D], "up": [TW_HEAD_U, TW_BELT_D], "left": [TW_HEAD_L, TW_BELT_L]})

# ====================================================================== WOMAN_2 -> spaceport worker (f)
# Ground crew: a green work cap (C) with a visor (V), green ear defenders (E), her long hair kept
# under it; the long dress turned into baggy grey coveralls (J, ramp a) split into two legs, a
# white reflective band (R), a brown tool belt (B) with a white tool (t), dark boots (O).
W2_CAP_D = block(0, 11, """
......CCCC......
....CCCCCCCC....
...CCChCChCCC...
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..
...VVVVVVVVVV...""")
W2_EARS_D = block(0, 17, """
EE____________EE
EE____________EE
EE____________EE""")
W2_BODY_D = block(0, 24, """
___BBBtBBBBBB___
________________
___RRRRRRRRRR___
________________
_______.._______
___JJJJ..JJJJ___
____OOO..OOO____""")
W2_CAP_U = block(0, 11, """
......CCCC......
....CCCCCCCC....
...CCCCCCCCCC...
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..
..CCCCCHHCCCCC..
......HHHH......""")
W2_EARS_U = block(0, 17, """
EE____________EE
EE____________EE
EE____________EE""")
W2_BODY_U = block(0, 24, """
________________
________________
___RRRRRRRRRR___""")
W2_CAP_L = block(0, 11, """
......CCCCC.....
....CCCCCCCC....
...CChCCChCCC...
..CCCCCCCCCCCC..
.VVVCCCCCCCCCC..
VVVV____________""")
W2_EARS_L = block(0, 17, """
________EE______
________EE______
_________E______""")
W2_BODY_L = block(0, 25, """
_____BtBBB______
________________
____RRRRRRRR____""")
spec("woman_2", "Woman2", "npc_3", "woman_2.png",
     "Spaceport worker (f): green work cap and ear defenders, baggy grey coveralls with a white reflective band, tool belt and boots (replaces Woman 2).",
     "r_g2, B style: Woman 2's own body as regions (long hair, arms, walk kept; dress -> grey coveralls J split into two legs), new green work cap with a visor, green ear defenders, white reflective band, brown tool belt with a tool, dark boots. Stays on NPC_3.",
     materials={"C": "b", "V": "b", "E": "b", "J": "a", "R": "w/a", "B": "c", "O": "c", "H": "c"}, legend={"k": 15, "h": 8, "t": 14},
     accept={},
     base="woman_2.png", remap={"b": "J", "a": "J", "w": "J", "c": "H"},
     patches={"down": [W2_CAP_D, W2_EARS_D, W2_BODY_D], "up": [W2_CAP_U, W2_EARS_U, W2_BODY_U, block(5, 17, "_HHHH_\nHHHHHH\n_HHHH_")],
              "left": [W2_CAP_L, W2_EARS_L, W2_BODY_L, block(12, 15, "_H_\nHHH\nHHH\n_H_")]})

print("ok")

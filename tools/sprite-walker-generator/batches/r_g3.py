"""Group 3 (worker 3), B style: each vanilla sheet is the body as regions, new heads and costume
cues are patched in, the learned shader picks every tone. Writes art/<name>.yaml.
Run from the tool folder: python batches/r_g3.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402

# ====================================================================== GIRL_1: moisture-farm girl
# White desert headwrap with a red stripe hanging to the shoulders, brown fringe under it,
# sand tunic (vanilla top + sleeves + shoes), brown wrap skirt.
G1_D = block(0, 10, """
................
......WWWW......
....WWWWWWWW....
...WWWWWWWWWW...
..WWWWWWWWWWWW..
..RRRRRRRRRRRR..
.WWWHHHHHHHHWWW.
.WWHH______HHWW.
.WW__________WW.
.WW___k__k___WW.
.WW___k__k___WW.
..W__________W..""")
G1_U = block(0, 10, """
................
......WWWW......
....WWWWWWWW....
...WWWWWWWWWW...
..WWWWWWWWWWWW..
..RRRRRRRRRRRR..
.WWWWWWWWWWWWWW.
.WWWWWWRRWWWWWW.
.WWWWWRRRRWWWWW.
.WWWWWWRRWWWWWW.
.WWWWWWWWWWWWWW.
._WWWWWWWWWWWW_.
..__WWWWWWWW__..""")
G1_L = block(0, 10, """
................
......WWWWW.....
....WWWWWWWW....
...WWWWWWWWWW...
..WWWWWWWWWWWW..
..RRRRRRRRRRRR..
..HHHWWWWWWWWW..
..HH_HHWWWWWWWW.
..____HWWWWWWWW.
..___k__WWWWWWW.
..___k_____WWWW.
..._________WWW.
....______WWWW..""")
spec("girl_1", "Girl1", "npc_2", "girl_1.png",
     "Moisture-farm girl in a white desert headwrap and wrap skirt (replaces Girl 1).",
     "Group 3, B style: Girl 1's own body as regions (top + sleeves + shoes -> faded red tunic T, skirt -> brown wrap K), new white headwrap with a sand band and a knot at the back, hanging to the shoulders, brown fringe.",
     materials={"H": "c", "T": "b", "K": "c", "W": "w/c", "R": "a"}, legend={"k": 15},
     accept={},
     base="girl_1.png", remap={"c": "H", "b": "T", "a": "K"},
     patches={"down": [G1_D], "up": [G1_U], "left": [G1_L]})

# ====================================================================== MAN_4: bearded spacer
# Man 4's dark hair, a full dark beard and moustache, flight goggles pushed up on the forehead
# (steel lenses with a glint on a grey strap), grey spacer jacket over a maroon shirt.
M4_D = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HGGGGHHGGGGH..
.HHGLWGHHGLWGHH.
________________
________________
___B__k__k__B___
...BBsBBBBsBB...
____BBBBBBBB____
____BBBBBBBB____
______BBBB______""")
M4_U = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..GGGGGGGGGGGG..
.HHHHHHHHHHHHHH.""")
M4_L = block(0, 11, """
......HHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..GLWGGGGGGGGG..
..GGGHHHHHHHHH..
________________
________________
________________
__BBBBBBB_______
____BBBBBB______
_____BBBB_______
_____BBB________""")
spec("man_4", "Man4", "npc_3", "man_4.png",
     "Bearded spacer with flight goggles on his forehead (replaces Man 4).",
     "Group 3, B style: Man 4's own body as regions (jacket -> grey spacer jacket J, shirt -> green V, trousers T), auburn hair with a full beard and moustache, goggles with green lenses pushed up on the forehead.",
     materials={"H": "c", "B": "c", "T": "c", "J": "a", "V": "b", "G": "a"}, legend={"k": 15, "L": 9, "W": 14},
     accept={},
     base="man_4.png", remap={"a": "T", "c": "J", "b": "V"},
     patches={"down": [M4_D], "up": [M4_U], "left": [M4_L]})

# ====================================================================== MOM: homesteader
# Auburn hair swept back into a low bun (Beru-style), brown homestead tunic, sand skirt.
MOM_D = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHssssssHHH..
.HHHssssssssHHH.
.HHssskssksssHH.
.HHssskssksssHH.
.HHssssssssssHH.
.HHHssssssssHHH.
..HH________HH..""")
MOM_U = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHNNHHHHH..
..HHHHHNNHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..""")
MOM_L = block(0, 11, """
......HHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..sHHHHHHHHHHH..
..ssssHHHHHHHH..
..sssksHHHHHHHN.
..sssksssHHHHNN.
...ssssssHHHHNN.
....ssssssHHHH..
.....ss__HHHH...""")
spec("mom", "Mom", "npc_2", "mom.png",
     "MOM: the player's mother as a moisture-farm homesteader (replaces Mom).",
     "Group 3, B style: Mom's own body as regions (shirt -> cream homespun tunic T, skirt -> ochre wrap K, belt Y red), new brown hair swept back into a low bun.",
     materials={"H": "c", "N": "c", "T": "w/c", "K": "a", "Y": "b"}, legend={"k": 15},
     accept={},
     base="mom.png", remap={"b": "T", "a": "K", "c": "Y"},
     patches={"down": [MOM_D], "up": [MOM_U], "left": [MOM_L]})

# ====================================================================== WOMAN_3: trader with satchel
# Woman 3's long brown hair under a white cloth headband, sand tunic, red-brown skirt, a dark
# leather strap across the chest to a satchel on the right hip.
W3_D = block(3, 22, """
_WWWWWWWW_
___WWWW___""")
W3_U = block(3, 22, """
_WWWWWWWW_""")
W3_L = block(4, 22, """
_WWWWWW""")
W3_STRAP_D = block(4, 23, """
S________
_S_______
__SS_____
____SPPPP
_____PPPP
_____PPPP""")
W3_STRAP_U = block(2, 23, """
_________S
_______SS_
_____SS___
PPPPS_____
PPPP______
PPPP______""")
spec("woman_3", "Woman3", "npc_2", "woman_3.png",
     "Desert trader with a neck scarf and a satchel on a shoulder strap (replaces Woman 3).",
     "Group 3, B style: Woman 3's own body as regions (sleeves -> red T, vest + skirt -> brown leather K), long brown hair, a sand scarf at the neck, leather strap across the chest to a canvas satchel on the hip.",
     materials={"H": "c", "T": "b", "K": "c", "Y": "w/c", "W": "a", "S": "c", "P": "a@"}, legend={"k": 15},
     accept={},
     base="woman_3.png", remap={"c": "H", "a": "T", "b": "K", "w": "Y"},
     patches={"down": [W3_D, W3_STRAP_D], "up": [W3_U, W3_STRAP_U], "left": [W3_L, block(6, 25, "PPPP\nPPPP\nPPPP")]})

# ====================================================================== ANABEL: AURRA SING
# Chalk-white bald head (hand-shaded: white W, pale grey L/M, grey outline O) with a red topknot and ponytail (R) and
# a black cranial antenna; maroon bodysuit (Anabel's suit -> U), navy gloves (G), tan leather
# belt (Y, skin ramp), long rifle slung across her back (f stock, F barrel).
AS_D = block(0, 8, """
...........k....
......RR...k....
.....RRRR..k....
.....RRRR..k....
....OORROOOk....
...OWWWWWWWWO...
..OWWWWWWWWWLO..
.OWWWWWWWWWWWLO.
.OWWWWWWWWWWLLO.
.OLWWWWWWWWWLLO.
.OLWWddWWddWLLO.
.OLWWWkWWkWWLLO.
.OLLLWkWWkWLLMO.
..OOLLWmmWLMOO..
....OMMMMMMO....""")
AS_U = block(0, 8, """
...........k....
......RR...k....
.....RRRR..k....
.....RRRR..k....
....OORROOOk....
...OWWWRRWWWO...
..OWWWWRRWWWLO..
.OWWWWWRRWWWWLO.
.OWWWWWRRWWWLLO.
.OLWWWWRRWWWLLO.
.OLWWWWRRWWLLLO.
.OLLWWWRRWLLLMO.
.OLLLWWRRLLLLMO.
..OOLLLRRLLMOO..
....OMMRRMMO....
_______RR_______
_______RR_______""")
AS_L = block(0, 8, """
.........k......
.........k.RR...
.........kRRRR..
.........kRRRR..
......OOOkRRRR..
....OOWWWWWWRO..
...OWWWWWWWWLO..
..OWWWWWWWWWWLOR
.OWWWWWWWWWWLLOR
.OWWWWWWWWWLLLRR
.OddWWWWWWLLLLRR
.OWkWWWWWLLLLMR.
.OWkWWWWLLLLLMR.
..mWWWWWLLLMMO..
...OLLLLMMMMO...""")
AS_RIFLE_U = block(4, 21, """
_______FF
______F__
_____F___
____F____
___f_____
__ff_____
_ff______
_f_______""")
AS_RIFLE_L = block(10, 19, """
___F
___F
__F_
__F_
_F__
_f__
ff__
f___""")
spec("anabel", "Anabel", "npc_4", "frontier_brains/anabel.png",
     "AURRA SING: chalk-white bald bounty hunter with a red topknot, head antenna and a long rifle on her back (replaces Anabel).",
     "Group 3, B style: Anabel's own body as regions (suit -> maroon bodysuit U, arms -> navy gloves G, belt -> tan leather Y), new chalk-white bald head hand-shaded in white and pale grey, red topknot and ponytail, a black cranial antenna, a long rifle slung across her back.",
     materials={"R": "b", "U": "b", "G": "a", "Y": "s", "B": "a"}, legend={"k": 15, "m": 9, "d": 13, "F": 15, "f": 12, "W": 14, "L": 11, "M": 12, "O": 13},
     accept={"height": "the cranial antenna rises above the head (Aurra Sing's signature)", "hair_rows": "bald: a topknot instead of hair",
             "step_change": "the hand-shaded chalk-white head bobs without changing tone; the body keeps Anabel's own walk",
             "skin_tones": "Aurra Sing's chalk-white skin is the grey ramp; the skin ramp is only her leather belt"},
     base="frontier_brains/anabel.png", remap={"b": "U", "s": "G", "c": "U", "a": "B", "w": "U"},
     patches={"down": [AS_D, block(5, 26, "YYYYYY")], "up": [AS_RIFLE_U, AS_U, block(4, 26, "YYY__YYY")], "left": [AS_RIFLE_L, AS_L, block(5, 26, "YYYYY")]})

# ====================================================================== GLACIA: KI-ADI-MUNDI
# Stand-only, so the whole figure is redrawn: a tall egg-shaped Cerean cranium (K, skin as a
# round volume) over a face (s), white hair, moustache and beard edged in frost blue (H, M, B),
# olive-tan Jedi robe (R) open over a frost-blue tunic (V) like a Force vision, belt Y, boots D.
KA_D = block(0, 5, """
......KKKK......
.....KKKKKK.....
....KKKKKKKK....
....KKKKKKKK....
...KKKKKKKKKK...
...KKKKKKKKKK...
...KKKKKKKKKK...
..KKKKKKKKKKKK..
..KKKKKKKKKKKK..
..KKKKKKKKKKKK..
.HKKKKKKKKKKKKH.
.HH2MM1111MM2HH.
.HH221e11e122HH.
.HH332e22e233HH.
.HH4333333334HH.
.HH4MMMMMMMM4HH.
..HBBBBBBBBBBH..
..RRBBBBBBBBRR..
.RRRRBBBBBBRRRR.
RRRRVVBBBBVVRRRR
RRRRVVVBBVVVRRRR
RssRVVVVVVVVRssR
.RRRYYYYYYYYRRR.
..RRRVVVVVVRRR..
..RRRVVVVVVRRR..
...DDD....DDD...
................""")
KA_U = block(0, 5, """
......KKKK......
.....KKKKKK.....
....KKKKKKKK....
....KKKKKKKK....
...KKKKKKKKKK...
...KKKKKKKKKK...
...KKKKKKKKKK...
..KKKKKKKKKKKK..
..KKKKKKKKKKKK..
..KKKKKKKKKKKK..
.HKKKKKKKKKKKKH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
..RRHHHHHHHHRR..
.RRRRRHHHHRRRRR.
RRRRRRRQQRRRRRRR
RRRRRRRQQRRRRRRR
RRRRRRRQQRRRRRRR
.RRRYYYYYYYYRRR.
..RRRRRQQRRRRR..
..RRRRRQQRRRRR..
...DDD....DDD...
................""")
KA_L = block(0, 5, """
......KKKK......
.....KKKKKK.....
.....KKKKKKK....
....KKKKKKKK....
....KKKKKKKKK...
...KKKKKKKKKK...
...KKKKKKKKKK...
..KKKKKKKKKKKK..
..KKKKKKKKKKKK..
..KKKKKKKKKKKK..
..KKKKKKKKKKHH..
..MM11112HHHHH..
..21e1122HHHHHH.
..32e2223HHHHHH.
..3333334HHHHHH.
.MMMM3344HHHHH..
.BBBBBsssHHHH...
.BBBBBRRRRHHR...
..BBBRRRRRRRR...
...RRRRRRRRRRR..
...RVVsRRRRRRR..
...RVVsRRRRRRR..
...RYYYYYRRRRR..
...RVVVRRRRRR...
...RVVVRRRRRR...
....DDD.DDD.....
................""")
spec("glacia", "Glacia", "npc_1", "elite_four/glacia.png",
     "KI-ADI-MUNDI (Force vision): tall Cerean cranium, white beard, Jedi robes over a frost-blue tunic (replaces Glacia).",
     "Group 3, B style (stand-only, figure redrawn over Glacia's frame): tall egg-shaped Cerean cranium over a bearded face, white hair, moustache and beard edged in frost blue, olive-tan Jedi robe open over a frost-blue tunic.",
     materials={"K": "s@", "H": "w/b", "B": "w/b", "M": "w/b", "R": "c!", "Q": "c", "V": "b", "Y": "c", "D": "c"}, legend={"k": 15, "q": 9, "e": 15, "1": 1, "2": 2, "3": 3, "4": 4},
     accept={"height": "the Cerean cranium is a head taller than a human's (Ki-Adi-Mundi's signature)", "hair_rows": "the tall bald cranium stands in for hair",
             "head_w": "the Cerean cranium is an egg narrower than a human head; hair and beard make the face 14 wide",
             "eye_row": "eyes sit low on the face under white brows, 12 rows below the top of the tall cranium"},
     base="elite_four/glacia.png",
     patches={"down": [KA_D], "up": [KA_U], "left": [KA_L]},
     kit="person16x32_still")

# ====================================================================== ROXANNE: BIGGS DARKLIGHTER
# Stand-only, figure redrawn: short dark-brown hair with a side part, thin moustache, orange
# flight suit (F) under a white pilot vest (V) with a chest box, red collar (C), dark belt and
# boots, a datapad in his right hand.
BD_D = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.4HHH11111HHHH4.
.42111111111124.
.42221e11e12224.
..4322e22e2234..
..4332ZZZZ2334..
...4333333334...
..FFVVCssCVVFF..
.FFFVVVXXVVVFFF.
.FFFVVVXrVVVFFF.
.ssFYYYYYYYYFss.
...FFFFFFFFFF...
...FFFFFFFFFF...
...FFFF..FFFF...
....KKK..KKK....
................""")
BD_U = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.sHHHHHHHHHHHHs.
.sHHHHHHHHHHHHs.
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
...HHHHHHHHHH...
....ssssssss....
..FFCCCCCCCCFF..
.FFFVVVVVVVVFFF.
.FFFVVVVVVVVFFF.
.ssFYYYYYYYYFss.
...FFFFFFFFFF...
...FFFFFFFFFF...
...FFFF..FFFF...
....KKK..KKK....
................""")
BD_L = block(0, 11, """
......HHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..1HHHHHHHHHHH..
..1111HHHHHHH...
..21e112HHHHH...
..32e22224HHH...
..Z3333324H.....
...44333344.....
....CVVVFFF.....
....VVVFFFFF....
....VXVFFFFF....
....YYYYFssF....
.....FFFFFF.....
.....FFFFF......
.....FFFFF......
.....KKKK.......
................""")
BD_PAD = block(12, 25, """
DDD
DED
DDD""")
BD_PAD_L = block(9, 26, """
DDD
DED""")
spec("roxanne", "Roxanne", "npc_2", "gym_leaders/roxanne.png",
     "BIGGS DARKLIGHTER: young Rebel pilot in an orange flight suit and white vest, with a datapad (replaces Roxanne).",
     "Group 3, B style (stand-only, figure redrawn over Roxanne's frame): short dark-brown hair with a side part and a thin moustache, orange flight suit under a white pilot vest with a chest box, red collar, a datapad with a lit screen in his hand.",
     materials={"H": "c", "F": "a", "V": "w/c", "C": "b", "Y": "c", "K": "c"}, legend={"k": 15, "D": 15, "E": 8, "Z": 12, "X": 15, "r": 9, "e": 15, "1": 1, "2": 2, "3": 3, "4": 4},
     accept={},
     base="gym_leaders/roxanne.png",
     patches={"down": [BD_D, BD_PAD], "up": [BD_U], "left": [BD_L, BD_PAD_L]},
     kit="person16x32_still")

# ====================================================================== HOT_SPRINGS_OLD_WOMAN: Sullustan
# Only the head shows above the water: a light grey towel (T) with a pink stripe (S), round Sullustan ears (E), big glossy black eyes, a wide jowled face and a small mouth.
SU_D = block(0, 8, """
................
......TTTT......
....TTTTTTTT....
...TTTTTTTTTT...
..TTTTTTTTTTTT..
..SSSSSSSSSSSS..
.ETTTTTTTTTTTTE.
EEEssssssssssEEE
EEssssssssssssEE
.sOWOssssssOWOs.
.sOOOssssssOOOs.
.sOOOssssssOOOs.
ssssssssssssssss
ssssssmmmmssssss
.ssssssssssssss.
..ssssssssssss..""")
SU_U = block(0, 8, """
................
......TTTT......
....TTTTTTTT....
...TTTTTTTTTT...
..TTTTTTTTTTTT..
..SSSSSSSSSSSS..
.ETTTTTTTTTTTTE.
EEETTTTTTTTTTEEE
EETTTTTTTTTTTTEE
.TTTTTTTTTTTTTT.
.sTTTTTTTTTTTTs.
.ssTTTTTTTTTTss.
ssssssssssssssss
ssssssssssssssss
.ssssssssssssss.
..ssssssssssss..""")
SU_L = block(0, 8, """
................
.......TTTT.....
.....TTTTTTTT...
....TTTTTTTTTT..
...TTTTTTTTTTT..
...SSSSSSSSSSS..
...TTTTTTTTTTT..
..sssssssTTTTT..
.ssssssEEETTTT..
.ssssssEEEETTs..
OWOssssssEEEss..
OOOsssssssssss..
OOOsssssssssss..
ssssssssssssss..
mmsssssssssss...
..ssssssssss....""")
spec("hot_springs_old_woman", "HotSpringsOldWoman", "npc_4", "hot_springs_old_woman.png",
     "Old Sullustan woman soaking in a hot spring with a towel on her head (replaces the Hot Springs Old Woman).",
     "Group 3, B style: the vanilla bather's head-above-water layout, redrawn as a Sullustan: light grey towel with a pink stripe, round ears, big glossy black eyes, a wide jowled face.",
     materials={"T": "c", "S": "b", "E": "s@", "s": "s@"}, legend={"O": 15, "W": 14, "m": 4},
     accept={"height": "only the head shows above the hot-spring water, as in vanilla"},
     base="hot_springs_old_woman.png", remap={"c": "T"},
     patches={"down": [SU_D], "up": [SU_U], "left": [SU_L]})
# ====================================================================== CAMERAMAN: HoloNet camera operator
# Dark hair under a black headset band with an ear cup and a mic boom, a grey holocam (Q) on his
# shoulder with a black lens ring, blue glass (L), a glint and a red REC light; grey jacket
# bits, magenta HoloNet crew vest (V), navy trousers.
CM_D = block(0, 11, """
.....HHHHHH.....
...HHHHHHHHHH...
..eeeeeeeeeeee..
..HHHHHHHHHHHH..
..HHHHH_________
.eHHHH__________
_ee_____________
________________
________________
___e____________
____e___________""")
CM_CAM_D = block(7, 15, """
QQQQQQQ.
QQQQQQQQ
QQQQQQrQ
QQQQQQQQ
QQQQQQQ_
QeeeeeQ_
_eLLWeQ_
_eLLLeQ_
__eee___""")
CM_U = block(0, 11, """
.....HHHHHH.....
...HHHHHHHHHH...
..eeeeeeeeeeee..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.eHHHHHHHHHHHHe.
___HHHHHHHHHH___""")
CM_L = block(0, 11, """
.....HHHHHH.....
...HHHHHeHHHH...
..HHHHHHeHHHHH..
..HHHHHHeHHHHH..
..HHHHHeeeHHHH..
___HHHHeeeHHH___""")
CM_CAM_L = block(0, 16, """
..HHQQQQQQQQH___
eeeQQQQQQQrQ____
eLWQQQQQQQQQ____
eLLQQQQQQQQQ____
eeeQssQQQQQ_____""")
spec("cameraman", "Cameraman", "npc_4", "cameraman.png",
     "HOLONET camera operator with a holocam on his shoulder and a headset (replaces the Cameraman).",
     "Group 3, B style: the Cameraman's own body as regions (jacket and camera panels -> grey Q, shirt -> magenta crew vest V, trousers T), new dark hair under a black headset with an ear cup and mic, the shoulder camera redrawn as a grey holocam with a blue lens, glint and red REC light.",
     materials={"H": "a", "Q": "c", "V": "b", "T": "a"}, legend={"k": 15, "e": 15, "L": 5, "W": 14, "r": 9},
     accept={},
     base="cameraman.png", remap={"c": "Q", "b": "V", "a": "T"},
     patches={"down": [CM_D, CM_CAM_D], "up": [CM_U], "left": [CM_L, CM_CAM_L]})

# ====================================================================== POKEFAN_M: beast fan
# Pokefan M's balding head and side hair, a red headband with two curled bantha horns (N, bone
# white edged in brown), a sand-yellow vest with dark creature spots (p) over the red shirt.
PF_D = block(0, 12, """
_NN__________NN_
NNNBBBBBBBBBBNNN
N_N__________N_N
NNN__________NNN
_N____________N_""")
PF_U = block(0, 12, """
_NN__________NN_
NNNBBBBBBBBBBNNN
N_N__________N_N
NNN__________NNN
_N____________N_""")
PF_L = block(0, 12, """
________________
____BBBBBBBBB___
_______NNNN_____
______NN__NN____
__________NN____
_________NN_____""")
PF_VEST_D = block(1, 21, """
_VV________VV_
__VVV____VVV__
___VpVV__VpV__
___VVVp_VVVV__
__VpVVV_VVpVV_""")
PF_VEST_U = block(1, 21, """
_VVVVVVVVVVVV_
__VVVVVVVVVV__
__VpVVVVVpVV__
__VVVpVVVVVV__
__VpVVVVVVpV__""")
PF_VEST_L = block(4, 22, """
VVVVVV
VpVVVV
VVVpVV
VVVVpV""")
spec("pokefan_m", "PokefanM", "npc_2", "pokefan_m.png",
     "Beast fan (m) in a bantha-horn headband and a creature-print vest (replaces Pokefan M).",
     "Group 3, B style: Pokefan M's own body as regions (shirt S, belt Y), a red headband with two curled bantha horns, a sand vest with dark creature spots open over the shirt.",
     materials={"H": "c", "S": "b", "Y": "a", "B": "b", "N": "w/c", "V": "a"}, legend={"k": 15, "p": 13},
     accept={},
     base="pokefan_m.png", remap={"c": "H", "b": "S", "a": "Y"},
     patches={"down": [PF_VEST_D, PF_D], "up": [PF_VEST_U, PF_U], "left": [PF_VEST_L, PF_L]})

# ====================================================================== ROOFTOP_SALE_WOMAN: Cloud City clerk
# Bespin clerk: a blue pillbox cap (C) with a gold band (y) and a white badge on her olive bob, blue
# uniform (U) with gold trim (Y), white tabard (W).
RS_D = block(0, 9, """
................
.....CCCCCC.....
....CCCCCCCC....
....CCCWWCCC....
...yyyyyyyyyy...""")
RS_U = block(0, 9, """
................
.....CCCCCC.....
....CCCCCCCC....
....CCCCCCCC....
...yyyyyyyyyy...""")
RS_L = block(0, 9, """
................
......CCCCCC....
.....CCCCCCCC...
....WCCCCCCCC...
..yyyyyyyyyyy...""")
spec("rooftop_sale_woman", "RooftopSaleWoman", "npc_1", "rooftop_sale_woman.png",
     "Cloud City sales clerk in a Bespin pillbox cap and blue uniform (replaces the Rooftop Sale Woman).",
     "Group 3, B style: her own body as regions (uniform -> Bespin blue U, trim -> gold Y, apron -> white tabard W), olive bob kept, new blue pillbox cap with a gold band and a white badge.",
     materials={"H": "c", "U": "b", "Y": "c", "W": "w/b", "C": "b@", "y": "c"}, legend={"k": 15, "W": 14},
     accept={},
     base="rooftop_sale_woman.png", remap={"c": "H", "b": "U", "a": "Y", "w": "W"},
     patches={"down": [RS_D], "up": [RS_U], "left": [RS_L]})

# ====================================================================== SCIENTIST_2: senior researcher
# Big brass lab goggles (G) with blue lenses (E), a glint and eyes behind them, worn over the
# eyes on a strap; white lab coat (L) over a blue shirt (S) and pink tie; grey-streaked hair.
SC_D = block(0, 11, """
......HHHH......
....HWWHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHssssHHHH..
..HHHssssssHHH..
.sGGGGGssGGGGGs.
.sGEEWGGGGEEWGs.
.sGEkEGssGEkEGs.
..sGGGssssGGGs..""")
SC_U = block(0, 11, """
......HHHH......
....HWWHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.GGGGGGGGGGGGGG.
.sHHHHHHHHHHHHs.
..sHHHHHHHHHHs..
...SSSSSSSSSS...""")
SC_L = block(0, 11, """
......HHHH......
....HWWHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..sssHHHHHHHHH..
..sssssHHHHHHH..
.GGGGGGGGGGGGG..
.GEEWG__HHHHHH__
.GEkEG___HHHHH__
..GGG_____HHH___""")
spec("scientist_2", "Scientist2", "npc_1", "scientist_2.png",
     "Senior researcher in big brass lab goggles and a white lab coat (replaces Scientist 2).",
     "Group 3, B style: Scientist 2's own body as regions (coat -> white lab coat L, shirt -> blue S, tie kept pink), dark hair with a grey streak, big brass goggles with blue lenses worn over the eyes on a strap.",
     materials={"H": "c", "L": "w/b", "S": "b", "G": "c", "s": "s"}, legend={"k": 15, "E": 8, "W": 14},
     accept={},
     base="scientist_2.png", remap={"c": "H", "b": "L", "w": "S"},
     patches={"down": [SC_D], "up": [SC_U], "left": [SC_L]})

# ====================================================================== AQUA_MEMBER_F: Weequay enforcer
# Weequay: bald leathery tan scalp with forehead, brow and mouth wrinkles (4), dark red-brown
# braids and a topknot (H), drab green tunic (L), scrap-metal shoulder and chest plates (M),
# brown boots (D).
WQ_D = block(0, 10, """
......HHH.......
.....HHHHH......
....ssHHHss.....
...ssssssssss...
..ssssssssssss..
..s4s4ss4s4sss..
.HssssssssssssH.
.Hsss44ss44sssH.
.HssssksskssssH.
.HssssksskssssH.
HHs4ssssssss4sHH
HH.4ss4444ss4.HH
HH____4ssss4__HH
HH____________HH""")
WQ_U = block(0, 10, """
......HHH.......
.....HHHHH......
....ssHHHss.....
...sssHHHssss...
..sssssHHsssss..
..sssssHHsssss..
.HsssssHHssssH..
.HsssssHHssssHs.
.HsssssHHsssssH.
.HsssssHHsssssH.
HHssssHHssssssHH
HH.ssssHHssss.HH
HH_____HH_____HH
HH_____HH_____HH""")
WQ_L = block(0, 10, """
.......HHH......
......HHHHH.....
.....sHHHHs.....
...sssssssHss...
..sssssssssHss..
..4s4ssssssHss..
..sssssssssHHs..
..44sssssssssHH.
..ssksssssssssH.
..ssksssssssssH.
..4sssssssssssHH
...44ssssssssHHH
....4sssss__HHH.
.....____HHHH...""")
WQ_ARMOR_D = block(0, 22, """
________________
_MMM________MMM_
MMMM_MMMMMM_MMMM""")
WQ_ARMOR_U = block(0, 22, """
________________
_MMM________MMM_
MMMM________MMMM""")
spec("aqua_member_f", "AquaMemberF", "npc_3", "team_aqua/aqua_member_f.png",
     "Cartel thug (f): Weequay enforcer with a topknot and braids, a wrinkled leathery face and scrap armour (replaces the Aqua Grunt F).",
     "Group 3, B style: the grunt's own body as regions (top and skirt -> drab green tunic L, boots -> brown D), new Weequay head: bald leathery tan scalp with forehead, brow and mouth wrinkles, dark red-brown braids and a topknot; scrap-metal shoulder plates and a chest plate.",
     materials={"H": "c", "L": "b", "D": "c", "M": "a"}, legend={"k": 15, "4": 4},
     accept={"hair_rows": "Weequay: a bald wrinkled scalp with a topknot and braids"},
     base="team_aqua/aqua_member_f.png", remap={"a": "L", "b": "D", "c": "L", "w": "L"},
     patches={"down": [WQ_D, WQ_ARMOR_D], "up": [WQ_U, WQ_ARMOR_U], "left": [WQ_L, block(5, 23, "MMMM")]})

# ====================================================================== UNION_ROOM_ATTENDANT: HoloNet Club
# Stand-only. Auburn hair (H) under a black headset band with an ear cup and a mic boom (green
# tip), lavender-grey uniform (U) with green HoloNet trim (T) and a glowing holo badge.
UA_D = block(0, 10, """
................
......HHHH......
....HHHHHHHH....
...eeeeeeeeee...""")
UA_U = block(0, 10, """
................
......HHHH......
....HHHHHHHH....
...eeeeeeeeee...""")
UA_L = block(0, 9, """
................
................
.....HHHHH......
...HHHHHHHHH....
...HHHHHeHHHH...""")
UA_MIC_D = block(0, 17, """
ee___
eee__
eeq__
__q__
___q_
____g""")
UA_MIC_L = block(4, 17, """
____ee
____ee
____ee
___q__
_qq___
g_____""")
UA_BADGE_D = block(4, 24, """
gG
GW""")
spec("union_room_attendant", "UnionRoomAttendant", "npc_3", "union_room_attendant.png",
     "HOLONET CLUB attendant with a headset and a glowing holo badge (replaces the Union Room attendant).",
     "Group 3, B style (stand-only): the attendant's own body as regions (uniform -> lavender-grey U, white trim -> green HoloNet trim T), nurse cap replaced by auburn hair under a black headset with an ear cup and a green-tipped mic, a glowing green holo badge on the chest.",
     materials={"H": "c", "U": "a", "T": "b", "O": "a"}, legend={"k": 15, "e": 15, "q": 15, "g": 8, "G": 9, "W": 14},
     accept={},
     base="union_room_attendant.png", remap={"b": "H", "a": "U", "w": "T", "k": "O"},
     patches={"down": [block(1, 18, "H____e__e____H\nH__H_e__e_H__H\nH__H________H_\nH____________H\n_H__________H_"), UA_D, UA_MIC_D, UA_BADGE_D],
              "up": [block(1, 18, "H____________H\nH____________H\nH____________H\n_H__________H_\n_H__________H_"), UA_U],
              "left": [block(5, 18, "e________H\ne________H\n___H_____H\n___H_____H\n___H____H_"), UA_L, UA_MIC_L]},
     kit="person16x32_still")
print("ok")

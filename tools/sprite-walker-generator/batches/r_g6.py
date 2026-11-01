"""Group 6 (worker 6): B-style Star Wars walkers. Each vanilla body is used as regions; only heads,
costume cues and small props are drawn. Writes art/<name>.yaml. Run from the tool folder:
python batches/r_g6.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402

ONLY = set(sys.argv[1:])


def want(n):
    return not ONLY or n in ONLY


# ====================================================================== MAN_1: desert townsman
# Hood up (H, brown ramp c) framing the face, a grey neck scarf (S), man_1's body as regions
# turned into a robe (R) with a green sash (G), grey leg wraps (L) and dark boots (D).
if want("man_1"):
    MW_D = block(0, 10, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHssssssHHH..
.HHHssssssssHHH.
.HHssssssssssHH.
.HHssksssskssHH.
.HHssksssskssHH.
.HHHssssssssHHH.
..HHSSSSSSSSHH..
___SSSSSSSSSS___""")
    MW_U = block(0, 10, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
___HHHHHHHHHH___""")
    MW_L = block(0, 10, """
......HHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HsssssHHHHHH..
..ssssssHHHHHH..
..sksssHHHHHHH..
..sksssHHHHHHH..
..sssssHHHHHHH..
...sssHHHHHHH...
...SSSSSSSSS....
_____SSSS_______""")
    SASH_D = block(0, 26, "___GGGGGGGGGG___")
    SASH_L = block(0, 26, "____GGGGGGG_____")
    spec("man_1", "Man1", "npc_3", "man_1.png",
         "Desert townsman in a hooded robe (replaces Man 1).",
         "Group 6, B style: man_1's body as regions (shirt -> robe R, trousers -> grey leg wraps L, shoes -> boots D), new brown hood framing the face, grey neck scarf, green sash.",
         materials={"H": "c@", "S": "a", "R": "c", "L": "c", "D": "c", "G": "b"}, legend={"k": 15},
         accept={"hair_rows": "hood up, no hair"},
         base="man_1.png", remap={"w": "R", "a": "R", "b": "L", "c": "D"},
         patches={"down": [MW_D, SASH_D], "up": [MW_U, SASH_D], "left": [MW_L, SASH_L]})
# ====================================================================== COOK: Twi'lek cantina cook
# Blue Twi'lek (face T and two head-tails L on ramp b) with tan leather wraps (B) round the tails,
# a white cook's skullcap (W), the cook's own apron (A) and olive trousers (P). Moves to NPC_1.
if want("cook"):
    CK_D = block(0, 10, """
.....WWWWWW.....
...WWWWWWWWWW...
..WWWWWWWWWWWW..
..WWWWWWWWWWWW..
..LTTTTTTTTTTL..
.LLTTTTTTTTTTLL.
.LLTTTTTTTTTTLL.
.LLTTkTTTTkTTLL.
.LLTTkTTTTkTTLL.
.LLLTTTTTTTTLLL.
.BBB_TTTTTT_BBB.
_LLL________LLL_
_LL__________LL_
_LL__________LL_""")
    CK_U = block(0, 10, """
.....WWWWWW.....
...WWWWWWWWWW...
..WWWWWWWWWWWW..
..WWWWWWWWWWWW..
..TTTTTTTTTTTT..
.TTTTTTTTTTTTTT.
.TTTTTTTTTTTTTT.
.TTTTTTTTTTTTTT.
.TTTTTTTTTTTTTT.
..TTTTLTTLTTTT..
____LLL__LLL____
____LLL__LLL____
____LLL__LLL____
_____LL__LL_____
_____LL__LL_____""")
    CK_L = block(0, 10, """
......WWWWW.....
....WWWWWWWW....
...WWWWWWWWWW...
..WWWWWWWWWWW...
..TTTTTTTTTTL...
..TTTTTTTTTLLL..
..TTTTTTTTTLLL..
..TkTTTTTTTLLL..
..TkTTTTTTLLLL..
..TTTTTTTTLLLL..
...TTTTTTTBBB...
....TTTT__LLL...
__________LLL___
__________LLL___
___________LL___""")
    spec("cook", "Cook", "npc_1", "cook.png",
         "Blue Twi'lek cantina cook in an apron (replaces Cook).",
         "Group 6, B style: the cook's own body as regions (pink apron A, blue arms H, olive trousers P), new blue Twi'lek head: two head-tails over the shoulders with tan leather wraps, under a white cook's skullcap.",
         materials={"T": "skin-b@", "L": "b", "H": "b", "W": "w/c", "A": "a", "B": "s", "P": "c"}, legend={"k": 15},
         accept={"skin_tones": "Twi'lek skin is the blue ramp; the skin ramp is the leather wraps", "hair_rows": "a skullcap over a bald Twi'lek head"},
         base="cook.png", remap={"s": "H", "a": "A", "w": "A", "c": "P", "b": "P"},
         patches={"down": [CK_D], "up": [CK_U], "left": [CK_L]}, kit="person16x32_still")
# ====================================================================== EXPERT_M: veteran spacer
# A new bald old head (S) with a full white beard (B) and brown-strapped flight goggles (C, black
# lenses with white glints) pushed up on the forehead; expert_m's coat becomes an orange flight
# suit (F) with a red belt (R) and brown boots (D). Moves to NPC_2 (orange suit).
if want("expert_m"):
    EX_D = block(0, 12, """
......SSSS......
....SSSSSSSS....
...SggSSSSggS...
..CgWCCCCCCgWC..
..SSSSSSSSSSSS..
.SSSSSSSSSSSSSS.
.SSSSkSSSSkSSSS.
.SSSSkSSSSkSSSS.
..SSBBSSSSBBSS..
..SBBBBBBBBBBS..
___BBBBBBBBBB___
____BBBBBBBB____
_____BBBBBB_____
______BBBB______""")
    EX_U = block(0, 12, """
......SSSS......
....SSSSSSSS....
...SSSSSSSSSS...
..CCCCCCCCCCCC..
..SSSSSSSSSSSS..
.SSSSSSSSSSSSSS.
.SSSSSSSSSSSSSS.
.SSSSSSSSSSSSSS.
..SSSSSSSSSSSS..
...SSSSSSSSSS...""")
    EX_L = block(0, 12, """
.....SSSSS......
...SSSSSSSS.....
..ggSSSSSSSS....
.gWCCCCCCCCCC...
.SSSSSSSSSSSS...
.SSSSSSSSSSSS...
.SkSSSSSSSSSS...
.SkSSSSSSSSSS...
.BBBSSSSSSSSS...
.BBBBSSSSSSS....
.BBBB___________
..BBB___________
..BB____________""")
    spec("expert_m", "ExpertM", "npc_2", "expert_m.png",
         "Veteran spacer in an old orange flight suit with goggles (replaces Expert M).",
         "Group 6, B style: expert_m's own body as regions (coat -> orange flight suit F, belt -> red R, shoes -> brown boots D), new bald old head with a full white beard and flight goggles pushed up on the forehead.",
         materials={"S": "s@", "F": "a", "R": "b!", "C": "c", "B": "w/c", "D": "c"}, legend={"k": 15, "W": 14, "g": 10},
         accept={"hair_rows": "bald veteran; goggles on the bare crown"},
         base="expert_m.png", remap={"a": "F", "b": "R", "c": "D", "w": "B"},
         patches={"down": [EX_D], "up": [EX_U], "left": [EX_L]})
# ====================================================================== TUCKER: DENGAR
# Head wrapped in white bandages (W, edged lavender) leaving a strip of face with the eyes, and
# Tucker's body as regions turned into heavy armour: shoulder pads and plates P (grey ramp a),
# a brown flight suit U and sleeves A (ramp c), green belt G. Moves to NPC_3.
if want("tucker"):
    DG_D = block(0, 10, """
......WWWW......
....WWxxWWWW....
...WWWWWxxWWW...
..xxWWWWWWxxWW..
.WWWxxWWWWWWxxW.
.WWWWWxxxxWWWWW.
.WWWssssssssWWW.
.WWWskssssksWWW.
..WWskssssksWW..
..WWWssssssWWW..
...xWWssssWWx...
....WWxxxxWW....""")
    DG_U = block(0, 10, """
......WWWW......
....WWxxWWWW....
...WWWWWxxWWW...
..xxWWWWWWxxWW..
.WWWxxWWWWWWxxW.
.WWWWWxxxxWWWWW.
.WWxxWWWWWWxxWW.
.WWWWxxWWxxWWWW.
..WWWWWxxWWWWW..
..WWWWWWWWWWWW..
...WWxxWWxxWW...
....WWWWWWWW....""")
    DG_L = block(0, 10, """
.......WWWW.....
.....WWxxWWWW...
....WWWWWxxWWW..
...xxWWWWWWxxW..
..WWWxxWWWWWWWW.
..WWWWWxxxWWWWW.
..sssssWWWxxWWW.
..skssssWWWWxxW.
..skssssWWWWWW..
..ssssssWxxWWW..
...sssWWWWWxx...
....WWxxxWWW....""")
    DG_BODY_D = block(0, 22, """
___PPPPPPPPPP___
___PPPPPPPPPP___
___UPPPPPPPPU___
___GGGGcGGGGG___
___UUUUUUUUUU___""")
    DG_BODY_U = block(0, 22, """
___PPPPPPPPPP___
___PPPPPPPPPP___
___UPPPPPPPPU___
___GGGGGGGGGG___
___UUUUUUUUUU___""")
    DG_BODY_L = block(0, 22, """
_____PPPPPP_____
____PPPPPPP_____
____UPPPPPU_____
____GGGGGGG_____
____UUUUUUU_____""")
    spec("tucker", "Tucker", "npc_3", "frontier_brains/tucker.png",
         "DENGAR: bounty hunter with a bandaged head and heavy armour (replaces Tucker).",
         "Group 6, B style: Tucker's own body as regions (shoulder pieces and plates -> grey armour P, dress -> brown suit U, bare arms -> brown sleeves A, trims -> green belt G), new head wrapped in white bandages leaving a strip of face with the eyes.",
         materials={"W": "w/a", "P": "a", "U": "c", "A": "c", "G": "b", "B": "s"}, legend={"k": 15, "x": 6, "c": 14},
         accept={"hair_rows": "head wrapped in bandages, no hair"},
         base="frontier_brains/tucker.png", remap={"w": "P", "a": "U", "s": "A", "b": "G", "c": "B"},
         patches={"down": [DG_D, DG_BODY_D], "up": [DG_U, DG_BODY_U], "left": [DG_L, DG_BODY_L]})
# ====================================================================== FLANNERY: SABINE WREN
# Short dyed bob (H, blue ramp b) with a pink streak (D) in the fringe; Mandalorian armour: white
# pauldrons and gauntlets (P, G edged olive), a pink painted chest plate (A), olive bodysuit (C),
# blue belt (K) with black holsters at the hips, olive boots (B). Stand-only: the figure is redrawn
# over Flannery's frame (her legs and stance kept as the base). Stays on NPC_1.
if want("flannery"):
    SW_D = block(0, 10, """
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHhHHHH..
.HHhHHHhHHHHhHH.
.DHHHHHHHHHHHHH.
.DDHHHHHHHsssHH.
.DDHHHssssssHHH.
.DDHskssssksHHH.
.DDHskssssksHHH.
.DDHssssssssHHH.
..DD.ssssss.HH..
..PyPCssssCPyP..
.PPPPAAAAAAPPPP.
.CCCAAWkWAAACCC.
.GGCAAAAAAAACGG.
.GyCKWKKKKWKCyG.
..kCCCCCCCCCCk..
...CCCC..CCCC...
...CWCC..CCWC...
...BBBB..BBBB...""")
    SW_U = block(0, 10, """
................
.....JJJJJJ.....
...JJJJJJJJJJ...
..JJJJJJJJJJJJ..
.JJJJJJJJJJJJJJ.
.JJJJJJJJJJJJJD.
.JJJJJJJJJJJJDD.
.JJJJJJJJJJJJDD.
.JJJJJJJJJJJJDD.
.JJJJJJJJJJJJDD.
.JJJJJJJJJJJJDD.
..JJ.JJJJ.JJDD..
..PPPCCCCCCPPP..
.PPPPAAAAAAPPPP.
.CCCAAAAAAAACCC.
.GGCAAAAAAAACGG.
.GyCKWKKKKWKCyG.
..kCCCCCCCCCCk..
...CCCC..CCCC...
...CWCC..CCWC...
...BBBB..BBBB...""")
    SW_L = block(0, 10, """
................
......HHHHHH....
....HHHHHHHHHH..
...HHHHHhHHHHHH.
..HHHHHhHHHHhHH.
.HHHHHHHHHHHHHH.
.HHHHsHHHHHHHHH.
.HsssssHHHHHHDD.
.HkssssHHHHHHDD.
.HkssssHHHHHDDD.
.HssssssHHHHDD..
..sssssHH.HDD...
....CssssPPP....
....AAAAPPPPP...
....AAWACPPPP...
....AAAACGGGG...
....KWKKKGyGk...
.....CCCCCCCk...
.....CCCCCCC....
......CCWCC.....
......BBBBB.....""")
    spec("flannery", "Flannery", "npc_1", "gym_leaders/flannery.png",
         "SABINE WREN: Mandalorian girl in painted armour with dyed hair (replaces Flannery).",
         "Group 6, B style (stand-only, so the figure is redrawn over Flannery's frame): short blue bob with a pink-dyed fringe, white Mandalorian pauldrons and gauntlets, pink painted chest plate, olive bodysuit, blue belt with black holsters.",
         materials={"H": "b", "J": "b", "D": "a", "P": "w/c", "G": "w/c", "A": "a", "C": "c", "K": "b", "B": "c"}, legend={"k": 15, "W": 14, "h": 8, "y": 6},
         accept={},
         base="gym_leaders/flannery.png",
         patches={"down": [SW_D], "up": [SW_U], "left": [SW_L]}, kit="person16x32_still")
# ====================================================================== WINONA: CHIRPA
# Elder Ewok chief, stand-only and redrawn over Winona's frame: brown leather hood (C) with two
# white bone horns (w), grey fur face (F) and body (U, arms A), big black eyes with glints, a tan
# muzzle (M, skin ramp) with a black nose, a green leaf necklace (L), and a short brown staff (S)
# topped with a bone knob (K), never higher than the head. Moves to NPC_3 (grey fur, green, brown).
if want("winona"):
    def chirpa(body, staff):
        assert len(body) == len(staff) == 19
        rows = ["................"] + [b + t for b, t in zip(body, staff)]
        for r in rows:
            assert len(r) == 16, r
        return block(0, 11, "\n".join(rows))
    STAFF_R = [".K", "SK"] + ["S."] * 17
    STAFF_L_ = None
    CH_D = chirpa([
        ".h...CCCC...h.",
        "..hCCCCCCCCh..",
        ".CCCCCCCCCCCC.",
        "CCCCCCCCCCCCCC",
        "CCFFFFFFFFFFCC",
        "CFFWkFFFFWkFFC",
        "CFFkkFFFFkkFFC",
        "CFFFFMMMMFFFFC",
        ".CFFMMkkMMFFC.",
        "..FFFMMMMFFF..",
        "...LLLLLLLL...",
        ".UUUUULLUUUUU.",
        "AUUUUUUUUUUUUA",
        "AUUUUUUUUUUUAA",
        "AAUUUUUUUUUUAA",
        ".AUUUUUUUUUUA.",
        "..UUUUUUUUUU..",
        "..UUUU..UUUU..",
        "..DDDD..DDDD.."], STAFF_R)
    CH_U = chirpa([
        ".h...CCCC...h.",
        "..hCCCCCCCCh..",
        ".CCCCCCCCCCCC.",
        "CCCCCCCCCCCCCC",
        "CCCCCCCCCCCCCC",
        "CCCCCCCCCCCCCC",
        "CCCCCCCCCCCCCC",
        "CCCCCCCCCCCCCC",
        ".CCCCCCCCCCCC.",
        "..CCCCCCCCCC..",
        "...LLLLLLLL...",
        ".UUUUUUUUUUUU.",
        "AUUUUUUUUUUUUA",
        "AAUUUUUUUUUUAA",
        "AAUUUUUUUUUUAA",
        ".AUUUUUUUUUUA.",
        "..UUUUUUUUUU..",
        "..UUUU..UUUU..",
        "..DDDD..DDDD.."], STAFF_R)
    CH_L = block(0, 11, """
................
.K......CCCC..h.
.KS...CCCCCCCh..
..S..CCCCCCCCC..
..S.CCCCCCCCCCC.
..SCFFFFCCCCCCC.
..SWkFFFFCCCCCC.
..SkkFFFFCCCCCC.
.MMMFFFFFCCCCCC.
MkMMFFFFFCCCCC..
.MMMFFFFFCCCC...
..SLLLLLLLLL....
..AAUUUUUUUUU...
..SAAUUUUUUUUU..
..SAAUUUUUUUUU..
..S.UUUUUUUUU...
..S.UUUUUUUU....
..S..UUUUUUU....
..S..DDD.DDD....""")
    spec("winona", "Winona", "npc_3", "gym_leaders/winona.png",
         "CHIRPA: elder Ewok chief in a horned leather hood with a staff (replaces Winona).",
         "Group 6, B style (stand-only, so the figure is redrawn over Winona's frame): grey-furred Ewok with big black eyes and a tan muzzle, brown leather hood with two bone horns, green leaf necklace, short brown staff with a bone knob held at his side.",
         materials={"C": "c@", "F": "skin-a", "U": "a", "A": "a", "M": "s", "L": "b", "S": "c", "D": "c"},
         legend={"k": 15, "W": 14, "h": 14, "K": 14},
         accept={"skin_tones": "Ewok fur is the grey ramp; only the muzzle uses the skin ramp", "hair_rows": "a leather hood over fur",
                 "eye_row": "big Ewok eyes inside grey fur"},
         base="gym_leaders/winona.png",
         patches={"down": [CH_D], "up": [CH_U], "left": [CH_L]}, kit="person16x32_still")
# ====================================================================== MART_EMPLOYEE: depot clerk
# The clerk's own head and hair kept, with a black comlink headset (band over the crown, earpiece,
# boom mic); his shirt and trousers become a blue jumpsuit (J, T), the apron a pink utility vest
# (V) with white pocket studs, olive collar and shoes (S); a small datapad with a lit screen held at
# the hip. Stays on NPC_1.
if want("mart_employee"):
    ME_HS_D = block(0, 12, """
....kkkkkkkk....
________________
________________
________________
________________
_k____________k_
_k____________k_""")
    ME_HS_U = block(0, 12, """
....kkkkkkkk....
________________
________________
________________
________________
_k____________k_
_k____________k_""")
    ME_HS_L = block(0, 12, """
.....kkkkkk.....
________________
________________
________________
_________k______
________kk______
________kk______""")
    ME_PAD_D = block(0, 25, """
__________kkkk__
__________kWPk__""")
    ME_PAD_L = block(0, 25, """
___kkkk_________
___kWPk_________""")
    ME_POCK_D = block(0, 25, "_____W__W_______")
    spec("mart_employee", "MartEmployee", "npc_1", "mart_employee.png",
         "Supply-depot clerk in a utility vest with a comlink headset and datapad (replaces Mart Employee).",
         "Group 6, B style: the clerk's own head and body as regions (shirt and trousers -> blue jumpsuit J/T, apron -> pink utility vest V with pocket studs), black comlink headset, datapad with a lit screen at the hip.",
         materials={"H": "c", "J": "b", "T": "b", "V": "a", "S": "c"}, legend={"k": 15, "W": 14, "P": 8},
         accept={},
         base="mart_employee.png", remap={"c": "H", "b": "J", "w": "V", "a": "S"},
         patches={"down": [ME_HS_D, ME_PAD_D, ME_POCK_D], "up": [ME_HS_U], "left": [ME_HS_L, ME_PAD_L]})
# ====================================================================== OLD_WOMAN: elder in a shawl
# A brown desert shawl (H, ramp c) drawn up over her grey hair (a, only the fringe shows) and
# falling over the shoulders, with a green woven stripe (S) and white tassels; a new face framed by it; her own green cardigan
# (G) and long skirt (K) kept as regions. Stays on NPC_3.
if want("old_woman"):
    OW_D = block(0, 12, """
......HHHH......
....HHHHHHHH....
...SSSSSSSSSS...
..HHHHHHHHHHHH..
.HHHaaaaaaaaHHH.
.HHaassssssaaHH.
.HHassssssssaHH.
.HHssksssskssHH.
.HHssksssskssHH.
.HHHssssssssHHH.
HHHHHssssssHHHHH
.tHtH______HtHt.""")
    OW_U = block(0, 12, """
......HHHH......
....HHHHHHHH....
...SSSSSSSSSS...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
HHHHHHHHHHHHHHHH
HHHHHHHHHHHHHHHH
HHHHHHHHHHHHHHHH
.HHHHHHHHHHHHHH.
.tHtHtHtHtHtHtH.""")
    OW_L = block(0, 12, """
......HHHH......
....HHHHHHHH....
...SSSSSSSSSS...
..HHHHHHHHHHHH..
..aaaaHHHHHHHH..
.aasssaHHHHHHH..
.sssssaHHHHHHH..
.skssssHHHHHHH..
.skssssHHHHHHH..
.ssssssHHHHHH...
..sssssHHHHHH...
...____HtHtH....""")
    spec("old_woman", "OldWoman", "npc_3", "old_woman.png",
         "Elderly woman in a desert shawl drawn over her hair (replaces Old Woman).",
         "Group 6, B style: the old woman's own body as regions (cardigan G, skirt K), new head: a brown desert shawl drawn up over the hair and falling over the shoulders, with a green woven stripe and white tassels.",
         materials={"H": "c@", "S": "b", "a": "a", "G": "b", "K": "c"}, legend={"k": 15, "t": 14, "W": 14},
         accept={},
         base="old_woman.png", remap={"b": "G", "c": "K"},
         patches={"down": [OW_D], "up": [OW_U], "left": [OW_L]})
# ====================================================================== REPORTER_F: HoloNet reporter
# The reporter's own body, hair and microphone kept as regions; a small grey holocam droid (D,
# round on ramp c) floats at her shoulder with a magenta lens and a white glint, no higher than her
# head, and she gets a black comlink earpiece. Stays on NPC_4.
if want("reporter_f"):
    CAM = block(12, 10, """
_DD_
DWLD
_DD_""")
    CAM_L = block(12, 10, """
_DD_
DDDD
_DD_""")
    EAR_D = block(0, 17, "_k______________")
    EAR_L = block(0, 17, "_______k________")
    spec("reporter_f", "ReporterF", "npc_4", "reporter_f.png",
         "HoloNet reporter (f) with a microphone and a floating holocam droid (replaces Reporter F).",
         "Group 6, B style: the reporter's own body, hair and microphone as regions, a small grey holocam droid with a magenta lens floating at her shoulder, a black comlink earpiece.",
         materials={"D": "c@", "T": "b!"}, legend={"k": 15, "W": 14, "L": 9},
         accept={},
         base="reporter_f.png", remap={"b": "T"},
         patches={"down": [CAM, EAR_D], "up": [CAM_L], "left": [CAM_L, EAR_L]})
# ====================================================================== SAILOR: deck spacer
# The sailor's own body as regions turned into a deck jumpsuit: blue top (J, ramp b) with olive
# collar and harness straps (P), olive-brown hair and trousers (N); a new olive deck cap (K) with a
# blue visor (V) and a white crest, a pink rank plaque on the chest (hard pixels). Stays on NPC_1.
if want("sailor"):
    SP_CAP_D = block(0, 11, """
................
....KKKKKKKK....
...KKKKWKKKKK...
___KKKKKKKKKK___
__KKKKKKKKKKKK__
__VVVVVVVVVVVV__""")
    SP_CAP_U = block(0, 11, """
................
....KKKKKKKK....
...KKKKKKKKKK...
___KKKKKKKKKK___
__KKKKKKKKKKKK__
__KKKKKKKKKKKK__""")
    SP_CAP_L = block(0, 11, """
................
....KKKKKKKK....
...KKKKKKKKKK...
___KKKKKKKKKK___
.VVVKKKKKKKKKK__
VVVV____________""")
    SP_RANK_D = block(0, 23, "____pqp_________")
    SP_RANK_L = block(0, 24, "_______pq_______")
    spec("sailor", "Sailor", "npc_1", "sailor.png",
         "Deck spacer in a jumpsuit with harness straps and a visored deck cap (replaces Sailor).",
         "Group 6, B style: the sailor's own body as regions (shirt -> blue jumpsuit top J, collar stripes -> olive harness straps P, hair and trousers -> olive-brown N), new olive deck cap with a blue visor and white crest, pink rank plaque on the chest.",
         materials={"K": "c@", "V": "b", "J": "b", "P": "c", "N": "c"}, legend={"k": 15, "W": 14, "p": 6, "q": 5},
         accept={},
         base="sailor.png", remap={"b": "J", "c": "N", "w": "P"},
         patches={"down": [SP_CAP_D, SP_RANK_D], "up": [SP_CAP_U], "left": [SP_CAP_L, SP_RANK_L]})
# ====================================================================== SWIMMER_F: diver
# Swimming head above the water: a navy dive hood (H, ramp a) over the hair, a grey dive mask (M)
# with pale lenses (L, steel light) and white glints over the eyes, and a small grey A99-style
# breather (B) with a magenta tip at the mouth; her arms and the white splash are kept as regions.
# Moves to NPC_4 (navy, greys).
if want("swimmer_f"):
    SF_D = block(0, 15, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHMMMMMMMMHHH.
.HHMLLLMMLLLMHH.
.HHMLkLMMLkLMHH.
..HHMMMMMMMMHH..
...HsssBBsssH...
____ssssqsss____""")
    SF_U = block(0, 15, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.MMMMMMMMMMMMMM.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..""")
    SF_L = block(0, 15, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.MMMMMMHHHHHHH..
.LLLMMMMMMMMMH..
.LkLMHHHHHHHHH..
.MMMMHHHHHHHH...
BBssssHHHHHHH...
q_sssssHHHHH____""")
    spec("swimmer_f", "SwimmerF", "npc_4", "swimmer_f.png",
         "Swimmer (f) in a dive hood and mask with a small breather (replaces Swimmer F).",
         "Group 6, B style: the swimmer's own arms and white splash as regions, new head: navy dive hood over the hair, grey dive mask with pale lenses, small grey A99-style breather with a magenta tip at the mouth.",
         materials={"H": "a@", "M": "c", "B": "c", "b": "a"}, legend={"k": 15, "W": 14, "L": 14, "q": 9},
         accept={"hair_rows": "a dive hood, not hair", "eye_row": "eyes behind the dive mask, above the visible skin"},
         base="swimmer_f.png",
         patches={"down": [SF_D], "up": [SF_U], "left": [SF_L]})
# ====================================================================== MAGMA_MEMBER_F: stormtrooper
# A new stormtrooper helmet (W, white edged in the lavender-grey ramp, shaded underneath by Q): green-tinted lenses (E,
# glint e), a grey nose ridge, frowning vocoder grille and cheek tubes (g, d); her body as regions turned into
# white armour (arms U, legs/boots L, plates P) over a black bodyglove (k), with a white chest
# plate patched over the torso, a grey belt (B) and a black-and-orange squad pauldron (O, ramp c).
# Moves to NPC_3 (lavender-grey shades the white).
if want("magma_member_f"):
    ST_D = block(0, 11, """
.....WWWWWW.....
...WWWWWWWWWW...
..WWWWWWWWWWWW..
..WWgWWWWWWgWW..
.QWWWWWggWWWWWQ.
.QWWeEWWWWEeWWQ.
.gWEEEWWWWEEEWg.
.QQWWWWggWWWWQQ.
.QgQWWggggWWQgQ.
..QgQdgddgdQgQ..
...QQQggggQQQ...""")
    ST_U = block(0, 11, """
.....WWWWWW.....
...WWWWWWWWWW...
..WWWWWWWWWWWW..
..WWgWWWWWWgWW..
.QWWWWWggWWWWWQ.
.gWWWWWWWWWWWWg.
.QgWgWgWgWgWgWQ.
.QQWWWWWWWWWWQQ.
.QQQWWWWWWWWQQQ.
..QQQQWWWWQQQQ..
...QQQQQQQQQQ...""")
    ST_L = block(0, 11, """
......WWWWW.....
....WWWWWWWWW...
...WWWWWWWWWWW..
..WWWWWWWgWWWW..
..WWWWWWWWWWWWQ.
.EEEWWWWWWgWWWQ.
.WeEWWWWWWWWWQQ.
QWWWWgWWWWWWWQQ.
gdgQWgWWWWWWQQ..
.ggQQWWWWWWQQQ..
..QQQQQQQQQQQ...""")
    ST_BODY_D = block(0, 22, """
___kkkkkkkkkk___
_OOkPPPgPPPPkUU_
_OOkkkkkkkkkkUU_
___kkPgPPgPkk___
___BBBdBBdBBB___""")
    ST_BODY_U = block(0, 22, """
___kkkkkkkkkk___
_UUkPPPPPPPPkOO_
_UUkkkkkkkkkkOO_
___kkPPggPPkk___
___BBBdBBdBBB___""")
    ST_BODY_L = block(0, 22, """
____kkkkkkk_____
____PPPgPkk_____
____kkkkkkk_____
____kPPPPkk_____
____BBdBBBB_____""")
    spec("magma_member_f", "MagmaMemberF", "npc_3", "team_magma/magma_member_f.png",
         "Stormtrooper (f) in white armour with a squad pauldron (replaces Team Magma Grunt F).",
         "Group 6, B style: her body as regions (arms, legs and boots -> white armour over a black bodyglove), new stormtrooper helmet with green-tinted lenses, frowning grille and grey cheek tubes, white chest plate, grey belt, orange squad pauldron.",
         materials={"W": "w/a", "Q": "a", "U": "w/a", "L": "w/a", "P": "w/a", "B": "a", "O": "c"},
         legend={"k": 15, "E": 10, "e": 9, "g": 6, "d": 7},
         accept={"hair_rows": "a helmet, no hair", "skin_tones": "full armour: no skin shows", "eye_row": "black helmet lenses, no face",
                 "edge_black": "the bodyglove between the plates is black by design", "inner_black": "the bodyglove between the plates is black by design",
                 "colours_used": "a stormtrooper is white armour on a black bodyglove: white, black, the grey shading ramp, green-tinted lenses and the orange squad pauldron are every colour the costume has"},
         base="team_magma/magma_member_f.png", remap={"s": "U", "b": "L", "c": "P"},
         patches={"down": [ST_D, ST_BODY_D], "up": [ST_U, ST_BODY_U], "left": [ST_L, ST_BODY_L]})
# ====================================================================== WALLY: LUKE SKYWALKER
# A new head with a sandy-blond mop (H, olive ramp c) and a visible face; Wally's shirt
# becomes Luke's white farm tunic with the crossover wrap (T, edged olive), a dark blue belt (K)
# with a white buckle, tan trousers (H's ramp) and dark boots (B), and a lightsaber hilt (black
# and white hard pixels) hanging at the right hip. Stays on NPC_1.
if want("wally"):
    LK_HD = block(0, 11, """
................
.....HHHHHH.....
...HHhHHHHhHH...
..HHHHHhHHHHHH..
..HhHHHHHHHhHH..
.HHHHhHHHdHHHHH.
.HHHHHHHsssHHHH.
.HHHssssssssHHH.
.HHssksssskssHH.
.HHssksssskssHH.
..HssssssssssH..""")
    LK_HU = block(0, 11, """
................
.....HHHHHH.....
...HHhHHHHhHH...
..HHHHHhHHHHHH..
..HhHHHHHHHhHH..
.HHHHhHHHHHHHHH.
.HHHHHHHHhHHHHH.
.HHhHHHHHHHHdHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
...HHHHHHHHHH...""")
    LK_HL = block(0, 11, """
................
......HHHHHH....
....HHHhHHHHH...
...HHHHHHhHHHH..
..HhHHHHHHHHhH..
.HHHHHhHHHHHHH..
.sssHHHHHHHHHH..
.sssssHHHHHHHH..
.skssssHHHHHHH..
.skssssHHHHHH...
..ssssssHHHH....""")
    LK_D = block(0, 22, """
____TTssssTT____
____TgTsTTTT____
____TTgTTTTT____
____TTTgTTTT____
____KKKWKKKKk___
____TTTTTTTTW___""")
    LK_U = block(0, 22, """
____TTTTTTTT____
____TTTTTTTT____
____TTTTTTTT____
____TTTTTTTT____
____KKKKKKKK____
____TTTTTTTT____""")
    LK_L = block(0, 23, """
______TTTT______
_____TgTTTT_____
_____TTgTTT_____
_____KKKKKK_____
____kTTTTTT_____
____W___________""")
    spec("wally", "Wally", "npc_1", "wally.png",
         "LUKE SKYWALKER: farm-boy tunic, white wrappings, lightsaber at the hip (replaces Wally).",
         "Group 6, B style: new head with a sandy-blond mop of hair, Wally's own body as regions (shirt -> white crossover farm tunic T, trousers -> tan, shoes -> dark boots B), dark belt with a white buckle and a lightsaber hilt at the hip.",
         materials={"H": "c", "T": "w/c", "K": "b", "B": "b"}, legend={"k": 15, "W": 14, "h": 11, "d": 13, "g": 12},
         accept={},
         base="wally.png", remap={"c": "H", "w": "T", "b": "B"},
         patches={"down": [LK_HD, LK_D], "up": [LK_HU, LK_U], "left": [LK_HL, LK_L]})
# ====================================================================== YOUNGSTER: farm boy
# A new head with shaggy brown hair (H, ramp c) and pod-racing goggles pushed up on it (red strap G,
# amber lenses with white glints); the youngster's own body as regions: off-white wrap tunic (T,
# edged brown), ochre shorts (S, ramp a), bare legs and brown boots (D). Moves to NPC_2.
if want("youngster"):
    YG_D = block(0, 11, """
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..GLWGGGGGGLWG..
.HHHHHHHHHHHHHH.
.HHHsHHHsHHHsHH.
.HHssssssssssHH.
.HHssksssskssHH.
.HHssksssskssHH.
..HssssssssssH..""")
    YG_U = block(0, 11, """
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..GGGGGGGGGGGG..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
...HHHHHHHHHH...""")
    YG_L = block(0, 11, """
................
......HHHHHH....
....HHHHHHHHH...
...HHHHHHHHHHH..
..LWGGGGGGGGGH..
.HHHHHHHHHHHHH..
.sHsHHHHHHHHHH..
.sssssHHHHHHHH..
.skssssHHHHHHH..
.skssssHHHHHH...
..ssssssHHHH....""")
    spec("youngster", "Youngster", "npc_2", "youngster.png",
         "Young Tatooine farm boy in a wrap tunic, shorts and boots, racing goggles on his head (replaces Youngster).",
         "Group 6, B style: new head with shaggy brown hair and pod-racing goggles pushed up (red strap, amber lenses), the youngster's own body as regions (shirt -> off-white wrap tunic T, cap-coloured shorts -> ochre S, shoes -> brown boots D).",
         materials={"H": "c@", "G": "b", "T": "w/c", "S": "a", "D": "c"}, legend={"k": 15, "W": 14, "L": 5},
         accept={},
         base="youngster.png", remap={"w": "T", "b": "S", "c": "D"},
         patches={"down": [YG_D], "up": [YG_U], "left": [YG_L]})
print("ok")

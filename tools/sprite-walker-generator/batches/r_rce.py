"""Recast group e: NEW walkers for the Mos Eisley Cantina (net:mos-eisley-cantina).
WUHER the bartender (still kit, drawn whole on a stocky body), PONDA BABA the Aqualish thug
(Man 4's body as regions, new walrus head) and DR. EVAZAN (Man 3's body as regions, new scarred
head and high collar). None has a vanilla sheet of its own: `replaces` names the placeholder.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_rce.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402


def g(text):
    rows = text.strip("\n").split("\n")
    return ["................"] * (32 - len(rows)) + rows


# ====================================================================== WUHER (net:walker-wuher)
# Stocky and wide (fat-man proportions), dark brown hair (hand-indexed h/i, ramp c dark) combed back, heavy brows slanting down
# to the nose and a downturned mouth (the scowl), rust-brown shirt (T, sleeves R), grey bib apron (A)
# from the chest to the knees with a waist tie (Y) and a pocket (p), a white bar rag (w) over his
# left shoulder, dark trousers (P), black boots (K).
WU_DOWN = g("""
.....hhhhhh.....
...hhhiiiihhh...
..hhiihiihiihh..
.hhhihhihhihhhh.
.hhhssshhssshhh.
.hhsbssssssbshh.
.hsssbksskbsssh.
.ssssskssksssss.
..ssssksskssss..
..ssssmmmmssss..
...ssmssssmsss..
.TTTTAssssATTTT.
RRTTTAAAAAATwwRR
RRRTAAAWAAAAwwRR
RRRTYYYYYYYYTwRR
ssRTAAAAAAAATRss
ss.TApppAAAAT.ss
...PApAAAAAAP...
...PPAAAAAAPP...
...KKK....KKK...
................""")
WU_UP = g("""
.....hhhhhh.....
...hhhiiiihhh...
..hhiihiihiihh..
.hhhihhihhihhhh.
.hhhhihhihhihhh.
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
.shhhhhhhhhhhhs.
..shhhhhhhhhhs..
..sshhhhhhhhss..
...TssssssssT...
.TTTTATTTTATTTT.
RRwwTTATTATTTTRR
RRwwTTTAATTTTRRR
RRRTYYYYYYYYTRRR
ssRTTTTYYTTTTRss
ss.TTTYTTYTTT.ss
...PPPPPPPPPP...
...PPPPPPPPPP...
...KKK....KKK...
................""")
WU_LEFT = g("""
......hhhhhh....
....hhhiiiihhh..
...hhiihiihiihh.
..hhhhihhihhihh.
..hssshhhhhhhhh.
..ssbbbsshhhhhh.
.ssssbsssshhhhh.
.ssssksssssshhh.
..sssksssssshh..
..mmssssssshh...
...sssssssss....
...ATTTTTTTTT...
...AATTRRRTTTT..
...AAATRRRTTTT..
...YYYYRRRYYYY..
...AApTRRRTTTT..
...AAAAsssTTT...
....AAAAPPPP....
....AAAPPPPP....
.....KKKKKK.....
................""")
spec("sw_wuher", "Wuher", "npc_3", "man_4.png",
     "NEW WALKER (net:walker-wuher): WUHER, the Mos Eisley cantina bartender: stocky, scowling, dark hair, grey apron over a brown shirt (placeholder: Man 4).",
     "Recast group e, shade mode, drawn whole on a stocky fat-man-width body (still kit: he stands behind the round bar). Cues: wide stocky build, scowl (brows slanting to the nose, downturned mouth), grey bib apron over a rust-brown shirt, a white bar rag over one shoulder.",
     materials={"T": "c", "R": "c", "A": "a", "Y": "a", "P": "b", "K": "b", "w": "w/c"},
     legend={"k": 15, "W": 14, "m": 4, "h": 13, "i": 12, "b": 13, "p": 7},
     accept={},
     frames={"down": WU_DOWN, "up": WU_UP, "left": WU_LEFT}, kit="person16x32_still")


# ====================================================================== PONDA BABA (net:walker-aqualish)
# Aqualish: bald grey dome (F, round-shaded) with tiny wide-set black eyes, a broad walrus muzzle (M)
# with a dark mouth line, two white tusks (W) hanging down over the jacket; rust-brown leather jacket
# (Man 4's jacket regions, J) with grey Aqualish hands, tan trousers, a black blaster in a brown
# holster on the right hip.
PB_D = [block(0, 10, """
................
.....FtFFtF.....
...FFFFFFFFFF...
..FFFzzFFzzFFF..
..FFFFFzzFFFFF..
.FFFkFFFFFFkFFF.
.FFFkFFFFFFkFFF.
.FFFFFFFFFFFFFF.
FFFMMMMMMMMMMFFF
FFMMMMMMMMMMMMFF
.FMWMddddddMWMF.
..MWMMMMMMMMWM..
__JW________WJ__
__J__________J__"""), block(11, 25, """
_ho__
_hk__
_hk__""")]
PB_U = [block(0, 10, """
................
.....FtFFtF.....
...FFFFFFFFFF...
..FFFFFFFFFFFF..
..FFFzFFFFzFFF..
.FFFFzFFFFzFFFF.
.FFFFFFFFFFFFFF.
.FFFFFFFFFFFFFF.
FFFFFFFFFFFFFFFF
FFFFFFFFFFFFFFFF
.WFFFFFFFFFFFFW.
..WFFFFFFFFFFW..
__JJJJJJJJJJJJ__
__JJJJJJJJJJJJ__"""), block(0, 25, """
__h__
__k__""")]
PB_L = [block(0, 10, """
................
......FtFFt.....
....FFFFFFFF....
...FzzFFFFFFF...
..FFFFzFFFFzFF..
..FkFFFFFFFFFF..
..FkFFFFFFFFFF..
.MFFFFFFFFFFFF..
MMMMMFFFFFFFF...
MMMMMMFFFFFFF...
ddMMMMFFFFFF....
.WMMMMFFFFF.....
.W__JJJJJJJ_____
_W______________""")]
spec("sw_aqualish", "Aqualish", "npc_3", "man_4.png",
     "NEW WALKER (net:walker-aqualish): PONDA BABA, Aqualish thug: walrus face with two down-turned tusks, small eyes, brown leather jacket, holstered blaster (placeholder: Man 4).",
     "Recast group e, shade mode: Man 4's own body as regions (jacket -> rust-brown leather J, shirt -> dark green V, trousers -> tan on the skin ramp, arms -> grey Aqualish hands), new grey Aqualish dome (forehead creases, a few scalp tufts) with tiny wide-set eyes, a broad muzzle and two white tusks hanging over the jacket; black blaster in a brown hip holster.",
     materials={"F": "skin-a@", "M": "a", "J": "c", "V": "b", "G": "a", "P": "s"},
     legend={"k": 15, "W": 14, "d": 13, "h": 4, "o": 3, "z": 7, "t": 15},
     accept={"skin_tones": "Aqualish skin is the grey ramp a; no human skin on him",
             "hair_rows": "bald Aqualish dome, no hair",
             "eye_row": "tiny wide-set Aqualish eyes on a tall dome above the muzzle"},
     base="man_4.png", remap={"a": "P", "c": "J", "b": "V", "s": "G"},
     patches={"down": PB_D, "up": PB_U, "left": PB_L})


# ====================================================================== DR. EVAZAN (net:walker-evazan)
# Slim (Man 3's body), black-brown hair (H) slicked back with a widow's peak, a twisted face: the
# right eye lower than the left, a red scar (r) running from the brow over the cheek, a crooked mouth;
# reddish-brown jacket (J, ramp c) with a tall stand-up collar (Q) rising beside the jaw, crimson
# waistcoat (V) with a crimson cravat (x/X) and gold collar studs (y) and brown trousers (P). Hair is hand-indexed in the dark ramp-c tones.
EV_D = [block(0, 10, """
................
.....hhhhhh.....
...hhhiWiihhh...
..hihhiihiihih..
..hhihhihhihhh..
..hihhihhihhih..
.hhssshhhssshhh.
.hssssssssssrsh.
.hsssskssssrssh.
.sssssksskrssss.
..sssssssskrss..
.QsssmmmsssssQ..
.QQQssssssssQQQ.
__QQQyxxxxyQQQ__
______xXXx______
_______XX_______""")]
EV_U = [block(0, 10, """
................
.....hhhhhh.....
...hhhiWiihhh...
..hihhiihiihih..
..hhihhihhihhh..
..hihhihhihhih..
.hhhihhihhihhhh.
.hihhihhihhihhh.
.shhhhhhhhhhhhs.
..shhhhhhhhhhs..
..sshhhhhhhhss..
.QQQQssssssQQQQ.
.QQQQQQQQQQQQQQ.""")]
EV_L = [block(0, 10, """
................
......hhhhh.....
....hhhiWiihh...
...hhiihiihihh..
..hihhihhihhhh..
..hhihhihhihhh..
..sshhhhhhhhhh..
..ssssshhhhhhh..
.ssskrsshhhhhh..
..sskrssshhhhh..
..sssrsssshhQ...
..mmsssssssQQ...
____ssssQQQQ____""")]
spec("sw_evazan", "Evazan", "npc_2", "man_3.png",
     "NEW WALKER (net:walker-evazan): DR. CORNELIUS EVAZAN: scarred, twisted face, dark hair, reddish-brown jacket with a high collar (placeholder: Man 3).",
     "Recast group e, shade mode: Man 3's own body as regions (jacket -> reddish-brown J, shirt -> crimson waistcoat V with a crimson cravat, trousers P), new head: slicked-back dark brown hair with a widow's peak, lopsided eyes, a red scar across the right side of the face, a crooked mouth, and a tall stand-up collar flaring beside the jaw. Slim against Wuher's stocky build; reddish-brown jacket, hair near-black with a widow's peak, against Wuher's grey apron and combed-back brown hair.",
     materials={"J": "c", "Q": "c", "V": "b!", "P": "c"},
     legend={"k": 15, "W": 14, "r": 9, "m": 4, "h": 13, "i": 12, "x": 9, "X": 10, "y": 6},
     accept={},
     base="man_3.png", remap={"a": "H", "b": "J", "w": "V", "c": "P"},
     patches={"down": EV_D, "up": EV_U, "left": EV_L})

"""Recast group a (trainer recast 2026-11-01, wiki/bible/RECAST.md): five generic walkers whose class
now shows someone else. Each keeps the vanilla body it replaces as material regions (base + remap,
so the walk cycle stays) and patches in the new species head and costume cues; the learned shader
picks the tones (D13), round heads are banded (D15).

  hiker        UGNAUGHT miner    pink pig snout, white side whiskers, blue overalls, tan hard hat + lamp
  black_belt   WOOKIEE warrior   dark multi-tone brown fur, black nose, silver-box bandolier, bowcaster
  bug_catcher  JAWA              short brown hooded robe, glowing yellow eyes in a black hood, bandolier
  fisherman    QUARREN angler    squid dome head with four face tentacles, olive slicker, long pole
  maniac       RODIAN hunter     green head, big black eyes, snout, antennae and ear frills, hunter's vest

Writes art/<name>.yaml. Run from the tool folder: python batches/r_rca.py
"""
import sys

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P, block, spec  # noqa: E402
from walker_sprite.shade import regions_of  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import game_dir  # noqa: E402

ORDER = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]


def compose(path, remap, patches, mark=None, sway=0):
    """Whole frames from a vanilla sheet: its regions renamed by `remap`, then each stand frame's
    patches laid over it and over its two step frames one row lower (the bob). mark(name, grid,
    vanilla_regions) may then edit a frame (e.g. hands that follow the vanilla arm tips)."""
    fr, _ = read_frames(game_dir() / (P + path), (16, 32))
    out = {}
    for name, f in zip(ORDER, fr):
        van = regions_of(f)
        g = [[remap.get(c, c) for c in row] for row in van]
        stand = name.split("_")[0]
        dy = 0 if name == stand else 1
        # sway: the patches lean 1 px toward the stepping side on the down/up step frames
        dx = sway * {"down_a": -1, "down_b": 1, "up_a": 1, "up_b": -1}.get(name, 0)
        for p in patches.get(stand, []):
            for ry, ln in enumerate(p["rows"].split("\n")):
                if p["x"] == 0 and len(ln) == 16 and "_" not in ln:
                    g[p["y"] + ry + dy] = ["."] * 16  # a full redrawn row: no vanilla left at the swayed edge
                for rx, ch in enumerate(ln):
                    x = p["x"] + rx + dx
                    if ch != "_" and 0 <= x < 16:
                        g[p["y"] + ry + dy][x] = ch
        if mark:
            mark(name, g, van)
        out[name] = ["".join(r) for r in g]
    return out

# ====================================================================== HIKER -> UGNAUGHT miner
# NPC_1: tan hard hat (H dome, B brim, ramp c) with a white headlamp (L) on a dark mount (y);
# peach face (s) with a pink pig snout (P, skin-a) and dark nostrils; white whiskers (W) that
# flare out past the cheeks and meet in a short beard; blue work overalls (the Hiker's shirt b,
# trousers O) over the Hiker's own arms; a tan tool belt (G).
UG_D = block(0, 10, """
......HHHH......
....HHHHHHHH....
...HHHHyyHHHH...
..HHHHyLLyHHHH..
.BBBBBBBBBBBBBB.
..ssssssssssss..
.WssskssssksssW.
WWssskppppksssWW
WWWssqnppnqssWWW
.WWWssrrrrssWWW.
__WWWWWWWWWWWW__
_____WWWWWW_____
_____bbbbbb_____""")
UG_U = block(0, 10, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.BBBBBBBBBBBBBB.
..ssssssssssss..
.WssssssssssssW.
WWWssssssssssWWW
WWWWWWWWWWWWWWWW
.WWWWWWWWWWWWWW.
__WWbbbbbbbbWW__
_bbbbbbbbbbbbbb_
_bbbbbbbbbbbbbb_""")
UG_L = block(0, 10, """
......HHHH......
....HHHHHHHH....
..yLyHHHHHHHH...
..yLyHHHHHHHHH..
BBBBBBBBBBBBBB..
..ssssssssssss..
..ssksssssWWWW..
ppsksssssWWWWW..
pnqssssWWWWWW...
rrrsWWWWWWWWW...
.WWWWWWWWWWWbb..
___WWWWWWbbbb...
_____ssbbbbb____""")
UG_BELT_D = block(0, 26, "_GGGGGGGGGGGGGG_")
UG_BELT_L = block(0, 26, "___GGGGGGGGGG___")
spec("hiker", "Hiker", "npc_1", "hiker.png",
     "UGNAUGHT miner: pig snout, white whiskers, blue overalls, hard hat with a lamp (replaces the Hiker).",
     "Recast group a: the Hiker's own stout body as regions (shirt -> blue overalls b, trousers -> overall legs O, "
     "arms kept), new tan hard hat with a white headlamp, peach face with a pink pig snout (skin-a) and nostrils, "
     "white side whiskers flaring past the cheeks into a short beard, tan tool belt. Stays on NPC_1.",
     materials={"H": "c", "B": "c", "W": "w/c", "O": "b", "G": "c"},
     legend={"k": 15, "L": 14, "y": 13, "n": 15, "p": 5, "q": 6, "r": 7},
     accept={},
     base="hiker.png", remap={"a": "H", "c": "O"},
     patches={"down": [UG_D, UG_BELT_D], "up": [UG_U, UG_BELT_D], "left": [UG_L, UG_BELT_L]})

# ====================================================================== BLACK_BELT -> WOOKIEE warrior
# NPC_2 (Tarfful is orange NPC_3 fur and stand-only; this generic Wookiee is chocolate fur, ramp
# c): shaggy head (H, c@) with tufts, deep-set eyes under a brow, a peach muzzle (M, skin) with a
# black nose, lighter fur streaks (j: c light, J: skin shade) through head and chest; the Black
# Belt's body as fur (gi -> G, limbs -> F, belt -> lower fur D); a gold-brown leather bandolier
# (A, ramp a) with silver boxes (X: white edged in black); a bowcaster (Y, ramp b dark red frame,
# white limb tips) slung across the back.
WK_D = block(0, 10, """
.....H.HH.H.....
....HHHHHHHH..Ww
...HHHjHHHjHHyY.
..HHHHHHHHHHHHY.
..HjHHHHHHHHjH..
.HHHHHHHHHHHHHH.
.HHHHkHHHHkHHHH.
.HHHHkMMMMkHHHH.
.HHHMMMnnMMMHHH.
.jHHHMMMMMMHHHj.
..HHHHMMMMHHHH..""")
WK_D_B = block(0, 21, """
__AX____________
___AA___________
____XA__________
_____AA_________
______XA________
_______AA_______""")
WK_U = block(0, 10, """
.....H.HH.H.....
Ww..HHHHHHHH....
.YyHHHjHHHjHH...
.YHHHHHHHHHHHH..
..HjHHHHHHHHjH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHjHHHHHHjHHH.
.jHHHHHHHHHHHHj.
..HHHHHHHHHHHH..""")
WK_U_B = block(0, 21, """
____yY_______AA_
_____yY____AA___
______yY_AA_____
_______yAA______
______AAyY______
____AA___yY_____""")
WK_L = block(0, 10, """
......H.HH.H....
....HHHHHHHH.wW.
...HHHHHHjHHYy..
..HHHHHHHHHHYH..
..HHHHHHHjHHHH..
.HHHHHHHHHHHHH..
.HkHHHHHHHHHHH..
MkHHHHHHHHjHHH..
nMMHHHHHHHHHH...
MMMHHHHHHHHHH...
.MMHHHHHHHHH....""")
WK_L_B = block(0, 21, """
_______AA_______
________XA______
________AA______
_________XA_____""")
spec("black_belt", "BlackBelt", "npc_2", "black_belt.png",
     "WOOKIEE warrior: shaggy chocolate fur, black nose, silver-box bandolier, bowcaster slung on the back (replaces the Black Belt).",
     "Recast group a: the Black Belt's body as fur regions (gi -> torso fur G, limbs -> fur F, belt -> lower fur D), "
     "new shaggy Wookiee head (c@) with tufts, deep-set eyes, a peach muzzle and black nose, lighter fur streaks, "
     "a gold-brown bandolier with silver boxes, a bowcaster (dark red frame, white limb tips) across the back. "
     "Moves to NPC_2 so its chocolate fur reads apart from TARFFUL's orange NPC_3 fur.",
     materials={"H": "c@", "G": "c@", "F": "c", "M": "s"},
     legend={"k": 15, "n": 15, "X": 14, "W": 14, "w": 5, "j": 11, "A": 7, "Y": 7, "y": 6},
     accept={"hair_rows": "the whole head is fur", "eye_row": "deep-set Wookiee eyes inside fur",
             "skin_tones": "fur, not skin: only the muzzle uses the skin ramp"},
     base="black_belt.png", remap={"s": "F", "a": "G", "w": "G", "b": "G", "c": "H"},
     patches={"down": [WK_D, WK_D_B], "up": [WK_U, WK_U_B], "left": [WK_L, WK_L_B]})

# ====================================================================== BUG_CATCHER -> JAWA
# NPC_2: a short figure (top on row 13) in a chocolate-brown hooded robe (H hood, R robe body,
# S sleeves, all ramp c) with a pointed hood peak; a black hood opening (k) with two glowing
# yellow eyes (Y bright, y glow below); a gold-brown bandolier (A) with gold cells (X) across the
# chest; small wrapped hands (h, skin ramp); a maroon sash belt (L, ramp b). The Bug Catcher's own
# legs and walk stay as the robe hem (R) and dark boots (K).
JW_D = block(0, 11, """
................
................
.......HH.......
.....HHHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
..HHHkkkkkkHHH..
.HHHkkkkkkkkHHH.
.HHHkWkkkkWkHHH.
.HHHkYkkkkYkHHH.
.HHHHkkkkkkHHHH.
__SHHHHHHHHHHS__
____AXRRRRRR____
____RAXRRRRR____
____RRRAXRRR____
____RRRRRAXR____
___LLLLlLLLLL___""")
JW_U = block(0, 11, """
................
................
.......HH.......
.....HHHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
__SHHHHHHHHHHS__
____RRRRRRXA____
____RRRRRXAR____
____RRRXARRR____
____RXARRRRR____
___LLLLLLLLLL___""")
JW_L = block(0, 11, """
................
................
........HH......
......HHHHHH....
.....HHHHHHHH...
....HHHHHHHHHH..
...kkkHHHHHHHH..
..kkkkkHHHHHHH..
..kWkkkHHHHHHH..
..kYkkkHHHHHHH..
...kkkHHHHHHHH..
...HHHHHHHHHHH..
________________
__________AX____
_________AX_____
________________
____LL____LL____""")


def jw_hands(name, g, van):
    """Wrapped hands (h, outline g) on the tips of the Bug Catcher's own swinging arms."""
    if name.startswith("left"):
        return
    for xs in (range(0, 4), range(12, 16)):
        tips = [(y, x) for y in range(21, 29) for x in xs if van[y][x] == "s"]
        if tips:
            y, x = max(tips)
            g[y][x] = "g"
            if g[y - 1][x] in "SR":
                g[y - 1][x] = "h"


JW_FRAMES = compose("bug_catcher.png", {"s": "S", "b": "R", "k": "R", "c": "K"},
                    {"down": [JW_D], "up": [JW_U], "left": [JW_L]}, jw_hands, sway=1)
spec("bug_catcher", "BugCatcher", "npc_2", "bug_catcher.png",
     "JAWA: short scavenger in a brown hooded robe, glowing yellow eyes in a black hood, bandolier (replaces the Bug Catcher).",
     "Recast group a: a short figure (top on row 13) over the Bug Catcher's legs and walk: chocolate hooded robe "
     "(ramp c) with a pointed peak, black hood opening with two glowing yellow eyes, a gold-brown bandolier with "
     "gold cells across the chest, small wrapped hands, maroon sash belt, robe hem and dark boots. Moves to NPC_2.",
     materials={"H": "c@", "R": "c", "S": "c"},
     legend={"k": 15, "W": 14, "Y": 5, "A": 7, "X": 6, "K": 13, "L": 10, "l": 9, "h": 3, "g": 4},
     accept={"skin_tones": "hooded Jawa: only the small wrapped hands use the skin ramp",
             "hair_rows": "a hood, no hair", "eye_row": "two glowing eyes inside the black hood"},
     frames=JW_FRAMES)

# ====================================================================== FISHERMAN -> QUARREN angler
# NPC_1: tall squid-dome head (S, s@ banded, white glint W) with wide-set eyes, four rose face
# tentacles (hard ramp a: u light tip-roots, T mid, t dark ends) hanging over the collar; the
# Fisherman's jacket as an olive-khaki rain slicker (J, ramp c, its white trims merged in), blue
# trousers and sleeves (T -> O, ramp b), black boots; a long dark fishing pole (r) held upright at
# the hand with a white line tip (l) above the head.
QU_D = block(0, 10, """
......SSSS.....l
....SSSWSSSS...r
...SSSSWSSSSS..r
...SSSSSSSSSS..r
..SSSSSSSSSSSS.r
..SSSSSSSSSSSS.r
.SkSSSSSSSSSSkSr
.SkSSSSSSSSSSkSr
..SSSSSSSSSSSS.r
...SSSSSSSSSS..r
__uuJuuJJuuJuu_r
__TTJTTJJTTJTT_r
__TTJTTJJTTJTT_r
_eTJJTTJJTTJJTe_
______e__e_____r""")
QU_POLE = block(14, 25, """
r_
r_""")
QU_U = block(0, 10, """
l.....SSSS......
r...SSSWSSSS....
r..SSSSWSSSSS...
r..SSSSSSSSSS...
r.SSSSSSSSSSSS..
r.SSSSSSSSSSSS..
rSSSSSSSSSSSSSS.
rSSSSSSSSSSSSSS.
r.SSSSSSSSSSSS..
r.TSSSSSSSSSST..
rJTJJJJJJJJJJTJ_
rJeJJJJJJJJJJeJ_""")
QU_L = block(0, 10, """
.......SSSS...l.
.....SSSWSSSS.r.
....SSSSWSSSSSr.
...SSSSSSSSSSSr.
..SSSSSSSSSSSSr.
.SSSSSSSSSSSSSr.
.SkSSSSSSSSSSSr.
.SkSSSSSSSSSSSr.
.SSSSSSSSSSSS_r_
..SSSSSSSSSS__r_
uuJuuSSSSSS___r_
TTJTTJ________r_
TTJTT_________r_
e__eT_________r_
____e_________r_
______________r_""")


def qu_tips(name, g, van):
    """The tentacle ends (e) swing 1 px with the step, opposite to the stepping leg."""
    if name.endswith("_a") or name.endswith("_b"):
        d = -1 if name.endswith("_a") else 1
        cells = [(y, x) for y in range(32) for x in range(16) if g[y][x] == "e"]
        for y, x in cells:
            g[y][x] = "J" if y < 24 else "."
        for y, x in cells:
            if 0 <= x + d < 16:
                g[y][x + d] = "e"


QU_FRAMES = compose("fisherman.png", {"b": "J", "w": "J", "a": "O"},
                    {"down": [QU_D, QU_POLE], "up": [QU_U], "left": [QU_L]}, qu_tips)
spec("fisherman", "Fisherman", "npc_1", "fisherman.png",
     "QUARREN angler: squid-dome head with four face tentacles, khaki rain slicker, long fishing pole (replaces the Fisherman).",
     "Recast group a: the Fisherman's body as regions (jacket and its trims -> olive-khaki slicker J, sleeves and "
     "trousers -> blue O, boots kept), new tall banded squid-dome head with wide-set eyes and a white glint, four "
     "rose face tentacles hanging over the collar, a long dark pole held upright at the hand (in the "
     "side view it stands behind the far shoulder). Moves from NPC_2 to NPC_1 (khaki slicker, rose tentacles).",
     materials={"S": "skin-a@", "J": "c", "O": "b"},
     legend={"k": 15, "W": 14, "l": 14, "r": 13, "u": 5, "T": 6, "e": 7},
     accept={"hair_rows": "a bald squid dome, no hair", "eye_row": "wide-set Quarren eyes high on the dome",
             "skin_tones": "Quarren hide is the rose ramp; only the hands use the skin ramp"},
     frames=QU_FRAMES)

# ====================================================================== MANIAC -> RODIAN game hunter
# NPC_3 (green ramp b): round green head (G, skin-b@) with two thin antennae (q stalk, Q tip), fan
# ear frills (F, ramp b) sticking out at the sides, big black eyes with a white glint, a tapering
# snout (N, ramp b) ending in a dark mouth (m); green arms (the Maniac's skin -> A); an
# orange-brown hunter's vest (V, ramp c, his shirt) open over a tan undershirt (U, skin ramp), a
# dark belt with a holster (L, h); his grey-lavender trousers (a) and black boots kept.
RO_D = block(0, 10, """
...Q........Q...
....q......q....
.....GGGGGG.....
...GGGGGGGGGG...
..GGGGGGGGGGGG..
FFGGGGGGGGGGGGFF
FFGkkWGGGGWkkGFF
.FGkkkGGGGkkkGF.
..GGkkGGGGkkGG..
...GGGGNNGGGG...
....GGNNNNGG....
_____NNNNNN_____
______NmmN______""")
RO_D_T = block(0, 23, """
__VVVUUUUVVV____
__VVVUUUUVVV____
___VVUUUUVV_____
__VVVVUUVVVVV___
___LLLLLLLhL____""")
RO_U = block(0, 10, """
...Q........Q...
....q......q....
.....GGGGGG.....
...GGGGGGGGGG...
..GGGGGGGGGGGG..
FFGGGGGGGGGGGGFF
FFGGGGGGGGGGGGFF
.FGGGGGGGGGGGGF.
..GGGGGGGGGGGG..
...GGGGGGGGGG...
....GGGGGGGG....
__VVVVVVVVVVVV__
__VVVVVVVVVVVV__""")
RO_L = block(0, 10, """
.......Q........
........q.......
......GGGGGG....
....GGGGGGGGG...
...GGGGGGGGGGF..
..GGGGGGGGGGGFF.
..GkkWGGGGGGFFF.
.GGkkkGGGGGGGF..
NNGkkGGGGGGGG...
NNNGGGGGGGGG....
mNNNGGGGGGGG....
.mNN.GGGGGVVV...
_____UUVVVVV____
___________V____""")
spec("maniac", "Maniac", "npc_3", "maniac.png",
     "RODIAN game hunter: green head, big black eyes, tapering snout, antennae and ear frills, hunter's vest (replaces the Maniac).",
     "Recast group a: the Maniac's body as regions (skin -> green arms A, shirt -> orange-brown hunter's vest V, "
     "trousers and boots kept), new round green Rodian head (skin-b@) with thin antennae, fan ear frills, big black "
     "eyes with a white glint and a tapering snout with a dark mouth; a tan undershirt under the open vest, dark belt "
     "with a holster. Moves from NPC_2 to NPC_3 (green ramp).",
     materials={"G": "skin-b@", "F": "b", "N": "skin-b", "A": "skin-b", "V": "c", "U": "s"},
     legend={"k": 15, "W": 14, "q": 9, "Q": 8, "m": 10, "L": 13, "h": 12},
     accept={"hair_rows": "a bald Rodian head with antennae, no hair", "eye_row": "big Rodian eyes"},
     base="maniac.png", remap={"s": "A", "c": "V", "w": "V"},
     patches={"down": [RO_D, RO_D_T], "up": [RO_U], "left": [RO_L]})

if __name__ == "__main__":
    print("ok")

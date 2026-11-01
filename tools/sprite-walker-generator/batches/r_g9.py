"""Group 9: overworld companions (pokemon/ sheets) redrawn as STAR WARS: KYBER creatures.
Each subject is its wiki species row (wiki/mapping/species.csv). The vanilla sheet's size,
footprint and pose are kept so the creature sits where the Pokemon sat.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_g9.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import PK, block, spec  # noqa: E402,F401


def g(text):
    return [r for r in text.strip("\n").split("\n")]


NOSKIN = {"skin_tones": "creature: no human skin", "hair_rows": "creature: no hair", "eye_row": "creature eyes, not a human face"}

# ====================================================================== IONRAT (replaces Pikachu)
# Felucia rodent: round mouse ears with pink insides, yellow fur (round head H, body B), red ion
# glands on the cheeks, brown back stripes, a zigzag brown tail ending in a white ion spark.
spec("pikachu", "Pikachu", "npc_2", "pikachu.png",
     "IONRAT: Felucian rodent that discharges ion bolts (replaces Pikachu).",
     "Group 9: drawn on Pikachu's footprint; round mouse ears with pink insides, yellow fur, glowing red ion glands on the cheeks, brown back stripes and a thin zigzag tail crackling with a white spark.",
     materials={"H": "a@", "B": "a", "E": "a", "S": "s", "c": "c", "T": "c", "P": "s"},
     legend={"k": 15, "W": 14, "n": 4, "g": 8, "G": 9},
     accept=NOSKIN, kit="person16x16_still", root=PK,
     frames={"down": g("""
................
.EEE.......EEE..
ESSSE.....ESSSE.
ESSSEHHHHHESSSE.
.EEHHHHHHHHHEE..
..HHHHHHHHHHH...
.HHHkHHHHHkHHH..
.HHWkHHHHWkHHH..
.HgGHHHnHHHgGH.W
..HHHHHHHHHHH.T.
..HHHHHHHHHHHTT.
.HHHHHHHHHHHHT..
.HHHHHHHHHHHHH..
..HHHHHHHHHHH...
...PP.....PP....
................"""),
             "up": g("""
...............W
.EEE.......EEETT
EEEEE.....EEEET.
EEEEEHHHHHEEEET.
.EEHHHHHHHHHEET.
..HHHHHHHHHHHT..
.HHHHHHHHHHHHT..
.HHHHHHHHHHHTH..
.HHHHHHHHHHHTH..
..HHHHHHHHHHH...
..HHcHHHHHcHHH..
.HHHcHHHHHcHHH..
.HHHHcHHHcHHHH..
..HHHHHHHHHHH...
...PP.....PP....
................"""),
             "left": g("""
................
.......EEE......
......ESSSE.....
.....EESSSE...W.
...HHHHEEE...TT.
..HHHHHHHHH...T.
.HHkHHHHHHHH.TT.
.HWkHHHHHHHH.T..
nHHHgGHHHHHH.T..
.HHHHHHHHHHHTT..
..HHHHHHHHHHT...
...HHHHHHcHHHH..
...HHHHHHHcHHH..
...HHHHHHHHHH...
....PP....PP....
................""")})

# ====================================================================== BLOOPHARE (replaces Azumarill)
# Naboo swamp hare: tall upright ears with pink insides, round blue head (H) and body (B), white
# belly, pink cheeks, olive webbed feet and an olive reed-tuft tail.
HARE_MAT = {"H": "b@", "B": "b", "E": "b", "S": "a", "w": "w/c", "f": "c", "t": "c"}
spec("azumarill", "Azumarill", "npc_1", "azumarill.png",
     "BLOOPHARE: long-eared Naboo water rodent (replaces Azumarill).",
     "Group 9: drawn on Azumarill's footprint; tall hare ears with pink insides, round blue head and body, white belly, olive webbed feet and reed-tuft tail.",
     materials=HARE_MAT, legend={"k": 15, "W": 14, "p": 5, "n": 4},
     accept=NOSKIN, kit="person16x16_still", root=PK,
     frames={"down": g("""
..EEE....EEE....
..ESE....ESE....
..ESE....ESE....
..ESEHHHHESE....
..HHHHHHHHHHH...
.HHHHHHHHHHHHH..
.HHWkHHHHWkHHH..
.HHpkHHnHHkpHH..
BBHHHHHHHHHHHBB.
BBBBwwwwwwwBBBB.
BBBwwwwwwwwwBBB.
.BBwwwwwwwwwBBtt
..BBwwwwwwwBBttt
...BBBBBBBBBB.t.
...ff.....ff....
................"""),
             "up": g("""
..EEE....EEE....
..EEE....EEE....
..EEE....EEE....
..EEEHHHHEEE....
..HHHHHHHHHHH...
.HHHHHHHHHHHHH..
.HHHHHHHHHHHHH..
.HHHHHHHHHHHHH..
BBHHHHHHHHHHHBB.
BBBBBBBBBBBBBBB.
BBBBBBBBBBBBBBB.
.BBBBBBttBBBBB..
..BBBBtttBBBB...
...BBBBtBBBBB...
...ff.....ff....
................"""),
             "left": g("""
......EEE.......
.....ESSE.......
.....ESSE.......
....HHESE.......
..HHHHHEE.......
.HHHHHHHHH......
.HWkHHHHHH......
nHpkHHHHHH......
.HHHHHHHHBBB....
..wwwBBBBBBBB...
.wwwwBBBBBBBB...
.wwwwBBBBBBBBtt.
..wwwBBBBBBBttt.
...BBBBBBBBB.t..
....ff....ff....
................""")})

# ====================================================================== BLOOPKIT (replaces Azurill)
# The hare's kit: short round ears, round blue head and body, white belly, pink cheeks, and the
# bouncy tail: a coiled olive stalk ending in a round swamp-float bulb (O).
spec("azurill", "Azurill", "npc_1", "azurill.png",
     "BLOOPKIT: bouncy Naboo swamp rodent kit (replaces Azurill).",
     "Group 9: drawn on Azurill's footprint; short round pink-lined ears, round blue body, white belly and a coiled tail ending in an olive swamp-float bulb.",
     materials={**HARE_MAT, "O": "c@"}, legend={"k": 15, "W": 14, "p": 5, "n": 4},
     accept=NOSKIN, kit="person16x16_still", root=PK,
     frames={"down": g("""
................
................
................
..EE.......EE...
.ESSE.....ESSE..
.ESEHHHHHHHESE..
..HHHHHHHHHHH...
.HHWkHHHHWkHHH..
.HHpkHHnHHkpHH.t
..HHHHHHHHHHH.tO
..BBBwwwwwBBBOOO
..BBwwwwwwwBBOOO
...BBwwwwwBB.OO.
...BBBBBBBBB....
....ff...ff.....
................"""),
             "up": g("""
................
................
................
...EE.......EE..
..EEEE.....EEEE.
..EEEHHHHHHHEEE.
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
...HHHHHHHHHHH..
..tBBBBBBBBBBB..
OOtBBBBBBBBBB...
OOOBBBBBBBBBB...
OOOBBBBBBBBB....
.OO.ff...ff.....
................"""),
             "left": g("""
................
................
.......EE.......
......ESSE......
.....EESSE......
...HHHHEE.......
..HHHHHHHH......
.HWkHHHHHHH.....
nHpkHHHHHHHBB...
.HHHHHHHHBBBBB..
..wwwBBBBBBBBt..
.wwwwBBBBBBBBtOO
..wwwBBBBBBBBOOO
...BBBBBBBBB.OOO
....ff...ff..OO.
................""")})

# ====================================================================== SCURRIER (replaces Zigzagoon)
# Tatooine scavenger rodent: sand-olive fur (head H, body B), curled cream ram horns (h, skin
# ramp), a pink nose, a darker spine ridge, and a blue scrap bolt (x) carried in its mouth.
spec("zigzagoon_ow", "Zigzagoon", "npc_1", "zigzagoon.png",
     "SCURRIER: Tatooine scrap-hunting rodent with curled horns (replaces the small Zigzagoon).",
     "Group 9: drawn on Zigzagoon's footprint; sand fur, curled cream ram horns, pink nose, dark spine ridge and a blue scrap bolt carried in its mouth (Pickup).",
     materials={"H": "c@", "B": "c", "h": "s", "x": "b", "d": "c", "f": "c", "T": "c"}, legend={"k": 15, "W": 14, "n": 6},
     accept=NOSKIN, kit="person16x16_still", root=PK,
     frames={"down": g("""
................
.hhh........hhh.
hh.hhHHHHHHhh.hh
h..hHHHHHHHHh..h
hh.HHHHHHHHHH.hh
.hHHHHHHHHHHHHh.
..HHHkHHHHkHHH..
..HHWkHHHWkHHH..
...HHHHnnHHHH...
..BBBHHxxHHBBB..
.BBBBBBxxBBBBBB.
.BBBBBBBBBBBBBB.
..BBBBBBBBBBBB..
...BBBBBBBBBB...
...ff......ff...
................"""),
             "up": g("""
................
.hhh........hhh.
hh.hhHHHHHHhh.hh
h..hHHHHHHHHh..h
hh.HHHHHHHHHH.hh
.hHHHHHHHHHHHHh.
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
...HHHHddHHHH...
..BBBBBddBBBBB..
.BBBBBBddBBBBBB.
.BBBBBBddBBBBBB.
..BBBBBddBBBBB..
...BBBBTTBBBB...
...ff..TT..ff...
................"""),
             "left": g("""
................
................
......hhh.......
.....hh.hh......
.....h...h......
...HHHhhhh......
..HHHHHHHH...TT.
.HHkHHHHHHBBBBT.
nHWkHHHHHddddBB.
nnHHHHHHBBBBBBB.
.xxHHHHBBBBBBBB.
.xx.BBBBBBBBBB..
...BBBBBBBBBB...
...BBBBBBBBBB...
....ff....ff....
................""")})

# ====================================================================== TAOZIN (replaces Kecleon)
# Endor's unseen beast: a pale lavender-grey hide (H head, B body) dotted with white shimmer
# (it is invisible to sight), a green spine crest, orange turret eyes, a green belly band.
spec("kecleon", "Kecleon", "npc_3", "kecleon.png",
     "TAOZIN: Endor creature invisible to sight and to the Force (replaces Kecleon).",
     "Group 9: drawn on Kecleon's footprint; pale shimmering lavender hide dotted with white, green spine crest, orange turret eyes and a green belly band.",
     materials={"H": "a@", "B": "a", "s": "b", "E": "c", "z": "b", "f": "a"}, legend={"k": 15, "W": 14, "m": 4},
     accept=NOSKIN, kit="person16x16_still", root=PK,
     frames={"down": g("""
....ss....ss....
...sHHs..sHHs...
..HHHHHHHHHHHH..
.HHHWHHHHHHWHHH.
.HEEEHHHHHHEEEH.
.HEkEHHHHHHEkEH.
.HHEEHHHHHHEEHH.
..HHHHmmmmHHHH..
.sBBBBBBBBBBBBs.
ssBBWBBBBBBWBBss
.sBBBzzzzzzBBBs.
..BBBBzzzzBBBB..
...BBBBBBBBBB...
...ff.BBBB.ff...
...ff......ff...
................"""),
             "up": g("""
....ss....ss....
...sHHs..sHHs...
..HHHHssssHHHH..
.HHHWHHssHHWHHH.
.HHHHHHssHHHHHH.
.HHHHHHssHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHssHHHHH..
.sBBBBBssBBBBBs.
ssBBWBBssBBWBBss
.sBBBBBssBBBBBs.
..BBBBBssBBBBB..
...BBBBBBBBBB...
...ff.BBBB.ff...
...ff......ff...
................"""),
             "left": g("""
.........ss.....
.......ssHHs....
.....HHHHHHHs...
...HHHHHWHHHHs..
..EEEHHHHHHHHs..
.EkEEHHHHHHHs...
.EEEHHHHHHHHs...
mHHHHHHHHHHHss..
.HHHBBBBBBBBBs..
..BBBBBBWBBBBBs.
..zzzzBBBBBBBBs.
...zzzBBBBBBBB..
....ffBBBBBff...
....ff.....ff...
................
................""")})

# ====================================================================== LOTHKIT (replaces Skitty)
# Lothal loth-cat kitten: cream fur on the skin ramp (H head, B body), tall ears banded in orange
# (E) with black tufts, orange forehead stripes, big yellow eyes with slit pupils, red nose,
# and a ringed fluffy tail.
spec("skitty", "Skitty", "npc_2", "skitty.png",
     "LOTHKIT: playful Lothal loth-cat kitten (replaces Skitty).",
     "Group 9: drawn on Skitty's footprint; cream fur, tall orange-banded ears with black tufts, orange forehead stripes, big yellow slit eyes, red nose and a ringed tail.",
     materials={"H": "s@", "B": "s", "E": "a", "i": "s", "r": "a", "T": "s", "f": "c"}, legend={"k": 15, "W": 14, "y": 5, "n": 9, "t": 13},
     accept={"hair_rows": "creature: no hair", "eye_row": "creature eyes, not a human face"}, kit="person16x16_still", root=PK,
     frames={"down": g("""
..t..........t..
..EE........EE..
..EiE......EiE..
..EiiEHHHHEiiE..
..EiHHHrrHHHiE..
..HHHHrHHrHHHH..
.HHHHHHHHHHHHHH.
.HHyyHHHHHHyyHH.
.HHykHHHHHHkyHH.
..HHHHHnnHHHHH..
...HHHHHHHHHH...
...BBrrBBrrBB...
...BBBBBBBBBB...
...BBBBBBBBBB...
....ff....ff....
................"""),
             "up": g("""
..t..........t..
..EE........EE..
..EEE......EEE..
..EEEEHHHHEEEE..
..EEHHHrrHHHEE..
..HHHHrHHrHHHH..
.HHHHHrHHrHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHTTHHHHH..
...HHHrTTrHHH...
...BBBBrrBBBB...
...BBBBTTBBBB...
...BBBBBBBBBB...
....ff....ff....
................"""),
             "left": g("""
......t.........
.....EE.........
.....EiE........
.....EiiE.......
....HEiiEH..TT..
...HHHrHHH..rT..
..HHHHHrHHH.TT..
.HyyHHHHHHH..r..
.HykHHHHHHHBTT..
nHHHHHHHBBBBBr..
.HHHHHHBBBBBBB..
..HHHrrBBrrBBB..
....BBBBBBBBBB..
....BBBBBBBBB...
.....ff...ff....
................""")})

# ====================================================================== SITHWRAITH (replaces Dusclops)
# A hooded wraith on Dusclops' footprint and walk: a round maroon hood (H) over a void face (v)
# with one burning eye (yellow core y, orange o, red ring r), a robe (R) with wide sleeves (S),
# a red Sith sash (D) and bone-pale claws (h); the feet and hem keep Dusclops' own walk.
SW_D = block(0, 11, """
.......HH.......
......HHHH......
.....HHHHHH.....
....HHHHHHHH....
....HHvvvvHH....
...HHvvrrvvHH...
...HHvrWyrvHH...
..HHHvroorvHHH..
..HHHHvrrvHHHH..
..RRHHvvvvHHRR..
.RRRRRHHHHRRRRR.
.RRRRRRRRRRRRRR.
RRRRRRDDDDRRRRRR
RRRRRDDDDDDRRRRR
hhRRRRRDDRRRRRhh
jhjRRRRRRRRRRjhj""")
SW_U = block(0, 11, """
.......HH.......
......HHHH......
.....HHHHHH.....
....HHHHHHHH....
....HHHHHHHH....
...HHHHHHHHHH...
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..RRHHHHHHHHRR..
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
RRRRRRRRRRRRRRRR
RRRRRDDDDDDRRRRR
RRRRRRDDDDRRRRRR
.RRRRRRDDRRRRRR.""")
SW_L = block(0, 11, """
......HH........
.....HHHH.......
.....HHHHH......
....HHHHHHH.....
...vvHHHHHHH....
..vrrvHHHHHH....
..rooyHHHHHHH...
..vrrvHHHHHHH...
.HvvHHHHHHHHH...
.RHHHHHHHHHHRR..
RRRRRRRRRRRRRR..
RRRRRRRRRRRRRRR.
RRRRRRRRDDRRRRR.
.RRRRRRRDDRRRRR.
..hhRRRRDDRRRRR.
..jhjRRRRRRRRRRR""")
spec("dusclops", "Dusclops", "npc_2", "dusclops.png",
     "SITHWRAITH: dark-side wraith with one burning eye (replaces Dusclops).",
     "Group 9: a hooded maroon Sith wraith on Dusclops' footprint and walk; a void face with one burning yellow-orange-red eye, wide sleeves, a red Sith sash and bone-pale claws.",
     materials={"H": "c@", "R": "c", "D": "b"}, legend={"k": 15, "W": 14, "y": 5, "o": 6, "r": 9, "v": 15, "h": 1, "j": 3},
     accept=NOSKIN, kit="person16x32", root=PK,
     base="dusclops.png", remap={"c": "R", "a": "R", "w": "R", "s": "R", "b": "R"},
     patches={"down": [SW_D], "up": [SW_U], "left": [SW_L]})

# ====================================================================== AURADANCER (replaces Kirlia)
# Dagobah Force sprite: a glowing pale head (F) with two fine antennae (A) tipped with light (o),
# big green leaf ears (L), big dark eyes, and Kirlia's skirt turned into leaves (P) on stems (S).
KH_D = block(0, 15, """
....o......o....
.....A....A.....
.....FFFFFF.....
....FFFFFFFF....
LL.FFFFFFFFFF.LL
LLLFFFFFFFFFFLLL
.LLLFFFFFFFFLLL.
..LLFkkFFkkFLL..
...FFkWFFkWFF...
...FFpFFFFpFF...
....FFFFFFFF....
.....FFFFFF.....""")
KH_U = block(0, 15, """
....o......o....
.....A....A.....
.....FFFFFF.....
....FFFFFFFF....
LL.FFFFFFFFFF.LL
LLLFFFFFFFFFFLLL
.LLLFFFFFFFFLLL.
..LLFFFFFFFFLL..
...FFFFFFFFFF...
...FFFFFFFFFF...
....FFFFFFFF....
.....FFFFFF.....""")
KH_L = block(0, 15, """
........o..o....
.........AA.....
.....FFFFFF.....
....FFFFFFFF....
...FFFFFFFFFLL..
..FFFFFFFFFLLLL.
..FFFFFFFFFFLLL.
.FkkFFFFFFFF.L..
.FWkFFFFFFFF....
..FpFFFFFFFF....
...FFFFFFFF.....
....FFFFFF......""")
spec("kirlia", "Kirlia", "npc_3", "kirlia.png",
     "AURADANCER: Dagobah Force sprite that dances when its trainer is happy (replaces Kirlia).",
     "Group 9: Kirlia's own body as regions; new glowing pale-lavender sprite head with two fine antennae tipped with amber light, two big green leaf ears, big dark eyes with glints, pink cheeks, and a green leaf skirt on brown stems.",
     materials={"F": "skin-a@", "L": "b", "P": "b", "S": "c"}, legend={"k": 15, "W": 14, "o": 11, "A": 6, "p": 3},
     accept=NOSKIN, kit="person16x32", root=PK,
     base="kirlia.png", remap={"a": "P", "b": "S", "c": "S", "w": "W"},
     patches={"down": [KH_D], "up": [KH_U], "left": [KH_L]})
# ====================================================================== PRIMORDIAL (replaces Mew)
# Mew's floating pose and swinging tail are kept pixel for pixel, but the region shader turns
# its thin tail and limbs to mud (tried: two region passes), so this one is a hand recolour of
# the vanilla tones written as hard pixels: a pale glowing lavender body (skin tones -> ramp A,
# white kept as the glow), warm skin-ramp ears, green Wellspring eyes, a green life-mark on the
# brow and a tail that ends in a green leaf-bud of light.
NPC1 = "../../game/graphics/object_events/palettes/npc_1.pal"
MEW_MAP = {1: 5, 2: 5, 3: 6, 4: 7, 7: 7, 14: 14, 9: 9, 6: 3}
HEX = ".123456789ABCDEF"


def _mew_frames():
    from PIL import Image
    pal = [tuple(map(int, ln.split())) for ln in open(NPC1).read().split("\n")[3:19]]
    im = Image.open("../../game/" + PK + "mew.png").convert("RGB")
    names = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]
    out = {}
    for i, n in enumerate(names):
        idx = [[pal.index(im.getpixel((i * 16 + x, y))) for x in range(16)] for y in range(32)]
        top = next(y for y in range(32) if any(idx[y]))
        g2 = [[MEW_MAP.get(v, v) if v else 0 for v in row] for row in idx]
        for y in range(top, top + 2):                      # tail tip -> green bud of light
            for x in range(16):
                if idx[y][x]:
                    g2[y][x] = 10 if idx[y][x] == 7 else (8 if y == top + 1 else 9)
        out[n] = ["".join(HEX[v] for v in row) for row in g2]
    for n, dy in (("down", 0), ("down_a", 1), ("down_b", -1), ("up", 0), ("up_a", 1), ("up_b", -1)):  # life-mark
        r = list(out[n][17 + dy]); r[7] = r[8] = HEX[8]; out[n][17 + dy] = "".join(r)
        r = list(out[n][16 + dy]); r[7] = r[8] = HEX[9]; out[n][16 + dy] = "".join(r)
    return out


spec("mew", "Mew", "npc_3", "mew.png",
     "PRIMORDIAL: the first creature, born in the Wellspring of Life on Mortis (replaces Mew).",
     "Group 9: Mew's floating pose and swinging tail kept as a hand recolour: pale glowing lavender body with white glow, warm ears, green Wellspring eyes, a green life-mark on the brow and crown, and a tail ending in a green leaf-bud of light.",
     materials={}, legend={c: i for i, c in enumerate(HEX) if i},
     accept=NOSKIN, kit="person16x32", root=PK, frames=_mew_frames())

# ====================================================================== GNARLTREE (replaces Sudowoodo)
# Sudowoodo's three still poses (stand, left bough up, right bough up) as regions: a twisted bark
# trunk (T) with spreading roots and shelf fungus (f), mossy Dagobah boughs (M) with pale
# lavender moss hanging from them (m), and two small eyes on the knot that give the act away.
GT_EYES = block(6, 14, "e__e")
GT_FUNGUS = [block(10, 24, "fF"), block(4, 25, "Ff")]
spec("sudowoodo", "Sudowoodo", "npc_3", "sudowoodo.png",
     "GNARLTREE: Dagobah creature that pretends to be a gnarltree (replaces Sudowoodo).",
     "Group 9: Sudowoodo's three poses as regions turned into a twisted bark trunk with spreading roots and shelf fungus, mossy green boughs hung with pale lavender Dagobah moss, and two small glowing eyes on the knot.",
     materials={"T": "c", "M": "b@", "m": "a"}, legend={"k": 15, "W": 14, "e": 11, "f": 2, "F": 3},
     accept=NOSKIN, kit="person16x32_still", root=PK,
     base="sudowoodo.png", remap={"s": "T", "c": "T", "b": "M"},
     patches={"down": [GT_EYES, *GT_FUNGUS, block(2, 21, "m_m\nm__"), block(11, 21, "m_m\n__m")],
              "up": [block(6, 15, "e__e"), *GT_FUNGUS, block(2, 21, "m_m\nm__"), block(11, 23, "m_m\n__m")],
              "left": [block(6, 15, "e__e"), *GT_FUNGUS, block(2, 23, "m_m\nm__"), block(11, 21, "m_m\n__m")]})

# ====================================================================== SHYYYOLET (replaces Wingull)
# Wingull's six glide/flap frames kept pixel for pixel (thin wing outlines do not survive the region
# shader) as a hand recolour: a white down-covered chick with olive-tan Kashyyyk wings, pale blue
# feather tips, a blue double crest tuft and blue tail streamers, black eyes, a pink beak and feet.
WG_MAP = {9: 12, 8: 8, 10: 13, 14: 14, 13: 15, 12: 6, 2: 5, 3: 7}


def _wingull_frames():
    from PIL import Image
    pal = [tuple(map(int, ln.split())) for ln in open(NPC1).read().split("\n")[3:19]]
    im = Image.open("../../game/" + PK + "wingull.png").convert("RGB")
    names = ["down", "down_a", "up", "up_a", "left", "left_a"]
    out = {}
    for i, n in enumerate(names):
        idx = [[pal.index(im.getpixel((i * 16 + x, y))) for x in range(16)] for y in range(16)]
        g2 = [[WG_MAP.get(v, v) if v else 0 for v in row] for row in idx]
        if n.startswith("left"):                              # tail streamers stay blue
            for y in range(16):
                for x in range(11, 16):
                    if idx[y][x] == 9:
                        g2[y][x] = 9
        else:
            for y in range(16):                               # outer wing feathers olive-tan
                for x in (0, 1, 2, 3, 12, 13, 14, 15):
                    if idx[y][x] == 14:
                        g2[y][x] = 11
                                                              # crest: head-top bumps go blue,
            top = next(y for y in range(16) if any(idx[y][5:11]))  # with a light tip above
            for x in range(5, 11):
                if idx[top][x] == 9 and not any(idx[top][x2] for x2 in range(x - 1, x + 2) if x2 != x):
                    g2[top][x] = 9
                    if top > 0:
                        g2[top - 1][x] = 8
                    if top + 1 < 16 and idx[top + 1][x] == 9:
                        g2[top + 1][x] = 10
        out[n] = ["".join(HEX[v] for v in row) for row in g2]
    return out


spec("wingull", "Wingull", "npc_1", "wingull.png",
     "SHYYYOLET: Shyyyo chick that glides on the sea winds of Kashyyyk (replaces Wingull).",
     "Group 9: Wingull's glide and flap frames kept as a hand recolour: a white chick with olive-tan wings, pale blue feather tips, a blue double crest tuft and tail streamers, black eyes, pink beak and feet.",
     materials={}, legend={c: i for i, c in enumerate(HEX) if i},
     accept=NOSKIN, kit="flyer16x16", root=PK, frames=_wingull_frames())

print("ok")

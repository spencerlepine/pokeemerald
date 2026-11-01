"""Batch 3: three variations each of Yoda, IG-88 and Dexter, for the owner to say which one is
getting closer (owner, after v3: "slightly better but still not there... the robot doesn't look
top-down"). Each variation tests one hypothesis, named in its notes. Writes art/<name>_<a|b|c>.yaml.
Run from the tool folder: python batches/batch3.py
"""
import shutil
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402  (same helpers; batch2 also re-writes its own specs on import)

P = "graphics/object_events/pics/people/"


def rows16(*rs):
    for r in rs:
        assert len(r) == 16, (len(r), r)
    return list(rs)


def auto_steps(stand: dict, patch_y: int, split_x: int):
    """Step frames for a regions-only sprite: body drops 1 px (shift), legs stay on the ground,
    and one leg lifts its foot by a row (a: right leg, b: left leg; left frames alternate too)."""
    out = {}
    for d in ("down", "up", "left"):
        legs = stand[d][patch_y:31]
        for suffix, lift_right in (("_a", True), ("_b", False)):
            rows = []
            for i, r in enumerate(legs):
                lo, hi = (split_x, 16) if lift_right else (0, split_x)
                # lifted side: take the row below (shift that leg up by one), last row empty
                src = legs[i + 1] if i + 1 < len(legs) else "." * 16
                rows.append(r[:lo] + src[lo:hi] + r[hi:])
            out[d + suffix] = (d, patch_y, rows)
    return out


EMPTY = ["................"] * 32

# ====================================================================== YODA
# A: v3 as approved for review (short, dome/face/ears volumes) -- copied unchanged.
shutil.copy("art/yoda.yaml", "art/yoda_a.yaml")

# B: vanilla kid proportions. boy_1's body as regions under a new head the size of a vanilla
# head (10 rows, 14 wide + ears), robe with sleeves, tunic V, legs showing under the hem.
# Hypothesis: the squat v3 is what reads as "not Emerald"; vanilla proportions fix it.
YB_HEAD_D = block(0, 12, """
.....GGGGGG.....
...WGGGGGGGGW...
..GGGGGGGGGGGG..
..GGGGGGGGGGGG..
E.GGGGGGGGGGGG.E
EEEgggggggggggEE
EEEggkggggkggEEE
.EEggkggggkggEE.
..gggggggggggg..
...gggggggggg...
..CCccwwwwccCC..
.CCCccwwwwccCCC.
.gCCcccwwcccCCg.
..CCaaaaaaaaCC..
..cccccccccccc..
...cccccccccc...""")
YB_HEAD_U = block(0, 12, """
.....GGGGGG.....
...WGGGGGGGGW...
..GGGGGGGGGGGG..
..GGGGGGGGGGGG..
E.GGGGGGGGGGGG.E
EEEGGGGGGGGGGGEE
EEEGGGGGGGGGGEEE
.EEGGGGGGGGGGEE.
..GGGGGGGGGGGG..
...cccccccccc...
..CCccccccccCC..
.CCCccccccccCCC.
.gCCccccccccCCg.
..CCaaaaaaaaCC..
..cccccccccccc..
...cccccccccc...""")
YB_HEAD_L = block(0, 12, """
....GGGGGG......
..WGGGGGGGG.....
..GGGGGGGGGG....
.GGGGGGGGGGG....
.GGGGGGGGGGG..E.
.gggggggggGGEEEE
.ggkggggggggEEE.
.ggkggggggggEE..
..gggggggggg....
...ggggggggg....
....cwwccccc....
...ccwwCCcccc...
...ccwcCCcccc...
...caaaggaaac...
...cccccccccc...
....cccccccc....""")
spec("yoda_b", "Juan", "npc_3", "gym_leaders/juan.png",
     "YODA (B): vanilla kid proportions, robe with sleeves, legs under the hem.",
     "Batch 3 B. Hypothesis: vanilla proportions (10-row head, 20 rows tall) read as Emerald where the squat A does not. boy_1 body as regions.",
     materials={"g": "skin-b@", "G": "b@", "E": "b", "c": "c!", "C": "c!", "w": "s", "a": "a"}, legend={"k": 15, "W": 14},
     accept={"hair_rows": "two wisps, no hair mass", "skin_tones": "green hide uses ramp B", "head_w": "16 wide ear to ear",
             "eye_row": "eyes are on row 18-19; the detector looks for them beside human skin tones", "step_change": "a robe body changes fewer pixels than a shirt with bare arms"},
     base="boy_1.png", remap={"s": "g", "a": "c", "k": "c", "b": "g", "c": "G"},
     patches={"down": [YB_HEAD_D], "up": [YB_HEAD_U], "left": [YB_HEAD_L]})

# C: hood up. The robe's hood frames the green face, ears poke out of the hood, same body as B.
# Hypothesis: the hood is the Jedi silhouette; the brown frame makes the face pop.
YC_HEAD_D = block(0, 12, """
.......HH.......
......HHHH......
.....HHHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
...HHggggggHH...
E..HHgkggkgHH..E
EEEHHgkggkgHHEEE
.EEHHggggggHHEE.
...HHHHggHHHH...
..CCHHHwwHHHCC..
.CCCccwwwwccCCC.
.gCCcccwwcccCCg.
..CCccccccccCC..
..cccccccccccc..
...cccccccccc...""")
YC_HEAD_U = block(0, 12, """
.......HH.......
......HHHH......
.....HHHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
...HHHHHHHHHH...
E..HHHHHHHHHH..E
EEEHHHHHHHHHHEEE
.EEHHHHHHHHHHEE.
...HHHHHHHHHH...
..CCHHHHHHHHCC..
.CCCccccccccCCC.
.gCCccccccccCCg.
..CCccccccccCC..
..cccccccccccc..
...cccccccccc...""")
YC_HEAD_L = block(0, 12, """
......HH........
.....HHHH.......
....HHHHHH......
...HHHHHHHH.....
..HHHHHHHHHH....
..HgggggHHHH..E.
..HgkgggHHHHEEEE
..HgkgggHHHHEEE.
..HgggggHHHHEE..
...HHggHHHHH....
....HwwHHHHH....
...ccwwCCcccc...
...ccwcCCcccc...
...ccccggcccc...
...cccccccccc...
....cccccccc....""")
spec("yoda_c", "Juan", "npc_3", "gym_leaders/juan.png",
     "YODA (C): hood up, ears out of the hood, vanilla proportions.",
     "Batch 3 C. Hypothesis: the hood is the Jedi silhouette and frames the green face. boy_1 body as regions, hood (H) as its own volume over the face.",
     materials={"g": "skin-b", "E": "b", "H": "c", "c": "c!", "C": "c!", "w": "w/c"}, legend={"k": 15},
     accept={"hair_rows": "a hood, not hair", "skin_tones": "green hide uses ramp B", "head_w": "16 wide ear to ear",
             "eye_row": "the face sits low inside the hood"},
     base="boy_1.png", remap={"s": "g", "a": "c", "k": "c", "b": "g", "c": "H"},
     patches={"down": [YC_HEAD_D], "up": [YC_HEAD_U], "left": [YC_HEAD_L]})

# ====================================================================== IG-88
# A: top-down redraw. The top of the head cylinder is a lit disc (T) you look down on, then the
# rim, the sensor band, the cylinder side; shoulders are an ellipse (S) wider than the chest;
# the torso is foreshortened; 21 rows. Hypothesis: the missing perspective was the visible top
# of the head and the shoulder ellipse.
IGA = {
    "down": EMPTY[:10] + rows16(
        "......TTTT......",  # 10 top disc
        ".....TTTTTT.....",  # 11
        ".....TTTTTT.....",  # 12
        ".....dpWWpd.....",  # 13 sensor band on the rim
        ".....dddddd.....",  # 14
        ".....cccccc.....",  # 15 cylinder side
        ".....cdccdc.....",  # 16 slits
        ".....cdccdc.....",  # 17
        ".....cccccc.....",  # 18
        "......dddd......",  # 19 neck
        "..SSSSSSSSSSSS..",  # 20 shoulder ellipse
        ".cc.cccccccc.cc.",  # 21 arms, chest
        ".dd.cceeeecc.dd.",  # 22
        ".dd.cceeeecc.dd.",  # 23
        ".cc..cccccc..cc.",  # 24
        ".dd..dddddd..dd.",  # 25 hands, hip
        ".....cc..cc.....",  # 26
        ".....cc..cc.....",  # 27
        ".....dd..dd.....",  # 28
        ".....cc..cc.....",  # 29
        "....ddd..ddd....",  # 30
        "................"),
    "left": EMPTY[:10] + rows16(
        "......TTTT......",
        ".....TTTTTT.....",
        ".....TTTTTT.....",
        ".....dpWddd.....",
        ".....dddddd.....",
        ".....cccccc.....",
        ".....cdccdc.....",
        ".....cdccdc.....",
        ".....cccccc.....",
        "......dddd......",
        "....SSSSSSSS....",
        "....cccccccc....",
        "...ddcccccc.....",
        "...ddcccccc.....",
        "...cc.cccccc....",
        "...dd.dddddd....",
        "......cccc......",
        "......cccc......",
        "......dddd......",
        "......cccc......",
        ".....ddddd......",
        "................"),
}
IGA["up"] = [r.replace("p", "d").replace("W", "d").replace("e", "c") for r in IGA["down"]]
IGA["up"][16] = IGA["up"][17] = ".....cccccc....."
IG_MATS = {"c": "c", "T": "c", "S": "c", "d": "a", "e": "a"}
IG_ACCEPT = {"head_w": "6 px cylinder head by design", "eye_row": "no eyes; a sensor band", "hair_rows": "no hair; the lit top of the cylinder",
             "skin_tones": "a droid has no skin", "orphans": "machined surfaces; the only specks are the sensor lights",
             "step_change": "thin limbs change few pixels"}
spec("ig88_a", "Noland", "npc_4", "frontier_brains/noland.png",
     "IG-88 (A): top-down redraw, lit top of the head cylinder, shoulder ellipse, 21 rows.",
     "Batch 3 A. Hypothesis: perspective = the visible top of the head (T) and the shoulder ellipse (S); torso foreshortened to vanilla's 6 rows.",
     materials=IG_MATS, legend={"p": 9, "W": 14}, accept={**IG_ACCEPT, "height": "21 rows (vanilla p95)"},
     frames=IGA, steps=auto_steps(IGA, 26, 8))

# B: vanilla man proportions. man_1's body as regions (shirt -> plating, trousers -> legs), a
# droid head the size of a vanilla head in place of hair+face. Hypothesis: use a vanilla body
# wholesale; only the head says "droid".
IGB_HEAD_D = block(0, 11, """
......TTTT......
.....TTTTTT.....
....TTTTTTTT....
....ddpWWpdd....
....dddddddd....
....cccccccc....
....ccdccdcc....
....ccdccdcc....
.....cccccc.....
......dddd......""")
IGB_HEAD_U = block(0, 11, """
......TTTT......
.....TTTTTT.....
....TTTTTTTT....
....dddddddd....
....dddddddd....
....cccccccc....
....cccccccc....
....cccccccc....
.....cccccc.....
......dddd......""")
IGB_HEAD_L = block(0, 11, """
......TTTT......
.....TTTTTT.....
....TTTTTTTT....
....dpWddddd....
....dddddddd....
....cccccccc....
....cdccdccc....
....cdccdccc....
.....cccccc.....
......dddd......""")
spec("ig88_b", "Noland", "npc_4", "frontier_brains/noland.png",
     "IG-88 (B): vanilla man body, droid head the size of a vanilla head.",
     "Batch 3 B. Hypothesis: a vanilla body (man_1 as regions: shirt -> plating c, sleeves/cuffs -> joints a, trousers -> legs) carries the style; only the head is new.",
     materials={**IG_MATS, "P": "c"}, legend={"p": 9, "W": 14},
     accept={k: v for k, v in IG_ACCEPT.items() if k != "step_change"} | {"head_w": "8 px cylinder head by design"},
     base="man_1.png", remap={"s": "c", "w": "c", "a": "d", "b": "c", "c": "d"},
     patches={"down": [IGB_HEAD_D], "up": [IGB_HEAD_U], "left": [IGB_HEAD_L]})

# C: A's drawing in gunmetal (chassis on the steel-blue ramp, joints and band in grey), head two
# rows taller. Hypothesis: the light grey is why it reads as a toy; IG-88 is dark.
IGC = {k: [r.replace("c", "x").replace("d", "c").replace("x", "d") for r in v] for k, v in IGA.items()}
for k in IGC:
    IGC[k] = IGC[k][:8] + IGC[k][10:13] + IGC[k][10:13] + IGC[k][13:]  # repeat the disc rows: taller head
    IGC[k] = IGC[k][:32]
spec("ig88_c", "Noland", "npc_4", "frontier_brains/noland.png",
     "IG-88 (C): A in gunmetal (steel-blue chassis, grey joints), taller head.",
     "Batch 3 C. Hypothesis: colour. Same regions as A with the ramps swapped and a taller cylinder; 23 rows.",
     materials={"c": "c", "T": "a", "S": "a", "d": "a", "e": "c"}, legend={"p": 9, "W": 14},
     accept={**IG_ACCEPT, "height": "23 rows: IG-88 towers over people"},
     frames=IGC, steps=auto_steps(IGC, 26, 8))

# ====================================================================== DEXTER
# A: v3 -- copied unchanged.
shutil.copy("art/dexter.yaml", "art/dexter_a.yaml")

# B: head wider than tall with jowls (j) under a wide mouth, crest as a dark fin, wide-set eyes;
# fat_man's body; the lower arms folded across the apron as two forearms (L, R) meeting in the
# middle, the upper pair fat_man's own. Hypothesis: jowls + folded forearms are the Besalisk cues.
DB_HEAD_D = block(0, 11, """
.......rr.......
....hhhrrhhh....
..hhhhhhhhhhhh..
.hhhhhhhhhhhhhh.
.hhkhhhhhhhhkhh.
.hhkhhhhhhhhkhh.
hhhhMMMMMMMMhhhh
hjjjjjjjjjjjjjjh
.jjjjjjjjjjjjjj.
..jjjjjjjjjjjj..""")
DB_HEAD_U = block(0, 11, """
.......rr.......
....hhhrrhhh....
..hhhhhrrhhhhh..
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
hhhhhhhhhhhhhhhh
hhhhhhhhhhhhhhhh
.hhhhhhhhhhhhhh.
..hhhhhhhhhhhh..""")
DB_HEAD_L = block(0, 11, """
.......rr.......
.....hhhrrh.....
...hhhhhhhrhh...
..hhhhhhhhhhhh..
..hkhhhhhhhhhhh.
..hkhhhhhhhhhhh.
.MMMMMMMhhhhhhhh
.jjjjjjjjhhhhhhh
..jjjjjjjhhhhhh.
...jjjjjjhhhhh..""")
DB_ARMS_D = block(1, 24, """
hLLLLLLRRRRRRh
hLLLLLLRRRRRRh""")
DB_ARMS_L = block(2, 24, """
LLLLLLLLhh
LLLLLLLLhh""")
DB_MATS = {"h": "skin-a@", "j": "s@", "L": "a", "R": "a", "w": "w/a!", "b": "c!"}
DB_ACCEPT = {"skin_tones": "Besalisk hide uses ramp A, not the human skin ramp", "eye_row": "small eyes high on a wide hairless head",
             "hair_rows": "no hair: a short crest", "step_change": "the folded arms and apron hang still; the bob, hem and feet move"}
spec("dexter_b", "Brandon", "npc_3", "frontier_brains/brandon.png",
     "DEXTER (B): wide jowled head, crest fin, forearms folded across the apron.",
     "Batch 3 B. Hypothesis: jowls under a wide mouth and two folded forearms (L, R as separate volumes) are the Besalisk cues; fat_man body.",
     materials=DB_MATS, legend={"k": 15, "M": 7, "r": 7}, accept=DB_ACCEPT,
     base="fat_man.png", remap={"s": "h", "b": "w", "c": "b", "a": "b"},
     patches={"down": [DB_HEAD_D, DB_ARMS_D], "up": [DB_HEAD_U], "left": [DB_HEAD_L, DB_ARMS_L]})

# C: B's head in warm tan (NPC_2's brown ramp lit like a face), mouth open (black), long apron
# to the shins, bare legs, upper arms raised. Hypothesis: colour (Dexter is tan, not grey) and a
# long apron silhouette.
DC_ARMS = [block(0, 19, "U.\nUU\nUU\n.U"), block(14, 19, ".U\nUU\nUU\nU.")]
DC_HEAD_D = block(0, 11, DB_HEAD_D["rows"].replace("M", "K"))
DC_HEAD_L = block(0, 11, DB_HEAD_L["rows"].replace("M", "K"))
DC_LEGS_D = block(0, 27, """
.wwwwwwwwwwwwww.
..hhhhhhhhhhhh..
..hhhhh..hhhhh..
...kkk....kkk...""")
DC_LEGS_L = block(0, 27, """
..wwwwwwwwwww...
...hhhhhhhhh....
....hhh.hhh.....
.....kk..kk.....""")
spec("dexter_c", "Brandon", "npc_1", "frontier_brains/brandon.png",
     "DEXTER (C): olive-tan hide, open mouth, long apron, bare legs, upper arms raised.",
     "Batch 3 C. Hypothesis: colour (olive-tan on NPC_1's ramp C lit like a face; NPC_2's brown was too dark) and a long-apron silhouette with four arms visible.",
     materials={"h": "skin-c", "j": "skin-c", "U": "c", "L": "c", "R": "c", "w": "w/c!", "b": "c!"}, legend={"k": 15, "K": 15, "r": 13},
     accept={**DB_ACCEPT, "skin_tones": "Besalisk hide uses ramp C (tan), not the human skin ramp", "height": "22 rows: head sits higher with the raised arms"},
     base="fat_man.png", remap={"s": "h", "b": "w", "c": "w", "a": "w"},
     patches={"down": [DC_HEAD_D, DB_ARMS_D, *DC_ARMS, DC_LEGS_D], "up": [DB_HEAD_U, *DC_ARMS, DC_LEGS_D], "left": [DC_HEAD_L, DB_ARMS_L, DC_ARMS[0], DC_LEGS_L]})
print("ok")

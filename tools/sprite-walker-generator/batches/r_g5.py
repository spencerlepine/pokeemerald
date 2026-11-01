"""Group 5 (worker N=5), B style: each vanilla sheet the row replaces is the body, used as material
regions; heads and costume cues are new. Body edits that must follow the step frames' own arm and
leg positions are computed per frame from the base regions (body_edit) and stored as one
full-frame patch ('_' = keep) per frame, so the YAML stays plain base + patches.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_g5.py [name ...]
"""
import sys

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
import yaml  # noqa: E402
from helpers import P, block, spec  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.shade import regions_of  # noqa: E402
from walker_sprite.spec import KITS, game_dir  # noqa: E402

import os  # noqa: E402
ONLY = set(sys.argv[1:])
DEBUG = {} if os.environ.get("DBG") else None
BOB = {"down": 0, "up": 0, "left": 0, "down_a": 1, "down_b": 1, "up_a": 1, "up_b": 1, "left_a": 1, "left_b": 1}


def base_regions(base, remap):
    frs, _ = read_frames(game_dir() / (P + base))
    order = KITS["person16x32"]["order"]
    return {n: [[(remap or {}).get(c, c) for c in row] for row in regions_of(f)] for n, f in zip(order, frs)}


def apply(grid, patches):
    for p in patches:
        for dy, ln in enumerate(p["rows"].split("\n")):
            for dx, ch in enumerate(ln):
                if ch != "_":
                    grid[p["y"] + dy][p["x"] + dx] = ch


def sw(name, *a, body_edit=None, extra=None, **k):
    """spec() plus per-frame edits. body_edit(frame, x, y, ch, grid) -> new letter or None, run on
    the base+remap+stand/step patches grid (y already includes the step bob via BOB if used).
    extra: {frame: [patches]} appended after the generated ones."""
    if ONLY and name not in ONLY:
        return
    spec(name, *a, **k)
    if not (body_edit or extra):
        return
    path = f"art/{name}.yaml"
    d = yaml.safe_load(open(path))
    kit = d["kit"]
    regs = base_regions(k["base"], k.get("remap"))
    for fn in KITS[kit]["order"]:
        f = d["frames"].setdefault(fn, {"patches": []})
        pts = f.setdefault("patches", [])
        pts.extend((extra or {}).get(fn, []))
        if not body_edit:
            continue
        g = [row[:] for row in regs[fn]]
        apply(g, pts)
        out, changed = [], False
        for y in range(32):
            r = ""
            for x in range(16):
                n = body_edit(fn, x, y, g[y][x], g)
                if n is not None and n != g[y][x]:
                    r += n
                    changed = True
                else:
                    r += "_"
            out.append(r)
        if DEBUG is not None:
            for y in range(32):
                DEBUG.setdefault(fn, [""] * 32)[y] = "".join(out[y][x] if out[y][x] != "_" else g[y][x] for x in range(16))
        if changed:
            pts.append({"x": 0, "y": 0, "rows": "\n".join(out)})
    open(path, "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


def shift(b, dy):
    return {**b, "y": b["y"] + dy}


def extent(g, y):
    xs = [x for x in range(16) if g[y][x] != "."]
    return (min(xs), max(xs)) if xs else (None, None)


# ====================================================================== OBI-WAN (replaces Wallace)
# Old Ben: white hair and a full white beard (white edged in ramp a's brown), Wallace's caped
# jacket repainted per frame as the dark brown Jedi robe R (ramp c) over a cream tunic V (skin
# ramp) crossed at the collar, a leather belt Y (ramp a), tan trousers, brown boots.
OB_HEAD_D = block(0, 10, """
................
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHssssssssHHH.
.HHssssssssssHH.
.HHssskssksssHH.
.HHssskssksssHH.
..HsBssssssBsH..
...sBBBqqBBBs...
....BBBBBBBB....
_____qBBBBq_____
______qBBq______""")
OB_HEAD_U = block(0, 10, """
................
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.sHHHHHHHHHHHHs.
..sHHHHHHHHHHs..
...RRRRRRRRRR...""")
OB_HEAD_L = block(0, 10, """
................
................
......HHHHH.....
....HHHHHHHHH...
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..ssssHHHHHHHH..
.sssssHHHHHHH...
.sksssssHHHHHH..
.sksssssHHHHH...
.BsssssHHHHH....
.BBqssssHHH.....
..BBBBsss_______
..qBBq__________
...qq___________""")


def ob_edit(fn, x, y, ch, g):
    b = BOB[fn]
    if ch in ".kHBY" or y < 22 + b:
        return None
    lo, hi = extent(g, y)
    yy = y - b
    if yy >= 28:                          # legs
        return "T" if yy == 28 and ch != "D" else "D"
    if fn.startswith("left"):
        if ch == "s" and yy <= 25:
            return "s"
        if yy == 25:
            return "Y"
        if x <= lo + 1 and yy >= 23:
            return "V"
        return "T" if ch == "s" else "R"
    if ch == "s" and (x <= lo + 2 or x >= hi - 2):
        return "s"                        # hands
    if fn.startswith("up"):
        return "R"
    cx = (lo + hi) / 2
    half = {22: 0.5, 23: 1.5, 24: 2.0, 25: 2.5, 26: 2.5, 27: 2.5}[yy]
    if abs(x + 0.5 - cx - 0.5) <= half:
        return "Y" if yy == 25 else "V"
    return "R"


sw("wallace", "Wallace", "npc_3", "wallace.png",
   "OBI-WAN KENOBI: brown Jedi robe, cream tunic, white hair and beard (replaces Wallace).",
   "Group 5, B style: Wallace's caped jacket repainted as the brown Jedi robe over a cream crossed tunic and leather belt, new white hair and full beard (old Ben).",
   materials={"H": "a", "B": "w/a", "R": "c", "V": "s", "Y": "c", "T": "s", "D": "c"}, legend={"k": 15, "q": 6},
   accept={},
   base="wallace.png", remap={"a": "R", "w": "V", "b": "T", "c": "D"},
   patches={"down": [OB_HEAD_D], "up": [OB_HEAD_U], "left": [OB_HEAD_L]},
   body_edit=ob_edit)


# ====================================================================== LEIA (replaces Steven)
# ANH Leia: dark brown centre-parted hair (H, ramp c) with the two side buns (N, round c@), a
# floor-length white gown (G, white edged in ramp a) over Steven's own suit, arms and walk, and
# the silver belt (Y, ramp a).
LE_HEAD_D = block(0, 9, """
................
................
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
NNHHssssssssHHNN
NNNHssssssssHNNN
NNNssskssksssNNN
NNNssskssksssNNN
.NN.ssssssss.NN.""")
LE_HEAD_U = block(0, 9, """
................
................
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
NNHHHHHHHHHHHHNN
NNNHHHHHHHHHHNNN
NNNHHHHHHHHHHNNN
NNNHHHHHHHHHHNNN
.NN.HHHHHHHH.NN.
....GGGGGGGG....""")
LE_HEAD_L = block(0, 9, """
................
................
................
......HHHHH.....
....HHHHHHHHH...
...HHHHHHHHHHH..
..HHHHHHHHHHHHH.
..sssHHNNNNHHHH.
.ssssHNNNNNNHHH.
.skssHNNNNNNHHH.
.skssHNNNNNNHH..
..sssHHNNNNHH...
...sssHHHHH.....""")


def le_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch in ".kHN" and yy < 21 or yy < 21:
        return None
    if ch == ".":
        return None
    lo, hi = extent(g, y)
    if fn.startswith("left"):
        if ch == "s" and 23 <= yy <= 28 and x >= lo + 1:
            return "s"
        if yy <= 22:
            return "s" if ch == "s" and yy == 21 else "G"
    elif ch == "s" and 23 <= yy <= 28 and (x <= lo + 2 or x >= hi - 2):
        return "s"
    elif 22 <= yy <= 26 and (x <= lo + 1 or x >= hi - 1):
        return "L"                         # sleeves
    if yy == 25:
        return "Y"
    if not fn.startswith("left"):
        if 22 <= yy <= 24 and (x == lo + 2 or x == hi - 2):
            return "q"                     # sleeve seams
        if fn.startswith("down") and yy in (27, 28) and x == (lo + hi) // 2:
            return "q"                     # centre fold of the skirt
        if fn.startswith("up") and yy == 22 and lo + 3 <= x <= hi - 3:
            return "q"                     # hood folded at the back of the neck
    return "G"


sw("steven", "Steven", "npc_3", "steven.png",
   "LEIA ORGANA: white gown, silver belt, side-bun hair (replaces Steven).",
   "Group 5, B style: Steven's suit, arms and walk repainted as Leia's floor-length white gown with a silver belt, new centre-parted dark hair with the two round side buns.",
   materials={"H": "c", "N": "c@", "G": "w/a", "L": "w/a", "Y": "a"}, legend={"k": 15, "q": 6},
   accept={},
   base="steven.png", remap={"c": "H"},
   patches={"down": [LE_HEAD_D], "up": [LE_HEAD_U], "left": [LE_HEAD_L]},
   body_edit=le_edit)


# ====================================================================== JABBA (replaces Archie)
# Drawn whole over Archie's frames (a Hutt has no human part): a pear-shaped olive slug (head H
# round c@, body J, small arms A) with a tan belly (b, skin ramp), wide black mouth line, orange
# slit eyes, sitting on a blue-grey repulsor sled (S top deck, T front skirt) with red running
# lights; step frames bob the sled and alternate the repulsor glow under it.
JA_D = block(0, 10, """
................
................
................
.....HHHHHH.....
...HHHWHHHHHH...
..HHHHHHHHHHHH..
.HHHokHHHHkoHHH.
.HHHHHHHHHHHHHH.
.HHMMMMMMMMMMHH.
..HHHHHHHHHHHH..
.AJJJbhhhhbJJJA.
AAJJbbbbbbbbJJAA
.JJJffffffffJJJ.
JJJJbbbbbbbbJJJJ
JJJJbbbbbbbbJJJJ
JJJJJffffffJJJJJ
uuJJJJJJJJJJJJLL
vvvvvvvvvvvvvLLv
TTTTTTTTTTTTTTTT
TrTTTTTTTTTTTTrT
.TTTTTTTTTTTTTT.""")
JA_U = block(0, 10, """
................
................
................
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
.AHHHHHHHHHHHHA.
AAHHHHHHHHHHHHAA
.HHHHHHHHHHHHHH.
HHHHHHHHHHHHHHHH
HHHHHHHHHHHHHHHH
HHHHHHHHHHHHHHHH
uuHHHHHHHHHHHHuu
vvvvvvvvLLLLLLvv
TTTTTTTTTTTTTTTT
TrTTTTTTTTTTTTrT
.TTTTTTTTTTTTTT.""")
JA_L = block(0, 10, """
................
................
................
....HHHHHH......
..HHHWHHHHHH....
.HHHHHHHHHHHH...
HokHHHHHHHHHH...
HHHHHHHHHHHHH...
MMMMMHHHHHHHH...
.HHHHHHHHHHHH...
..hhbAAHHHHHHH..
..bbbbAAHHHHHH..
.ffffffHHHHHHH..
.bbbbbbHHHHHHHH.
.bbbbbbHHHHHHHH.
..ffffHHHHHHHHLL
uuuuuHHHHHHHHHLL
vvvvvvvvvvvvvLLv
TTTTTTTTTTTTTTTT
TrTTTTTTTTTTTTTT
.TTTTTTTTTTTTTT.""")
JA_GLOW = {k: block(2, 31, "gg__________" if k.endswith("a") else "__________gg")
           for k in ("down_a", "down_b", "up_a", "up_b", "left_a", "left_b")}
JA_EXTRA = {k: [v] for k, v in JA_GLOW.items()}
JA_EXTRA["down_a"].append(block(0, 19, "_A\nAA\n_A\n_."))
JA_EXTRA["down_b"].append(block(14, 19, "A_\nAA\nA_\n._"))
sw("archie", "Archie", "npc_1", "team_aqua/archie.png",
   "JABBA THE HUTT on his repulsor sled (replaces Archie).",
   "Group 5, B style (alien: drawn whole over Archie's frames): olive Hutt slug with a tan belly, wide mouth, orange slit eyes and stubby arms, sitting on a blue-grey repulsor sled with red running lights; the sled bobs and its glow alternates as he moves.",
   materials={"H": "c@", "J": "c", "A": "c", "L": "c", "b": "s@", "S": "b!", "T": "b"},
   legend={"k": 15, "o": 3, "M": 7, "r": 6, "g": 8, "W": 14, "f": 3, "h": 1, "u": 8, "v": 9},
   accept={"hair_rows": "a Hutt: no hair", "eye_row": "slit eyes in a slug head", "step_change": "he rides a hovering sled: no legs, the sled bobs and the glow alternates",
           "height": "the sled adds rows", "skin_tones": "Hutt hide is ramp C; the belly uses the skin ramp"},
   base="team_aqua/archie.png",
   patches={"down": [JA_D], "up": [JA_U], "left": [JA_L]}, extra=JA_EXTRA)


# ====================================================================== GARDULLA (replaces Lucy)
# Drawn whole over Lucy's frames: a taller, slimmer brown Hutt (head H round, body J, arms A, tail
# L, all ramp c on NPC_2) with a tan belly (b), a gold headband and necklace with red gems
# (Y ramp a, r), gold bracelets; she slithers: the tail swings side to side in the step frames.
GA_D = block(0, 10, """
................
................
.....HHHHHH.....
...HHHWHHHHHH...
..HYYYYRrYYYYH..
.HHHHHHHHHHHHHH.
.HHHokHHHHkoHHH.
.HHHHHHHHHHHHHH.
.HHHMMMMMMMMHHH.
..HHHHHHHHHHHH..
.AJYYYYRrYYYYJA.
.AJJJbhhhhbJJJA.
AAJJbbbbbbbbJJAA
.JJJffffffffJJJ.
.JJJbbbbbbbbJJJ.
JJJJbbbbbbbbJJJJ
JJJJJffffffJJJJJ
JJJJJJJJJJJJJJJJ
LJJJJJJJJJJJJJJ.
LLJJJJJJJJJJJJ..
.LLLJJJJJJJJJ...""")
GA_U = block(0, 10, """
................
................
.....HHHHHH.....
...HHHHHHHHHH...
..HYYYYYYYYYYH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
.AHYYYYYYYYYYHA.
.AHHHHHHHHHHHHA.
AAHHHHHHHHHHHHAA
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
HHHHHHHHHHHHHHHH
HHHHHHHHHHHHHHHH
HHHHHHLLLLHHHHHH
.HHHHLLLLLLHHHH.
..HHHHLLLLHHHH..
.......LL.......""")
GA_L = block(0, 10, """
................
................
....HHHHHH......
..HHHWHHHHHH....
.YYYYYYYrYYHH...
HHHHHHHHHHHHH...
HokHHHHHHHHHH...
HHHHHHHHHHHHH...
MMMMHHHHHHHHH...
.HHHHHHHHHHHH...
..YYrYYAHHHHHH..
..hhbYAAHHHHHH..
.bbbbbAAHHHHHH..
.ffffffHHHHHHH..
.bbbbbbHHHHHHHH.
.bbbbbbHHHHHHHH.
..ffffHHHHHHHHH.
..HHHHHHHHHHHHHH
...HHHHHHHHHLLLL
....HHHHHHHLLLL.
.....HHHHH......""")
GA_EXTRA = {
    "down_a": [block(0, 29, "LJJJJJJJJJJJJJJ.\nLLJJJJJJJJJJJJ..\n.LLLJJJJJJJJJ...")],
    "down_b": [block(0, 29, ".JJJJJJJJJJJJJJL\n..JJJJJJJJJJJJLL\n...JJJJJJJJJLLL.")],
    "up_a": [block(0, 29, ".HHHHHLLLLHHHHH.\n..HHHLLLLHHHHH..\n.....LL.........")],
    "up_b": [block(0, 29, ".HHHHHLLLLHHHHH.\n..HHHHHLLLLHHH..\n.........LL.....")],
    "left_a": [block(0, 29, "..HHHHHHHHHHHHHH\n...HHHHHHHHHHLLL\n....HHHHHHHHLLLL")],
    "left_b": [block(0, 29, "..HHHHHHHHHHHLLL\n...HHHHHHHHHLLL.\n....HHHHHHHH....")],
}
sw("lucy", "Lucy", "npc_2", "frontier_brains/lucy.png",
   "GARDULLA THE HUTT: brown Hutt matriarch in gold jewelry (replaces Lucy).",
   "Group 5, B style (alien: drawn whole over Lucy's frames): a tall brown Hutt with a tan belly, gold headband and necklace set with red gems, gold bracelets; the tail swings as she slithers.",
   materials={"H": "c@", "J": "c", "A": "c", "L": "c", "b": "s@", "Y": "a"},
   legend={"k": 15, "o": 6, "M": 10, "r": 9, "R": 8, "W": 14, "f": 3, "h": 1},
   accept={"hair_rows": "a Hutt: no hair, a gold headband", "eye_row": "slit eyes in a slug head", "step_change": "a Hutt slithers: the body bobs and the tail swings, no legs",
           "skin_tones": "Hutt hide is ramp C; the belly uses the skin ramp"},
   base="frontier_brains/lucy.png",
   patches={"down": [GA_D], "up": [GA_U], "left": [GA_L]}, extra=GA_EXTRA)


# ====================================================================== WATTO (replaces Wattson)
# Toydarian, drawn whole over Wattson's stand frames: blue-grey head (H, ramp a lit like a face)
# with a long trunk nose (N), white tusks, a stubble tuft; pale fluttering wings (W, white edged in
# grey) at the shoulders, round blue belly (B), tan vest (V, skin ramp), magenta-brown belt
# pouches (Y, ramp b), thin legs and grey feet, hovering just off the ground.
WA_D = block(0, 10, """
................
................
................
.......hh.......
.....HHHHHH.....
...HHHHHHHHHH...
.WWHHHHHHHHHHWW.
WWWHHkHHHHkHHWWW
WWWHHkHHHHkHHWWW
WWWHHHHnmHHHHWWW
.WWHHtHnmHtHHWW.
..WWHHHnmHHHWW..
...VVVVnmVVVV...
..AVVVBnmBVVVA..
.AAVVBBBBBBVVAA.
.AA.VBBBBBBV.AA.
....VBBBBBBV....
....YYYYYYYY....
....YYL..LYY....
.....LL..LL.....
....FFF..FFF....""")
WA_U = block(0, 10, """
................
................
................
.......hh.......
.....HHHHHH.....
...HHHHHHHHHH...
.WWHHHHHHHHHHWW.
WWWWHHHHHHHHWWWW
WWWWWHHHHHHWWWWW
WWWWWHHHHHHWWWWW
.WWWWHHHHHHWWWW.
..WWWHHHHHHWWW..
...VVWWVVWWVV...
..AVVVVVVVVVVA..
.AAVVVVVVVVVVAA.
.AA.VVVVVVVV.AA.
....VVVVVVVV....
....YYYYYYYY....
....YYL..LYY....
.....LL..LL.....
....FFF..FFF....""")
WA_L = block(0, 10, """
................
................
................
........hh......
......HHHHH.....
....HHHHHHHH....
...HHHHHHHHHWW..
..HkHHHHHHHWWWW.
..HkHHHHHHHWWWWW
nnHHHHHHHHHWWWWW
mmmtHHHHHHHWWWW.
m..HHHHHHH.WWW..
m...VVVVVVV.....
...ABBVVVVV.....
..AABBBVVVV.....
..AABBBVVVV.....
....BBBVVV......
....YYYYYY......
....YYL.LL......
.....LL.LL......
....FFF.FF......""")
sw("wattson", "Wattson", "npc_4", "gym_leaders/wattson.png",
   "WATTO: winged Toydarian junk dealer (replaces Wattson).",
   "Group 5, B style (alien: drawn whole over Wattson's stand frames): blue-grey Toydarian head with a long trunk nose, tusks and a stubble tuft, pale fluttering wings, round blue belly, tan vest and belt pouches, thin legs.",
   materials={"H": "skin-a@", "B": "skin-a@", "W": "c", "V": "s", "Y": "b", "F": "c"},
   legend={"k": 15, "t": 14, "h": 13, "n": 5, "m": 6, "A": 5, "L": 6},
   accept={"skin_tones": "Toydarian hide is the steel-blue ramp; the vest uses the skin ramp", "hair_rows": "bald with a stubble tuft",
           "eye_row": "small eyes over a long trunk nose", "head_w": "wings make the figure 16 wide"},
   base="gym_leaders/wattson.png",
   patches={"down": [WA_D], "up": [WA_U], "left": [WA_L]}, kit="person16x32_still")


# ====================================================================== CONTEST JUDGE (Cloud City)
# The judge's own head (grey hair G, moustache) over his body repainted as a Bespin noble's
# knee-length steel-blue robe (J, ramp a) with a magenta sash and brooch (T, ramp b), a tall white
# collar (C) standing up beside the jaw, and a magenta-lined cape at the back.
def cj_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch == ".":
        return None
    if ch == "a" and yy <= 21:
        return "G"
    if yy < 20:
        return None
    lo, hi = extent(g, y)
    if fn.startswith("down"):
        if (yy == 20 and x in (3, 12)) or (yy == 21 and x in (3, 4, 11, 12)):
            return "C"
    if fn.startswith("left") and yy in (20, 21) and ch in "kc" and x >= hi - 3:
        return "C"
    if yy <= 20:
        return None
    if ch == "c":
        return "V"
    if ch == "a":
        return "T" if yy <= 26 else "k"
    if ch == "b":
        if yy == 25 and lo + 2 <= x <= hi - 2 and not fn.startswith("up"):
            return "T"
        if fn.startswith("up") and 23 <= yy <= 27 and lo + 3 <= x <= hi - 3:
            return "K"
        return "J"
    if ch == "k" and fn.startswith("up") and yy <= 23:
        return "C"
    return None


sw("contest_judge", "ContestJudge", "npc_1", "contest_judge.png",
   "Showcase judge in formal Cloud City robes (replaces the Contest Judge).",
   "Group 5, B style: the judge's own head and walk, his suit repainted as a Bespin noble's sky-blue robe with a white shirt front, gold belt and buckle, a tall white collar and a blue cape panel at the back.",
   materials={"G": "c", "J": "b", "T": "c", "C": "w/b", "V": "w/b", "K": "b", "w": "w/a"}, legend={"k": 15},
   accept={},
   base="contest_judge.png", body_edit=cj_edit)


# ====================================================================== HOLONET RECEPTIONIST (Link)
# Her own bob haircut and walk; the maid headband becomes a blue comm headset band, the dress a
# sky-blue HoloNet uniform (U, ramp b) with a white collar and front panel (V, white edged blue),
# a pink holo-badge on the chest and a mic pickup by the cheek; olive-brown hair (H, ramp c).
def lr_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch == ".":
        return None
    lo, hi = extent(g, y)
    if yy <= 20:
        if ch == "b":
            return "H"
        if ch in "wa":
            return "E"
        return None
    if ch in "caw":
        if ch in "aw" and yy <= 23:
            return "V"
        if fn.startswith("down") and yy == 24 and x in (lo + 4, lo + 5):
            return "P" if x == lo + 4 else "Q"
        if not fn.startswith("up") and yy == 25 and lo + 2 <= x <= hi - 2:
            return "k"
        return "U"
    if ch == "b":
        return "k"
    return None


sw("link_receptionist", "LinkReceptionist", "npc_1", "link_receptionist.png",
   "HOLONET CLUB receptionist in a sky-blue uniform with a comm headset (replaces the Link Receptionist).",
   "Group 5, B style: her own bob and walk, the headband turned into a comm headset band, the dress into a sky-blue HoloNet uniform with a white collar, a rank plaque on the chest and a black belt.",
   materials={"H": "c", "U": "b", "V": "w/b"}, legend={"k": 15, "E": 10, "P": 6, "Q": 11},
   accept={},
   base="link_receptionist.png", body_edit=lr_edit)


# ====================================================================== BEAST MANIAC
# His own spiky black hair and walk; the goggles turn red (G, ramp b), the shirt becomes a
# yellow creature-print shirt (P, ramp a) with dark brown spots, brown trousers (T, ramp c), and
# a fang necklace on the open collar.
def mn_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch == ".":
        return None
    if yy <= 20:
        if ch == "a":
            return "G"
        if ch in "ck":
            return "H"
        if ch == "w" and fn.startswith("down") and x in (6, 9):
            return "k"
        if ch == "w" and fn.startswith("left") and x == 3:
            return "k"
        return None
    if fn.startswith("down") and yy == 21 and x in (6, 9) and ch == "s":
        return "W"
    if ch in "cw":
        if yy % 2 == 0 and (x + yy) % 4 == 0:
            return "q"
        return "P"
    if ch == "a":
        return "T"
    return None


sw("maniac", "Maniac", "npc_2", "maniac.png",
   "Beast maniac in a creature-print shirt and a fang necklace (replaces the Maniac).",
   "Group 5, B style: his own spiky hair and walk; red goggles, a yellow creature-print shirt with brown spots, a fang necklace, brown trousers.",
   materials={"G": "b", "H": "c", "P": "a", "T": "c"}, legend={"k": 15, "q": 7, "W": 14},
   accept={},
   base="maniac.png", body_edit=mn_edit)


# ====================================================================== FORCE ADEPT (Psychic M)
# A deep hood (O, steel-navy ramp a, shadowed inside I) replaces the hair, the face peering out;
# the bare arms become long robe sleeves (R) with only the hands showing, the vest a grey inner
# tunic (V, ramp c), a magenta sash knot (Y, ramp b) at the waist, grey trousers.
FA_HEAD_D = block(0, 10, """
................
......OOOO......
....OOOOOOOO....
...OOOOOOOOOO...
..OOOOOOOOOOOO..
..OOOIIIIIIOOO..
.OOOIssssssIOOO.
.OOIssssssssIOO.
.OOIssksskssIOO.
.OOIssksskssIOO.
.OOOIssssssIOOO.
..OOOOssssOOOO..
..OOOOOOOOOOOO..""")
FA_HEAD_U = block(0, 10, """
................
......OOOO......
....OOOOOOOO....
...OOOOOOOOOO...
..OOOOOOOOOOOO..
..OOOOOOOOOOOO..
.OOOOOOOOOOOOOO.
.OOOOOOOOOOOOOO.
.OOOOOOOOOOOOOO.
.OOOOOOOOOOOOOO.
..OOOOOOOOOOOO..
..OOOOOOOOOOOO..
...OOOOOOOOOO...""")
FA_HEAD_L = block(0, 10, """
................
.......OOOO.....
.....OOOOOOOO...
....OOOOOOOOOO..
...OOOOOOOOOOOO.
..OOIIOOOOOOOOO.
..OIssIOOOOOOOO.
.OIsssIOOOOOOOO.
..skssIOOOOOOOO.
..skssIOOOOOOOO.
..sssIOOOOOOOO..
...ssIOOOOOOOO..
...OOOOOOOOOO___""")


def fa_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch in ".OI" or yy < 22 + (1 if fn.startswith("left") else 0) and yy <= 22:
        return None
    lo, hi = extent(g, y)
    if yy >= 28:
        return "T" if ch in "sa" else None
    if ch == "s":
        if yy in (25, 26) and (x == lo or x == hi):
            return "s"
        if fn.startswith("left") and yy in (25, 26) and x <= lo + 2:
            return "s"
        return "R"
    if yy == 27 and fn.startswith("down") and x in (7, 8):
        return "W"
    if ch == "a":
        return "V"
    if ch == "b":
        return "Y" if (x + yy) % 2 else "Z"
    if ch == "k" and yy == 27 and fn.startswith("down") and x in (7, 8):
        return "W"
    return None


sw("psychic_m", "PsychicM", "npc_4", "psychic_m.png",
   "Force adept in a deep hooded robe (replaces the Psychic M).",
   "Group 5, B style: his own walk; a deep steel-navy hood with the face peering out replaces the hair, his bare arms become long robe sleeves, the vest a grey inner tunic with a magenta sash.",
   materials={"O": "a@", "R": "a", "V": "c", "T": "c"}, legend={"k": 15, "I": 7, "W": 14, "Y": 9, "Z": 8},
   accept={"hair_rows": "a deep hood instead of hair", "step_change": "long robe sleeves and the hood hang still; the bob, hem and feet move"},
   base="psychic_m.png",
   patches={"down": [FA_HEAD_D], "up": [FA_HEAD_U], "left": [FA_HEAD_L]}, body_edit=fa_edit)


# ====================================================================== SWOOP RACER M (Running Triathlete M)
# His own spiky hair (H, brown ramp c) and run cycle; racing goggles pushed up on the forehead
# (yellow lenses y, dark strap g), a red padded racing suit (J, ramp b) with a yellow racing
# stripe (S) and yellow sleeves (L, ramp a), brown gloves and suit legs, dark boots.
def sr_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch == ".":
        return None
    lo, hi = extent(g, y)
    head_end = 22 if fn.startswith("left") else 20
    if yy <= head_end:
        if ch == "a" or (ch == "k" and fn.startswith("left") and yy <= 20):
            gy = 17 if fn.startswith("up") else 16
            if yy == gy:
                if fn.startswith("down") and x in (4, 5, 10, 11):
                    return "y"
                if fn.startswith("left") and x <= lo + 2:
                    return "y"
                return "g"
            return "H"
        return None
    if ch == "a":
        return "S" if (not fn.startswith("left") and x in (7, 8) and yy <= 25) else "J"
    if ch == "s":
        if yy >= 27:
            return "P"
        if fn.startswith(("down", "up")) and yy in (24, 25) and (x == lo or x == hi):
            return "s"
        return "L"
    if ch == "c":
        return "K" if yy <= 26 else "k"
    if ch == "b":
        return "P" if yy <= 28 else "k"
    return None


sw("running_triathlete_m", "RunningTriathleteM", "npc_2", "running_triathlete_m.png",
   "Swoop racer (m) out training on foot: red racing suit, goggles up (replaces the Running Triathlete M).",
   "Group 5, B style: his own spiky hair and run cycle; racing goggles pushed up on the forehead, a red padded racing suit with a yellow stripe and sleeves, brown gloves, dark boots.",
   materials={"H": "c", "J": "b", "S": "a", "L": "a", "K": "c", "P": "c"}, legend={"k": 15, "y": 5, "g": 13},
   accept={},
   base="running_triathlete_m.png", body_edit=sr_edit)


# ====================================================================== VETERAN SPACER (Expert F)
# Her own grey bun and hunched walk; old flight goggles strapped over the hair (pale lenses y,
# dark strap g), her dress turned into a steel-blue spacer flight jacket and skirt (J, ramp a)
# with magenta patches and piping (T, ramp b), and a short walking cane (n) under her hands.
def ef_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    lo, hi = extent(g, y)
    if yy <= 18 and ch == "c":
        gy = 16
        if yy == gy:
            if fn.startswith("down") and x in (5, 6, 9, 10):
                return "y"
            if fn.startswith("left") and x <= lo + 2:
                return "y"
            return "g"
        return None
    if ch == "b" and yy >= 22:
        return "J"
    if ch == "a" and yy >= 22:
        return "T"
    return None


def ef_cane(fn):
    """Cane pixels for one frame: under the clasped hands (down), under the hands at the back (left, up)."""
    regs = base_regions("expert_f.png", None)[fn]
    b = BOB[fn]
    pts = []
    if fn.startswith("down"):
        x, top = 8, 27 + b
    else:
        ss = [(xx, yy) for yy in range(24 + b, 31) for xx in range(16) if regs[yy][xx] == "s"]
        if fn.startswith("up"):
            ss = [p for p in ss if p[0] >= 9]
        x = max(p[0] for p in ss)
        top = max(p[1] for p in ss if p[0] == x) + 1
    rows = "\n".join("n" for _ in range(top, 31))
    return [block(x, top, rows)]


sw("expert_f", "ExpertF", "npc_4", "expert_f.png",
   "Veteran spacer woman: old flight goggles, spacer jacket, walking cane (replaces the Expert F).",
   "Group 5, B style: her own grey bun and hunched walk; old flight goggles strapped over the hair, her dress turned into a steel-blue spacer jacket and skirt with magenta patches, a short walking cane under her hands.",
   materials={"J": "a", "T": "b"}, legend={"k": 15, "y": 5, "g": 13, "n": 4},
   accept={},
   base="expert_f.png", body_edit=ef_edit,
   extra={fn: ef_cane(fn) for fn in KITS["person16x32"]["order"]})


# ====================================================================== MARKET GIRL (Girl 3)
# Her own hair and bun (H, brown ramp c) with a red kerchief ribbon (R, ramp b); her dress
# becomes an off-white Tatooine wrap tunic (W, white edged brown) with an orange sash (S, ramp
# a) over a brown skirt (K); a woven basket (orange ramp a, hard tones) hangs from her hand.
def g3_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch == ".":
        return None
    if yy <= 14 and ch == "a":
        return "R"
    if ch == "c" and yy <= 22:
        return None
    if yy >= 22:
        if ch == "a":
            if yy >= 29:
                return "F"
            lo, hi = extent(g, y)
            return "S" if yy == 25 else "W"
        if ch == "b":
            return "K"
    return None


def g3_basket(fn):
    regs = base_regions("girl_3.png", None)[fn]
    b = BOB[fn]
    if fn.startswith("left"):
        ss = [(x, y) for y in range(24 + b, 28 + b) for x in range(16) if regs[y][x] == "s" and x <= 8]
    else:
        ss = [(x, y) for y in range(23 + b, 28 + b) for x in range(11, 16) if regs[y][x] == "s"]
    hy = max(p[1] for p in ss)
    hx = max(p[0] for p in ss if p[1] == hy) if not fn.startswith("left") else min(p[0] for p in ss if p[1] == hy)
    x0 = max(0, min(12, hx - 1))
    top = min(hy - 1, 26 + b)
    return [block(x0, top, "_oo_\no__o\nqpqp\nopop")]


sw("girl_3", "Girl3", "npc_2", "girl_3.png",
   "Market-town girl in Tatooine wraps carrying a woven basket (replaces Girl 3).",
   "Group 5, B style: her own hair and walk; a red kerchief ribbon, an off-white desert wrap tunic with an orange sash over a brown skirt, a woven basket hanging from her hand.",
   materials={"H": "c", "R": "b", "W": "w/c", "S": "a", "K": "c", "F": "c"}, legend={"k": 15, "o": 7, "p": 6, "q": 5},
   accept={},
   base="girl_3.png", remap={"c": "H"}, body_edit=g3_edit,
   extra={fn: g3_basket(fn) for fn in KITS["person16x32"]["order"]})


# ====================================================================== DESERT ELDER (Old Man)
# His own bushy brows, white moustache and beard under a brown desert hood (O, ramp c); his
# shirt becomes a sand-coloured poncho (P, white edged brown) with a red sash knot (S, ramp b),
# brown trousers (T), and a short walking stick (n) in his hand, no taller than his chest.
OM_HEAD_D = block(0, 10, """
................
......OOOO......
....OOOOOOOO....
...OOOOOOOOOO...
..OOOOOOOOOOOO..
..OOOssssssOOO..
.OOOssssssssOOO.
.OOssssssssssOO.
.OOssssssssssOO.
.OOsskksskkssOO.
.OOssswwwwsssOO.
..OOswwwwwwsOO..
.PPOOwwwwwwOOPP.""")
OM_HEAD_U = block(0, 10, """
................
......OOOO......
....OOOOOOOO....
...OOOOOOOOOO...
..OOOOOOOOOOOO..
..OOOOOOOOOOOO..
.OOOOOOOOOOOOOO.
.OOOOOOOOOOOOOO.
.OOOOOOOOOOOOOO.
.OOOOOOOOOOOOOO.
.OOOOOOOOOOOOOO.
..OOOOOOOOOOOO..
.PPOOOOOOOOOOPP.""")
OM_HEAD_L = block(0, 10, """
................
.......OOOO.....
.....OOOOOOOO...
....OOOOOOOOOO..
...OOOOOOOOOOOO.
..OOssOOOOOOOOO.
..ssssOOOOOOOOO.
.sssssOOOOOOOO..
.sssssOOOOOOOO..
.skkssOOOOOOO...
.wwssssOOOOOO...
.wwwwssOOOOO....
..wwwwOOOO______""")
OM_STICK = {"down": block(13, 23, "_s_\n_n_\n_n_\n_n_\n_n_\n_n_\n_n_"),
            "up": block(0, 23, "_s_\n_n_\n_n_\n_n_\n_n_\n_n_\n_n_"),
            "left": block(1, 23, "s\nn\nn\nn\nn\nn\nn")}


def om_edit(fn, x, y, ch, g):
    if y < 23 or ch in ".snO":
        return None
    if ch in "bw":
        return "P"
    if ch == "a":
        return "S" if y <= 26 and 6 <= x <= 9 and not fn.startswith("up") else "T"
    if ch == "c":
        return "k"
    return None


sw("old_man", "OldMan", "npc_2", "old_man.png",
   "Elderly desert man in a hood and poncho with a short walking stick (replaces the Old Man).",
   "Group 5, B style: his own bushy brows, white moustache and beard under a brown desert hood, his shirt turned into a sand-coloured poncho with a red sash knot, brown trousers, a short walking stick in hand.",
   materials={"O": "c", "P": "a", "S": "b", "T": "c", "w": "w/c"}, legend={"k": 15, "n": 12},
   accept={"hair_rows": "a desert hood instead of hair"},
   base="old_man.png",
   patches={"down": [OM_HEAD_D, OM_STICK["down"]], "up": [OM_HEAD_U, OM_STICK["up"]], "left": [OM_HEAD_L, OM_STICK["left"]]},
   body_edit=om_edit, kit="person16x32_still")


# ====================================================================== NABOO LADY (Woman 5)
# Her own long brown hair and walk; a gold Naboo crest headdress set with pearls (Y, ramp a; r)
# fans out above the hair, red beauty marks on the cheeks, her dress becomes a red Naboo gown
# (G, ramp b) with gold trim (from her collar and belt details) and a layered floor-length skirt.
NB_CREST_D = block(0, 9, """
......ouuo......
....ouuuuuuo....
...ovrvvvvrvo...""")
NB_CREST_U = block(0, 9, """
......ouuo......
....ouuuuuuo....
...ovvvvvvvvo...""")
NB_CREST_L = block(0, 9, """
.....ouuo.......
...ouuuuuuo.....
...rvvvrvvvo....""")


def nb_edit(fn, x, y, ch, g):
    b = BOB[fn]
    yy = y - b
    if ch == ".":
        return None
    if fn.startswith("down") and yy == 20 and x in (4, 11) and ch == "s":
        return "m"
    if ch == "c" and 13 <= yy <= 21 and (x * 5 + yy * 3) % 11 == 0 and 0 < x < 15 \
            and g[y][x - 1] == "c" and g[y][x + 1] == "c" and g[y - 1][x] == "c":
        return "h"                         # single-pixel hair strands
    if yy < 21:
        return None
    if ch == "b":
        return "G"
    if ch == "w":
        return "Y"
    if ch == "k" and yy >= 22:
        return "G"
    if ch == "a" or (ch == "s" and yy >= 27):
        return "L"
    return None


sw("woman_5", "Woman5", "npc_2", "woman_5.png",
   "Elegant Naboo noblewoman: gold crest headdress, red gown (replaces Woman 5).",
   "Group 5, B style: her own long hair and walk; a gold Naboo crest headdress set with pearls, red beauty marks on the cheeks, a red Naboo gown with gold trim and a layered floor-length skirt.",
   materials={"Y": "a", "G": "b", "L": "b"}, legend={"k": 15, "r": 14, "m": 9, "h": 11, "u": 5, "v": 6, "o": 7},
   accept={"height": "the Naboo crest headdress rises above the hair"},
   base="woman_5.png",
   patches={"down": [NB_CREST_D], "up": [NB_CREST_U], "left": [NB_CREST_L]}, body_edit=nb_edit)

if DEBUG:
    ks = [k for k in os.environ["DBG"].split(",")]
    for y in range(9, 31):
        print(f"{y:2d} " + "  ".join(DEBUG[k][y] for k in ks))
print("ok")

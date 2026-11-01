"""Recast group d2: redraw of the NEW walker sw_ewok (net:walker-ewok), the Ewok scout of the EWOK and
SHAMAN trainers. The first version (batches/r_rcd.py) sat on the 16x16 kit and the owner found it
"a little too squished": this one walks on the 16x32 kit, 19 rows tall (top on row 12), on Boy 1's
kid body as regions so the vanilla walk cycle and bob stay.

Layers per frame: Boy 1's body below the head (rows >= 23 at the frame's bob, renamed to fur and
leather), the spear behind, the new head over it, then the strap/pouch details.
Writes art/sw_ewok.yaml (overwrites the r_rcd.py version). Run from the tool folder:
python batches/r_rcd2.py
"""
import sys

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P, spec  # noqa: E402
from walker_sprite.shade import regions_of  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import game_dir  # noqa: E402

ORDER = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]
SWAY = {"down_a": -1, "down_b": 1, "up_a": 1, "up_b": -1}
BODY_Y = 23  # stand-frame row where Boy 1's body is kept; everything above is redrawn


def rows(text):
    return text.strip("\n").split("\n")


def top(f):
    return next(y for y, r in enumerate(f) if r.strip("."))


def overlay(g, block, x0, y0):
    for dy, ln in enumerate(block):
        for dx, ch in enumerate(ln):
            x, y = x0 + dx, y0 + dy
            if ch == "_" or not (0 <= x < 16 and 0 <= y < 32):
                continue
            g[y][x] = ch


def compose(path, classify, layers):
    """layers[frame or facing] = [(x, y, rows)] in stand coordinates, laid over in order at the
    frame's bob ('_' leaves what is under it, '.' clears)."""
    fr, _ = read_frames(game_dir() / (P + path), (16, 32))
    reg = {n: regions_of(f) for n, f in zip(ORDER, fr)}
    stand_top = {n: top(reg[n]) for n in ("down", "up", "left")}
    out = {}
    for name in ORDER:
        facing = name.split("_")[0]
        bob = top(reg[name]) - stand_top[facing]
        g = [["."] * 16 for _ in range(32)]
        for y, r in enumerate(reg[name]):
            for x, ch in enumerate(r):
                if ch != "." and y - bob >= BODY_Y:
                    g[y][x] = classify(ch, x, y - bob, facing, name)
        # the head and strap lean 1 px with the stepping body on the down/up step frames (as r_rca.py)
        dx = SWAY.get(name, 0)
        for i, (px, py, prow) in enumerate(layers.get(name, layers.get(facing, []))):
            overlay(g, rows(prow), px + (dx if i else 0), py + bob)
        out[name] = ["".join(r) for r in g]
    return out


# ====================================================================== EWOK scout (net:walker-ewok)
# NPC_2. The head is hand-toned (hard pixels), the body is Boy 1's regions shaded by the tool.
# Fur on ramp c (f light, g mid, d dark): round ears E poking through the hood, a face lit on the
# brow and cheekbones, darker under the hood rim. Big black eyes (k) with a white glint (W) on the
# lit side. Tan muzzle on the skin ramp (q light, M base, m shade) with a black nose (n). Ochre
# leather hood on ramp a (Y light crown, O mid, h dark rim, outline and stitched seams) framing the face and hanging
# in a pointed drape down the back, a red crown bead (r). A hide strap (A/y, ramp a dark/mid) across
# the chest to a leather belt (O/Y/h) with a tan pouch hanging at the hip (U, outline t). Spear: dark shaft p, red binding r, white
# stone tip W edged in skin outline t. Brown and hornless, unlike grey, bone-horned Chirpa (winona).
HEAD_D = """
__dd________dd__
_dfgd_hhhh_dgfd_
_dggdhOYYOhdggd_
__dhOOYYOrOOhd__
_hOOOYOOOOOOOOh_
_hOOhhhhhhhhOOh_
_hOhdggggggdhOh_
_hOgWkffffWkgOh_
_hhgkkgffgkkghh_
_hhggfqMMqfgghh_
__hdgMMnnMMgdh__
___hdgmMMmgdh___"""
HEAD_U = """
__dd________dd__
_dfgd_hhhh_dgfd_
_dggdhOYYOhdggd_
__dhOOYYOrOOhd__
_hOOYOOhhOOOOOh_
_hOOOOhOOhOOOOh_
_hOOOOhOOhOOOOh_
_hOOOOhOOhOOOOh_
_hhOOOhOOhOOOhh_
_dhhOOhOOhOOhhd_
_gdhhhOOOOhhhdg_
__dgdhhOOhhdgd__
_____hhhhhh_____"""
HEAD_L = """
______dd___dd___
_____dfgd_dfgd__
____hdggdhdggdh_
___hOOddOYOddOh_
__hOOOOYYOOOrOh_
__hOOOOOOhOOOOh_
_hhhhhOOOhOOOOh_
_dggghhOOhOOOOh_
_gWkfghOOhOOOOh_
qgkkgghOOhOOOh__
nMMggghOhhOOhh__
_MmgdhhhOOOhh___"""
SPEAR = """
t
W
W
r
p
p
p
p
p
p
p
p
p
p
p
p
p
p"""
STRAP_D = """
___yA___________
_____yA_________
_______yA_______
__hOOYOOOOAhh___
________hUUh____
_________tt_____"""
STRAP_U = """
__________Ay____
________Ay______
______Ay________
__hhAOOYOOOOh___"""
STRAP_L = """
______yA____
________yA__
___hOYOOOOh_
_______hUUh_
________tt__"""

EW_LAYERS = {
    "down": [(15, 12, SPEAR), (0, 12, HEAD_D), (0, 24, STRAP_D)],
    "up": [(0, 12, SPEAR), (0, 12, HEAD_U), (0, 24, STRAP_U)],
    "left": [(15, 12, SPEAR), (0, 12, HEAD_L), (0, 24, STRAP_L)],
}
# the spear arm swings with the step: the spear rides one row up or down with it
for st, sx in {"down": 15, "up": 0, "left": 15}.items():
    for step, dy in zip((st + "_a", st + "_b"), (-1, 1)):
        lay = list(EW_LAYERS[st])
        lay[0] = (sx, 12 + dy, SPEAR)
        EW_LAYERS[step] = lay


def ewok_cls(ch, x, y, facing, name):
    if ch == "a":
        return "T"          # Boy 1's shirt -> torso fur
    if ch == "k":
        return "D"          # shorts -> lower fur
    if ch == "b":
        return "D"          # shoes -> dark fur feet
    return "B"              # arms and legs -> fur limbs


EW = compose("boy_1.png", ewok_cls, EW_LAYERS)
spec("sw_ewok", "SwEwok", "npc_2", "boy_1.png",
     "NEW WALKER (net:walker-ewok): Ewok scout: brown multi-tone fur, ochre leather hood with round fur ears poking "
     "through, big glinting black eyes, tan muzzle, hide strap and pouch, a small stone-tipped spear (placeholder: Boy 1). "
     "Used by the EWOK and SHAMAN trainers.",
     "Recast group d2 (redraw of the 16x16 r_rcd.py version, rejected as too squished): 16x32 kit, 19 rows tall, "
     "shade mode on Boy 1's kid body as regions (shirt -> torso fur T, arms/legs -> fur B, shorts and shoes -> lower "
     "fur D). Hand-toned head: brown fur face lit on brow and cheeks, tan muzzle with a black nose, big eyes with white "
     "glints, ochre hood framing the face with a back drape and a red crown bead, round fur ears through it. "
     "Hide strap to a tan hip pouch; spear (dark shaft, red binding, white stone tip). Brown and hornless, unlike "
     "grey horn-hooded Chirpa (winona).",
     materials={"T": "c@", "B": "c", "D": "c"},
     legend={"k": 15, "W": 14, "n": 15, "f": 11, "g": 12, "d": 13, "Y": 5, "O": 6, "h": 7,
             "q": 1, "M": 2, "m": 3, "t": 4, "U": 2, "p": 7, "A": 7, "y": 6, "r": 9},
     accept={"skin_tones": "Ewok fur is the brown ramp; only the muzzle and pouch use the skin ramp",
             "hair_rows": "a leather hood over fur",
             "eye_row": "big Ewok eyes inside the fur face"},
     frames=EW)

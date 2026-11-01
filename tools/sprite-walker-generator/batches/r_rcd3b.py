"""Recast group d2, round 3 variant B: sw_ewok_b (net:walker-ewok), same figure as variant A
(batches/r_rcd3.py -> art/sw_ewok.yaml, NPC_2, left untouched) but on NPC_3 so the hood is the film's
burnt-orange rust (ramp c) and the face a grizzled grey (ramp a) instead of A's pink-tan hood and peach
face that read lion/monkey. The face is smaller (6 px wide) so the hood fills more, like the refs; the
body is dark (123 65 65 and black) under a dark 82 16 0 line at the cape hem so the orange hood stands
out over it. Same kit, Boy 1's walk, no spear. Writes art/sw_ewok_b.yaml.
Run from the tool folder: python batches/r_rcd3b.py
"""
import sys

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P, spec  # noqa: E402
from walker_sprite.shade import regions_of  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import game_dir  # noqa: E402

ORDER = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]


def rows(text):
    return text.strip("\n").split("\n")


def top(f):
    return next(y for y, r in enumerate(f) if r.strip("."))


def overlay(g, block, x0, y0):
    for dy, ln in enumerate(block):
        for dx, ch in enumerate(ln):
            x, y = x0 + dx, y0 + dy
            if ch != "_" and 0 <= x < 16 and 0 <= y < 32:
                g[y][x] = ch

SWAY = {"down_a": -1, "down_b": 1, "up_a": 1, "up_b": -1}
HEM = {"down_a": 1, "down_b": -1, "up_a": -1, "up_b": 1, "left_a": 1, "left_b": 1}
HEM_ROW = 13  # head-block row where the cape hem starts (stand row 25)
BODY_Y = 23  # stand-frame row where Boy 1's body is kept; everything above is the new head

# Hard letters: hood R/o/X,x = rust 11/12/13; cord C = 4 with beads W = 14 and H = 5; face g = 6 grey,
# L = 5 light speck, f = 2 / K = 1 skin-light flecks, B = 7 slate brow and lower ring shade, eyes e / nose n = 15, mouth m = 13; ear
# tufts u = 4 with a grey tip V = 6. Body fur (fur()): Z = 13, Q = 15, P = 4, Y = 3, V = 6.
HEAD_D = """
___Vu______uV___
___uxRRRRRRxu___
__xRRRRRRRRRRx__
_xRRoRRRRRRoRRx_
_xoCCHWCCCCCCox_
_xooxgKggLgxoox_
_xooxgBggBgxoox_
_xXoxBeffeBxoXx_
_xXoxBfnnfBxoXx_
_xXooxBmmBxooXx_
__xxooxBBxooxx__
___xRRoxxoRRx___
___xoRRRRRRox___
___xXooRRooXx___
___xxoxxxoxx____"""
HEAD_U = """
___Vu______uV___
___uxRRRRRRxu___
__xRRRRRRRRRRx__
_xRRRRRRRRRRRRx_
_xoCCCCCCHWCCox_
_xRRRRRRRRRRRRx_
_xoooRRRRRRooox_
_xXooooooooooXx_
_xXoRRRRRRRRoXx_
_xXooooRRooooXx_
_xXooRRRRRRoXXx_
__xoxooxxooxox__
___x_xx__xx_x___"""
HEAD_L = """
_____Vu___uV____
____uxRRRRRxu___
___xRRRRRRRRRx__
__xRRRRRRRRRRRx_
_xWHCCRRRRRRRox_
_xgKgxRRRRRRoox_
_xBggxoooooooXx_
_xegfxRRRRRRoXx_
nBffxoooRRooXXx_
mBBxoRRRRRoXXXx_
_xxxoRoooooXxx__
__xoRRRRRox_____
__xooooooox_____
__xXooRRox______
___xxoxxx_______"""

LAYERS = {"down": [(0, 12, HEAD_D)], "up": [(0, 12, HEAD_U)], "left": [(0, 12, HEAD_L)]}


def compose(path):
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
                    g[y][x] = "F"
        for (px, py, prow) in LAYERS[facing]:
            blk = rows(prow)
            overlay(g, blk[:HEM_ROW], px + SWAY.get(name, 0), py + bob)
            # the ragged cape hem swings against the step (the cloth lags the body)
            overlay(g, blk[HEM_ROW:], px + SWAY.get(name, 0) + HEM.get(name, 0), py + bob + HEM_ROW)
        out[name] = fur(g)
    return out


def fur(g):
    """Tone the leftover body pixels (F) as dark fur, distinct from the rust hood: rust-dark outline
    (Z = 82 16 0) high up, black (Q) low down and on the soles, base P = 123 65 65 (skin outline),
    sparse tan strands (Y = 222 148 115) and grey tips (V = 156 156 189) on the arm tops."""
    H, Wd = len(g), len(g[0])
    op = lambda x, y: 0 <= x < Wd and 0 <= y < H and g[y][x] != "."  # noqa: E731
    out = [r[:] for r in g]
    for y in range(H):
        for x in range(Wd):
            if g[y][x] != "F":
                continue
            side = not (op(x - 1, y) and op(x + 1, y))
            if not op(x, y + 1) or (side and y >= 26):
                out[y][x] = "Q"
            elif side or not op(x, y - 1):
                out[y][x] = "Z"
            elif g[y - 1][x] != "F" and (x <= 3 or x >= 12):
                out[y][x] = "V"                       # grey tip on the arm top under the cape
            elif y < 29 and (x + 2 * y) % 4 == 0:
                out[y][x] = "Y"                       # a sparse lit strand
            else:
                out[y][x] = "P"
    return ["".join(r) for r in out]


EW = compose("boy_1.png")
spec("sw_ewok_b", "SwEwok", "npc_3", "boy_1.png",
     "NEW WALKER (net:walker-ewok): variant B. Ewok scout like the film's Wicket: burnt-orange rust leather hood "
     "with a bone-bead cord, draping as a short ragged cape to the belly, small grizzled grey face deep in the hood, "
     "small dark eyes, dark brown-black fur, dark ear tufts, empty hands (placeholder: Boy 1). Used by the EWOK and "
     "SHAMAN trainers.",
     "Recast group d2 round 3, variant B (A is art/sw_ewok.yaml on NPC_2). 16x32 kit, 19 rows, on Boy 1's kid body "
     "as regions (walk and bob kept), all hand-toned on NPC_3: hood and cape on the rust ramp c (205 98 74 / "
     "148 57 41 / 82 16 0) with a dark cord, white and pale-grey bone beads, a dark 82 16 0 line under the cape hem; "
     "a small face (6 px) in grey ramp a with skin-light flecks, slate brow, 1-px black eyes, black nose, dark mouth; "
     "the body is dark fur (123 65 65 base, black and rust-dark outline, sparse 222 148 115 strands, grey arm tips); "
     "dark ear tufts with a grey tip. Brown-black furred and hornless, unlike grey-furred, bone-horned Chirpa "
     "(winona) who shares the rust hood ramp.",
     materials={},
     legend={"R": 11, "o": 12, "X": 13, "x": 13, "C": 4, "H": 5, "W": 14, "g": 6, "L": 5, "K": 1, "B": 7, "f": 2,
             "e": 15, "n": 15, "m": 13, "u": 4, "V": 6, "Z": 13, "Q": 15, "P": 4, "Y": 3},
     accept={"hair_rows": "a leather hood over fur",
             "eye_row": "small Ewok eyes deep in the hood"},
     frames=EW)

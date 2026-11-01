"""Recast group d2, round 3: sw_ewok (net:walker-ewok), the Ewok scout of the EWOK and SHAMAN trainers.

Round 2 (batches/r_rcd2.py) was "closer! Still looks too cute": the owner wants it closer to the film
Wicket (scratchpad refs: film photo + painted concept), no spear ("he can't carry anything"), and
earthier, less bright colours. This round:
- NPC_2, all hard pixels (no shader on this one): the hood is muted tan-rust leather (skin shade
  222 148 115 lit, ramp a dark 106 57 8 burnt umber body and folds, ramp b dark 98 0 24 in the deepest
  folds, ramp c dark outline); the face ring pale beige (skin light/base); the fur ramp c brown, dark.
  NPC_3's rust ramp was tried first but its fur tones were the same red as the hood (one red block),
  and NPC_2's gold ramp-a mid read too bright, so the hood is lit with the skin shade instead.
- Hood hugging the head with a dark cord across the brow carrying a white bone bead and an amber bead
  (no top bead), draping as a short ragged cape over the chest to the belly, darker underside, leather
  fold bands on the back. The cape hem swings 1 px against the step.
- Face framed tight: pale fur ring, heavy dark-brown brow, SMALL 1-px dark eyes (no glints), dark
  muzzle with a black nose and a dark mouth line.
- Small dark fur ear tufts above the hood.
- Body: Boy 1's kid body as regions (walk cycle and bob kept), hand-toned as dark shaggy fur (dark brown
  base, near-black-brown outline, black low down and on the soles, lighter arms with pale tips under the
  cape), empty hanging arms, stocky fur feet.
Writes art/sw_ewok.yaml (replaces the round 2 version; do not rerun r_rcd2.py after this).
Run from the tool folder: python batches/r_rcd3.py
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

# Hard letters: hood R = 3 lit, o = 7 body, X = 10 deep fold, x = 13 outline; cord C = 4 with beads
# W = 14 (bone) and H = 6 (amber); face ring b = 2, tips G/L = 1, brow B = 12, muzzle s = 11, eyes e
# and nose n = 15, mouth m = 13; ear tufts u = 12. Body fur (fur()): Z = 13, Q = 15, P = 12, Y = 11, V = 3.
HEAD_D = """
___uu______uu___
___uxRRRRRRxu___
__xRRRRRRRRRRx__
_xRoooRRRRoooRx_
_xoCCHWCCCCCCox_
_xoobLGbbGLboox_
_xRobBBbbBBboRx_
_xXobeBbbBeboXx_
_xXobbsnnsbboXx_
_xXoGbbmmbbGoXx_
__xxoGbbbbGoxx__
___xRRoxxoRRx___
___xooRRRRoox___
___xXooRRooXx___
___xxoxxxoxx____"""
HEAD_U = """
___uu______uu___
___uxRRRRRRxu___
__xRRRRRRRRRRx__
_xRRRRRRRRRRRRx_
_xoCCCCCCHWCCox_
_xRRRRRRRRRRRRx_
_xoooRRRRRRooox_
_xXooooooooooXx_
_xXoRRRRRRRRoXx_
_xXooooRRooooXx_
_xXoooooooooXXx_
__xoxooxxooxox__
___x_xx__xx_x___"""
HEAD_L = """
_____uu___uu____
____uxRRRRRxu___
___xRRRRRRRRRx__
__xRRRRRRRRRRRx_
_xWHCCRRRRRRRox_
_xbLGxRRRRRRoox_
_BBbbxoooooooXx_
_eBbbxRRRRRRoXx_
nsbbbxooRRooXXx_
mbGbxoooooooXXx_
_xbbxoRoooooXx__
__xRRoxoooox____
__xoRRRRRox_____
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
    """Tone the leftover body pixels (F) as dark shaggy fur, darker than the rust hood so the cape
    reads over it: near-black-brown outline (Z), black low down and on the soles (Q), dark brown base
    (P), lighter arms and the odd lit strand (Y), pale tips on the arm tops under the cape (V)."""
    H, Wd = len(g), len(g[0])
    op = lambda x, y: 0 <= x < Wd and 0 <= y < H and g[y][x] != "."  # noqa: E731
    out = [r[:] for r in g]
    for y in range(H):
        for x in range(Wd):
            if g[y][x] != "F":
                continue
            side = not (op(x - 1, y) and op(x + 1, y))
            if not op(x, y + 1) or (side and y >= 27):
                out[y][x] = "Q"                       # soles and leg edges
            elif side or not op(x, y - 1):
                out[y][x] = "Q" if y >= 26 else "Z"     # edge: near-black-brown, black low down
            elif g[y - 1][x] != "F" and (x <= 3 or x >= 12):
                out[y][x] = "V"                       # grey tip on the arm top under the cape
            elif (x <= 3 or x >= 12):
                out[y][x] = "Y"                       # arm fur, lighter than the body
            elif y < 29 and (x + 2 * y) % 4 == 0:
                out[y][x] = "Y"                       # a lit strand
            else:
                out[y][x] = "P"
    return ["".join(r) for r in out]


EW = compose("boy_1.png")
spec("sw_ewok", "SwEwok", "npc_2", "boy_1.png",
     "NEW WALKER (net:walker-ewok): Ewok scout like the film's Wicket: muted tan-rust leather hood with a "
     "bone-bead cord, draping as a short ragged cape to the belly, pale fur face ring, small dark eyes, dark shaggy "
     "brown fur, small fur ear tufts, empty hands (placeholder: Boy 1). Used by the EWOK and SHAMAN trainers.",
     "Recast group d2 round 3 (owner: closer to the film, no spear, less cute and bright). 16x32 kit, 19 rows, "
     "on Boy 1's kid body as regions (walk and bob kept), all hand-toned on NPC_2: muted tan-rust leather hood "
     "and short ragged cape (skin shade lit, burnt-umber ramp-a dark body, ramp-b dark deep folds), dark cord "
     "with a bone and an amber bead, pale beige face ring, heavy brow, 1-px dark eyes, dark muzzle, black nose, "
     "mouth line, small dark ear tufts; the body is dark shaggy brown fur with empty swinging arms. "
     "Brown-furred and hornless, unlike grey-furred, bone-horned Chirpa (winona).",
     materials={},
     legend={"R": 3, "H": 6, "o": 7, "X": 10, "x": 13, "C": 4, "W": 14, "G": 1, "L": 1, "b": 2, "B": 12,
             "s": 11, "e": 15, "n": 15, "m": 13, "u": 12, "g": 11, "Z": 13, "Q": 15, "P": 12, "V": 3, "Y": 11},
     accept={"hair_rows": "a leather hood over fur",
             "eye_row": "small Ewok eyes deep in the hood"},
     frames=EW)

"""Group 7 of the B-style rollout: the player, KAEL (replaces Brendan) and MIRA (replaces May).

One design per character, drawn once and placed on every sheet the player uses (walking, running,
decorating, and the old Ruby/Sapphire walking/running sheets) so they read as one character.

The player sheets use their own palettes (brendan.pal / may.pal), whose index layout is not the
NPC layout, so the tool's `regions` would mix ramps up. Instead this file reads each vanilla sheet
itself and turns its indices into material letters by colour AND position (torso / belt / legs /
boots bands), so the vanilla proportions, arms and walk/run cycles stay; then the new head is laid
over each frame at the offset that sheet's head sits at (the running sheets lower the head and
lean it forward). The result goes to spec() as whole frames in shade mode (the learned shader
picks every tone). Palettes: palettes/kael.pal and palettes/mira.pal (NPC index order); the
spec keeps the player's own palette tag, since install replaces brendan.pal / may.pal.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_g7.py
"""
import sys

import yaml

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P, spec  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import game_dir  # noqa: E402

ORDER = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]
SKIN = (1, 2, 3, 4)


def vanilla(path):
    fr, _ = read_frames(game_dir() / (P + path), (16, 32))
    return fr


def top(f):
    return next(y for y, r in enumerate(f) if any(r))


def overlay(g, rows, x0, y0, keep=None):
    for dy, ln in enumerate(rows.strip("\n").split("\n")):
        assert x0 + len(ln) <= 16 + 2 or len(ln) == 16, ln
        for dx, ch in enumerate(ln):
            x, y = x0 + dx, y0 + dy
            if ch == "_" or not (0 <= x < 16 and 0 <= y < 32) or (keep and keep(x, y)):
                continue
            g[y][x] = ch


def build(path, classify, heads, offsets, extra=None, order=ORDER, face=None, keep=None):
    """classify(v, x, y, facing) -> letter, y in stand coordinates (the frame's bob removed);
    heads: facing -> (y, rows) drawn for the walking sheet; offsets: facing -> (dx, dy) of this
    sheet's head against the walking sheet; extra: facing -> [(x, y, rows)] costume patches
    (they follow the head offset's dy and the bob); face: frame -> facing override (decorating);
    keep: (frame, x, y) -> True keeps the vanilla pixel under the head (hands raised beside it)."""
    van = vanilla(path)
    out, stand_top = {}, {}
    for name, f in zip(order, van):
        if "_" not in name:
            stand_top[name] = top(f)
    for name, f in zip(order, van):
        stand = name.split("_")[0]
        facing = (face or {}).get(name, stand)
        bob = top(f) - stand_top[stand]
        dx, dy = offsets.get(facing, (0, 0))
        g = [["." if not v else classify(v, x, y - bob, facing) for x, v in enumerate(r)] for y, r in enumerate(f)]
        for (px, py, rows) in (extra or {}).get(facing, []):
            overlay(g, rows, px + dx, py + dy + bob)
        hy, hrows = heads[facing]
        k = (lambda x, y: f[y][x] and keep(name, x, y - bob)) if keep else None
        overlay(g, hrows, dx, hy + dy + bob, k)
        out[name] = ["".join(r) for r in g]
    return out


def write(name, gi, pal, replaces, tag, desc, note, materials, legend, accept, frames, kit="person16x32"):
    spec(name, gi, pal, replaces, desc, note, materials, legend, accept, frames=frames, kit=kit)
    p = f"art/{name}.yaml"
    d = yaml.safe_load(open(p))
    d["palette_tag"] = tag  # keep the player's own tag: install replaces brendan.pal / may.pal
    open(p, "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


# ====================================================================== KAEL (replaces Brendan)
# Tousled short brown hair (H, ramp b) under a kyber-blue headband (C, ramp c) whose knot tails
# flick out behind; sand wrapped tunic (T, ramp a) over a white crossover undershirt (V), white
# arm wraps (G); brown leather belt (L), sand trousers (D), brown boots (K), brown satchel (S) on
# the back and hip; a one-pixel kyber-crystal pendant (q, light blue) at the collar.
K_DOWN = """
................
................
.....H...H......
....HHH.HHHH....
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..CCCCCCCCCCCCC.
..HHsHHHHHsHHHCC
_sHssssssssssHs_
_sHsssessesssHs_
__ssssessessss__
___ssssssssss___"""
K_UP = """
................
................
......H...H.....
....HHHH.HHH....
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.CCCCCCCCCCCCC..
CCHHHHHCCHHHHH..
_sHHHHHCCHHHHHs_
_sHHHHCHHCHHHHs_
__sHHHHHHHHHHs__
___ssHHHHHHss___"""
K_LEFT = """
................
................
........H.H.....
.....HHHHHHH....
...HHHHHHHHHHH..
..HHHHHHHHHHHHH.
..HHHHHHHHHHHHH.
..CCCCCCCCCCCCC.
..sHHsHHHHHHHCCC
__sssssHHHHHHC.C
__ssessHsHHHH___
__ssessssHHHH___
___sssssssHH____
____sssssss_____"""
K_HEADS = {"down": (9, K_DOWN), "up": (9, K_UP), "left": (9, K_LEFT)}
# Brendan-family band rows (stand coordinates): facing -> (belt, legs, boots)
K_BANDS = {"walk": {"down": (26, 27, 29), "up": (26, 27, 29), "left": (26, 27, 29)},
           "run": {"down": (26, 27, 28), "up": (26, 27, 28), "left": (26, 27, 29)}}


def kael_classifier(b, item_x=-1):
    """Brendan-family sheets (Emerald and R/S share the layout): 1-4 skin, 5-8 navy, 9/14 white,
    10-11 green (Emerald) or yellow (R/S) bag and gloves, 12-13 red, 15 black."""
    def c(v, x, y, facing):
        belt, legs, boots = b[facing]
        if x <= item_x and 19 <= y <= 26:
            return "O"
        if y >= boots:
            return "K"
        if y >= legs:
            return "D"
        if v in SKIN:
            return "s"
        if y == belt:
            return "L"
        arm = x <= 3 or x >= 12
        bag = v in (9, 10, 11, 14)
        if facing == "left":
            if bag:
                return "S" if x >= 9 else "G"
            if v in (12, 13):
                return "G" if x <= 7 else "S"
            return "T"
        if facing == "up":
            if bag:
                return "G" if arm else "S"
            if v in (12, 13):
                return "G" if arm else "T"
            return "T"
        if bag or v in (12, 13):
            return "G" if arm else "V"
        return "T"
    return c


K_MAT = {"s": "s", "H": "b", "C": "c", "T": "a", "V": "w/a", "G": "w/a", "L": "b", "D": "a", "K": "b",
         "S": "b", "O": "w/c"}
K_LEG = {"e": 15, "q": 11}
K_EXTRA = {"down": [(7, 22, "q")]}
K_NOTE = ("moves to the new kael.pal (install replaces {pal} and its reflection; the bike, surf and field-move "
          "sheets still use the old layout until they are redrawn)")
K_DESC = ("Tousled brown hair under a kyber-blue headband with knot tails, sand wrap tunic over a white "
          "crossover, white arm wraps, brown belt, satchel and boots, a kyber pendant")


def run_keep(name, x, y):
    # running step frames raise a hand beside the head: keep it
    return name in ("down_a", "down_b") and (x <= 1 or x >= 14) and y >= 15


# ====================================================================== MIRA (replaces May)
# Chestnut hair (H, ramp c) with May's side bunches turned into two round buns (U, c@) wrapped in
# rust-red cloth (R, ramp b) that also makes the headwrap band and its knot tails; cream wrap
# tunic (T, ramp a) with a rust-red tabard (V) down the front, white arm wraps (G), chestnut
# leather sash (L), cream leggings (D), chestnut boots (K), a chestnut hip pack (S).
M_DOWN = """
................
................
...UUU....UUU...
..URRRU..URRRU..
..UUUUHHHHUUUU..
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..RRRRRRRRRRRR..
.HHHHsHHHHsHHHH.
.HHssssssssssHH.
.HHsssessesssHH.
.HHsssessesssHH.
.H..ssssssss..H."""
M_UP = """
................
................
...UUU....UUU...
..URRRU..URRRU..
..UUUUHHHHUUUU..
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..RRRRRRRRRRRR..
.HHHHHRRRRHHHHH.
.HHHHHHRRHHHHHH.
.HHHHHHRRHHHHHH.
.HHHHHHHHHHHHHH.
.H.HHHHHHHHHH.H."""
M_LEFT = """
................
................
..........UUU...
......HHHURRRU..
....HHHHHUUUUU..
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..RRRRRRRRRRRRR.
..sHHHHHHHHHHRR.
..ssssHHHHHHHHR.
..ssessHsHHHHH..
..ssessssHHHHH..
___sssssssHHH___
____sssssHHH____"""
M_HEADS = {"down": (9, M_DOWN), "up": (9, M_UP), "left": (9, M_LEFT)}
M_BANDS = {"walk": {"down": (26, 28, 29), "up": (-1, 28, 29), "left": (-1, 28, 29)},
           "run": {"down": (25, 27, 28), "up": (-1, 27, 28), "left": (-1, 28, 29)}}


def mira_classifier(b, item_x=-1):
    """May-family sheets (Emerald and R/S share the layout): 1-4 skin, 5-6 greys, 7 hair,
    8 dark brown, 9/14 white gloves, 10-11 green (Emerald) or yellow (R/S) pack, 12-13 red top,
    15 black."""
    def c(v, x, y, facing):
        belt, legs, boots = b[facing]
        if x <= item_x and 19 <= y <= 26:
            return "O"
        if y >= boots:
            return "K"
        if y >= legs:
            return "D"
        if v in SKIN:
            return "s"
        if y <= 22 and v in (7, 8, 15):
            return "H"  # hair kept beside the head (swinging buns in the running step frames)
        if v == 7 or (v == 8 and facing in ("up", "left") and y <= 25):
            return "H"
        if y == belt:
            return "L"
        if v in (9, 14):
            return "G"
        if v in (10, 11):
            return "S"
        if v in (12, 13):
            return "V"
        return "T"
    return c


M_MAT = {"s": "s", "H": "c", "U": "c@", "R": "b", "T": "a", "V": "b", "G": "w/a", "L": "c", "D": "a",
         "K": "c", "S": "c", "O": "w/c"}
M_LEG = {"e": 15}
M_NOTE = ("moves to the new mira.pal (install replaces {pal} and its reflection; the bike, surf and field-move "
          "sheets still use the old layout until they are redrawn)")
M_DESC = ("Chestnut hair with two round buns wrapped in rust-red cloth and a matching headwrap, cream wrap "
          "tunic with a rust-red tabard, white arm wraps, chestnut sash, pack and boots")

# ====================================================================== build
RUN_OFFS_K = {"down": (0, 1), "up": (0, 1), "left": (-2, 1)}
RUN_OFFS_M = {"down": (0, 1), "up": (0, 0), "left": (-2, 1)}
SHEETS = [
    # name, path, graphics info, palette tag, palette file it replaces, who, mode, head offsets, keep, subject
    ("brendan_walking", "brendan/walking.png", "BrendanNormal", "BRENDAN", "brendan.pal", "K", "walk",
     {}, None, "KAEL, the player (boy), walking"),
    ("brendan_running", "brendan/running.png", "BrendanNormal", "BRENDAN", "brendan.pal", "K", "run",
     RUN_OFFS_K, run_keep, "KAEL, the player (boy), running"),
    ("rs_brendan_walking", "ruby_sapphire_brendan/walking.png", "RubySapphireBrendanNormal", "RS_BRENDAN",
     "ruby_sapphire_brendan.pal", "K", "walk", {}, None, "KAEL (old Ruby/Sapphire sheet), walking"),
    ("rs_brendan_running", "ruby_sapphire_brendan/running.png", "RubySapphireBrendanNormal", "RS_BRENDAN",
     "ruby_sapphire_brendan.pal", "K", "run", RUN_OFFS_K, run_keep, "KAEL (old Ruby/Sapphire sheet), running"),
    ("may_walking", "may/walking.png", "MayNormal", "MAY", "may.pal", "M", "walk", {}, None,
     "MIRA, the player (girl), walking"),
    ("may_running", "may/running.png", "MayNormal", "MAY", "may.pal", "M", "run",
     RUN_OFFS_M, run_keep, "MIRA, the player (girl), running"),
    ("rs_may_walking", "ruby_sapphire_may/walking.png", "RubySapphireMayNormal", "RS_MAY",
     "ruby_sapphire_may.pal", "M", "walk", {}, None, "MIRA (old Ruby/Sapphire sheet), walking"),
    ("rs_may_running", "ruby_sapphire_may/running.png", "RubySapphireMayNormal", "RS_MAY",
     "ruby_sapphire_may.pal", "M", "run", RUN_OFFS_M, run_keep, "MIRA (old Ruby/Sapphire sheet), running"),
]

if __name__ == "__main__":
    for name, path, gi, tag, palf, who, mode, offs, keep, subj in SHEETS:
        if who == "K":
            fr = build(path, kael_classifier(K_BANDS[mode]), K_HEADS, offs, extra=K_EXTRA, keep=keep)
            write(name, gi, "kael", path, "OBJ_EVENT_PAL_TAG_" + tag,
                  f"{subj}: Tatooine farm kid with a kyber-blue headband (replaces Brendan).",
                  f"Group 7: {subj}. Vanilla sheet as regions (its walk/run cycle kept). {K_DESC}; "
                  + K_NOTE.format(pal=palf) + ".", K_MAT, K_LEG, {}, fr)
        else:
            fr = build(path, mira_classifier(M_BANDS[mode]), M_HEADS, offs, keep=keep)
            write(name, gi, "mira", path, "OBJ_EVENT_PAL_TAG_" + tag,
                  f"{subj}: Tatooine scavenger girl with wrapped buns (replaces May).",
                  f"Group 7: {subj}. Vanilla sheet as regions (its walk/run cycle kept). {M_DESC}; "
                  + M_NOTE.format(pal=palf) + ".", M_MAT, M_LEG, {}, fr)
    # decorating: one frame, the left-facing pose holding a decoration (now a white supply crate)
    fr = build("brendan/decorating.png", kael_classifier(K_BANDS["walk"], item_x=2), K_HEADS, {},
               order=["down"], face={"down": "left"})
    write("brendan_decorating", "BrendanDecorating", "kael", "brendan/decorating.png", "OBJ_EVENT_PAL_TAG_BRENDAN",
          "KAEL, the player (boy), decorating a secret base: carries a supply crate (replaces Brendan).",
          f"Group 7: KAEL decorating, Brendan's decorating frame as regions. {K_DESC}, holding a white "
          "supply crate; " + K_NOTE.format(pal="brendan.pal") + ".", K_MAT, K_LEG, {}, fr, kit="person16x32_single")
    fr = build("may/decorating.png", mira_classifier(M_BANDS["walk"], item_x=2), M_HEADS, {},
               order=["down"], face={"down": "left"})
    write("may_decorating", "MayDecorating", "mira", "may/decorating.png", "OBJ_EVENT_PAL_TAG_MAY",
          "MIRA, the player (girl), decorating a secret base: carries a supply crate (replaces May).",
          f"Group 7: MIRA decorating, May's decorating frame as regions. {M_DESC}, holding a white "
          "supply crate; " + M_NOTE.format(pal="may.pal") + ".", M_MAT, M_LEG,
          {"head_w": "the one decorating frame faces left, as vanilla's does; the side view is 13 wide"}, fr, kit="person16x32_single")
    print("ok")

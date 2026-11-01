"""Large-companion group 2: mockups of the 32x32 legendary / story creatures, drawn in shade mode.

SHIFTSTAR (deoxys), ASHLA / BOGAN (latias_latios), the three WARDENS (regi), SLOTHFURY carrying a
cargo crate (vigoroth), MASSIFF (poochyena) and the large SCURRIER (enemy_zigzagoon).
Every frame keeps the vanilla sheet's frame size, count, order and footprint.
Writes art/<name>.yaml and palettes/sw_<stem>.pal. Run from the tool folder:
    python batches/r_lg2.py
"""
import sys

import yaml

sys.path.insert(0, "batches")
from helpers import PK  # noqa: E402

W = 32


# ---------------------------------------------------------------- helpers
def grid(text, x0=None):
    """Rows of a block -> 32-wide rows (centred unless x0 is given)."""
    rows = [r.strip() for r in text.strip("\n").split("\n")]
    w = len(rows[0])
    assert all(len(r) == w for r in rows), [(i, len(r), r) for i, r in enumerate(rows) if len(r) != w]
    if x0 is None:
        x0 = (W - w) // 2
    assert 0 <= x0 and x0 + w <= W, (x0, w)
    return ["." * x0 + r + "." * (W - x0 - w) for r in rows]


def sym(text, flip=None):
    """Left half (16 wide) mirrored into a 32-wide frame. flip maps letters on the right side."""
    rows = [r.strip() for r in text.strip("\n").split("\n")]
    assert all(len(r) == 16 for r in rows), [(i, len(r)) for i, r in enumerate(rows) if len(r) != 16]
    flip = flip or {}
    return [r + "".join(flip.get(c, c) for c in r[::-1]) for r in rows]


def pad(rows, h=32):
    """Bottom-anchor to h rows."""
    assert len(rows) <= h, len(rows)
    return ["." * W] * (h - len(rows)) + list(rows)


def over(base, patch, x, y):
    """Paste patch rows (32-wide grid or narrow block text) onto base; '_' keeps the base pixel."""
    base = [list(r) for r in base]
    rows = [r.strip() for r in patch.strip("\n").split("\n")] if isinstance(patch, str) else patch
    for dy, r in enumerate(rows):
        for dx, c in enumerate(r):
            if c != "_":
                base[y + dy][x + dx] = c
    return ["".join(r) for r in base]


def lay(base, top):
    """Overlay top's opaque pixels onto base (both 32-wide grids of the same height)."""
    return ["".join(t if t != "." else b for b, t in zip(br, tr)) for br, tr in zip(base, top)]


def shift(rows, dy=0, dx=0):
    out = [["."] * W for _ in range(32)]
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != "." and 0 <= y + dy < 32 and 0 <= x + dx < W:
                out[y + dy][x + dx] = c
    return ["".join(r) for r in out]


def mirror(rows):
    return [r[::-1] for r in rows]


def write_pal(stem, cols):
    assert len(cols) == 16 and tuple(cols[0]) == (115, 197, 164)
    with open(f"palettes/sw_{stem}.pal", "w", newline="\r\n") as f:
        f.write("JASC-PAL\n0100\n16\n" + "".join(f"{r} {g} {b}\n" for r, g, b in cols))


def put(name, replaces, gi, kit, pal, tag, desc, notes, materials, legend, accept, frames):
    fr = {}
    for k, rows in frames.items():
        rows = pad(rows)
        assert all(len(r) == W for r in rows), (name, k, [len(r) for r in rows])
        fr[k] = "\n".join(rows) + "\n"
    d = {"name": name, "description": desc, "kit": kit, "replaces": PK + replaces, "graphics_info": gi,
         "notes": notes, "palette": pal, "palette_tag": tag, "shade": True, "materials": materials,
         "legend": legend, "accept": accept, "frames": fr}
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


CREATURE = {"skin_tones": "creature: no human skin", "hair_rows": "creature: no hair",
            "eye_row": "creature eyes, not a human face"}

# ====================================================================== WARDENS (regi.png)
# One frame, recoloured by palette tag: ROCKWARDEN NPC_2 (yellow-orange sandstone, red glyph light),
# ICEWARDEN NPC_3 (lavender-grey ice, green glyph light), DURAWARDEN NPC_4 (navy durasteel,
# magenta glyph light). So the body lives on ramp a, the glowing visor and Aurebesh glyphs on
# ramp b, deep cracks on ramp c's darkest tone only (dark maroon / dark brown / dark grey all
# read as shadow), white glints; nothing on the skin ramp (peach in every NPC palette).
REGI = sym("""
................
................
................
................
...........HHHHH
.........HHHHHHH
........HHHHHHHH
........HHHHHHHH
.......HHHHHVVVV
.......HHHHHVVVV
..PPPP.HHHHHHHHV
.PPPPPPPHHHHHHHV
PPPPPPPPHHHHHHHV
PPPPPPPPPBBBBBBB
PPPPPPPPPBBBBBBB
PPPPPPPPBBBBBBBB
.RRRRRRBBBBBBBBB
.RRRRRRBGGGGGGGG
.RRRRRRBGGGGGGGG
.RRRRRRBGGGGGGGG
.RRRRRRBGGGGGGGG
.RRRRRRBGGGGGGGG
.CCCCCCBBBBBBBBB
CCCCCCCBBBBBBBBB
FFFFFFFFBBBBBBBB
FFFFFFFF.LLLLLLL
FFFFFFFF.LLLLL..
.FFFFFF.LLLLLL..
..FFFF..LLLLLL..
........LLLLLL..
.......LLLLLLL..
................
""")
# Aurebesh-like glyphs glowing on the sealed chest plate (g light, h mid glow)
REGI = over(REGI, """
gggh_ghg_hgg
hg___ggg__gh
gg___h_g__hg""", 10, 18)
# glints on the hood and boulder shoulders, cracks in ramp c's darkest tone
REGI = over(REGI, "XX", 13, 5)
REGI = over(REGI, "X", 3, 11)
REGI = over(REGI, "X", 26, 11)
REGI = over(REGI, """
__x
_x_
x__""", 3, 13)
REGI = over(REGI, """
x__
_xx""", 26, 14)
REGI = over(REGI, """
_x
x_""", 2, 26)
REGI = over(REGI, """
xx_
__x""", 27, 25)
REGI = over(REGI, "xx", 19, 15)
put("regi", "regi.png", "Regirock / Regice / Registeel", "frames32x32_1", "npc_2", "OBJ_EVENT_PAL_TAG_NPC_2",
    "ROCKWARDEN / ICEWARDEN / DURAWARDEN: ancient sentinel sealed behind Aurebesh glyphs (replaces the Regi sheet).",
    "Group lg2: one sentinel for all three palette tags; body on ramp a, glowing T-visor and Aurebesh glyph plate on ramp b.",
    materials={"H": "a!", "P": "a!", "B": "a!", "R": "a!", "F": "a!", "L": "a!", "V": "b!", "C": "c!"},
    legend={"g": 8, "h": 9, "G": 10, "x": 13, "X": 14},
    accept=CREATURE, frames={"down": REGI})

# ====================================================================== ASHLA / BOGAN (latias_latios.png)
# Force dragons of Tython, seen head-on and hovering, wings raised (frame 0 stand, 1-2 wing flaps;
# the pic table uses frame 0 for every facing). One sheet, two palettes: the body lives on ramp c,
# the wing membranes on ramp a, the brow kyber gem on ramp b, chest white.
#   ASHLA (light moon) on NPC_4: silver-grey hide, steel-blue membranes, pink kyber.
#   BOGAN (dark moon)  on NPC_2: dark maroon hide, amber membranes and eyes, red kyber.
# Head-on and hovering like vanilla: a long horned head with the snout toward the camera, wings
# raised in a V from the shoulders (finger bone, scalloped membrane), belly scutes, a tail
# curling off to one side.
LAT_BODY = sym("""
................
................
..........X.....
..........XX....
...........XX...
...........hXHHH
............HHHH
...........HHHqg
...........HeHHH
...........HkHHH
............HHHH
............HHHH
.............HHH
.............HnH
.............JJJ
..............NN
..............NN
...........BBBBW
..........BBBBBW
..........BBBBzz
...........BBBWW
...........BBBzz
.........LLBBBWW
........LLLBBBzz
........L..BBBWW
............BBBB
.............BBB
................
................
................
................
................
""")
LAT_BODY = over(LAT_BODY, """
TTT.....
.TTTT...
...TTTT.
.....TTT
......T.""", 15, 26)
LAT_WING_HALF = """
EE..............
EEE.............
.EMME...........
.EMMME..........
..EMMMME........
..EMMMMME.......
...EMMMMMME.....
...EMMMMMMME....
....EMMMMMMMEE..
....EMMMMMMEMME.
.....MMMMMEMMMME
.....MMMMEMMMMME
......MMEMMMMMME
......MEMMMMMMME
.......MMMMMMMME
.......M.MMMMMME
..........MMMMME
...........MMMME
............MMM.
"""


def lat_wing(dx, dy):
    rows = [r.strip() for r in LAT_WING_HALF.strip().split("\n")]
    half = [list("." * 16) for _ in range(32)]
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != "." and 0 <= y + dy < 32 and 0 <= x + dx < 16:
                half[y + dy][x + dx] = c
    return sym("\n".join("".join(r) for r in half))


LAT = [lay(lat_wing(0, 0), LAT_BODY), lay(lat_wing(1, 0), shift(LAT_BODY, 1)), lay(lat_wing(3, 1), shift(LAT_BODY, 2))]
put("latias_latios", "latias_latios.png", "Latias / Latios", "frames32x32_3", "npc_4", "OBJ_EVENT_PAL_TAG_NPC_4",
    "ASHLA / BOGAN: light- and dark-side Force dragons of Tython (replaces Latias / Latios).",
    "Group lg2: one hovering dragon for both; hide on ramp c, membranes ramp a, kyber gem ramp b. Ashla on NPC_4, Bogan on NPC_2.",
    materials={"H": "c@", "J": "c", "N": "c", "B": "c!", "T": "c!", "E": "c!", "M": "a", "W": "w/c", "L": "c!"},
    legend={"h": 13, "e": 5, "k": 15, "g": 8, "q": 9, "n": 13, "z": 11, "X": 14},
    accept=CREATURE, frames={"down": LAT[0], "f1": LAT[1], "f2": LAT[2]})

# ====================================================================== SHIFTSTAR (deoxys.png)
# Star-born shapeshifter of Atollon: a four-pointed crystal star crest over a pale glowing mask
# with one visor slit, a violet nebula body with a gold star-core in the chest, teal crystal
# shoulder facets, two ribbon tendrils that change shape between frames (it never holds one
# form), legs tapering to points. Frame 0 stand, frame 1 the shifted pose (1 px lower, as vanilla).
write_pal("deoxys", [(115, 197, 164),
                     (232, 216, 248), (192, 168, 232), (144, 112, 200), (80, 48, 128),   # star-glow mask
                     (248, 232, 120), (232, 160, 48), (152, 80, 24),                     # A gold core
                     (152, 240, 232), (64, 184, 200), (24, 96, 128),                     # B teal crystal
                     (152, 112, 216), (96, 64, 168), (48, 24, 96),                       # C violet body
                     (255, 255, 255), (16, 8, 32)])
DX_BODY = sym("""
................
...............Q
...............Q
..............QQ
..............QQ
.............QQQ
............QFFF
...........QFFFF
........QQQFFFFF
.....QQQQQQFFFFF
........QQQFkkkY
...........QFFFF
............QFFF
.........PPP.CCC
........PPPPCCCC
........PPPCCCCA
.........PCCCCAA
..........CCCAAA
..........CCCCAA
..........CCCCCA
...........CCCCC
...........CCCCC
..........LLL...
..........LLL...
.........LLLL...
.........KLLL...
.........LLL....
.........LLL....
..........LL....
..........L.....
................
................
""")
# the tendrils are thin ribbons the shader breaks, so they are hand-toned: o outline (b dark),
# m mid, l light, Y gold tip
DX_TENDRILS = [
    (["....ooo", "...omlo", "..omlo.", ".omlo..", ".omo...", "omlo...", "omo....", "omlo...", ".omo...", ".oYYo..", "..oYY.."], 1, 13,
     ["ooo....", "olmo...", ".olmo..", "..olmo.", "...omo.", "...olmo", "..omo..", ".omo...", ".omo...", "oYYo...", ".YY...."], 24, 13),
    (["..oooo.", ".omllo.", "omlo...", "omo....", "omlo...", ".omo...", "..omo..", "..omlo.", "...omo.", "..oYYo.", "..YY..."], 1, 13,
     ["oooo...", ".llmo..", "...omo.", "....omo", "....omo", "...omo.", "..omo..", "..omo..", "...oYo.", "...YY..", "......."], 24, 13),
]
# star specks in the nebula body (star-born)
DX_SPECKS = [(13, 20), (19, 18), (17, 21)]


def dx_frame(i):
    body = shift(DX_BODY, i)
    lt, lx, ly, rt, rx, ry = DX_TENDRILS[i]
    body = over(body, "\n".join(r.replace(".", "_") for r in lt), lx, ly + i)
    body = over(body, "\n".join(r.replace(".", "_") for r in rt), rx, ry + i)
    for x, y in DX_SPECKS:
        body = over(body, "v", x, y + i)
    return body


put("deoxys", "deoxys.png", "Deoxys", "frames32x32_2", "sw_deoxys", "OBJ_EVENT_PAL_TAG_DEOXYS",
    "SHIFTSTAR: star-born shapeshifter of Atollon (replaces Deoxys).",
    "Group lg2: star crest, glowing mask with a visor slit, gold star-core, ribbon tendrils that change shape. Own palette sw_deoxys.pal (NPC layout).",
    materials={"Q": "b", "F": "s@", "P": "b", "C": "c!", "A": "a@", "L": "c!", "R": "b"},
    legend={"v": 14, "K": 8, "Y": 5, "k": 15, "o": 10, "m": 9, "l": 8},
    accept={**CREATURE, "skin_tones": "the skin ramp is the star-glow mask"}, frames={"down": dx_frame(0), "f1": dx_frame(1)})

# ====================================================================== SLOTHFURY (vigoroth.png)
# Restless Nal Hutta swamp sloth: shaggy moss-green fur (ramp a) with a dark brown mane and spine
# stripe (ramp c), a pale tan face mask (skin ramp) with the dark sloth eye-band, long arms with
# ivory hook claws. Frames 0-2 haul a steel cargo crate (ramp b, white stencil) facing left
# (stand, two steps); frames 3-4 are the back view it fidgets in.
write_pal("vigoroth", [(115, 197, 164),
                       (232, 216, 176), (200, 168, 120), (152, 112, 72), (88, 56, 32),    # face mask, claws
                       (176, 192, 104), (112, 136, 64), (56, 72, 32),                     # A moss fur
                       (200, 208, 216), (128, 136, 160), (64, 72, 96),                    # B crate steel
                       (160, 120, 72), (104, 72, 48), (56, 40, 24),                       # C mane
                       (255, 255, 255), (16, 16, 24)])
VG_SIDE_BODY = grid("""
................................
................................
................................
........M.MM.M..................
.......MMMMMMMM.................
......MMHHHHHHMM..M.M...........
.....MHHSSSSSHHMMGGGGM..........
.....HSSkkSSkkSHGGGGGGGM........
.....HSSkeSSkeSHGGGGGGGGM.......
.....HSSSSnnSSHGGGGGGGGGGM......
......HSSSSSSHGGGGGGGGGGGGM.....
..........HHHAAAGGGGGGGGGGG.....
.........AAAAAAGGGGGGGGGGGGM....
..........AAAAGGGGGGGGGGGGGG....
...........AAGGGGGGGGGGGGGGM....
...........GGGGGGGGGGGGGGGGG....
...........GGGGGGGGGGGGGGGGM....
............GGGGGGGGGGGGGGG.....
............GGGGGGGGGGGGGGM.....
............GGGGGGGGGGGGGG......
............GGGGGGGGGGGGGM......
...........BBBGGGGGG............
..........BBBBBGGGG.............
...........BBB..................
................................
................................""", 0)
VG_CRATE = """
oooooooooo
oTTTTTTTTo
oTTTTTTTTo
oooooooooo
oKKKKKKKKo
oKlllKKKKo
oKKKKKXKKo
oKKKKXKXKo
oKKKKKKKKo
oooooooooo
oKKKKKKKKo
oKKKKKKKKo
oKKKKKKKKo
oKKKKKKKKo
oooooooooo"""
VG_CLAWS = [("c_\ncc\n_c", 7, 12), ("cc\n_c", 9, 23)]
VG_FUR = [(18, 9), (18, 10), (22, 11), (22, 12), (15, 15), (15, 16), (20, 16), (20, 17), (24, 14), (24, 15), (17, 19), (23, 19)]
VG_LEGS = [grid("""
...................LLLLL........
...............FFF.LLLLLLL......
...............FFF.LLLLLLL......
...............FFF..LLLLLL......
...............FFF...LLLLL......
..............FFF....LLLLL......
.............cccc...cccccc......
................................
................................
................................""", 0), grid("""
...................LLLLL........
..............FFF..LLLLLL.......
.............FFF....LLLLLL......
............FFF......LLLLL......
...........FFF........LLLLL.....
..........ccc.........LLLLL.....
......................cccccc....
................................
................................
................................""", 0), grid("""
...................LLLLL........
................FFFLLLLL........
................FFLLLLL.........
................FLLLLL..........
...............LLLLL............
..............LLLLL.............
.............cccccc.............
................................
................................
................................""", 0)]


def vg_side(i):
    body = VG_SIDE_BODY[:22] + VG_LEGS[i]
    for x, y in VG_FUR:
        body = over(body, "m", x, y)
    body = over(body, VG_CRATE, 0, 11)
    for t, x, y in VG_CLAWS:
        body = over(body, t, x, y)
    return body if i == 0 else shift(body[:31] + ["." * W], 0) if False else (shift(body, 1)[:22] + body[22:] if True else body)


VG_SIDE = [vg_side(0), vg_side(1), vg_side(2)]
VG_BACK = sym("""
................
................
................
..............MM
............MMMM
...........JJJMM
..........JJJJJJ
..........JJJJJJ
..........JJJJJJ
........GGGJJJJJ
......GGGGGGJJJJ
.....GGGGGGGGGGG
....AGGGGGGGGGGG
...AAAGGGGGGGGGG
...AAAGGGGGGGGGG
..AAAA.GGGGGGGGG
..AAAA.GGGGGGGGG
..AAAA.GGGGGGGGG
..AAA..GGGGGGGGG
..AAA..GGGGGGGGG
..AAA...GGGGGGGG
..AAA...GGGGGGGG
..AAA....GGGGGGG
..ccc..LLLLGGGGG
...c...LLLL.....
.......LLLL.....
.......LLLL.....
......ccccc.....
................
................
................
................
""")
for x, y in [(9, 13), (9, 14), (12, 17), (12, 18), (21, 13), (21, 14), (19, 17), (19, 18), (15, 20), (16, 21), (14, 8), (17, 7)]:
    VG_BACK = over(VG_BACK, "m", x, y)
# fidget: the body rocks down a pixel and the arms lift, the feet stay planted
VG_BACK2 = shift(VG_BACK, 1)[:27] + VG_BACK[27:]
put("vigoroth", "vigoroth.png", "VigorothCarryingBox / VigorothFacingAway", "frames32x32_5", "sw_vigoroth",
    "OBJ_EVENT_PAL_TAG_VIGOROTH",
    "SLOTHFURY: restless Nal Hutta swamp sloth hauling a cargo crate (replaces Vigoroth).",
    "Group lg2: moss fur, dark mane, tan face mask with the sloth eye-band, ivory hook claws, steel cargo crate. Own palette sw_vigoroth.pal (NPC layout).",
    materials={"M": "c", "H": "c@", "J": "a@", "S": "s@", "G": "a!", "A": "a", "B": "a", "L": "a", "F": "a"},
    legend={"k": 12, "e": 15, "n": 4, "c": 1, "X": 14, "m": 7, "o": 10, "T": 8, "K": 9, "l": 2},
    accept={**CREATURE, "skin_tones": "the skin ramp is the face mask and claws"},
    frames={"down": VG_SIDE[0], "f1": VG_SIDE[1], "f2": VG_SIDE[2], "f3": VG_BACK, "f4": VG_BACK2})

# ---------------------------------------------------------------- 9-frame walkers
def walker(body, legs, x0, h=32):
    """body: block rows (without legs) ending on the row above the legs; legs: 3 variants (stand,
    step a, step b) of leg rows. Returns stand, step a, step b as 32x32 grids; steps bob the body
    down 1 px over the swung legs, as vanilla does."""
    out = []
    for i, lg in enumerate(legs):
        rows = [r.strip() for r in body.strip("\n").split("\n")]
        lrows = [r.strip() for r in lg.strip("\n").split("\n")]
        full = pad(grid("\n".join(rows + lrows), x0))
        if i:
            b = pad(grid("\n".join(rows + ["." * len(rows[0])] * len(lrows)), x0))
            b = shift(b, 1)
            l = pad(grid("\n".join(["." * len(rows[0])] * len(rows) + lrows), x0))
            full = lay(l, b)
        out.append(full)
    return out


# ====================================================================== MASSIFF (poochyena.png)
# Tusken guard beast of Tatooine: sandy reptile hide (skin ramp), a bony brow plate and a row of
# dorsal spikes (ramp a, bone), small amber eyes and a wide toothy jaw (ramp b), a Tusken
# leather harness collar (ramp c). Vanilla footprint: ~16 wide facing, ~22 in profile, feet on row 31.
write_pal("poochyena", [(115, 197, 164),
                        (232, 208, 160), (200, 168, 120), (160, 120, 80), (96, 64, 40),    # hide
                        (240, 232, 208), (184, 176, 152), (112, 104, 88),                  # A bone
                        (248, 176, 64), (200, 64, 48), (104, 24, 32),                      # B eyes, maw
                        (176, 120, 72), (120, 80, 48), (64, 40, 24),                       # C harness
                        (255, 255, 255), (24, 16, 16)])
MS_DOWN = walker("""
.....R.RR.R.....
....RBRBBRBR....
...BPPPPPPPPB...
..BPPPPPPPPPPB..
..HHPPPPPPPPHH..
.HHekHHHHHHkeHH.
.HHHHHHHHHHHHHH.
.HHHHHnHHnHHHHH.
..HwmmwmmwmmwH..
..HHHHHHHHHHHH..
..LLCCCCCCCCLL..""", ["""
..LLL.CCCC.LLL..
..LLL......LLL..
..LLL......LLL..
..fff......fff..""", """
..LLL.CCCC.LLL..
..LLL......LLL..
..fff......LLL..
...........fff..""", """
..LLL.CCCC.LLL..
..LLL......LLL..
..LLL......fff..
..fff...........""",], 8)
MS_UP = walker("""
......P..P......
.....PPPPPP.....
....HPPPPPPH....
...BBBBppBBBB...
..BBBBBqqBBBBB..
..BBBBBppBBBBB..
..CCCCCqqCCCCC..
..BBBBBppBBBBB..
..BBBBBqqBBBBB..
...BBBBppBBBB...
..LLBBBTTBBBLL..""", ["""
..LLL..TT..LLL..
..LLL..T...LLL..
..LLL......LLL..
..fff......fff..""", """
..LLL..TT..LLL..
..LLL...T..LLL..
..fff......LLL..
...........fff..""", """
..LLL..TT..LLL..
..LLL..T...LLL..
..LLL......fff..
..fff...........""",], 8)
MS_LEFT = walker("""
........R.R.R.R.........
.......RBRBRBRBR........
.PPPP.BBBBCCBBBBB.......
PPPPPPBBBBCCBBBBBB......
PPPPPPPBBBCCBBBBBBTT....
HHekHHCBBBCCBBBBBBBTTT..
HHHHHHCBBBCCBBBBBBB..TT.
nHHHHHCBBBCCBBBBBBB.....
HmmmmmCBBBCCBBBBBB......
wHwHwHCBBBBBBBBBB.......
.HHHH.LLLBBBBLLL........""", ["""
....LLL.....LLL.........
....LLL.....LLL.........
....LL......LL..........
...fff.....fff..........""", """
...LLL.......LLL........
..LLL.........LLL.......
..LL...........LL.......
.fff...........fff......""", """
.....LLL...LLL..........
.....LLL...LLL..........
.....LL....LL...........
....fff...fff...........""",], 4)
put("poochyena", "poochyena.png", "Poochyena", "person32x32", "sw_poochyena", "OBJ_EVENT_PAL_TAG_POOCHYENA",
    "MASSIFF: snapping Tatooine lizard-hound kept by Tuskens (replaces Poochyena).",
    "Group lg2: sandy reptile hide, bony brow plate and dorsal spikes, amber eyes, toothy jaw, Tusken leather collar. Own palette sw_poochyena.pal (NPC layout).",
    materials={"H": "s", "B": "s!", "P": "a@", "R": "a", "L": "s", "C": "c", "T": "s"},
    legend={"e": 8, "k": 15, "n": 4, "m": 10, "w": 14, "f": 7, "p": 5, "q": 6},
    accept={**CREATURE, "skin_tones": "the skin ramp is the reptile hide"},
    frames={"down": MS_DOWN[0], "up": MS_UP[0], "left": MS_LEFT[0], "down_a": MS_DOWN[1], "down_b": MS_DOWN[2],
            "up_a": MS_UP[1], "up_b": MS_UP[2], "left_a": MS_LEFT[1], "left_b": MS_LEFT[2]})

# ====================================================================== SCURRIER (enemy_zigzagoon.png)
# The large walking version of the small SCURRIER (art/zigzagoon_ow.yaml), same design and the same
# colours: sand fur (ramp c), curled cream ram horns (skin ramp), pink nose (ramp a), dark spine
# ridge, a blue scrap bolt carried in its mouth (ramp b), black eyes with a white glint, and the
# long ringed tail it zigzags with. sw_enemy_zigzagoon.pal is npc_1's colours in NPC layout, so the
# small and large Scurrier match exactly.
write_pal("enemy_zigzagoon", [(115, 197, 164),
                              (255, 213, 180), (255, 197, 148), (222, 148, 115), (123, 65, 65),
                              (255, 164, 180), (213, 106, 123), (139, 65, 82),
                              (148, 197, 246), (90, 139, 189), (16, 49, 82),
                              (180, 164, 98), (123, 115, 65), (57, 57, 24),
                              (255, 255, 255), (0, 0, 0)])
SC_DOWN = walker("""
.hhh........hhh.
hh.hhHHddHHhh.hh
h..hHHHddHHHh..h
hh.HHHHHHHHHH.hh
.hHHHHHHHHHHHHh.
..HHHkHHHHkHHH..
..HHWkHHHWkHHH..
...HHHHNnHHHH...
..BBBHHXxHHBBB..
.BBBBBBxxBBBBBB.
.BBBBBBBBBBBBBB.
..BBBBBBBBBBBB..""", ["""
..ffBBBBBBBBff..
..ff........ff..
..ff........ff..""", """
..ffBBBBBBBBff..
..ff........ff..
............ff..""", """
..ffBBBBBBBBff..
..ff........ff..
..ff............""",], 8)
SC_UP = walker("""
.hhh........hhh.
hh.hhHHHHHHhh.hh
h..hHHHHHHHHh..h
hh.HHHHHHHHHH.hh
.hHHHHHddHHHHHh.
..HHHHHddHHHHH..
..HHHHHddHHHHH..
...HHHHddHHHH...
..BBBBBddBBBBB..
.BBBBBBddBBBBBB.
.BBBBBBddBBBBBB.
..BBBBBTTBBBBB..
...BBBBttBBBB...""", ["""
..ff...TT...ff..
..ff...tt...ff..
..ff........ff..""", """
..ff...TT...ff..
..ff...tt.......
............ff..""", """
..ff...TT...ff..
.......tt...ff..
..ff............""",], 8)
SC_LEFT = walker("""
.........hhh............
........hh.hh...........
........h...h...........
......HHHhhhh...........
.....HHHHHHHH......TT...
....HHkHHHHHHBBBB.TttT..
...NHWkHHHHHddddBBTTtT..
...nnHHHHHHBBBBBBBttTT..
....XxHHHHBBBBBBBBBTT...
....xx.BBBBBBBBBBBB.....""", ["""
......BBBBBBBBBBBB......
.......ff.....ff........
.......ff.....ff........""", """
......BBBBBBBBBBBB......
......ff.......ff.......
.....ff.........ff......""", """
......BBBBBBBBBBBB......
........ff...ff.........
........ff...ff.........""",], 4)
put("enemy_zigzagoon", "enemy_zigzagoon.png", "EnemyZigzagoon", "person32x32", "sw_enemy_zigzagoon",
    "OBJ_EVENT_PAL_TAG_ZIGZAGOON",
    "SCURRIER: Tatooine scrap-hunting rodent with curled horns, large walking version (replaces the enemy Zigzagoon).",
    "Group lg2: same design as zigzagoon_ow: sand fur, curled cream ram horns, pink nose, dark spine ridge, blue scrap bolt in its mouth, ringed tail. Own palette sw_enemy_zigzagoon.pal (npc_1 colours).",
    materials={"H": "c@", "B": "c", "h": "s", "x": "b", "d": "c", "f": "c", "T": "c", "t": "s"},
    legend={"k": 15, "W": 14, "n": 6, "N": 5, "X": 8},
    accept=CREATURE,
    frames={"down": SC_DOWN[0], "up": SC_UP[0], "left": SC_LEFT[0], "down_a": SC_DOWN[1], "down_b": SC_DOWN[2],
            "up_a": SC_UP[1], "up_b": SC_UP[2], "left_a": SC_LEFT[1], "left_b": SC_LEFT[2]})

if __name__ == "__main__":
    pass

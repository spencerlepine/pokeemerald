"""Large-companion group 2, second iteration (BRIEF4): the 32x32 legendary / story creatures redrawn
as stacks of shaded FORMS (the `%` material flag, DECISIONS D17) seen from Emerald's top-down camera.

SHIFTSTAR (deoxys), ASHLA / BOGAN (latias_latios), the three WARDENS (regi), SLOTHFURY hauling a
cargo crate (vigoroth), MASSIFF (poochyena) and the large SCURRIER (enemy_zigzagoon).
Frame layout, footprint and palettes are kept from batches/r_lg2.py; the art is new.
Run from the tool folder:   python batches/r_lg2b.py [name ...]
"""
import math
import sys

import yaml

sys.path.insert(0, "batches")
from helpers import PK  # noqa: E402

W = 32


# ---------------------------------------------------------------- canvas: paint forms by letter
class Canvas:
    """A 32x32 letter grid. Forms are painted back to front; a later paint overwrites."""

    def __init__(self, rows=None):
        self.g = [list(r) for r in rows] if rows else [["."] * W for _ in range(32)]

    def copy(self):
        return Canvas(["".join(r) for r in self.g])

    def set(self, x, y, ch):
        if 0 <= x < W and 0 <= y < 32:
            self.g[y][x] = ch

    def ell(self, ch, cx, cy, rx, ry, only=None):
        """Filled ellipse; cx, cy, rx, ry in pixel units (centre on a pixel boundary for even widths).
        only: paint only over these letters (None = everywhere)."""
        for y in range(32):
            for x in range(W):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    if only is None or self.g[y][x] in only:
                        self.g[y][x] = ch
        return self

    def rect(self, ch, x0, y0, x1, y1, only=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if only is None or self.g[y][x] in only:
                    self.set(x, y, ch)
        return self

    def poly(self, ch, pts, only=None):
        """Filled polygon (pixel centres inside, even-odd), pts = [(x, y), ...] in pixel units."""
        n = len(pts)
        for y in range(32):
            py = y + 0.5
            xs = []
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= py < y1) or (y1 <= py < y0):
                    xs.append(x0 + (py - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(W):
                    if a <= x + 0.5 <= b and (only is None or self.g[y][x] in only):
                        self.g[y][x] = ch
        return self

    def band(self, ch, x0, y0, x1, y1, r, only=None):
        """A thick line (capsule) of radius r from (x0, y0) to (x1, y1): arms, tails, necks."""
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1
        for y in range(32):
            for x in range(W):
                px, py = x + 0.5, y + 0.5
                t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
                qx, qy = x0 + t * dx, y0 + t * dy
                if (px - qx) ** 2 + (py - qy) ** 2 <= r * r and (only is None or self.g[y][x] in only):
                    self.g[y][x] = ch
        return self

    def line(self, ch, x0, y0, x1, y1, only=None):
        """1 px line (Bresenham) from (x0, y0) to (x1, y1): wing bones, creases."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        x, y = x0, y0
        while True:
            if 0 <= x < W and 0 <= y < 32 and (only is None or self.g[y][x] in only):
                self.g[y][x] = ch
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return self

    def paint(self, text, x, y):
        """Hand edit: rows of letters at (x, y); '_' keeps the pixel under it, '.' clears it."""
        rows = [r.strip() for r in text.strip("\n").split("\n")]
        for dy, r in enumerate(rows):
            for dx, c in enumerate(r):
                if c != "_":
                    self.set(x + dx, y + dy, c)
        return self

    def dots(self, ch, pts, only=None):
        for x, y in pts:
            if only is None or self.g[y][x] in only:
                self.set(x, y, ch)
        return self

    def replace(self, a, b):
        for y in range(32):
            for x in range(W):
                if self.g[y][x] == a:
                    self.g[y][x] = b
        return self

    def mirror(self, flip=None):
        """Copy the left half onto the right (x -> 31 - x); flip renames letters on the right side."""
        flip = flip or {}
        for y in range(32):
            for x in range(16):
                c = self.g[y][x]
                self.g[y][31 - x] = flip.get(c, c)
        return self

    def shift(self, dx=0, dy=0, rows=None):
        """Move the whole grid (or only rows y0..y1 inclusive) by dx, dy; pixels moved out are lost."""
        out = [["."] * W for _ in range(32)]
        y0, y1 = rows if rows else (0, 31)
        for y in range(32):
            for x in range(W):
                c = self.g[y][x]
                if c == ".":
                    continue
                if y0 <= y <= y1:
                    X, Y = x + dx, y + dy
                else:
                    X, Y = x, y
                if 0 <= X < W and 0 <= Y < 32:
                    out[Y][X] = c
        self.g = out
        return self

    def lay(self, other):
        """Overlay another canvas's opaque pixels on this one."""
        for y in range(32):
            for x in range(W):
                if other.g[y][x] != ".":
                    self.g[y][x] = other.g[y][x]
        return self

    def rows(self):
        return ["".join(r) for r in self.g]


def write_pal(stem, cols):
    assert len(cols) == 16 and tuple(cols[0]) == (115, 197, 164)
    with open(f"palettes/sw_{stem}.pal", "w", newline="\r\n") as f:
        f.write("JASC-PAL\n0100\n16\n" + "".join(f"{r} {g} {b}\n" for r, g, b in cols))


def put(name, replaces, gi, kit, pal, tag, desc, notes, materials, legend, accept, frames):
    fr = {}
    for k, cv in frames.items():
        rows = cv.rows() if isinstance(cv, Canvas) else cv
        assert len(rows) == 32 and all(len(r) == W for r in rows), (name, k)
        used = {c for r in rows for c in r} - {"."}
        missing = used - set(materials) - set(legend)
        assert not missing, (name, k, missing)
        fr[k] = "\n".join(rows) + "\n"
    d = {"name": name, "description": desc, "kit": kit, "replaces": PK + replaces, "graphics_info": gi,
         "notes": notes, "palette": pal, "palette_tag": tag, "shade": True, "materials": materials,
         "legend": legend, "accept": accept, "frames": fr}
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


CREATURE = {"skin_tones": "creature: no human skin", "hair_rows": "creature: no hair",
            "eye_row": "creature eyes, not a human face"}
BUILDERS = {}


def builder(fn):
    BUILDERS[fn.__name__] = fn
    return fn


# ====================================================================== SLOTHFURY (vigoroth.png)
# Restless Nal Hutta swamp sloth hauling a steel cargo crate. Palette sw_vigoroth (NPC layout):
# skin = tan face mask / claws, a = moss-green fur, b = crate steel, c = dark brown mane and tail.
#
# Forms plan, side frames (facing left; camera 45 degrees above and in front), front to back:
#   1 crate            b, hard pixels: lid lit, two riveted panels, rust corner straps (c), stencil
#   2 near arm + hand  A% moss: from the shoulder hump down-left over the crate edge to the ground;
#                      ivory hook claws (skin light) at the hand
#   3 head             S% skin: low over the crate corner; top of the skull takes the upper rows,
#                      the dark sloth eye-band at ~65%, nose at the bottom-left corner
#   4 mane crest       M% c: shaggy cap on the back of the skull, tuft spikes (hard c dark)
#   5 shoulder hump    H% moss: the high point of the silhouette, right behind the head
#   6 torso / back     T% moss: big lit back sloping down to the rear; fur strokes along the curve
#   7 hind haunch      Q% moss: over the rear of the torso, lowest of the body forms
#   8 hind foot        skin: claws on the ground at row 28 (vanilla stands on row 28 side-on)
#   9 tail tuft        U% c: short shaggy tail at the back
# Back frames (f3, f4): mane crest, head-back (mane), two shoulders, big back with the spine
# stripe, two long arms with claws on the ground, two hind legs, feet on row 31 as vanilla.
write_pal("vigoroth", [(115, 197, 164),
                       (232, 216, 176), (200, 168, 120), (152, 112, 72), (88, 56, 32),    # face mask, claws
                       (176, 192, 104), (112, 136, 64), (56, 72, 32),                     # A moss fur
                       (200, 208, 216), (128, 136, 160), (64, 72, 96),                    # B crate steel
                       (160, 120, 72), (104, 72, 48), (56, 40, 24),                       # C mane
                       (255, 255, 255), (16, 16, 24)])
VG_MAT = {"A": "a%", "S": "s%", "M": "c%", "H": "a%", "T": "a%", "Q": "a%", "U": "c%",
          "B": "a%", "D": "a%", "E": "a%", "F": "a%", "G": "a%", "I": "a%", "J": "c%"}
# hard pixels: crate (o outline, t lid light, p panel mid, r rust strap), claws c, eyes, fur strokes
VG_LEG = {"o": 10, "t": 8, "p": 9, "r": 12, "R": 13, "X": 14, "c": 1, "d": 3, "k": 15, "e": 4,
          "f": 7, "m": 13, "n": 6, "l": 11}


def vg_crate(cv, x, y):
    """Steel cargo crate seen a little from above: lit top face, two riveted front panels with rust
    corner straps and a white stencil."""
    cv.paint("""
.oooooooooo.
otttttttttto
ottttttttpto
oooooooooooo
orppppppppro
oppXpppppppo
opppppppppXo
oppppppppppo
oppppppppppo
orppppppppro
oooooooooooo
orppppppppro
oppppXpppppo
oppppXpXpppo
oppppppppppo
orppppppppro
oooooooooooo
""", x, y)
    return cv


def vg_side(hand_dx=0, foot_dx=0, bob=0):
    """Side frame facing left. hand_dx / foot_dx swing the near hand and hind foot; bob drops the
    body (not the feet) one row."""
    cv = Canvas()
    cv.ell("U", 28.5, 17.5, 2.8, 4.0)                       # tail tuft
    cv.dots("U", [(30, 13), (31, 15), (31, 19)])            # tuft spikes
    cv.ell("T", 21.0, 16.5, 9.5, 8.5)                       # torso: big lit back
    cv.ell("Q", 22.0, 22.0, 5.5, 4.0)                       # hind haunch
    cv.ell("H", 17.0, 11.5, 5.5, 4.5)                       # shoulder hump (high point)
    # fur strokes along the back curve (a dark), drawn on the lit tops only
    cv.dots("f", [(20, 10), (21, 11), (24, 12), (25, 13), (27, 15), (28, 16),
                  (18, 16), (19, 17), (22, 17), (23, 18), (20, 21), (21, 22), (25, 21), (26, 22)])
    vg_crate(cv, 0, 9)                                      # the crate, in front of the torso
    cv.ell("S", 11.5, 12.5, 5.0, 4.5)                       # head: x7..16, y8..16
    cv.ell("M", 16.0, 8.0, 4.0, 2.5)                        # mane cap on the back-top of the skull
    cv.dots("M", [(13, 5), (14, 5), (16, 5), (17, 5), (14, 4), (17, 4), (19, 6), (20, 7)])  # tufts
    cv.dots("l", [(15, 7), (16, 7)])                        # lit strands on the mane
    # face: dark sloth eye-band at ~65% of the head height, eyes with a glint, black nose, mouth
    cv.paint("""
_rrrrrrrr
rrkXrrkXr
e_dd_dd__
""", 7, 13)
    # near arm: from under the hump down-left over the crate's right edge to the hand on the ground
    cv.band("A", 16.5, 16.0, 7.5 + hand_dx, 24.5, 2.5)
    cv.ell("A", 6.5 + hand_dx, 26.0, 3.2, 2.0)              # hand
    cv.paint("c_c_c", 4 + hand_dx, 28)                      # three hook claws
    cv.paint("d_d_d", 4 + hand_dx, 27)                      # claw roots
    # hind foot with claws
    cv.ell("E", 20.5 + foot_dx, 26.5, 3.5, 1.8)
    cv.paint("cc", 17 + foot_dx, 28).paint("dd", 17 + foot_dx, 27)
    if bob:
        # vanilla drops the whole figure (crate included) one row and redraws the feet
        feet = cv.copy()
        cv.shift(0, 1)
        for y in (27, 28):
            for x in range(W):
                cv.g[y][x] = feet.g[y][x] if feet.g[y][x] != "." else cv.g[y][x]
        # keep the ground row clean: nothing below row 28
        for x in range(W):
            cv.g[29][x] = "."
    return cv


def vg_back(fidget=0):
    """Back view (frames 3 and 4): mane crest, two shoulders, the big back with the spine stripe,
    two long arms with hook claws on the ground, two hind legs; feet on row 31 like vanilla."""
    cv = Canvas()
    cv.ell("T", 16.0, 17.5, 10.5, 9.0)                      # back
    cv.ell("B", 9.0, 13.0, 4.5, 3.5)                        # near shoulders (left, right)
    cv.ell("D", 23.0, 13.0, 4.5, 3.5)
    cv.ell("J", 16.0, 7.5, 4.5, 3.5)                        # head from behind: all mane
    cv.dots("J", [(12, 3), (13, 3), (15, 3), (16, 3), (18, 3), (19, 3), (13, 2), (16, 2), (19, 2),
                  (11, 5), (10, 6), (20, 5), (21, 6)])  # crest tufts
    cv.dots("l", [(14, 6), (15, 6), (17, 6)])               # lit strands on the mane
    # spine stripe and fur strokes
    cv.dots("m", [(16, 11), (16, 12), (15, 14), (16, 15), (16, 17), (15, 18), (16, 20), (16, 21)])
    cv.dots("f", [(8, 12), (9, 13), (22, 12), (23, 13), (10, 18), (11, 19), (21, 18), (22, 19),
                  (12, 23), (13, 24), (19, 23), (20, 24)])
    # arms hang from the shoulders to the ground
    cv.band("E", 6.5, 15.0, 4.5 + fidget, 25.5, 2.5)
    cv.band("F", 25.5, 15.0, 27.5 - fidget, 25.5, 2.5)
    cv.ell("E", 4.5 + fidget, 26.5, 3.0, 1.8)
    cv.ell("F", 27.5 - fidget, 26.5, 3.0, 1.8)
    cv.paint("c_c", 3 + fidget, 29).paint("c_c", 27 - fidget, 29)
    cv.paint("d_d", 3 + fidget, 28).paint("d_d", 27 - fidget, 28)
    # legs and feet
    cv.ell("G", 10.5, 28.0, 3.5, 3.0)
    cv.ell("I", 21.5, 28.0, 3.5, 3.0)
    cv.paint("c_c_c", 8, 31).paint("c_c_c", 19, 31)
    if fidget:
        # the body rocks down a row, the feet stay planted
        feet = cv.copy()
        cv.shift(0, 1, rows=(0, 27))
        for y in (28, 29, 30, 31):
            for x in range(W):
                if feet.g[y][x] in "GIcd":
                    cv.g[y][x] = feet.g[y][x]
    return cv


@builder
def vigoroth():
    put("vigoroth", "vigoroth.png", "VigorothCarryingBox / VigorothFacingAway", "frames32x32_5", "sw_vigoroth",
        "OBJ_EVENT_PAL_TAG_VIGOROTH",
        "SLOTHFURY: restless Nal Hutta swamp sloth hauling a cargo crate (replaces Vigoroth).",
        "Group lg2b: moss fur, dark mane, tan face mask with the sloth eye-band, ivory hook claws, steel cargo crate. Own palette sw_vigoroth.pal (NPC layout).",
        materials=VG_MAT, legend=VG_LEG,
        accept={**CREATURE, "skin_tones": "the skin ramp is the face mask and claws"},
        frames={"down": vg_side(), "f1": vg_side(-2, 2, 1), "f2": vg_side(2, -2, 1),
                "f3": vg_back(), "f4": vg_back(1)})


# ====================================================================== MASSIFF (poochyena.png)
# Tusken guard beast of Tatooine, 9-frame 32x32 walker on Poochyena's footprint (down/up x9..22,
# y17..31; side x4..28, y15..30). Palette sw_poochyena (NPC layout): skin = sandy reptile hide,
# a = bone (brow plate, dorsal spikes, claws), b = amber eyes / red maw, c = Tusken leather collar.
#
# Forms plan, down frame (camera 45 degrees above), front to back:
#   1 dorsal spikes   hard bone pixels: three spike tips above the skull, a row down the spine (up)
#   2 brow plate      B% bone: a bony plate on the top of the skull
#   3 skull           S% skin: wide low head, the crown takes the upper 60%, eyes at ~65%
#   4 muzzle / jaw    J% skin: broad muzzle at the bottom edge with the wide toothy maw (teeth 14,
#                     maw b dark, tongue b mid)
#   5 collar          C  c! flat leather band with a white stud, under the jaw
#   6 near forelegs   L% / N% skin: broad, lowest, claws in bone
#   7 body / haunches T% skin: behind the head, showing at the sides
write_pal("poochyena", [(115, 197, 164),
                        (232, 208, 160), (200, 168, 120), (160, 120, 80), (96, 64, 40),    # hide
                        (240, 232, 208), (184, 176, 152), (112, 104, 88),                  # A bone
                        (248, 176, 64), (200, 64, 48), (104, 24, 32),                      # B eyes, maw
                        (176, 120, 72), (120, 80, 48), (64, 40, 24),                       # C harness
                        (255, 255, 255), (24, 16, 16)])
MS_MAT = {"S": "s%", "J": "s%", "T": "s%", "L": "s%", "N": "s%", "Q": "s%", "H": "s%", "U": "s%",
          "B": "a%", "C": "c!"}
MS_LEG = {"u": 7, "P": 5, "q": 6, "e": 8, "k": 15, "M": 10, "g": 9, "w": 14, "X": 14, "d": 4, "y": 3, "x": 13, "o": 11}


def ms_spike(cv, x, y):
    """A bone spike: tip row y, base row y+1, centred on x."""
    cv.paint(".u.\nuPu", x - 1, y)


def ms_legs(cv, lx, rx, step, top=27, bottom=31, claw="o", lift=1):
    """Two legs (left letter L at lx, right N at rx), 4 wide. step 1: left leg forward (stretched
    to the ground), right lifted `lift` rows; step 2 the other way; the body bobs up a row in both."""
    for ch, x, s in (("L", lx, 1), ("N", rx, 2)):
        y0 = top - 1 if step else top
        y1 = bottom if (step == 0 or step == s) else bottom - lift
        cv.ell(ch, x + 2.0, (y0 + y1 + 1) / 2, 2.0, (y1 - y0 + 1) / 2)
        if claw:
            cv.dots(claw, [(x, y1), (x + 3, y1)])   # claws


def ms_down(step=0):
    cv = Canvas()
    cv.ell("T", 16.0, 26.5, 7.5, 3.0)                       # haunches behind
    cv.ell("S", 16.0, 23.0, 7.0, 5.0)                       # skull x9..22 y18..27
    cv.ell("B", 16.0, 19.5, 4.5, 2.5)                       # brow plate, lit on top
    cv.paint("ek______ke", 11, 24)                          # small amber eyes, pupils inward
    cv.paint("_y____y_", 12, 26)                            # nostrils
    cv.paint("wMwMggMwMw", 11, 27)                          # the wide toothy maw on the jaw's edge
    cv.paint("CCXCCC", 13, 28)                              # collar under the jaw
    for x in (12, 16, 20):
        ms_spike(cv, x, 16)
    if step:
        cv.shift(0, -1)
    ms_legs(cv, 9, 19, step)
    return cv


def ms_up(step=0):
    cv = Canvas()
    cv.ell("T", 16.0, 24.5, 7.0, 5.0)                       # back x9..22 y20..29
    cv.ell("H", 16.0, 20.0, 4.5, 3.0)                       # top of the head
    cv.ell("Q", 10.5, 26.5, 3.5, 3.2)                       # haunches
    cv.ell("U", 21.5, 26.5, 3.5, 3.2)
    cv.dots("d", [(13, 24), (19, 24), (16, 29)])            # deep creases between the haunches
    cv.paint("dd", 15, 29).paint(".d", 15, 30)              # tail stub
    for y in (16, 20, 23, 26):
        ms_spike(cv, 16, y)
    cv.dots("y", [(11, 22), (12, 23), (20, 22), (19, 23), (12, 26), (20, 26), (13, 19), (19, 19)])  # scales
    cv.paint("CCCCCCCC", 12, 23).dots("X", [(15, 23)])      # collar seen from behind
    if step:
        cv.shift(0, -1)
    ms_legs(cv, 9, 19, step)
    return cv


def ms_left(step=0):
    cv = Canvas()
    cv.ell("U", 26.0, 21.5, 2.5, 2.0)                       # tail stub
    cv.ell("T", 19.0, 24.0, 7.5, 4.5)                       # body x12..26 y20..28
    cv.ell("Q", 22.5, 24.5, 4.0, 3.5)                       # hind haunch
    cv.paint("CC\nCC\nCC\nXC\nCC\nCC", 13, 20)              # collar band around the neck
    cv.ell("S", 10.5, 20.5, 5.0, 4.5)                       # skull x6..15 y16..25
    cv.ell("B", 11.5, 18.0, 3.5, 1.8)                       # brow plate
    cv.ell("J", 8.0, 23.5, 4.0, 2.5)                        # muzzle x4..12 y21..26
    cv.paint("ke", 8, 21)                                   # near eye
    cv.paint("d", 5, 23)                                    # nostril
    cv.paint("wMwMgMw", 4, 25)                              # maw
    for x, y in ((11, 14), (15, 15), (19, 17), (23, 18)):
        ms_spike(cv, x, y)
    cv.dots("y", [(17, 22), (18, 23), (21, 21), (22, 22), (16, 25)])  # scale strokes along the flank
    if step:
        cv.shift(0, -1)
    # near foreleg and hind leg, feet on row 30 side-on like vanilla
    ms_legs(cv, 12, 21, step, top=26, bottom=30)
    return cv


@builder
def poochyena():
    put("poochyena", "poochyena.png", "Poochyena", "person32x32", "sw_poochyena", "OBJ_EVENT_PAL_TAG_POOCHYENA",
        "MASSIFF: snapping Tatooine lizard-hound kept by Tuskens (replaces Poochyena).",
        "Group lg2b: sandy reptile hide, bony brow plate and dorsal spikes, small amber eyes, wide toothy maw, Tusken leather collar. Own palette sw_poochyena.pal (NPC layout).",
        materials=MS_MAT, legend=MS_LEG,
        accept={**CREATURE, "skin_tones": "the skin ramp is the reptile hide"},
        frames={"down": ms_down(), "up": ms_up(), "left": ms_left(),
                "down_a": ms_down(1), "down_b": ms_down(2), "up_a": ms_up(1), "up_b": ms_up(2),
                "left_a": ms_left(1), "left_b": ms_left(2)})


# ====================================================================== SCURRIER (enemy_zigzagoon.png)
# The large walking SCURRIER: the same design and colours as the small art/zigzagoon_ow.yaml
# (npc_1 colours in NPC layout): sand fur (ramp c), curled cream ram horns (skin), pink nose (a),
# blue scrap bolt in its mouth (b), black eyes with a white glint, dark spine ridge, ringed tail.
# Footprint as vanilla: down/up x9..22, y15..31; side x6..30, y14..30.
#
# Forms plan, down frame, front to back:
#   1 horns        hard skin pixels: a curl each side of the head, lit on top, shade inside
#   2 head         H% c: round, the crown takes the upper 60%, eyes at ~65%, nose at the bottom
#   3 nose + bolt  hard: pink nose (a), the blue bolt held in the mouth (b) under it
#   4 ridge tufts  hard c dark along the top of the head and back
#   5 chest        B% c: below the head
#   6 forelegs     L% / N% c
write_pal("enemy_zigzagoon", [(115, 197, 164),
                              (255, 213, 180), (255, 197, 148), (222, 148, 115), (123, 65, 65),
                              (255, 164, 180), (213, 106, 123), (139, 65, 82),
                              (148, 197, 246), (90, 139, 189), (16, 49, 82),
                              (180, 164, 98), (123, 115, 65), (57, 57, 24),
                              (255, 255, 255), (0, 0, 0)])
SC_MAT = {"H": "c%", "B": "c%", "L": "c%", "N": "c%", "Q": "c%", "T": "c%"}
SC_LEG = {"1": 1, "3": 3, "4": 4, "k": 15, "W": 14, "p": 5, "n": 6, "v": 7, "X": 8, "x": 9, "z": 10,
          "r": 13, "m": 12, "l": 11, "c": 1}
SC_HORN_L = """
.4444
41114
41434
.444.
"""
SC_HORN_R = "\n".join(r[::-1] for r in SC_HORN_L.strip("\n").split("\n"))


SC_WIGGLE = {0: 0, 1: -1, 2: 1}   # the head (horns, face) swings a pixel each step: it zigzags


def sc_down(step=0):
    cv = Canvas()
    d = SC_WIGGLE[step]
    cv.ell("B", 16.0, 27.0, 6.5, 3.5)                       # chest x10..22 y24..30
    cv.ell("H", 16.0 + d, 21.5, 6.5, 4.5)                   # head x10..22 y17..25
    cv.dots("r", [(13 + d, 16), (16 + d, 15), (16 + d, 16), (19 + d, 16), (11 + d, 18), (21 + d, 18)])
    cv.paint(SC_HORN_L, 7 + d, 15).paint(SC_HORN_R, 20 + d, 15)    # curled horns
    cv.paint("Wk____kW", 12 + d, 22)                        # eyes with glints
    cv.paint("ppn", 15 + d, 23).paint("nnv", 15 + d, 24)    # pink nose, shaded underneath
    cv.paint("Xxxz", 14 + d, 25)                            # the scrap bolt in its mouth
    cv.paint("zXxz", 14 + d, 26)
    if step:
        cv.shift(d, -1)                                     # bob up and sway with the step
    ms_legs(cv, 10, 18, step, claw=None, lift=2)
    return cv


def sc_up(step=0):
    cv = Canvas()
    d = SC_WIGGLE[step]
    cv.ell("B", 16.0, 26.0, 7.0, 5.0)                       # back x9..22 y21..30
    cv.ell("H", 16.0 + d, 20.5, 5.5, 3.5)                   # back of the head
    cv.paint(SC_HORN_L, 7 + d, 15).paint(SC_HORN_R, 20 + d, 15)
    # the dark spine ridge zigzags down the back
    cv.dots("r", [(16 + d, 18), (15 + d, 19), (16, 22), (17, 23), (16, 24), (15, 25), (16, 26), (17, 27)])
    cv.paint("rmmr\nrccr\nrmmr\nrccr\n.rr.", 14 - d, 27)     # ringed tail stub, swinging
    if step:
        cv.shift(d, -1)
    ms_legs(cv, 9, 19, step, claw=None, lift=2)
    return cv


def sc_left(step=0):
    cv = Canvas()
    d = SC_WIGGLE[step]
    cv.band("T", 26.5, 22.5, 29.5 + d, 16.0 - d, 1.8)        # ringed tail, up and back, swinging
    cv.dots("c", [(27, 20), (28, 20), (28 + d, 17 - d), (29 + d, 17 - d)])  # pale rings
    cv.ell("B", 20.0, 24.0, 8.0, 4.5)                       # body x12..28 y20..28
    cv.ell("Q", 23.5, 24.5, 4.0, 3.5)                       # hind haunch
    cv.dots("r", [(15, 19), (16, 20), (18, 19), (19, 20), (21, 19), (22, 20), (24, 19), (25, 20)])
    cv.ell("H", 10.5 + d, 20.5, 5.0, 4.5)                   # head x6..15 y16..25
    cv.paint(SC_HORN_L, 9 + d, 13)                          # near horn
    cv.paint("44", 15 + d, 15).paint("4", 16 + d, 16)       # far horn tip
    cv.paint("kW", 8 + d, 21)                               # eye
    cv.paint("pn", 6 + d, 22).paint("nv", 6 + d, 23)        # nose
    cv.paint("Xxz", 6 + d, 24)                              # the bolt held in the mouth
    if step:
        cv.shift(d, -1)
    ms_legs(cv, 12, 22, step, top=26, bottom=30, claw=None, lift=2)
    return cv


@builder
def enemy_zigzagoon():
    put("enemy_zigzagoon", "enemy_zigzagoon.png", "EnemyZigzagoon", "person32x32", "sw_enemy_zigzagoon",
        "OBJ_EVENT_PAL_TAG_ZIGZAGOON",
        "SCURRIER: Tatooine scrap-hunting rodent with curled horns, large walking version (replaces the enemy Zigzagoon).",
        "Group lg2b: same design as zigzagoon_ow: sand fur, curled cream ram horns, pink nose, dark spine ridge, blue scrap bolt in its mouth, ringed tail. Own palette sw_enemy_zigzagoon.pal (npc_1 colours).",
        materials=SC_MAT, legend=SC_LEG, accept=CREATURE,
        frames={"down": sc_down(), "up": sc_up(), "left": sc_left(),
                "down_a": sc_down(1), "down_b": sc_down(2), "up_a": sc_up(1), "up_b": sc_up(2),
                "left_a": sc_left(1), "left_b": sc_left(2)})


# ====================================================================== SHIFTSTAR (deoxys.png)
# Star-born shapeshifter of Atollon. Palette sw_deoxys (NPC layout): skin = pale star-glow mask,
# a = gold star core, b = teal crystal (crest, shoulder facets, tendrils), c = violet nebula body.
# Vanilla footprint: head x11..20 from row 2, arms out to x3..28, legs x7..24, feet on row 30;
# frame 1 is the shifted pose one row lower with the feet planted.
#
# Forms plan, front to back:
#   1 crystal crest    Q% b: four-pointed star standing on the crown
#   2 mask             F% skin: round glowing head, the visor slit at ~65% with two glints
#   3 star core        A@ a: small round gold core on the chest, white glint
#   4 shoulder facets  P% / R% b: teal crystal pads over the chest's shoulders, facet highlight
#   5 chest            C% c: violet torso, star specks (14)
#   6 pelvis           D% c
#   7 legs             L% / N% c: tapering to points, feet on row 30
#   8 tendrils         hard b pixels: ribbons from behind the shoulders, gold tips (a light)
write_pal("deoxys", [(115, 197, 164),
                     (232, 216, 248), (192, 168, 232), (144, 112, 200), (80, 48, 128),   # star-glow mask
                     (248, 232, 120), (232, 160, 48), (152, 80, 24),                     # A gold core
                     (152, 240, 232), (64, 184, 200), (24, 96, 128),                     # B teal crystal
                     (152, 112, 216), (96, 64, 168), (48, 24, 96),                       # C violet body
                     (255, 255, 255), (16, 8, 32)])
DX_MAT = {"Q": "b%", "F": "s%", "P": "b%", "R": "b%", "C": "c%", "A": "a%", "D": "c%", "L": "c%", "N": "c%"}
DX_LEG = {"v": 14, "X": 14, "k": 15, "o": 10, "m": 9, "l": 8, "Y": 5, "y": 6, "G": 8, "g": 11, "w": 13, "e": 4}
# the tendrils are thin ribbons the shader breaks, so they are hand-toned: o outline (b dark),
# m mid, l light, Y gold tip
DX_TENDRILS = [
    (["....ooo", "...omlo", "..omlo.", ".omlo..", ".omo...", "omlo...", "omo....", "omlo...", ".omo...", ".oYYo..", "..oyy.."], 1, 13,
     ["ooo....", "olmo...", ".olmo..", "..olmo.", "...omo.", "...olmo", "..omo..", ".omo...", ".omo...", "oYYo...", ".yy...."], 24, 13),
    (["..oooo.", ".omllo.", "omlo...", "omo....", "omlo...", ".omo...", "..omo..", "..omlo.", "...omo.", "..oYYo.", "..yy..."], 1, 13,
     ["oooo...", ".llmo..", "...omo.", "....omo", "....omo", "...omo.", "..omo..", "..omo..", "...oYo.", "...yy..", "......."], 24, 13),
]
DX_STAR = [(16, 0.5), (17.6, 4.2), (21.5, 5), (17.6, 5.8), (16, 9.5), (14.4, 5.8), (10.5, 5), (14.4, 4.2)]


def dx_frame(i):
    cv = Canvas()
    lt, lx, ly, rt, rx, ry = DX_TENDRILS[i]
    cv.paint("\n".join(r.replace(".", "_") for r in lt), lx, ly)
    cv.paint("\n".join(r.replace(".", "_") for r in rt), rx, ry)
    cv.ell("D", 16.0, 23.0, 4.5, 2.5)                       # pelvis
    cv.band("L", 14.0, 23.5, 11.0, 28.0, 2.3)               # legs taper to points
    cv.poly("L", [(9, 31), (12.5, 31), (11, 27)])
    cv.band("N", 18.0, 23.5, 21.0, 28.0, 2.3)
    cv.poly("N", [(19.5, 31), (23, 31), (21, 27)])
    cv.ell("C", 16.0, 17.0, 5.5, 5.0)                       # chest
    cv.ell("P", 9.5, 15.0, 3.5, 3.0)                        # shoulder facets
    cv.ell("R", 22.5, 15.0, 3.5, 3.0)
    cv.dots("G", [(8, 13), (9, 13), (22, 13), (23, 13), (7, 15), (24, 15)])  # facet highlights
    cv.ell("A", 16.0, 18.5, 3.0, 3.0)                       # gold star core
    cv.set(15, 17, "X")
    cv.ell("F", 16.0, 9.5, 5.5, 5.0)                        # mask x10..21 y5..14
    cv.paint("eeXkeekXee", 11, 11)                          # visor slit: glint + pupil each side
    cv.poly("Q", DX_STAR)                                   # crystal crest over the crown
    cv.dots("v", [(13, 20), (19, 19), (17, 22)])            # star specks in the nebula body
    cv.dots("w", [(11, 18), (12, 19), (21, 18), (20, 19), (12, 26), (13, 27), (19, 26), (18, 27), (16, 13), (16, 14)])  # creases
    if i:
        cv.shift(0, 1, rows=(0, 27))                        # the shifted pose, feet planted
    return cv


@builder
def deoxys():
    put("deoxys", "deoxys.png", "Deoxys", "frames32x32_2", "sw_deoxys", "OBJ_EVENT_PAL_TAG_DEOXYS",
        "SHIFTSTAR: star-born shapeshifter of Atollon (replaces Deoxys).",
        "Group lg2b: crystal star crest, glowing mask with a visor slit, gold star-core, teal shoulder facets, ribbon tendrils that change shape. Own palette sw_deoxys.pal (NPC layout).",
        materials=DX_MAT, legend=DX_LEG,
        accept={**CREATURE, "skin_tones": "the skin ramp is the star-glow mask"},
        frames={"down": dx_frame(0), "f1": dx_frame(1)})


# ====================================================================== WARDENS (regi.png)
# One frame shown on three palette tags: ROCKWARDEN NPC_2 (sandstone, red glyph glow), ICEWARDEN
# NPC_3 (lavender ice, green glow), DURAWARDEN NPC_4 (navy durasteel, magenta glow). The body is
# ramp a, the T-visor and the Aurebesh glyph strip ramp b, cracks ramp c's dark tones and the skin
# ramp's darkest (dark in every NPC palette). Vanilla footprint: dome rows 4..31, full width at the
# shoulders, legs x6..13 / x18..25, feet on row 31.
#
# Forms plan, front to back:
#   1 T-visor        hard b: glowing slit across the hood
#   2 glyph strip    hard: a recessed dark band on the chest with three Aurebesh glyphs (b light/mid)
#   3 fists          F% / G% a: at the ends of the arms, knuckle creases
#   4 legs           H% / I% a: short pillars, toe creases
#   5 chest plate    C% a: wide, below the hood
#   6 shoulders      D% / E% a: boulders either side of the hood
#   7 hood dome      A% a: the crown, lit on top, glints
RG_MAT = {"A": "a%", "C": "a%", "D": "a%", "E": "a%", "F": "a%", "G": "a%", "H": "a%", "I": "a%"}
RG_LEG = {"g": 8, "h": 9, "B": 10, "x": 13, "w": 12, "u": 11, "e": 4, "X": 14, "k": 15}


def rg_frame():
    cv = Canvas()
    cv.ell("A", 16.0, 11.5, 8.5, 7.5)                       # hood dome x8..24 y4..18
    cv.ell("C", 16.0, 22.0, 10.0, 6.0)                      # chest plate x6..26 y16..27
    cv.ell("D", 5.5, 14.5, 5.5, 4.5)                        # left shoulder boulder
    cv.ell("F", 3.5, 22.5, 3.5, 4.5)                        # left fist
    cv.ell("H", 10.0, 27.5, 4.0, 3.5)                       # left leg x6..13 y24..31
    cv.mirror({"D": "E", "F": "G", "H": "I"})
    # T-visor glowing across the hood
    cv.paint("""
BBBBBBBBBB
BgggggggggB
BBBggggBBB
...BghB...
...BBBB...
""".replace("BgggggggggB", "BggggggggB"), 11, 9)
    cv.paint("kk", 9, 31).paint("kk", 21, 31)              # black soles
    cv.dots("X", [(12, 10)]).dots("u", [(5, 12), (26, 12)])   # visor glint, lit shoulder flecks
    # recessed glyph strip with three Aurebesh glyphs
    cv.paint("""
xxxxxxxxxxxxxx
xghgxgghxhgghx
xgxgxgxhxgxgxx
xghgxhggxgghgx
xxxxxxxxxxxxxx
""", 9, 20)
    # cracks (c dark, deepest in skin dark), weathered edges (c mid / light), glints on the lit tops
    cv.paint("x_\n_x\n_x", 11, 6).paint("_x\nx_", 19, 5)
    cv.paint("x\nx_\n_e", 3, 12).paint("_x\nx_\ne_", 27, 12)
    cv.paint("xx_\n__x", 8, 26).paint("_xx\nx__", 21, 26)
    cv.paint("wx\n_w", 14, 15).paint("x_\nwu", 17, 16)
    cv.dots("x", [(2, 20), (3, 21), (29, 20), (28, 21), (4, 24), (27, 24)])   # knuckle creases
    cv.dots("X", [(13, 5), (14, 5), (3, 11), (28, 11), (8, 25), (23, 25)])
    cv.paint("x_\n_x", 21, 10).dots("x", [(9, 29), (11, 29), (20, 29), (22, 29)])  # dome crack, toe creases
    return cv


@builder
def regi():
    put("regi", "regi.png", "Regirock / Regice / Registeel", "frames32x32_1", "npc_2", "OBJ_EVENT_PAL_TAG_NPC_2",
        "ROCKWARDEN / ICEWARDEN / DURAWARDEN: ancient sentinel sealed behind Aurebesh glyphs (replaces the Regi sheet).",
        "Group lg2b: one sentinel for all three palette tags; hood dome, shoulder boulders, fists and legs on ramp a, glowing T-visor and Aurebesh glyph strip on ramp b, cracks in ramp c dark.",
        materials=RG_MAT, legend=RG_LEG, accept=CREATURE, frames={"down": rg_frame()})


# ====================================================================== ASHLA / BOGAN (latias_latios.png)
# Force dragons of Tython, hovering head-on with the wings raised (frame 0 stand, 1-2 wing beats;
# the pic table shows frame 0 for every facing). One sheet, two palettes: hide on ramp c, wing
# membranes on ramp a, the brow kyber gem on ramp b.
#   ASHLA (light moon) on NPC_4: silver-grey hide, steel-blue membranes, pink kyber.
#   BOGAN (dark moon)  on NPC_2: dark maroon hide, amber membranes, red kyber.
# Vanilla footprint: wing tips in the top corners, head x8..23 from row 2, body x3..28 to row 28.
#
# Forms plan, front to back:
#   1 horns          hard c: two swept-back horns on the crown
#   2 kyber gem      hard b: diamond on the brow
#   3 snout          J% c: short muzzle at the bottom of the head, nostrils
#   4 head           H% c: round, eyes at ~60% with glints
#   5 forearms       F% / G% c: tucked claws either side of the belly, three claws each
#   6 neck / chest   N% c
#   7 body           B% c: wide belly with scute crease rows (c dark) under lit plate tops
#   8 wing arms      E% / Z% c: the leading-edge bone from shoulder to wing tip
#   9 wings          W% / V% a: membranes raised in a V, finger bones (a dark) from the shoulder
#  10 tail           T% c: curls off to the right behind the body
LT_MAT = {"H": "c%", "J": "c%", "N": "c%", "B": "c%", "F": "c%", "G": "c%", "E": "c%", "Z": "c%",
          "W": "a%", "V": "a%", "T": "c%"}
LT_LEG = {"u": 11, "x": 13, "k": 15, "X": 14, "p": 8, "q": 9, "P": 10, "d": 7, "l": 5, "1": 1}
LT_TIP = {0: 0.5, 1: 2.5, 2: 5.5}   # wing tip x per frame: the beat lifts the wings upright


def lt_frame(i):
    tx = LT_TIP[i]
    tail = Canvas()
    tail.band("T", 22.0, 27.0, 29.5, 24.5, 1.9)
    tail.band("T", 29.5, 24.5, 30.5, 19.5, 1.4)
    cv = Canvas()
    # wing membrane and its leading-edge arm, left side
    cv.poly("W", [(tx, 0), (tx + 6, 0), (11 + tx * 0.3, 6), (13, 12), (13, 19), (6, 19), (2 + tx * 0.6, 11)])
    cv.band("E", 11.0, 16.5, tx + 2.0, 1.0, 1.3)
    cv.line("d", 11, 17, int(tx + 4), 6, only="W")          # finger bones through the membrane
    cv.line("d", 11, 17, int(3 + tx * 0.5), 12, only="W")
    cv.ell("B", 16.0, 23.0, 9.5, 5.5)                       # body x6..26 y18..28
    cv.ell("N", 16.0, 17.0, 5.0, 3.5)                       # neck / chest
    cv.ell("F", 8.0, 24.0, 3.0, 3.5)                        # forearm and claws
    cv.paint("u_u_u", 6, 28)
    cv.ell("H", 16.0, 9.5, 5.5, 4.5)                        # head x10..21 y5..14
    cv.ell("J", 16.0, 13.0, 3.5, 2.0)                       # snout
    cv.paint("__xx\n_xux\nxuu_\nxux_\nxx__", 10, 1)               # left horn, swept back and out
    cv.mirror({"W": "V", "E": "Z", "F": "G"})
    cv.paint("kX____Xk", 12, 10)                            # eyes with glints
    cv.paint("__q__\n_qpq_\nqppPq\n_qPq_\n__P__", 14, 5)        # kyber gem on the brow
    cv.paint("x__x", 14, 14)                                # nostrils
    cv.paint("11111111", 12, 21).paint("xxxxxxxx", 12, 22)  # cream belly scutes: lit top, crease
    cv.paint("11111111", 12, 24).paint("xxxxxxxx", 12, 25)
    cv.paint("1111", 14, 27)
    out = tail.lay(cv)
    return out


@builder
def latias_latios():
    put("latias_latios", "latias_latios.png", "Latias / Latios", "frames32x32_3", "npc_4", "OBJ_EVENT_PAL_TAG_NPC_4",
        "ASHLA / BOGAN: light- and dark-side Force dragons of Tython (replaces Latias / Latios).",
        "Group lg2b: one hovering dragon for both; hide on ramp c, membranes ramp a, kyber gem ramp b. Ashla on NPC_4, Bogan on NPC_2.",
        materials=LT_MAT, legend=LT_LEG, accept=CREATURE,
        frames={"down": lt_frame(0), "f1": lt_frame(1), "f2": lt_frame(2)})


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(BUILDERS)):
        BUILDERS[n]()
        print("wrote", n)

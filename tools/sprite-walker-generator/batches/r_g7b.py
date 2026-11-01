"""Group 7b: KAEL and MIRA's 32x32 action sheets (bikes, surfing, field move, fishing, watering,
underwater), in the same design as the walking sheets in r_g7.py.

These sheets have up to 27 frames in poses no hand-drawn head set could follow (wheelies, hops,
casts), so every frame is derived from its vanilla frame by rule, in palette-index mode:
- The vanilla head is found by flood-filling the hat (Brendan) / hair and bandana (May) from the
  topmost pixel; head, torso and legs bands are measured from it.
- Each band maps the player's palette indices onto kael.pal / mira.pal ramps, keeping vanilla's
  own tone structure: Brendan's white hat becomes Kael's brown hair (same tufted silhouette) and
  his green band the kyber-blue headband; May's bandana bows become rust-wrapped buns over
  chestnut hair; black clothing becomes the sand (Kael) or cream (Mira) wrap tunic with
  coloured silhouette outlines, gloves become white wraps, the bag and pack brown/chestnut.
- Vehicles: the bicycle is removed and a hover hull is drawn instead. Side views find the two
  wheel hubs (the enclosed holes of the wheel rings) and draw a slanted hull between them, so
  every wheelie and hop keeps its tilt; front/back views draw a hull seen end-on under the
  handlebars. Mach Bike -> brown SWOOP BIKE; Acro Bike -> white SPEEDER BIKE with front vanes.
- Underwater keeps the shared underwater palette and only restyles the hair cue.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_g7b.py
"""
import sys

import yaml

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import KITS, game_dir  # noqa: E402

SKIN = (1, 2, 3, 4)
HEX = ".123456789ABCDEF"


def vanilla(path):
    fr, _ = read_frames(game_dir() / (P + path), (32, 32))
    return [[list(r) for r in f] for f in fr]


def opaque_rows(f):
    ys = [y for y, r in enumerate(f) if any(r)]
    return ys[0], ys[-1]


def flood(f, start, allowed):
    h, w = len(f), len(f[0])
    seen, st = set(), [start]
    while st:
        x, y = st.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or f[y][x] not in allowed:
            continue
        seen.add((x, y))
        st += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return seen


def edge(f, x, y):
    h, w = len(f), len(f[0])
    return any(not (0 <= x + dx < w and 0 <= y + dy < h) or not f[y + dy][x + dx]
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


EYE_ROWS = (0, 99)


def is_eye(f, x, y):
    w = len(f[0])
    return EYE_ROWS[0] <= y <= EYE_ROWS[1] and 0 < x < w - 1 and f[y][x - 1] in SKIN and f[y][x + 1] in SKIN


def holes(f, y0):
    """Transparent pixels at or below row y0 not reachable from the frame border: wheel hubs."""
    h, w = len(f), len(f[0])
    out = set()
    border = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    reach, st = set(), [p for p in border if not f[p[1]][p[0]]]
    while st:
        x, y = st.pop()
        if (x, y) in reach or not (0 <= x < w and 0 <= y < h) or f[y][x]:
            continue
        reach.add((x, y))
        st += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(y0, h):
        for x in range(w):
            if not f[y][x] and (x, y) not in reach:
                out.add((x, y))
    return out


def clusters(pts, d=3):
    cl = []
    for p in sorted(pts):
        for c in cl:
            if any(abs(p[0] - q[0]) <= d and abs(p[1] - q[1]) <= d for q in c):
                c.append(p)
                break
        else:
            cl.append([p])
    return [(sum(x for x, _ in c) / len(c), sum(y for _, y in c) / len(c)) for c in cl]


# ---------------------------------------------------------------- characters
class Kael:
    pal, tag_note = "kael", "kael.pal"
    hat = {5, 6, 7, 9, 14, 10, 11}
    face_rows, torso_rows = 4, 5
    eyes = (1, 4)
    zone, hub = 9, 7  # rows below the hat bottom: vehicle zone (front views), wheel-hub search

    @staticmethod
    def head(f, x, y, v):
        if v in SKIN:
            return v
        if v == 8:
            return 15 if is_eye(f, x, y) else 10
        return {14: 8, 9: 9, 5: 10, 6: 10, 7: 10, 15: 10, 10: 11, 11: 12, 12: 12, 13: 13}[v]

    @staticmethod
    def torso(f, x, y, v):
        if v in SKIN:
            return v
        if v == 15:
            return 7 if edge(f, x, y) else 6
        return {8: 5, 5: 6, 6: 6, 7: 6, 14: 8, 9: 9, 10: 8, 11: 9, 12: 14, 13: 5}[v]

    @staticmethod
    def legs(f, x, y, v, boot):
        if v == 15:
            return 10 if boot else (7 if edge(f, x, y) else 6)
        return {1: 5, 2: 5, 3: 6, 4: 7, 8: 5, 5: 6, 6: 6, 7: 7, 14: 8, 9: 9, 10: 9, 11: 10, 12: 9, 13: 10}[v]

    # hover hulls: outline, light, mid, trim, glow, underside
    swoop = {"o": 10, "l": 8, "m": 9, "t": 5, "g": 11, "k": 15}
    speeder = {"o": 7, "l": 14, "m": 5, "t": 6, "g": 11, "k": 15}


class Mira:
    pal, tag_note = "mira", "mira.pal"
    hat = {7, 8, 9, 10, 11, 14}
    face_rows, torso_rows = 1, 6
    eyes = (-2, 0)
    zone, hub = 7, 3

    @staticmethod
    def head(f, x, y, v):
        if v in SKIN:
            return v
        if v == 8:
            return 15 if is_eye(f, x, y) else 13
        if v == 7:
            up = f[y - 1][x] if y else 0
            return 11 if up in (0, 10, 11, 14, 9) else 12
        return {15: 13, 10: 8, 11: 9, 14: 11, 9: 12, 5: 10, 6: 10, 12: 9, 13: 10}[v]

    @staticmethod
    def torso(f, x, y, v):
        if v in SKIN:
            return v
        if v == 15:
            return 7 if edge(f, x, y) else 6
        return {12: 9, 13: 10, 5: 5, 6: 6, 9: 5, 14: 14, 10: 11, 11: 12, 7: 12, 8: 13}[v]

    @staticmethod
    def legs(f, x, y, v, boot):
        if v == 15:
            return 13 if boot else (7 if edge(f, x, y) else 6)
        return {1: 5, 2: 5, 3: 6, 4: 7, 5: 5, 6: 6, 7: 12, 8: 13, 9: 14, 14: 14, 10: 11, 11: 12, 12: 12, 13: 13}[v]

    swoop = {"o": 13, "l": 11, "m": 12, "t": 5, "g": 8, "k": 15}
    speeder = {"o": 7, "l": 14, "m": 5, "t": 6, "g": 8, "k": 15}


# ---------------------------------------------------------------- frame conversion
def head_box(f, who):
    # the hat / hair is the largest connected patch of its colours near the top (a fishing rod
    # in the same navy can reach higher, but it is thin)
    top, _ = opaque_rows(f)
    hat, seen = set(), set()
    for y in range(top, min(32, top + 14)):
        for x in range(32):
            if (x, y) not in seen and f[y][x] in who.hat:
                comp = flood(f, (x, y), who.hat)
                seen |= comp
                if len(comp) > len(hat):
                    hat = comp
    t0 = min(y for _, y in hat)
    hat = {(x, y) for x, y in hat if y <= t0 + 11}  # May's hair can touch dark torso pixels
    x0, x1 = min(x for x, _ in hat), max(x for x, _ in hat)
    for y in range(t0, t0 + 12):  # strands split off by the face (May's side hair)
        for x in range(max(0, x0 - 3), min(32, x1 + 4)):
            if f[y][x] in who.hat and f[y][x] != 5:
                hat.add((x, y))
    xs = [x for x, _ in hat]
    ys = [y for _, y in hat]
    return min(xs), max(xs), min(ys), max(ys), hat


def convert(f, who, vehicle=None, zone_top=None):
    global EYE_ROWS
    hx0, hx1, ht, hb, hat = head_box(f, who)
    EYE_ROWS = (hb + who.eyes[0], hb + who.eyes[1])
    head_bot = hb + who.face_rows
    torso_bot = head_bot + who.torso_rows
    _, bottom = opaque_rows(f)
    g = [[0] * 32 for _ in range(32)]
    for y in range(32):
        for x in range(32):
            v = f[y][x]
            if not v:
                continue
            if (x, y) in hat or (y <= head_bot and hx0 - 1 <= x <= hx1 + 1):
                g[y][x] = who.head(f, x, y, v)
            elif y <= torso_bot:
                g[y][x] = who.torso(f, x, y, v)
            else:
                g[y][x] = who.legs(f, x, y, v, y >= bottom - 1)
    if vehicle:
        draw_vehicle(g, f, who, vehicle, zone_top if zone_top is not None else hb + who.zone, hb + who.hub)
    return g


def draw_vehicle(g, f, who, kind, zt, hub_top):
    c = getattr(who, kind)
    hs = clusters(holes(f, hub_top))
    if len(hs) >= 2:  # side view: hull between the two hubs (front = left)
        hs = sorted(hs)
        (xf, yf), (xb, yb) = hs[0], hs[-1]
        xs = [x for y in range(int(min(yf, yb)) - 2, 32) for x in range(32) if f[y][x]]
        lo, hi = min(xs), max(xs)
        ytop = int(round(min(yf, yb))) - 2
        lo = min(lo, int(xf) - 5)
        for y in range(ytop, 32):
            for x in range(lo, hi + 1):
                g[y][x] = 0
        speeder = kind == "speeder"
        nose, tail = int(xf) - (3 if speeder else 4), int(round(xb)) + 3
        for x in range(max(0, nose - (4 if speeder else 0)), min(31, tail) + 1):
            t = (x - xf) / (xb - xf) if xb != xf else 0
            yc = int(round(yf + (yb - yf) * t))
            col = {}
            if x < nose:  # speeder steering rod and vane
                col = {yc: c["o"]} if x > nose - 3 else {yc - 1: c["o"], yc: c["l"], yc + 1: c["o"]}
            elif x == nose:
                col = {yc: c["o"], yc + 1: c["o"]}
            elif x == nose + 1:
                col = {yc - 1: c["o"], yc: c["l"], yc + 1: c["m"], yc + 2: c["o"]}
            elif x >= tail - 1:
                col = {yc - 1: c["o"], yc: c["k"] if x == tail - 1 else c["g"], yc + 1: c["o"]}
                if x == tail:
                    col = {yc - 1: c["g"], yc: c["g"], yc + 1: c["g"]}
            else:
                col = {yc - 2: c["o"], yc - 1: c["l"], yc: c["t"], yc + 1: c["m"], yc + 2: c["k"] if speeder else c["o"]}
                if speeder:
                    col[yc - 2] = c["o"] if x % 5 else c["l"]
            for y, v in col.items():
                if 0 <= y < 32:
                    g[y][x] = v
    else:  # front or back view: hull end-on under the handlebars
        pts = [(x, y) for y in range(zt, 32) for x in range(32) if f[y][x]]
        if not pts:
            return
        cx = round(sum(x for x, _ in pts) / len(pts) - 0.5)
        yb = max(y for _, y in pts)
        for x, y in pts:
            g[y][x] = 0
        if kind == "speeder":
            rows = ["..oooo..", "oolllloo", "oltggtlo", ".ommmmo.", "..okko.."]
        else:
            rows = ["..oooo..", ".ollllo.", "oltggtlo", ".ommmmo.", "..okko.."]
        n = max(3, min(5, yb - zt + 1))
        if n < 5:
            rows = [rows[0], rows[2], rows[4]] if n == 3 else [rows[0], rows[1], rows[2], rows[4]]
        for dy, r in enumerate(rows):
            for dx, ch in enumerate(r):
                x = cx - 3 + dx
                if ch != "." and 0 <= x < 32 and zt + dy < 32:
                    g[zt + dy][x] = c[ch]


def underwater(f, who):
    """Shared underwater palette: keep it; restyle the hair cue only."""
    g = [r[:] for r in f]
    top, _ = opaque_rows(f)
    brim = next(y for y in range(top, 32) if sum(1 for v in f[y] if v == 8) >= 5)
    if who is Kael:
        for y in range(top, brim):  # white hat -> darker tousled hair, a light headband above the brim
            for x in range(32):
                if g[y][x] == 9:
                    g[y][x] = 6
        for x in range(32):
            if f[brim - 1][x] and f[brim - 1][x] != 15:
                g[brim - 1][x] = 9
        xs = [x for x in range(32) if f[top][x]]
        for x in (min(xs) - 3, max(xs) + 2):  # extra tufts beside the spike
            if 0 <= x < 32 and f[top + 1][x]:
                g[top][x] = 15
    else:
        for y in range(top, top + 3):  # bandana bows -> two wrapped hair buns (mid tone, dark outline)
            for x in range(32):
                if g[y][x] == 9:
                    g[y][x] = 7
                elif g[y][x] == 5:
                    g[y][x] = 9
    return g


# ---------------------------------------------------------------- sheets
SHEETS = {
    "mach_bike": ("person32x32", "swoop", "the brown SWOOP BIKE, a low hover bike", "{G}MachBike"),
    "acro_bike": ("frames32x32_27", "speeder", "the white SPEEDER BIKE (Endor style) in every wheelie and hop pose", "{G}AcroBike"),
    "surfing": ("frames32x32_6", None, "riding a companion across water (the rider; the mount is a separate sprite)", "{G}Surfing"),
    "field_move": ("frames32x32_5", None, "using a field move, calling the companion with a holo-puck", "{G}FieldMove"),
    "fishing": ("frames32x32_12", None, "fishing with a rod", "{G}Fishing"),
    "watering": ("frames32x32_6", None, "watering fruit with a sand-coloured water canteen", "{G}Watering"),
    "underwater": ("frames32x32_4", None, "diving (silhouette with the hair cue)", "{G}Underwater"),
}
# per-frame zone tops for the vehicle where the hat-based guess misses (frame index -> row)
ZONE = {}


def gi_name(who, stem):
    base = {"mach_bike": "MachBike", "acro_bike": "AcroBike", "surfing": "Surfing", "field_move": "FieldMove",
            "fishing": "Fishing", "watering": "Watering", "underwater": "Underwater"}[stem]
    return ("Brendan" if who is Kael else "May") + base


def main(only=None):
    for who, person in ((Kael, "brendan"), (Mira, "may")):
        for stem, (kit, veh, subj, _) in SHEETS.items():
            name = f"{person}_{stem}"
            if only and name not in only:
                continue
            path = f"{person}/{stem}.png"
            van = vanilla(path)
            order = KITS[kit]["order"]
            assert len(van) == len(order), (name, len(van), len(order))
            frames = {}
            for i, (n, f) in enumerate(zip(order, van)):
                if stem == "underwater":
                    g = underwater(f, who)
                else:
                    g = convert(f, who, veh, ZONE.get((name, i)))
                frames[n] = "\n".join("".join(HEX[v] for v in r) for r in g) + "\n"
            char = "KAEL" if who is Kael else "MIRA"
            if stem == "underwater":
                pal, tag = "player_underwater", "OBJ_EVENT_PAL_TAG_PLAYER_UNDERWATER"
                pnote = "stays on PLAYER_UNDERWATER (the shared underwater palette)"
            else:
                pal = who.pal
                tag = "OBJ_EVENT_PAL_TAG_" + ("BRENDAN" if who is Kael else "MAY")
                pnote = (f"moves to the new {who.tag_note} (install replaces "
                         f"{'brendan' if who is Kael else 'may'}.pal and its reflection)")
            d = {"name": name, "description": f"{char}, the player, {subj} (replaces {person}/{stem}.png).",
                 "kit": kit, "replaces": P + path, "graphics_info": gi_name(who, stem),
                 "notes": f"Group 7b: derived frame by frame from the vanilla sheet by rule (r_g7b.py); {pnote}.",
                 "palette": pal, "palette_tag": tag, "legend": {ch: i for i, ch in enumerate(HEX)},
                 "accept": {}, "frames": frames}
            open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))
            print("wrote", name)


if __name__ == "__main__":
    main(sys.argv[1:])

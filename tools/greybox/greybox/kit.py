"""Building categories, added one at a time and reviewed before the next (owner's rule, 2026-11-02).

Each category is a small set of greybox models registered into build.BUILDS. Every piece in a category
must pass the simplicity guardrail, so the kit stays as plain as the original game's art:
  - at most BUDGET["solids"] solids per model (boxes, cylinders, domes, cones, cuts),
  - colours only from the piece palette (wall, roof, trim, glass, light, dark), no ad-hoc shades,
  - round shapes only through solid.py's primitives, which apply the 45° projection rule.
Variation comes from the seed (heights, counts, which side a part sits on), never from detail.

`python3 -m greybox kit <category> [--grey]` draws wiki/world/greybox/_kit-<category>[-grey].png: every piece at
its sizes in three seeded variations, on plain ground with a person and a house for scale.
"""
from . import solid as S
from .style import shade

BUDGET = {"solids": 16}


def palette(m):
    """The only colours a category piece may use."""
    if m.grey:
        light = (236, 236, 236)
    else:
        light = (255, 214, 120)
    return {"wall": m.wall, "roof": m.roof, "trim": m.trim, "glass": m.glass, "light": light,
            "dark": shade(m.trim, -0.45)}


def check(m, name):
    """The guardrail. Raises if a piece is too busy or uses a colour outside its palette."""
    sols = m.sc.solids
    if len(sols) > BUDGET["solids"]:
        raise ValueError(f"{name}: {len(sols)} solids, budget is {BUDGET['solids']}")
    ok = {tuple(int(v) for v in c) for c in palette(m).values()}
    for s in sols:
        for c in (s.side, s.top):
            if c is not None and tuple(int(v) for v in c) not in ok:
                raise ValueError(f"{name}: colour {c} is not in the piece palette")
    return len(sols)


# --------------------------------------------------------------------------- category 1: doorless structures
# Utility and signal pieces with no door: a player walks around them, never into them.
K = S.K


def _fit(m, a, top):
    """Clamp a round footprint radius so the oval (depth 2aK) plus `top` px of height fit the box."""
    return max(2.0, min(a, m.W / 2 - 1, (m.H - top) / (2 * K)))


def d_vaporator(m):
    """Moisture vaporator: a thin column on a base ring, one to three cooling fins, a pointed cap."""
    p = palette(m)
    cx = m.W / 2
    a = _fit(m, 5.5, 20)
    cy = a * K + 1
    h = (m.H - cy - a * K - 5) * (0.75 + 0.08 * m.r(1, 4))
    m.add(S.cylinder(cx, cy, a, 0, 0, 4, p["trim"], p["roof"]),
          S.cylinder(cx, cy, a * 0.42, 0, 4, h, p["wall"], p["roof"]),
          S.cone(cx, cy, a * 0.5, 0, h, 5, p["roof"]))
    for i in range(1 + m.r(2, 3)):
        z = h * (0.35 + 0.22 * i)
        m.add(S.cylinder(cx, cy, a * (0.95 - 0.12 * i), 0, z, z + 2, p["roof"]))


def d_mast(m):
    """Signal mast: four legs, two or three cross rings, an antenna and a red-light beacon."""
    p = palette(m)
    s = min(m.W - 4, 14)
    x0 = (m.W - s) / 2
    y0 = 1
    h = (m.H - s - 10) * (0.8 + 0.07 * m.r(1, 4))
    t = 2
    for lx, ly in ((x0, y0), (x0 + s - t, y0), (x0, y0 + s - t), (x0 + s - t, y0 + s - t)):
        m.add(S.box(lx, ly, 0, lx + t, ly + t, h, p["wall"], p["roof"]))
    n = 2 + m.r(2, 2)
    for i in range(n):
        z = h * (i + 1) / (n + 0.4) - 1
        m.add(S.box(x0, y0, z, x0 + s, y0 + s, z + 2, p["trim"]),
              S.box(x0 + t, y0 + t, z - 1, x0 + s - t, y0 + s - t, z + 3, p["trim"], subtract=True))
    cx, cy = m.W / 2, y0 + s / 2
    m.add(S.box(x0, y0, h, x0 + s, y0 + s, h + 2, p["roof"]),
          S.box(cx - 1, cy - 1, h + 2, cx + 1, cy + 1, h + 9, p["trim"]),
          S.box(cx - 1.5, cy - 1.5, h + 9, cx + 1.5, cy + 1.5, h + 11, p["light"]))


def d_dish(m):
    """Sky dish: a block pedestal, a neck, a bowl open to the sky and a feed spike over its centre."""
    p = palette(m)
    cx = m.W / 2
    a = _fit(m, m.W / 2 - 2, 18)
    cy = a * K + 1
    s = a * 0.5
    z = 6 + 3 * m.r(1, 3)
    m.add(S.box(cx - s, cy - s * K, 0, cx + s, cy + s * K, 6, p["wall"], p["roof"]),
          S.cylinder(cx, cy, a * 0.18, 0, 6, z, p["trim"]),
          S.cylinder(cx, cy, a, 0, z, z + 5, p["roof"], p["roof"]),
          S.dome(cx, cy, a - 1.5, 0, z + 2, None, p["wall"], subtract=True),
          S.box(cx - 0.8, cy - 0.8, z + 2, cx + 0.8, cy + 0.8, z + 5 + a * 0.5, p["trim"]),
          S.box(cx - 1.5, cy - 1.5, z + 5 + a * 0.5, cx + 1.5, cy + 1.5, z + 7 + a * 0.5, p["light"]))


def d_beacon(m):
    """Navigation beacon: a tapered octagonal pylon with trim bands and a lit cap."""
    p = palette(m)
    w = min(m.W - 2, 12)
    x0 = (m.W - w) / 2
    k = w * 0.3
    poly = [(x0 + k, 0), (x0 + w - k, 0), (x0 + w, k), (x0 + w, w * K - k * 0.5), (x0 + w - k, w * K),
            (x0 + k, w * K), (x0, w * K - k * 0.5), (x0, k)]
    h = (m.H - w * K - 6) * (0.7 + 0.1 * m.r(1, 4))
    m.add(S.prism(poly, 0, h, p["wall"], p["roof"], taper=w * 0.22))
    for i in range(1 + m.r(2, 2)):
        z = 4 + i * 8
        m.add(S.prism(poly, z, z + 2, p["trim"], taper=0))
    cx, cy = m.W / 2, w * K / 2
    m.add(S.box(cx - 2, cy - 1.5, h, cx + 2, cy + 1.5, h + 4, p["light"]))


def d_tanks(m):
    """Fuel tanks: two or three upright tanks with domed caps on a slab, joined by a pipe."""
    p = palette(m)
    n = 2 + (m.cw >= 4 and m.r(1, 2))
    a = min((m.W - 4) / (2 * n) - 1, 12)
    cy = a * K + 3
    hmax = m.H - 2 * a * K - a * K - 6
    m.add(S.box(1, 1, 0, m.W - 1, cy + a * K + 2, 3, p["trim"], p["roof"]))
    xs = [2 + a + 1 + i * (m.W - 4 - 2 * a - 2) / max(1, n - 1) for i in range(n)]
    for i, x in enumerate(xs):
        h = hmax * (0.75 + 0.12 * m.r(10 + i, 3))
        m.add(S.cylinder(x, cy, a, 0, 3, h, p["wall"]), S.dome(x, cy, a, 0, h, None, p["roof"]),
              S.cylinder(x, cy, a + 0.6, 0, h * 0.55, h * 0.55 + 2, p["trim"]))
    m.add(S.box(xs[0], cy - 1, 10, xs[-1], cy + 1, 12, p["trim"]))


def d_stack(m):
    """Exhaust stack: one or two tapered round chimneys on a plinth, hollow at the top."""
    p = palette(m)
    n = 1 + (m.cw >= 3 and m.r(1, 2) == 0)
    a = min((m.W - 4) / (2 * n) - 1, 11)
    cy = a * K + 2
    m.add(S.box(1, 0.5, 0, m.W - 1, cy + a * K + 1.5, 5, p["trim"], p["roof"]))
    for i in range(n):
        x = (m.W / 2) if n == 1 else (2 + a + 1 + i * (m.W - 6 - 2 * a))
        h = (m.H - 2 * a * K - 4) * (0.8 + 0.1 * m.r(4 + i, 3) - 0.15 * i)
        m.add(S.prism(S.ring_pts(x, cy, a, a * K, 24), 5, h, p["wall"], p["roof"], taper=a * 0.3),
              S.cylinder(x, cy, a * 0.72, 0, h - 1.5, h + 0.5, p["roof"]),
              S.cylinder(x, cy, a * 0.55, 0, h - 4, h + 1, p["dark"], p["dark"], subtract=True))


def d_relay(m):
    """Sensor relay: a low slab with three to five rods of different heights, each with a lit tip."""
    p = palette(m)
    D = min(m.H * 0.4, 14)
    m.add(S.box(1, 1, 0, m.W - 1, D, 4, p["wall"], p["roof"]))
    n = 3 + m.r(1, 3)
    for i in range(n):
        x = 4 + i * (m.W - 8) / (n - 1)
        y = 3 + (D - 6) * (m.r(10 + i, 3) / 2)
        h = 10 + (m.H - D - 14) * (0.35 + 0.2 * m.r(20 + i, 4))
        m.add(S.box(x - 0.8, y - 0.8, 4, x + 0.8, y + 0.8, h, p["trim"]),
              S.box(x - 1.6, y - 1.2, h, x + 1.6, y + 1.2, h + 2.5, p["light"]))


def d_crates(m):
    """Cargo stack: wide crates in two colours, some stacked two high, laid out by the seed."""
    p = palette(m)
    W = m.W
    w, dp, hz = 14, 10, 9
    k = 0
    for gy in (11, 1):
        x = 1 + 3 * m.r(k + 3, 2)
        while x + w <= W - 1:
            k += 1
            if m.r(k, 4) == 0:
                x += w // 2
                continue
            col = p["wall"] if m.r(k + 99, 2) else p["roof"]
            m.add(S.box(x, gy, 0, x + w, gy + dp, hz, col, p["trim"]))
            if gy == 11 and m.r(k + 50, 2):
                m.add(S.box(x + 1, gy + 1, hz, x + w - 1, gy + dp - 1, 2 * hz - 1, p["roof"] if col == p["wall"] else p["wall"], p["trim"]))
            x += w + 1


def d_core(m):
    """Generator core: an octagonal plinth, a glass core cylinder and a capped top ring."""
    p = palette(m)
    cx = m.W / 2
    a = _fit(m, m.W / 2 - 2, 26)
    cy = a * K + 1
    k = a * 0.4
    poly = [(cx - a + k, cy - a * K), (cx + a - k, cy - a * K), (cx + a, cy - a * K + k * K),
            (cx + a, cy + a * K - k * K), (cx + a - k, cy + a * K), (cx - a + k, cy + a * K),
            (cx - a, cy + a * K - k * K), (cx - a, cy - a * K + k * K)]
    h = (m.H - 2 * a * K - 6) * (0.75 + 0.1 * m.r(1, 3))
    m.add(S.prism(poly, 0, 6, p["wall"], p["roof"]),
          S.cylinder(cx, cy, a * 0.5, 0, 6, h, p["glass"]),
          S.cylinder(cx, cy, a * 0.62, 0, h, h + 3, p["roof"], p["roof"]))
    for i in range(1 + m.r(2, 2)):
        z = 6 + (h - 6) * (i + 1) / (3 + m.r(2, 2))
        m.add(S.cylinder(cx, cy, a * 0.56, 0, z, z + 2, p["trim"]))


# name -> (model, sizes in cells)
DOORLESS = {
    "vaporator": (d_vaporator, [(1, 2), (1, 3)]),
    "mast": (d_mast, [(1, 4), (2, 5)]),
    "dish": (d_dish, [(2, 3), (3, 3)]),
    "beacon": (d_beacon, [(1, 2), (1, 3)]),
    "tanks": (d_tanks, [(3, 3), (4, 3)]),
    "stack": (d_stack, [(2, 3), (3, 4)]),
    "relay": (d_relay, [(2, 2), (3, 3)]),
    "crates": (d_crates, [(2, 3), (3, 3)]),
    "core": (d_core, [(2, 3), (3, 4)]),
}

# --------------------------------------------------------------------------- category 2: sunken pieces
# Cut into the ground. The terrain is a see-through slab (its top shows the map's ground), and a pit is a
# subtractive solid allowed below ground, so the ray sees the pit's north wall and floor, never the south
# wall. Doors in a pit sit in its north wall, facing the player.


def _slab(m, depth):
    p = palette(m)
    return S.box(-2, -4, -depth - 6, m.W + 2, m.H + 8, 0, p["trim"], hide_top=True, below=True, outline=False)


def _pit(x0, y0, x1, y1, depth, wall, floor):
    return S.box(x0, y0, -depth, x1, y1, 1, wall, floor, subtract=True, below=True)


def _round_pit(cx, cy, a, depth, wall, floor, top=1):
    return S.cylinder(cx, cy, a, 0, -depth, top, wall, floor, subtract=True, below=True)


def _recess(x, yn, z0, w, h, col):
    """A doorway or hatch cut into a pit's north wall (at y = yn), facing south."""
    return S.box(x - w / 2, yn - 1, z0, x + w / 2, yn + 4, z0 + h, col, subtract=True, below=True)


def s_pithome(m):
    """Pit home: a round courtyard sunk into the ground, doorways in its far wall, an entry hut on the rim."""
    p = palette(m)
    dep = 16 + 2 * m.r(1, 3)
    a = min(m.W / 2 - 10, (m.H - 6) / (2 * K))
    cx = m.W / 2 + (6 if m.r(2, 2) else -6)
    cy = a * K + 3
    yn = cy + a * K
    m.add(_slab(m, dep), _round_pit(cx, cy, a, dep, p["wall"], p["roof"]))
    n = 1 + m.r(3, 3)
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * 14
        yw = cy + a * K * (1 - ((x - cx) / a) ** 2) ** 0.5
        m.add(_recess(x, yw, -dep, 8, 12, p["dark"]))
    hx = 9 if cx > m.W / 2 else m.W - 9
    m.add(S.cylinder(hx, cy + 2, 7, 0, 0, 5, p["wall"]), S.dome(hx, cy + 2, 7, 0, 5, None, p["roof"]),
          S.box(hx - 2.5, cy + 2 - 7 * K - 1, 0, hx + 2.5, cy + 2 - 7 * K + 1.5, 7, p["dark"], subtract=True))


def s_stairwell(m):
    """Stairwell: a rectangular cut with steps running down toward the viewer into a passage under the
    south rim, and a low rail along the far edge."""
    p = palette(m)
    dep = 18
    x0, x1 = 3, m.W - 3
    y0, y1 = 2, min(m.H - 4, 30)
    m.add(_slab(m, dep), _pit(x0, y0, x1, y1, dep, p["wall"], p["roof"]))
    n = 4 + m.r(1, 2)
    sw = (x1 - x0) * (0.55 if m.r(2, 2) else 1.0)
    sx = x0 if m.r(3, 2) else x1 - sw
    L = (y1 - y0) - 4
    for i in range(n):
        ya = y1 - L * (i + 1) / n
        col = p["roof"] if i % 2 else p["wall"]
        m.add(S.box(sx, ya, -dep, sx + sw, y1, -dep * (i + 1) / (n + 1), p["trim"], col, below=True))
    m.add(S.box(x0 - 1, y1, 0, x1 + 1, y1 + 2, 4, p["trim"]))


def s_hatch(m):
    """Hatch: a round collar in the ground, either shut with a lid or open over a dark shaft and ladder."""
    p = palette(m)
    a = min(m.W / 2 - 2, (m.H - 6) / (2 * K) - 1)
    cx, cy = m.W / 2, a * K + 2
    m.add(_slab(m, 30), S.cylinder(cx, cy, a, 0, 0, 2.5, p["trim"], p["roof"]))
    if m.r(1, 2):
        m.add(_round_pit(cx, cy, a * 0.7, 30, p["dark"], p["dark"], top=3))
        for z in range(-4, -26, -5):
            m.add(S.box(cx - 3, cy + a * 0.7 * K - 1.5, z, cx + 3, cy + a * 0.7 * K, z + 1, p["trim"], below=True))
    else:
        m.add(S.cylinder(cx, cy, a * 0.72, 0, 2.5, 4, p["roof"]),
              S.box(cx - 1, cy - a * 0.5 * K, 4, cx + 1, cy + a * 0.5 * K, 5, p["trim"]))


def s_grate(m):
    """Vent grate: a square shaft with bars across the top and a lit fan housing far below."""
    p = palette(m)
    dep = 12
    s = min(m.W - 6, m.H - 6, 30)
    x0, y0 = (m.W - s) / 2, 3
    m.add(_slab(m, dep + 4), _pit(x0, y0, x0 + s, y0 + s, dep, p["trim"], p["dark"]),
          S.box(x0 - 2, y0 - 2, 0, x0 + s + 2, y0 + s + 2, 1.5, p["trim"], p["roof"]),
          S.box(x0, y0, -1, x0 + s, y0 + s, 2, p["trim"], subtract=True, below=True),
          S.box(x0 + s * 0.25, y0 + s * 0.3, -dep, x0 + s * 0.75, y0 + s * 0.9, -dep + 3, p["light"], below=True))
    n = 3 + m.r(1, 3)
    for i in range(n):
        x = x0 + (i + 0.5) * s / n
        m.add(S.box(x - 1, y0 - 1, 0, x + 1, y0 + s + 1, 1.5, p["roof"]))


def s_trench(m):
    """Trench: a long narrow cut with braced walls and a bunker door at one end."""
    p = palette(m)
    dep = 16
    w = 16 + 2 * m.r(1, 3)
    y0 = 3
    x0, x1 = 3, m.W - 3
    m.add(_slab(m, dep), _pit(x0, y0, x1, y0 + w, dep, p["trim"], p["roof"]))
    xd = x1 - 10 if m.r(2, 2) else x0 + 10
    m.add(_recess(xd, y0 + w, -dep, 8, 12, p["dark"]))
    k = 0
    for x in range(int(x0) + 12, int(x1) - 6, 18):
        k += 1
        if abs(x - xd) > 8:
            m.add(S.box(x, y0 + w - 2, -dep, x + 2, y0 + w, 0, p["trim"], below=True))
    m.add(S.box(x0 - 1, y0 + w, 0, x1 + 1, y0 + w + 3, 3, p["roof"], p["roof"]))


def s_sunken_bay(m):
    """Sunken landing bay: a deep octagonal pit with a ringed pad on its floor and two doors in the far wall."""
    p = palette(m)
    dep = 22
    W = m.W
    D = min(m.H - 6, W * K + 8)
    k = min(14, W * 0.18)
    x0, y0, x1, y1 = 3, 3, W - 3, 3 + D
    poly = [(x0 + k, y0), (x1 - k, y0), (x1, y0 + k * K), (x1, y1 - k * K), (x1 - k, y1), (x0 + k, y1),
            (x0, y1 - k * K), (x0, y0 + k * K)]
    cx, cy = W / 2, (y0 + y1) / 2
    a = min(W / 2 - 14, (D / 2 - 4) / K)
    m.add(_slab(m, dep), S.prism(poly, -dep, 1, p["trim"], p["roof"], subtract=True, below=True),
          S.cylinder(cx, cy, a, 0, -dep, -dep + 1, p["trim"], p["trim"], below=True),
          S.cylinder(cx, cy, a - 2.5, 0, -dep, -dep + 1.4, p["roof"], p["roof"], below=True))
    for x in (x0 + k + 10, x1 - k - 10):
        m.add(_recess(x, y1, -dep, 10, 14, p["dark"]))
    m.add(S.box(x0 + k, y1, 0, x1 - k, y1 + 2, 3, p["trim"]))


def s_well(m):
    """Well or cistern: a stone collar over a round shaft with water shining at the bottom."""
    p = palette(m)
    a = min(m.W / 2 - 2, (m.H - 8) / (2 * K) - 1)
    cx, cy = m.W / 2, a * K + 2
    m.add(_slab(m, 20), S.cylinder(cx, cy, a, 0, 0, 5, p["wall"], p["roof"]),
          _round_pit(cx, cy, a * 0.7, 10, p["wall"], p["glass"], top=6))
    if m.r(1, 2):
        m.add(S.box(cx - a, cy - 1, 5, cx - a + 2, cy + 1, 16, p["trim"]),
              S.box(cx + a - 2, cy - 1, 5, cx + a, cy + 1, 16, p["trim"]),
              S.box(cx - a, cy - 1, 16, cx + a, cy + 1, 18, p["roof"]))


def s_mineshaft(m):
    """Mine shaft: a square shaft dropping out of sight under a head frame with a winch wheel."""
    p = palette(m)
    s = min(m.W - 12, 26)
    x0, y0 = (m.W - s) / 2, 4
    h = min(m.H - s - 12, 40) * (0.8 + 0.1 * m.r(1, 3))
    m.add(_slab(m, 40), _pit(x0, y0, x0 + s, y0 + s, 40, p["wall"], p["dark"]),
          S.box(x0 - 3, y0 - 3, 0, x0 + s + 3, y0 + s + 3, 2, p["trim"], p["roof"]),
          S.box(x0, y0, -1, x0 + s, y0 + s, 3, p["trim"], subtract=True, below=True))
    cy = y0 + s / 2
    for x in (x0 - 3, x0 + s + 1):
        m.add(S.box(x, cy - 1, 2, x + 2, cy + 1, h, p["wall"], p["roof"]))
    m.add(S.box(x0 - 3, cy - 1.5, h, x0 + s + 3, cy + 1.5, h + 3, p["roof"], p["roof"]),
          S.cylinder(m.W / 2, cy, 5, 0, h + 3, h + 5, p["trim"]),
          S.box(m.W / 2 - 0.5, cy - 0.5, 8, m.W / 2 + 0.5, cy + 0.5, h, p["trim"]))


SUNKEN = {
    "pit-home": (s_pithome, [(4, 3), (5, 4)]),
    "stairwell": (s_stairwell, [(2, 3), (3, 3)]),
    "hatch": (s_hatch, [(1, 1), (2, 2)]),
    "grate": (s_grate, [(2, 2), (3, 3)]),
    "trench": (s_trench, [(4, 2), (6, 2)]),
    "sunken-bay": (s_sunken_bay, [(5, 4), (6, 5)]),
    "well": (s_well, [(2, 2), (2, 3)]),
    "mineshaft": (s_mineshaft, [(3, 4), (3, 5)]),
}


# --------------------------------------------------------------------------- category 3: Imperial military
# Angular, sloped walls, dark slits and blast doors. Shown in Imperial greys (MATERIAL), not planet colours.


def _door(m, x, yf, w=8, h=12, z0=0):
    """A door recess in a south face at y = yf."""
    return S.box(x - w / 2, yf - 1, z0, x + w / 2, yf + 3, z0 + h, palette(m)["dark"], subtract=True)


def _band(x0, x1, yf, z, hgt, col):
    """A recessed window or slit band across a south face."""
    return S.box(x0, yf - 1, z, x1, yf + 1.2, z + hgt, col, subtract=True)


def i_barricade(m):
    """Barricade: a row of sloped blast blocks with gaps, laid out by the seed."""
    p = palette(m)
    D = min(m.H - 12, 12)
    x = 1 + 2 * m.r(1, 2)
    k = 0
    while x < m.W - 8:
        k += 1
        w = 10 + 4 * m.r(k + 3, 3)
        w = min(w, m.W - 1 - x)
        h = 8 + 4 * m.r(k + 11, 2)
        m.add(S.prism([(x, 0), (x + w, 0), (x + w, D), (x, D)], 0, h, p["wall"], p["roof"], taper=3))
        m.add(S.box(x + 2, -0.5, h * 0.4, x + w - 2, 0.8, h * 0.4 + 1.5, p["trim"], subtract=True))
        x += w + 3 + 3 * m.r(k + 7, 2)


def i_sentry(m):
    """Sentry tower: four legs, a cab with a dark window band, a sloped cap and a red light."""
    p = palette(m)
    s = min(m.W - 4, 22)
    x0 = (m.W - s) / 2
    D = s * 0.7
    cab = 14
    h = (m.H - D - cab - 8) * (0.85 + 0.07 * m.r(1, 3))
    t = 2.5
    for lx in (x0 + 2, x0 + s - 2 - t):
        for ly in (2, D - 2 - t):
            m.add(S.box(lx, ly, 0, lx + t, ly + t, h, p["trim"]))
    m.add(S.box(x0 + 2, 2, h * 0.45, x0 + s - 2, 2 + t, h * 0.45 + 2, p["trim"]))
    m.add(S.prism([(x0, 0), (x0 + s, 0), (x0 + s, D), (x0, D)], h, h + cab, p["wall"], p["roof"], taper=-2),
          _band(x0 + 2, x0 + s - 2, -1.5, h + 6, 4, p["dark"]),
          S.prism([(x0 - 2, -2), (x0 + s + 2, -2), (x0 + s + 2, D + 2), (x0 - 2, D + 2)], h + cab, h + cab + 4,
                  p["roof"], p["roof"], taper=4),
          S.box(m.W / 2 - 1.5, D / 2 - 1, h + cab + 4, m.W / 2 + 1.5, D / 2 + 1, h + cab + 6, p["light"]))


def i_garage(m):
    """Walker garage: a tall slab-sided hall with a sloped front, a huge blast door and roof lights."""
    p = palette(m)
    W = m.W
    h = m.H * 0.45
    D = m.H - h - 4
    m.add(S.prism([(1, 0), (W - 1, 0), (W - 1, D), (1, D)], 0, h, p["wall"], p["roof"], taper=4))
    dw = W * (0.45 + 0.1 * m.r(1, 2))
    m.add(S.box(W / 2 - dw / 2, -1, 0, W / 2 + dw / 2, 5, h * 0.82, p["dark"], subtract=True),
          S.box(W / 2 - dw / 2 + 2, 1.5, 0, W / 2 + dw / 2 - 2, 3, h * 0.82 - 2, p["trim"]))
    for i in range(2 + m.r(2, 2)):
        z = 4 + i * (h * 0.82 - 6) / 3
        m.add(S.box(W / 2 - dw / 2 + 2, 1, z, W / 2 + dw / 2 - 2, 2, z + 1.5, p["roof"]))
    m.add(S.box(W * 0.2, D * 0.3, h, W * 0.8, D * 0.7, h + 3, p["roof"], p["roof"]),
          S.box(5, 2.5, h - 4, 8, 3, h - 2, p["light"]), S.box(W - 8, 2.5, h - 4, W - 5, 3, h - 2, p["light"]))


def i_barracks(m):
    """Barracks: a long low block with sloped side walls, a slit window band, a door and roof vents."""
    p = palette(m)
    W = m.W
    h = 18
    D = m.H - h - 6
    m.add(S.prism([(1, 0), (W - 1, 0), (W - 1, D), (1, D)], 0, h, p["wall"], p["roof"], taper=3))
    xd = W * (0.25 + 0.25 * m.r(1, 3))
    m.add(_door(m, xd, 1.5, 8, 12))
    m.add(_band(6, xd - 7, 1.5, 9, 3, p["dark"]), _band(xd + 7, W - 6, 1.5, 9, 3, p["dark"]))
    n = 2 + m.r(2, 3)
    for i in range(n):
        x = 10 + i * (W - 26) / max(1, n - 1)
        m.add(S.box(x, D * 0.35, h, x + 6, D * 0.35 + 6, h + 4, p["trim"], p["roof"]))


def i_pillbox(m):
    """Pillbox: a low hexagonal bunker with sloped walls, a dark firing slit and a hatch on top."""
    p = palette(m)
    W = m.W
    D = min(m.H - 14, W * K)
    k = W * 0.22
    poly = [(k, 0), (W - k, 0), (W - 1, D / 2), (W - k, D), (k, D), (1, D / 2)]
    h = 12 + 2 * m.r(1, 2)
    m.add(S.prism(poly, 0, h, p["wall"], p["roof"], taper=4),
          _band(k + 2, W - k - 2, 1.5, h * 0.55, 2.5, p["dark"]),
          S.cylinder(W / 2, D / 2, 4, 0, h, h + 2, p["trim"], p["roof"]))


def i_command(m):
    """Command post: two sloped tiers stepping back, a dark window band and a mast with a light."""
    p = palette(m)
    W = m.W
    h1, h2 = 16, 12
    D = m.H - h1 - h2 - 10
    m.add(S.prism([(1, 0), (W - 1, 0), (W - 1, D), (1, D)], 0, h1, p["wall"], p["roof"], taper=3),
          _door(m, W / 2, 1.5, 10, 12))
    x0, x1 = W * 0.2, W * 0.8
    y0, y1 = D * 0.3, D - 4
    m.add(S.prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], h1, h1 + h2, p["wall"], p["roof"], taper=-1.5),
          _band(x0 + 2, x1 - 2, y0 - 1, h1 + 4, 4, p["dark"]))
    mx = x1 - 4 if m.r(1, 2) else x0 + 4
    m.add(S.box(mx - 1, y1 - 3, h1 + h2, mx + 1, y1 - 1, h1 + h2 + 10, p["trim"]),
          S.box(mx - 1.5, y1 - 3.5, h1 + h2 + 10, mx + 1.5, y1 - 0.5, h1 + h2 + 12, p["light"]))


def i_gate(m):
    """Gate: two blocky towers with sloped faces and a closed blast door between them."""
    p = palette(m)
    W = m.W
    tw = W * 0.24
    D = 18
    h = m.H - D - 6
    for x in (1, W - 1 - tw):
        m.add(S.prism([(x, 0), (x + tw, 0), (x + tw, D), (x, D)], 0, h, p["wall"], p["roof"], taper=3),
              _band(x + 3, x + tw - 3, 1.5, h * 0.7, 3, p["dark"]))
    m.add(S.box(1 + tw, 4, 0, W - 1 - tw, D - 4, h * 0.72, p["trim"], p["roof"]),
          S.box(W / 2 - 0.6, 3, 0, W / 2 + 0.6, 5, h * 0.72 - 2, p["dark"], subtract=True),
          S.box(1 + tw, 3, h * 0.72 - 4, W - 1 - tw, 4.5, h * 0.72 - 2.5, p["light"]))


IMPERIAL = {
    "barricade": (i_barricade, [(3, 1), (5, 2)]),
    "sentry": (i_sentry, [(2, 4), (2, 5)]),
    "garage": (i_garage, [(4, 5), (5, 6)]),
    "barracks": (i_barracks, [(5, 3), (6, 3)]),
    "pillbox": (i_pillbox, [(2, 2), (3, 2)]),
    "command": (i_command, [(4, 4), (5, 5)]),
    "gate": (i_gate, [(4, 4), (6, 5)]),
}


# --------------------------------------------------------------------------- shared: irregular natural shapes
def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p_ in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p_) <= 0:
            lo.pop()
        lo.append(p_)
    for p_ in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p_) <= 0:
            hi.pop()
        hi.append(p_)
    return lo[:-1] + hi[:-1]


def rock_poly(m, k, cx, cy, a, n=9):
    """A convex, irregular footprint about `a` px in true radius, depth by the projection rule."""
    import math
    pts = []
    for i in range(n):
        t = 2 * math.pi * (i + 0.3 * (m.r(k + i, 7) / 7)) / n
        rr = a * (0.78 + 0.22 * m.r(k + 40 + i, 9) / 8)
        pts.append((round(cx + rr * math.cos(t), 2), round(cy + rr * K * math.sin(t), 2)))
    return _hull(pts)


# --------------------------------------------------------------------------- category 4: nature
# The things a 'T' cell can be, per planet: trees only where a planet has them. One cell each, or two
# for a big one. Colours: wall = trunk or rock side, roof = canopy or rock top.


def n_pine(m):
    """Pine: two or three stacked cones on a stub trunk."""
    p = palette(m)
    cx = m.W / 2
    a = min(m.W / 2 - 1, 7 + 4 * (m.cw - 1))
    cy = a * K + 1
    m.add(S.box(cx - 1, cy - 1, 0, cx + 1, cy + 1, 5, p["wall"]))
    z = 3
    n = 2 + m.r(1, 2)
    for i in range(n):
        r = a * (1 - 0.22 * i)
        m.add(S.cone(cx, cy, r, 0, z, r * 1.25, p["roof"]))
        z += r * 0.7


def n_boulder(m):
    """Boulder: one to three irregular rocks with sloped sides."""
    p = palette(m)
    n = 1 + m.r(1, 3) if m.cw > 1 else 1
    for i in range(n):
        a = (m.W / 2 - 1) * (1 - 0.3 * i)
        cx = m.W / 2 + (i - (n - 1) / 2) * m.W * 0.3
        cy = a * K + 1 + 2 * i
        h = a * (0.7 + 0.15 * m.r(5 + i, 3))
        m.add(S.prism(rock_poly(m, 10 * i, cx, cy, a), 0, h, p["wall"], p["roof"], taper=a * 0.45))


def n_shard(m):
    """Ice or crystal shard cluster: tall tapered spikes of different heights."""
    p = palette(m)
    n = 2 + m.r(1, 2)
    for i in range(n):
        a = m.W * (0.22 - 0.04 * i)
        cx = m.W / 2 + (i - (n - 1) / 2) * m.W * 0.26
        cy = a * K + 1 + 2 * (i % 2)
        h = (m.H - 2 * a * K - 2) * (1 - 0.25 * i) * (0.8 + 0.1 * m.r(3 + i, 3))
        m.add(S.prism(rock_poly(m, 20 * i, cx, cy, a, 5), 0, h, p["glass"], p["roof"], taper=a * 0.9))


def n_fungus(m):
    """Giant fungus: a pale stalk under a wide shallow cap."""
    p = palette(m)
    cx = m.W / 2
    a = m.W / 2 - 1
    cy = a * K + 1
    h = (m.H - 2 * a * K - 6) * (0.7 + 0.1 * m.r(1, 3))
    m.add(S.cylinder(cx, cy, a * 0.25, 0, 0, h, p["wall"]),
          S.cylinder(cx, cy, a, 0, h, h + 2, p["roof"]), S.dome(cx, cy, a, 0, h + 2, a * 0.35, p["roof"]))


NATURE = {
    "pine": (n_pine, [(1, 2), (2, 3)]),
    "boulder": (n_boulder, [(1, 1), (2, 2)]),
    "shard": (n_shard, [(1, 2), (2, 3)]),
    "fungus": (n_fungus, [(1, 2), (2, 3)]),
}


# --------------------------------------------------------------------------- category 5: landforms
# Large natural structures that bound an area instead of a wall of trees. Big, partly off the map is fine.


def l_mesa(m):
    """Mesa: two or three tapered rock tiers with a flat top."""
    p = palette(m)
    cx = m.W / 2
    a = m.W / 2 - 2
    cy = a * K + 2
    n = 2 + m.r(1, 2)
    hs = (m.H - 2 * a * K - 4)
    z = 0
    for i in range(n):
        r = a * (1 - 0.18 * i)
        h = hs * (0.5 if i == 0 else 0.5 / (n - 1))
        m.add(S.prism(rock_poly(m, 30 * i, cx + (m.r(9 + i, 5) - 2) * 1.5, cy + i * 1.5, r), z, z + h,
                      p["wall"], p["roof"], taper=r * 0.12))
        z += h


def l_spire(m):
    """Rock spire: a tall narrow column of stacked, offset tapered blocks."""
    p = palette(m)
    a = m.W / 2 - 2
    cy = a * K + 1
    z = 0
    n = 3 + m.r(1, 2)
    hs = (m.H - 2 * a * K - 2) / n
    for i in range(n):
        r = a * (1 - 0.17 * i)
        cx = m.W / 2 + (m.r(5 + i, 5) - 2) * 1.2
        m.add(S.prism(rock_poly(m, 50 * i, cx, cy + i, r, 7), z, z + hs, p["wall"], p["roof"], taper=r * 0.2))
        z += hs


def l_arch(m):
    """Natural arch: two rock legs and a heavy lintel across them."""
    p = palette(m)
    W = m.W
    lw = W * 0.24
    D = min(18, m.H * 0.3)
    h = m.H - D - 16
    for i, x in enumerate((lw / 2 + 1, W - lw / 2 - 1)):
        m.add(S.prism(rock_poly(m, 60 + 20 * i, x, D / 2 + 1, lw / 2, 7), 0, h, p["wall"], p["roof"], taper=-2))
    m.add(S.prism(rock_poly(m, 100, W / 2, D / 2 + 1, W / 2 - 1, 10), h, h + 14, p["wall"], p["roof"], taper=3))


def l_boulders(m):
    """Boulder field: a scatter of rocks of mixed sizes, laid out by the seed."""
    p = palette(m)
    k = 0
    for gy in range(int(m.H * 0.6) - 8, 0, -12):
        for gx in range(6, int(m.W) - 4, 14):
            k += 1
            if m.r(k, 3) == 0 or len(m.sc.solids) >= 14:
                continue
            a = 4 + 2 * m.r(k + 5, 4)
            x = gx + (m.r(k + 9, 5) - 2) * 2
            m.add(S.prism(rock_poly(m, 7 * k, x, gy + a * K, a, 7), 0, a * 0.9, p["wall"], p["roof"], taper=a * 0.4))


def l_ridge(m):
    """Ridge: a long jagged rock wall made of overlapping peaks, for an area border."""
    p = palette(m)
    n = max(3, int(m.W // 24))
    for i in range(n):
        a = m.W / n * 0.75
        cx = (i + 0.5) * m.W / n + (m.r(i, 5) - 2) * 2
        cy = a * K + 2 + 2 * m.r(i + 20, 3)
        h = (m.H - 2 * a * K - 4) * (0.65 + 0.12 * m.r(i + 40, 4))
        m.add(S.prism(rock_poly(m, 13 * i, cx, cy, a, 8), 0, h, p["wall"], p["roof"], taper=a * 0.5))


def l_crater(m):
    """Crater: a low rocky rim around a shallow bowl cut into the ground."""
    p = palette(m)
    cx = m.W / 2
    a = m.W / 2 - 2
    cy = a * K + 2
    m.add(_slab(m, 10),
          S.prism(rock_poly(m, 3, cx, cy, a, 12), 0, 5, p["wall"], p["roof"], taper=3),
          S.cylinder(cx, cy, a * 0.75, 0, -8, 6, p["wall"], p["roof"], subtract=True, below=True))


LANDFORM = {
    "mesa": (l_mesa, [(4, 4), (6, 6)]),
    "spire": (l_spire, [(2, 5), (3, 7)]),
    "arch": (l_arch, [(5, 5), (7, 6)]),
    "boulders": (l_boulders, [(4, 3), (6, 4)]),
    "ridge": (l_ridge, [(8, 4), (10, 6)]),
    "crater": (l_crater, [(4, 3), (6, 4)]),
}


# --------------------------------------------------------------------------- category 6: hangars and bays
# Angular sci-fi shapes, no tubes or round walls (owner, 2026-11-02): hexagons, chamfers, sloped walls.


def _chamfer(x0, y0, x1, y1, k):
    return [(x0 + k, y0), (x1 - k, y0), (x1, y0 + k * K), (x1, y1 - k * K), (x1 - k, y1), (x0 + k, y1),
            (x0, y1 - k * K), (x0, y0 + k * K)]


def _hex(x0, y0, x1, y1, k):
    """An elongated hexagon: points east and west."""
    ym = (y0 + y1) / 2
    return [(x0 + k, y0), (x1 - k, y0), (x1, ym), (x1 - k, y1), (x0 + k, y1), (x0, ym)]


def _door_x(m):
    return m.door_x if m.door_x is not None else m.W / 2


def h_hangar(m):
    """Hex hangar: an elongated hexagonal hall with sloped walls, a framed hangar door and a roof spine."""
    p = palette(m)
    W = m.W
    h = m.wall_h(1.25)
    D = m.H - h - 6
    k = min(W * 0.16, 16)
    poly = _hex(1, 0, W - 1, D, k)
    m.add(S.prism(poly, 0, h, p["wall"], p["roof"], taper=3))
    dw = min(W - 2 * k - 6, W * 0.5)
    x = W / 2
    m.add(S.box(x - dw / 2 - 2, -0.5, 0, x + dw / 2 + 2, 1.5, h * 0.8 + 2, p["trim"]),
          S.box(x - dw / 2, -1, 0, x + dw / 2, 4, h * 0.8, p["dark"], subtract=True),
          S.box(x - dw / 2, 1, h * 0.8 - 3, x + dw / 2, 2, h * 0.8 - 1.5, p["light"]))
    m.add(S.prism(_hex(W * 0.25, D * 0.35, W * 0.75, D * 0.65, 4), h, h + 3, p["trim"], p["roof"], taper=1))


def h_bay(m):
    """Docking bay: an open-topped walled bay on a chamfered plan, a pad marked on its floor, a gate south."""
    p = palette(m)
    W = m.W
    h = m.wall_h(0.9)
    D = m.H - h - 2
    k = min(W, D) * 0.22
    t = 4
    m.add(S.prism(_chamfer(1, 0, W - 1, D, k), 0, h, p["wall"], p["roof"]),
          S.prism(_chamfer(1 + t, t, W - 1 - t, D - t, k * 0.8), 0.5, h + 1, p["wall"], p["roof"], subtract=True))
    gw = min(16, W * 0.3)
    x = _door_x(m)
    m.add(S.box(x - gw / 2, -1, 0.5, x + gw / 2, t + 1, h + 1, p["wall"], p["roof"], subtract=True),
          S.box(x - gw / 2 - 2, -0.5, 0, x - gw / 2, t, h + 3, p["trim"]),
          S.box(x + gw / 2, -0.5, 0, x + gw / 2 + 2, t, h + 3, p["trim"]))


def h_shipyard(m):
    """Shipyard: a hex landing pad between two docking towers, each reaching a clamp arm over the pad."""
    p = palette(m)
    W = m.W
    h = m.H * 0.5
    D = m.H - h - 4
    m.add(S.prism(_hex(1, 0, W - 1, D, min(14, W * 0.15)), 0, 3, p["trim"], p["roof"]))
    cx, cy = W / 2, D / 2
    s = min(W * 0.3, D * 0.4 / K)
    m.add(S.prism(_hex(cx - s, cy - s * K, cx + s, cy + s * K, s * 0.5), 3, 3.6, p["light"], p["light"]),
          S.prism(_hex(cx - s + 2, cy - s * K + 1.5, cx + s - 2, cy + s * K - 1.5, s * 0.5 - 1), 3, 3.8,
                  p["roof"], p["roof"]))
    g = 11
    yb = D * 0.5
    for x in (5, W - 5 - g):
        m.add(S.prism([(x, yb), (x + g, yb), (x + g, yb + g * K), (x, yb + g * K)], 3, h, p["trim"], p["roof"],
                      taper=2),
              S.box(x + 1, yb - 0.5, h * 0.6, x + g - 1, yb + 0.5, h * 0.6 + 2, p["dark"], subtract=True))
    reach = W * 0.18
    m.add(S.box(5 + g, yb + 1, h - 8, 5 + g + reach, yb + g * K - 1, h - 4, p["trim"], p["roof"]),
          S.box(W - 5 - g - reach, yb + 1, h - 8, W - 5 - g, yb + g * K - 1, h - 4, p["trim"], p["roof"]),
          S.box(5 + g + reach - 2, yb + 1.5, h - 7, 5 + g + reach, yb + g * K - 1.5, h - 5, p["light"]),
          S.box(W - 5 - g - reach, yb + 1.5, h - 7, W - 3 - g - reach, yb + g * K - 1.5, h - 5, p["light"]))


HANGARS = {
    "hex-hangar": (h_hangar, [(5, 4), (7, 5)]),
    "bay-hex": (h_bay, [(5, 4), (7, 5)]),
    "shipyard": (h_shipyard, [(6, 5), (8, 6)]),
}


# --------------------------------------------------------------------------- category 7: gyms (boss houses)
# Each gym is a different Star Wars seat of power: a palace, a temple, a sci-fi hall, a fortress. What they
# share is one bold doorway (a tall framed portal with a lit lintel); the game's sign out front does the rest.


def portal(m, x, yf, w=18, h=24, z0=0):
    """The gym's bold doorway: a tall dark opening in a heavy stepped frame that stands proud of the wall,
    with a lit lintel. Every gym has one; it is the shared mark, the sign out front is the other."""
    p = palette(m)
    return [S.box(x - w / 2 - 5, yf - 3, z0, x + w / 2 + 5, yf + 1, z0 + h + 7, p["trim"], p["roof"]),
            S.box(x - w / 2 - 2, yf - 4, z0, x + w / 2 + 2, yf + 1, z0 + h + 3, p["roof"], p["roof"]),
            S.box(x - w / 2, yf - 5, z0, x + w / 2, yf + 4, z0 + h, p["dark"], subtract=True),
            S.box(x - w / 2 - 2, yf - 4.5, z0 + h + 3.5, x + w / 2 + 2, yf - 3, z0 + h + 6, p["light"])]


def g_palace(m):
    """Palace gym: a heavy main block, a square tower at a back corner, a lower side wing."""
    p = palette(m)
    W = m.W
    h = m.wall_h(1.5)
    tw = W * 0.22
    D = m.H - h - 26
    right = m.r(1, 2)
    m.add(S.prism([(1, 0), (W - 1, 0), (W - 1, D), (1, D)], 0, h, p["wall"], p["roof"], taper=2))
    tx = W - 1 - tw if right else 1
    m.add(S.prism([(tx, D * 0.45), (tx + tw, D * 0.45), (tx + tw, D), (tx, D)], 0, h + 24, p["wall"], p["roof"],
                  taper=2),
          S.box(tx + 2, D * 0.45 - 1, h + 14, tx + tw - 2, D * 0.45 + 1, h + 17, p["dark"], subtract=True))
    m.add(S.box(W * 0.3, D * 0.3, h, W * 0.7, D * 0.8, h + 4, p["roof"], p["roof"]))
    m.add(*portal(m, _door_x(m), 0, 18, min(26, h - 6)))


def g_temple(m):
    """Temple gym: three stepped stone tiers, a shrine on top, the portal at the foot."""
    p = palette(m)
    W = m.W
    tiers = 3
    hz = (m.H * 0.55) / tiers
    D = m.H - hz * tiers - 10
    z = 0
    for i in range(tiers):
        k = i * W * 0.13
        y1 = D - i * D * 0.12
        m.add(S.prism([(1 + k, i * 3), (W - 1 - k, i * 3), (W - 1 - k, y1), (1 + k, y1)], z, z + hz, p["wall"],
                      p["roof"], taper=2))
        z += hz
    s = W * 0.12
    m.add(S.box(W / 2 - s, D * 0.45, z, W / 2 + s, D * 0.75, z + 8, p["trim"], p["roof"]))
    m.add(*portal(m, W / 2, 0, 18, min(24, hz * 1.7)))


def g_hex(m):
    """Hex hall gym: a sloped hexagonal hall with a raised hex crown and a lit band, sci-fi."""
    p = palette(m)
    W = m.W
    h = m.wall_h(1.4)
    D = m.H - h - 14
    k = W * 0.2
    m.add(S.prism(_hex(1, 0, W - 1, D, k), 0, h, p["wall"], p["roof"], taper=3),
          S.prism(_hex(1, 0, W - 1, D, k), h * 0.62, h * 0.62 + 2, p["light"], taper=0))
    m.add(S.prism(_hex(W * 0.25, D * 0.25, W * 0.75, D * 0.85, k * 0.45), h, h + 10, p["wall"], p["roof"],
                  taper=2))
    m.add(*portal(m, W / 2, 0, 18, min(24, h * 0.6)))


def g_fortress(m):
    """Fortress gym: a wide dark block with two angled pylons flanking the portal, a slab roof."""
    p = palette(m)
    W = m.W
    h = m.wall_h(1.4)
    D = m.H - h - 20
    m.add(S.prism([(4, 2), (W - 4, 2), (W - 4, D), (4, D)], 0, h, p["wall"], p["roof"], taper=4))
    pw = W * 0.16
    x = _door_x(m)
    for px in (x - 15 - pw, x + 15):
        m.add(S.prism([(px, 0), (px + pw, 0), (px + pw, pw * K + 4), (px, pw * K + 4)], 0, h + 18, p["trim"],
                      p["roof"], taper=pw * 0.35))
    m.add(S.box(2, 1, h, W - 2, D + 1, h + 3, p["roof"], p["roof"]))
    m.add(*portal(m, x, 2, 18, min(26, h - 6)))


def g_court(m):
    """Court gym: a long colonnaded hall, two end pavilions with pitched roofs, the portal in the middle."""
    p = palette(m)
    W = m.W
    h = m.wall_h(1.2)
    D = m.H - h - 16
    m.add(S.box(1, 4, 0, W - 1, D, h, p["wall"], p["roof"]))
    pw = W * 0.24
    for x0 in (1, W - 1 - pw):
        m.add(S.box(x0, 0, 0, x0 + pw, D, h + 6, p["wall"], p["roof"]),
              S.hip(x0 - 1, -1, x0 + pw + 1, D + 1, h + 6, 10, p["roof"]))
    n = 3 + m.r(1, 2)
    for i in range(n):
        x = 1 + pw + 4 + i * (W - 2 * pw - 10) / max(1, n - 1)
        if abs(x - W / 2) > 12:
            m.add(S.box(x - 1.5, 2, 0, x + 1.5, 4, h, p["trim"]))
    m.add(*portal(m, W / 2, 4, 18, min(24, h - 4)))


GYMS = {
    "gym-palace": (g_palace, [(6, 6), (8, 7)]),
    "gym-temple": (g_temple, [(6, 6), (8, 7)]),
    "gym-hex": (g_hex, [(6, 5), (8, 6)]),
    "gym-fortress": (g_fortress, [(6, 5), (8, 6)]),
    "gym-court": (g_court, [(7, 5), (9, 6)]),
}

# Categories whose kit sheet shows the game's sign in front of each piece.
SIGNED = {"gyms"}

# Colours a category is shown in when its look belongs to a faction, not a planet.
MATERIAL = {"imperial": {"wall": (150, 156, 164), "roof": (98, 104, 112), "trim": (52, 54, 60)},
            "nature": {"wall": (120, 92, 64), "roof": (96, 140, 72), "trim": (70, 60, 50)},
            "landform": {"wall": (176, 124, 78), "roof": (214, 176, 126), "trim": (110, 80, 54)}}

CATEGORIES = {"doorless": DOORLESS, "sunken": SUNKEN, "imperial": IMPERIAL, "nature": NATURE,
              "landform": LANDFORM, "hangars": HANGARS, "gyms": GYMS}


def register(builds):
    for cat in CATEGORIES.values():
        for name, (fn, _) in cat.items():
            def run(m, fn=fn, name=name):
                fn(m)
                check(m, name)
            builds[name] = run

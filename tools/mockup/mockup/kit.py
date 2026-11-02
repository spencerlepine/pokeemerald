"""Building categories, added one at a time and reviewed before the next (owner's rule, 2026-11-02).

Each category is a small set of greybox models registered into build.BUILDS. Every piece in a category
must pass the simplicity guardrail, so the kit stays as plain as the original game's art:
  - at most BUDGET["solids"] solids per model (boxes, cylinders, domes, cones, cuts),
  - colours only from the piece palette (wall, roof, trim, glass, light, dark), no ad-hoc shades,
  - round shapes only through solid.py's primitives, which apply the 45° projection rule.
Variation comes from the seed (heights, counts, which side a part sits on), never from detail.

`python3 -m mockup kit <category> [--grey]` draws wiki/mockup/kit/<category>[-grey].png: every piece at
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


def d_pylon(m):
    """Power pylon: one or two posts with a crossbeam and hanging insulators."""
    p = palette(m)
    W = m.W
    h = (m.H - 8) * (0.78 + 0.08 * m.r(1, 3))
    two = m.cw >= 3 or m.r(2, 2)
    posts = [W * 0.28, W * 0.72] if two else [W / 2]
    for x in posts:
        m.add(S.box(x - 2, 2, 0, x + 2, 6, h, p["wall"], p["roof"]))
    m.add(S.box(2, 2, h - 2, W - 2, 6, h + 2, p["roof"], p["roof"]))
    for x in (4, W / 2, W - 4) if two else (4, W - 4):
        m.add(S.box(x - 1, 3, h - 7, x + 1, 5, h - 2, p["trim"]),
              S.box(x - 1.5, 2.5, h - 9, x + 1.5, 5.5, h - 7, p["glass"]))


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
    "pylon": (d_pylon, [(2, 3), (3, 4)]),
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


def i_checkpoint(m):
    """Checkpoint: a guard booth with a window band and a striped barrier arm across the road."""
    p = palette(m)
    bw = 18
    bx = 2 if m.r(1, 2) else m.W - 2 - bw
    D = 14
    h = 18
    m.add(S.prism([(bx, 0), (bx + bw, 0), (bx + bw, D), (bx, D)], 0, h, p["wall"], p["roof"], taper=2),
          _band(bx + 2, bx + bw - 2, 0.3, 10, 4, p["glass"]),
          S.box(bx - 1, -1, h, bx + bw + 1, D + 1, h + 2, p["roof"]))
    ax0, ax1 = (bx + bw + 2, m.W - 2) if bx < m.W / 2 else (2, bx - 2)
    post = ax0 if bx < m.W / 2 else ax1 - 3
    m.add(S.box(post, 4, 0, post + 3, 7, 10, p["trim"]))
    n = max(2, int((ax1 - ax0) // 8))
    for i in range(n):
        xa = ax0 + (ax1 - ax0) * i / n
        m.add(S.box(xa, 5, 8, xa + (ax1 - ax0) / n, 6.5, 10, p["light"] if i % 2 else p["trim"]))


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
    "checkpoint": (i_checkpoint, [(3, 2), (4, 2)]),
    "barricade": (i_barricade, [(3, 1), (5, 2)]),
    "sentry": (i_sentry, [(2, 4), (2, 5)]),
    "garage": (i_garage, [(4, 5), (5, 6)]),
    "barracks": (i_barracks, [(5, 3), (6, 3)]),
    "pillbox": (i_pillbox, [(2, 2), (3, 2)]),
    "command": (i_command, [(4, 4), (5, 5)]),
    "gate": (i_gate, [(4, 4), (6, 5)]),
}

# Colours a category is shown in when its look belongs to a faction, not a planet.
MATERIAL = {"imperial": {"wall": (150, 156, 164), "roof": (98, 104, 112), "trim": (52, 54, 60)}}

CATEGORIES = {"doorless": DOORLESS, "sunken": SUNKEN, "imperial": IMPERIAL}


def register(builds):
    for cat in CATEGORIES.values():
        for name, (fn, _) in cat.items():
            def run(m, fn=fn, name=name):
                fn(m)
                check(m, name)
            builds[name] = run

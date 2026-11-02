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

CATEGORIES = {"doorless": DOORLESS}


def register(builds):
    for cat in CATEGORIES.values():
        for name, (fn, _) in cat.items():
            def run(m, fn=fn, name=name):
                fn(m)
                check(m, name)
            builds[name] = run

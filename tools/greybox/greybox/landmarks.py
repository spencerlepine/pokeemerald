"""Category 11: landmarks (kit category `landmarks`, `lm-` names): one-off set pieces seen from outside.

A landmark is big and singular (Fortress Vader, the Cave of Evil, a ring of standing stones), but it is
still a greybox: at most 16 solids, palette colours only, seed for variation. A landmark that needs a
special colour story (black fortress over lava) gets it from its planet palette or styles.yaml, not here.
"""
import math

from . import solid as S

K = S.K


def _p(m):
    from .kit import palette
    return palette(m)


def _poly(m, k, cx, cy, a, n=8):
    from .kit import rock_poly
    return rock_poly(m, k, cx, cy, a, n)


def lm_fortress(m):
    """Fortress tower (Vader's): a rock base, a wide plinth block, a tall tapering stem that splits into two
    prongs, a band of lit slit windows, a bridge out to the front."""
    p = _p(m)
    W = m.W
    D = min(m.H * 0.35, W * 0.45)
    cx, cy = W / 2, D / 2
    m.add(S.prism(_poly(m, 1, cx, cy, W / 2 - 2), 0, 10, p["wall"], p["roof"], taper=6),
          S.prism([(cx - W * 0.28, cy - D * 0.32), (cx + W * 0.28, cy - D * 0.32), (cx + W * 0.28, cy + D * 0.32),
                   (cx - W * 0.28, cy + D * 0.32)], 10, 30, p["trim"], p["roof"], taper=3))
    top = m.H - D - 4
    sw = W * 0.14
    m.add(S.prism([(cx - sw, cy - 4), (cx + sw, cy - 4), (cx + sw, cy + 4), (cx - sw, cy + 4)], 30, top * 0.62,
                  p["trim"], p["roof"], taper=sw * 0.3))
    for side in (-1, 1):
        x0 = cx + side * sw * 0.15
        x1 = cx + side * sw * 1.05
        a, b = sorted((x0, x1))
        m.add(S.box(a, cy - 3, top * 0.62, b, cy + 3, top, p["trim"], p["roof"]))
    m.add(S.box(cx - W * 0.22, cy - D * 0.33, 20, cx + W * 0.22, cy - D * 0.3, 23, p["light"]),
          S.box(cx - 3, 0, 8, cx + 3, cy - D * 0.32, 11, p["wall"], p["roof"]),
          S.box(cx - 4, cy - D * 0.34, 10, cx + 4, cy - D * 0.3, 20, p["dark"], subtract=True))


def lm_cavemouth(m):
    """Cave mouth: a rock mound with a dark opening in its south face, roots draping over it and a black
    dead tree on top."""
    p = _p(m)
    a = m.W / 2 - 1
    cy = a * K + 1
    cx = m.W / 2
    h = min(22, m.H - 2 * a * K - 14)
    m.add(S.prism(_poly(m, 2, cx, cy, a), 0, h, p["wall"], p["roof"], taper=a * 0.35),
          S.box(cx - a * 0.35, -2, 0, cx + a * 0.35, cy, h * 0.6, p["dark"], p["dark"], subtract=True))
    for i in range(4):
        x = cx - a * 0.4 + i * a * 0.27
        m.add(S.box(x, cy - a * K * 0.75, h * 0.25 + 2 * (i % 2), x + 1.5, cy - a * K * 0.6, h + 1, p["trim"]))
    m.add(S.box(cx - 1.5, cy - 1, h - 2, cx + 1.5, cy + 2, m.H - 2 * a * K - 2, p["trim"], p["dark"]),
          S.box(cx - a * 0.5, cy, m.H - 2 * a * K - 8, cx + a * 0.5, cy + 1, m.H - 2 * a * K - 6.5, p["trim"]))


def lm_stones(m):
    """Standing stones: a ring of worn upright stones on a low round dais, a glowing stone or a dark hollow
    at the centre (Tython's ring, the Tusken ruins)."""
    p = _p(m)
    a = m.W / 2 - 2
    cx, cy = m.W / 2, a * K + 2
    m.add(S.cylinder(cx, cy, a, 0, 0, 2, p["wall"], p["roof"]))
    n = 7
    for i in range(n):
        if m.r(10 + i, 5) == 0:            # a fallen or missing stone
            continue
        t = 2 * math.pi * (i + 0.5) / n
        x, y = cx + a * 0.8 * math.cos(t), cy + a * 0.8 * K * math.sin(t)
        h = 10 + 4 * m.r(20 + i, 4)
        m.add(S.prism(_poly(m, 30 + i, x, y, 3.8, 6), 2, h, p["wall"], p["roof"], taper=1.2))
    glow = m.r(1, 2) == 0
    m.add(S.cylinder(cx, cy, a * 0.22, 0, 2, 4 if glow else 2.5, p["light"] if glow else p["dark"],
                     p["light"] if glow else p["dark"]))


def lm_pool(m):
    """Glowing pool: a round basin of light set in a ring of low rocks and plants."""
    p = _p(m)
    a = m.W / 2 - 1
    cx, cy = m.W / 2, a * K + 1
    m.add(S.cylinder(cx, cy, a, 0, 0, 3, p["wall"], p["roof"]),
          S.cylinder(cx, cy, a * 0.7, 0, 1, 3.5, p["glass"], p["light"], subtract=True),
          S.cylinder(cx, cy, a * 0.7, 0, 0, 1.5, p["light"], p["light"]))
    for i in range(6):
        t = 2 * math.pi * (i + 0.3) / 6
        x, y = cx + a * 0.88 * math.cos(t), cy + a * 0.88 * K * math.sin(t)
        tall = i % 2 == 0
        m.add(S.prism(_poly(m, 40 + i, x, y, 3.6, 6), 0, 12 if tall else 7, p["roof"] if tall else p["wall"],
                      p["roof"], taper=1.5))


def lm_glyphwall(m):
    """Glyph wall (Aurebesh vault): a thick wall with rows of recessed glyph panels, lit, and a sealed door."""
    p = _p(m)
    D = 8
    h = min(m.H - D - 2, 26)
    m.add(S.box(0, 1, 0, m.W, D, h, p["wall"], p["roof"]),
          S.box(-0.5, 0.5, h - 2, m.W + 0.5, D + 0.5, h, p["trim"], p["roof"]))
    cols = min(6, max(2, int(m.W // 10)))
    for i in range(cols):
        x = 3 + i * (m.W - 6) / cols
        for z in (5, 13):
            if i == cols // 2 and z == 5:
                continue
            m.add(S.box(x, 0, z, x + 4, 2, z + 5, p["light"], subtract=True))
    m.add(S.box(m.W / 2 - 4, 0, 0, m.W / 2 + 4, 2, 11, p["dark"], subtract=True))


def lm_spire(m):
    """Ancient spire on an asteroid: a lumpy rock base, a tall stepped tower with a ring platform and a
    lit tip."""
    p = _p(m)
    a = m.W / 2 - 2
    cx, cy = m.W / 2, a * K + 1
    m.add(S.prism(_poly(m, 3, cx, cy, a, 9), 0, 12, p["wall"], p["roof"], taper=a * 0.4))
    top = m.H - 2 * a * K - 6
    z = 12
    for i in range(3):
        r = a * (0.42 - 0.1 * i)
        hz = (top - 12) * (0.4 - 0.08 * i)
        m.add(S.prism(S.ring_pts(cx, cy, r, r * K, 8), z, z + hz, p["trim"], p["roof"], taper=r * 0.2))
        z += hz
        if i == 0:
            m.add(S.prism(S.ring_pts(cx, cy, r * 1.6, r * 1.6 * K, 8), z - 2, z, p["roof"], p["roof"]))
    m.add(S.prism(S.ring_pts(cx, cy, 2, 2 * K, 6), z, top, p["trim"], p["roof"], taper=1.5),
          S.box(cx - 1.5, cy - 1, top, cx + 1.5, cy + 1, top + 3, p["light"]))


LANDMARKS = {
    "lm-fortress": (lm_fortress, [(6, 8), (8, 10)]),
    "lm-cavemouth": (lm_cavemouth, [(4, 4)]),
    "lm-stones": (lm_stones, [(4, 4), (5, 5)]),
    "lm-pool": (lm_pool, [(4, 3), (4, 4)]),
    "lm-glyphwall": (lm_glyphwall, [(4, 2), (6, 3)]),
    "lm-spire": (lm_spire, [(4, 6), (6, 8)]),
}

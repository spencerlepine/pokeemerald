"""Buildings as greybox 3D models, ray-cast into sprites (see solid.py for the projection).

Each building fills its phase-1 cell box (`at`, `size`). Inside the box, a model of footprint W x D px and
height h px takes exactly D + h rows, so the footprint sits on the bottom rows and the roof rises above it.
The door is on the south face, at the building's `door` column.

A `build` name in styles.yaml picks a model from BUILDS. Colours come from the style (wall, roof, trim)
and the planet's ground; `--grey` renders the same models in neutral greys.
"""
import math

from . import solid as S
from .style import shade

C = 16


class M:
    """One model being built: the box size in px, the colours and a random source."""

    def __init__(self, b, st, seed, grey=False):
        (self.cw, self.ch) = b["size"]
        self.W, self.H = self.cw * C, self.ch * C
        self.st, self.seed = st, seed
        if grey:
            self.wall, self.roof, self.trim = (150, 150, 150), (182, 182, 182), (104, 104, 104)
        else:
            self.wall, self.roof, self.trim = st["wall"], st["roof"], st["trim"]
        self.ground = st.get("ground", (200, 190, 170))
        self.grey = grey
        self.door_col = b.get("door")
        self.door_x = None if self.door_col is None else int(self.door_col) * C + C / 2
        self.tall = float(st.get("height") or 1.0)
        self.sc = S.Scene()

    def r(self, k, n):
        return ((self.seed >> (k * 3)) & 0xFFFF) % n

    def wall_h(self, k=1.0):
        base = 16 if self.ch <= 4 else 24
        return max(8, int(base * self.tall * k))

    @property
    def door_col_rgb(self):
        return shade(self.trim, -0.45)

    @property
    def glass(self):
        return (70, 70, 80) if self.grey else shade(self.trim, 0.55)

    @property
    def dirt(self):
        return shade(self.ground, -0.1)

    def add(self, *s):
        self.sc.add(*s)

    def door(self, yf, z0=0, w=8, h=12):
        """A door recess in the south face at the door column. yf: the face's y at that column."""
        if self.door_x is None:
            return
        x = self.door_x
        self.add(S.box(x - w / 2, yf - 1, z0, x + w / 2, yf + 3, z0 + h, self.door_col_rgb, subtract=True))

    def windows(self, x0, x1, yf, z, every=16, w=4, hgt=4):
        x = x0 + 6
        while x + w < x1 - 4:
            if self.door_x is None or abs(x + w / 2 - self.door_x) > 9:
                self.add(S.box(x, yf - 1, z, x + w, yf + 1.2, z + hgt, self.glass, subtract=True))
            x += every


def _yfront_ellipse(cx, cy, a, b, x):
    t = max(-1.0, min(1.0, (x - cx) / a))
    return cy - b * math.sqrt(1 - t * t)


def parapet(m, x0, y0, x1, y1, z, t=2, hgt=2):
    col = shade(m.roof, 0.12)
    m.add(S.box(x0, y0, z, x1, y0 + t, z + hgt, col), S.box(x0, y1 - t, z, x1, y1, z + hgt, col),
          S.box(x0, y0, z, x0 + t, y1, z + hgt, col), S.box(x1 - t, y0, z, x1, y1, z + hgt, col))


# ------------------------------------------------------------------------------------------------ models
def m_block(m, foot="rect", roof="flat"):
    h = m.wall_h()
    rise = {"pitched": 12, "barrel": 10}.get(roof, 2)
    D = max(8, m.H - h - rise)
    W = m.W
    boxes = []
    if foot == "L":
        a = W * (0.5 + 0.1 * m.r(2, 2))
        if m.door_x is not None and m.door_x > W - a:
            boxes = [(1, 0, W - 1, D * 0.55), (W - a, 0, W - 1, D)]
        else:
            boxes = [(1, 0, W - 1, D * 0.55), (1, 0, a, D)]
    elif foot == "T":
        boxes = [(1, D * 0.45, W - 1, D), (W * 0.3, 0, W * 0.7, D)]
        if m.door_x is not None and not (W * 0.3 + 5 < m.door_x < W * 0.7 - 5):
            boxes = [(1, 0, W - 1, D)]
    else:
        boxes = [(1, 0, W - 1, D)]
    if foot == "oct":
        k = min(8, W * 0.2, D * 0.3)
        poly = [(k, 0), (W - k, 0), (W, k), (W, D - k), (W - k, D), (k, D), (0, D - k), (0, k)]
        m.add(S.prism(poly, 0, h, m.wall, m.roof))
        ip = [(k, 2), (W - k, 2), (W - 2, k), (W - 2, D - k), (W - k, D - 2), (k, D - 2), (2, D - k), (2, k)]
        m.add(S.prism(poly, h, h + 2, shade(m.roof, 0.12)), S.prism(ip, h, h + 3, m.roof, m.roof, subtract=True))
    else:
        for x0, y0, x1, y1 in boxes:
            m.add(S.box(x0, y0, 0, x1, y1, h, m.wall, m.roof))
            if roof == "pitched":
                m.add(S.gable(x0 - 1, y0 - 2, x1 + 1, y1 + 1, h, rise, m.roof))
            elif roof == "barrel":
                m.add(S.vault(x0, y0, x1, y1, h, rise, m.roof))
        if roof == "flat" and len(boxes) == 1:
            parapet(m, *boxes[0], h)
    if foot == "notch" and m.door_x is not None:
        x = m.door_x
        m.add(S.box(x - 12, -1, 0, x + 12, 6, h - 4, shade(m.wall, -0.1), subtract=True))
        m.door(6)
    else:
        m.door(0)
        m.windows(0, W, 0, h * 0.45)


def m_court(m):
    h = m.wall_h(0.85)
    D = m.H - h - 2
    W = m.W
    m.add(S.box(1, 0, 0, W - 1, D, h, m.wall, m.roof))
    parapet(m, 1, 0, W - 1, D, h)
    iw, idp = max(10, W * 0.28), max(6, D * 0.22)
    m.add(S.box(iw, idp, 1, W - iw, D - idp, h + 4, shade(m.wall, -0.08), m.dirt, subtract=True))
    m.door(0)
    m.windows(0, W, 0, h * 0.45)


def m_wings(m, towers=False, dome_mid=False):
    h = m.wall_h(1.15)
    hw = int(h * 0.6)
    D = m.H - h - 2
    W = m.W
    a, b = W * 0.3, W * 0.7
    m.add(S.box(1, 0, 0, a, D * 0.75, hw, m.wall, shade(m.roof, -0.06)),
          S.box(b, 0, 0, W - 1, D * 0.75, hw, m.wall, shade(m.roof, -0.06)),
          S.box(a, 0, 0, b, D, h, m.wall, m.roof))
    parapet(m, a, 0, b, D, h)
    if dome_mid:
        m.add(S.dome((a + b) / 2, D / 2, (b - a) * 0.3, D * 0.3, h, max(4, min(10, m.H - h - D)), shade(m.roof, 0.1)))
    if towers:
        r = min(W * 0.07, 8)
        for x in (r + 1, W - r - 1):
            m.add(S.cylinder(x, D * 0.75 - r, r, r * 0.8, 0, h + 4, m.wall, m.roof),
                  S.dome(x, D * 0.75 - r, r, r * 0.8, h + 4, 6, m.roof))
    m.door(0, w=16 if m.cw >= 6 else 8, h=min(16, h - 3))
    m.windows(1, a, 0, hw * 0.45)
    m.windows(b, W - 1, 0, hw * 0.45)


def _round(m, h, cap, rise=None, z0=0, box=None):
    """A round building on an oval footprint filling the box (or a sub-box x0..x1)."""
    x0, x1 = box or (1, m.W - 1)
    a = (x1 - x0) / 2
    rise = rise if rise is not None else {"dome": min(a * 0.55, 18), "cone": min(a * 0.8, 22)}.get(cap, 2)
    D = max(8, m.H - h - rise - z0)
    b = min(D / 2, a * 0.75)
    cx, cy = (x0 + x1) / 2, b
    m.add(S.cylinder(cx, cy, a, b, z0, z0 + h, m.wall, m.roof))
    if cap == "dome":
        m.add(S.dome(cx, cy, a, b, z0 + h, rise, m.roof))
    elif cap == "cone":
        m.add(S.cone(cx, cy, a + 2, b + 1.5, z0 + h, rise, m.roof))
    elif cap == "ring":
        m.add(S.cylinder(cx, cy, a * 0.7, b * 0.7, z0 + h, z0 + h + 2, shade(m.roof, 0.12)))
    return cx, cy, a, b


def _round_door(m, cx, cy, a, b, z0=0, **kw):
    if m.door_x is not None:
        m.door(_yfront_ellipse(cx, cy, a, b, m.door_x) + 0.5, z0=z0, **kw)


def _round_windows(m, cx, cy, a, b, z):
    for f in (-0.6, -0.25, 0.25, 0.6) if a > 28 else (-0.5, 0.5):
        x = cx + a * f
        if m.door_x is None or abs(x - m.door_x) > 9:
            yf = _yfront_ellipse(cx, cy, a, b, x)
            m.add(S.box(x - 2, yf - 1, z, x + 2, yf + 2.5, z + 4, m.glass, subtract=True))


def m_dome(m, k=1.0):
    h = max(8, int(m.wall_h(0.6) * k))
    cx, cy, a, b = _round(m, h, "dome")
    _round_door(m, cx, cy, a, b, h=min(12, h + 4))
    if h >= 12:
        _round_windows(m, cx, cy, a, b, h * 0.4)


def m_domes2(m):
    left = m.r(4, 2)
    h = max(8, m.wall_h(0.55))
    big = (1, m.W * 0.66) if left else (m.W * 0.34, m.W - 1)
    small = (m.W * 0.6, m.W - 1) if left else (1, m.W * 0.4)
    D = m.H - h - 14
    m.add(S.box(m.W * 0.25, 2, 0, m.W * 0.75, D * 0.7, h - 2, m.wall, m.roof))
    _round(m, h - 2, "dome", rise=10, box=small)
    cx, cy, a, b = _round(m, h, "dome", box=big)
    if m.door_x is not None and big[0] + 4 <= m.door_x <= big[1] - 4:
        _round_door(m, cx, cy, a, b, h=min(12, h + 4))
    else:
        m.door(2, h=min(12, h - 3))


def m_dome_block(m):
    h = max(8, m.wall_h(0.7))
    left = m.r(5, 2)
    D = m.H - h - 2
    bx = (1, m.W * 0.58) if left else (m.W * 0.42, m.W - 1)
    dm = (m.W * 0.4, m.W - 1) if left else (1, m.W * 0.6)
    m.add(S.box(bx[0], 0, 0, bx[1], D * 0.7, h, m.wall, m.roof))
    cx, cy, a, b = _round(m, h, "dome", box=dm)
    if m.door_x is not None and dm[0] + 4 <= m.door_x <= dm[1] - 4:
        _round_door(m, cx, cy, a, b, h=min(12, h + 3))
    else:
        m.door(0, h=min(12, h - 2))


def m_store(m):
    h = m.wall_h(0.9)
    cx, cy, a, b = _round(m, h, "dome", rise=min(14, m.H * 0.2))
    m.add(S.cylinder(cx, cy, a + 1, b + 1, h * 0.55, h * 0.55 + 2, m.trim))
    _round_door(m, cx, cy, a, b, w=14, h=min(13, h * 0.5))
    _round_windows(m, cx, cy, a, b, h * 0.7)


def m_cone(m):
    h = max(8, m.wall_h(0.55))
    cx, cy, a, b = _round(m, h, "cone", box=(3, m.W - 3))
    _round_door(m, cx, cy, a, b, h=min(11, h + 2))


def _pit(m, x0, x1, depth=12, rim=3):
    a = (x1 - x0) / 2
    D = m.H - rim - 1
    b = min(D / 2 - 2, a * 0.8)
    cx, cy = (x0 + x1) / 2, b + 2
    m.add(S.cylinder(cx, cy, a + 2, b + 2, -depth - 2, 0, m.dirt, m.ground, outline=False),
          S.cylinder(cx, cy, a + 2, b + 2, 0, rim, m.roof),
          S.cylinder(cx, cy, a - 2, b - 2, -depth, rim + 1, shade(m.wall, -0.05), shade(m.ground, -0.2),
                     subtract=True))
    return cx, cy, a, b


def m_sunken(m):
    cx, cy, a, b = _pit(m, 2, m.W - 2)
    # doors into the far wall of the pit
    for f in (-0.45, 0.45) if a > 30 else (0,):
        x = cx + a * f
        yb = cy + (b - 2) * math.sqrt(max(0, 1 - f * f)) - 1
        m.add(S.box(x - 3, yb - 3, -12, x + 3, yb + 2, -3, m.door_col_rgb, subtract=True))
    if m.door_x is not None:      # a small entry dome on the rim at the door
        x = m.door_x
        r = 7
        m.add(S.cylinder(x, r * 0.6, r, r * 0.6, 0, 5, m.wall, m.roof),
              S.dome(x, r * 0.6, r, r * 0.6, 5, 6, m.roof))
        m.door(0.5, h=9, w=6)


def m_sunken_dome(m):
    cx, cy, a, b = _pit(m, 2, m.W - 2, depth=8)
    m.add(S.dome(cx, cy + 2, a * 0.55, b * 0.55, -8, min(20, m.H * 0.35), m.roof))
    if m.door_x is not None:
        m.door(1, h=5, w=6)


def m_bunker(m):
    h = max(10, m.wall_h(0.6))
    D = m.H - h - 3
    W = m.W
    m.add(S.prism([(0, 0), (W, 0), (W, D), (0, D)], 0, h - 2, m.dirt, shade(m.ground, -0.04), taper=8))
    m.add(S.prism([(5, 2), (W - 5, 2), (W - 5, D - 1), (5, D - 1)], 0, h, m.wall, m.roof, taper=4))
    m.add(S.box(W * 0.2, -1, h * 0.55, W * 0.8, 6, h * 0.55 + 2, (25, 25, 30), subtract=True))
    if m.door_x is not None:
        x = m.door_x
        m.add(S.box(x - 7, -2, 0, x + 7, 8, h * 0.45, shade(m.wall, -0.15), subtract=True))
        m.door(7, h=min(10, h * 0.45))


def m_buried(m):
    W = m.W
    rise = min(W * 0.32, m.H * 0.5)
    D = m.H - rise + 6
    a, b = W / 2 - 1, min(D / 2, W * 0.4)
    cx, cy = W / 2, b
    m.add(S.prism(S.ring_pts(cx, cy, a, b), 0, 6, m.dirt, shade(m.ground, -0.04), taper=8))
    m.add(S.dome(cx, cy, a * 0.78, b * 0.78, -6, rise, m.roof))
    if m.door_x is not None:
        x = m.door_x
        m.add(S.box(x - 6, 0, 0, x + 6, cy, 11, m.wall, m.roof))
        m.door(0, h=9)


def m_quonset(m, wide=False):
    W = m.W
    rise = min(W / 2 - 1, m.H * 0.45)
    D = m.H - rise
    m.add(S.vault(1, 0, W - 1, D, 0, rise, m.roof))
    m.add(S.box(4, -0.5, 0, W - 4, 1.5, rise * 0.75, m.wall))
    m.door(0, w=18 if wide or m.cw >= 6 else 8, h=min(14, rise * 0.6))


def m_stilts(m, cap="pitched", round_=False):
    L = max(8, int(m.H * 0.18))
    h = m.wall_h(0.7)
    rise = 10 if cap in ("pitched", "dome") else 2
    leg = shade(m.trim, -0.1)
    W = m.W
    if round_:
        D = m.H - L - h - rise
        a, b = W / 2 - 2, min(D / 2 - 1, W * 0.35)
        cx, cy = W / 2, b + 2
        for f in (-0.6, -0.2, 0.2, 0.6):
            x = cx + a * f
            m.add(S.box(x - 1.5, cy - b * 0.6, 0, x + 1.5, cy - b * 0.6 + 3, L, leg))
        m.add(S.cylinder(cx, cy, a, b, L, L + h, m.wall, m.roof), S.dome(cx, cy, a, b, L + h, rise, m.roof))
        yf = _yfront_ellipse(cx, cy, a, b, m.door_x) if m.door_x is not None else 0
    else:
        D = m.H - L - h - rise
        y0 = 5
        for x in (4, W / 2, W - 4):
            m.add(S.box(x - 1.5, y0, 0, x + 1.5, y0 + 3, L, leg))
        m.add(S.box(2, y0, L, W - 2, D, L + h, m.wall, m.roof))
        if cap == "pitched":
            m.add(S.gable(0, y0 - 2, W, D + 1, L + h, rise, m.roof))
        else:
            parapet(m, 2, y0, W - 2, D, L + h)
        m.windows(2, W - 2, y0, L + h * 0.4)
        yf = y0
    if m.door_x is not None:
        x = m.door_x
        for i in range(3):        # steps down to the ground
            m.add(S.box(x - 4, yf - 2 - (i + 1) * 1.6, 0, x + 4, yf - 2 - i * 1.6 + 0.01, L * (3 - i) / 3,
                        shade(m.trim, 0.1)))
        m.door(yf, z0=L, h=min(11, h - 1))


def m_tower(m):
    D = max(16, int(m.H * 0.35))
    h = m.H - D - 2
    W = m.W
    if m.r(6, 2):
        k = min(8, W * 0.2)
        poly = [(k, 0), (W - k, 0), (W - 1, k), (W - 1, D - k), (W - k, D), (k, D), (1, D - k), (1, k)]
        m.add(S.prism(poly, 0, h, m.wall, m.roof))
    else:
        m.add(S.box(1, 0, 0, W - 1, D, h, m.wall, m.roof))
        parapet(m, 1, 0, W - 1, D, h)
    for z in range(16, int(h) - 6, 12):
        m.windows(4, W - 4, 0, z, every=8, w=3, hgt=5)
    m.door(0, w=10)


def m_round_tower(m):
    h = int(min(m.H * 0.55 * m.tall, m.H - 24))
    cap = m.st.get("top", "ring")
    cx, cy, a, b = _round(m, h, cap, rise=12 if cap == "dome" else 2)
    for z in range(14, h - 4, 16):
        m.add(S.cylinder(cx, cy, a + 1, b + 1, z, z + 2, m.trim))
    _round_door(m, cx, cy, a, b)
    _round_windows(m, cx, cy, a, b, 18 if h > 26 else h * 0.4)


def m_stepped(m, tiers=3):
    h = max(7, m.wall_h(0.42))
    D = m.H - h * tiers - 2
    W = m.W
    for t in range(tiers):
        ix, iy = W * 0.12 * t, D * 0.14 * t
        m.add(S.prism([(ix + 1, iy * 0.6), (W - ix - 1, iy * 0.6), (W - ix - 1, D - iy), (ix + 1, D - iy)],
                      h * t, h * (t + 1), m.wall, shade(m.roof, 0.06 * t), taper=2))
    if m.door_x is not None:
        x = m.door_x
        for i in range(tiers):
            m.add(S.box(x - 6, -1, 0, x + 6, D * 0.14 * i * 0.6 + 4, h * (i + 1) - 2, shade(m.wall, 0.12)))
        m.door(-1, h=min(11, h * 1.5))


def m_deck(m):
    L = max(6, int(m.H * 0.14))
    W = m.W
    D = m.H - L - 4
    a, b = W / 2 - 1, D / 2
    cx, cy = W / 2, b
    m.add(S.cylinder(cx, cy, 5, 3, 0, L, shade(m.wall, -0.2)))
    m.add(S.cylinder(cx, cy, a, b, L, L + 3, m.wall, m.roof))
    m.add(S.cylinder(cx, cy, a * 0.7, b * 0.7, L + 3, L + 3.6, (200, 200, 200) if m.grey else shade(m.trim, 0.2)))
    m.add(S.cylinder(cx, cy, a * 0.62, b * 0.62, L + 3, L + 3.8, m.roof))


def m_plant(m):
    h = m.wall_h(0.8)
    W = m.W
    D = m.H - h - 14
    n = 2 if m.cw < 6 else 3
    r = min(W * 0.12, 10)
    for i in range(n):
        x = r + 2 + (W - 2 * r - 4) * i / max(1, n - 1)
        m.add(S.cylinder(x, D - r * 0.7, r, r * 0.7, 0, h + 8, shade(m.wall, 0.05), m.roof),
              S.dome(x, D - r * 0.7, r, r * 0.7, h + 8, 4, m.roof))
    m.add(S.box(1, 0, 0, W - 1, D * 0.55, h, m.wall, m.roof))
    parapet(m, 1, 0, W - 1, D * 0.55, h)
    m.door(0)
    m.windows(0, W, 0, h * 0.45)


def m_lab(m):
    m_block(m, "L")
    h = m.wall_h()
    x = m.W - 10 if m.r(3, 2) else 10
    y = 6
    m.add(S.box(x - 1, y - 1, h, x + 1, y + 1, h + 7, m.trim),
          S.cylinder(x, y, 7, 4, h + 7, h + 9, shade(m.wall, 0.15)))


def m_arena(m):
    h = m.wall_h(0.8)
    W = m.W
    D = m.H - h - 2
    a, b = W / 2 - 1, D / 2
    cx, cy = W / 2, b
    m.add(S.cylinder(cx, cy, a, b, 0, h, m.wall, m.roof))
    m.add(S.cylinder(cx, cy, a + 1, b + 1, h * 0.5, h * 0.5 + 2, m.trim))
    field = (120, 120, 120) if m.grey else m.st.get("field", (108, 150, 80))
    m.add(S.cylinder(cx, cy, a * 0.8, b * 0.78, 3, h + 2, shade(m.wall, -0.18), field, subtract=True))
    _round_door(m, cx, cy, a, b, w=14, h=min(12, h * 0.55))


BUILDS = {
    "block": m_block, "box": m_block,
    "L": lambda m: m_block(m, "L"), "oct": lambda m: m_block(m, "oct"), "T": lambda m: m_block(m, "T"),
    "notch": lambda m: m_block(m, "notch"),
    "pitched": lambda m: m_block(m, "rect", "pitched"), "barrel": lambda m: m_block(m, "rect", "barrel"),
    "court": m_court, "wings": m_wings, "palace": lambda m: m_wings(m, towers=True),
    "hall": lambda m: m_wings(m, dome_mid=True),
    "dome": m_dome, "domes2": m_domes2, "dome-block": m_dome_block, "store": m_store,
    "sunken": m_sunken, "sunken-dome": m_sunken_dome, "bunker": m_bunker, "buried": m_buried,
    "quonset": m_quonset, "hangar": lambda m: m_quonset(m, wide=True),
    "stilts": m_stilts, "stilts-dome": lambda m: m_stilts(m, "dome", round_=True),
    "stilts-flat": lambda m: m_stilts(m, "flat"),
    "cone": m_cone, "tower": m_tower, "round-tower": m_round_tower, "stepped": m_stepped,
    "deck": m_deck, "plant": m_plant, "lab": m_lab, "arena": m_arena,
}
# the first-pass `kind` names, so an old catalogue entry still draws
KIND_TO_BUILD = {"box": "block", "dome": "dome", "pitched": "pitched", "stepped": "stepped", "tower": "tower",
                 "hall": "hall", "dish": "sunken", "platform": "deck"}

_cache = {}


def sprite(b, st, seed, grey=False):
    name = st.get("build") or KIND_TO_BUILD.get(st.get("kind"), "block")
    key = (name, tuple(b["size"]), b.get("door"), st["wall"], st["roof"], st["trim"], st.get("ground"),
           st.get("height"), st.get("top"), seed & 0xFFFFFF, grey)
    if key not in _cache:
        m = M(b, st, seed, grey)
        BUILDS.get(name, m_block)(m)
        _cache[key] = S.render(m.sc, m.W, m.H)
    return _cache[key]


def building(img, b, st, seed, grey=False):
    sp = sprite(b, st, seed, grey)
    img.paste(sp, (b["at"][0] * C, b["at"][1] * C), sp)

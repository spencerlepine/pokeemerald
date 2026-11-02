"""Buildings as greybox 3D models, ray-cast into sprites (see solid.py for the projection).

Each building fills its phase-1 cell box (`at`, `size`). Inside the box, a model of footprint W x D px and
height h px takes exactly D + h rows, so the footprint sits on the bottom rows and the roof rises above it.
The door is on the south face, at the building's `door` column.

A `build` name in styles.yaml picks a model from BUILDS. Colours come from the style (wall, roof, trim)
and the planet's ground; `--grey` renders the same models in neutral greys.
"""
import math

import numpy as np

from . import solid as S
from .style import shade

C = 16
OVAL = S.K        # depth / width of every round footprint (the projection rule in solid.py)


def fit_round(width, height, h, per):
    """The largest true radius whose oval (depth 2aK) plus walls h plus a cap of per * a fits the box."""
    return max(3.0, min(width / 2, (height - h) / (2 * OVAL + per)))


class M:
    """One model being built: the box size in px, the colours and a random source."""

    def __init__(self, b, st, seed, grey=False):
        (self.cw, self.ch) = b["size"]
        self.W, self.H = self.cw * C, self.ch * C
        self.st, self.seed = st, seed
        self.b = b
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
        h = (self.seed * 2654435761 + (k + 1) * 40503) & 0xFFFFFFFF
        h ^= h >> 15
        h = (h * 2246822519) & 0xFFFFFFFF
        h ^= h >> 13
        return h % n

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
    """A round building filling the box (or a sub-box x0..x1). Domes are hemispheres unless `rise` asks for
    a lower one; if the box is too shallow, the building gets narrower rather than squashed."""
    x0, x1 = box or (1, m.W - 1)
    if cap == "dome":
        per = OVAL if rise is None else 0
        a = fit_round(x1 - x0, m.H - z0 - (rise or 0), h, per)
        rise = a * OVAL if rise is None else min(rise, a * OVAL)
    elif cap == "cone":
        a = fit_round(x1 - x0, m.H - z0, h, 0.8)
        rise = a * 0.8
    else:
        a = fit_round(x1 - x0, m.H - z0 - 3, h, 0)
        rise = 2
    b = a * OVAL
    cx, cy = (x0 + x1) / 2, b
    m.add(S.cylinder(cx, cy, a, b, z0, z0 + h, m.wall, m.roof))
    if cap == "dome":
        m.add(S.dome(cx, cy, a, b, z0 + h, rise, m.roof))
    elif cap == "cone":
        m.add(S.cone(cx, cy, a + 2, b, z0 + h, rise, m.roof))
    elif cap == "ring":
        m.add(S.cylinder(cx, cy, a * 0.7, b, z0 + h, z0 + h + 2, shade(m.roof, 0.12)))
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
    a = fit_round(W - 2, m.H + 6, 0, OVAL * 0.78)
    b = a * OVAL
    cx, cy = W / 2, b
    m.add(S.prism(S.ring_pts(cx, cy, a, b), 0, 6, m.dirt, shade(m.ground, -0.04), taper=8))
    m.add(S.dome(cx, cy, a * 0.78, None, -6, None, m.roof))
    if m.door_x is not None:
        x = m.door_x
        m.add(S.box(x - 6, 0, 0, x + 6, cy, 11, m.wall, m.roof))
        m.door(0, h=9)


def m_quonset(m, wide=False):
    """A barrel-vault hangar: the vault runs north-south, its arched end faces south with a big door."""
    W = m.W
    rise = min(W / 2 - 1, m.H * 0.45)
    D = m.H - rise
    m.add(S.vault(1, 0, W - 1, D, 0, rise, m.roof))
    # ribs over the vault, and the arched front frame in the wall colour
    for y in range(8, int(D) - 4, 12):
        m.add(S.vault(0.5, y, W - 0.5, y + 2, 0, rise + 0.6, shade(m.roof, -0.12)))
    m.add(S.vault(0.5, -0.5, W - 0.5, 2, 0, rise + 0.6, m.wall))
    if m.door_x is not None:
        dw = 18 if wide or m.cw >= 6 else 9
        dh = min(rise * (0.75 if wide else 0.6), 18)
        m.add(S.vault(m.door_x - dw / 2, -1, m.door_x + dw / 2, 4, 0, dh, m.door_col_rgb, subtract=True))


def m_stilts(m, cap="pitched", round_=False):
    L = max(8, int(m.H * 0.18))
    h = m.wall_h(0.7)
    rise = 10 if cap in ("pitched", "dome") else 2
    leg = shade(m.trim, -0.1)
    W = m.W
    if round_:
        a = fit_round(W - 4, m.H - L - 2, h, OVAL)
        rise = a * OVAL
        b = a * OVAL
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


def _oval(m, x0, x1, k=OVAL):
    """An oval footprint seen at the game's angle: depth about 0.6 of the width, front edge at y = 0."""
    a = (x1 - x0) / 2
    return (x0 + x1) / 2, a * k, a, a * k


def _rings(m, cx, cy, a, b, z, col, rings=(0.8,), w=0.08):
    """Painted rings on a flat top (thin raised bands)."""
    for r in rings:
        m.add(S.cylinder(cx, cy, a * r, b * r, z, z + 0.4, col))
        m.add(S.cylinder(cx, cy, a * (r - w), b * (r - w), z, z + 0.6, m.roof))


def _H(m, cx, cy, s, z, col):
    z += 0.7      # above the painted rings
    m.add(S.box(cx - s, cy - s * 0.7, z, cx - s + 2.5, cy + s * 0.7, z + 0.5, col),
          S.box(cx + s - 2.5, cy - s * 0.7, z, cx + s, cy + s * 0.7, z + 0.5, col),
          S.box(cx - s, cy - 1, z, cx + s, cy + 1.2, z + 0.5, col))


def m_deck(m):
    """A raised round landing deck (Cloud City): a thick oval slab on struts, a landing ring painted on top."""
    L = 11 if m.ch >= 4 else 7
    cx, cy, a, b = _oval(m, 1, m.W - 1)
    if 2 * b + L + 7 > m.H:          # a short box: a smaller deck rather than one cut off at the top
        b = (m.H - L - 7) / 2
        a = b / OVAL
        cx = m.W / 2
        cy = b
    leg = shade(m.wall, -0.25)
    for f in (-0.55, 0.0, 0.55):
        x = cx + a * f
        y = _yfront_ellipse(cx, cy, a, b, x) + 2
        m.add(S.box(x - 2, y, 0, x + 2, y + 3, L, leg))
    m.add(S.cylinder(cx, cy, a, b, L, L + 5, m.wall, m.roof))
    mark = (210, 210, 210) if m.grey else m.trim
    _rings(m, cx, cy, a, b, L + 5, mark, (0.82,))
    _H(m, cx, cy, min(a * 0.25, 10), L + 5, mark)


def m_pad(m):
    """A landing pad at ground level: a low octagonal slab, a painted ring and an H."""
    cx, cy, a, b = _oval(m, 1, m.W - 1)
    k = 0.42
    poly = [(cx - a, cy - b * k), (cx - a * k, cy - b), (cx + a * k, cy - b), (cx + a, cy - b * k),
            (cx + a, cy + b * k), (cx + a * k, cy + b), (cx - a * k, cy + b), (cx - a, cy + b * k)]
    m.add(S.prism(poly, 0, 3, m.wall, m.roof))
    mark = (220, 220, 220) if m.grey else m.trim
    _rings(m, cx, cy, a, b, 3, mark, (0.78,), w=0.07)
    _H(m, cx, cy, min(a * 0.28, 11), 3, mark)
    for f in (-1, 1):         # edge lights
        m.add(S.box(cx + f * a * 0.92 - 1, cy - 1, 3, cx + f * a * 0.92 + 1, cy + 1, 5, mark))


def m_bay(m):
    """A docking bay: a round wall open to the sky, the ship floor at ground level, an arched gate."""
    h = m.wall_h(0.75)
    W = m.W
    D = m.H - h - 1
    a = fit_round(W - 2, m.H - 1, h, 0)
    b = a * OVAL
    cx, cy = W / 2, b
    m.add(S.cylinder(cx, cy, a, b, 0, h, m.wall, m.roof))
    m.add(S.cylinder(cx, cy, a - 4, b - 4, 0.6, h + 1, shade(m.wall, -0.15), shade(m.ground, -0.12), subtract=True))
    for f in (-0.45, 0.45):     # doors in the far inner wall
        x = cx + (a - 4) * f
        yb = cy + (a - 4) * OVAL * math.sqrt(1 - f * f) - 1
        m.add(S.box(x - 3, yb - 1, 0.6, x + 3, yb + 3, 9, m.door_col_rgb, subtract=True))
    mark = (205, 205, 205) if m.grey else shade(m.trim, 0.2)
    m.add(S.cylinder(cx, cy + 2, (a - 4) * 0.55, (b - 4) * 0.55, 0.6, 1.0, mark))
    m.add(S.cylinder(cx, cy + 2, (a - 4) * 0.48, (b - 4) * 0.48, 0.6, 1.2, shade(m.ground, -0.12)))
    if m.door_x is not None:
        yf = _yfront_ellipse(cx, cy, a, b, m.door_x)
        m.add(S.vault(m.door_x - 6, yf - 1, m.door_x + 6, yf + 6, 0, min(11, h - 2), m.door_col_rgb, subtract=True))


def m_dome_porch(m):
    """The Tatooine homestead: a dome with a boxy arched entry block in front of it."""
    h = max(8, m.wall_h(0.5))
    x0, x1 = (3, m.W - 3)
    a = fit_round(x1 - x0, m.H - 6, h, OVAL)
    rise = a * OVAL
    b = a * OVAL
    cx = m.door_x if m.door_x is not None else m.W / 2
    cx = max(x0 + a, min(x1 - a, cx))
    cy = 6 + b
    m.add(S.cylinder(cx, cy, a, b, 0, h, m.wall, m.roof), S.dome(cx, cy, a, b, h, rise, m.roof))
    if m.cw >= 6:     # a second, smaller dome behind to one side
        sx = cx + (a * 0.75 if m.r(4, 2) else -a * 0.75)
        sx = max(9, min(m.W - 9, sx))
        m.add(S.dome(sx, cy + b * 0.6, a * 0.4, b * 0.4, 0, rise * 0.8, shade(m.roof, -0.05)))
    px = m.door_x if m.door_x is not None else cx
    pw, ph = 11, h + 7
    m.add(S.box(px - pw, 0, 0, px + pw, cy, ph, m.wall, m.roof),
          S.vault(px - pw, 0, px + pw, cy, ph, 4, m.roof))
    if m.door_x is not None:
        m.add(S.box(px - 4, -1, 0, px + 4, 3, 8, m.door_col_rgb, subtract=True),
              S.vault(px - 4, -1, px + 4, 3, 8, 4, m.door_col_rgb, subtract=True))


def m_spire(m):
    """A Mos Espa-style tower: stacked drums getting narrower, a mast on top."""
    W = m.W
    a0 = min(W / 2 - 2, 18)
    b0 = a0 * 0.6
    cx, cy = W / 2, b0 + 1
    z = 0
    tiers = [(1.0, 16), (0.75, 14), (0.55, 12), (0.35, 10)]
    top = m.H - 2 * b0 - 12
    for k, (f, hh) in enumerate(tiers):
        hh = min(hh, top - z)
        if hh < 4:
            break
        col = m.wall if k % 2 == 0 else shade(m.wall, -0.06)
        m.add(S.cylinder(cx, cy, a0 * f, b0 * f, z, z + hh, col, m.roof))
        m.add(S.cylinder(cx, cy, a0 * f + 1, b0 * f + 1, z + hh - 2, z + hh, m.trim))
        z += hh
    m.add(S.box(cx - 1, cy - 1, z, cx + 1, cy + 1, min(z + 12, m.H - 2 * b0), m.trim))
    _round_door(m, cx, cy, a0, b0, h=10)


def m_saucer(m):
    """Cloud City: a wide disc on a slim stalk, a small dome on top."""
    W = m.W
    a = max(8, min(W / 2 - 1, (m.H - 36) / (2 * OVAL)))     # leave room for a visible stalk
    b = a * OVAL
    cx, cy = W / 2, b + 1
    stalk = max(14, int(m.H - 2 * b - 16))
    sa, sb = max(5, a * 0.22), max(3, b * 0.22)
    m.add(S.cylinder(cx, cy, sa, sb, 0, stalk, m.wall, m.roof))
    m.add(S.cylinder(cx, cy, a * 0.6, b * 0.6, stalk - 4, stalk, shade(m.wall, -0.1)))
    m.add(S.cylinder(cx, cy, a, b, stalk, stalk + 5, m.trim, m.roof))
    m.add(S.dome(cx, cy, a * 0.45, b * 0.45, stalk + 5, 7, shade(m.roof, 0.1)))
    _round_door(m, cx, cy, sa, sb, w=6, h=10)


def m_glass_dome(m):
    """A faceted glass greenhouse dome on a low ring wall (Sullust ash farms)."""
    h = 5
    a = fit_round(m.W - 2, m.H, h, OVAL)
    rise = a * OVAL
    b = a * OVAL
    cx, cy = m.W / 2, b
    glass = (150, 170, 180) if m.grey else m.st.get("glass", (150, 200, 205))
    m.add(S.cylinder(cx, cy, a, b, 0, h, m.wall, m.roof))
    m.add(S.dome(cx, cy, a, b, h, rise, glass, rings=4, n=12))
    _round_door(m, cx, cy, a, b, h=8)


def m_comm_tower(m):
    """A comms mast: a lattice tower tapering up, crossbars, a dish near the top, a small hut at its foot."""
    W = m.W
    s = min(W * 0.32, 16)
    cx, cy = W / 2, s + 6
    top = m.H - 2 * s - 14
    leg = m.trim
    for dx in (-1, 1):
        for dy in (-1, 1):
            m.add(S.prism([(cx + dx * s - 1.2, cy + dy * s * 0.6 - 1.2), (cx + dx * s + 1.2, cy + dy * s * 0.6 - 1.2),
                           (cx + dx * s + 1.2, cy + dy * s * 0.6 + 1.2), (cx + dx * s - 1.2, cy + dy * s * 0.6 + 1.2)],
                          0, top, leg))
    for k, z in enumerate(range(10, int(top), 12)):
        f = 1 - z / max(top, 1) * 0.0
        m.add(S.box(cx - s, cy - s * 0.6 - 1, z, cx + s, cy - s * 0.6 + 1, z + 1.5, shade(leg, 0.15)))
    m.add(S.box(cx - s - 1, cy - s * 0.6 - 1, top, cx + s + 1, cy + s * 0.6 + 1, top + 3, m.wall, m.roof))
    m.add(S.box(cx - 1, cy - 1, top + 3, cx + 1, cy + 1, top + 14, leg))
    m.add(S.cylinder(cx + s * 0.6, cy - s * 0.6, 6, 3, top + 6, top + 8, shade(m.wall, 0.2)))
    m.add(S.box(cx - 9, 0, 0, cx + 9, 8, 10, m.wall, m.roof))
    m.door(0, h=8, w=6)


def m_cliff_door(m):
    """A hangar dug into a rock or ice face: the face fills the box, a framed blast door in it."""
    W = m.W
    rock = (150, 150, 150) if m.grey else m.st.get("rock", shade(m.ground, -0.25))
    h = m.H - 12
    m.add(S.prism([(0, 4), (W, 4), (W, 12), (0, 12)], 0, h, rock, shade(rock, 0.15), taper=4))
    m.add(S.box(0, 4, 0, W, 12, h * 0.3, rock))
    if m.door_x is None:
        m.door_x = W / 2
    if True:
        dw = min(W * 0.35, 26)
        m.add(S.box(m.door_x - dw / 2 - 3, 2, 0, m.door_x + dw / 2 + 3, 6, min(h * 0.7, 26), m.wall, m.roof))
        m.add(S.box(m.door_x - dw / 2, 1, 0, m.door_x + dw / 2, 8, min(h * 0.62, 22), m.door_col_rgb, subtract=True))
        for z in range(4, int(min(h * 0.62, 22)), 5):
            m.add(S.box(m.door_x - dw / 2, 6.5, z, m.door_x + dw / 2, 7.5, z + 1, shade(m.door_col_rgb, 0.25)))


def m_obelisk(m):
    """A tall tapering tower on a stepped base (Vader's fortress, the Kyber temple)."""
    W = m.W
    D = max(16, int(m.H * 0.3))
    m.add(S.box(1, 0, 0, W - 1, D, 8, m.wall, m.roof))
    w0 = W * 0.28
    cx, cy = W / 2, D * 0.55
    top = m.H - D - 2
    m.add(S.prism([(cx - w0, cy - w0 * 0.55), (cx + w0, cy - w0 * 0.55), (cx + w0, cy + w0 * 0.55),
                   (cx - w0, cy + w0 * 0.55)], 8, top, m.wall, m.roof, taper=w0 * 0.42))
    if m.st.get("fork"):
        for dx in (-3, 3):
            m.add(S.box(cx + dx - 1.5, cy - 1, top - 2, cx + dx + 1.5, cy + 1, top + 8, m.trim))
    m.door(0, w=10)


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
    a = fit_round(W - 2, m.H - 2, h, 0)
    b = a * OVAL
    cx, cy = W / 2, b
    m.add(S.cylinder(cx, cy, a, b, 0, h, m.wall, m.roof))
    m.add(S.cylinder(cx, cy, a + 1, b + 1, h * 0.5, h * 0.5 + 2, m.trim))
    field = (120, 120, 120) if m.grey else m.st.get("field", (108, 150, 80))
    m.add(S.cylinder(cx, cy, a * 0.8, b * 0.78, 3, h + 2, shade(m.wall, -0.18), field, subtract=True))
    _round_door(m, cx, cy, a, b, w=14, h=min(12, h * 0.55))



# ------------------------------------------------------------------------------------------------ giants
# Huge pieces for the edges of a map: cliff towns, city skylines, a crashed ship, hangar and fortress walls.
# They are meant for big boxes (12+ cells wide) on blocked border cells; place them with mockup overrides.
def m_hipped(m):
    h = m.wall_h()
    rise = min(14, m.H * 0.25)
    D = m.H - h - rise
    m.add(S.box(1, 0, 0, m.W - 1, D, h, m.wall, m.roof))
    m.add(S.hip(-1, -2, m.W + 1, D + 1, h, rise, m.roof))
    m.door(0)
    m.windows(0, m.W, 0, h * 0.45)


def m_cliff_town(m):
    """Homes carved into a rock face: two stepped rock tiers, doorways, windows, balconies and ladders."""
    W, H = m.W, m.H
    rock = m.st.get("cliff") or shade(m.ground, -0.3)
    D = max(16, H * 0.3)
    h1 = (H - D) * 0.5
    h2 = (H - D) - h1 - 2
    m.add(S.prism([(0, 0), (W, 0), (W, D), (0, D)], 0, h1, rock, shade(rock, 0.12), taper=3))
    m.add(S.prism([(0, D * 0.45), (W, D * 0.45), (W, D), (0, D)], h1 - 1, h1 + h2, shade(rock, -0.05),
                  shade(rock, 0.1), taper=3))
    dark = (30, 26, 24)
    x = 10 + m.r(1, 8)
    k = 0
    while x < W - 14:
        k += 1
        if (k + m.r(2, 3)) % 3:
            m.add(S.box(x, -1, 0, x + 7, 4, 11, dark, subtract=True),
                  S.vault(x, -1, x + 7, 4, 11, 3, dark, subtract=True))
        else:
            m.add(S.box(x - 1, -2, h1 * 0.55, x + 9, 2, h1 * 0.55 + 1.5, shade(m.trim, 0.1)))     # a balcony
        if k % 2:
            m.add(S.box(x + 2, D * 0.45 + 2, h1 + h2 * 0.35, x + 6, D * 0.45 + 6, h1 + h2 * 0.35 + 5, dark,
                        subtract=True))
        x += 18 + m.r(k % 5 + 3, 10)
    for lx in (W * 0.3, W * 0.72):
        m.add(S.box(lx - 2, 1.5 - 0.5, 0, lx + 2, 2.3, h1 + 1, shade(m.trim, -0.1)))


def m_city_edge(m):
    """A city skyline wall: a row of roofed towers of different widths, heights and depths."""
    W, H = m.W, m.H
    x = 0
    k = 0
    while x < W - 8:
        k += 1
        w = 16 + 8 * m.r(k, 4)
        w = min(w, W - x)
        d = 16 + 8 * m.r(k + 7, 3)
        hgt = min(H - d - 10, 24 + 12 * m.r(k + 3, 5))
        y0 = 4 * m.r(k + 11, 3)
        col = shade(m.wall, -0.06 * (k % 3))
        m.add(S.box(x + 0.5, y0, 0, x + w - 0.5, y0 + d, hgt, col, m.roof))
        roof = m.r(k + 5, 3)
        if roof == 0 and hgt + 10 < H - d:
            m.add(S.gable(x, y0 - 1, x + w, y0 + d + 1, hgt, 8, m.roof))
        elif roof == 1 and hgt + 10 < H - d:
            m.add(S.hip(x, y0 - 1, x + w, y0 + d + 1, hgt, 8, m.roof))
        else:
            m.add(S.box(x + w / 2 - 0.8, y0 + d / 2, hgt, x + w / 2 + 0.8, y0 + d / 2 + 1.6, hgt + 9, m.trim))
        for z in range(8, int(hgt) - 4, 8):
            for wx in range(int(x) + 4, int(x + w) - 4, 6):
                m.add(S.box(wx, y0 - 1, z, wx + 2.5, y0 + 1, z + 3.5, m.glass, subtract=True))
        x += w


def _hull(m):
    return (150, 150, 150) if m.grey else m.st.get("hull", (158, 162, 168))


def m_ship_hull(m):
    """A crashed Star Destroyer at true scale: only its bow fits on the map. The wedge runs on past the box
    edge and the top of the map, half buried in a sand berm, with plating grooves and a trench."""
    W, H = m.W, m.H
    hull = _hull(m)
    east = m.b.get("facing", "east" if not m.r(3, 2) else "west") == "east"   # which way the bow points
    L = W * 4.0                         # hull length, mostly off the map
    tipx = W * 0.88 if east else W * 0.12
    backx = tipx - L if east else tipx + L
    yc = H * 0.62
    half = L * 0.3
    poly = [(tipx, yc), (backx, yc - half), (backx, yc + half)]
    if not east:
        poly = [poly[0], poly[2], poly[1]]
    rise = L * 0.22
    # stepped decks: each tier set back from the one below, the upper ones running off the top of the map
    z, inset = -24, 0
    for k, (top, step) in enumerate(((0.3, 0), (0.55, 18), (0.85, 40), (1.3, 66))):
        p2 = S._inset2(poly, step) if step else poly
        m.add(S.prism(p2, z, H * top, shade(hull, -0.12 + 0.03 * k), shade(hull, 0.08 + 0.03 * k), taper=3))
        z = H * top - 1
    # the bridge superstructure, far back on the deck (mostly off the map)
    bx = tipx + (backx - tipx) * 0.45
    m.add(S.box(bx - 40, yc - 30, H * 1.3, bx + 40, yc + 30, H * 2.0, shade(hull, -0.05), hull))
    # plating grooves across the hull, and one long trench along it
    for k in range(1, 14):
        x = tipx + (backx - tipx) * k / 14
        m.add(S.box(x - 0.8, -400, -30, x + 0.8, 800, 600, shade(hull, -0.35), subtract=True))


def m_debris(m):
    """A field of capital-ship wreckage: hull slabs stuck in the sand, a buried engine bell, a fin."""
    W, H = m.W, m.H
    hull = _hull(m)
    sand = shade(m.ground, -0.08)
    x = 4
    k = 0
    while x < W - 20:
        k += 1
        kind = m.r(k, 3)
        w = 28 + 10 * m.r(k + 3, 4)
        y = 6 + 6 * m.r(k + 9, 4)
        if kind == 0:      # a slab of hull plating stuck in at an angle
            hgt = 30 + 12 * m.r(k + 5, 4)
            m.add(S.prism([(x, y), (x + w, y + 6), (x + w - 4, y + 14), (x + 2, y + 10)], -6, hgt, hull,
                          shade(hull, 0.1), taper=5))
        elif kind == 1:    # an engine bell lying on its side, half buried
            r = w / 2
            m.add(S.vault(x, y, x + w, y + 40, -r * 0.3, r, shade(hull, -0.05)))
            m.add(S.vault(x + 5, y - 1, x + w - 5, y + 6, -r * 0.3, r - 5, (30, 30, 34), subtract=True))
        else:              # a tall broken fin
            hgt = 50 + 15 * m.r(k + 6, 4)
            m.add(S.prism([(x, y + 4), (x + w * 0.6, y), (x + w * 0.7, y + 6), (x + 4, y + 10)], 0, hgt, hull,
                          shade(hull, 0.1), taper=4))
        m.add(S.cylinder(x + w / 2, y + 6, w * 0.65, 8, -2, 4, sand, shade(m.ground, -0.02), outline=False))
        x += w + 10 + 6 * m.r(k + 2, 3)


def m_palace_wall(m):
    """Jabba's palace outer wall: an adobe wall too tall to fit, a round tower, a sealed blast gate."""
    W, H = m.W, m.H
    hgt = H * 3
    m.add(S.prism([(-W, 6), (2 * W, 6), (2 * W, 400), (-W, 400)], 0, hgt, m.wall, m.roof, taper=6))
    m.add(S.box(-W, 2, 0, 2 * W, 8, 6, shade(m.wall, -0.05), m.roof))       # footing
    tx = W * (0.2 if m.r(2, 2) else 0.75)
    m.add(S.cylinder(tx, 30, 26, 18, 0, hgt * 1.2, shade(m.wall, 0.04), m.roof))
    m.add(S.cylinder(tx, 30, 27, 19, 22, 25, m.trim))
    gx = W * 0.5
    m.add(S.box(gx - 20, 0, 0, gx + 20, 9, 34, shade(m.wall, -0.08)))
    m.add(S.box(gx - 16, -1, 0, gx + 16, 6, 28, shade(m.trim, -0.35), subtract=True))
    for z in range(4, 28, 6):
        m.add(S.box(gx - 16, 4, z, gx + 16, 5, z + 1, shade(m.trim, -0.15)))
    for x in range(int(-W), int(2 * W), 22):
        if abs(x - gx) > 30 and abs(x - tx) > 34:
            m.add(S.box(x, -1, 30, x + 2, 9, 38, (30, 26, 22), subtract=True))


def m_trench_wall(m):
    """The Death Star trench: a sheer grey wall far taller than the map, covered in machinery."""
    W, H = m.W, m.H
    hull = _hull(m)
    m.add(S.box(-40, 4, -20, W + 40, 600, H * 4, hull))
    k = 0
    for z in range(4, int(H * 1.5), 10):
        for x in range(-8, int(W) + 8, 14):
            k += 1
            if m.r(k, 3) == 0:
                continue
            w = 6 + 4 * m.r(k + 1, 4)
            hz = 4 + 3 * m.r(k + 2, 3)
            dp = 2 + 2 * m.r(k + 3, 3)
            col = shade(hull, (m.r(k + 4, 5) - 2) * 0.06)
            m.add(S.box(x, 4 - dp, z, x + w, 4, z + hz, col))
            if m.r(k + 5, 9) == 0:
                m.add(S.box(x + 1, 4 - dp - 0.5, z + 1, x + 3, 4 - dp + 0.5, z + 2.5, (255, 236, 160)))
    for z in (24, 60, 100):
        m.add(S.box(-40, 0, z, W + 40, 4, z + 2.5, shade(hull, 0.15)))


def m_stilt_city(m):
    """Kamino's sea edge: giant domed platforms on clusters of tall pillars, rising off the top of the map."""
    W, H = m.W, m.H
    wall, roof = (m.wall, m.roof)
    x = 30 if m.r(1, 2) else 70
    while x < W + 60:
        a, b = 52, 30
        cy = b + 20
        for f in (-0.6, -0.2, 0.2, 0.6):
            px = x + a * f
            m.add(S.cylinder(px, cy - b * 0.7, 4, 3, -6, 90, shade(wall, -0.15)))
            m.add(S.cylinder(px, cy - b * 0.7, 5, 3.6, -6, -2, shade(wall, -0.3)))
        m.add(S.cylinder(x, cy, a * 0.5, b * 0.5, 40, 90, shade(wall, -0.1)))
        m.add(S.cylinder(x, cy, a, b, 90, 104, wall, roof))
        m.add(S.dome(x, cy, a * 0.9, b * 0.9, 104, 22, roof))
        x += 150


def m_undercity_rim(m):
    """Cloud City's edge seen from the plaza: the deck stays see-through, and below its oval rim the city's
    side drops away into the clouds with bands, window rows and hanging vanes. `rim: [cx, cy, a, b]` in
    cells, box-local (cy counted north from the box bottom)."""
    cxc, cyc, ac, bc = m.b.get("rim", [m.cw / 2, m.ch * 0.8, m.cw * 0.45, m.ch * 0.6])
    cx, cy, a, b = cxc * C, cyc * C, ac * C, bc * C
    wall = m.wall
    # the deck (see-through on top), its rim wall, then the underside sweeping back in toward a central stalk
    rim = 34
    m.add(S.cylinder(cx, cy, a, b, -rim, 0, wall, wall, hide_top=True, n=64, below=True, exact=True))
    t = b * 0.8
    m.add(S.prism(S.ring_pts(cx, cy, a - t, b - t, 64), -rim - 160, -rim, shade(wall, -0.15), shade(wall, -0.15),
                  taper=-t, below=True))
    for z0, col, g in ((-4, m.trim, 1.5), (-15, m.glass, 0.8), (-26, m.trim, 1.5)):
        m.add(S.cylinder(cx, cy, a + g, b + g, z0 - 3, z0, col, col, n=64, below=True, exact=True))
    m.add(S.cylinder(cx, cy, a * 0.12, b * 0.12, -900, -rim, shade(wall, -0.25), below=True))
    for k in range(14):
        th = math.pi * (0.1 + 0.8 * k / 13)
        x = cx - a * math.cos(th)
        y = cy - b * math.sin(th)
        m.add(S.box(x - 1.5, y - 2, -rim - 60, x + 1.5, y + 2, -rim, shade(wall, -0.3), below=True))


def m_temple_stairs(m):
    """The base of a Massassi temple too big to fit: stone tiers stepping up off the top of the map, a
    central stair climbing them."""
    W, H = m.W, m.H
    stone, top = shade(m.wall, -0.12), shade(m.roof, 0.18)
    step, back = 9, 7
    sx = W * (0.35 + 0.3 * m.r(1, 2))
    for t in range(40):
        y0 = 2 + t * back
        m.add(S.box(-W, y0, t * step, 2 * W, y0 + 600, (t + 1) * step, shade(stone, -0.03 * (t % 2)), top))
    k = step / back
    n = np.array([0, -k, 1.0]) / math.hypot(k, 1)
    m.add(S.Solid([[1, 0, 0, sx + 14], [-1, 0, 0, -(sx - 14)], [0, -1, 0, 0], [0, 0, -1, 0], [*n, n @ np.array([0, 0, 2])]],
                  shade(stone, 0.12), shade(top, 0.12)))
    for t in range(80):          # step lines on the stair
        y = t * 3
        m.add(S.box(sx - 14, y, y * k + 1.2, sx + 14, y + 0.9, y * k + 2.2, shade(stone, -0.18)))
    for dx in (-16, 14):         # side ramps (balustrades)
        m.add(S.Solid([[1, 0, 0, sx + dx + 2], [-1, 0, 0, -(sx + dx)], [0, -1, 0, 0], [0, 0, -1, 0],
                       [*n, n @ np.array([0, 0, 6])]], shade(stone, -0.05), shade(top, 0.0)))


def m_hangar_wall(m):
    """A giant hangar front: a huge block with an open bay door, landing lights, a vaulted roof."""
    W, H = m.W, m.H
    h = H * 0.42
    rise = min(16, H * 0.2)
    D = H - h - rise
    m.add(S.box(0, 0, 0, W, D, h, m.wall, m.roof), S.vault(0, 0, W, D, h, rise, m.roof))
    dw = W * 0.5
    x0 = (W - dw) / 2
    m.add(S.box(x0, -1, 0, x0 + dw, D * 0.6, h * 0.8, (28, 30, 34), shade(m.ground, -0.3), subtract=True))
    for x in range(int(x0) + 3, int(x0 + dw) - 2, 6):
        m.add(S.box(x, -1.5, h * 0.8 + 1, x + 2, -0.5, h * 0.8 + 3, (250, 220, 120) if not m.grey else (220, 220, 220)))
    m.add(S.box(x0 - 2, -1, 0, x0, 1, h * 0.85, m.trim), S.box(x0 + dw, -1, 0, x0 + dw + 2, 1, h * 0.85, m.trim))
    m.windows(0, x0 - 4, 0, h * 0.5)
    m.windows(x0 + dw + 4, W, 0, h * 0.5)


def m_fortress_wall(m):
    """A long fortress wall with buttress towers, crenellations and a central gate."""
    W, H = m.W, m.H
    h = H * 0.45
    D = H - h - 14
    m.add(S.box(0, D * 0.3, 0, W, D, h, m.wall, m.roof))
    for x in range(2, int(W) - 4, 8):
        m.add(S.box(x, D * 0.3, h, x + 4, D * 0.3 + 3, h + 3, m.wall, m.roof))
    n = max(2, int(W // 64) + 1)
    for i in range(n + 1):
        x = 4 + (W - 24) * i / n
        m.add(S.box(x, 0, 0, x + 16, D, h + 10, shade(m.wall, -0.06), m.roof))
        m.add(S.hip(x - 1, -1, x + 17, D + 1, h + 10, 4, m.roof))
    if m.door_x is not None:
        m.door(D * 0.3, w=14, h=min(18, h * 0.6))


GIANTS = ["ship-hull", "debris", "palace-wall", "trench-wall", "stilt-city", "undercity-rim", "temple-stairs",
          "cliff-town", "city-edge", "hangar-wall", "fortress-wall", "cliff-door"]

BUILDS = {
    "block": m_block, "box": m_block,
    "L": lambda m: m_block(m, "L"), "oct": lambda m: m_block(m, "oct"), "T": lambda m: m_block(m, "T"),
    "notch": lambda m: m_block(m, "notch"),
    "pitched": lambda m: m_block(m, "rect", "pitched"), "barrel": lambda m: m_block(m, "rect", "barrel"),
    "court": m_court, "wings": m_wings, "palace": lambda m: m_wings(m, towers=True),
    "hall": lambda m: m_wings(m, dome_mid=True),
    "dome": m_dome, "domes2": m_domes2, "dome-block": m_dome_block, "store": m_store,
    "bunker": m_bunker, "buried": m_buried, "bay": m_bay, "pad": m_pad, "dome-porch": m_dome_porch,
    "spire": m_spire, "saucer": m_saucer, "glass-dome": m_glass_dome, "comm-tower": m_comm_tower,
    "hipped": m_hipped, "cliff-town": m_cliff_town, "city-edge": m_city_edge, "ship-hull": m_ship_hull,
    "hangar-wall": m_hangar_wall, "fortress-wall": m_fortress_wall, "debris": m_debris,
    "palace-wall": m_palace_wall, "trench-wall": m_trench_wall, "stilt-city": m_stilt_city,
    "undercity-rim": m_undercity_rim, "temple-stairs": m_temple_stairs,
    "cliff-door": m_cliff_door, "obelisk": m_obelisk,
    "quonset": m_quonset, "hangar": lambda m: m_quonset(m, wide=True),
    "stilts": m_stilts, "stilts-dome": lambda m: m_stilts(m, "dome", round_=True),
    "stilts-flat": lambda m: m_stilts(m, "flat"),
    "cone": m_cone, "tower": m_tower, "round-tower": m_round_tower, "stepped": m_stepped,
    "deck": m_deck, "plant": m_plant, "lab": m_lab, "arena": m_arena,
}
# the first-pass `kind` names, so an old catalogue entry still draws
KIND_TO_BUILD = {"box": "block", "dome": "dome", "pitched": "pitched", "stepped": "stepped", "tower": "tower",
                 "hall": "hall", "dish": "bay", "platform": "deck",
                 "sunken": "dome-porch", "sunken-dome": "dome-porch"}

_cache = {}


def sprite(b, st, seed, grey=False):
    name = st.get("build") or KIND_TO_BUILD.get(st.get("kind"), "block")
    name = KIND_TO_BUILD.get(name, name) if name not in BUILDS else name
    key = (name, tuple(b["size"]), b.get("door"), st["wall"], st["roof"], st["trim"], st.get("ground"),
           st.get("height"), st.get("top"), st.get("fork"), st.get("cliff"), str(b.get("rim")), b.get("facing"), seed & 0xFFFFFF, grey)
    if key not in _cache:
        m = M(b, st, seed, grey)
        BUILDS.get(name, m_block)(m)
        _cache[key] = S.render(m.sc, m.W, m.H)
    return _cache[key]


def building(img, b, st, seed, grey=False):
    sp = sprite(b, st, seed, grey)
    img.paste(sp, (b["at"][0] * C, b["at"][1] * C), sp)

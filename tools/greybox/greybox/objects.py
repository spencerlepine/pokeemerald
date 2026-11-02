"""Category 9: outdoor objects and props (kit category `objects`), one model per kind of thing.

Many wiki rows share a model: a parked X-wing and a parked fighter are both `o-fighter`, a sail barge
wreck and a cruiser hull are both `o-hull`. Rules are the kit's (kit.py): at most 16 solids, colours only
from the piece palette, variation from the seed. Scene y runs from the front (y = 0) to the back; a model
of footprint depth D and height h fills D + h rows of its box, so `_room(m, hz)` gives the depth left
once `hz` px of height are reserved.
"""
import math

from . import solid as S

K = S.K


def _p(m):
    from .kit import palette
    return palette(m)


def _room(m, hz):
    return max(6.0, m.H - hz)


def _wedge(x0, x1, y0, y1, nose, z0, z1, side, top, taper=0.0, **kw):
    """A hull pointing east: a box whose east end narrows to a nose `nose` px long."""
    ym = (y0 + y1) / 2
    poly = [(x0, y0), (x1 - nose, y0), (x1, ym - (y1 - y0) * 0.15), (x1, ym + (y1 - y0) * 0.15), (x1 - nose, y1), (x0, y1)]
    return S.prism(poly, z0, z1, side, top, taper=taper, **kw)


# ------------------------------------------------------------------------------------------------ craft
def o_speeder(m):
    """Parked landspeeder or snowspeeder: a low wedge hull hovering over its shadow, an open cockpit,
    one or two engine pods at the back."""
    p = _p(m)
    D = min(_room(m, 12), 22)
    y0, y1 = 2, D - 2
    m.add(_wedge(2, m.W - 2, y0, y1, m.W * 0.3, 3, 8, p["wall"], p["roof"]),
          S.box(m.W * 0.35, y0 + 3, 6, m.W * 0.6, y1 - 3, 9, p["glass"], p["dark"], subtract=True))
    n = 1 + m.r(1, 2)
    for i in range(n):
        y = (y0 + y1) / 2 if n == 1 else y0 + 2 + i * (y1 - y0 - 6)
        m.add(S.box(0, y, 4, m.W * 0.3, y + 4, 10, p["trim"], p["roof"]))


def o_fighter(m):
    """Parked starfighter (X-wing style, nose east): a long fuselage, wings out north and south with an
    engine at each tip, a glass canopy."""
    p = _p(m)
    D = _room(m, 14)
    cy = D / 2
    w = 5
    m.add(_wedge(4, m.W - 1, cy - w / 2, cy + w / 2, m.W * 0.35, 3, 10, p["wall"], p["roof"]),
          S.box(m.W * 0.45, cy - 1.5, 10, m.W * 0.6, cy + 1.5, 12, p["glass"], p["glass"]))
    for sgn in (-1, 1):
        ya, yb = sorted((cy + sgn * w / 2, cy + sgn * (D / 2 - 1)))
        m.add(S.box(m.W * 0.15, ya, 6, m.W * 0.4, yb, 7.5, p["roof"], p["roof"]),
              S.box(m.W * 0.08, (yb if sgn > 0 else ya) - 2, 5, m.W * 0.42, (yb if sgn > 0 else ya) + 2, 9, p["trim"], p["dark"]))
    m.add(S.box(0, cy - 1, 5, 4, cy + 1, 9, p["light"]))


def o_shuttle(m):
    """Lambda shuttle, wings folded up for landing: a cockpit body, a tall dorsal fin, two tall side wings."""
    p = _p(m)
    D = _room(m, 30)
    cy = D / 2
    m.add(_wedge(m.W * 0.2, m.W - 2, cy - 5, cy + 5, m.W * 0.25, 2, 12, p["wall"], p["roof"]),
          S.box(m.W * 0.7, cy - 5.5, 7, m.W - 6, cy - 3, 11, p["glass"], subtract=True),
          S.box(m.W * 0.25, cy - 1, 12, m.W * 0.6, cy + 1, 30, p["wall"], p["roof"]))
    for y in (cy - 7, cy + 5):
        m.add(S.box(m.W * 0.2, y, 4, m.W * 0.55, y + 2, 24, p["roof"], p["trim"]))
    m.add(S.box(0, cy - 3, 2, m.W * 0.2, cy + 3, 8, p["trim"], p["dark"]))


def o_freighter(m):
    """Light freighter: a flat hexagonal saucer hull, a cockpit pod off one side, two forward mandibles,
    a sensor dish on top."""
    p = _p(m)
    D = _room(m, 14)
    w = min(m.W * 0.75, D / K)
    cx, cy = m.W * 0.45, D / 2
    hx, hy = w / 2, w * K / 2
    k = hx * 0.45
    poly = [(cx - hx + k, cy - hy), (cx + hx - k, cy - hy), (cx + hx, cy), (cx + hx - k, cy + hy),
            (cx - hx + k, cy + hy), (cx - hx, cy)]
    m.add(S.prism(poly, 2, 9, p["wall"], p["roof"], taper=2))
    side = -1 if m.r(1, 2) else 1
    py = cy + side * hy * 0.7
    m.add(S.box(cx + hx * 0.4, py - 3, 4, cx + hx + 8, py + 3, 9, p["wall"], p["roof"]),
          S.box(cx + hx + 4, py - 2, 7, cx + hx + 8.5, py + 2, 9.5, p["glass"]))
    for dy in (-hy * 0.45, hy * 0.15):
        m.add(S.box(cx + hx - 2, cy + dy, 3, min(m.W - 1, cx + hx + 10), cy + dy + hy * 0.3, 7, p["roof"], p["trim"]))
    m.add(S.cylinder(cx - hx * 0.2, cy + hy * 0.3, 3, 0, 9, 11, p["trim"], p["light"]),
          S.box(cx - hx * 0.6, cy - hy * 0.3, 9, cx + hx * 0.1, cy + hy * 0.1, 10, p["roof"], p["trim"]))


def o_crawler(m):
    """Sandcrawler: a huge tapered hull on dark tracks, a ramp down the front, a slit window band."""
    p = _p(m)
    D = _room(m, 40)
    h = m.H - D - 2
    m.add(S.box(2, 1, 0, m.W - 2, D - 1, 6, p["dark"], p["dark"]),
          S.prism([(0, 2), (m.W, 2), (m.W - 4, D), (4, D)], 6, h, p["wall"], p["roof"], taper=m.W * 0.12),
          S.box(m.W * 0.1, 0, h * 0.62, m.W * 0.9, 3, h * 0.62 + 3, p["dark"], subtract=True))
    x = m.W * (0.3 + 0.1 * m.r(1, 4))
    m.add(S.prism([(x, -3), (x + 14, -3), (x + 14, 3), (x, 3)], 0, 3, p["trim"], p["roof"], taper=0),
          S.box(x + 1, 0, 6, x + 13, 3, 16, p["dark"], subtract=True))


def o_walker(m):
    """Fallen walker (AT-ST): the boxy head on its side, two broken legs and a few plates around it."""
    p = _p(m)
    D = _room(m, 14)
    m.add(S.prism([(m.W * 0.25, 2), (m.W * 0.7, 3), (m.W * 0.75, D - 4), (m.W * 0.3, D - 2)], 0, 12, p["wall"], p["roof"], taper=2),
          S.box(m.W * 0.7, D * 0.35, 4, m.W * 0.78, D * 0.55, 8, p["dark"]),
          S.box(2, D * 0.2, 0, m.W * 0.25, D * 0.2 + 3, 4, p["trim"], p["roof"]),
          S.box(m.W * 0.05, D * 0.6, 0, m.W * 0.3, D * 0.6 + 3, 4, p["trim"], p["roof"]))
    for i in range(2 + m.r(1, 2)):
        x = 4 + m.r(10 + i, int(max(2, m.W - 10)))
        y = 1 + m.r(20 + i, int(max(2, D - 4)))
        m.add(S.box(x, y, 0, x + 4, y + 3, 1.5, p["trim"]))


def o_hull(m):
    """Wreck or hull: a long broken hull half sunk in the ground, ribs showing where it split."""
    p = _p(m)
    D = _room(m, 16)
    h = 12 + 4 * m.r(1, 2)
    split = m.W * (0.45 + 0.1 * m.r(2, 3))
    m.add(S.prism([(2, 2), (split - 2, 1), (split, D - 3), (4, D - 2)], 0, h, p["wall"], p["roof"], taper=3),
          S.prism([(split + 3, 3), (m.W - 6, 3), (m.W - 1, D / 2), (m.W - 6, D - 3), (split + 5, D - 4)], 0, h * 0.7,
                  p["wall"], p["roof"], taper=3),
          S.box(split - 6, 2.5, 3, split - 2, D - 3, h - 2, p["dark"], subtract=True))
    for i in range(3):
        x = split - 5 + i * 1.6
        m.add(S.box(x, 3, 0, x + 0.6, D - 3, h - 1, p["trim"]))


def o_podracer(m):
    """Podracer on display: two long engines side by side, cables to a small cockpit pod behind."""
    p = _p(m)
    D = _room(m, 12)
    for y in (2, D - 7):
        m.add(_wedge(m.W * 0.35, m.W - 1, y, y + 5, 6, 2, 8, p["wall"], p["roof"]),
              S.box(m.W * 0.35, y + 1, 3, m.W * 0.38, y + 4, 7, p["dark"], subtract=True))
    m.add(S.box(m.W * 0.15, D / 2 - 0.5, 5, m.W * 0.4, D / 2 + 0.5, 6, p["trim"]),
          _wedge(1, m.W * 0.2, D / 2 - 3, D / 2 + 3, 4, 1, 7, p["roof"], p["trim"]),
          S.box(m.W * 0.06, D / 2 - 1.5, 6, m.W * 0.14, D / 2 + 1.5, 8, p["glass"]))


def o_pod(m):
    """Escape pod: an upright capsule with a domed cap, a hatch and a scorched ring around it."""
    p = _p(m)
    a = min(m.W / 2 - 2, 8)
    cy = a * K + 3
    cx = m.W / 2
    h = min(14, m.H - 2 * a * K - a * K - 6)
    m.add(S.cylinder(cx, cy, a + 3, 0, 0, 0.6, p["dark"], p["dark"]),
          S.cylinder(cx, cy, a, 0, 0, h, p["wall"]), S.dome(cx, cy, a, 0, h, None, p["roof"]),
          S.box(cx - 3, cy - a * K - 1, 2, cx + 3, cy - a * K + 2, h - 3, p["trim"], subtract=True),
          S.cylinder(cx, cy, a + 0.5, 0, h * 0.3, h * 0.3 + 1.5, p["trim"]))


# ------------------------------------------------------------------------------------------------ town props
def o_stall(m):
    """Market stall: a counter, four posts and a sloped cloth awning, goods on the counter."""
    p = _p(m)
    D = _room(m, 20)
    m.add(S.box(2, 2, 0, m.W - 2, 7, 8, p["wall"], p["roof"]))
    for x in (1, m.W - 3):
        for y in (1, D - 3):
            m.add(S.box(x, y, 0, x + 2, y + 2, 18 if y > 2 else 16, p["trim"]))
    m.add(S.prism([(0, 0), (m.W, 0), (m.W, D), (0, D)], 16, 18, p["roof"], p["light"] if m.r(1, 2) else p["roof"]),
          S.box(4, 3, 8, 8, 6, 11, p["light"]), S.box(m.W - 9, 3, 8, m.W - 5, 6, 10, p["glass"]))


def o_droid(m):
    """Droid (gonk style): a box body on two stubby legs, a light on top."""
    p = _p(m)
    cx = m.W / 2
    w = min(m.W - 4, 10)
    m.add(S.box(cx - w / 2 + 1, 2, 0, cx - w / 2 + 3, 5, 3, p["dark"]), S.box(cx + w / 2 - 3, 2, 0, cx + w / 2 - 1, 5, 3, p["dark"]),
          S.box(cx - w / 2, 1, 3, cx + w / 2, 7, 13, p["wall"], p["roof"]),
          S.box(cx - 1, 3, 13, cx + 1, 5, 14.5, p["light"]))


def o_sign(m):
    """Holo-sign: a post with a lit panel on top, a frame around it."""
    p = _p(m)
    cx = m.W / 2
    w = min(m.W - 2, 14)
    h = min(m.H - 8, 24)
    m.add(S.box(cx - 1, 2, 0, cx + 1, 4, h - 8, p["trim"]),
          S.box(cx - w / 2, 2, h - 9, cx + w / 2, 4, h, p["trim"], p["dark"]),
          S.box(cx - w / 2 + 1, 1.5, h - 8, cx + w / 2 - 1, 3, h - 1, p["light"]))


def o_trough(m):
    """Trough or basin: a long low stone box, hollow, with a pump post at one end."""
    p = _p(m)
    D = min(_room(m, 12), 12)
    m.add(S.box(2, 2, 0, m.W - 2, D, 6, p["wall"], p["roof"]),
          S.box(4, 4, 2, m.W - 4, D - 2, 7, p["glass"], p["glass"], subtract=True))
    x = 3 if m.r(1, 2) else m.W - 6
    m.add(S.box(x, D - 3, 0, x + 3, D, 12, p["trim"], p["dark"]))


def o_wall(m):
    """Free-standing wall: a long low wall with rounded posts at the ends and a cap, broken by the seed."""
    p = _p(m)
    D = 6
    h = min(m.H - D - 2, 14)
    gap = m.r(1, 3) == 0
    xs = [(1, m.W / 2 - 3), (m.W / 2 + 3, m.W - 1)] if gap else [(1, m.W - 1)]
    for x0, x1 in xs:
        m.add(S.box(x0, 1, 0, x1, D, h, p["wall"], p["roof"]),
              S.box(x0 - 0.5, 0.5, h, x1 + 0.5, D + 0.5, h + 1.5, p["trim"], p["roof"]))
    for x in (2.5, m.W - 2.5):
        m.add(S.cylinder(x, D / 2 + 0.5, 3, 0, 0, h + 2, p["wall"], p["roof"]))


def o_rail(m):
    """Railing or promenade rail: thin posts and a top bar along the front edge."""
    p = _p(m)
    h = 9
    m.add(S.box(0, 1, h - 1.5, m.W, 3, h, p["trim"], p["light"]))
    n = max(2, int(m.W // 12) + 1)
    for i in range(n):
        x = i * (m.W - 2) / (n - 1)
        m.add(S.box(x, 1.5, 0, x + 2, 2.5, h - 1.5, p["trim"]))


def o_walkway(m):
    """Raised walkway, dock or bridge: a deck on posts, plank seams, a low rail on the far side."""
    p = _p(m)
    z = 8
    D = _room(m, z + 6)
    m.add(S.box(0, 1, z - 2, m.W, D, z, p["wall"], p["roof"]))
    for x in (2, m.W / 2 - 1, m.W - 4):
        for y in (2, D - 3):
            m.add(S.box(x, y, 0, x + 2, y + 2, z - 2, p["trim"], p["dark"]))
    m.add(S.box(0, D - 1.5, z, m.W, D, z + 5, p["trim"]))
    for i in range(1, 4):
        m.add(S.box(m.W * i / 4 - 0.3, 0.5, z - 1, m.W * i / 4 + 0.3, D, z + 0.3, p["dark"], subtract=True))


def o_tent(m):
    """Camp: two or three pitched cloth tents and a fire ring."""
    p = _p(m)
    D = _room(m, 12)
    n = 2 + (m.cw >= 4 and m.r(1, 2))
    w = (m.W - 4) / n
    for i in range(n):
        x = 2 + i * w
        y = 1 + (i % 2) * 3
        dp = min(D - y - 1, 14)
        m.add(S.box(x, y, 0, x + w - 2, y + dp, 1, p["wall"], p["wall"]),
              S.gable(x, y, x + w - 2, y + dp, 1, 11, p["roof"]),
              S.box(x + (w - 2) / 2 - 2, y - 0.5, 0, x + (w - 2) / 2 + 2, y + 2, 6, p["dark"], subtract=True))
    m.add(S.cylinder(m.W / 2, 1.5, 2.5, 0, 0, 1.5, p["dark"], p["light"]))


def o_totem(m):
    """Totem and drum: a carved post of stacked blocks and a big drum beside it."""
    p = _p(m)
    cx = m.W * 0.35
    h = min(m.H - 10, 30)
    n = 3
    for i in range(n):
        z0 = i * h / n
        w = 5 - i * 0.7
        m.add(S.box(cx - w, 3, z0, cx + w, 7, z0 + h / n - 1, p["wall"] if i % 2 else p["roof"], p["roof"]))
    m.add(S.box(cx - 6, 4, h - 2, cx + 6, 6, h, p["trim"]))
    a = min(m.W * 0.22, 6)
    m.add(S.cylinder(m.W * 0.75, a * K + 2, a, 0, 0, 8, p["trim"], p["light"]))


def o_glider(m):
    """Glider or trap: a triangular wing of cloth on a light frame, propped on two poles."""
    p = _p(m)
    D = _room(m, 16)
    m.add(S.prism([(1, 2), (m.W - 1, D / 2), (1, D - 2)], 12, 13.5, p["roof"], p["light"]),
          S.box(m.W * 0.25, D / 2 - 1, 0, m.W * 0.25 + 1.5, D / 2 + 1, 12, p["trim"]),
          S.box(m.W * 0.7, D / 2 - 1, 0, m.W * 0.7 + 1.5, D / 2 + 1, 12, p["trim"]),
          S.box(1, D / 2 - 0.5, 13.5, m.W - 1, D / 2 + 0.5, 14.5, p["trim"]))


def o_logs(m):
    """Log trap or fallen log: one or two long logs on the ground or slung between two posts."""
    p = _p(m)
    D = _room(m, 16)
    slung = m.r(1, 2) == 0
    z = 10 if slung else 0
    for i in range(1 + (not slung)):
        y = 2 + i * 6
        m.add(S.box(2, y, z, m.W - 2, y + 5, z + 5, p["wall"], p["roof"]),
              S.box(m.W - 3, y + 0.5, z + 0.5, m.W - 1.5, y + 4.5, z + 4.5, p["light"]))
    if slung:
        for x in (1, m.W - 3):
            m.add(S.box(x, 3, 0, x + 2, 5, 17, p["trim"], p["dark"]))
        m.add(S.box(1, 3.5, 15, m.W - 1, 4.5, 16, p["trim"]))


def o_rack(m):
    """Rack: a frame with two to four panels or weapons hanging in it (TIE rack, bowcaster rack)."""
    p = _p(m)
    D = 6
    h = min(m.H - D - 2, 26)
    m.add(S.box(0, 1, h - 2, m.W, D, h, p["trim"], p["roof"]),
          S.box(0, 1, 0, 2, D, h, p["trim"]), S.box(m.W - 2, 1, 0, m.W, D, h, p["trim"]))
    n = 2 + m.r(1, 3)
    w = (m.W - 6) / n
    for i in range(n):
        x = 3 + i * w
        m.add(S.prism([(x + w * 0.25, 2), (x + w * 0.75, 2), (x + w - 1, 3.5), (x + w * 0.75, 5), (x + w * 0.25, 5), (x + 1, 3.5)],
                      4, h - 3, p["wall"], p["roof"]))


def o_bones(m):
    """Skeleton (bantha, krayt): a spine along the ground with rib pairs arching over it and a skull."""
    p = _p(m)
    D = _room(m, 12)
    cy = D / 2
    m.add(S.box(4, cy - 1, 0, m.W - 6, cy + 1, 3, p["wall"], p["roof"]))
    n = max(2, min(6, int((m.W - 14) // 7)))
    for i in range(n):
        x = 8 + i * 7
        h = 10 - abs(i - n / 2) * 1.2
        m.add(S.prism([(x, cy - D / 2 + 2), (x + 1.5, cy - D / 2 + 2), (x + 1.5, cy + D / 2 - 2), (x, cy + D / 2 - 2)],
                      0, h, p["wall"], p["roof"], taper=0))
    m.add(S.prism([(m.W - 8, cy - 4), (m.W - 2, cy - 2), (m.W - 1, cy + 2), (m.W - 8, cy + 4)], 0, 6, p["wall"], p["roof"], taper=1),
          S.box(m.W - 6, cy - 4.5, 3, m.W - 4, cy - 3, 5, p["dark"], subtract=True))


def o_pipe(m):
    """Pipe run: a long pipe on supports with a valve wheel, east-west."""
    p = _p(m)
    z = 6
    m.add(S.box(0, 2, z, m.W, 6, z + 4, p["wall"], p["roof"]))
    for x in (3, m.W - 6):
        m.add(S.box(x, 2.5, 0, x + 3, 5.5, z, p["trim"], p["dark"]))
    x = m.W * (0.4 + 0.2 * m.r(1, 2))
    m.add(S.box(x - 1, 1, z - 1, x + 1, 7, z + 5, p["trim"]),
          S.box(x - 0.5, 3.5, z + 5, x + 0.5, 4.5, z + 9, p["trim"]),
          S.box(x - 3, 3.5, z + 9, x + 3, 4.5, z + 10, p["light"]))


def o_greenhouse(m):
    """Greenhouse: a glass box with a pitched glass roof on a low wall, a frame line down the middle."""
    p = _p(m)
    D = _room(m, 20)
    m.add(S.box(1, 1, 0, m.W - 1, D, 4, p["wall"], p["roof"]),
          S.box(2, 2, 4, m.W - 2, D - 1, 12, p["glass"], p["glass"]),
          S.gable(2, 2, m.W - 2, D - 1, 12, 7, p["glass"]),
          S.box(m.W / 2 - 0.5, 1.5, 4, m.W / 2 + 0.5, D - 0.5, 18, p["trim"]),
          S.box(m.W / 2 - 3, 1, 0, m.W / 2 + 3, 3, 10, p["trim"], subtract=True))


def o_candles(m):
    """Candles or offerings: a cluster of small posts of different heights with lit tops, on a step."""
    p = _p(m)
    D = _room(m, 12)
    m.add(S.box(1, 1, 0, m.W - 1, D - 1, 2, p["wall"], p["roof"]))
    n = 4 + m.r(1, 4)
    for i in range(n):
        x = 3 + m.r(10 + i, int(max(2, m.W - 6)))
        y = 2 + m.r(20 + i, int(max(2, D - 5)))
        h = 4 + m.r(30 + i, 6)
        m.add(S.box(x, y, 2, x + 1.5, y + 1.5, 2 + h, p["wall"], p["light"]))


def o_statue(m):
    """Toppled statue: a long figure lying on its side, its head broken off beside it, the empty plinth."""
    p = _p(m)
    D = _room(m, 14)
    m.add(S.box(1, D - 9, 0, 9, D - 1, 8, p["wall"], p["roof"]),
          S.prism([(10, 3), (m.W - 10, 2), (m.W - 9, 9), (11, 10)], 0, 9, p["wall"], p["roof"], taper=2),
          S.box(m.W * 0.45, 2, 0, m.W * 0.55, 10, 10, p["trim"], p["roof"]),
          S.prism(S.ring_pts(m.W - 5, 5, 4, 3, 10), 0, 7, p["wall"], p["roof"], taper=1))


def o_lift(m):
    """Lift or doorway block: a tall box with a lit door slot and a light strip on top."""
    p = _p(m)
    D = 10
    h = min(m.H - D - 2, 30)
    m.add(S.box(1, 1, 0, m.W - 1, D, h, p["wall"], p["roof"]),
          S.box(m.W / 2 - 5, 0, 0, m.W / 2 + 5, 2, 18, p["dark"], subtract=True),
          S.box(m.W / 2 - 5, 0.5, 18.5, m.W / 2 + 5, 1.5, 20, p["light"]))


OBJECTS = {
    "o-speeder": (o_speeder, [(3, 2), (4, 2)]),
    "o-fighter": (o_fighter, [(4, 3), (5, 4)]),
    "o-shuttle": (o_shuttle, [(4, 4), (5, 4)]),
    "o-freighter": (o_freighter, [(6, 4), (8, 5)]),
    "o-crawler": (o_crawler, [(6, 5), (8, 6)]),
    "o-walker": (o_walker, [(3, 2), (4, 3)]),
    "o-hull": (o_hull, [(6, 3), (8, 4)]),
    "o-podracer": (o_podracer, [(4, 2), (5, 3)]),
    "o-pod": (o_pod, [(2, 2)]),
    "o-stall": (o_stall, [(3, 2), (4, 3)]),
    "o-droid": (o_droid, [(1, 2)]),
    "o-sign": (o_sign, [(1, 2), (2, 2)]),
    "o-trough": (o_trough, [(3, 2)]),
    "o-wall": (o_wall, [(4, 2), (6, 2)]),
    "o-rail": (o_rail, [(4, 1), (6, 1)]),
    "o-walkway": (o_walkway, [(4, 2), (6, 3)]),
    "o-tent": (o_tent, [(4, 2), (5, 3)]),
    "o-totem": (o_totem, [(2, 3)]),
    "o-glider": (o_glider, [(3, 2)]),
    "o-logs": (o_logs, [(4, 2)]),
    "o-rack": (o_rack, [(3, 2), (4, 3)]),
    "o-bones": (o_bones, [(4, 2), (6, 3)]),
    "o-pipe": (o_pipe, [(4, 1), (6, 2)]),
    "o-greenhouse": (o_greenhouse, [(3, 3), (4, 3)]),
    "o-candles": (o_candles, [(2, 2)]),
    "o-statue": (o_statue, [(4, 2), (5, 3)]),
    "o-lift": (o_lift, [(2, 3)]),
}

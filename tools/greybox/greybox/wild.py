"""Category 10: wild nature that is not a tree canopy (kit category `wild`, `w-` names).

The nature category (kit.py) holds what a `T` cell becomes (pine, boulder, shard, fungus); landforms hold
big rock shapes. This one holds the rest of the planets' nature as placed pieces: reeds and scrub, ferns,
hanging vines, crystal clusters, basalt columns, steam vents, dunes, the sarlacc pit, giant trunks (the
canopy is above the screen, so only trunk and roots show), dead trees and spore pods. Trees with full
canopies stay parked until the end (owner); `w-trunk` is the stand-in for the giant forest trees.
Same rules as every kit category: at most 16 solids, palette colours only, variation from the seed.
Colours: wall = stem, trunk or rock side; roof = leaf, cap or rock top; glass = crystal; light = glow.
"""
import math

from . import solid as S

K = S.K


def _p(m):
    from .kit import palette
    return palette(m)


def _poly(m, k, cx, cy, a, n=7):
    from .kit import rock_poly
    return rock_poly(m, k, cx, cy, a, n)


def w_reeds(m):
    """Reeds or scrub: a clump of thin stems of different heights, a few with a seed head."""
    p = _p(m)
    n = min(14, 5 + m.cw * 3)
    hmax = m.H - 8
    for i in range(n):
        x = 2 + m.r(i, int(max(2, m.W - 4)))
        y = 1 + m.r(20 + i, 6)
        h = hmax * (0.45 + 0.08 * m.r(40 + i, 7))
        m.add(S.box(x, y, 0, x + 1.2, y + 1.2, h, p["roof"], p["roof"] if i % 3 else p["wall"]))


def w_scrub(m):
    """Desert scrub: two or three low, spiky rounded clumps."""
    p = _p(m)
    n = 1 + m.r(1, 2) + (m.cw > 1)
    for i in range(n):
        a = (m.W / 2 - 2) * (1 - 0.25 * i)
        cx = m.W / 2 + (i - (n - 1) / 2) * m.W * 0.3
        m.add(S.prism(_poly(m, 7 * i, cx, a * K + 1 + i, a, 7), 0, a * 0.8, p["roof"], p["roof"], taper=a * 0.7))


def w_fern(m):
    """Fern clump: fronds fanning out from a centre, low and wide."""
    p = _p(m)
    cx, cy = m.W / 2, (m.H - 8) / 2
    n = 6 + m.r(1, 3)
    L = min(m.W / 2 - 1, (m.H - 8) / 2 / K)
    for i in range(n):
        t = 2 * math.pi * (i + 0.3 * m.r(i, 3)) / n
        ex, ey = cx + L * math.cos(t), cy + L * K * math.sin(t)
        nx, ny = -math.sin(t) * 2, math.cos(t) * 2 * K
        m.add(S.prism([(cx - nx, cy - ny), (cx + nx, cy + ny), (ex, ey)], 0, 4 + 2 * (i % 2),
                      p["roof"], p["roof"], taper=1.5))
    m.add(S.cylinder(cx, cy, 2, 0, 0, 5, p["wall"], p["roof"]))


def w_vines(m):
    """Hanging vines or moss: a curtain of strands hanging from a high bar (a branch above the screen)."""
    p = _p(m)
    top = m.H - 6
    m.add(S.box(0, 3, top - 2, m.W, 6, top, p["wall"], p["wall"]))
    n = max(3, int(m.W // 4))
    for i in range(n):
        x = 1 + i * (m.W - 2) / n
        L = top * (0.35 + 0.1 * m.r(i, 6))
        m.add(S.box(x, 4, top - L, x + 1.5, 5, top - 2, p["roof"], p["roof"]))
        if i >= 13:
            break


def w_crystal(m):
    """Crystal outcrop (kyber): hexagonal crystals leaning out of a low rock base, lit at the tips."""
    p = _p(m)
    a = m.W * 0.32
    cy = a * K + 2
    m.add(S.prism(_poly(m, 3, m.W / 2, cy, a), 0, 4, p["wall"], p["roof"], taper=2))
    n = 3 + m.r(1, 3)
    hmax = m.H - cy - 6
    for i in range(n):
        r = 2.6 + m.r(10 + i, 3) * 0.7
        cx = m.W / 2 + (i - (n - 1) / 2) * (m.W - 10) / max(1, n - 1)
        y = cy - 1 + m.r(20 + i, 3)
        h = hmax * (0.45 + 0.12 * m.r(30 + i, 5))
        hexa = [(cx + r * math.cos(math.pi / 3 * j), y + r * K * math.sin(math.pi / 3 * j)) for j in range(6)]
        m.add(S.prism(hexa, 2, h, p["glass"], p["light"], taper=r * 0.75))


def w_columns(m):
    """Basalt columns: a packed cluster of hexagonal columns stepping up toward the back."""
    p = _p(m)
    r = 4.0
    dx, dy = r * 1.5, r * K * 1.73
    cols = max(2, int((m.W - 2) // dx))
    rows = 3
    k = 0
    for j in range(rows):
        for i in range(cols):
            if k >= 15:
                break
            cx = 1 + r + i * dx
            cy = 1 + r * K + j * dy + (i % 2) * dy / 2
            h = 6 + j * 5 + 4 * m.r(k, 3)
            if cy + r * K + h > m.H - 1 or cx + r > m.W:
                continue
            hexa = [(cx + r * math.cos(math.pi / 3 * q), cy + r * K * math.sin(math.pi / 3 * q)) for q in range(6)]
            m.add(S.prism(hexa, 0, h, p["wall"], p["roof"]))
            k += 1


def w_vent(m):
    """Steam vent: a cracked rock cone with a dark mouth and a pale plume rising from it."""
    p = _p(m)
    a = m.W / 2 - 2
    cy = a * K + 1
    cx = m.W / 2
    m.add(S.prism(_poly(m, 5, cx, cy, a), 0, 6, p["wall"], p["roof"], taper=a * 0.5),
          S.cylinder(cx, cy, a * 0.3, 0, 2, 7, p["dark"], p["dark"], subtract=True))
    h = m.H - 2 * a * K - 4
    for i in range(3):
        z = 6 + i * (h - 6) / 3
        r = a * (0.3 + 0.12 * i)
        m.add(S.cylinder(cx + (i - 1) * 1.5, cy, r, 0, z, z + (h - 6) / 3 - 1, p["glass"], p["glass"]))


def w_dune(m):
    """Dune or ash drift: a long low mound with a sharp crest and a steep lee side."""
    p = _p(m)
    D = m.H - 10
    crest = D * (0.45 + 0.1 * m.r(1, 3))
    h = min(10, D * 0.6)
    # a ridge running east-west: a gentle windward slope in front, a steeper lee slope behind
    m.add(S.Solid([[0, 0, -1, 0], [1, 0, 0, m.W - 1], [-1, 0, 0, -1],
                   [0, -h, crest, 0], [0, h, D - crest, h * D]], p["roof"], p["roof"]),
          S.box(1, crest - 0.6, h - 1.2, m.W - 1, crest + 0.6, h + 0.3, p["wall"]))


def w_pit(m):
    """Sarlacc pit: a funnel of sand sloping down to a dark mouth ringed with teeth."""
    from .kit import _slab
    p = _p(m)
    m.add(_slab(m, 16))
    cx = m.W / 2
    a = m.W / 2 - 1
    cy = a * K + 1
    m.add(S.cylinder(cx, cy, a, 0, -4, 1, p["roof"], p["roof"], subtract=True, below=True),
          S.cylinder(cx, cy, a * 0.6, 0, -8, -3, p["wall"], p["wall"], subtract=True, below=True),
          S.cylinder(cx, cy, a * 0.25, 0, -14, -7, p["dark"], p["dark"], subtract=True, below=True))
    for i in range(6):
        t = 2 * math.pi * i / 6
        x, y = cx + a * 0.3 * math.cos(t), cy + a * 0.3 * K * math.sin(t)
        m.add(S.box(x - 0.7, y - 0.5, -8, x + 0.7, y + 0.5, -5, p["light"], below=True))


def w_trunk(m):
    """Giant trunk (wroshyr, redwood, massassi): a thick trunk rising off the top of the screen, a flare
    of roots at its foot, one low branch."""
    p = _p(m)
    cx = m.W / 2
    a = min(m.W / 2 - 4, 12)
    cy = a * K + 4
    h = m.H - 2 * a * K - 4
    m.add(S.cylinder(cx, cy, a, 0, 0, h, p["wall"], p["wall"]))
    for i in range(4):
        t = math.pi * (0.15 + 0.7 * i / 3)
        x, y = cx + (a + 2) * math.cos(t + math.pi), cy - (a + 2) * K * math.sin(t)
        m.add(S.prism(_poly(m, 11 * i, x, y, 3.5, 5), 0, 5, p["wall"], p["wall"], taper=2))
    side = 1 if m.r(1, 2) else -1
    z = h * 0.6
    m.add(S.box(cx + side * a * 0.6 if side > 0 else 1, cy - 1, z, m.W - 1 if side > 0 else cx - a * 0.6, cy + 1, z + 3, p["wall"]),
          S.box(1 if side < 0 else m.W - 8, cy - 2, z + 3, 8 if side < 0 else m.W - 1, cy + 2, z + 6, p["roof"], p["roof"]))


def w_deadtree(m):
    """Dead tree: a bare leaning trunk with two or three bare branches."""
    p = _p(m)
    cx = m.W / 2
    h = m.H - 8
    m.add(S.prism([(cx - 2, 2), (cx + 2, 2), (cx + 2, 5), (cx - 2, 5)], 0, h * 0.7, p["wall"], p["wall"], taper=1))
    for i in range(2 + m.r(1, 2)):
        z = h * (0.35 + 0.15 * i)
        side = 1 if (i + m.r(2, 2)) % 2 else -1
        L = m.W / 2 - 2
        x0, x1 = (cx, cx + L) if side > 0 else (cx - L, cx)
        m.add(S.box(x0, 3, z, x1, 4, z + 1.5, p["wall"]),
              S.box(x1 - 1 if side > 0 else x0, 3, z, x1 if side > 0 else x0 + 1, 4, z + 5, p["wall"]))


def w_pods(m):
    """Spore pods: thin stalks of different heights, each ending in a round glowing pod."""
    p = _p(m)
    n = 2 + m.r(1, 3)
    for i in range(n):
        cx = 3 + (i + 0.5) * (m.W - 6) / n
        cy = 4 + 3 * (i % 2)
        h = (m.H - 14) * (0.5 + 0.12 * m.r(10 + i, 4))
        r = 2.5 + m.r(20 + i, 2)
        m.add(S.box(cx - 0.6, cy - 0.6, 0, cx + 0.6, cy + 0.6, h, p["wall"]),
              S.dome(cx, cy, r, 0, h - r * K, r * K, p["light"] if i % 2 else p["roof"]),
              S.cylinder(cx, cy, r, 0, h - r * K - 2, h - r * K, p["roof"], p["roof"]))


WILD = {
    "w-reeds": (w_reeds, [(1, 2), (2, 2)]),
    "w-scrub": (w_scrub, [(1, 1), (2, 1)]),
    "w-fern": (w_fern, [(2, 2)]),
    "w-vines": (w_vines, [(2, 3), (3, 3)]),
    "w-crystal": (w_crystal, [(2, 2), (3, 3)]),
    "w-columns": (w_columns, [(3, 3), (4, 4)]),
    "w-vent": (w_vent, [(2, 3)]),
    "w-dune": (w_dune, [(4, 2), (6, 3)]),
    "w-pit": (w_pit, [(4, 3), (6, 4)]),
    "w-trunk": (w_trunk, [(2, 4), (3, 5)]),
    "w-deadtree": (w_deadtree, [(2, 3)]),
    "w-pods": (w_pods, [(2, 3)]),
}

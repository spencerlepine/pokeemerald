"""Greybox 3D: convex solids, exact ray casting in the game's projection, shading to pixel sprites.

The approach comes from z-day's building generator (.claude/tools/art/world/structures/buildings):
model the building as simple 3D solids, then cast one ray per pixel and shade by the surface normal.
Nothing is drawn by hand, so perspective, ovals and occlusion are always right.

Units are pixels: 1 map cell = 16 px. World axes: +x east (screen right), +y north (away from the
camera), +z up. A screen row is the line y + z = const, so one cell north on the ground and one cell up a
wall both move 16 px up the screen. A building of footprint W x D px and wall height h px fills a sprite
of W x (D + h) px, which keeps every footprint on whole map cells. Only top and south faces show.

A solid is a convex polytope (planes n.p <= d). A scene is additive solids minus subtractive ones
(a door recess, a sunken courtyard, the inside of an arena). Round things are many-sided polytopes:
an elliptic prism, a half-ellipsoid dome, a cone, a barrel vault.
"""
import math

import numpy as np

EPS = 1e-4
RAY = np.array([0.0, 1.0, -1.0])
# THE PROJECTION RULE for round things. The game's view is a 45-degree camera drawn without
# foreshortening (one cell north = one cell up = 16 px). Seen through that camera, a real circle of radius r
# on the ground shows as an oval r wide and r * K deep, and a real height h shows as h * K. So every round
# primitive below takes only its true radius `a`: the depth is always a * K, a dome is at most a * K tall
# (a hemisphere), and a cone's base follows the same oval. Callers cannot pass their own depth, so no
# building can squash or stretch a round shape. A shape that does not fit its box must shrink, not squash.
K = math.cos(math.radians(45))
LIGHT = np.array([-0.5, -0.25, 0.83])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


class Solid:
    def __init__(self, planes, side, top=None, subtract=False, outline=True, hide_top=False, below=False):
        self.planes = np.asarray(planes, float)
        self.side = side                    # colour of steep faces
        self.top = top if top is not None else side   # colour of faces that look up
        self.subtract = subtract
        self.outline = outline              # False for ground slabs that should blend into the terrain
        self.below = below                  # may be seen below ground level (a cliff edge dropping away)
        self.hide_top = hide_top            # its top faces stay see-through (the terrain shows), but still hide what is behind

    def intersect(self, o, d):
        n, dist = self.planes[:, :3], self.planes[:, 3]
        num = dist[None, :] - o @ n.T
        den = np.broadcast_to(d @ n.T, num.shape)
        with np.errstate(divide="ignore", invalid="ignore"):
            t = num / den
        enter, leave = den < -1e-12, den > 1e-12
        miss = np.any((np.abs(den) <= 1e-12) & (num < 0), axis=1)
        t_in = np.where(enter, t, -np.inf)
        t_out = np.where(leave, t, np.inf)
        i_in, i_out = np.argmax(t_in, axis=1), np.argmin(t_out, axis=1)
        N = len(o)
        tin, tout = t_in[np.arange(N), i_in], t_out[np.arange(N), i_out]
        tout = np.where(miss | (tin >= tout), -np.inf, tout)
        return tin, tout, i_in, i_out

    def inside(self, p):
        return np.all(p @ self.planes[:, :3].T <= self.planes[:, 3] + 1e-9, axis=1)


class Scene:
    def __init__(self, solids=()):
        self.solids = list(solids)

    def add(self, *s):
        self.solids.extend(s)
        return self

    def solid_at(self, p):
        """Solids combine in the order they were added: a cut removes only what came before it, so a
        pit can be cut and then furnished (steps, a pad, a ladder)."""
        add = np.zeros(len(p), bool)
        for s in self.solids:
            if s.subtract:
                add &= ~s.inside(p)
            else:
                add |= s.inside(p)
        return add

    def cast(self, o, d, tmin=0.0):
        N = len(o)
        best_t = np.full(N, np.inf)
        best_s = np.full(N, -1)
        best_n = np.zeros((N, 3))
        for si, s in enumerate(self.solids):
            tin, tout, i_in, i_out = s.intersect(o, d)
            if s.subtract:
                t, plane, sign = tout, i_out, -1.0
            else:
                t, plane, sign = tin, i_in, 1.0
            ok = np.isfinite(t) & (tout > tin) & (t > tmin) & (t < best_t)
            if not ok.any():
                continue
            idx = np.nonzero(ok)[0]
            q = o[idx] + (t[idx, None] + EPS) * d
            idx = idx[self.solid_at(q)]
            best_t[idx], best_s[idx] = t[idx], si
            best_n[idx] = sign * s.planes[plane[idx], :3]
        nn = np.linalg.norm(best_n, axis=1, keepdims=True)
        best_n = np.where(nn > 0, best_n / np.maximum(nn, 1e-12), 0)
        return best_t, best_s, best_n


# ------------------------------------------------------------------------------------------------ solids
def box(x0, y0, z0, x1, y1, z1, side, top=None, **kw):
    return Solid([[1, 0, 0, x1], [-1, 0, 0, -x0], [0, 1, 0, y1], [0, -1, 0, -y0], [0, 0, 1, z1], [0, 0, -1, -z0]],
                 side, top, **kw)


def ring_pts(cx, cy, a, b, n=28):
    return [(cx + a * math.cos(2 * math.pi * (i + 0.5) / n), cy + b * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


def _inset2(poly, t):
    """A convex polygon moved inward by t px (mitred corners)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    lines = []
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        nx, ny = by - ay, -(bx - ax)
        L = math.hypot(nx, ny) or 1
        nx, ny = nx / L, ny / L
        if nx * (cx - ax) + ny * (cy - ay) < 0:
            nx, ny = -nx, -ny
        lines.append((nx, ny, nx * ax + ny * ay + t))     # inward normal, n.p = d
    out = []
    for i in range(len(lines)):
        a1, b1, c1 = lines[i - 1]
        a2, b2, c2 = lines[i]
        det = a1 * b2 - a2 * b1
        out.append(((c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det))
    return out


def prism(poly, z0, z1, side, top=None, taper=0.0, **kw):
    """A convex footprint polygon (counter-clockwise or not) extruded from z0 to z1. taper slopes the
    walls inward by that many px over the height (a bunker, a pyramid tier)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    k = taper / max(z1 - z0, 1e-6)
    planes = [[0, 0, 1, z1], [0, 0, -1, -z0]]
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        nx, ny = by - ay, -(bx - ax)
        L = math.hypot(nx, ny) or 1
        nx, ny = nx / L, ny / L
        if nx * (cx - ax) + ny * (cy - ay) > 0:
            nx, ny = -nx, -ny
        planes.append([nx, ny, k, nx * ax + ny * ay + k * z0])
    return Solid(planes, side, top, **kw)


def cylinder(cx, cy, a, b, z0, z1, side, top=None, n=28, exact=False, **kw):
    """A round prism of true radius a. Its depth is a * K by the projection rule; `b` is ignored unless
    `exact` (a footprint fixed by the map, like Cloud City's outline)."""
    return prism(ring_pts(cx, cy, a, b if exact else a * K, n), z0, z1, side, top, **kw)


def dome(cx, cy, a, b, z0, c, col, rings=6, n=24, **kw):
    """A dome of true radius a sitting on z0: depth a * K, height c but never more than a * K (a
    hemisphere). A lower c gives a shallower dome. `b` is ignored (projection rule)."""
    b = a * K
    c = b if c is None else max(1.0, min(c, b))
    planes = [[0, 0, -1, -z0]]
    for j in range(rings):
        ph = (j + 0.5) / rings * (math.pi / 2)
        for i in range(n):
            th = 2 * math.pi * (i + 0.5 * (j % 2)) / n
            p0 = np.array([a * math.cos(ph) * math.cos(th), b * math.cos(ph) * math.sin(th), c * math.sin(ph)])
            nrm = p0 / np.array([a * a, b * b, c * c])
            nrm /= np.linalg.norm(nrm)
            planes.append([*nrm, nrm @ p0 + nrm @ np.array([cx, cy, z0])])
    planes.append([0, 0, 1, z0 + c])
    return Solid(planes, col, col, **kw)


def cone(cx, cy, a, b, z0, hgt, col, n=20, **kw):
    """A cone of true base radius a (depth a * K by the projection rule), hgt tall on screen."""
    b = a * K
    apex = np.array([cx, cy, z0 + hgt])
    pts = ring_pts(cx, cy, a, b, n)
    planes = [[0, 0, -1, -z0]]
    for i in range(n):
        p = np.array([*pts[i], z0])
        q = np.array([*pts[(i + 1) % n], z0])
        nrm = np.cross(q - p, apex - p)
        if nrm @ (np.array([cx, cy, z0 + hgt * 0.3]) - p) > 0:
            nrm = -nrm
        nrm /= np.linalg.norm(nrm)
        planes.append([*nrm, nrm @ p])
    return Solid(planes, col, col, **kw)


def gable(x0, y0, x1, y1, z0, rise, col, **kw):
    """A pitched roof, ridge running east-west."""
    ym = (y0 + y1) / 2
    half = (y1 - y0) / 2
    f = np.array([0, -rise, half]) / math.hypot(rise, half)
    bk = np.array([0, rise, half]) / math.hypot(rise, half)
    return Solid([[1, 0, 0, x1], [-1, 0, 0, -x0], [0, 0, -1, -z0],
                  [*f, f @ np.array([0, y0, z0])], [*bk, bk @ np.array([0, y1, z0])]], col, col, **kw)


def hip(x0, y0, x1, y1, z0, rise, col, **kw):
    """A hip roof: four slopes meeting at a ridge (or a point on a square)."""
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    r = min(hw, hd)
    planes = [[0, 0, -1, -z0]]
    for nx, ny, px, py in ((0, -1, 0, y0), (0, 1, 0, y1), (-1, 0, x0, 0), (1, 0, x1, 0)):
        n = np.array([nx * rise, ny * rise, r])
        n /= np.linalg.norm(n)
        planes.append([*n, n @ np.array([px, py, z0])])
    return Solid(planes, col, col, **kw)


def vault(x0, y0, x1, y1, z0, rise, col, n=12, **kw):
    """A barrel vault running north-south (a quonset hut): half-ellipse across x."""
    cx, a = (x0 + x1) / 2, (x1 - x0) / 2
    planes = [[0, 1, 0, y1], [0, -1, 0, -y0], [0, 0, -1, -z0]]
    for i in range(n):
        th = math.pi * (i + 0.5) / n
        p0 = np.array([a * math.cos(th), 0, rise * math.sin(th)])
        nrm = np.array([p0[0] / (a * a), 0, p0[2] / (rise * rise)])
        nrm /= np.linalg.norm(nrm)
        planes.append([*nrm, nrm @ p0 + nrm @ np.array([cx, 0, z0])])
    return Solid(planes, col, col, **kw)


# ------------------------------------------------------------------------------------------------ render
def _q(k, step=0.08):
    return round(k / step) * step


def _shade(c, k):
    if k < 0:
        return tuple(max(0, int(v * (1 + k))) for v in c)
    return tuple(min(255, int(v + (255 - v) * k)) for v in c)


def _shade_arr(c, k):
    k = k[:, None]
    return np.where(k < 0, c * (1 + k), c + (255 - c) * k)


def render(scene, W, H, margin=6):
    """Ray-cast the scene into a sprite W x H px (plus `margin` px on the right for the cast shadow).
    Returns an RGBA image: lit colours where a solid is hit, translucent black for shadow on open ground."""
    from PIL import Image
    Wm = W + margin
    rr, cc = np.mgrid[0:H, 0:Wm]
    s = (H - rr - 0.5).ravel()
    x = (cc + 0.5).ravel()
    Z = 600.0
    o = np.column_stack([x, s - Z, np.full_like(x, Z)])
    t, si, n = scene.cast(o, RAY)
    hit = np.isfinite(t) & (x < W)
    p = o + np.where(np.isfinite(t), t, 0)[:, None] * RAY
    # the ground hides whatever is buried, unless the solid is allowed below ground
    belowok = np.array([sol.below for sol in scene.solids] + [False])[si]
    buried = hit & (p[:, 2] < -0.01) & ~belowok
    hit &= ~buried
    t = np.where(buried, np.inf, t)
    si = np.where(buried, -1, si)
    n = np.where(buried[:, None], np.array([0.0, 0.0, 1.0]), n)
    # open ground where nothing was hit: the z = 0 plane
    ground = ~hit
    p[ground] = np.column_stack([x[ground], s[ground], np.zeros(ground.sum())])
    # cast shadows toward the light
    lit_t, _, _ = scene.cast(p + n * 0.05 + LIGHT * 0.05, LIGHT, tmin=1e-3)
    shadow = np.isfinite(lit_t)
    ndl = n @ LIGHT
    out = np.zeros((H * Wm, 4), np.float64)
    solids = scene.solids
    tops = np.array([sol.top for sol in solids] + [(0, 0, 0)], float)
    sides = np.array([sol.side for sol in solids] + [(0, 0, 0)], float)
    outl = np.array([sol.outline for sol in solids] + [False])[si]
    base = np.where((n[:, 2] > 0.6)[:, None], tops[si], sides[si])
    k = np.round((ndl - 0.3) * 0.55 / 0.08) * 0.08 - np.where(shadow, 0.16, 0)
    out[:, :3] = _shade_arr(base, k)
    hidet = np.array([sol.hide_top for sol in solids] + [False])[si] & (n[:, 2] > 0.6)
    hit = hit & ~hidet
    outl = outl & ~hidet
    out[:, 3] = np.where(hit, 255, 0)
    gs = (ground | hidet) & shadow
    out[gs] = (0, 0, 0, 60)
    img = out.reshape(H, Wm, 4)
    # outlines: the silhouette, and the far side of depth jumps
    sil = (hit & outl).reshape(H, Wm)
    tt = np.where(hit, t, np.inf).reshape(H, Wm)
    pad = np.pad(sil, 1)
    nb_all = pad[2:, 1:-1] & pad[:-2, 1:-1] & pad[1:-1, 2:] & pad[1:-1, :-2]
    edge = sil & ~nb_all
    tp = np.pad(tt, 1, constant_values=np.inf)
    jump = np.zeros_like(sil)
    for nt in (tp[2:, 1:-1], tp[:-2, 1:-1], tp[1:-1, 2:], tp[1:-1, :-2]):
        with np.errstate(invalid="ignore"):
            jump |= sil & np.isfinite(nt) & (tt - nt > 2.5)
    for m, kk in ((jump & ~edge, -0.28), (edge, -0.5)):
        img[m, :3] = _shade_arr(img[m, :3], np.full(m.sum(), kk))
    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img, "RGBA")

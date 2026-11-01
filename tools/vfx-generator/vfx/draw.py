"""Pixel-art primitives in the style of Emerald's effects (see ../STYLE.md).

Every shape is rendered as (coverage, value) on a 4x supersampled grid, then snapped to whole pixels:
a pixel is painted when at least half of it is covered, so edges are crisp, never blurred. The value
(0..1, 1 = hottest) picks a step on a ramp through hard `bands`, never a gradient, so a glow reads as
the vanilla "white core, pale ring, saturated rim" instead of a smooth airbrush.

The Canvas holds palette indices. Ops are plain functions so a spec (YAML) or a Python batch can call
them; `ops.py` maps spec keys onto them.
"""
from __future__ import annotations

import math
import random

import numpy as np

from .pal import Palette

SS = 4  # supersampling factor


def _grid(w: int, h: int):
    ys, xs = np.mgrid[0:h * SS, 0:w * SS]
    return (xs + 0.5) / SS, (ys + 0.5) / SS


def _down(a: np.ndarray, w: int, h: int) -> np.ndarray:
    return a.reshape(h, SS, w, SS).mean(axis=(1, 3))


def resolve(cov_ss: np.ndarray, val_ss: np.ndarray, w: int, h: int, threshold: float = 0.5):
    cov = _down(cov_ss.astype(float), w, h)
    num = _down(val_ss * cov_ss, w, h)
    val = np.where(cov > 0, num / np.maximum(cov, 1e-9), 0.0)
    return cov >= threshold, val


DEFAULT_BANDS = {1: [], 2: [0.5], 3: [0.66, 0.33], 4: [0.75, 0.5, 0.25], 5: [0.8, 0.6, 0.4, 0.2]}


def bands_for(n: int, bands=None) -> list[float]:
    if bands is not None:
        return list(bands)
    if n in DEFAULT_BANDS:
        return DEFAULT_BANDS[n]
    return [1 - (k + 1) / n for k in range(n - 1)]


def quantise(val: np.ndarray, n: int, bands=None) -> np.ndarray:
    """value (1 hot .. 0 cold) -> ramp step (0 = lightest)."""
    b = bands_for(n, bands)
    step = np.zeros(val.shape, dtype=int)
    for th in b:
        step += (val < th).astype(int)
    return np.clip(step, 0, n - 1)


class Canvas:
    def __init__(self, w: int, h: int, pal: Palette):
        self.w, self.h, self.pal = w, h, pal
        self.pix = np.zeros((h, w), dtype=np.uint8)

    def copy(self) -> "Canvas":
        c = Canvas(self.w, self.h, self.pal)
        c.pix = self.pix.copy()
        return c

    # -- compositing ------------------------------------------------------------------------
    def paint(self, mask: np.ndarray, val: np.ndarray | float, ramp, *, mode: str = "over", bands=None,
              offset: int = 0, dither: float = 0.0, seed: int = 0):
        """Write ramp steps where `mask`. mode: over (replace), under (only empty pixels),
        lighten (only where the new colour is brighter), darken, erase."""
        idx = self.pal.ramp(ramp)
        if mode == "erase":
            self.pix[mask] = 0
            return
        if np.isscalar(val):
            val = np.full(mask.shape, float(val))
        if dither:
            # ordered (Bayer 2x2) nudge across band edges: the checker Emerald uses on big glows
            bay = np.array([[0.0, 0.5], [0.75, 0.25]])
            tile = np.tile(bay, (self.h // 2 + 1, self.w // 2 + 1))[: self.h, : self.w]
            val = val + (tile - 0.375) * dither
        step = np.clip(quantise(val, len(idx), bands) + offset, 0, len(idx) - 1)
        new = np.array(idx)[step]
        if mode == "under":
            mask = mask & (self.pix == 0)
        elif mode in ("lighten", "darken"):
            lum = np.array([self.pal.luma_of(i) for i in range(len(self.pal.colours))])
            cur = np.where(self.pix == 0, -1 if mode == "lighten" else 1e9, lum[self.pix])
            better = lum[new] > cur if mode == "lighten" else lum[new] < cur
            mask = mask & better
        self.pix[mask] = new[mask]

    def fill(self, mask: np.ndarray, index: int):
        self.pix[mask] = index

    @property
    def opaque(self) -> np.ndarray:
        return self.pix > 0


# -- shapes: each returns (mask, value) at 1x ------------------------------------------------


def disc(w, h, cx, cy, r, *, light=(0.0, 0.0), hot=1.0, cold=0.0, falloff=1.0):
    """Filled circle. value 1 at the centre (or at the light point) falling to 0 at the rim."""
    X, Y = _grid(w, h)
    d = np.hypot(X - cx, Y - cy)
    inside = d <= r
    lx, ly = cx + light[0] * r, cy + light[1] * r
    dl = np.hypot(X - lx, Y - ly) / max(r * (1 + math.hypot(*light)), 1e-6)
    v = hot - (hot - cold) * np.clip(dl, 0, 1) ** falloff
    return resolve(inside, v, w, h)


def ellipse(w, h, cx, cy, rx, ry, *, angle=0.0, light=(0.0, 0.0), falloff=1.0):
    X, Y = _grid(w, h)
    a = math.radians(angle)
    dx, dy = X - cx, Y - cy
    u = (dx * math.cos(a) + dy * math.sin(a)) / max(rx, 1e-6)
    v = (-dx * math.sin(a) + dy * math.cos(a)) / max(ry, 1e-6)
    d = np.hypot(u - light[0], v - light[1]) / (1 + math.hypot(*light))
    inside = np.hypot(u, v) <= 1
    return resolve(inside, 1 - np.clip(d, 0, 1) ** falloff, w, h)


def ring(w, h, cx, cy, r, thick, *, bright="center"):
    X, Y = _grid(w, h)
    d = np.hypot(X - cx, Y - cy)
    inside = np.abs(d - r) <= thick / 2
    t = (d - (r - thick / 2)) / max(thick, 1e-6)        # 0 inner edge .. 1 outer edge
    v = {"center": 1 - np.abs(t - 0.5) * 2, "inner": 1 - t, "outer": t}[bright]
    return resolve(inside, np.clip(v, 0, 1), w, h)


def _seg_dist(X, Y, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1) if L2 > 0 else np.zeros_like(X)
    return np.hypot(X - (x0 + t * dx), Y - (y0 + t * dy)), t


def capsule(w, h, x0, y0, x1, y1, r0, r1=None, *, falloff=1.0):
    """A beam / bolt segment, radius r0 at the start tapering to r1. Value 1 on the spine."""
    r1 = r0 if r1 is None else r1
    X, Y = _grid(w, h)
    d, t = _seg_dist(X, Y, x0, y0, x1, y1)
    r = r0 + (r1 - r0) * t
    inside = d <= r
    v = 1 - np.clip(d / np.maximum(r, 1e-6), 0, 1) ** falloff
    return resolve(inside, v, w, h)


def polyline(w, h, pts, r0, r1=None, *, falloff=1.0):
    """Union of capsules along a path (lightning, trails). Radius tapers r0 -> r1 along the path."""
    r1 = r0 if r1 is None else r1
    X, Y = _grid(w, h)
    best_d = np.full(X.shape, 1e9)
    best_r = np.full(X.shape, 1.0)
    lens = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    total = sum(lens) or 1.0
    acc = 0.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        d, t = _seg_dist(X, Y, x0, y0, x1, y1)
        frac = (acc + t * lens[i]) / total
        r = r0 + (r1 - r0) * frac
        closer = d / np.maximum(r, 1e-6) < best_d / np.maximum(best_r, 1e-6)
        best_d = np.where(closer, d, best_d)
        best_r = np.where(closer, r, best_r)
        acc += lens[i]
    inside = best_d <= best_r
    v = 1 - np.clip(best_d / np.maximum(best_r, 1e-6), 0, 1) ** falloff
    return resolve(inside, v, w, h)


def polygon(w, h, pts, *, light=(0.0, 0.0)):
    """Filled polygon (even-odd). Value: 1 deep inside, 0 at the edge (an inset glow)."""
    X, Y = _grid(w, h)
    inside = np.zeros(X.shape, bool)
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        cond = ((y0 > Y) != (y1 > Y)) & (X < (x1 - x0) * (Y - y0) / ((y1 - y0) or 1e-9) + x0)
        inside ^= cond
    d = np.full(X.shape, 1e9)
    for i in range(n):
        dd, _ = _seg_dist(X, Y, *pts[i], *pts[(i + 1) % n])
        d = np.minimum(d, dd)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    rad = max(math.hypot(p[0] - cx, p[1] - cy) for p in pts)
    v = np.clip(d / max(rad * 0.6, 1e-6), 0, 1)
    if light != (0.0, 0.0):
        v = np.clip(v * 0.7 + 0.3 * (1 - np.hypot(X - (cx + light[0] * rad), Y - (cy + light[1] * rad)) / (2 * rad)), 0, 1)
    return resolve(inside, v, w, h)


def star(w, h, cx, cy, r_in, r_out, points=8, rot=0.0, jitter=0.0, seed=0):
    """Impact starburst (Emerald's hit sparks): alternating outer/inner vertices."""
    rng = random.Random(seed)
    pts = []
    for k in range(points * 2):
        a = math.radians(rot) + math.pi * k / points
        r = r_out if k % 2 == 0 else r_in
        r *= 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    X, Y = _grid(w, h)
    m, _ = polygon(w, h, pts)
    d = np.hypot(X - cx, Y - cy)
    v = 1 - np.clip(d / r_out, 0, 1)
    _, val = resolve(np.ones_like(X, bool), v, w, h)
    return m, val


def crescent(w, h, cx, cy, r, thick, a0, a1, *, taper=True, bright="outer"):
    """A slash arc from angle a0 to a1 (degrees, 0 = right, clockwise on screen), thickest mid-way."""
    X, Y = _grid(w, h)
    ang = np.degrees(np.arctan2(Y - cy, X - cx))
    lo, hi = min(a0, a1), max(a0, a1)
    ang = np.where(ang < lo - 180, ang + 360, ang)
    ang = np.where(ang > hi + 180, ang - 360, ang)
    t = np.clip((ang - lo) / max(hi - lo, 1e-6), 0, 1)
    within = (ang >= lo) & (ang <= hi)
    th = thick * (np.sin(math.pi * t) if taper else 1.0)
    d = np.hypot(X - cx, Y - cy)
    inside = within & (d <= r) & (d >= r - th)
    u = (d - (r - th)) / np.maximum(th, 1e-6)
    v = {"outer": u, "inner": 1 - u, "center": 1 - np.abs(u - 0.5) * 2}[bright]
    return resolve(inside, np.clip(v, 0, 1), w, h)


def rect(w, h, x, y, rw, rh):
    m = np.zeros((h, w), bool)
    m[max(0, int(y)):max(0, int(y + rh)), max(0, int(x)):max(0, int(x + rw))] = True
    return m, np.ones((h, w))


# -- paths -----------------------------------------------------------------------------------


def zigzag(x0, y0, x1, y1, segments=6, amp=3.0, seed=0, smooth=0.0):
    """Lightning path: points from (x0,y0) to (x1,y1) displaced sideways, ends pinned."""
    rng = random.Random(seed)
    L = math.hypot(x1 - x0, y1 - y0) or 1.0
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    pts = [(x0, y0)]
    prev = 0.0
    for k in range(1, segments):
        t = k / segments
        off = rng.uniform(-amp, amp)
        off = prev * smooth + off * (1 - smooth)
        prev = off
        pts.append((x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off))
    pts.append((x1, y1))
    return pts


def branches(pts, count=2, length=4.0, seed=0, spread=50.0):
    """Short forks off a lightning path."""
    rng = random.Random(seed + 7)
    out = []
    for _ in range(count):
        i = rng.randrange(1, max(2, len(pts) - 1))
        x, y = pts[i]
        px, py = pts[i - 1]
        a = math.atan2(y - py, x - px) + math.radians(rng.choice([-1, 1]) * rng.uniform(spread * 0.5, spread))
        L = length * rng.uniform(0.6, 1.2)
        out.append(zigzag(x, y, x + L * math.cos(a), y + L * math.sin(a), segments=2, amp=1.0, seed=rng.randrange(999)))
    return out


# -- pixel-level helpers ---------------------------------------------------------------------


def neighbours(mask: np.ndarray, diag: bool = False) -> list[np.ndarray]:
    shifts = [(0, 1), (0, -1), (1, 0), (-1, 0)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else [])
    out = []
    for dy, dx in shifts:
        s = np.zeros_like(mask)
        hs, ws = mask.shape
        ys = slice(max(dy, 0), hs + min(dy, 0))
        yd = slice(max(-dy, 0), hs + min(-dy, 0))
        xs = slice(max(dx, 0), ws + min(dx, 0))
        xd = slice(max(-dx, 0), ws + min(-dx, 0))
        s[ys, xs] = mask[yd, xd]
        out.append(s)
    return out


def dilate(mask: np.ndarray, diag=False) -> np.ndarray:
    out = mask.copy()
    for s in neighbours(mask, diag):
        out |= s
    return out


def erode(mask: np.ndarray, diag=False) -> np.ndarray:
    out = mask.copy()
    for s in neighbours(mask, diag):
        out &= s
    return out


def edge(mask: np.ndarray, diag=False) -> np.ndarray:
    """Pixels of `mask` touching the outside."""
    return mask & ~erode(mask, diag)


def outline(canvas: Canvas, index: int, *, inner: bool = False, diag: bool = False, of: np.ndarray | None = None):
    """Outer outline (around the opaque area) or inner (recolour the edge pixels)."""
    m = canvas.opaque if of is None else of
    if inner:
        canvas.pix[edge(m, diag)] = index
    else:
        ring_ = dilate(m, diag) & ~m
        canvas.pix[ring_ & (canvas.pix == 0)] = index


def selout(canvas: Canvas, *, ramp_of: dict[int, list[int]] | None = None, diag=False, light=None):
    """Selective outline: each edge pixel takes a dark step of its own ramp (Emerald objects are rimmed
    in their own colour, never pure black). With `light` (e.g. [-1, -1]) the edges facing the light take
    the second-darkest step and the rest the darkest, as on the vanilla coin and Poke Ball."""
    pal = canvas.pal
    dark, mid = {}, {}
    for r in pal.ramps.values():
        for i in r:
            dark.setdefault(i, r[-1])
            mid.setdefault(i, r[-2] if len(r) > 1 else r[-1])
    if ramp_of:
        dark.update({k: v[-1] for k, v in ramp_of.items()})
    o = canvas.opaque
    e = edge(o, diag)
    lit = np.zeros_like(e)
    if light:
        lx, ly = int(np.sign(light[0])), int(np.sign(light[1]))
        lit = e & ~shift(o.astype(np.uint8), -lx, 0).astype(bool) | e & ~shift(o.astype(np.uint8), 0, -ly).astype(bool)
        lit &= e
    ys, xs = np.nonzero(e)
    for y, x in zip(ys, xs):
        v = int(canvas.pix[y, x])
        canvas.pix[y, x] = (mid if lit[y, x] else dark).get(v, v)


def shade_mask(mask: np.ndarray, *, light=(-1, -1), rim: int = 1, depth: int = 3) -> np.ndarray:
    """Volume shading of a flat region the way Emerald shades objects: lit edge toward the light,
    shadow edge away from it, a body tone in between. Returns value 0..1 (1 = lit)."""
    h, w = mask.shape
    lx, ly = light
    lx, ly = int(np.sign(lx)), int(np.sign(ly))
    val = np.full((h, w), 0.55)
    # distance from the edge, in pixels (cheap iterative erosion)
    dist = np.zeros((h, w), int)
    cur = mask.copy()
    k = 0
    while cur.any() and k < 32:
        dist[cur] += 1
        cur = erode(cur)
        k += 1
    def shifted(dx, dy):
        s = np.zeros_like(mask)
        ys = slice(max(dy, 0), h + min(dy, 0))
        yd = slice(max(-dy, 0), h + min(-dy, 0))
        xs = slice(max(dx, 0), w + min(dx, 0))
        xd = slice(max(-dx, 0), w + min(-dx, 0))
        s[ys, xs] = mask[yd, xd]
        return s
    toward = ~shifted(-lx, -ly) & mask     # neighbour toward the light is empty -> lit rim
    away = ~shifted(lx, ly) & mask         # neighbour away from the light is empty -> shadow rim
    away2 = ~shifted(2 * lx, 2 * ly) & mask
    val = np.where(dist >= depth, 0.62, val)
    val = np.where(away2, 0.32, val)
    val = np.where(away, 0.12, val)
    val = np.where(toward & ~away, 0.9, val)
    return np.where(mask, val, 0.0)


def shift(pix: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(pix)
    h, w = pix.shape
    ys = slice(max(dy, 0), h + min(dy, 0))
    yd = slice(max(-dy, 0), h + min(-dy, 0))
    xs = slice(max(dx, 0), w + min(dx, 0))
    xd = slice(max(-dx, 0), w + min(-dx, 0))
    out[ys, xs] = pix[yd, xd]
    return out


def rotate_nn(pix: np.ndarray, deg: float, cx: float | None = None, cy: float | None = None) -> np.ndarray:
    """Nearest-neighbour rotation (what the GBA affine unit does): no new colours, no blur."""
    h, w = pix.shape
    cx = (w - 1) / 2 if cx is None else cx
    cy = (h - 1) / 2 if cy is None else cy
    a = math.radians(-deg)
    ys, xs = np.mgrid[0:h, 0:w]
    sx = np.cos(a) * (xs - cx) - np.sin(a) * (ys - cy) + cx
    sy = np.sin(a) * (xs - cx) + np.cos(a) * (ys - cy) + cy
    sxi, syi = np.round(sx).astype(int), np.round(sy).astype(int)
    ok = (sxi >= 0) & (sxi < w) & (syi >= 0) & (syi < h)
    out = np.zeros_like(pix)
    out[ok] = pix[syi[ok], sxi[ok]]
    return out


def scale_nn(pix: np.ndarray, f: float, cx=None, cy=None, fy: float | None = None) -> np.ndarray:
    """Nearest-neighbour scale about (cx, cy); fy scales y separately (a coin turning edge-on)."""
    h, w = pix.shape
    fy = f if fy is None else fy
    cx = (w - 1) / 2 if cx is None else cx
    cy = (h - 1) / 2 if cy is None else cy
    ys, xs = np.mgrid[0:h, 0:w]
    sx = np.round((xs - cx) / f + cx).astype(int)
    sy = np.round((ys - cy) / fy + cy).astype(int)
    ok = (sx >= 0) & (sx < w) & (sy >= 0) & (sy < h)
    out = np.zeros_like(pix)
    out[ok] = pix[sy[ok], sx[ok]]
    return out


def despeckle(canvas: Canvas, min_neighbours: int = 1, keep: set[int] | None = None):
    """Drop lone pixels (no opaque 8-neighbour): vanilla effects almost never have them except sparks."""
    m = canvas.opaque
    cnt = sum(n.astype(int) for n in neighbours(m, diag=True))
    lone = m & (cnt < min_neighbours)
    if keep:
        lone &= ~np.isin(canvas.pix, list(keep))
    canvas.pix[lone] = 0

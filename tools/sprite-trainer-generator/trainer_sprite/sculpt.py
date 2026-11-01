"""Sculpt: draw a whole figure organically, as soft volumes, then shade it as one figure (D14).

The repaint (D8) keeps a vanilla pic's pose, clothes and hair, so every character still reads as
the trainer it was painted over. `sculpt:` draws the figure from the ground up instead, the way a
sprite artist blocks one in: a gesture skeleton, then soft volumes (limbs that taper and melt into
the torso, a coat that flares, hair in locks), then light. The engine does the parts that make
hand-made rig drawings look like patchwork:

- volumes in one *group* melt together (smooth union), so a shoulder flows into an arm and a
  hand into a wrist without seams;
- every pixel gets a surface normal from the volume it belongs to, so the whole figure is lit
  from one light (upper left, as in every Emerald pic) and shading falls into clean 3-4 tone
  clusters per material, with no hand-placed shading;
- a group in front casts a short shadow on what is behind it (under the chin, under an arm);
- outlines: black around the silhouette, and a line where a group passes in front of another
  (black, the group's own darkest tone, or none);
- then the finisher (finish.py) removes stray pixels and L-shaped outline doubles.

Faces, eyes, emblems and the sheen pixels stay hand-placed with `patches:`.

    front:
      sculpt:
        light: [-0.55, -0.7, 0.55]      # x, y (down is +), z (toward the viewer)
        materials:                      # name: ramp of legend chars, dark -> light (2-4)
          skin: dcba
          coat: hgfe
        joints: {head: [30, 12], neck: [31, 19], ...}
        groups:                         # back to front
          - name: far arm
            mat: coat
            line: K                     # where it overlaps a group behind: K / dark / none
            blend: 1.5                  # smooth-union radius between its shapes (px)
            round: 3                    # how far in from the edge the volume is fully round
            shapes:
              - {limb: [sh_far, el_far, wr_far], r: [3, 2.6, 2.2]}   # tapered chain
              - {ellipse: [30, 12], r: [7, 8], angle: -10}
              - {blob: [[x, y, r], ...]}                             # soft lump
              - {poly: [[x, y], ...], soft: 1}                       # flat panel, rounded corners
              - {curve: [p0, ctrl, p1], r: [2, 0.5]}                 # bent, tapering lock/fold
              - {cut: {...any shape...}}                             # carve out of the group
            paint:                       # sub-regions of the group in another material
              - {mat: skin, shape: {ellipse: [..], r: [..]}}
            creases:                     # fold lines, drawn in the group's dark tone
              - {pts: [[x, y], ...], tone: 0}
"""
from __future__ import annotations

import math

import numpy as np


class SculptError(ValueError):
    pass


def _pt(p, joints, where):
    if isinstance(p, str):
        if p not in joints:
            raise SculptError(f"{where}: unknown joint {p!r}")
        return joints[p]
    return [float(p[0]), float(p[1])]


def _smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def _seg(X, Y, a, b, ra, rb):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0, 1)
    px, py = ax + t * dx, ay + t * dy
    return np.hypot(X - px, Y - py) - (ra + t * (rb - ra))


def _poly_sdf(X, Y, pts):
    n = len(pts)
    d = np.full(X.shape, 1e9)
    inside = np.zeros(X.shape, bool)
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        d = np.minimum(d, _seg(X, Y, (ax, ay), (bx, by), 0, 0))
        cond = ((ay > Y) != (by > Y)) & (X < (bx - ax) * (Y - ay) / ((by - ay) or 1e-9) + ax)
        inside ^= cond
    return np.where(inside, -d, d)


def shape_sdf(s: dict, joints, where):
    """A function (X, Y) -> signed distance (negative inside) for one shape."""
    if "limb" in s:
        pts = [_pt(p, joints, where) for p in s["limb"]]
        r = s.get("r", 2)
        rs = [float(v) for v in r] if isinstance(r, list) else [float(r)] * len(pts)
        if len(rs) != len(pts):
            raise SculptError(f"{where}: limb needs one radius per point")
        def f(X, Y):
            d = np.full(X.shape, 1e9)
            for i in range(len(pts) - 1):
                d = np.minimum(d, _seg(X, Y, pts[i], pts[i + 1], rs[i], rs[i + 1]))
            return d
        return f
    if "ellipse" in s:
        cx, cy = _pt(s["ellipse"], joints, where)
        rx, ry = (float(v) for v in s["r"])
        th = math.radians(float(s.get("angle", 0)))
        c, sn = math.cos(th), math.sin(th)
        def f(X, Y):
            u = (X - cx) * c + (Y - cy) * sn
            v = -(X - cx) * sn + (Y - cy) * c
            k = np.hypot(u / rx, v / ry)
            return (k - 1) * min(rx, ry)
        return f
    if "blob" in s:
        cs = [(float(a), float(b), float(r)) for a, b, r in s["blob"]]
        k = float(s.get("k", 2.0))
        def f(X, Y):
            d = None
            for x, y, r in cs:
                e = np.hypot(X - x, Y - y) - r
                d = e if d is None else _smin(d, e, k)
            return d
        return f
    if "poly" in s:
        pts = [_pt(p, joints, where) for p in s["poly"]]
        soft = float(s.get("soft", 0))
        return lambda X, Y: _poly_sdf(X, Y, pts) - soft
    if "curve" in s:
        p0, c, p1 = (_pt(p, joints, where) for p in s["curve"])
        r = s.get("r", 1)
        r0, r1 = (float(v) for v in r) if isinstance(r, list) else (float(r), float(r))
        n = 10
        bez = []
        for i in range(n + 1):
            t = i / n
            bez.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1], r0 + (r1 - r0) * t))
        def f(X, Y):
            d = np.full(X.shape, 1e9)
            for i in range(n):
                d = np.minimum(d, _seg(X, Y, bez[i][:2], bez[i + 1][:2], bez[i][2], bez[i + 1][2]))
            return d
        return f
    raise SculptError(f"{where}: unknown shape {sorted(s)}")


def _group_sdf(gr, joints, where):
    blend = float(gr.get("blend", 1.5))
    adds, cuts = [], []
    for i, s in enumerate(gr.get("shapes") or []):
        w = f"{where} shape {i}"
        if "cut" in s:
            cuts.append(shape_sdf(s["cut"], joints, w))
        else:
            adds.append((shape_sdf(s, joints, w), float(s.get("blend", blend))))
    if not adds:
        raise SculptError(f"{where}: a group needs at least one shape")
    def f(X, Y):
        d = None
        for fn, k in adds:
            e = fn(X, Y)
            d = e if d is None else _smin(d, e, k)
        for fn in cuts:
            d = np.maximum(d, -fn(X, Y))
        return d
    return f


def _height(d, R):
    t = np.clip(-d, 0, R)
    return np.sqrt(np.maximum(0, 2 * R * t - t * t))


TONES = {2: [0.30], 3: [0.18, 0.62], 4: [0.02, 0.30, 0.80]}


def render(sc: dict, legend: dict[str, int], w: int, h: int, where: str):
    joints = {k: [float(v[0]), float(v[1])] for k, v in (sc.get("joints") or {}).items()}
    mats = {}
    for name, ramp in (sc.get("materials") or {}).items():
        ramp = str(ramp)
        if not 2 <= len(ramp) <= 4 or any(c not in legend for c in ramp):
            raise SculptError(f"{where}: material {name}: ramp must be 2-4 legend characters")
        mats[name] = [legend[c] for c in ramp]
    K = legend.get(str(sc.get("outline", "K")))
    L = np.array(sc.get("light", [-0.55, -0.7, 0.55]), float)
    L /= np.linalg.norm(L)
    tones = sc.get("tones") or {}

    Y, X = np.mgrid[0:h, 0:w].astype(float)
    gid = np.full((h, w), -1)
    mat = np.full((h, w), "", dtype=object)
    shade = np.zeros((h, w))
    info = []
    e = 0.5
    for gi, gr in enumerate(sc.get("groups") or []):
        gw = f"{where}: group {gr.get('name', gi)}"
        if gr.get("mat") not in mats:
            raise SculptError(f"{gw}: mat {gr.get('mat')!r} is not in materials")
        f = _group_sdf(gr, joints, gw)
        R = float(gr.get("round", 3))
        d = f(X, Y)
        inside = d <= 0
        hx = (_height(f(X + e, Y), R) - _height(f(X - e, Y), R)) / (2 * e)
        hy = (_height(f(X, Y + e), R) - _height(f(X, Y - e), R)) / (2 * e)
        flat = float(gr.get("flat", 1.0))  # <1 flattens the bulge (cloth), >1 exaggerates
        nx, ny, nz = -hx * flat, -hy * flat, np.ones_like(hx)
        nn = np.sqrt(nx * nx + ny * ny + nz * nz)
        s = (nx * L[0] + ny * L[1] + nz * L[2]) / nn
        s = s + float(gr.get("bright", 0))
        m = np.full((h, w), gr["mat"], dtype=object)
        for j, p in enumerate(gr.get("paint") or []):
            if p.get("mat") not in mats:
                raise SculptError(f"{gw}: paint {j}: mat {p.get('mat')!r} is not in materials")
            pf = shape_sdf(p["shape"], joints, f"{gw} paint {j}")
            m = np.where(pf(X, Y) <= 0, p["mat"], m)
        behind = bool(gr.get("behind"))
        put = inside & (gid < 0) if behind else inside
        gid = np.where(put, gi, gid)
        mat = np.where(put, m, mat)
        shade = np.where(put, s, shade)
        info.append(gr)

    g = [[0] * w for _ in range(h)]
    tone = np.zeros((h, w), int)
    for y in range(h):
        for x in range(w):
            if gid[y, x] < 0:
                continue
            ramp = mats[mat[y, x]]
            th = tones.get(len(ramp)) or TONES[len(ramp)]
            t = sum(1 for v in th if shade[y, x] >= v)
            # cast shadow: a group in front, up and to the light side, darkens this pixel
            for dx, dy in ((-1, -1), (-1, 0), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and gid[yy, xx] > gid[y, x] and not info[gid[yy, xx]].get("behind") \
                        and info[gid[y, x]].get("cast", True):
                    t = max(0, t - 1)
                    break
            tone[y, x] = t
            g[y][x] = ramp[t]
    # lines where a group passes in front of another, on the front group's own edge
    for y in range(h):
        for x in range(w):
            gi = gid[y, x]
            if gi < 0:
                continue
            line = str(info[gi].get("line", "K"))
            if line == "none":
                continue
            for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and 0 <= gid[yy, xx] < gi and not info[gi].get("behind"):
                    g[y][x] = K if line == "K" else mats[mat[y, x]][0]
                    break
    # creases and paint seams
    for gi, gr in enumerate(info):
        for c in gr.get("creases") or []:
            pts = [_pt(p, joints, where) for p in c["pts"]]
            mname = c.get("mat", gr["mat"])
            col = mats[mname][int(c.get("tone", 0))] if "char" not in c else legend[c["char"]]
            for i in range(len(pts) - 1):
                (x0, y0), (x1, y1) = pts[i], pts[i + 1]
                n = int(max(abs(x1 - x0), abs(y1 - y0))) or 1
                for k in range(n + 1):
                    x = int(round(x0 + (x1 - x0) * k / n))
                    y = int(round(y0 + (y1 - y0) * k / n))
                    if 0 <= x < w and 0 <= y < h and gid[y, x] == gi:
                        g[y][x] = col
    # the silhouette outline
    for y in range(h):
        for x in range(w):
            if gid[y, x] < 0:
                continue
            for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                xx, yy = x + dx, y + dy
                if not (0 <= xx < w and 0 <= yy < h):
                    if yy < h:
                        g[y][x] = K
                    break
                if gid[yy, xx] < 0:
                    g[y][x] = K
                    break
    return g

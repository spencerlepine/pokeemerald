"""Object-kit generators: entries in a blueprint's `parts` that become several low-poly world-art parts,
seeded. World-art has its own (`lobes`, `branches`, `tiers`, `scatter`, `ring`, `limb`); these are the
ones nature and small structures need on top. Every one takes `mat` and `name`.

    rock:    {c: [x, y, z], r: [rx, ry, rz], rings: [[zf, rf], ...], n: 7, jitter: 0.12, round: 0.03,
              lean: [dx, dy]}
             one convex hull of jittered points in rings up an ellipsoid: a boulder, a hoodoo (`rings`
             sets the profile: z and radius as fractions of rz and r), a crystal, a skull.
    spike:   {c: [x, y, z], r: 0.2, h: 1.0, sides: 5, lean: [dx, dy], top: 0.0, round: 0.02}
             a faceted spike: a `sides`-gon base and an apex (`top` > 0 = a cut-off top of that radius).
    columns: {c: [x, y], w, d, r: 0.2, h: [lo, hi], sides: 6, round: 0.02, peak: [x, y] | none}
             hexagonal prisms packed to fill w x d (centre c): basalt columns, a crystal bed, stacked
             crates. Heights are random in [lo, hi], tallest near `peak` when given.
    roots:   {c: [x, y, z], n: 5, reach: [lo, hi], r: 0.1, arc: [a0, a1], kind: arch | wedge, z0: 0, sag: 0.1, bend_at: 0.5}
             n roots from a point `c` on a trunk out to the ground (arc in degrees, 270 = due south): `arch` =
             two cones, out to a bend `sag` m above c, then down (a mangrove), `wedge` = a thin buttress fin that widens to the ground (a wroshyr).
"""
import math

import numpy as np


def _rng_of(rng):
    """random.Random (a blueprint) or a numpy Generator (world-art, inside a template) -> numpy Generator."""
    if hasattr(rng, "randrange"):
        return np.random.default_rng(rng.randrange(1 << 30))
    return rng


def _f(v, rng):
    if isinstance(v, (list, tuple)):
        return float(rng.uniform(float(v[0]), float(v[1])))
    return float(v)


def gen_rock(g, rng):
    R = _rng_of(rng)
    c = np.asarray(g.get("c", [0, 0, 0]), float)
    r = np.asarray(g.get("r", [0.5, 0.4, 0.6]), float)
    rings = g.get("rings") or [[0.0, 0.72], [0.14, 0.95], [0.45, 1.0], [0.76, 0.82], [1.0, 0.38]]
    n = int(g.get("n", 7))
    jit = float(g.get("jitter", 0.12))
    lean = np.asarray(g.get("lean", [0, 0]), float)
    pts = []
    for zf, rf in rings:
        rf = rf if isinstance(rf, (list, tuple)) else [rf, rf]
        base = R.uniform(0, math.tau)
        for i in range(n):
            a = base + math.tau * i / n + R.uniform(-0.5, 0.5) * math.tau / n * 0.8
            k = 1 + R.uniform(-jit, jit)
            x = c[0] + math.cos(a) * r[0] * rf[0] * k + lean[0] * zf
            y = c[1] + math.sin(a) * r[1] * rf[1] * k + lean[1] * zf
            z = c[2] + r[2] * (zf + (R.uniform(-jit, jit) * 0.35 if 0 < zf < 1 else 0))
            pts.append([round(x, 3), round(y, 3), round(max(z, 0.0), 3)])
    return [{"name": g.get("name", "rock"), "mat": g["mat"], "group": g.get("group", "body"),
             "hull": {"points": pts, "round": float(g.get("round", 0.03))}}]


def gen_spike(g, rng):
    R = _rng_of(rng)
    c = np.asarray(g.get("c", [0, 0, 0]), float)
    r, h = float(g.get("r", 0.2)), float(g.get("h", 1.0))
    sides = int(g.get("sides", 5))
    lean = np.asarray(g.get("lean", [0, 0]), float)
    top = float(g.get("top", 0.0))
    base = R.uniform(0, math.tau)
    pts = []
    for i in range(sides):
        a = base + math.tau * i / sides
        pts.append([round(c[0] + math.cos(a) * r, 3), round(c[1] + math.sin(a) * r * float(g.get("ry", 1.0)), 3), round(c[2], 3)])
    if top > 0:
        for i in range(sides):
            a = base + math.tau * i / sides
            pts.append([round(c[0] + lean[0] + math.cos(a) * top, 3), round(c[1] + lean[1] + math.sin(a) * top, 3), round(c[2] + h, 3)])
    else:
        pts.append([round(c[0] + lean[0], 3), round(c[1] + lean[1], 3), round(c[2] + h, 3)])
    return [{"name": g.get("name", "spike"), "mat": g["mat"], "group": g.get("group", "body"),
             "hull": {"points": pts, "round": float(g.get("round", 0.02))}}]


def gen_columns(g, rng):
    R = _rng_of(rng)
    cx, cy = (float(v) for v in g.get("c", [0, 0]))
    w, d = float(g["w"]), float(g["d"])
    r = float(g.get("r", 0.2))
    sides = int(g.get("sides", 6))
    lo, hi = (float(v) for v in g.get("h", [0.4, 1.2]))
    peak = g.get("peak")
    dx = r * 2 * 0.92
    dy = r * math.sqrt(3) * 0.92
    out = []
    ny = max(1, int(round(d / dy)) + 1)
    nx = max(1, int(round(w / dx)))
    for j in range(ny):
        y = cy - d / 2 + r + j * dy
        if y + r > cy + d / 2 + 0.02:
            continue
        off = (dx / 2) if j % 2 else 0.0
        for i in range(nx):
            x = cx - w / 2 + r + i * dx + off
            if x + r > cx + w / 2 + 0.02:
                continue
            if peak:
                dist = math.hypot(x - float(peak[0]), y - float(peak[1]))
                f = max(0.0, 1 - dist / max(w, d))
                h = lo + (hi - lo) * (0.35 * R.uniform(0, 1) + 0.65 * f)
            else:
                h = R.uniform(lo, hi)
            a0 = math.tau / (2 * sides)
            poly = [[round(x + math.cos(a0 + math.tau * k / sides) * r, 3), round(y + math.sin(a0 + math.tau * k / sides) * r, 3)]
                    for k in range(sides)]
            out.append({"name": f"{g.get('name', 'col')}/{len(out)}", "mat": g["mat"], "group": g.get("group", "body"),
                        "prism": {"poly": poly, "z": [0, round(h, 3)], "round": float(g.get("round", 0.02))}})
    return out


def gen_roots(g, rng):
    R = _rng_of(rng)
    c = np.asarray(g.get("c", [0, 0, 0.6]), float)
    n = int(g.get("n", 5))
    a0, a1 = (float(v) for v in g.get("arc", [200, 340]))      # degrees, 270 = due south
    kind = g.get("kind", "arch")
    rr = float(g.get("r", 0.1))
    z0 = float(g.get("z0", 0.0))
    out = []
    for i in range(n):
        t = (i + 0.5) / n
        a = math.radians(a0 + (a1 - a0) * t + R.uniform(-0.3, 0.3) * (a1 - a0) / n)
        reach = _f(g.get("reach", [0.6, 1.0]), R)
        tip = np.array([c[0] + math.cos(a) * reach, c[1] + math.sin(a) * reach, z0])
        name = f"{g.get('name', 'root')}/{i}"
        if kind == "wedge":
            # a thin fin: at the trunk it stands c.z tall, at the tip it is on the ground
            side = np.array([-math.sin(a), math.cos(a), 0]) * float(g.get("t", 0.12)) / 2
            base = np.array([c[0] + math.cos(a) * float(g.get("inset", 0.0)), c[1] + math.sin(a) * float(g.get("inset", 0.0)), 0])
            pts = [base - side, base + side, base - side + [0, 0, c[2]], base + side + [0, 0, c[2]],
                   tip - side * 0.7, tip + side * 0.7, tip - side * 0.5 + [0, 0, float(g.get("tip_h", 0.12))], tip + side * 0.5 + [0, 0, float(g.get("tip_h", 0.12))]]
            out.append({"name": name, "mat": g["mat"], "group": g.get("group", "body"),
                        "hull": {"points": np.round(pts, 3).tolist(), "round": float(g.get("round", 0.02))}})
        else:
            # an arch: two cones, out and a little up, then down to the ground
            # `sag`: how far the bend rises above the root's start (an arch out, then down to the mud)
            mid = c + (tip - c) * float(g.get("bend_at", 0.5))
            mid[2] = c[2] + float(g.get("sag", 0.0))
            out.append({"name": name + "a", "mat": g["mat"], "group": g.get("group", "body"),
                        "cone": {"a": np.round(c, 3).tolist(), "b": np.round(mid, 3).tolist(), "r1": rr, "r2": rr * 0.85}})
            out.append({"name": name + "b", "mat": g["mat"], "group": g.get("group", "body"),
                        "cone": {"a": np.round(mid, 3).tolist(), "b": np.round(tip, 3).tolist(), "r1": rr * 0.85, "r2": rr * 0.6}})
    return out


GENERATORS = {"rock": gen_rock, "spike": gen_spike, "columns": gen_columns, "roots": gen_roots}

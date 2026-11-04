"""Load a model `.yaml` file into instances of parts, materials and a palette.

Ported from the z-day object-tile-generator (`.claude/tools/art/world/props/objgen/model.py`); the
camera is not in here, so the file format carries over: parts (ellipsoid, cone, box), smooth-union
groups, procedural generators (`scatter`, `branches`, `tiers`), surface noise, and instances (one
object may be several shapes, each with its own foot). Differences for Emerald: world Y is north
(as before) and the light is a world-space vector (`render.light`: east, north, up); palettes come
from `palettes/<planet>.yaml`, 15 colours per object at most (one GBA bank).
"""
import copy
import math
import os

import numpy as np
import yaml

from . import sdf

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULTS = {
    "views": [0],
    "collider": "instances",
    "collider_pad": [0, 0],
    "enforce_palette": False,
    "render": {
        "px_per_m": 16.0,        # one tile = one metre, for every object, so sizes stay comparable
        "supersample": 4,        # sub-samples per pixel side
        "coverage": 0.4,         # fraction of a pixel that must be covered to fill it
        "outline": True,         # 1 px silhouette outline in the palette's outline colour
        "inner_lines": "selout", # "selout" | "black" | "none"
        "depth_jump": 0.35,      # metres of depth step that draws an inner line
        "light": [-0.35, -0.42, 0.84],  # world: east, north, up (from the upper left, in front, above)
        "dither": 0.06,          # N.L half-width of the 50% checker band at each tone cut of a `dither` material
        "ao": {"strength": 1.0, "threshold": 0.35},  # crevices one tone darker; strength 0 = off
        "ground_clip": True,     # nothing renders below z = 0
        "margin": 1,             # art must keep this many px from the image edge (room for the outline)
    },
}

# Default N.L thresholds per ramp length: below the first = darkest tone, and so on up.
DEFAULT_BANDS = {
    1: [],
    2: [0.25],
    3: [0.05, 0.72],
    4: [-0.15, 0.35, 0.78],
    5: [-0.35, 0.05, 0.45, 0.82],
    6: [-0.45, -0.1, 0.25, 0.55, 0.85],
}


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def euler(pitch=0.0, yaw=0.0, roll=0.0):
    """pitch>0 tips +x up, yaw>0 turns +x toward +y, roll>0 tips +z toward +y."""
    p, y, r = np.radians([pitch, yaw, roll])
    cz, sz = math.cos(y), math.sin(y)
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    cp, sp = math.cos(-p), math.sin(-p)
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    cr, sr = math.cos(-r), math.sin(-r)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    return Rz @ Ry @ Rx


def rot_toward(v, axis, deg):
    """Rotate vector v around unit `axis` by deg (Rodrigues)."""
    a = math.radians(deg)
    axis = axis / (np.linalg.norm(axis) + 1e-12)
    return v * math.cos(a) + np.cross(axis, v) * math.sin(a) + axis * (axis @ v) * (1 - math.cos(a))


def perpendicular(v, rng):
    """A random unit vector perpendicular to v."""
    r = rng.normal(size=3)
    r -= v * (r @ v) / (v @ v)
    return r / (np.linalg.norm(r) + 1e-12)


REGION_ENV = {"abs": np.abs, "sqrt": np.sqrt, "minimum": np.minimum, "maximum": np.maximum, "np": np}


# ------------------------------------------------------------------ parts

def hull_points(kind, g):
    """Points of a low-poly solid.
    hull:    {points: [[x, y, z], ...]}                       any convex solid
    prism:   {poly: [[x, y], ...], z: [z0, z1], top: s}        a plan outline raised from z0 to z1; `top`
             scales the top face about its centre (number or [sx, sy]) and `lean: [dx, dy]` shifts it,
             so one prism makes slabs, trapezoids, pyramids (top: 0.01) and sloped roofs
    extrude: {axis: x|y, profile: [[a, z], ...], span: [s0, s1], end: s}   a side profile (y-z for an x
             extrusion, x-z for a y extrusion) pushed along the axis; `end` scales the far end's profile
             about its centre: noses, wings, hulls and ramps"""
    if kind == "hull":
        return np.asarray(g["points"], float)
    if kind == "prism":
        poly = np.asarray(g["poly"], float)
        z0, z1 = (float(v) for v in g["z"])
        top = g.get("top", 1.0)
        top = np.asarray(top if isinstance(top, (list, tuple)) else [top, top], float)
        lean = np.asarray(g.get("lean", [0, 0]), float)
        c = poly.mean(0)
        up = c + (poly - c) * top + lean
        return np.vstack([np.c_[poly, np.full(len(poly), z0)], np.c_[up, np.full(len(up), z1)]])
    prof = np.asarray(g["profile"], float)
    s0, s1 = (float(v) for v in g["span"])
    end = g.get("end", 1.0)
    end = np.asarray(end if isinstance(end, (list, tuple)) else [end, end], float)
    c = prof.mean(0)
    far = c + (prof - c) * end + np.asarray(g.get("lean", [0, 0]), float)
    if g.get("axis", "x") == "x":
        a = np.c_[np.full(len(prof), s0), prof[:, 0], prof[:, 1]]
        b = np.c_[np.full(len(far), s1), far[:, 0], far[:, 1]]
    else:
        a = np.c_[prof[:, 0], np.full(len(prof), s0), prof[:, 1]]
        b = np.c_[far[:, 0], np.full(len(far), s1), far[:, 1]]
    return np.vstack([a, b])

class Part:
    KINDS = ("ellipsoid", "cone", "cylinder", "box", "hull", "prism", "extrude")

    def __init__(self, spec, mat_names, where="part"):
        self.name = spec.get("name", where)
        self.group = spec.get("group", "body")
        self.mat = spec.get("mat")
        if self.mat not in mat_names:
            raise ValueError(f"{self.name}: unknown material {self.mat!r} (have {sorted(mat_names)})")
        self.op = spec.get("op", "union")
        self.regions = []
        for i, r in enumerate(spec.get("regions", []) or []):
            if r["mat"] not in mat_names:
                raise ValueError(f"{self.name}: region uses unknown material {r['mat']!r}")
            self.regions.append((compile(str(r["where"]), f"{self.name}.regions[{i}]", "eval"), r["mat"]))
        kinds = [k for k in self.KINDS if k in spec]
        if len(kinds) != 1:
            raise ValueError(f"{self.name}: needs exactly one of {self.KINDS}")
        self.kind = kinds[0]
        g = spec[self.kind]
        if self.kind == "ellipsoid":
            self.c, self.r = np.asarray(g["c"], float), np.asarray(g["r"], float)
            self.center, self.radius_bound = self.c, float(self.r.max())
        elif self.kind in ("cone", "cylinder"):
            self.a, self.b = np.asarray(g["a"], float), np.asarray(g["b"], float)
            self.r1, self.r2 = float(g["r1"]), float(g.get("r2", g["r1"]))
            if np.linalg.norm(self.b - self.a) < 1e-6:
                self.b = self.a + [0, 0, 1e-3]
            self.center = 0.5 * (self.a + self.b)
            self.radius_bound = 0.5 * float(np.linalg.norm(self.b - self.a)) + max(self.r1, self.r2)
        elif self.kind == "box":
            self.c, self.half = np.asarray(g["c"], float), np.asarray(g["half"], float)
            self.round = float(g.get("radius", 0.0))
            self.center, self.radius_bound = self.c, float(np.linalg.norm(self.half))
        else:
            # low-poly solids: the convex hull of some points, with optionally rounded edges (`round`, m)
            pts = hull_points(self.kind, g)
            self.planes = sdf.hull_planes(pts)
            self.round = float(g.get("round", 0.0))
            self.center = pts.mean(0)
            self.radius_bound = float(np.linalg.norm(pts - self.center, axis=1).max())
        self.rot = euler(*spec["rot"]) if "rot" in spec else None
        fr = spec.get("_frame")             # set by a template's `at` / `turn`: world = R p + t
        self.frame = None if fr is None else (np.asarray(fr[0], float), np.asarray(fr[1], float))
        sq = spec.get("squash")             # {scale: [sx, sy, sz], center: [..]} or just [sx, sy, sz]
        self.squash = None
        if sq is not None:
            sq = sq if isinstance(sq, dict) else {"scale": sq}
            s = np.asarray(sq["scale"], float)
            sc = np.asarray(sq.get("center", self.center), float)
            self.squash = (sc, s)
            self.radius_bound *= float(s.max())
        # culling sphere centre, in the space the part is evaluated from (after squash)
        self.bcenter = self.center if self.squash is None else self.squash[0] + (self.center - self.squash[0]) * self.squash[1]
        if self.frame is not None:
            self.bcenter = self.frame[0] @ self.bcenter + self.frame[1]
        nz = spec.get("noise")
        self.noise = None
        if nz:
            self.noise = (float(nz.get("amp", 0.04)), float(nz.get("freq", 6.0)), int(nz.get("seed", 0)))
            self.radius_bound += self.noise[0]

    def sdf(self, c):
        k = 1.0
        if self.frame is not None:
            R, t = self.frame
            c = (c - t) @ R                  # R^T (c - t), row vectors
        if self.squash is not None:
            sc, s = self.squash
            c = sc + (c - sc) / s
            k = float(s.min())
        if self.rot is not None:
            c = self.center + (c - self.center) @ self.rot
        if self.kind == "ellipsoid":
            d = sdf.ellipsoid(c, self.c, self.r)
        elif self.kind == "cone":
            d = sdf.round_cone(c, self.a, self.b, self.r1, self.r2)
        elif self.kind == "cylinder":
            d = sdf.capped_cone(c, self.a, self.b, self.r1, self.r2)
        elif self.kind == "box":
            d = sdf.round_box(c, self.c, self.half, self.round)
        else:
            d = sdf.convex(c, self.planes, self.round)
        if self.noise is not None:
            amp, freq, seed = self.noise
            d = d + amp * sdf.value_noise(c * freq, seed)
        return d * k


# ------------------------------------------------------------------ generators

def _range(v, rng):
    """A number, or [lo, hi] -> uniform sample."""
    if isinstance(v, (list, tuple)):
        return float(rng.uniform(v[0], v[1]))
    return float(v)


def gen_scatter(g, rng):
    """`count` ellipsoid blobs at random points inside an ellipsoid region (leaf clumps, tufts)."""
    c = np.asarray(g["within"]["c"], float)
    r = np.asarray(g["within"]["r"], float)
    shell = float(g.get("shell", 0.0))           # 0 = anywhere inside, 0.8 = near the surface only
    zmin = g.get("zmin")                          # optional: no blob below this height (region-local)
    out = []
    tries = 0
    while len(out) < int(g["count"]) and tries < 5000:
        tries += 1
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        rad = rng.uniform(shell, 1.0) ** (1 / 3) if shell < 1 else 1.0
        rad = max(rad, shell)
        p = c + d * r * rad
        if zmin is not None and p[2] < c[2] + float(zmin) * r[2]:
            continue
        s = _range(g["size"], rng)
        sq = np.asarray(g.get("squash", [1, 1, 1]), float)
        spec = {"name": f"{g.get('name', 'scatter')}{len(out)}", "mat": g["mat"], "group": g.get("group", "body"),
                "ellipsoid": {"c": p.tolist(), "r": (s * sq).tolist()}}
        if "noise" in g:
            spec["noise"] = dict(g["noise"], seed=int(rng.integers(1 << 20)))
        if "regions" in g:
            spec["regions"] = g["regions"]
        out.append(spec)
    return out


def gen_branches(g, rng):
    """A recursive tree of tapered cones: trunks, limbs and twigs (dead trees, a crown's skeleton)."""
    out = []
    gravity = float(g.get("gravity", 0.0))       # + bends tips down, - up
    up_bias = float(g.get("up_bias", 0.0))       # pulls every child toward +z
    min_r = float(g.get("min_radius", 0.04))
    shrink = g.get("shrink", [0.6, 0.8])
    taper = float(g.get("taper", 0.7))
    spread = g.get("spread", [25, 45])
    split = g.get("split", [2, 3])
    side = g.get("side_start", [0.55, 1.0])     # where along a parent a child starts (fraction)

    def grow(p, d, length, radius, depth, name):
        d = d / np.linalg.norm(d)
        if gravity:
            d = d + np.array([0, 0, -gravity]) * (1 - abs(d[2]))
            d /= np.linalg.norm(d)
        end = p + d * length
        r2 = max(radius * taper, min_r)
        out.append({"name": name, "mat": g["mat"], "group": g.get("group", "body"),
                    "cone": {"a": p.tolist(), "b": end.tolist(), "r1": max(radius, min_r), "r2": r2}})
        if depth <= 0:
            return
        n = int(rng.integers(int(split[0]), int(split[1]) + 1))
        for i in range(n):
            t = 1.0 if i == 0 and g.get("continue_leader", True) else _range(side, rng)
            start = p + (end - p) * t
            rad_here = radius + (r2 - radius) * t
            nd = rot_toward(d, perpendicular(d, rng), _range(spread, rng) * (0.5 if i == 0 else 1.0))
            if up_bias:
                nd = nd + np.array([0, 0, up_bias])
            grow(start, nd, length * _range(shrink, rng), max(rad_here * 0.8, min_r), depth - 1, f"{name}.{i}")

    grow(np.asarray(g["start"], float), np.asarray(g.get("dir", [0, 0, 1]), float),
         float(g["length"]), float(g["radius"]), int(g.get("depth", 3)), g.get("name", "branch"))
    return out


def gen_tiers(g, rng):
    """Stacked skirts for a conifer: `count` flattened cones from `base_z` to `top_z`, each with
    optional drooping tufts around its rim so the silhouette is ragged, not a smooth cone."""
    out = []
    n = int(g["count"])
    base_z, top_z = float(g["base_z"]), float(g["top_z"])
    base_r, top_r = float(g["base_r"]), float(g["top_r"])
    height = float(g.get("height", (top_z - base_z) / n * 1.8))   # each skirt's own height
    jit = float(g.get("jitter", 0.0))
    tufts = int(g.get("tufts", 0))
    tuft_size = g.get("tuft_size", [0.08, 0.12])
    droop = float(g.get("droop", 0.0))          # how far a tuft hangs below its skirt's rim
    lean = np.asarray(g.get("lean", [0, 0]), float)    # top offset in x, y (a bent leader)
    flat = float(g.get("flat", 0.5))            # z squash of each skirt about its base: < 1 = a lampshade
                                                # with a hard, shaded underside, so the tiers read
    for i in range(n):
        f = i / max(n - 1, 1)
        z = base_z + (top_z - base_z) * f
        r = (base_r + (top_r - base_r) * f) * (1 + rng.uniform(-jit, jit))
        off = lean * f ** 2
        a = [off[0], off[1], z]
        b = [off[0], off[1], z + height / flat]
        spec = {"name": f"tier{i}", "mat": g["mat"], "group": g.get("group", "body"),
                "cone": {"a": a, "b": b, "r1": r, "r2": max(r * float(g.get("tip", 0.08)), 0.03)},
                "squash": {"scale": [1, 1, flat], "center": a}}
        if "noise" in g:
            spec["noise"] = dict(g["noise"], seed=int(rng.integers(1 << 20)))
        out.append(spec)
        for k in range(tufts):
            ang = (k + rng.uniform(-0.3, 0.3)) / tufts * math.tau
            s = _range(tuft_size, rng)
            p = [off[0] + math.cos(ang) * r * 0.95, off[1] + math.sin(ang) * r * 0.95, z + r * 0.05 - droop]
            out.append({"name": f"tier{i}tuft{k}", "mat": g["mat"], "group": g.get("group", "body"),
                        "ellipsoid": {"c": p, "r": [s, s, s * 0.8]}})
    return out


def gen_lobes(g, rng):
    """Leaf clumps on the surface of a crown ellipsoid, in rows by elevation (degrees above the
    equator), spread over the south-facing half from west to east and symmetric left/right. Each clump
    is a separate group (hard union), so the depth step between clumps draws the dark line that
    separates vanilla's leaf clumps. `k` pulls the clumps in towards the centre; `xs` narrows the
    crown east-west. Approved on the Hoenn tree (models/calibration/hoenn-tree.yaml)."""
    c = np.asarray(g["within"]["c"], float)
    r = np.asarray(g["within"]["r"], float)
    k, xs = float(g.get("k", 0.85)), float(g.get("xs", 1.0))
    s = float(g["size"])
    sq = np.asarray(g.get("squash", [1.0, 0.9, 0.75]), float)
    out = []
    for elev, n in g["rows"]:
        e = np.radians(float(elev))
        for i in range(int(n)):
            a = np.radians(-90 + 180 * (i + 0.5) / int(n))
            p = c + r * k * np.array([xs * np.sin(a) * np.cos(e), -np.cos(a) * np.cos(e), np.sin(e)])
            name = f"{g.get('name', 'lobe')}{len(out)}"
            out.append({"name": name, "mat": g["mat"], "group": name, "_new_group": True,
                        "ellipsoid": {"c": np.round(p, 3).tolist(), "r": (s * sq).tolist()}})
    return out


def gen_limb(g, rng):
    """A jointed leg or arm as low-poly boxes: walker legs, droid arms, cranes.
    root: [x, y, z]            where the first segment starts (the hip)
    yaw: deg                   the plane the limb bends in: 0 = bends swing the far end toward +x
    splay: deg                 tips the whole limb sideways, out of that plane (toward -y at yaw 0)
    segments: [{len, w, d, bend, taper, mat, round, joint: {r, len, mat}}]
        each starts where the last ended; `bend` (deg) is added to the angle from straight down, so a
        knee is a bend; `w` is the width across the plane, `d` the depth in it; `taper` scales the far
        end; `joint` is a disc (cylinder across the plane) at the segment's start
    foot: {r, r2, h, mat, flat: true}  a round pad at the end; `flat` keeps it level with the ground
        (a standing walker), otherwise it follows the last segment
    Part names are <name>/seg0, <name>/joint0, ..., <name>/foot, so `drop: [<name>/*]` removes it."""
    name = g.get("name", "limb")
    p = np.asarray(g["root"], float)
    yaw = math.radians(float(g.get("yaw", 0.0)))
    f = np.array([math.cos(yaw), math.sin(yaw), 0.0])
    side = np.array([-math.sin(yaw), math.cos(yaw), 0.0])
    splay = float(g.get("splay", 0.0))
    side_s = rot_toward(side, f, splay)
    ang = 0.0
    out = []
    d = np.array([0, 0, -1.0])
    for i, sg in enumerate(g["segments"]):
        ang += float(sg.get("bend", 0.0))
        a = math.radians(ang)
        d = -math.cos(a) * np.array([0, 0, 1.0]) + math.sin(a) * f
        d = rot_toward(d, f, splay)
        v = np.cross(d, side_s)
        v /= np.linalg.norm(v) + 1e-12
        L = float(sg["len"])
        w, dd = float(sg.get("w", 0.3)) / 2, float(sg.get("d", sg.get("w", 0.3))) / 2
        tp = sg.get("taper", 1.0)
        tw, td = (tp if isinstance(tp, (list, tuple)) else [tp, tp])
        q = p + d * L
        pts = [c + sw * side_s * ww + sv * v * vv
               for c, ww, vv in ((p, w, dd), (q, w * tw, dd * td)) for sw in (-1, 1) for sv in (-1, 1)]
        mat = sg.get("mat", g.get("mat"))
        if sg.get("joint"):
            j = sg["joint"]
            jl = float(j.get("len", 2 * w + 0.1)) / 2
            out.append({"name": f"{name}/joint{i}", "mat": j.get("mat", mat), "group": g.get("group", "body"),
                        "cylinder": {"a": (p - side_s * jl).tolist(), "b": (p + side_s * jl).tolist(), "r1": float(j["r"])}})
        out.append({"name": f"{name}/seg{i}", "mat": mat, "group": g.get("group", "body"),
                    "hull": {"points": np.round(pts, 4).tolist(), "round": float(sg.get("round", g.get("round", 0.03)))}})
        p = q
    ft = g.get("foot")
    if ft:
        h = float(ft.get("h", 0.3))
        ax = np.array([0, 0, -1.0]) if ft.get("flat", True) else d
        top = p - ax * float(ft.get("rise", 0.0))
        out.append({"name": f"{name}/foot", "mat": ft.get("mat", g.get("mat")), "group": g.get("group", "body"),
                    "cylinder": {"a": top.tolist(), "b": (top + ax * h).tolist(), "r1": float(ft.get("r2", ft["r"])),
                                 "r2": float(ft["r"])}})
    return out


GENERATORS = {"limb": gen_limb, "scatter": gen_scatter, "branches": gen_branches, "tiers": gen_tiers, "lobes": gen_lobes}


def expand_parts(specs, seed):
    """Replace every generator entry with the plain parts it produces."""
    out = []
    for i, spec in enumerate(specs or []):
        kind = next((k for k in GENERATORS if k in spec), None)
        if kind is None:
            out.append(spec)
            continue
        g = dict(spec[kind])
        g.setdefault("name", spec.get("name", f"{kind}{i}"))
        for key in ("mat", "group", "noise", "regions"):
            if key in spec and key not in g:
                g[key] = spec[key]
        rng = np.random.default_rng(int(g.get("seed", i)) + 7919 * int(seed))
        made = GENERATORS[kind](g, rng)
        if "_frame" in spec:
            for m in made:
                m["_frame"] = spec["_frame"]
        out.extend(made)
    return out


# ------------------------------------------------------------------ params, templates, drop

EXPR_ENV = {k: getattr(math, k) for k in ("sin", "cos", "tan", "radians", "degrees", "sqrt", "pi", "atan2")}
EXPR_ENV.update(min=min, max=max, abs=abs, round=round)


def evaluate(node, params):
    """Every string starting with `=` becomes the value of the expression after it, with `params`
    and math (sin, cos, radians, sqrt, pi, min, max) in scope: `len: "=thigh * 1.1"`."""
    if isinstance(node, str) and node.startswith("="):
        return eval(node[1:], {"__builtins__": {}}, dict(EXPR_ENV, **params))
    if isinstance(node, dict):
        return {k: evaluate(v, params) for k, v in node.items()}
    if isinstance(node, list):
        return [evaluate(v, params) for v in node]
    return node


def resolve_params(defaults, over=None):
    """Params in order; a later one may be an expression of earlier ones."""
    out = {}
    for k, v in dict(defaults or {}, **(over or {})).items():
        out[k] = evaluate(v, out)
    return out


def _compose(frame, R, t):
    """frame (R0, t0) applied after (R, t): world = R0 (R p + t) + t0."""
    if frame is None:
        return R, t
    R0, t0 = np.asarray(frame[0]), np.asarray(frame[1])
    return R0 @ R, R0 @ t + t0


def expand_templates(parts, templates, params, prefix="", depth=0):
    """`use: <template>` entries become the template's parts, evaluated with its params (template
    defaults < the model's params < the entry's `with`), named <entry name>/<part name>, moved by the
    entry's `at: [x, y, z]` and turned by `turn` (deg about z) and `rot: [pitch, yaw, roll]`.
    `mirror: y` flips the template north-south (a left leg from a right one)."""
    if depth > 8:
        raise ValueError("templates nest more than 8 deep")
    out = []
    for i, spec in enumerate(parts or []):
        if "use" not in spec:
            p = evaluate(spec, params)
            if prefix:
                p["name"] = prefix + p.get("name", f"part{i}")
            out.append(p)
            continue
        t = templates.get(spec["use"])
        if t is None:
            raise ValueError(f"unknown template {spec['use']!r} (have {sorted(templates)})")
        sp = evaluate({k: v for k, v in spec.items() if k != "with"}, params)
        local = resolve_params(dict(params, **(t.get("params") or {})), evaluate(spec.get("with") or {}, params))
        name = sp.get("name", f"{spec['use']}{i}")
        inner = expand_templates(t.get("parts"), templates, local, prefix + name + "/", depth + 1)
        R = euler(*(sp.get("rot") or [0, 0, 0]))
        R = euler(0, float(sp.get("turn", 0.0)), 0) @ R
        if sp.get("mirror") in ("y", True):
            R = R @ np.diag([1.0, -1.0, 1.0])
        T = np.asarray(sp.get("at", [0, 0, 0]), float)
        for p in inner:
            if "mat" in sp and "mat" not in p:
                p["mat"] = sp["mat"]
            Rp, Tp = _compose((R, T), *(p["_frame"] if "_frame" in p else (np.eye(3), np.zeros(3))))
            p["_frame"] = (Rp.tolist(), Tp.tolist())
            out.append(p)
    return out


# ------------------------------------------------------------------ instances

class Instance:
    """One shape placed in the object image: parts + a foot (anchor), collider box and shadow."""

    def __init__(self, spec, mat_names, where, needs_parts=True):
        self.where = where
        self.foot = np.asarray(spec["foot"], float)                 # px in the object image
        self.seed = int(spec.get("seed", 0))
        self.scale = float(spec.get("scale", 1.0))
        self.stretch = np.asarray(spec.get("stretch", [1, 1, 1]), float) * self.scale
        self.mirror = bool(spec.get("mirror", False))
        # `turn` spins the instance about the vertical line through `pivot` (metres from the foot),
        # so one model yields its other facings while the foot and collider stay put
        self.turn = float(spec.get("turn", 0.0))
        self.pivot = np.array([*spec.get("pivot", [0, 0]), 0.0], float)
        # `tilt: [pitch, roll]` tips the instance about the ground point at `pivot` (same sense as a
        # part's `rot`) and `sink` lowers it (m); the ground clip then cuts it flat at z = 0, e.g. a
        # wreck settled in water or mud
        tilt = spec.get("tilt")
        self.tilt = None if not tilt else euler(float(tilt[0]), 0.0, float(tilt[1]))
        self.sink = float(spec.get("sink", 0.0))
        box = spec.get("box", [6, 4])
        self.box = None if box is None else (int(box[0]), int(box[1]))
        sh = spec.get("shadow")
        self.shadow = None if not sh else (float(sh["rx"]), float(sh["ry"]), float(sh.get("dx", 0)), float(sh.get("dy", 0)))
        self.groups = {}
        for gname, g in (spec.get("groups") or {"body": {}}).items():
            self.groups[gname] = {"k": float(g.get("k", 0.0)), "join": float(g.get("join", 0.0))}
        expanded = expand_parts(spec.get("parts"), self.seed)
        drop = spec.get("drop") or []          # name patterns (fnmatch): a variant without some parts
        if drop:
            import fnmatch
            expanded = [p for p in expanded if not any(fnmatch.fnmatch(p.get("name", ""), d) for d in drop)]
        for p in expanded:
            if p.pop("_new_group", False):
                self.groups.setdefault(p["group"], {"k": 0.0, "join": 0.0})
        self.parts = [Part(p, mat_names, f"{where}.parts[{i}]") for i, p in enumerate(expanded)]
        for p in self.parts:
            if p.group not in self.groups:
                raise ValueError(f"{where}: part {p.name} uses unknown group {p.group!r}")
        if not self.parts and needs_parts:
            raise ValueError(f"{where}: no parts")
        self.union_ids = np.array([i for i, p in enumerate(self.parts) if p.op == "union"])
        self.centers = np.array([p.bcenter for p in self.parts])
        self.bounds = np.array([p.radius_bound for p in self.parts])
        self.cull = 0.25 + 3 * max([g["k"] for g in self.groups.values()] + [g["join"] for g in self.groups.values()])

    # model space <- world space: undo yaw, mirror and stretch
    def to_model(self, P, yaw):
        if yaw:
            a = math.radians(-yaw)
            c, s = math.cos(a), math.sin(a)
            P = P @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]]).T
        if self.turn:
            a = math.radians(-self.turn)
            c, s = math.cos(a), math.sin(a)
            P = (P - self.pivot) @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]]).T + self.pivot
        if self.sink:
            P = P + [0, 0, self.sink]
        if self.tilt is not None:
            P = self.pivot + (P - self.pivot) @ self.tilt
        if self.mirror:
            P = P * [-1, 1, 1]
        return P / self.stretch

    def sdf(self, P, yaw=0.0, want=False):
        Q = self.to_model(P, yaw)
        k = self.stretch.min()
        raw = np.empty((len(self.parts), len(Q)))
        for i, part in enumerate(self.parts):
            ds = np.linalg.norm(Q - self.centers[i], axis=1) - self.bounds[i]
            near = ds < self.cull
            row = ds.copy()
            if near.any():
                row[near] = part.sdf(Q[near])
            raw[i] = row
        raw *= k
        gd, subs = {}, {}
        for i, p in enumerate(self.parts):
            g = self.groups[p.group]
            if p.op == "subtract":
                subs.setdefault(p.group, []).append(i)
                continue
            gd[p.group] = raw[i] if p.group not in gd else sdf.smin(gd[p.group], raw[i], g["k"])
        for gname, ids in subs.items():
            for i in ids:
                if gname in gd:
                    gd[gname] = sdf.ssub(gd[gname], raw[i], self.groups[gname]["k"])
        d = None
        for gname, g in self.groups.items():
            if gname in gd:
                d = gd[gname] if d is None else sdf.smin(d, gd[gname], g["join"])
        d = np.maximum(d, -P[:, 2])          # ground clip
        if not want:
            return d
        # which part owns a surface point: the nearest union part AFTER its group's subtractions,
        # else a door standing inside a recess cut from a wall would take the wall's material
        carved = raw.copy()
        for gname, ids in subs.items():
            k = self.groups[gname]["k"]
            for j, p in enumerate(self.parts):
                if p.group == gname and p.op == "union":
                    for i in ids:
                        carved[j] = sdf.ssub(carved[j], raw[i], k)
        pid = self.union_ids[np.argmin(carved[self.union_ids], axis=0)]
        return d, pid, Q

    def material_of(self, pid, Q):
        out = np.empty(len(pid), dtype=object)
        for i in np.unique(pid):
            m = pid == i
            part = self.parts[i]
            names = np.full(m.sum(), part.mat, dtype=object)
            if part.regions:
                c = Q[m]
                env = dict(REGION_ENV, x=c[:, 0], y=c[:, 1], z=c[:, 2])
                for code, mat in part.regions:
                    sel = np.asarray(eval(code, {"__builtins__": {}}, env), bool)
                    names[np.broadcast_to(sel, names.shape)] = mat
            out[m] = names
        return out

    def world_bounds(self):
        """Conservative world-space AABB (any yaw) of every part."""
        lo = (self.centers - self.bounds[:, None]) * self.stretch
        hi = (self.centers + self.bounds[:, None]) * self.stretch
        if self.mirror:
            lo, hi = np.minimum(lo * [-1, 1, 1], hi * [-1, 1, 1]), np.maximum(lo * [-1, 1, 1], hi * [-1, 1, 1])
        r = np.max(np.abs(np.concatenate([lo[:, :2], hi[:, :2]])), axis=0).max()
        if self.turn:
            r += 2 * np.linalg.norm(self.pivot)
        zlo, zhi = lo[:, 2].min(), hi[:, 2].max()
        if self.tilt is not None:
            r3 = np.abs(np.concatenate([lo, hi])).max() + np.linalg.norm(self.pivot)
            r, zlo, zhi = max(r, r3), -r3, r3
        zhi -= self.sink
        return np.array([-r, -r, max(zlo - self.sink, 0)]), np.array([r, r, zhi])


# ------------------------------------------------------------------ the object file

def _load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


SHAPE_KEYS = ("parts", "groups", "box", "shadow", "materials")


def _remat(parts, mapping):
    """Copy of `parts` with every `mat` (on a part, its regions, or a generator) renamed by `mapping`."""
    out = copy.deepcopy(parts or [])
    for p in out:
        for d in [p] + [p[k] for k in GENERATORS if isinstance(p.get(k), dict)]:
            if d.get("mat") in mapping:
                d["mat"] = mapping[d["mat"]]
            for r in d.get("regions") or []:
                if r.get("mat") in mapping:
                    r["mat"] = mapping[r["mat"]]
    return out


SHAPE_KEYS = SHAPE_KEYS + ("drop",)
# how a single-shape file is posed: the keys an instance reads besides its shape
INSTANCE_KEYS = ("foot", "seed", "scale", "stretch", "mirror", "turn", "pivot", "tilt", "sink")


class Object:
    def __init__(self, path, raw=None):
        self.path = os.path.abspath(path)
        raw = copy.deepcopy(raw) if raw is not None else _load_yaml(path)
        raw.pop("variants", None)
        # params, expressions and templates: resolved into plain parts before anything else
        self.params = resolve_params(raw.get("params"))
        templates = {}
        for f in raw.get("kits") or []:                 # shared template files, relative to the model
            kit = _load_yaml(os.path.join(os.path.dirname(self.path), f))
            templates.update(kit.get("templates") or {})
        templates.update(raw.get("templates") or {})
        for key in ("parts", "ground"):
            if key in raw:
                raw[key] = expand_templates(raw[key], templates, self.params)
        for k in [k for k in raw if k not in ("parts", "ground", "templates", "params", "kits")]:
            raw[k] = evaluate(raw[k], self.params)
        self.raw = raw
        self.name = raw.get("name") or os.path.basename(path).split(".")[0]
        self.description = raw.get("description", "")
        cfg = deep_merge(DEFAULTS, {k: raw[k] for k in DEFAULTS if k in raw})
        self.rnd = cfg["render"]
        self.views = [float(v) for v in cfg["views"]]
        self.collider_mode = cfg["collider"]
        self.collider_pad = (int(cfg["collider_pad"][0]), int(cfg["collider_pad"][1]))
        self.enforce_palette = bool(cfg["enforce_palette"])
        cells = raw.get("cells", [1, 1])
        self.cells = (int(cells[0]), int(cells[1]))
        self.size = (self.cells[0] * 16, self.cells[1] * 16)
        # `sprite`: a pre-rendered PNG pasted in place of the parts (see README -> "Sprite objects")
        sprite = raw.get("sprite")
        self.sprite = None if not sprite else {
            "image": os.path.join(os.path.dirname(self.path), sprite["image"]),
            "at": (int(sprite.get("at", [0, 0])[0]), int(sprite.get("at", [0, 0])[1])),
        }

        # instances: the file itself, or a list of them (each may `include` another object file)
        specs = raw.get("instances")
        if specs is None:
            base = {k: raw[k] for k in SHAPE_KEYS + INSTANCE_KEYS if k in raw}
            base.setdefault("foot", [self.size[0] / 2, self.size[1] - 3])
            specs = [base]
            # `ground`: parts lying on the ground around the piece (snow drifts, debris, an ice shelf).
            # They share its foot but are never posed: tilt, turn, sink and scale leave them alone.
            # Drawn first, so the piece covers them where they meet.
            if raw.get("ground"):
                specs.append({"foot": base["foot"], "parts": raw["ground"], "box": None, "seed": base.get("seed", 0)})
        materials = dict(raw.get("materials") or {})
        resolved = []
        for i, s in enumerate(specs):
            s = dict(s)
            if "include" in s:
                inc_path = os.path.join(os.path.dirname(self.path), s.pop("include"))
                inc = _load_yaml(inc_path)
                # `instance: n` takes one tree out of a file with instances (a cluster's tuned crowns)
                pick = s.pop("instance", None)
                src = inc
                if inc.get("instances"):
                    if pick is None:
                        raise ValueError(f"{path}: instances[{i}] includes {inc_path}, which has instances: "
                                         "say which with `instance: <index>`")
                    src = inc["instances"][int(pick)]
                    if "include" in src:
                        raise ValueError(f"{path}: instances[{i}] takes instance {pick} of {inc_path}, which is itself an include")
                elif pick is not None:
                    raise ValueError(f"{path}: instances[{i}] asks for instance {pick} of {inc_path}, which has no instances")
                merged = {k: src[k] for k in SHAPE_KEYS + ("seed",) if k in src}
                merged.update(s)
                s = merged
                for k, v in (inc.get("materials") or {}).items():
                    materials.setdefault(k, v)
            for k, v in (s.get("materials") or {}).items():
                materials.setdefault(k, v)
            # `remat: {old: new}` renames the materials this instance's parts use, so one included
            # model can appear twice in an object in different colours (a stack of mixed containers)
            remat = s.pop("remat", None)
            if remat:
                s["parts"] = _remat(s.get("parts"), remat)
            resolved.append(s)
        self._load_palette(raw, materials)
        self.instances = [Instance(s, set(self.mats), f"{self.name}.instances[{i}]", needs_parts=self.sprite is None)
                          for i, s in enumerate(resolved)]

    # ---------------------------------------------------------- palette
    def _load_palette(self, raw, materials):
        lib = {"ramps": {}, "singles": {}, "outline": [31, 28, 24], "shadow": [31, 28, 24, 110]}
        pal_name = raw.get("palette", "common")
        p = pal_name if os.path.exists(str(pal_name)) else os.path.join(REPO, "palettes", f"{pal_name}.yaml")
        lib = deep_merge(lib, _load_yaml(p))
        allowed = [tuple(lib["outline"])] + [tuple(c) for r in lib["ramps"].values() for c in r] + \
                  [tuple(c) for c in lib["singles"].values()]

        def snap(col):
            if not self.enforce_palette:
                return tuple(col)
            arr = np.asarray(allowed, float)
            return allowed[int(np.argmin(((arr - np.asarray(col, float)) ** 2).sum(1)))]

        colors = [(0, 0, 0), tuple(raw.get("outline", lib["outline"]))]
        self.shadow_rgba = tuple(lib["shadow"])
        self.highlight_rgb = tuple(lib.get("highlight", (255, 255, 255)))
        self.mats = {}
        for name, spec in materials.items():
            m = {"priority": float(spec.get("priority", 1.0)), "cutout": spec.get("cutout"),
                 "dither": bool(spec.get("dither", False)), "shares": spec.get("shares"),
                 "emissive": bool(spec.get("emissive", False))}
            if "ramp" in spec:
                ramp = spec["ramp"]
                ramp = lib["ramps"][ramp] if isinstance(ramp, str) else ramp
                m["idx"] = []
                for c in ramp:                      # materials sharing a colour share its index
                    c = snap(c)
                    if c not in colors[1:]:
                        colors.append(c)
                    m["idx"].append(colors.index(c, 1))
                bands = spec.get("bands", DEFAULT_BANDS.get(len(ramp)))
                if bands is None or len(bands) != len(ramp) - 1:
                    raise ValueError(f"material {name}: needs {len(ramp) - 1} band thresholds")
                m["bands"] = [float(b) for b in bands]
            else:
                col = spec["color"]
                col = lib["singles"][col] if isinstance(col, str) else col
                col = snap(col)
                if col not in colors[1:]:
                    colors.append(col)
                m["idx"] = [colors.index(col, 1)]
                m["bands"] = []
            self.mats[name] = m
        # the ground shadow is an opaque checker in one colour of the bank (a GBA tile has no alpha)
        self.shadow_idx = len(colors)
        colors.append(tuple(lib["shadow"][:3]))
        self.palette = np.array(colors, dtype=np.uint8)
        self.priority = np.ones(len(colors))
        self.shadow_of = np.arange(len(colors))     # one tone darker (inner lines)
        self.darkest_of = np.ones(len(colors), int)  # the material's darkest tone (outlines)
        for m in self.mats.values():
            for i in m["idx"]:
                self.priority[i] = m["priority"]
                self.darkest_of[i] = m["idx"][0]
            if len(m["idx"]) > 1:
                self.shadow_of[m["idx"][0]] = m["idx"][0]
                for i in m["idx"][1:]:
                    self.shadow_of[i] = m["idx"][0]
        # ground shadow rings (`ground_shadow:`), outermost first: {rx, ry, dx, dy, color, checker}
        # `color` names a single, or `ramp:k` for tone k of a ramp; drawn only where the object is not
        self.ground_shadow = []
        for g in raw.get("ground_shadow", []) or []:
            c = g["color"]
            if isinstance(c, str) and ":" in c:
                rname, k = c.split(":")
                c = lib["ramps"][rname][int(k)]
            elif isinstance(c, str):
                c = lib["singles"][c]
            c = snap(c)
            if tuple(c) not in colors[1:]:
                colors.append(tuple(c))
            self.ground_shadow.append({"rx": float(g["rx"]), "ry": float(g["ry"]), "dx": float(g.get("dx", 0)),
                                       "dy": float(g.get("dy", 0)), "idx": colors.index(tuple(c), 1),
                                       "checker": bool(g.get("checker", False))})
        # `drop_shadow`: the silhouette shifted by (dx, dy) px, painted on empty ground in one colour,
        # like the grey band vanilla rocks and buildings cast to the lower right
        self.drop_shadow = []
        for g in raw.get("drop_shadow", []) or []:
            c = g["color"]
            c = lib["singles"][c] if isinstance(c, str) else c
            c = snap(c)
            if tuple(c) not in colors[1:]:
                colors.append(tuple(c))
            self.drop_shadow.append({"dx": int(g.get("dx", 1)), "dy": int(g.get("dy", 1)), "idx": colors.index(tuple(c), 1),
                                     "below": float(g.get("below", 0.0))})
        extra = len(colors) - len(self.palette)
        if extra:
            self.palette = np.array(colors, dtype=np.uint8)
            self.priority = np.concatenate([self.priority, np.ones(extra)])
            self.shadow_of = np.concatenate([self.shadow_of, np.arange(len(colors) - extra, len(colors))])
            self.darkest_of = np.concatenate([self.darkest_of, np.arange(len(colors) - extra, len(colors))])
        used = len(colors) - 1
        if used > 30:
            raise ValueError(f"{self.name}: {used} colours, more than two GBA banks (30)")

    # ---------------------------------------------------------- footprint and colliders
    def footprint_rows(self):
        """Cell rows (0 = top) the player cannot enter: `footprint: n` = the bottom n rows, or the
        rows any collider box touches."""
        rows = self.cells[1]
        fp = self.raw.get("footprint")
        if fp is not None:
            return list(range(max(rows - int(fp), 0), rows))
        out = set()
        for x, y, w, h in self.foot_boxes():
            for r in range(max(y // 16, 0), min((y + h - 1) // 16 + 1, rows)):
                out.add(r)
        return sorted(out)

    def foot_boxes(self):
        """Collider boxes in object-image pixels: [(x, y, w, h)]."""
        boxes = []
        for inst in self.instances:
            if inst.box is None:
                continue
            w, h = inst.box
            boxes.append((int(round(inst.foot[0] - w / 2)), int(round(inst.foot[1] - h)), w, h))
        if self.collider_mode == "bbox" and boxes:
            x0 = min(b[0] for b in boxes)
            y0 = min(b[1] for b in boxes)
            x1 = max(b[0] + b[2] for b in boxes)
            y1 = max(b[1] + b[3] for b in boxes)
            boxes = [(x0, y0, x1 - x0, y1 - y0)]
        top, bottom = self.collider_pad
        return [(x, y - top, w, h + top + bottom) for x, y, w, h in boxes]

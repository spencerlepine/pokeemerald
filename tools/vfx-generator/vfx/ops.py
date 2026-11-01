"""Spec ops -> drawing calls.

An op is a one-key mapping, e.g. `{disc: {cx: 8, cy: 8, r: 6, ramp: ion}}`. Any number in an op may be
an expression string starting with '=', evaluated per frame with:

  t     0..1 across the drawn frames (0 on the first, 1 on the last)
  i, n  frame index and frame count
  pi, sin, cos, sqrt, abs, min, max, floor, ceil, clamp(x, lo, hi), lerp(a, b, u)
  rnd(k)  a repeatable random number 0..1 for key k (same on every build)

Paint options on every shape: ramp (name, list of indices, or a single index), mode
(over/under/lighten/darken/erase), bands (thresholds, hot to cold), offset (shift down the ramp),
dither (0..1, ordered checker across band edges).
"""
from __future__ import annotations

import importlib.util
import math
import random

import numpy as np

from . import draw
from .game import GAME, HERE
from .sheet import read_indexed, split_frames

_ENV = {k: getattr(math, k) for k in ("pi", "sin", "cos", "tan", "sqrt", "floor", "ceil", "atan2", "hypot", "exp", "log")}
_ENV.update(abs=abs, min=min, max=max, round=round, int=int,
            clamp=lambda x, lo, hi: max(lo, min(hi, x)), lerp=lambda a, b, u: a + (b - a) * u)


def ev(v, ctx):
    if isinstance(v, str) and v.startswith("="):
        env = dict(_ENV)
        env.update(ctx)
        env["rnd"] = lambda k: random.Random(hash((str(k), ctx.get("seed", 0))) & 0xFFFFFFFF).random()
        return eval(v[1:], {"__builtins__": {}}, env)
    if isinstance(v, list):
        return [ev(x, ctx) for x in v]
    if isinstance(v, dict):
        return {k: ev(x, ctx) for k, x in v.items()}
    return v


PAINT_KEYS = ("ramp", "mode", "bands", "offset", "dither", "index", "when")


def _paint(canvas, mask, val, a):
    if "index" in a and "ramp" not in a:
        if a.get("mode") == "erase":
            canvas.pix[mask] = 0
        elif a.get("mode") == "under":
            canvas.pix[mask & (canvas.pix == 0)] = canvas.pal.index(a["index"])
        else:
            canvas.pix[mask] = canvas.pal.index(a["index"])
        return
    canvas.paint(mask, val, a.get("ramp", 0), mode=a.get("mode", "over"), bands=a.get("bands"),
                 offset=int(a.get("offset", 0)), dither=float(a.get("dither", 0.0)))


def _vanilla_frames(path, frame_size, mw=1, mh=1):
    pix, cols = read_indexed(GAME / path if not str(path).startswith("/") else path)
    return split_frames(pix, frame_size[0], frame_size[1], mw, mh), cols


def run(canvas, ops, ctx, built=None):
    """Apply a list of ops to a canvas. `built` holds frames already made (for `copy`)."""
    w, h = canvas.w, canvas.h
    for op in ops or []:
        if not isinstance(op, dict) or len(op) != 1:
            raise ValueError(f"an op is a one-key mapping, got {op!r}")
        (name, a), = op.items()
        a = ev(a or {}, ctx)
        if "when" in a and not a["when"]:
            continue
        if name == "disc":
            m, v = draw.disc(w, h, a["cx"], a["cy"], a["r"], light=tuple(a.get("light", (0, 0))),
                             falloff=a.get("falloff", 1.0))
        elif name == "ellipse":
            m, v = draw.ellipse(w, h, a["cx"], a["cy"], a["rx"], a["ry"], angle=a.get("angle", 0),
                                light=tuple(a.get("light", (0, 0))), falloff=a.get("falloff", 1.0))
        elif name == "ring":
            m, v = draw.ring(w, h, a["cx"], a["cy"], a["r"], a.get("thick", 1.5), bright=a.get("bright", "center"))
        elif name == "beam":
            m, v = draw.capsule(w, h, a["x0"], a["y0"], a["x1"], a["y1"], a["r0"], a.get("r1"),
                                falloff=a.get("falloff", 1.0))
        elif name == "bolt":
            pts = draw.zigzag(a["x0"], a["y0"], a["x1"], a["y1"], a.get("segments", 6), a.get("amp", 3),
                              int(a.get("seed", 0)), a.get("smooth", 0.0))
            m, v = draw.polyline(w, h, pts, a.get("r0", 1.2), a.get("r1"), falloff=a.get("falloff", 1.0))
            for br in draw.branches(pts, int(a.get("branches", 0)), a.get("branch_len", 4), int(a.get("seed", 0))):
                bm, bv = draw.polyline(w, h, br, a.get("branch_r", 0.8), a.get("branch_r1", 0.6))
                m, v = m | bm, np.maximum(v, bv * bm)
        elif name == "path":
            m, v = draw.polyline(w, h, [tuple(p) for p in a["points"]], a.get("r0", 1.0), a.get("r1"),
                                 falloff=a.get("falloff", 1.0))
        elif name == "polygon":
            m, v = draw.polygon(w, h, [tuple(p) for p in a["points"]], light=tuple(a.get("light", (0, 0))))
        elif name == "star":
            m, v = draw.star(w, h, a["cx"], a["cy"], a["r_in"], a["r_out"], int(a.get("points", 8)),
                             a.get("rot", 0), a.get("jitter", 0), int(a.get("seed", 0)))
        elif name == "crescent":
            m, v = draw.crescent(w, h, a["cx"], a["cy"], a["r"], a["thick"], a["a0"], a["a1"],
                                 taper=a.get("taper", True), bright=a.get("bright", "outer"))
        elif name == "rect":
            m, v = draw.rect(w, h, a["x"], a["y"], a["w"], a["h"])
        elif name == "sparks":
            _sparks(canvas, a, ctx)
            continue
        elif name == "grid":
            _grid(canvas, a)
            continue
        elif name == "outline":
            draw.outline(canvas, canvas.pal.index(a["index"]), inner=a.get("inner", False), diag=a.get("diag", False))
            continue
        elif name == "selout":
            draw.selout(canvas, diag=a.get("diag", False))
            continue
        elif name == "despeckle":
            keep = {canvas.pal.index(k) for k in a.get("keep", [])}
            draw.despeckle(canvas, int(a.get("min", 1)), keep or None)
            continue
        elif name == "recolor":
            src = {canvas.pal.index(k): canvas.pal.index(v) for k, v in a.items() if k not in PAINT_KEYS}
            out = canvas.pix.copy()
            for k, v in src.items():
                out[canvas.pix == k] = v
            canvas.pix = out
            continue
        elif name == "vanilla":
            _vanilla(canvas, a)
            continue
        elif name == "copy":
            src = built[int(a["frame"])]
            pix = src.copy()
            pix = _xform(pix, a)
            m = pix > 0
            canvas.pix[m] = pix[m]
            continue
        elif name == "transform":
            canvas.pix = _xform(canvas.pix, a)
            continue
        elif name == "python":
            _python(canvas, a, ctx)
            continue
        else:
            raise ValueError(f"unknown op {name!r}")
        _paint(canvas, m, v, a)


def _xform(pix, a):
    if a.get("flipx"):
        pix = pix[:, ::-1]
    if a.get("flipy"):
        pix = pix[::-1, :]
    if a.get("rot90"):
        pix = np.rot90(pix, -int(a["rot90"]))
    if a.get("rotate"):
        pix = draw.rotate_nn(pix, a["rotate"], a.get("cx"), a.get("cy"))
    if a.get("scale"):
        pix = draw.scale_nn(pix, a["scale"], a.get("cx"), a.get("cy"))
    if a.get("dx") or a.get("dy"):
        pix = draw.shift(pix, int(round(a.get("dx", 0))), int(round(a.get("dy", 0))))
    return np.ascontiguousarray(pix)


def _sparks(canvas, a, ctx):
    """Scattered sparks: `n` specks in a box (x, y, w, h) or on a ring (cx, cy, r). shape: dot | plus |
    cross | diamond. Steps along `ramp` pick hot (centre) and cold (arms) colours."""
    rng = random.Random(int(a.get("seed", 0)))
    idx = canvas.pal.ramp(a.get("ramp", 0))
    shape = a.get("shape", "plus")
    for _ in range(int(a.get("n", 4))):
        if "r" in a:
            ang = rng.uniform(0, 2 * math.pi)
            rr = a["r"] * rng.uniform(a.get("r_min", 0.7), 1.0)
            x, y = a["cx"] + rr * math.cos(ang), a["cy"] + rr * math.sin(ang)
        else:
            x = a.get("x", 0) + rng.uniform(0, a.get("w", canvas.w))
            y = a.get("y", 0) + rng.uniform(0, a.get("h", canvas.h))
        x, y = int(round(x)), int(round(y))
        pts = [(0, 0, 0)]
        if shape == "plus":
            pts += [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1)]
        elif shape == "cross":
            pts += [(1, 1, 1), (-1, -1, 1), (1, -1, 1), (-1, 1, 1)]
        elif shape == "diamond":
            pts += [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (2, 0, 2), (-2, 0, 2), (0, 2, 2), (0, -2, 2)]
        for dx, dy, s in pts:
            px, py = x + dx, y + dy
            if 0 <= px < canvas.w and 0 <= py < canvas.h:
                if a.get("mode") == "under" and canvas.pix[py, px]:
                    continue
                canvas.pix[py, px] = idx[min(s + int(a.get("offset", 0)), len(idx) - 1)]


def _grid(canvas, a):
    """Hand-placed pixels. rows: strings; legend: char -> palette ref ('pod.1', 7). '.' and ' ' are
    empty. shade: char -> ramp, to volume-shade that letter's region (lit toward `light`)."""
    rows = a["rows"]
    legend = a.get("legend", {})
    shade = a.get("shade", {})
    x0, y0 = int(a.get("x", 0)), int(a.get("y", 0))
    gh, gw = len(rows), max(len(r) for r in rows)
    chars = np.full((gh, gw), " ")
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            chars[y, x] = ch
    for ch, ramp in shade.items():
        m = chars == ch
        v = draw.shade_mask(m, light=tuple(a.get("light", (-1, -1))), depth=int(a.get("depth", 3)))
        idx = canvas.pal.ramp(ramp)
        step = draw.quantise(v, len(idx), a.get("bands"))
        for y, x in zip(*np.nonzero(m)):
            px, py = x0 + x, y0 + y
            if 0 <= px < canvas.w and 0 <= py < canvas.h:
                canvas.pix[py, px] = idx[step[y, x]]
    for ch, ref in legend.items():
        if ch in shade:
            continue
        m = chars == ch
        val = canvas.pal.index(ref) if ref not in (None, "") else 0
        for y, x in zip(*np.nonzero(m)):
            px, py = x0 + x, y0 + y
            if 0 <= px < canvas.w and 0 <= py < canvas.h:
                canvas.pix[py, px] = val


def _vanilla(canvas, a):
    """Start from a vanilla frame. remap: {old_index: new_ref}; luma: ramp (map the vanilla colours by
    brightness onto a ramp); keep: true leaves unmapped indices as they are (only on the same palette)."""
    frames, cols = _vanilla_frames(a["path"], a.get("frame_size", (canvas.w, canvas.h)),
                                   int(a.get("mwidth", 1)), int(a.get("mheight", 1)))
    src = frames[int(a.get("frame", 0))].copy()
    src = _xform(src, a)
    out = np.zeros_like(src)
    if "luma" in a:
        idx = canvas.pal.ramp(a["luma"])
        used = sorted({int(v) for v in np.unique(src) if v})
        lum = {u: 0.299 * cols[u][0] + 0.587 * cols[u][1] + 0.114 * cols[u][2] for u in used}
        order = sorted(used, key=lambda u: -lum[u])
        lo, hi = min(lum.values(), default=0), max(lum.values(), default=1)
        for u in order:
            k = 0 if hi == lo else int(round((hi - lum[u]) / (hi - lo) * (len(idx) - 1)))
            out[src == u] = idx[k]
    remap = {int(k): canvas.pal.index(v) for k, v in (a.get("remap") or {}).items()}
    for k, v in remap.items():
        out[src == k] = v
    if a.get("keep"):
        rest = (out == 0) & (src > 0)
        out[rest] = src[rest]
    m = out > 0
    if a.get("mode") == "under":
        m &= canvas.pix == 0
    canvas.pix[m] = out[m]


def _python(canvas, a, ctx):
    path = HERE / a["module"]
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    getattr(mod, a.get("func", "draw"))(canvas, ctx, **(a.get("args") or {}))

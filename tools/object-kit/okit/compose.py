"""A blueprint plus a seed becomes one world-art model (a dict), rendered by the world-art camera.

A blueprint (`blueprints/<style>/<name>.yaml`) is a family of objects, not one object:

    name: boulder
    style: tatooine                 # kits/<style>.yaml: its materials and templates
    role: edge                      # edge | noise | landmark | walkable (wiki/bible/WORLD_ART.md)
    footprint: [[1, 1], [2, 2]]     # hit box options, W x D cells; one is picked per seed (or one [W, D])
    fill: true                      # the art may run edge to edge sideways (a border piece that tiles)
    drawn: 4                        # optional: fix the sprite at this many rows (a trunk cut off at the top)
    choose:                         # params picked per seed, in order; later ones may use earlier ones
      h: [0.6, 0.9]                 #   [lo, hi]: a number between
      kind: {pick: [round, flat]}   #   pick: one of (weights: {pick: [...], weights: [...]})
      n: {int: [2, 4]}              #   a whole number, both ends in
      r: "=h * 0.6"                 #   an expression of earlier params
    parts:                          # world-art parts and `use:` templates, plus:
      - {when: "=kind == 'flat'", parts: [...], else: [...]}
      - {chance: 0.5, parts: [...]}                   # on some seeds
      - {pick: [{weight: 2, parts: [...], set: {...}}, {parts: [...]}]}   # one of these
      - {repeat: "=n", parts: [...]}                  # n times, with `i` (0..n-1) in scope
      - {rock: {...}}, {spike: {...}}, {columns: {...}}   # object-kit generators (gens.py)
    ground: [...]                   # parts lying flat round it (never counted in the hit box)
    ground_shadow: [...]            # world-art ground-shade ellipses (the vanilla tree's halo)

Params always in scope: `W`, `D` (the hit box in cells), `w_max`, `d_max` (metres the object may use),
`seed`. Axes: x east (0 = the middle of the sprite), y north (0 = the south edge of the hit box, so the
object stands on 0 <= y <= D), z up, 1 m = 1 cell = 16 px. The sprite is W cells wide and as many
rows tall as the art needs: the bottom D rows are the hit box, the rows above are walk-behind.
"""
import copy
import math
import os
import random
import sys

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
KITS = os.path.join(HERE, "kits")
BLUEPRINTS = os.path.join(HERE, "blueprints")
WORLDART = os.environ.get("WORLDART_DIR", os.path.join(ROOT, "tools", "world-art"))
sys.path.insert(0, WORLDART)
from worldart import model as M  # noqa: E402

from . import gens as G  # noqa: E402

M.GENERATORS.update(G.GENERATORS)   # so templates in kits may use rock, spike, columns, roots too

TALL = 8          # cells of canvas the render starts with; cropped to the art afterwards
MARGIN = 0.1      # metres kept clear on each side of a piece that does not `fill`


def load(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def blueprint_path(name):
    """`style/name` or a bare name (the first style that has it), or a path."""
    if os.path.exists(name):
        return os.path.abspath(name)
    if "/" in name:
        p = os.path.join(BLUEPRINTS, f"{name}.yaml")
        if os.path.exists(p):
            return p
        raise SystemExit(f"no blueprint {name} (blueprints/{name}.yaml)")
    for style in sorted(os.listdir(BLUEPRINTS)):
        p = os.path.join(BLUEPRINTS, style, f"{name}.yaml")
        if os.path.exists(p):
            return p
    raise SystemExit(f"no blueprint {name} in blueprints/<style>/")


def all_blueprints(style=None):
    out = []
    for s in sorted(os.listdir(BLUEPRINTS)):
        if style and s != style:
            continue
        d = os.path.join(BLUEPRINTS, s)
        if not os.path.isdir(d):
            continue
        out += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".yaml")]
    return out


def kit_files(style):
    """The kits a style uses: common first, then the style (its `uses:` list pulls in others)."""
    seen, order = set(), []

    def add(name):
        if name in seen:
            return
        seen.add(name)
        p = os.path.join(KITS, f"{name}.yaml")
        k = load(p) if os.path.exists(p) else {}
        for u in k.get("uses") or []:
            add(u)
        order.append(name)
    add("common")
    add(style)
    return [k for k in order if os.path.exists(os.path.join(KITS, f"{k}.yaml"))]


def _pick(spec, rng, params):
    """A `choose` value: [lo, hi] -> uniform, {pick: [...]} -> one, {int: [lo, hi]} -> whole number,
    "=expr" -> computed, else as is."""
    if isinstance(spec, list) and len(spec) == 2 and all(isinstance(v, (int, float, str)) for v in spec) \
            and not any(isinstance(v, str) and not v.startswith("=") for v in spec):
        lo, hi = (float(M.evaluate(v, params)) for v in spec)
        return rng.uniform(min(lo, hi), max(lo, hi))
    if isinstance(spec, dict) and "pick" in spec:
        opts = M.evaluate(spec["pick"], params)
        w = M.evaluate(spec.get("weights"), params)
        return rng.choices(opts, weights=w)[0]
    if isinstance(spec, dict) and "int" in spec:
        lo, hi = (int(round(float(M.evaluate(v, params)))) for v in spec["int"])
        return rng.randint(min(lo, hi), max(lo, hi))
    return M.evaluate(spec, params)


def _expand(entries, params, rng, depth=0):
    """Resolve when / chance / pick / repeat and the object-kit generators into plain parts and
    `use:` entries (still unevaluated, except inside a repeat or a pick)."""
    out = []
    for e in entries or []:
        if "when" in e:
            if M.evaluate(e["when"], params):
                out += _expand(e.get("parts"), params, rng, depth + 1)
            elif "else" in e:
                out += _expand(e["else"], params, rng, depth + 1)
            continue
        if "chance" in e:
            if rng.random() < float(M.evaluate(e["chance"], params)):
                out += _expand(e.get("parts"), params, rng, depth + 1)
            elif "else" in e:
                out += _expand(e["else"], params, rng, depth + 1)
            continue
        if "pick" in e:
            opts = e["pick"]
            w = [float(M.evaluate(o.get("weight", 1), params)) for o in opts]
            o = rng.choices(opts, weights=w)[0]
            local = dict(params, **{k: _pick(v, rng, params) for k, v in (o.get("set") or {}).items()})
            out += [M.evaluate(p, local) for p in _expand(o.get("parts"), local, rng, depth + 1)]
            continue
        if "repeat" in e:
            n = int(M.evaluate(e["repeat"], params))
            for i in range(n):
                local = dict(params, i=i, n=n)
                out += [M.evaluate(p, local) for p in _expand(e.get("parts"), local, rng, depth + 1)]
            continue
        kind = next((k for k in G.GENERATORS if k in e), None)
        if kind is not None:
            spec = M.evaluate(e, params)
            g = dict(spec[kind])
            for key in ("mat", "name", "group"):
                if key in spec and key not in g:
                    g[key] = spec[key]
            out += G.GENERATORS[kind](g, rng)
            continue
        out.append(e)
    return out


def footprint_options(bp):
    fp = bp.get("footprint", [1, 1])
    if isinstance(fp[0], (list, tuple)):
        return [tuple(int(v) for v in f) for f in fp]
    return [tuple(int(v) for v in fp)]


def compose(path, seed, footprint=None, overrides=None):
    """(raw world-art model, params, info) for one seed of a blueprint. `footprint` (W, D) fixes the
    hit box; else one of the blueprint's options is picked per seed."""
    bp = load(path)
    style = bp["style"]
    rng = random.Random(f"{bp['name']}:{seed}")
    W, D = footprint or rng.choice(footprint_options(bp))
    fill = bool(bp.get("fill", False))
    margin = 0.0 if fill else MARGIN
    params = {"W": W, "D": D, "w_max": W - 2 * margin, "d_max": float(D), "seed": seed, "fill": fill}
    style_kit = {}
    materials = {}
    for k in kit_files(style):
        kit = load(os.path.join(KITS, f"{k}.yaml"))
        materials.update(kit.get("materials") or {})
        params.update({kk: v for kk, v in (kit.get("defaults") or {}).items() if kk not in params})
        style_kit = kit
    materials.update(bp.get("materials") or {})
    for k, v in (bp.get("choose") or {}).items():
        params[k] = _pick(v, rng, params)
    for k, v in (overrides or {}).items():
        params[k] = yaml.safe_load(v) if isinstance(v, str) else v
    parts = _expand(bp.get("parts"), params, rng)
    ground = _expand(bp.get("ground"), params, rng)
    render = {"light": [-0.55, -0.3, 0.78], "outline": False, "inner_lines": "none",
              "ao": {"strength": 0.0, "threshold": 0.3}, "margin": 0, "cleanup": True, "supersample": 3}
    render.update(style_kit.get("render") or {})
    render.update(M.evaluate(bp.get("render") or {}, params))
    tall = int(bp.get("drawn") or TALL)
    raw = {
        "name": f"{bp['name']}-{seed}",
        "palette": bp.get("palette", style_kit.get("palette", "greybox")),
        "kits": [f"{k}.yaml" for k in kit_files(style)],
        "cells": [W, tall],
        "foot": [W * 8, tall * 16 - 2],
        "footprint": tall,
        "seed": seed,
        "render": render,
        "materials": materials,
        "params": params,
        "parts": parts,
    }
    shadow = bp.get("drop_shadow", style_kit.get("drop_shadow", [{"dx": 1, "dy": 1, "color": "shade", "below": 2}]))
    if shadow:
        raw["drop_shadow"] = M.evaluate(shadow, params)
    gs = bp.get("ground_shadow")
    if gs:
        raw["ground_shadow"] = M.evaluate(gs, params)
    if ground:
        raw["ground"] = ground
    if bp.get("templates"):
        raw["templates"] = bp["templates"]
    info = {"blueprint": f"{style}/{bp['name']}", "name": bp["name"], "style": style, "seed": seed,
            "role": bp.get("role", "noise"), "W": W, "D": D, "fill": fill, "fixed_rows": bp.get("drawn"),
            "picked": {k: params[k] for k in (bp.get("choose") or {})}}
    return raw, params, info


def obj_from(raw):
    """A world-art Object; kits resolve from kits/ (a model path there that is never written)."""
    raw = copy.deepcopy(raw)
    return M.Object(os.path.join(KITS, f"{raw['name']}.yaml"), raw)


def fmt(v):
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)

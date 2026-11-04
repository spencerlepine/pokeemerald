"""A blueprint plus a seed becomes one world-art model (a dict), rendered by the world-art camera.

A blueprint (`blueprints/<style>/<name>.yaml`) is a family of buildings, not one building:

    name: block-house
    style: tatooine                 # kits/<style>.yaml: its materials and templates
    width: [4, 5, 6]                # cells; one is picked per seed (or fixed with --width)
    choose:                         # params picked per seed, in order; later ones may use earlier ones
      d: [1.8, 2.6]                 #   [lo, hi]: a number between
      roof: {pick: [flat, dome]}    #   pick: one of (weights: {pick: [...], weights: [...]})
      h: "=d * 0.6"                 #   an expression of earlier params
    parts:                          # world-art parts and `use:` templates, plus:
      - {use: adobe-block, with: {w: "=w", d: "=d", h: "=h"}}
      - {when: "=roof == 'dome'", parts: [...]}       # only when the expression is true
      - {chance: 0.5, parts: [...]}                   # on some seeds
      - {pick: [{weight: 2, parts: [...]}, {parts: [...]}]}   # one of these
      - {repeat: "=n", parts: [...]}                  # n times, with `i` (0..n-1) in scope

Params always in scope: `W` (cells wide), `w_max` (metres the building may use: W less a margin),
`H` (cells tall the catalog asks for, or 0 when free), `door_x` (metres east of the middle where the
catalog wants the door, or None: then the blueprint picks), `seed`. Name the door entry `door`, so the
build can find which cell column it is in. Axes: x east (0 = the middle of the sprite), y north (0 = the south wall's foot), z up,
1 m = 1 cell = 16 px. The sprite is W cells wide and as many cells tall as the art needs.
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

# blueprints may also use int() and float() in expressions
M.EXPR_ENV.update(int=int, float=float)

TALL = 9          # cells of canvas the render starts with; cropped to the art afterwards
MARGIN = 0.25     # metres kept clear on each side of the sprite


def load(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def blueprint_path(name):
    """`style/name` (always unique) or a bare name (the first style that has it)."""
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
        if name.startswith(style + "/"):
            p = os.path.join(BLUEPRINTS, f"{name}.yaml")
            if os.path.exists(p):
                return p
    raise SystemExit(f"no blueprint {name} in blueprints/<style>/")


def all_blueprints(style=None):
    out = []
    for s in sorted(os.listdir(BLUEPRINTS)):
        if style and s != style:
            continue
        d = os.path.join(BLUEPRINTS, s)
        out += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".yaml")]
    return out


def kit_files(style):
    """The kits a style uses: common first, then the style (its `uses:` list pulls in others)."""
    seen, order = set(), []

    def add(name):
        if name in seen:
            return
        seen.add(name)
        k = load(os.path.join(KITS, f"{name}.yaml"))
        for u in k.get("uses") or []:
            add(u)
        order.append(name)
    add("common")
    add(style)
    return order


def _pick(spec, rng, params):
    """A `choose` value: [lo, hi] -> uniform, {pick: [...]} -> one, "=expr" -> computed, else as is."""
    if isinstance(spec, list) and len(spec) == 2 and all(isinstance(v, (int, float, str)) for v in spec) \
            and not any(isinstance(v, str) and not v.startswith("=") for v in spec):
        lo, hi = (float(M.evaluate(v, params)) for v in spec)
        return rng.uniform(min(lo, hi), max(lo, hi))
    if isinstance(spec, dict) and "pick" in spec:
        opts = M.evaluate(spec["pick"], params)
        return rng.choices(opts, weights=spec.get("weights"))[0]
    if isinstance(spec, dict) and "int" in spec:          # {int: [lo, hi]}: a whole number, both ends in
        lo, hi = (int(round(float(M.evaluate(v, params)))) for v in spec["int"])
        return rng.randint(min(lo, hi), max(lo, hi))
    return M.evaluate(spec, params)


def _expand(entries, params, rng, depth=0):
    """Resolve when / chance / pick / repeat into plain parts and `use:` entries (still unevaluated)."""
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
            out += [_bind(p, local) for p in _expand(o.get("parts"), local, rng, depth + 1)]
            continue
        if "repeat" in e:
            n = int(M.evaluate(e["repeat"], params))
            for i in range(n):
                local = dict(params, i=i, n=n)
                out += [_bind(p, local) for p in _expand(e.get("parts"), local, rng, depth + 1)]
            continue
        out.append(e)
    return out


def _bind(part, params):
    """Evaluate a part now (inside a repeat or a pick, where `i` and `set` params exist), keeping the
    `with` of a template use for the template's own params."""
    return M.evaluate(part, params)


def compose(path, seed, width=None, overrides=None, height=None, door=None):
    """(raw world-art model, params, info) for one seed of a blueprint. `height` (cells) and `door`
    (cell column, 0 = west) are what a catalog entry asks for; the blueprint reads them as H, door_x."""
    bp = load(path)
    style = bp["style"]
    rng = random.Random(f"{bp['name']}:{seed}")
    widths = bp.get("width", [5])
    widths = widths if isinstance(widths, list) else [widths]
    W = int(width or rng.choice(widths))
    door_x = None if door is None else float(door) + 0.5 - W / 2
    params = {"W": W, "w_max": W - 2 * MARGIN, "H": int(height or 0), "door_x": door_x, "seed": seed}
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
    raw = {
        "name": f"{bp['name']}-{seed}",
        "palette": bp.get("palette", "greybox"),
        "kits": [f"{k}.yaml" for k in kit_files(style)],
        "cells": [W, TALL],
        "foot": [W * 8, TALL * 16 - 3],
        "footprint": TALL,
        "render": render,
        "materials": materials,
        "drop_shadow": [{"dx": 1, "dy": 1, "color": "shade", "below": 3}],
        "params": params,
        "parts": parts,
    }
    if ground:
        raw["ground"] = ground
    dx = None
    for e in parts:
        if e.get("name") == "door":
            at = M.evaluate(e.get("at", [0, 0, 0]), params)
            dx = float(at[0])
    info = {"blueprint": f"{style}/{bp['name']}", "name": bp["name"], "style": style, "seed": seed, "W": W,
            "door_col": None if dx is None else int(math.floor(dx + W / 2)),
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

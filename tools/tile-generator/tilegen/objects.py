"""Stage 3 prototypes: Tatooine objects built from primitives and rendered with the Emerald camera."""
from __future__ import annotations

import numpy as np

from . import raster as R


def vaporator(mats: dict) -> list[R.Mesh]:
    """GX-8 moisture vaporator: a tall thin shaft with three stacked fin rings and a boxy base.
    Footprint one cell (16 px), ~3 cells tall."""
    m = mats["durasteel"]; dark = mats["durasteel_dark"]
    parts = [
        R.box(10, 8, 6, dark, x=3, y=4, z=0),                      # base block
        R.cylinder(2.5, 40, m, cx=8, cy=8, z=6, segs=12),            # shaft
    ]
    for z in (14, 24, 34):
        parts.append(R.cylinder(6, 3, m, cx=8, cy=8, z=z, segs=16))       # fin ring
    parts.append(R.cylinder(4, 5, dark, cx=8, cy=8, z=46, segs=12))      # head
    return parts


def rock(mats: dict, w=28, d=18, h=14) -> list[R.Mesh]:
    m = mats["rock"]
    return [R.ellipsoid(w / 2, d / 2, h, m, cx=w / 2, cy=d / 2 + 2, cz=0, top_only=True, segs=48, rings=32)]


def scrub_tree(mats: dict) -> list[R.Mesh]:
    """A squat desert tree: short trunk, a lumpy canopy made of three overlapping spheres (2x3 cells)."""
    canopy, trunk = mats["canopy"], mats["trunk"]
    parts = [R.cylinder(2.5, 14, trunk, cx=16, cy=36, z=0, segs=10)]
    parts += [
        R.ellipsoid(14, 10, 11, canopy, cx=16, cy=30, cz=20, segs=48, rings=28),
        R.ellipsoid(10, 8, 8, canopy, cx=9, cy=26, cz=24, segs=40, rings=24),
        R.ellipsoid(10, 8, 8, canopy, cx=23, cy=26, cz=25, segs=40, rings=24),
    ]
    return parts


def homestead_dome(mats: dict, r=22) -> list[R.Mesh]:
    """Lars-style adobe dome with a square door block in front. ~3x3 cells."""
    adobe, door = mats["adobe"], mats["durasteel_dark"]
    cx, cy = r + 2, r + 6
    parts = [R.ellipsoid(r, r * 0.8, r * 0.75, adobe, cx=cx, cy=cy, cz=0, top_only=True, segs=64, rings=40),
             R.box(14, 6, 14, adobe, x=cx - 7, y=cy + r * 0.8 - 4, z=0),          # entry block
             R.box(8, 1, 12, door, x=cx - 4, y=cy + r * 0.8 + 1.5, z=0)]          # door face
    return parts


def crate(mats: dict) -> list[R.Mesh]:
    m = mats["durasteel"]
    return [R.box(14, 12, 10, m, x=1, y=2, z=0), R.box(14, 1.5, 2, mats["durasteel_dark"], x=1, y=7.5, z=10)]


CATALOG = {
    "vaporator": (vaporator, 16, 64),
    "rock": (rock, 32, 32),
    "scrub_tree": (scrub_tree, 32, 48),
    "homestead_dome": (homestead_dome, 48, 64),
    "crate": (crate, 16, 24),
}


def tatooine_materials() -> dict:
    """Prototype ramps (will come from the planet theme once it is in the wiki)."""
    return {
        "durasteel": R.ramp("durasteel", (168, 176, 184), 3, spread=16),
        "durasteel_dark": R.ramp("durasteel_dark", (96, 104, 112), 3, spread=14),
        "rock": R.ramp("rock", (184, 144, 104), 4, spread=14, smooth=True, highlight=True),
        "canopy": R.ramp("canopy", (152, 160, 88), 4, spread=14, smooth=True, hue_shift=-6, texture="scallop"),
        "trunk": R.ramp("trunk", (120, 88, 64), 3, spread=14),
        "adobe": R.ramp("adobe", (216, 184, 136), 4, spread=12, smooth=True, hue_shift=-5, highlight=True),
    }


def render_object(name: str, mats: dict | None = None):
    mats = mats or tatooine_materials()
    fn, w, h = CATALOG[name]
    meshes = fn(mats)
    # the world y=0..? : objects are modelled with their footprint at y in [0, d], z >= 0; the screen
    # shows y - z, so tall parts go up (negative). Put the screen origin so that the ground row y=d maps
    # to the bottom of the image: origin_y = (max footprint y) - h.
    foot = max(float(m.verts[:, 1].max()) for m in meshes)
    r = R.render(meshes, w, h, origin=(0.0, foot - h))
    R.texture(r)
    R.outline(r)
    R.highlight(r)
    return r

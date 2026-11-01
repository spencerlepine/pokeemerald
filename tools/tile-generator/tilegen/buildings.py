"""Stage 4: parametric buildings rendered with the Emerald camera.

A building is a footprint in cells, a wall height, and a roof. Everything is modelled in pixels
(16 px per cell) and rendered so the ground row of the footprint sits on a cell boundary.

Measured on the vanilla Littleroot house (Petalburg tileset, metatiles 520-584): 5 cells wide, 5 rows
tall on screen: upper roof 3 rows (back-slope ridge band ~12 px + front slope ~36 px), a lower porch
roof + wall top on row 4, the wall with door on row 5. Walls are ~24 px tall; the door is 16 wide,
24 tall; the roof tiles are staggered 8x4 bricks; the eave casts a 2-3 px dark line on the wall.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import raster as R

CELL = 16


@dataclass
class HouseSpec:
    w_cells: int = 5
    d_cells: int = 3           # footprint depth (plan)
    wall_h: int = 32
    roof_h: int = 12           # ridge height above the eave
    overhang: int = 4
    porch: bool = True         # a flat awning over the front wall (vanilla Littleroot's lower roof)
    porch_depth: int = 8
    porch_h: int = 3
    door_cell: int = 2         # cell index from the left for the door
    windows: tuple[int, ...] = (0, 4)
    roof_style: str = "gable"  # gable | flat | dome
    name: str = "house"


def house(spec: HouseSpec, mats: dict) -> list[R.Mesh]:
    W, D = spec.w_cells * CELL, spec.d_cells * CELL
    wall, roof, trim, door, glass, frame = (mats[k] for k in ("wall", "roof", "trim", "door", "glass", "frame"))
    parts: list[R.Mesh] = []
    # walls: a box; the plan top of the box is hidden by the roof
    parts.append(R.box(W, D, spec.wall_h, wall, x=0, y=0, z=0))
    o = spec.overhang
    if spec.roof_style == "gable":
        parts.append(R.gable_roof(W, D, spec.roof_h, roof, x=0, y=0, z=spec.wall_h, overhang=o))
        # fascia: a thin dark strip under the front eave (the eave shadow line)
        parts.append(R.box(W + 2 * o, 1.5, 2.5, trim, x=-o, y=D + o - 1.5, z=spec.wall_h - 0.5))
    elif spec.roof_style == "flat":
        parts.append(R.box(W + 2 * o, D + 2 * o, 3, roof, x=-o, y=-o, z=spec.wall_h))
        parts.append(R.box(W + 2 * o, 1.5, 2.5, trim, x=-o, y=D + o - 1.5, z=spec.wall_h))
    elif spec.roof_style == "dome":
        parts.append(R.ellipsoid(W / 2 + o, D / 2 + o, spec.roof_h, roof, cx=W / 2, cy=D / 2, cz=spec.wall_h, top_only=True, segs=64, rings=40))
    if spec.porch:
        # a flat awning slab hanging off the front wall just under the eave, with a dark front edge
        pz = spec.wall_h - spec.porch_h - 2
        parts.append(R.box(W + 2 * o, spec.porch_depth, spec.porch_h, roof, x=-o, y=D + o - spec.porch_depth, z=pz))
        parts.append(R.box(W + 2 * o, 1.0, 2.0, trim, x=-o, y=D + o - 1.0, z=pz - 2.0))
    # corner posts and a dark base line on the front wall (vanilla houses frame the wall)
    parts.append(R.box(2, 1.0, spec.wall_h - 1, trim, x=0, y=D, z=0))
    parts.append(R.box(2, 1.0, spec.wall_h - 1, trim, x=W - 2, y=D, z=0))
    parts.append(R.box(W, 1.0, 1.0, trim, x=0, y=D, z=0))
    # door: a recessed-looking slab on the front wall, 16 wide and 24 tall, cell-aligned
    dx = spec.door_cell * CELL
    dh = min(spec.wall_h - 8, 24)
    parts.append(R.box(CELL - 2, 1.0, dh, door, x=dx + 1, y=D, z=0))
    parts.append(R.box(CELL, 1.2, 1.5, frame, x=dx, y=D, z=dh))          # lintel
    # windows: 12x8 glass with a 1 px frame, sill at z=8
    for wc in spec.windows:
        wx = wc * CELL + 2
        parts.append(R.box(12, 1.2, 10, frame, x=wx, y=D, z=10))
        parts.append(R.box(10, 1.4, 8, glass, x=wx + 1, y=D, z=11))
    return parts


def render_house(spec: HouseSpec, mats: dict) -> R.Render:
    meshes = house(spec, mats)
    W = spec.w_cells * CELL + 2 * spec.overhang
    foot = max(float(m.verts[:, 1].max()) for m in meshes)
    top = min(float((m.verts[:, 1] - m.verts[:, 2]).min()) for m in meshes)
    H = int(np.ceil((foot - top) / CELL)) * CELL
    # screen origin so the footprint's front edge (y = D) sits on the bottom cell boundary
    r = R.render(meshes, W, H, origin=(-spec.overhang, foot - H))
    R.texture(r)
    R.outline(r)
    R.highlight(r)
    return r


def tatooine_house_materials() -> dict:
    return {
        "wall": R.ramp("adobe_wall", (224, 200, 160), 3, spread=14, hue_shift=-4),
        "roof": R.ramp("clay_roof", (200, 136, 96), 4, spread=13, hue_shift=-8, texture="rooftile"),
        "trim": R.ramp("trim", (96, 80, 80), 3, spread=10),
        "door": R.ramp("door", (144, 104, 64), 3, spread=14, texture="plank"),
        "glass": R.Material("glass", [(136, 208, 232), (96, 168, 208)], emissive=False, thresholds=(0.5,)),
        "frame": R.ramp("frame", (120, 112, 120), 3, spread=12),
    }


def hoenn_house_materials() -> dict:
    """Vanilla-like colours, to compare geometry against the Littleroot house."""
    return {
        "wall": R.Material("wall", [(238, 230, 205), (213, 205, 148), (172, 139, 123)]),
        "roof": R.Material("roof", [(255, 230, 180), (246, 164, 131), (205, 139, 106), (123, 90, 90)], texture="rooftile"),
        "trim": R.Material("trim", [(98, 98, 123), (65, 74, 106), (41, 49, 90)]),
        "door": R.Material("door", [(222, 172, 115), (189, 139, 115), (156, 106, 115)], texture="plank"),
        "glass": R.Material("glass", [(156, 205, 246), (98, 156, 238)], thresholds=(0.5,)),
        "frame": R.Material("frame", [(131, 131, 139), (98, 98, 123), (65, 74, 106)]),
    }

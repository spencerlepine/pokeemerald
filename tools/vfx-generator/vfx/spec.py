"""Specs (art/<name>.yaml) -> game-ready sheets.

A spec names the sheet it replaces (or describes a new one), the palette as ramps, and the ops that draw
each frame. The tool supplies everything the game dictates (sheet size, frame size, frame slots, tile
order, which palette is locked) from the catalog, so a spec only says what the effect looks like.

    name: ion_cannon
    replaces: graphics/battle_anims/sprites/black_ball_2.png
    palette: {mode: new, transparent: "#000000", ramps: {ion: ["#F8F8F8", "#A8E8F8", "#58C8F8", "#2878D0"]}}
    ops:
      - disc: {cx: 8, cy: 8, r: 6.5, ramp: ion, light: [-0.3, -0.3]}

See README.md for every key.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

from . import catalog, ops
from .draw import Canvas
from .game import GAME, OUT
from .pal import Palette, build as build_palette
from .sheet import indexed_image, join_frames, read_indexed, split_frames


@dataclass
class Built:
    spec: dict
    entry: dict
    pal: Palette
    frames: list[np.ndarray]
    slots: list[int]
    sheet: np.ndarray
    size: tuple[int, int]
    frame: tuple[int, int]
    out_dir: Path
    png: Path
    notes: list[str] = field(default_factory=list)


def load_spec(path: str | Path) -> dict:
    p = Path(path)
    spec = yaml.safe_load(p.read_text())
    spec.setdefault("name", p.stem)
    spec["_path"] = str(p)
    return spec


def entry_for(spec: dict) -> dict:
    if spec.get("replaces"):
        return catalog.find(spec["replaces"])
    new = spec.get("new")
    if not new:
        raise ValueError("a spec needs `replaces:` (a vanilla sheet) or `new:` {path, size, frame}")
    size = list(new["size"])
    frame = list(new.get("frame", size))
    return {"id": new["path"].replace("graphics/", "").removesuffix(".png"), "path": new["path"], "kind": new.get("kind", "new"),
            "group": new.get("group", "new"), "size": size, "frame": frame,
            "frame_slots": (size[0] * size[1]) // (frame[0] * frame[1]), "mwidth": new.get("mwidth", 1),
            "mheight": new.get("mheight", 1), "palette": {"kind": "own", "source": None, "touched_by": []},
            "templates": [], "users": [], "frames_used": list(range((size[0] * size[1]) // (frame[0] * frame[1]))),
            "exists": False, "new": True}


def build(spec: dict, out_root: Path = OUT) -> Built:
    entry = entry_for(spec)
    size = tuple(spec.get("size", entry["size"]))
    frame = tuple(spec.get("frame", entry["frame"]))
    slots_total = (size[0] // 8) * (size[1] // 8) // ((frame[0] // 8) * (frame[1] // 8))
    notes: list[str] = []

    vpath = entry["path"] if entry.get("exists") else None
    pspec = spec.get("palette") or {"mode": "vanilla"}
    if pspec.get("mode") in ("locked", "vanilla") and not pspec.get("source"):
        src = entry.get("palette", {}).get("source") or vpath
        pspec = dict(pspec, source=src)
    pal = build_palette(pspec, vpath)
    pk = entry.get("palette", {})
    if pk.get("shared_with_tags") and pspec.get("mode") == "new":
        notes.append(f"WARNING palette is shared with {', '.join(pk['shared_with_tags'])}: a new palette recolours those "
                     f"sprites too. Use mode: locked, or redraw them in the same build.")
    if pk.get("kind") in ("player", "shared") and pspec.get("mode") == "new":
        notes.append(f"WARNING this sheet is drawn with a {pk['kind']} bank ({pk.get('source')}); a new palette will not "
                     f"reach the game. Use mode: locked with that source.")
    if pk.get("touched_by"):
        notes.append("NOTE the game changes this palette at runtime (" + "; ".join(pk["touched_by"][:3]) +
                     "): keep bright/dark index order similar to vanilla so the flash still reads.")

    want = spec.get("frames")
    if want is None:
        slots = list(range(slots_total))
    elif isinstance(want, int):
        slots = list(range(want))
    else:
        slots = [int(x) for x in want]
    n = len(slots)

    base_pix = None
    if entry.get("exists") and spec.get("keep_vanilla", True):
        bp, bcols = read_indexed(GAME / entry["path"])
        if bp.shape == (size[1], size[0]):
            base_pix = bp
            if not pal.locked or [tuple(c) for c in bcols[:16]] != [tuple(c) for c in pal.colours[:16]]:
                # vanilla pixels on a different palette would show wrong colours: clear the slack instead
                base_pix = np.zeros_like(bp) if not spec.get("keep_vanilla_pixels") else bp

    built_frames: list[np.ndarray] = []
    by_slot: dict[int, np.ndarray] = {}
    per_frame = spec.get("frame_ops") or {}
    for k, slot in enumerate(slots):
        cv = Canvas(frame[0], frame[1], pal)
        ctx = {"t": k / (n - 1) if n > 1 else 0.0, "i": k, "n": n, "slot": slot, "seed": spec.get("seed", 0),
               "W": frame[0], "H": frame[1], "cx": frame[0] / 2, "cy": frame[1] / 2}
        ctx.update(ops.ev(spec.get("vars") or {}, ctx))
        ops.run(cv, spec.get("ops"), ctx, built_frames)
        ops.run(cv, per_frame.get(k) or per_frame.get(str(k)), ctx, built_frames)
        built_frames.append(cv.pix)
        by_slot[slot] = cv.pix

    # place frames into their slots, through the tile order
    if base_pix is not None:
        all_frames = split_frames(base_pix, frame[0], frame[1], entry.get("mwidth", 1), entry.get("mheight", 1), slots_total)
    else:
        all_frames = [np.zeros((frame[1], frame[0]), np.uint8) for _ in range(slots_total)]
    for s, f in by_slot.items():
        if s < len(all_frames):
            all_frames[s] = f
    sheet = join_frames(all_frames, size, entry.get("mwidth", 1), entry.get("mheight", 1), base=base_pix)

    out_dir = out_root / spec["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / Path(entry["path"]).name
    indexed_image(sheet, pal.colours[:16]).save(png, bits=4, optimize=False)
    b = Built(spec, entry, pal, built_frames, slots, sheet, size, frame, out_dir, png, notes)
    (out_dir / "build.json").write_text(json.dumps({
        "name": spec["name"], "replaces": entry["path"], "png": png.name, "size": size, "frame": frame,
        "slots": slots, "palette": [list(c) for c in pal.colours[:16]], "ramps": pal.ramps,
        "palette_locked": pal.locked, "notes": notes}, indent=1))
    return b

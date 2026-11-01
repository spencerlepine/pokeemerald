"""Trainer back pic spec files (YAML) -> four indexed 64x64 frames (the capture-pod throw).

A spec is what the LLM writes. It never contains RGB: every character maps to a palette
*index* through `legend`, so the output cannot leave the palette.

Every back pic is a repaint of a vanilla back pic strip (D2): `repaint:` copies all four
vanilla frames with every vanilla palette index remapped to one of our legend characters, then
`layers:` kitbash them (erase, recolour, graft, move, rows, cols, small shaded parts, `pixels`,
`edge`; see rig.py). Each layer runs on every frame unless it names `frames:`, and
`shift: {frame: [dx, dy]}` moves it on the frames where the body has moved (the head dips on
the wind-up, the arm swings through on the throw):

    name: kael_back
    kit: trainerback64x4
    replaces: graphics/trainers/back_pics/brendan.png
    palette: [[115, 197, 164], ...]     # the SAME 16 colours as the front pic (shared palette)
    legend: {'.': 0, K: 1, ...}
    repaint: {pic: graphics/trainers/back_pics/brendan.png, remap: {1: a, 2: b, ...}}
    layers:
      - {name: cap, shape: poly, pts: [...], erase: true}
      - {name: headband, shape: pixels, x: 20, y: 10, rows: "...", shift: {2: [3, 1]}}
      - {name: pod, shape: pixels, frames: [0], x: 2, y: 30, rows: "..."}
    patches:                              # per frame, `_` keeps the pixel underneath
      2: [{x: 50, y: 12, rows: "KK"}]
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import rig as rig_mod

KITS = {
    # Emerald's own back pics (Brendan, May, Wally, Steven): four 64x64 frames stacked in one
    # 64x256 PNG, played by src/data/trainer_graphics/back_pic_anims.h as
    # 0 (24 ticks), 1 (9), 2 (24), 0 (9), 3 (50): idle, wind-up, throw, idle, follow-through.
    "trainerback64x4": {
        "frame": (64, 64),
        "order": ["idle", "windup", "throw", "follow"],
        "anim": [(0, 24), (1, 9), (2, 24), (0, 9), (3, 50)],
    },
}

Grid = list[list[int]]


@dataclass
class Spec:
    name: str
    kit: str
    palette: list
    legend: dict[str, int]
    frames: list[Grid]
    path: Path
    replaces: str | None = None
    front: str | None = None
    meta: dict = field(default_factory=dict)

    @property
    def w(self) -> int:
        return KITS[self.kit]["frame"][0]

    @property
    def h(self) -> int:
        return KITS[self.kit]["frame"][1]


class SpecError(ValueError):
    pass


def load_strip(rel: str) -> Grid:
    """A vanilla pic's palette-index grid (whole strip), relative to EMERALD_DIR."""
    from PIL import Image

    from .cli import emerald_dir

    src = emerald_dir() / rel
    if not src.exists():
        raise SpecError(f"pic {src} not found (set EMERALD_DIR)")
    im = Image.open(src)
    if im.mode != "P":
        raise SpecError(f"{src} is not an indexed PNG")
    px = im.load()
    return [[px[x, y] for x in range(im.width)] for y in range(im.height)]


def _frame_loader(frame: int):
    """graft source loader for one frame: a back pic strip gives the same frame of that strip
    (or `frame_of:` in the layer picks another), a 64x64 front pic is used whole."""

    def load(rel: str, layer=None) -> Grid:
        g = load_strip(rel)
        if len(g) > 64:
            f = frame if layer is None or "src_frame" not in layer else int(layer["src_frame"])
            return g[f * 64 : f * 64 + 64]
        return g

    return load


def _repaint(rp: dict, legend: dict[str, int], n: int, where: str) -> list[Grid]:
    g = load_strip(rp["pic"])
    if len(g[0]) != 64 or len(g) < 64 * n:
        raise SpecError(f"{where}: repaint pic must be a 64-wide strip of at least {n} frames")
    remap = {int(k): str(v) for k, v in (rp.get("remap") or {}).items()}
    used = {v for row in g[: 64 * n] for v in row} - {0}
    missing = sorted(used - set(remap))
    if missing:
        raise SpecError(f"{where}: repaint remap is missing vanilla indices {missing}")
    for k, ch in remap.items():
        if ch not in legend:
            raise SpecError(f"{where}: repaint remap {k} -> {ch!r}: not in the legend")
    ox, oy = rp.get("offset", [0, 0])
    order = rp.get("frames", list(range(n)))  # which vanilla frame feeds each of ours
    out = []
    for f in range(n):
        src = g[order[f] * 64 : order[f] * 64 + 64]
        fr = [[0] * 64 for _ in range(64)]
        for y in range(64):
            for x in range(64):
                v = src[y][63 - x if rp.get("flip") else x]
                tx, ty = x + int(ox), y + int(oy)
                if v and 0 <= tx < 64 and 0 <= ty < 64:
                    fr[ty][tx] = legend[remap[v]]
        out.append(fr)
    return out


def shift_layer(layer: dict, dx: int, dy: int) -> dict:
    """The same layer moved by (dx, dy), whatever its shape."""
    if not (dx or dy):
        return layer
    L = dict(layer)
    op = L.get("shape")
    if op == "pixels":
        L["x"], L["y"] = int(L["x"]) + dx, int(L["y"]) + dy
    elif op == "graft":
        ax, ay = L.get("at", L["box"][:2])
        L["at"] = [int(ax) + dx, int(ay) + dy]
    elif op == "move":
        b = list(L["box"])
        L["box"] = [b[0] + dx, b[1] + dy, b[2], b[3]]
    elif op == "rows":
        L["at"] = int(L["at"]) + dy
        if "x" in L:
            L["x"] = [L["x"][0] + dx, L["x"][1] + dx]
    elif op == "cols":
        L["at"] = int(L["at"]) + dx
        if "y" in L:
            L["y"] = [L["y"][0] + dy, L["y"][1] + dy]
    elif op in ("edge", "fringe", "speckle"):
        if "box" in L:
            b = list(L["box"])
            L["box"] = [b[0] + dx, b[1] + dy, b[2], b[3]]
    elif op == "trim":
        b = list(L["box"])
        L["box"] = [b[0] + dx, b[1] + dy, b[2], b[3]]
        L["keep"] = shift_layer(L["keep"], dx, dy)
    else:
        ox, oy = L.get("offset", [0, 0])
        L["offset"] = [ox + dx, oy + dy]
    return L


def load(path: str | Path) -> Spec:
    path = Path(path)
    d = yaml.safe_load(path.read_text())
    kit = d.get("kit", "trainerback64x4")
    if kit not in KITS:
        raise SpecError(f"unknown kit {kit!r}; known: {', '.join(KITS)}")
    n = len(KITS[kit]["order"])
    legend = {str(k): int(v) for k, v in d["legend"].items()}
    for ch, idx in legend.items():
        if len(ch) != 1 or not 0 <= idx <= 15:
            raise SpecError(f"legend entry {ch!r}: {idx} must be one character -> index 0..15")
    pal = d["palette"]
    if not (isinstance(pal, list) and 2 <= len(pal) <= 16 and all(len(c) == 3 and all(0 <= v <= 255 for v in c) for c in pal)):
        raise SpecError("palette: 2-16 entries of [r, g, b], 0-255")
    if "repaint" not in d:
        raise SpecError("a back pic is a `repaint:` of a vanilla back pic strip (D2)")
    frames = _repaint(d["repaint"], legend, n, "repaint")
    layers = d.get("layers") or []
    for f in range(n):
        mine = []
        for L in layers:
            fl = L.get("frames")
            if fl is not None and f not in fl:
                continue
            dx, dy = (L.get("shift") or {}).get(f, [0, 0])
            L2 = shift_layer({k: v for k, v in L.items() if k not in ("frames", "shift")}, int(dx), int(dy))
            mine.append(L2)
        try:
            frames[f] = rig_mod.render({"layers": mine}, legend, 64, 64, f"frame {f}", base=frames[f],
                                       load_pic=_frame_loader(f))
        except rig_mod.RigError as e:
            raise SpecError(str(e)) from None
        for i, pt in enumerate((d.get("patches") or {}).get(f, []) or []):
            px, py = int(pt["x"]), int(pt["y"])
            for dy, ln in enumerate(pt["rows"].strip("\n").split("\n")):
                for dx, ch in enumerate(ln.strip()):
                    if ch == "_":
                        continue
                    if ch not in legend:
                        raise SpecError(f"frame {f}: patch {i}: character {ch!r} is not in the legend")
                    if 0 <= px + dx < 64 and 0 <= py + dy < 64:
                        frames[f][py + dy][px + dx] = legend[ch]
    return Spec(name=d["name"], kit=kit, palette=pal, legend=legend, frames=frames, path=path,
                replaces=d.get("replaces"), front=d.get("front"), meta=d)


def palette16(spec: Spec) -> list[tuple[int, int, int]]:
    cols = [tuple(int(v) for v in c) for c in spec.palette]
    return cols + [(0, 0, 0)] * (16 - len(cols))

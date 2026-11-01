"""Palettes as named ramps.

A spec never picks raw colours per pixel: it names ramps (light -> dark lists of palette indices) and the
drawing ops pick a step on a ramp. That is how the vanilla effects are built (a white or pale core, two
or three saturated steps, a dark rim colour), and it keeps every pixel on a known index, so the palette
gate is a formality and locked banks (shared tags, the player bank) work the same way as new ones.

Three ways to get a palette:
  new     - ramps given as hex colours; indices are assigned in order after index 0.
  locked  - a vanilla .pal / PNG palette is kept index for index; ramps name existing indices.
  vanilla - the sheet's own vanilla palette (shorthand for locked on the file being replaced).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from gba_palette import core

from .game import GAME, HERE
from .sheet import read_indexed

Colour = tuple[int, int, int]


def snap(c: Colour) -> Colour:
    return core.snap(c)


def luma(c: Colour) -> float:
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def parse_colour(v) -> Colour:
    if isinstance(v, (list, tuple)):
        return tuple(int(x) for x in v[:3])
    return core.parse_hex(str(v))


def load_palette_file(path: str | Path) -> list[Colour]:
    p = Path(path)
    if not p.is_absolute():
        for root in (GAME, HERE):
            if (root / p).exists():
                p = root / p
                break
    if p.suffix == ".pal":
        cols = core.load_jasc(p)
    else:
        _, cols = read_indexed(p)
    cols = list(cols[:16])
    while len(cols) < 16:
        cols.append((0, 0, 0))
    return cols


@dataclass
class Palette:
    colours: list[Colour]
    ramps: dict[str, list[int]] = field(default_factory=dict)
    locked: bool = False
    source: str | None = None

    def ramp(self, name) -> list[int]:
        if isinstance(name, int):
            return [name]
        if isinstance(name, list):
            return [int(x) for x in name]
        if name not in self.ramps:
            raise KeyError(f"no ramp named {name!r}; ramps: {', '.join(self.ramps)}")
        return self.ramps[name]

    def index(self, ref) -> int:
        """'ion' -> first (lightest) step; 'ion.2' -> third step; 7 -> index 7."""
        if isinstance(ref, int):
            return ref
        s = str(ref)
        if s.isdigit():
            return int(s)
        if "." in s:
            name, k = s.rsplit(".", 1)
            r = self.ramp(name)
            k = int(k)
            return r[max(-len(r), min(len(r) - 1, k))]
        return self.ramp(s)[0]

    def luma_of(self, i: int) -> float:
        return luma(self.colours[i])

    def used_count(self) -> int:
        return len({i for r in self.ramps.values() for i in r})


def build(spec: dict, vanilla_path: str | None = None) -> Palette:
    """spec['palette'] -> Palette."""
    ps = spec or {}
    mode = ps.get("mode", "new")
    if mode in ("locked", "vanilla"):
        src = ps.get("source") or vanilla_path
        if not src:
            raise ValueError("palette mode locked/vanilla needs a source (or a sheet to replace)")
        cols = load_palette_file(src)
        ramps = {k: [int(x) for x in v] for k, v in (ps.get("ramps") or {}).items()}
        # colour overrides on a locked bank are only legal on the sheet's own (unshared) palette
        for i, c in (ps.get("set") or {}).items():
            cols[int(i)] = snap(parse_colour(c))
        return Palette(cols, ramps, locked=not ps.get("set"), source=str(src))
    cols: list[Colour] = [snap(parse_colour(ps.get("transparent", "#000000")))]
    ramps: dict[str, list[int]] = {}
    for name, hexes in (ps.get("ramps") or {}).items():
        idx = []
        for h in hexes:
            c = snap(parse_colour(h))
            if c in cols[1:]:
                idx.append(cols.index(c, 1))
            else:
                cols.append(c)
                idx.append(len(cols) - 1)
        ramps[name] = idx
    if len(cols) > 16:
        raise ValueError(f"palette has {len(cols) - 1} visible colours; a 4bpp bank holds 15")
    while len(cols) < 16:
        cols.append((0, 0, 0))
    return Palette(cols, ramps, locked=False, source=None)

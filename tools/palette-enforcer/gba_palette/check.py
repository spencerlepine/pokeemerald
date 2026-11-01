"""The gate: does a PNG (or .pal) obey layer 1 (hardware) and, if asked, layer 2 (theme / shared palette)?

Returns errors (must fix before install) and warnings (look at it). A tool's post-processing calls
`check_png` on everything it writes and refuses to install on any error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from . import core
from .core import Colour


@dataclass
class Report:
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def lines(self) -> list[str]:
        head = f"{'OK  ' if self.ok else 'FAIL'} {self.path}"
        if self.info:
            head += "  (" + ", ".join(f"{k} {v}" for k, v in self.info.items()) + ")"
        return [head] + [f"  error: {e}" for e in self.errors] + [f"  warn:  {w}" for w in self.warnings]


def _palette(im: Image.Image) -> list[Colour]:
    flat = im.getpalette() or []
    return [tuple(flat[i : i + 3]) for i in range(0, len(flat), 3)]


def _step_rule(rep: Report, used: dict[int, Colour], strict: bool) -> None:
    off = [(i, c) for i, c in used.items() if i != 0 and not core.on_step(c)]
    if off:
        msg = "colours not on a GBA step (shift in game): " + ", ".join(
            f"[{i}] {core.hex_of(c)}->{core.hex_of(core.truncate(c))}" for i, c in off[:8]
        ) + (" ..." if len(off) > 8 else "")
        (rep.errors if strict else rep.warnings).append(msg)
    seen: dict[int, list[int]] = {}
    for i, c in used.items():
        if i != 0:
            seen.setdefault(core.bgr555(c), []).append(i)
    dupes = [ix for ix in seen.values() if len(ix) > 1]
    if dupes:
        rep.warnings.append("entries that are the same GBA colour (slots wasted): "
                            + ", ".join("/".join(map(str, ix[:6])) + ("/..." if len(ix) > 6 else "") for ix in dupes[:6])
                            + (f" (+{len(dupes) - 6} more groups)" if len(dupes) > 6 else ""))


def check_png(
    path: str | Path,
    *,
    bpp: int | None = None,
    pal: list[Colour] | None = None,
    theme: list[Colour] | None = None,
    strict_theme: bool = False,
    tolerance: float = 12.0,
    strict_step: bool = True,
    tile: bool = False,
) -> Report:
    path = Path(path)
    rep = Report(str(path))
    im = Image.open(path)
    depth = core.png_bit_depth(path)
    if im.mode in ("L", "1") and depth in core.VISIBLE:
        # Greyscale PNGs (fonts, masks, some vanilla UI): gbagfx reads the grey level as the pixel
        # index and the colours come from a .pal loaded elsewhere. Only the index range can be checked.
        levels = sorted(set(im.convert("L").getdata()))
        rep.info = {"bpp": depth, "grey levels": f"{len(levels)}/{1 << depth}"}
        if bpp and depth > bpp:
            rep.errors.append(f"PNG is {depth}-bit but the target is {bpp}bpp")
        rep.warnings.append("greyscale PNG: indices only, its colours come from a separate .pal")
        return rep
    if im.mode != "P":
        rep.errors.append(f"not an indexed PNG (mode {im.mode}); run `enforce` first")
        return rep
    bpp = bpp or depth
    if bpp not in core.VISIBLE:
        rep.errors.append(f"unsupported bit depth {bpp}")
        return rep
    if depth > bpp:
        rep.errors.append(f"PNG is {depth}-bit but the target is {bpp}bpp")
    colours = _palette(im)
    used_idx = [i for i, n in enumerate(im.histogram()) if n]
    if used_idx and max(used_idx) > core.VISIBLE[bpp]:
        rep.errors.append(f"pixel index {max(used_idx)} used; {bpp}bpp allows 0-{core.VISIBLE[bpp]}")
    used = {i: colours[i] for i in used_idx if i < len(colours)}
    visible = [i for i in used if i != 0]
    rep.info = {"bpp": bpp, "colours": f"{len(visible)}/{core.VISIBLE[bpp]}"}
    if len(visible) > core.VISIBLE[bpp]:
        rep.errors.append(f"{len(visible)} colours used; {bpp}bpp holds {core.VISIBLE[bpp]} + transparent")
    if bpp == 1:
        return rep  # 1bpp has no palette of its own (footprints, fonts): ink or empty
    if pal is None:  # a locked palette is checked as its own file (check_pal), not per image
        _step_rule(rep, used, strict_step)
    if tile and (im.width % 8 or im.height % 8):
        rep.errors.append(f"size {im.width}x{im.height} is not a multiple of 8 (tiles are 8x8)")
    if pal is not None:
        bad = [i for i in visible if i >= len(pal) or core.truncate(pal[i]) != core.truncate(used[i])]
        if bad:
            rep.errors.append(
                "pixels use indices whose colour differs from the locked palette: "
                + ", ".join(f"[{i}] {core.hex_of(used[i])}" + (f" != {core.hex_of(pal[i])}" if i < len(pal) else " (beyond palette)") for i in bad[:8])
            )
    if theme:
        cols = [used[i] for i in visible]
        if cols:
            j, d = core.nearest(cols, theme)
            off = [(i, used[i], theme[k], dist) for i, k, dist in zip(visible, j, d) if dist > tolerance + 1e-6]
            if off:
                msg = f"{len(off)} of {len(visible)} colours are off-theme: " + ", ".join(
                    f"[{i}] {core.hex_of(c)} (nearest {core.hex_of(t)}, dE {dist:.0f})" for i, c, t, dist in off[:6]
                ) + (" ..." if len(off) > 6 else "")
                (rep.errors if strict_theme else rep.warnings).append(msg)
            rep.info["on-theme"] = f"{len(visible) - len(off)}/{len(visible)}"
    return rep


def check_pal(path: str | Path, *, strict_step: bool = True) -> Report:
    rep = Report(str(path))
    try:
        cols = core.load_jasc(path)
    except ValueError as e:
        rep.errors.append(str(e))
        return rep
    rep.info = {"entries": len(cols)}
    if len(cols) > 16 and len(cols) % 16:
        rep.errors.append(f"{len(cols)} entries; a file holds whole 16-colour banks (16, 32, ... 256)")
    if len(cols) < 16:
        rep.warnings.append(f"{len(cols)} entries; game palettes are written with 16")
    _step_rule(rep, dict(enumerate(cols)), strict_step)
    return rep

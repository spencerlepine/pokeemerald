"""Sprite spec files (YAML) -> indexed frames.

A spec is what the LLM writes. It never contains RGB: every character in a grid maps to a
palette *index* through `legend`, so the output cannot leave the palette.

Grids are 16 characters wide and BOTTOM-anchored: the last line of a grid is row 31 of the
frame. Write the stand frames with an empty last line so the feet land on row 30, as every
Emerald walker does.

Step frames are usually derived, not redrawn (a step is ~20% of the pixels):

    down_a:
      base: down        # start from this frame
      shift: 1          # move everything down 1 px (Emerald's step bob)
      patch_y: 24       # replace rows from here down with `rows`
      rows: |
        ...
    down_b:
      mirror_of: down_a # horizontal mirror of another frame

Front-facing art is mostly symmetric, so a frame can be drawn as its left half and mirrored:

    front:
      half: |           # lines are right-aligned to the centre line and may be shorter than
        ....KKKK        #   w/2 (missing pixels on the left are transparent)
      mirror_shade: "h:m m:d"  # optional: recolour the mirrored half (light from the left)
      patches:          # then redraw the asymmetric parts; `_` keeps the pixel underneath
        - {x: 20, y: 30, rows: "KK_K"}

`palette:` is the name of a shared NPC palette file in palettes/; index 0 is transparent.

Composing from vanilla art (STYLE.md section 6), the default way to make a generic NPC:

    base_sheet: graphics/object_events/pics/people/youngster.png   # all 9 frames start here
    recolor: {8: 11, 9: 12, 10: 13}        # index remap over the whole base sheet
    parts:                                 # regions taken from other vanilla sheets, per frame
      - sheet: graphics/object_events/pics/people/hiker.png
        rows: [11, 20]                     # rows of that sheet's facing-down frame (inclusive);
        recolor: {5: 8, 6: 9, 7: 10}       #   each frame's own bob is followed automatically
        dx: 0                              # optional horizontal shift
        frames: [down, down_a, down_b]     # optional: only these frames (default: all 9)
    frames:                                # optional; a frame given only as `patches:` starts
      down:                                #   from the composed frame
        patches:
          - {x: 3, y: 12, rows: "..KK.."}

A patch character `_` keeps the pixel underneath.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Frame layout of sAnimTable_Standard (src/data/object_events/object_event_anims.h):
# 0 face down, 1 face up, 2 face left, 3/4 walk down, 5/6 walk up, 7/8 walk left.
# East is frame 2/7/8 drawn with hFlip, so there is no right-facing art.
KITS = {
    "person16x32": {
        "frame": (16, 32),
        "order": ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"],
        "stand": ["down", "up", "left"],
        "walk": {  # direction -> (step, stand, step, stand) as sAnim_Go* plays it
            "down": ["down_a", "down", "down_b", "down"],
            "up": ["up_a", "up", "up_b", "up"],
            "left": ["left_a", "left", "left_b", "left"],
        },
        "size": 256,  # .size in ObjectEventGraphicsInfo (bytes per frame at 4bpp)
        "oam": "16x32",
    },
    # Stand-only people: gym leaders, Elite Four and other NPCs that never walk ship a 48x32 sheet
    # (down, up, left); their pic table points every step frame at a stand frame.
    "person16x32_still": {
        "frame": (16, 32),
        "order": ["down", "up", "left"],
        "stand": ["down", "up", "left"],
        "walk": {"down": ["down"] * 4, "up": ["up"] * 4, "left": ["left"] * 4},
        "size": 256,
        "oam": "16x32",
        "still": True,
    },
    # Multi-tile walkers: same nine frames, 32x32 each (sheet 288x32), as the Mach/Acro bike
    # sheets and the 32x32 legendaries use. graphics_info needs .size = 512, .width/.height = 32,
    # .oam = &gObjectEventBaseOam_32x32, .subspriteTables = sOamTables_32x32.
    "person32x32": {
        "frame": (32, 32),
        "order": ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"],
        "stand": ["down", "up", "left"],
        "walk": {
            "down": ["down_a", "down", "down_b", "down"],
            "up": ["up_a", "up", "up_b", "up"],
            "left": ["left_a", "left", "left_b", "left"],
        },
        "size": 512,
        "oam": "32x32",
    },
}

Grid = list[list[int]]


@dataclass
class Spec:
    name: str
    kit: str
    palette: str | list
    legend: dict[str, int]
    frames: dict[str, Grid]
    path: Path
    replaces: str | None = None
    palette_tag: str | None = None
    notes: str = ""
    meta: dict = field(default_factory=dict)

    @property
    def w(self) -> int:
        return KITS[self.kit]["frame"][0]

    @property
    def h(self) -> int:
        return KITS[self.kit]["frame"][1]


class SpecError(ValueError):
    pass


def _parse_rows(text: str, legend: dict[str, int], w: int, where: str, chars: bool = False) -> Grid:
    """Grid text -> rows of palette indices (or of the raw characters in shade mode)."""
    lines = [ln.rstrip("\n") for ln in text.strip("\n").split("\n")]
    rows = []
    for i, ln in enumerate(lines):
        ln = ln.strip()
        if len(ln) != w:
            raise SpecError(f"{where}: line {i + 1} is {len(ln)} wide, expected {w}: {ln!r}")
        try:
            rows.append([(legend[ch] and ch) or (ch if chars else legend[ch]) if False else (ch if chars else legend[ch]) for ch in ln])
            if chars:
                for ch in ln:
                    legend[ch]  # validates the letter
        except KeyError as e:
            raise SpecError(f"{where}: line {i + 1}: character {e} is not in the legend") from None
    return rows












def _transparent(legend: dict[str, int]) -> str:
    for ch, idx in legend.items():
        if idx == 0:
            return ch
    raise SpecError("legend needs a character for index 0 (transparent)")


def _bottom_anchor(rows: Grid, w: int, h: int, where: str) -> Grid:
    if len(rows) > h:
        raise SpecError(f"{where}: {len(rows)} rows, frame is {h} tall")
    return [[0] * w for _ in range(h - len(rows))] + rows


def game_dir() -> Path:
    """The pokeemerald checkout vanilla sheets are read from (same rule as the CLI)."""
    import os
    env = os.environ.get("EMERALD_DIR")
    if env:
        return Path(env).resolve()
    tool = Path(__file__).resolve().parents[1]
    for d in tool.parents:
        if (d / "game" / "graphics").is_dir():
            return (d / "game").resolve()
    return (tool.parent / "pokeemerald").resolve()


def _top(g: Grid) -> int:
    for y, row in enumerate(g):
        if any(row):
            return y
    return len(g)


def _recolor(g: Grid, m: dict[int, int]) -> Grid:
    return [[m.get(v, v) for v in row] for row in g] if m else g


def compose(d: dict, kit: str) -> dict[str, Grid]:
    """Frames built from `base_sheet`, `recolor` and `parts` (vanilla sheets, index grids)."""
    from .sheet import read_frames  # local import: sheet imports spec

    order = KITS[kit]["order"]
    w, h = KITS[kit]["frame"]
    game = game_dir()
    base, _ = read_frames(game / d["base_sheet"], (w, h))
    if len(base) != len(order):
        raise SpecError(f"base_sheet {d['base_sheet']}: {len(base)} frames, kit {kit} needs {len(order)}")
    rec = {int(k): int(v) for k, v in (d.get("recolor") or {}).items()}
    frames = {n: _recolor([list(r) for r in g], rec) for n, g in zip(order, base)}
    for i, pt in enumerate(d.get("parts") or []):
        where = f"parts[{i}]"
        src, _ = read_frames(game / pt["sheet"], (w, h))
        if len(src) != len(order):
            raise SpecError(f"{where}: {pt['sheet']} has {len(src)} frames, need {len(order)}")
        a, b = (int(v) for v in pt["rows"])
        prec = {int(k): int(v) for k, v in (pt.get("recolor") or {}).items()}
        dx = int(pt.get("dx", 0))
        only = pt.get("frames") or order
        src0_top, base0_top = _top(src[0]), _top(base[0])
        for n in only:
            k = order.index(n)
            # follow each frame's own bob: a step frame sits 1 px lower than its stand frame
            sy = a + (_top(src[k]) - src0_top)
            ty = a + (_top(base[k]) - base0_top)
            g = frames[n]
            for r in range(b - a + 1):
                if not (0 <= sy + r < h and 0 <= ty + r < h):
                    continue
                row = _recolor([src[k][sy + r]], prec)[0]
                for x in range(w):
                    tx = x + dx
                    if 0 <= tx < w and (row[x] or pt.get("replace", True)):
                        g[ty + r][tx] = row[x]
    return frames


def load(path: str | Path) -> Spec:
    path = Path(path)
    d = yaml.safe_load(path.read_text())
    kit = d.get("kit", "person16x32")
    if kit not in KITS:
        raise SpecError(f"unknown kit {kit!r}; known: {', '.join(KITS)}")
    w, h = KITS[kit]["frame"]
    # Shade mode (D13): grids are material letters; `materials:` maps letters to s/a/b/c/w/k and
    # `legend:` holds only hard pixels (letter -> index) such as eyes. The learned shader picks
    # every other tone. Transparent is always '.'.
    shade_mode = bool(d.get("shade"))
    materials = {str(k): str(v) for k, v in (d.get("materials") or {}).items()}
    if shade_mode:
        from .shade import MAT_TONES
        legend = {".": 0}
        legend.update({str(k): int(v) for k, v in (d.get("legend") or {}).items()})
        for ch, m in materials.items():
            m = m.replace("@", "").rstrip("!")
            ok = m in MAT_TONES or (m.startswith("w/") and m[2:] in ("s", "a", "b", "c")) \
                or (m.startswith("skin-") and m[5:] in ("a", "b", "c"))
            if not ok:
                raise SpecError(f"materials {ch!r}: {m!r} is not one of {' '.join(MAT_TONES)}, w/<ramp> or skin-<ramp>")
            legend.setdefault(ch, 0)  # presence only; the shader assigns the index
        for m in MAT_TONES:
            legend.setdefault(m, 0)
    else:
        legend = {str(k): int(v) for k, v in d["legend"].items()}
    for ch, idx in legend.items():
        if len(ch) != 1 or not 0 <= idx <= 15:
            raise SpecError(f"legend entry {ch!r}: {idx} must be one character -> index 0..15")

    if isinstance(d["palette"], list):
        if not 2 <= len(d["palette"]) <= 16 or any(len(c) != 3 or not all(0 <= v <= 255 for v in c) for c in d["palette"]):
            raise SpecError("inline palette: 2-16 entries of [r, g, b], 0-255")
    raw = d.get("frames") or {}
    frames: dict[str, Grid] = {}
    composed = compose(d, kit) if d.get("base_sheet") else {}
    if shade_mode and composed:
        # the vanilla base becomes material letters (its tones are re-shaded with everything
        # else); `remap:` renames letters, e.g. {b: w} turns the shirt ramp into a white apron
        from .shade import regions_of
        remap = {str(k): str(v) for k, v in (d.get("remap") or {}).items()}
        for ch in remap.values():
            legend.setdefault(ch, 0)
        composed = {n: [[remap.get(c, c) for c in row] for row in regions_of(g)] for n, g in composed.items()}

    def resolve(name: str, stack: tuple[str, ...] = ()) -> Grid:
        if name in frames:
            return frames[name]
        if name in stack:
            raise SpecError(f"frame {name}: circular reference {' -> '.join(stack + (name,))}")
        if name not in raw and name in composed:
            frames[name] = composed[name]
            return frames[name]
        if name not in raw:
            raise SpecError(f"frame {name} is required by kit {kit} but missing")
        f = raw[name]
        where = f"frame {name}"
        if isinstance(f, dict) and name in composed and not ({"half", "mirror_of", "base"} & set(f)):
            g = [list(r) for r in composed[name]]
        elif isinstance(f, str):
            g = _bottom_anchor(_parse_rows(f, legend, w, where, shade_mode), w, h, where)
        elif "half" in f:
            lines = [ln.rstrip() for ln in f["half"].strip("\n").split("\n")]
            half = w // 2
            if any(len(ln.strip()) > half for ln in lines):
                raise SpecError(f"{where}: a `half` line is wider than {half}")
            left = _parse_rows("\n".join(ln.strip().rjust(half, _transparent(legend)) for ln in lines), legend, half, where, shade_mode)
            # `mirror_shade` recolours the mirrored (right) half, e.g. "h:m m:d", so light
            # can come from the upper left even though the shape is mirrored.
            shade = {}
            for pair in str(f.get("mirror_shade", "")).split():
                a_, b_ = pair.split(":")
                if a_ not in legend or b_ not in legend:
                    raise SpecError(f"{where}: mirror_shade {pair!r} uses a character not in the legend")
                shade[legend[a_]] = legend[b_]
            g = _bottom_anchor([row + [shade.get(v, v) for v in row[::-1]] for row in left], w, h, where)
        elif "mirror_of" in f:
            g = [row[::-1] for row in resolve(f["mirror_of"], stack + (name,))]
        elif "base" in f:
            base = resolve(f["base"], stack + (name,))
            s = int(f.get("shift", 0))
            g = [[0] * w for _ in range(h)]
            for y in range(h):
                if 0 <= y - s < h:
                    g[y] = list(base[y - s])
            if "rows" in f:
                py = int(f["patch_y"])
                patch = _parse_rows(f["rows"], legend, w, where, shade_mode)
                if py + len(patch) > h:
                    raise SpecError(f"{where}: patch runs past the bottom of the frame")
                for i, row in enumerate(patch):
                    g[py + i] = row
        else:
            raise SpecError(f"{where}: give a grid, `half:`, `base:` or `mirror_of:`")
        if isinstance(f, dict):
            for i, pt in enumerate(f.get("patches") or []):
                px, py = int(pt["x"]), int(pt["y"])
                for dy, ln in enumerate(pt["rows"].strip("\n").split("\n")):
                    for dx, ch in enumerate(ln.strip()):
                        if ch == "_":
                            continue
                        if ch not in legend:
                            raise SpecError(f"{where}: patch {i}: character {ch!r} is not in the legend")
                        if not (0 <= px + dx < w and 0 <= py + dy < h):
                            raise SpecError(f"{where}: patch {i} runs outside the frame at ({px + dx}, {py + dy})")
                        g[py + dy][px + dx] = ch if shade_mode else legend[ch]
        frames[name] = g
        return g

    for name in KITS[kit]["order"]:
        resolve(name)

    if shade_mode:
        from .shade import shade
        hard = {ch: idx for ch, idx in legend.items() if idx}
        for name, g in frames.items():
            rows = ["".join("." if (c == 0 or c == ".") else str(c) for c in row) for row in g]
            frames[name] = shade(rows, materials, hard, facing=name.split("_")[0])

    return Spec(
        name=d["name"],
        kit=kit,
        palette=d["palette"],
        legend=legend,
        frames=frames,
        path=path,
        replaces=d.get("replaces"),
        palette_tag=d.get("palette_tag"),
        notes=d.get("notes", ""),
        meta=d,
    )

"""Parts library: hand-pixelled helmets, hoods, armour and props that any spec can place (D13).

A part is drawn once, in *roles* instead of palette characters, so it takes any character's
colours. `parts/<name>.yaml`:

    name: xwing_helmet
    # brief: what it is, which way it faces (3/4 toward the viewer's left), where it sits
    rows: |                 # `.` empty, `K` outline, roles below
      ....KKKKK....
      ..KK33332KK..
    notes: ...

Roles (dark -> light inside a group, light from the upper left, as every Emerald pic):
    K          outline
    1 2 3 4    main material (shadow, base, light, sheen)
    5 6 7      second material (shadow, base, light)
    8 9        third material (dark, light): visor, lenses, markings
    W          white (glints, teeth)
    s t u      skin (shadow, base, light), for parts that show a bit of face

Placing it (a rig layer):

    - {shape: part, part: xwing_helmet, at: [24, 2], flip: false, behind: false,
       paint: {"1234": "nmlW", "567": "fed", "89": "Kj", W: W}}

`paint` maps role groups (a string of roles -> a string of legend characters, same length) or
single roles to legend characters. Every role the part uses must be painted. `at` is the
top-left of the part's grid; `flip: true` mirrors it (for a pic turned the other way).
`behind: true` paints only empty pixels (a hood's back, a cape).
"""
from __future__ import annotations

from pathlib import Path

import yaml

PARTS = Path(__file__).resolve().parents[1] / "parts"
ROLES = "K1234567 89Wstu".replace(" ", "")


class PartError(ValueError):
    pass


def load(name: str) -> dict:
    p = PARTS / f"{name}.yaml"
    if not p.exists():
        known = ", ".join(sorted(q.stem for q in PARTS.glob("*.yaml")))
        raise PartError(f"no part {name!r} (known: {known})")
    d = yaml.safe_load(p.read_text())
    rows = [r.rstrip() for r in str(d["rows"]).strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, ".") for r in rows]
    bad = {c for r in rows for c in r} - set(ROLES) - {"."}
    if bad:
        raise PartError(f"part {name}: unknown role characters {sorted(bad)}")
    d["rows"] = rows
    return d


def paint_map(paint: dict, legend: dict[str, int], where: str) -> dict[str, int]:
    out = {}
    for roles, chars in (paint or {}).items():
        roles, chars = str(roles), str(chars)
        if len(roles) != len(chars):
            raise PartError(f"{where}: paint {roles!r} -> {chars!r}: lengths differ")
        for r, c in zip(roles, chars):
            if c not in legend:
                raise PartError(f"{where}: paint {r!r} -> {c!r}: not in the legend")
            out[r] = legend[c]
    return out


def place(g, layer: dict, legend: dict[str, int], w: int, h: int, where: str) -> None:
    d = load(str(layer["part"]))
    pm = paint_map(layer.get("paint"), legend, where)
    if "K" not in pm and "K" in legend:
        pm["K"] = legend["K"]
    if "W" not in pm and "W" in legend:
        pm["W"] = legend["W"]
    used = {c for r in d["rows"] for c in r} - {"."}
    missing = sorted(used - set(pm))
    if missing:
        raise PartError(f"{where}: part {d['name']} uses roles {missing}; add them to `paint`")
    ax, ay = (int(v) for v in layer.get("at", [0, 0]))
    flip = bool(layer.get("flip"))
    behind = bool(layer.get("behind"))
    snap = [list(r) for r in g] if behind else None
    pw = len(d["rows"][0])
    for dy, row in enumerate(d["rows"]):
        for dx, ch in enumerate(row):
            if ch == ".":
                continue
            x = ax + (pw - 1 - dx if flip else dx)
            y = ay + dy
            if 0 <= x < w and 0 <= y < h and not (behind and snap[y][x]):
                g[y][x] = pm[ch]


def cut(png: Path, box: list[int], roles: dict[int, str]) -> list[str]:
    """Cut a box out of a built pic into role rows (`roles`: palette index -> role character;
    unmapped indices become empty). How the approved helmets became parts."""
    from PIL import Image

    im = Image.open(png)
    px = im.load()
    x0, y0, bw, bh = box
    return ["".join(roles.get(px[x, y], ".") if px[x, y] else "." for x in range(x0, x0 + bw)) for y in range(y0, y0 + bh)]

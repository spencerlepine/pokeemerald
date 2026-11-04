"""Every wiki area and the game map it becomes.

An area either replaces a vanilla map (`replaces: <MapName>`, the map keeps its constant, scripts and flags)
or is new (`replaces: new`, a new map in the gMapGroup_StarWars group). How its terrain is built:

  vanilla  same size as the vanilla map and the same grid: the vanilla cells are kept (planet kit swaps and
           pieces placed on top still apply).
  hybrid   a route or cave of the same size with a few cells changed: vanilla cells where the grid is
           unchanged, the changed cells drawn from the grid.
  redraw   a redrawn town or landmark, a resized map, or a new area: every cell drawn from the grid.
"""
import csv
import glob
import re

import yaml

from . import base as B

SKIP = {
    # Mirage Isle is Route 130's island, shown by a script on the same map (vanilla's mirage); not its own map.
    "mirage-isle": "Route 130's island, shown by the vanilla mirage script; ported with route-130.",
    # The hideout kit is the secret-base furniture set, not a place.
    "hideout-kit": "The secret-base kit, not a map.",
}
NEW_GROUP = "gMapGroup_StarWars"


def camel(area_id):
    return "".join(p.capitalize() if not p.isdigit() else p for p in re.split(r"[-_ ]", area_id))


def snake(name):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    return re.sub(r"(?<=[A-Za-z])(?=[0-9])", "", s).upper()


class Area:
    def __init__(self, path):
        self.path = path
        raw = yaml.safe_load(open(path))
        self.raw = raw
        self.id = raw["id"]
        self.name = raw.get("name", self.id)
        self.planet = raw.get("planet", "")
        self.kind = raw.get("kind", "town")
        self.replaces = raw.get("replaces", "new")
        self.grid = [r for r in (raw.get("grid") or "").splitlines() if r.strip()]
        self.w = max((len(r) for r in self.grid), default=0)
        self.h = len(self.grid)
        self.grid = [r.ljust(self.w, "x") for r in self.grid]
        for k in ("exits", "buildings", "props", "people", "signs", "warps", "travel"):
            setattr(self, k, raw.get(k) or [])
        self.pos = raw.get("pos")
        self.room = raw.get("room") or {}
        self.new = self.replaces == "new"
        if self.new:
            self.map_name = "Sw" + camel(self.id)
            self.map_const = "MAP_SW_" + self.id.upper().replace("-", "_")
        else:
            self.map_name = self.replaces
            self.map_const = B.base_map(self.replaces)["id"]
        self.mode = None          # vanilla | hybrid | redraw (set by classify)
        self.vgrid = None         # the vanilla map's grid in blockout terms (same size only)
        self.changed = set()      # cells whose grid char differs from vanilla

    def cell(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.grid[y][x]
        return None

    def __repr__(self):
        return f"<{self.id} {self.mode} {self.map_name}>"


def load_areas():
    out = {}
    for p in sorted(glob.glob(str(B.WORLD / "**" / "*.yaml"), recursive=True)):
        a = Area(p)
        if a.id in SKIP:
            continue
        out[a.id] = a
    return out


def classify(areas, V):
    """Set each area's mode from its grid against the vanilla map's (blockout's own vanilla import)."""
    for a in areas.values():
        if a.new:
            a.mode = "redraw"
            continue
        rows, (w, h) = V.terrain_grid(a.replaces)
        if (w, h) != (a.w, a.h):
            a.mode = "redraw"
            continue
        a.vgrid = rows
        a.changed = {(x, y) for y in range(h) for x in range(w) if rows[y][x] != a.grid[y][x]}
        if not a.changed:
            a.mode = "vanilla"
        elif a.kind in ("town", "landmark"):
            a.mode = "redraw"
        else:
            a.mode = "hybrid"
    return areas


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

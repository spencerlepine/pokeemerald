"""The world as the StarNAV map sees it: every overworld area of every planet, squeezed into one small map.

Reads the blockout yamls (../../wiki/world/<planet>/<area>.yaml, only the ones with a `pos`), the planet graph
(../../wiki/mapping/hyperlanes.csv) and the planet table (../../wiki/mapping/planets.csv). Nothing in ../../game.

The map is not to scale. Each planet gets a box on the 224x120 map (LAYOUT, in pixels) and its areas are shrunk
to fit it, one pixel for several tiles. Each pixel gets a terrain class (CLASSES), from the cells of the area
grids it covers. The 8x8 cells of the map are what the cursor steps over, like Emerald's map sections.
"""
from __future__ import annotations

import csv
import glob
import math
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"

MAP_W, MAP_H = 224, 120          # 28 x 15 cells of 8 px, Emerald's region map grid
CELL = 8

# terrain classes, in draw order
SPACE, WILD, WATER, ROCK, TREE, GRASS, GROUND, PATH, TOWN = range(9)
CLASSES = ["space", "wild", "water", "rock", "tree", "grass", "ground", "path", "town"]
CHAR_CLASS = {"~": WATER, ".": GROUND, "#": ROCK, "T": TREE, '"': GRASS, ":": PATH, "=": PATH,
              "v": GROUND, "<": GROUND, ">": GROUND, "H": PATH}

# planet -> box on the map (x, y, w, h) in pixels. Areas keep their aspect and are centred in the box.
# Laid out left to right along the story's hyperlanes: Tatooine (the hub), then Endor, Bespin, Yavin 4, Dagobah.
LAYOUT = {
    "TATOOINE":       (4, 4, 58, 70),
    "KASHYYYK":       (4, 84, 56, 30),
    "SULLUST":        (70, 6, 40, 18),
    "MUSTAFAR":       (72, 32, 18, 18),
    "GRAND ARENA":    (68, 88, 22, 22),
    "ENDOR":          (96, 30, 36, 26),
    "FELUCIA":        (96, 66, 24, 16),
    "JEDHA":          (118, 4, 22, 20),
    "BESPIN":         (130, 62, 18, 18),
    "TYTHON":         (104, 92, 12, 18),
    "ATOLLON":        (124, 96, 12, 12),
    "MORTIS":         (140, 88, 10, 26),
    "YAVIN 4":        (148, 26, 30, 22),
    "HOTH":           (150, 4, 18, 16),
    "DEATH STAR":     (180, 4, 16, 16),
    "KAMINO":         (156, 96, 64, 14),
    "DAGOBAH":        (160, 54, 38, 32),
    "ASTEROID FIELD": (204, 52, 14, 22),
    "ILUM":           (200, 24, 16, 20),
}

PLANET_NAMES = {p: p for p in LAYOUT}


def load_areas():
    """Every overworld area with a world position, grouped by planet."""
    out = defaultdict(list)
    for f in sorted(glob.glob(str(WIKI / "world" / "*" / "*.yaml"))):
        d = yaml.safe_load(open(f)) or {}
        if "pos" not in d or not d.get("grid"):
            continue
        rows = [r for r in d["grid"].splitlines() if r.strip()]
        w = max(len(r) for r in rows)
        rows = [r.ljust(w, "x") for r in rows]
        travel = d.get("travel") or []
        bnames = " ".join(b.get("name", "") for b in d.get("buildings") or []).lower()
        out[d["planet"]].append({
            "id": d["id"], "name": d.get("name", d["id"]), "kind": d.get("kind", "route"),
            "planet": d["planet"], "x": d["pos"][0], "y": d["pos"][1], "w": w, "h": len(rows), "grid": rows,
            "hangar": any(t.get("via") in ("ship", "shuttle") for t in travel) or "hangar" in bnames,
            "bacta": "bacta" in bnames, "market": "market" in bnames or "mart" in bnames,
            "arena": "arena" in bnames,
        })
    return out


def load_planets():
    rows = list(csv.DictReader(open(WIKI / "mapping" / "planets.csv")))
    return {r["planet"]: r for r in rows}


def load_lanes():
    pairs = set()
    for r in csv.DictReader(open(WIKI / "mapping" / "hyperlanes.csv")):
        a, b = r["from_planet"], r["to_planet"]
        if a != b:
            pairs.add(tuple(sorted((a, b))))
    return sorted(pairs)


def planet_class_map(areas, bw, bh, scale=None):
    """Shrink one planet's areas into a bw x bh pixel box.

    Returns (cls, owner, (ox, oy, s)): cls[y][x] a terrain class, owner[y][x] an area index or -1,
    and the transform (pixel = (tile - origin) / s + offset)."""
    x0 = min(a["x"] for a in areas); y0 = min(a["y"] for a in areas)
    x1 = max(a["x"] + a["w"] for a in areas); y1 = max(a["y"] + a["h"] for a in areas)
    tw, th = x1 - x0, y1 - y0
    s = scale or max(tw / bw, th / bh)
    pw, ph = math.ceil(tw / s), math.ceil(th / s)
    ox, oy = (bw - pw) // 2, (bh - ph) // 2
    cls = [[SPACE] * bw for _ in range(bh)]
    owner = [[-1] * bw for _ in range(bh)]
    for py in range(ph):
        for px in range(pw):
            tx0, ty0 = x0 + px * s, y0 + py * s
            votes, own = Counter(), Counter()
            n = 0
            steps = max(2, int(math.ceil(s)))
            for j in range(steps):
                for i in range(steps):
                    tx = tx0 + (i + 0.5) * s / steps
                    ty = ty0 + (j + 0.5) * s / steps
                    n += 1
                    for k, a in enumerate(areas):
                        if a["x"] <= tx < a["x"] + a["w"] and a["y"] <= ty < a["y"] + a["h"]:
                            ch = a["grid"][int(ty - a["y"])][int(tx - a["x"])]
                            c = CHAR_CLASS.get(ch)
                            if c is not None:
                                votes[c] += 1
                                own[k] += 1
                            break
            if not votes:
                continue
            total = sum(votes.values())
            if total < n * 0.3:
                continue
            # thin features survive the shrink: paths win at 20%, water at 35%
            if votes[PATH] >= total * 0.2:
                c = PATH
            elif votes[WATER] >= total * 0.35 and votes[WATER] < total * 0.9:
                c = WATER if votes[WATER] >= total * 0.5 else votes.most_common(1)[0][0]
            else:
                c = votes.most_common(1)[0][0]
            cls[oy + py][ox + px] = c
            owner[oy + py][ox + px] = own.most_common(1)[0][0]
    return cls, owner, (x0, y0, s, ox, oy)


def dilate(mask, w, h, r):
    out = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if mask[y][x]:
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy <= r * r + 1 and 0 <= x + dx < w and 0 <= y + dy < h:
                            out[y + dy][x + dx] = True
    return out


class World:
    """The whole map: per-pixel class, planet and area; per-cell section names; towns; lanes."""

    def __init__(self):
        self.areas = load_areas()
        self.planets = load_planets()
        self.lanes = load_lanes()
        W, H = MAP_W, MAP_H
        self.cls = [[SPACE] * W for _ in range(H)]
        self.planet = [[None] * W for _ in range(H)]
        self.area = [[None] * W for _ in range(H)]
        self.centres = {}
        self.area_info = {}
        for p, (bx, by, bw, bh) in LAYOUT.items():
            self.centres[p] = (bx + bw / 2, by + bh / 2)
            areas = self.areas.get(p)
            if not areas:
                continue
            cls, owner, _ = planet_class_map(areas, bw, bh)
            land = [[cls[y][x] != SPACE for x in range(bw)] for y in range(bh)]
            wild = dilate(land, bw, bh, 2)
            for y in range(bh):
                for x in range(bw):
                    if wild[y][x]:
                        self.cls[by + y][bx + x] = cls[y][x] if land[y][x] else WILD
                        self.planet[by + y][bx + x] = p
                        if owner[y][x] >= 0:
                            self.area[by + y][bx + x] = areas[owner[y][x]]["id"]
            for a in areas:
                self.area_info[a["id"]] = a
        # Death Star has no overworld: a station, drawn by the variants
        self.special = {"DEATH STAR": LAYOUT["DEATH STAR"]}
        for p, (bx, by, bw, bh) in self.special.items():
            cx, cy, r = bx + bw / 2, by + bh / 2, min(bw, bh) / 2 - 1
            for y in range(by, by + bh):
                for x in range(bx, bx + bw):
                    if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                        self.cls[y][x] = ROCK
                        self.planet[y][x] = p
        self._sections()

    def _sections(self):
        """Name every 8x8 cell: the area with most pixels in it; each town and landmark claims its own cell."""
        CW, CH = MAP_W // CELL, MAP_H // CELL
        votes = [[Counter() for _ in range(CW)] for _ in range(CH)]
        pvotes = [[Counter() for _ in range(CW)] for _ in range(CH)]
        sums = defaultdict(lambda: [0, 0, 0])
        for y in range(MAP_H):
            for x in range(MAP_W):
                a = self.area[y][x]
                if a:
                    votes[y // CELL][x // CELL][a] += 1
                    s = sums[a]; s[0] += x; s[1] += y; s[2] += 1
                if self.planet[y][x]:
                    pvotes[y // CELL][x // CELL][self.planet[y][x]] += 1
        self.cells = [[None] * CW for _ in range(CH)]
        self.cell_planet = [[None] * CW for _ in range(CH)]
        for cy in range(CH):
            for cx in range(CW):
                if pvotes[cy][cx]:
                    self.cell_planet[cy][cx] = pvotes[cy][cx].most_common(1)[0][0]
                if votes[cy][cx]:
                    self.cells[cy][cx] = votes[cy][cx].most_common(1)[0][0]
        # towns and landmarks claim the cell under their middle, so none is lost in the shrink
        self.towns = {}
        claimed = set()
        order = sorted(sums, key=lambda a: (self.area_info[a]["kind"] not in ("town",), self.area_info[a]["kind"] != "landmark"))
        for a in order:
            sx, sy, n = sums[a]
            mx, my = sx / n, sy / n
            cx, cy = int(mx // CELL), int(my // CELL)
            # nearest unclaimed cell
            best = None
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    c = (cx + dx, cy + dy)
                    if 0 <= c[0] < CW and 0 <= c[1] < CH and c not in claimed \
                            and self.cell_planet[c[1]][c[0]] == self.area_info[a]["planet"]:
                        d = (c[0] * CELL + 4 - mx) ** 2 + (c[1] * CELL + 4 - my) ** 2
                        if self.cells[c[1]][c[0]] == a:
                            d -= 30
                        if best is None or d < best[0]:
                            best = (d, c)
            if not best:
                continue
            c = best[1]
            kind = self.area_info[a]["kind"]
            if kind in ("town", "landmark") or a not in {v for row in self.cells for v in row}:
                self.cells[c[1]][c[0]] = a
                claimed.add(c)
            if kind in ("town", "landmark"):
                self.towns[a] = c
        for p in self.special:
            bx, by, bw, bh = LAYOUT[p]
            c = (int((bx + bw / 2) // CELL), int((by + bh / 2) // CELL))
            self.cells[c[1]][c[0]] = "death-star"
            self.cell_planet[c[1]][c[0]] = p
        self.area_info["death-star"] = {"id": "death-star", "name": "DEATH STAR", "kind": "landmark",
                                        "planet": "DEATH STAR", "hangar": True, "bacta": False,
                                        "market": False, "arena": False}
        self.towns["death-star"] = c

    def sections(self):
        """JSON-ready: names per cell and the info for each area."""
        info = {}
        for a, d in self.area_info.items():
            p = self.planets.get(d["planet"], {})
            info[a] = {"name": d["name"], "kind": d["kind"].upper(), "planet": d["planet"],
                       "badges": p.get("arrive_badges", ""), "role": p.get("role", ""),
                       "hangar": d["hangar"], "bacta": d["bacta"], "market": d["market"], "arena": d["arena"]}
        return {"cells": self.cells, "cell_planet": self.cell_planet, "info": info,
                "towns": {a: list(c) for a, c in self.towns.items()}}


def planet_detail(world, planet, bw=224, bh=120):
    """One planet alone, big: class map plus per-cell area names (for the galaxy -> planet zoom)."""
    areas = world.areas.get(planet) or []
    if not areas:
        return None
    cls, owner, xf = planet_class_map(areas, bw, bh)
    land = [[cls[y][x] != SPACE for x in range(bw)] for y in range(bh)]
    wild = dilate(land, bw, bh, 3)
    out = [[(cls[y][x] if land[y][x] else (WILD if wild[y][x] else SPACE)) for x in range(bw)] for y in range(bh)]
    CW, CH = bw // CELL, bh // CELL
    votes = [[Counter() for _ in range(CW)] for _ in range(CH)]
    sums = defaultdict(lambda: [0, 0, 0])
    for y in range(bh):
        for x in range(bw):
            if owner[y][x] >= 0:
                a = areas[owner[y][x]]["id"]
                votes[min(y // CELL, CH - 1)][min(x // CELL, CW - 1)][a] += 1
                s = sums[a]; s[0] += x; s[1] += y; s[2] += 1
    cells = [[(v.most_common(1)[0][0] if v else None) for v in row] for row in votes]
    towns = {}
    for a in sorted(sums, key=lambda a: world.area_info[a]["kind"] != "town"):
        sx, sy, n = sums[a]
        c = (min(int(sx / n // CELL), CW - 1), min(int(sy / n // CELL), CH - 1))
        if world.area_info[a]["kind"] in ("town", "landmark"):
            towns[a] = list(c)
            cells[c[1]][c[0]] = a
        elif a not in {v for row in cells for v in row}:
            cells[c[1]][c[0]] = a
    return {"cls": out, "cells": cells, "towns": towns, "w": bw, "h": bh, "xf": xf}

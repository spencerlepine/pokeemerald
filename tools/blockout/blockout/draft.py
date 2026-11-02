"""Helpers for drafting an area by script: start from an empty or imported grid, carve shapes, place
pieces, check, and save the area file. The saved YAML is the source of truth; a draft script is only a
quicker way to write it.

    from blockout.draft import Draft
    d = Draft.new("mos-entha", "MOS ENTHA", "TATOOINE", 44, 30, replaces="PetalburgCity")
    d.fill(0, 0, 43, 29, "T"); d.blob(22, 15, 18, 12, ".")
    d.road([(0, 14), (43, 14)], 2)
    d.building("Arena", "art:tatooine:mos-entha-arena", 18, 4, 7, 5, door=3, to="mos-entha-arena")
    d.save()
"""
import math
import os
import random

import yaml

from .area import Area
from .cli import _Dumper
from . import catalog as K

WORLD_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "wiki", "world")


class Draft:
    def __init__(self, doc, path):
        self.doc = doc
        self.path = path
        rows = [r for r in (doc.get("grid") or "").splitlines()]
        self.g = [list(r) for r in rows]
        for k in ("exits", "buildings", "props", "people", "signs", "warps", "todo"):
            doc.setdefault(k, [])
        self.rng = random.Random(doc["id"])

    # ---------------------------------------------------------------- creation
    @classmethod
    def load(cls, area_id):
        for root, _, files in os.walk(WORLD_ROOT):
            if area_id + ".yaml" in files:
                p = os.path.join(root, area_id + ".yaml")
                return cls(yaml.safe_load(open(p)), p)
        raise FileNotFoundError(area_id)

    @classmethod
    def new(cls, area_id, name, planet, w, h, kind="town", replaces="new", fill="T", folder=""):
        doc = {"id": area_id, "name": name, "planet": planet, "kind": kind, "replaces": replaces,
               "status": "BLOCKOUT", "story": "", "grid": "\n".join([fill * w] * h)}
        p = os.path.join(WORLD_ROOT, planet.lower().replace(" ", "-"), folder, area_id + ".yaml")
        return cls(doc, os.path.normpath(p))

    @property
    def w(self):
        return len(self.g[0])

    @property
    def h(self):
        return len(self.g)

    def resize(self, w, h, fill="T", dx=0, dy=0):
        """New canvas size; the old grid is copied at (dx, dy) and every piece moves with it."""
        ng = [[fill] * w for _ in range(h)]
        for y, row in enumerate(self.g):
            for x, ch in enumerate(row):
                if 0 <= x + dx < w and 0 <= y + dy < h:
                    ng[y + dy][x + dx] = ch
        self.g = ng
        for k in ("buildings", "props", "people", "signs", "warps"):
            for o in self.doc[k]:
                o["at"] = [o["at"][0] + dx, o["at"][1] + dy]
        for e in self.doc["exits"]:
            off = dx if e["edge"] in ("north", "south") else dy
            e["cells"] = [c + off for c in e["cells"]]
        if self.doc.get("pos"):
            self.doc["pos"] = [self.doc["pos"][0] - dx, self.doc["pos"][1] - dy]

    # ---------------------------------------------------------------- terrain
    def set(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def fill(self, x0, y0, x1, y1, ch, only=None):
        for y in range(max(y0, 0), min(y1, self.h - 1) + 1):
            for x in range(max(x0, 0), min(x1, self.w - 1) + 1):
                if only is None or self.g[y][x] in only:
                    self.g[y][x] = ch

    def replace(self, a, b, box=None):
        x0, y0, x1, y1 = box or (0, 0, self.w - 1, self.h - 1)
        self.fill(x0, y0, x1, y1, b, only=a)

    def blob(self, cx, cy, rx, ry, ch, rough=0.18, only=None):
        """An irregular ellipse: towns and clearings that are not rectangles."""
        k = [self.rng.uniform(-rough, rough) for _ in range(8)]
        for y in range(int(cy - ry - 2), int(cy + ry + 3)):
            for x in range(int(cx - rx - 2), int(cx + rx + 3)):
                a = math.atan2((y - cy) / max(ry, 1), (x - cx) / max(rx, 1))
                wob = 1 + sum(k[i] * math.sin((i + 2) * a + i) for i in range(len(k))) / 2
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= wob * wob:
                    if only is None or self.get(x, y) in only:
                        self.set(x, y, ch)

    def road(self, pts, width=2, ch=":", only=None):
        """A path through points, `width` cells wide (straight segments, axis-aligned elbows)."""
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for k in range(width):
                    if only is None or self.get(x, y0 + k) in only:
                        self.set(x, y0 + k, ch)
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for k in range(width):
                    if only is None or self.get(x1 + k, y) in only:
                        self.set(x1 + k, y, ch)

    def scatter(self, ch, n, box=None, on=".", gap=1):
        """`n` single cells of `ch` on cells of `on`, not touching each other."""
        x0, y0, x1, y1 = box or (0, 0, self.w - 1, self.h - 1)
        placed, tries = 0, 0
        while placed < n and tries < n * 60:
            tries += 1
            x, y = self.rng.randint(x0, x1), self.rng.randint(y0, y1)
            if self.get(x, y) != on:
                continue
            if any(self.get(x + i, y + j) == ch for i in range(-gap, gap + 1) for j in range(-gap, gap + 1)):
                continue
            self.set(x, y, ch)
            placed += 1

    def edge(self, ch="T", depth=1, rough=0, fill_from=".:\"="):
        """Close the map border with `ch`, except where exits are."""
        open_cells = set()
        for e in self.doc["exits"]:
            for c in e["cells"]:
                open_cells.add((e["edge"], c))
        for x in range(self.w):
            for d in range(depth + (self.rng.randint(0, rough) if rough else 0)):
                if ("north", x) not in open_cells:
                    self.set(x, d, ch)
                if ("south", x) not in open_cells:
                    self.set(x, self.h - 1 - d, ch)
        for y in range(self.h):
            for d in range(depth + (self.rng.randint(0, rough) if rough else 0)):
                if ("west", y) not in open_cells:
                    self.set(d, y, ch)
                if ("east", y) not in open_cells:
                    self.set(self.w - 1 - d, y, ch)

    # ---------------------------------------------------------------- pieces
    def clear(self, *kinds):
        for k in kinds or ("buildings", "props", "people", "signs", "warps"):
            self.doc[k] = []

    def building(self, name, art, x, y, w, h, door=None, to=None, ground="."):
        b = {"name": name, "art": art, "at": [x, y], "size": [w, h]}
        if door is not None:
            b["door"] = door
            self.fill(x + door, y + h, x + door, y + h, ground, only="T#x~")
        if to:
            b["to"] = to
        self.fill(x, y, x + w - 1, y + h - 1, ".", only="T#x")
        self.doc["buildings"].append(b)
        return b

    def prop(self, name, art, x, y, w=1, h=1):
        self.fill(x, y, x + w - 1, y + h - 1, ".", only="T#x")
        self.doc["props"].append({"name": name, "art": art, "at": [x, y], "size": [w, h]})

    def person(self, name, x, y, role="npc"):
        self.doc["people"].append({"name": name, "at": [x, y], "role": role})

    def sign(self, name, x, y):
        self.doc["signs"].append({"name": name, "at": [x, y]})

    def warp(self, name, x, y, to):
        self.doc["warps"].append({"name": name, "at": [x, y], "to": to})

    def exit(self, edge, cells, to):
        self.doc["exits"] = [e for e in self.doc["exits"] if not (e["edge"] == edge and e.get("to") == to)]
        self.doc["exits"].append({"edge": edge, "cells": list(cells), "to": to})

    def keep_people(self, roles=("trainer", "item", "berry")):
        """Keep only the imported people with these roles (vanilla trainers and items keep their spots)."""
        self.doc["people"] = [p for p in self.doc["people"] if p.get("role") in roles]

    # ---------------------------------------------------------------- output
    def text(self):
        return "\n".join("".join(r) for r in self.g)

    def save(self, render=True):
        self.doc["grid"] = self.text() + "\n"
        order = ["id", "name", "planet", "kind", "replaces", "status", "story", "pos", "grid", "exits", "buildings",
                 "props", "people", "signs", "warps", "todo"]
        doc = {k: self.doc[k] for k in order if k in self.doc and self.doc[k] is not None}
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as fh:
            yaml.dump(doc, fh, Dumper=_Dumper, sort_keys=False, width=160, allow_unicode=True, default_flow_style=None)
        a = Area(self.path)
        probs = a.check()
        if render:
            from .render import sheet
            from . import vanilla as V
            van = V.render(a.replaces) if a.replaces and a.replaces != "new" else None
            sheet(a, van).save(os.path.splitext(self.path)[0] + ".png")
        print(f"{a.id}: {a.w}x{a.h}, {len(a.pieces())} pieces, {len(probs)} problems")
        for q in probs:
            print("   ", q)
        return probs


# -------------------------------------------------------------------- re-theming imported areas
def _walk(d, extra_block=frozenset()):
    """Cells reachable on foot from the first exit (or first walkable cell), ignoring levels."""
    from .terrain import walkable
    solid = set(extra_block)
    for k in ("buildings", "props"):
        for o in d.doc[k]:
            (x, y), (w, h) = o["at"], o.get("size", [1, 1])
            solid |= {(x + i, y + j) for i in range(w) for j in range(h)}
    def ok(x, y):
        ch = d.get(x, y)
        return ch is not None and (walkable(ch) or ch == "~") and (x, y) not in solid
    start = None
    for e in d.doc["exits"]:
        c = e["cells"][0] if e["cells"] else None
        if c is None:
            continue
        start = {"north": (c, 0), "south": (c, d.h - 1), "west": (0, c), "east": (d.w - 1, c)}[e["edge"]]
        break
    if start is None or not ok(*start):
        start = next(((x, y) for y in range(d.h) for x in range(d.w) if ok(x, y)), None)
    seen = {start} if start else set()
    todo = [start] if start else []
    while todo:
        x, y = todo.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and ok(nx, ny):
                seen.add((nx, ny)); todo.append((nx, ny))
    return seen


def _targets(d):
    t = set()
    for e in d.doc["exits"]:
        for c in e["cells"]:
            t.add({"north": (c, 0), "south": (c, d.h - 1), "west": (0, c), "east": (d.w - 1, c)}[e["edge"]])
    for b in d.doc["buildings"]:
        if "door" in b:
            t.add((b["at"][0] + b["door"], b["at"][1] + b["size"][1]))
    for k in ("people", "warps"):
        for o in d.doc[k]:
            t.add(tuple(o["at"]))
    return t


def place_near(d, name, art, w, h, near, radius=12, kind="prop", **kw):
    """Put a prop (or building) on open ground near `near`, hugging edge nature, without cutting off
    any exit, door, person or warp that was reachable before. Returns True if placed."""
    before = _walk(d)
    need = {t for t in _targets(d) if t in before}
    taken = set()
    for k in ("buildings", "props", "people", "signs", "warps"):
        for o in d.doc[k]:
            (x, y), (ww, hh) = o["at"], o.get("size", [1, 1])
            taken |= {(x + i, y + j) for i in range(-1, ww + 1) for j in range(-1, hh + 1)}
    cands = []
    nx0, ny0 = near
    for y in range(max(1, ny0 - radius), min(d.h - h - 1, ny0 + radius) + 1):
        for x in range(max(1, nx0 - radius), min(d.w - w - 1, nx0 + radius) + 1):
            cells = [(x + i, y + j) for i in range(w) for j in range(h)]
            if any(d.get(*c) != "." or c in taken for c in cells):
                continue
            ring = [(x + i, y + j) for i in range(-1, w + 1) for j in range(-1, h + 1) if (x + i, y + j) not in cells]
            hug = sum(1 for c in ring if d.get(*c) in ("T", "#", None))
            dist = abs(x - nx0) + abs(y - ny0)
            cands.append((-hug * 3 + dist, x, y, cells))
    for _, x, y, cells in sorted(cands)[:40]:
        after = _walk(d, frozenset(cells))
        if need <= after:
            if kind == "building":
                d.doc["buildings"].append(dict({"name": name, "art": art, "at": [x, y], "size": [w, h]}, **kw))
            else:
                d.doc["props"].append({"name": name, "art": art, "at": [x, y], "size": [w, h]})
            return True
    return False


def auto_buildings(d, art="art:tatooine:homestead-dome"):
    """Turn each vanilla house (a block of '#' with a door warp on its bottom row) into a building."""
    from .catalog import kebab  # noqa: F401
    used = set()
    keep = []
    for wp in d.doc["warps"]:
        x, y = wp["at"]
        seed = None
        for sx, sy in ((x, y), (x, y - 1)):
            if d.get(sx, sy) == "#":
                seed = (sx, sy); break
        if seed is None or seed in used:
            keep.append(wp); continue
        comp, todo = {seed}, [seed]
        while todo:
            cx, cy = todo.pop()
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if (nx, ny) not in comp and d.get(nx, ny) == "#":
                    comp.add((nx, ny)); todo.append((nx, ny))
        xs = [c[0] for c in comp]; ys = [c[1] for c in comp]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        bw, bh = x1 - x0 + 1, y1 - y0 + 1
        if bw > 12 or bh > 10 or len(comp) < 0.6 * bw * bh or bw * bh < 4:
            keep.append(wp); continue
        used |= comp
        y1 = max(y1, y)
        bh = y1 - y0 + 1
        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                d.set(cx, cy, ".")
        to = wp.get("to", "")
        label = str(to).split("-", 2)[-1].replace("-", " ") if to else "house"
        b = {"name": label[:1].upper() + label[1:], "art": art, "at": [x0, y0], "size": [bw, bh], "door": x - x0, "to": to}
        d.doc["buildings"].append(b)
        if d.get(x, y1 + 1) not in (".", ":", '"'):
            d.set(x, y1 + 1, ".")
    d.doc["warps"] = keep


NPC_NAMES = {"Rate Pokedex Or Register": "Prof. Korr's aide", "Birchs Bag": "Prof. Korr's dropped bag",
             "Event Script_Cut Tree": "Shrub to cut (Vibroblade)", "Rock Smash": "Rock to smash",
             "Item": "Item", "Berry tree": "Berry plant"}


def clean_people(d):
    import re
    for p in d.doc["people"]:
        n = p["name"]
        if n in NPC_NAMES:
            p["name"] = NPC_NAMES[n]
        elif re.fullmatch(r"(0x)?[0-9A-Fa-f]+|0x0", n) or n.startswith("Event Script"):
            p["name"] = "Event object"
            p["role"] = "object"
        elif "Cut Tree" in n or "Cuttable" in n:
            p["name"] = "Shrub to cut (Vibroblade)"; p["role"] = "object"
        elif "Rock Smash" in n or "Breakable Rock" in n:
            p["name"] = "Rock to smash"; p["role"] = "object"
        elif "Boulder" in n or "Strength" in n:
            p["name"] = "Boulder to push"; p["role"] = "object"
        if p["name"] in ("Shrub to cut (Vibroblade)", "Event object"):
            p["role"] = "object"


def cut_borders(d, planet_of):
    """Remove exits that lead to another planet and close that edge; returns what was cut."""
    cut = []
    d.doc["exits"] = [e for e in d.doc["exits"] if e.get("cells")]
    for e in list(d.doc["exits"]):
        to = e.get("to")
        if to in planet_of and planet_of[to] != d.doc["planet"]:
            for c in e["cells"]:
                x, y = {"north": (c, 0), "south": (c, d.h - 1), "west": (0, c), "east": (d.w - 1, c)}[e["edge"]]
                d.set(x, y, "T" if d.get(x, y) != "~" else "~")
            d.doc["exits"].remove(e)
            cut.append(f"{e['edge']} edge to {to} ({planet_of[to]})")
    return cut


def open_exit(d, edge, at, to, width=2, ch="."):
    """Carve a side path from the map edge inward (at row/column `at`) until it meets ground that is
    already reachable, and add the exit. Used to hang new optional areas off existing ones."""
    reach = _walk(d)
    cells = list(range(at, at + width))
    for k in range(0, max(d.w, d.h)):
        pts = []
        for c in cells:
            pts.append({"north": (c, k), "south": (c, d.h - 1 - k), "west": (k, c), "east": (d.w - 1 - k, c)}[edge])
        if k > 0 and any(p in reach for p in pts):
            break
        for p in pts:
            if d.get(*p) not in (".", ":", '"', "="):
                d.set(*p, ch)
    d.exit(edge, cells, to)


def link_all(d):
    """Carve the shortest ground path from every unreachable exit, door, warp or person to the
    reachable part of the map (through rock or trees, never through buildings, props or water)."""
    from collections import deque
    solid = set()
    for k in ("buildings", "props"):
        for o in d.doc[k]:
            (x, y), (w, h) = o["at"], o.get("size", [1, 1])
            solid |= {(x + i, y + j) for i in range(w) for j in range(h)}
    for _ in range(40):
        reach = _walk(d)
        todo = [t for t in _targets(d) if t not in reach and t not in solid]
        if not todo:
            return
        t = todo[0]
        prev = {t: None}
        q = deque([t])
        hit = None
        while q:
            c = q.popleft()
            if c in reach:
                hit = c
                break
            x, y = c
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in prev and d.get(*n) is not None and n not in solid and d.get(*n) != "~":
                    prev[n] = c
                    q.append(n)
        if hit is None:
            return
        c = hit
        while c is not None:
            if d.get(*c) not in (".", ":", '"', "=", "H", "v", "^", "<", ">", "_"):
                d.set(*c, ".")
            c = prev[c]

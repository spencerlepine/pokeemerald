"""An area blockout file (wiki/world/<planet>/<area>.yaml): a terrain grid plus placed pieces.

    id: mos-pelgo                    # unique, kebab-case
    name: MOS PELGO
    planet: TATOOINE
    kind: town                       # town | route | dungeon | interior | landmark
    replaces: LittlerootTown         # vanilla map it is built into (sets size, exits and doors), or `new`
    status: BLOCKOUT                 # TODO | BLOCKOUT | APPROVED   (the layout)
    art_status: pending-mockup       # pending-mockup | pending-final-art | art-complete | imported-in-game
    story: one or two lines on what happens here
    notes: what this area needs drawn, in plain words (what is there, what borders it, what is unique)
    grid: |                          # one char per cell, legend in terrain.py
      TTTT::TTTT
    exits:                           # map edges the player leaves by
      - {edge: north, cells: [9, 10], to: route-101}
    buildings:                       # solid rectangles with a door on the bottom row
      - {name: Player's homestead, art: art:tatooine:homestead-dome, at: [3, 4], size: [5, 4], door: 2, to: homestead-interior}
    props:                           # big and small objects (art id: a row in ../mapping/world_art.csv)
      - {name: Vaporator, art: art:tatooine:moisture-vaporator, at: [2, 9], size: [1, 2]}
    people:                          # pink sprites
      - {name: Prof. Korr, at: [14, 10], role: story}
    signs:                           # pink, readable
      - {name: Town sign, at: [15, 13]}
    warps:                           # doorways that are not a building door (cave mouths, ladders, hatches)
      - {name: Cave, at: [4, 2], to: some-cave}
    travel:                          # links that are not a door or an edge (ship, shuttle, dive, script)
      - {to: starnav, via: ship, name: StarNAV flight console}
    todo:                            # open questions and work left on the layout
      - text

`at` is the top-left cell [x, y]. `door` is the door's column inside the building, counted from its
left edge; the door is on the building's bottom row and the cell below it must be walkable.
"""
import yaml

from .terrain import TERRAIN, walkable

KINDS = ("town", "route", "dungeon", "interior", "landmark", "space")
STATUSES = ("TODO", "BLOCKOUT", "APPROVED")


class Area:
    def __init__(self, path):
        self.path = path
        raw = yaml.safe_load(open(path)) or {}
        self.raw = raw
        self.id = raw["id"]
        self.name = raw.get("name", self.id)
        self.planet = raw.get("planet", "")
        self.kind = raw.get("kind", "town")
        self.replaces = raw.get("replaces", "new")
        self.status = raw.get("status", "TODO")
        self.pos = raw.get("pos")
        self.story = raw.get("story", "")
        self.grid = [r for r in (raw.get("grid") or "").splitlines() if r.strip() != "" or False]
        self.w = max((len(r) for r in self.grid), default=0)
        self.h = len(self.grid)
        self.grid = [r.ljust(self.w, "x") for r in self.grid]
        self.exits = raw.get("exits") or []
        self.buildings = raw.get("buildings") or []
        self.props = raw.get("props") or []
        self.people = raw.get("people") or []
        self.signs = raw.get("signs") or []
        self.warps = raw.get("warps") or []
        self.travel = raw.get("travel") or []   # links not on the map: ships, shuttles, dives
        self.todo = raw.get("todo") or []

    def cell(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.grid[y][x]
        return None

    def solid_cells(self):
        """Cells covered by buildings and props."""
        out = {}
        for kind, items in (("building", self.buildings), ("prop", self.props)):
            for b in items:
                (x, y), (w, h) = b["at"], b.get("size", [1, 1])
                for yy in range(y, y + h):
                    for xx in range(x, x + w):
                        out.setdefault((xx, yy), []).append(f"{kind} {b.get('name')}")
        return out

    def check(self):
        """Layout problems, as strings. An empty list means the blockout is consistent."""
        p = []
        if self.kind not in KINDS:
            p.append(f"kind {self.kind!r} not in {KINDS}")
        if self.status not in STATUSES:
            p.append(f"status {self.status!r} not in {STATUSES}")
        for r, row in enumerate(self.grid):
            for c, ch in enumerate(row):
                if ch not in TERRAIN:
                    p.append(f"grid row {r} col {c}: unknown terrain {ch!r}")
        solid = self.solid_cells()
        for (x, y), who in solid.items():
            if not (0 <= x < self.w and 0 <= y < self.h):
                p.append(f"{who[0]} goes off the map at [{x}, {y}]")
            elif len(who) > 1:
                p.append(f"overlap at [{x}, {y}]: {', '.join(who)}")

        for b in self.buildings:
            (x, y), (w, h) = b["at"], b["size"]
            if "door" in b:
                dx = x + int(b["door"])
                below = (dx, y + h)
                if self.cell(*below) is None or not walkable(self.cell(*below)) or below in solid:
                    p.append(f"building {b['name']}: the cell below its door {list(below)} is not walkable")
        for kind, items in (("person", self.people), ("sign", self.signs), ("warp", self.warps)):
            for o in items:
                x, y = o["at"]
                ch = self.cell(x, y)
                if ch is None:
                    p.append(f"{kind} {o.get('name')} is off the map")
                elif kind == "person" and o.get("role") not in ("berry", "item", "object") \
                        and ch != "~" and (not walkable(ch) or (x, y) in solid):
                    p.append(f"{kind} {o.get('name')} stands on a blocked cell [{x}, {y}]")
        for e in self.exits:
            if not e.get("cells"):
                p.append(f"exit {e['edge']} to {e.get('to')} has no cells")
            for c in e["cells"]:
                x, y = {"north": (c, 0), "south": (c, self.h - 1), "west": (0, c), "east": (self.w - 1, c)}[e["edge"]]
                if self.cell(x, y) is None or not (walkable(self.cell(x, y)) or self.cell(x, y) == "~") or (x, y) in solid:
                    p.append(f"exit {e['edge']} to {e.get('to')}: edge cell [{x}, {y}] is not walkable")
        # Imported routes and caves keep vanilla geometry (stairs, bridges, stacked rooms joined by
        # warps) that the grid does not model, so only redrawn towns and new areas get the reach check.
        if self.kind in ("town", "landmark") or self.replaces == "new":
            p += self.reach_problems(solid)
        return p

    def reach_problems(self, solid):
        """Every exit, door, person and warp must be reachable on foot (or by surf) from the first
        exit. Ledges and levels are ignored, so this catches blocked paths, not one-way puzzles."""
        def ok(x, y):
            ch = self.cell(x, y)
            return ch is not None and (walkable(ch) or ch == "~") and (x, y) not in solid
        targets = []
        for e in self.exits:
            for c in e["cells"][:1]:
                targets.append((f"exit {e['edge']}", {"north": (c, 0), "south": (c, self.h - 1),
                                                      "west": (0, c), "east": (self.w - 1, c)}[e["edge"]]))
        for b in self.buildings:
            if "door" in b:
                targets.append((f"door of {b['name']}", (b["at"][0] + int(b["door"]), b["at"][1] + b["size"][1])))
        for o in self.warps:
            targets.append((f"warp {o.get('name')}", tuple(o["at"])))
        targets = [t for t in targets if ok(*t[1]) or t[0].startswith("warp")]
        if not targets:
            return []
        start = next((t[1] for t in targets if ok(*t[1])), None)
        if start is None:
            return []
        seen, todo = {start}, [start]
        while todo:
            x, y = todo.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in seen and ok(*n):
                    seen.add(n)
                    todo.append(n)
        out = []
        for name, (x, y) in targets:
            near = {(x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)}
            if not (near & seen):
                out.append(f"{name} at [{x}, {y}] cannot be reached from {targets[0][0]}")
        return out

    def pieces(self):
        """Every placed piece, numbered in drawing order, for the legend and the tracker."""
        out = []
        for kind, items in (("building", self.buildings), ("prop", self.props), ("person", self.people),
                            ("sign", self.signs), ("warp", self.warps)):
            for o in items:
                out.append(dict(o, kind=kind))
        return out

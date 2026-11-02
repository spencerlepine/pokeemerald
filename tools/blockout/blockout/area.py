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
            p += self.softlock_problems(solid)
        # content reach runs everywhere outdoors: a cut planet border or a prop on the only path must not
        # strand trainers, items or signs (imported caves keep vanilla puzzles the grid does not model)
        if self.kind != "interior" and not (self.kind == "dungeon" and self.replaces != "new"):
            p += self.content_problems(solid)
        if self.kind == "town":
            p += self.road_problems(solid)
        return p

    def road_steps(self, solid, start, limit=12):
        """Walking steps from a cell to the nearest path or platform cell (`:` or `=`), or None."""
        from collections import deque
        seen = {start}
        q = deque([(start, 0)])
        while q:
            (x, y), d = q.popleft()
            if self.cell(x, y) in (":", "="):
                return d
            if d >= limit:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                ch = self.cell(nx, ny)
                if ch is not None and (nx, ny) not in seen and (nx, ny) not in solid and walkable(ch) and ch not in "v<>^":
                    seen.add((nx, ny))
                    q.append(((nx, ny), d + 1))
        return None

    def road_problems(self, solid):
        """Every town door is within a few steps of a road (the compact-town rule: a spur to every door)."""
        p = []
        for b in self.buildings:
            if "door" not in b:
                continue
            (x, y), (w, h) = b["at"], b["size"]
            d = self.road_steps(solid, (x + int(b["door"]), y + h))
            if d is None or d > 5:
                p.append(f"building {b['name']}: its door is {d or 'more than 12'} steps from any road (paint a `:` spur to it)")
        return p

    def softlock_problems(self, solid):
        """One-way moves must never trap the player. Ledges are jumped in their direction only (a `v` cell is
        crossed from the cell north of it to the cell south of it); water counts only with SURF, so the check
        runs twice: on foot, and with surf. A cell the player can reach but from which no exit, door or warp
        can be reached again is a trap."""
        LEDGE = {"v": (0, 1), "^": (0, -1), "<": (-1, 0), ">": (1, 0)}

        def land(x, y, surf):
            ch = self.cell(x, y)
            return ch is not None and (x, y) not in solid and (walkable(ch) and ch not in LEDGE or (surf and ch == "~"))

        def moves(x, y, surf):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                ch = self.cell(nx, ny)
                if ch in LEDGE:
                    if LEDGE[ch] == (dx, dy) and land(nx + dx, ny + dy, surf):
                        yield (nx + dx, ny + dy)
                elif land(nx, ny, surf):
                    yield (nx, ny)

        def back_moves(x, y, surf):      # cells that can move into (x, y)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px, py = x - dx, y - dy
                ch = self.cell(px, py)
                if ch in LEDGE:
                    if LEDGE[ch] == (dx, dy) and land(px - dx, py - dy, surf):
                        yield (px - dx, py - dy)
                elif land(px, py, surf):
                    yield (px, py)

        exits = []
        for e in self.exits:
            for c in e["cells"]:
                exits.append({"north": (c, 0), "south": (c, self.h - 1), "west": (0, c), "east": (self.w - 1, c)}[e["edge"]])
        for b in self.buildings:
            if "door" in b:
                exits.append((b["at"][0] + int(b["door"]), b["at"][1] + b["size"][1]))
        for o in self.warps:
            exits.append(tuple(o["at"]))
        out = []
        for surf in (False, True):
            starts = [c for c in exits if land(*c, surf)]
            if not starts:
                continue
            fwd, todo = set(starts), list(starts)
            while todo:
                c = todo.pop()
                for n in moves(*c, surf):
                    if n not in fwd:
                        fwd.add(n); todo.append(n)
            back, todo = set(starts), list(starts)
            while todo:
                c = todo.pop()
                for n in back_moves(*c, surf):
                    if n not in back:
                        back.add(n); todo.append(n)
            traps = sorted(fwd - back)
            if traps:
                x, y = traps[0]
                out.append(f"softlock{' with surf' if surf else ' on foot'}: {len(traps)} reachable cells have no way "
                           f"back to any exit, door or warp, e.g. [{x}, {y}] (a one-way ledge or water with no landing)")
            if surf:
                break
        return out

    def content_problems(self, solid):
        """Every placed thing must be reachable the way the player actually moves: ledges in their direction,
        water with surf. A trainer, item, berry plant, sign, door or warp that no entry (exit, door, warp)
        can reach, even with surf, is content the player can never see."""
        fwd = self._forward_reach(solid, surf=True)
        if fwd is None:
            return []
        out = []
        targets = []
        for e in self.exits:
            for c in e["cells"]:
                targets.append((f"exit {e['edge']} to {e.get('to')}", {"north": (c, 0), "south": (c, self.h - 1),
                                                                        "west": (0, c), "east": (self.w - 1, c)}[e["edge"]]))
        for b in self.buildings:
            if "door" in b:
                targets.append((f"door of {b['name']}", (b["at"][0] + int(b["door"]), b["at"][1] + b["size"][1])))
        for o in self.warps:
            targets.append((f"warp {o.get('name')}", tuple(o["at"])))
        for o in self.people:
            if o.get("role") in ("trainer", "item", "berry", "story"):   # npcs behind counters and objects are vanilla placement
                targets.append((f"{o.get('role', 'person')} {o.get('name')}", tuple(o["at"])))
        for o in self.signs:
            targets.append((f"sign {o.get('name')}", tuple(o["at"])))
        seen_exits = set()
        for name, (x, y) in targets:
            if name.startswith("exit") and name in seen_exits:
                continue
            near = {(x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)}
            if not (near & fwd):
                out.append(f"unreachable: {name} at [{x}, {y}] cannot be reached from any entry (ledges and surf considered)")
                seen_exits.add(name)
        return out

    def _forward_reach(self, solid, surf):
        """Cells the player can reach from any exit, door or warp, moving the way the game moves."""
        LEDGE = {"v": (0, 1), "^": (0, -1), "<": (-1, 0), ">": (1, 0)}

        def land(x, y):
            ch = self.cell(x, y)
            return ch is not None and (x, y) not in solid and (walkable(ch) and ch not in LEDGE or (surf and ch == "~"))

        def moves(x, y):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                ch = self.cell(nx, ny)
                if ch in LEDGE:
                    if LEDGE[ch] == (dx, dy) and land(nx + dx, ny + dy):
                        yield (nx + dx, ny + dy)
                elif land(nx, ny):
                    yield (nx, ny)

        starts = []
        for e in self.exits:
            for c in e["cells"]:
                starts.append({"north": (c, 0), "south": (c, self.h - 1), "west": (0, c), "east": (self.w - 1, c)}[e["edge"]])
        for b in self.buildings:
            if "door" in b:
                starts.append((b["at"][0] + int(b["door"]), b["at"][1] + b["size"][1]))
        for o in self.warps:   # a cave mouth or door tile is solid: the player stands on the cell in front of it
            x, y = o["at"]
            starts += [(x, y), (x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        starts = [c for c in starts if land(*c)]
        if not starts:
            return None
        fwd, todo = set(starts), list(starts)
        while todo:
            c = todo.pop()
            for n in moves(*c):
                if n not in fwd:
                    fwd.add(n); todo.append(n)
        return fwd

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

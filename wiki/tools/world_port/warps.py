"""Warps and map connections of every area, from the wiki.

Warps. An area's warp list is:
  - vanilla and hybrid areas: the vanilla warp events whose cell is still a door or warp in the wiki (a
    building door or a `warps:` entry), in vanilla order, then every wiki door or warp vanilla does not have
    (a hangar door added to a route). Vanilla warps the wiki cut (a cave on another planet now) are dropped.
  - redrawn and new areas: every building door (in `buildings:` order), then every `warps:` entry.
Each warp leads to the area its `to` names; its destination warp is the matching warp back (the k-th warp
from A to B lands on the k-th warp from B to A; extra warps land on the last one). When neither end changed,
vanilla's destination is kept as is. Warps to MAP_DYNAMIC and to maps the wiki does not hold (secret bases)
keep vanilla's destination.

Connections. A map edge with an `exits:` entry connects to the area it names; the offset comes from the two
areas' `pos` on the planet layout. Vanilla connections to areas that are no longer exits (planet borders) are
dropped; dive and emerge connections are kept.
"""
from collections import defaultdict

from . import base as B


class Warp:
    __slots__ = ("x", "y", "to", "dest_map", "dest_id", "vanilla", "name", "kind")

    def __init__(self, x, y, to, name="", vanilla=None, kind="warp"):
        self.x, self.y, self.to, self.name, self.vanilla, self.kind = x, y, to, name, vanilla, kind
        self.dest_map, self.dest_id = None, None

    def __repr__(self):
        return f"Warp({self.x},{self.y}->{self.to}:{self.dest_id})"


def wiki_doors(area):
    """(x, y, to, name) for every building door and warp of the area, in wiki order."""
    out = []
    for b in area.buildings:
        if "door" in b and b.get("to"):
            out.append((b["at"][0] + int(b["door"]), b["at"][1] + b["size"][1] - 1, b["to"], b["name"], "door"))
    for w in area.warps:
        if w.get("to"):
            out.append((w["at"][0], w["at"][1], w["to"], w.get("name", ""), "warp"))
    return out


def map_to_area(areas):
    """vanilla map constant -> area id (for areas that replace a map)."""
    return {a.map_const: a.id for a in areas.values()}


def _inert_cell(area, taken):
    """A blocked cell with no warp on it, for a vanilla warp the wiki no longer has a door for."""
    for y in range(area.h):
        for x in range(area.w):
            if area.grid[y][x] in "T#x|" and (x, y) not in taken:
                return x, y
    return 0, 0


def build_warps(areas):
    """area id -> [Warp] with destinations resolved; problems.

    A map that replaces a vanilla one keeps every vanilla warp at its index, so warp ids named by scripts, heal
    spots and maps outside the port still land where they did. Each wiki door takes the vanilla warp at its cell,
    else the first unclaimed vanilla warp to the same place; doors left over are added after. A vanilla warp no
    wiki door claims stays: at its own cell in a vanilla or hybrid map (the cell is vanilla there), on a blocked
    cell in a redrawn one (inert: a warp only fires on a door or warp tile).
    """
    m2a = map_to_area(areas)
    problems = []
    lists = {}
    for a in areas.values():
        doors = wiki_doors(a)
        if a.new:
            lists[a.id] = [Warp(d[0], d[1], d[2], d[3], kind=d[4]) for d in doors]
            continue
        vw = B.base_map(a.replaces).get("warp_events") or []
        ws = [None] * len(vw)
        claimed = set()
        def keep(i, w, x, y, note):
            wp = Warp(x, y, None, note, vanilla=w)
            wp.dest_map, wp.dest_id = w["dest_map"], w["dest_warp_id"]
            ws[i] = wp

        # 0. warps to places the wiki does not hold (MAP_DYNAMIC, secret bases) stay as they are
        for i, w in enumerate(vw):
            if w["dest_map"] not in m2a:
                keep(i, w, w["x"], w["y"], "vanilla")
                for j, d in enumerate(doors):
                    if (d[0], d[1]) == (w["x"], w["y"]):
                        claimed.add(j)
        doors = [d if d[2] in areas else None for d in doors]
        claimed |= {j for j, d in enumerate(doors) if d is None}
        # 1. same cell
        for i, w in enumerate(vw):
            if ws[i] is not None:
                continue
            for j, d in enumerate(doors):
                if j not in claimed and (d[0], d[1]) == (w["x"], w["y"]):
                    claimed.add(j)
                    ws[i] = Warp(d[0], d[1], d[2], d[3], vanilla=w, kind=d[4])
                    break
        # 2. same destination
        for i, w in enumerate(vw):
            if ws[i] is not None:
                continue
            for j, d in enumerate(doors):
                if j not in claimed and m2a.get(w["dest_map"]) == d[2]:
                    claimed.add(j)
                    ws[i] = Warp(d[0], d[1], d[2], d[3], vanilla=w, kind=d[4])
                    break
        taken = {(d[0], d[1]) for d in doors if d}
        for i, w in enumerate(vw):
            if ws[i] is not None:
                continue
            # a second vanilla door to a place this map already has a door to (a two-cell door): same cell
            twin = next((x for x in ws if x is not None and x.to and x.to == m2a.get(w["dest_map"])), None)
            if twin is not None and a.mode == "redraw":
                ws[i] = Warp(twin.x, twin.y, twin.to, twin.name, vanilla=w, kind=twin.kind)
                continue
            if a.mode == "redraw":
                x, y = _inert_cell(a, taken)
                taken.add((x, y))
                note = "inert"
            else:
                x, y = w["x"], w["y"]
                note = "vanilla"
            keep(i, w, x, y, note)
            if note == "inert" and w["dest_map"] in m2a:
                problems.append(f"{a.id}: vanilla warp {i} to {m2a[w['dest_map']]} has no door in the wiki (inert)")
        for j, d in enumerate(doors):
            if j not in claimed and d is not None:
                ws.append(Warp(d[0], d[1], d[2], d[3], kind=d[4]))
        lists[a.id] = ws
    for aid, ws in lists.items():
        by_to = defaultdict(list)
        for w in ws:
            if w.to:
                by_to[w.to].append(w)
        for to, mine in by_to.items():
            if to not in areas:
                problems.append(f"{aid}: warp to unknown area {to}")
                continue
            back = [i for i, w in enumerate(lists[to]) if w.to == aid]
            for k, w in enumerate(mine):
                w.dest_map = areas[to].map_const
                # vanilla's own destination, when that warp still leads back here
                if w.vanilla is not None and w.vanilla["dest_map"] == areas[to].map_const:
                    w.dest_id = w.vanilla["dest_warp_id"]
                    continue
                if back:
                    w.dest_id = str(back[min(k, len(back) - 1)])
                elif w.vanilla is not None:
                    w.dest_map, w.dest_id = w.vanilla["dest_map"], w.vanilla["dest_warp_id"]
                    problems.append(f"{aid}: warp at ({w.x},{w.y}) to {to} has no warp back there; kept vanilla's "
                                    f"{w.dest_map} {w.dest_id}")
                else:
                    w.dest_id = "0" if lists[to] else None
                    problems.append(f"{aid}: warp at ({w.x},{w.y}) to {to} has no warp back there"
                                    + ("" if lists[to] else " and that map has no warps"))
    return lists, problems


DIRS = {"north": "up", "south": "down", "west": "left", "east": "right"}
OPP = {"north": "south", "south": "north", "west": "east", "east": "west"}


def build_connections(areas):
    """area id -> [connection dict]; problems."""
    problems = []
    out = {}
    for a in areas.values():
        cons = []
        if not a.new:
            for c in B.base_map(a.replaces).get("connections") or []:
                if c["direction"] in ("dive", "emerge"):
                    cons.append(dict(c))
        for e in a.exits:
            to = e.get("to")
            if to not in areas:
                problems.append(f"{a.id}: exit {e['edge']} to unknown area {to}")
                continue
            b = areas[to]
            back = [x for x in b.exits if x.get("to") == a.id and x["edge"] == OPP[e["edge"]]]
            if not back:
                problems.append(f"{a.id}: exit {e['edge']} to {to} has no exit back on its {OPP[e['edge']]} edge")
                continue
            if a.pos is None or b.pos is None:
                problems.append(f"{a.id}: no planet position for the exit to {to}")
                continue
            if e["edge"] in ("north", "south"):
                offset = b.pos[0] - a.pos[0]
            else:
                offset = b.pos[1] - a.pos[1]
            # the exit cells must meet: this edge's cell c faces the other's cell c - offset
            mine = set(e["cells"])
            theirs = {c + offset for c in back[0]["cells"]}
            if not mine & theirs:
                # fall back to lining up the first cells, and say so
                offset = e["cells"][0] - back[0]["cells"][0]
                problems.append(f"{a.id}: exit {e['edge']} to {to} does not meet its exit back at the planet "
                                f"positions; offset {offset} lines up the first cells")
            if any(c["map"] == b.map_const and c["direction"] == DIRS[e["edge"]] for c in cons):
                continue
            cons.append({"map": b.map_const, "offset": offset, "direction": DIRS[e["edge"]]})
        out[a.id] = cons
    # both sides must agree
    for a in areas.values():
        for c in out[a.id]:
            if c["direction"] in ("dive", "emerge"):
                continue
            b = next((x for x in areas.values() if x.map_const == c["map"]), None)
            opp = {"up": "down", "down": "up", "left": "right", "right": "left"}[c["direction"]]
            rc = [x for x in out.get(b.id, []) if x["map"] == a.map_const and x["direction"] == opp]
            if not rc:
                problems.append(f"{a.id}: connection {c['direction']} to {b.id} has none back")
            elif rc[0]["offset"] != -c["offset"]:
                problems.append(f"{a.id}: connection {c['direction']} to {b.id} offset {c['offset']} but "
                                f"{rc[0]['offset']} back")
    return out, problems

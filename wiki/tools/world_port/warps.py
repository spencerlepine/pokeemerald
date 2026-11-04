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


def build_warps(areas):
    """area id -> [Warp] with destinations resolved. Also returns problems."""
    m2a = map_to_area(areas)
    problems = []
    lists = {}
    for a in areas.values():
        doors = wiki_doors(a)
        if a.mode in ("vanilla", "hybrid"):
            mj = B.base_map(a.replaces)
            ws = []
            claimed = set()
            for w in mj.get("warp_events") or []:
                x, y = w["x"], w["y"]
                dest = w["dest_map"]
                hit = [i for i, d in enumerate(doors) if (d[0], d[1]) == (x, y) and i not in claimed]
                if dest == "MAP_DYNAMIC" or dest not in m2a:
                    wp = Warp(x, y, None, "vanilla", vanilla=w)
                    wp.dest_map, wp.dest_id = dest, w["dest_warp_id"]
                    ws.append(wp)
                    if hit:
                        claimed.add(hit[0])
                    continue
                if not hit:
                    continue                       # cut by the wiki
                claimed.add(hit[0])
                d = doors[hit[0]]
                ws.append(Warp(x, y, d[2], d[3], vanilla=w, kind=d[4]))
            for i, d in enumerate(doors):
                if i not in claimed and not any((w.x, w.y) == (d[0], d[1]) for w in ws):
                    ws.append(Warp(d[0], d[1], d[2], d[3], kind=d[4]))
            lists[a.id] = ws
        else:
            lists[a.id] = [Warp(d[0], d[1], d[2], d[3], kind=d[4]) for d in doors]
    # vanilla warp index -> its index in the new list, for maps that keep vanilla warps
    vmap = {}
    for a in areas.values():
        if a.mode in ("vanilla", "hybrid"):
            v = B.base_map(a.replaces).get("warp_events") or []
            vmap[a.id] = {i: j for j, w in enumerate(lists[a.id]) for i, vw in enumerate(v) if w.vanilla is vw}
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
                # vanilla's own destination, when it still exists on that map
                if w.vanilla is not None and w.vanilla["dest_map"] == areas[to].map_const and to in vmap:
                    j = vmap[to].get(int(w.vanilla["dest_warp_id"]))
                    if j is not None:
                        w.dest_id = str(j)
                        continue
                if back:
                    w.dest_id = str(back[min(k, len(back) - 1)])
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

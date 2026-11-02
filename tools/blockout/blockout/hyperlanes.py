"""The planet graph: wiki/mapping/hyperlanes.csv, one row per ship link between two planets.

Each edge names its two ends: an overworld area on each planet and the ship room (hangar, cabin, shuttle
station) the player boards in. A shared cabin (the Falcon) is the room at both ends. An empty room means the
ship lands in the open (a beach): the area carries a `travel` row with `via: ship` instead.

`check(areas)` lists what is missing or inconsistent, so a planet can never be left without a way in or out:
  - both areas and rooms exist, and the area has a door or warp into the room and the room a warp back out;
  - both ends are placed on their planet map (`pos`); a hangar building has a sign within three cells of its door;
  - the unlock is one the progression table knows (flag:badge0N-get, item:hm-*, event:<timeline id>, ...).
`entry_badges(edges)` walks the graph from Tatooine and gives the badge count a player has on first landing
on each planet (the max unlock along the easiest path), for the balance report.
"""
import csv

from . import vanilla as V

PATH = V.ROOT / "wiki" / "mapping" / "hyperlanes.csv"

# how many badges a player holds when a gate opens (Emerald's order; story events by their timeline id)
BADGE_OF = {"flag:returned-devon-goods": 1, "item:hm-cut": 1, "item:hm-flash": 2, "item:hm-rock-smash": 3,
            "event:meteor-falls-meteorite": 3, "event:mt-chimney": 3, "item:hm-strength": 4, "item:hm-surf": 5,
            "item:hm-fly": 6, "event:devon-scope": 6, "item:hm-dive": 7, "event:sootopolis-crisis": 7,
            "item:hm-waterfall": 7, "event:sky-pillar-rayquaza": 7, "flag:sys-game-clear": 8, "item:ss-ticket": 8,
            "item:eon-ticket": 8, "item:old-sea-map": 8, "item:aurora-ticket": 8, "item:mystic-ticket": 8}


def load():
    return list(csv.DictReader(open(PATH)))


def badge_of(unlock):
    """Badges held when `unlock` (a|b|c, all needed) opens; None if a gate is unknown."""
    worst = 0
    for g in [u for u in (unlock or "").split("|") if u]:
        if g.startswith("flag:badge") and g.endswith("-get"):
            worst = max(worst, int(g[len("flag:badge"):len("flag:badge") + 2]))
        elif g in BADGE_OF:
            worst = max(worst, BADGE_OF[g])
        else:
            return None
    return worst


def _door_cells(area, room):
    """Cells of the doors in `area` that lead into `room`."""
    out = []
    for b in area.buildings:
        if b.get("to") == room and "door" in b:
            (x, y), (w, h) = b["at"], b["size"]
            out.append((x + int(b["door"]), y + h))   # the walkable cell in front of the door
    for w_ in area.warps:
        if w_.get("to") == room:
            out.append(tuple(w_["at"]))
    return out


def _end_problems(e, side, by_id):
    area_id, room_id, planet = e[f"{side}_area"], e[f"{side}_room"], e[f"{side}_planet"]
    p = []
    area = by_id.get(area_id)
    if area is None:
        return [f"{side} area {area_id} does not exist"]
    if area.planet != planet:
        p.append(f"{side} area {area_id} is on {area.planet}, not {planet}")
    if area.kind in ("town", "route", "landmark", "space") and area.pos is None:
        p.append(f"{side} area {area_id} is not placed on the {planet} map (no pos)")
    if room_id:
        room = by_id.get(room_id)
        if room is None:
            return p + [f"{side} room {room_id} does not exist"]
        doors = _door_cells(area, room_id)
        if not doors:
            p.append(f"{area_id} has no door or warp into {room_id}")
        if not any(w.get("to") == area_id for w in room.warps):
            p.append(f"{room_id} has no warp back out to {area_id}")
    else:
        doors = [tuple(t.get("at")) for t in area.travel if t.get("via") == "ship" and t.get("at")]
        if not any(t.get("via") == "ship" for t in area.travel):
            p.append(f"{area_id} has no room and no `travel` row with via: ship")
    building_doors = [(x + int(b["door"]), y + h) for b in area.buildings if b.get("to") == room_id and "door" in b
                      for (x, y), (w, h) in [(b["at"], b["size"])]]
    doors = building_doors   # a warp (cave mouth, ramp, lift) is the path itself; a hangar building can be walked past
    if doors and area.kind in ("town", "route", "landmark", "space"):
        near = any(abs(s["at"][0] - x) + abs(s["at"][1] - y) <= 3 for s in area.signs for x, y in doors if s.get("at"))
        if not near:
            p.append(f"{area_id}: no sign within 3 cells of the door into {room_id or 'the landing'} (the player must see where the ship is)")
    return p


def check(by_id, edges=None):
    """Problems with the planet graph, as strings."""
    edges = load() if edges is None else edges
    p = []
    planets = {x.planet for x in by_id.values()} - {"SHARED"}
    linked = {"TATOOINE"}
    for e in edges:
        for side in ("from", "to"):
            p += [f"{e['id']}: {q}" for q in _end_problems(e, side, by_id)]
        if badge_of(e["unlock"]) is None:
            p.append(f"{e['id']}: unknown unlock {e['unlock']!r} (add it to BADGE_OF in hyperlanes.py)")
        linked |= {e["from_planet"], e["to_planet"]}
    for pl in sorted(planets - linked):
        p.append(f"planet {pl} has no hyperlane: no way in or out")
    return p


def entry_badges(edges=None):
    """Badges held on first landing on each planet, walking every edge both ways from Tatooine."""
    edges = load() if edges is None else edges
    entry = {"TATOOINE": 0}
    changed = True
    while changed:
        changed = False
        for e in edges:
            need = badge_of(e["unlock"]) or 0
            for a, b in ((e["from_planet"], e["to_planet"]), (e["to_planet"], e["from_planet"])):
                if a in entry:
                    v = max(entry[a], need)
                    if v < entry.get(b, 99):
                        entry[b] = v
                        changed = True
    return entry

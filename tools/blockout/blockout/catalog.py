"""Every vanilla map, sorted into the Star Wars world: which planet, which area id, which folder.

The link is the map's `region_map_section` (MAPSEC_ROUTE_102 -> location:route-102 in
wiki/mapping/locations.csv), which gives the planet and the Star Wars name. A map's area id is that
name in kebab case plus what is left of the vanilla map name (GraniteCave_B1F -> shadowlands-b1f),
with vanilla-only words swapped for this game's (PokemonCenter -> bacta-center)."""
import csv
import glob
import json
import os
import re

from .vanilla import GAME, ROOT

SWAPS = [  # vanilla words in map names -> this game's words (applied to the kebab-case suffix)
    ("pokemon-center", "bacta-center"), ("poke-mart", "supply-depot"), ("mart", "supply-depot"),
    ("gym", "arena"), ("brendans-house", "player-home"), ("mays-house", "korr-home"),
    ("professor-birchs-lab", "lab"), ("pokemon-league", "temple"), ("pokemon-fan-club", "fan-club"),
    ("contest-hall", "showcase-hall"), ("contest-lobby", "showcase-lobby"), ("stevens-room", "leias-room"),
    ("stevens-cave", "hidden-cave"), ("pokemon-day-care", "creature-nursery"), ("department-store", "galleria"),
    ("cable-car-station", "shuttle-station"), ("trick-house", "puzzle-house"), ("game-corner", "sabacc-den"),
    ("bike-shop", "speeder-shop"), ("pretty-petal-flower-shop", "flower-shop"), ("weather-institute", "endor-station"),
    ("space-center", "launch-tower"), ("pokemon-school", "academy"), ("devon-corp", "organa-tower"),
    ("oceanic-museum", "spacer-museum"), ("harbor", "hangar"), ("lilycove-museum", "museum"),
    ("battle-tent", "battle-tent"), ("trainer-hill", "trial-spire"), ("mr-brineys-house", "han-hangar"),
]
KIND = {"MAP_TYPE_TOWN": "town", "MAP_TYPE_CITY": "town", "MAP_TYPE_ROUTE": "route", "MAP_TYPE_OCEAN_ROUTE": "route",
        "MAP_TYPE_UNDERGROUND": "dungeon", "MAP_TYPE_UNDERWATER": "dungeon", "MAP_TYPE_INDOOR": "interior"}
# event islands whose vanilla map type is not an overworld type, but which are walked outdoors
OUTDOOR = {"BirthIsland_Exterior": "landmark", "NavelRock_Exterior": "landmark",
           "FarawayIsland_Entrance": "landmark", "FarawayIsland_Interior": "landmark"}
FOLDER = {"town": "", "route": "", "landmark": "", "dungeon": "caves", "interior": "interiors"}


def kebab(s):
    s = s.replace("'", "")
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    s = re.sub(r"([A-Za-z])(\d)", r"\1-\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", s)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s)
    return s.strip("-").lower()


def locations():
    out = {}
    for r in csv.DictReader(open(ROOT / "wiki/mapping/locations.csv")):
        out[r["emerald_id"].replace("location:", "")] = r
    return out


def _mapsec_to_loc(mapsec):
    return kebab(mapsec.replace("MAPSEC_", "").title().replace("_", ""))


def maps():
    """name -> dict(map, area, planet, kind, folder, sw_name, location, mapsec, map_type)."""
    locs = locations()
    out = {}
    for f in sorted(glob.glob(str(GAME / "data/maps/*/map.json"))):
        mj = json.load(open(f))
        name = os.path.basename(os.path.dirname(f))
        mt = mj["map_type"]
        if mt == "MAP_TYPE_SECRET_BASE" or "Unused" in name or "Prototype" in name:
            continue
        loc_id = _mapsec_to_loc(mj["region_map_section"])
        loc_id = re.sub(r"-(\d+)$", r"-\1", loc_id)
        loc = locs.get(loc_id) or locs.get(loc_id.replace("route-", "route-")) or {}
        sw = loc.get("sw_name") or loc_id.replace("-", " ").upper()
        planet = loc.get("planet") or "UNSORTED"
        kind = OUTDOOR.get(name) or KIND.get(mt, "interior")
        base = kebab(sw)
        prefix, _, rest = name.partition("_")
        suffix = kebab(rest)
        if kind in ("town", "route") and not suffix:
            area = base
        else:
            if not rest:
                suffix = kebab(prefix)
                if kebab(prefix).replace("-", "") == base.replace("-", "") or kind == "dungeon":
                    suffix = ""
            for a, b in SWAPS:
                suffix = re.sub(rf"(^|-){a}(-|$)", rf"\g<1>{b}\g<2>", suffix)
            area = f"{base}-{suffix}" if suffix else base
        if prefix == "Underwater":
            area = f"underwater-{kebab(rest)}"
        area = re.sub(r"(\d)-([fr])(?=-|$)", r"\1\2", area)          # 1-f -> 1f, b1-f -> b1f, 2-f-1-r -> 2f-1r
        area = re.sub(r"(^|-)b-(\d)", r"\1b\2", area)                     # b-1f -> b1f
        if planet == "UNSORTED" and mj["region_map_section"] == "MAPSEC_DYNAMIC":
            planet = "GRAND ARENA" if name.startswith("BattlePyramid") else "SHARED"
            area = kebab(name)
            for a, b in SWAPS:
                area = re.sub(rf"(^|-){a}(-|$)", rf"\g<1>{b}\g<2>", area)
        out[name] = {"map": name, "area": area, "planet": planet, "kind": kind, "folder": FOLDER[kind],
                     "sw_name": sw, "location": loc_id, "mapsec": mj["region_map_section"], "map_type": mt}
    # make ids unique
    seen = {}
    for name, m in out.items():
        seen.setdefault(m["area"], []).append(name)
    for area, names in seen.items():
        if len(names) > 1:
            for n in names:
                out[n]["area"] = f"{area}-{kebab(n)}"
    return out


def path_for(m):
    planet = m["planet"].lower().replace(" ", "-")
    parts = [ROOT, "wiki", "world", planet] + ([m["folder"]] if m["folder"] else []) + [m["area"] + ".yaml"]
    return os.path.join(*map(str, parts))

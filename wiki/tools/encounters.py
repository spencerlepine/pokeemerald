#!/usr/bin/env python3
"""Wild encounter tables for the Star Wars world -> database/encounters.csv.

Emerald's tables (emerald/wild_encounters.csv) are the balance: every map, method, slot, rate and level range
stays. Only the species in a slot changes, three ways, in this order:
  1. the Dune Sea (database/dune_sea_encounters.csv, built by tools/sand_skim.py): Tatooine's water slots;
  2. habitat swaps (mapping/habitat_swaps.csv): on a planet, a foreign species gives its slot to a native one
     (`planet`, `from_species`, `to_species`, optional `maps` and `methods`, pipe-separated; `reason`);
  3. new-area tables (mapping/wild_extra.csv): slots for areas Emerald does not have (the Hoth tundra).

Checks: every species and map is known, a swap's `from_species` really sits on those maps, the target's
home planet is the swap's planet, and the base stat total moves by at most 150. Then tools/habitats.py reads
the result, so species_habitats.csv explains what the player actually meets.

  python3 tools/encounters.py            # database/encounters.csv (+ warnings, exit 1 if any)
  python3 tools/encounters.py --install  # also write the species into ../game/src/data/wild_encounters.json

The install changes only species (rates and levels are the game's), matching each slot by the Emerald species it
still holds, and adds the tables of the new areas (wild_extra.csv) as new headers. Run tools/sand_skim.py first:
its Dune Sea tables are already in the game and are left as they are.
"""
import collections
import csv
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMERALD = Path(os.environ.get("EMERALD_DB_DIR", ROOT / "emerald"))
DB, MAPPING = ROOT / "database", ROOT / "mapping"
COLS = ["map_id", "planet", "method", "slot", "slot_rate_percent", "min_level", "max_level", "emerald_species",
        "sw_species", "sw_name", "source", "stat_change", "reason"]
MAX_STAT_CHANGE = 150


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    warnings = []
    warn = warnings.append
    planet = {r["map_id"]: r["planet"] for r in read(DB / "area_progression.csv")}
    species = {r["emerald_id"]: r for r in read(MAPPING / "species.csv")}
    bst = {r["id"]: int(r["base_stat_total"] or 0) for r in read(DB / "entities.csv") if r["id"].startswith("species:")}
    # a net-new species in a free slot has no Emerald stats: its total is in its design row ("... = 410")
    by_name = {r["sw_name"]: sid for sid, r in species.items()}
    for n in read(DB / "net_new.csv"):
        m = re.search(r"=\s*(\d{3})\b", n["description"]) if n["entity_type"] == "species" else None
        if m and n["sw_name"] in by_name:
            bst[by_name[n["sw_name"]]] = int(m.group(1))
    rows = [r for r in read(EMERALD / "wild_encounters.csv") if r["group"] == "gWildMonHeaders"]
    for r in rows:
        r["source"], r["sw_species"], r["reason"] = "emerald", r["species_id"], ""
    if (MAPPING / "wild_extra.csv").exists():
        for r in read(MAPPING / "wild_extra.csv"):
            if r["map_id"] not in planet:
                warn(f"wild_extra: {r['map_id']} is not in database/area_progression.csv")
            rows.append({**r, "source": "new", "sw_species": r["species_id"], "reason": r.get("note", "")})
    # 1. the Dune Sea
    dune = {(r["map_id"], r["method"], r["slot"]): r for r in read(DB / "dune_sea_encounters.csv")} \
        if (DB / "dune_sea_encounters.csv").exists() else {}
    for r in rows:
        d = dune.get((r["map_id"], "skim" if r["method"] == "water" else r["method"], r["slot"]))
        if d and d["dune_species"]:
            r["sw_species"], r["source"], r["reason"] = d["dune_species"], "dune-sea", d["note"]
    # 2. habitat swaps
    by_map = collections.defaultdict(list)
    for r in rows:
        by_map[r["map_id"]].append(r)
    for s in read(MAPPING / "habitat_swaps.csv"):
        src, dst = s["from_species"], s["to_species"]
        if src not in species or dst not in species:
            warn(f"habitat_swaps: unknown species {src} -> {dst}")
            continue
        home = species[dst]["home_planet"]
        if home and home != s["planet"]:
            warn(f"habitat_swaps: {dst} ({species[dst]['sw_name']}) is from {home}, swapped in on {s['planet']}")
        maps = [m for m in s["maps"].split("|") if m] or [m for m, p in planet.items() if p == s["planet"]]
        methods = {m for m in s["methods"].split("|") if m}
        hit = 0
        for m in maps:
            if m not in planet:
                warn(f"habitat_swaps: {m} is not a map")
            for r in by_map.get(m, []):
                if r["sw_species"] == src and (not methods or r["method"] in methods) and r["source"] != "dune-sea":
                    r["sw_species"], r["source"], r["reason"] = dst, "habitat-swap", s["reason"]
                    hit += 1
        if not hit:
            warn(f"habitat_swaps: {src} is not on any {s['planet']} map{' with method ' + s['methods'] if methods else ''}")
    out = []
    for r in rows:
        a, b = bst.get(r["species_id"], 0), bst.get(r["sw_species"], 0)
        change = (b - a) if (a and b) else 0
        if abs(change) > MAX_STAT_CHANGE:
            warn(f"{r['map_id']} {r['method']} slot {r['slot']}: {r['species_id']} -> {r['sw_species']} moves the stat total by {change}")
        out.append({"map_id": r["map_id"], "planet": planet.get(r["map_id"], ""), "method": r["method"], "slot": r["slot"],
                    "slot_rate_percent": r["slot_rate_percent"], "min_level": r["min_level"], "max_level": r["max_level"],
                    "emerald_species": r["species_id"], "sw_species": r["sw_species"],
                    "sw_name": species.get(r["sw_species"], {}).get("sw_name", ""), "source": r["source"],
                    "stat_change": change if a and b else "", "reason": r["reason"]})
    out.sort(key=lambda r: (r["planet"], r["map_id"], r["method"], int(r["slot"])))
    with open(DB / "encounters.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows(out)
    c = collections.Counter(r["source"] for r in out)
    print(f"{len(out)} slots -> database/encounters.csv: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
    for w_ in warnings:
        print("  !", w_)
    return 1 if warnings else 0


METHODS = {"land": "land_mons", "water": "water_mons", "rock_smash": "rock_smash_mons"}
RODS = {"old_rod": 0, "good_rod": 2, "super_rod": 5}


def install():
    """Write database/encounters.csv's species into ../game (see the module doc). Returns the problems."""
    import json
    sys.path.insert(0, str(ROOT / "tools"))
    import sand_skim as SK
    gj = ROOT.parent / "game/src/data/wild_encounters.json"
    text = gj.read_text()
    data = json.loads(text)
    assert SK.dump_json(data) == text, "wild_encounters.json layout changed; fix sand_skim.dump_json"
    enc = read(DB / "encounters.csv")
    label_map = {r["base_label"]: r["map_id"] for r in read(EMERALD / "wild_encounters.csv")}
    by = {(r["map_id"], r["method"], int(r["slot"])): r for r in enc}
    problems, changed = [], 0
    heads = data["wild_encounter_groups"][0]["encounters"]
    for h in heads:
        mid = label_map.get(h["base_label"])
        if not mid:
            continue
        for method, field in [*METHODS.items(), *((m, "fishing_mons") for m in RODS)]:
            mons = (h.get(field) or {}).get("mons") or []
            slots = range(len(mons)) if field != "fishing_mons" else range(RODS[method], RODS[method] + (2, 3, 5)[list(RODS).index(method)])
            for i in slots:
                if i >= len(mons):
                    continue
                r = by.get((mid, method, i))
                if not r or r["source"] in ("emerald", "dune-sea"):
                    continue
                want = "SPECIES_" + SK.key(r["sw_species"])
                if mons[i]["species"] == want:
                    continue
                if mons[i]["species"] != "SPECIES_" + SK.key(r["emerald_species"]):
                    problems.append(f"{h['base_label']} {method} {i}: game has {mons[i]['species']}, not "
                                    f"{r['emerald_species']}; left as is")
                    continue
                mons[i]["species"] = want
                changed += 1
    # new areas: one header each, after Emerald's
    new = collections.defaultdict(list)
    for r in enc:
        if r["source"] == "new":
            new[r["map_id"]].append(r)
    rates = collections.defaultdict(dict)
    for r in read(MAPPING / "wild_extra.csv"):
        rates[r["map_id"]][r["method"]] = int(r["area_rate"])
    for mid, rows in new.items():
        area = mid.split(":", 1)[1]
        const = "MAP_SW_" + area.upper().replace("-", "_")
        label = "gSw" + "".join(w.capitalize() for w in area.split("-"))
        h = {"map": const, "base_label": label}
        def mons(rs):
            return [{"min_level": int(r["min_level"]), "max_level": int(r["max_level"]),
                     "species": "SPECIES_" + SK.key(r["sw_species"])} for r in sorted(rs, key=lambda r: int(r["slot"]))]
        for method, field in METHODS.items():
            rs = [r for r in rows if r["method"] == method]
            if rs:
                h[field] = {"encounter_rate": rates[mid][method], "mons": mons(rs)}
        rods = [x for m in RODS for x in mons([r for r in rows if r["method"] == m])]   # old, good, super
        if rods:
            if len(rods) != 10:
                problems.append(f"{mid}: {len(rods)} rod slots, the game needs 10 (2 old, 3 good, 5 super)")
            else:
                h["fishing_mons"] = {"encounter_rate": rates[mid].get("old_rod") or rates[mid].get("good_rod"),
                                     "mons": rods}
        old = [i for i, x in enumerate(heads) if x["base_label"] == label]
        if old:
            if heads[old[0]] != h:
                heads[old[0]] = h
                changed += 1
        else:
            heads.append(h)
            changed += 1
    if changed:
        gj.write_text(SK.dump_json(data))
    print(f"installed into ../game: {changed} changes")
    return problems


if __name__ == "__main__":
    rc = main()
    if "--install" in sys.argv:
        for p_ in install():
            print("  !", p_)
            rc = 1
    sys.exit(rc)

"""SAND SKIM, the Dune Sea field move (bible/NET_NEW_DESIGNS.md, section Dune Sea).

Reads the hand-written rules and swaps in mapping/, the species types and TM/HM learnsets from ../game, the
Emerald wild tables and balance table in emerald/, and the world layouts in world/. Writes:

  database/sand_skim.csv           every species: types, SURF (for comparison), SAND SKIM yes/no and the rule
  database/dune_sea_encounters.csv the Dune Sea's own table on each Tatooine map (Emerald's sea table with the
                                   sea species swapped); there is no fishing on the Dune Sea

and prints the balance checks (learners catchable before badge 5, no species losing its last wild home) and
whether ../game matches. With --install it writes the tables into ../game/src/data/wild_encounters.json (sea
species swapped, fishing tables removed) and the map list into ../game/src/data/dune_sea_maps.h, which
CanFish() in src/item_use.c reads to refuse the rod.

Edit mapping/sand_skim_rules.csv or mapping/dune_sea_swaps.csv, then re-run: python3 tools/sand_skim.py [--install]
"""
import csv, glob, json, re, sys
from pathlib import Path

import yaml

WIKI = Path(__file__).resolve().parents[1]
GAME = WIKI.parent / "game"


SEA = ("water",)
RODS = ("old_rod", "good_rod", "super_rod")
GAME_JSON = GAME / "src/data/wild_encounters.json"
GAME_MAPS_H = GAME / "src/data/dune_sea_maps.h"


def read(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def write(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "rows ->", p.relative_to(WIKI))


def game_species():
    src = (GAME / "src/data/pokemon/species_info.h").read_text()
    types, bst = {}, {}
    for m in re.finditer(r"\[SPECIES_(\w+)\]\s*=\s*\{(.*?)\n\s*\},", src, re.S):
        body = m.group(2)
        t = re.search(r"\.types\s*=\s*\{\s*TYPE_(\w+),\s*TYPE_(\w+)", body)
        if t:
            types[m.group(1)] = list(dict.fromkeys(t.groups()))
        stats = [re.search(rf"\.base{k}\s*=\s*(\d+)", body) for k in ("HP", "Attack", "Defense", "Speed", "SpAttack", "SpDefense")]
        if all(stats):
            bst[m.group(1)] = sum(int(s.group(1)) for s in stats)
    tm = (GAME / "src/data/pokemon/tmhm_learnsets.h").read_text()
    learn = {m.group(1): set(re.findall(r"\.(\w+)\s*=\s*TRUE", m.group(2)))
             for m in re.finditer(r"\[SPECIES_(\w+)\]\s*=\s*\{\s*\.learnset\s*=\s*\{(.*?)\}\s*\}", tm, re.S)}
    return types, bst, learn


def key(species_id):            # species:nidoran-f -> NIDORAN_F
    return species_id.split(":", 1)[1].upper().replace("-", "_")


def map_planets():
    """map:route103 -> TATOOINE, from the world layouts' `replaces`."""
    out = {}
    for f in glob.glob(str(WIKI / "world" / "**" / "*.yaml"), recursive=True):
        d = yaml.safe_load(open(f))
        rep = d.get("replaces")
        if rep and rep != "new":
            out["map:" + re.sub(r"(?<=[a-z])(?=[A-Z])", "-", rep).replace("_", "-").lower()] = d["planet"]
    return out


def game_const(map_id):        # map:petalburg-city -> MAP_PETALBURG_CITY
    return "MAP_" + map_id.split(":", 1)[1].upper().replace("-", "_")


def dump_json(d):
    """json.dumps in the layout of the game's wild_encounters.json (round-trips the file unchanged)."""
    out = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    out = re.sub(r'"encounter_rates": \[\s*([\d,\s]+?)\s*\]', lambda m: '"encounter_rates": [\n            '
                 + ", ".join(re.findall(r"\d+", m.group(1))) + "\n          ]", out)
    return re.sub(r'"(\w+_rod)": \[\s*([\d,\s]+?)\s*\]', lambda m: f'"{m.group(1)}": ['
                  + ", ".join(re.findall(r"\d+", m.group(2))) + "]", out)


def game_sync(dune_maps, enc, install):
    """Compare (or with --install, write) the Dune Sea tables and map list in ../game."""
    text = GAME_JSON.read_text()
    data = json.loads(text)
    assert dump_json(data) == text, "wild_encounters.json layout changed; fix dump_json before installing"
    want = {}
    for e in enc:
        want.setdefault(game_const(e["map_id"]), {})[int(e["slot"])] = "SPECIES_" + key(e["dune_species"])
    diffs = []
    for g in data["wild_encounter_groups"]:
        for h in g["encounters"]:
            if h.get("map") not in want:
                continue
            if "fishing_mons" in h:
                diffs.append(f"{h['map']}: fishing table still there")
                if install:
                    del h["fishing_mons"]
            for i, mon in enumerate(h.get("water_mons", {}).get("mons", [])):
                if mon["species"] != want[h["map"]][i]:
                    diffs.append(f"{h['map']} skim slot {i}: {mon['species']} -> {want[h['map']][i]}")
                    if install:
                        mon["species"] = want[h["map"]][i]
    header = ("// The Dune Sea maps (Tatooine): the rod can't be cast here. Written by wiki/tools/sand_skim.py --install;\n"
              "// the list and the encounter tables come from the wiki (bible/NET_NEW_DESIGNS.md, Dune Sea and SAND SKIM).\n"
              "static const u16 sDuneSeaMaps[] =\n{\n" + "".join(f"    {game_const(m)},\n" for m in dune_maps) + "};\n")
    if not GAME_MAPS_H.exists() or GAME_MAPS_H.read_text() != header:
        diffs.append(f"{GAME_MAPS_H.relative_to(GAME)} differs from the Dune Sea map list")
    if install and diffs:
        GAME_JSON.write_text(dump_json(data))
        GAME_MAPS_H.write_text(header)
        nn = WIKI / "database" / "net_new.csv"
        rows = read(nn)
        for r in rows:
            if r["id"] == "net:dune-sea-encounters":
                r["game_status"] = "DONE"
        write(nn, rows, list(rows[0].keys()))
        print(f"installed into ../game: {len(diffs)} changes")
    elif diffs:
        print(f"../game does not match the Dune Sea tables ({len(diffs)} differences); run with --install:")
        for d in diffs[:12]:
            print("  ", d)
    else:
        print("../game matches the Dune Sea tables")


def main():
    types, bst, learn = game_species()
    sw = {r["emerald_id"]: r for r in read(WIKI / "mapping" / "species.csv")}
    rules = read(WIKI / "mapping" / "sand_skim_rules.csv")
    by_type = {r["value"]: r for r in rules if r["kind"] == "type"}
    by_species = {r["value"]: r for r in rules if r["kind"] == "species"}
    planets = map_planets()
    badges = {r["map_id"]: r["badges_expected"] for r in read(WIKI / "emerald" / "area_progression.csv")}
    wild = read(WIKI / "emerald" / "wild_encounters.csv")

    # where each species can first be caught: (badges, planet, map)
    first = {}
    for w in wild:
        b = badges.get(w["map_id"], "")
        cand = (int(b) if b.isdigit() else 99, planets.get(w["map_id"], "?"), w["map_id"], w["method"])
        if w["species_id"] not in first or cand < first[w["species_id"]]:
            first[w["species_id"]] = cand

    rows = []
    for sid, r in sw.items():
        k = key(sid)
        if k not in types:
            continue
        t = types[k]
        rule = by_species.get(k) or next((by_type[x] for x in t if x in by_type), None)
        can_tm = bool(learn.get(k))
        yes = bool(rule) and rule["learns"] == "YES" and can_tm
        why = rule["reason"] if rule else ""
        if rule and not can_tm:
            why = "Learns no TM or HM at all."
        f = first.get(sid)
        rows.append({"emerald_id": sid, "sw_name": r["sw_name"], "types": "/".join(t), "home_planet": r["home_planet"],
                     "stat_total": bst.get(k, ""), "surf": "YES" if "SURF" in learn.get(k, ()) else "",
                     "sand_skim": "YES" if yes else "", "rule": (rule["kind"] + ":" + rule["value"]) if rule else "",
                     "reason": why, "first_wild": f"{f[2]} ({f[1]}, {f[3]}, badges {f[0]})" if f and f[0] != 99 else (f"{f[2]} ({f[1]}, {f[3]})" if f else "")})
    rows.sort(key=lambda x: (x["sand_skim"] != "YES", x["emerald_id"]))
    write(WIKI / "database" / "sand_skim.csv", rows,
          ["emerald_id", "sw_name", "types", "home_planet", "stat_total", "surf", "sand_skim", "rule", "reason", "first_wild"])

    # Dune Sea encounter slots: Tatooine maps, sea table only (no fishing on the Dune Sea)
    swaps = read(WIKI / "mapping" / "dune_sea_swaps.csv")

    def swap_for(w):
        """The most specific row wins: map and slot, then map, then any."""
        best = None
        for s in swaps:
            if s["from_species"] != w["species_id"]:
                continue
            if s["maps"] and w["map_id"] not in s["maps"].split("|"):
                continue
            if s["slots"] and w["slot"] not in s["slots"].split("|"):
                continue
            rank = bool(s["maps"]) + bool(s["slots"])
            if best is None or rank > best[0]:
                best = (rank, s)
        return best[1] if best else None

    has_sea = {}
    for f in glob.glob(str(WIKI / "world" / "tatooine" / "*.yaml")):
        d = yaml.safe_load(open(f))
        m = "map:" + re.sub(r"(?<=[a-z])(?=[A-Z])", "-", d["replaces"]).replace("_", "-").lower() if d["replaces"] != "new" else ""
        if m:
            has_sea[m] = d["grid"].count("~")
    dune_maps = sorted({w["map_id"] for w in wild if planets.get(w["map_id"]) == "TATOOINE" and w["method"] in SEA + RODS})
    enc = []
    for w in wild:
        if w["map_id"] not in dune_maps or w["method"] != "water":
            continue
        s = swap_for(w)
        to = s["to_species"] if s else w["species_id"]
        enc.append({"map_id": w["map_id"], "method": "skim", "slot": w["slot"],
                    "rate_percent": w["slot_rate_percent"], "min_level": w["min_level"], "max_level": w["max_level"],
                    "emerald_species": w["species_id"], "dune_species": to,
                    "sw_name": sw.get(to, {}).get("sw_name", ""),
                    "stat_total_change": bst.get(key(to), 0) - bst.get(key(w["species_id"]), 0),
                    "note": (s["reason"] if s else "Kept: fits the Dune Sea as is.")
                    + ("" if has_sea.get(w["map_id"]) else " The new layout has no Dune Sea cells here, so in the finished game this table never runs.")})
    write(WIKI / "database" / "dune_sea_encounters.csv", enc,
          ["map_id", "method", "slot", "rate_percent", "min_level", "max_level", "emerald_species", "dune_species",
           "sw_name", "stat_total_change", "note"])
    game_sync(dune_maps, enc, install="--install" in sys.argv)

    # balance checks
    yes = [r for r in rows if r["sand_skim"] == "YES"]
    early = sorted({(sw[r["emerald_id"]]["sw_name"], first[r["emerald_id"]][2], first[r["emerald_id"]][1]) for r in yes
                    if r["emerald_id"] in first and first[r["emerald_id"]][0] <= 4})
    print(f"SAND SKIM learners: {len(yes)} species; catchable before badge 5 (when the HM is given): {len(early)}")
    for n, m, pl in early:
        print("  ", n, m, pl)
    starters = [sw[s]["sw_name"] for s in ("species:marshtomp", "species:swampert", "species:combusken", "species:blaziken")
                if any(r["emerald_id"] == s for r in yes)]
    print("  starter evolutions that learn it:", ", ".join(starters))
    after = {(w["map_id"], w["method"], w["slot"]): w["species_id"] for w in wild}
    for k in [k for k in after if k[0] in dune_maps and k[1] in RODS]:
        del after[k]
    for e in enc:
        after[(e["map_id"], "water", e["slot"])] = e["dune_species"]
    still = set(after.values())
    lost = {w["species_id"] for w in wild if w["map_id"] in dune_maps and w["method"] in SEA + RODS} - still
    for s in sorted(lost):
        print(f"  PROBLEM: {sw[s]['sw_name']} ({s}) is no longer wild anywhere")
    if not lost:
        print("  every species fished or met on the Dune Sea maps is still wild somewhere")
    worst = max(enc, key=lambda e: abs(e["stat_total_change"]))
    print(f"  largest stat-total change in a Dune Sea slot: {worst['stat_total_change']} ({worst['emerald_species']} -> {worst['dune_species']})")


if __name__ == "__main__":
    main()

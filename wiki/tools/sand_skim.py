"""SAND SKIM, the Dune Sea field move (bible/NET_NEW_DESIGNS.md, section Dune Sea).

Reads the hand-written rules and swaps in mapping/, the species types and TM/HM learnsets from ../game (read
only), the Emerald wild tables and balance table in emerald/, and the world layouts in world/. Writes:

  database/sand_skim.csv           every species: types, SURF (for comparison), SAND SKIM yes/no and the rule
  database/dune_sea_encounters.csv Tatooine's sea and fishing slots on the Dune Sea, with the stat-total change

and prints the balance checks (learners catchable before badge 5, species still wild elsewhere).
Edit mapping/sand_skim_rules.csv to add a type or a species, then re-run: python3 tools/sand_skim.py
"""
import csv, glob, re
from pathlib import Path

import yaml

WIKI = Path(__file__).resolve().parents[1]
GAME = WIKI.parent / "game"


def read(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def write(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
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

    # Dune Sea encounter slots: Tatooine maps, sea and fishing methods
    swap = {s["from_species"]: s for s in read(WIKI / "mapping" / "dune_sea_swaps.csv")}
    has_sea = {}
    for f in glob.glob(str(WIKI / "world" / "tatooine" / "*.yaml")):
        d = yaml.safe_load(open(f))
        m = "map:" + re.sub(r"(?<=[a-z])(?=[A-Z])", "-", d["replaces"]).replace("_", "-").lower() if d["replaces"] != "new" else ""
        if m:
            has_sea[m] = d["grid"].count("~")
    enc = []
    for w in wild:
        if planets.get(w["map_id"]) != "TATOOINE" or w["method"] not in ("water", "old_rod", "good_rod", "super_rod"):
            continue
        s = swap.get(w["species_id"])
        to = s["to_species"] if s else w["species_id"]
        enc.append({"map_id": w["map_id"], "method": "skim" if w["method"] == "water" else w["method"], "slot": w["slot"],
                    "rate_percent": w["slot_rate_percent"], "min_level": w["min_level"], "max_level": w["max_level"],
                    "emerald_species": w["species_id"], "dune_species": to,
                    "sw_name": sw.get(to, {}).get("sw_name", ""),
                    "stat_total_change": bst.get(key(to), 0) - bst.get(key(w["species_id"]), 0),
                    "note": (s["reason"] if s else "Kept: fits the Dune Sea as is.")
                    + ("" if has_sea.get(w["map_id"]) else " The area has no Dune Sea cells now, so this table never runs.")})
    write(WIKI / "database" / "dune_sea_encounters.csv", enc,
          ["map_id", "method", "slot", "rate_percent", "min_level", "max_level", "emerald_species", "dune_species",
           "sw_name", "stat_total_change", "note"])

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
    gone = {w["species_id"] for w in wild if planets.get(w["map_id"]) == "TATOOINE" and w["species_id"] in swap
            and w["method"] in ("water", "old_rod", "good_rod", "super_rod")}
    for s in sorted(gone):
        elsewhere = sorted({planets.get(w["map_id"], "?") for w in wild if w["species_id"] == s and planets.get(w["map_id"]) != "TATOOINE"})
        print(f"  {sw[s]['sw_name']:11} still wild on: {', '.join(elsewhere) or 'NOWHERE (problem)'}")
    worst = max(enc, key=lambda e: abs(e["stat_total_change"]))
    print(f"  largest stat-total change in a Dune Sea slot: {worst['stat_total_change']} ({worst['emerald_species']} -> {worst['dune_species']})")


if __name__ == "__main__":
    main()

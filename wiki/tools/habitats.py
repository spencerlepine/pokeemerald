#!/usr/bin/env python3
"""E2 habitat check: where each companion lives in the Star Wars lore vs. where Emerald's encounter tables put it.

Encounter tables are NOT changed (balance stays identical to Emerald). Instead every species whose home planet
is not one of the planets it is found on gets an explanation:
  RESERVE    only in the Felucia Reserve (Safari Zone), which keeps beasts from many worlds
  FACILITY   only in Grand Arena facilities (Battle Pyramid, Altering/Artisan caves) or the Asteroid Field
  WIDESPREAD found on three or more planets (fishing/surf commons and cave dwellers)
  SEA        a sea species found on the open-water routes between worlds
  MIGRANT / REHOME / STORY   hand decisions in mapping/habitat_notes.csv

Writes database/species_habitats.csv. Run after tools/build.py.
"""
import collections
import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMERALD = Path(os.environ.get("EMERALD_DB_DIR", ROOT / "emerald"))


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    planet = {r["map_id"]: r["planet"] for r in read(ROOT / "database" / "area_progression.csv")}
    species = {r["emerald_id"]: r for r in read(ROOT / "mapping" / "species.csv")}
    notes = {r["emerald_id"]: r for r in read(ROOT / "mapping" / "habitat_notes.csv")}
    found = collections.defaultdict(collections.Counter)
    sea = collections.defaultdict(float)
    for r in read(EMERALD / "wild_encounters.csv"):
        m = r["map_id"]
        p = "FACILITY" if not m else planet.get(m, "")
        if "safari-zone" in m:
            p = "RESERVE"
        if p in ("GRAND ARENA", "ASTEROID FIELD"):
            p = "FACILITY"
        rate = float(r["slot_rate_percent"] or 0)
        found[r["species_id"]][p] += rate
        if r["method"] in ("water", "fishing") or m.startswith("map:underwater") or m.startswith("map:route12") or m.startswith("map:route13"):
            sea[r["species_id"]] += rate
    out, unexplained = [], []
    for sid, s in species.items():
        f = found.get(sid)
        if not f:
            continue
        real = {p: v for p, v in f.items() if p not in ("RESERVE", "FACILITY")}
        wild = "|".join(sorted(f))
        if s["home_planet"] in f:
            dec, note = "HOME", ""
        elif sid in notes:
            dec, note = notes[sid]["decision"], notes[sid]["lore_note"]
        elif not real:
            dec = "RESERVE" if "RESERVE" in f else "FACILITY"
            note = "The Felucia Reserve keeps beasts from many worlds." if dec == "RESERVE" else "Only in Grand Arena facilities."
        elif len(real) >= 3:
            dec, note = "WIDESPREAD", "Found across the galaxy."
        elif sea.get(sid, 0) >= sum(real.values()) * 0.5:
            dec, note = "SEA", "Roams the open water between worlds."
        else:
            dec, note = "UNEXPLAINED", ""
            unexplained.append(sid)
        out.append({"emerald_id": sid, "sw_name": s["sw_name"], "home_planet": s["home_planet"], "wild_planets": wild,
                    "decision": dec, "lore_note": note})
    with open(ROOT / "database" / "species_habitats.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    c = collections.Counter(r["decision"] for r in out)
    print(f"{len(out)} wild species; " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
    for sid in unexplained:
        print("UNEXPLAINED", sid, species[sid]["sw_name"], species[sid]["home_planet"], dict(found[sid]))


if __name__ == "__main__":
    main()

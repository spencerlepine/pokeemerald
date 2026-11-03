"""Copy the Star Wars names from database/entities.csv into ../game.

    python3 tools/port_names.py            # every type below
    python3 tools/port_names.py --dry-run  # only report

For each entity row (HOTSWAP, or KEEP with a different name) of the types in FILES it finds the entry by its C
constant (`source_constant`) and swaps the name string right after it, only if it still holds Emerald's name
(`game_name`). Constants never change: SPECIES_BULBASAUR stays, its name becomes SPROUTLIZ.

  ported / done   the game now shows `sw_name`; the row gets `game_status` DONE in database/entities.csv
  too_long        `sw_name` is longer than the game's buffer (LIMITS): left alone, listed
  Also the Datapad entries: `dex_category` and the 4-line `datapad_text` of every species.
  changed         the game has some other name (edited by hand): left alone, listed
  missing         the constant is not found in the file: left alone, listed
Writes the changed / missing list to database/name_port_report.csv.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(os.environ.get("GAME_DIR", ROOT.parent / "game"))
ENTS = ROOT / "database" / "entities.csv"
REPORT = ROOT / "database" / "name_port_report.csv"

# entity_type -> (file in ../game, or None for the row's source_file; anchor style; name field)
C_KEY = r"\[{c}\]\s*="
FILES = {
    "species": ("src/data/text/species_names.h", C_KEY, r"_\(\"(?P<n>[^\"]*)\"\)"),
    "move": ("src/data/text/move_names.h", C_KEY, r"_\(\"(?P<n>[^\"]*)\"\)"),
    "ability": ("src/data/text/abilities.h", C_KEY, r"_\(\"(?P<n>[^\"]*)\"\)"),
    "game_type": ("src/battle_main.c", C_KEY, r"_\(\"(?P<n>[^\"]*)\"\)"),
    "trainer_class": ("src/data/text/trainer_class_names.h", C_KEY, r"_\(\"(?P<n>[^\"]*)\"\)"),
    "item": ("src/data/items.h", C_KEY, r"\.name\s*=\s*_\(\"(?P<n>[^\"]*)\"\)"),
    "trainer": ("src/data/trainers.h", C_KEY, r"\.trainerName\s*=\s*_\(\"(?P<n>[^\"]*)\"\)"),
    "facility_trainer": (None, C_KEY, r"\.trainerName\s*=\s*_\(\"(?P<n>[^\"]*)\"\)"),
    "contest_opponent": ("src/data/contest_opponents.h", C_KEY, r"\.trainerName\s*=\s*_\(\"(?P<n>[^\"]*)\"\)"),
    "decoration": ("src/data/decoration/header.h", r"\.id\s*=\s*{c}\s*,", r"\.name\s*=\s*_\(\"(?P<n>[^\"]*)\"\)"),
    "location": ("src/data/region_map/region_map_sections.json", r"\"id\":\s*\"{c}\"",
                 r"\"name\":\s*\"(?P<n>[^\"]*)\""),
}
# Longest name each game buffer holds, without the end-of-string byte (é counts as one character).
# items.h stores names in u8 name[ITEM_NAME_LENGTH], so an item name has 13 letters at most.
# A longer sw_name is not ported.
LIMITS = {"species": 10, "move": 12, "item": 13, "ability": 12, "game_type": 6, "trainer_class": 12,
          "trainer": 10, "facility_trainer": 7, "contest_opponent": 7, "decoration": 15, "location": 16}
WINDOW = 800  # the name field must sit this close after the constant


def norm(s: str) -> str:
    return s.replace("{PKMN}", "PKMN").replace("{POKEBLOCK}", "POKéBLOCK")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--types", default=",".join(FILES))
    args = ap.parse_args()
    types = set(args.types.split(","))

    with ENTS.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = rd.fieldnames
        rows = list(rd)

    by_file = defaultdict(list)
    for r in rows:
        t = r["entity_type"]
        if t not in types or not r["source_constant"] or not r["sw_name"] or not r["game_name"]:
            continue
        if r["swap_kind"] not in ("HOTSWAP", "KEEP"):
            continue
        f = FILES[t][0] or r["source_file"].split("|")[0]
        by_file[f].append(r)

    stats, report = Counter(), []
    for f, frows in sorted(by_file.items()):
        path = GAME / f
        src = path.read_text(encoding="utf-8")
        orig = src
        for r in frows:
            _, anchor, field = FILES[r["entity_type"]]
            a = re.search(anchor.format(c=re.escape(r["source_constant"])) + r"(?![A-Z0-9_])", src)
            if not a:
                stats["missing"] += 1
                report.append((r["id"], f, "missing", r["source_constant"]))
                continue
            m = re.compile(field).search(src, a.end(), a.end() + WINDOW)
            if not m:
                stats["missing"] += 1
                report.append((r["id"], f, "missing", "no name field after " + r["source_constant"]))
                continue
            cur, sw, emer = m.group("n"), r["sw_name"], r["game_name"]
            if norm(cur) == norm(sw):
                stats["done"] += 1
                r["game_status"] = "DONE"
                continue
            if norm(cur) != norm(emer):
                stats["changed"] += 1
                report.append((r["id"], f, "changed", cur))
                continue
            if len(norm(sw)) > LIMITS[r["entity_type"]]:
                stats["too_long"] += 1
                report.append((r["id"], f, "too_long", f"{sw} is {len(norm(sw))} letters, the game holds "
                                                          f"{LIMITS[r['entity_type']]}"))
                continue
            src = src[:m.start("n")] + sw + src[m.end("n"):]
            r["game_status"] = "DONE"
            stats["ported"] += 1
        if src != orig and not args.dry_run:
            path.write_text(src, encoding="utf-8")

    if "species" in types:
        port_datapad(rows, stats, report, args.dry_run)

    if not args.dry_run:
        with ENTS.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with REPORT.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["id", "game_file", "result", "detail"])
            w.writerows(sorted(report, key=lambda x: (x[1], x[0])))
    print(", ".join(f"{k}: {v}" for k, v in sorted(stats.items())))
    for x in report[:30]:
        print("  ", *x)
    return 0


ENTRIES = "src/data/pokemon/pokedex_entries.h"
DEX_TEXT = "src/data/pokemon/pokedex_text.h"
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')


def port_datapad(rows, stats, report, dry_run) -> None:
    """Datapad (Pokédex) entries: the category and the 4-line text, from `dex_category` / `datapad_text`
    (mapping/datapad.csv, already wrapped by tools/build.py to fit the Datapad page)."""
    entries = (GAME / ENTRIES).read_text(encoding="utf-8")
    texts = (GAME / DEX_TEXT).read_text(encoding="utf-8")
    e0, t0 = entries, texts
    for r in rows:
        if r["entity_type"] != "species" or not r["datapad_text"] or not r["source_constant"]:
            continue
        dex = "NATIONAL_DEX_" + r["source_constant"].removeprefix("SPECIES_")
        a = re.search(rf"\[{dex}\]\s*=", entries)
        if not a:
            stats["datapad missing"] += 1
            report.append((r["id"], ENTRIES, "missing", dex))
            continue
        cat = re.compile(r'\.categoryName\s*=\s*_\("(?P<n>[^"]*)"\)').search(entries, a.end(), a.end() + 400)
        desc = re.compile(r"\.description\s*=\s*(\w+)").search(entries, a.end(), a.end() + 400)
        new_cat = r["dex_category"].upper()
        if cat and new_cat and cat.group("n") != new_cat:
            entries = entries[:cat.start("n")] + new_cat + entries[cat.end("n"):]
            stats["datapad category ported"] += 1
        t = re.search(rf"\b{desc.group(1)}\[\]\s*=\s*_\(", texts) if desc else None
        if not t:
            stats["datapad missing"] += 1
            report.append((r["id"], DEX_TEXT, "missing", desc.group(1) if desc else "no .description"))
            continue
        end = texts.index(");", t.end())
        cur = "".join(STR.findall(texts[t.end():end]))
        # ASCII quotes end a C string, and the GBA font has curly ones: "gonk" -> “gonk”
        want = re.sub(r'"([^"]*)"', "“\\1”", r["datapad_text"])
        lines = want.split("\\n")
        if cur == want:
            stats["datapad done"] += 1
            continue
        body = "\n" + "\n".join(f'    "{x}\\n"' if i < len(lines) - 1 else f'    "{x}"'
                                for i, x in enumerate(lines))
        texts = texts[:t.end()] + body + texts[end:]
        stats["datapad text ported"] += 1
    if not dry_run:
        if entries != e0:
            (GAME / ENTRIES).write_text(entries, encoding="utf-8")
        if texts != t0:
            (GAME / DEX_TEXT).write_text(texts, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

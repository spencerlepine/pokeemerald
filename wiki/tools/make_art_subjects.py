#!/usr/bin/env python3
"""Write mapping/art_subjects.csv: the Star Wars subject for every overworld sprite and trainer picture.

Hand-written subjects live in mapping/art_subjects_src/*.txt (one "stem|subject" per line). Creature sprites,
dolls and fruit trees are derived from species.csv / items.csv. Run after editing a source file, then build.
Standard library only.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "mapping" / "art_subjects_src"


def table(name):
    out = {}
    for ln in (SRC / name).read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            k, v = ln.split("|", 1)
            out[k.strip()] = v.strip()
    return out


people, misc, cush, pics = table("people.txt"), table("objects.txt"), table("cushions.txt"), table("trainer_pics.txt")
tiles = table("tilesets.txt")
species = {r["emerald_id"].split(":", 1)[1].replace("-", "_"): r["sw_name"]
           for r in csv.DictReader(open(ROOT / "mapping" / "species.csv", encoding="utf-8"))}
fruit = {r["emerald_id"].split(":", 1)[1].replace("-berry", ""): r["sw_name"]
         for r in csv.DictReader(open(ROOT / "mapping" / "items.csv", encoding="utf-8")) if r["emerald_id"].endswith("-berry")}
PLAYER = {"brendan": "KAEL (player, boy)", "may": "MIRA (player, girl)",
          "ruby_sapphire_brendan": "KAEL (old Ruby/Sapphire sprite)", "ruby_sapphire_may": "MIRA (old Ruby/Sapphire sprite)"}
ACTION = {"acro_bike": "riding the white SPEEDER BIKE", "mach_bike": "riding the brown SWOOP BIKE",
          "decorating": "decorating a hideout", "field_move": "using a field move", "fishing": "fishing",
          "running": "running", "surfing": "riding a COMPANION across water", "underwater": "diving underwater",
          "walking": "walking", "watering": "watering fruit with the WATER CANTEEN"}

rows, missing = [], []
for a in csv.DictReader(open(ROOT / "database" / "pending_art.csv", encoding="utf-8")):
    if a["kind"] == "tileset":
        rel = a["path"].split("data/tilesets/", 1)[1]
        key, _, rest = rel.partition("/anim/")
        key = key.rsplit("/", 1)[0] if not rest else key
        base = tiles.get(key, "")
        anim = rest.split("/", 1)[0] if rest else ""
        subj = f"{base} (animation: {anim.replace('_', ' ')})" if base and anim else base
        if not subj:
            missing.append(a["asset_id"])
        rows.append({"asset_id": a["asset_id"], "sw_subject": subj})
        continue
    if a["kind"] not in ("object_events", "trainers"):
        continue
    parts = a["path"].split("/")
    stem, folder = parts[-1].rsplit(".", 1)[0], parts[-2]
    subj = ""
    if a["kind"] == "trainers":
        subj = pics.get(f"{folder}:{stem}") or pics.get(stem, "")
    elif folder in PLAYER:
        subj = f"{PLAYER[folder]}, {ACTION.get(stem, stem)}"
    elif folder == "berry_trees":
        subj = "Fruit sprout" if stem == "sprout" else "Loose soil" if stem == "dirt_pile" else \
            f"{fruit.get(stem, stem.upper())} plant"
    elif folder == "dolls":
        name = stem.replace("unused_", "").replace("big_", "").replace("_doll", "")
        if name == "latias_latios":
            name = "latias"
        subj = ("Big " if "big_" in stem else "") + f"{species.get(name, name.upper())} doll"
    elif folder == "cushions":
        subj = cush.get(stem, "")
    elif folder == "pokemon":
        name = stem.replace("enemy_", "").replace("_still", "")
        if name == "latias_latios":
            subj = "ASHLA / BOGAN (overworld)"
        elif name == "regi":
            subj = "ROCKWARDEN / ICEWARDEN / DURAWARDEN (overworld)"
        else:
            subj = f"{species.get(name, name.upper())} (overworld)"
    elif folder == "misc":
        subj = misc.get(stem, "")
    else:
        subj = people.get(stem, "")
    if not subj:
        missing.append(a["asset_id"])
    rows.append({"asset_id": a["asset_id"], "sw_subject": subj})

with open(ROOT / "mapping" / "art_subjects.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["asset_id", "sw_subject"])
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows;", len(missing), "missing:", " ".join(m.split("/")[-1] for m in missing))

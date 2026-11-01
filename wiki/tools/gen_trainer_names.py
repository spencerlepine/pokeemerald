"""One-off generator for mapping/trainers.csv (generic trainer names).

    python3 tools/gen_trainer_names.py      # only adds rows that are missing

Each Emerald trainer name gets a Star Wars-sounding name with the same first
letter and gender (so Step 4 can still recognise it), deterministically from
a hash of the Emerald name. Stormtrooper grunts get TK numbers; cartel grunts
get thug names; pairs ("AMY & LIV") get two short names. Rows already in
mapping/trainers.csv are never changed, so hand edits survive a re-run.
"""
from __future__ import annotations

import csv
import hashlib
import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMERALD = Path(os.environ.get("EMERALD_DB_DIR", ROOT / "emerald"))
OUT = ROOT / "mapping" / "trainers.csv"
VOWELS = "AEIOU"
V = ["A", "E", "I", "O", "A", "O", "U"]
MID = ["R", "L", "N", "D", "K", "V", "TH", "SH", "Z", "X", "B", "SS", "RR", "NN", "LD", "RK", "SK", "M", "T", "G"]
END_M = ["AN", "EK", "O", "US", "IR", "ON", "AX", "EL", "AR", "IK", "EN", "OS", "AL", "UN", "ESH"]
END_F = ["A", "IA", "RA", "ELLE", "INA", "YS", "ETH", "ISSA", "ARA", "I", "ENA", "ORA", "EE", "ILA"]
END_THUG = ["UK", "OG", "RAK", "UGG", "OTH", "ARG", "ODO", "UB"]
# canon characters and English words a generated name must not hit
BLOCK = {"LUKE", "HAN", "LEIA", "OWEN", "BERU", "YODA", "ANAKIN", "PADME", "REY", "FINN", "POE", "KYLO", "BEN", "JYN",
         "CASSIAN", "SABINE", "EZRA", "KANAN", "HERA", "ZEB", "MACE", "DOOKU", "MAUL", "JANGO", "BOBA", "LANDO", "WEDGE",
         "BIGGS", "JABBA", "GREEDO", "BOSSK", "DENGAR", "OBI", "QUI", "SIDIOUS", "KAEL", "MIRA", "KORR", "DORAN",
         "TARKIN", "VADER", "ASAJJ", "AHSOKA", "REX", "CODY", "WOLFE", "SARA", "DARK", "SITH", "JEDI", "BANE", "MAN",
         "KILL", "DIE", "SIN", "SEX", "ASS", "DAMN", "HELL", "BUTT", "GOD", "NAZI", "KUK", "SHIT", "DIK", "DICK", "ROAR", "BOSS"}


def h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest(), 16)


def gen(letter: str, gender: str, seed: str, used: set[str], maxlen: int = 8, ends=None) -> str:
    ends = ends or (END_F if gender == "f" else END_M)
    for i in range(500):
        x = h(f"{seed}:{i}")
        if letter in VOWELS:
            start = letter + "RLNDKVTHSZMB"[x % 12]
        else:
            start = letter + V[x % len(V)]
        x //= 97
        mid = "" if (x % 3 == 0 or maxlen <= 4) else MID[(x // 3) % len(MID)]
        x //= 211
        name = start + mid + ends[x % len(ends)]
        if re.search(r"[^AEIOUY]{3}|[AEIOU]{3}|(.)\1[^AEIOUY]|[^AEIOUY](.)\2", name) or "BOSS" in name:
            continue
        if not (3 <= len(name) <= maxlen) or name in used or any(b in name for b in BLOCK if len(b) > 3) or name in BLOCK:
            continue
        used.add(name)
        return name
    raise SystemExit(f"could not generate a name for {seed}")


def main():
    existing = {}
    if OUT.exists():
        with OUT.open(encoding="utf-8", newline="") as f:
            existing = {r["key"]: r for r in csv.DictReader(f)}
    with (EMERALD / "entities.csv").open(encoding="utf-8", newline="") as f:
        trainers = [e for e in csv.DictReader(f) if e["entity_type"] == "trainer"]
    # trainers that belong to a story character already get the character's name in build.py
    with (ROOT / "database" / "swap_map.csv").open(encoding="utf-8", newline="") as f:
        named = {r["emerald_id"] for r in csv.DictReader(f) if r["derived_from"].startswith("character:")}
    used = {r["sw_name"] for r in existing.values()} | {b for b in BLOCK}
    rows = dict(existing)
    tk = 100
    for e in sorted(trainers, key=lambda e: e["id"]):
        if e["id"] in named:
            continue
        name, g, cls = e["game_name"], (e["gender"] or "m")[:1].lower(), e["trainer_class"]
        if name == "GRUNT":
            key = e["id"]
            if key in rows:
                continue
            if "magma" in cls:
                tk += 1 + h(key) % 37
                sw, note = f"TK-{tk}", "Stormtrooper designation"
            else:
                sw, note = gen("GKTRBDV"[h(key) % 7], "m", key, used, 7, END_THUG), "Cartel thug"
            rows[key] = {"key": key, "emerald_name": name, "sw_name": sw, "map_status": "DRAFT", "notes": note}
            continue
        key = "name:" + name
        if key in rows:
            continue
        if name in ("BRENDAN", "MAY"):
            sw, note = ("KAEL" if name == "BRENDAN" else "MIRA"), "player / rival default name"
        elif " & " in name:
            a, b = name.split(" & ")
            sa = gen(a[0], "f" if a[-1] in "AEIY" else "m", key + "a", used, 4)
            sw = sa + " & " + gen(b[0], "f" if b[-1] in "AEIY" else "m", key + "b", used, 7 - len(sa))
            note = "pair"
        else:
            sw, note = gen(name[0], g, key, used), ""
        assert len(sw) <= 10, sw
        rows[key] = {"key": key, "emerald_name": name, "sw_name": sw, "map_status": "DRAFT", "notes": note}
    # Grand Arena / Battle Tent / Trial Spire trainers and Showcase rivals: same scheme, keyed by name so a
    # name shared with a story trainer keeps one Star Wars name. Showcase rivals' companion nicknames get a
    # "nick:" row built from the Star Wars species name (POOCHY the Poochyena -> MASSY the MASSIFF).
    with (EMERALD / "entities.csv").open(encoding="utf-8", newline="") as f:
        others = [e for e in csv.DictReader(f) if e["entity_type"] in ("facility_trainer", "contest_opponent")]
    with (ROOT / "mapping" / "species.csv").open(encoding="utf-8", newline="") as f:
        sw_species = {r["emerald_id"]: r["sw_name"] for r in csv.DictReader(f)}
    FEMALE = ("lass", "beauty", "picnicker", "parasol", "aroma", "battle-girl", "lady", "-f", "girl", "woman",
              "hex-maniac", "tuber-f", "swimmer-f", "twin", "nurse")
    for e in sorted(others, key=lambda e: e["id"]):
        name = e["game_name"]
        look = (e.get("trainer_pic") or "") + " " + (e.get("sprite") or "") + " " + (e.get("trainer_class") or "")
        g = "f" if any(k in look for k in FEMALE) else "m" if look.strip() else ("f" if name[-1] in "AEIY" else "m")
        key = "name:" + name
        if key not in rows:
            rows[key] = {"key": key, "emerald_name": name, "sw_name": gen(name[0], g, key, used), "map_status": "DRAFT",
                         "notes": e["entity_type"].replace("_", " ")}
        nick = e.get("nickname")
        if nick and "nick:" + nick not in rows:
            base = re.sub(r"[^A-Z]", "", sw_species.get(e.get("species", ""), nick))[:4]
            sw = base + ("Y" if base[-1] not in "AEIOUY" else "")
            while sw in used:
                sw = base[:3] + "IE" if not sw.endswith("IE") else base[:3] + "O"
            used.add(sw)
            rows["nick:" + nick] = {"key": "nick:" + nick, "emerald_name": nick, "sw_name": sw, "map_status": "DRAFT",
                                    "notes": "Showcase rival's companion nickname"}
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["key", "emerald_name", "sw_name", "map_status", "notes"])
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: r["key"]))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} rows ({len(rows) - len(existing)} new)")


if __name__ == "__main__":
    main()

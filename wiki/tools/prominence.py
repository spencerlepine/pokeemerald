#!/usr/bin/env python3
"""Prominence score for every film entity in starwars-db, joined to what the game uses.

Reads ../starwars-db/database (or STARWARS_DB_DIR) and the mapping tables, writes
mapping/proposals/prominence.csv: one row per starwars-db character, creature, droid, species,
vehicle, starship and location, with its score and where (if anywhere) the game uses it.

The score (bible/FAN_CRITIQUE.md, section 1):
  films_w  = sum over the six films the entity appears in: 1.0 for a prequel, 1.5 for an
             original-trilogy film (timeline_entities, relationship 'appearance')
  lines_w  = dialogue lines by speaker_entity_id (quotes.csv), same film weights
  scenes_w = scenes a location or vehicle is in (timeline_scene_entities), same film weights
  reach    = other films and series the entity appears in (metadata 'appearances' that are
             not one of the six films), capped at 6
  db_score = 10 * films_w + 22 * log10(1 + lines_w) + 15 * log10(1 + scenes_w) + 2 * reach
  fan      = a bonus from a published fan ranking (FAN_RANK below), for the cases the six
             films alone cannot settle (Maul, Ahsoka, Thrawn ...)
  score    = db_score + fan

Run: python3 tools/prominence.py
"""
import csv
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.environ.get("STARWARS_DB_DIR", ROOT.parent.parent / "starwars-db" / "database"))
OUT = ROOT / "mapping" / "proposals" / "prominence.csv"
SLOTS = ROOT / "mapping" / "proposals" / "prominence_slots.csv"

csv.field_size_limit(10**9)

FILMS = {
    "phantom-menace": 1.0, "attack-clones": 1.0, "revenge-sith": 1.0,
    "new-hope": 1.5, "empire-strikes-back": 1.5, "return-jedi": 1.5,
}
SIX_FILMS = {
    "Star Wars: The Phantom Menace (Episode I)", "Star Wars: Attack of the Clones (Episode II)",
    "Star Wars: Revenge of the Sith (Episode III)", "Star Wars: A New Hope (Episode IV)",
    "Star Wars: The Empire Strikes Back (Episode V)", "Star Wars: Return of the Jedi (Episode VI)",
}
CATEGORIES = {"characters", "creatures", "driods", "species", "vehicles", "starships", "locations"}

# Fan bonus: Complex, "The Top 50 Star Wars Characters, Ranked" (Jamie Iovine; read 2026-11-03,
# https://www.complex.com/pop-culture/a/jamieiovine/top-50-star-wars-characters-ranked), the one
# ranked list that loaded in full. Used only to settle what the six-film data cannot (characters
# famous from the series and the newer films). Top 10: +30, 11-25: +20, 26-50: +10. Names in
# NOT_IN_DB are not six-film databank entities; they get a synthetic row so the ranking can show them.
FAN_RANK = {
    1: "Anakin Skywalker", 2: "Han Solo", 3: "Luke Skywalker", 4: "Boba Fett", 5: "Yoda",
    6: "Obi-Wan Kenobi", 7: "Leia Organa", 8: "Chewbacca", 9: "Grogu", 10: "R2-D2",
    11: "C-3PO (See-Threepio)", 12: "Lando Calrissian", 13: "Din Djarin",
    14: "Emperor Palpatine (Darth Sidious)", 15: "Grand Admiral Thrawn", 16: "Maul", 17: "Qui-Gon Jinn",
    18: "Cassian Andor", 19: "Moff Gideon", 20: "Ahsoka Tano", 21: "Count Dooku", 22: "Mace Windu",
    23: "Jabba the Hutt", 24: "Grand Moff Tarkin", 25: "Asajj Ventress", 26: "Kylo Ren", 27: "Cad Bane",
    28: "Dash Rendar", 29: "Hera Syndulla", 30: "Poe Dameron", 31: "Orson Krennic", 32: "Jango Fett",
    33: "Ezra Bridger", 34: "Padmé Amidala", 35: "Rey", 36: "Finn", 37: "BB-8", 38: "Hondo Ohnaka",
    39: "Supreme Leader Snoke", 40: "Bo-Katan Kryze", 41: "Chopper", 42: "General Grievous",
    43: "Admiral Ackbar", 44: "Saw Gerrera", 45: "Mon Mothma", 46: "Wicket W. Warrick",
    47: "Aurra Sing", 48: "Maz Kanata", 49: "Wedge Antilles", 50: "Bib Fortuna",
}
# Anakin and Vader share one entry on that list; the bonus goes to both.
FAN_ALIAS = {"Darth Vader": "Anakin Skywalker"}
# Fan-list names with no six-film databank row: (title, alive and reachable around 2 BBY?)
NOT_IN_DB = {
    "Grogu": "alive, in hiding (skip: no film-era role)", "Din Djarin": "a child in 2 BBY (skip)",
    "Grand Admiral Thrawn": "alive: hunts the Rebels in the Outer Rim in 2 BBY (Rebels S3)",
    "Cassian Andor": "alive: Rebel agent with K-2SO in 2 BBY (Andor S2)",
    "Moff Gideon": "ISB officer later; nothing known for 2 BBY (skip)",
    "Ahsoka Tano": "alive: lost at Malachor 3 BBY, back 1 BBY (in the game at the Mortis Gate)",
    "Asajj Ventress": "dead 19 BBY", "Kylo Ren": "not born", "Cad Bane": "alive (Clone Wars, Book of Boba Fett)",
    "Dash Rendar": "Legends only (skip)", "Hera Syndulla": "alive: pilot of the Ghost, Rebel captain in 2 BBY",
    "Poe Dameron": "not born", "Orson Krennic": "alive: runs the Death Star project (in the game)",
    "Ezra Bridger": "alive: Kanan's Padawan (in the game)", "Rey": "not born", "Finn": "not born",
    "BB-8": "not built", "Hondo Ohnaka": "alive: Weequay pirate, turns up wherever there is profit (Rebels)",
    "Supreme Leader Snoke": "skip", "Bo-Katan Kryze": "alive: Mandalorian leader in exile, 2 BBY (Rebels S4 is 1 BBY)",
    "Chopper": "alive: the Ghost's astromech", "Saw Gerrera": "alive: Partisan leader, Geonosis 2 BBY then Jedha",
    "Maz Kanata": "alive: Takodana castle (optional cameo)", "Kanan Jarrus": "alive (in the game)",
    "Sabine Wren": "alive (in the game)", "Captain Rex": "alive (in the game)", "K-2SO": "in the game",
    "Chirrut Îmwe": "in the game", "Baze Malbus": "in the game",
}

def fan_bonus(title):
    title = FAN_ALIAS.get(title, title)
    for rank, name in FAN_RANK.items():
        if name == title:
            return 30 if rank <= 10 else 20 if rank <= 25 else 10
    return 0


def read(name):
    with open(DB / f"{name}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    if not DB.exists():
        sys.exit(f"starwars-db not found at {DB}; set STARWARS_DB_DIR")
    entities = {e["id"]: e for e in read("entities")}
    alias = {a["alias_id"]: a["entity_id"] for a in read("entity_aliases")}

    def canon(i):
        return alias.get(i, i)

    films = defaultdict(set)
    for t in read("timeline_entities"):
        if t["relationship"] == "appearance" and t["event_id"] in FILMS:
            films[canon(t["entity_id"])].add(t["event_id"])
    lines = defaultdict(float)
    for q in read("quotes"):
        if q["speaker_entity_id"]:
            lines[canon(q["speaker_entity_id"])] += FILMS.get(q["event_id"], 1.0)
    scenes = defaultdict(float)
    for s in read("timeline_scene_entities"):
        ev = s["scene_id"].split(":")[0]
        scenes[canon(s["entity_id"])] += FILMS.get(ev, 1.0)
    reach = defaultdict(set)
    for m in read("metadata"):
        if m["field"] == "appearances" and m["value"] not in SIX_FILMS:
            reach[canon(m["entity_id"])].add(m["value"])

    rows = []
    for i, e in entities.items():
        if e["category"] not in CATEGORIES or i in alias:
            continue
        fw = sum(FILMS[f] for f in films[i])
        lw = lines[i]
        sw = scenes[i]
        rc = min(len(reach[i]), 6)
        db_score = 10 * fw + 22 * math.log10(1 + lw) + 15 * math.log10(1 + sw) + 2 * rc
        fan = fan_bonus(e["title"])
        rows.append({
            "id": i, "category": e["category"], "title": e["title"],
            "films": len(films[i]), "films_w": round(fw, 1), "lines": int(round(lw / 1.0)),
            "lines_w": round(lw, 1), "scenes_w": round(sw, 1), "reach": rc,
            "db_score": round(db_score, 1), "fan": fan, "score": round(db_score + fan, 1),
        })

    titles = {e["title"] for e in entities.values()}
    for title, note in NOT_IN_DB.items():
        if title in titles:
            continue
        fan = fan_bonus(title)
        rows.append({
            "id": "fan:" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-"), "category": "characters",
            "title": title, "films": 0, "films_w": 0, "lines": 0, "lines_w": 0, "scenes_w": 0, "reach": 0,
            "db_score": 0, "fan": fan, "score": fan, "era_note": note,
        })
    for r in rows:
        r.setdefault("era_note", "")
        r["source"] = "fan-list" if r["id"].startswith("fan:") else "starwars-db"
    use = game_use(entities)
    for r in rows:
        u = use.get(r["id"], []) or use.get(r["title"], [])
        r["in_game"] = "yes" if u else "no"
        r["game_use"] = "; ".join(u)
    rows.sort(key=lambda r: (-r["score"], r["title"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{OUT.relative_to(ROOT)}: {len(rows)} rows, {sum(r['in_game'] == 'yes' for r in rows)} used by the game")
    slots(rows, entities)


SERVICE = {"character:tv-interviewer", "character:tv-cast", "character:talking-pokemon", "character:mart-clerk",
           "character:contest-mc", "character:contest-judge", "character:arena-referee", "character:frontier-guide",
           "character:blend-master", "character:dock", "character:pokemon-center-nurse"}


def slot_kind(role):
    r = role.lower()
    if "arena leader" in r or "arena (" in r:
        return "arena leader"
    if "trial" in r:
        return "trial"
    if "final battle" in r or "champion" in r:
        return "champion"
    if "grand arena" in r and "ace" in r:
        return "grand arena ace"
    if "leader of the imperial" in r or "cartel boss" in r:
        return "faction boss"
    if "field commander" in r or "bounty hunter" in r:
        return "faction lieutenant"
    if "rival" in r:
        return "rival"
    if "player" in r or "mother" in r:
        return "family"
    return "story / gift"


def slots(rows, entities):
    """One row per visible slot: who holds it, its score, and whether it reads as filler."""
    score = {r["id"]: r for r in rows}
    by_title = {r["title"]: r for r in rows}

    def lookup(basis, name):
        if basis in score:
            return score[basis]
        t = NAME_TO_TITLE.get((name or "").upper(), name)
        return by_title.get(t)

    out = []
    with open(ROOT / "mapping" / "characters.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["emerald_id"] in SERVICE or r["emerald_id"].startswith("organization:"):
                continue
            hit = lookup(r["sw_basis"], r["sw_name"])
            out.append({
                "slot": r["emerald_id"], "kind": slot_kind(r["role"]), "sw_name": r["sw_name"],
                "basis": r["sw_basis"], "planet": r["home_planet"],
                "score": hit["score"] if hit else ("" if r["sw_basis"] == "original" else "n/a"),
                "verdict": verdict(r["sw_basis"], hit), "role": r["role"][:90],
            })
    with open(ROOT / "mapping" / "people.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["kind"] not in ("boss",) and not (r["kind"] == "trainer" and r["character"]):
                continue
            name = r["trainer_name"]
            hit = lookup("", name)
            out.append({
                "slot": r["person_id"], "kind": "new boss", "sw_name": name, "basis": r["character"],
                "planet": r["area"], "score": hit["score"] if hit else "n/a",
                "verdict": verdict(r["character"], hit), "role": r["notes"][:90],
            })
    with open(SLOTS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"{SLOTS.relative_to(ROOT)}: {len(out)} visible slots")


def verdict(basis, hit):
    if basis == "original":
        return "original"
    if hit is None or hit["id"].startswith("fan:"):
        return "series / spin-off (no six-film data)"
    s = float(hit["score"])
    return "classic" if s >= 60 else "known" if s >= 35 else "filler"


# Game name -> starwars-db title, for names the title index does not match on its own.
NAME_TO_TITLE = {
    "C-3PO": "C-3PO (See-Threepio)", "SEN. ORGANA": "Bail Organa", "LEIA": "Leia Organa",
    "HAN": "Han Solo", "CHEWIE": "Chewbacca", "RIC OLIÉ": "Ric Olie", "BIGGS": "Biggs Darklighter",
    "CHIRPA": "Chief Chirpa", "QUI-GON": "Qui-Gon Jinn", "KI-ADI": "Ki-Adi-Mundi",
    "ANAKIN": "Anakin Skywalker", "OBI-WAN": "Obi-Wan Kenobi", "LANDO": "Lando Calrissian",
    "VADER": "Darth Vader", "VEERS": "General Veers", "JABBA": "Jabba the Hutt",
    "AURRA": "Aurra Sing", "GARDULLA": "Gardulla the Hutt", "DEXTER": "Dexter Jettster",
    "FODE&BEED": "Fode and Beed", "2-1B": "2-1B Droid", "OWEN": "Owen Lars", "LUKE": "Luke Skywalker",
    "SALACIOUS CRUMB": "Salacious B. Crumb", "REX": "Captain Rex", "RIEEKAN": "General Rieekan",
    "DERLIN": "Major Bren Derlin", "CODY": "Clone Commander Cody", "WEDGE": "Wedge Antilles",
    "JANSON": "Wes Janson", "HOBBIE": 'Derek "Hobbie" Klivian', "ZEV": "Zev Senesca",
    "DAK": "Dak Ralter", "PIETT": "Admiral Piett", "OZZEL": "Admiral Ozzel", "NEEDA": "Captain Needa",
    "MOTTI": "Admiral Motti", "TAGGE": "General Tagge", "PALPATINE": "Emperor Palpatine (Darth Sidious)",
    "AHSOKA": "Ahsoka Tano", "WINDY": "Windy", "TIREE": "Dex Tiree", "DEAK": "Deak",
    "KITWARR": "Kitwarr", "DUTCH": 'Jon "Dutch" Vander', "SABE": "Sabé", "CLEGG": "Clegg Holdfast",
    "MERRIN": "Merrin", "DREIS": "Garven Dreis", "PORKINS": "Jek Porkins", "LUMPY": "Lumpawarrump",
    "SAN TEKKA": "Lor San Tekka", "GREEDO": "Greedo", "WUHER": "Wuher", "PONDA BABA": "Ponda Baba",
    "DR. EVAZAN": "Doctor Cornelius Evazan", "MOMAW NADON": "Momaw Nadon", "FIGRIN D'AN": "Figrin D’an",
    "KANAN": "Kanan Jarrus", "EZRA": "Ezra Bridger", "SABINE": "Sabine Wren", "CAMIE": "Camie Marstrap",
    "FIXER": "Fixer", "DOOKU": "Count Dooku", "GRIEVOUS": "General Grievous", "KRENNIC": "Orson Krennic",
    "K-2SO": "K-2SO", "CHIRRUT": "Chirrut Îmwe", "BAZE": "Baze Malbus", "MALAKILI": "Malakili",
    "BIB FORTUNA": "Bib Fortuna", "SEBULBA": "Sebulba", "JAR JAR BINKS, THE TRAVELLER": "Jar Jar Binks",
    "GUARDIANS": "Chirrut Îmwe", "MAUL": "Maul", "WATTO": "Watto", "WALD": "Wald", "YODA": "Yoda",
    "TARFFUL": "Tarfful", "BOBA FETT": "Boba Fett", "BOSSK": "Bossk", "DENGAR": "Dengar",
    "ZUCKUSS": "Zuckuss", "4-LOM": "4-LOM", "IG-88": "IG-88", "GARINDAN": "Garindan", "LOBOT": "Lobot",
    "NIEN NUNB": "Nien Nunb", "R2-D2": "R2-D2", "LOGRAY": "Logray", "TEEBO": "Teebo", "PAPLOO": "Paploo",
    "SIO BIBBLE": "Sio Bibble",
    # places
    "MOS PELGO": "Mos Pelgo", "TOSCHE STATION": "Tosche Station", "KACHIRHO": "Kachirho",
    "MOS EISLEY": "Mos Eisley Spaceport", "MOS ESPA": "Mos Espa", "BESTINE": "Bestine IV",
    "BRIGHT TREE": "Bright Tree Village", "CLOUD CITY": "Cloud City", "YAVIN 4": "Yavin 4",
    "DAGOBAH": "Dagobah", "JUNDLAND WASTES": "Jundland Wastes", "SHADOWLANDS": "Kashyyyk",
    "MUSTAFAR PEAK": "Mustafar", "FELUCIA RESERVE": "Felucia", "JEDHA TEMPLE": "Jedha",
    "WAMPA CAVE": "Hoth", "CAVE OF EVIL": "Cave of Evil", "ILUM": "Ilum", "SANDCRAWLER": "Sandcrawler",
    "ASTEROID SPIRE": "Asteroid Field", "KRAYT GRAVEYARD": "Dune Sea", "TUSKEN RUINS": "Dune Sea",
    "FORTRESS VADER": "Mustafar", "HUTT HIDEOUT": "Cloud City", "TIPOCA CITY": "Kamino",
    "SEALED VAULT": "Kamino", "PIRIN": "Sullust", "INYUSU TOR": "Sullust", "ANCHORHEAD": "Anchorhead",
    "MOS ENTHA": "Mos Entha", "REPUBLIC WRECK": "Republic Cruiser", "DUNE SEA": "Dune Sea",
    "MOS EISLEY CANTINA": "Mos Eisley Cantina", "JABBA'S PALACE": "Jabba the Hutt's Palace",
    "BEN'S HUT": "Obi-Wan Kenobi's House", "DEATH STAR": "Death Star", "ENDOR": "Endor",
    "HOTH": "Hoth", "KAMINO": "Kamino", "KASHYYYK": "Kashyyyk", "TATOOINE": "Tatooine",
    "SULLUST": "Sullust", "MUSTAFAR": "Mustafar", "BESPIN": "Bespin", "JEDHA": "Jedha",
    "ATOLLON": "Atollon", "MORTIS": "Mortis", "TYTHON": "Tython", "ALDERAAN": "Alderaan",
    "NABOO": "Naboo", "CORUSCANT": "Coruscant", "GEONOSIS": "Geonosis", "DANTOOINE": "Dantooine",
    "UTAPAU": "Utapau", "MYGEETO": "Mygeeto", "CORELLIA": "Corellia", "TRANDOSHA": "Trandosha",
    "LARS HOMESTEAD": "Lars Moisture Farm", "ECHO BASE": "Echo Base", "SARLACC PIT": "Sarlacc Pit",
    # ships
    "MILLENNIUM FALCON": "Millennium Falcon", "IMPERIAL SHUTTLE": "Imperial Shuttle",
    "SAIL BARGE": "The Khetanna (Jabba's Sail Barge)", "X-WING": "X-wing Starfighter",
    "TIE FIGHTER": "TIE Fighter", "AT-ST": "AT-ST Walker", "AT-AT": "AT-AT Walker (All Terrain Armored Transport)",
    "SPEEDER BIKE": "Speeder Bike", "SWOOP": "Swoop", "SNOWSPEEDER": "Snowspeeder",
    "STAR DESTROYER": "Imperial Star Destroyer", "ESCAPE POD": "Escape Pod", "PODRACER": "Podracer",
    "LANDSPEEDER": "X-34 Landspeeder", "SKYHOPPER": "T-16 skyhopper", "SKIFF": "Desert Skiff",
    "BONGO": "Gungan Bongo Submarine", "REPUBLIC CRUISER": "Republic Cruiser", "TANTIVE IV": "Tantive IV",
    "Y-WING": "Y-wing Starfighter", "SLAVE I": "Boba Fett's starship", "CLOUD CAR": "Cloud Car",
}


def game_use(entities):
    """Map starwars-db id -> list of 'where (how)' strings from the mapping tables."""
    by_title = defaultdict(list)
    for i, e in entities.items():
        by_title[e["title"].upper()].append(i)

    def ids_for(name):
        name = (name or "").strip()
        if not name:
            return []
        if name.startswith("databank:") or name.startswith("swapi:"):
            return [name] if name in entities else []
        title = NAME_TO_TITLE.get(name.upper(), name)
        return by_title.get(title.upper(), [])

    use = defaultdict(list)

    def add(name, where):
        ids = ids_for(name)
        if not ids:
            title = NAME_TO_TITLE.get((name or "").upper(), "")
            if title in NOT_IN_DB:
                ids = [title]
        for i in ids:
            if where not in use[i]:
                use[i].append(where)

    def table(path):
        with open(ROOT / "mapping" / path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    for r in table("characters.csv"):
        slot = r["role"].split(".")[0][:60]
        add(r["sw_basis"], f"{r['emerald_id']} {r['sw_name']}: {slot}")
        add(r["sw_name"], f"{r['emerald_id']} {r['sw_name']}: {slot}")
    for r in table("species.csv"):
        add(r["sw_basis"], f"companion {r['sw_name']} ({r['home_planet']})")
    for r in table("trainer_classes.csv"):
        add(r["sw_basis"], f"trainer class {r['sw_name']}")
    for r in table("locations.csv"):
        add(r["sw_name"], f"{r['emerald_id']} {r['sw_name']} ({r['planet']})")
    for r in table("net_new.csv"):
        if r["entity_type"] in ("character", "trainer", "cutscene"):
            add(r["sw_name"], f"{r['id']} ({r['planet']})")
        if r["entity_type"] == "area":
            add(r["sw_name"], f"{r['id']} ({r['planet']})")
    for r in table("people.csv"):
        if r["trainer_name"]:
            add(r["trainer_name"], f"{r['person_id']} ({r['kind']}, {r['area']})")
    add("DOOKU", "net:relic-dooku (MUSTAFAR)")
    add("GRIEVOUS", "net:vision-grievous (DAGOBAH)")
    for r in table("trainers.csv"):
        if "cameo" in r["notes"]:
            add(r["sw_name"], f"trainer name {r['sw_name']} ({r['notes'].split(':')[1].strip()[:40]})")
    for r in table("planets.csv"):
        add(r["planet"], f"planet {r['planet']} ({r['role']}, act {r['act']})")
    for r in table("hyperlanes.csv"):
        ship = re.sub(r"\s*\(.*\)", "", r["ship"]).strip()
        add(ship, f"hyperlane {r['id']} ({r['ship']})")
    for r in table("world_art.csv"):
        add(r["name"], f"world art {r['concept_id']}")
    # the cantina people from the design doc
    for name, where in [("WUHER", "net:mos-eisley-cantina"), ("PONDA BABA", "net:mos-eisley-cantina"),
                        ("DR. EVAZAN", "net:mos-eisley-cantina"), ("MOMAW NADON", "net:mos-eisley-cantina"),
                        ("FIGRIN D'AN", "net:mos-eisley-cantina"), ("GREEDO", "net:cantina-greedo-battle"),
                        ("SAIL BARGE", "world art sail barge wreck, Jabba's barge dock"),
                        ("AT-ST", "world art Endor clearing wrecks"), ("X-WING", "world art Yavin 4, Dagobah"),
                        ("TIE FIGHTER", "world art Death Star rack"), ("ESCAPE POD", "world art route landmark"),
                        ("SNOWSPEEDER", "world art Hoth"), ("LANDSPEEDER", "world art Tatooine"),
                        ("CARBON-FREEZING CHAMBER", "Hutt Hideout room"),
                        ("MILLENNIUM FALCON", "hyperlane Tatooine/Kashyyyk"), ("IMPERIAL SHUTTLE", "hyperlane Jedha/Mustafar, Death Star")]:
        add(name, where)
    return use


if __name__ == "__main__":
    main()

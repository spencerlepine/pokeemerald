"""Build database/ from emerald-db (read-only) + mapping/ (hand-written Star Wars rows).

    python3 tools/build.py

Inputs
  ../emerald-db/database/*.csv   (or EMERALD_DB_DIR)   every Emerald row, never edited
  ../starwars-db/database/       (or STARWARS_DB_DIR)  used to validate sw_basis ids
  mapping/*.csv                                         the Star Wars rewrite, by emerald id
  mapping/texts/*.csv                                   curated dialogue rewrites (optional)

Outputs (database/, generated, never edit by hand)
  swap_map.csv        one row per Emerald entity + every NET_NEW row: the Step 4 find/replace table
  entities.csv        Emerald entities with the Star Wars title/description and status columns
  texts.csv           every Emerald text with an auto-drafted (or curated) Star Wars version
  pending_art.csv     every art asset, which entity uses it, its new name and art status
  area_progression.csv  Emerald balance table + planet and new map titles
  timeline_events.csv   Emerald story chronology rewritten (mapping/timeline.csv)
  net_new.csv         all net-new content (copied from mapping/net_new.csv, validated)
  build_info.csv      inputs, counts, warnings

Deterministic: same inputs give byte-identical outputs.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAPPING = ROOT / "mapping"
OUT = ROOT / "database"
EMERALD = Path(os.environ.get("EMERALD_DB_DIR", ROOT.parent / "emerald-db" / "database"))
STARWARS = Path(os.environ.get("STARWARS_DB_DIR", ROOT.parent / "starwars-db" / "database"))

csv.field_size_limit(sys.maxsize)

# In-game name limits (../game/include/constants/global.h, ../game/include/region_map.h)
NAME_LIMITS = {"species": 10, "move": 12, "item": 14, "ability": 12, "game_type": 6,
               "trainer_class": 12, "location": 16, "trainer": 10, "badge": 14}
CONSTANT_PREFIX = {"species": "SPECIES_", "move": "MOVE_", "item": "ITEM_", "ability": "ABILITY_",
                   "game_type": "TYPE_", "trainer_class": "TRAINER_CLASS_", "location": "MAPSEC_",
                   "trainer": "TRAINER_"}
# Entity types whose names are generic game mechanics and stay as they are unless mapped.
KEEP_BY_DEFAULT = {"nature", "growth_rate", "ribbon"}
MAPPING_FILES = ["species", "characters", "items", "moves", "types", "abilities", "badges",
                 "trainer_classes", "locations", "world_objects"]
SWAP_KINDS = {"HOTSWAP", "NET_NEW", "KEEP", "CUT"}
MAP_STATUSES = {"TODO", "DRAFT", "DONE", "IDEA"}
ART_STATUSES = {"PENDING_ART", "NEEDS_PLACEHOLDER", "KEEP_ANIM", "KEEP_ART", "NO_ART", "ART_READY"}
AUDIO_STATUSES = {"PENDING_AUDIO", "NEEDS_PLACEHOLDER", "KEEP_AUDIO", "NO_AUDIO", "DONE"}

warnings: list[str] = []

# FireRed/LeafGreen key items that exist in the item table but are never obtainable in Emerald.
FRLG_KEY_ITEMS = {"oaks-parcel", "poke-flute", "secret-key", "bike-voucher", "gold-teeth", "old-amber", "card-key",
                  "lift-key", "helix-fossil", "dome-fossil", "silph-scope", "bicycle", "town-map", "vs-seeker",
                  "fame-checker", "tm-case", "berry-pouch", "teachy-tv", "tri-pass", "rainbow-pass", "tea",
                  "ruby", "sapphire"}


def default_keep(e: dict) -> bool:
    """Rows that need no Star Wars name: placeholders, unused slots, TM/HM labels, mail, sprite forms."""
    et, col, s = e["entity_type"], e.get("collection", ""), e["id"].split(":", 1)[-1]
    if et == "":  # Unown letter forms and the Egg: follow their species rows
        return True
    if et == "species" and col == "unused-placeholder":
        return True
    if et == "item" and (col in ("unused", "tm-hm") or s in FRLG_KEY_ITEMS or s.endswith("-mail")):
        return True
    return False


def warn(msg: str) -> None:
    warnings.append(msg)


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write(name: str, rows: list[dict], cols: list[str] | None = None) -> None:
    if cols is None:
        cols = []
        for r in rows:
            for k in r:
                if k not in cols:
                    cols.append(k)
    OUT.mkdir(exist_ok=True)
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print(f"  database/{name}: {len(rows)} rows")


def constant(prefix: str, name: str) -> str:
    s = name.upper().replace("é", "E").replace("♀", "_F").replace("♂", "_M").replace("&", "_AND_")
    s = re.sub(r"[^A-Z0-9]+", "_", s).strip("_")
    return prefix + s if s else ""


def slug(name: str) -> str:
    s = name.lower().replace("é", "e").replace("&", "-and-")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# --------------------------------------------------------------------------- load

def load_inputs():
    if not EMERALD.exists():
        sys.exit(f"emerald-db not found at {EMERALD}; clone it next to this repo or set EMERALD_DB_DIR")
    entities = read(EMERALD / "entities.csv")
    by_id = {e["id"]: e for e in entities}
    sw_ids = set()
    if (STARWARS / "entities.csv").exists():
        sw_ids = {r["id"] for r in read(STARWARS / "entities.csv")}
    else:
        warn(f"starwars-db not found at {STARWARS}; sw_basis ids not validated")

    mapping: dict[str, dict] = {}
    for name in MAPPING_FILES:
        for r in read(MAPPING / f"{name}.csv"):
            eid = r["emerald_id"]
            if eid not in by_id:
                warn(f"mapping/{name}.csv: unknown emerald id {eid}")
                continue
            if eid in mapping:
                warn(f"mapping/{name}.csv: {eid} mapped twice")
            r["_file"] = name
            mapping[eid] = r
            for col, allowed in (("swap_kind", SWAP_KINDS), ("map_status", MAP_STATUSES), ("art_status", ART_STATUSES)):
                if r.get(col) and r[col] not in allowed:
                    warn(f"mapping/{name}.csv: {eid} bad {col} {r[col]}")
            basis = r.get("sw_basis", "")
            if sw_ids and (basis.startswith("databank:") or basis.startswith("swapi:")) and basis not in sw_ids:
                warn(f"mapping/{name}.csv: {eid} sw_basis {basis} not in starwars-db")
    return entities, by_id, mapping, sw_ids


# --------------------------------------------------------------------------- derive names

def derive(entities, by_id, mapping):
    """Return {emerald_id: swap row} for every Emerald entity."""
    # character text terms: OLD=>NEW pairs, used for trainer names and text
    char_terms: list[tuple[str, str]] = []
    trainer_char: dict[str, dict] = {}
    for eid, m in mapping.items():
        for pair in filter(None, (m.get("text_terms") or "").split("|")):
            old, _, new = pair.partition("=>")
            if old and new and old != new:
                char_terms.append((old, new))
        e = by_id[eid]
        for tid in filter(None, (e.get("trainer_ids") or "").split("|")):
            trainer_char[tid] = m

    loc_rows = {eid: m for eid, m in mapping.items() if eid.startswith("location:")}
    rows: dict[str, dict] = {}
    for e in entities:
        eid, et = e["id"], e["entity_type"]
        m = mapping.get(eid)
        r = {
            "emerald_id": eid, "entity_type": et,
            "emerald_name": e.get("game_name") or e.get("title", ""),
            "emerald_title": e.get("title", ""),
            "emerald_constant": e.get("source_constant", ""),
            "source_file": e.get("source_file", ""),
        }
        if m:
            r.update(swap_kind=m.get("swap_kind") or "HOTSWAP", map_status=m.get("map_status") or "DRAFT",
                     art_status=m.get("art_status") or "PENDING_ART", sw_name=m.get("sw_name", ""),
                     sw_title=m.get("sw_title") or m.get("sw_name", ""), sw_basis=m.get("sw_basis", ""),
                     planet=m.get("home_planet") or m.get("planet", ""),
                     sw_description=m.get("sw_description") or m.get("role", ""),
                     notes="; ".join(x for x in (m.get("notes"), m.get("habitat_note"), m.get("canon_note")) if x),
                     derived_from="mapping/" + m["_file"] + ".csv")
            if r["swap_kind"] == "KEEP" and not r["sw_name"]:
                r["sw_name"] = r["emerald_name"]
                r["sw_title"] = r["emerald_title"]
        elif et in KEEP_BY_DEFAULT or default_keep(e):
            r.update(swap_kind="KEEP", map_status="DONE", art_status="NO_ART", sw_name=r["emerald_name"],
                     sw_title=r["emerald_title"], derived_from="default")
        else:
            r.update(swap_kind="HOTSWAP", map_status="TODO", art_status="PENDING_ART", sw_name="", sw_title="",
                     derived_from="")
        rows[eid] = r

    # trainers: named characters take the character's name; generic trainers take mapping/trainers.csv
    # (keyed by trainer id, or by "name:<EMERALD NAME>" so rematches share a name); the rest stay TODO
    tn = {r["key"]: r for r in read(MAPPING / "trainers.csv")} if (MAPPING / "trainers.csv").exists() else {}
    tn_used = set()
    for e in entities:
        if e["entity_type"] != "trainer":
            continue
        r = rows[e["id"]]
        if r["derived_from"].startswith("mapping"):
            continue
        name = e.get("game_name", "")
        m = trainer_char.get(e["id"])
        cls = rows.get(e.get("trainer_class", ""), {})
        cls_name = cls.get("sw_name") or ""
        if m:
            new = name
            for old, rep in sorted(char_terms, key=lambda t: -len(t[0])):
                new = re.sub(rf"(?<![A-Z]){re.escape(old)}(?![A-Z])", rep, new)
            r.update(sw_name=new, sw_title=f"{cls_name} {new}".strip(), map_status="DONE",
                     planet=m.get("home_planet", ""), derived_from="character:" + m["emerald_id"])
        elif e["id"] in tn or f"name:{name}" in tn:
            k = e["id"] if e["id"] in tn else f"name:{name}"
            t = tn[k]
            tn_used.add(k)
            r.update(sw_name=t["sw_name"], sw_title=f"{cls_name} {t['sw_name']}".strip(),
                     map_status=t.get("map_status") or "DRAFT", notes=t.get("notes", ""),
                     derived_from="mapping/trainers.csv")
        else:
            r.update(sw_name=name, sw_title=f"{cls_name} {name}".strip(), map_status="TODO",
                     derived_from="trainer class; name not yet Star Wars-ified")
    # Grand Arena / Battle Tent / Trial Spire trainers and Showcase rivals share the name table
    for e in entities:
        if e["entity_type"] not in ("facility_trainer", "contest_opponent"):
            continue
        r = rows[e["id"]]
        k = "name:" + e.get("game_name", "")
        if k not in tn:
            continue
        tn_used.add(k)
        cls = rows.get(e.get("trainer_class", ""), {}).get("sw_name") or ""
        r.update(sw_name=tn[k]["sw_name"], map_status=tn[k].get("map_status") or "DRAFT",
                 sw_title=f"{cls} {tn[k]['sw_name']}".strip(), derived_from="mapping/trainers.csv")
        if e["entity_type"] == "contest_opponent":
            nk = "nick:" + e.get("nickname", "")
            sp = rows.get(e.get("species", ""), {}).get("sw_name", "")
            if nk in tn:
                tn_used.add(nk)
                cats = ", ".join(json.loads(e.get("contest_categories") or "[]"))
                r["sw_description"] = f"Showcase rival with {tn[nk]['sw_name']} the {sp} ({cats})."
    for k in tn:
        if k not in tn_used:
            warn(f"mapping/trainers.csv: key {k} matches no generic trainer")

    # maps: title from the region-map location + room suffix
    for e in entities:
        if e["entity_type"] != "map":
            continue
        r = rows[e["id"]]
        loc = loc_rows.get(e.get("location", ""))
        if not loc:
            continue
        base = loc.get("sw_name") or ""
        emer_loc = by_id[e["location"]].get("title", "")
        suffix = e.get("title", "")
        if suffix.startswith(emer_loc):
            suffix = suffix[len(emer_loc):].lstrip(" ·")
        if r["derived_from"].startswith("mapping") and r["sw_name"]:
            # a room renamed in mapping/world_objects.csv ("MOS EISLEY · Cantina") keeps its own name and description
            r.update(planet=loc.get("planet", ""), swap_kind=r["swap_kind"] or loc.get("swap_kind", "HOTSWAP"))
            continue
        r.update(sw_name=(base + (" · " + suffix if suffix else "")) if base else "",
                 sw_title=(base + (" · " + suffix if suffix else "")) if base else "",
                 planet=loc.get("planet", ""), map_status=loc.get("map_status", "TODO") if base else ("DONE" if loc.get("swap_kind") == "KEEP" else "TODO"),
                 swap_kind=loc.get("swap_kind", "HOTSWAP"),
                 derived_from="location:" + e["location"])

    # constants
    for r in rows.values():
        p = CONSTANT_PREFIX.get(r["entity_type"])
        if p and r["sw_name"] and r["swap_kind"] == "HOTSWAP":
            name = r["sw_name"].split(" / ")[0]
            r["sw_constant"] = constant(p, name)
        elif r["swap_kind"] == "KEEP":
            r["sw_constant"] = r["emerald_constant"]
        else:
            r["sw_constant"] = ""
        r["game_status"] = "NOT_STARTED"
        lim = NAME_LIMITS.get(r["entity_type"])
        if lim and r["sw_name"] and r["entity_type"] != "trainer" and len(r["sw_name"]) > lim \
                and r["entity_type"] != "location":
            warn(f"{r['emerald_id']}: name '{r['sw_name']}' is longer than the game limit {lim}")
        if r["entity_type"] == "location" and len(r["sw_name"]) > 16:
            warn(f"{r['emerald_id']}: map name '{r['sw_name']}' is longer than 16")

    # duplicate Star Wars names within one type (species/moves/items must be unique)
    for et in ("species", "move", "item", "ability"):
        c = Counter(r["sw_name"] for r in rows.values() if r["entity_type"] == et and r["sw_name"] and r["swap_kind"] == "HOTSWAP")
        for n, k in c.items():
            if k > 1:
                warn(f"duplicate {et} name {n} ({k} rows)")
    return rows, char_terms


# --------------------------------------------------------------------------- text

def build_terms(rows, by_id, char_terms):
    terms: dict[str, set[str]] = defaultdict(set)
    sources: dict[str, str] = {}

    def add(old: str, new: str, src: str) -> None:
        old, new = old.strip(), new.strip()
        if not old or not new or old == new or not any(ch.isalpha() for ch in old):
            return
        terms[old].add(new)
        sources.setdefault(old, src)

    glossary = {}
    for g in read(MAPPING / "glossary.csv"):
        add(g["emerald_term"], g["sw_term"], "glossary")
        glossary[g["emerald_term"].strip()] = g["sw_term"].strip()
    for old, new in char_terms:
        add(old, new, "character")
    for r in rows.values():
        et = r["entity_type"]
        if r["swap_kind"] != "HOTSWAP" or not r["sw_name"]:
            continue
        # trainer-class names are not used: in dialogue CHAMPION / LEADER / PSYCHIC are generic words
        if et in ("species", "move", "item", "ability", "game_type", "badge"):
            name = r["emerald_name"].upper() if et != "badge" else r["emerald_title"].upper()
            add(name, r["sw_name"], et)
            if et == "item" and not name.endswith("S"):  # "POKé BALLS", "POTIONS" in dialogue
                sw = r["sw_name"]
                add(name + "S", sw if sw.endswith(("S", "FRUIT")) else sw + ("ES" if sw.endswith(("CH", "SH", "X")) else "S"), et)
        elif et == "location":
            t = r["emerald_title"].upper()
            add(t, r["sw_name"], "location")
            w = t.split(" ")
            if len(w) == 2 and w[1] in ("TOWN", "CITY"):
                add(w[0], r["sw_name"], "location")
        elif et == "trainer" and " & " in r["emerald_name"] and " & " in r["sw_name"]:
            # pair trainers speak as "JOHN: ..." in dialogue; swap the speaker label of each member
            for a, b in zip(r["emerald_name"].split(" & "), r["sw_name"].split(" & ")):
                add(a.upper() + ":", b + ":", "trainer pair")
    # ambiguous terms (one Emerald word, several Star Wars meanings) are not auto-replaced
    final, ambiguous = {}, {}
    for old, news in terms.items():
        if old in glossary:  # the glossary always wins over names derived from entities
            final[old] = glossary[old]
        elif len(news) == 1:
            final[old] = next(iter(news))
        else:
            ambiguous[old] = sorted(news)
    # Emerald breaks long names across lines ("GRANITE\nCAVE"): add a split variant for every space in a
    # multi-word term. The break moves to the Star Wars name's space nearest the same relative spot. A one-word
    # Star Wars name gets no split variant: the words are swapped one by one and the spec fixes the leftover.
    for old, new in list(final.items()):
        if " " not in old or " " not in new or "\\" in old:
            continue
        for i, ch in enumerate(old):
            if ch != " ":
                continue
            spaces = [j for j, c in enumerate(new) if c == " "]
            for sep in ("\\n", "\\l"):
                split_old = old[:i] + sep + old[i + 1:]
                if split_old in final or split_old in ambiguous:
                    continue
                j = min(spaces, key=lambda j: abs(j / len(new) - i / len(old)))
                final[split_old] = new[:j] + sep + new[j + 1:]
                sources.setdefault(split_old, sources.get(old, "split"))
    for old, news in sorted(ambiguous.items()):
        warn(f"ambiguous text term {old!r} -> {news}; left unchanged in auto drafts")
    return final, sources, ambiguous


# "POKéMON" is both singular and plural; "COMPANION" is not. Fix the obvious plurals.
PLURAL_AFTER = re.compile(r"COMPANION(?=(?:\\[nl]|\s)(?:(?:that |who )?(?:are|were|have|aren't|weren't|don't|do|haven't|"
                          r"live|hide|grow|await|react|become|appear|gather|like|love|seem|tend|need|come|get|"
                          r"make|look|want|know|can't seem|all)|that are|who are)\b)")
PLURAL_BEFORE = re.compile(r"(\b(?:all|many|some|several|two|three|four|five|six|these|those|other|more|"
                           r"lots of|both|few|your two|your six|bunch of|lot of|types of|kinds of|sorts of|"
                           r"world of|full of|number of|variety of|plenty of|love of|study|studying|catching|"
                           r"raising|collecting|various|countless)(?: of)?(?: your| my| the| our| their| his| her)?"
                           r"(?:\\[nl]| ))COMPANION\b")


# Pixel width of a text line in Emerald's normal font (glyph widths from ../game/src/fonts.c,
# mapped through ../game/charmap.txt into tools/font_widths.json). The field text box is 208 px wide:
# no Emerald script line without placeholders is wider than that.
FONT_WIDTHS = json.loads((ROOT / "tools" / "font_widths.json").read_text(encoding="utf-8"))
BOX_PX = 208
PLACEHOLDER_PX = {"PLAYER": 42, "RIVAL": 42, "KUN": 0, "STR_VAR_1": 60, "STR_VAR_2": 60, "STR_VAR_3": 60}


# "rare COMPANION" is plural unless an article or determiner comes first ("a rare COMPANION").
# "rare COMPANION", "BIRD COMPANION", "GRASS-type COMPANION", "with COMPANION": plural unless a determiner comes
# first ("a rare COMPANION") or COMPANION is used as an adjective ("COMPANION battle", "BIRD COMPANION feathers")
PLURAL_ADJ = re.compile(r"(?:(?<=\\[nlp])|\b)(rare|strong|cute|cool|tough|weak|wild|different|powerful|new|pretty|lively|beautiful|smart|great|fine|amazing|precious|BIRD|BUG|[A-Z]+-type|"
                        r"NORMAL|FIRE|WATER|GRASS|ELECTRIC|ICE|FIGHTING|POISON|GROUND|FLYING|PSYCHIC|ROCK|GHOST|DRAGON|DARK|STEEL|"
                        r"BEAUTIFUL|CUTE|SMART|COOL|TOUGH|"
                        r"eligible|rental|personal|decent|darling|opposing|three|four|five|six|two|several|many|all|"
                        r"with|of|and|about|love|like|adore|steal|trade|raise|catch|judging|toughening up|taught to)((?:\\[nl]| ))COMPANION\b(?!'s)"
                        r"(?!(?:\\[nl]| )(?:battles?|battling|training|trainers?|TRAINERS?|feathers|team|NURSERY|CENTER|"
                        r"Storage|STORAGE|HERB|fans?|moves?|types?|kinds?|species|world|sound|cry|DATAPAD|lovers?|"
                        r"RANGERS?|LEAGUE|SHOWCASES?|BREEDERS?|FAN|CLUB|EGG|data)\b)")
SINGULAR_BEFORE = re.compile(r"(?:(?<=\\[nlp])|\b)(?:a|an|one|this|that|the|any|each|every|your|my|his|her|its|their|our|no|which|what|same)"
                             r"(?: [a-z]+)?(?:\\[nl]| )$")


def _plural_adj(m):
    before = m.string[max(0, m.start() - 24):m.start()]
    if SINGULAR_BEFORE.search(before):
        return m.group(0)
    return m.group(1) + m.group(2) + "COMPANIONS"


def fix_articles(text: str, new_terms: set[str]) -> str:
    for term in sorted(new_terms, key=len, reverse=True):
        if not term[:1].isalpha():
            continue
        vowel = term[0] in "AEIO" or (term[0] == "U" and not term.startswith(("UNI", "USE", "USU", "UTI"))) \
            or re.match(r"[FHLMNRSX][0-9-]", term)  # "an R2 UNIT", "an X-WING"
        art = "an" if vowel else "a"
        text = re.sub(r"(?:(?<=\\[nlp])|\b)([Aa])n?((?: |\\[nl]))(?=" + re.escape(term) + r"\b)",
                      lambda m: (art if m.group(1) == "a" else art.capitalize()) + m.group(2), text)
    return text


def line_px(line: str) -> int:
    total = 0
    for tok in re.findall(r"\{[^}]*\}|.", line):
        if tok.startswith("{"):
            k = tok[1:-1].split(" ")[0]
            total += PLACEHOLDER_PX.get(k, 8 if ("ARROW" in k or "BUTTON" in k or k.startswith("EMOJI")) else 0)
        elif tok != "$":
            total += FONT_WIDTHS.get(tok, 6)
    return total


# Menu and screen strings sit in fixed or auto-sized windows that only the game code knows. A Star Wars string
# wider than Emerald's gets `ui_wider_px`; during the port its window must fit it (or the text gets shorter).
UI_FILES = ("src/strings.c", "src/battle_message.c", "src/text_input_strings.c", "src/landmark.c",
            "src/data/text/gift_ribbon_descriptions.h", "src/data/union_room.h", "src/data/credits.h")


def draft_texts(terms: dict[str, str]):
    keys = sorted(terms, key=lambda k: (-len(k), k))
    pattern = re.compile(r"(?:(?<=\\[nlp])|(?<![A-Za-z0-9é]))(" + "|".join(re.escape(k) for k in keys) + r")(?![A-Za-z0-9é])")
    curated = {}
    tdir = MAPPING / "texts"
    if tdir.exists():
        for p in sorted(tdir.glob("*.csv")):
            for r in read(p):
                curated[r["text_id"]] = (r["sw_text_raw"], p.name, r.get("notes", ""))
    out = []
    counts = Counter()
    for t in read(EMERALD / "texts.csv"):
        raw = t["text_raw"]
        used = []

        def sub(m):
            used.append(m.group(1))
            return terms[m.group(1)]

        new = pattern.sub(sub, raw)
        if used:  # "an GRAPPLE LINE" -> "a GRAPPLE LINE", "a ICE…" -> "an ICE…"
            new = fix_articles(new, {terms[u] for u in used})
        if "COMPANION" in new:
            new = PLURAL_AFTER.sub("COMPANIONS", new)
            new = PLURAL_BEFORE.sub(lambda m: m.group(1) + "COMPANIONS", new)
            new = PLURAL_ADJ.sub(_plural_adj, new)
        status, note = ("AUTO" if used else "UNCHANGED"), ""
        if t["text_id"] in curated:
            new, src, note = curated[t["text_id"]]
            status = "CURATED"
        old_lines = re.split(r"\\[nlp]", raw)
        new_lines = re.split(r"\\[nlp]", new)
        longest = max((line_px(x) for x in old_lines), default=0)
        overflow = any(line_px(x) > max(longest, BOX_PX) for x in new_lines)
        ui_over = 0
        if t["source_file"] in UI_FILES or (t["source_file"].startswith("src/") and t["text_context"] != "dialogue"):
            ui_over = max(0, max(line_px(x) for x in new_lines) - max(line_px(x) for x in old_lines))
        counts[status] += 1
        out.append({"text_id": t["text_id"], "map_id": t["map_id"], "source_file": t["source_file"],
                    "source_line": t["source_line"], "speaker_label": t["speaker_label"],
                    "text_origin": t["text_origin"], "text_context": t["text_context"],
                    "emerald_text_raw": raw, "sw_text_raw": new, "text_status": status,
                    "terms_applied": "|".join(sorted(set(used))), "overflow_risk": "yes" if overflow else "",
                    "ui_wider_px": str(ui_over) if ui_over else "", "notes": note})
    return out, counts


# --------------------------------------------------------------------------- art

# Datapad (Pokedex) entries: the Emerald entry is up to 4 lines of at most 224 px; categories are at most 11
# characters. mapping/datapad.csv holds the text unwrapped; the build wraps it greedily.
DEX_LINE_PX, DEX_LINES, DEX_CATEGORY_LEN = 224, 4, 11


def wrap_datapad(text: str) -> list[str]:
    lines, cur = [], ""
    for word in text.split(" "):
        t = f"{cur} {word}" if cur else word
        if line_px(t) > DEX_LINE_PX and cur:
            lines.append(cur)
            cur = word
        else:
            cur = t
    lines.append(cur)
    return lines


def load_datapad() -> dict[str, dict]:
    path = MAPPING / "datapad.csv"
    out = {}
    if not path.exists():
        return out
    for r in read(path):
        if not r["sw_datapad_text"]:
            continue
        lines = wrap_datapad(r["sw_datapad_text"])
        if len(lines) > DEX_LINES:
            warn(f"datapad text for {r['emerald_id']} wraps to {len(lines)} lines (max {DEX_LINES})")
        if len(r["sw_category"]) > DEX_CATEGORY_LEN or line_px(r["sw_category"]) > 66:
            warn(f"datapad category for {r['emerald_id']} is too long: {r['sw_category']!r}")
        out[r["emerald_id"]] = {"category": r["sw_category"], "text": "\\n".join(lines)}
    return out


def pending_art(rows):
    assets = {a["asset_id"]: a for a in read(EMERALD / "art_assets.csv")}
    used_by = defaultdict(list)
    for ea in read(EMERALD / "entity_art.csv"):
        used_by[ea["asset_id"]].append((ea["entity_id"], ea["role"]))
    subjects_path = MAPPING / "art_subjects.csv"  # written by tools/make_art_subjects.py
    subjects = {r["asset_id"]: r["sw_subject"] for r in read(subjects_path)} if subjects_path.exists() else {}
    out = []
    for aid in sorted(assets):
        a = assets[aid]
        links = used_by.get(aid, [])
        ents = [rows[e] for e, _ in links if e in rows]
        sw = next((r for r in ents if r["sw_name"] and r["swap_kind"] == "HOTSWAP"), None)
        path = a["path"]
        new_path = ""
        if sw:
            old_slug = sw["emerald_id"].split(":", 1)[1].replace("-", "_")
            new_slug = slug(sw["sw_name"].split(" / ")[0]).replace("-", "_")
            if f"/{old_slug}/" in path:
                new_path = path.replace(f"/{old_slug}/", f"/{new_slug}/")
            elif f"/{old_slug}." in path:
                new_path = path.replace(f"/{old_slug}.", f"/{new_slug}.")
        statuses = {r["art_status"] for r in ents}
        if a["kind"] == "battle_animation":
            status = "PENDING_ART" if "PENDING_ART" in statuses else "KEEP_ANIM"
        else:
            status = "PENDING_ART"  # Step 5 redraws every image
        out.append({"asset_id": aid, "kind": a["kind"], "subkind": a["subkind"], "path": path,
                    "width": a["width"], "height": a["height"],
                    "used_by": "|".join(f"{e}:{role}" for e, role in links),
                    "sw_entity": sw["sw_name"] if sw else "", "sw_subject": subjects.get(aid, ""),
                    "suggested_path": new_path,
                    "art_status": status, "drawn_by": "", "art_notes": ""})
    return out


def apply_art_ready(art):
    """mapping/art_ready.csv: new art the owner approved, stored in ../art/<path>, not yet copied into ../game."""
    path = MAPPING / "art_ready.csv"
    if not path.exists():
        return
    by_id = {a["asset_id"]: a for a in art}
    for d in read(path):
        a = by_id.get(d["asset_id"])
        if not a:
            warn(f"mapping/art_ready.csv: {d['asset_id']} is not in pending_art.csv")
            continue
        if not (ROOT / d["art_file"]).exists():
            warn(f"mapping/art_ready.csv: {d['art_file']} missing")
        a.update(art_status="ART_READY", drawn_by=d.get("drawn_by", ""),
                 art_notes="; ".join(x for x in (f"art: {d['art_file']}", d.get("notes", "")) if x))


def apply_audio_done(audio):
    """mapping/audio_done.csv: sounds the owner approved and a tool installed into ../game (cry-generator,
    sfx-generator). audio_status becomes DONE; game_status is DONE when the row's call sites already play it
    (hot-swaps). Net-new SEs get their song id but stay NOT_STARTED until something in ../game calls them."""
    path = MAPPING / "audio_done.csv"
    if not path.exists():
        return
    by_id = {a["asset_id"]: a for a in audio}
    for d in read(path):
        a = by_id.get(d["asset_id"])
        if not a:
            warn(f"mapping/audio_done.csv: {d['asset_id']} is not in pending_audio.csv")
            continue
        if not (ROOT.parent / "game" / d["game_file"]).exists():
            warn(f"mapping/audio_done.csv: ../game/{d['game_file']} missing")
        a.update(audio_status="DONE", made_by=d.get("made_by", ""),
                 notes="; ".join(x for x in (f"in game: {d['game_file']}", d.get("notes", "")) if x))
        a["game_status"] = "DONE" if a["swap_kind"] == "HOTSWAP" else "NOT_STARTED"


def net_new_art(net):
    """NET_NEW rows that need new art have no Emerald asset; list them so the art list is complete."""
    out = []
    for n in net:
        if n["art_status"] not in ("PENDING_ART", "NEEDS_PLACEHOLDER"):
            continue
        out.append({"asset_id": n["id"], "kind": "net_new", "subkind": n["entity_type"], "path": "",
                    "width": "", "height": "", "used_by": f"{n['id']}:net_new", "sw_entity": n["sw_name"],
                    "sw_subject": n["sw_name"], "suggested_path": "", "art_status": n["art_status"],
                    "drawn_by": "", "art_notes": (f"placeholder: copy the art of {n['placeholder_from']}"
                                                  if n.get("placeholder_from") else "new art, no Emerald asset")})
    return out


# --------------------------------------------------------------------------- sound and visual effects
# mapping/asset_inventory.csv is generated from ../game by tools/scan_game_assets.py (music, sound effects,
# cries, VFX). mapping/audio.csv and mapping/vfx.csv hold the hand-written Star Wars decision for each row,
# plus net-new rows (`net:*`) and ghost rows (swap_kind CUT: an Emerald asset to delete, never added back).

AUDIO_COLS = ["asset_id", "category", "kind", "swap_kind", "map_status", "audio_status", "priority",
              "emerald_constant", "sw_constant", "sw_subject", "used_in", "used_by", "placeholder_from",
              "replaced_by", "depends_on", "source_file", "source_line", "asset_file", "suggested_path",
              "ref_count", "refs", "made_by", "notes"]
ART_EXTRA_COLS = ["swap_kind", "todo", "source_line", "placeholder_from", "replaced_by", "depends_on"]
TODOS = {"", "HUMAN-TODO"}


def _check_decision(src, d, status_col, statuses):
    for col, allowed in (("swap_kind", SWAP_KINDS), ("map_status", MAP_STATUSES), (status_col, statuses)):
        if d.get(col) not in allowed:
            warn(f"{src}: {d['asset_id']} bad {col} {d.get(col)!r}")
    if d["swap_kind"] == "NET_NEW" and not d["asset_id"].startswith("net:"):
        warn(f"{src}: {d['asset_id']} is NET_NEW but its id does not start with net:")
    if d["asset_id"].startswith("net:") and d["swap_kind"] != "NET_NEW":
        warn(f"{src}: {d['asset_id']} must be NET_NEW")
    if d["swap_kind"] == "CUT" and d[status_col] not in ("NO_ART", "NO_AUDIO"):
        warn(f"{src}: ghost row {d['asset_id']} must have {status_col} NO_ART / NO_AUDIO")


def load_asset_decisions():
    inv_path = MAPPING / "asset_inventory.csv"
    if not inv_path.exists():
        warn("mapping/asset_inventory.csv missing; run tools/scan_game_assets.py")
        return {}, {}, {}
    inv = {r["asset_id"]: r for r in read(inv_path)}
    audio = {r["asset_id"]: r for r in read(MAPPING / "audio.csv")} if (MAPPING / "audio.csv").exists() else {}
    vfx = {r["asset_id"]: r for r in read(MAPPING / "vfx.csv")} if (MAPPING / "vfx.csv").exists() else {}
    for d in audio.values():
        _check_decision("mapping/audio.csv", d, "audio_status", AUDIO_STATUSES)
    for d in vfx.values():
        _check_decision("mapping/vfx.csv", d, "art_status", ART_STATUSES)
    # branding, title screen, cutscenes and menus: overrides of pending_art rows plus `brand:*` rows (not images)
    if (MAPPING / "branding.csv").exists():
        for d in read(MAPPING / "branding.csv"):
            _check_decision("mapping/branding.csv", d, "art_status", ART_STATUSES)
            if d.get("todo", "") not in TODOS:
                warn(f"mapping/branding.csv: {d['asset_id']} bad todo {d['todo']!r}")
            if d["asset_id"] in vfx:
                warn(f"mapping/branding.csv: {d['asset_id']} is also in mapping/vfx.csv")
            vfx[d["asset_id"]] = d
    return inv, audio, vfx


def _refs_ok(d, src, known):
    for col in ("placeholder_from", "replaced_by", "depends_on"):
        v = d.get(col, "")
        if v and v not in known:
            warn(f"{src}: {d['asset_id']} {col} {v} is not a known asset, entity, flag or net-new id")


def pending_audio(rows, entities, inv, decisions, known):
    """One row per music track, sound effect, phoneme and cry in ../game, plus net-new and ghost audio."""
    folder_map = {e["map_folder"]: e["id"] for e in entities if e["entity_type"] == "map" and e.get("map_folder")}
    trainers_by_music = Counter(e["encounter_music"] for e in entities if e["entity_type"] == "trainer")
    out = []
    for aid, r in inv.items():
        if r["category"] not in ("music", "sfx", "cry"):
            continue
        d = decisions.get(aid)
        used = []
        for u in filter(None, r["used_by"].split("|")):
            if u.startswith("map_folder:"):
                mid = folder_map.get(u.split(":", 1)[1])
                if mid:
                    used.append(mid)
            else:
                used.append(u)
        if r["category"] == "cry" and not d:
            sp = rows.get(used[0]) if used else None
            if not sp:
                warn(f"cry {aid}: no species row and no decision in mapping/audio.csv")
                continue
            is_droid = "droid" in (sp.get("sw_description", "") + " " + sp.get("sw_basis", "")).lower()
            voice = ("electronic droid voice: beeps, whistles and servo whirs" if is_droid
                     else "creature call that fits its look and size")
            d = {"sw_constant": "CRY_" + constant("", sp["sw_name"]), "swap_kind": "HOTSWAP", "map_status": "DRAFT",
                 "audio_status": "PENDING_AUDIO", "priority": "2",
                 "sw_subject": f"{sp['sw_name']}: {voice}. {sp.get('sw_description', '')}".strip(),
                 "notes": "derived from mapping/species.csv"}
        if not d:
            warn(f"{aid}: no decision in mapping/audio.csv")
            continue
        # where the player hears it, in Star Wars terms
        used_in = []
        if r["category"] == "music":
            seen = set()
            for mid in used:
                m = rows.get(mid, {})
                t = (m.get("sw_title") or m.get("emerald_title") or "").split(" · ")[0]
                if t and t not in seen:
                    seen.add(t)
                    used_in.append(f"{t} ({m.get('planet')})" if m.get("planet") else t)
            key = r["emerald_constant"].replace("MUS_ENCOUNTER_", "").lower().replace("_", "-")
            if r["emerald_constant"].startswith("MUS_ENCOUNTER_") and trainers_by_music.get(key):
                used_in.append(f"{trainers_by_music[key]} trainers' encounter music")
        elif r["category"] == "sfx":
            used_in = sorted({rows[u]["sw_name"] for u in used if u in rows and rows[u].get("sw_name")})
        elif r["category"] == "cry" and used and used[0] in rows:
            used_in = [rows[used[0]]["sw_name"]]
        sw_const = d.get("sw_constant", "")
        suggested = ""
        if d["swap_kind"] in ("HOTSWAP", "NET_NEW") and sw_const:
            suggested = (f"sound/direct_sound_samples/cries/{sw_const[4:].lower()}.wav" if r["category"] == "cry"
                         else f"sound/songs/midi/{sw_const.lower()}.mid")
        _refs_ok(d, "mapping/audio.csv", known)
        out.append({"asset_id": aid, "category": r["category"], "kind": r["kind"], "swap_kind": d["swap_kind"],
                    "map_status": d["map_status"], "audio_status": d["audio_status"], "priority": d.get("priority", ""),
                    "emerald_constant": r["emerald_constant"], "sw_constant": sw_const,
                    "sw_subject": d.get("sw_subject", ""), "used_in": "; ".join(used_in[:12]) +
                    (f"; +{len(used_in) - 12} more" if len(used_in) > 12 else ""),
                    "used_by": "|".join(used), "placeholder_from": d.get("placeholder_from", ""),
                    "replaced_by": d.get("replaced_by", ""), "depends_on": d.get("depends_on", ""),
                    "source_file": r["source_file"], "source_line": r["source_line"], "asset_file": r["asset_file"],
                    "suggested_path": suggested, "ref_count": r["ref_count"], "refs": r["refs"], "made_by": "",
                    "notes": d.get("notes", "")})
    for aid, d in decisions.items():
        if aid in inv:
            continue
        if not aid.startswith("net:"):
            warn(f"mapping/audio.csv: {aid} is not in mapping/asset_inventory.csv")
            continue
        _refs_ok(d, "mapping/audio.csv", known)
        ph = inv.get(d.get("placeholder_from", ""), {})
        cat = ph.get("category", "sfx")
        out.append({"asset_id": aid, "category": cat, "kind": "net_new", "swap_kind": "NET_NEW",
                    "map_status": d["map_status"], "audio_status": d["audio_status"], "priority": d.get("priority", ""),
                    "sw_constant": d.get("sw_constant", ""), "sw_subject": d.get("sw_subject", ""),
                    "placeholder_from": d.get("placeholder_from", ""), "replaced_by": d.get("replaced_by", ""),
                    "depends_on": d.get("depends_on", ""),
                    "suggested_path": f"sound/songs/midi/{d.get('sw_constant', '').lower()}.mid" if d.get("sw_constant") else "",
                    "made_by": "", "notes": d.get("notes", "") or (
                        f"placeholder: copy {ph.get('asset_file') or d.get('placeholder_from')} under the new name first")})
    for r in out:
        for c in AUDIO_COLS:
            r.setdefault(c, "")
        r["game_status"] = "NOT_STARTED"
    order = {"music": 0, "sfx": 1, "cry": 2}
    out.sort(key=lambda r: (order.get(r["category"], 9), r["kind"] == "net_new", r["asset_id"]))
    return out


def vfx_art(inv, decisions, art, known):
    """VFX rows (battle status/general/special animations, field effects, weather, battle transitions), net-new VFX
    and ghost overrides for existing art rows, in pending_art.csv's format."""
    art_ids = {a["asset_id"]: a for a in art}
    out = []
    for a in art:  # every existing art row says whether it is a hotswap, a keep or net-new
        a["swap_kind"] = "NET_NEW" if a["kind"] == "net_new" else ("KEEP" if a["art_status"] == "KEEP_ANIM" else "HOTSWAP")
    for aid, r in inv.items():
        if r["category"] != "vfx":
            continue
        d = decisions.get(aid)
        if not d:
            warn(f"{aid}: no decision in mapping/vfx.csv")
            continue
        _refs_ok(d, "mapping/vfx.csv", known)
        out.append({"asset_id": aid, "kind": "vfx_" + r["kind"], "subkind": r["subkind"], "path": r["source_file"],
                    "width": "", "height": "", "used_by": r["used_by"], "sw_entity": "",
                    "sw_subject": d.get("sw_subject", ""), "suggested_path": "", "art_status": d["art_status"],
                    "drawn_by": "", "art_notes": d.get("notes", ""), "swap_kind": d["swap_kind"],
                    "todo": d.get("todo", ""), "source_line": r["source_line"], "placeholder_from": d.get("placeholder_from", ""),
                    "replaced_by": d.get("replaced_by", ""), "depends_on": d.get("depends_on", "")})
    for aid, d in decisions.items():
        if aid in inv:
            continue
        _refs_ok(d, "mapping/vfx.csv", known)
        if aid in art_ids:  # override of an existing art row (ghosts for unused art)
            art_ids[aid].update(swap_kind=d["swap_kind"], art_status=d["art_status"], todo=d.get("todo", ""),
                                sw_subject=d.get("sw_subject") or art_ids[aid]["sw_subject"],
                                art_notes=d.get("notes", ""), replaced_by=d.get("replaced_by", ""))
        elif aid.startswith("brand:"):
            out.append({"asset_id": aid, "kind": "branding", "subkind": "", "path": d.get("path", ""), "width": "",
                        "height": "", "used_by": "", "sw_entity": "", "sw_subject": d.get("sw_subject", ""),
                        "suggested_path": "", "art_status": d["art_status"], "drawn_by": "",
                        "art_notes": d.get("notes", ""), "swap_kind": d["swap_kind"], "todo": d.get("todo", ""),
                        "source_line": d.get("source_line", ""), "placeholder_from": d.get("placeholder_from", ""),
                        "replaced_by": d.get("replaced_by", ""), "depends_on": d.get("depends_on", "")})
        elif aid.startswith("net:"):
            out.append({"asset_id": aid, "kind": "vfx_net_new", "subkind": "", "path": "", "width": "", "height": "",
                        "used_by": "", "sw_entity": "", "sw_subject": d.get("sw_subject", ""), "suggested_path": "",
                        "art_status": d["art_status"], "drawn_by": "",
                        "art_notes": d.get("notes", "") or f"placeholder: copy {d.get('placeholder_from')} first",
                        "swap_kind": "NET_NEW", "source_line": "", "placeholder_from": d.get("placeholder_from", ""),
                        "replaced_by": d.get("replaced_by", ""), "depends_on": d.get("depends_on", "")})
        else:
            warn(f"mapping/vfx.csv: {aid} is neither in mapping/asset_inventory.csv nor in pending_art.csv")
    for a in art + out:
        a.setdefault("todo", "")
    out.sort(key=lambda a: (a["kind"], a["asset_id"]))
    return out


# --------------------------------------------------------------------------- game port (Step 4)
# One row per thing to copy from this wiki into ../game by hand. The wiki and the game never import each
# other: a porter edits ../game/<game_file>, then sets game_status DONE here (in the table named by `table`).

PORT_COLS = ["port_id", "table", "kind", "wiki_id", "swap_kind", "action", "game_file", "game_line",
             "wiring", "depends_on", "game_status", "notes"]
# Entity columns that tie a row to other game content (maps, sprites, scripts, flags, parties...).
WIRING_COLS = ["map", "graphics", "script", "visibility_flag", "map_ids", "home_map", "trainer_ids",
               "trainer_class", "trainer_pic", "party_symbol", "species", "sprite", "sprite_ids", "layout",
               "primary_tileset", "secondary_tileset", "heal_location", "sign_text_id", "flag_id",
               "teaches_move", "taught_by_item", "organization_ids", "related_entity_ids"]
ENTITY_ACTION = {"HOTSWAP": "swap name/constant/description to the Star Wars version",
                 "KEEP": "keep as is; check every reference still matches after the swaps",
                 "NET_NEW": "build new content (see bible/NET_NEW_DESIGNS.md)"}


def _wiring(r, cols):
    return "; ".join(f"{c}={r[c]}" for c in cols if r.get(c))


GHOST_ACTION = "ghost: delete it from ../game (see notes) and never add it back; DONE means deleted"


def game_port(ents, net, texts, tl, art, audio):
    out = []
    net_by_id = {n["id"]: n for n in net}

    def add(**kw):
        out.append({c: kw.get(c, "") for c in PORT_COLS} | {"game_status": "NOT_STARTED"})

    for e in sorted(ents, key=lambda e: (e["entity_type"], e["id"])):
        n = net_by_id.get(e["id"])
        src = e.get("source_file", "")
        note = ""
        if e["swap_kind"] == "NET_NEW":
            src = ""
        elif not src or src == "curated":
            note = "no game source file recorded; find it in ../game by hand"
            src = ""
        add(port_id=f"entity|{e['id']}", table="entities.csv", kind=e["entity_type"] or "unknown",
            wiki_id=e["id"], swap_kind=e["swap_kind"], action=ENTITY_ACTION[e["swap_kind"]], game_file=src,
            wiring=_wiring(n, ("placeholder_from",)) if n else _wiring(e, WIRING_COLS),
            depends_on=n["depends_on"] if n else "", notes=note)
    for t in texts:
        add(port_id=f"text|{t['text_id']}", table="texts.csv", kind=f"text:{t['text_context'] or t['text_origin']}",
            wiki_id=t["text_id"], swap_kind="HOTSWAP" if t["sw_text_raw"] != t["emerald_text_raw"] else "KEEP",
            action="replace the text with sw_text_raw", game_file=t["source_file"], game_line=t["source_line"],
            wiring=_wiring(t, ("map_id", "speaker_label")),
            notes="; ".join(x for x in ("may overflow the text box" if t["overflow_risk"] else "",
                                        f"UI string {t['ui_wider_px']} px wider than Emerald's: make its window fit"
                                        if t["ui_wider_px"] else "") if x))
    for t in tl:
        add(port_id=f"event|{t['id']}", table="timeline_events.csv", kind=f"event:{t.get('type', '')}",
            wiki_id=t["id"], swap_kind="HOTSWAP",
            action="check the event's scripts, flags, maps, trainers and characters all use the swapped content",
            wiring=_wiring(t, ("trigger_flag", "completion_flag", "map_ids", "trainer_ids", "character_ids",
                               "related_entity_ids")),
            depends_on=t.get("previous_event_id", ""))
    for a in art:
        sk = a["swap_kind"]
        if sk == "CUT":
            action, dep = GHOST_ACTION, a.get("replaced_by", "")
        elif a.get("todo") == "HUMAN-TODO":
            action, dep = "HUMAN-TODO: replace it by hand (no generator tool), then set game_status DONE", ""
        elif a["art_status"] in ("KEEP_ANIM", "KEEP_ART", "NO_ART"):
            action, dep = "keep as is; rename only if suggested_path is set", ""
        elif a["art_status"] == "NEEDS_PLACEHOLDER" and a.get("placeholder_from"):
            action = f"add it: copy {a['placeholder_from']} as a placeholder, swap in the new art once art_status is DONE"
            dep = a.get("depends_on", "")
        else:
            action, dep = "copy the redrawn art into ../game once art_status is ART_READY", "art_status ART_READY in pending_art.csv"
        add(port_id=f"art|{a['asset_id']}", table="pending_art.csv", kind=f"art:{a['kind']}",
            wiki_id=a["asset_id"], swap_kind=sk, action=action, game_file=a["path"], game_line=a.get("source_line", ""),
            wiring=a["used_by"], depends_on=dep,
            notes=a.get("art_notes", "") if sk == "CUT" else (f"HUMAN-TODO: {a['sw_subject']}" if a.get("todo") else ""))
    for s in audio:
        sk = s["swap_kind"]
        action = {"HOTSWAP": "replace the sound with the new one once audio_status is DONE; keep its song/cry id",
                  "KEEP": "keep as is",
                  "CUT": GHOST_ACTION,
                  "NET_NEW": f"add a new sound ({s['sw_constant']}): copy {s['placeholder_from']} as a placeholder, "
                             "then swap in the new one once audio_status is DONE"}[sk]
        add(port_id=f"audio|{s['asset_id']}", table="pending_audio.csv", kind=f"audio:{s['category']}:{s['kind']}",
            wiki_id=s["asset_id"], swap_kind=sk, action=action, game_file=s["asset_file"] or s["source_file"],
            game_line="" if s["asset_file"] else s["source_line"], wiring=s["used_by"],
            depends_on=s["depends_on"] or ("audio_status DONE in pending_audio.csv" if sk == "HOTSWAP" else s["replaced_by"]),
            notes=s["notes"] if sk in ("CUT", "NET_NEW") else "")
    return out


# --------------------------------------------------------------------------- main

def main() -> None:
    print("building emerald-sw-db")
    entities, by_id, mapping, sw_ids = load_inputs()
    rows, char_terms = derive(entities, by_id, mapping)

    # net-new rows
    net = read(MAPPING / "net_new.csv")
    flag_ids = {f["flag_id"] for f in read(EMERALD / "story_flags.csv")}
    for n in net:
        for ref in (n.get("placeholder_from"), n.get("depends_on")):
            if ref and ref not in by_id and ref not in flag_ids:
                warn(f"net_new {n['id']}: unknown reference {ref}")
        if n["swap_kind"] != "NET_NEW":
            warn(f"net_new {n['id']}: swap_kind must be NET_NEW")

    # sprite, trainer-picture and tileset rows take the Star Wars subject named for their art (D1/D2)
    subjects_path = MAPPING / "art_subjects.csv"
    if subjects_path.exists():
        subj = {r["asset_id"]: r["sw_subject"] for r in read(subjects_path) if r["sw_subject"]}
        for ea in read(EMERALD / "entity_art.csv"):
            r = rows.get(ea["entity_id"])
            if r and r["entity_type"] in ("object_graphics", "trainer_pic", "tileset") and ea["asset_id"] in subj \
                    and r["map_status"] == "TODO":
                r.update(sw_description=subj[ea["asset_id"]], map_status="DONE",
                         derived_from="mapping/art_subjects.csv")
        # tilesets are not linked in entity_art: match "tileset:battlefrontieroutsideeast" to its folder
        by_folder = {}
        for aid, text in subj.items():
            m = re.match(r"data/tilesets/(?:primary|secondary)/(.+)/[^/]+$", aid)
            if m and "/anim/" not in aid:
                by_folder.setdefault(m.group(1).replace("_", "").replace("/", ""), text)
        for r in rows.values():
            key = r["emerald_id"].split(":", 1)[1].replace("-", "") if r["entity_type"] == "tileset" else ""
            if key in by_folder and r["map_status"] == "TODO":
                r.update(sw_description=by_folder[key], map_status="DONE", derived_from="mapping/art_subjects.csv")
        # map NPCs: who they look like (their sprite's subject) and where they stand (the map's Star Wars title)
        for e in entities:
            if e["entity_type"] != "npc":
                continue
            r, g, m = rows[e["id"]], rows.get(e.get("graphics", ""), {}), rows.get(e.get("map", ""), {})
            look = g.get("sw_description", "")
            if r["map_status"] == "TODO" and look:
                who = re.split(r"[:,(]", look)[0].strip()
                r.update(sw_title=f"{who} ({m.get('sw_title') or m.get('sw_name') or ''})".replace(" ()", ""),
                         sw_description=f"Looks like: {look}. Dialogue: see texts.csv for its script.",
                         map_status="DONE", derived_from="sprite subject + map")

    swap_cols = ["emerald_id", "sw_id", "entity_type", "swap_kind", "map_status", "art_status", "game_status",
                 "emerald_name", "sw_name", "emerald_title", "sw_title", "emerald_constant", "sw_constant",
                 "planet", "sw_basis", "sw_description", "notes", "derived_from", "source_file"]
    swap = sorted(rows.values(), key=lambda r: (r["entity_type"], r["emerald_id"]))
    for r in swap:
        r["sw_id"] = r["emerald_id"]
    for n in net:
        swap.append({"emerald_id": "", "sw_id": n["id"], "entity_type": n["entity_type"], "swap_kind": "NET_NEW",
                     "map_status": n["map_status"], "art_status": n["art_status"], "game_status": "NOT_STARTED",
                     "sw_name": n["sw_name"], "sw_title": n["sw_name"], "planet": n["planet"],
                     "sw_description": n["description"], "notes": n["balance_note"],
                     "derived_from": "mapping/net_new.csv"})
    write("swap_map.csv", swap, swap_cols)
    for n in net:
        n["game_status"] = "NOT_STARTED"
    write("net_new.csv", net)

    # entities: Emerald columns + Star Wars overlay
    ent_out = []
    datapad = load_datapad()
    for e in entities:
        r = rows[e["id"]]
        o = dict(e)
        if e["id"] in datapad:  # species: Star Wars datapad category and entry; Emerald's stay alongside
            o["emerald_dex_category"] = e.get("dex_category", "")
            o["dex_category"] = datapad[e["id"]]["category"]
            o["datapad_text"] = datapad[e["id"]]["text"]
        o["emerald_title"] = e.get("title", "")
        o["emerald_description"] = e.get("description", "")
        if r["sw_title"]:
            o["title"] = r["sw_title"]
        if r.get("sw_description"):
            o["description"] = r["sw_description"]
        for k in ("swap_kind", "map_status", "art_status", "game_status", "sw_name", "sw_constant", "planet", "sw_basis"):
            o[k] = r.get(k, "")
        o["image_path"] = ""  # Emerald art is not copied into this repo; see pending_art.csv
        o["image_status"] = "PENDING_ART"
        ent_out.append(o)
    for n in net:
        ent_out.append({"id": n["id"], "entity_type": n["entity_type"], "category": "net-new", "collection": "net-new",
                        "title": n["sw_name"], "description": n["description"], "swap_kind": "NET_NEW",
                        "map_status": n["map_status"], "art_status": n["art_status"], "game_status": "NOT_STARTED",
                        "planet": n["planet"], "image_status": n["art_status"]})
    lead = ["id", "entity_type", "category", "collection", "title", "description", "history", "swap_kind",
            "map_status", "art_status", "game_status", "sw_name", "sw_constant", "planet", "sw_basis",
            "emerald_title", "emerald_description", "source_constant", "source_file", "image_path", "image_status"]
    cols = lead + [c for c in (ent_out[0].keys()) if c not in lead] + ["emerald_dex_category", "datapad_text"]
    write("entities.csv", ent_out, cols)

    terms, sources, ambiguous = build_terms(rows, by_id, char_terms)
    write("text_terms.csv", [{"emerald_term": k, "sw_term": terms[k], "source": sources.get(k, "")}
                             for k in sorted(terms)] +
          [{"emerald_term": k, "sw_term": " / ".join(v), "source": "AMBIGUOUS (not applied)"}
           for k, v in sorted(ambiguous.items())])
    texts, tcounts = draft_texts(terms)
    for t in texts:
        t["game_status"] = "NOT_STARTED"
    write("texts.csv", texts)

    art = pending_art(rows) + net_new_art(net)
    inv, audio_dec, vfx_dec = load_asset_decisions()
    known = (set(by_id) | {f["flag_id"] for f in read(EMERALD / "story_flags.csv")} | {n["id"] for n in net}
             | set(inv) | set(audio_dec) | set(vfx_dec) | {a["asset_id"] for a in art})
    art += vfx_art(inv, vfx_dec, art, known)
    apply_art_ready(art)
    import frame_sizes  # tools/frame_sizes.py: frame_size + size_class from ../game
    frame_sizes.apply(art)
    for a in art:
        a["game_status"] = "NOT_STARTED"
    art_cols = list(art[0].keys())
    art_cols = [c for c in art_cols if c not in ART_EXTRA_COLS + ["game_status"]] + ART_EXTRA_COLS + ["game_status"]
    art_cols = frame_sizes.order_cols(art_cols)
    write("pending_art.csv", art, art_cols)
    audio = pending_audio(rows, entities, inv, audio_dec, known)
    apply_audio_done(audio)
    write("pending_audio.csv", audio, AUDIO_COLS + ["game_status"])

    # area progression with planets
    ap = []
    for a in read(EMERALD / "area_progression.csv"):
        r = rows.get(a["map_id"], {})
        a = dict(a)
        a["sw_map_title"] = r.get("sw_title", "")
        a["planet"] = r.get("planet", "")
        ap.append(a)
    write("area_progression.csv", ap)

    # timeline
    tl_map = {t["emerald_event_id"]: t for t in read(MAPPING / "timeline.csv")} if (MAPPING / "timeline.csv").exists() else {}
    tl = []
    for t in read(EMERALD / "timeline_events.csv"):
        m = tl_map.get(t["id"])
        o = dict(t)
        o["emerald_title"], o["emerald_description"] = t["title"], t["description"]
        o["planet"] = ""
        o["map_status"] = "TODO"
        if m:
            o["title"] = m["sw_title"] or t["title"]
            o["tagline"] = m.get("sw_tagline") or t.get("tagline", "")
            o["description"] = m["sw_description"] or t["description"]
            o["planet"] = m.get("planet", "")
            o["map_status"] = m.get("map_status") or "DRAFT"
            o["lore"] = m.get("sw_lore") or t.get("lore", "")
        tl.append(o)
    for t in tl_map:
        if t not in {x["id"] for x in tl}:
            warn(f"mapping/timeline.csv: unknown event {t}")
    for o in tl:
        o["game_status"] = "NOT_STARTED"
    write("timeline_events.csv", tl)

    port = game_port(ent_out, net, texts, tl, art, audio)
    write("game_port.csv", port, PORT_COLS)

    info = [{"key": "emerald_db", "value": str(EMERALD)},
            {"key": "emerald_db_commit", "value": next((r["value"] for r in read(EMERALD / "build_info.csv")
                                                       if r.get("key") == "pokeemerald_commit"), "")},
            {"key": "entities", "value": str(len(entities))},
            {"key": "net_new", "value": str(len(net))},
            {"key": "texts_auto", "value": str(tcounts["AUTO"])},
            {"key": "texts_curated", "value": str(tcounts["CURATED"])},
            {"key": "texts_unchanged", "value": str(tcounts["UNCHANGED"])},
            {"key": "art_rows", "value": str(len(art))},
            {"key": "audio_rows", "value": str(len(audio))},
            {"key": "ghost_rows", "value": str(sum(r["swap_kind"] == "CUT" for r in art + audio))},
            {"key": "human_todo_rows", "value": str(sum(r.get("todo") == "HUMAN-TODO" for r in art))},
            {"key": "warnings", "value": str(len(warnings))}]
    write("build_info.csv", info)
    write("build_warnings.csv", [{"warning": w} for w in sorted(set(warnings))])
    print(f"done: {len(warnings)} warnings (see database/build_warnings.csv)")
    for w in sorted(set(warnings))[:40]:
        print("  !", w)


if __name__ == "__main__":
    main()

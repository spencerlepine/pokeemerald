#!/usr/bin/env python3
"""Port every person into ../game from the wiki, and list every person and their assets in one table.

Steps (run all with no argument, or name some):

  walkers  Installs every approved people walker that is still only in the wiki, through the walker tool's spec
           (tools/sprite-walker-generator: the sheet, its palette tag and slot, its size). The spec is the one the
           art row's `drawn_by` names. Walkers, trainer fronts and backs and the professor's portrait already in the
           game byte for byte are marked DONE in pending_art.csv.
  new      The net-new people (mapping/new_people.csv and mapping/people.csv):
           - walker rows: new object graphics in free slots (the six unused doll slots, now ghost rows, and 237-239;
             NUM_OBJ_EVENT_GFX is 240). A walker uses its art from art/<art>, or a copy of `copies`' sheet until
             it is drawn. Constant, pic, pic table, graphics info and pointer, with the palette tag of the spec.
           - class rows: a new trainer class (name, prize money copied from `copies`).
           - trainer rows: Greedo in TRAINER_TERRY (never placed in Emerald).
           - every trainer and boss of mapping/people.csv gets a new trainer slot after TRAINER_MAY_PLACEHOLDER
             (`trainer_const`; MAX_TRAINERS_COUNT is raised to fit, owner 2026-11-04), with its class, pic,
             encounter music, name and the party the wiki gives it.
           - the lines of every net-new person (people.csv `lines`, " / " between texts) go into
             data/text/sw_people.inc, word-wrapped for the 208 px box. Labels: SwPeople_Text_<Name><nnn>_<i>.
           Nothing is placed on a map and no script calls these yet: that is the world-building pass.
  check    Writes database/persons.csv: one row per person (character, walker, trainer pic, back pic, trainer
           class, trainer, Grand Arena trainer, net-new person) with the state of each asset in ../game and
           what still needs wiring.

Run tools/port_names.py and tools/port_texts.py before, as for the creatures. Idempotent: a second run changes
nothing. Needs Pillow only through the walker tool.
"""
import argparse
import collections
import csv
import filecmp
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from port_creatures import (ART, DB, GAME, MAP, ROOT, TOOLS, Src, read_csv, write_csv)  # noqa: E402

WALKER = TOOLS / "sprite-walker-generator"
TAG = "wiki/tools/port_people.py"
FONT = json.loads((ROOT / "tools" / "font_widths.json").read_text(encoding="utf-8"))
BOX_PX = 208
GI = "src/data/object_events/object_event_graphics_info.h"
GFX = "src/data/object_events/object_event_graphics.h"
PICS = "src/data/object_events/object_event_pic_tables.h"
PTRS = "src/data/object_events/object_event_graphics_info_pointers.h"
EV = "include/constants/event_objects.h"
OPP = "include/constants/opponents.h"
FLAGS = "include/constants/flags.h"
TRAINERS = "src/data/trainers.h"
PARTIES = "src/data/trainer_parties.h"
CLASSES = "include/constants/trainers.h"
CLASS_NAMES = "src/data/text/trainer_class_names.h"
BATTLE_MAIN = "src/battle_main.c"
TEXTS = "data/text/sw_people.inc"
FIRST_NEW_TRAINER = 855  # after TRAINER_MAY_PLACEHOLDER
MUSIC = {"male": "MALE", "female": "FEMALE", "girl": "GIRL", "suspicious": "SUSPICIOUS", "intense": "INTENSE",
         "cool": "COOL", "aqua": "AQUA", "magma": "MAGMA", "swimmer": "SWIMMER", "twins": "TWINS",
         "elite-four": "ELITE_FOUR", "hiker": "HIKER", "interviewer": "INTERVIEWER", "rich": "RICH", "boba-fett": "BOBA_FETT"}
# encounter music id -> the song it plays (src/battle_setup.c, PlayTrainerEncounterMusic)
SONG = {"MALE": "MUS_ENCOUNTER_MALE", "FEMALE": "MUS_ENCOUNTER_FEMALE", "GIRL": "MUS_ENCOUNTER_GIRL",
        "SUSPICIOUS": "MUS_ENCOUNTER_SUSPICIOUS", "INTENSE": "MUS_ENCOUNTER_INTENSE", "COOL": "MUS_ENCOUNTER_COOL",
        "AQUA": "MUS_ENCOUNTER_AQUA", "MAGMA": "MUS_ENCOUNTER_MAGMA", "SWIMMER": "MUS_ENCOUNTER_SWIMMER",
        "TWINS": "MUS_ENCOUNTER_TWINS", "ELITE_FOUR": "MUS_ENCOUNTER_ELITE_FOUR", "HIKER": "MUS_ENCOUNTER_HIKER",
        "INTERVIEWER": "MUS_ENCOUNTER_INTERVIEWER", "RICH": "MUS_ENCOUNTER_RICH",
        "BOBA_FETT": "MUS_ENCOUNTER_BOBA_FETT"}
STILL_FRAMES = [0, 1, 2, 0, 0, 1, 1, 2, 2]  # a 3-frame still sheet in the 9-frame standard table


def managed(rel, tag, body, anchor_after=None, anchor_before=None, comment="//"):
    s = Src.get(rel)
    begin = f"{comment} BEGIN {tag} ({TAG})\n"
    end = f"{comment} END {tag}\n"
    block = begin + body + end
    if begin in s.text:
        a = s.text.index(begin)
        b = s.text.index(end, a) + len(end)
        s.text = s.text[:a] + block + s.text[b:]
        return
    m = re.search(anchor_after or anchor_before, s.text, re.M)
    if not m:
        raise SystemExit(f"{rel}: anchor not found: {anchor_after or anchor_before}")
    at = m.end() if anchor_after else m.start()
    s.text = s.text[:at] + block + s.text[at:]


def sub1(rel, pat, rep, flags=0):
    """Replace a regex once if it matches (returns True if the text changed)."""
    s = Src.get(rel)
    new = re.sub(pat, rep, s.text, count=1, flags=flags)
    changed = new != s.text
    s.text = new
    return changed


def entities():
    _, rows = read_csv(DB / "entities.csv")
    return {r["id"]: r for r in rows}


# ---------------------------------------------------------------- walkers
def port_walkers(stats, dry):
    """Install the approved walkers through their specs (before any Src edit: the tool writes the files)."""
    _, art = read_csv(DB / "pending_art.csv")
    for a in art:
        p = a["path"]
        if a["art_status"] != "ART_READY" or not p.startswith("graphics/object_events/pics/people/"):
            continue
        w, g = ART / p, GAME / p
        if w.exists() and g.exists() and filecmp.cmp(w, g, shallow=False):
            continue
        m = re.search(r"\((art/[\w.]+\.yaml)", a["drawn_by"])
        if not m:
            stats["walkers without a spec (not installed)"] += 1
            continue
        if dry:
            stats["walkers to install"] += 1
            continue
        r = subprocess.run([sys.executable, "-m", "walker_sprite", "install", m.group(1)], cwd=WALKER,
                           capture_output=True, text=True)
        if r.returncode:
            print(f"walker install failed: {m.group(1)}\n{r.stdout}{r.stderr}")
            stats["walker installs failed"] += 1
            continue
        if not filecmp.cmp(w, g, shallow=False):  # the spec's output is older than the wiki art: the wiki wins
            shutil.copyfile(w, g)
        stats["walkers installed"] += 1


def mark_art_done(stats, dry):
    """game_status DONE for every people art row (walkers, trainer pics, the professor) in ../game byte for byte."""
    cols, art = read_csv(DB / "pending_art.csv")
    pcols, port = read_csv(DB / "game_port.csv")
    port_by = {p["wiki_id"]: p for p in port if p["table"] == "pending_art.csv"}
    for a in art:
        p = a["path"]
        people = (p.startswith("graphics/object_events/pics/people/") or p.startswith("graphics/trainers/")
                  or a["kind"] == "birch_speech")
        if not people or a["art_status"] != "ART_READY":
            continue
        w, g = ART / p, GAME / p
        if w.exists() and g.exists() and filecmp.cmp(w, g, shallow=False) and a["game_status"] != "DONE":
            a["game_status"] = "DONE"
            stats["art rows marked DONE"] += 1
            if a["asset_id"] in port_by:
                port_by[a["asset_id"]]["game_status"] = "DONE"
    # the net-new walker rows, by the slot they now fill
    _, new = read_csv(MAP / "new_people.csv")
    for n in new:
        if n["kind"] != "walker":
            continue
        for a in art:
            if a["asset_id"] == n["id"]:
                own = (ART / n["art"]).exists() and (GAME / n["art"]).exists() and filecmp.cmp(ART / n["art"], GAME / n["art"], shallow=False)
                if own and a["game_status"] != "DONE":
                    a["game_status"] = "DONE"
                    stats["art rows marked DONE"] += 1
    # the doll pics the new walkers replaced are deleted ghosts
    for a in art:
        if a["swap_kind"] == "CUT" and "/dolls/unused_" in a["path"] and not (GAME / a["path"]).exists() \
                and a["game_status"] != "DONE":
            a["game_status"] = "DONE"
            stats["ghost rows marked DONE"] += 1
            if a["asset_id"] in port_by:
                port_by[a["asset_id"]]["game_status"] = "DONE"
    # the net-new rows that are now in the game (walkers, the class, Greedo)
    ncols, nrows = read_csv(DB / "net_new.csv")
    done_ids = {n["id"] for n in new if (n["kind"] == "walker" and (GAME / n["art"]).exists())
                or (n["kind"] == "class" and n["constant"] in (GAME / "include/constants/trainers.h").read_text())
                or (n["kind"] == "trainer" and f'_("{n["sw_name"]}")' in (GAME / "src/data/trainers.h").read_text())}
    port_net = {p["wiki_id"]: p for p in port if p["table"] == "net_new.csv"}
    for r in nrows:
        if r["id"] in done_ids and r["game_status"] != "DONE":
            r["game_status"] = "DONE"
            stats["net-new rows marked DONE"] += 1
            if r["id"] in port_net:
                port_net[r["id"]]["game_status"] = "DONE"
    if not dry:
        write_csv(DB / "pending_art.csv", cols, art)
        write_csv(DB / "game_port.csv", pcols, port)
        write_csv(DB / "net_new.csv", ncols, nrows)


# ---------------------------------------------------------------- new walkers
def gi_block(text, sym):
    m = re.search(rf"^const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_{sym} = \{{\n.*?^\}};\n\n?",
                  text, re.M | re.S)
    return m


def drop_unused_doll(sym, stats):
    """Remove an unused doll's pic, pic table, graphics info and pointer (its slot is reused)."""
    changed = False
    changed |= sub1(GFX, rf"^const u32 gObjectEventPic_{sym}\[\] = .*\n", "", re.M)
    changed |= sub1(PICS, rf"^static const struct SpriteFrameImage sPicTable_{sym}\[\] = \{{\n.*?^\}};\n\n", "",
                    re.M | re.S)
    s = Src.get(GI)
    m = gi_block(s.text, sym)
    if m:
        s.text = s.text[:m.start()] + s.text[m.end():]
        changed = True
    changed |= sub1(PTRS, rf"^extern const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_{sym};\n", "", re.M)
    changed |= sub1(PTRS, rf"^    \[OBJ_EVENT_GFX_\w+\] = +&gObjectEventGraphicsInfo_{sym},\n", "", re.M)
    if changed:
        stats["unused doll slots freed"] += 1


def port_new_walkers(new, ent, stats, dry):
    walkers = [n for n in new if n["kind"] == "walker"]
    ev = Src.get(EV)
    # free slots: six unused dolls (76-81) and 237-239 (NUM_OBJ_EVENT_GFX 240, OBJ_EVENT_GFX_VARS without the + 1)
    dolls = {76: "UNUSED_NATU_DOLL", 77: "UNUSED_MAGNEMITE_DOLL", 78: "UNUSED_SQUIRTLE_DOLL",
             79: "UNUSED_WOOPER_DOLL", 80: "UNUSED_PIKACHU_DOLL", 81: "UNUSED_PORYGON2_DOLL"}
    for slot, old in dolls.items():
        sym = "".join(p.capitalize() for p in old.lower().split("_"))
        drop_unused_doll(sym, stats)
        png = GAME / f"graphics/object_events/pics/dolls/{old.lower()}.png"
        if png.exists() and not dry:
            png.unlink()
            stats["unused doll pics deleted"] += 1
        n = next((w for w in walkers if int(w["slot"]) == slot), None)
        if n:
            sub1(EV, rf"^#define OBJ_EVENT_GFX_{old} +{slot}\n", f"#define {n['constant']:<41}{slot} // {n['id']}\n",
                 re.M)
    extra = [w for w in walkers if int(w["slot"]) >= 237]
    managed(EV, "net-new walkers", "".join(f"#define {w['constant']:<41}{w['slot']} // {w['id']}\n" for w in extra),
            anchor_after=r"^#define OBJ_EVENT_GFX_HOOH +236\n")
    top = max([236] + [int(w["slot"]) for w in extra]) + 1
    sub1(EV, r"^#define NUM_OBJ_EVENT_GFX +\d+", f"#define NUM_OBJ_EVENT_GFX                        {top}", re.M)
    if top > 239:  # pret: no graphics id uses 239, so the + 1 can go (VAR_F is then 255, the u8 limit)
        sub1(EV, r"^#define OBJ_EVENT_GFX_VARS +\(NUM_OBJ_EVENT_GFX \+ 1\)",
             "#define OBJ_EVENT_GFX_VARS   (NUM_OBJ_EVENT_GFX)", re.M)
        sub1(EV, r"(#define OBJ_EVENT_GFX_VAR_0 +\(OBJ_EVENT_GFX_VARS \+ 0x0\) // )\d+", rf"\g<1>{top}")
        sub1(EV, r"(#define OBJ_EVENT_GFX_VAR_F +\(OBJ_EVENT_GFX_VARS \+ 0xF\) // )\d+", rf"\g<1>{top + 15}")
    pics, tables, infos, externs, ptrs = [], [], [], [], []
    gi_text = Src.get(GI).text
    for w in walkers:
        sym = w["symbol"]
        src = ent[w["copies"]]
        src_sym = src["graphics_info_symbol"].removeprefix("gObjectEventGraphicsInfo_")
        src_png = json.loads(src["sprite_paths"])[0]
        dst = GAME / w["art"]
        own = (ART / w["art"]).exists()
        if not dry:
            if own:
                if not dst.exists() or not filecmp.cmp(ART / w["art"], dst, shallow=False):
                    shutil.copyfile(ART / w["art"], dst)
                    stats["net-new walker sheets installed"] += 1
            elif not dst.exists():
                shutil.copyfile(GAME / src_png, dst)
                stats["net-new walker placeholders made"] += 1
        still = False
        if own:
            from PIL import Image  # noqa: only to read the sheet width
            still = Image.open(ART / w["art"]).width == 48
        pics.append(f'const u32 gObjectEventPic_{sym}[] = INCGFX_U32("{w["art"]}", ".4bpp", "-mwidth 2 -mheight 4");\n')
        frames = STILL_FRAMES if still else range(9)
        tables.append(f"static const struct SpriteFrameImage sPicTable_{sym}[] = {{\n"
                      + "".join(f"    overworld_frame(gObjectEventPic_{sym}, 2, 4, {i}),\n" for i in frames) + "};\n\n")
        m = gi_block(gi_text, src_sym)
        if not m:
            raise SystemExit(f"no gObjectEventGraphicsInfo_{src_sym} to copy for {w['id']}")
        block = m.group(0).rstrip() + "\n\n"
        block = block.replace(f"gObjectEventGraphicsInfo_{src_sym} =", f"gObjectEventGraphicsInfo_{sym} =")
        block = re.sub(r"\.images = \w+,", f".images = sPicTable_{sym},", block)
        if w["palette_tag"]:
            block = re.sub(r"\.paletteTag = \w+,", f".paletteTag = {w['palette_tag']},", block)
            block = re.sub(r"\.paletteSlot = \w+,", f".paletteSlot = {w['palette_tag'].replace('OBJ_EVENT_PAL_TAG_', 'PALSLOT_')},", block)
        infos.append(f"// {w['id']}: {w['sw_name']}\n" + block)
        externs.append(f"extern const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_{sym};\n")
        ptrs.append(f"    [{w['constant']}] = &gObjectEventGraphicsInfo_{sym},\n")
    managed(GFX, "net-new walkers", "".join(pics), anchor_after=r"^const u16 gObjectEventPal_HoOh\[\] = .*\n")
    managed(PICS, "net-new walkers", "".join(tables), anchor_after=r"^static const struct SpriteFrameImage sPicTable_HoOh\[\] = \{\n(?:.*\n)*?\};\n")
    managed(GI, "net-new walkers", "".join(infos), anchor_after=r"^const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_HoOh = \{\n(?:.*\n)*?\};\n")
    managed(PTRS, "net-new walker externs", "".join(externs),
            anchor_after=r"^extern const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_HoOh;\n")
    managed(PTRS, "net-new walkers", "".join(ptrs), anchor_after=r"^    \[OBJ_EVENT_GFX_HOOH\] = .*\n")
    stats["net-new walkers"] = len(walkers)


# ---------------------------------------------------------------- text
def text_px(s):
    return sum(FONT.get(c, 6) for c in s)


CHARS = {'"': None, "—": "-", "–": "-", "‘": "'", "’": "'"}


def clean(s):
    """Plain wiki text to the game's charset: straight double quotes become “ ”, dashes become -."""
    out, open_q = [], True
    for c in s:
        if c == '"':
            out.append("“" if open_q else "”")
            open_q = not open_q
        else:
            out.append(CHARS.get(c, c) or c)
    return "".join(out)


def wrap(s):
    """Word-wrap one plain line into Emerald boxes: two lines per box (\\n), boxes split by \\p, ends with $."""
    s = s.strip()
    if "\\n" in s or "\\p" in s or s.endswith("$"):
        return s if s.endswith("$") else s + "$"
    lines, cur = [], ""
    for word in clean(s).split():
        t = f"{cur} {word}".strip()
        if cur and text_px(t) > BOX_PX:
            lines.append(cur)
            cur = word
        else:
            cur = t
    lines.append(cur)
    out = ""
    for i, ln in enumerate(lines):
        out += ln + ("" if i == len(lines) - 1 else ("\\n" if i % 2 == 0 else "\\p"))
    return out + "$"


def split_lines(lines):
    return [x for x in (p.strip() for p in lines.split(" / ")) if x]


def label_of(name, num):
    base = "".join(p.capitalize() for p in re.split(r"[^A-Za-z0-9]+", name) if p) or "Person"
    return f"SwPeople_Text_{base}{num}"


def asm_string(text):
    parts = re.split(r"(?<=\\[nlp])", text)
    return "".join(f'\t.string "{p}"\n' for p in parts if p)


# ---------------------------------------------------------------- trainers
def pic_const(ent, pid):
    return ent[pid]["source_constant"]


def class_const(ent, new_by, cid):
    if cid in new_by:
        return new_by[cid]["constant"]
    if cid == "net:trainer-class-skiff-rider":
        return "TRAINER_CLASS_SKIFF_RIDER"
    return ent[cid]["source_constant"]


def party_mons(party):
    out = []
    for p in party.split("|"):
        sp, lvl = p.split("@")
        out.append((f"SPECIES_{sp.split(':', 1)[1].upper().replace('-', '_')}", int(lvl)))
    return out


def trainer_entry(const, cls, music, gender, pic, name, party_sym, boss):
    mus = f"TRAINER_ENCOUNTER_MUSIC_{MUSIC[music or 'male']}"
    if gender == "female":
        mus = "F_TRAINER_FEMALE | " + mus
    ai = ("AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY" if boss
          else "AI_SCRIPT_CHECK_BAD_MOVE")
    return (f"    [{const}] =\n    {{\n        .trainerClass = {cls},\n        .encounterMusic_gender = {mus},\n"
            f"        .trainerPic = {pic},\n        .trainerName = _(\"{name}\"),\n        .items = {{}},\n"
            f"        .doubleBattle = FALSE,\n        .aiFlags = {ai},\n"
            f"        .party = NO_ITEM_DEFAULT_MOVES({party_sym}),\n    }},\n\n")


def party_def(sym, mons, iv):
    body = "".join(f"    {{\n    .iv = {iv},\n    .lvl = {lvl},\n    .species = {sp},\n    }},\n" for sp, lvl in mons)
    return f"static const struct TrainerMonNoItemDefaultMoves {sym}[] = {{\n{body}}};\n\n"


def port_people_trainers(new, ent, stats, dry=False):
    new_by = {n["id"]: n for n in new}
    # the new class
    for c in (n for n in new if n["kind"] == "class"):
        src = ent[c["copies"]]["source_constant"]
        managed(CLASSES, "net-new classes", f"#define {c['constant']:<28}{c['slot']} // Star Wars net-new: {c['notes']}\n",
                anchor_after=r"^#define TRAINER_CLASS_SKIFF_RIDER .*\n")
        managed(CLASS_NAMES, "net-new classes", f"    [{c['constant']}] = _(\"{c['sw_name']}\"),\n",
                anchor_after=r"^    \[TRAINER_CLASS_SKIFF_RIDER\] = .*\n")
        money = re.search(rf"\{{{src}, (\d+)\}}", Src.get(BATTLE_MAIN).text).group(1)
        managed(BATTLE_MAIN, "net-new classes", f"    {{{c['constant']}, {money}}}, // as {src}\n",
                anchor_after=r"^    \{TRAINER_CLASS_SKIFF_RIDER, \d+\},.*\n")
        stats["net-new trainer classes"] += 1
    texts = []
    # Greedo in an Emerald slot that is never placed
    for t in (n for n in new if n["kind"] == "trainer"):
        const = t["constant"]
        sym = "sParty_" + "".join(p.capitalize() for p in const.removeprefix("TRAINER_").lower().split("_"))
        entry = trainer_entry(const, class_const(ent, new_by, t["trainer_class"]), t["music"], t["gender"],
                              pic_const(ent, t["trainer_pic"]), t["sw_name"], sym, False).rstrip() + "\n"
        s = Src.get(TRAINERS)
        m = re.search(rf"^    \[{const}\] =\n    \{{\n.*?^    \}},\n", s.text, re.M | re.S)
        s.text = s.text[:m.start()] + entry + s.text[m.end():]
        p = Src.get(PARTIES)
        m = re.search(rf"^static const struct \w+ {sym}\[\] = \{{\n.*?^\}};\n", p.text, re.M | re.S)
        p.text = p.text[:m.start()] + party_def(sym, party_mons(t["party"]), 0).rstrip() + "\n" + p.text[m.end():]
        for i, ln in enumerate(split_lines(t["lines"]), 1):
            texts.append((f"{label_of(t['sw_name'], '')}_{i}", t["id"], wrap(ln)))
        stats["net-new trainers in Emerald slots"] += 1
    # every trainer and boss of the new areas, in new slots
    _, people = read_csv(MAP / "people.csv")
    defines, entries, parties = [], [], []
    slot = FIRST_NEW_TRAINER
    for p in people:
        num = p["person_id"].rsplit(":", 1)[1]
        if p["kind"] in ("trainer", "boss") and p["trainer_const"]:
            sym = "sParty_Sw" + "".join(x.capitalize() for x in p["trainer_const"].removeprefix("TRAINER_SW_").lower().split("_"))
            defines.append(f"#define {p['trainer_const']:<36}{slot} // {p['person_id']}\n")
            entries.append(trainer_entry(p["trainer_const"], class_const(ent, new_by, p["trainer_class"]), p["music"],
                                         p["gender"], pic_const(ent, p["trainer_pic"]), p["trainer_name"], sym,
                                         p["kind"] == "boss"))
            parties.append(party_def(sym, party_mons(p["party"]), 100 if p["kind"] == "boss" else 0))
            slot += 1
        if p["lines"] and (p["character"].startswith("net:") or not p["character"]):
            name = p["trainer_name"] or p["yaml_name"] or p["character"].split(":")[-1].removeprefix("character-")
            for i, ln in enumerate(split_lines(p["lines"]), 1):
                texts.append((f"{label_of(name, num)}_{i}", p["person_id"], wrap(ln)))
    count = slot
    max_count = (count + 7) // 8 * 8
    managed(OPP, "net-new trainers", "".join(defines), anchor_after=r"^#define TRAINER_MAY_PLACEHOLDER +854\n")
    sub1(OPP, r"^#define TRAINERS_COUNT +\d+", f"#define TRAINERS_COUNT                      {count}", re.M)
    sub1(OPP, r"^#define MAX_TRAINERS_COUNT +\d+", f"#define MAX_TRAINERS_COUNT                  {max_count}", re.M)
    sub1(OPP, r"there is only space for \d+ additional trainers", f"there is only space for {max_count - count} additional trainers")
    end = 0x500 + max_count - 1
    sub1(FLAGS, r"Trainer flags occupy 0x500 - 0x[0-9A-F]+, the last \d+ of which are unused",
         f"Trainer flags occupy 0x500 - 0x{end:X}, the last {max_count - count} of which are unused")
    sub1(FLAGS, r"(MAX_TRAINERS_COUNT - 1\) // )0x[0-9A-F]+", rf"\g<1>0x{end:X}")
    sub1(FLAGS, r"(#define SYSTEM_FLAGS +\(TRAINER_FLAGS_END \+ 1\) // )0x[0-9A-F]+", rf"\g<1>0x{end + 1:X}")
    managed(TRAINERS, "net-new trainers", "".join(entries), anchor_before=r"^\};\s*\Z")
    managed(PARTIES, "net-new trainers", "".join(parties), anchor_before=r"\Z")
    stats["net-new trainers in new slots"] = count - FIRST_NEW_TRAINER
    # the lines
    body = "".join(f"@ {src}\n{lab}::\n{asm_string(txt)}\n" for lab, src, txt in texts)
    path = GAME / TEXTS
    head = (f"@ Lines of the net-new people (wiki/mapping/people.csv, mapping/new_people.csv), written by {TAG}.\n"
            "@ No script uses them yet: the world-building pass places the people and calls these labels.\n\n")
    if not dry and (not path.exists() or path.read_text(encoding="utf-8") != head + body):
        path.write_text(head + body, encoding="utf-8")
        stats["text file written"] += 1
    Src.open_files.pop(TEXTS, None)
    managed("data/event_scripts.s", "net-new people text", f'\t.include "{TEXTS}"\n',
            anchor_after=r'^\t\.include "data/text/obtain_item\.inc"\n', comment="@")
    stats["net-new texts"] = len(texts)


# ---------------------------------------------------------------- check
def check(stats):
    """database/persons.csv: every person and the state of each of their assets in ../game."""
    ent = entities()
    _, art = read_csv(DB / "pending_art.csv")
    art_by = {a["path"]: a for a in art}
    _, music = read_csv(DB / "music.csv")
    song_status = {m.get("emerald_constant") or m.get("constant") or "": m.get("rewrite_status", "") for m in music}
    _, texts = read_csv(DB / "texts.csv")
    _, people = read_csv(MAP / "people.csv")
    _, new = read_csv(MAP / "new_people.csv")
    _, npcs = read_csv(DB / "npcs.csv")
    new_by = {n["id"]: n for n in new}
    gi = (GAME / GI).read_text()
    ptrs = (GAME / PTRS).read_text()
    ev = (GAME / EV).read_text()
    tr_src = (GAME / TRAINERS).read_text()
    opp = dict(re.findall(r"#define (TRAINER_\w+) +(\d+)", (GAME / OPP).read_text()))
    tr_game = {m.group(1): m.group(2) for m in re.finditer(r"^    \[(TRAINER_\w+)\] =\n    \{\n(.*?)^    \},", tr_src, re.M | re.S)}
    cls_names = dict(re.findall(r"\[(TRAINER_CLASS_\w+)\] = _\(\"([^\"]*)\"\)", (GAME / CLASS_NAMES).read_text()))
    money = dict(re.findall(r"\{(TRAINER_CLASS_\w+), (\d+)\}", (GAME / BATTLE_MAIN).read_text()))
    front_tbl = (GAME / "src/data/trainer_graphics/front_pic_tables.h").read_text()
    sw_people = (GAME / TEXTS).read_text() if (GAME / TEXTS).exists() else ""
    rematch = set(re.findall(r"REMATCH\(\s*(TRAINER_\w+)", (GAME / "src/battle_setup.c").read_text()))
    used = set()
    for f in (GAME / "data/maps").glob("*/scripts.inc"):
        used.update(re.findall(r"\b(TRAINER_\w+)\b", f.read_text()))
    for f in (GAME / "data/scripts").glob("*.inc"):
        used.update(re.findall(r"\b(TRAINER_\w+)\b", f.read_text()))
    placed_gfx = collections.Counter(n["graphics_id"] for n in npcs)
    for f in (GAME / "data/maps").glob("*/map.json"):
        pass
    speaker = collections.defaultdict(lambda: [0, 0])
    for t in texts:
        if t["speaker_label"]:
            speaker[t["speaker_label"]][1] += 1
            speaker[t["speaker_label"]][0] += t["game_status"] == "DONE"

    def art_state(path):
        if not path:
            return ""
        a = art_by.get(path)
        g = (GAME / path).exists()
        if a and a["game_status"] == "DONE":
            return "DONE"
        if a and a.get("todo") == "HUMAN-TODO":
            return "HUMAN-TODO"
        if a:
            return a["art_status"] if g else "MISSING"
        return "IN_GAME" if g else "MISSING"

    def walker_state(wid):
        """(constant, file, state, palette tag) of an object-gfx id or a net-new walker id."""
        if not wid:
            return "", "", "GAP: no walker", ""
        if wid in new_by:
            n = new_by[wid]
            in_game = f"[{n['constant']}]" in ptrs and (GAME / n["art"]).exists()
            own = (ART / n["art"]).exists()
            state = ("DONE" if own else "PLACEHOLDER") if in_game else "MISSING"
            m = re.search(rf"gObjectEventGraphicsInfo_{n['symbol']} = \{{.*?\.paletteTag = (\w+)", gi, re.S)
            return n["constant"], n["art"], state, m.group(1) if m else ""
        e = ent.get(wid)
        if not e:
            return "", "", f"GAP: unknown walker {wid}", ""
        path = json.loads(e["sprite_paths"] or "[]")
        path = path[0] if path else ""
        sym = e["graphics_info_symbol"]
        m = re.search(rf"{sym} = \{{.*?\.paletteTag = (\w+)", gi, re.S)
        return e["source_constant"], path, art_state(path), m.group(1) if m else ""

    rows = []

    def add(**kw):
        gaps = [k for k, v in kw.items() if isinstance(v, str) and (v.startswith("GAP") or v in ("MISSING", "PENDING_ART", "NEEDS_PLACEHOLDER", "TODO", "NOT_IN_GAME", "HUMAN-TODO"))]
        kw["gaps"] = "; ".join(f"{g}={kw[g]}" for g in gaps)
        rows.append(kw)

    # walkers (people object graphics)
    for e in ent.values():
        if e["entity_type"] == "object_graphics" and "/people/" in (e["sprite_paths"] or "") and not e["id"].startswith("net:"):
            c, path, st, pal = walker_state(e["id"])
            add(person_id=e["id"], kind="walker", sw_name=e["description"], game_constant=c, walker=e["id"],
                walker_file=path, walker_status=st, palette_tag=pal,
                wiring=f"placed {placed_gfx.get(c, 0)} times" if placed_gfx.get(c) else "not placed on any map")
    for n in new:
        if n["kind"] == "walker":
            c, path, st, pal = walker_state(n["id"])
            add(person_id=n["id"], kind="walker", sw_name=n["sw_name"], game_constant=c, walker=n["id"],
                walker_file=path, walker_status=st, palette_tag=pal, wiring="not placed yet (world-building)")
    # trainer portraits and back pics
    for e in ent.values():
        if e["entity_type"] == "trainer_pic":
            p = e["image_source_path"]
            add(person_id=e["id"], kind="trainer_pic", sw_name=e["description"][:80], game_constant=e["source_constant"],
                portrait=p, portrait_status=art_state(p) if e["image_symbol"] in front_tbl or (GAME / p).exists() else "MISSING")
    for a in art:
        if a["path"].startswith("graphics/trainers/back_pics/") and a["path"].endswith(".png"):
            add(person_id=a["asset_id"], kind="back_pic", sw_name=a["sw_subject"], back_pic=a["path"],
                back_status=art_state(a["path"]))
    # classes
    for e in ent.values():
        if e["entity_type"] == "trainer_class":
            c = e["source_constant"]
            add(person_id=e["id"], kind="trainer_class", sw_name=e["sw_name"], game_constant=c,
                class_name=("DONE" if cls_names.get(c) == e["sw_name"] else ("NOT_IN_GAME" if c not in cls_names else f"GAP: game says {cls_names.get(c)}")),
                money=money.get(c, ""))
    for cid, const, name in (("net:trainer-class-skiff-rider", "TRAINER_CLASS_SKIFF_RIDER", "SKIFF RIDER"),) + tuple(
            (n["id"], n["constant"], n["sw_name"]) for n in new if n["kind"] == "class"):
        add(person_id=cid, kind="trainer_class", sw_name=name, game_constant=const,
            class_name="DONE" if cls_names.get(const) == name else "NOT_IN_GAME", money=money.get(const, ""))

    def trainer_row(pid, kind, const, sw_name, walker, extra_wiring=""):
        body = tr_game.get(const)
        if body is None or const not in opp:
            add(person_id=pid, kind=kind, sw_name=sw_name, game_constant=const, trainer="NOT_IN_GAME")
            return
        g = dict(re.findall(r"\.(\w+) = (.*?),?\n", body))
        name = re.search(r'_\("([^"]*)"\)', g.get("trainerName", "")).group(1)
        cls, pic = g.get("trainerClass", ""), g.get("trainerPic", "")
        mus = re.search(r"TRAINER_ENCOUNTER_MUSIC_(\w+)", g.get("encounterMusic_gender", ""))
        song = SONG.get(mus.group(1), "") if mus else ""
        pic_e = next((e for e in ent.values() if e["entity_type"] == "trainer_pic" and e["source_constant"] == pic), None)
        c, wfile, wst, pal = walker_state(walker) if walker or kind.startswith("new_") else ("", "", "", "")
        add(person_id=pid, kind=kind, sw_name=sw_name, game_constant=const, trainer="DONE",
            name_status="DONE" if name == sw_name else f"GAP: game says {name}", trainer_class=cls,
            class_name=cls_names.get(cls, "NOT_IN_GAME"), money=money.get(cls, ""),
            portrait=pic, portrait_status=art_state(pic_e["image_source_path"]) if pic_e else "MISSING",
            walker=walker, walker_file=wfile, walker_status=wst, palette_tag=pal,
            music=song, music_status=song_status.get(song, ""), match_call="yes" if const in rematch else "",
            wiring=extra_wiring or ("in a map script" if const in used else "not in any script"))

    # Emerald trainers (the walker is the one a map gives them, when placed)
    reused = {n["constant"]: n["id"] for n in new if n["kind"] == "trainer"}
    for e in ent.values():
        if e["entity_type"] == "trainer" and not e["id"].startswith("net:"):
            if e["source_constant"] in reused:  # an unplaced Emerald slot that now holds a net-new trainer
                add(person_id=e["id"], kind="trainer", sw_name=e["sw_name"], game_constant=e["source_constant"],
                    trainer=f"slot reused by {reused[e['source_constant']]}")
                continue
            trainer_row(e["id"], "trainer", e["source_constant"], e["sw_name"], "")
    # Grand Arena trainers: names only (the class and pic come from their facility class)
    fr = (GAME / "src/data/battle_frontier/battle_frontier_trainers.h").read_text()
    for e in ent.values():
        if e["entity_type"] == "facility_trainer":
            m = re.search(rf"\[{e['source_constant']}\] =.*?\.trainerName = _\(\"([^\"]*)\"\)", fr, re.S)
            add(person_id=e["id"], kind="grand_arena_trainer", sw_name=e["sw_name"], game_constant=e["source_constant"],
                name_status=("DONE" if m and m.group(1) == e["sw_name"] else (f"GAP: game says {m.group(1)}" if m else "")),
                trainer_class=e["trainer_class"], portrait=e["trainer_pic"])
    # characters (a net-new one uses the walker its people.csv row names)
    net_walker = {p["character"]: p["walker"] for p in people if p["character"].startswith("net:") and p["walker"]}
    for e in ent.values():
        if e["entity_type"] == "character":
            wid = (e["sprite_ids"] or "").split("|")[0] or net_walker.get(e["id"], "")
            c, wfile, wst, pal = walker_state(wid) if wid else ("", "", "", "")
            tid = (e["trainer_ids"] or "").split("|")[0]
            pic = ent[tid]["trainer_pic"] if tid in ent else ""
            sp = speaker.get(e["emerald_title"].split(" (")[0].upper(), [0, 0])
            add(person_id=e["id"], kind="character", sw_name=e["sw_name"], game_constant=ent[tid]["source_constant"] if tid in ent else "",
                walker=wid, walker_file=wfile, walker_status=wst if wid else "no walker (never on a map)", palette_tag=pal,
                portrait=ent[pic]["source_constant"] if pic in ent else "", portrait_status=art_state(ent[pic]["image_source_path"]) if pic in ent else "",
                dialogue=f"{sp[0]}/{sp[1]} lines DONE" if sp[1] else "")
    # net-new people (characters without an Emerald slot and every person of the new areas)
    for p in people:
        num = p["person_id"].rsplit(":", 1)[1]
        lines = split_lines(p["lines"]) if p["lines"] else []
        name = p["trainer_name"] or p["yaml_name"] or p["character"].split(":")[-1].removeprefix("character-")
        lab = label_of(name, num)
        said = sum(f"{lab}_{i}::" in sw_people for i in range(1, len(lines) + 1))
        dialogue = ("Emerald character: its own lines" if p["character"].startswith("character:") else
                    (f"{said}/{len(lines)} lines in {TEXTS}" if lines else "GAP: no lines"))
        if p["kind"] in ("trainer", "boss") and p["trainer_const"]:
            trainer_row(p["person_id"], f"new_{p['kind']}", p["trainer_const"], p["trainer_name"], p["walker"],
                        "not placed yet (world-building)")
            rows[-1]["dialogue"] = dialogue
            rows[-1]["character"] = p["character"]
            continue
        c, wfile, wst, pal = walker_state(p["walker"]) if p["kind"] != "wild" else ("", "", "", "")
        add(person_id=p["person_id"], kind=f"new_{p['kind']}", sw_name=p["yaml_name"] or p["character"],
            character=p["character"], game_constant=c, walker=p["walker"], walker_file=wfile, walker_status=wst,
            palette_tag=pal, dialogue=dialogue if p["kind"] != "wild" else "", wiring="not placed yet (world-building)")
    for n in new:
        if n["kind"] == "trainer":
            trainer_row(n["id"], "new_trainer", n["constant"], n["sw_name"], n["walker"], "not placed yet (world-building)")
            lines = split_lines(n["lines"])
            said = sum(f"{label_of(n['sw_name'], '')}_{i}::" in sw_people for i in range(1, len(lines) + 1))
            rows[-1]["dialogue"] = f"{said}/{len(lines)} lines in {TEXTS}"
    cols = ["person_id", "kind", "sw_name", "character", "game_constant", "walker", "walker_file", "walker_status",
            "palette_tag", "portrait", "portrait_status", "back_pic", "back_status", "trainer", "trainer_class",
            "class_name", "money", "name_status", "music", "music_status", "match_call", "dialogue", "wiring", "gaps"]
    write_csv(DB / "persons.csv", cols, [{c: r.get(c, "") for c in cols} for r in rows])
    c = collections.Counter(r["kind"] for r in rows)
    stats["persons.csv rows"] = len(rows)
    stats["persons.csv rows with gaps"] = sum(bool(r["gaps"]) for r in rows)
    for k, v in sorted(c.items()):
        stats[f"persons: {k}"] = v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("steps", nargs="*", default=["walkers", "new", "check"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    stats = collections.Counter()
    if "walkers" in a.steps:  # first: the walker tool writes the game files itself
        port_walkers(stats, a.dry_run)
    if "new" in a.steps:
        _, new = read_csv(MAP / "new_people.csv")
        ent = entities()
        port_new_walkers(new, ent, stats, a.dry_run)
        port_people_trainers(new, ent, stats, a.dry_run)
    changed = Src.save_all(a.dry_run)
    if "walkers" in a.steps or "new" in a.steps:
        mark_art_done(stats, a.dry_run)
    if "check" in a.steps:
        check(stats)
    print(", ".join(f"{k}: {v}" for k, v in sorted(stats.items())))
    print("changed:" if changed else "no source changes", *changed, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())

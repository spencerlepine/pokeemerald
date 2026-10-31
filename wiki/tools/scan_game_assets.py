"""Inventory every sound and visual-effect asset in ../game -> mapping/asset_inventory.csv.

    python3 tools/scan_game_assets.py            # GAME_DIR=/path/to/game to override

Images (PNGs) are already listed one per file in database/pending_art.csv (from emerald-db). This scan
adds what emerald-db does not track:

  music   every MUS_* song (sound/songs/midi/*.mid), BGM or fanfare
  sfx     every SE_* sound effect and PH_* phoneme (the Mauville bard's voice)
  cry     every companion cry sample (sound/direct_sound_samples/cries/*.wav, gCryTable)
  vfx     battle status/general/special animations (data/battle_anim_scripts.s), field effects
          (data/field_effect_scripts.s), overworld weather (src/field_weather.c) and battle
          transitions (src/battle_transition.c)

Move animations are not repeated here: they are already rows in pending_art.csv (anim:Move_*).

Every row points back at the game source (`source_file:source_line`, `asset_file`) so the wiki is a source
map. `refs` lists where the game uses the asset. The scan is generated, never edit it by hand: the
Star Wars decision for each row is hand-written in mapping/audio.csv or mapping/vfx.csv, and
tools/build.py warns when an inventory row has no decision.

Deterministic: same game source gives a byte-identical file.
"""
from __future__ import annotations

import csv
import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(os.environ.get("GAME_DIR", ROOT.parent / "game"))
OUT = ROOT / "mapping" / "asset_inventory.csv"
COLS = ["asset_id", "category", "kind", "subkind", "emerald_constant", "source_file", "source_line",
        "asset_file", "ref_count", "refs", "used_by"]
MAX_REFS = 6

SRC_EXT = (".c", ".h", ".inc", ".s", ".json")


def rel(p: Path) -> str:
    return p.relative_to(GAME).as_posix()


def source_files():
    for top in ("src", "data", "include", "asm"):
        for dp, dn, fn in os.walk(GAME / top):
            dn.sort()
            for f in sorted(fn):
                if f.endswith(SRC_EXT):
                    yield Path(dp) / f


def find_line(path: Path, needle: str) -> int:
    for i, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
        if needle in line:
            return i
    return 0


def slug_species(name: str) -> str:
    return name.lower().replace("_", "-")


def main() -> None:
    songs_h = GAME / "include/constants/songs.h"
    # ---- reference index: constant -> [path:line]
    refs: dict[str, list[str]] = defaultdict(list)
    pat = re.compile(r"\b((?:MUS|SE|PH)_[A-Z0-9_]+|Cry_[A-Za-z0-9_]+|FLDEFF_[A-Z0-9_]+|WEATHER_[A-Z0-9_]+|"
                     r"B_TRANSITION_[A-Z0-9_]+|B_ANIM_[A-Z0-9_]+)\b")
    for p in source_files():
        if p == songs_h:
            continue
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            for m in set(pat.findall(line)):
                refs[m].append(f"{rel(p)}:{i}")

    rows: list[dict] = []

    def add(**kw):
        r = {c: "" for c in COLS}
        r.update(kw)
        rs = refs.get(r["emerald_constant"], [])
        own = f"{r['source_file']}:{r['source_line']}"
        rs = [x for x in rs if x != own]
        r["ref_count"] = str(len(rs))
        r["refs"] = " ".join(rs[:MAX_REFS]) + (f" (+{len(rs) - MAX_REFS} more)" if len(rs) > MAX_REFS else "")
        rows.append(r)

    # ---- music + sfx
    table = {}
    st = GAME / "sound/song_table.inc"
    for i, line in enumerate(st.read_text().splitlines(), 1):
        m = re.match(r"\s*song (\w+), (MUSIC_PLAYER_\w+)", line)
        if m:
            table.setdefault(m.group(1).upper(), (m.group(2), i))
    fanfares = set(re.findall(r"\{ (MUS_\w+),", (GAME / "src/sound.c").read_text()))
    # maps that play each song (data/maps/*/map.json "music")
    map_music: dict[str, list[str]] = defaultdict(list)
    for mj in sorted((GAME / "data/maps").glob("*/map.json")):
        m = re.search(r'"music": "(\w+)"', mj.read_text())
        if m:
            map_music[m.group(1)].append(mj.parent.name)
    # move animation -> sound effects it plays
    se_moves: dict[str, list[str]] = defaultdict(list)
    anim_src = GAME / "data/battle_anim_scripts.s"
    labels: list[str] = []
    for line in anim_src.read_text().splitlines():
        lm = re.match(r"^(Move_\w+):", line)
        if lm:
            labels.append(lm.group(1))
            continue
        if re.match(r"^\w+:", line):
            labels = []
            continue
        for se in re.findall(r"\b(SE_[A-Z0-9_]+)\b", line):
            for lab in labels:
                mv = "move:" + lab[5:].lower().replace("_", "-")
                if mv not in se_moves[se] and lab not in ("Move_NONE",):
                    se_moves[se].append(mv)
        if line.strip() == "end":
            labels = []
    for i, line in enumerate(songs_h.read_text().splitlines(), 1):
        m = re.match(r"#define ((MUS|SE|PH)_\w+)\s+(\d+)", line)
        if not m:
            continue
        const, prefix = m.group(1), m.group(2)
        if const == "MUS_NONE":
            continue
        midi = GAME / "sound/songs/midi" / (const.lower() + ".mid")
        player = table.get(const, ("", 0))[0]
        if prefix == "MUS":
            cat = "music"
            if const in fanfares:
                kind = "fanfare"
            elif const.startswith("MUS_RG_"):
                kind = "frlg_music"
            elif const.startswith(("MUS_VS_", "MUS_ENCOUNTER_", "MUS_VICTORY_")) or "_VS_" in const:
                kind = "battle_music"
            else:
                kind = "bgm"
        else:
            cat = "sfx"
            kind = "phoneme" if prefix == "PH" else ("move_sfx" if const.startswith("SE_M_") else "sfx")
        used = [f"map_folder:{n}" for n in map_music.get(const, [])] + se_moves.get(const, [])
        add(asset_id=f"audio:{const}", category=cat, kind=kind, subkind=player.replace("MUSIC_PLAYER_", "").lower(),
            emerald_constant=const, source_file=rel(songs_h), source_line=str(i),
            asset_file=rel(midi) if midi.exists() else "", used_by="|".join(used))

    # ---- cries
    dsd = GAME / "sound/direct_sound_data.inc"
    cry_file = {}
    text = dsd.read_text().splitlines()
    for i, line in enumerate(text):
        m = re.match(r"^(Cry_\w+)::", line)
        if m and i + 1 < len(text):
            f = re.search(r'"(sound/direct_sound_samples/cries/[^"]+)\.bin"', text[i + 1])
            if f:
                cry_file[m.group(1)] = (f.group(1) + ".wav", i + 1)
    seen = set()
    ct = GAME / "sound/cry_tables.inc"
    for i, line in enumerate(ct.read_text().splitlines(), 1):
        m = re.match(r"\s*cry (Cry_\w+)", line)
        if not m or m.group(1) in seen:
            continue
        lab = m.group(1)
        seen.add(lab)
        wav, _ = cry_file.get(lab, ("", 0))
        name = Path(wav).stem
        add(asset_id=f"cry:{name}", category="cry", kind="cry", subkind="unused" if name.startswith("unused") else "species",
            emerald_constant=lab, source_file=rel(ct), source_line=str(i), asset_file=wav,
            used_by="" if name.startswith("unused") else f"species:{slug_species(name)}")

    # ---- battle animations (status, general, special)
    groups = {"gBattleAnims_StatusConditions": "status", "gBattleAnims_General": "general",
              "gBattleAnims_Special": "special"}
    lines = anim_src.read_text().splitlines()
    label_line = {}
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(\w+):", line)
        if m:
            label_line.setdefault(m.group(1), i)
    cur = None
    for line in lines:
        m = re.match(r"^(\w+)::", line)
        if m:
            cur = groups.get(m.group(1))
            continue
        m = re.match(r"\s*\.4byte (\w+)\s*@ (B_ANIM_\w+)", line)
        if cur and m:
            lab, const = m.groups()
            # sound effects and sprite tags the script uses
            start = label_line.get(lab, 0)
            ses, tags = [], []
            for l2 in lines[start:start + 400]:
                if l2.strip() == "end" or (re.match(r"^\w+:", l2) and not l2.startswith(lab)):
                    break
                ses += [s for s in re.findall(r"\b(SE_[A-Z0-9_]+)\b", l2) if s not in ses]
                tags += [t for t in re.findall(r"loadspritegfx (ANIM_TAG_\w+)", l2) if t not in tags]
            add(asset_id=f"vfx:{lab}", category="vfx", kind="battle_anim", subkind=cur, emerald_constant=const,
                source_file=rel(anim_src), source_line=str(start),
                asset_file="", used_by="|".join(tags + ses))
        elif line.strip() and not line.strip().startswith((".4byte", ".align", "@")):
            cur = None

    # ---- field effects
    fes = GAME / "data/field_effect_scripts.s"
    fe_lines = fes.read_text().splitlines()
    fe_label_line = {}
    for i, line in enumerate(fe_lines, 1):
        m = re.match(r"^(\w+)::", line)
        if m:
            fe_label_line[m.group(1)] = i
    for line in fe_lines:
        m = re.match(r"\s*\.4byte (\w+)\s*@ (FLDEFF_\w+)", line)
        if m:
            lab, const = m.groups()
            add(asset_id=f"vfx:{const}", category="vfx", kind="field_effect", subkind="",
                emerald_constant=const, source_file=rel(fes), source_line=str(fe_label_line.get(lab, 0)))

    # ---- weather
    fw = GAME / "src/field_weather.c"
    for i, line in enumerate(fw.read_text().splitlines(), 1):
        m = re.match(r"\s*\[(WEATHER_\w+)\]\s*=\s*\{(\w+)_InitVars", line)
        if m and m.group(2) != "None":
            add(asset_id=f"vfx:{m.group(1)}", category="vfx", kind="weather", subkind=m.group(2).lower(),
                emerald_constant=m.group(1), source_file=rel(fw), source_line=str(i))

    # ---- battle transitions
    bt = GAME / "src/battle_transition.c"
    for i, line in enumerate(bt.read_text().splitlines(), 1):
        m = re.match(r"\s*\[(B_TRANSITION_\w+)\]\s*=\s*(Task_\w+),", line)
        if m:
            add(asset_id=f"vfx:{m.group(1)}", category="vfx", kind="battle_transition", subkind="",
                emerald_constant=m.group(1), source_file=rel(bt), source_line=str(i))

    rows.sort(key=lambda r: (r["category"], r["kind"], r["asset_id"]))
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    counts = defaultdict(int)
    for r in rows:
        counts[(r["category"], r["kind"])] += 1
    print(f"mapping/asset_inventory.csv: {len(rows)} rows")
    for k in sorted(counts):
        print(f"  {k[0]:6} {k[1]:18} {counts[k]}")


if __name__ == "__main__":
    main()

"""Music tracker for tools/music-generator -> database/music.csv and database/music_by_map.csv.

    python3 tools/build_music.py            # GAME_DIR=/path/to/game to override

Runs at the end of tools/build.py, and on its own (it only needs database/pending_audio.csv, which build.py
writes, and ../game for the tech notes).

database/music.csv has one row per song: every MUS_* track in ../game plus every net-new song (`net:mus-*`).
  - music_category / music_form come from mapping/music.csv (hand-written labels, see mapping/README.md).
  - wiki_title is the song's Star Wars title once it has one (mapping/music.csv sw_title); until then the
    Emerald constant (or the draft constant for net-new songs).
  - rewrite_status is TODO for every song the player hears (HOTSWAP and NET_NEW) and SKIP for ghosts
    (CUT, never played in Emerald) and MUS_DUMMY. Set it to DONE when the new song is in ../game.
  - planets come from the maps that set the song in map.json (database/area_progression.csv), plus any
    planets listed by hand in mapping/music.csv.
  - player / voicegroup / volume / reverb / priority come from sound/songs/midi/midi.cfg and
    sound/song_table.inc; midi_tracks / tempo_bpm / length_s / loops are read from the .mid itself.

database/music_by_map.csv lists every map with the song it plays, its planet and map type, so each planet's
music can be read in one place.

Deterministic: same inputs give a byte-identical file.
"""
from __future__ import annotations

import csv
import os
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(os.environ.get("GAME_DIR", ROOT.parent / "game"))
MAPPING = ROOT / "mapping"
DB = ROOT / "database"

CATEGORIES = {"TOWN", "ROUTE", "TRAVEL", "DUNGEON", "BUILDING", "FACILITY", "MINIGAME", "BATTLE", "VICTORY",
              "ENCOUNTER", "FANFARE", "EVENT", "FRONT_END", "SYSTEM", "UNUSED"}
FORMS = {"LOOP", "AMBIENT", "CUE", "JINGLE", "SILENT", "NONE"}

COLS = ["asset_id", "wiki_title", "music_category", "music_form", "rewrite_status", "audio_status", "swap_kind",
        "priority", "emerald_constant", "sw_constant", "sw_title", "planets", "map_count", "used_in", "sw_subject",
        "placeholder_from", "depends_on", "asset_file", "suggested_path", "player", "voicegroup", "volume",
        "reverb", "song_priority", "midi_tracks", "tempo_bpm", "length_s", "loops", "tech_notes", "notes"]
MAP_COLS = ["map_id", "sw_map_title", "map_title", "planet", "map_type", "music", "wiki_title", "music_category",
            "music_form"]

warnings: list[str] = []


def warn(msg: str) -> None:
    warnings.append(msg)


def read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path: Path, rows: list[dict], cols: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def midi_cfg() -> dict[str, dict]:
    """sound/songs/midi/midi.cfg: `mus_x.mid: -E -R50 -G_route101 -V080 -P5` per song."""
    out = {}
    path = GAME / "sound" / "songs" / "midi" / "midi.cfg"
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        if ":" not in line:
            continue
        name, args = line.split(":", 1)
        o = {}
        for a in args.split():
            if a.startswith("-G"):
                o["voicegroup"] = a[2:].lstrip("_")
            elif a.startswith("-V"):
                o["volume"] = str(int(a[2:]))
            elif a.startswith("-R"):
                o["reverb"] = str(int(a[2:]))
            elif a.startswith("-P"):
                o["song_priority"] = str(int(a[2:]))
        out[name.strip()] = o
    return out


def song_players() -> dict[str, str]:
    path = GAME / "sound" / "song_table.inc"
    if not path.exists():
        return {}
    return {m.group(1): m.group(2).replace("MUSIC_PLAYER_", "")
            for m in re.finditer(r"song\s+(\w+),\s*(MUSIC_PLAYER_\w+)", path.read_text())}


def _varlen(d: bytes, i: int) -> tuple[int, int]:
    v = 0
    while True:
        b = d[i]
        i += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, i


def midi_info(path: Path) -> dict:
    """Track count, first tempo, length in seconds (tempo map applied) and whether the song loops ([ ] markers)."""
    d = path.read_bytes()
    if d[:4] != b"MThd":
        return {}
    _fmt, ntrk, div = struct.unpack(">HHH", d[8:14])
    i, tempos, end, loops, tracks = 14, [], 0, False, 0
    while i < len(d) and d[i:i + 4] == b"MTrk":
        ln = struct.unpack(">I", d[i + 4:i + 8])[0]
        j, stop, t, run, notes = i + 8, i + 8 + ln, 0, 0, False
        while j < stop:
            dt, j = _varlen(d, j)
            t += dt
            st = d[j]
            if st == 0xFF:
                typ = d[j + 1]
                n, j = _varlen(d, j + 2)
                data = d[j:j + n]
                j += n
                if typ == 0x51 and n == 3:
                    tempos.append((t, int.from_bytes(data, "big")))
                elif typ in (0x01, 0x06) and data in (b"[", b"]"):
                    loops = True
            elif st in (0xF0, 0xF7):
                n, j = _varlen(d, j + 1)
                j += n
            else:
                if st & 0x80:
                    run, j = st, j + 1
                hi = run & 0xF0
                if hi == 0x90:
                    notes = True
                j += 1 if hi in (0xC0, 0xD0) else 2
        end = max(end, t)
        tracks += notes
        i = stop
    tempos.sort()
    if not tempos or tempos[0][0] != 0:
        tempos.insert(0, (0, 500000))
    secs, last_t, last_us = 0.0, 0, tempos[0][1]
    for t, us in tempos[1:]:
        if t > end:
            break
        secs += (t - last_t) * last_us / div / 1e6
        last_t, last_us = t, us
    secs += (end - last_t) * last_us / div / 1e6
    return {"midi_tracks": str(tracks), "tempo_bpm": str(round(60e6 / tempos[0][1])), "length_s": f"{secs:.1f}",
            "loops": "yes" if loops else "no"}


def main() -> list[str]:
    audio = [r for r in read(DB / "pending_audio.csv") if r["category"] == "music"]
    labels = {r["asset_id"]: r for r in read(MAPPING / "music.csv")}
    maps = {r["map_id"]: r for r in read(DB / "area_progression.csv")} if (DB / "area_progression.csv").exists() else {}
    cfg, players = midi_cfg(), song_players()
    out, by_map = [], {}
    for a in audio:
        aid = a["asset_id"]
        lab = labels.get(aid)
        if not lab:
            warn(f"mapping/music.csv: no label for {aid}")
            lab = {}
        cat, form = lab.get("music_category", ""), lab.get("music_form", "")
        if cat not in CATEGORIES:
            warn(f"mapping/music.csv: {aid} bad music_category {cat!r}")
        if form not in FORMS:
            warn(f"mapping/music.csv: {aid} bad music_form {form!r}")
        map_ids = [u for u in a["used_by"].split("|") if u.startswith("map:")]
        planets = []
        for m in map_ids:
            p = maps.get(m, {}).get("planet", "")
            if p and p not in planets:
                planets.append(p)
        for p in filter(None, lab.get("planets", "").split("|")):
            if p not in planets:
                planets.append(p)
        skip = a["swap_kind"] in ("CUT", "KEEP") or aid == "audio:MUS_DUMMY"
        sw_title = lab.get("sw_title", "")
        r = {k: a.get(k, "") for k in COLS}
        r.update(wiki_title=sw_title or a["emerald_constant"] or a["sw_constant"], music_category=cat,
                 music_form=form, sw_title=sw_title, rewrite_status="SKIP" if skip else "TODO",
                 planets="|".join(sorted(planets)), map_count=str(len(map_ids)), tech_notes=lab.get("tech_notes", ""))
        if a.get("game_status") == "DONE" and not skip:
            r["rewrite_status"] = "DONE"
        f = a["asset_file"]
        if f:
            name = Path(f).name
            r.update(cfg.get(name, {}))
            r["player"] = players.get(Path(f).stem, "")
            if (GAME / f).exists():
                r.update(midi_info(GAME / f))
            else:
                warn(f"{aid}: ../game/{f} missing")
        out.append(r)
        for m in map_ids:
            by_map.setdefault(m, []).append(r)
    order = {c: i for i, c in enumerate(["FRONT_END", "TOWN", "ROUTE", "TRAVEL", "DUNGEON", "BUILDING", "FACILITY",
                                         "MINIGAME", "EVENT", "ENCOUNTER", "BATTLE", "VICTORY", "FANFARE", "SYSTEM",
                                         "UNUSED"])}
    out.sort(key=lambda r: (order.get(r["music_category"], 99), r["swap_kind"] == "NET_NEW", r["asset_id"]))
    for aid in labels:
        if aid not in {r["asset_id"] for r in out}:
            warn(f"mapping/music.csv: {aid} is not a music row in database/pending_audio.csv")
    write(DB / "music.csv", out, COLS)

    map_music = {e["id"]: e.get("music", "") for e in read(DB / "entities.csv") if e["entity_type"] == "map"} \
        if (DB / "entities.csv").exists() else {}
    mrows = []
    for mid, m in sorted(maps.items()):
        songs = by_map.get(mid, [])
        if not songs and map_music.get(mid) == "MUS_NONE":
            songs = [{"asset_id": "MUS_NONE", "wiki_title": "MUS_NONE", "music_category": "SILENT",
                      "music_form": "SILENT"}]  # map.json plays nothing: a script sets the song, or silence
        if not songs:
            warn(f"music_by_map: {mid} has no music row")
        mrows.append({"map_id": mid, "sw_map_title": m.get("sw_map_title", ""), "map_title": m.get("map_title", ""),
                      "planet": m.get("planet", ""), "map_type": m.get("map_type", ""),
                      "music": "|".join(s["asset_id"] for s in songs),
                      "wiki_title": "|".join(s["wiki_title"] for s in songs),
                      "music_category": "|".join(s["music_category"] for s in songs),
                      "music_form": "|".join(s["music_form"] for s in songs)})
    mrows.sort(key=lambda r: (r["planet"] or "~", r["map_id"]))
    write(DB / "music_by_map.csv", mrows, MAP_COLS)
    todo = sum(r["rewrite_status"] == "TODO" for r in out)
    print(f"music: {len(out)} songs, {todo} TODO, {len(mrows)} maps, {len(warnings)} warnings")
    for w in warnings[:20]:
        print("  !", w)
    return warnings


if __name__ == "__main__":
    main()

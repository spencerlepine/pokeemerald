#!/usr/bin/env python3
"""Apply mapping/audio_done.csv to database/ without a full rebuild (tools/build.py).

Each row of mapping/audio_done.csv is a sound the owner approved that a tool (cry-generator, sfx-generator)
installed into ../game at `game_file`. In pending_audio.csv the row becomes `audio_status` DONE with
`made_by` set. Hot-swaps already play from their old call sites, so their `game_status` is DONE too (here
and in game_port.csv). Net-new SEs have their song id but nothing calls them yet, so they stay NOT_STARTED
until the port wires them in. build.py applies the same file, so a full rebuild gives the same result.
Standard library only.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "database"
GAME = ROOT.parent / "game"


def read(path):
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(path, cols, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    _, done = read(ROOT / "mapping" / "audio_done.csv")
    cols, audio = read(DB / "pending_audio.csv")
    by_id = {a["asset_id"]: a for a in audio}
    pcols, port = read(DB / "game_port.csv")
    port_by = {p["wiki_id"]: p for p in port if p["table"] == "pending_audio.csv"}
    bad = 0
    for d in done:
        a = by_id.get(d["asset_id"])
        if not a:
            print(f"error: {d['asset_id']} is not in pending_audio.csv"); bad += 1; continue
        if not (GAME / d["game_file"]).exists():
            print(f"error: ../game/{d['game_file']} missing"); bad += 1; continue
        gs = "DONE" if a["swap_kind"] == "HOTSWAP" else "NOT_STARTED"
        a.update(audio_status="DONE", made_by=d.get("made_by", ""), game_status=gs,
                 notes="; ".join(x for x in (f"in game: {d['game_file']}", d.get("notes", "")) if x))
        p = port_by.get(d["asset_id"])
        if p:
            p["game_status"] = gs
            if gs != "DONE":
                p["notes"] = "; ".join(x for x in (f"sound installed: {d['game_file']}", d.get("notes", "")) if x)
        print(f"DONE  {d['asset_id']:<24} game_status {gs:<11} {d['game_file']}")
    if bad:
        sys.exit(1)
    write(DB / "pending_audio.csv", cols, audio)
    write(DB / "game_port.csv", pcols, port)


if __name__ == "__main__":
    main()

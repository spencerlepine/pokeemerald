#!/usr/bin/env python3
"""Apply mapping/art_ready.csv to database/ without a full rebuild (tools/build.py).

Each row of mapping/art_ready.csv is art the owner approved: the image is stored in the wiki at
`art_file` (art/<game path>), and the row becomes `art_status` ART_READY in pending_art.csv. It is
not in ../game yet, so `game_status` stays NOT_STARTED until it is copied over. build.py applies the
same file, so a later full rebuild gives the same result. Standard library only.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "database"


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
    _, ready = read(ROOT / "mapping" / "art_ready.csv")
    cols, art = read(DB / "pending_art.csv")
    by_id = {a["asset_id"]: a for a in art}
    bad = 0
    for d in ready:
        a = by_id.get(d["asset_id"])
        if not a:
            print(f"error: {d['asset_id']} is not in pending_art.csv"); bad += 1; continue
        if not (ROOT / d["art_file"]).exists():
            print(f"error: {d['art_file']} missing"); bad += 1; continue
        a.update(art_status="ART_READY", drawn_by=d.get("drawn_by", ""),
                 art_notes="; ".join(x for x in (f"art: {d['art_file']}", d.get("notes", "")) if x))
        print(f"ART_READY  {d['asset_id']}  ->  {d['art_file']}")
    if bad:
        sys.exit(1)
    write(DB / "pending_art.csv", cols, art)
    # the port checklist's art action points at ART_READY (same text build.py writes)
    pcols, port = read(DB / "game_port.csv")
    for p in port:
        p["action"] = p["action"].replace("once art_status is DONE", "once art_status is ART_READY")
        p["depends_on"] = p["depends_on"].replace("art_status DONE in", "art_status ART_READY in")
    write(DB / "game_port.csv", pcols, port)


if __name__ == "__main__":
    main()

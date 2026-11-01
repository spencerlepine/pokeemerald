#!/usr/bin/env python3
"""Tag every object_events row of pending_art.csv with its frame size and a size class.

    python3 tools/frame_sizes.py      # patch database/pending_art.csv in place (no full rebuild)

A walker sheet is a row of frames; the frame size, not the sheet size, says how big the
character is on the map. It comes from ../game/src/data/object_events/object_event_graphics.h,
where every sheet is converted with `-mwidth W -mheight H` (W x H tiles of 8 px per frame).
Sheets converted without them are a single frame (item balls, dolls), so the frame is the image.

Columns added after `height`:
  frame_size   e.g. 16x32 (pixels per frame)
  size_class   SMALL  = one map tile wide (16x16 or 16x32 frames: people, small props)
               LARGE  = wider than one tile (32x32 and up: bikes, big Pokemon, legendaries)
build.py calls apply() too, so a full rebuild keeps the columns. Standard library only.
"""
import csv
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT.parent / "game"
DB = ROOT / "database"
GFX_H = GAME / "src/data/object_events/object_event_graphics.h"
NEW_COLS = ["frame_size", "size_class"]


def _png_size(p: Path):
    with p.open("rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


def frame_sizes(game: Path = GAME) -> dict:
    """game-relative .png path -> (frame width, frame height) in pixels."""
    out = {}
    if not (game / "src/data/object_events/object_event_graphics.h").exists():
        return out
    for line in (game / "src/data/object_events/object_event_graphics.h").read_text().splitlines():
        m = re.search(r'"(graphics/object_events/[^"]+?)\.(?:png|4bpp|8bpp)"', line)
        if not m:
            continue
        path = m.group(1) + ".png"
        mw, mh = re.search(r"-mwidth (\d+)", line), re.search(r"-mheight (\d+)", line)
        if mw and mh:
            out[path] = (int(mw.group(1)) * 8, int(mh.group(1)) * 8)
        elif (game / path).exists():
            out[path] = _png_size(game / path)
    return out


def apply(art: list, game: Path = GAME) -> None:
    sizes = frame_sizes(game)
    for a in art:
        fs = sizes.get(a.get("path", "")) if a.get("kind") == "object_events" else None
        if fs:
            a["frame_size"] = f"{fs[0]}x{fs[1]}"
            a["size_class"] = "SMALL" if fs[0] <= 16 and fs[1] <= 32 else "LARGE"
        else:
            a.setdefault("frame_size", "")
            a.setdefault("size_class", "")


def order_cols(cols: list) -> list:
    cols = [c for c in cols if c not in NEW_COLS]
    i = cols.index("height") + 1 if "height" in cols else len(cols)
    return cols[:i] + NEW_COLS + cols[i:]


def main():
    with (DB / "pending_art.csv").open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        cols, art = r.fieldnames, list(r)
    apply(art)
    cols = order_cols(cols)
    with (DB / "pending_art.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(art)
    obj = [a for a in art if a["kind"] == "object_events"]
    missing = [a["path"] for a in obj if not a["frame_size"]]
    from collections import Counter
    print("object_events rows:", len(obj), dict(Counter(a["size_class"] for a in obj)))
    print("frame sizes:", dict(Counter(a["frame_size"] for a in obj)))
    for p in missing:
        print("no frame size:", p)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

"""Parts catalogue: every vanilla 16x32 people sheet, its palette and where its head ends, plus a
labelled contact sheet so a head or body can be picked for `base_sheet:` / `parts:` (STYLE.md 6).

    python -m walker_sprite parts        -> corpus/parts.json, corpus/parts.png
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

from .lint import SKIN
from .sheet import read_frames
from .spec import KITS, _top

CORPUS = Path(__file__).resolve().parents[1] / "corpus"


def palette_tags(game: Path) -> dict[str, str]:
    """sheet path -> OBJ_EVENT_PAL_TAG_* via gObjectEventPic_X -> gObjectEventGraphicsInfo_X."""
    pics = {}
    for m in re.finditer(r"gObjectEventPic_(\w+)\[\] = INCGFX_U32\(\"([^\"]+)\"", (game / "src/data/object_events/object_event_graphics.h").read_text()):
        pics.setdefault(m.group(1), m.group(2))
    tags = {}
    info = (game / "src/data/object_events/object_event_graphics_info.h").read_text()
    for m in re.finditer(r"gObjectEventGraphicsInfo_(\w+) = \{(.*?)\};", info, re.S):
        t = re.search(r"\.paletteTag = (\w+)", m.group(2))
        img = re.search(r"\.images = (\w+)", m.group(2))
        if t and m.group(1) in pics:
            tags[pics[m.group(1)]] = t.group(1)
    return tags


def chin_row(g) -> int:
    """Last row of the face (skin light/base/shade) in a facing-down frame, or -1."""
    rows = [y for y, row in enumerate(g) if any(v in SKIN[:3] for v in row)]
    if not rows:
        return -1
    # the face is the first run of skin rows; arms/legs come later after a gap or the collar
    end = rows[0]
    for y in rows[1:]:
        if y != end + 1:
            break
        end = y
    return end


def build(game: Path) -> dict:
    tags = palette_tags(game)
    order = KITS["person16x32"]["order"]
    out = {}
    for f in sorted((game / "graphics/object_events/pics/people").rglob("*.png")):
        try:
            frames, _ = read_frames(f)
        except ValueError:
            continue
        if len(frames) != len(order):
            continue
        rel = str(f.relative_to(game))
        down = frames[0]
        out[rel] = {"palette": tags.get(rel, "?").replace("OBJ_EVENT_PAL_TAG_", "").lower(),
                    "top": _top(down), "chin": chin_row(down), "feet": max(y for y, r in enumerate(down) if any(r))}
    CORPUS.mkdir(exist_ok=True)
    (CORPUS / "parts.json").write_text(json.dumps(out, indent=1))
    # contact sheet: 6 per row, down/left/up at 3x with the name, palette and head rows
    z, per = 3, 6
    cell_w, cell_h = 16 * 3 * z + 10 + 150, 32 * z + 8
    names = list(out)
    rows_n = (len(names) + per - 1) // per
    im = Image.new("RGB", (per * cell_w, rows_n * cell_h), (24, 24, 30))
    d = ImageDraw.Draw(im)
    for i, rel in enumerate(names):
        frames, cols = read_frames(game / rel)
        x0, y0 = (i % per) * cell_w, (i // per) * cell_h
        for j, k in enumerate((0, 2, 1)):
            fr = Image.new("RGB", (16, 32), (115, 197, 164))
            for y in range(32):
                for x in range(16):
                    v = frames[k][y][x]
                    if v:
                        fr.putpixel((x, y), cols[v])
            im.paste(fr.resize((16 * z, 32 * z), Image.NEAREST), (x0 + j * 16 * z, y0 + 4))
        short = rel.replace("graphics/object_events/pics/people/", "")
        info = out[rel]
        d.text((x0 + 16 * 3 * z + 6, y0 + 6), short, fill=(230, 230, 230))
        d.text((x0 + 16 * 3 * z + 6, y0 + 22), info["palette"], fill=(180, 180, 190))
        d.text((x0 + 16 * 3 * z + 6, y0 + 38), f"top {info['top']} chin {info['chin']}", fill=(180, 180, 190))
    im.save(CORPUS / "parts.png")
    return out

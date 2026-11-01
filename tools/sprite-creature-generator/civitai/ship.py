#!/usr/bin/env python3
"""Ship approved creature battle sprites from wiki/art into the game (free, no Buzz).

    python ship.py                 # every species with art in wiki/art/graphics/pokemon (unown letters, castform forms too)
    python ship.py skitty aggron   # just these

Per species: copies front.png, anim_front.png, back.png, normal.pal, shiny.pal into game/graphics/pokemon/<sp>/
(unown: one normal.pal/shiny.pal for all letters), sets the species' front/back MonCoords from the sprite
(size = figure box rounded up to 8, y_offset = empty rows under the figure, so the feet sit on the battle
floor; castform forms go to gCastformFrontSpriteCoords), and marks the rows DONE in wiki/database/pending_art.csv
and game_port.csv. Same steps as the MASSIFF (poochyena) install (commit 73ed34c5).
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ART = REPO / "wiki" / "art" / "graphics" / "pokemon"
GAME = REPO / "game"
FRONT_C = GAME / "src" / "data" / "pokemon_graphics" / "front_pic_coordinates.h"
BACK_C = GAME / "src" / "data" / "pokemon_graphics" / "back_pic_coordinates.h"
CASTFORM_C = GAME / "src" / "battle_anim_mons.c"
PENDING = REPO / "wiki" / "database" / "pending_art.csv"
PORT = REPO / "wiki" / "database" / "game_port.csv"
FILES = ("front.png", "anim_front.png", "back.png")
CAST = {"normal": "CASTFORM_NORMAL", "sunny": "CASTFORM_FIRE", "rainy": "CASTFORM_WATER", "snowy": "CASTFORM_ICE"}
NOTE = ("Shipped 2026-11-01 by tools/sprite-creature-generator/civitai (ship.py): battle sprite, owner-approved; "
        "normal.pal + shiny.pal copied too, front/back y_offset set from the sprite.")


def coords(png: Path) -> tuple[int, int, int]:
    im = Image.open(png)
    a = np.array(im)[:64]  # anim_front is 64x128; frame 1 only
    m = (a != 0) if im.mode == "P" else np.array(im.convert("RGBA"))[:64, :, 3] > 0
    ys, xs = np.nonzero(m)
    w, h = int(np.ptp(xs)) + 1, int(np.ptp(ys)) + 1
    up8 = lambda v: min(64, (v + 7) // 8 * 8)
    return up8(w), up8(h), 63 - int(ys.max())


def set_coord(text: str, key: str, c: tuple[int, int, int], name: str) -> str:
    pat = re.compile(rf"^(\s*\[{key}\]\s*=\s*){{[^}}]*}},.*$", re.M)
    if not pat.search(text):
        raise SystemExit(f"{key} not found")
    return pat.sub(lambda m: f"{m.group(1)}{{ .size = MON_COORDS_SIZE({c[0]}, {c[1]}), .y_offset = {c[2]:2} }},  // {name} (sprite-creature-generator)", text, count=1)


def units(only: list[str]) -> list[tuple[str, str, str]]:
    """(art key, SPECIES_ constant, display name)"""
    out = []
    for d in sorted(ART.iterdir()):
        if not d.is_dir() or (only and d.name not in only):
            continue
        if d.name == "unown":
            for l in sorted(x.name for x in d.iterdir() if x.is_dir()):
                k = {"a": "", "question_mark": "_QMARK", "exclamation_mark": "_EMARK"}.get(l, "_" + l.upper())
                out.append((f"unown/{l}", f"SPECIES_UNOWN{k}", f"AUREBESH {l}"))
        elif d.name == "castform":
            for f in CAST:
                out.append((f"castform/{f}", CAST[f], f"CLIMADROID {f}"))
        elif (d / "front.png").exists():
            out.append((d.name, f"SPECIES_{d.name.upper()}", d.name))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("species", nargs="*")
    ap.add_argument("--skip", nargs="*", default=["poochyena"], help="already shipped by hand (default: poochyena)")
    a = ap.parse_args()
    sys.path.insert(0, str(HERE))
    import civitai_creature as cc
    front, back, castc = FRONT_C.read_text(), BACK_C.read_text(), CASTFORM_C.read_text()
    shipped = set()
    for key, const, name in units(a.species):
        sp = key.split("/")[0]
        if sp in a.skip:
            continue
        src, dst = ART / key, GAME / "graphics" / "pokemon" / key
        dst.mkdir(parents=True, exist_ok=True)
        for n in FILES:
            shutil.copyfile(src / n, dst / n)
        pal_src = src.parent if sp == "unown" else src
        pal_dst = dst.parent if sp == "unown" else dst
        for n in ("normal.pal", "shiny.pal"):
            shutil.copyfile(pal_src / n, pal_dst / n)
        try:
            label = cc.brief(sp)["sw_name"] if sp not in ("unown", "castform") else name
        except SystemExit:
            label = name
        fc, bc = coords(src / "front.png"), coords(src / "back.png")
        if sp == "castform":
            castc = set_coord(castc, const, fc, label)
            if key.endswith("normal"):
                front = set_coord(front, "SPECIES_CASTFORM", fc, label)
                back = set_coord(back, "SPECIES_CASTFORM", bc, label)
        else:
            front = set_coord(front, const, fc, label)
            back = set_coord(back, const, bc, label)
        shipped.add(key)
    FRONT_C.write_text(front); BACK_C.write_text(back); CASTFORM_C.write_text(castc)
    paths = {f"graphics/pokemon/{k}/{n}" for k in shipped for n in FILES}
    for f, col_note, col_status in ((PENDING, None, -1), (PORT, 5, 10)):
        rows = list(csv.reader(f.open(newline="")))
        n = 0
        for r in rows[1:]:
            p = r[0].split("|", 1)[-1]
            if p in paths:
                r[col_status] = "DONE"
                if col_note is not None:
                    r[col_note] = NOTE
                n += 1
        buf = io.StringIO(); csv.writer(buf, lineterminator="\n").writerows(rows); f.write_text(buf.getvalue())
        print(f"{f.name}: {n} rows DONE")
    print(f"shipped {len(shipped)} sprites sets")


if __name__ == "__main__":
    main()

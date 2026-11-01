#!/usr/bin/env python3
"""Review sheet (free): per species one row of reference start | installed front | installed back,
3x, on a battle-green background, labelled with the Star Wars name.

    python review.py abra absol bulbasaur ... --out /tmp/review.png   # up to ~8 species per sheet reads well
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ART = REPO / "wiki" / "art" / "graphics" / "pokemon"
sys.path.insert(0, str(HERE))
import civitai_creature as cc  # noqa: E402

S = 192
BG = (156, 204, 140)


def sprite(p: Path) -> Image.Image:
    im = Image.open(p)
    a = np.array(im.convert("RGBA"))
    if im.mode == "P":
        a[np.array(im) == 0, 3] = 0
    t = Image.new("RGBA", (64, 64), BG + (255,))
    t.alpha_composite(Image.fromarray(a))
    return t.convert("RGB").resize((S, S), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("species", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    rows = []
    for sp in a.species:
        r = Image.new("RGB", (S * 3 + 16, S + 22), "white")
        d = ImageDraw.Draw(r)
        b = cc.brief(sp)
        pick = HERE / "refs" / "picks" / f"{sp}.json"
        note = "text only" if pick.exists() and "init" not in json.loads(pick.read_text()) else "reference"
        d.text((4, 3), f"{b.get('sw_name') or sp}  ({sp})  ref | front | back   [{note}]", fill="black", font=font)
        prep = HERE / "refs" / f"{sp}_prep.png"
        if prep.exists() and note == "reference":
            r.paste(Image.open(prep).convert("RGB").resize((S, S), Image.NEAREST), (0, 22))
        for i, n in enumerate(("front.png", "back.png"), 1):
            p = ART / sp / n
            if p.exists():
                r.paste(sprite(p), (i * (S + 8), 22))
            else:
                d.text((i * (S + 8) + 40, 100), "not made yet", fill="red", font=font)
        rows.append(r)
    sheet = Image.new("RGB", (rows[0].width, sum(x.height for x in rows)), "white")
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.height
    sheet.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()

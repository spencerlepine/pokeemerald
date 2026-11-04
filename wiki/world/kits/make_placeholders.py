"""Placeholder tiles for the world kits (../../mapping/world_kits.csv). Not the drawing tool.

Every row becomes a PNG of its drawn size in 16x16 cells, each cell the shared placeholder sprite
(../objects/16x16-placeholder.png). Every category gets a labelled sheet at real size (the first row of each
item: the other planets' copies are the same size). Re-run after a size changes:

    python3 wiki/world/kits/make_placeholders.py
"""
import csv
import os
import shutil

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.normpath(os.path.join(HERE, "..", ".."))
TILE = Image.open(os.path.join(WIKI, "world", "objects", "16x16-placeholder.png")).convert("RGBA")
C, GAP, LABEL, SHEET_W = 16, 8, 10, 480


def png(drawn):
    w, h = (int(v) for v in drawn.split("x"))
    im = Image.new("RGBA", (w * C, h * C), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            im.paste(TILE, (x * C, y * C))
    return im


def main():
    rows = list(csv.DictReader(open(os.path.join(WIKI, "mapping", "world_kits.csv"))))
    for d in ("placeholders", "sheets"):
        shutil.rmtree(os.path.join(HERE, d), ignore_errors=True)
    cats, cache = {}, {}
    for r in rows:
        im = cache.setdefault(r["drawn"], png(r["drawn"]))
        out = os.path.join(WIKI, r["placeholder"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im.save(out)
        items = cats.setdefault(r["category"], {})
        items.setdefault(r["item"], (r, im, set()))[2].add(r["planet"])
    os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    for cat, items in sorted(cats.items()):
        place, x, y, shelf = [], GAP, GAP + LABEL + 6, 0
        for item, (r, im, planets) in items.items():
            label = f"{item} x{len(planets)}"
            lw = max(im.width, int(probe.textlength(label)) + 2)
            if x + lw > SHEET_W and x > GAP:
                x, y, shelf = GAP, y + shelf + GAP + LABEL, 0
            place.append((label, im, x, y))
            x += lw + GAP
            shelf = max(shelf, im.height)
        sheet = Image.new("RGBA", (SHEET_W, y + shelf + GAP), (40, 40, 48, 255))
        dr = ImageDraw.Draw(sheet)
        dr.text((GAP, 2), f"world kits: {cat} ({len(items)} items; xN = planets that need one)", fill=(255, 255, 255, 255))
        for label, im, px, py in place:
            sheet.alpha_composite(im, (px, py))
            dr.text((px, py - LABEL), label, fill=(220, 220, 140, 255))
        sheet.save(os.path.join(HERE, "sheets", f"{cat}.png"))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(HERE, "sheets", f"{cat}_review.png"))
    print(len(rows), "rows,", len(cats), "sheets")


if __name__ == "__main__":
    main()

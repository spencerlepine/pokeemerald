"""Placeholder tiles for the interior objects (`interior` rows of ../../../mapping/world_art.csv with a
`placeholder`). Not the drawing tool.

Every object becomes a PNG of its drawn size in 16x16 cells, each cell the shared placeholder sprite
(../../objects/16x16-placeholder.png). Every planet gets a labelled sheet of its objects at real size, and a
3x review copy with the hit box tinted (red blocks, blue drawn over the player, green walkable).
Re-run after a size changes:

    python3 wiki/world/interiors/placeholders/make_placeholders.py
"""
import csv
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
TILE = Image.open(os.path.join(WIKI, "world", "objects", "16x16-placeholder.png")).convert("RGBA")
C, GAP, LABEL, SHEET_W = 16, 8, 10, 480
TINT = {"#": (200, 40, 40, 90), "o": (40, 80, 220, 110), ".": (40, 200, 60, 70)}
FONT = ImageFont.load_default(size=11)


def size(s):
    return tuple(int(v) for v in s.split("x"))


def cells(r):
    """Hit box per cell: '#' blocks (the bottom footprint rows), 'o' drawn over the player, '.' walkable."""
    dw, dh = size(r["drawn"] or r["footprint"])
    fw, fh = size(r["footprint"])
    return [["#" if fw and y >= dh - fh and x < fw else ("." if not fw else "o") for x in range(dw)] for y in range(dh)]


def main():
    rows = [r for r in csv.DictReader(open(os.path.join(WIKI, "mapping", "world_art.csv")))
            if r["category"] == "interior" and r.get("placeholder")]
    for d in os.listdir(HERE):
        if os.path.isdir(os.path.join(HERE, d)):
            shutil.rmtree(os.path.join(HERE, d))
    planets = {}
    for r in rows:
        dw, dh = size(r["drawn"] or r["footprint"])
        im = Image.new("RGBA", (dw * C, dh * C), (0, 0, 0, 0))
        for y in range(dh):
            for x in range(dw):
                im.paste(TILE, (x * C, y * C))
        out = os.path.join(WIKI, r["placeholder"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im.save(out)
        planets.setdefault(os.path.basename(os.path.dirname(out)), []).append((r, im))
    os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    for planet, items in sorted(planets.items()):
        place, x, y, shelf = [], GAP, GAP + LABEL + 6, 0
        for r, im in items:
            name = r["concept_id"].split(":")[-1]
            lw = max(im.width, int(probe.textlength(name)) + 2)
            if x + lw > SHEET_W and x > GAP:
                x, y, shelf = GAP, y + shelf + GAP + LABEL, 0
            place.append((r, im, name, x, y))
            x += lw + GAP
            shelf = max(shelf, im.height)
        sheet = Image.new("RGBA", (SHEET_W, y + shelf + GAP), (40, 40, 48, 255))
        dr = ImageDraw.Draw(sheet)
        dr.text((GAP, 2), f"interior objects: {planet} ({len(items)})", fill=(255, 255, 255, 255))
        for r, im, name, px, py in place:
            sheet.alpha_composite(im, (px, py))
            dr.text((px, py - LABEL), name, fill=(220, 220, 140, 255))
        out = os.path.join(HERE, "sheets", f"{planet}.png")
        sheet.save(out)
        big = sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST)
        tint = Image.new("RGBA", big.size, (0, 0, 0, 0))
        dt = ImageDraw.Draw(tint)
        for r, im, name, px, py in place:
            for cy, line in enumerate(cells(r)):
                for cx, code in enumerate(line):
                    bx, by = (px + cx * C) * 3, (py + cy * C) * 3
                    dt.rectangle([bx, by, bx + C * 3 - 1, by + C * 3 - 1], fill=TINT[code])
        big.alpha_composite(tint)
        ImageDraw.Draw(big).text((big.width - 330, 8), "red blocks  blue drawn over the player  green walkable",
                                 fill=(220, 220, 220, 255), font=FONT)
        big.save(out.replace(".png", "_review.png"))
    print(len(rows), "objects,", len(planets), "sheets")


if __name__ == "__main__":
    main()

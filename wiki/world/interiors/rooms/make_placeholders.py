"""Placeholder tiles for the room kits in ../../../mapping/rooms.csv (not the room tool).

Every kit part becomes a PNG of its size in 16x16 cells, each cell the shared placeholder sprite
(../../objects/16x16-placeholder.png). Every style gets a labelled sheet of all its parts at real size,
and a 3x review copy with the hit-box code drawn in each cell. Re-run after a size changes:

    python3 wiki/world/interiors/rooms/make_placeholders.py
"""
import csv
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
TILE = Image.open(os.path.join(WIKI, "world", "objects", "16x16-placeholder.png")).convert("RGBA")
C, GAP, LABEL, SHEET_W = 16, 8, 10, 400
# review copy only: what each hit-box code does (rooms.csv `hit_box`)
TINT = {"#": (200, 40, 40, 90), "o": (40, 80, 220, 110), "^": (40, 200, 220, 90), ".": (40, 200, 60, 70), "s": (230, 200, 40, 90),
        "d": (255, 255, 255, 110), "c": (230, 120, 30, 100), "v": (160, 230, 60, 100), "_": (0, 0, 0, 170), "~": (40, 120, 255, 120)}
LEGEND = "# block  . walk  o block+over  ^ walk under  c counter  s stairs  d warp  v ledge  _ pit  ~ liquid"
FONT, SMALL = ImageFont.load_default(size=16), ImageFont.load_default(size=11)


def part_png(w, h):
    im = Image.new("RGBA", (w * C, h * C), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            im.paste(TILE, (x * C, y * C))
    return im


def main():
    rows = list(csv.DictReader(open(os.path.join(WIKI, "mapping", "rooms.csv"))))
    for d in ("placeholders", "sheets"):
        shutil.rmtree(os.path.join(HERE, d), ignore_errors=True)
    styles = {}
    for r in rows:
        if r["kind"] != "part":
            continue
        w, h = (int(v) for v in r["size"].split("x"))
        path = os.path.join(WIKI, r["placeholder"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im = part_png(w, h)
        im.save(path)
        styles.setdefault(r["style"], []).append((r, im))
    for r in rows:
        if r["kind"] != "style":
            continue
        parts = styles.get(r["style"], [])
        # shelf layout: parts left to right with a label above each, wrapping at SHEET_W
        place, x, y, shelf = [], GAP, GAP + LABEL + 4, 0
        for p, im in parts:
            lw = max(im.width, int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(p["part"])) + 2)
            if x + lw > SHEET_W and x > GAP:
                x, y, shelf = GAP, y + shelf + GAP + LABEL, 0
            place.append((p, im, x, y))
            x += lw + GAP
            shelf = max(shelf, im.height)
        H = y + shelf + GAP
        sheet = Image.new("RGBA", (SHEET_W, H), (40, 40, 48, 255))
        dr = ImageDraw.Draw(sheet)
        dr.text((GAP, 2), f"{r['room_id']}  {r['name']}", fill=(255, 255, 255, 255))
        for p, im, px, py in place:
            sheet.alpha_composite(im, (px, py))
            dr.text((px, py - LABEL), p["part"], fill=(220, 220, 140, 255))
        out = os.path.join(WIKI, r["placeholder"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sheet.save(out)
        big = sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST)
        tint = Image.new("RGBA", big.size, (0, 0, 0, 0))
        db = ImageDraw.Draw(tint)
        for p, im, px, py in place:   # hit box: a tint and the code in every cell
            for cy, line in enumerate(p["hit_box"].split("/")):
                for cx, code in enumerate(line):
                    bx, by = (px + cx * C) * 3, (py + cy * C) * 3
                    db.rectangle([bx, by, bx + C * 3 - 1, by + C * 3 - 1], fill=TINT.get(code, (0, 0, 0, 0)))
                    db.text((bx + 3, by + 1), code, fill=(255, 255, 255, 255), font=FONT)
        big.alpha_composite(tint)
        ImageDraw.Draw(big).text((sheet.width * 3 - 560, 6), LEGEND, fill=(200, 200, 200, 255), font=SMALL)
        big.save(out.replace(".png", "_review.png"))
    print(sum(len(v) for v in styles.values()), "parts,", len(styles), "sheets")


if __name__ == "__main__":
    main()

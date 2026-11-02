"""Stitch the overworld areas of a planet (or the whole world) into one map, using each area's `pos`
(its top-left cell in world coordinates). Areas without `pos` (caves, interiors) are listed beside it."""
from PIL import Image, ImageDraw

from .render import F, F_BIG, F_SMALL
from .terrain import TERRAIN, PINK

PX = 4   # px per cell

TINT = {  # one flat placeholder hue per planet, only for the whole-world overview
    "TATOOINE": (230, 200, 140), "KASHYYYK": (140, 190, 120), "SULLUST": (170, 150, 150), "MUSTAFAR": (220, 120, 90),
    "ENDOR": (110, 170, 110), "BESPIN": (230, 190, 170), "JEDHA": (210, 190, 150), "YAVIN 4": (120, 180, 140),
    "HOTH": (220, 230, 240), "DAGOBAH": (120, 150, 120), "KAMINO": (150, 170, 200), "ILUM": (200, 220, 240),
    "FELUCIA": (220, 150, 200), "GRAND ARENA": (200, 200, 120), "TYTHON": (180, 200, 160), "ATOLLON": (190, 170, 140),
    "MORTIS": (170, 160, 200), "ASTEROID FIELD": (160, 160, 170), "SHARED": (200, 200, 200),
}


def _cell_colour(ch):
    name, _, fill, _ = TERRAIN.get(ch, TERRAIN["x"])
    if name == "nature":
        return (112, 112, 112)
    if name.startswith("ledge"):
        return (150, 150, 150)
    return fill


def _tinted(c, t, k=0.45):
    return tuple(int(a * (1 - k) + b * k * a / 200) for a, b in zip(c, t))


def stitch(areas, title, tint=False):
    placed = [a for a in areas if a.pos is not None and a.w]
    if not placed:
        return None
    x0 = min(a.pos[0] for a in placed)
    y0 = min(a.pos[1] for a in placed)
    x1 = max(a.pos[0] + a.w for a in placed)
    y1 = max(a.pos[1] + a.h for a in placed)
    pad, head = 16, 40
    W, H = (x1 - x0) * PX + 2 * pad, (y1 - y0) * PX + 2 * pad + head
    img = Image.new("RGB", (max(W, 600), H), (28, 28, 32))
    d = ImageDraw.Draw(img)
    d.text((pad, 8), title, font=F_BIG, fill=(255, 255, 255))
    ox, oy = pad - x0 * PX, pad + head - y0 * PX
    for a in placed:
        ax, ay = ox + a.pos[0] * PX, oy + a.pos[1] * PX
        t = TINT.get(a.planet, (200, 200, 200))
        for y, row in enumerate(a.grid):
            for x, ch in enumerate(row):
                c = _cell_colour(ch)
                if tint:
                    c = _tinted(c, t)
                d.rectangle([ax + x * PX, ay + y * PX, ax + x * PX + PX - 1, ay + y * PX + PX - 1], fill=c)
        for b in a.buildings:
            (bx, by), (bw, bh) = b["at"], b["size"]
            d.rectangle([ax + bx * PX, ay + by * PX, ax + (bx + bw) * PX - 1, ay + (by + bh) * PX - 1],
                        fill=(80, 80, 80), outline=(20, 20, 20))
        for p in a.props:
            (bx, by), (bw, bh) = p["at"], p.get("size", [1, 1])
            d.rectangle([ax + bx * PX, ay + by * PX, ax + (bx + bw) * PX - 1, ay + (by + bh) * PX - 1], fill=(170, 170, 170))
        for p in a.people + a.signs + a.warps:
            px, py = p["at"]
            d.rectangle([ax + px * PX, ay + py * PX, ax + px * PX + PX - 1, ay + py * PX + PX - 1], fill=PINK)
        d.rectangle([ax, ay, ax + a.w * PX - 1, ay + a.h * PX - 1], outline=(0, 0, 0))
    for a in placed:   # labels on top
        ax, ay = ox + a.pos[0] * PX, oy + a.pos[1] * PX
        label = a.name
        tw = d.textlength(label, font=F)
        cx, cy = ax + a.w * PX / 2 - tw / 2, ay + a.h * PX / 2 - 7
        d.rectangle([cx - 3, cy - 1, cx + tw + 3, cy + 14], fill=(0, 0, 0))
        d.text((cx, cy), label, font=F, fill=(255, 255, 255) if a.status != "TODO" else (255, 200, 120))
    return img


def side_list(areas, height):
    rest = [a for a in areas if a.pos is None]
    img = Image.new("RGB", (340, max(height, 200)), (28, 28, 32))
    d = ImageDraw.Draw(img)
    d.text((10, 8), "Reached by doors (caves, interiors)", font=F, fill=(230, 230, 230))
    y = 28
    for a in sorted(rest, key=lambda a: (a.kind, a.id)):
        if y > img.height - 14:
            d.text((10, y), f"... and {len(rest)} in all", font=F_SMALL, fill=(200, 200, 200))
            break
        col = (255, 200, 120) if a.status == "TODO" else (200, 230, 200)
        d.text((10, y), f"{a.kind[:4]}  {a.id}  {a.w}x{a.h}", font=F_SMALL, fill=col)
        y += 12
    return img

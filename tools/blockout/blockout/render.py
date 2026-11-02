"""Draw an area blockout as a review sheet: grey placeholder tiles, grey blocks for buildings and props,
pink placeholders for every sprite and event, a numbered legend, and the vanilla map it replaces."""
import textwrap

from PIL import Image, ImageDraw, ImageFont

from .terrain import TERRAIN, PINK, PINK_DARK, OUTLINE

C = 16          # px per cell, native
S = 2           # review scale
M = 34          # margin round the map (scaled px) for exit labels


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


F_SMALL, F, F_BIG = _font(10), _font(12), _font(16)


def _h(x, y):
    v = (x * 73856093) ^ (y * 19349663)
    v ^= v >> 13
    return (v * 0x5bd1e995) & 0xFFFFFFFF


def _tile(d, ch, x, y, area):
    name, _, fill, _ = TERRAIN.get(ch, TERRAIN["x"])
    x0, y0 = x * C, y * C
    box = [x0, y0, x0 + C - 1, y0 + C - 1]
    ground = TERRAIN["."][2]
    d.rectangle(box, fill=fill if name not in ("nature",) else ground)
    dark = tuple(max(v - 34, 0) for v in fill)
    if name == "ground":
        for k in range(2):
            h = _h(x * 2 + k, y)
            d.point((x0 + h % 16, y0 + (h >> 8) % 16), fill=dark)
    elif name == "wild":
        for tx, ty in ((2, 3), (9, 2), (5, 9), (12, 10)):
            d.line([(x0 + tx, y0 + ty + 3), (x0 + tx + 1, y0 + ty), (x0 + tx + 2, y0 + ty + 3)], fill=(110, 110, 110))
    elif name == "water":
        light = (172, 182, 196)
        for ty in (4, 11):
            d.line([(x0 + 2, y0 + ty), (x0 + 6, y0 + ty - 1), (x0 + 10, y0 + ty)], fill=light)
    elif name == "nature":
        d.ellipse([x0 + 1, y0 + 1, x0 + 14, y0 + 14], fill=(112, 112, 112), outline=(60, 60, 60))
        d.ellipse([x0 + 4, y0 + 3, x0 + 8, y0 + 6], fill=(140, 140, 140))
    elif name == "cliff":
        if area.cell(x, y - 1) != "#":
            d.rectangle([x0, y0, x0 + C - 1, y0 + 2], fill=(136, 136, 136))
        if area.cell(x, y + 1) != "#":
            d.rectangle([x0, y0 + C - 3, x0 + C - 1, y0 + C - 1], fill=(70, 70, 70))
    elif name.startswith("ledge"):
        side = name[-1]
        band = {"s": [x0, y0 + 11, x0 + 15, y0 + 15], "n": [x0, y0, x0 + 15, y0 + 4],
                "w": [x0, y0, x0 + 4, y0 + 15], "e": [x0 + 11, y0, x0 + 15, y0 + 15]}[side]
        d.rectangle(band, fill=(120, 120, 120))
        cx, cy = x0 + 7, y0 + 6
        tri = {"s": [(cx - 3, cy - 1), (cx + 3, cy - 1), (cx, cy + 3)], "n": [(cx - 3, cy + 4), (cx + 3, cy + 4), (cx, cy + 1)],
               "w": [(x0 + 9, cy - 3), (x0 + 9, cy + 3), (x0 + 6, cy)], "e": [(x0 + 6, cy - 3), (x0 + 6, cy + 3), (x0 + 9, cy)]}[side]
        d.polygon(tri, fill=(120, 120, 120))
    elif name == "bridge":
        for tx in range(1, 16, 4):
            d.line([(x0 + tx, y0), (x0 + tx, y0 + 15)], fill=dark)
    elif name == "ladder":
        for ty in range(2, 16, 4):
            d.line([(x0 + 3, y0 + ty), (x0 + 12, y0 + ty)], fill=(110, 96, 80))
        d.line([(x0 + 3, y0), (x0 + 3, y0 + 15)], fill=(110, 96, 80))
        d.line([(x0 + 12, y0), (x0 + 12, y0 + 15)], fill=(110, 96, 80))
    elif name == "blocked":
        for k in range(-16, 16, 5):
            d.line([(x0 + max(k, 0), y0 + max(-k, 0)), (x0 + min(15, 15 + k), y0 + min(15, 15 - k))], fill=(126, 126, 126))
    elif name == "wall":
        d.rectangle([x0, y0 + C - 3, x0 + C - 1, y0 + C - 1], fill=(60, 60, 60))


def _label(d, text, box, font=F, fill=(255, 255, 255), shadow=(0, 0, 0)):
    x0, y0, x1, y1 = box
    width = max(int((x1 - x0) / 6.2), 4)
    lines = textwrap.wrap(text, width)[:4]
    hh = sum(d.textbbox((0, 0), ln, font=font)[3] + 1 for ln in lines)
    y = (y0 + y1) / 2 - hh / 2
    for ln in lines:
        tw = d.textlength(ln, font=font)
        x = (x0 + x1) / 2 - tw / 2
        if shadow:
            d.text((x + 1, y + 1), ln, font=font, fill=shadow)
        d.text((x, y), ln, font=font, fill=fill)
        y += d.textbbox((0, 0), ln, font=font)[3] + 1


def _badge(d, n, x, y, fill=(30, 30, 30), fg=(255, 255, 255)):
    t = str(n)
    w = d.textlength(t, font=F_SMALL) + 6
    d.rounded_rectangle([x, y, x + w, y + 13], 3, fill=fill)
    d.text((x + 3, y + 1), t, font=F_SMALL, fill=fg)


def draw_map(area):
    """The blockout itself at review scale, with a margin for exit labels."""
    base = Image.new("RGB", (area.w * C, area.h * C), (0, 0, 0))
    d = ImageDraw.Draw(base)
    for y in range(area.h):
        for x in range(area.w):
            _tile(d, area.grid[y][x], x, y, area)
    big = base.resize((base.width * S, base.height * S), Image.NEAREST)
    img = Image.new("RGB", (big.width + 2 * M, big.height + 2 * M), (40, 40, 44))
    img.paste(big, (M, M))
    d = ImageDraw.Draw(img)
    u = C * S

    def cell_box(x, y, w=1, h=1, inset=0):
        return [M + x * u + inset, M + y * u + inset, M + (x + w) * u - 1 - inset, M + (y + h) * u - 1 - inset]

    # light grid so cells can be counted
    for x in range(area.w + 1):
        if x % 5 == 0:
            d.line([(M + x * u, M), (M + x * u, M + area.h * u)], fill=(0, 0, 0))
    for y in range(area.h + 1):
        if y % 5 == 0:
            d.line([(M, M + y * u), (M + area.w * u, M + y * u)], fill=(0, 0, 0))
    # cell coordinates every 5 cells
    for x in range(0, area.w, 5):
        d.text((M + x * u + 2, M - 12), str(x), font=F_SMALL, fill=(170, 170, 170))
    for y in range(0, area.h, 5):
        d.text((4, M + y * u + 2), str(y), font=F_SMALL, fill=(170, 170, 170))

    n = 0
    for b in area.buildings:
        n += 1
        (x, y), (w, h) = b["at"], b["size"]
        box = cell_box(x, y, w, h)
        d.rectangle(box, fill=(150, 150, 150), outline=OUTLINE, width=2)
        roof_h = max(h - 1, 1) if h > 1 else 1
        d.rectangle(cell_box(x, y, w, roof_h, 2), fill=(108, 108, 108))
        if "door" in b:
            dx = x + int(b["door"])
            db = cell_box(dx, y + h - 1, 1, 1)
            d.rectangle([db[0] + 6, db[1] + 8, db[2] - 6, db[3]], fill=(20, 20, 20))
        _label(d, b.get("name", ""), cell_box(x, y, w, roof_h, 4), font=F if w >= 3 else F_SMALL)
        _badge(d, n, box[0] + 3, box[1] + 3)
    for p in area.props:
        n += 1
        (x, y), (w, h) = p["at"], p.get("size", [1, 1])
        box = cell_box(x, y, w, h, 3)
        d.rounded_rectangle(box, 5, fill=(186, 186, 186), outline=(64, 64, 64), width=2)
        if w * h >= 4:
            _label(d, p.get("name", ""), box, font=F_SMALL, fill=(30, 30, 30), shadow=None)
        _badge(d, n, box[0] + 2, box[1] + 2, fill=(90, 90, 90))
    for o in area.people:
        n += 1
        x, y = o["at"]
        bx = cell_box(x, y, 1, 1, 5)
        d.rounded_rectangle([bx[0] + 3, bx[1] - 4, bx[2] - 3, bx[3]], 6, fill=PINK, outline=PINK_DARK, width=2)
        _badge(d, n, bx[2] - 2, bx[1] - 8, fill=PINK_DARK)
    for s in area.signs:
        n += 1
        x, y = s["at"]
        bx = cell_box(x, y, 1, 1, 6)
        d.rectangle([bx[0], bx[1], bx[2], bx[1] + 12], fill=PINK, outline=PINK_DARK, width=2)
        d.line([((bx[0] + bx[2]) / 2, bx[1] + 12), ((bx[0] + bx[2]) / 2, bx[3])], fill=PINK_DARK, width=3)
        _badge(d, n, bx[2] - 2, bx[1] - 8, fill=PINK_DARK)
    for wp in area.warps:
        n += 1
        x, y = wp["at"]
        bx = cell_box(x, y, 1, 1, 3)
        d.rectangle(bx, outline=PINK, width=3)
        d.rectangle([bx[0] + 7, bx[1] + 7, bx[2] - 7, bx[3] - 7], fill=(20, 20, 20))
        _badge(d, n, bx[2] - 2, bx[1] - 8, fill=PINK_DARK)

    for e in area.exits:
        cells = e["cells"]
        a, b = min(cells), max(cells) + 1
        to = str(e.get("to", "?"))
        if e["edge"] in ("north", "south"):
            yy = 4 if e["edge"] == "north" else M + area.h * u + 4
            box = [M + a * u, yy, M + b * u - 1, yy + M - 8]
        else:
            xx = 2 if e["edge"] == "west" else M + area.w * u + 2
            box = [xx, M + a * u, xx + M - 4, M + b * u - 1]
        d.rectangle(box, fill=(255, 255, 255))
        _label(d, ("^ " if e["edge"] == "north" else "v " if e["edge"] == "south" else "") + to, box,
               font=F_SMALL, fill=(0, 0, 0), shadow=None)
    return img


def legend(area, height):
    W = 420
    img = Image.new("RGB", (W, height), (28, 28, 32))
    d = ImageDraw.Draw(img)
    y = 8
    d.text((10, y), "Pieces (grey = building or prop, pink = sprite or event)", font=F, fill=(230, 230, 230))
    y += 20
    for i, p in enumerate(area.pieces(), 1):
        size = "x".join(str(v) for v in p.get("size", [1, 1]))
        line = f"{i:>2}  {p['kind']:<8} {p.get('name', '')}"
        extra = []
        if p["kind"] in ("building", "prop"):
            extra.append(size)
        if p.get("art"):
            extra.append(p["art"].replace("art:", ""))
        if p.get("to"):
            extra.append("-> " + str(p["to"]))
        if p.get("role"):
            extra.append(p["role"])
        col = PINK if p["kind"] in ("person", "sign", "warp") else (220, 220, 220)
        d.text((10, y), line, font=F, fill=col)
        y += 14
        if extra:
            for ln in textwrap.wrap("    " + "  ".join(extra), 64):
                d.text((10, y), ln, font=F_SMALL, fill=(150, 150, 150))
                y += 12
        y += 2
        if y > height - 60:
            d.text((10, y), "...", font=F, fill=(200, 200, 200))
            break
    if area.todo:
        y += 8
        d.text((10, y), "Open on this layout", font=F, fill=(255, 210, 120))
        y += 16
        for t in area.todo:
            for ln in textwrap.wrap("- " + t, 62):
                if y < height - 14:
                    d.text((10, y), ln, font=F_SMALL, fill=(220, 200, 160))
                    y += 12
    return img


def sheet(area, vanilla_img=None):
    m = draw_map(area)
    parts = []
    if vanilla_img is not None:
        v = vanilla_img.resize((vanilla_img.width * S, vanilla_img.height * S), Image.NEAREST)
        vv = Image.new("RGB", (v.width + 2 * M, v.height + 2 * M), (40, 40, 44))
        vv.paste(v, (M, M))
        parts.append(("vanilla " + area.replaces, vv))
    parts.append((f"blockout  {area.name}", m))
    h = max(p.height for _, p in parts)
    lg = legend(area, max(h, 400))
    head = 52
    W = sum(p.width for _, p in parts) + lg.width
    out = Image.new("RGB", (W, max(h, lg.height) + head), (28, 28, 32))
    d = ImageDraw.Draw(out)
    d.text((10, 6), f"{area.name}  ({area.planet}, {area.kind})   layout: {area.status}", font=F_BIG, fill=(255, 255, 255))
    d.text((10, 28), area.story[:170], font=F, fill=(190, 190, 190))
    x = 0
    for title, p in parts:
        out.paste(p, (x, head))
        d.text((x + M, head + 2), title, font=F_SMALL, fill=(200, 200, 200))
        x += p.width
    out.paste(lg, (x, head))
    return out

"""Interior room shells: wiki/mapping/rooms.csv and the `room:` block of an area yaml.

rooms.csv has one row per room style (`room:<style>`, kind `style`) and one per kit part
(`room:<style>:<part>`, kind `part`). A part's `size` is its drawn size in 16x16 cells (W x H) and its
`hit_box` gives one code per cell, rows top to bottom joined by `/`:

    #  blocks            .  walkable              o  blocks, drawn over the player (top layer)
    ^  walkable, drawn over the player (walk under it)          c  counter: blocks, talk across it
    s  stairs or ramp (walkable, changes level)   d  door or warp (walkable, leaves the room)
    v  ledge, jump down only                      _  pit, shaft or void (blocks)    ~  liquid (blocks)

An area that has a room shell names it in its yaml:

    room:
      style: room:tatooine-adobe        # a style row
      map: 11x9                         # the map size the room is drawn at (its grid)
      parts: [floor, wall-back, ..., room:cloud-city:window]   # parts of its style by name, or any part by id
      grow: '13x10: why the room needs a bigger map than Emerald's'   # optional

Every interior area must have one; built dungeons (Death Star decks, Fortress Vader...) may.
"""
import csv
import os

from .vanilla import ROOT

PATH = ROOT / "wiki" / "mapping" / "rooms.csv"
CODES = set("#.o^csdv_~")
CORE = ["floor", "floor-alt", "wall-back", "wall-side", "wall-front", "corner-in", "corner-out", "corner-front",
        "wall-end", "exit-mat", "doorway", "stairs", "window"]


def load():
    if not PATH.exists():
        return {}
    return {r["room_id"]: r for r in csv.DictReader(open(PATH))}


def part_ids(block):
    """The full part ids an area's `room:` block names."""
    st = (block or {}).get("style", "")
    return [p if p.startswith("room:") else f"{st}:{p}" for p in (block or {}).get("parts") or []]


def check(areas):
    """Problems with rooms.csv and with the `room:` block of every area (Area objects)."""
    rows = load()
    out = []
    if not rows:
        return ["rooms.csv is missing"]
    styles = {k: r for k, r in rows.items() if r["kind"] == "style"}
    for rid, r in rows.items():
        if r["kind"] != "part":
            continue
        if f"room:{r['style']}" not in styles:
            out.append(f"{rid}: style room:{r['style']} has no style row")
        try:
            w, h = (int(v) for v in r["size"].split("x"))
        except ValueError:
            out.append(f"{rid}: size {r['size']!r} is not WxH")
            continue
        hb = r["hit_box"].split("/")
        if len(hb) != h or any(len(line) != w for line in hb) or set("".join(hb)) - CODES:
            out.append(f"{rid}: hit_box {r['hit_box']!r} does not fit {r['size']} or has unknown codes")
        if not (ROOT / "wiki" / r["placeholder"]).exists():
            out.append(f"{rid}: placeholder {r['placeholder']} is missing (run wiki/world/interiors/rooms/make_placeholders.py)")
    for sid, s in styles.items():
        have = {r["part"] for r in rows.values() if r["kind"] == "part" and r["style"] == s["style"]}
        for p in CORE:
            if p not in have:
                out.append(f"{sid}: core part {p} is missing")
        if not (ROOT / "wiki" / s["placeholder"]).exists():
            out.append(f"{sid}: sheet {s['placeholder']} is missing (run wiki/world/interiors/rooms/make_placeholders.py)")
    for a in areas:
        block = a.raw.get("room")
        if not block:
            if a.kind == "interior":
                out.append(f"{a.id}: interior has no room style (`room:` block)")
            continue
        st = block.get("style", "")
        if st not in styles:
            out.append(f"{a.id}: room style {st!r} is not a style in rooms.csv")
            continue
        for pid in part_ids(block):
            if pid not in rows or rows[pid]["kind"] != "part":
                out.append(f"{a.id}: room part {pid} is not in rooms.csv")
        if block.get("map") != f"{a.w}x{a.h}":
            out.append(f"{a.id}: room map {block.get('map')} does not match the grid {a.w}x{a.h}")
    return out


def index(areas):
    """Write `used_in` and `areas` of every rooms.csv row from the area yamls; return {area id: block}."""
    rows = load()
    if not rows:
        return {}
    uses, blocks = {}, {}
    for a in areas:
        block = a.raw.get("room")
        if not block:
            continue
        blocks[a.id] = block
        for rid in [block.get("style", "")] + part_ids(block):
            uses.setdefault(rid, set()).add(a.id)
    for rid, r in rows.items():
        where = sorted(uses.get(rid, ()))
        r["used_in"] = str(len(where))
        r["areas"] = " ".join(where[:6]) + (" ..." if len(where) > 6 else "")
    with open(PATH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(next(iter(rows.values())).keys()))
        w.writeheader()
        w.writerows(rows.values())
    print(PATH)
    return blocks

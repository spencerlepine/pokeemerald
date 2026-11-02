"""python3 -m mockup render [area-id ...] [--planet P] [--all]   -> wiki/mockup/<planet>/<area>.png
python3 -m mockup world                                        -> wiki/mockup/<planet>/_planet.png and _world.png
python3 -m mockup missing                                      -> art ids with no entry in styles.yaml

Phase 1 (wiki/world) is read, never written. Per-area tweaks go in wiki/mockup/overrides/<area>.yaml."""
import argparse
import glob
import os
import sys

from PIL import Image, ImageDraw

from . import draw
from .style import MOCK, WORLD, Styles, apply_overrides, load_area

ORDER = ["TATOOINE", "KASHYYYK", "SULLUST", "MUSTAFAR", "ENDOR", "BESPIN", "JEDHA", "YAVIN 4", "HOTH", "DAGOBAH",
         "KAMINO", "ILUM", "GRAND ARENA", "FELUCIA", "TYTHON", "ATOLLON", "MORTIS", "ASTEROID FIELD", "DEATH STAR", "SHARED"]


def _areas():
    out = []
    for p in sorted(glob.glob(str(WORLD / "**" / "*.yaml"), recursive=True)):
        doc = load_area(p)
        doc["_path"] = p
        out.append(doc)
    return out


def _out(doc):
    rel = os.path.relpath(os.path.dirname(doc["_path"]), WORLD)
    return MOCK / rel / f"{doc['id']}.png"


def cmd_render(a):
    st = Styles()
    docs = _areas()
    if a.ids:
        docs = [x for x in docs if x["id"] in a.ids]
    elif a.planet:
        docs = [x for x in docs if x.get("planet") == a.planet.upper()]
    elif not a.all:
        sys.exit("name areas, --planet P or --all")
    for doc in docs:
        img = draw.area(apply_overrides(doc), st, labels=not a.no_labels)
        out = _out(doc)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
    print(f"{len(docs)} areas rendered")


def cmd_world(a):
    st = Styles()
    docs = _areas()
    panels = []
    for pl in ORDER + sorted({x.get("planet") for x in docs} - set(ORDER)):
        mine = [x for x in docs if x.get("planet") == pl and x.get("kind") in ("town", "route", "landmark", "space")]
        if not mine:
            continue
        if all(x.get("pos") is None for x in mine):
            cx = 0
            for x in mine:
                w = max(len(r) for r in x["grid"].splitlines() if r)
                x["pos"], cx = [cx, 0], cx + w + 4
        placed = [x for x in mine if x.get("pos") is not None]
        imgs = {x["id"]: draw.area(apply_overrides(x), st, labels=False) for x in placed}
        x0 = min(x["pos"][0] for x in placed)
        y0 = min(x["pos"][1] for x in placed)
        x1 = max(x["pos"][0] + imgs[x["id"]].width // draw.C for x in placed)
        y1 = max(x["pos"][1] + imgs[x["id"]].height // draw.C for x in placed)
        k = a.cell
        pad, head = 12, 30
        sheet = Image.new("RGB", ((x1 - x0) * k + 2 * pad, (y1 - y0) * k + 2 * pad + head), (24, 24, 30))
        dd = ImageDraw.Draw(sheet)
        dd.text((pad, 8), pl, font=draw.F_BIG, fill=(255, 255, 255))
        for x in placed:
            im = imgs[x["id"]].resize((imgs[x["id"]].width * k // draw.C, imgs[x["id"]].height * k // draw.C), Image.LANCZOS)
            sheet.paste(im, (pad + (x["pos"][0] - x0) * k, head + pad + (x["pos"][1] - y0) * k))
        for x in placed:
            w, h = imgs[x["id"]].width * k // draw.C, imgs[x["id"]].height * k // draw.C
            cx, cy = pad + (x["pos"][0] - x0) * k + w / 2, head + pad + (x["pos"][1] - y0) * k + h / 2
            draw.label(dd, x.get("name", x["id"]), cx, cy)
        out = MOCK / pl.lower().replace(" ", "-") / "_planet.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
        panels.append(sheet)
        print(os.path.relpath(out, MOCK))
    cols, gap = 4, 16
    cw = max(p.width for p in panels)
    rows = [panels[i:i + cols] for i in range(0, len(panels), cols)]
    H = sum(max(p.height for p in r) for r in rows) + gap * (len(rows) + 1)
    world = Image.new("RGB", (cols * cw + gap * (cols + 1), H), (24, 24, 30))
    y = gap
    for r in rows:
        x = gap
        for p in r:
            world.paste(p, (x, y))
            x += cw + gap
        y += max(p.height for p in r) + gap
    world.save(MOCK / "_world.png")
    print("_world.png", world.size)


def cmd_missing(a):
    st = Styles()
    seen = set()
    for doc in _areas():
        for k in ("buildings", "props"):
            for o in doc.get(k) or []:
                if o.get("art") and o["art"] not in st.shapes:
                    seen.add(o["art"])
    for s in sorted(seen):
        print(s)
    print(f"{len(seen)} art ids without a shape")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mockup")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("ids", nargs="*")
    r.add_argument("--planet")
    r.add_argument("--all", action="store_true")
    r.add_argument("--no-labels", action="store_true")
    w = sub.add_parser("world")
    w.add_argument("--cell", type=int, default=4, help="px per cell on the planet sheets")
    sub.add_parser("missing")
    a = ap.parse_args(argv)
    {"render": cmd_render, "world": cmd_world, "missing": cmd_missing}[a.cmd](a)

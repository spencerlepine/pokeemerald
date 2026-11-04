"""The catalog: every building the game needs, one entry per design, in `catalog/<planet>.yaml`.

    buildings:
      - id: bld:tatooine:anchorhead-camie-s-family-home   # unique, never reused
        kind: home          # home bacta depot arena shop hall landmark hangar pad tower hut market fill
        name: Camie's family home
        areas: [anchorhead] # the areas (wiki/world/<planet>/<area>.yaml) that place it; [] = fill
        art: art:tatooine:homestead-dome   # the world_art.csv row it draws, if any
        size: [5, 4]        # the lot: drawn cells W x H (from the area's `buildings:` entry)
        door: 2             # the door's cell column, 0 = west (from the area)
        blueprint: tatooine/dome-hut       # empty until someone designs it
        seed: 3
        set: {roof: dome}   # optional param overrides
        about: one line on what it is, from the films

`init` adds an entry for every area building that has none (matched by area and name) and never
changes an entry already there. `build` renders every designed entry, checks it against its lot and
writes the wiki: `wiki/world/buildings/<planet>/<slug>.png` and `wiki/mapping/buildings.csv`.
"""
import csv
import glob
import os
import re

import yaml

from . import compose as C
from . import render as R

CATALOG = os.path.join(C.HERE, "catalog")
WIKI_WORLD = os.path.join(C.ROOT, "wiki", "world")
OUT_PNG = os.path.join(WIKI_WORLD, "buildings")
CSV = os.path.join(C.ROOT, "wiki", "mapping", "buildings.csv")
FIELDS = ["id", "planet", "kind", "name", "areas", "art", "blueprint", "seed", "set", "size", "drawn",
          "footprint", "door", "door_found", "fits", "tiles", "png", "status", "about"]
KINDS = ["bacta", "depot", "arena", "home", "hut", "shop", "market", "hall", "tower", "hangar", "pad",
         "landmark", "fill"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def planet_key(planet):
    return slug(planet)


def guess_kind(name, art):
    n = (name + " " + art).lower()
    for k, words in (("bacta", ["bacta"]), ("depot", ["supply depot", "supply-depot"]),
                     ("arena", ["arena", "temple (arena)"]), ("pad", ["landing", "pad", "shuttle", "clearing"]),
                     ("hangar", ["hangar", "docking", "shipyard", "dock shed"]),
                     ("shop", ["shop", "junk", "store", "galleria", "trader", "smith", "dealer"]),
                     ("landmark", ["palace", "temple", "tower", "museum", "fortress", "gate", "hall", "lab",
                                   "academy", "bunker", "cantina", "station", "refinery", "observatory",
                                   "outpost", "center", "co-op", "den", "bathhouse", "farm"]),
                     ("hut", ["hut", "shelter"]), ("home", ["home", "house", "flat", "quarters", "dwelling",
                                                           "dome", "barracks", "hostel", "motel"])):
        if any(w in n for w in words):
            return k
    return "home"


def area_buildings():
    """{planet key: [(area id, building dict)]} from every area yaml in the wiki."""
    out = {}
    for f in sorted(glob.glob(os.path.join(WIKI_WORLD, "*", "*.yaml"))):
        try:
            a = yaml.safe_load(open(f))
        except Exception:
            continue
        if not isinstance(a, dict) or not a.get("buildings"):
            continue
        for b in a["buildings"]:
            out.setdefault(planet_key(a.get("planet", "")), []).append((a["id"], a.get("planet", ""), b))
    return out


def load_catalog(pk):
    p = os.path.join(CATALOG, f"{pk}.yaml")
    if not os.path.exists(p):
        return p, {"planet": pk.upper(), "buildings": []}
    return p, C.load(p) or {"buildings": []}


def save_catalog(path, cat):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(f"# Building catalog for {cat.get('planet')}: one entry per building design (see bkit/catalog.py).\n")
        yaml.safe_dump(cat, fh, sort_keys=False, allow_unicode=True, width=140, default_flow_style=None)


def init():
    """A catalog file may hold any planet's entries (`planet:` at its top says which; a planet can be
    split over several files, e.g. tatooine.yaml and tatooine-landmarks.yaml). New entries go to
    catalog/<planet>.yaml."""
    added = 0
    have, have_ids = set(), set()
    for f in glob.glob(os.path.join(CATALOG, "*.yaml")):
        for e in (C.load(f).get("buildings") or []):
            have_ids.add(e["id"])
            for a in e.get("areas") or []:
                have.add(((a,), e.get("name")))
    for pk, items in area_buildings().items():
        path, cat = load_catalog(pk)
        cat.setdefault("planet", items[0][1])
        for area, planet, b in items:
            key = ((area,), b.get("name"))
            if key in have:
                continue
            bid = f"bld:{pk}:{slug(area)}-{slug(b.get('name', 'building'))}"
            n = 2
            while bid in have_ids:
                bid = f"bld:{pk}:{slug(area)}-{slug(b.get('name', 'building'))}-{n}"
                n += 1
            have_ids.add(bid)
            cat["buildings"].append({
                "id": bid, "kind": guess_kind(b.get("name", ""), b.get("art", "")), "name": b.get("name", ""),
                "areas": [area], "art": b.get("art", ""), "size": list(b.get("size") or [5, 4]),
                "door": b.get("door"), "blueprint": "", "seed": 0, "about": ""})
            added += 1
        save_catalog(path, cat)
    print(f"{added} new catalog entries")


def _read_csv():
    if not os.path.exists(CSV):
        return []
    return list(csv.DictReader(open(CSV)))


def build_one(e, planet):
    """Render one entry. Returns (row dict, sprite or None, messages)."""
    msgs = []
    W, H = (int(v) for v in e["size"])
    path = C.blueprint_path(e["blueprint"])
    raw, params, info = C.compose(path, int(e.get("seed", 0)), W, e.get("set"), H, e.get("door"))
    img, ind, warns, tiles = R.render(raw)
    msgs += warns
    depth = R.plan_depth(raw)
    img2, ind2, ok = R.fit(img, ind, H)
    drawn = f"{img.width // 16}x{img.height // 16}"
    if not ok:
        msgs.append(f"{e['id']}: drawn {drawn}, taller than its lot {W}x{H}")
    if depth > H:
        msgs.append(f"{e['id']}: stands on {depth} rows, deeper than its lot ({H})")
    if e.get("door") is not None and info["door_col"] is not None and info["door_col"] != int(e["door"]):
        msgs.append(f"{e['id']}: door in column {info['door_col']}, the area wants {e['door']}")
    if info["door_col"] is None and e.get("kind") not in ("landmark", "fill", "pad", "market", "tower"):
        msgs.append(f"{e['id']}: no part named `door`")
    row = {
        "id": e["id"], "planet": planet, "kind": e.get("kind", ""), "name": e.get("name", ""),
        "areas": " ".join(e.get("areas") or []), "art": e.get("art", ""), "blueprint": e["blueprint"],
        "seed": str(e.get("seed", 0)), "set": " ".join(f"{k}={v}" for k, v in (e.get("set") or {}).items()),
        "size": f"{W}x{H}", "drawn": f"{W}x{max(img.height // 16, H) if ok else img.height // 16}",
        "footprint": f"{W}x{depth}", "door": "" if e.get("door") is None else str(e["door"]),
        "door_found": "" if info["door_col"] is None else str(info["door_col"]),
        "fits": "yes" if ok and depth <= H else "NO", "tiles": str(tiles), "png": "", "status": "greybox",
        "about": e.get("about", ""),
    }
    return row, (img2 if ok else img), msgs


def build(planets=None, wiki=True, only=None):
    # a full build starts the csv afresh (so removed entries go); --planet / --only keep the other rows,
    # and a rebuilt entry replaces its old row
    full = not planets and not only
    rows = {} if full else {r["id"]: r for r in _read_csv()}
    problems = 0
    made = 0
    shots = {}
    for path in sorted(glob.glob(os.path.join(CATALOG, "*.yaml"))):
        pk = os.path.basename(path)[:-5]
        if planets and pk not in {planet_key(p) for p in planets} and \
                planet_key(C.load(path).get("planet") or "") not in {planet_key(p) for p in planets}:
            continue
        cat = C.load(path)
        stem, pk = pk, planet_key(cat.get("planet") or pk)
        for e in cat.get("buildings") or []:
            if not e.get("blueprint") or (only and not any(o in e["id"] for o in only)):
                continue
            try:
                row, img, msgs = build_one(e, pk)
            except (SystemExit, Exception) as ex:
                print("ERROR", e["id"], ex)
                problems += 1
                continue
            for m in msgs:
                print("WARNING", m)
            problems += bool(msgs)
            name = e["id"].split(":", 2)[-1]
            d = os.path.join(OUT_PNG if wiki else os.path.join(C.HERE, "output", "build"), pk)
            os.makedirs(d, exist_ok=True)
            img.save(os.path.join(d, f"{name}.png"))
            row["png"] = os.path.relpath(os.path.join(d, f"{name}.png"), os.path.join(C.ROOT, "wiki")) if wiki else ""
            rows[row["id"]] = row
            shots.setdefault(stem, []).append((f"{e.get('name', '')[:22]} {row['size']} fp{row['footprint'].split('x')[1]} "
                                             f"{'' if row['fits'] == 'yes' else 'NO FIT '}{row['tiles']}t", img))
            made += 1
    print(f"{made} buildings rendered, {problems} with warnings")
    for pk, sh in shots.items():                  # a review sheet per planet, always in output/
        out = os.path.join(C.HERE, "output", "build", f"_sheet_{pk}.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        R.sheet(f"{pk}: {len(sh)} buildings (lot size, footprint rows, tiles)", sh, scale=2, max_w=1800).save(out)
        print("->", os.path.relpath(out, C.HERE))
    rows = list(rows.values())
    if wiki:
        rows.sort(key=lambda r: (r["planet"], KINDS.index(r["kind"]) if r["kind"] in KINDS else 99, r["id"]))
        with open(CSV, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in FIELDS})
        print("->", os.path.relpath(CSV, C.ROOT))
    return rows


def collage(out=None, scale=2):
    """Every built building, grouped by planet, at real proportions, labelled. One image."""
    from PIL import Image, ImageDraw
    rows = [r for r in _read_csv() if r.get("png") and os.path.exists(os.path.join(C.ROOT, "wiki", r["png"]))]
    out = out or os.path.join(OUT_PNG, "_collage.png")
    Wmax = 2400
    order = []
    for r in rows:
        if r["planet"] not in order:
            order.append(r["planet"])
    blocks = []
    for pk in order:
        ims = [(r, Image.open(os.path.join(C.ROOT, "wiki", r["png"])).convert("RGBA")) for r in rows if r["planet"] == pk]
        # shelf-pack at `scale`
        x, y, rowh, placed = 0, 0, 0, []
        for r, im in ims:
            w, h = im.width * scale, im.height * scale + 12
            if x + w > Wmax - 16:
                x, y, rowh = 0, y + rowh + 8, 0
            placed.append((x, y, r, im))
            x += w + 8
            rowh = max(rowh, h)
        blocks.append((pk, placed, y + rowh))
    H = sum(b[2] + 36 for b in blocks) + 40
    sheet = Image.new("RGB", (Wmax, H), (28, 28, 32))
    d = ImageDraw.Draw(sheet)
    d.text((12, 10), f"Building kit: {len(rows)} greybox buildings, by planet (2x, a cell = 32 px)", fill=(240, 240, 240))
    y0 = 40
    for pk, placed, h in blocks:
        d.text((12, y0), f"{pk.upper()} ({len(placed)})", fill=(255, 210, 120))
        for x, y, r, im in placed:
            g = R.on_ground(im, scale)
            sheet.paste(g.convert("RGB"), (16 + x, y0 + 18 + y + 12))
            d.text((16 + x, y0 + 18 + y), r["name"][: max(6, im.width * scale // 6)], fill=(200, 200, 200))
        y0 += h + 36
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    print("->", os.path.relpath(out, C.ROOT), sheet.size)

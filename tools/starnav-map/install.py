"""Install the Holo Globe StarNAV map (round 2, style 3) into ../../game.

    python3 install.py           # write the art and the C tables into ../../game
    python3 install.py --check   # only report tile and colour counts (nothing written)

What it writes (all generated, never edit by hand):
- graphics/pokenav/region_map/starnav/galaxy.{png,bin,pal}: the galaxy view (zoomed out).
- graphics/pokenav/region_map/starnav/planet_<n>.{png,bin} and holo.pal: each planet as a hologram (zoomed in).
- graphics/pokenav/region_map/cursor_small.png, cursor_large.png, cursor.pal: the cell cursor and the planet ring.
- src/data/region_map/starnav_map.h: planets, their place in the galaxy, the cursor jumps, each planet's 28x15
  grid of map sections, where every map section sits, and where every overworld map lands on its planet.

The region map code in src/region_map.c draws them (look for STARNAV). The map BG is Emerald's: one 8bpp affine
BG, 64x64 tilemap, at most 256 tiles, colours in BG palettes 7-9. So each image is cut into 8x8 tiles, the
starry space is drawn from a few shared star tiles, and if an image still has more than 255 tiles the rarest
tiles are swapped for their nearest look-alike until it fits.
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import variants as V  # noqa: E402
from world import CELL, LAYOUT, World, load_lanes  # noqa: E402

ROOT = HERE.parents[1]
GAME = ROOT / "game"
GFX = GAME / "graphics" / "pokenav" / "region_map"
OUT_GFX = GFX / "starnav"
HEADER = GAME / "src" / "data" / "region_map" / "starnav_map.h"
WIKI = ROOT / "wiki"

MAP_X, MAP_Y = 1, 2          # where the 28x15 map sits in the 64x64 affine tilemap (MAPCURSOR_X_MIN / _Y_MIN)
PAL_FIRST = 112              # BG palette 7
PAL_SLOTS = [i for i in range(112, 160) if i % 16 != 0]   # 45 colours; the first entry of each 16 is left alone
MAX_TILES = 256
INNER = (7, 1, 14, 12)       # Holo Globe: the planet sits in these cells of the 28x15 grid
SPACE = V.g((8, 8, 16))
CURSOR_COLS = {1: (248, 208, 0), 2: (248, 240, 160), 3: (88, 200, 248), 4: (184, 240, 248), 5: (16, 40, 64)}


# ---------------------------------------------------------------- images

def screen_image(map_img):
    """The 224x120 map on the 512x512 affine layer, at tile (1, 2), space all round."""
    full = Image.new("RGB", (512, 512), SPACE)
    full.paste(map_img.convert("RGB"), (MAP_X * 8, MAP_Y * 8))
    return full


def star_tiles(seed, cols, n=10):
    """A few shared space tiles: one empty, the rest with one or two stars."""
    rnd = random.Random(seed)
    tiles = [Image.new("RGB", (8, 8), SPACE)]
    for i in range(n - 1):
        t = Image.new("RGB", (8, 8), SPACE)
        for _ in range(1 + (i % 2)):
            t.putpixel((rnd.randrange(8), rnd.randrange(8)), V.g(rnd.choice(cols)))
        tiles.append(t)
    return tiles


def respace(img, bg_cols, stars, seed):
    """Every 8x8 tile that is only space (and stars) becomes one of the shared star tiles."""
    rnd = random.Random(seed)
    bg_cols = {V.g(c) for c in bg_cols}
    px = img.load()
    for ty in range(0, img.height, 8):
        for tx in range(0, img.width, 8):
            cols = {px[tx + i, ty + j] for j in range(8) for i in range(8)}
            if cols <= bg_cols:
                pick = stars[0] if rnd.random() < 0.45 else rnd.choice(stars)
                img.paste(pick, (tx, ty))


def reduce_colours(imgs, n=len(PAL_SLOTS)):
    """Quantize a set of images together to at most n GBA colours (nearest colour, no dithering)."""
    cols = Counter()
    for im in imgs:
        cols.update(im.getdata())
    if len(cols) <= n:
        return
    # a strip with every colour, repeated by how often it is used (capped), for median cut
    strip = []
    for c, k in cols.items():
        strip += [c] * min(k, 400)
    w = 256
    h = (len(strip) + w - 1) // w
    sim = Image.new("RGB", (w, h))
    sim.putdata(strip + [strip[-1]] * (w * h - len(strip)))
    q = sim.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[:n * 3]
    keep = sorted({V.g(tuple(pal[i:i + 3])) for i in range(0, len(pal), 3)})
    near = {c: min(keep, key=lambda k: (k[0] - c[0]) ** 2 + (k[1] - c[1]) ** 2 + (k[2] - c[2]) ** 2) for c in cols}
    for im in imgs:
        im.putdata([near[c] for c in im.getdata()])


def tiles_of(img):
    px = img.load()
    out = []
    for ty in range(0, img.height, 8):
        for tx in range(0, img.width, 8):
            out.append(tuple(px[tx + i, ty + j] for j in range(8) for i in range(8)))
    return out


def tile_distance(a, b):
    return sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2]) for p, q in zip(a, b))


def fit_tiles(img, limit=MAX_TILES):
    """Unique tiles of a 512x512 image, merged down to `limit`. Tile 0 is plain space.
    Returns (tileset list, tilemap list of 64*64 indices, merged count)."""
    ts = tiles_of(img)
    space = tuple([SPACE] * 64)
    count = Counter(ts)
    uniq = [space] + [t for t, _ in count.most_common() if t != space]
    merged = 0
    remap = {}
    while len(uniq) > limit:
        # the rarest tile goes to its nearest look-alike
        rare = min(uniq[1:], key=lambda t: count[t])
        uniq.remove(rare)
        best = min(uniq, key=lambda t: tile_distance(t, rare))
        remap[rare] = best
        count[best] += count[rare]
        merged += 1
    def resolve(t):
        while t in remap:
            t = remap[t]
        return t
    index = {t: i for i, t in enumerate(uniq)}
    return uniq, [index[resolve(t)] for t in ts], merged


def palette_for(tilesets):
    cols = Counter()
    for uniq in tilesets:
        for t in uniq:
            cols.update(t)
    if len(cols) > len(PAL_SLOTS):
        raise SystemExit(f"{len(cols)} colours, more than {len(PAL_SLOTS)}: simplify the art")
    order = sorted(cols, key=lambda c: (sum(c), c))
    return {c: PAL_SLOTS[i] for i, c in enumerate(order)}


def write_png(path, uniq, pal_index):
    """An indexed PNG, 16 tiles wide, palette indices as on the GBA (112-159)."""
    rows = (len(uniq) + 15) // 16
    im = Image.new("P", (128, rows * 8), 0)
    flat = [0, 0, 0] * 256
    for c, i in pal_index.items():
        flat[i * 3:i * 3 + 3] = list(c)
    im.putpalette(flat)
    px = im.load()
    for n, t in enumerate(uniq):
        x0, y0 = (n % 16) * 8, (n // 16) * 8
        for k, c in enumerate(t):
            px[x0 + k % 8, y0 + k // 8] = pal_index[c]
    im.save(path)


def write_pal(path, pal_index):
    cols = [(0, 0, 0)] * 48
    for c, i in pal_index.items():
        cols[i - PAL_FIRST] = c
    # the entries left alone copy their neighbour, so nothing reads as a stray colour
    for i in range(48):
        if i % 16 == 0:
            cols[i] = cols[i + 1]
    path.write_text("JASC-PAL\r\n0100\r\n48\r\n" + "".join(f"{r} {g} {b}\r\n" for r, g, b in cols))


def cursor_art():
    """cursor_small: 2 frames 16x16, a gold bracket box round an 8x8 cell. cursor_large: 3 frames 32x32, a
    dashed cyan ring round a planet globe, turning."""
    small = Image.new("P", (16, 32), 0)
    for f, o in enumerate((3, 2)):
        a, b = o, 15 - o
        for i in range(4):
            for (x, y) in ((a + i, a), (a, a + i), (b - i, a), (b, a + i), (a + i, b), (a, b - i), (b - i, b), (b, b - i)):
                small.putpixel((x, y + 16 * f), 1)
    large = Image.new("P", (32, 96), 0)
    for f in range(3):
        for k in range(96):
            ang = k / 96 * 2 * math.pi
            if (k + f * 4) % 12 >= 8:
                continue
            for r, col in ((10.5, 3), (11.5, 4)):
                x, y = int(round(16 + math.cos(ang) * r - 0.5)), int(round(16 + math.sin(ang) * r - 0.5))
                if 0 <= x < 32 and 0 <= y < 32:
                    large.putpixel((x, y + 32 * f), col)
    pal = [0, 0, 0] * 256
    pal[0:3] = [8, 8, 16]
    for i, c in CURSOR_COLS.items():
        pal[i * 3:i * 3 + 3] = list(c)
    small.putpalette(pal)
    large.putpalette(pal)
    return small, large


# ---------------------------------------------------------------- tables

def map_sections():
    """game map name -> its region map section, from data/maps/*/map.json."""
    out = {}
    for f in (GAME / "data" / "maps").glob("*/map.json"):
        m = json.load(open(f))
        out[f.parent.name] = m.get("region_map_section", "MAPSEC_NONE")
    return out


def camel(s):
    return "".join(p.capitalize() for p in s.split("-"))


def map_const(name):
    """The map's constant, as mapjson makes it: the id in data/maps/<name>/map.json (MAP_ROUTE130)."""
    return json.loads((GAME / "data" / "maps" / name / "map.json").read_text())["id"]

def all_yaml_areas():
    import yaml
    out = []
    for f in sorted((WIKI / "world").glob("*/**/*.yaml")):
        d = yaml.safe_load(open(f)) or {}
        if "id" not in d or "planet" not in d:
            continue
        rep = d.get("replaces") or "new"
        out.append({"id": d["id"], "planet": d["planet"], "kind": d.get("kind"),
                    "map": ("Sw" + camel(d["id"])) if rep == "new" else rep})
    return out


def connections():
    import csv
    out = defaultdict(set)
    for r in csv.DictReader(open(WIKI / "world" / "CONNECTIONS.csv")):
        out[r["from"]].add(r["to"])
        out[r["to"]].add(r["from"])
    return out


def main():
    check = "--check" in sys.argv
    world = World()
    planets = [p for p in LAYOUT if p != "DEATH STAR"] + ["DEATH STAR"]
    pidx = {p: i for i, p in enumerate(planets)}

    # ---- art
    gal = V.galaxy_map(world)
    gal_full = screen_image(gal)
    neb = {V.g(c) for c in [(8, 8, 16)]}
    respace(gal_full, neb | {V.g((120, 128, 160)), V.g((248, 248, 240))},
            star_tiles(11, [(120, 128, 160), (248, 248, 240), (64, 72, 96)]), 3)
    holo = V.holo_planets(world, backing=V.projector, inner=INNER)
    reduce_colours([gal_full])
    images = {"galaxy": gal_full}
    for p, v in holo.items():
        im = screen_image(v["img"])
        # the colours of plain space: whatever is left of the sphere (x 8-56 on screen)
        spx = im.load()
        space_cols = {spx[x, y] for x in range(8, 56) for y in range(16, 136)}
        respace(im, space_cols, star_tiles(pidx[p] + 20, [(32, 48, 72), (48, 72, 104)]), pidx[p])
        images[p] = im
    reduce_colours([images[p] for p in holo])
    fitted = {}
    for k, im in images.items():
        uniq, tmap, merged = fit_tiles(im)
        fitted[k] = (uniq, tmap)
        print(f"{k:16s} {len(uniq):3d} tiles ({merged} merged)")
    gal_pal = palette_for([fitted["galaxy"][0]])
    holo_pal = palette_for([fitted[p][0] for p in holo])
    print(f"galaxy colours {len(gal_pal)}, holo colours {len(holo_pal)}")
    if check:
        return

    OUT_GFX.mkdir(parents=True, exist_ok=True)
    for f in OUT_GFX.glob("*"):
        f.unlink()
    write_png(OUT_GFX / "galaxy.png", fitted["galaxy"][0], gal_pal)
    (OUT_GFX / "galaxy.bin").write_bytes(bytes(fitted["galaxy"][1]))
    write_pal(OUT_GFX / "galaxy.pal", gal_pal)
    write_pal(OUT_GFX / "holo.pal", holo_pal)
    slug = {}
    for p in holo:
        s = p.lower().replace(" ", "_")
        slug[p] = s
        write_png(OUT_GFX / f"planet_{s}.png", fitted[p][0], holo_pal)
        (OUT_GFX / f"planet_{s}.bin").write_bytes(bytes(fitted[p][1]))
    small, large = cursor_art()
    small.save(GFX / "cursor_small.png")
    large.save(GFX / "cursor_large.png")
    cols = [(8, 8, 16)] + [CURSOR_COLS.get(i, (0, 0, 0)) for i in range(1, 16)]
    (GFX / "cursor.pal").write_text("JASC-PAL\r\n0100\r\n16\r\n" + "".join(f"{r} {g} {b}\r\n" for r, g, b in cols))

    # ---- tables
    secs = map_sections()
    areas = all_yaml_areas()
    area_by_id = {a["id"]: a for a in areas}
    links = connections()
    # every map section's planet: the planet most of its maps are on
    votes = defaultdict(Counter)
    for a in areas:
        ms = secs.get(a["map"])
        if ms and ms != "MAPSEC_NONE":
            votes[ms][a["planet"]] += 1
    sec_planet = {ms: c.most_common(1)[0][0] for ms, c in votes.items()}

    # each planet's grid of sections (Holo Globe inner box), and each overworld area's place
    layouts = {}
    cells_of = defaultdict(list)       # mapsec -> cells on its planet's grid
    towns_at = {}
    for p, v in holo.items():
        grid = [["MAPSEC_NONE"] * 28 for _ in range(15)]
        for y, row in enumerate(v["cells"]):
            for x, a in enumerate(row):
                if a:
                    ms = secs.get(area_by_id[a]["map"], "MAPSEC_NONE")
                    grid[y][x] = ms
                    if ms != "MAPSEC_NONE" and sec_planet.get(ms) == p:
                        cells_of[ms].append((x, y))
        for a, c in v["towns"].items():
            ms = secs.get(area_by_id[a]["map"], "MAPSEC_NONE")
            if ms != "MAPSEC_NONE" and sec_planet.get(ms) == p:
                towns_at[ms] = tuple(c)
        layouts[p] = grid

    def home(ms):
        cs = cells_of.get(ms)
        if ms in towns_at:
            # the town's marker, or its own cell nearest the marker when a route took that cell
            t = towns_at[ms]
            return min(cs, key=lambda c: (c[0] - t[0]) ** 2 + (c[1] - t[1]) ** 2) if cs else t
        if cs:
            mx = sum(c[0] for c in cs) / len(cs)
            my = sum(c[1] for c in cs) / len(cs)
            return min(cs, key=lambda c: (c[0] - mx) ** 2 + (c[1] - my) ** 2)
        return None

    valid = {m["id"] for m in json.load(open(GAME / "src" / "data" / "region_map" / "region_map_sections.json"))["map_sections"]}
    homes = {}
    for ms, p in sec_planet.items():
        if ms not in valid or ms in ("MAPSEC_DYNAMIC", "MAPSEC_SECRET_BASE"):
            continue
        h = home(ms)
        if h is None:
            # a dungeon or a section with no outdoor cell: the place of an area it connects to
            seen, todo = set(), [a["id"] for a in areas if secs.get(a["map"]) == ms]
            while todo and h is None:
                a = todo.pop(0)
                if a in seen:
                    continue
                seen.add(a)
                for b in sorted(links.get(a, ())):
                    bb = area_by_id.get(b)
                    if not bb or bb["planet"] != p:
                        continue
                    bms = secs.get(bb["map"])
                    if bms and home(bms) and sec_planet.get(bms) == p:
                        h = home(bms)
                        break
                    todo.append(b)
        if h is None and p in holo:
            t = next(iter(holo[p]["towns"].values()), [14, 7])
            h = tuple(t)
        homes[ms] = (p, h)

    # where each overworld map lands: cell = ((tile - origin) / scale + offset) / 8
    map_xf = []
    for p, v in holo.items():
        x0, y0, s, ox, oy = v["xf"]
        for a in world.areas[p]:
            name = area_by_id[a["id"]]["map"]
            if not (GAME / "data" / "maps" / name).exists():
                continue
            # pixel of tile (tx, ty) on the map = (a.x + tx - x0) / s + ox; kept in 1/256 px
            bx = int(round(((a["x"] - x0) / s + ox) * 256))
            by = int(round(((a["y"] - y0) / s + oy) * 256))
            inv = int(round(256 / s))
            map_xf.append((map_const(name), pidx[p], bx, by, inv))

    # galaxy jumps: the nearest planet each way, scored as in the mockup player
    gpos = {p: V.GALAXY_POS[p] for p in planets}
    jumps = {}
    for p in planets:
        x0, y0 = gpos[p]
        row = []
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            best = None
            for q in planets:
                if q == p:
                    continue
                x, y = gpos[q]
                along = (x - x0) * dx + (y - y0) * dy
                if along <= 0:
                    continue
                score = along + 2 * (abs((x - x0) * dy) + abs((y - y0) * dx))
                if best is None or score < best[0]:
                    best = (score, q)
            row.append(pidx[best[1]] if best else 0xFF)
        jumps[p] = row

    write_header(planets, pidx, slug, gpos, jumps, layouts, homes, map_xf, fitted)
    print("wrote", HEADER.relative_to(ROOT), "and", OUT_GFX.relative_to(ROOT))
    preview(HERE / "out" / "ingame")


def preview(out_dir):
    """Rebuild each screen from the written tiles, tilemap and palette, as the GBA will show it (no sprites)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    def pal(path):
        lines = path.read_text().split()[3:]
        return [tuple(int(v) for v in lines[i:i + 3]) for i in range(0, len(lines), 3)]
    for png in sorted(OUT_GFX.glob("*.png")):
        name = png.stem
        p = pal(OUT_GFX / ("galaxy.pal" if name == "galaxy" else "holo.pal"))
        ts = Image.open(png)
        tmap = (OUT_GFX / f"{name}.bin").read_bytes()
        scr = Image.new("RGB", (240, 160), (0, 0, 0))
        tpx = ts.load()
        for ty in range(20):
            for tx in range(30):
                t = tmap[ty * 64 + tx]
                for j in range(8):
                    for i in range(8):
                        v = tpx[(t % 16) * 8 + i, (t // 16) * 8 + j]
                        scr.putpixel((tx * 8 + i, ty * 8 + j), p[v - PAL_FIRST] if v else (0, 0, 0))
        scr.resize((480, 320), Image.NEAREST).save(out_dir / f"{name}.png")


def c_name(p):
    return p.replace(" ", "_").replace("4", "4")


def write_header(planets, pidx, slug, gpos, jumps, layouts, homes, map_xf, fitted):
    L = []
    w = L.append
    w("// Generated by tools/starnav-map/install.py from the wiki world. Do not edit by hand.")
    w("// The Holo Globe StarNAV map: the galaxy (zoomed out) and each planet as a hologram (zoomed in).")
    w("#ifndef GUARD_DATA_REGION_MAP_STARNAV_MAP_H")
    w("#define GUARD_DATA_REGION_MAP_STARNAV_MAP_H")
    w("")
    w(f"#define STARNAV_PLANET_COUNT {len(planets)}")
    w("#define STARNAV_PLANET_NONE 0xFF")
    w(f"#define STARNAV_MAP_COUNT {len(map_xf)}")
    w("")
    for p in planets:
        w(f"static const u8 sStarNavPlanetName_{c_name(p)}[] = _(\"{p}\");")
    w("")
    w("static const u16 sStarNavGalaxyPal[] = INCGFX_U16(\"graphics/pokenav/region_map/starnav/galaxy.pal\", \".gbapal\");")
    w("static const u16 sStarNavHoloPal[] = INCGFX_U16(\"graphics/pokenav/region_map/starnav/holo.pal\", \".gbapal\");")
    n = len(fitted["galaxy"][0])
    w(f"static const u32 sStarNavGalaxyGfxLZ[] = INCGFX_U32(\"graphics/pokenav/region_map/starnav/galaxy.png\", \".8bpp.lz\", \"-num_tiles {n} -Wnum_tiles\");")
    w("static const u32 sStarNavGalaxyTilemapLZ[] = INCGFX_U32(\"graphics/pokenav/region_map/starnav/galaxy.bin\", \".lz\");")
    for p in planets:
        if p not in slug:
            continue
        s = slug[p]
        n = len(fitted[p][0])
        w(f"static const u32 sStarNavPlanetGfxLZ_{c_name(p)}[] = INCGFX_U32(\"graphics/pokenav/region_map/starnav/planet_{s}.png\", \".8bpp.lz\", \"-num_tiles {n} -Wnum_tiles\");")
        w(f"static const u32 sStarNavPlanetTilemapLZ_{c_name(p)}[] = INCGFX_U32(\"graphics/pokenav/region_map/starnav/planet_{s}.bin\", \".lz\");")
    w("")
    w("struct StarNavPlanet")
    w("{")
    w("    const u8 *name;")
    w("    const u32 *gfx;         // NULL: no map of its own (the Death Star), A does nothing there")
    w("    const u32 *tilemap;")
    w("    u8 x, y;                // globe centre in the galaxy, in map pixels (screen = +8, +16)")
    w("    u8 radius;")
    w("    u8 jump[4];             // next planet up, down, left, right (STARNAV_PLANET_NONE: none)")
    w("};")
    w("")
    w("static const struct StarNavPlanet sStarNavPlanets[STARNAV_PLANET_COUNT] =")
    w("{")
    for p in planets:
        x, y = gpos[p]
        r = V.GLOBE_R.get(p, 5)
        j = ", ".join(("STARNAV_PLANET_NONE" if v == 0xFF else str(v)) for v in jumps[p])
        if p in slug:
            g = f"sStarNavPlanetGfxLZ_{c_name(p)}, sStarNavPlanetTilemapLZ_{c_name(p)}"
        else:
            g = "NULL, NULL"
        w(f"    [{pidx[p]}] = {{sStarNavPlanetName_{c_name(p)}, {g}, {x}, {y}, {r}, {{{j}}}}}, // {p}")
    w("};")
    w("")
    w("// Each planet's map sections on the 28x15 grid (the same grid as Emerald's map: cursor x 1-28, y 2-16).")
    w("static const mapsec_u8_t sStarNavLayouts[STARNAV_PLANET_COUNT][15][28] =")
    w("{")
    for p in planets:
        if p not in layouts:
            continue
        w(f"    [{pidx[p]}] = {{ // {p}")
        for row in layouts[p]:
            w("        {" + ", ".join(row) + "},")
        w("    },")
    w("};")
    w("")
    w("// Where each map section sits: planet + 1 (0: not on the StarNAV map), and its cell on that planet's grid.")
    w("struct StarNavHome { u8 planet; u8 x; u8 y; };")
    w("static const struct StarNavHome sStarNavMapSecHomes[MAPSEC_NONE] =")
    w("{")
    for ms in sorted(homes):
        p, h = homes[ms]
        if h is None:
            w(f"    [{ms}] = {{{pidx[p] + 1}, 0xFF, 0xFF}},")
        else:
            w(f"    [{ms}] = {{{pidx[p] + 1}, {h[0]}, {h[1]}}},")
    w("};")
    w("")
    w("// Where an overworld map lands on its planet: pixel = (base + tile * step) / 256, cell = pixel / 8.")
    w("struct StarNavMapPlace { u16 map; u8 planet; s32 baseX; s32 baseY; u16 step; };")
    w("static const struct StarNavMapPlace sStarNavMapPlaces[STARNAV_MAP_COUNT] =")
    w("{")
    for (m, p, bx, by, inv) in map_xf:
        w(f"    {{{m}, {p}, {bx}, {by}, {inv}}},")
    w("};")
    w("")
    w("#endif // GUARD_DATA_REGION_MAP_STARNAV_MAP_H")
    HEADER.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()

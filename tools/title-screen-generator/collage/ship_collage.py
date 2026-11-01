"""Ship the approved title-screen collage (round 2, v6: no creatures, back-row depth, foreground ridge; Kael's cape
recoloured tan by hand in final/kael.png) into ../../../game. Owner picked it on 2026-11-01.

    python3 ship_collage.py [PREVIEW_DIR]

Writes, all under game/:
  graphics/title_screen/collage/<name>.png/.pal   one figure each: 4bpp tile strip (8 px wide, tiles in OAM order) and
                                                  its own 16-colour palette (index 0 transparent)
  graphics/title_screen/rayquaza.png/.bin         BG0 is now the foreground ridge only (the Exogorth is gone); same file
                                                  names so the build rules and title_screen.c loads stay as they are
  src/data/title_screen_collage.h                 graphics, subsprite tables (one Sprite per figure, its OAM pieces as
                                                  subsprites) and the slide-in table, included by src/title_screen.c

Hardware layout the C code relies on:
  - figures: OBJ priority 2, so the logo (BG2, priority 1) and the ridge (BG0, priority 1) cover them and they cover
    the clouds (BG1, priority 2). OBJ palettes 1-7 (title_screen.c reserves 0-8; 0 is the version banner).
  - each figure is cut to what is visible at rest: pixels off screen, or under the ridge for every x the figure passes
    while sliding in, are dropped. The rest is covered with the fewest OBJ tiles + pieces (cost = tiles + 3 per piece).
  - BG0 (ridge) uses palette 14 indices 9 (body) and 4 (lit lip) of rayquaza_and_clouds.pal; everything else is tile 0
    (blank), so the clouds blend over the backdrop exactly like the mockup.

Then it renders the screen back from the written game files (not from the mockup) to PREVIEW_DIR: final.png (1x, 3x) and
final_slide_in.gif, and runs the shared palette gate (tools/PALETTES.md).
"""
import os, sys, struct
from functools import lru_cache
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)   # this folder's round2.py, not the logo round2.py one level up
import gba_title as g
import compose as C, blocking
import importlib.util
_spec = importlib.util.spec_from_file_location("collage_round2", os.path.join(HERE, "round2.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)

GAME = os.path.normpath(g.GAME)
TS = g.TS
COLLAGE_DIR = os.path.join(TS, "collage")
HEADER = os.path.join(GAME, "src", "data", "title_screen_collage.h")
SLIDE_DIST, SLIDE_FRAMES, DELAY_PER_ROW = 90, 32, 8   # mockup gif: 16 steps at 2 game frames, rows 4 steps apart
PIECE_COST = 3
OBJ_PRIORITY = 2
FIRST_PAL = 1
SIZES = {(8, 8): "8x8", (16, 16): "16x16", (32, 32): "32x32", (64, 64): "64x64", (16, 8): "16x8", (32, 8): "32x8",
         (32, 16): "32x16", (64, 32): "64x32", (8, 16): "8x16", (8, 32): "8x32", (16, 32): "16x32", (32, 64): "32x64"}
BG14 = g.read_jasc(os.path.join(TS, "rayquaza_and_clouds.pal"))


def final_cast():
    cs = R.cast([])
    for c in cs:
        if c["name"] == "kael":
            c["src"] = os.path.join(HERE, "final", "kael.png")   # blue cape -> tan (owner, 2026-11-01)
    return cs


def slide_table():
    out = []
    for k in range(SLIDE_FRAMES + 1):
        t = k / SLIDE_FRAMES
        out.append(int((1 - t) ** 3 * SLIDE_DIST))
    return out   # out[k] = distance still to travel after k frames


def visible_mask(s, x, y, side):
    """Pixels to keep: on screen at rest, and above the ridge somewhere along the slide path."""
    px = s.load()
    keep = Image.new("1", s.size, 0)
    kp = keep.load()
    for yy in range(s.size[1]):
        for xx in range(s.size[0]):
            if not px[xx, yy][3]:
                continue
            X, Y = x + xx, y + yy
            if not (0 <= X < 240 and 0 <= Y < 160):
                continue
            path = range(X - SLIDE_DIST, X + 1) if side == "L" else range(X, X + SLIDE_DIST + 1)
            if any(Y < R.ridge_y(min(239, max(0, p))) for p in path):
                kp[xx, yy] = 1
    return keep


def cover(mask_tiles, wt, ht):
    @lru_cache(None)
    def best(x, y, w, h):
        if not any((tx, ty) in mask_tiles for tx in range(x, x + w) for ty in range(y, y + h)):
            return (0, ())
        opts = []
        if (w * 8, h * 8) in SIZES:
            opts.append((w * h + PIECE_COST, ((x, y, w, h),)))
        if w > 1:
            a, b = best(x, y, w // 2, h), best(x + w // 2, y, w // 2, h)
            opts.append((a[0] + b[0], a[1] + b[1]))
        if h > 1:
            a, b = best(x, y, w, h // 2), best(x, y + h // 2, w, h // 2)
            opts.append((a[0] + b[0], a[1] + b[1]))
        return min(opts)
    pieces = ()
    for cy in range(0, ht, 8):
        for cx in range(0, wt, 8):
            pieces += best(cx, cy, 8, 8)[1]
    return pieces


def write_jasc(path, cols):
    with open(path, "w", newline="\r\n") as f:
        f.write("JASC-PAL\n0100\n%d\n" % len(cols))
        for c in cols:
            f.write("%d %d %d\n" % tuple(c))


def ship_figure(c, s, x, y, slot):
    keep = visible_mask(s, x, y, c["side"])
    sp, kp = s.load(), keep.load()
    cols = {}
    for yy in range(s.size[1]):
        for xx in range(s.size[0]):
            if kp[xx, yy]:
                q = g.gba(sp[xx, yy])
                cols[q] = cols.get(q, 0) + 1
    order = sorted(cols, key=lambda q: -cols[q])
    assert len(order) <= 15, f"{c['name']}: {len(order)} colours"
    pal = [(248, 0, 248)] + order + [(0, 0, 0)] * (15 - len(order))
    idx = {q: i + 1 for i, q in enumerate(order)}
    wt, ht = (s.size[0] + 7) // 8, (s.size[1] + 7) // 8
    occupied = frozenset((xx // 8, yy // 8) for yy in range(s.size[1]) for xx in range(s.size[0]) if kp[xx, yy])
    pieces = cover(occupied, wt, ht)
    tiles, subs = [], []
    for tx, ty, w, h in pieces:
        subs.append((tx * 8, ty * 8, SIZES[(w * 8, h * 8)], len(tiles)))
        for r in range(h):
            for q in range(w):
                tile = []
                for py in range(8):
                    row = []
                    for pxx in range(8):
                        X, Y = (tx + q) * 8 + pxx, (ty + r) * 8 + py
                        inside = X < s.size[0] and Y < s.size[1] and kp[X, Y]
                        row.append(idx[g.gba(sp[X, Y])] if inside else 0)
                    tile.append(row)
                tiles.append(tile)
    strip = Image.new("P", (8, 8 * len(tiles)), 0)
    flat = []
    for col in pal:
        flat += list(col)
    strip.putpalette(flat)
    stp = strip.load()
    for i, t in enumerate(tiles):
        for py in range(8):
            for pxx in range(8):
                stp[pxx, i * 8 + py] = t[py][pxx]
    strip.save(os.path.join(COLLAGE_DIR, c["name"] + ".png"))
    write_jasc(os.path.join(COLLAGE_DIR, c["name"] + ".pal"), pal)
    return dict(name=c["name"], x=x, y=y, side=c["side"], z=c["z"], slot=slot, tiles=len(tiles), subs=subs, colours=len(order))


def ship_ridge():
    """BG0: the ridge, palette 14. Tile 0 is blank; every map entry without ridge is 0."""
    body, lip = BG14.index(R.RIDGE), BG14.index(R.RIDGE_LIT)
    full = [[0] * 256 for _ in range(256)]
    for x in range(240):
        top = R.ridge_y(x)
        for y in range(top, 160):
            full[y][x] = lip if y == top else body
    tl, seen, tmap = [tuple(tuple([0] * 8) for _ in range(8))], {}, []
    seen[tl[0]] = 0
    for ty in range(32):
        for tx in range(32):
            t = tuple(tuple(full[ty * 8 + yy][tx * 8:tx * 8 + 8]) for yy in range(8))
            if t == tl[0]:
                tmap.append(0)
                continue
            if t not in seen:
                seen[t] = len(tl); tl.append(t)
            tmap.append(seen[t] | (14 << 12))
    cols = 16
    rows = (len(tl) + cols - 1) // cols
    out = Image.new("P", (cols * 8, rows * 8), 0)
    flat = []
    for c in BG14:
        flat += list(c)
    out.putpalette(flat)
    op = out.load()
    for i, t in enumerate(tl):
        for yy in range(8):
            for xx in range(8):
                op[(i % cols) * 8 + xx, (i // cols) * 8 + yy] = t[yy][xx]
    out.save(os.path.join(TS, "rayquaza.png"))
    open(os.path.join(TS, "rayquaza.bin"), "wb").write(struct.pack("<1024H", *tmap))
    return len(tl)


def write_header(figs, table):
    L = ["// Title-screen character collage. Generated by tools/title-screen-generator/collage/ship_collage.py:",
         "// edit the art or the layout there and re-run it, not this file.",
         "// One Sprite per figure; its OAM pieces are subsprites (offsets from the figure's top-left at rest).",
         "",
         "#define COLLAGE_FIGURE_COUNT %d" % len(figs),
         "#define COLLAGE_SLIDE_FRAMES %d" % SLIDE_FRAMES,
         "#define COLLAGE_OBJ_PRIORITY %d" % OBJ_PRIORITY,
         ""]
    for f in figs:
        n = f["name"]
        L.append('static const u32 sCollageGfx_%s[] = INCGFX_U32("graphics/title_screen/collage/%s.png", ".4bpp.lz");' % (n, n))
        L.append('static const u16 sCollagePal_%s[] = INCGFX_U16("graphics/title_screen/collage/%s.pal", ".gbapal");' % (n, n))
    L.append("")
    for f in figs:
        L.append("static const struct Subsprite sCollageSubsprites_%s[] =" % f["name"])
        L.append("{")
        for sx, sy, dim, off in f["subs"]:
            L.append("    { .x = %3d, .y = %3d, .shape = SPRITE_SHAPE(%s), .size = SPRITE_SIZE(%s), .tileOffset = %3d, .priority = %d },"
                     % (sx, sy, dim, dim, off, OBJ_PRIORITY))
        L.append("};")
        L.append("static const struct SubspriteTable sCollageSubspriteTable_%s[] = { { ARRAY_COUNT(sCollageSubsprites_%s), sCollageSubsprites_%s } };"
                 % (f["name"], f["name"], f["name"]))
        L.append("")
    L.append("// Distance (px) a figure still has to slide after k frames: ease-out cubic over COLLAGE_SLIDE_FRAMES.")
    L.append("static const u8 sCollageSlide[COLLAGE_SLIDE_FRAMES + 1] = { %s };" % ", ".join(map(str, table)))
    L.append("")
    L.append("struct CollageFigure")
    L.append("{")
    L.append("    struct CompressedSpriteSheet sheet;")
    L.append("    const u16 *pal;")
    L.append("    const struct SubspriteTable *subsprites;")
    L.append("    s16 x, y;      // top-left at rest (screen px)")
    L.append("    s8 dir;        // -1 slides in from the left, 1 from the right")
    L.append("    u8 delay;      // frames before it starts (back row first)")
    L.append("    u8 subpriority;// lower draws on top (front row)")
    L.append("    u8 palSlot;    // OBJ palette")
    L.append("};")
    L.append("")
    L.append("// Needs sOamData_CollageFigure and SpriteCB_CollageFigure, declared in title_screen.c before this file.")
    L.append("static const struct SpriteTemplate sCollageSpriteTemplates[COLLAGE_FIGURE_COUNT] =")
    L.append("{")
    for i, f in enumerate(figs):
        L.append("    { .tileTag = TAG_COLLAGE_FIRST + %d, .paletteTag = TAG_NONE, .oam = &sOamData_CollageFigure, .anims = gDummySpriteAnimTable,"
                 " .images = NULL, .affineAnims = gDummySpriteAffineAnimTable, .callback = SpriteCB_CollageFigure }, // %s" % (i, f["name"]))
    L.append("};")
    L.append("")
    L.append("static const struct CollageFigure sCollageFigures[COLLAGE_FIGURE_COUNT] =")
    L.append("{")
    for i, f in enumerate(figs):
        L.append("    { { sCollageGfx_%s, %d * TILE_SIZE_4BPP, TAG_COLLAGE_FIRST + %d }, sCollagePal_%s, sCollageSubspriteTable_%s, %d, %d, %d, %d, %d, %d },"
                 % (f["name"], f["tiles"], i, f["name"], f["name"], f["x"], f["y"], -1 if f["side"] == "L" else 1,
                    (f["z"] - 1) * DELAY_PER_ROW, 8 - f["z"], f["slot"]))
    L.append("};")
    L.append("")
    open(HEADER, "w").write("\n".join(L))


# ------------------------------------------------------------------ preview from the written game files

def read_strip(name):
    im = Image.open(os.path.join(COLLAGE_DIR, name + ".png"))
    pal = g.read_jasc(os.path.join(COLLAGE_DIR, name + ".pal"))
    p = im.load()
    tiles = []
    for i in range(im.size[1] // 8):
        tiles.append([[p[x, i * 8 + y] for x in range(8)] for y in range(8)])
    return tiles, pal


def figure_image(f):
    tiles, pal = read_strip(f["name"])
    W = max(sx + int(d.split("x")[0]) for sx, sy, d, o in f["subs"])
    H = max(sy + int(d.split("x")[1]) for sx, sy, d, o in f["subs"])
    im = Image.new("RGBA", (W, H))
    px = im.load()
    for sx, sy, d, off in f["subs"]:
        w, h = (int(v) // 8 for v in d.split("x"))
        for r in range(h):
            for q in range(w):
                t = tiles[off + r * w + q]
                for yy in range(8):
                    for xx in range(8):
                        if t[yy][xx]:
                            px[sx + q * 8 + xx, sy + r * 8 + yy] = g.gba(pal[t[yy][xx]]) + (255,)
    return im


def game_screen(figs, offsets=None):
    lp = g.read_jasc(os.path.join(TS, "pokemon_logo.pal"))
    bgpal = (lp[:224] + [(0, 0, 0)] * 224)[:224] + BG14
    bgpal += [(0, 0, 0)] * (256 - len(bgpal))
    bg0 = g.text_bg(os.path.join(TS, "rayquaza.png"), os.path.join(TS, "rayquaza.bin"), bgpal)
    bg1 = g.text_bg(os.path.join(TS, "clouds.png"), os.path.join(TS, "clouds.bin"), bgpal)
    logo = g.place(g.affine_bg(os.path.join(TS, "pokemon_logo.png"), os.path.join(TS, "pokemon_logo.bin"), bgpal), g.LOGO_X, g.LOGO_Y)
    banner = g.sprite_rgba(Image.open(os.path.join(TS, "emerald_version.png")))
    ps, cr = g.press_start_strips(Image.open(os.path.join(TS, "press_start.png")))
    # priority order, back to front: backdrop, BG1 clouds (blended over BG0/backdrop), OBJ pri 2 figures,
    # BG0 ridge + BG2 logo (pri 1), OBJ pri 0 banner and text
    img = g.compose(bgpal[0], None, bg1, None, []).convert("RGBA")
    for f in sorted(figs, key=lambda f: -f["subpri"]):
        s = figure_image(f)
        tmp = Image.new("RGBA", (240, 160))
        tmp.paste(s, (f["x"] + (offsets or {}).get(f["name"], 0), f["y"]), s)
        img.alpha_composite(tmp)
    img.alpha_composite(bg0.crop((0, 0, 240, 160)))
    img.alpha_composite(logo)
    for im, xy in [(banner, g.BANNER_XY), (ps, (48, g.PRESS_START_Y)), (cr, (48, g.COPYRIGHT_Y))]:
        img.paste(im, xy, im)
    return img


def gate():
    sys.path.insert(0, os.path.join(HERE, "..", "..", "palette-enforcer"))
    from gba_palette import check
    reps = [check.check_png(os.path.join(TS, "rayquaza.png"))]
    for f in sorted(os.listdir(COLLAGE_DIR)):
        p = os.path.join(COLLAGE_DIR, f)
        reps.append(check.check_png(p) if f.endswith(".png") else check.check_pal(p))
    bad = [r for r in reps if not r.ok]
    for r in bad:
        print("\n".join(r.lines()))
    if bad:
        raise SystemExit("palette gate failed (tools/PALETTES.md)")
    print("palette gate: %d files OK" % len(reps))


def main():
    prev = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
    os.makedirs(prev, exist_ok=True)
    os.makedirs(COLLAGE_DIR, exist_ok=True)
    R.LAYERS = blocking.layers()
    _, layers = R.build(final_cast(), True, False, use_ridge=True)
    figs = []
    for i, (c, s, x, y) in enumerate(layers):
        f = ship_figure(c, s, x, y, FIRST_PAL + i)
        f["subpri"] = 8 - f["z"]
        figs.append(f)
        print("%-8s at (%4d,%4d) %2d colours, %3d tiles, %2d pieces" % (f["name"], x, y, f["colours"], f["tiles"], len(f["subs"])))
    print("figures: %d tiles, %d OAM entries" % (sum(f["tiles"] for f in figs), sum(len(f["subs"]) for f in figs)))
    print("ridge: %d BG0 tiles" % ship_ridge())
    table = slide_table()
    write_header(figs, table)

    img = game_screen(figs)
    img.convert("RGB").save(os.path.join(prev, "final_1x.png"))
    img.convert("RGB").resize((720, 480), Image.NEAREST).save(os.path.join(prev, "final.png"))
    frames = []
    total = max((f["z"] - 1) * DELAY_PER_ROW for f in figs) + SLIDE_FRAMES
    for fr in range(0, total + 1, 2):   # every 2nd game frame, 30 fps gif = real speed
        offs = {}
        for f in figs:
            k = min(SLIDE_FRAMES, max(0, fr - (f["z"] - 1) * DELAY_PER_ROW))
            offs[f["name"]] = table[k] * (-1 if f["side"] == "L" else 1)
        frames.append(game_screen(figs, offs).convert("RGB").resize((480, 320), Image.NEAREST))
    frames[0].save(os.path.join(prev, "final_slide_in.gif"), save_all=True,
                   append_images=frames[1:] + [frames[-1]] * 45, duration=33, loop=0)
    gate()


if __name__ == "__main__":
    main()

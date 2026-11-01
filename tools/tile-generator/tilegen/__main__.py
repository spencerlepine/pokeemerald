"""tile-generator CLI.

    python -m tilegen render-map  <LayoutName|LAYOUT_ID> out.png [--zoom N]
    python -m tilegen render-tileset <gTileset_X> out.png [--with gTileset_Y] [--cols N]
    python -m tilegen list-layouts [filter]
    python -m tilegen list-tilesets
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from . import gba


def _zoom(im: Image.Image, z: int) -> Image.Image:
    return im if z == 1 else im.resize((im.width * z, im.height * z), Image.NEAREST)


def cmd_render_map(a):
    L = gba.layouts()
    lay = L[a.layout]
    im = gba.render_layout(lay)
    _zoom(im, a.zoom).save(a.out)
    print(f"{a.out}: {lay.name} {lay.width}x{lay.height} metatiles, {lay.primary} + {lay.secondary}")


def cmd_render_tileset(a):
    ts = gba.load_tileset_by_header(a.tileset)
    if ts.secondary:
        prim = gba.load_tileset_by_header(a.with_ or "gTileset_General")
        pair = gba.TilesetPair(prim, ts)
        which = "secondary"
    else:
        sec = gba.load_tileset_by_header(a.with_ or ("gTileset_Petalburg" if ts.name == "general" else "gTileset_GenericBuilding"))
        pair = gba.TilesetPair(ts, sec)
        which = "primary"
    im = pair.render_metatile_sheet(which, cols=a.cols, backdrop=(255, 0, 255))
    _zoom(im, a.zoom).save(a.out)
    print(f"{a.out}: {ts.name} {ts.n_metatiles} metatiles, {len(ts.tiles)} tiles")


def cmd_recolour(a):
    from . import recolour, review
    rec = recolour.Recipe.load(a.recipe)
    L = gba.layouts()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    panels = []
    pairs: dict[tuple[str, str], tuple[gba.TilesetPair, gba.TilesetPair]] = {}
    for name in a.layouts:
        lay = L[name]
        key = (lay.primary, lay.secondary)
        if key not in pairs:
            van = gba.TilesetPair(gba.load_tileset_by_header(lay.primary), gba.load_tileset_by_header(lay.secondary))
            pairs[key] = (van, recolour.recolour_pair(van, rec, log))
        van, new = pairs[key]
        panels.append(review.side_by_side([(f"{lay.name} vanilla", gba.render_layout(lay, pair=van)),
                                           (f"{lay.name} {rec.name}", gba.render_layout(lay, pair=new))], zoom_factor=a.zoom))
    sw_rows = []
    for (p, s), (van, new) in pairs.items():
        for ts_v, ts_n, rng in ((van.primary, new.primary, range(0, 6)), (van.secondary, new.secondary, range(6, 13))):
            for b in rng:
                if any(c != ts_v.palettes[b][0] for c in ts_v.palettes[b]):
                    sw_rows.append((f"{ts_v.name}:{b}", ts_v.palettes[b], ts_n.palettes[b]))
            recolour.write_palettes(ts_n, out / "palettes" / ts_n.name)
    review.stack(panels + [review.swatches(sw_rows)]).save(out / f"review_{rec.name}.png")
    (out / f"log_{rec.name}.txt").write_text("\n".join(log) + "\n")
    print(f"{out}/review_{rec.name}.png, palettes under {out}/palettes/<tileset>/NN.pal")


def _build_pair(rec, primary: str, secondary: str):
    """Recolour both tilesets of a pair and apply the recipe's `retexture:` ops to them."""
    from . import recolour, edit, ground
    import numpy as np
    van = gba.TilesetPair(gba.load_tileset_by_header(primary), gba.load_tileset_by_header(secondary))
    new = gba.TilesetPair(edit.copy_tileset(recolour.recolour_tileset(van.primary, rec)),
                          edit.copy_tileset(recolour.recolour_tileset(van.secondary, rec)))
    for op in rec.retexture:
        ts = new.primary if op.get("tileset", "primary") == "primary" else new.secondary
        if op["op"] == "speckle":
            t = op["tones"]
            A = ground.speckle(8, t["base"], t.get("light"), t.get("dark"), seed=op.get("seed", 0) * 2,
                               light_blobs=op.get("light_blobs", 2), dark_dots=op.get("dark_dots", 4), blob=op.get("blob", 2))
            B = ground.speckle(8, t["base"], t.get("light"), t.get("dark"), seed=op.get("seed", 0) * 2 + 1,
                               light_blobs=op.get("light_blobs", 2), dark_dots=op.get("dark_dots", 4), blob=op.get("blob", 2))
            for mid in op["metatiles"]:
                edit.set_metatile_layer(ts, mid, op.get("layer", 0), np.block([[A, B], [B, A]]))
        elif op["op"] == "pattern":           # write a tone-level pattern into tile ids (all metatiles using them follow)
            lvl = ground.PATTERNS[op["pattern"]](**op.get("args", {}))
            lut = np.array(op["tones"], np.uint8)
            img = lut[np.minimum(lvl, len(lut) - 1)]
            base = gba.NUM_TILES_IN_PRIMARY if ts.secondary else 0
            for r, row in enumerate(op["tiles"]):
                for c, tid in enumerate(row):
                    ts.tiles[tid - base] = img[r * 8:(r + 1) * 8, c * 8:(c + 1) * 8]
        elif op["op"] == "rebank":
            mids = list(op.get("metatiles", []))
            if "metatiles_with_tiles" in op:
                mids += edit.metatiles_using_tiles(ts, *op["metatiles_with_tiles"])
            alloc = edit.free_tile_ids(ts, op.get("free_below", gba.NUM_TILES_IN_PRIMARY))
            n = edit.rebank_metatiles(ts, sorted(set(mids)), op["from"], op["to"], op.get("map", {}), alloc)
            if n == 0:
                raise SystemExit(f"rebank op matched nothing: {op}")
        else:
            raise SystemExit(f"unknown retexture op {op['op']}")
    return van, new


def cmd_build(a):
    """recipe -> game-format tileset pair under out/<recipe>/, the palette gate, and a review sheet."""
    from . import recolour, review, pack
    rec = recolour.Recipe.load(a.recipe)
    L = gba.layouts()
    lay = L[a.layouts[0]]
    van, new = _build_pair(rec, lay.primary, lay.secondary)
    out = Path(a.out) / rec.name
    ok_all = True
    for ts in (new.primary, new.secondary):
        d = pack.write_tileset(ts, out / ts.name)
        ok, lines = pack.check_tileset(ts, d)
        ok_all &= ok
        (d / "check.txt").write_text("\n".join(lines) + "\n")
        print(f"{'OK  ' if ok else 'FAIL'} {d}  ({len(ts.tiles)} tiles, {ts.n_metatiles} metatiles)")
    panels = [review.side_by_side([(f"{L[n].name} vanilla", gba.render_layout(L[n], pair=van)),
                                   (f"{L[n].name} {rec.name}", gba.render_layout(L[n].edited(rec.layout_edits.get(n, {})), pair=new))],
                                  zoom_factor=a.zoom)
              for n in a.layouts if (L[n].primary, L[n].secondary) == (lay.primary, lay.secondary)]
    review.stack(panels).save(out / "review.png")
    print(f"review: {out / 'review.png'}")
    if not ok_all:
        raise SystemExit("palette gate failed; see check.txt")


def cmd_install(a):
    """Copy a built pair into game/ (after the gate). Use --revert to put the vanilla files back (git)."""
    from . import recolour, pack
    import subprocess
    rec = recolour.Recipe.load(a.recipe)
    L = gba.layouts(); lay = L[a.layout]
    van, new = _build_pair(rec, lay.primary, lay.secondary)
    out = Path(a.out) / rec.name
    for ts in (new.primary, new.secondary):
        d = pack.write_tileset(ts, out / ts.name)
        pack.install_tileset(ts, d)
        print(f"installed {ts.path.relative_to(gba.game_dir())}")


def cmd_anim(a):
    """Stage 6: play a layout's tileset animations for vanilla and each recipe, as one GIF grid."""
    from . import anim, recolour, review
    L = gba.layouts(); lay = L[a.layout]
    crop = tuple(a.crop) if a.crop else None
    cols = []
    van = None
    for r in a.recipes:
        rec = recolour.Recipe.load(r)
        v, new = _build_pair(rec, lay.primary, lay.secondary)
        van = van or v
        cols.append((rec.name, anim.render_frames(lay, new, a.steps, crop)))
    cols.insert(0, ("vanilla", anim.render_frames(lay, van or gba.TilesetPair(gba.load_tileset_by_header(lay.primary),
                                                 gba.load_tileset_by_header(lay.secondary)), a.steps, crop)))
    rows = [cols[i:i + a.cols] for i in range(0, len(cols), a.cols)]
    frames = [review.stack([review.side_by_side([(n, f[i]) for n, f in row], zoom_factor=a.zoom) for row in rows])
              for i in range(a.steps)]
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    anim.save_gif(frames, out, zoom=1)
    frames[0].save(out.with_suffix(".png"))
    print(f"{out}  ({a.steps} steps, {len(cols)} panels)")


def cmd_list_layouts(a):
    for name, l in sorted(gba.layouts().items()):
        if name.startswith("LAYOUT_"):
            continue
        if a.filter and a.filter.lower() not in name.lower():
            continue
        print(f"{name:50s} {l.width:3d}x{l.height:<3d} {l.primary} + {l.secondary}")


def cmd_list_tilesets(a):
    for h, p in sorted(gba.tileset_folders().items()):
        print(f"{h:40s} {p.relative_to(gba.game_dir())}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="tilegen")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("render-map"); s.add_argument("layout"); s.add_argument("out"); s.add_argument("--zoom", type=int, default=1)
    s.set_defaults(fn=cmd_render_map)
    s = sub.add_parser("render-tileset"); s.add_argument("tileset"); s.add_argument("out")
    s.add_argument("--with", dest="with_"); s.add_argument("--cols", type=int, default=16); s.add_argument("--zoom", type=int, default=1)
    s.set_defaults(fn=cmd_render_tileset)
    s = sub.add_parser("recolour", help="stage 1: re-theme a tileset pair by palette, render vanilla vs new")
    s.add_argument("recipe"); s.add_argument("--layouts", nargs="+", default=["LittlerootTown_Layout", "Route101_Layout"])
    s.add_argument("--out", default="out/recolour"); s.add_argument("--zoom", type=int, default=2)
    s.set_defaults(fn=cmd_recolour)
    s = sub.add_parser("build", help="recipe -> game-format tileset pair + palette gate + review")
    s.add_argument("recipe"); s.add_argument("--layouts", nargs="+", default=["LittlerootTown_Layout", "Route101_Layout"])
    s.add_argument("--out", default="out"); s.add_argument("--zoom", type=int, default=2); s.set_defaults(fn=cmd_build)
    s = sub.add_parser("install", help="build and copy the pair a layout uses into game/ (gate enforced)")
    s.add_argument("recipe"); s.add_argument("--layout", default="LittlerootTown_Layout"); s.add_argument("--out", default="out")
    s.set_defaults(fn=cmd_install)
    s = sub.add_parser("anim", help="stage 6: GIF of a layout's tileset animations, vanilla and per recipe")
    s.add_argument("layout"); s.add_argument("out"); s.add_argument("recipes", nargs="*")
    s.add_argument("--crop", type=int, nargs=4, metavar=("L", "T", "R", "B")); s.add_argument("--steps", type=int, default=8)
    s.add_argument("--cols", type=int, default=4); s.add_argument("--zoom", type=int, default=1); s.set_defaults(fn=cmd_anim)
    s = sub.add_parser("list-layouts"); s.add_argument("filter", nargs="?"); s.set_defaults(fn=cmd_list_layouts)
    s = sub.add_parser("list-tilesets"); s.set_defaults(fn=cmd_list_tilesets)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()

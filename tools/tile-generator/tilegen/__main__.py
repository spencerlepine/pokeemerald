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
    s = sub.add_parser("list-layouts"); s.add_argument("filter", nargs="?"); s.set_defaults(fn=cmd_list_layouts)
    s = sub.add_parser("list-tilesets"); s.set_defaults(fn=cmd_list_tilesets)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()

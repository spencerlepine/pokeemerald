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
    s = sub.add_parser("list-layouts"); s.add_argument("filter", nargs="?"); s.set_defaults(fn=cmd_list_layouts)
    s = sub.add_parser("list-tilesets"); s.set_defaults(fn=cmd_list_tilesets)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()

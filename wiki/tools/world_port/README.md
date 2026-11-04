# world_port

Ports the wiki world (`wiki/world/`) into `../game`: terrain, buildings and props, warps, connections,
people, signs and wild tables. Work in progress; nothing is installed yet.

The modules:

- `base.py`: paths, and the vanilla snapshot (commit `c663bddf`) every pass reads from (`.base/`, not committed).
- `model.py`: the areas and how each is ported (`vanilla`, `hybrid`, `redraw`, new).
- `terrain.py`: the metatile, collision and elevation of every cell.
- `pieces.py`: buildings and props as solid cells drawn with their greybox or kit render.
- `tiles.py`: the per-area secondary tileset that holds the new metatiles (placeholders included).
- `pins.py`: what a tileset copy must keep in place (labelled metatiles, animated tiles).
- `warps.py`: warps and map connections.

Art stays pending in the wiki: a placeholder or greybox tile goes in as a real tile in its own slot, so it can
be redrawn later without touching the maps.

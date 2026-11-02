# World blockout: every area laid out before the art

The owner's plan (2026-11-02): build the whole world conceptually first, then fill in the art.

1. **Blockout (now).** Every town, route, dungeon, interior and new planet is laid out on a cell grid
   with placeholder tiles: grey terrain, grey blocks for buildings and props sized to the cell, pink
   placeholders for people, signs and other sprites. Nothing is drawn.
2. **Dumb shapes and colours (later).** Simple shapes and flat planet colours on the same layouts, to
   get the feel of each place.
3. **Art (last).** Real pixel art per piece, tracked by the same rows.

## Files

- `<planet>/<area>.yaml`: one area. The format is documented at the top of
  [`tools/blockout/blockout/area.py`](../../tools/blockout/blockout/area.py).
- `<planet>/<area>.png`: its review sheet (vanilla map it replaces | blockout | numbered legend).
- `INDEX.csv`: every area and every placed piece. This is the to-do list. Each piece links to its
  concept in [`../mapping/world_art.csv`](../mapping/world_art.csv) by `art` id; `art_known = NEW` means
  the piece needs a new concept row.

Status: an area's `status` is `TODO`, `BLOCKOUT` (laid out, waiting for the owner) or `APPROVED`.
Every piece's art is `TODO` until phase 2.

## Terrain legend (one character per cell)

| Char | Meaning |
|---|---|
| `.` | open ground |
| `:` | path, street or plaza (the signal the player follows) |
| `"` | wild encounter ground (tall grass, scrub, ash, ferns) |
| `~` | water (surf) |
| `=` | raised walkway: bridge, tree platform, catwalk |
| `H` | ladder or stairs between levels |
| `T` | edge nature that blocks (trees, rocks) |
| `#` | cliff, wall or rock face |
| `v ^ < >` | ledge, jump down in that direction |
| `_` / `\|` | indoor floor / indoor wall |
| `x` | blocked, not yet decided (left over from a vanilla import) |

## Rules

- An area that replaces a vanilla map keeps its size, its exits and its number of doors, so it can be
  built into that map later. A new area (`replaces: new`) is free.
- Signal and noise (`../bible/WORLD_ART.md`): paths stay clear; props sit at edges, corners and dead space.
- `python3 -m blockout check` must report no problems before an area is sent for review.

## Pilots (2026-11-02)

| Area | Planet | Replaces | Status |
|---|---|---|---|
| [MOS PELGO](tatooine/mos-pelgo.png) | Tatooine | Littleroot | BLOCKOUT |
| [BRIGHT TREE](endor/bright-tree.png) | Endor | Fortree | BLOCKOUT |

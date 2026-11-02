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

- **Each planet is its own map (owner, 2026-11-02).** Walkable borders between planets are cut; ships
  link them (hangars, docking bays, shuttles). `blockout layout <PLANET>` fits a planet's towns, routes and
  landmarks together from their exits and writes each area's `pos`; it reports exits with no way back,
  loops that do not close and overlaps.
- Towns can be bigger and any shape (owner, 2026-11-02): GBA storage is no longer the limit, but walks
  must stay short. Optional side areas are welcome; they use the characters already in the wiki.
- `replaces` names the vanilla map an area is built into (its doors, trainers and scripts come from
  there). The size, shape and exits can change.
- `~` is each planet's surf medium: water on most planets, the salt lake on Tatooine.
- Signal and noise (`../bible/WORLD_ART.md`): paths stay clear; props sit at edges, corners and dead space.
- `python3 -m blockout check` must report no problems before an area is sent for review.

## How each area was made

- Every vanilla map was imported (`blockout import-all`) as a `TODO` starting point: terrain from its
  collision (`T` where vanilla is green, `#` otherwise), its trainers (names from `trainers.csv`), items,
  signs, doors and connections.
- **Towns** are redrawn from scratch: new shapes, more buildings, Star Wars landmarks.
- **Routes and caves** keep vanilla's walkable shape (it is already well paced), with vanilla houses turned
  into buildings, cross-planet edges cut, and planet props placed at the edges of open ground without
  blocking any path.
- **New optional areas** (`kind: landmark`, `replaces: new`) hang off a route by a side exit.

## Progress

| Planet | Overview | Laid out |
|---|---|---|
| Tatooine | [_planet.png](tatooine/_planet.png) | 7 towns, 11 routes, 11 caves, 2 new areas (Ben's hut, Jabba's palace). Interiors to do. |
| Endor | [_planet.png](endor/_planet.png) | Bright Tree (pilot) |

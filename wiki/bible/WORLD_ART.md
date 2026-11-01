# World art: new buildings, interiors, objects and nature per biome

**Source of truth:** [`../mapping/world_art.csv`](../mapping/world_art.csv), one row per concept (a building, an
interior kit, a world object or a piece of nature) that the Star Wars world adds on top of the re-coloured vanilla
tilesets. Concept and reference images live in [`../art/concept/<planet>/`](../art/concept), listed in the row.

## Why

The tile-generator recipes (see [`TILESET_INSTALL.md`](TILESET_INSTALL.md)) re-colour Emerald's tilesets per planet.
Ground and water are done that way. Everything else (trees, houses, props, rooms) still has Hoenn's shapes, so the
game still reads as Pokémon. This list is what gets **new shapes**: drawn in Emerald's style and inside its
constraints (16x16 metatiles, 3-4 tone ramps, top-down camera with south faces only, `tools/tile-generator/STYLE.md`),
but Star Wars in content. Layouts do not have to mirror Hoenn's; towns can grow new buildings.

## Signal and noise (layout rule for every row)

The player must always see where they can walk.

- **Signal** is open, calm ground: paths, plazas, floors. Keep it low-contrast and uncluttered.
- **Noise** is detail the player never has to walk through: trees, rocks, props, building fronts. It frames the
  signal and sits at its edges.
- `map_role` in the CSV says where each concept belongs:

| map_role | Meaning | Placement rule |
|---|---|---|
| `walkable` | Floor or ground the player walks on (interiors, walkways, tall-grass variants) | Low contrast, no bold shapes |
| `edge` | Blocks movement and outlines paths (trees, cliffs, walls, railings) | Line paths and map borders; never scatter in the middle of a path |
| `noise` | Small decor that blocks one or two cells (crates, vaporators, droids) | Corners, building sides and dead space only; never in a path or a doorway |
| `landmark` | A big unique piece (docking bay, temple, sandcrawler) | One or two per map, at a point the path leads to |

## Columns

| Column | Meaning |
|---|---|
| `concept_id` | `art:<planet>:<name>` |
| `planet`, `place` | Planet and town/route/area (`planet-wide` = the planet's shared kit; `SHARED` = every planet) |
| `category` | `building` (exterior), `interior` (room kit), `object` (prop), `nature` (flora, rock), `landmark` (unique set piece) |
| `description` | The brief: shape, materials, what makes it read as Star Wars at 16x16 |
| `footprint` | Size in 16x16 cells, width x height on screen |
| `vanilla_template` | The Emerald tiles it replaces or is built from (`(done)` = covered by a recipe already) |
| `sw_refs` | `starwars-db` entity ids used as reference (github.com/spencerlepine/starwars-db) |
| `reference_art` | Local reference images (`art/concept/...`): starwars-db databank images (`__db_`), web references (`__web_`, sources in `art/concept/SOURCES.csv`) and paintings generated in code where nothing usable was found (`__gen_`, made by `art/concept/_generated/paint.py`) |
| `concept_art` | Concept art made for this game (pixel mock-ups), once drawn |
| `concept_status` | `NEEDS_CONCEPT` / `REFERENCE_READY` (references collected) / `CONCEPT_READY` (concept approved) |
| `build_status` | `NOT_STARTED` / `IN_PROGRESS` / `ART_READY` / `DONE` (in `../game`) |

Reference images are film and franchise stills (Lucasfilm) kept only as private mood references for drawing; they are
never shipped in the game.

## Order of work

1. Collect references for every row (`REFERENCE_READY`). **Stop and review with the owner.**
2. Concept art per biome, owner approves.
3. Build per chunk, one category at a time, each with its own approvals. Nature and 2D props first; buildings and
   objects that need 3D thinking (domes, ships, walkers) go slowly with the owner's guidance.

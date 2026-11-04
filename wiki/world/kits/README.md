# World kits: placeholder tiles

Everything the world needs drawn that is not terrain (`../../mapping/terrain.csv`), a building or outdoor
object (`world_art.csv`, `buildings.csv`, `objects.csv`), a room shell (`rooms.csv`) or a room object
(`world_art.csv` `interior` rows). Found by scanning the game source (2026-11-04).

No art yet. Each row is a sheet of 16x16 placeholder tiles at its drawn size.

## Where things are

- [`../../mapping/world_kits.csv`](../../mapping/world_kits.csv): one row per item and planet
  (`kit:<category>:<planet>:<item>`), with `emerald` (the vanilla piece, behaviour or asset it replaces),
  `drawn` (cells, W x H), `hit_box` (codes as in [`../interiors/rooms/README.md`](../interiors/rooms/README.md)),
  `used_in` / `areas`, `status`, `tool`, `description`, `notes` and `placeholder`.
- `placeholders/<category>/<planet>/<item>.png`: one PNG per row, every cell the shared placeholder
  ([`../objects/16x16-placeholder.png`](../objects/16x16-placeholder.png)).
- `sheets/<category>.png`: every item of a category, labelled, at real size (`xN` = how many planets need
  one); `_review.png` is 2x.
- `make_placeholders.py`: writes both from the CSV. Re-run it after a size changes.

## Categories

| Category | What it is |
|---|---|
| `field-object` | Sprites the player pushes, cuts, smashes or picks up: boulders, cut growths, smash rocks, item pods, fruit plants, Puzzle House statues. |
| `mechanic` | Floor tiles with a rule: slide floors, cracking and crumbling floors, currents, waterfalls, bike slopes and rails, deep sand, hot springs, push tiles, teleport pads, steam-vent warps, maze warps, rotating gates, charged gates, one-way edges, puddles, drop holes, the Trial Spire timer. |
| `door` | Door animations per planet and building kind (home, Bacta Center, Supply Depot, arena, hangar, landmark, shop, inner doors). |
| `warp` | Ladders, moving walkways, cave mouths, dive doors, drop holes, lifts, sealed doors. |
| `tile-anim` | Animated tiles: water, shore, waterfalls, swaying plants, lava, steam, banners, fountains, lights, screens... |
| `underwater` | The dive routes' seafloor, sea plants, rock walls and surfacing light. |
| `battle-bg` | Battle backgrounds per planet and environment, the arena floors and the story ones. |
| `hideout` | Hideout entrances per planet, the hideout room, and the 120 hideout decorations (Star Wars names from `world_objects.csv`). |
| `location-ui` | The map name popup frame and the StarNAV galaxy map panel, per planet. |
| `field-effect` | Footprints, grass rustle, ash puffs, splashes, sinking sand, hot-spring steam, dive bubbles. |
| `weather` | Sun, shade, mist, ashfall, sandstorm, rain, snow, bubbles, per planet. |
| `border` | The tiles drawn past the map edge, per planet. |
| `field-prop` | Big props in story scenes: the star liner, the cargo hauler, the shuttle cab, the Cartel sub's shadow, the moving crates. |
| `interactive` | Interior tiles with a script: the wall StarNAV map, datacard shelves, bins, jars, survey terminals, blueprints, link results screens, shop shelves, game tables. |

## How rows are wired

`python3 -m blockout kits` (in `tools/blockout`) scans every area yaml and, for areas built into a vanilla
map, that map in `../game` (object events, metatile behaviours, warps, tilesets and their animations, map and
script weather, secret-base spots). It writes `used_in` / `areas` and lists scan hits with no row; `--add`
writes them. `blockout index` runs the same refresh. `blockout check` fails if a hit has no row, a row is used
by no area, or a placeholder is missing. `blockout todo --kind kit` (or `kit:door`, `kit:battle-bg`...) lists the rows.

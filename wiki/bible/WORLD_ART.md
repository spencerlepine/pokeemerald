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
| `backdrop` | A giant bigger than the screen (a Star Destroyer, a krayt skeleton) | Along a map edge, running off it; only part of it shows |

## Fill the tile (sizing rule for every row, owner 2026-11-02)

Emerald's art fills whole 16x16 cells, so the player can see the hit box: a building's edge, a statue's base
and a rock's outline sit on the cell line. Z-day's art was finer and more detailed; here it is not.

- **Footprint is the hit box.** Every piece has a `footprint` in whole cells (width x depth). Those cells are
  blocked; nothing else is. The drawn sprite may rise above the footprint (a 2-cell-deep house drawn 4 cells
  tall) and the player walks behind the upper rows, as the game layers sprites. Two pieces may overlap
  visually as long as their footprints do not touch where a walkway is needed.
- **Fill the cells.** Size a piece to fill its footprint edge to edge. No half-empty cells at the sides of a
  building or statue, no 10 px rock in a 16 px cell. A piece that does not fill a whole cell is a `noise`
  decoration drawn on a walkable tile, not a blocker.
- **Scale to the grid, not to life.** A fossil, a shipwreck or a statue is drawn at the size that looks right
  in cells (2x2, 3x2, 4x3), bigger or smaller than it would really be. Pick the footprint first, then draw.
- **Place first, draw later.** World building comes before art: every piece (statues, trees of many shapes
  and sizes, ships, shipwrecks, fossils, stalagmites, mangroves, bushes) gets a row with a footprint and a
  place on the map while it is still a wireframe; the art is drawn afterwards, one row at a time.

## Planet borders and surfaces (owner 2026-11-02)

Hoenn frames every map with the same tree line. That reads as Earth. Only Endor and Yavin 4 keep trees; every
other planet borders its maps with its own thing, and swaps the surfaces that do not fit. The table is code
(`PLANET_KIT` in `tools/tile-generator/tilegen/terrain.py`): the terrain renders apply it to every area,
vanilla layout or not, so a Tatooine route's tree line is already drawn as mesa cliffs and a Kashyyyk route's
as wroshyr trunks (placeholder until drawn). Net-new items get their own sheet, `wiki/world/greybox/sheets/sw-<planet>.png`,
and one row per edge and corner in `terrain.csv`.

| Planet | Border (replaces trees) | Surfaces swapped | Drawn with |
|---|---|---|---|
| Tatooine | Mesa and canyon cliffs | Sea becomes the Dune Sea, crossed with SAND SKIM (HM09, its own move; see NET_NEW_DESIGNS.md) | vanilla cliffs; `dune-sea` net-new |
| Kashyyyk | Wroshyr trunks and roots | Tree platforms become wroshyr platforms | `wroshyr`, `wroshyr-platform` net-new |
| Sullust | Lava-rock ridges | | vanilla cliffs, Sullust recipe |
| Mustafar | Obsidian cliffs | Lava by recipe | vanilla cliffs, lava recipe |
| Endor | Redwoods (trees kept) | | vanilla trees |
| Bespin | Platform edge over the cloud layer | Water becomes cloud | `cloud-edge`, `cloud` net-new |
| Jedha | Desert stone and ruin walls | | vanilla cliffs |
| Yavin 4 | Jungle (trees kept) and temple stone | | vanilla trees |
| Hoth | Ice cliffs and drifts | | vanilla cliffs, Hoth recipe |
| Dagobah | Gnarltree roots and mangroves | Sand and paths become mud | `gnarltree`, `mud` net-new |
| Kamino | Platform railings | Rock and grass become deck | `platform-rail`, `deck` net-new |
| Ilum | Ice and crystal walls | | vanilla cliffs, Hoth recipe |
| Felucia | Giant fungi | | `fungus` net-new |
| Grand Arena, Tython, Atollon, Mortis | Rock | | vanilla cliffs |
| Asteroid Field | Void edge | | `void-edge` net-new |
| Death Star | Durasteel walls | | `durasteel-wall` net-new |

## Large scenery (owner 2026-11-03)

Big static pieces placed through the world: crashed ships, toppled walkers, fossils, statues, ruins, broken
bridges and stairs. They are scenery only. None can be entered, none is a building, and none changes where the
player can walk. Every one is a `scenery` row in `world_art.csv` and a prop in its area's yaml.

- **They replace the border, they don't add walls.** A piece only sits on cells that are already blocked (the
  tree line, the cliff, the rock mass) or on water. So a wreck stands where the planet's border was, and the map
  edge reads as a place instead of a fence. The path never moves and `blockout check` stays green.
- **Hit box = footprint.** Whole cells, like a building. The drawn piece is taller than its hit box: the `drawn`
  column is the footprint plus the rows that rise above it. In the game those rows go in the metatiles' top
  layer, so the player walks behind them, as behind a tree top.
- **Roles.** `edge`: lines a border or closes a side way (broken bridge, fallen trunk, collapsed stairs).
  `landmark`: one per map, a place the path leads past. `noise`: small, in dead space. `backdrop`: a giant
  that is far bigger than the screen; it lies along the map edge and runs off it, so only part of it shows (the
  greater krayt skeleton, the Venator, the Star Destroyer over NiJedha, Fortress Vader beyond Ashen Pass).
- **On the screen.** The GBA shows 15x10 cells. Every non-backdrop piece is drawn at most 10 cells wide and 7 tall, so it is
  seen whole with room around it. Big is the point: a wreck should read from across the screen. Sizes are picked to look right, not to scale.
- **Facing.** The camera is the game's 3/4 top-down view, so a piece can't turn freely. `facings` lists the
  drawings: `e` and `w` are one drawing mirrored (the tilemap's flip bit, free), `n` and `s` are drawings of
  their own. Each placement says which it uses (`facing` in the yaml); the greybox mirrors `w`.
- **Clean edges.** A land piece stands on one kind of ground (all rock or all trees), never across a cliff
  line or a bank, and its drawn rows never hang over water. A water piece keeps a ring of water round it.
  Where an area has no blocked spot that big, the piece takes open ground at the map's edge (never next to a
  road, stairs or a ledge, never cutting a route) and its placement says so in `fit`: the terrain is evened
  out there when the piece is placed for real.
- **Water.** Pieces on water (`~`: sea, swamp, lava, the cloud sea, the Dune Sea) never cut a surf route; the
  placer checks that every body of water stays one piece.
- **Events.** `shown` is `always`, or tied to an existing story flag. The map script swaps the metatiles on
  load with `setmetatile` (as vanilla does for its puzzle doors), so no new flag is spent. A piece that
  changes (the drill rig topples, the ion cannon dish gets built) needs a second drawing; a piece that only
  appears or leaves needs none. Collision never changes with an event.
- **Tile budget.** A secondary tileset holds 512 tiles and 512 metatiles, shared with the planet's buildings
  and terrain. `metatiles` is the piece's cost (every drawn cell, every drawing, every state) and `tiles` is
  four per metatile, an upper bound before repeated tiles are shared. Counted per planet and tileset, the
  metatiles fit: the most is Hoth with 239 of 512. The tile upper bound does not: 11 planet tilesets go over
  512 (Hoth, Felucia and Yavin 4 near 900). So the big pieces must be drawn from repeated tiles (hull plating,
  rib arcs, rock), the way vanilla draws its cliffs, and each planet's tileset is checked when its pieces are
  drawn. If one is still over, the heaviest piece moves to a map with room or shrinks.

Review sheets: `world/greybox/scenery/placements-*.png`, one screen-sized crop (15x10 cells) per placement with its hit box in red. Placements are made by `tools/blockout/drafts/scenery.py` from the catalog in `scenery_spec.py` (rerun it after
an area's grid changes; it redoes every scenery prop). Query the rows with
`python3 -m blockout todo --kind scenery`. Greybox renders use a stand-in model per piece (named in `build`
and `notes`); each needs its own shape when its category is reviewed.

**3D models.** Each scenery row is also a low-poly grey model in `tools/world-art/models/scenery/`, rendered
by the Emerald camera (`python3 -m worldart scenery`, [README](../../tools/world-art/README.md)). Four
columns track it: `model` (the yaml), `model_status` (`TODO`, `IN-PROGRESS`, `IN-REVIEW`, `APPROVED`),
`model_png` (the sprite in `world/models/`, with a `_scene.png` screen check beside it) and `model_tiles`
(unique 8x8 tiles). Query: `python3 -m blockout todo --model IN-REVIEW`. Nothing is in the game yet.

| Planet | Pieces (where) | Lore |
|---|---|---|
| Every planet | Crashed X-wing, Crashed TIE fighter, Y-wing wreck, Vulture droid wreck, Droid tank wreck, AT-TE wreck, Republic gunship wreck, Hull debris, Fallen comm tower, Broken bridge, Collapsed stairs, Ruined wall, Rubble pile | Clone Wars wrecks seventeen years on, and the first Rebel and Imperial losses. One drawing each, recoloured per planet. |
| Tatooine | Sandcrawler far off (Routes 103, 112, backdrop), Greater krayt skeleton (Route 111, backdrop), Gutted sandcrawler (Jundland Wastes), Crashed skyhopper (Routes 104, 116), Podracer wreck (Route 110, Mos Espa), Fallen canyon arch (Route 110), B'omarr ruin (Jabba's palace), Abandoned homestead (Routes 101, 117, Anchorhead), Wrecked freighter (Route 115) | The Sandcrawler the player enters (`art:tatooine:sandcrawler`, the wandering one after a sandstorm) is a building, not scenery. A New Hope's krayt skeleton, Beggar's Canyon, the Boonta Eve course, the B'omarr monastery. |
| Kashyyyk | Juggernaut wreck (Route 109), Sunken tank droid (Route 105, water), Fallen wroshyr trunk (Route 106), Catamaran wreck (Route 108) | The Battle of Kashyyyk (Revenge of the Sith). |
| Sullust | Separatist frigate wreck (Route 113, backdrop), Hyena bomber wreck (Route 114), Collapsed lava tube (Inyusu Tor, Route 113) | SoroSuub joined the Separatists. |
| Mustafar | Fallen collector arm (mining facility, in the lava), Fortress Vader far off (Ashen Pass, backdrop), Imperial drill rig (Mustafar Peak, topples after Vader is beaten there) | The duel on the collector arm; Vader's castle from Rogue One. |
| Endor | Fallen redwood (Routes 118, 121), Towani starcruiser wreck (Route 123), Crashed Imperial shuttle (Route 120) | The Ewok film Caravan of Courage (Legends); the Imperial survey that picked Endor. |
| Bespin | Beldon (Cloud City, in the cloud sea), Crashed cloud car, Drifting platform (Tibanna refinery) | Beldons breathe out Tibanna gas. |
| Jedha | Star Destroyer overhead (NiJedha, backdrop, leaves once the temple's kyber is safe), Assault tank wreck (NiJedha, Route 122), Headless Jedi statue (temple terraces and summit) | Rogue One. |
| Yavin 4 | Crashed Republic frigate (Route 125, backdrop), Massassi ruin (Routes 124, 125), Fallen Massassi head (Route 124, river) | The Massassi temples; a Clone Wars Pelta frigate. |
| Hoth | Gozanti cruiser wreck (backdrop), Frozen AT-AT (the frozen lake), Probe droid crater, Ion cannon footing (dish built after the player is champion) | Alternate telling: the Empire tested cold-weather walkers here years early. |
| Dagobah | Sunken landing craft (Routes 126, 128, in the bog), Dragonsnake skeleton (Routes 126, 128, in the bog), Fallen gnarltree (Routes 129, 130) | The dragonsnake that spat out R2-D2. |
| Kamino | Sunken Venator stern (Route 134, in the sea), Trident drill wreck (Routes 132, 133, in the sea), Toppled stilt dome (Route 131), Aiwha skeleton (Route 134) | The Battle of Kamino (The Clone Wars). |
| Ilum | Abandoned kyber drill, Frozen Jedi statues, Crystal spires far off (backdrop) | The Empire stripped Ilum's kyber. |
| Post-game | Statue of Lando and a Star Destroyer bridge tower Lando won at sabacc (Grand Arena), Venator wreck (Felucia, backdrop), Ruined temple arch (Tython), AT-AT wreck (Atollon, appears after the Bendu wakes), Mortis statues (the Daughter, the Father and the Son), Chewed freighter (Asteroid Spire) | Order 66 on Felucia; Rebels' Battle of Atollon; the Mortis arc; the exogorth. |

Open: no piece has its own greybox model yet; 40 rows have no reference image (`reference_art` is blank); the
sunken X-wing rising after shard 8 (bible/FAN_CRITIQUE.md) is not set as an event until the owner approves it.

## Columns

| Column | Meaning |
|---|---|
| `concept_id` | `art:<planet>:<name>` |
| `planet`, `place` | Planet and town/route/area (`planet-wide` = the planet's shared kit; `SHARED` = every planet) |
| `category` | `building` (exterior), `interior` (room kit), `object` (prop), `nature` (flora, rock), `landmark` (unique set piece), `scenery` (large static scenery, see above) |
| `description` | The brief: shape, materials, what makes it read as Star Wars at 16x16 |
| `footprint` | Size in 16x16 cells, width x height on screen |
| `used_in`, `areas` | How many times the piece is placed in `../world/`, and where (generated by `blockout index`) |
| `build`, `variants` | The greybox model name in `tools/greybox` (and alternates picked by position); blank = no model yet |
| `tool` | The tool that draws it (`greybox piece`); blank = no tool yet, open work |
| `status` | `pending-mockup`, `pending-final-art`, `art-complete`, `imported-in-game` |
| `greybox` | Path of the rendered greybox PNG under `wiki/` |
| `notes` | What it needs, in plain words |
| `drawn` | Scenery: cells drawn, the footprint plus the rows that rise above it (walk-behind) |
| `facings` | Scenery: the facings that exist; `e` and `w` share one mirrored drawing |
| `metatiles`, `tiles` | Scenery: metatiles it costs in its tileset (all drawings and states) and 8x8 tiles, an upper bound |
| `shown` | Scenery: `always`, or the story flag that makes it appear, leave or change |
| `vanilla_template` | The Emerald tiles it replaces or is built from (`(done)` = covered by a recipe already) |
| `sw_refs` | `starwars-db` entity ids used as reference (github.com/spencerlepine/starwars-db) |
| `reference_art` | Local reference images (`art/concept/...`): starwars-db databank images (`__db_`), web references (`__web_`, sources in `art/concept/SOURCES.csv`) and paintings generated in code where nothing usable was found (`__gen_`, made by `art/concept/_generated/paint.py`; `__civ_`, SDXL paintings from Civitai made by `tools/tile-generator/scripts/civitai_concepts.py`) |
| `concept_art` | Concept art made for this game (pixel mock-ups), once drawn |

Reference images are film and franchise stills (Lucasfilm) kept only as private mood references for drawing; they are
never shipped in the game.

## Order of work

1. Collect references for every row (`REFERENCE_READY`). **Stop and review with the owner.**
2. Concept art per biome, owner approves.
3. Build per chunk, one category at a time, each with its own approvals. New art is rendered from 3D
   models with `tools/world-art`. The Hoenn tree is approved (`tools/tile-generator/STYLE.md` section 9);
   each new kind of object is calibrated against its vanilla counterpart before anything is built.

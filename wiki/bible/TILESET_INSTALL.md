# Tileset install notes (read before porting any tileset)

The tile-generator ([`../../tools/tile-generator`](../../tools/tile-generator)) builds approved tilesets as **recipes**
(`tools/tile-generator/recipes/*.yaml`). None of them are in `../game` yet: the owner chose to import them later.
This page lists everything the import has to do beyond copying files, so nothing is lost. Build a recipe with
`python -m tilegen build recipes/<name>.yaml` (palette gate included) and see the tool's README for `install`.

## Status of every recipe (owner approved on 2026-11-01)

| Recipe | What it re-themes | Tileset pair | Install needs |
|---|---|---|---|
| `tatooine.yaml` | Tatooine outdoors | General + town secondaries | Its own copy of the General primary (see rule 1) |
| `hoth.yaml`, `sullust.yaml`, `endor.yaml`, `dagobah.yaml`, `kamino.yaml` | Planet outdoors | General + town secondaries | Its own General copy per planet (rule 1) |
| `sullust-lava.yaml` | Sullust with lava instead of water | General + Lavaridge etc. | Rule 1, plus its `rebank` op clones 14 tiles into free General tile ids below 432 |
| `tatooine-homestead.yaml` | Player's house interior | Building + BrendansMaysHouse | Palette-only: already ART_READY in `art/`, copy `palettes/06-12.pal` |
| `bacta-center.yaml` | Pokémon Center interior | Building + PokemonCenter | Palette-only: already ART_READY in `art/` |
| `death-star.yaml` | Death Star interior and hangar | General + Facility | Rule 1 (its `trench-wall`, `dock-deck`, `coolant` rules recolour General banks 3-5) and rule 2 (new floor pixels in Facility tiles 660-661, 768-769, 784-785, 800-801, 816-817) |
| `star-destroyer.yaml` | Star Destroyer quarters and corridors | General + InsideShip | Rule 2 (InsideShip palettes change) and rule 3 (the buoy map edits below) |
| battle `battle:` rules in each planet recipe | Battle backgrounds | `graphics/battle_environment/*` | Copy `palette.pal` per environment |

## Rules for the import

1. **Never overwrite the shared General primary.** Every route and town uses `gTileset_General`. A planet recipe
   (and the Death Star hangar) recolours it, so each planet gets its **own copy** of the primary
   (e.g. `data/tilesets/primary/general_tatooine/`, a new `gTileset_GeneralTatooine` header in
   `src/data/tilesets/headers.h`, and its maps' `primary_tileset` in `data/layouts/layouts.json` pointed at it).
   Copy the tile animations with it (`tileset_anims.c` callback stays `TilesetAnim_General`).
2. **Secondaries that other maps share also need a copy.** Facility is used by Aqua Hideout, Space Center,
   Abandoned Ship deck, Mt. Pyre and more; InsideShip by the Abandoned Ship and the S.S. Tidal. Copy the secondary for the
   re-themed maps (e.g. `facility_death_star`, `inside_ship_star_destroyer`) and point only those layouts at it.
   The vanilla InsideShip stays as is (it keeps the life buoys for a sailing ship).
3. **Apply each recipe's `layout_edits:`** to the copied maps' `map.bin` (metatile id swap, keep bits 10-15).
   `install` does not write map.bin yet. Current edits:

| Recipe | Layout | Swap (old metatile -> new) | Why |
|---|---|---|---|
| `star-destroyer.yaml` | `AbandonedShip_Rooms_1F_Layout` | 577, 578, 579, 580 -> 551; 585 -> 627; 586, 587 -> 559; 588 -> 629 | No life buoys on a Star Destroyer. 585 and 588 also hold half a bunk label, so they become the label-only cells. |
| `star-destroyer.yaml` | `AbandonedShip_Rooms2_B1F_Layout` | same as above | same |

   Other layouts that show buoys (do the same if they become Imperial): `AbandonedShip_Rooms_B1F_Layout`,
   `AbandonedShip_Rooms2_1F_Layout`. `SSTidalRooms_Layout` keeps them.
4. **Gate:** nothing installs unless `palette-enforcer check --tile` passes (the build runs it).
5. When a recipe lands, add its rows to `mapping/art_ready.csv` (or set `game_status` `DONE`) and remove its line here.

# tile-generator (overworld tilesets, metatiles, animations, battle backgrounds)

**Status: IN PROGRESS; greybox terrain READY (below).** Nothing installed into `game/` yet. The tool is being
built stage by stage, each stage ending in a review sheet the owner approves before the next one
starts; the full art run happens only when every stage is approved. See [PLAN.md](PLAN.md).

Categories: D1 tilesets, D2 tileset animations, E1 battle backgrounds (`../README.md`). Rows:
`../../wiki/database/pending_art.csv`, `kind` = `tileset` (247 PNGs) and `battle_environment` (21).

## Greybox terrain (phase 1 of the world art, 2026-11-02)

Status: **READY** for greybox. Final colours wait for the palette; shapes are the game's own tiles. Every tile
the game needs is a row in the wiki; 13 rows have no tile yet and show the placeholder.

```bash
python -m tilegen terrain run                       # catalog + sheets + every area's tile render (about 25 s)
python -m tilegen terrain render --area mos-espa     # one area (or --planet HOTH)
python -m tilegen terrain catalog                    # terrain.csv only
python -m tilegen terrain mark --status pending-final-art   # set every phase 1 row that has a tile
python -m tilegen terrain build --planet HOTH        # game-format greybox tilesets for a planet -> out/greybox/hoth/
```

- **Vocabulary** (`tilegen/roles.py`). A terrain item is a fixed set of named tiles, the same for every tileset
  and planet. Water, cliffs, walls and paths are blob sets: `fill`, edges `n e s w`, outer corners `ne nw se sw`,
  inner corners `inner-*`, one-cell strips `strip-h strip-v`, tips `tip-*`, `single`; walls add `top` (the row
  above a face, as Emerald draws a wall as top + face). Ledges: `fill`, end caps, `single`. Bridges: `h`, `v`.
  Grounds, wild grass, sand, ice, trees, structures: `fill`.
- **Catalog.** Every cell of every vanilla layout an area replaces is classed the way blockout classes it
  (ground, wild grass, water, ledge, bridge, blocked, tree), named as an item of its tileset (`ground-grass`,
  `ground-path` for Hoenn's dirt, `ground-stone` for stairs and stone, `water-pond`, `cliff`, `wall`, `floor`...)
  and given its role from its neighbours. Its metatile is filed under `terrain:<tileset>:<item>:<role>` in
  `wiki/mapping/terrain.csv`: `metatile_ids` (every vanilla metatile seen, the chosen one first), `use` (the one
  the autotiler draws), `use_set` (`learned`, or `hand` when you set `use` yourself: a hand value is kept across
  runs and wins; `fill` for a thin path drawn with the plain path tile), `cells`, `planets`, `areas`, `needed_by` (redesigned areas that need it), `status`, `sheet`
  and `sheet_cell`. Phase 1 rows have the tool `tilegen terrain`; trees and structures are phase 2, listed only.
  `terrain_areas.csv` links each area to its pair, render, items and `missing_roles`.
- **Autotile.** 466 areas keep their vanilla layout and are drawn with it. 62 areas were redesigned or are
  new; their grid is drawn from the vocabulary: each cell gets an item (the pair's usual ground, Hoenn's dirt for
  `:`, its water, its wild grass; wall or cliff for blocked cells) and its role, then the tile vanilla uses for
  that item and role in that tileset pair (voted by the number of layouts that use it, so one big map cannot win
  alone; grounds take the shared primary tiles first, cliffs, walls and water the pair's own). A role vanilla
  never drew in that pair has no tile: the cell shows the placeholder and the row is added as TODO
  (`pending-mockup`) with the areas that need it. `PAIR_OVERRIDE` picks the pair for a redesigned area whose
  vanilla pair is wrong for it (NiJedha: Rustboro's stone city, not Mt. Pyre).
- **Sheets.** `wiki/world/greybox/sheets/<tileset>.png` is real size: 128 px wide, 16x16 cells, one per csv row
  in csv order (`sheet_cell` = column,row), the placeholder where the tile is missing. The placeholder is z-day's
  `16x16-placeholder-image-sprite.png` (magenta circle), copied to `tilegen/data/placeholder-16x16.png`.
  `wiki/world/greybox/terrain/<tileset>.png` is the labelled sheet: every item as a strip of its roles at 2x,
  missing roles named in magenta. Renders: `wiki/world/greybox/tiles/<area>.png`.
- **Greybox.** Each planet's tilesets get its approved planet recipe (Tatooine, Hoth/Ilum, Sullust, Mustafar,
  Endor/Yavin/Kashyyyk, Dagobah, Kamino, Death Star) and are then desaturated (`GREY_CHROMA`). Shading and
  shapes stay; colour waits.
- **Build.** `terrain build` writes the planet's greybox pairs in game format through the palette gate (all 19
  planets pass). Nothing is installed: the map work writes the autotiled map.bin later.

## Setup

```bash
cd tools/tile-generator
pip install -r requirements.txt            # pillow, numpy
# the game is found automatically (this repo's game/); EMERALD_DIR overrides it
```

| Path | What |
| --- | --- |
| `tilegen/` | The Python package (`python -m tilegen ...`) |
| `tilegen/gba.py` | Reads tilesets (tiles.png, palettes, metatiles.bin, attributes) and layouts; renders metatiles and whole maps exactly as the game composites them |
| `PLAN.md` | The stages, what each one proves, and the review gate for it |
| `STYLE.md` | Emerald's overworld art rules, measured (grows with each stage) |

## Commands (stage 0)

```bash
python -m tilegen list-tilesets                                  # the 75 tilesets and their folders
python -m tilegen list-layouts [filter]                          # every map layout and its tileset pair
python -m tilegen render-map LittlerootTown_Layout out.png --zoom 2   # a map as the game draws it
python -m tilegen render-tileset gTileset_Petalburg out.png --cols 16 # every metatile of a tileset
```

```bash
python -m tilegen anim Route103_Layout out/anim/route103.gif recipes/tatooine.yaml recipes/sullust-lava.yaml --crop 336 40 656 264
```

`anim` plays the pair's tileset animations (parsed from `src/tileset_anims.c`, one step per 16 game frames)
for vanilla and each recipe and writes a GIF grid plus a still of the first frame.

`render-map` is the review tool for everything that follows: a generated tileset is dropped into a real
layout and compared with the vanilla render side by side, so the owner judges it in context and not as
a sheet of squares.

## Build, gate and check in the ROM

```bash
python -m tilegen build recipes/tatooine.yaml --layouts LittlerootTown_Layout Route101_Layout   # out/tatooine/ + review.png
python -m tilegen install recipes/tatooine.yaml --layout LittlerootTown_Layout   # copies into game/ (gate enforced)
(cd ../../game && make -j8 && cp pokeemerald.gba /some/test.gba && git checkout -- data/tilesets src/data/tilesets/graphics.h)
scripts/rom-shots.sh /some/test.gba out/rom 0:9:10:9:littleroot 0:0:15:12:petalburg 0:16:10:10:route101
scripts/rom-battle.sh /some/test.gba out/rom   # wild battle in Route 101 grass, screenshots the battle background
```

A recipe's `layout_edits:` (metatile swaps per layout, e.g. no life buoys on a Star Destroyer) are applied to
the review renders; `install` does not write map.bin yet, so they go in with the map work.

Until the owner approves a planet, installs are for test ROMs only: restore `game/` and never commit it.

## Format (what the game needs)

| Fact | Value | Source |
| --- | --- | --- |
| Tile sheet | `tiles.png`, indexed, 128 px wide, 8x8 tiles row-major; primary max 512 tiles, secondary max 512 (ids 512-1023) | `include/fieldmap.h` |
| Palettes | 16 x `palettes/NN.pal` (JASC) per tileset; the game loads **0-5 from the primary, 6-12 from the secondary**; 13-15 are the UI's | `src/fieldmap.c` |
| One bank per tile | Every 8x8 tile is drawn with one 16-colour bank (index 0 transparent); the bank is chosen **per tile per metatile** in `metatiles.bin`, so one tile can be reused in another bank (recolour for free) | metatile entry bits 12-15 |
| Metatile | 16x16 = 2 layers x 4 tiles, 8 u16 (`metatiles.bin`); u16 = tile id (0-9), hflip (10), vflip (11), bank (12-15) | `fieldmap.h` |
| Attributes | u16 per metatile: behaviour (0-7, `metatile_behaviors.h`), layer type (12-15): NORMAL middle+top, COVERED bottom+middle, SPLIT bottom+top | `global.fieldmap.h` |
| Layer rule | Top layer draws **over** walkers and the player (roofs, tree tops, signs' tops); bottom/middle under | `fieldmap.c` BG layers |
| Primary pairs | Outdoors: `gTileset_General` + one town/route secondary. Interiors: `gTileset_Building` (only 8 metatiles) + a room secondary that carries the whole room kit | `data/layouts/layouts.json` |
| Compression | Tiles and metatiles `.lz` (`INCGFX_U32(... ".4bpp.lz", "-num_tiles N")`): the `-num_tiles` in `src/data/tilesets/graphics.h` must match the sheet's tile count | `graphics.h` |
| Animations | Frames are tile sheets copied into fixed VRAM tile ranges by `src/tileset_anims.c` (e.g. General water: 30 tiles at 432, 8 frames); a new tileset keeps the ranges and frame counts of the one it replaces | `tileset_anims.c` |

### Palette gate (required: [`../PALETTES.md`](../PALETTES.md))

Layer 1: 4bpp, one bank per tile, primary 0-5 / secondary 6-12, GBA steps. Layer 2: one planet theme per
biome, added to `../../wiki/bible/PALETTE.md` as `## Planet: <name>` before the biome's tiles are made;
interiors use the faction themes, battle backgrounds `battle-backdrop`. The pipeline ends with
`palette-enforcer` `enforce --pal bank.pal` per bank and `check --tile`; nothing that fails installs.

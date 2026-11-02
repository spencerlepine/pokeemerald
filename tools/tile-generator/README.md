# tile-generator (overworld tilesets, metatiles, animations, battle backgrounds)

**Status: IN PROGRESS; greybox terrain READY (below).** Nothing installed into `game/` yet. The tool is being
built stage by stage, each stage ending in a review sheet the owner approves before the next one
starts; the full art run happens only when every stage is approved. See [PLAN.md](PLAN.md).

Categories: D1 tilesets, D2 tileset animations, E1 battle backgrounds (`../README.md`). Rows:
`../../wiki/database/pending_art.csv`, `kind` = `tileset` (247 PNGs) and `battle_environment` (21).

## Greybox terrain (phase 1 of the world art, 2026-11-02)

Status: **READY** for greybox. Final colours wait for the palette; shapes are the game's own tiles.

```bash
python -m tilegen terrain run                       # catalog + item sheets + every area's tile render (about 30 s)
python -m tilegen terrain render --area mos-espa     # one area (or --planet HOTH)
python -m tilegen terrain mark --status pending-final-art   # set every phase 1 item's status
python -m tilegen terrain build --planet HOTH        # game-format greybox tilesets for a planet -> out/greybox/hoth/
```

- **Items.** Every cell of every vanilla layout an area replaces is classed like blockout classes it (ground, wild
  grass, water, ledge, bridge, blocked, tree) and its metatile is filed under an item of its tileset:
  `terrain:general:ledge-south`, `terrain:general:water-shore`, `terrain:cave:cliff`, `terrain:lab:floor`. Phase 1
  items (ground, grass, sand, snow, water, shores, ledges, bridges, cliffs, floors, walls) have the tool
  `tilegen terrain`; trees and structures are phase 2 and only listed. Written to `wiki/mapping/terrain.csv`
  with planets, area counts and status, plus `terrain_areas.csv` (area -> tileset pair, render, items).
- **Greybox.** Each planet's tilesets get its approved planet recipe (Tatooine, Hoth/Ilum, Sullust, Mustafar,
  Endor/Yavin/Kashyyyk, Dagobah, Kamino, Death Star) and are then desaturated (`GREY_CHROMA`). Shading and
  shapes stay; colour waits.
- **Areas.** 466 areas keep their vanilla layout and are drawn with it. 62 areas were redesigned or are new;
  their blockout grid is **autotiled**: each cell takes the metatile vanilla maps use most for the same cell
  class with the same 8 neighbours (then 4, then none), so shores, cliff edges and ledge ends match the game.
  Renders: `wiki/world/greybox/tiles/<area>.png`. Item sheets: `wiki/world/greybox/terrain/<tileset>.png`.
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

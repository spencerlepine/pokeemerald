# tile-generator: the plan

The goal is a tool that turns a short brief ("Mos Pelgo: Tatooine homestead town, adobe domes, vaporators")
into game-ready tilesets at vanilla Emerald quality, without drawing tiles by hand. It is built in stages.
Each stage ends with a **review sheet** (vanilla vs generated, rendered inside a real map) that the owner
approves before the next stage starts. The full art run (all 247 PNGs) only happens after every stage is
approved.

## What the vanilla art actually is (stage 0 findings)

- A tileset is a **kit of 16x16 metatiles** built from 8x8 tiles. One town secondary (Petalburg) is 144
  metatiles from 160 tiles; the shared outdoor primary (General) is 512 metatiles from 512 tiles, of which
  421 are used. Interiors live almost entirely in the secondary: `gTileset_Building` has only 8 metatiles.
- **Colour is per tile, chosen per metatile.** A tile is a 4-bit index map; the bank (16 colours) is picked
  in `metatiles.bin`. 63% of General's metatiles mix two or more banks. A recolour (sand instead of grass)
  is a palette change plus a bank renumber, with no pixel work.
- Each bank uses 9-15 of its 15 colours, typically as 3-4 tone ramps per material (ground 3 tones, water
  4, roof 3-4, wall 3, trim/outline darks, 1-2 highlights).
- **Perspective:** ground is drawn in plan (straight down); every vertical face is drawn head-on with no
  side faces, so a building is roof (plan view, light from top-left) stacked on front wall (elevation).
  Objects (trees, rocks, signs) are the same: a top ellipse plus a front. There is no horizon, no
  vanishing point, no visible side wall. Depth is sold by (a) a 1 px dark base line and a drop shadow on
  the ground row under every object, (b) the top layer drawing over the player, (c) roofs 1.5-2 tiles deep
  for a 2-tile-tall wall. This is the invariant every generator below must keep.
- Category inventory in a town/route pair (General + town): ground (grass, tall grass, sand, dirt path,
  ledges in 4 directions + corners), water (still, shore edges, waterfall, reflections), objects (trees in
  2x2/2x3 with overlap, rocks, signs, fences, flowers, mailbox, boulders), buildings (house kit: roof
  rows, wall rows, door, window, steps; Center/Mart/Gym as fixed assemblies), and the animations.

## Stages

| # | Stage | What it proves | Method | Review gate |
|---|---|---|---|---|
| 0 | **Foundation** (this commit) | We can read and render everything the game has, pixel-exact | `tilegen/gba.py`: tilesets, metatiles, layouts, map render | Vanilla Littleroot / Petalburg / Center renders match the ROM |
| 1 | **Biome recolour** | A planet theme + per-bank recolour turns vanilla terrain into a new biome with zero pixel loss | Theme in `wiki/bible/PALETTE.md`; ramp-aware palette mapping (hue/value per ramp, not per colour); bank renumbering | Littleroot as Mos Pelgo ground: grass->scrub, dirt->sand, trees->desert trees; side by side |
| 2 | **Ground texture synthesis** | New ground materials (sand, ash, snow, swamp, durasteel decking, Death Star floor) that tile seamlessly in the vanilla idiom | Procedural 8x8/16x16 texture generators (noise density, speck placement, edge rules measured from vanilla), quantised to a 3-4 tone ramp; auto-generated ledge/edge sets from a mask | A sheet of 8 ground materials rendered in a route layout, next to the vanilla route |
| 3 | **Objects from 3D** | A simple 3D model renders into a vanilla-looking object metatile (top ellipse + front, drop shadow, coloured outline) | Numpy orthographic rasteriser with the Emerald camera (plan for horizontal faces, elevation for vertical), 3-tone flat shading, 1 px outline in the ramp's dark tone, tile split + dedup, layer type assignment | Vaporator, Tatooine rock, scrub tree, holo-sign, fence; dropped into Route 101 |
| 4 | **Buildings from 3D** | A parametric building (footprint, height, roof type: dome / flat / slope / tower, door, windows, trim) renders into a house kit that matches vanilla houses tile for tile | Same rasteriser + a building grammar; roof rows and wall rows become reusable metatiles; door at a walkable cell; top layer rule for the roof | Mos Pelgo (Littleroot) with 3 domed homesteads and the lab; Imperial outpost; side by side |
| 5 | **Interiors** | A room kit (back wall, side walls, floor, door mat, props) from a brief | Wall/floor generators + object stage for props (console, cot, table, bacta tank) | Player's homestead and the Bacta Center rendered in their layouts |
| 6 | **Water and animations** | Animated water, lava, steam, blinking lights with the right frame counts and VRAM ranges | Frame generators per animation type; keeps `tileset_anims.c` ranges | GIF of the Dune Sea shoreline and Sullust lava |
| 7 | **Assembly and install** | A whole tileset pair builds, passes the palette gate, compiles, and runs in the ROM | Tile packer (dedup with flips, 128-wide sheet, bank per tile), `metatiles.bin` + attributes writer, `graphics.h` `-num_tiles` update, `palette-enforcer check --tile --pal`, `play-tester` screenshot | ROM screenshot of Mos Pelgo matching the review render |
| 8 | **Battle backgrounds** (E1) | 21 environments | Same renderers at battle scale; `battle-backdrop` theme | Battle screenshot per environment |
| 9 | **Full run** | All 247 rows | One brief per tileset row, batch, review sheets per planet | Owner approves per planet; rows set to `DONE` |

Diffusion (Civitai) is a possible **texture source** in stages 2 and 3 (img2img from the rendered 3D with
a pixel-art LoRA), never the source of geometry: geometry and perspective come from the rasteriser so the
top-down illusion cannot break. We only spend Buzz once the deterministic path is approved and a texture
visibly needs it.

## Open decisions for the owner (asked as each stage reaches them)

- Stage 1: the first planet theme values (Tatooine). The tool proposes a palette from reference colours;
  the owner approves the swatch before it goes in the wiki.
- Stage 4: building vocabulary per planet (Tatooine domes/adobe, Imperial durasteel, Ewok platforms,
  Cloud City white curves, Kamino stilts, Dagobah huts).
- Stage 9: which vanilla kits stay recoloured only (caves, generic rooms) and which are rebuilt.

## Progress and next steps (2026-11-01)

Done and pushed: stage 0 (reader/renderer), stage 1 (recolour recipes: tatooine, hoth, sullust), stage 2 first
cut (ground `speckle` + recipe `retexture:` ops), stage 7 writer (`python -m tilegen build|install`, 4-bit
tiles.png, .pal, metatiles.bin, attributes, palette gate passes). A test ROM with the Tatooine pair compiles
(installed, built, then game/ restored; nothing committed in game/).

**Owner direction:** the 3D path (stage 3 objects, stage 4 buildings) is **parked**. The owner rejected the
generated trees; 3D objects and buildings wait for the owner's guidance. Work the 2D categories first.

Next, in order:
1. ~~ROM screenshot of the Tatooine pair~~ done: `scripts/rom-shots.sh` (mash New Game in lua, teleport,
   screenshot). The vanilla savestates do not load into a rebuilt ROM, hence the mash.
2. Stage 2: sand patch edges, ledges, tall grass / scrub tuft redraws, more planets (Endor, Dagobah, Kamino).
3. Stage 6 first cut: `tilegen/anim.py` + `python -m tilegen anim` play the vanilla animations into a
   recoloured pair (frames are index maps, so recolours animate for free and keep the ranges). Water turns
   into lava with a bank-scoped recipe (`recipes/sullust-lava.yaml`: `banks:`, `hue_by_light`, `extends:`)
   and the `rebank` retexture op, which moves the water rocks out of the shared bank 1. New frame
   drawings (steam, sparks) wait until a recolour can't do it.
4. ~~Stage 5: interior floor and wall kits (2D)~~ shipped as ART_READY (Brendan/May house, Pokémon Center).
5. ~~Stage 8: battle backgrounds~~ recipe `battle:` rules; Tatooine tall grass checked in the ROM with `scripts/rom-battle.sh`.

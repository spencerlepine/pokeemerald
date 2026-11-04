# starnav-map: the StarNAV map screen

The StarNAV map screen (Emerald's region map, category D8). Mockups are drawn at the GBA's 240x160 and played in
a browser without building the ROM: the cursor moves, A zooms in, B zooms out. Round 1 (2026-11-04): five styles.
Round 2 (owner, 2026-11-04): the Galaxy Chart and the Holotable combined, all planets first and the planet opening
as a cyan hologram, with a faint pink nebula; three variants. The page keeps every round, newest first.

The owner picked **Holo Globe** (round 2, style 3), and `install.py` puts it in the game (2026-11-04). See
[In the game](#in-the-game).

```sh
python3 build.py      # out/starnav_map.html (the player, one self-contained page) and out/<style>/ layers
python3 capture.py    # out/previews/round<N>/: a zoom tour GIF and an out|in still per style, all_styles.png
                      # (--round N picks a round; the newest by default)
```

`capture.py` runs `capture.js` with node and the pre-installed Playwright Chromium. Both runs take under a minute.

## How the map is made

`world.py` reads every overworld area with a `pos` from `../../wiki/world/<planet>/*.yaml`, the planet graph
(`../../wiki/mapping/hyperlanes.csv`) and `../../wiki/mapping/planets.csv`. Each planet gets a box on a 224x120
map (`LAYOUT`) and its areas are shrunk into it, a few tiles per pixel, not to scale. Each pixel takes a terrain
class from the area grids (water, rock, trees, grass, ground, path) and a planet's land gets a 2 px rim of
wilderness. The map is cut into Emerald's 28x15 grid of 8x8 sections: each cell is named after the area with
the most pixels in it, and every town and landmark claims one cell so none is lost. The Death Star has no
overworld and is drawn as a station.

`variants.py` draws each style's static layers: the map (zoom is 2x of it, like Emerald's affine zoom) and the
frame. `player.js` draws the cursor, the header (area and planet) and the info card shown when zoomed in
(kind, Bacta Center, market, hangar, arena). Text uses the game's own fonts (`font.py` reads
`../../game/graphics/fonts` and `src/fonts.c`) and the Aurebesh letters of `../glyph-maker/aurebesh.py`.
All colours are on the GBA's 15-bit grid.

## The styles

| # | Style | Look | Zoom |
|---|---|---|---|
| 1 | Holotable | Rebel briefing hologram: one cyan hue on black, scanlines, gold bracket cursor | 2x |
| 2 | Star Atlas | Every planet in its own biome colours in space, gold hyperlanes and town pills | 2x |
| 3 | Imperial Tactical | Greys on black, the section grid shown, red town marks and a crosshair | 2x |
| 4 | Targeting Computer | The X-wing's amber screen in a rounded bezel, reticle cursor | 2x |
| 5 | Galaxy Chart | The galaxy with one globe per planet; A opens the planet's own map | galaxy -> planet |

Styles 1-4 work with Emerald's region map code as it is (one 8bpp affine BG, a 28x15 section grid, 2x zoom);
only the art, the section table and the cursor change. Style 5 needs new code: a second map per planet and
cursor jumps between planets.

Round 2:

| # | Style | Galaxy | Planet |
|---|---|---|---|
| 1 | Holo Projection | colour globes, steel and gold frame | the planet's map as a cyan hologram, gold bracket cursor |
| 2 | Full Holo | wireframe holo globes, the holotable frame | the same hologram |
| 3 | Holo Globe | as 1 | the hologram smaller, inside a wireframe sphere over a holo projector |

All three need the galaxy -> planet code of Galaxy Chart.

To add a style, write a `style_<name>(world)` in `variants.py` that returns its layers and add it to a round in
`ROUNDS`.

## In the game

```sh
python3 install.py    # writes the art and tables below into ../../game, then: cd ../../game && make
```

It writes, every time from the wiki world (the run gives the same files each time):

| File in `../../game` | What it is |
|---|---|
| `graphics/pokenav/region_map/starnav/galaxy.png`, `.bin`, `.pal` | The galaxy view: 8bpp, 256 tiles at most, 64x64 affine tilemap, 45 colours in BG palettes 7-9 |
| `graphics/pokenav/region_map/starnav/planet_<planet>.png`, `.bin`, `holo.pal` | Each planet's hologram (18; the Death Star has none). All share `holo.pal` |
| `graphics/pokenav/region_map/cursor_small.png`, `cursor_large.png`, `cursor.pal` | Gold cell brackets (planet view) and the cyan ring around a globe (galaxy view) |
| `src/data/region_map/starnav_map.h` | Planet names, globe places and the D-pad jump from each globe, each planet's 28x15 grid of map sections, each map section's home cell, and where each overworld map lands on its planet |

What is made from data and what is set by hand:

- From the wiki: each planet's hologram, its grid of map sections and the names (the area yamls with a `pos`,
  their `map`, and the map section in each map's `map.json`); where the player stands (each map's place on the
  grid); the hyperlanes drawn between globes (`hyperlanes.csv`).
- By hand in `variants.py`: the globe of each planet in the galaxy (`GALAXY_POS`, `GLOBE_R`) and the colours.
  The D-pad jumps are worked out from the globe places.

The art has to fit Emerald's affine background: 256 tiles of 8x8 and 48 colours. Plain space becomes a few
shared star tiles, the hologram textures repeat every 8 px, and when the galaxy has more than 256 tiles the
rarest tiles are merged into their nearest look-alike. Colours are cut to 45 with a median cut.

The code is in `../../game/src/region_map.c` (the StarNAV state lives in the unused `filler_084` of
`struct RegionMap`), with small changes to `pokenav_region_map.c` and `field_region_map.c`:

- **Galaxy** (zoomed out): the ring cursor jumps from globe to globe with the D-pad; the name box shows the
  planet. The player's head sits beside their planet's globe. A zooms in (not on the Death Star).
- **Planet** (zoomed in): the planet's hologram at full size with Emerald's cell cursor over its own grid; the
  name box shows the map section. The cursor starts on the player on their planet, else near the middle.
- **Zoom**: the old view zooms into the globe (or shrinks onto it) and fades out, the new art is loaded while
  the map is black, and the new view zooms and fades in (18 frames).
- **StarNAV**: A zooms in and out, B leaves (Emerald's buttons and help bar). The side panel stays folded
  down to the name box in both views. The last view is remembered.
- **Wall map** (Bacta Centers): A zooms in and out, B leaves.
- **Fly map**: it opens on the player's planet with that planet's fly icons. A flies (Emerald's rules); B goes
  out to the galaxy, where A zooms into another planet and B cancels.
- **Datapad area screen** (`pokedex_area_screen.c`): it opens on the galaxy with a flashing mark on each planet
  where the species lives. A steps through those planets one by one (fade out, fade in), each with the pink
  habitat glow over its areas and the cave marks, then back to the galaxy. A does nothing for AREA UNKNOWN.
  The glow uses the planet grids, so an area glows only on its own planet.

Map section names follow Emerald's rules, except Tython: it is all `MAPSEC_SOUTHERN_ISLAND`, which Emerald hides
until `FLAG_LANDMARK_SOUTHERN_ISLAND` is set, so the StarNAV always names it. The header strip above the map says
STAR MAP (GALAXY MAP did not fit), drawn by `../glyph-maker/starnav_map_header.py`.

Check it in the emulator with `../play-tester/scripts/ui-check.sh starnav` (also `starnav_town`, `starnav_fly`,
`starnav_reopen`, `starnav_dex`, `starnav_dex_cave`).

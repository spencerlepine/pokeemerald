# starnav-map: StarNAV map screen mockups

Mockups of the StarNAV map screen (Emerald's region map, category D8), made without building the ROM. The
screen is drawn at the GBA's 240x160 and played in a browser: the cursor moves, A zooms in, B zooms out.
Nothing in `../../game` is built or changed. Round 1 (2026-11-04): five styles, waiting for the owner's pick.

```sh
python3 build.py      # out/starnav_map.html (the player, one self-contained page) and out/<style>/ layers
python3 capture.py    # out/previews/: a zoom tour GIF and an out|in still per style, all_styles.png
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

To add a style, write a `style_<name>(world)` in `variants.py` that returns its layers and add it to `STYLES`.

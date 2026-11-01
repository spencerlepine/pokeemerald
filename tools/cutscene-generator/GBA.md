# GBA output: from pxl art to game files

This repo's additions to pxl (upstream: [crsolver/claude-pxl](https://github.com/crsolver/claude-pxl), MIT).
They turn pxl scenes and sprites into files that drop into `../../game` unchanged, and load the
game's own art back in so a redraw can be checked against the original. Read [STYLE.md](STYLE.md)
before drawing.

Worked example: [`scenes/intro_bike/intro_bike.px.js`](scenes/intro_bike/intro_bike.px.js), intro scene 2
(Emerald's bike ride) redrawn as KAEL's speeder ride on Tatooine.

```sh
cd scenes/intro_bike
node ../../bin/pxl.js build intro_bike.px.js      # out/game/graphics/... + previews
../../scripts/rom-preview.sh out 1300 1950 10       # build a scratch ROM, screenshot the scene in mGBA
```

## Palettes are ordered, and written by index

A GBA palette is 16 colors and **index 0 is transparent**. Code sometimes touches palette entries
by number (intro scene 2 swaps BG entries 9 and 10 every 8 frames), so the order matters. Write
each palette as a 16-entry list and `use()` it; then draw with **numbers** (`rect(0, 0, 8, 8, 13)`),
or with the keys `0-9a-f` (`"d"` is 13). Small integers are palette indices everywhere in pxl
(this repo's change; larger numbers are still packed colors).

Keep colors on GBA steps (each channel a multiple of 8, like `wiki/bible/PALETTE.md`). Two entries
that are the same 15-bit color count as one.

## `gba(path, opts)`: write a game file

`path` is relative to the game root. Every target is checked against the hardware: colors must be
in the target's palette (off-palette pixels are listed with coordinates), sizes must be tile
multiples, OBJ frames a legal sprite size, BG tile sets within budget.

| Target | Writes | Options |
|---|---|---|
| `gba("graphics/.../trees.png", { bg: ["bg3", "bg2"], map: "graphics/.../trees_map.bin", pal })` | 4bpp tile sheet (128 px wide, deduplicated with flips, tile 0 blank) + text-mode tilemap with every listed 256x256 screen back to back | `palSlot` (BG palette number in the map entries, default 0), `tiles` (budget, default 512), `flips: false`, `blank: false`, `cols` |
| `gba("graphics/.../brendan.png", { obj: ["kael_0", ...], pal })` | OBJ sheet: frames stacked vertically (an anim expands to its frames) | `cells` (below) |
| `gba("graphics/.../trees_small.png", { image: "scenery_small", pal })` | one image, any multiple of 8 | `cells` |
| `gba("graphics/.../player.pal", { pal })` | JASC palette, CRLF, as the game's files | |

**`cells`**: gbagfx reads a sheet's tiles row-major over the whole PNG and a sprite uses that many
consecutive tiles. A sheet holding sprites narrower than the PNG (Emerald's `trees_small.png`: a
32x32 at tile 0, 16x32s at tiles 16 and 24) therefore looks scrambled in an image viewer. Draw the
cells side by side and pass `cells: [[32, 32], [16, 32], [16, 32]]`; the tool writes the game's
order. `ref()` takes the same option to unscramble the original.

Files land in `<out>/game/<path>`. Nothing writes into `../../game`: copying a scene in is a
separate, reviewed step (the wiki row's status changes when it lands).

## `ref(name, path, opts)`: load game art as an asset

Defines a sprite `name` from a game file, colored the way the game shows it (15-bit colors,
index 0 transparent), so it can be stamped next to the redraw or under it.

| Option | Meaning |
|---|---|
| `map: "x.bin"` | the PNG is a tile set; render the tilemap (256x256 per screen block) |
| `screen: n` | which screen block of the map (`trees_map.bin` holds BG3 in 0 and BG2 in 1) |
| `pal: "x.pal"` | color with this palette instead of the PNG's own (sunset/night variants, `player.pal`) |
| `frame: [w, h, n]` | frame n of a vertical OBJ strip |
| `cells: [[w, h], ...]` | unscramble a 1D-mapped sheet |
| `transparent: false` | keep index 0 as a color |

The game root is `../../game` from this folder, or `$PXL_GAME_DIR`.

## `gbaScreen(name, opts)`: the screen as the GBA composes it

`include("../../gba/screen.px.js")`, then describe the hardware state instead of drawing a picture:
BG layers back to front with their scroll speed (px per game frame, from the C code), OBJs with
their top-left corner, and palette cycling. It renders a 240x160 animation (GIF in `out/_preview/`).
Build the vanilla screen the same way from `ref()` assets for a side-by-side.

Positions: `CreateSprite(x, y)` is the sprite's **center**, so a 64x64 at (272, 100) has its corner at
(240, 68). Scroll: the bike-ride task does `HOFS -= speed << 4` in 16.16 fixed point, so
`CreateBicycleBgAnimationTask(1, 0x4000, 0x400, 0x10)` is 4, 1/4 and 1/256 px per frame for BG1-3.

## Checks that caught real mistakes

- Round trip: `ref()` the vanilla `trees.png` screens, `gba()` them back out and `ref()` the result:
  pixel-identical (86 tiles with flip dedup vs Emerald's 202).
- `bicycle.png` is 4 frames of **64x32**, not 64x64, drawn 8 px below the rider's center. The preview
  only lined up after reading `sOamData`/`CreateIntroBrendanSprite`; do that before drawing any actor.
- The intro picks Brendan or May at random each boot: a redraw needs both sheets.
- In the ROM, scene 2 also shows Manectric, Torchic, Volbeat and Flygon (their own palettes): they stay
  Emerald's until the companions are drawn.

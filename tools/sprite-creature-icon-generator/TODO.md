# sprite-creature-icon-generator

**Status:** TODO. Not built yet; this file marks the scope.

**Engine: Python** (no image model). The icon is a small redraw of the creature's approved battle
front, so it is derived from that front rather than generated from text. No public diffusion
model draws clean 32x32 sprites; an img2img pass can be tried later, but the finisher is Python
either way.

Companion party and PC box icons: the small creature that wiggles in the party menu, PC boxes,
day-care, mail and Union Room screens.

- **Categories:** A3
- **Wiki rows:** `pending_art.csv` kind `pokemon`, files `icon.png` (every species folder, every
  Unown letter, `egg/`, `question_mark/`) plus `deoxys/icon_speed.png` and
  `deoxys/icon_speed_wide.png`; 417 PNGs
- **Format in the game:** `icon.png` 32x64 = two 32x32 frames (the wiggle), 4bpp. It has **no
  palette of its own**: it uses one of 3 shared icon palettes
  (`game/graphics/pokemon/icon_palettes/icon_palette_0.pal` to `_2.pal`), and the species' index
  is set in `gMonIconPaletteIndices` in `game/src/pokemon_icon.c`
- **Frame 2:** 381 of 387 vanilla icons redraw frame 2 (squash, limbs or head moved); only 6 are
  a plain 1-2 px shift

## What it makes, per species

| File / data | Made by |
|---|---|
| `icon.png` frame 1: the front reduced to fit 32x32 | Python: downscale the approved `game/graphics/pokemon/<species>/front.png`, snap to the closest shared icon palette, clean outline |
| `icon.png` frame 2: the wiggle pose | Python: squash/shift parts of frame 1; hand-touch when it reads wrong |
| `gMonIconPaletteIndices[species]` (0, 1 or 2) | Python: the shared palette that fits the front best |
| The 3 shared icon palettes | Kept vanilla unless too many new creatures fit none of them; changing one recolours every icon that uses it |

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` the Emerald original, `suggested_path` the new name) and the species' approved front, and writes the icon and its palette index.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

# sprite-creature-extras-generator

**Status:** TODO. Not built yet; this file marks the scope.

**Engine: Python** and hand touch-up (no image model). These are one-off sheets with exact
layouts that code animates (the hatch crack, the shell shards, Spinda's spot masks), so they are
drawn to the layout rather than generated.

The creature sprites that are not a species: the Egg, Spinda's random spots, and the
question-mark placeholder pics.

- **Categories:** A5, plus the `egg/` and `question_mark/` front/back files the category table counts under A1/A2
- **Wiki rows:** `pending_art.csv` kind `pokemon`, subkinds `egg` (front, anim_front, hatch, shard),
  `question_mark` (circled and double: front, anim_front, back) and `spinda` (`spots/spot_0-3.png`); 14 PNGs
- **Format in the game:**

| Folder | Files | Format | Where it shows |
|---|---|---|---|
| `game/graphics/pokemon/egg/` | `front.png` 64x64, `anim_front.png` 64x128, `normal.pal` | Same as a battle front, own palette | Summary and day-care for an unhatched egg |
| | `hatch.png` 32x128 | 4 frames of 32x32 (egg cracking) | Hatching scene |
| | `shard.png` 32x8 | 4 shards of 8x8 | Hatching scene |
| `game/graphics/pokemon/spinda/spots/` | `spot_0.png` to `spot_3.png` | 16x16, 1 bit masks | Painted onto Spinda's front at runtime from its personality value; positions are in code |
| `game/graphics/pokemon/question_mark/circled/`, `double/` | `front.png`, `anim_front.png`, `back.png`, `normal.pal`, `shiny.pal` | Battle-pic format | Placeholder for empty species slots (`SPECIES_NONE` and the unused slots); rarely seen |

The Egg's party icon is `egg/icon.png` and the placeholders' icons and footprint are icon and
footprint files; they are not made here.

If Spinda's replacement creature has no random markings, the spot masks can be left blank
(one empty mask each) instead of redrawn.

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** the Egg and the `question_mark` pics are battle pics (own 4bpp bank, front/back/frame 2
  share it, shiny same indices); `hatch.png` and `shard.png` use the Egg's bank (**locked** to `egg/normal.pal`);
  Spinda's spots are **1bpp** masks.
- **Theme (layer 2):** none (creature).
- **Post-processing:** as `sprite-creature-generator` for the pics; `enforce ... --pal egg/normal.pal` for the
  hatch and shard sheets; `enforce ... --bpp 1` for the spots; then `check`.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` the Emerald original, `suggested_path` the new name) and draws it to the vanilla layout.
3. Show the owner a few samples, iterate, then set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

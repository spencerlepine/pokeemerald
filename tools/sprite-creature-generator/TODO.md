# sprite-creature-generator

**Status:** TODO. Not built yet; this file marks the scope.

Companion battle sprites: front (2-frame anim), back, normal and shiny palettes, egg/hatch and form extras.

- **Categories:** A1, A2, A5
- **Wiki rows:** `pending_art.csv` kind `pokemon` (front, anim_front, back, palettes) for each species; 1,262 PNGs
- **Format in the game:** 64x64 front + 64x128 anim_front, 64x64 back, one 16-colour palette per species plus shiny

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

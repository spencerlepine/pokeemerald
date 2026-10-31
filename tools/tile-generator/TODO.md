# tile-generator

**Status:** TODO. Not built yet; this file marks the scope.

Overworld tilesets per planet and building, their tile animations, metatiles, and battle backgrounds.

- **Categories:** D1, D2, E1
- **Wiki rows:** `pending_art.csv` kinds `tileset` and `battle_environment`; 247 PNGs plus their .pal, metatiles.bin and tilemaps
- **Format in the game:** 8x8 tiles in 128-wide sheets, 16-colour palettes (primary 0-5, secondary 6-12), metatiles + attributes

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

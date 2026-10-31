# sprite-walker-generator

**Status:** TODO. Not built yet; this file marks the scope.

Overworld walking sprites: people (player, rivals, NPCs), overworld companions, placed dolls and cushions.

- **Categories:** A6, B3, C4
- **Wiki rows:** `pending_art.csv` kind `object_events`; 207 PNGs
- **Format in the game:** 16x32 nine-frame sheet (plus 32x32, 16x16, bike, surf, fish and field-move sheets), shared NPC palettes

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

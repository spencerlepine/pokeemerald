# sprite-trainer-back-generator

**Status:** IN-REVIEW. The tool is built (`trainer_back_sprite/`); Kael, Mira, Luke and Leia mockups are in `output/`. This file is the original scope.

Player and partner battle back sprites (the capture-pod throw).

- **Categories:** B2
- **Wiki rows:** `pending_art.csv` kind `trainers` (back pics); 8 PNGs
- **Format in the game:** 4-5 frames of 64x64, palette in graphics/trainers/palettes

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

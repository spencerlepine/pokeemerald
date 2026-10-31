# sprite-trainer-generator

**Status:** TODO. Not built yet; this file marks the scope.

Trainer battle portraits and Prof. Korr's intro portrait.

- **Categories:** B1, B4
- **Wiki rows:** `pending_art.csv` kind `trainers` (front pics) and `birch_speech`; 95 PNGs
- **Format in the game:** 64x64, one frame, own 16-colour palette

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

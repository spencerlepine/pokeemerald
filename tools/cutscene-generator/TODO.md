# cutscene-generator

**Status:** TODO. Not built yet; this file marks the scope.

Title screen, intro movie, credits, the titan/EXOGORTH scene, evolution, trade and shuttle-ride scenes.

- **Categories:** G1, G2, G3, G4
- **Wiki rows:** `pending_art.csv` kinds `title_screen`, `intro`, `credits`, `rayquaza_scene`, `evolution_scene`, `trade`, `cable_car`; 83 PNGs
- **Format in the game:** BG tiles + large OBJ actors

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

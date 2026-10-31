# sprite-icon-generator

**Status:** TODO. Not built yet; this file marks the scope.

Small fixed-size stills: item icons, fruit (berries), decoration icons, capture pods in battle, type labels, companion party icons and Datapad footprints.

- **Categories:** A3, A4, C1, C2, C3, C5, C6
- **Wiki rows:** `pending_art.csv` kinds `items`, `berries`, `decorations`, `balls`, `types`, plus `pokemon` icon/footprint files; 1,144 PNGs
- **Format in the game:** 24x24 items, 48x48 fruit, 32x64 two-frame party icons, 16x16 footprints, 32x16 labels

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

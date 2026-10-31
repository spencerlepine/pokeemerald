# ui-skin-generator

**Status:** TODO. Not built yet; this file marks the scope.

Tile-based screens: text windows, map popups, region map, battle HUD, menus, Datapad, comlink, PC, trainer card, minigames, Grand Arena screens.

- **Categories:** D7, D8, E2, F1, F3-F10, H1-H5
- **Wiki rows:** `pending_art.csv` UI kinds (`text_window`, `map_popup`, `battle_interface`, `pokedex`, `pokenav`, `pokemon_storage`, ...); 488 PNGs. Mostly kept: only re-skin what reads as Pokémon
- **Format in the game:** tiles + tilemap + palette per screen

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

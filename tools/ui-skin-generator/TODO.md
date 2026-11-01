# ui-skin-generator

**Status:** TODO. Not built yet; this file marks the scope.

Tile-based screens: text windows, map popups, region map, battle HUD, menus, Datapad, comlink, PC, trainer card, minigames, Grand Arena screens.

- **Categories:** D7, D8, E2, F1, F3-F10, H1-H5
- **Wiki rows:** `pending_art.csv` UI kinds (`text_window`, `map_popup`, `battle_interface`, `pokedex`, `pokenav`, `pokemon_storage`, ...); 488 PNGs. Mostly kept: only re-skin what reads as Pokémon
- **Format in the game:** tiles + tilemap + palette per screen

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** BG tiles + tilemap per screen, 4bpp (a few 8bpp: region maps, frontier pass); text
  uses 3 entries of its bank (fill, shadow, background) and the window frames sit in BG banks 14-15 in the overworld.
- **Theme (layer 2):** the `hud` group, **strict** for surfaces and text (`--strict-theme`); gold is the only cursor
  colour; HP and status colours only from `status-and-accents`. Creature art on these screens keeps its own bank.
- **Post-processing:** `enforce raw.png screen.png --bpp 4 --theme hud --strict-theme --write-pal screen.pal`, then
  `check --tile --theme hud --strict-theme`.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

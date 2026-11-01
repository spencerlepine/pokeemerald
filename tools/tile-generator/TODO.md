# tile-generator

**Status:** TODO. Not built yet; this file marks the scope.

Overworld tilesets per planet and building, their tile animations, metatiles, and battle backgrounds.

- **Categories:** D1, D2, E1
- **Wiki rows:** `pending_art.csv` kinds `tileset` and `battle_environment`; 247 PNGs plus their .pal, metatiles.bin and tilemaps
- **Format in the game:** 8x8 tiles in 128-wide sheets, 16-colour palettes (primary 0-5, secondary 6-12), metatiles + attributes

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** 4bpp 8x8 tiles. Every tile uses **one** 16-colour bank. Overworld banks: primary tileset
  0-5, secondary 6-12; 13-15 are the UI's (never use them). Tile animations reuse their tileset's banks; weather
  and day/night tint the banks at runtime. Battle backgrounds have their own banks. `check --tile`.
- **Theme (layer 2):** a **planet theme per biome**. None exist yet: before the first biome, add a
  `## Planet: <name>` section (GBA-step hex, roles) to `../../wiki/bible/PALETTE.md`, so it becomes a theme id.
  Imperial and Rebel interiors use `imperial-order` / `alliance-dawn`; battle backgrounds use `battle-backdrop`
  (mid-tones, so sprite outlines stay visible).
- **Post-processing:** decide the bank's 15 colours first (`enforce sample.png x.png --theme <planet> --write-pal bank.pal`),
  then map every tile onto its bank with `enforce tile_raw.png tiles.png --pal bank.pal`, and `check --tile --pal`.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

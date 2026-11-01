# sprite-icon-generator

**Status:** TODO. Not built yet; this file marks the scope.

Small fixed-size stills: item icons, fruit (berries), decoration icons, capture pods in battle and type labels. Creature icons and footprints are not made here.

- **Categories:** C1, C2, C3, C5, C6
- **Wiki rows:** `pending_art.csv` kinds `items`, `berries`, `decorations`, `balls`, `types`; 340 PNGs
- **Format in the game:** 24x24 items, 48x48 fruit, 16x48 capture pods (3 frames), 32x16 labels

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** 4bpp. Items (24x24) and fruit (48x48) own a bank each (`graphics/items/icon_palettes/`);
  decorations, capture pods and type labels share small banks with each other (**locked**: map onto the vanilla
  `.pal` the row's file uses).
- **Theme (layer 2):** type and category labels use the `hud` group (they sit on menus); faction items use their
  faction theme; everything else is free but must not use the gold cursor colour as its main colour.
- **Post-processing:** `enforce raw.png icon.png --bpp 4 --key auto --colours 15 --write-pal icon.pal` (own bank)
  or `--pal <shared>.pal`, then `check`.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

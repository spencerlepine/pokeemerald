# cutscene-generator

**Status:** READY (owner, 2026-11-01: "ready to be used"). The tool is pxl (vendored from crsolver/claude-pxl, MIT) plus GBA output; one prototype
scene (intro scene 2, the bike ride, as KAEL's speeder ride on Tatooine) builds into a working ROM. That scene is a
draft: the owner liked the backgrounds and parallax, the foreground characters need another pass. It is not imported.
Start with [GBA.md](GBA.md) (how art becomes game files) and [STYLE.md](STYLE.md) (what to match).

Title screen, intro movie, credits, the titan/EXOGORTH scene, evolution, trade and shuttle-ride scenes.

- **Categories:** G1, G2, G3, G4
- **Wiki rows:** `pending_art.csv` kinds `title_screen`, `intro`, `credits`, `rayquaza_scene`, `evolution_scene`, `trade`, `cable_car`; 83 PNGs
- **Format in the game:** BG tiles + large OBJ actors

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** enforced by the tool: `gba()` checks every target against its 16-colour `pal` and the
  tile/OBJ budgets, and `pal` colours off a GBA step are truncated with a warning. `scripts/rom-preview.sh` runs
  `palette-enforcer audit` on the scene output before it builds a ROM.
- **Theme (layer 2):** per scene: `kyber-gold` for title/branding, the faction themes for characters, a planet
  theme (add it to `../../wiki/bible/PALETTE.md` first) for backgrounds. Palette-cycled entries keep their index.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

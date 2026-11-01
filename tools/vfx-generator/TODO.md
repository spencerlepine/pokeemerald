# vfx-generator

**Status:** TODO. Not built yet; this file marks the scope.

Animated effects: field effects (grass, sand, ash, ripples, emotes), doors, field objects, weather, move-animation particles, battle transitions, and the VFX rows (status/general/special battle animations, net-new VFX like hyperspace and lightsabers).

- **Categories:** D3, D4, D5, D6, E3, E4
- **Wiki rows:** `pending_art.csv` kinds `field_effects`, `door_anims`, `weather`, `battle_anims`, `battle_transitions`, `rotating_gates`, `battle_animation` and every `vfx_*` kind; 513 PNGs + 170 VFX rows
- **Format in the game:** small multi-frame OBJ sheets and BG overlays; animation scripts stay as they are unless the row is HOTSWAP or NET_NEW

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** 4bpp OBJ sheets and BG overlays. Many effects share a bank by tag (field effects, doors
  and weather reuse NPC or tileset colours), and some animations **fade or cycle entries by index** in code: those
  indices are locked. Map onto the vanilla `.pal` unless the row is NET_NEW.
- **Theme (layer 2):** lightsabers and blasters from the faction themes (`Saber Blue`, `Saber Red`, `Signal Red`),
  weather from the planet theme of its map, hyperspace from `kyber-gold` / `hyperspace-console`.
- **Post-processing:** `enforce raw.png fx.png --pal <vanilla>.pal` (or `--theme ... --write-pal` for NET_NEW),
  then `check`.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

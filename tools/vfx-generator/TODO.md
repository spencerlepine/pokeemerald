# vfx-generator

**Status:** TODO. Not built yet; this file marks the scope.

Animated effects: field effects (grass, sand, ash, ripples, emotes), doors, field objects, weather, move-animation particles, battle transitions, and the VFX rows (status/general/special battle animations, net-new VFX like hyperspace and lightsabers).

- **Categories:** D3, D4, D5, D6, E3, E4
- **Wiki rows:** `pending_art.csv` kinds `field_effects`, `door_anims`, `weather`, `battle_anims`, `battle_transitions`, `rotating_gates`, `battle_animation` and every `vfx_*` kind; 513 PNGs + 170 VFX rows
- **Format in the game:** small multi-frame OBJ sheets and BG overlays; animation scripts stay as they are unless the row is HOTSWAP or NET_NEW

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

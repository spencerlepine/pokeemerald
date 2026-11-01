# sfx-generator

**Status:** TODO. Not built yet; this file marks the scope.

Sound effects: the 26 mapped ones (capture pods, comlink, doors, hover-bike, kyber, freighter) and 17 net-new (blaster, lightsabers, Force, turbolaser, hyperspace, astromech, Vader's breath...).

- **Categories:** audio: sfx
- **Wiki rows:** `pending_audio.csv` category `sfx`, swap_kind HOTSWAP or NET_NEW: 43 rows (277 KEEP rows need nothing)
- **Format in the game:** MIDI-driven SE in sound/songs/midi/ (se_*.mid) using the existing voicegroups, or a new direct-sound sample

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

Not applicable: audio, no art.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

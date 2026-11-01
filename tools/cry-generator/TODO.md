# cry-generator

**Status:** TODO. Not built yet; this file marks the scope.

One cry per companion: creature calls, droid beeps and servos.

- **Categories:** audio: cry
- **Wiki rows:** `pending_audio.csv` category `cry`, HOTSWAP: 386 rows
- **Format in the game:** short mono .wav in sound/direct_sound_samples/cries/ (converted to .bin at build), same cry-table slot

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

Not applicable: audio, no art.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

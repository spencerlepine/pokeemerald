# music-generator

**Status:** TODO. Not built yet; this file marks the scope.

Background music, battle music and fanfares, from the briefs in the wiki.

- **Categories:** audio: music
- **Wiki rows:** `pending_audio.csv` category `music`: 140 HOTSWAP + 5 NET_NEW (70 ghost rows are deletions, nothing to make)
- **Format in the game:** MIDI in sound/songs/midi/, played by the GBA m4a engine with the existing voicegroups; original compositions, never film quotes

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

Not applicable: audio, no art.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

# music-generator

**Status:** TODO. Not built yet; this file marks the scope.

Background music, battle music and fanfares, from the briefs in the wiki.

- **Categories:** audio: music
- **Wiki rows:** `music.csv`, one row per song: 178 with `rewrite_status` TODO (140 HOTSWAP + 38 NET_NEW, 29 of them per-planet versions of town, route and dungeon songs Emerald shares across planets). The 70 ghost rows (never played in Emerald) and `MUS_DUMMY` are SKIP. Same rows as `pending_audio.csv` category `music`, plus labels and tech notes.
- **Labels:** `music_category` (TOWN, ROUTE, BATTLE, FANFARE…) and `music_form` (`LOOP`, `AMBIENT`, `CUE`, `JINGLE`); see `wiki/mapping/README.md` (`music.csv`).
- **Tech notes per row:** `player` (BGM or the fanfare player), `voicegroup`, `volume`, `reverb`, `midi_tracks`, `tempo_bpm`, `length_s`, `loops` (the Emerald file's `[` `]` loop markers), `tech_notes`. Keep a song's loop/no-loop and roughly its length so scripts that wait on it still line up.
- **Names:** `wiki_title` is the Emerald constant until the song gets its Star Wars title (`sw_title` in `wiki/mapping/music.csv`).
- **Format in the game:** MIDI in sound/songs/midi/, played by the GBA m4a engine with the existing voicegroups; original compositions, never film quotes

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

Not applicable: audio, no art.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE` (`audio_status` in `pending_audio.csv`; `rewrite_status` in `music.csv` follows `game_status`).

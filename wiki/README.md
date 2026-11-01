# Star Wars Emerald wiki

Every Pokémon Emerald row (creature, character, place, item, move, trainer, line of dialogue, story event,
art file, visual effect, music track, sound effect, cry) mapped to its Star Wars replacement, keyed by the same Emerald id. The mapping is finished and
approved. **`database/` is the source of truth** for porting it into the game source in [`../game`](../game).

The wiki and `../game` never import each other. Content is copied into the game by hand, piece by piece.

## Porting into the game

Three lists drive the work. All live in `database/` and can be browsed with `python3 wiki/server.py`.

- **Art:** `pending_art.csv`, one row per image, move animation and visual effect (battle status/general/special
  animations, field effects, weather, battle transitions), including the art that net-new rows need.
  `art_status` says what to draw.
- **Audio:** `pending_audio.csv`, one row per music track, sound effect and companion cry in `../game`, plus net-new
  sounds. `audio_status` says what to compose or record; `sw_subject` is the brief and `priority` the order.
- **Music:** `music.csv`, one row per song (every `MUS_*` track in `../game` plus net-new songs), labelled by
  `music_category` and `music_form`, with `rewrite_status` (TODO for every song the player hears) and tech notes
  read from the MIDI files. `music_by_map.csv` lists the song each map plays, by planet.
- **Game port:** `game_port.csv`, one row per thing to change in `../game`: every entity, line of text,
  story event and art file.
  - `game_file` / `game_line`: where it lives in `../game`.
  - `wiring`: what it is tied to (map, sprite, script, speaker, flags, trainers), so dialogue and events stay hooked up.
  - `depends_on`: what must land first.
  - `notes`: things to check, such as a menu string wider than Emerald's (`ui_wider_px` in `texts.csv`) whose
    window must fit it.

Approved new art lives in [`art/`](art) at the same path it has in `../game` (`art/graphics/...`), listed in
`mapping/art_ready.csv`. `python3 tools/mark_art_ready.py` applies that list to `database/` (a full rebuild does too).
Approved sounds installed into `../game` are listed in `mapping/audio_done.csv`; `python3 tools/mark_audio_done.py`
applies it the same way.

When a row is in the game, set `game_status` to `DONE` in its source table (named in `table`) and rebuild.
`game_port.csv` is generated from those tables. Net-new content (`NET_NEW` rows) is built after all
hotswaps, following [`bible/NET_NEW_DESIGNS.md`](bible/NET_NEW_DESIGNS.md).

## Statuses

| Column | Values | Meaning |
|---|---|---|
| `swap_kind` | `HOTSWAP` | 1:1 replacement (same id and numbers, new name and lore). |
| | `KEEP` | Generic term kept as is (natures, most moves, TM labels, unused slots). |
| | `NET_NEW` | New content with no Emerald counterpart. |
| `map_status` | `DONE` | The Star Wars version is written and approved (every row). |
| `art_status` | `PENDING_ART` | Uses the renamed Emerald art until it is redrawn. |
| | `NEEDS_PLACEHOLDER` | Net-new: copy the asset named in `placeholder_from` first. |
| | `KEEP_ANIM` / `KEEP_ART` / `NO_ART` | Reuse the existing animation or art, or nothing to draw. |
| | `ART_READY` | New art drawn and approved by the owner, stored in `art/<path>`; still to be copied into `../game` (`game_status` says when). |
| `audio_status` | `PENDING_AUDIO` | Mapped: the Emerald sound plays as a placeholder until the Star Wars one replaces it (same song / cry id). |
| | `NEEDS_PLACEHOLDER` | Net-new: copy the sound named in `placeholder_from` under the new name first. |
| | `KEEP_AUDIO` / `NO_AUDIO` | Reuse the Emerald sound as is, or nothing to make. |
| | `DONE` | The new sound is approved and installed in `../game` by cry-generator or sfx-generator (`made_by`), listed in `mapping/audio_done.csv`. Net-new SEs keep `game_status` `NOT_STARTED` until something calls them. |
| `game_status` | `NOT_STARTED` / `DONE` | Whether the row has landed in `../game`. For a `CUT` row, `DONE` means deleted. |

Object-event rows (overworld sprites) also carry **`frame_size`** (pixels per frame, e.g. `16x32`, read from
the `-mwidth/-mheight` conversion flags in `../game/src/data/object_events/object_event_graphics.h`) and
**`size_class`**: `SMALL` is one map tile wide (16x16 and 16x32 frames: people, berry trees, small Pokémon), `LARGE`
is wider (32x32 and up: bikes, big Pokémon, legendaries). `python3 tools/frame_sizes.py` refreshes both without a
full rebuild. The walker generator's people kit covers `frame_size` `16x32`.
Query: `grep ',16x32,SMALL,' database/pending_art.csv`.

`todo` is **`HUMAN-TODO`** on art rows a person replaces by hand, with no generator tool: the game logo, the
title screen, the intro and credits, story cutscenes, and every menu image with Pokémon branding baked in (POKéDEX /
POKéNAV / HOENN text, Poké Ball icons, the Pikachu diploma, type labels, wallpapers with Pokémon). Their decisions
are in `mapping/branding.csv`, which also holds `brand:*` rows for branding that is not an image (the ROM header
title in `Makefile`). Menu art without Pokémon branding there is `KEEP_ART`.
Query: `grep HUMAN-TODO database/pending_art.csv`.

`swap_kind` also takes **`CUT`**: a **ghost row**, an Emerald asset that is not in the Star Wars game (unused FireRed
songs, never-played sound effects, unused art and field effects). Ghost rows are never added to the game; they stay
in the wiki so the port knows what to delete and can tell what has been deleted (`game_status` `DONE`). Song, cry
and field-effect ids are table indexes, so deleting a ghost keeps its slot (point it at a silent song or cry).
`replaced_by` names the row that takes a ghost's place, if any.

## Tables (database/, generated)

| Table | What it is |
|---|---|
| `game_port.csv` | The port checklist (above). |
| `swap_map.csv` | One row per Emerald entity plus every net-new row: old and new name, title and C constant (`SPECIES_TREECKO` → `SPECIES_WOOKLET`). |
| `entities.csv` | Emerald's entities with the Star Wars title and description; Emerald's stay in `emerald_title` / `emerald_description`. Stats and game columns are unchanged. |
| `texts.csv` | Every Emerald text with its Star Wars version (`sw_text_raw`), `source_file` / `source_line`, `overflow_risk` (wider than the 208 px text box) and `ui_wider_px`. |
| `text_terms.csv` | Term dictionary (glossary + every mapped name). |
| `pending_art.csv` | Every art asset and visual effect, who uses it, its Star Wars subject, a `suggested_path`, its `art_status` and `swap_kind`. VFX rows (`kind` `vfx_*`) point at `path:source_line` in `../game`. |
| `pending_audio.csv` | Every music track, sound effect, phoneme and cry: `emerald_constant` → `sw_constant`, the brief (`sw_subject`), where it plays (`used_in`, `used_by`), `source_file:source_line`, `asset_file`, `suggested_path`, `refs`, `priority`, `audio_status`, `swap_kind`. |
| `music.csv` | Every song, for `tools/music-generator`: `wiki_title` (the Star Wars title once named; the Emerald constant until then), `music_category`, `music_form`, `rewrite_status` (TODO / DONE / SKIP), `planets`, `map_count`, the brief, placeholder, `asset_file` → `suggested_path`, and tech notes from `../game` (`player`, `voicegroup`, `volume`, `reverb`, `midi_tracks`, `tempo_bpm`, `length_s`, `loops`, `tech_notes`). Built by `tools/build_music.py`. |
| `music_by_map.csv` | Every map with the song it plays (`MUS_NONE` = silent or set by a script), its planet and map type. |
| `timeline_events.csv` | The 45 story events, rewritten. |
| `net_new.csv` | Net-new content with placeholder, dependencies and balance notes. |
| `area_progression.csv` | Emerald's balance table (levels, badges, gating) with planet and new map titles. |
| `species_habitats.csv` | Why each wild companion lives where Emerald's encounter tables put it. Tables are unchanged. |
| `build_info.csv`, `build_warnings.csv` | Inputs, counts, warnings (must be 0). |

Unchanged game data (learnsets, parties, encounters, map events, scripts, flags) is not copied; it stays as is
in `../game`. Every `source_file` is a path relative to `../game`.

## Rules for the port

- Balance never changes in a HOTSWAP row (stats, levels, encounter rates, gating).
- Named characters are people, never companions. COMPANION replaces POKéMON; PC is a TERMINAL, TV is the HOLONET.
- New flags and vars use only Emerald's unused slots (listed in `bible/NET_NEW_DESIGNS.md`).
- Name limits: creature 10, move 12, item 14, ability 12, type 6, trainer class 12, trainer name 10, map name 16.
- [`bible/STORY.md`](bible/STORY.md) is the story: planets, factions, cast, acts.
- **World art:** [`bible/WORLD_ART.md`](bible/WORLD_ART.md) and `mapping/world_art.csv` are the source of truth for
  the new buildings, interiors, objects and nature each planet and town gets (with signal/noise placement rules and
  reference images in `art/concept/`).
- **Tilesets:** [`bible/TILESET_INSTALL.md`](bible/TILESET_INSTALL.md) lists every approved tile-generator recipe and what
  its import must do beyond copying files (per-planet copies of the shared General primary, map edits such as
  removing life buoys from Star Destroyer rooms). Read it before porting any tileset.
- [`bible/PALETTE.md`](bible/PALETTE.md) is the chosen color themes (title screen, factions, HUD and menus), enforced by the art tools through `tools/palette-enforcer`; the hardware rules are in [`../tools/PALETTES.md`](../tools/PALETTES.md).

## Sound and visual effects

`tools/scan_game_assets.py` walks `../game` and writes `mapping/asset_inventory.csv` (every song, sound effect, cry and
VFX, with its source line and where the game uses it). The Star Wars decision for each is hand-written in
`mapping/audio.csv` and `mapping/vfx.csv`; the build warns about any inventory row without a decision, so a new asset
cannot be missed. Images were already complete: all 4,076 PNGs under `graphics/` and `data/tilesets/` are rows in
`pending_art.csv` (check: every PNG path in `../game` is a `path` there).

The current pass (all `DRAFT`, waiting for the owner's review):

- **Music** (211 Emerald songs): 140 mapped to a Star Wars track with a brief, 70 ghosts (FireRed/LeafGreen and
  beta songs Emerald never plays), `MUS_DUMMY` kept. 5 net-new tracks: Fortress Vader, VS Vader, VS Boba Fett, the
  Death Star site, hyperspace travel. Briefs ask for original music, never quotes of the film scores.
- **Sound effects** (269 + 51 bard phonemes): 277 reused as is (UI, field, most move sounds, the phonemes),
  26 mapped (capture pods, comlink, blast doors, hover-bike, kyber hum, the opening freighter), 17 ghosts
  (never played). 17 net-new: blaster bolt, lightsaber ignite / swing / clash / hum, Force push / choke / lightning,
  turbolaser, ion cannon, vibroblade, slicer spike, hyperspace jump, astromech chatter, Imperial alarm, Vader's
  breathing, TIE flyby. Each new move sound replaces the old one only in that move's animation.
- **Cries** (388): one per companion (droids get beeps and servos), derived from `mapping/species.csv`; 2 ghosts
  (unused slots).
- **VFX** (162 + 8 net-new): most animations are kept and only their sprites are redrawn (already in
  `pending_art.csv`). Mapped: transitions that draw Pokémon shapes or logos in code (capture pod, Cartel and Imperial
  crests, titans, Aurebesh instead of Braille, the Grand Arena logo), the Bacta Center heal, the EXOGORTH spotlight
  and the vault puzzle. Net-new: hyperspace jump, Vader and Boba Fett transitions, an overworld lightsaber, a field
  Force push, and the move animations for BLASTER SHOT, SABER SLASH and FORCE CHOKE.
- **Ghost art:** the 11 files in `graphics/unused/` and 3 unused field effects.

## Open decisions

- **Water on desert worlds.** Tatooine maps (Mos Eisley, Routes 103/104/109/110) have sea tiles and SURF works
  there. Option: draw those tiles as the DUNE SEA and theme SURF on Tatooine as sand-skimming (art only,
  mechanics unchanged). Dialogue is already neutral ("the water"). Not decided.
- **Optional extras**, not tracked as rows: a landing pad and shuttle at the Tatooine / Sullust border
  (`net:border-tatooine-sullust`), more invented creature names swapped for canon ones, and the ideas in
  `bible/STORY.md` section 8 that have no row yet (light / dark side evolution branches, blizzard weather).

## Rebuilding

`tools/build.py` regenerates `database/` from `mapping/` (hand-written rows, see
[`mapping/README.md`](mapping/README.md)) plus [`emerald/`](emerald/README.md), the read-only Emerald tables it
needs, copied into this repo. Nothing outside the repo is needed; starwars-db is optional (it only validates
`sw_basis` ids).

```sh
python3 tools/scan_game_assets.py   # mapping/asset_inventory.csv from ../game (re-run after the game changes)
python3 tools/build.py              # optional: STARWARS_DB_DIR=/path/to/starwars-db/database
python3 tools/habitats.py   # species_habitats.csv
python3 wiki/server.py      # browse at http://127.0.0.1:8000
```

A rebuild keeps every `game_status` DONE already in `database/` (ship tools write it there once an asset is in
`../game`), so it never un-ships anything. The Emerald tables in `emerald/` match the `wiki/database` folder of
commit `3ef77dfe` (before this wiki replaced it). The history of how the mapping was built (checklists, notes, coverage reports) is in git history.

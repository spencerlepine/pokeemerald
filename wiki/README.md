# Star Wars Emerald wiki

Every Pokémon Emerald row (creature, character, place, item, move, trainer, line of dialogue, story event,
art file) mapped to its Star Wars replacement, keyed by the same Emerald id. The mapping is finished and
approved. **`database/` is the source of truth** for porting it into the game source in [`../game`](../game).

The wiki and `../game` never import each other. Content is copied into the game by hand, piece by piece.

## Porting into the game

Two lists drive the work. Both live in `database/` and can be browsed with `python3 wiki/server.py`.

- **Art:** `pending_art.csv`, one row per image or animation (including the art that net-new rows need).
  `art_status` says what to draw.
- **Game port:** `game_port.csv`, one row per thing to change in `../game`: every entity, line of text,
  story event and art file.
  - `game_file` / `game_line`: where it lives in `../game`.
  - `wiring`: what it is tied to (map, sprite, script, speaker, flags, trainers), so dialogue and events stay hooked up.
  - `depends_on`: what must land first.
  - `notes`: things to check, such as a menu string wider than Emerald's (`ui_wider_px` in `texts.csv`) whose
    window must fit it.

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
| `game_status` | `NOT_STARTED` / `DONE` | Whether the row has landed in `../game`. |

## Tables (database/, generated)

| Table | What it is |
|---|---|
| `game_port.csv` | The port checklist (above). |
| `swap_map.csv` | One row per Emerald entity plus every net-new row: old and new name, title and C constant (`SPECIES_TREECKO` → `SPECIES_WOOKLET`). |
| `entities.csv` | Emerald's entities with the Star Wars title and description; Emerald's stay in `emerald_title` / `emerald_description`. Stats and game columns are unchanged. |
| `texts.csv` | Every Emerald text with its Star Wars version (`sw_text_raw`), `source_file` / `source_line`, `overflow_risk` (wider than the 208 px text box) and `ui_wider_px`. |
| `text_terms.csv` | Term dictionary (glossary + every mapped name). |
| `pending_art.csv` | Every art asset, who uses it, its Star Wars subject, a `suggested_path` and its `art_status`. |
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

## Open decisions

- **Water on desert worlds.** Tatooine maps (Mos Eisley, Routes 103/104/109/110) have sea tiles and SURF works
  there. Option: draw those tiles as the DUNE SEA and theme SURF on Tatooine as sand-skimming (art only,
  mechanics unchanged). Dialogue is already neutral ("the water"). Not decided.
- **Optional extras**, not tracked as rows: a landing pad and shuttle at the Tatooine / Sullust border
  (`net:border-tatooine-sullust`), more invented creature names swapped for canon ones, and the ideas in
  `bible/STORY.md` section 8 that have no row yet (light / dark side evolution branches, blizzard weather).

## Rebuilding

`tools/build.py` regenerates `database/` from `mapping/` (hand-written rows, see
[`mapping/README.md`](mapping/README.md)) plus the emerald-db and starwars-db databases:

```sh
EMERALD_DB_DIR=/path/to/emerald-db/database STARWARS_DB_DIR=/path/to/starwars-db/database python3 tools/build.py
python3 tools/habitats.py   # species_habitats.csv
python3 wiki/server.py      # browse at http://127.0.0.1:8000
```

The emerald-db database is the `wiki/database` folder of pokeemerald commit `3ef77dfe` (before this wiki
replaced it). The history of how the mapping was built (checklists, notes, coverage reports) is in git history.

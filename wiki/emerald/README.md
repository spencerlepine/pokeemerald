# emerald/: the Emerald snapshot the build reads

Read-only copy of the nine emerald-db tables that `tools/build.py`, `tools/habitats.py` and
`tools/gen_trainer_names.py` read, so the wiki rebuilds with nothing outside this repo. Never edit these
files; the Star Wars rewrite lives in `mapping/`.

| File | Read by |
|---|---|
| `entities.csv` | build.py (every Emerald entity), gen_trainer_names.py |
| `texts.csv` | build.py (every game text) |
| `art_assets.csv`, `entity_art.csv` | build.py (pending_art.csv, game_port.csv) |
| `story_flags.csv` | build.py (flag ids that net-new rows may reference) |
| `area_progression.csv` | build.py (balance table with planets) |
| `timeline_events.csv` | build.py (story events) |
| `build_info.csv` | build.py (`emerald_db_commit` in database/build_info.csv) |
| `wild_encounters.csv` | habitats.py |

Source: `database/` of [spencerlepine/emerald-db](https://github.com/spencerlepine/emerald-db), extracted from
pokeemerald commit `731ad5bf` (the same files as `wiki/database` at commit `3ef77dfe` of this repo). The other
emerald-db tables (dialogue, scripts, map events, parties, learnsets…) are not read by any tool here and are not copied.
To use a different snapshot, set `EMERALD_DB_DIR` to its folder.

Rows for Emerald assets that have been deleted from `../game` are deleted here too, so the wiki only lists what
the game has. Deleted so far: the FireRed/LeafGreen link leftovers RED and LEAF (trainer front and back pics,
overworld sprite, the `PKMN TRAINER RED` / `LEAF` trainers) and 72 never-loaded images (`graphics/unused/`, the Japanese
contest screens, unused battle-anim, battle-interface, intro, door, tileset and trade art).

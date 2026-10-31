# POPULATE-EMERALD-SW-DB-PROMPT

You are continuing the build of **emerald-sw-db**: the Star Wars rewrite of
emerald-db. Every Emerald character, creature, place, item, move, trainer,
line of dialogue, story beat and art file gets a Star Wars replacement here,
keyed by the **same Emerald id**. Hand this file to an agent and it can pick
up exactly where the last session stopped.

## Why this exists

Step 3 of a five-step project to rebuild Pokémon Emerald with Star Wars content:

1. `starwars-db`: Star Wars database (done, read-only reference).
2. `emerald-db`: snapshot of everything in the pokeemerald source (done, read-only).
3. **`emerald-sw-db` (this repo): the Star Wars version of every emerald-db row,
   with each row marked HOTSWAP (1:1 replacement), KEEP (generic, unchanged),
   NET_NEW (new content with no Emerald counterpart) or CUT, plus art status.**
4. Refactor the game source with `database/swap_map.csv` and `database/texts.csv`
   (find/replace by constant and text). Art stays Pokémon art but is renamed;
   anything new is copied from a placeholder asset and marked `PENDING_ART`.
5. Redraw all art, driven by `database/pending_art.csv`.

Precision and consistency matter more than prose. Game balance (stats, levels,
encounter rates, gating) must not change in a HOTSWAP row; anything that would
change balance is a NET_NEW row with a `balance_note`.

## Setup

Clone side by side. **Only emerald-sw-db is written to.**

```sh
git clone https://github.com/spencerlepine/emerald-sw-db.git
git clone https://github.com/spencerlepine/emerald-db.git     # read-only
git clone https://github.com/spencerlepine/starwars-db.git    # read-only
git clone https://github.com/spencerlepine/pokeemerald.git    # read-only, optional (emerald-db already has the data)
cd emerald-sw-db
python3 tools/build.py      # mapping/ + ../emerald-db/database -> database/
python3 tools/coverage.py   # progress/COVERAGE.md
python3 wiki/server.py      # optional: http://127.0.0.1:8000
```

Python 3.10+ standard library only. Set `EMERALD_DB_DIR` / `STARWARS_DB_DIR`
if the other repos are not next to this one.

## Rules

- **Never push to emerald-db, starwars-db or pokeemerald.**
- **Never hand-edit `database/`.** Edit `mapping/*.csv` (or `bible/`, `tools/`)
  and rebuild.
- **`bible/STORY.md` is the creative source of truth.** If a mapping row
  disagrees with it, fix one of them on purpose and note it in
  `progress/NOTES.md`.
- **HOTSWAP never changes numbers.** Same stats, types, levels, locations,
  evolution methods. A rename + re-theme only.
- **Named characters are people, never creatures.** Only species and droid
  models are catchable. There is one player, picked at the start (boy or girl),
  with no switching.
- Respect in-game name limits: creature 10, move 12, item 14, ability 12,
  type 6, trainer class 12, trainer name 10, map name 16. `build.py` warns.
- English only.
- Commit and push after every chunk, straight to `main`. Commit as
  `spencerlepine <60903378+spencerlepine@users.noreply.github.com>` with **no
  Co-Authored-By trailer**.
- Before committing: `python3 tools/build.py` must end with **0 warnings**,
  then run `python3 tools/coverage.py`.

## How to resume

1. Read `progress/CHECKLIST.md`. The first chunk that is not `[x]` is your
   job. `[~]` means a previous session started it: check `git log` and the
   session log at the bottom of the checklist.
2. Read `progress/COVERAGE.md` for the numbers.
3. Read `bible/STORY.md` (the story) and `README.md` (the schema).
4. Do the chunk. Rebuild, run coverage, tick the box, append a log line,
   commit, push. Repeat.
5. If the session ends mid-chunk, mark it `[~]`, write what's left in the
   log line, commit and push. Nothing should live only in your context.

Decisions and open questions go in `progress/NOTES.md`.

## Layout

```
POPULATE-EMERALD-SW-DB-PROMPT.md  this file (single entry point)
README.md                         schema, statuses, queries
bible/STORY.md                    setting, planets, factions, cast, acts, creature rules
mapping/*.csv                     the hand-written Star Wars rows (see mapping/README.md)
mapping/texts/*.csv               curated dialogue rewrites (one file per area)
tools/build.py                    mapping + emerald-db -> database/
tools/coverage.py                 progress/COVERAGE.md
progress/CHECKLIST.md             chunked work list + session log
progress/COVERAGE.md              generated
progress/NOTES.md                 decisions, gotchas, open questions
database/                         generated tables
wiki/                             read-only browser for database/
```

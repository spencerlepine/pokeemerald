# Star Wars Emerald DB

The Star Wars rewrite of [emerald-db](https://github.com/spencerlepine/emerald-db):
every Pokémon Emerald row (creature, character, place, item, move, trainer,
line of dialogue, story beat, art file) mapped to its Star Wars replacement,
keyed by the same Emerald id. Lore comes from
[starwars-db](https://github.com/spencerlepine/starwars-db); the game is
[pokeemerald](https://github.com/spencerlepine/pokeemerald).

**Resuming work?** Start at [`POPULATE-EMERALD-SW-DB-PROMPT.md`](POPULATE-EMERALD-SW-DB-PROMPT.md).
Story: [`bible/STORY.md`](bible/STORY.md) ·
progress: [`progress/CHECKLIST.md`](progress/CHECKLIST.md) ·
coverage: [`progress/COVERAGE.md`](progress/COVERAGE.md).

## Build

```sh
# emerald-db and starwars-db cloned next to this repo
python3 tools/build.py      # regenerate database/
python3 tools/coverage.py   # refresh progress/COVERAGE.md
python3 tools/habitats.py   # refresh progress/HABITATS.md (wild companions vs. home planets)
python3 wiki/server.py      # browse at http://127.0.0.1:8000
```

## Statuses

Every row carries four status columns:

| Column | Values | Meaning |
|---|---|---|
| `swap_kind` | `HOTSWAP` | 1:1 replacement of an Emerald row (same id, same numbers, new name and lore). Step 4 can apply these with find/replace. |
| | `KEEP` | Generic game term kept as is (natures, most moves, TM labels, unused slots). |
| | `NET_NEW` | New content with no Emerald counterpart (`mapping/net_new.csv`). Step 4 builds these *after* all hotswaps. |
| | `CUT` | Emerald content to remove (none yet). |
| `map_status` | `TODO` / `DRAFT` / `DONE` / `IDEA` | Authoring state in this DB. `DRAFT` = a Star Wars version exists but has not been reviewed. `IDEA` = net-new proposal not designed yet. |
| `art_status` | `PENDING_ART` | Uses (renamed) Emerald art for now; must be redrawn in Step 5. |
| | `NEEDS_PLACEHOLDER` | Net-new: Step 4 must copy an existing asset (`placeholder_from`) first. |
| | `KEEP_ANIM` / `KEEP_ART` / `NO_ART` | Reuse the existing animation / art, or nothing to draw. |
| `game_status` | `NOT_STARTED` | Step 4 updates this as rows land in the game. |

## Tables (database/, generated)

| Table | What it is |
|---|---|
| `swap_map.csv` | **The Step 4 table.** One row per Emerald entity plus every NET_NEW row: `emerald_id, sw_id, entity_type, swap_kind, map_status, art_status, game_status, emerald_name, sw_name, emerald_title, sw_title, emerald_constant, sw_constant, planet, sw_basis, sw_description, notes, derived_from`. `sw_constant` is the proposed new C constant (`SPECIES_TREECKO` → `SPECIES_WOOKLET`). |
| `entities.csv` | Emerald `entities.csv` with `title` / `description` replaced by the Star Wars version and the status columns added; the Emerald values stay in `emerald_title` / `emerald_description`. All stats and game columns are unchanged. |
| `texts.csv` | Every Emerald text block: `emerald_text_raw`, `sw_text_raw`, `text_status` (`CURATED` hand-written, `AUTO` names and terms swapped, `UNCHANGED`), `terms_applied`, `overflow_risk` (a line is wider than the 208 px text box in Emerald's font, see `progress/NOTES.md`). |
| `text_terms.csv` | The term dictionary the auto drafts used (glossary + every mapped name), plus ambiguous terms that were left alone. |
| `pending_art.csv` | Every art asset (PNG or move animation), the entities that use it, the Star Wars entity, a `suggested_path` with the new name, and its `art_status`. |
| `area_progression.csv` | Emerald's balance table (levels, badges expected, gating) with `planet` and `sw_map_title`. Use it before adding or moving anything. |
| `timeline_events.csv` | The 45 Emerald story events with the Star Wars version (`emerald_title` / `emerald_description` kept). |
| `net_new.csv` | All net-new content with placeholder source, dependencies and balance notes. |
| `build_info.csv`, `build_warnings.csv` | Inputs, counts, warnings (must be 0 before committing). |

Unchanged game data (learnsets, parties, encounters, map events, scripts,
flags) is not copied: join emerald-db's tables on the same ids.

## Hand-written input (mapping/)

See [`mapping/README.md`](mapping/README.md). One CSV per area
(`species`, `characters`, `items`, `moves`, `types`, `abilities`, `badges`,
`trainer_classes`, `locations`, `glossary`, `net_new`, `timeline`), keyed by
`emerald_id`. Trainers, maps and texts are mostly *derived* from these.

## Queries

```sh
# everything still waiting for art
python3 -c "import csv;print(sum(r['art_status']=='PENDING_ART' for r in csv.DictReader(open('database/pending_art.csv'))))"
# every net-new item
grep NET_NEW database/swap_map.csv
# all hotswaps for creatures, old -> new constant
python3 -c "import csv;[print(r['emerald_constant'],r['sw_constant']) for r in csv.DictReader(open('database/swap_map.csv')) if r['entity_type']=='species' and r['swap_kind']=='HOTSWAP']"
```

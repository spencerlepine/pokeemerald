# mapping/ (hand-written)

Every file is keyed by `emerald_id` (the id from emerald-db) and carries
`swap_kind`, `map_status`, `art_status`. `tools/build.py` merges these onto
emerald-db and writes `database/`. Rows not listed in any file default to
`HOTSWAP / TODO` (or `KEEP` for generic mechanics).

| File | Rows | Extra columns |
|---|---|---|
| `species.csv` | all 386 creatures | `sw_basis` (starwars-db id, `canon:<name>` or `original`), `home_planet`, `sw_description` (datapad concept), `habitat_note` (where Emerald's wild placement doesn't fit the new planet) |
| `characters.csv` | 59 characters + 25 organizations | `sw_title`, `home_planet`, `role`, `canon_note` (how it bends canon), `text_terms` (`OLD=>NEW` pairs used in dialogue and trainer names) |
| `trainer_classes.csv`, `badges.csv`, `types.csv`, `abilities.csv`, `moves.csv`, `items.csv` | | `sw_basis`, `sw_description`, `notes` |
| `locations.csv` | 213 region-map sections | `planet`. Map titles (`map:*`) are derived: location name + room. |
| `glossary.csv` | | `emerald_term, sw_term`: generic words (POKéMON → COMPANION). Wins over names derived from entities. |
| `net_new.csv` | | `id` (`net:*`), `placeholder_from` (Emerald asset or map to copy), `depends_on` (flag / item), `balance_note` |
| `trainers.csv` | 489 generic trainer names | `key` (`name:<EMERALD NAME>` shared by rematches, or a `trainer:<id>` override, used for the 53 GRUNTs), `emerald_name`, `sw_name`, `notes`. Seeded by `tools/gen_trainer_names.py` (same first letter and gender, deterministic); edit freely, re-runs only add missing rows. |
| `timeline.csv` | 45 story events | `emerald_event_id, sw_title, sw_tagline, sw_description, sw_lore, planet, map_status` |
| `texts/*.csv` | curated dialogue | `text_id, sw_text_raw, notes`. Keep Emerald's control codes (`\n`, `\l`, `\p`, `$`, `{PLAYER}` …). Generated from `texts/specs/*.py` with `tools/curate_texts.py` (edit the spec, re-run); the CSV is what the build reads. |
| `asset_inventory.csv` | 1,081 sound and VFX assets | **Generated** by `tools/scan_game_assets.py` from `../game`; never edit. One row per music track, sound effect, phoneme, cry, battle status/general/special animation, field effect, weather and battle transition, with `source_file` / `source_line`, `asset_file`, `refs` (where the game uses it) and `used_by` (maps, moves, species, sprite tags). |
| `audio.csv` | every music track and sound effect, cry overrides, net-new audio | `asset_id` (inventory id or `net:*`), `sw_constant` (new song constant), `swap_kind`, `map_status`, `audio_status`, `priority` (1 heard constantly, 2 story moments, 3 rare), `sw_subject` (the brief for the composer / sound designer), `placeholder_from`, `replaced_by`, `depends_on`, `notes`. Cries without a row are derived from `species.csv`. |
| `vfx.csv` | every VFX inventory row, net-new VFX, ghost overrides for existing art rows | `asset_id`, `swap_kind`, `map_status`, `art_status`, `sw_subject`, `placeholder_from`, `replaced_by`, `depends_on`, `notes`. A row whose id is a `pending_art.csv` asset (e.g. `graphics/unused/*.png`) overrides that row. |
| `branding.csv` | every title screen, intro, credits, cutscene and menu image, plus `brand:*` rows | same columns as `vfx.csv` plus `todo` (`HUMAN-TODO` = replace by hand, no tool) and `path` / `source_line` for `brand:*` rows (e.g. the ROM title in `Makefile`). Overrides those rows in `pending_art.csv`: `HOTSWAP` + `HUMAN-TODO` where Pokémon branding must go, `KEEP_ART` for generic UI. |

Name limits: creature 10, move 12, item 14, ability 12, type 6, trainer
class 12, trainer name 10, map name 16.

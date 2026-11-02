# Agent notes

Every session reads this file. The wiki and tool indexes are pulled in below; the handoff notes follow.

# Wiki

@wiki/README.md

# Tools

@tools/README.md

# Handoff / Notes

A Star Wars conversion of Pokémon Emerald (owner: spencer, GitHub `spencerlepine`). Setting: 2 BBY, an
alternate telling. Twelve planets plus a post-game; PokéNAV is called **StarNAV** in every doc.

| Path | What it is |
|---|---|
| `game/` | The pret/pokeemerald C source. Content is ported in by hand, later. |
| `wiki/` | **The source of truth.** Every Emerald entity mapped to its Star Wars version ([`wiki/README.md`](wiki/README.md)), the story ([`wiki/bible/STORY.md`](wiki/bible/STORY.md)), and the world. |
| `wiki/world/` | The world: all 528 areas as tile layouts, placed on one connected world map ([`wiki/world/README.md`](wiki/world/README.md)). Keep this map; sizes may grow later. |
| `wiki/mapping/world_art.csv` | Every world piece (building, object, nature, landmark, interior kit) with its status, model and notes. |
| `wiki/mapping/terrain.csv` | Every terrain tile the game needs: one row per tileset, item and role (`terrain:general:cliff:ne`), with the vanilla metatile it uses (`use`, empty = missing, placeholder), planets, areas and status. Real-size sheets in `wiki/world/greybox/sheets/`. `terrain_areas.csv` links areas to rows. |
| `tools/` | One tool per asset group, listed in [`tools/README.md`](tools/README.md); TODO marks the ones with work left. |

## Standing rules (from the owner)

- Commit as `spencerlepine <60903378+spencerlepine@users.noreply.github.com>`. Never add a co-author line.
  Push straight to `master`, no pull request. Commit and push often. Always `git pull --rebase origin master`
  before pushing.
- Don't change `game/` during world-building. Never commit the untracked `game/graphics/unused/`.
- The Civitai key is in the env var `CIVITAI_API_TOKEN`. Never commit or paste it. Spend Buzz frugally.
- Write docs in plain, short sentences. Keep a tool's README current in the same commit as the work.
- Don't keep separate to-do lists or status docs. The wiki holds the list; query it at runtime.

## How work flows now (owner, 2026-11-02)

1. **Ask the wiki what to draw:** `cd tools/blockout && python3 -m blockout todo [--status S] [--planet P]
   [--kind K] [--tool T]`. Every area (`art_status` and `notes` in its yaml) and every art id (`status`,
   `build`, `tool`, `notes` in `world_art.csv`) and every terrain item (`terrain.csv`, `--kind terrain`) is a
   row. Statuses: `pending-mockup` (TODO) → `pending-final-art` (GREYBOX done) → `art-complete` (READY TO
   IMPORT) → `imported-in-game`.
2. **Use the tool the row names.** `greybox piece`, `greybox terrain` and `greybox room` are in [`tools/greybox/`](tools/greybox/README.md); `tilegen terrain` is in [`tools/tile-generator/`](tools/tile-generator/README.md). A row with no tool needs a tool or a model that doesn't exist yet; its notes say what it needs.
   Nothing is documented or built ahead for those: they are open work, marked in the wiki.
3. **Record progress:** `python3 -m blockout todo --set <id> <status>`, then `python3 -m blockout index`.

World art goes in three phases (owner): 1. terrain, ground and water (now: greybox tiles for all 528 areas),
2. large structures, natural barriers and medium structures, 3. towns, buildings and the fill. The current phase is **greybox**: simple 3D shapes in placeholder colours, one category at a time, reviewed by the
owner before the next. Final art and the colour palette come later, on the same rows. Town scenes are not
assembled yet (the asset collection comes first); the world map layout in `wiki/world/` is kept as drafted.

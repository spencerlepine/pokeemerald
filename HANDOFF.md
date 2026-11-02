# Handoff: start here

The single entry point for picking this project back up. Read this file first, then the links it names.
Last updated 2026-11-02, at the end of the world-blockout pass.

## The project

A Star Wars conversion of Pokémon Emerald (owner: spencer, GitHub `spencerlepine`).

| Path | What it is |
|---|---|
| `game/` | The pret/pokeemerald C source. Content is ported in by hand. |
| `wiki/` | Every Emerald entity mapped to its Star Wars version. Start at [`wiki/README.md`](wiki/README.md). The story is [`wiki/bible/STORY.md`](wiki/bible/STORY.md). |
| `tools/` | One asset tool per group, with statuses in [`tools/README.md`](tools/README.md). |
| `wiki/world/` | The world blockout: every area as a tile layout. See below. |

The setting is 2 BBY, an alternate telling. The planets are Tatooine, Kashyyyk, Sullust, Mustafar, Endor, Bespin, Jedha,
Yavin 4, Hoth, Dagobah, Kamino and Ilum. The post-game adds the Grand Arena, Felucia, Tython, Atollon, Mortis, the Asteroid
Spire and the Death Star site. PokéNAV is called **StarNAV**; use that name in all new docs.

## Standing rules (from the owner)

- **Commits:**
  - Commit as `spencerlepine <60903378+spencerlepine@users.noreply.github.com>`.
  - Never add a co-author line.
  - Push straight to `master`, with no pull request.
  - Commit and push often, in chunks.
  - Always rebase before pushing (`git pull --rebase origin master`), because other agents push to the same branch.
- **The game source:**
  - Don't change `game/` during world-building. The owner said: "we can't touch the game source code yet".
  - Never commit the untracked `game/graphics/unused/`.
- **Civitai:**
  - The key is in the env var `CIVITAI_API_TOKEN`. Never commit it or paste it anywhere.
  - Spend Buzz frugally.
- **Docs:**
  - Write docs in plain, short sentences.
  - Keep tool READMEs current in the same commit as the work.

## Where the work is (phases)

The owner split the remaining work into phases on 2026-11-02.

1. **World blockout: DONE, waiting for the owner's review.**
   - Every area on every planet is laid out in grey placeholder tiles with pink people and signs. That is 528 areas, all `BLOCKOUT`, none `APPROVED`. A coverage audit (2026-11-02) matched every vanilla map, every location in `wiki/mapping/locations.csv` and every net-new area to an area file.
   - Buildings are sized.
   - Every piece is listed as a TODO in `INDEX.csv`.
2. **Dumb shapes and colours: SECOND PASS DONE (2026-11-02), waiting for the owner's colour guidance.** All 528 areas are drawn
   in flat colours and simple shapes by [`tools/mockup`](tools/mockup/README.md) into [`wiki/mockup/`](wiki/mockup/README.md).
   It is a layer on top of phase 1: it reads `wiki/world/` and never writes there (owner's rule), so it can be scrapped
   and redrawn. Iterate through `wiki/mockup/styles.yaml` (colours and shapes) and `wiki/mockup/overrides/<area>.yaml`.
   Owner rules for this phase: keep the game's **top-down 45° view** (round roofs are ovals, never circles), and
   vary building shapes beyond roofs: footprints (L, octagon, courtyard, wings) and types (bunkers, half-buried,
   sunken, stilts). Buildings are 3D greybox models ray-cast to pixels (owner's call, z-day's method): `tools/mockup/mockup/solid.py` and `build.py`; `wiki/mockup/_buildings.png`
   shows them all. The owner wants images shown in the chat, not left in folders for them to find.
3. **Real art.** This resumes the paused art tools. The first art step is calibrating the Fortree tree house in
   [`tools/world-art`](tools/world-art/README.md) (STYLE.md section 9). The tile pipeline is in
   [`tools/tile-generator/PLAN.md`](tools/tile-generator/PLAN.md).
4. **Port into `game/`.** Maps, scripts and the rows in `wiki/database/game_port.csv`.

## The world blockout (phase 1)

| File | What it is |
|---|---|
| [`wiki/world/README.md`](wiki/world/README.md) | Format, terrain legend, rules, progress table per planet |
| [`wiki/world/GUIDE.md`](wiki/world/GUIDE.md) | Every planet: areas, stories, connections, ship links, caves. Generated. |
| [`wiki/world/CONNECTIONS.csv`](wiki/world/CONNECTIONS.csv) | The area graph, one row per link. Generated, never edited by hand. |
| [`wiki/world/INDEX.csv`](wiki/world/INDEX.csv) | Every area and every placed piece with its art id. This is the to-do list for phases 2 and 3. |
| [`wiki/world/_world.png`](wiki/world/_world.png) | One sheet, one panel per planet |
| `wiki/world/<planet>/<area>.yaml` + `.png` | One area and its review sheet (vanilla map, blockout, legend) |
| [`tools/blockout/`](tools/blockout/README.md) | The `blockout` tool: import, render, check, layout, world, index, guide |
| [`tools/blockout/drafts/`](tools/blockout/drafts/README.md) | The scripts that laid out each planet, with their run order |

Key decisions (all from the owner):
- **Each planet is its own map.** Walkable borders between planets are cut, and ships link them. Each planet has a hangar
  room with a StarNAV flight console.
- **Towns can be bigger and any shape**, as long as walks stay short. Optional side areas are welcome. Use the
  characters already in the wiki.
- **Connections are computed, not maintained.** Running `python3 -m blockout guide` (from `tools/blockout/`) builds the
  graph from three sources:
  - each area's exits, doors and warps;
  - its `travel:` list, for links that are not on the map: ships, shuttles, tides, dives and scripted moves;
  - vanilla's dive connections and script warps.

  The guide checks that every area can be reached from Mos Pelgo. Right now all of them can.

Before pushing world changes, from `tools/blockout/` run:

    python3 -m blockout check && python3 -m blockout world && python3 -m blockout index && python3 -m blockout guide

## Pending items

- **Owner colour guidance on the phase 2 mockup.** Palette ideas were proposed per planet in the chat; apply
  the owner's picks in `wiki/mockup/styles.yaml`.
- **Owner review of the blockout.** Review planet by planet, start with Tatooine. Set `status: APPROVED` on each area the
  owner signs off.
- **Small known issue:** Routes 115 and 116 overlap by 4x4 cells at one corner in the Tatooine layout.
- **Graph check:** 133 links have no direct way back. Most are ledges, holes and one-way warps. Skim them for any
  missing back door before balancing.
- **Placeholder rooms:** 40 new rooms are placeholders. Their props use `art:new:...` ids, which need concept rows in
  `wiki/mapping/world_art.csv`.
- **Vanilla interiors:** the 293 vanilla interiors keep their vanilla layout with a kit note. They are dressed per
  planet in phase 3.
- **Balancing:** use `CONNECTIONS.csv` together with `wiki/database/area_progression.csv`.
- **Other open work** is outside the world blockout, in [`tools/README.md`](tools/README.md):
  - creature sprites are in progress;
  - the tile-generator is paused;
  - the ui-skin, icon, footprint and extras tools are still TODO.

## How to resume

1. Read this file, then [`wiki/world/README.md`](wiki/world/README.md) and [`wiki/world/GUIDE.md`](wiki/world/GUIDE.md).
2. `git pull --rebase origin master`, then run `python3 -m blockout check` from `tools/blockout/`. It should report nothing.
3. Ask the owner for feedback on the phase 2 mockup, then iterate on `wiki/mockup/styles.yaml` and overrides.
4. Update this file whenever a phase or a pending item changes.

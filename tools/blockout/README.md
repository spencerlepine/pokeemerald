# blockout: lay out the world in placeholder tiles

Draws the layout of every area before any art exists: grey placeholder tiles for terrain, grey blocks
for buildings and props, pink placeholders for every sprite and event. Areas live as text in
[`wiki/world/`](../../wiki/world/README.md); this tool checks them, renders a review sheet for each,
and writes the tracker `wiki/world/INDEX.csv`.

```bash
cd tools/blockout && pip install -r requirements.txt
python3 -m blockout new mos-pelgo --replaces LittlerootTown --planet TATOOINE --name "MOS PELGO"   # start from the vanilla map's collision
python3 -m blockout new my-area --planet HOTH --size 30 20                                          # a brand-new area
python3 -m blockout render            # every area -> wiki/world/<planet>/<area>.png (vanilla | blockout | legend)
python3 -m blockout check             # layout problems (overlaps, blocked doors and exits, softlock pockets behind one-way ledges, trainers / items / signs no entry can reach the way the player moves, town doors more than five steps from a road) and the planet graph (`../../wiki/mapping/hyperlanes.csv`: every edge's hangars, doors, the marked path at each door, ramps and signs; every planet linked); exit 1 if any
python3 -m blockout index             # wiki/world/INDEX.csv, and `used_in` / `areas` of every row in wiki/mapping/world_art.csv
python3 -m blockout layout TATOOINE   # place a planet's overworld areas from their exits (writes each area's pos)
python3 -m blockout world             # <planet>/_planet.png and _world.png (one panel per planet)
python3 -m blockout world-tiles       # <planet>/_planet_tiles.png (16 px per cell, from the greybox terrain renders) and _world_tiles.png (half size, not committed)
python3 -m blockout guide             # wiki/world/GUIDE.md and CONNECTIONS.csv: the computed area graph, reachability from the start, and the progression check (planet level bands, net-new area gates and level bands), and the way-home check: areas with no forward path to any hangar
python3 -m blockout todo --kind room:style         # room shells (rooms.csv): styles, or room:part for the kit parts
python3 -m blockout todo --kind scenery --model IN-REVIEW   # what to draw next; --model filters scenery rows by their 3D model status (TODO, IN-PROGRESS, IN-REVIEW, APPROVED, any)
```

- `drafts/`: the scripts that laid out every planet, with their run order ([`drafts/README.md`](drafts/README.md)).

- `blockout/area.py`: the area file format (documented at the top of the file) and its checks.
- `blockout/hyperlanes.py`: the planet graph (`wiki/mapping/hyperlanes.csv`), its checks, and the badge count on first landing per planet (documented at the top of the file).
- `blockout/terrain.py`: the terrain legend, one character per cell.
- `blockout/vanilla.py`: reads a vanilla map (collision, behaviours, doors, people, connections) via `../tile-generator`.
- `blockout/render.py`: the review sheet.
- `blockout/rooms.py`: the room shells (`../../wiki/mapping/rooms.csv` and each area's `room:` block, documented at the top of the file). `check` fails if an interior has no room style or a part, size, hit box or placeholder is wrong; `index` writes each row's `used_in` and `areas` and adds a `room` row per area to `INDEX.csv`; `todo --kind room` (or `room:style`, `room:part`) lists the rows and `--set room:<id> <status>` records progress. It also checks the interior objects: every room lists some (`objects:` or placed props), every id is in `world_art.csv`, every interior object with a placeholder is used and has its PNG; `index` counts `objects:` in `used_in` / `areas` and adds an `object` row per room to `INDEX.csv`.

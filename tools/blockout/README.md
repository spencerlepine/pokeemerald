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
python3 -m blockout check             # layout problems (overlaps, blocked doors and exits, softlock pockets behind one-way ledges); exit 1 if any
python3 -m blockout index             # wiki/world/INDEX.csv
python3 -m blockout layout TATOOINE   # place a planet's overworld areas from their exits (writes each area's pos)
python3 -m blockout world             # <planet>/_planet.png and _world.png (one panel per planet)
python3 -m blockout world-tiles       # <planet>/_planet_tiles.png (16 px per cell, from the greybox terrain renders) and _world_tiles.png (half size, not committed)
python3 -m blockout guide             # wiki/world/GUIDE.md and CONNECTIONS.csv: the computed area graph, reachability from the start, and the progression check (planet level bands, net-new area gates and level bands)
```

- `drafts/`: the scripts that laid out every planet, with their run order ([`drafts/README.md`](drafts/README.md)).

- `blockout/area.py`: the area file format (documented at the top of the file) and its checks.
- `blockout/terrain.py`: the terrain legend, one character per cell.
- `blockout/vanilla.py`: reads a vanilla map (collision, behaviours, doors, people, connections) via `../tile-generator`.
- `blockout/render.py`: the review sheet.

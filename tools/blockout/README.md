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
python3 -m blockout check             # layout problems (overlaps, blocked doors and exits); exit 1 if any
python3 -m blockout index             # wiki/world/INDEX.csv
```

- `blockout/area.py`: the area file format (documented at the top of the file) and its checks.
- `blockout/terrain.py`: the terrain legend, one character per cell.
- `blockout/vanilla.py`: reads a vanilla map (collision, behaviours, doors, people, connections) via `../tile-generator`.
- `blockout/render.py`: the review sheet.

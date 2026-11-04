# Interior objects: placeholder tiles

The objects that fill the rooms: furniture, machines, counters, consoles, beds, shelves, crates, plants,
wall-mounted things and the small set pieces of each room (the cantina bar, Jabba's dais, a bacta tank).
The room shells (walls, floors, steps) are in [`../rooms/`](../rooms/README.md).

No art yet (owner, 2026-11-04). Each object is a sheet of 16x16 placeholder tiles at its drawn size, so the
rooms can be planned on the grid before the interior-object tool exists.

## Where things are

- [`../../../mapping/world_art.csv`](../../../mapping/world_art.csv), `category` `interior`: one row per object
  (`art:new:<name>`) with `planet`, `drawn` (drawn size in cells, W x H), `footprint` (the hit box: the bottom
  rows that block; `0x0` = walkable), `vanilla_template` (`reused: <the Emerald piece>` or `net-new`),
  `placeholder` (its PNG here), `used_in` / `areas`, `status` and `notes` (the hit box in words, what draws over
  the player, and whether it sits on the floor, the back wall, a counter or hangs from the ceiling).
- Each room's yaml lists the objects it needs in a top-level `objects:` list (art ids). They are placed later;
  objects already placed are `props:`.
- `<planet>/<name>.png`: one PNG per object, every cell the shared placeholder
  ([`../../objects/16x16-placeholder.png`](../../objects/16x16-placeholder.png)).
- `sheets/<planet>.png`: every object of a planet (or `shared`), labelled, at real size. `sheets/<planet>_review.png`
  is 3x with the hit box tinted: red blocks, blue is drawn over the player, green is walkable.
- `make_placeholders.py`: writes both from `world_art.csv`. Re-run it after a size changes. It is not the drawing tool.

## Rules

- Rows drawn taller than their footprint are walk-behind: the player passes behind the upper rows.
- `python3 -m blockout check` (in `tools/blockout`) fails if a room has no objects, a room names an unknown
  object, an object is used by no room or its placeholder is missing. `blockout todo --kind interior` lists the rows.

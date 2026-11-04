# Room shells: placeholder tiles

The shells of every interior (floors, walls, corners, doorways, steps, levels, pillars, railings, windows,
counters built into the wall, alcoves, ramps, catwalks, pits). Furniture and props are not here: they are
the `interior` rows of [`../../../mapping/world_art.csv`](../../../mapping/world_art.csv).

No art yet (owner, 2026-11-04). Each part is a sheet of 16x16 placeholder tiles at its real size, so the
kits can be planned on the grid before the room tool exists. The tool and the drawing come later, on the
same rows.

## Where things are

- [`../../../mapping/rooms.csv`](../../../mapping/rooms.csv): one row per room style (`room:<style>`) and one
  per kit part (`room:<style>:<part>`), with `size` (drawn size in cells, W x H), `hit_box`, `role`, the
  `placeholder` PNG, `used_in` and `areas` (from the yamls), `status` and `notes`.
- Each interior yaml has a `room:` block: its `style`, its `map` size, the `parts` it needs (and a `grow`
  note if the room needs a bigger map than Emerald's). Built dungeons (Death Star, Fortress Vader, the
  Republic wreck, the sandcrawler, the Espa generator, the warden tombs) have one too.
- `placeholders/<style>/<part>.png`: one PNG per part, every cell the shared placeholder
  ([`../../objects/16x16-placeholder.png`](../../objects/16x16-placeholder.png)).
- `sheets/<style>.png`: every part of a style, labelled, at real size. `sheets/<style>_review.png` is 3x,
  with each cell tinted and marked with its hit-box code.
- `make_placeholders.py`: writes both from `rooms.csv`. Re-run it after a size changes. It is not the room tool.

## Hit box codes

One code per cell, rows top to bottom joined by `/` (a back wall 1x3 is `o/#/#`).

| Code | Meaning |
|---|---|
| `#` | blocks |
| `.` | walkable |
| `o` | blocks, drawn over the player (top layer: ceiling strip, lintel, pillar top) |
| `^` | walkable, drawn over the player (walk under an arch or a beam) |
| `c` | counter: blocks, talk across it |
| `s` | stairs or ramp: walkable, changes level |
| `d` | door or warp: walkable, leaves the room |
| `v` | ledge: jump down only |
| `_` | pit, shaft or void: blocks |
| `~` | liquid (water, lava, hot spring): blocks |

## Rules

- Every part snaps to the 16x16 grid. The kit's core parts are the same in every style (floor, floor
  variant, back wall, side wall, front wall, inner, outer and front corners, wall end, exit, doorway,
  stairs, window); the extras give each style its shape (curves, split levels, pits, catwalks...).
- A side part is drawn once and mirrored for the other side.
- Shared rooms (Bacta Center, Supply Depot, docking hangar, gatehouse, hideout) borrow the window and
  floor variant of the planet's home style, so the room still says which planet you are on.
- `python3 -m blockout check` (in `tools/blockout`) fails if an interior has no style, a part is missing,
  a hit box does not fit its size or a placeholder is missing. `blockout todo --kind room` lists the rows.

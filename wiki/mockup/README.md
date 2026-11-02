# World mockup (phase 2: shapes and colours)

Every area of the world blockout drawn with flat colours and simple shapes, so towns and routes read as
places before any real art exists. Made by [`tools/mockup`](../../tools/mockup/README.md).

This folder is a **layer on top of phase 1** ([`../world/`](../world/README.md)). Phase 1 owns the layout:
terrain, sizes, positions, doors and connections. This layer owns only how things look. Nothing here edits
phase 1, so the whole folder can be thrown away and redrawn.

| File | What it is |
|---|---|
| [`_world.png`](_world.png) | Every planet's overworld, one panel each |
| `<planet>/_planet.png` | One planet's towns, routes and landmarks stitched together |
| `<planet>/<area>.png`, `<planet>/caves/`, `<planet>/interiors/` | One area each, same folders as phase 1 |
| [`styles.yaml`](styles.yaml) | Colours per planet and one shape per building and prop type |
| `overrides/<area>.yaml` | Mockup-only tweaks for one area (hide, move, add, restyle a piece) |

How to read a mockup:
- Buildings: roof on top, front wall below with windows and the door; the name is printed on the roof.
- Props: trees, rocks, crates, tanks, vehicles and ships as simple shapes.
- People: pink figures. Gold ring = story character, red ring = trainer, plain = townsfolk. Small balls are items.
- Signs are brown boards; dark doorways are warps (cave mouths, hatches); white arrows mark exits.

Status: first pass of all 528 areas, waiting for the owner's look. Iterate here (styles and overrides);
change phase 1 only when a layout itself is wrong.

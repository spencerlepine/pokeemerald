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
| [`_buildings.png`](_buildings.png), [`_buildings-grey.png`](_buildings-grey.png) | Every building type at three sizes, in colour and in pure grey (`python3 -m mockup builds [--grey]`) |
| [`styles.yaml`](styles.yaml) | Colours per planet and one shape per building and prop type |
| `overrides/<area>.yaml` | Mockup-only tweaks for one area (hide, move, add, restyle a piece) |

How to read a mockup:
- Buildings are 3D greybox models ray-cast into pixels in the game's top-down 3/4 view (owner's call: model
  simple 3D shapes and convert them, as z-day did): the roof is the footprint seen from above, the south
  wall shows below it with windows and the door, and round buildings are ovals. Footprints vary (L, octagon,
  T, courtyard, wings), and so do types: domes, cones, quonsets, towers, stepped temples, bunkers in earth
  berms, half-buried mounds, sunken courtyards, stilt houses, arenas and landing decks. The name is printed
  on the roof.
- Props: trees, rocks, crates, tanks, vehicles and ships as simple shapes.
- People: pink figures. Gold ring = story character, red ring = trainer, plain = townsfolk. Small balls are items.
- Signs are brown boards; dark doorways are warps (cave mouths, hatches); white arrows mark exits.

Status: third pass (2026-11-02): 3D greybox buildings, varied footprints and types, all 528 areas. Colours are
still the first guess and wait for the owner's guidance. Iterate here (styles and overrides);
change phase 1 only when a layout itself is wrong.

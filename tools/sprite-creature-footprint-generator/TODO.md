# sprite-creature-footprint-generator

**Status:** TODO. Not built yet; this file marks the scope.

**Engine: Python** (no image model). A footprint is a 16x16 one-colour stamp, small enough to
draw from a short list of foot shapes.

Companion footprints: the print shown on the creature's Datapad (Pokédex) entry.

- **Categories:** A4
- **Wiki rows:** `pending_art.csv` kind `pokemon`, files `footprint.png`; 387 PNGs
- **Format in the game:** 16x16, 1 bit (ink or empty), no palette; listed in
  `game/src/data/pokemon_graphics/footprint_table.h`
- **Blank prints:** 87 vanilla species have an empty footprint (no feet: floating, serpents,
  fish, droids on repulsors). A blank is a valid output

## What it makes, per species

| File | Made by |
|---|---|
| `footprint.png` | Python: pick a foot type from the brief (paw, hoof, claw, talon, webbed, tread, wheel, none), size it to the creature, stamp it; hand-touch if needed |

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` the Emerald original, `suggested_path` the new name) and writes the footprint.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

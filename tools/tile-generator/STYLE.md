# Emerald overworld style, measured

What makes a tile read as Emerald overworld art. Measured on the vanilla tilesets rendered by
`tilegen/gba.py` (General + Petalburg, Littleroot Town, Route 101, the Pokémon Center). The rasteriser in
`tilegen/raster.py` encodes the camera; the passes in it encode the idioms. Add a section when a new
category teaches something.

## 1. The camera (never break this)

- Ground is drawn **in plan**, straight down: a 16x16 cell is a 16x16 square of ground.
- Every vertical face that looks **south** (toward the player) is drawn **head-on at full height**.
- East and west faces are **edge-on and vanish**; north faces are hidden. There is no side wall on any
  vanilla building, tree, rock or sign.
- Nothing is foreshortened: a point at depth `y` and height `z` lands on screen at `(x, y - z)`.
  Consequences: a roof of depth `d` is `d` px tall on screen; a wall of height `h` is `h` px tall; a
  thing that hangs in front of a wall at height `z` covers the wall rows behind it (so awnings are flat
  slabs, not slopes, or they would hide the wall).
- Depth order: larger `y` (further south) is nearer the camera. Tall things overlap what is north of them.

Vanilla Littleroot house (Petalburg metatiles 520-584): 5 cells wide, 5 rows tall on screen = back-slope
ridge band ~12-16 px (lighter), front slope ~36 px, awning + eave line ~10 px, wall ~26 px with a 16x24
door and 12x10 windows. The bottom row under the wall is a COVERED-layer ground cell with the entrance
mat and shadow (the player walks on it).

## 2. Light from the upper left, in front

Tops are the lightest tone, south faces the middle, undersides and seams the darkest. Round things
(domes, canopies, rocks) carry all 3-4 tones with a **50% checker band** at each transition, never a
smooth ramp. Flat faces snap to one tone each.

## 3. Ramps of 3-4 tones per material, 9-15 colours per bank

Each 16-colour bank holds 3-4 materials. A material is 3 tones (flat things) or 4 (round things, roofs).
Darker tones drift toward blue/purple (`#ee9473 -> #de6a62 -> #cd4152`: the hue turns from 46 to 21 in
LCh while L drops 81 -> 49). Index 15 of most outdoor banks is the ground green (`#73c5a4`) so any tile can
show ground through its transparent corners.

## 4. Outlines

A **1 px outline in the material's darkest tone** around every object's silhouette, drawn *inside* the
footprint so the cell grid stays exact. Depth steps between surfaces (eave over wall, canopy over trunk)
get the same line. Buildings add vertical corner posts and a dark base line on the wall; windows and
doors have a 1 px frame in the trim colour.

## 5. Textures are tiny periodic patterns

- Roof tiles: staggered 8x4 bricks, light top edge, dark bottom seam, dark vertical joint.
- Tree canopies: rows of 5x4 leaf scallops (dark underside, light crown), offset every other row.
- Ground: a flat field with sparse 1-2 px specks in the next tone (density ~6% in Littleroot grass); tall
  grass is a drawn tuft, not noise.
- Plaster walls: flat with sparse specks; wood: a dark line every 4 rows.

All patterns repeat on 8 or 16 px so metatile columns dedupe into left / middle / right kits.

## 6. Grounding

Objects sit on a **drop shadow**: a dark 50% checker ellipse under trees and rocks, a 1 px dark base
line under walls, plus the lit "mat" cell in front of doors.

## 7. Colour budget

Everything a tile shows must come from one bank: a building uses the secondary tileset's banks (6-12),
3-4 materials each; the ground primary (0-5) is shared by every town on the planet. A new planet gets its
own primary recolour (stage 1 recipe) and each town a secondary.

## 8. Lessons from the prototypes

- **Hand-authored stamps lose to vanilla shapes.** Three tries at a new 16x16 tall-grass tuft for Tatooine
  (sparse tufts, offset bushes, a dense grid) all read as noise or mushrooms next to the recoloured vanilla
  tall grass, which already reads as dry scrub. Rule: keep vanilla's drawn shapes wherever the brief allows and
  change them through the palette (and index remaps); only redraw what has no vanilla counterpart.
- **Recipes need a stone rule.** Achromatic stone (Sootopolis white, cave greys) and low-chroma pink cliff rock
  are untouched by hue rules; every planet recipe needs explicit `chroma_max` stone and `hue: [330, 70]` rock rules.
- Recolouring the shared primary also recolours the Pokémon Center / Mart roofs that live in it. Those become
  Bacta Center / supply depot assets later, so this is tolerated during prototyping.
- **Effects share banks with unrelated art.** The rocks and foam standing in General's water are drawn in
  bank 1, which also colours signs and fences, so a lava recipe can't recolour them alone. The `rebank` op
  clones those tiles into the water bank's free slots (vanilla magenta / duplicate entries) instead. Free
  slots per bank are the budget for this; check them before planning an effect.
- **Lava from water:** let hue follow lightness (`hue_by_light: [10, 100]`, dark red to yellow) and raise
  contrast (`light_scale: 1.3`): the drawn wave crests become glowing seams with no new pixels.
- **Metal floors are tone-level patterns.** The Facility floor kit has a lit set and a shadowed set (the
  shadow set is every index + 1) whose halves mix under walls, so a new floor is drawn once as tone levels
  (`ground.deck_plate`, `ground.grate`) and written into both sets by the `pattern` op with two tone maps.
  Keep every top half compatible with every bottom half.

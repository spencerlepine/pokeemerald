# Emerald VFX style, measured

`python -m vfx corpus` measures every vanilla VFX sheet the game actually loads (345 sheets: 178 move
sprites, 23 move backgrounds and masks, 59 field effects, doors, weather, transitions) into
`corpus/style.json`. `build` scores every new sheet against its group's 5th-95th percentile band and
against the vanilla sheet it replaces. These are the rules behind the score, with the numbers.

## 1. Hard bands, never gradients

Every glow is 3-5 flat steps of one ramp: white or pale core, one or two saturated steps, a dark rim of
the same hue (`orbs.png`, `circle_of_light.png`, `impact.png`, `small_ember.png`). Checkerboard dither
appears only on the largest glows and explosions (median 0, 95th percentile 15% of 2x2 windows). The
drawing ops quantise through `bands` for this reason; `dither:` exists for the big-glow case only.

## 2. The core is the brightest thing

Move sprites: interior is on average 27 luma brighter than the edge (band -19..97). Energy is drawn
from the inside out. An effect whose rim is brighter than its core reads as a ring or a hole.

## 3. Rim in its own colour, not black

Edge pixels are near-black on only 0% of the median move sprite. Objects (the coin, the Poke Ball, the
Fly bird) are the exception: they are outlined, but in a dark step of their own ramp, lit side lighter
(`selout: {light: [-1, -1]}`). Black outlines are for overworld objects that sit on the NPC/player
bank, like the bird.

## 4. Few colours, no specks

Median 6 colours per move sheet (max 11), 3 per field effect. No colour used by fewer than 3 pixels
(a FAIL). Lone pixels with no opaque neighbour are rare (95th percentile 2%) except in spark sheets:
allow them in the spec (`lint_allow: [lone]`) when the effect really is sparks.

## 5. Fill the frame, don't touch its edge

Median coverage 30% of the frame for move sprites (9-75%). Art on the frame border is clipped in game:
keep it under the vanilla sheet's own border share.

## 6. Contrast against the field

The battle field is pale (tall grass is light green stripes) and some moves blend it to black (HYPER
BEAM). Judge every effect in the battle preview, at 1x and 2x, not on the sheet card. Pale-only effects
vanish on grass: give them a saturated rim step. Use `motion: {dim: 1.0}` when the script blacks out the
background.

## 7. The game decides the layout and the palette

Not style, but the reason most first drafts fail in game:

- Only the frames the game plays matter (`python -m vfx show coin`: "the game shows [2]").
- Frame size comes from the template's OAM shape and the tile order, not the PNG shape.
- A palette can be shared with another tag (`sprites/pokeball` shares with `ANIM_TAG_SPOTLIGHT`),
  set by code (the Fly bird uses the player's bank, different for boy and girl), or flashed by index at
  runtime (HYPER BEAM flashes `ANIM_TAG_ORBS`). `build` prints these as WARNING/NOTE lines.

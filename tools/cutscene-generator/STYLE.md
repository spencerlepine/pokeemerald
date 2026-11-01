# Emerald cutscene style, measured

What makes a redraw sit in Emerald's intro and cutscenes instead of looking pasted in. Taken from
the vanilla intro (`game/graphics/intro/`, screenshots of the real ROM in mGBA) and checked against
the scene-2 prototype in `scenes/intro_bike/`. Add a section when a new scene teaches something.

Colors come from [`wiki/bible/PALETTE.md`](../../wiki/bible/PALETTE.md) where a theme fits; scene
palettes like Tatooine's desert are new and follow the same rule (GBA steps of 8). A new place's palette is
added to the wiki as its own `## Planet: <name>` theme first, so every tool shares it ([`../PALETTES.md`](../PALETTES.md)).

## 1. Backgrounds have no outlines

Every BG layer in intro scene 2 is drawn with **flat tone shapes only**: the mountains are one mid
tone plus a sunlit cap, the pines a lit edge plus a body. Shapes separate by value, not by lines.
The single dark line in the whole scene is the ground's top edge (`#4a5252`, 1 px, ragged), which
sets the actors' "floor". Same in the redraw: domes, vaporators and buttes have no outline; the
dune lip keeps a 1 px dark edge.

## 2. Bands joined by a 50% checker

Emerald does gradients as **flat bands with an 8-row 50% checkerboard between neighbours** (the
sky: `#c5e6ff` rows 0-7, checker 8-15, `#d5f6ff` 16-23, ...), and shades round things the same
way (the pines' lit side breaks into checker before the body color). Never a smooth ramp, never
noise. In pxl: `dither(x, y, w, 8, a, b, 0.5)` between `rect` bands; for a dome, a checker ring
between its lit, mid and shade zones (see `dome()` in the prototype).

## 3. Aerial perspective, three depths

Back to front the layers get **darker and more saturated**: sky (lightest) > far range (grey-
green, close to the sky) > pines (mid green) > ground (saturated). Each BG uses 2-4 colors of a
shared 16-color palette (scene 2's BG3 and BG2 share palette 0: 12 colors used in all). The
redraw: pale blue sky > cool rose-grey mesas > warm sunlit adobe and metal > orange sand.

## 4. Light from the upper left

Caps, lit edges and dome highlights are on the left/top. Shadows fall right/down. Keep the suns
(or whatever light source a scene shows) on the left so the shading agrees.

## 5. Actors: one warm dark outline, saturated accents

Intro actors are the opposite of the BGs: **outlined**, and mostly in one color. Share of outline
pixels: May 83% `#524a4a`, Brendan 82%, the bicycle 59% (the rest is lit edges dropping their
outline where light hits). This differs from the overworld walkers, which outline each material in
its own dark tone (`../sprite-walker-generator/STYLE.md`). Use pxl's `outline: 1` with a warm
near-black (`#483838` in the prototype), then let a few lit edges replace it by hand.

Actors carry the only saturated colors on screen (May's red top, the bike's red frame; KAEL's
flight-orange scarf, the kyber-blue thruster), so they read against pastel layers.

## 6. Match the hardware layout before drawing

Read the scene's C code first and keep its layout: which BG each image is, screen-block split
(`trees_map.bin` = BG3 screen + BG2 screen), palette slot (`grass` is BG palette 15), sprite sizes
and offsets (rider 64x64 at the center point, vehicle 64x32 at center + 8), scroll speeds, palette
cycling (BG entries 9/10 swap every 8 frames: put something there that should blink or shimmer,
and nothing else). The redraw replaces pictures, not code.

## 7. Motion comes from the scroll

The ground scrolls 4 px a frame, so its marks should be **sparse** (Emerald's grass is a flat field
with tufts only on the lit lip). Regular dash patterns read as road markings once they move. Four
rows of irregular ripples was the right density in the prototype.

## Open questions for the owner

- Player look: KAEL here is a placeholder (sand tunic, goggles, orange scarf). The trainer-back
  tool waits on the same decision.
- Speeder bike or swoop? STORY.md maps the bike to "white speeder bike"; the prototype follows it.
- The chasing companions (Manectric, Torchic, Volbeat, Flygon in Emerald) are not redrawn yet.

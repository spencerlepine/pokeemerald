# Intro scene 3 titans (GREATKRAYT, SANDO, EXOGORTH)

Shipped 2026-11-05 (owner: "ship it"). The titans are drawn from the films, not from the battle sprites (owner:
"draw these from scratch to match the actual concept art and make it look like the movie").

- Scene window: 240x96 (letterboxed). Each titan fills it with a few pixels of padding (owner, round 1).
- References (Wookieepedia, not committed): `Krayt-dragon-mando.png` (The Mandalorian), `SandoAquaMonster.png`
  (The Phantom Menace), `ExogorthObstacleToken-RitR.png` (the Empire Strikes Back slug in its crater).
- `mockups/`: the scripts that made the review sheets. `px.py` pixelates a cut-out reference to scene size
  (downscale, quantise, outline); `mock.py` builds clean scene backgrounds from the ROM capture and lays out sheets.
  They expect the ROM frames and references in a scratch folder (paths at the top of `mock.py`).
- `titan_gen.py`: Civitai image to image at the scene's grid (1008x672 = 144x96 x 7, the API caps a side at 1024)
  and SDXL text to image. Pay with `--currency green`. Findings: image to image at 0.35-0.5 drifts away from the
  film creature; SDXL text to image does not know these creatures (generic monsters), so it is not used.
- Pixel art pass (round 4): SDXL image to image with the Super PixelArt Sprite XL LoRA (`urn:air:sdxl:lora:civitai:579244@646044`,
  `titan_gen.i2i_xl`, denoise 0.6) from the smooth reference on white at 1024x768 (128x96 game pixels x 8), then
  `mockups/fin.py` block-votes it back to 128x96 (or 64x48 doubled for the chunky look). Pixel Art XL and Soft Pixel
  Art XL are not enabled for generation on Civitai. The cel-shading script (`mockups/cel.py`) looked muddy.
- 2x chunky pass (round 6): the reference is form-shaded at 64x48 (`mockups/form.py`), upscaled x8 to 512x384, and
  redrawn by the PixelArt Sprite XL LoRA at denoise 0.45-0.6 (`mockups/r7_xl512.py`): at 512 px the model's pixel is
  one chunky pixel, so teeth and eyes survive. `mockups/snap.py` reads it back to 64x48 in 6 colours (5 tones and
  teeth), merges islands under 3 px and outlines it; shown at 2x. `sprites/round6/` holds the nine 128x96 results.
- Draw, then pixelate (round 7, the owner's method): DreamShaper XL (`112902@126688`) image to image from the
  picked pose at denoise 0.5-0.8 with a bold cel-shaded illustration prompt (`mockups/r10.py`), then
  `mockups/illpx.py` turns the drawing into pixel art (cut the page, shrink, quantise, merge islands, outline).
- **Final candidate** (`sprites/final/`, 128x96, 12-13 colours each, under the 15-colour bank limit): DreamShaper XL
  image to image from the picked pose with a flat anime cel prompt (Ken Sugimori style, 2-tone shading; `mockups/r12.py`,
  `r13.py`), then `mockups/flatpx.py` (box shrink, 12 colours, island merge, 2 majority passes, one outline colour,
  bright specks kept as a tooth accent). Sources: krayt `s755866184`, sando `s1778252834` (saturation 0.9),
  exogorth `s1492340030`. `mockups/final.py` builds them.
- `review/round1`: silhouettes from the battle sprites (dropped). `review/round2`: film references, sized to the frame.

## Into the game

`python3 titans/export.py` snaps each final sprite to GBA colour steps, fits it to the bank entries it may use
and writes `titans.data.js` (palette and rows of index characters). `intro_legends.px.js` includes it, puts the
colours into banks 1, 2 and 5 and draws each titan:

- GREATKRAYT (bank 1, 11 colours) and SANDO (bank 2, 13 colours) use entries 1-14; 15 stays the glow the code
  pulses. Each is drawn three times, centred on Emerald's three pose spots and snapped to the tile grid, so the
  copies share tiles (102 and 112 of the 256 an affine sheet may hold). The camera cuts between the copies as
  it did between Emerald's poses.
- The EXOGORTH (bank 5) keeps off entries 8, 12, 13 and 14, which the code flashes (13 is the sky band), so it
  is cut down to 11 colours. It stands at the right edge of the sky band, jaws turned to the middle: the code's
  orb sprite grows there (Rayquaza coiled round it) and would hide a titan in the middle.
- Framing was measured in the ROM (`scripts/rom-preview.sh`); `review/shipped/` holds the real-speed capture.

To change a titan: replace its PNG in `sprites/final/`, run `export.py`, then build the scene as usual.

# Intro scene 3 titans (GREATKRAYT, SANDO, EXOGORTH)

Work in progress (2026-11-05). The titans are drawn from the films, not from the battle sprites (owner:
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
- `review/round1`: silhouettes from the battle sprites (dropped). `review/round2`: film references, sized to the frame.

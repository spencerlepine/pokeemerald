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
- `review/round1`: silhouettes from the battle sprites (dropped). `review/round2`: film references, sized to the frame.

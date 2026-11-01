# cry-generator

**Status:** DONE. Approved by the owner on 2026-11-01. The first six cries (SUNCHICK, MASSIFF, MYNOCK, EXOGORTH,
R2 UNIT, PERSUADER) are in `../../game`; the other 380 rows are made the same way, a spec at a time.

One cry per companion: creature calls, droid beeps and servos. Wiki rows: `../../wiki/database/pending_audio.csv`,
category `cry`, HOTSWAP (386 rows). Each row's `sw_subject` is the brief and `asset_file` the slot it replaces.

Read [`CONSTRAINTS.md`](CONSTRAINTS.md) first: the GBA limits (10512 Hz 8-bit, DPCM's 64-level slew limit,
2.34 s hard cut, the 0.33 s doubles window, reverse/faint/chorus modes) and how the tool meets each one.

## Setup

```bash
pip install -r requirements.txt     # numpy, scipy, pyyaml, pillow
python3 cry.py survey               # once: measures the 388 vanilla cries -> reference/vanilla_stats.json (committed)
```

`romtest.py` also needs the play-tester toolchain (`../play-tester/scripts/setup-ubuntu.sh`: agbcc, mGBA 0.11, Xvfb).

## Make a cry

1. Copy a spec in `specs/` that is close (a small bird: `sunchick`; a snarling beast: `massiff`; a titan:
   `exogorth`; a screech: `mynock`; an astromech: `r2_unit`; a heavy war droid: `persuader`).
2. Set `name`, `slot` (the vanilla file stem it replaces, e.g. `torchic`), `brief`, `size` (0 tiny to 1 huge),
   then draw the layers (below).
3. Render and gate it:

```bash
python3 cry.py make specs/sunchick.yaml   # -> out/sunchick.wav (game format) + out/sunchick_preview.wav + report
python3 review.py specs/sunchick.yaml     # spectrogram next to the slot's vanilla cry -> out/review.png
python3 cry.py modes out/sunchick.wav     # every in-game mode (doubles, faint, growl, howl...) -> out/modes/
python3 romtest.py specs/sunchick.yaml    # build a scratch ROM and record it from mGBA -> out/rom/, out/vanilla/
```

4. When the owner approves: `python3 cry.py install specs/sunchick.yaml` writes the .wav over the slot in
   `../../game` (same table slot, same file name; renaming the file and label is a separate port step), and the
   row is marked done: add it to `../../wiki/mapping/audio_done.csv` and run
   `python3 ../../wiki/tools/mark_audio_done.py` (sets `audio_status` and `game_status` DONE in the wiki).

`make` already fits the DPCM format: it tries more high-shelf cut and less loudness until the optimal DPCM
path is clean (SNR >= 20 dB, accepting 16 then 12 for very bright voices, as vanilla does), and bakes that path
into the .wav, so the build's own encoder reproduces it exactly.

## Spec layers

Every layer takes `at` (start, s), `env` ([[t, level], ...]), `gain`, optional `drive` (tanh saturation).
Curves are `[[t, value], ...]`, interpolated (pitch exponentially).

| type | What it is | Main keys |
|---|---|---|
| `voice` | A throat: saw/pulse/square/sine/tri/noise source through 3 formants | `pitch`, `source` {saw, pulse, pulse_width, noise...}, `vowels` [[t, a/e/i/o/u/ae/er/rr/ee/aw/m or [F1,F2,F3]]], `vibrato`, `jitter`, `growl` (subharmonic + roughness), `growl_rate`, `pitch_step` (frame-stepped pitch, chip-era style), `emphasis`, `formant_scale` |
| `tone` | Electronic tone (droids) | `wave` (square/pulse/tri/sine/saw), `pitch`, `width`, `warble` {rate, depth, shape: square} |
| `servo` | Motor whine: harmonic stack on an rpm curve + grit | `pitch`, `harmonics`, `grit` |
| `noise` | Breath, hiss, rasp: band-passed noise | `band` (curve or [hz]), `q` |
| `click` | Short transients (jaw snaps, relays) | `times` |

`master` (optional): `highpass`, `lowpass` (default 4200 Hz), `rms` (default 0.25), `tilt_db`.

Design notes learned on the first batch: put a creature's fundamental around 150-900 Hz and get brightness
from the formants (like the vanilla cries), not from a very high fundamental; very bright, loud voices hit the
DPCM slew limit and come out gritty and quieter. Droids read best with stepped tones (`pitch_step`) and warble.

## Files

| File | What |
|---|---|
| `gba.py` | Cry hardware model: constants, wav2agb DPCM port (bit-exact) and optimal DPCM, mode playback |
| `synth.py` | Layers and mastering |
| `cry.py` | CLI: survey, make, check, modes, install |
| `review.py` | Spectrogram sheet vs vanilla |
| `romtest.py` | Scratch-ROM build and mGBA recording |
| `specs/` | One spec per cry |
| `reference/vanilla_stats.json` | Measurements of all 388 vanilla cries (the gate's calibration) |
| `out/` | Renders (git-ignored) |

## Palette

Not applicable: audio, no art.

# sfx-generator

**Status:** IN-REVIEW. Works end to end (spec -> game-format sample + MIDI + voicegroup -> ROM). Eight draft
SFX are with the owner.

Sound effects: the 26 mapped hot-swaps (capture pods, comlink, doors, hover-bike, kyber, freighter) and the 17
net-new (blaster, lightsabers, Force, turbolaser, hyperspace, astromech, Vader's breath...). Wiki rows:
`../../wiki/database/pending_audio.csv`, category `sfx`, swap_kind HOTSWAP or NET_NEW (43 rows; KEEP rows need
nothing).

Read [`CONSTRAINTS.md`](CONSTRAINTS.md) first: the GBA's two sound systems (5 PCM voices mixed at 13379 Hz in
8 bits, plus the four Game Boy channels), the reverb every song uses, how vanilla SEs are built, and how this
tool fits inside them.

## Setup

```bash
pip install -r requirements.txt     # numpy, scipy, pyyaml, pillow
python3 sfx.py survey               # once: lengths/voicegroups of the 269 vanilla SEs -> reference/vanilla_se.json
```

`romtest.py` also needs the play-tester toolchain (`../play-tester/scripts/setup-ubuntu.sh`).

## Make an SE

1. Copy a close spec from `specs/`. Set `name`, `brief`, and either `replaces: SE_X` (hot-swap: the vanilla SE
   keeps its id and call sites) or `constant: SE_NEW_THING` (net-new: gets a free song id 270-349).
2. Draw the layers (below), then:

```bash
python3 sfx.py make specs/blaster_bolt.yaml   # -> out/blaster_bolt.wav (13379 Hz 8-bit) + _preview.wav (as heard)
python3 review.py specs/blaster_bolt.yaml     # spectrogram sheet -> out/review.png
python3 romtest.py specs/blaster_bolt.yaml    # scratch ROM, record from mGBA -> out/rom/ (+ out/vanilla/ for hot-swaps)
```

3. When the owner approves: `python3 sfx.py install specs/blaster_bolt.yaml` wires it into `../../game`:
   the sample in `sound/direct_sound_samples/sw_sfx/`, its label in `direct_sound_data.inc`, a one-voice
   voicegroup `sound/voicegroups/sw_<name>.inc`, the `se_*.mid` and its `midi.cfg` line (same `-E -R50` as
   vanilla), and for net-new SEs the song id in `songs.h`, `song_table.inc` and `ld_script.ld`. Calling a
   net-new SE from scripts or battle animations is port work (`game_port.csv`).

## Spec layers

Every layer takes `at` (start, s), `gain`, optional `drive`. Curves are `[[t, value], ...]` or a constant.

| type | Voice | Main keys |
|---|---|---|
| `square` | Game Boy square (register-exact) | `pitch`, `duty` 0-3 (12.5/25/50/75 %), `sweep` [time 1-7, negate, shift 1-7] (hardware sweep), `env` (quantised to 16 steps per frame) or `hw_env` {start, step, dir}, `vibrato` {rate, depth semitones}, `length` |
| `wave` | Game Boy wave | `table` (sine/tri/saw/organ/buzz or 32 values 0-15), `pitch`, `env` (snapped to 0/25/50/100 %) |
| `noise` | Game Boy LFSR | `clock` (Hz, snapped to the 112 legal clocks) or `nr43` [shift, divisor], `short` (7-bit metallic), `env` / `hw_env` |
| `pcm` | Sampled sound | `osc` (saw/square/tri/sine/noise), `pitch`, `unison` (cents), `fm` {ratio, index}, `am` {rate, depth}, `ring`, `filter` {type lp/bp/hp, cutoff, q, stages}, `crush`, `env` |

Top level: `loop: {start, end, crossfade}` for held loops (the sample gets loop points, the MIDI holds the note);
`master: {peak, lowpass, highpass, fade_out}`.

## Files

| File | What |
|---|---|
| `gba.py` | SE hardware model: mixer constants, Game Boy channel emulation, m4a reverb, preview, wav I/O with loop points |
| `synth.py` | Layers and mastering |
| `sfx.py` | CLI: survey, make, check, install (+ a tiny MIDI reader/writer) |
| `review.py` | Spectrogram sheet |
| `romtest.py` | Scratch-ROM build with the real installer and mGBA recording |
| `specs/` | One spec per SE |
| `reference/vanilla_se.json` | Survey of all vanilla SEs |
| `out/` | Renders (git-ignored) |

## Palette

Not applicable: audio, no art.

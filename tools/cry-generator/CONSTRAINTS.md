# Cry constraints (Emerald / GBA)

Researched 2026-11-01 from the game source in `../../game` and checked against recordings from the built ROM.
This file is cry-generator's own copy: sfx-generator keeps a separate one on purpose. `gba.py` holds every
number below as a constant; the gate in `cry.py check` enforces them.

## 1. The sound hardware the cry plays on

| Fact | Value | Source |
|---|---|---|
| Sound engine | m4a (MusicPlayer2000 / "Sappy") | `src/m4a.c`, `src/m4a_1.s` |
| PCM mixer rate | **13379 Hz** | `m4aSoundInit`: `SOUND_MODE_FREQ_13379` (`src/m4a.c:79`) |
| Mixer output | 8-bit DAC | `SOUND_MODE_DA_BIT_8` |
| PCM voices mixed at once | **5** (of 12 the engine allows) | `5 << SOUND_MODE_MAXCHN_SHIFT`; `MAX_DIRECTSOUND_CHANNELS 12` |
| Master volume | 12 / 15 | `12 << SOUND_MODE_MASVOL_SHIFT` |
| Game Boy (PSG) channels | 4: square 1 (with sweep), square 2, 32-step 4-bit wave, LFSR noise | `CgbSound` (`src/m4a.c:925`) |
| Cries at once | **2** | `MAX_POKEMON_CRIES 2` (`include/gba/m4a_internal.h`) |
| Reverb | Every song sets reverb 50 (`-R50` on all 209 BGM and 269 SE lines in `midi.cfg`; one BGM uses 40), and reverb is global to the PCM mixer, so cries in battle get it too | `m4a_1.s` `SoundMainRAM_Reverb` |

The reverb is a feedback echo: each new frame of the PCM buffer starts as the sum of the left and right
buffers 6 and 7 frames ago times reverb/512. For a centred voice that is
`y[n] = x[n] + (y[n-1344] + y[n-1568]) * 50/256` at 13379 Hz: two taps about 0.1 s back, loop gain 0.39.

Cries are PCM, so the Game Boy channels never touch them.

## 2. The cry sample format

| Fact | Value | Source |
|---|---|---|
| File | `sound/direct_sound_samples/cries/<species>.wav`, one per slot in `gCryTable` / `gCryTable_Reverse` (`sound/cry_tables.inc`) | |
| Format | mono, **8-bit**, **10512 Hz**: all 388 vanilla files | measured |
| Native pitch | `cry` macro = `voice_directsound_compressed 60, 0, sample, 255, 0, 255, 0`: key 60 plays the sample at its own rate; ADSR 255/0/255/0 = no envelope, hard stop | `asm/macros/music_voice.inc:152` |
| Top frequency | 5256 Hz (Nyquist of 10512); nothing above exists in a cry | |
| Build | `wav2agb -b -c -l 1 --no-pad` = **DPCM** compression | `audio_rules.mk` |

## 3. DPCM: the constraint that shapes the sound

wav2agb's DPCM (`tools/wav2agb/converter.cpp`) cuts the sample into 64-sample blocks. The first sample of each
block is stored raw; every other sample is a 4-bit index into a fixed step table:

    0, 1, 4, 9, 16, 25, 36, 49, -64, -49, -36, -25, -16, -9, -4, -1   (in 8-bit levels, of 256)

The build picks each step greedily (lookahead 1). Consequences:

* **Slew limit.** The level can move at most +49 / -64 per sample. A sine of amplitude A levels at f Hz needs a
  slope of about A x 2 pi f / 10512 per sample, so above about 2 kHz only quiet content survives cleanly:
  A <= 41 levels (a third of full scale) at 2 kHz, about 27 levels at 3 kHz. Loud high-pitched sound turns
  into grit. Vanilla bright cries show exactly this: the brightest (Shuppet, Lotad, Surskit, Plusle) sit at
  RMS ~0.15 against ~0.25 for the set, and 20-46 % of their steps are 36 levels or more.
* **Coarse steps** (no 2, 3, 5...) add a noise floor everywhere: vanilla spectrograms are grey all over.
* Vanilla cries are **DPCM-exact** files: re-encoding them with wav2agb is lossless (SNR > 150 dB). We do the
  same: `cry.py make` bakes the best possible DPCM path into the .wav (a Viterbi search over every legal step
  sequence, `gba.dpcm_optimal`), and because every step is a table step, the build's greedy encoder
  reproduces it exactly. Quality is the best the format allows, and the repo file is what the ROM plays.

Our port of the encoder matches the real wav2agb bit for bit (checked on abra, wailord, pidgey).

## 4. How the game plays a cry (`PlayCryInternal`, `src/sound.c`)

The same sample is reused for every mode, played on a one-note "song" (`gPokemonCrySongTemplate`,
`src/m4a_tables.c`) that ties the note for `length` frames (59.73 frames per second) and then releases.

| Mode | Hold | Release | Pitch (semitones) | Reverse | Used for |
|---|---|---|---|---|---|
| normal | 140 frames = **2.34 s** | 0 (cut) | 0 | | battle entry, Pokédex |
| doubles | 20 frames = **0.33 s** | 225 | 0 | | double battles |
| encounter | 140 | 225 | +0.94, chorus | | static encounters |
| howl | 50 | 200 | +1.72, chorus | | Howl |
| echo_start / echo_end | 25 / 140 | 100 / 220 | +0.94 / +0.76, wide chorus | start | Hyper Voice |
| faint | 140 | 200 | **-3.59** | | fainting |
| roar_1 / roar_2 | 10 / 60 | 100 / 225 | -2.0 / +1.0 | | Roar |
| growl_1 / growl_2 | 15 / 100 | 125 / 225 | -0.63 | 1st | Growl |
| weak | 140 | 0 | -1.41 | | low HP |

Pitch value p maps to semitones (p - 15360) / 256. So a cry must:

* be **at most 2.34 s** (later audio is never heard; we aim much shorter),
* say who it is in the **first 0.33 s** (doubles mode cuts there),
* still sound right **reversed** (Growl, Hyper Voice), **pitched down 3.6 semitones** (faint) and doubled
  with a detuned copy (chorus). `cry.py modes` renders all of them.

## 5. What the vanilla set looks like (`cry.py survey`, `reference/vanilla_stats.json`)

| Measure | 5 % | median | 95 % |
|---|---|---|---|
| Length | 0.33 s | 0.73 s | 1.43 s (max 2.24 s, Jynx) |
| Peak | 0.79 | 0.94 | 0.98 |
| RMS | 0.18 | 0.25 (about -12 dBFS) | 0.30 |
| Spectral centroid | 1150 Hz | 1690 Hz | 2310 Hz |

Cries are mastered hot and squashed. Many vanilla cries do not start or end at silence (hard cuts); ours do,
which only removes clicks.

Spectrogram character (see `out/review.png`): a buzzy, harmonic-rich source with strong energy between 1 and
3 kHz, often with **frame-stepped pitch** (flat lines that jump, the chip-era way of drawing a cry) and a
grey DPCM noise floor. The synth's defaults (lip-radiation pre-emphasis, formants, `pitch_step`) aim there.

## 6. The gate (`cry.py check`)

Hard rules (fail = not installed): 10512 Hz; length <= 2.34 s; head peak in the first 0.33 s >= 60 % of the
cry's peak; RMS in [0.12, 0.40] (the whole vanilla range); DPCM SNR >= 10 dB. Soft rules (warn): length in the
vanilla range and 0.5x-1.6x of the slot's original; RMS in the vanilla middle 90 %; peak >= 0.79; brightness
near the vanilla band; starts/ends at silence; DPCM SNR >= 16 dB. Calibration: all 388 vanilla cries pass
every hard rule.

## 7. Checked against the ROM

`romtest.py` builds a scratch copy of the game with the new cries in their slots and records them (and the
vanilla originals) from mGBA. On Torchic, the preview model (`gba.play_in_game` + zero-order hold to 44.1 kHz)
matches the ROM recording's length (0.450 vs 0.453 s) and its energy per band within 1-2 dB from 0 to 20 kHz.

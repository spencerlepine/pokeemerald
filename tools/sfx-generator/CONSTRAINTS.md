# Sound-effect constraints (Emerald / GBA)

Researched 2026-11-01 from the game source in `../../game` and checked against recordings from the built ROM.
This file is sfx-generator's own copy: cry-generator keeps a separate one on purpose. `gba.py` holds every
number below as a constant; the gate in `sfx.py check` enforces them.

## 1. Two kinds of voices

The GBA has two sound systems, and vanilla SEs use both.

### Direct Sound (PCM), mixed in software by m4a

| Fact | Value | Source |
|---|---|---|
| Mixer rate | **13379 Hz**: every PCM voice is resampled to it, so nothing above **6689 Hz** exists on the PCM side | `m4aSoundInit`, `SOUND_MODE_FREQ_13379` (`src/m4a.c:79`) |
| Output | 8-bit DAC | `SOUND_MODE_DA_BIT_8` |
| Voices at once | **5** (of 12 the engine allows), shared by music, SEs and cries | `5 << SOUND_MODE_MAXCHN_SHIFT` |
| Master volume | 12 / 15 | `12 << SOUND_MODE_MASVOL_SHIFT` |
| Samples | 8-bit signed mono, any rate (vanilla non-cry samples: 64 at 13379 Hz, the rest 1672-53516 Hz); key 60 = native rate | `sound/direct_sound_samples/*.wav`, `sound/direct_sound_data.inc` |
| Build | uncompressed: `wav2agb -b` (loop points come from the .wav `smpl` chunk) | `audio_rules.mk` |
| Reverb | **50 on every song** (all 269 SE and 209 of 210 BGM lines in `midi.cfg` have `-R50`); it is global to the PCM mixer | `m4a_1.s` `SoundMainRAM_Reverb` |

The reverb is a feedback echo: each new frame of the PCM buffer starts as (L + R, 6 frames ago) + (L + R,
7 frames ago), times reverb / 512. For a centred voice: `y[n] = x[n] + (y[n-1344] + y[n-1568]) * 50/256`
at 13379 Hz, two taps about 0.1 s back, loop gain 0.39. It never touches the Game Boy channels.

### The four Game Boy (CGB / PSG) channels, hardware

| Channel | What it can do | Notes |
|---|---|---|
| Square 1 | duty 12.5 / 25 / 50 / 75 %, 11-bit frequency `f = 131072 / (2048 - x)`, 4-bit volume, **hardware pitch sweep** (step every t/128 s, `x += or -= x >> shift`) | sweep is square 1 only |
| Square 2 | the same without sweep | |
| Wave | 32 steps of 4 bits, `f = 65536 / (2048 - x)`, volume only 0 / 25 / 50 / 100 % | |
| Noise | 15-bit LFSR (hiss) or 7-bit (metallic, tonal), clock `524288 / r / 2^(s+1)` with r in 0.5, 1..7 and s in 0..13 | 112 legal clocks |

m4a drives them per frame (59.73 Hz): volume envelopes in 4-bit steps (`CgbSound`, `src/m4a.c:925`;
the hardware envelope ticks at 64 Hz), pitch and vibrato updated once a frame. One of each at a time, shared
with music: an SE that takes a square steals it from the BGM.

## 2. How a vanilla SE is built

| Fact | Value | Source |
|---|---|---|
| Format | a MIDI file `sound/songs/midi/se_*.mid` turned into a track by `mid2agb` with options from `midi.cfg` | `audio_rules.mk` |
| Options | `-E -R50 -G<voicegroup> -V<volume> -P<priority>`: exact gate times, reverb 50, a voicegroup, volume 80-127, priority 4-5 | `midi.cfg` |
| Voicegroups | `rs_sfx_2` (199 SEs), `rs_sfx_1` (50), `frlg_sfx` (20) | `sfx.py survey` |
| Voices in them | Direct Sound samples (bells, drums, wind, bubbles, synths), square 1/2 (with sweep), noise; wave almost never | `sound/voicegroups/*_sfx*.inc` |
| Player | `MUSIC_PLAYER_SE1` (3 tracks), `SE2` (9), `SE3` (1) | `sound/song_table.inc`, `music_player_table.inc` |
| Length | 5 % 0.15 s, median **0.55 s**, 95 % **3.2 s**, max 8 s (`se_roulette_ball`) | `reference/vanilla_se.json` |
| Free song ids | **270-349** are `dummy_song_header` slots: room for 80 net-new SEs without moving any id | `song_table.inc`, `include/constants/songs.h` |
| Linking | every song object is named in `ld_script.ld`; a new song must be added there | `ld_script.ld` |

## 3. How sfx-generator fits inside this

A spec draws an SE with layers on the same voices the hardware has:

* `square`, `wave`, `noise` layers are **register-exact emulations** of the Game Boy channels: pitch snapped to
  the 11-bit register and held per frame, volume in 16 steps per frame (wave: 4 levels), the real sweep
  arithmetic (including overflow cut-off), the real LFSR at one of the 112 legal clocks.
* `pcm` layers are free synthesis (oscillators, unison, FM, AM, ring, moving filters, drive, bit-crush) that
  ends up as an 8-bit sample, like the game's own sampled sounds.

The whole SE is rendered to **one 8-bit sample at 13379 Hz** and installed as a one-note MIDI on its own
one-voice voicegroup (`voice_directsound_no_resample`, ADSR 255/0/255/0; loops use `voice_directsound` with a
short release). That costs one PCM voice while it plays (vanilla PCM SEs cost the same) and 13 KB of ROM per
second (the linker reports 14.9 MB of the 32 MB ROM space used). What you hear in the preview is what the game plays.

The trade-off: real Game Boy channels are not limited to 6.7 kHz, so a chip layer baked into the sample loses
the very top of its sparkle. A MIDI export that drives the real channels is possible later for chip-only SEs.

Hardware budget the gate enforces per moment (so an SE could exist on the real chip): at most 2 squares (the
sweep on one of them), 1 wave, 1 noise, and 3 PCM layers (the mixer has 5 and the music needs some).

## 4. The gate (`sfx.py check`)

Hard: 13379 Hz; length <= 8 s; peak 0.5-1.0; the voice budget above. Soft: length <= 3.2 s (unless it loops);
DC near 0; starts and ends at silence; ROM cost <= 40 KB.

## 5. Checked against the ROM

`romtest.py` builds a scratch copy of the game, installs the SEs with the real installer, records vanilla
(for hot-swaps) and new SEs out of mGBA. The preview (`gba.play_in_game` with the m4a reverb, plus zero-order
hold to 44.1 kHz) matches the ROM recordings within about 1-2 dB per band from 250 Hz to 20 kHz on five SEs.

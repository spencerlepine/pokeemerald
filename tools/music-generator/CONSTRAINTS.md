# Music constraints (Emerald / GBA)

Researched 2026-11-01 from the game source in `../../game` and checked against recordings from the built ROM.
This is music-generator's own copy (sfx-generator and cry-generator keep theirs on purpose). Every number below is
a constant in `gba.py`; `checks.py` enforces them on every render.

## 1. What a song is in Emerald

| Fact | Value | Source |
| --- | --- | --- |
| File | a type-1 MIDI in `sound/songs/midi/<song>.mid`, 24 ticks per quarter note (every vanilla file) | `sound/songs/midi/` |
| Build | `mid2agb` turns it into m4a track data (`<song>.s`) with the options on its `midi.cfg` line | `audio_rules.mk`, `tools/mid2agb` |
| Options | `-E` exact gate times, `-R50` reverb 50 (on 209 of 210 BGM lines), `-G<voicegroup>`, `-V<volume>` (master 76-127), `-P<priority>` (battle songs 1, fanfares 5) | `midi.cfg` |
| Tracks | one MIDI channel = one m4a track. The BGM player has **10 tracks**; a song with more loses the rest | `music_player_table.inc` |
| Clocks | 24 per beat; every note, gate and wait is a whole number of clocks | `mid2agb` (`agb.cpp`) |
| Tempo | one byte holding **bpm / 2**: even tempos only, 2-510 bpm (vanilla 44-214, median 128) | `TEMPO , bpm*tbs/2` |
| Loop | marker (meta text) events `[` and `]` on any track: mid2agb writes a label at `[` and a `GOTO` back to it at `]` in every track | `midi.cpp` |
| One-shot | no markers: the song plays once and ends with `FINE` (fanfares, cues) | |
| Controllers | CC1 MOD, CC7 VOL, CC10 PAN, CC20 BENDR, CC21 LFOS, CC22 MODT, CC24 TUNE, CC26 LFODL, CC33 PRIO | `midi.cpp` |
| Song ids | 0-609 used (`include/constants/songs.h`). New music goes after `PH_NURSE_SOLO` (609); the phoneme range is bounded by `FIRST/LAST_PHONEME_SONG`, so appending is safe. Every song object must be named in `ld_script.ld` | `songs.h`, `song_table.inc`, `ld_script.ld` |
| Size | 2.8 KB median of track data, 16 KB max (mid2agb compresses repeats with `PATT`) | `generate.py survey` |

Timing on the hardware: each VBlank (59.7275 Hz) the player adds `tempo` to a counter and plays one clock per
150 units. Every event therefore lands on a frame, and a loop that is not a whole number of frames (most of them,
vanilla included) plays each pass up to one frame (16.7 ms) apart, note by note. Tempos where
`loop_clocks * 150 / tempo` is a whole number make the loop frame-exact (for a 16-bar 4/4 loop: 96, 100, 120,
128, 144, 150, 160, 180, 192, 200 bpm).

## 2. The voices

A song plays one **voicegroup**: 128 program slots (`sound/voicegroups/<name>.inc`). Each slot is one of:

| Macro | What it plays | Budget |
| --- | --- | --- |
| `voice_directsound` / `_no_resample` / `_alt` | an 8-bit sample (piano, strings, flute, timpani...), pitched by resampling from key 60 = its native rate; `_no_resample` plays at native rate whatever the key (drums) | **5 voices at once** for music, SEs and cries together |
| `voice_square_1` / `_alt` | Game Boy square, duty 12.5/25/50/75 %, with hardware sweep | **1 note at a time** |
| `voice_square_2` / `_alt` | the same without sweep | 1 note |
| `voice_programmable_wave` / `_alt` | 32 x 4-bit wave table (`ProgrammableWaveData_*`), volume 0/25/50/100 % | 1 note |
| `voice_noise` / `_alt` | 15-bit hiss or 7-bit metallic noise, pitch from the key | 1 note |
| `voice_keysplit` | a sub-voicegroup chosen by key through a `keysplit_*` table (strings, piano, brass) | as the sub-voice |
| `voice_keysplit_all` | a drum kit: key n plays sub-slot n at its own base key | as the sub-voice |

Empty slots are a filler (`voice_square_1 60, 0, 0, 2, 0, 0, 15, 0`, 17,792 of them): a program that lands on
one plays a stray square note, so `checks.py` rejects it. `python3 generate.py voices` lists every slot of every
voicegroup a vanilla song uses in [`docs/voicegroups.md`](docs/voicegroups.md).

Envelopes are per frame: Direct Sound ADSR on 0-255 (attack adds, decay and release multiply by n/256),
Game Boy ADSR in 4-bit steps (frames per step, sustain 0-15).

## 3. The mixer

| Fact | Value | Source |
| --- | --- | --- |
| PCM mix rate | **13379 Hz** (nothing above 6689 Hz on the PCM side), no interpolation | `m4aSoundInit`, `SOUND_MODE_FREQ_13379` |
| PCM voices | **5** (`SOUND_MODE_MAXCHN`); a 6th note steals a releasing voice first, then the oldest of equal or lower priority | `m4a.c` `ply_note` |
| DAC | 8 bits, master volume 12/15 | `SOUND_MODE_DA_BIT_8`, `SOUND_MODE_MASVOL` |
| Reverb | on the PCM bus only: each frame adds (L+R from 6 and 7 frames back) x 50/256 | `m4a_1.s` `SoundMainRAM_Reverb` |
| Game Boy channels | not resampled, not reverbed; shared with SEs (a menu blip takes a square from the song) | |

What vanilla songs do (`reference/vanilla_songs.json`, 204 songs): 4-10 tracks (median 8); at most 4 (98 songs)
or 5 (71) Direct Sound notes at once, 21 songs briefly ask for a 6th; 182 use square 2, 178 square 1, 147 the
wave, 97 noise; 10 songs ever put two parts on one Game Boy channel at once. Loops: 7.5-82 s (LOOP songs, 5-95 %),
35-77 s (AMBIENT); jingles 1-13 s.

## 4. What the tool enforces

Errors (the song is broken or the build fails): more parts than the player has tracks; odd or out-of-range
tempo; a program that is an empty slot or a key that lands on an empty key-split or drum slot; channel, volume,
pan, priority out of range; an empty loop; mid2agb rejecting the file or not writing a `GOTO` for a looping song.

Warnings (vanilla songs never or rarely do this): notes starting while 5 Direct Sound voices play (a voice is
stolen); more Direct Sound notes at once than 90 % of vanilla songs; two parts on one Game Boy channel at once;
chords on a Game Boy part; a sample pitched more than 4x the mixer rate (aliasing); notes ringing past the loop
end; a loop length outside the vanilla range for its form; more track data than the largest vanilla song; the
PCM mix clipping.

Loop seam (`loopcheck.py`, from the z-day tool): run on the preview of the real playback order (intro, then the
loop three times), so the seam includes release tails crossing the jump, the reverb carrying over and the frame
grid. Each check compares the seam with the song's own bar lines; see the docstring for the list.

## 5. Checked against the ROM

`romtest.py` builds a scratch copy of the game with a small hook that starts a song by id and parks the main
loop (sound keeps running from the VBlank and VCount interrupts), then records mGBA's audio. A recording of
vanilla `mus_route101` against `generate.py vanilla MUS_ROUTE101`: envelopes correlate at 0.70 once aligned, and
a least-squares fit of the two spectrograms gives the Game Boy / Direct Sound balance `CGB_GAIN = 0.27`
(`preview.py`). The preview is a model, not an emulator: no LFO vibrato, no pitch bend, no sweep, CGB pitch not
register-quantized. Judge timing, voicing, voice counts and the loop by the preview; judge the final sound by
the ROM recording.

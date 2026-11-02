# music-generator

**Status:** DONE. Approved by the owner on 2026-11-01. Installed: `MUS_INTRO_CRAWL` (the opening crawl theme), and `MUS_INTRO` (the boot cutscene, scored to picture; with the owner for review). Every other song the player hears (175) is composed in `song-schemas/` and shipped to the wiki
(`python3 ../../wiki/tools/ship_audio.py song-schemas/<name>.yaml`): `rewrite_status` GENERATED in
`../../wiki/database/music.csv`, the .mid in `../../wiki/audio/sound/songs/midi/`, an MP3 preview in
`../../wiki/audio/previews/music/`. None of those are installed in `../../game` yet (`generate.py install`, after a ROM listen).

Known quirks (worked around in the models, not fixed): a section `fill` goes to every drum part in the section,
so two drum parts with different kits need their fills written into the groove; a part or phrase named `off`
(or `on`, `yes`, `no`) is read by YAML as a boolean; `analyze_reference.py --song` takes a net-new row by its
asset id (`net:mus-...`), not its constant.

Turns a song model (`song-schemas/<name>.yaml`, the z-day ai-music notation) into an Emerald song: a MIDI file
for `mid2agb`, played by the GBA m4a engine through one of the game's own voicegroups. Every limit of the
hardware and the engine is hard-coded (`gba.py`, sourced in [`CONSTRAINTS.md`](CONSTRAINTS.md)), so what comes
out sounds like Emerald because it is made of the same parts: 5 Direct Sound voices, 4 Game Boy channels, 10
tracks, 24 clocks per beat, reverb 50.

Read [`CONSTRAINTS.md`](CONSTRAINTS.md) first.

## Setup

```bash
pip install -r requirements.txt       # numpy, scipy, pyyaml; ffmpeg on PATH for analyze_reference.py
python3 generate.py survey            # once: vanilla stats -> reference/vanilla_songs.json (the warning ranges)
python3 generate.py voices            # once: every voicegroup's slots -> docs/voicegroups.md
```

`mid2agb` is built from `../../game/tools/mid2agb` on first use. `romtest.py` also needs the play-tester
toolchain (`../play-tester/scripts/setup-ubuntu.sh`: agbcc, mGBA 0.11, Xvfb).

## Commands

```bash
python3 generate.py render song-schemas/fortress-vader.yaml   # check, .mid, .s, preview, loop check, report
python3 generate.py check song-schemas/fortress-vader.yaml    # limits only
python3 generate.py vanilla MUS_FALLARBOR                     # a vanilla song through the same preview (A/B)
python3 generate.py voices mt_chimney                         # one voicegroup's slots
python3 analyze_reference.py --song MUS_FALLARBOR --end 120   # read the song's film cue (see below)
python3 romtest.py song-schemas/fortress-vader.yaml           # scratch ROM, record from mGBA -> out/rom/
python3 generate.py install song-schemas/x.yaml               # into ../../game (owner-approved songs only)
```

`render` writes `out/<name>/`: `<mus_x>.mid` (the file the game gets), `<mus_x>.s` (mid2agb's output, which
proves the game build accepts it), `<name>_preview.wav` (intro then the loop three times, as the m4a engine
plays it), `report.md` / `report.json` (tempo, lengths, tracks, voices per part, voice peaks, bytes, errors,
warnings, loop check). It exits non-zero on errors. A song is ready for the owner when it has no errors, no
warnings it cannot explain, and the loop check passes.

## The workflow (for an LLM or a human)

One wiki row at a time. The row (`../../wiki/database/music.csv`) gives the brief (`sw_subject`), the label
(`music_category`, `music_form`), the vanilla song's tech notes (`voicegroup`, `volume`, `tempo_bpm`, `length_s`,
`loops`), and the film cue to work from: `ref_use`, `ref_tracks`, `ref_files`, `ref_notes`
(see [`../../wiki/music/README.md`](../../wiki/music/README.md)).

1. **Listen to the reference.** `python3 analyze_reference.py --song MUS_X [--start s --end s]` decodes the
   row's main cue and prints tempo (with half/double candidates), key, chords per bar, sections and loop
   candidates, and writes `out/analysis/<name>.yaml` with a melody draft per bar in the song notation. The draft
   is rough on an orchestra: pitch classes and contour are usually right, octaves and rhythms often are not, and
   rubato cues (Binary Sunset) defeat the beat tracker (force it with `--bpm`). Use `ref_notes` to pick the part
   of the cue (`--start`/`--end`).
2. **Decide what to keep**, by `ref_use`:
   - `ARRANGE`: the cue's theme, harmony and groove, cut down to 8-24 bars that loop. Pick a span that ends on
     the harmony that leads back to its start (the analyzer's loop candidates help), and write the theme from
     the draft plus your own knowledge of it. Keep the cue's tempo (rounded to even).
   - `STYLE`: an original melody; take only the cue's tempo, key colour, texture and instrumentation.
   - `SCRATCH`: write it from the brief; the vanilla song's length and loop/no-loop still apply.
3. **Pick the voicegroup.** For a hot-swap, start from the vanilla song's (`voicegroup` in the row): its
   samples are what that place sounded like. Otherwise pick one whose slots fit the cue
   ([`docs/voicegroups.md`](docs/voicegroups.md); `mt_chimney` has brass, strings and timpani, `fallarbor`
   flute, harp and strings, `rs_drumset` slot 0 is the usual drum kit).
4. **Write the model** in `song-schemas/<name>.yaml` (format below), with `replaces: MUS_X` (hot-swap: keeps
   the song id and every caller) or `constant: MUS_NEW` (net-new: the row's `sw_constant`).
5. **Fit it to the hardware**: melody, harmony and bass on Direct Sound (at most 4 notes at once leaves a voice
   for sound effects), and lean on the Game Boy channels for pulses, arpeggios, counter-lines and noise drums,
   one note each, which is how vanilla Emerald gets its size. `render` until there are no errors and the loop
   check passes; read the warnings.
6. **Hear it in the ROM**: `romtest.py` (the vanilla song is recorded first for a hot-swap).
7. **Owner approval**, then `generate.py install`, a game build, and `rewrite_status` DONE through the wiki
   (`game_status` DONE in the row's source table).

## Song model format

Same notation as the z-day tool, retargeted: a part is an m4a track playing one `program` of the voicegroup,
and every time is a whole number of clocks.

### Top level

| Field | Meaning |
| --- | --- |
| `name` | output folder name |
| `replaces` / `constant` | `MUS_X` to hot-swap, or the new constant for a net-new song |
| `form` | `LOOP`, `AMBIENT`, `CUE`, `JINGLE` (the wiki's `music_form`; picks the length warning range) |
| `voicegroup` | a voicegroup name (`docs/voicegroups.md`) |
| `master_volume` | the `-V` value, 1-127 (vanilla 76-100) |
| `song_priority` | optional `-P` value (vanilla: battle 1, fanfares 5) |
| `tempo` | bpm, even, 2-510 |
| `steps_per_beat` | grid per quarter note; must divide 24 (1, 2, 3, 4, 6, 8, 12, 24) |
| `time_signature` | `[4, 4]`, `[3, 4]`, `[6, 8]`... |
| `transpose`, `swing`, `swing_unit`, `seed` | as in z-day |
| `loop` | `false` for a one-shot (no loop markers) |
| `player` | `BGM` (default) |
| `parts`, `phrases`, `progressions`, `grooves`, `sections`, `arrangement`, `loop_start` | as in z-day |
| `cues`, `sync` | scoring to picture (below): the cue sheet, and where each cue lands (`cue: "bar:beat"`) |

Sections can also carry `tempo` (bpm from the section start), `tempo_at` (`[[beats from the start, bpm], ...]`)
and `programs` (`{part: slot}`: the part's track switches program for the section, as vanilla tracks do).

## Scoring to picture (cutscenes)

A cutscene song has to land on the frames of the animation, so it is written against a cue sheet
(`cues/<scene>.yaml`: each event's frame, kind `hit` / `section` / `soft`, tolerance, and where the frame comes
from) and checked three ways:

1. **Measure the scene on the ROM.** `python3 romsync.py --as-is --video` runs the game headless in libmgba
   (`romcap/romcap.c`: every frame and every audio sample, no real-time audio device to drop samples) and logs,
   per frame, the scene's counter (`gIntroFrameCounter`) and the BGM player's clock. That gives the cue sheet's
   `shift`: where the counter and the song's own time line part (the boot intro: clock 0 plays when the counter
   reads 2, and loading scene 2 costs 3 lag frames on which the picture stands still and the music does not).
2. **Write the song on that grid.** Change tempo per section so each scene change is a bar line (vanilla
   `mus_intro` does this 8 times), and place hits on a fine step grid (`steps_per_beat: 12`) at their frame.
   `python3 cuesync.py check song.yaml` prints every cue with the frame its `sync` position plays on (the exact
   m4a accumulator, `Song.frame_of`), the notes starting there, and the audio onset strength of the preview
   against the 2 s around it; it fails on a position off by more than the tolerance or a hit under 3x.
3. **Verify on the ROM.** `python3 romsync.py song.yaml --video` installs the song in a scratch copy, builds,
   records, and runs `cuesync.py rom`: the clock the engine was really on at each cue frame, plus the onset check
   on the ROM recording. `capture.mp4` is the picture with its music at true speed, for the owner.

### Parts

```yaml
parts:
  trumpet: {program: 56, channel: 0, volume: 104, pan: 6, range: [G3, A5], gate: 0.9, humanize: {vel: 4}}
  bass:    {program: 82, channel: 3, volume: 110, role: bass, octave: 2}
  snare:   {program: 126, channel: 5, volume: 60, role: drums, kit: {sn: C5, rim: G5}}
```

`program` is the voicegroup slot. `channel` is the MIDI channel (one part per channel, default its index).
`volume` 0-127 (CC7), `pan` -64..63 (CC10), `gate` the note length fraction, `octave` where `^n` chord tones sit,
`range` where `ch` chords are voiced, `mono` for Game Boy parts. Optional controllers: `mod`, `lfo_speed`,
`mod_type`, `lfo_delay`, `bend_range`, `priority`. A drum part has `role: drums` and a `kit` naming keys (a drum
kit program plays each key's own sample; a noise program plays the key as the noise pitch).

### Notes, chords, drums, sections

Bars split by `|`, each adding up to the bar in steps. `A4:4` note, `r:4` rest, `~:4` tie, `^1`..`^4` chord
tones (`+`/`-` octave), `ch` the whole chord, `>` accent, `_` soft, `'` staccato before the duration
(`D5':1`). Chords: `"Am | F | C | G"`, `"Dm:4 E:4"`. Drum lines: `.` rest, `x` hit, `X` accent, `o` ghost,
`r`/`R` roll, `f` flam. Sections: `bars`, `chords`, `parts`, `fill` (replaces the last bar's groove), and
`gain` / `ramp` as **velocity offsets** (there is no mixer on the GBA: a part gets quieter by playing softer).

## Prototypes

| Model | Row | What it shows |
| --- | --- | --- |
| [`fortress-vader.yaml`](song-schemas/fortress-vader.yaml) | `net:mus-fortress-vader` (MUS_FORTRESS_VADER, net-new) | ARRANGE of the Imperial March: 104 bpm (the cue's own 103.4), 2-bar intro, 16-bar loop; trumpet theme, horn an octave down, strings, wave bass, timpani, noise snare, square pulse in the bridge. 7 tracks, 4 Direct Sound notes max, 1.1 KB |
| [`fallarbor-inyusu-tor.yaml`](song-schemas/fallarbor-inyusu-tor.yaml) | `audio:MUS_FALLARBOR` (hot-swap) | STYLE of Padmé's Destiny: original A minor melody at 88 bpm on the vanilla `fallarbor` voicegroup; flute, harp arpeggios, string pad, fretless bass, square echo. 5 tracks, 0.9 KB |

Both render with no errors or warnings and pass the loop check. Neither is installed in `../../game`; both rows
stay TODO.

## Installed

| Model | Row | Notes |
| --- | --- | --- |
| [`intro-boot.yaml`](song-schemas/intro-boot.yaml) | `audio:MUS_INTRO` (hot-swap; with the owner for review, wiki row still TODO) | Original cue in the Star Wars idiom for the boot cutscene (scenes 1-2, 34.6 s), scored to [`cues/intro-boot.yaml`](cues/intro-boot.yaml): 10 tempo zones, 29 cues (drops, camera rise, shuttle and TIE, twin suns, scene cut, the speeder's moves, the last shot), all within 2 frames on the ROM; the raiders pop up over a steady snare groove instead of a stab each (owner's call). 10 tracks (the flute's track is the noise snare in the chase), 5 Direct Sound notes max, 2 KB |
| [`title-throne.yaml`](song-schemas/title-throne.yaml) | `audio:MUS_TITLE` (hot-swap; with the owner for review, wiki row still TODO) | ARRANGE of the Throne Room march (`soundtrack:new-hope:16`, 0:00-0:50), transcribed from the cue (melody on a 16th grid, harmony per half bar; beat chroma vs the cue 0.60, 0.28 misaligned). 120 bpm in F: 4-bar fanfare once, then a 64 s loop (march, second strain with horn, quiet flute and harp, full tutti ending on the march's own C pickup). Loops, so the title screen no longer times out back to the boot intro. 10 tracks, 5 Direct Sound notes max, 2.3 KB |
| [`intro-crawl.yaml`](song-schemas/intro-crawl.yaml) | `net:mus-intro-crawl` (MUS_INTRO_CRAWL, id 610) | ARRANGE of the 1977 main title from the owner's recording of the original crawl (`wiki/music/concept/intro-crawl-1977.mp3`). Starts as the logo recedes on the title screen (`IntroCrawl_StartMusic`), 75 s of fanfare, theme and ending, then a quiet 4-bar loop; the crawl fades it out at about 77 s. 10 tracks, 2 KB |

## Files

| File | What |
| --- | --- |
| `gba.py` | hardware and engine constants; voicegroup, key split, sample and wave-table readers; mid2agb wrapper |
| `song.py` | song model loader: notation -> notes in clocks |
| `midi.py` | notes -> type-1 MIDI the way the vanilla files are laid out; MIDI reader for vanilla songs |
| `preview.py` | software model of the m4a mixer (frame timing, 5-voice stealing, ADSR, reverb, 8-bit DAC, Game Boy channels) |
| `checks.py` | the errors and warnings above |
| `loopcheck.py` | loop seam validation, adapted from z-day |
| `generate.py` | command line: render, check, vanilla, voices, survey, install |
| `analyze_reference.py` | reference cue -> tempo, key, chords, melody draft, sections, loop candidates |
| `romtest.py` | scratch ROM with the songs installed, recorded from mGBA |
| `cuesync.py` | scoring to picture: cue sheet vs song positions, note onsets and audio spikes (preview, or a ROM log + recording) |
| `romsync.py`, `romcap/romcap.c` | the ROM run headless in libmgba: per-frame log (scene counter, BGM clock), exact audio, video -> `out/rom-sync/` |
| `cues/` | cue sheets: the frames a cutscene song must hit |
| `reference/vanilla_songs.json` | survey of the 204 vanilla songs |
| `docs/voicegroups.md` | every voicegroup's slots |
| `song-schemas/` | song models |
| `out/` | renders, analyses and ROM recordings (not committed) |

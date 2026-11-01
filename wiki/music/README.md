# Film soundtrack reference

The six John Williams Star Wars soundtrack albums (Episodes I to VI, 85 tracks), kept here as the reference the
music generator ([`../../tools/music-generator`](../../tools/music-generator)) arranges from. This folder is
self-contained: it was copied out of starwars-db and nothing reads that repo any more.

These are commercial recordings, used only as listening references for writing the game's own GBA songs. They
are not game assets and never go into `../game`.

| File | One row per | Columns |
| --- | --- | --- |
| `soundtrack_albums.csv` | album | `album_id`, `event_id` (the film), `title`, `composer`, `performer`, label, years, `track_count`, playlist link |
| `soundtrack_tracks.csv` | track | `track_id` (`soundtrack:<album>:<NN>`), `album_id`, `track_number`, `title`, `duration_seconds`, `category` (main_theme, action, character_theme...), `essential`, `audio_path` (relative to this folder), `audio_duration_seconds`, `audio_bitrate_kbps`, `audio_status`, source video |
| `soundtrack_track_entities.csv` | track to databank entity link | `track_id`, `entity_id`, `relationship` (`depicts`, `leitmotif`) |
| `soundtrack/<album>__<NN>.mp3` | track audio | 128 kbps MP3 |

## Which cue each game song uses

`../mapping/music.csv` assigns cues to every song with `rewrite_status` TODO (all 85 tracks are used at least once):

- `ref_use`: `ARRANGE` (a chiptune arrangement of the cue: its melody, harmony and groove, cut down to a loop),
  `STYLE` (an original song in the cue's style: tempo, key colour, rhythm and instrumentation, no melody quoted)
  or `SCRATCH` (written from scratch; no film cue fits a Pokemart, a level-up jingle or a Poke Ball catch).
- `ref_tracks`: pipe-separated `track_id`s. The first is the main reference.
- `ref_notes`: which part of the cue, when only part of it fits ("the Arena half").

`tools/build_music.py` copies these into `database/music.csv` with the titles (`ref_titles`) and file paths
(`ref_files`, relative to the wiki root), and warns about unknown tracks, missing files, a SCRATCH song with
tracks or an ARRANGE/STYLE song without them.

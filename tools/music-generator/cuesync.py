#!/usr/bin/env python3
"""Lock a song to an animation: compare the frames a song's accents land on with the frames of a cutscene.

A cue sheet (`cues/<scene>.yaml`) lists the scene's key frames (frame 0 = the frame the song starts). A song
model names the cue sheet (`cues:`) and says where each cue lands in the music (`sync:` cue -> "bar:beat",
beat counted from 1, fractions allowed: "3:4.5" is the "and" of beat 4 in bar 3). The m4a engine's own clock
(Song.frame_of: tempoC += tempo each VBlank, one clock per 150) turns every position into a frame.

  python3 cuesync.py check song-schemas/intro-boot.yaml   # sync table, onset check on the preview, exit 1 on a miss
  python3 cuesync.py vanilla MUS_INTRO cues/intro-boot.yaml  # what the vanilla song does at each cue
  python3 cuesync.py rom out/rom-sync/<name>/log.csv song-schemas/intro-boot.yaml  # verify a ROM capture

Three checks per cue, strictest first:
  position  the frame of the `sync:` position (exact engine timing) is within the cue's `tol`
  notes     notes start within `tol` frames of the cue: summed velocity, and for a hit the loudest onset
  audio     spectral-flux onset strength of the rendered preview (or a ROM recording) within `tol`, as a
            multiple of the median onset strength of the 2 s around it: a hit should be a clear spike (>= 3x)
"""
from __future__ import annotations

import argparse
import csv
import struct
import sys
import wave
from pathlib import Path

import numpy as np
import yaml

import gba
import preview
from song import Song, load

HERE = Path(__file__).resolve().parent
SPIKE = 3.0          # a hit's audio onset must be at least this many times the median onset around it
CONTEXT = 60         # frames each side for that median (2 s): a hit has to stand out from its own surroundings


def load_cues(path) -> dict:
    """Cue sheet; each cue gets `song_frame`: its `frame` (the scene's own counter) on the song's time line,
    through the sheet's measured `shift` table ([[from_frame, add], ...])."""
    d = yaml.safe_load(Path(path).read_text())
    shifts = sorted(d.get("shift") or [[0, 0]])
    for c in d["cues"]:
        c.setdefault("tol", 3)
        c["song_frame"] = int(c["frame"]) + max((a for f, a in shifts if f <= int(c["frame"])), default=0)
    return d


def position_clock(song: Song, pos: str) -> int:
    bar, beat = str(pos).split(":")
    return (int(bar) - 1) * song.clocks_per_bar + int(round((float(beat) - 1) * gba.CLOCKS_PER_BEAT))


# ------------------------------------------------------------------ audio onsets

def frame_flux(x: np.ndarray, rate: int, floor_db: float = 48.0) -> np.ndarray:
    """Onset strength per VBlank frame: positive spectral flux (dB) of a mono mix, 1 value per frame. Levels more
    than floor_db under the loudest bin are clipped: the GBA's 8-bit DAC has about 48 dB of range, and below that
    is quantization noise, which would otherwise read as a constant stream of tiny onsets."""
    m = x.mean(axis=1) if x.ndim == 2 else x
    hop = rate / gba.FRAME_HZ
    n = int(len(m) / hop)
    win = 1024
    w = np.hanning(win)
    spec = np.empty((n, win // 2 + 1))
    for f in range(n):
        c = int(f * hop)
        seg = m[c:c + win]
        if len(seg) < win:
            seg = np.pad(seg, (0, win - len(seg)))
        spec[f] = np.abs(np.fft.rfft(seg * w))
    db = 20 * np.log10(spec + 1e-9)
    db = np.maximum(db, db.max() - floor_db)
    out = np.zeros(n)
    out[1:] = np.maximum(0, np.diff(db, axis=0)).sum(axis=1)
    return out


def read_wav(path) -> tuple[np.ndarray, int]:
    with wave.open(str(path)) as w:
        rate, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
    return x.reshape(-1, ch), rate


# ------------------------------------------------------------------ note onsets

def song_onsets(song: Song) -> list[tuple[int, int, str, int]]:
    """(frame, velocity, part, key) for every note of a model."""
    return [(song.frame_of(n.tick), n.vel, n.part, n.key) for n in song.notes]


def midi_onsets(path) -> tuple[list[tuple[int, int, str, int]], int]:
    """Same for a MIDI file with tempo changes (vanilla songs), through the same engine accumulator."""
    d = Path(path).read_bytes()
    tempos, notes, i, end = {0: 120}, [], 14, 0
    from midi import _rvlq
    while i < len(d) and d[i:i + 4] == b"MTrk":
        ln = struct.unpack(">I", d[i + 4:i + 8])[0]
        j, stop, t, run = i + 8, i + 8 + ln, 0, 0
        while j < stop:
            dt, j = _rvlq(d, j)
            t += dt
            st = d[j]
            if st == 0xFF:
                typ = d[j + 1]
                n, j = _rvlq(d, j + 2)
                if typ == 0x51:
                    tempos[t] = round(60e6 / int.from_bytes(d[j:j + n], "big"))
                j += n
                continue
            if st in (0xF0, 0xF7):
                n, j = _rvlq(d, j + 1)
                j += n
                continue
            if st & 0x80:
                run, j = st, j + 1
            hi, ch = run & 0xF0, run & 0x0F
            a = d[j]
            b = d[j + 1] if hi not in (0xC0, 0xD0) else 0
            j += 1 if hi in (0xC0, 0xD0) else 2
            if hi == 0x90 and b:
                notes.append((t, b, f"ch{ch}", a))
        end = max(end, t)
        i = stop
    # engine accumulator over the tempo map
    frames, c_acc, i_acc, f = [], 0, 150, -1
    while len(frames) <= end:
        f += 1
        c_acc += i_acc
        while c_acc >= 150 and len(frames) <= end:
            if len(frames) in tempos:
                i_acc = tempos[len(frames)]
            frames.append(f)
            c_acc -= 150
    return [(frames[t], v, p, k) for t, v, p, k in notes], frames[end]


def note_weight(onsets, frame: int, tol: int) -> tuple[int, int, int | None]:
    """Summed velocity of notes starting within tol frames, the number of notes, and the offset of the
    frame with the most velocity (None when nothing starts there)."""
    near = [(f, v) for f, v, _p, _k in onsets if abs(f - frame) <= tol]
    if not near:
        return 0, 0, None
    by = {}
    for f, v in near:
        by[f] = by.get(f, 0) + v
    best = max(by, key=lambda k: (by[k], -abs(k - frame)))
    return sum(v for _f, v in near), len(near), best - frame


def audio_peak(flux: np.ndarray, frame: int, tol: int) -> tuple[float, int]:
    """Strongest onset within tol frames of `frame`, as a multiple of the median onset strength of the CONTEXT
    frames around it (the hit itself excluded): how much the hit stands out from the music it sits in."""
    lo, hi = max(0, frame - tol), min(len(flux), frame + tol + 1)
    if lo >= hi:
        return 0.0, 0
    k = int(np.argmax(flux[lo:hi]))
    ctx = np.concatenate([flux[max(0, frame - CONTEXT):lo], flux[hi:frame + CONTEXT]])
    ctx = ctx[ctx > 0]
    med = float(np.median(ctx)) if len(ctx) else 0.0
    return (float(flux[lo + k] / med) if med else 0.0), lo + k - frame


# ------------------------------------------------------------------ reports

def table(rows, head) -> str:
    w = [max(len(str(r[i])) for r in rows + [head]) for i in range(len(head))]
    fmt = "  ".join("{:<%d}" % x for x in w)
    return "\n".join([fmt.format(*head), fmt.format(*["-" * x for x in w])] + [fmt.format(*map(str, r)) for r in rows])


def check(model_path, wav=None, quiet=False, offset=0) -> int:
    song = load(Path(model_path))
    cue_path = (Path(model_path).parent / song.model["cues"]).resolve()
    cues = load_cues(cue_path)
    sync = song.model.get("sync") or {}
    onsets = song_onsets(song)
    if wav is None:
        x, stats = preview.render(song, loops=1, master_volume=int(song.model.get("master_volume", 90)))
        rate = preview.OUT_RATE
    else:
        x, rate = read_wav(wav)
    flux = frame_flux(x, rate)
    if offset:
        flux = np.concatenate([np.zeros(offset), flux]) if offset > 0 else flux[-offset:]
    rows, misses = [], []
    for c in cues["cues"]:
        name, f, tol, kind = c["name"], int(c["song_frame"]), int(c["tol"]), c["kind"]
        p = sync.get(name)
        pf = err = "-"
        if p is not None:
            pf = song.frame_of(position_clock(song, p))
            err = pf - f
            if abs(err) > tol:
                misses.append(f"{name}: '{p}' plays at frame {pf}, cue {f} ({err:+d}, tol {tol})")
        elif kind != "soft":
            misses.append(f"{name}: no sync position for a {kind} cue")
        w, n, best = note_weight(onsets, f, tol)
        spike, at = audio_peak(flux, f, tol)
        if kind == "hit" and spike < SPIKE:
            misses.append(f"{name}: audio onset near frame {f} is {spike:.1f}x the music around it (a hit needs {SPIKE}x)")
        rows.append([name, kind, f, p or "-", pf, err if err == "-" else f"{err:+d}", tol, n, w,
                     "-" if best is None else f"{best:+d}", f"{spike:.1f}x {at:+d}"])
    if not quiet:
        print(f"{song.name}: tempo map " + ", ".join(f"clock {c} {t} bpm" for c, t in song.tempo_map))
        print(f"song ends at frame {song.frame_of(song.total_clocks)}; scene ends at {cues.get('scene_end')}")
        print(table(rows, ["cue", "kind", "song frame", "position", "plays", "err", "tol", "notes", "vel", "loudest",
                           "audio onset"]))
        print()
        print("\n".join(f"MISS {m}" for m in misses) or "all cues hit")
    return 1 if misses else 0


def vanilla(const: str, cue_path) -> None:
    cues = load_cues(cue_path)
    mid = gba.GAME / "sound" / "songs" / "midi" / f"{const.lower()}.mid"
    onsets, last = midi_onsets(mid)
    rows = []
    for c in cues["cues"]:
        w, n, best = note_weight(onsets, int(c["song_frame"]), int(c["tol"]))
        rows.append([c["name"], c["kind"], c["frame"], c["song_frame"], n, w, "-" if best is None else f"{best:+d}"])
    print(f"{const}: last event at frame {last}")
    print(table(rows, ["cue", "kind", "frame", "song frame", "notes", "vel", "loudest"]))


def rom(log_path, model_path, wav=None) -> int:
    """Verify a ROM capture (romsync.py): the log has one row per emulated frame with gIntroFrameCounter and
    the BGM player's clock, so each cue's frame maps to the clock the engine was really on, lag frames and
    start offset included."""
    song = load(Path(model_path))
    cues = load_cues((Path(model_path).parent / song.model["cues"]).resolve())
    sync = song.model.get("sync") or {}
    rows = list(csv.DictReader(open(log_path)))
    # this song's stretch of the log: from the row its header appears until another song replaces it
    hdr = next(r["bgm_header"] for r in rows if int(r["bgm_clock"]) > 0)
    i0 = next(i for i, r in enumerate(rows) if r["bgm_header"] == hdr)
    i1 = next((i for i in range(i0, len(rows)) if rows[i]["bgm_header"] != hdr), len(rows))
    rows = rows[i0:i1]
    by_counter = {}
    for r in rows:
        by_counter.setdefault(int(r["intro_frame"]), r)
    start = next((int(r["emu_frame"]) for r in rows if int(r["bgm_clock"]) > 0), None)
    out, misses = [], []
    for c in cues["cues"]:
        r = by_counter.get(int(c["frame"]))
        p = sync.get(c["name"])
        if r is None:
            out.append([c["name"], c["frame"], "-", "-", "-", "-"])
            continue
        clock = int(r["bgm_clock"])
        want = position_clock(song, p) if p else None
        if want is not None:
            # how many frames the music is off: when did the engine reach the wanted clock vs the cue frame
            # (a clock has played once the logged clock is past it; the counter's frame is the first row showing it)
            reach = next((int(x["emu_frame"]) for x in rows if int(x["bgm_clock"]) > want), None)
            err = reach - int(r["emu_frame"]) if reach is not None else None
            if err is None or abs(err) > int(c["tol"]):
                misses.append(f"{c['name']}: music reaches {p} at emu frame {reach}, cue shows at {r['emu_frame']}")
        else:
            err = None
        out.append([c["name"], c["frame"], r["emu_frame"], clock, p or "-", "-" if err is None else f"{err:+d}"])
    lag = [int(r["emu_frame"]) - int(r["intro_frame"]) for r in rows if int(r["intro_frame"]) > 0]
    print(f"song starts on emu frame {start}; emu frame - intro frame: min {min(lag)}, max {max(lag)} "
          f"({'no lag frames' if max(lag) == min(lag) else f'{max(lag) - min(lag)} lag frames'})")
    print(table(out, ["cue", "frame", "emu frame", "bgm clock", "position", "err (frames)"]))
    print("\n".join(f"MISS {m}" for m in misses) or "all synced cues hit on the ROM")
    rc = 1 if misses else 0
    if wav:
        print("\nROM recording:")
        rc |= check(model_path, wav=wav)
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("check")
    a.add_argument("model")
    a.add_argument("--wav", help="check this recording instead of the preview (frame 0 = its first sample)")
    a = sub.add_parser("vanilla")
    a.add_argument("const")
    a.add_argument("cues")
    a = sub.add_parser("rom")
    a.add_argument("log")
    a.add_argument("model")
    a.add_argument("--wav")
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return check(args.model, args.wav)
    if args.cmd == "vanilla":
        vanilla(args.const, args.cues)
        return 0
    return rom(args.log, args.model, args.wav)


if __name__ == "__main__":
    sys.exit(main())

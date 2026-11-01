#!/usr/bin/env python3
"""Read a reference recording (a film cue MP3 from wiki/music/soundtrack/) into the song model's terms, as a
starting point for an arrangement: tempo, meter grid, key, chords per bar, a melody draft, sections and loop
candidates. It transcribes an orchestra roughly, not exactly: the LLM (or a human) listens to the cue, keeps
what is right and fixes the rest. Output is a draft, never a finished song.

  python3 analyze_reference.py ../../wiki/music/soundtrack/new-hope__12.mp3 [--start 30 --end 90]
        [--bpm 72] [--beats-per-bar 4] [--name littleroot]
  python3 analyze_reference.py --song MUS_LITTLEROOT         the song's main ref_tracks file from the wiki

Writes out/analysis/<name>.yaml (the draft: tempo, key, per-bar chords, melody bars in the song notation, and a
section list) and prints a summary. Needs ffmpeg and numpy only.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
WIKI = HERE.parent.parent / "wiki"
SR = 22050
N_FFT = 4096
HOP = 512
PC = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
KS_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
TEMPLATES = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "dim": [0, 3, 6],
             "sus4": [0, 5, 7], "aug": [0, 4, 8]}


def decode(path: Path, start: float, end: float | None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start)]
    if end:
        cmd += ["-to", str(end)]
    cmd += ["-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<i2").astype(np.float32) / 32768


def stft(y: np.ndarray) -> np.ndarray:
    y = np.pad(y, (N_FFT // 2, N_FFT // 2))
    fr = np.lib.stride_tricks.sliding_window_view(y, N_FFT)[::HOP] * np.hanning(N_FFT).astype(np.float32)
    return np.abs(np.fft.rfft(fr, axis=1)).astype(np.float32)          # (frames, bins)


FREQS = np.fft.rfftfreq(N_FFT, 1 / SR)
FPS = SR / HOP


def onset_env(S: np.ndarray) -> np.ndarray:
    L = np.log1p(100 * S)
    flux = np.maximum(0, np.diff(L, axis=0)).sum(axis=1)
    flux = np.concatenate([[0], flux])
    flux -= np.convolve(flux, np.ones(16) / 16, "same")
    return np.maximum(flux, 0)


def tempo_candidates(env: np.ndarray, lo=50, hi=200) -> list[tuple[float, float]]:
    e = env - env.mean()
    ac = np.correlate(e, e, "full")[len(e) - 1:]
    ac /= ac[0] + 1e-9
    out = []
    for bpm in np.arange(lo, hi, 0.5):
        lag = FPS * 60 / bpm
        i = int(round(lag))
        if i + 1 >= len(ac):
            continue
        # sum the beat and its double, weighted with a gentle prior around 100 bpm
        s = ac[i] + 0.5 * ac[min(len(ac) - 1, 2 * i)] + 0.25 * ac[max(1, i // 2)]
        prior = np.exp(-0.5 * (np.log2(bpm / 100) / 1.0) ** 2)
        out.append((bpm, float(s * prior)))
    out.sort(key=lambda x: -x[1])
    best = []
    for bpm, s in out:
        if all(abs(bpm - b) > 4 for b, _ in best):
            best.append((bpm, s))
        if len(best) == 3:
            break
    return best


def track_beats(env: np.ndarray, bpm: float, tight: float = 100) -> np.ndarray:
    """Ellis dynamic-programming beat tracker. Returns beat frame indices."""
    period = FPS * 60 / bpm
    n = len(env)
    score = env / (env.std() + 1e-9)
    best = score.copy()
    back = -np.ones(n, int)
    lo, hi = int(round(period / 2)), int(round(period * 2))
    for t in range(lo, n):
        prev = np.arange(max(0, t - hi), t - lo + 1)
        if not len(prev):
            continue
        pen = -tight * np.log((t - prev) / period) ** 2
        k = int(np.argmax(best[prev] + pen))
        best[t] = score[t] + best[prev[k]] + pen[k]
        back[t] = prev[k]
    t = int(np.argmax(best[-int(period):])) + n - int(period)
    beats = [t]
    while back[beats[-1]] >= 0:
        beats.append(back[beats[-1]])
    return np.array(beats[::-1])


def chroma(S: np.ndarray, fmin=55, fmax=2000) -> np.ndarray:
    m = (FREQS >= fmin) & (FREQS <= fmax)
    midi = 69 + 12 * np.log2(FREQS[m] / 440)
    pcs = np.round(midi).astype(int) % 12
    C = np.zeros((S.shape[0], 12), np.float32)
    L = np.log1p(10 * S[:, m])
    for p in range(12):
        C[:, p] = L[:, pcs == p].sum(axis=1)
    return C / (C.sum(axis=1, keepdims=True) + 1e-9)


def key_of(c: np.ndarray) -> tuple[str, int, str, float]:
    v = c.mean(axis=0)
    best = None
    for i in range(12):
        for prof, mode in ((KS_MAJ, "major"), (KS_MIN, "minor")):
            r = float(np.corrcoef(v, np.roll(prof, i))[0, 1])
            if best is None or r > best[3]:
                best = (PC[i], i, mode, r)
    return best


def chord_of(v: np.ndarray, key_pc: int, mode: str) -> tuple[str, float]:
    scale = [0, 2, 4, 5, 7, 9, 11] if mode == "major" else [0, 2, 3, 5, 7, 8, 10]
    best = ("N", 0.0)
    vn = (v - v.mean()) / (v.std() + 1e-9)
    for r in range(12):
        for q, ivs in TEMPLATES.items():
            t = np.zeros(12)
            t[[(r + i) % 12 for i in ivs]] = 1
            t[r] += 0.5                     # the root counts a bit more
            t = (t - t.mean()) / t.std()
            s = float(vn @ t) / 12
            s += 0.05 if (r - key_pc) % 12 in scale else 0.0     # diatonic chords are likelier
            s -= {"": 0, "m": 0, "7": 0.04, "m7": 0.04}.get(q, 0.09)  # plain triads unless the colour is clear
            if s > best[1]:
                best = (PC[r] + q, s)
    return best


def salience(S: np.ndarray, lo=55, hi=91) -> tuple[np.ndarray, np.ndarray]:
    """Harmonic-sum pitch salience per frame for MIDI keys lo..hi (G3..G6: where film melodies sit). Returns (keys, frames x keys)."""
    keys = np.arange(lo, hi + 1)
    out = np.zeros((S.shape[0], len(keys)), np.float32)
    L = np.log1p(50 * S)
    f0e = np.zeros_like(out)
    for j, k in enumerate(keys):
        f0 = 440 * 2 ** ((k - 69) / 12)
        for h, wgt in ((1, 1.0), (2, 0.6), (3, 0.4), (4, 0.25), (5, 0.15)):
            b = int(round(f0 * h / (SR / N_FFT)))
            if b < S.shape[1] - 1:
                e = L[:, max(0, b - 1):b + 2].max(axis=1)
                out[:, j] += wgt * e
                if h == 1:
                    f0e[:, j] = e
    # octave errors: the harmonic sum alone favours the octave below (its harmonics include the melody's), so
    # weight by the energy at the fundamental itself
    return keys, out * np.sqrt(f0e / (f0e.max(axis=1, keepdims=True) + 1e-9))


def name(k: int) -> str:
    return f"{PC[k % 12]}{k // 12 - 1}"


def analyze(path: Path, start: float, end: float | None, bpm: float | None, bpb: int, steps_per_beat: int = 2):
    y = decode(path, start, end)
    S = stft(y)
    env = onset_env(S)
    cands = tempo_candidates(env)
    tempo = bpm or cands[0][0]
    beats = track_beats(env, tempo)
    if len(beats) > 4:
        tempo = float(60 * FPS / np.median(np.diff(beats)))
    C = chroma(S)
    kname, kpc, mode, kr = key_of(C)
    # bars: choose the downbeat phase whose beats carry the most onset energy
    strength = env[beats]
    phase = int(np.argmax([strength[p::bpb].mean() for p in range(bpb)]))
    bar_starts = beats[phase::bpb]
    bars = []
    keys, sal = salience(S)
    prev = None
    rms = np.sqrt((S ** 2).mean(axis=1))
    for i in range(len(bar_starts) - 1):
        a, b = bar_starts[i], bar_starts[i + 1]
        ch, conf = chord_of(C[a:b].mean(axis=0), kpc, mode)
        # melody: one pitch per step (beat / steps_per_beat), the most salient key, rests where it is weak
        steps = np.linspace(a, b, bpb * steps_per_beat + 1)
        mel = []
        for s0, s1 in zip(steps, steps[1:]):
            seg = sal[int(s0):max(int(s0) + 1, int(s1))].mean(axis=0)
            j = int(np.argmax(seg))
            if prev is not None:          # stay near the last note: melodies move by step, octave flips are errors
                adj = seg - 0.12 * seg[j] * (np.abs(keys - prev) >= 10)
                j = int(np.argmax(adj))
            strong = seg[j] > np.percentile(sal, 75) and seg[j] > 1.15 * np.median(seg)
            mel.append(keys[j] if strong else None)
            prev = keys[j] if strong else prev
        toks, k, n = [], 0, len(mel)
        while k < n:
            j = k
            while j + 1 < n and mel[j + 1] == mel[k]:
                j += 1
            d = j - k + 1
            toks.append(f"{'r' if mel[k] is None else name(mel[k])}:{d}")
            k = j + 1
        bars.append({"bar": i + 1, "time": round(float(start + a / FPS), 2), "chord": ch, "chord_conf": round(conf, 2),
                     "level_db": round(float(20 * np.log10(rms[a:b].mean() + 1e-9)), 1),
                     "melody": " ".join(toks)})
    # sections: novelty on the bar-level chroma + loudness self-similarity
    F = np.array([np.concatenate([C[a:b].mean(axis=0), [rms[a:b].mean()]]) for a, b in
                  zip(bar_starts[:-1], bar_starts[1:])]) if len(bar_starts) > 2 else np.zeros((0, 13))
    sections = []
    if len(F) >= 8:
        Fn = (F - F.mean(0)) / (F.std(0) + 1e-9)
        Sm = Fn @ Fn.T / Fn.shape[1]
        w = 4
        nov = np.zeros(len(F))
        for i in range(w, len(F) - w):
            A = Sm[i - w:i, i - w:i].mean() + Sm[i:i + w, i:i + w].mean()
            B = Sm[i - w:i, i:i + w].mean() * 2
            nov[i] = A - B
        cuts = [0] + [i for i in range(w, len(F) - w) if nov[i] == nov[max(0, i - 3):i + 4].max()
                      and nov[i] > np.percentile(nov, 70)] + [len(F)]
        for a, b in zip(cuts, cuts[1:]):
            if b - a >= 2:
                sections.append({"bars": f"{a + 1}-{b}", "time": f"{bars[a]['time']}-{bars[b - 1]['time']}",
                                 "level_db": round(float(np.mean([x["level_db"] for x in bars[a:b]])), 1),
                                 "chords": " | ".join(x["chord"] for x in bars[a:b])})
        # loop candidates: spans of 8+ bars whose next bar looks like the first bar (chroma + level)
        loops = []
        for i in range(len(F)):
            for j in range(i + 8, min(len(F), i + 49)):
                if j + 1 < len(F):
                    sim = float(Sm[i, j] + Sm[i + 1, j + 1]) / 2
                    loops.append((sim, i + 1, j))
        loops.sort(reverse=True)
        loop_c = [{"bars": f"{i}-{j}", "similarity": round(s, 2)} for s, i, j in loops[:5]]
    else:
        loop_c = []
    return {
        "file": str(path), "start_s": start, "end_s": end or round(start + len(y) / SR, 1),
        "tempo_candidates": [round(float(b), 1) for b, _ in cands], "tempo": round(float(tempo), 1),
        "tempo_even": int(2 * round(float(tempo) / 2)), "beats_per_bar": bpb, "steps_per_beat": steps_per_beat,
        "key": f"{kname} {mode}", "key_confidence": round(float(kr), 2),
        "bars": bars, "sections": sections, "loop_candidates": loop_c,
    }


def song_ref(const: str) -> Path:
    for r in csv.DictReader((WIKI / "database" / "music.csv").open()):
        if r["asset_id"] in (const, f"audio:{const}"):
            files = [f for f in r.get("ref_files", "").split("|") if f]
            if not files:
                raise SystemExit(f"{const}: no ref_files (ref_use {r.get('ref_use') or '-'})")
            return WIKI / files[0]
    raise SystemExit(f"{const} is not in wiki/database/music.csv")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--song", help="MUS_ constant or net:mus-* id: analyze its main reference cue")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--bpm", type=float, help="force the tempo (when the detector picks half or double)")
    ap.add_argument("--beats-per-bar", type=int, default=4)
    ap.add_argument("--steps-per-beat", type=int, default=2)
    ap.add_argument("--name")
    a = ap.parse_args(argv)
    path = song_ref(a.song) if a.song else Path(a.file)
    res = analyze(path, a.start, a.end, a.bpm, a.beats_per_bar, a.steps_per_beat)
    nm = a.name or (a.song or path.stem).lower().replace(":", "-")
    out = HERE / "out" / "analysis" / f"{nm}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(res, sort_keys=False, width=140, allow_unicode=True))
    print(f"{path.name} {res['start_s']}-{res['end_s']} s: tempo {res['tempo']} (candidates "
          f"{res['tempo_candidates']}), key {res['key']} (r={res['key_confidence']}), {len(res['bars'])} bars")
    for s in res["sections"]:
        print(f"  bars {s['bars']:>7}  {s['time']:>14} s  {s['level_db']:6.1f} dB  {s['chords']}")
    if res["loop_candidates"]:
        print("  loop candidates:", ", ".join(f"{c['bars']} ({c['similarity']})" for c in res["loop_candidates"]))
    print(f"  -> {out.relative_to(HERE)}")


if __name__ == "__main__":
    main()

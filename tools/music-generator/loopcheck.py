"""Loop validation: is the loop seam as smooth as the song's own bar lines?

Adapted from the z-day ai-music tool (.claude/tools/audio/music/loopcheck.py in spencerlepine/z-day). There the
renderer made the loop periodic by construction and this file checked the copy; here the input is the m4a
preview of the real playback order (intro, loop, loop, loop), so the seams are measured exactly as the game
produces them: notes still releasing ring across the jump, the reverb carries over, every event sits on a frame.

The rule is the same: every check compares the seam with every other bar line inside the loop, so a song is
judged against itself. The high band is 4 kHz instead of 6 kHz because the PCM side stops at 6.7 kHz.

Checks (each one PASS/FAIL):
  click       FAIL if the seam is sharper (2nd difference within 2 ms) than 1.1 x every other bar
              line AND its >4 kHz energy is within 6 dB of the brightest bar line: a
              discontinuity does both, a clean musical attack (soft piano) only the first
  stem_click  the same click test on the drum-free pitched parts, so drum hits on bar lines
              cannot mask a discontinuity in a sustained instrument
  hf_click    >4 kHz energy within 3 ms of the seam         <= loudest other bar line + 3 dB
  rms_50ms    RMS change across the seam (50 ms windows)    inside the other bar lines' range (+-1.5 dB)
  rms_400ms   RMS change across the seam (400 ms windows)   inside the other bar lines' range (+-1.5 dB)
  bar_level   last bar vs first bar level                   <= largest bar-to-bar change elsewhere (+1 dB) and <= 4 dB
  phrase      last 2 bars vs first 2 bars level             <= 3 dB ("continues the way it started")
  tone        last bar vs first bar spectral balance        <= largest bar-to-bar change elsewhere (+3 points)
              (share-weighted: how much of the energy moves between bands, so a near-empty
              band swinging between 0.0% and 0.1% cannot dominate)
  repeat      seam 1 vs seam 2 spectra within -20 dB      (the loop plays the same every time). -12 dB when the
              loop is not a whole number of frames (most songs, vanilla too): every pass then lands up to one
              frame (16.7 ms) apart, note by note
The same checks run at the intro -> loop hand-off when the song has an intro.
"""
from __future__ import annotations

import numpy as np
from scipy import signal

BANDS = [(20, 120), (120, 500), (500, 2000), (2000, 6700)]
HF_HZ = 4000


def _db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-9)


def _measure_line(play, hp, c, sr):
    w2, w3 = int(0.002 * sr), int(0.003 * sr)
    out = {"click": float(np.abs(np.diff(play[c - w2:c + w2], 2)).max()),
           "hf": 20 * np.log10(np.sqrt(np.mean(hp[c - w3:c + w3] ** 2)) + 1e-12)}
    for ms in (50, 400):
        n = int(ms / 1000 * sr)
        out[f"rms_{ms}ms"] = _db(play[c:c + n]) - _db(play[c - n:c])
    return out


def _band_share(x, sr):
    """Fraction of the bar's energy in each band (sums to ~1)."""
    f, P = signal.welch(x, sr, nperseg=min(4096, len(x)))
    tot = P.sum() + 1e-20
    return np.array([P[(f >= lo) & (f < hi)].sum() / tot for lo, hi in BANDS])


def _spec_diff(play, s1, s2, frame):
    """Energy of the difference between the magnitude spectrograms around two points, relative to the first,
    after aligning the second within one frame either way."""
    def spec(c):
        x = play[c - 8192:c + 8192]                 # ~90 ms windows: a frame of jitter barely moves them
        fr = np.lib.stride_tricks.sliding_window_view(x, 4096)[::1024] * np.hanning(4096)
        return np.abs(np.fft.rfft(fr, axis=1))
    A = spec(s1)
    best = min((float(np.sum((A - spec(s2 + k)) ** 2)), k) for k in range(-frame, frame + 1, 32))
    return 10 * np.log10(best[0] / (np.sum(A ** 2) + 1e-20) + 1e-12)


def _tone_dist(a, b):
    """Share of the energy that moves between bands (total variation, 0..1)."""
    return 0.5 * float(np.abs(a - b).sum())


def validate(audio: np.ndarray, sr: int, intro: int, loop_len: float, loop_bars: int,
             stem: np.ndarray | None = None, frame_exact: bool = True) -> dict:
    """audio: (2, n) float of the real playback order: intro, then at least 3 loops.
    loop_len: samples per loop (may be fractional on the GBA, since events sit on frames).
    Returns {"passed": bool, "checks": [...], "lines": [str]}."""
    play = audio.mean(axis=0)
    hp = signal.sosfilt(signal.butter(4, HF_HZ, "high", fs=sr, output="sos"), play)
    bar = loop_len / loop_bars
    base = int(round(intro + loop_len))                     # seam: end of loop 1 -> start of loop 2
    inner = [_measure_line(play, hp, int(round(intro + loop_len + k * bar)), sr) for k in range(1, loop_bars)]
    seam = _measure_line(play, hp, base, sr)
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "passed": bool(ok), "detail": detail})

    def grade(label, s, ref):
        mx_click = max(r["click"] for r in ref)
        mx_hf = max(r["hf"] for r in ref)
        sharp, bright = s["click"] > 1.1 * mx_click + 1e-4, s["hf"] > mx_hf - 6.0
        add(f"{label}click", not (sharp and bright),
            f"max 2nd diff {s['click']:.4f} vs other bar lines max {mx_click:.4f}; "
            f"HF {s['hf']:.1f} vs {mx_hf:.1f} dB")
        add(f"{label}hf_click", s["hf"] <= mx_hf + 3.0, f"HF {s['hf']:.1f} dB vs other bar lines max {mx_hf:.1f} dB")
        for k in ("rms_50ms", "rms_400ms"):
            lo, hi = min(r[k] for r in ref), max(r[k] for r in ref)
            add(f"{label}{k}", lo - 1.5 <= s[k] <= hi + 1.5,
                f"change {s[k]:+.2f} dB vs other bar lines {lo:+.2f}..{hi:+.2f}")

    grade("", seam, inner)
    # bars of the second loop (steady state: the first loop's start has no reverb tail from a previous pass)
    starts = [int(round(intro + loop_len + k * bar)) for k in range(loop_bars + 1)]
    bars = [play[starts[k]:starts[k + 1]] for k in range(loop_bars)]
    lvl = np.array([_db(b) for b in bars])
    steps = np.abs(np.diff(lvl)) if loop_bars > 1 else np.array([0.0])
    d_bar = abs(lvl[-1] - lvl[0])
    add("bar_level", d_bar <= min(steps.max() + 1.0, 4.0),
        f"last bar {lvl[-1]:.1f} dB vs first {lvl[0]:.1f} dB (diff {d_bar:.2f}; largest elsewhere {steps.max():.2f})")
    if loop_bars >= 4:
        d_ph = abs(_db(np.concatenate(bars[-2:])) - _db(np.concatenate(bars[:2])))
        add("phrase", d_ph <= 3.0, f"last 2 bars vs first 2 bars differ by {d_ph:.2f} dB (limit 3)")
    tone = [_band_share(b, sr) for b in bars]
    tsteps = [_tone_dist(tone[k + 1], tone[k]) for k in range(loop_bars - 1)] or [0.0]
    d_tone = _tone_dist(tone[-1], tone[0])
    add("tone", d_tone <= max(tsteps) + 0.03,
        f"{100 * d_tone:.1f}% of energy shifts band vs largest bar-to-bar elsewhere {100 * max(tsteps):.1f}%")
    # repeat: the second seam sounds like the first. Not sample-exact on the GBA: a loop is rarely a whole number
    # of frames (tempo counter), so every pass lands up to a frame apart. Compare short-time spectra instead.
    s1, s2 = base, int(round(intro + 2 * loop_len))
    diff = _spec_diff(play, s1, s2, int(sr / 59.7275))
    lim = -20 if frame_exact else -12
    add("repeat", diff < lim, f"seam 1 vs seam 2 spectra differ at {diff:.1f} dB (limit {lim}"
        + ("" if frame_exact else ", loop is not a whole number of frames so each pass lands up to a frame apart")
        + ")")
    if intro:
        grade("intro_", _measure_line(play, hp, int(round(intro)), sr), inner)
    if stem is not None and np.any(stem):
        sp = stem.mean(axis=0)
        shp = signal.sosfilt(signal.butter(4, HF_HZ, "high", fs=sr, output="sos"), sp)
        ss = _measure_line(sp, shp, base, sr)
        sinner = [_measure_line(sp, shp, int(round(intro + loop_len + k * bar)), sr) for k in range(1, loop_bars)]
        mxc, mxh = max(r["click"] for r in sinner), max(r["hf"] for r in sinner)
        bad = ss["click"] > 1.1 * mxc + 1e-5 and ss["hf"] > mxh - 6.0
        add("stem_click", not bad, f"pitched parts only: 2nd diff {ss['click']:.4f} vs {mxc:.4f}, "
            f"HF {ss['hf']:.1f} vs {mxh:.1f} dB")
    passed = all(c["passed"] for c in checks)
    out = [f"   loop validation: {'PASS' if passed else 'FAIL'}"]
    for c in checks:
        out.append(f"     {'ok  ' if c['passed'] else 'FAIL'} {c['name']:<16} {c['detail']}")
    return {"passed": passed, "checks": checks, "lines": out}

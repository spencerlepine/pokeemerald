"""Hear a song the way Emerald plays it, without building the ROM: a software model of the m4a engine.

  * timing: m4a advances `tempo` units per VBlank frame and plays one clock per 150 units, so every event
    lands on a frame (59.73 Hz). Tempo is stored as bpm / 2.
  * Direct Sound: at most 5 voices (voice stealing when a 6th note starts: a releasing voice first, then the
    oldest one of equal or lower priority), each sample stepped at its key's rate with no interpolation into a
    13379 Hz 8-bit mix, frame-stepped ADSR on the 0..255 scale (attack adds, decay/release multiply by n/256),
    then the -R50 reverb (two taps 6 and 7 frames back, gain 50/256 each) and master volume 12/15.
  * Game Boy channels: square 1, square 2, wave and noise each play one note at a time (a new note takes the
    channel), 4-bit volume with frame-stepped envelopes (attack/decay/release 0-7, sustain 0-15), not resampled
    and not reverbed, mixed after the PCM bus.
  * Output: zero-order hold to 44.1 kHz like the DAC, stereo 16-bit.

It is a model, not an emulator: `romtest.py` records the real ROM when the toolchain is installed. The PCM vs
CGB balance (CGB_GAIN) is the one number tuned by ear against ROM recordings (see CONSTRAINTS.md).
"""
from __future__ import annotations

import math

import numpy as np

import gba
from song import Note, Song

OUT_RATE = 44100
CGB_GAIN = 0.27            # one Game Boy channel at volume 15 vs one PCM voice at full volume: fitted to a ROM
                           # recording of mus_route101 (romtest.py --vanilla, see CONSTRAINTS.md)
SPF = gba.SAMPLES_PER_FRAME


def frame_of_tick(song: Song, tick: int) -> int:
    """m4a: each frame adds tempo (bpm) to a counter; every 150 units plays one clock."""
    return int(tick * 150 // song.tempo)


def _pcm_env(adsr, on_frames: int) -> np.ndarray:
    """Per-frame envelope 0..255 for a note held `on_frames` frames, through its release."""
    a, d, s, r = adsr
    env, out, phase, f = 0, [], "attack", 0
    while True:
        if f == on_frames and phase != "release":
            phase = "release"
        if phase == "attack":
            env = min(255, env + (a if a else 255))
            if env >= 255:
                phase = "decay"
        elif phase == "decay":
            env = (env * d) >> 8
            if env <= s:
                env, phase = s, "sustain"
        elif phase == "release":
            env = (env * r) >> 8
        out.append(env)
        f += 1
        if phase == "release" and env == 0:
            break
        if phase == "sustain" and s == 0 and f < on_frames:
            phase = "sustain"
        if len(out) > on_frames + 600:   # 10 s of release at most
            break
    return np.array(out, np.float32)


def _cgb_env(adsr, on_frames: int) -> np.ndarray:
    """Per-frame 4-bit envelope for a Game Boy voice: attack/decay/release are frames per volume step (0 = jump)."""
    a, d, s, r = (int(x) for x in adsr)
    s = min(15, s)
    out, v, f = [], 0, 0
    phase = "attack"
    while True:
        if f == on_frames and phase != "release":
            phase, cnt = "release", 0
        if phase == "attack":
            v = 15 if a == 0 else min(15, v + (1 if f % a == 0 else 0))
            if v >= 15:
                phase, cnt = "decay", 0
        elif phase == "decay":
            if d == 0:
                v = s
            else:
                cnt += 1
                if cnt >= d:
                    v, cnt = max(s, v - 1), 0
            if v <= s:
                phase = "sustain"
        elif phase == "release":
            if r == 0:
                v = 0
            else:
                cnt += 1
                if cnt >= r:
                    v, cnt = max(0, v - 1), 0
        out.append(v)
        f += 1
        if phase == "release" and v == 0:
            break
        if len(out) > on_frames + 600:
            break
    return np.array(out, np.float32)


def _pan_lr(pan: int) -> tuple[float, float]:
    p = (max(-64, min(63, pan)) + 64) / 127
    return math.sqrt(1 - p) * 1.414, math.sqrt(p) * 1.414


def _square(n, hz, duty, rate):
    ph = (np.arange(n) * hz / rate) % 1.0
    return np.where(ph < duty, 1.0, -1.0).astype(np.float32)


def _noise(n, key, short, rate):
    # m4a maps the key to the noise clock; higher keys = brighter. A register-exact LFSR at a clock from the key.
    clock = 524288 / 2 ** max(0, min(13, (80 - key) // 4)) / 2
    steps = int(n * clock / rate) + 2
    lfsr, bits, width = 0x7FFF, np.empty(steps, np.float32), (7 if short else 15)
    for i in range(steps):
        b = (lfsr ^ (lfsr >> 1)) & 1
        lfsr = (lfsr >> 1) | (b << (width - 1))
        bits[i] = 1.0 if lfsr & 1 else -1.0
    return bits[(np.arange(n) * clock / rate).astype(int)]


def schedule(song: Song, loops: int) -> list[tuple[Note, int, int]]:
    """Playback order the game produces: intro once, then the loop `loops` times. (note, start frame, on frames)."""
    out = []
    L = song.loop_clocks
    for k in range(max(1, loops) if L else 1):
        for n in song.notes:
            if k and n.tick < song.intro_clocks:
                continue
            t = n.tick + k * L
            end = min(n.tick + n.dur, song.total_clocks) + k * L      # nothing rings past the loop end
            f0 = frame_of_tick(song, t)
            out.append((n, f0, max(1, frame_of_tick(song, end) - f0)))
    out.sort(key=lambda x: (x[1], x[0].part))
    return out


def render(song: Song, loops: int = 2, master_volume: int = 100, only: set[str] | None = None):
    """Stereo float32 at OUT_RATE, plus stats. master_volume is the midi.cfg -V value (0-127). `only`: render just
    these parts (the loop check's drum-free stem); voice stealing still counts every part, as in the game."""
    total_clocks = song.intro_clocks + song.loop_clocks * max(1, loops) if song.loop_clocks else song.total_clocks
    n_frames = frame_of_tick(song, total_clocks) + 1
    n_pcm = n_frames * SPF
    n_out = int(n_pcm * OUT_RATE / gba.MIXER_RATE) + 1
    pcm = np.zeros((n_pcm + 600 * SPF, 2), np.float32)
    cgb = np.zeros((n_out + int(600 * OUT_RATE / gba.FRAME_HZ), 2), np.float32)
    mvl = master_volume / 127
    slots: list[dict | None] = [None] * gba.MAX_PCM_VOICES
    cgb_busy: dict[str, dict] = {}
    stats = {"pcm_steals": 0, "cgb_steals": 0, "max_pcm": 0, "unresolved": set()}
    pcm_notes = []

    for n, f0, on in schedule(song, loops):
        part = song.parts[n.part]
        prog = part.program if n.program is None else n.program
        voice, key = gba.resolve(song.voicegroup, prog, n.key)
        if voice is None or voice.kind == "?" or voice.filler:
            stats["unresolved"].add((n.part, prog, n.key))
            continue
        vol = ((part.volume if n.volume is None else n.volume) / 127) * (n.vel / 127) * mvl
        lr = _pan_lr((part.pan if n.pan is None else n.pan) + (voice.pan - 64 if voice.pan else 0))
        muted = only is not None and n.part not in only
        if voice.kind == "pcm":
            env = _pcm_env(voice.adsr, on)
            smp = gba.sample(voice.sample)
            if smp.loop_start is None:      # a one-shot frees its voice when the sample runs out
                rate = smp.rate if voice.fixed_rate else smp.rate * 2 ** ((key - 60) / 12)
                env = env[:max(1, int(np.ceil(len(smp.data) / rate * gba.FRAME_HZ)))]
                on = min(on, len(env))
            # allocate one of the 5 PCM voices
            free = [i for i, s in enumerate(slots) if s is None or s["end"] <= f0]
            if free:
                i = free[0]
            else:
                rel = [i for i, s in enumerate(slots) if s["off"] <= f0]
                i = min(rel or range(len(slots)), key=lambda j: slots[j]["start"])
                victim = slots[i]
                victim["cut"] = f0
                stats["pcm_steals"] += victim["off"] > f0     # a releasing voice going quiet is not a steal
            slots[i] = {"start": f0, "off": f0 + on, "end": f0 + len(env), "cut": None}
            busy = sum(1 for s in slots if s and s["end"] > f0)
            stats["max_pcm"] = max(stats["max_pcm"], busy)
            pcm_notes.append((voice, key, f0, env, 0.0 if muted else vol, lr, slots[i]))
        else:
            kind = voice.kind
            prev = cgb_busy.get(kind)
            if prev and prev["end"] > f0:
                prev["cut"] = f0
                stats["cgb_steals"] += 1 if prev["off"] > f0 else 0
            env = _cgb_env(voice.adsr, on)
            st = {"start": f0, "off": f0 + on, "end": f0 + len(env), "cut": None}
            cgb_busy[kind] = st
            pcm_notes.append((voice, key, f0, env, 0.0 if muted else vol, lr, st))

    for voice, key, f0, env, vol, lr, st in pcm_notes:
        if vol == 0.0:
            continue
        frames = len(env) if st["cut"] is None else max(0, min(len(env), st["cut"] - f0))
        if frames <= 0:
            continue
        env = env[:frames]
        if voice.kind == "pcm":
            smp = gba.sample(voice.sample)
            rate = smp.rate if voice.fixed_rate else smp.rate * 2 ** ((key - 60) / 12)
            ns = frames * SPF
            pos = np.arange(ns) * (rate / gba.MIXER_RATE)
            if smp.loop_start is not None:
                L = smp.loop_end - smp.loop_start
                over = pos >= smp.loop_end
                pos[over] = smp.loop_start + (pos[over] - smp.loop_start) % max(1, L)
                idx = pos.astype(int)
                valid = np.ones(ns, bool)
            else:
                idx = pos.astype(int)
                valid = idx < len(smp.data)
                idx = np.minimum(idx, len(smp.data) - 1)
            x = np.where(valid, smp.data[idx], 0) * np.repeat(env / 255, SPF) * vol
            a = f0 * SPF
            pcm[a:a + ns, 0] += x * lr[0]
            pcm[a:a + ns, 1] += x * lr[1]
        else:
            a = int(f0 * SPF * OUT_RATE / gba.MIXER_RATE)
            ns = int(frames * OUT_RATE / gba.FRAME_HZ)
            hz = 440 * 2 ** ((key - 69) / 12)
            if voice.kind in ("square1", "square2"):
                duty = gba.SQUARE_DUTIES[int(voice.args[3] if voice.kind == "square1" else voice.args[2]) & 3]
                w = _square(ns, hz, duty, OUT_RATE)
            elif voice.kind == "wave":
                tab = gba.wave_pcm(voice.args[2])
                w = tab[((np.arange(ns) * hz * 32 / OUT_RATE) % 32).astype(int)]
            else:
                w = _noise(ns, key, int(voice.args[2]) & 1, OUT_RATE)
            # 4-bit CGB volume: m4a scales the envelope by the track volume, then rounds to 0..15
            v4 = np.round(env[np.minimum((np.arange(ns) * gba.FRAME_HZ / OUT_RATE).astype(int), len(env) - 1)] * vol) / 15
            x = w * v4 * CGB_GAIN
            cgb[a:a + ns, 0] += x * lr[0]
            cgb[a:a + ns, 1] += x * lr[1]

    # m4a reverb on the PCM bus: each sample gets (L+R from 6 and 7 frames back) * reverb / 512 ... per side
    t1, t2 = gba.REVERB_TAPS
    g = gba.REVERB / 256
    y = pcm.copy()
    for i in range(t2, len(y), t1):
        j = min(len(y), i + t1)
        y[i:j] += (y[i - t1:j - t1] + y[i - t2:j - t2]) * (g / 2)
    y *= gba.MASTER_VOLUME
    stats["pcm_clip"] = float(np.mean(np.abs(y) > 1.0))
    y = np.clip(np.round(y * 127), -128, 127) / 128          # 8-bit DAC
    idx = (np.arange(len(cgb)) * gba.MIXER_RATE / OUT_RATE).astype(int)
    out = y[np.minimum(idx, len(y) - 1)] + cgb
    out = out[:n_out]
    stats["unresolved"] = sorted(stats["unresolved"])
    # the loop's true period is fractional in frames (the tempo counter carries over the jump)
    stats["samples_per_loop"] = song.loop_clocks * 150 / song.tempo * SPF * OUT_RATE / gba.MIXER_RATE
    stats["intro_samples"] = int(frame_of_tick(song, song.intro_clocks) * SPF * OUT_RATE / gba.MIXER_RATE)
    return out.astype(np.float32), stats


def write_wav(path, x: np.ndarray, rate: int = OUT_RATE) -> None:
    import wave
    peak = max(1e-9, float(np.abs(x).max()))
    y = x * (0.89 / peak) if peak > 0.89 else x
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())

"""GBA / m4a hardware model for Emerald cries. Every number here is sourced in CONSTRAINTS.md.

This file belongs to cry-generator only. sfx-generator keeps its own copy of the rules it needs:
the two tools share nothing on purpose.
"""
import wave

import numpy as np

# ---- Cry sample format (sound/direct_sound_samples/cries/*.wav, all 388 files) ----
CRY_RATE = 10512            # Hz, every vanilla cry
CRY_BITS = 8                # unsigned 8-bit PCM in the .wav, signed 8-bit in ROM
NYQUIST = CRY_RATE / 2      # 5256 Hz: nothing above this exists in a cry

# ---- Playback (src/sound.c PlayCryInternal, src/m4a_tables.c gPokemonCrySongTemplate) ----
FRAME_HZ = 16777216 / 280896          # 59.7275 frames per second (VBlank)
NORMAL_HOLD_FRAMES = 140              # CRY_MODE_NORMAL: TIE then xWAIT 140 frames, release 0 = hard cut
DOUBLES_HOLD_FRAMES = 20              # CRY_MODE_DOUBLES / WEAK_DOUBLES: 20 frames, then release 225
MAX_SECONDS = NORMAL_HOLD_FRAMES / FRAME_HZ    # 2.344 s: anything later is never heard
DOUBLES_SECONDS = DOUBLES_HOLD_FRAMES / FRAME_HZ  # 0.335 s: the identity must land inside this
MIXER_RATE = 13379                    # SOUND_MODE_FREQ_13379 (src/m4a.c m4aSoundInit)
BASE_PITCH = 15360                    # CRY_MODE_NORMAL pitch value = key 60, no detune = native rate

# Pitch value per mode (PlayCryInternal). Semitones = (value - 15360) / 256.
MODES = {
    # name: (pitch, hold_frames or None for full, release, reverse, chorus)
    'normal':     (15360, 140, 0,   False, 0),
    'doubles':    (15360, 20,  225, False, 0),
    'encounter':  (15600, 140, 225, False, 20),
    'howl':       (15800, 50,  200, False, 20),
    'echo_start': (15600, 25,  100, True,  192),
    'faint':      (14440, 140, 200, False, 0),
    'echo_end':   (15555, 140, 220, False, 192),
    'roar_1':     (14848, 10,  100, False, 0),
    'roar_2':     (15616, 60,  225, False, 0),
    'growl_1':    (15200, 15,  125, True,  0),
    'growl_2':    (15200, 100, 225, False, 0),
    'weak':       (15000, 140, 0,   False, 0),
}

# ---- DPCM (game/tools/wav2agb/converter.cpp; audio_rules.mk runs `wav2agb -b -c -l 1 --no-pad`) ----
DPCM_BLOCK = 64
DPCM_TABLE = [0, 1, 4, 9, 16, 25, 36, 49, -64, -49, -36, -25, -16, -9, -4, -1]
DPCM_LOOKAHEAD = 1

# ---- Loudness of the vanilla set (measured by `cry.py survey`, reference/vanilla_stats.json) ----
TARGET_PEAK = 0.94      # median vanilla peak (0.79-0.98 for 5-95 %)
TARGET_RMS = 0.25       # median vanilla RMS, about -12 dBFS (0.18-0.30)


def to_s8(x):
    """float -1..1 -> the int levels wav2agb sees: floor(x*128) clamped to -128..127."""
    return np.clip(np.floor(np.asarray(x, dtype=np.float64) * 128.0), -128, 127).astype(np.int16)


def dpcm_roundtrip(levels, lookahead=DPCM_LOOKAHEAD):
    """Encode then decode exactly like wav2agb -c -l 1 --no-pad. Returns decoded int levels (same length)."""
    lv = [int(v) for v in levels]
    out = []
    n = len(lv)
    for b in range(0, n, DPCM_BLOCK):
        blk = lv[b:b + DPCM_BLOCK]
        blk = blk + [0] * (DPCM_BLOCK - len(blk))
        s = blk[0]
        out.append(s)
        for i in range(1, min(DPCM_BLOCK, n - b)):
            if lookahead == 1:
                t = blk[i]
                best, bi = None, 0
                for k, d in enumerate(DPCM_TABLE):
                    nl = s + d
                    e = (t - nl) * (t - nl)
                    if (best is None or e < best) and -128 <= nl <= 127:
                        best, bi = e, k
                s += DPCM_TABLE[bi]
            else:
                s = _lookahead_step(blk, i, s, min(lookahead, DPCM_BLOCK - i))
            out.append(s)
    return np.array(out[:n], dtype=np.int16)


def _lookahead_step(blk, i, prev, la):
    def rec(j, p, depth):
        if depth == 0:
            return 0, None
        best, bi = 1 << 60, None
        t = blk[j]
        for k, d in enumerate(DPCM_TABLE):
            nl = p + d
            e = (t - nl) ** 2
            if e >= best:
                continue
            r, _ = rec(j + 1, nl, depth - 1) if j + 1 < len(blk) else (0, None)
            if e + r < best and -128 <= nl <= 127:
                best, bi = e + r, k
        return best, bi
    _, k = rec(i, prev, la)
    return prev + DPCM_TABLE[k]


def snr_db(clean, coded):
    clean = np.asarray(clean, float)
    err = clean - np.asarray(coded, float)
    return 10 * np.log10((clean ** 2).sum() / max((err ** 2).sum(), 1e-9))


def read_wav(path):
    with wave.open(str(path)) as w:
        rate, width, ch = w.getframerate(), w.getsampwidth(), w.getnchannels()
        raw = w.readframes(w.getnframes())
    if width == 1:
        x = (np.frombuffer(raw, np.uint8).astype(np.float64) - 128) / 128
    elif width == 2:
        x = np.frombuffer(raw, '<i2').astype(np.float64) / 32768
    else:
        raise ValueError(f'{path}: {width * 8}-bit wav not supported')
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, rate


def write_wav_u8(path, x, rate=CRY_RATE):
    """Game format: mono unsigned 8-bit. Input float -1..1."""
    lv = to_s8(x) + 128
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(lv.astype(np.uint8).tobytes())


def write_wav_16(path, x, rate):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def resample(x, src, dst):
    """Linear interpolation, the way the m4a mixer steps through a sample."""
    if src == dst:
        return np.asarray(x, float)
    n = int(round(len(x) * dst / src))
    pos = np.arange(n) * (src / dst)
    return np.interp(pos, np.arange(len(x)), x)


def play_in_game(levels, mode='normal'):
    """What the speaker gets: DPCM-decoded levels -> mode pitch/reverse/length -> 13379 Hz 8-bit mixer.

    Returns float audio at MIXER_RATE. Chorus is modelled as a second copy detuned by `chorus`/256 semitones.
    The m4a cry voice has ADSR 255/0/255/0; releases are the m4a multiply-per-frame (release/256)."""
    pitch, hold, release, reverse, chorus = MODES[mode]
    x = np.asarray(levels, float) / 128.0
    if reverse:
        x = x[::-1]
    semis = (pitch - BASE_PITCH) / 256.0
    rate = CRY_RATE * 2 ** (semis / 12)
    y = resample(x, rate, MIXER_RATE)
    if chorus:
        r2 = CRY_RATE * 2 ** ((semis + chorus / 256.0 * 0) / 12) * 2 ** (chorus / 256 / 12)
        y2 = resample(x, r2, MIXER_RATE)
        m = max(len(y), len(y2))
        y = (np.pad(y, (0, m - len(y))) + np.pad(y2, (0, m - len(y2)))) * 0.5
    hold_n = int(hold / FRAME_HZ * MIXER_RATE)
    env = np.ones(len(y))
    if len(y) > hold_n:
        if release == 0:
            env[hold_n:] = 0
        else:
            frames = np.arange(len(y) - hold_n) / MIXER_RATE * FRAME_HZ
            env[hold_n:] = (release / 256.0) ** np.floor(frames + 1)
    y = y * env
    # Mixer: master volume 12/15 then the 8-bit DAC.
    return np.round(np.clip(y * 12 / 15, -1, 127 / 128) * 128) / 128


def dpcm_optimal(levels):
    """Best-possible DPCM levels for this signal (Viterbi over every legal delta path in each 64-sample block).

    The ROM build re-encodes our .wav with wav2agb's greedy -l 1 search. A file whose every step is already a
    table delta re-encodes losslessly (the greedy search finds the zero-error delta), so baking the optimal path
    into the .wav gives the best quality the format allows, with the build's own encoder. `cry.py verify-build`
    checks that claim against the real wav2agb."""
    lv = np.asarray(levels, np.int64)
    n = len(lv)
    out = np.zeros(n, np.int64)
    L = np.arange(-128, 128)
    D = np.array(DPCM_TABLE)
    INF = np.int64(1) << 50
    for b in range(0, n, DPCM_BLOCK):
        t = lv[b:b + DPCM_BLOCK]
        m = len(t)
        cost = np.full(256, INF)
        cost[t[0] + 128] = 0
        back = np.zeros((m, 256), np.int64)
        for i in range(1, m):
            best = np.full(256, INF)
            arg = np.zeros(256, np.int64)
            for d in D:
                src = L - d                      # previous level that reaches each new level with delta d
                ok = (src >= -128) & (src <= 127)
                c = np.full(256, INF)
                c[ok] = cost[src[ok] + 128]
                better = c < best
                best[better] = c[better]
                arg[better] = (src[better] + 128)
            err = (t[i] - L) ** 2
            cost = best + err
            back[i] = arg
        s = int(np.argmin(cost))
        path = [s]
        for i in range(m - 1, 0, -1):
            s = int(back[i][s])
            path.append(s)
        out[b:b + m] = np.array(path[::-1]) - 128
    return out.astype(np.int16)

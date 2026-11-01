"""GBA / m4a hardware model for Emerald sound effects. Every number here is sourced in CONSTRAINTS.md.

This file belongs to sfx-generator only. cry-generator keeps its own copy of the rules it needs:
the two tools share nothing on purpose.

Two kinds of voices exist on the GBA:
  * Direct Sound (PCM): 8-bit samples mixed in software by m4a at 13379 Hz, at most 5 at once.
  * The four Game Boy (CGB/PSG) channels: square 1 (with pitch sweep), square 2, a 32-step 4-bit wave
    channel and an LFSR noise channel, each with a 4-bit volume.
Here the CGB channels are emulated register-exact (frequency quantised to the 11-bit register, 4-bit volume,
64 Hz envelope steps, 128 Hz sweep steps, the real LFSR), so a layer drawn with them sounds like the chip.
"""
import struct
import wave

import numpy as np

# ---- m4a mixer (src/m4a.c m4aSoundInit; include/gba/m4a_internal.h) ----
MIXER_RATE = 13379                    # SOUND_MODE_FREQ_13379: every PCM voice is resampled to this
NYQUIST = MIXER_RATE / 2              # 6689 Hz: the top of the whole PCM side of the game
MAX_PCM_VOICES = 5                    # SOUND_MODE_MAXCHN = 5 of the 12 possible
MASTER_VOLUME = 12 / 15               # SOUND_MODE_MASVOL = 12
FRAME_HZ = 16777216 / 280896          # 59.7275 Hz VBlank; m4a updates envelopes, pitch and volume per frame
SAMPLES_PER_FRAME = 224               # 13379 / 59.73
REVERB = 50                           # every song in midi.cfg uses -R50 (one BGM uses 40)
REVERB_TAPS = (6 * 224, 7 * 224)      # m4a_1.s SoundMainRAM_Reverb: ring buffer of pcmDmaPeriod=7 frames

# ---- CGB / PSG channels (GBATEK sound registers; m4a CgbSound in src/m4a.c) ----
CPU_HZ = 16777216
SQUARE_DUTIES = {0: 0.125, 1: 0.25, 2: 0.5, 3: 0.75}
ENVELOPE_STEP_HZ = 64                 # one volume step per n/64 s
SWEEP_STEP_HZ = 128                   # one sweep step per t/128 s
WAVE_STEPS = 32                       # 32 x 4-bit samples
NOISE_DIVISORS = [0.5, 1, 2, 3, 4, 5, 6, 7]

# ---- what a vanilla SE looks like (sfx.py survey over sound/songs/midi/se_*.mid) ----
SE_MEDIAN_SECONDS = 0.55
SE_MAX_SECONDS = 8.0                  # se_roulette_ball; next longest is se_truck_move at 6.4 s
TARGET_PEAK = 0.90


# ------------------------------------------------------------------ CGB channels

def square_freq_reg(hz):
    """Nearest legal 11-bit frequency register value for a square/sweep channel: f = 131072 / (2048 - x)."""
    x = np.clip(np.round(2048 - 131072 / np.maximum(hz, 64.0)), 0, 2047)
    return x


def square_hz(reg):
    return 131072.0 / (2048 - reg)


def wave_hz(reg):
    return 65536.0 / (2048 - reg)


def wave_freq_reg(hz):
    return np.clip(np.round(2048 - 65536 / np.maximum(hz, 32.0)), 0, 2047)


def envelope_4bit(n, rate, start=15, step=0, direction=-1, gate=None):
    """Hardware volume envelope: integer 0..15, changes every step/64 s (step 0 = constant).
    gate: seconds after which a release starts (m4a release), as (gate_s, release_step)."""
    t = np.arange(n) / rate
    if step:
        v = start + direction * np.floor(t * ENVELOPE_STEP_HZ / step)
    else:
        v = np.full(n, float(start))
    if gate:
        g, rstep = gate
        k = t >= g
        v0 = np.interp(g, t, v) if n else 0
        v[k] = v0 - np.floor((t[k] - g) * ENVELOPE_STEP_HZ / max(rstep, 1))
    return np.clip(v, 0, 15)


def chip_square(hz_curve, rate, duty=2, sweep=None):
    """Square channel. hz_curve: per-sample target Hz (m4a updates pitch per frame, so it is held per frame).
    sweep: (time 1-7, negate bool, shift 1-7) like NR10; only legal on square 1."""
    n = len(hz_curve)
    frame = max(1, int(rate / FRAME_HZ))
    reg = square_freq_reg(np.repeat(hz_curve[::frame], frame)[:n])
    if sweep:
        st, neg, sh = sweep
        period = st / SWEEP_STEP_HZ
        t = np.arange(n) / rate
        steps = np.floor(t / period).astype(int)
        r = float(reg[0])
        regs = [r]
        for _ in range(steps.max() + 1):
            d = int(r) >> sh
            r = r - d if neg else r + d
            regs.append(min(r, 2047))
        reg = np.array(regs)[steps]
        reg = np.where(reg >= 2047, np.nan, reg)          # overflow silences the channel, as on hardware
    hz = square_hz(np.nan_to_num(reg, nan=0))
    ph = np.cumsum(hz / rate) % 1.0
    out = np.where(ph < SQUARE_DUTIES[duty], 1.0, -1.0)
    if sweep:
        out = np.where(np.isnan(reg), 0.0, out)
    return out


def chip_wave(hz_curve, rate, table):
    """Wave channel: 32 4-bit steps (0-15), played as a staircase."""
    tb = (np.asarray(table, float) - 7.5) / 7.5
    assert len(tb) == WAVE_STEPS
    n = len(hz_curve)
    frame = max(1, int(rate / FRAME_HZ))
    hz = wave_hz(wave_freq_reg(np.repeat(hz_curve[::frame], frame)[:n]))
    ph = np.cumsum(hz / rate) % 1.0
    return tb[(ph * WAVE_STEPS).astype(int) % WAVE_STEPS]


def noise_hz(shift, divisor):
    return 524288.0 / NOISE_DIVISORS[divisor] / (2 ** (shift + 1))


def chip_noise(n, rate, shift=None, divisor=None, short=False, hz=None):
    """LFSR noise (15-bit, or 7-bit `short` = metallic/tonal). Either (shift, divisor) like NR43, or a target
    clock `hz` (scalar or per-sample curve) that is snapped to the nearest legal NR43 setting per frame."""
    legal = sorted((noise_hz(s, d), s, d) for s in range(14) for d in range(8))
    lf = np.array([x[0] for x in legal])
    if hz is None:
        clk = np.full(n, noise_hz(shift, divisor))
    else:
        h = np.broadcast_to(np.asarray(hz, float), (n,)).copy()
        frame = max(1, int(rate / FRAME_HZ))
        h = np.repeat(h[::frame], frame)[:n]
        clk = lf[np.abs(np.log(lf)[None, :] - np.log(h)[:, None]).argmin(axis=1)]
    lfsr = 0x7FFF
    out = np.empty(n)
    acc = 0.0
    bit = 1.0
    for i in range(n):
        acc += clk[i] / rate
        while acc >= 1.0:
            acc -= 1.0
            x = (lfsr ^ (lfsr >> 1)) & 1
            lfsr = (lfsr >> 1) | (x << 14)
            if short:
                lfsr = (lfsr & ~(1 << 6)) | (x << 6)
            bit = 1.0 if (lfsr & 1) == 0 else -1.0
        out[i] = bit
    return out


# ------------------------------------------------------------------ PCM side

def to_s8(x):
    return np.clip(np.round(np.asarray(x, float) * 127), -128, 127).astype(np.int16)


def m4a_reverb(x, amount=REVERB):
    """m4a's mixer reverb: each new frame of the PCM buffer starts as (L+R of the buffer 6 and 7 frames ago)
    * amount / 512. For a centred mono voice that is y[n] = x[n] + (y[n-1344] + y[n-1568]) * amount / 256."""
    y = np.concatenate([np.asarray(x, float), np.zeros(int(0.9 * MIXER_RATE))])
    g = amount / 256.0
    d1, d2 = REVERB_TAPS
    for i in range(d1, len(y)):
        y[i] += g * (y[i - d1] + (y[i - d2] if i >= d2 else 0.0))
    a = np.abs(y)
    last = np.where(a > 1 / 128)[0]
    return y[:last[-1] + 1] if len(last) else y


def play_in_game(sample, reverb=True):
    """What the speaker gets for a one-shot PCM SE at velocity 127, volume 100%: 8-bit sample -> master
    volume -> m4a reverb -> 8-bit DAC. Returned at MIXER_RATE."""
    x = to_s8(sample).astype(float) / 128.0
    y = x * MASTER_VOLUME
    if reverb:
        y = m4a_reverb(y)
    return np.round(np.clip(y, -1, 127 / 128) * 128) / 128


def zoh_44k(x):
    """The GBA holds each mixer sample until the next one (no smoothing filter), so the 13379 Hz staircase
    carries images above 6.7 kHz: that sparkle is part of the sound. Matches mGBA captures within ~1-2 dB/band."""
    up = np.repeat(np.asarray(x, float), 4)            # 53516 Hz
    n = int(len(up) * 44100 / (MIXER_RATE * 4))
    return np.interp(np.arange(n) * (MIXER_RATE * 4 / 44100), np.arange(len(up)), up)


def read_wav(path):
    with wave.open(str(path)) as w:
        rate, width, ch = w.getframerate(), w.getsampwidth(), w.getnchannels()
        raw = w.readframes(w.getnframes())
    if width == 1:
        x = (np.frombuffer(raw, np.uint8).astype(float) - 128) / 128
    else:
        x = np.frombuffer(raw, '<i2').astype(float) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, rate


def write_wav_u8(path, x, rate=MIXER_RATE, loop=None):
    """Game format (wav2agb input): mono unsigned 8-bit. loop=(start, end) samples adds a smpl chunk, which
    wav2agb turns into the sample's loop point."""
    data = (to_s8(x) + 128).astype(np.uint8).tobytes()
    fmt = struct.pack('<HHIIHH', 1, 1, rate, rate, 1, 8)
    chunks = b'fmt ' + struct.pack('<I', len(fmt)) + fmt
    chunks += b'data' + struct.pack('<I', len(data)) + data + (b'\0' if len(data) % 2 else b'')
    if loop:
        smpl = struct.pack('<9I', 0, 0, int(1e9 / rate), 60, 0, 0, 0, 1, 0)
        smpl += struct.pack('<6I', 0, 0, int(loop[0]), int(loop[1]) - 1, 0, 0)
        chunks += b'smpl' + struct.pack('<I', len(smpl)) + smpl
    with open(path, 'wb') as f:
        f.write(b'RIFF' + struct.pack('<I', 4 + len(chunks)) + b'WAVE' + chunks)


def write_wav_16(path, x, rate):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())

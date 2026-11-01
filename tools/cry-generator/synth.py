"""Cry synthesis: creature voices and droid voices, rendered from a spec (specs/*.yaml).

Everything is synthesised at SYNTH_RATE (4x the cry rate) and then band-limited and decimated to the
10512 Hz game rate in master(), so the GBA limits (gba.py, CONSTRAINTS.md) are applied last and always.
"""
import numpy as np
from scipy import signal

import gba

SYNTH_RATE = gba.CRY_RATE * 4   # 42048 Hz
BLOCK = 32                      # samples per filter-coefficient update

# Formants (F1, F2, F3 in Hz, bandwidths) for a medium creature (size 0.5). size scales them.
VOWELS = {
    'a': (750, 1250, 2600), 'e': (500, 1800, 2600), 'i': (320, 2300, 3100),
    'o': (480, 850, 2500), 'u': (350, 700, 2400), 'ae': (650, 1700, 2500),
    'er': (470, 1300, 1700), 'rr': (380, 900, 2300),      # rr: throaty growl
    'ee': (900, 2600, 3600),                              # ee: thin screech
    'aw': (650, 1000, 2700), 'm': (280, 1000, 2200),      # m: closed-mouth hum
}
BANDWIDTH = (90, 120, 180)


def size_scale(size):
    """0 = tiny (formants x1.8), 0.5 = medium (x1), 1 = huge (x0.55)."""
    return 2 ** ((0.5 - size) * 1.7)


def curve(points, n, rate, interp='lin'):
    """[[t, v], ...] keyframes -> per-sample array of length n. Exponential interp for pitch."""
    pts = sorted(([float(p[0]), p[1]] for p in points), key=lambda p: p[0])
    t = np.arange(n) / rate
    ts = np.array([p[0] for p in pts])
    vs = np.array([float(p[1]) for p in pts])
    if interp == 'exp':
        return np.exp(np.interp(t, ts, np.log(np.maximum(vs, 1e-6))))
    return np.interp(t, ts, vs)


def phase_from_hz(hz, rate):
    return np.cumsum(hz / rate)


def polyblep_saw(ph, dt):
    x = ph % 1.0
    y = 2 * x - 1
    # PolyBLEP anti-aliasing at the wrap
    m1 = x < dt
    t = x[m1] / dt[m1]
    y[m1] -= t + t - t * t - 1
    m2 = x > 1 - dt
    t = (x[m2] - 1) / dt[m2]
    y[m2] -= t * t + t + t + 1
    return y


def pulse(ph, dt, width):
    return polyblep_saw(ph, dt) - polyblep_saw(ph + width, dt) + (2 * width - 1) * 0


def osc(kind, hz, rate, width=0.5):
    ph = phase_from_hz(hz, rate)
    dt = np.clip(hz / rate, 1e-6, 0.5)
    if kind == 'sine':
        return np.sin(2 * np.pi * ph)
    if kind == 'tri':
        return 2 * np.abs(2 * (ph % 1.0) - 1) - 1
    if kind == 'saw':
        return polyblep_saw(ph, dt)
    if kind in ('square', 'pulse'):
        return pulse(ph, dt, width if kind == 'pulse' else 0.5)
    raise ValueError(kind)


def resonator_bank(x, formants, bws, gains, rate):
    """Parallel 2-pole resonators with per-block time-varying centre frequency.
    formants: (n, k) Hz, bws: (k,), gains: (k,)."""
    n, k = formants.shape
    out = np.zeros(n)
    for j in range(k):
        zi = np.zeros(2)
        r = np.exp(-np.pi * bws[j] / rate)
        y = np.zeros(n)
        for b in range(0, n, BLOCK):
            f = min(formants[b, j], rate * 0.45)
            a1 = -2 * r * np.cos(2 * np.pi * f / rate)
            a2 = r * r
            g = (1 - r) * np.sqrt(1 - 2 * r * np.cos(4 * np.pi * f / rate) + r * r)  # unity peak gain
            seg, zi = signal.lfilter([g], [1, a1, a2], x[b:b + BLOCK], zi=zi)
            y[b:b + BLOCK] = seg
        out += gains[j] * y
    return out


def vowel_track(spec_vowels, n, rate, scale):
    """[[t, 'a'], [t, [f1,f2,f3]], ...] -> (n, 3) formant Hz, smoothly interpolated."""
    pts = []
    for t, v in spec_vowels:
        f = VOWELS[v] if isinstance(v, str) else v
        pts.append((float(t), [x * scale for x in f]))
    pts.sort(key=lambda p: p[0])
    tt = np.arange(n) / rate
    ts = [p[0] for p in pts]
    return np.stack([np.exp(np.interp(tt, ts, [np.log(p[1][j]) for p in pts])) for j in range(3)], axis=1)


def envelope(points, n, rate):
    return np.clip(curve(points, n, rate), 0, None)


def duration_of(layer):
    keys = [k for k in ('env', 'pitch') if k in layer]
    return max(max(float(p[0]) for p in layer[k]) for k in keys) + float(layer.get('at', 0))


# ---------------------------------------------------------------- layers

def stepped(hz, L, rate):
    """pitch_step: hold the pitch for that many seconds, like the frame-stepped pitch of the chip-era cries."""
    st = float(L.get('pitch_step', 0))
    if st:
        k = max(1, int(st * rate))
        hz = np.repeat(hz[::k], k)[:len(hz)]
    return hz


def layer_voice(L, n, rate, rng, size):
    """A throat: glottal source (saw/pulse/noise mix) through formants, with vibrato, jitter, growl."""
    hz = stepped(curve(L['pitch'], n, rate, 'exp') * float(L.get('pitch_scale', 1.0)), L, rate)
    vib = L.get('vibrato', {})
    if vib:
        t = np.arange(n) / rate
        hz = hz * 2 ** (float(vib.get('depth', 0.02)) * np.sin(2 * np.pi * float(vib.get('rate', 6)) * t))
    jit = float(L.get('jitter', 0.0))
    if jit:
        w = rng.standard_normal(n // 64 + 2)
        hz = hz * 2 ** (jit * np.interp(np.arange(n), np.arange(len(w)) * 64, w))
    src = L.get('source', {'saw': 1.0})
    width = float(src.get('pulse_width', 0.3))
    x = np.zeros(n)
    for kind in ('saw', 'pulse', 'square', 'sine', 'tri'):
        if src.get(kind):
            x += float(src[kind]) * osc(kind, hz, rate, width)
    growl = float(L.get('growl', 0.0))
    if growl:
        # Period doubling (subharmonic) plus fast amplitude roughness: the "rough voice" of big animals.
        sub = osc('saw', hz / 2, rate)
        t = np.arange(n) / rate
        rough = 1 + 0.8 * np.sin(2 * np.pi * float(L.get('growl_rate', 45)) * t + rng.uniform(0, 6))
        x = (1 - growl) * x + growl * (0.6 * x * rough + 0.6 * sub)
    if src.get('noise'):
        x += float(src['noise']) * rng.standard_normal(n) * 0.7
    emph = float(L.get('emphasis', 0.9))
    if emph:
        # Lip radiation (+6 dB/octave): pushes energy up into the 1-3 kHz band where vanilla cries live.
        x = signal.lfilter([1, -emph], [1], x)
    if 'vowels' in L:
        scale = size_scale(size) * float(L.get('formant_scale', 1.0))
        F = vowel_track(L['vowels'], n, rate, scale)
        bw = np.array(L.get('bandwidths', BANDWIDTH), float) * scale ** 0.5
        gains = np.array(L.get('formant_gains', [1.0, 0.7, 0.4]), float)
        x = resonator_bank(x, F, bw, gains, rate) * 3 + 0.08 * x
    return x


def layer_noise(L, n, rate, rng, size):
    """Breath, hiss, rasp: white noise through a moving band-pass."""
    x = rng.standard_normal(n)
    if 'band' in L:
        lo = curve(L['band'], n, rate, 'exp') if isinstance(L['band'][0], list) else np.full(n, float(L['band'][0]))
        q = float(L.get('q', 2.0))
        F = lo[:, None]
        x = resonator_bank(x, F, np.array([max(40.0, float(np.median(lo)) / q)]), np.array([1.0]), rate) * 4
    return x


def layer_tone(L, n, rate, rng, size):
    """Droid/electronic tone: square, pulse, tri or sine with gliding pitch and optional warble (fast FM)."""
    hz = stepped(curve(L['pitch'], n, rate, 'exp'), L, rate)
    w = L.get('warble')
    if w:
        t = np.arange(n) / rate
        hz = hz * 2 ** (float(w.get('depth', 0.1)) * np.sign(np.sin(2 * np.pi * float(w.get('rate', 20)) * t))
                         if w.get('shape') == 'square' else
                         float(w.get('depth', 0.1)) * np.sin(2 * np.pi * float(w.get('rate', 20)) * t))
    return osc(L.get('wave', 'square'), hz, rate, float(L.get('width', 0.25)))


def layer_servo(L, n, rate, rng, size):
    """Motor whine: a harmonic stack locked to an rpm curve plus gritty band noise."""
    hz = curve(L['pitch'], n, rate, 'exp')
    x = np.zeros(n)
    for h, a in enumerate(L.get('harmonics', [1.0, 0.5, 0.35, 0.2]), start=1):
        x += a * osc('sine', hz * h, rate)
    grit = float(L.get('grit', 0.3))
    if grit:
        g = rng.standard_normal(n)
        g = resonator_bank(g, (hz * 3)[:, None], np.array([300.0]), np.array([1.0]), rate) * 3
        x += grit * g
    return x


def layer_click(L, n, rate, rng, size):
    """Short percussive transients (relay clicks, beak snaps, claw taps) at given times."""
    x = np.zeros(n)
    for t in L['times']:
        i = int(float(t) * rate)
        m = int(0.004 * rate)
        if i < n:
            burst = rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 5))
            x[i:i + m] += burst[:max(0, min(m, n - i))]
    return x


LAYERS = {'voice': layer_voice, 'noise': layer_noise, 'tone': layer_tone, 'servo': layer_servo, 'click': layer_click}


def render(spec):
    """spec dict -> float array at SYNTH_RATE (pre-master)."""
    rng = np.random.default_rng(int(spec.get('seed', 1)))
    size = float(spec.get('size', 0.5))
    total = max(duration_of(L) if L['type'] != 'click' else max(map(float, L['times'])) + 0.02
                for L in spec['layers'])
    N = int((total + 0.02) * SYNTH_RATE)
    mix = np.zeros(N)
    for L in spec['layers']:
        at = int(float(L.get('at', 0)) * SYNTH_RATE)
        n = N - at
        x = LAYERS[L['type']](L, n, SYNTH_RATE, rng, size)
        if 'env' in L:
            x = x * envelope(L['env'], n, SYNTH_RATE)
        if L.get('drive'):
            d = float(L['drive'])
            x = np.tanh(x * d) / np.tanh(d)
        x = x / (np.sqrt(np.mean(x[np.abs(x) > 0] ** 2)) + 1e-9) * 0.3 if L.get('normalize', True) else x
        mix[at:] += float(L.get('gain', 1.0)) * x
    return mix


def master(x, spec):
    """Band-limit and decimate to 10512 Hz, then match the vanilla loudness (CONSTRAINTS.md section 4)."""
    m = spec.get('master', {})
    sos_hp = signal.butter(2, float(m.get('highpass', 90)), 'hp', fs=SYNTH_RATE, output='sos')
    x = signal.sosfilt(sos_hp, x)
    # Anti-alias: everything above ~4.2 kHz is cut before the 10512 Hz rate (Nyquist 5256 Hz).
    sos_lp = signal.butter(8, float(m.get('lowpass', 4200)), 'lp', fs=SYNTH_RATE, output='sos')
    x = signal.sosfiltfilt(sos_lp, x)
    tilt = float(m.get('tilt_db', 0.0))
    if tilt:
        # High-shelf cut above ~1.2 kHz: DPCM can only move 64 levels per sample, so loud highs smear.
        x = x + (10 ** (tilt / 20) - 1) * signal.sosfilt(signal.butter(2, 1200, 'hp', fs=SYNTH_RATE, output='sos'), x)
    x = x[::4]
    rate = gba.CRY_RATE
    # Trim leading/trailing silence, short fades so the sample starts and ends at 0 (no click).
    a = np.abs(x)
    thr = a.max() * 0.01
    idx = np.where(a > thr)[0]
    x = x[max(0, idx[0] - 8): idx[-1] + 32]
    fi, fo = int(0.002 * rate), int(0.012 * rate)
    x[:fi] *= np.linspace(0, 1, fi)
    x[-fo:] *= np.linspace(1, 0, fo) ** 2
    # Loudness: vanilla cries are hot (median RMS 0.25, peak 0.94). Peak-normalise, then a soft-clip
    # (tanh) whose drive is found by bisection so the RMS lands on the target: the same squashed, loud
    # character as the vanilla set, without hard clipping.
    target_rms = float(m.get('rms', gba.TARGET_RMS))
    x = x / max(np.abs(x).max(), 1e-9)

    def shaped(k):
        y = np.tanh(x * k) / np.tanh(k)
        return y * gba.TARGET_PEAK

    lo, hi = 0.05, 12.0
    if np.sqrt(np.mean(shaped(lo) ** 2)) >= target_rms:
        x = shaped(lo) * target_rms / np.sqrt(np.mean(shaped(lo) ** 2))
    else:
        for _ in range(40):
            k = (lo + hi) / 2
            if np.sqrt(np.mean(shaped(k) ** 2)) < target_rms:
                lo = k
            else:
                hi = k
        x = shaped(hi)
    x[0] = 0
    x[-1] = 0
    return x

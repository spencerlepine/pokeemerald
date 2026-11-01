"""SFX synthesis from a spec (specs/*.yaml).

Layers are either CGB chip voices (square, wave, noise: register-exact emulation in gba.py) or `pcm`
voices (free synthesis that ends up as an 8-bit sample, like the game's own direct-sound samples).
Everything renders at SYNTH_RATE and is band-limited and decimated to the 13379 Hz mixer rate in master().
"""
import numpy as np
from scipy import signal

import gba

SYNTH_RATE = gba.MIXER_RATE * 4        # 53516 Hz
WAVE_PRESETS = {
    'sine': [8, 10, 11, 13, 14, 15, 15, 15, 15, 15, 14, 13, 11, 10, 8, 7, 7, 5, 4, 2, 1, 0, 0, 0, 0, 0, 1, 2, 4, 5, 7, 7],
    'tri': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    'saw': list(range(16)) + list(range(16)),
    'organ': [8, 12, 14, 13, 10, 9, 11, 14, 15, 13, 9, 6, 6, 8, 9, 8, 7, 6, 7, 9, 9, 6, 2, 1, 2, 5, 6, 5, 3, 1, 2, 4],
    'buzz': [15, 15, 15, 15, 0, 0, 0, 0, 15, 15, 15, 15, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
}
WAVE_VOLUMES = [0.0, 0.25, 0.5, 1.0]   # NR32: mute, 25 %, 50 %, 100 %


def curve(points, n, rate, interp='lin'):
    if not isinstance(points, list):
        return np.full(n, float(points))
    pts = sorted(([float(p[0]), float(p[1])] for p in points), key=lambda p: p[0])
    t = np.arange(n) / rate
    ts = np.array([p[0] for p in pts])
    vs = np.array([p[1] for p in pts])
    if interp == 'exp':
        return np.exp(np.interp(t, ts, np.log(np.maximum(vs, 1e-6))))
    return np.interp(t, ts, vs)


def layer_end(L):
    ends = [float(p[0]) for k in ('env', 'pitch', 'clock', 'cutoff') if isinstance(L.get(k), list) for p in L[k]]
    return float(L.get('at', 0)) + (max(ends) if ends else float(L.get('length', 0.2)))


def frame_hold(x, rate):
    k = max(1, int(rate / gba.FRAME_HZ))
    return np.repeat(x[::k], k)[:len(x)]


def chip_env(L, n, rate):
    """CGB volume: 4-bit (0-15), changed at most once per frame by m4a (or by the 64 Hz hardware envelope)."""
    if 'hw_env' in L:
        e = L['hw_env']
        rel = (float(e['release_at']), int(e.get('release_step', 1))) if 'release_at' in e else None
        v = gba.envelope_4bit(n, rate, int(e.get('start', 15)), int(e.get('step', 0)), int(e.get('dir', -1)), rel)
    else:
        v = np.round(frame_hold(np.clip(curve(L.get('env', [[0, 1]]), n, rate), 0, 1), rate) * 15)
    return v / 15.0


def vibrato(hz, L, rate):
    v = L.get('vibrato')
    if v:
        t = np.arange(len(hz)) / rate
        hz = hz * 2 ** (float(v.get('depth', 0.5)) / 12 * np.sin(2 * np.pi * float(v.get('rate', 6)) * t))
    return hz


# ---------------------------------------------------------------- chip layers

def layer_square(L, n, rate, rng):
    hz = vibrato(curve(L['pitch'], n, rate, 'exp'), L, rate)
    sw = L.get('sweep')
    x = gba.chip_square(hz, rate, int(L.get('duty', 2)), tuple(sw) if sw else None)
    return x * chip_env(L, n, rate)


def layer_wave(L, n, rate, rng):
    hz = vibrato(curve(L['pitch'], n, rate, 'exp'), L, rate)
    tb = L.get('table', 'sine')
    x = gba.chip_wave(hz, rate, WAVE_PRESETS[tb] if isinstance(tb, str) else tb)
    # The wave channel only has four volumes; m4a picks the nearest per frame.
    v = frame_hold(np.clip(curve(L.get('env', [[0, 1]]), n, rate), 0, 1), rate)
    v = np.array(WAVE_VOLUMES)[np.abs(v[:, None] - np.array(WAVE_VOLUMES)[None, :]).argmin(axis=1)]
    return x * v


def layer_noise(L, n, rate, rng):
    if 'nr43' in L:
        s, d = L['nr43']
        x = gba.chip_noise(n, rate, int(s), int(d), bool(L.get('short', False)))
    else:
        x = gba.chip_noise(n, rate, short=bool(L.get('short', False)), hz=curve(L['clock'], n, rate, 'exp'))
    return x * chip_env(L, n, rate)


# ---------------------------------------------------------------- pcm layers

def osc(kind, hz, rate, rng, width=0.5):
    ph = np.cumsum(hz / rate)
    if kind == 'sine':
        return np.sin(2 * np.pi * ph)
    if kind == 'tri':
        return 2 * np.abs(2 * (ph % 1) - 1) - 1
    if kind == 'saw':
        return 2 * (ph % 1) - 1
    if kind == 'square':
        return np.where(ph % 1 < width, 1.0, -1.0)
    if kind == 'noise':
        return rng.standard_normal(len(hz))
    raise ValueError(kind)


def svf(x, cutoff, q, kind, rate):
    """Time-varying state-variable filter (cutoff per sample). kind: lp, bp, hp."""
    y = np.zeros_like(x)
    lp = bp = 0.0
    f = 2 * np.sin(np.pi * np.clip(cutoff, 20, rate * 0.22) / rate)
    damp = 1.0 / max(q, 0.5)
    for i in range(len(x)):
        hp = x[i] - lp - damp * bp
        bp += f[i] * hp
        lp += f[i] * bp
        y[i] = lp if kind == 'lp' else (bp if kind == 'bp' else hp)
    return y


def layer_pcm(L, n, rate, rng):
    """Free synthesis that becomes an 8-bit sample: oscillators (with detuned unison), FM, AM, ring mod,
    a moving filter, drive and bit-crush."""
    kind = L.get('osc', 'saw')
    hz = vibrato(curve(L.get('pitch', 440), n, rate, 'exp'), L, rate)
    if 'fm' in L:
        fm = L['fm']
        mod = np.sin(2 * np.pi * np.cumsum(hz * float(fm.get('ratio', 1.0)) / rate))
        hz = hz * (1 + curve(fm.get('index', 1.0), n, rate) * mod)
    x = np.zeros(n)
    det = L.get('unison', [0.0])
    for c in det:
        x += osc(kind, hz * 2 ** (float(c) / 1200), rate, rng, float(L.get('width', 0.5)))
    x /= len(det)
    if 'am' in L:
        am = L['am']
        t = np.arange(n) / rate
        depth = curve(am.get('depth', 0.5), n, rate)
        rate_hz = curve(am.get('rate', 8), n, rate)
        x *= 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(rate_hz) / rate))
    if 'ring' in L:
        x *= np.sin(2 * np.pi * np.cumsum(curve(L['ring'], n, rate, 'exp')) / rate)
    if 'filter' in L:
        fl = L['filter']
        cut = curve(fl['cutoff'], n, rate, 'exp')
        for _ in range(int(fl.get('stages', 1))):        # stages: cascade for a steeper slope
            x = svf(x, cut, float(fl.get('q', 1.0)), fl.get('type', 'lp'), rate)
    if L.get('crush'):
        steps = 2 ** int(L['crush'])
        x = np.round(x / (np.abs(x).max() + 1e-9) * steps) / steps
    return x


LAYERS = {'square': layer_square, 'wave': layer_wave, 'noise': layer_noise, 'pcm': layer_pcm}
CHIP = {'square', 'wave', 'noise'}


def render(spec):
    rng = np.random.default_rng(int(spec.get('seed', 1)))
    total = max(layer_end(L) for L in spec['layers'])
    N = int((total + 0.01) * SYNTH_RATE)
    mix = np.zeros(N)
    for L in spec['layers']:
        at = int(float(L.get('at', 0)) * SYNTH_RATE)
        n = int((layer_end(L) - float(L.get('at', 0))) * SYNTH_RATE)
        n = min(n, N - at)
        x = LAYERS[L['type']](L, n, SYNTH_RATE, rng)
        if L['type'] == 'pcm' and 'env' in L:
            x = x * np.clip(curve(L['env'], n, SYNTH_RATE), 0, None)
        if L.get('drive'):
            d = float(L['drive'])
            x = np.tanh(x * d) / np.tanh(d)
        if L['type'] == 'pcm' and L.get('normalize', True):
            x = x / (np.abs(x).max() + 1e-9)
        # Chip layers keep their 4-bit levels: full volume 15 = amplitude 1 before the layer gain.
        mix[at:at + n] += float(L.get('gain', 1.0)) * x
    return mix


def master(x, spec):
    """Band-limit and decimate to the 13379 Hz mixer rate, trim, fade, peak-normalise, optional loop."""
    m = spec.get('master', {})
    if m.get('highpass', 40):
        x = signal.sosfilt(signal.butter(2, float(m.get('highpass', 40)), 'hp', fs=SYNTH_RATE, output='sos'), x)
    x = signal.sosfiltfilt(signal.butter(8, float(m.get('lowpass', 6000)), 'lp', fs=SYNTH_RATE, output='sos'), x)
    x = x[::4]
    rate = gba.MIXER_RATE
    loop = spec.get('loop')
    if loop:
        # Loop region [start, end): crossfade the tail into the loop start so the seam is continuous.
        s, e = int(float(loop['start']) * rate), int(float(loop['end']) * rate)
        xf = int(float(loop.get('crossfade', 0.05)) * rate)
        seg = x[:e].copy()
        w = np.linspace(0, 1, xf)
        seg[e - xf:e] = seg[e - xf:e] * (1 - w) + x[s - xf:s] * w
        x = seg
        x = x / max(np.abs(x).max(), 1e-9) * float(m.get('peak', gba.TARGET_PEAK))
        return x, (s, e)
    a = np.abs(x)
    idx = np.where(a > a.max() * 0.004)[0]
    x = x[max(0, idx[0] - 4): idx[-1] + 16]
    fi, fo = int(0.001 * rate), int(float(m.get('fade_out', 0.01)) * rate)
    x[:fi] *= np.linspace(0, 1, fi)
    x[-fo:] *= np.linspace(1, 0, fo)
    x = x / max(np.abs(x).max(), 1e-9) * float(m.get('peak', gba.TARGET_PEAK))
    return x, None

#!/usr/bin/env python3
"""cry-generator CLI.

  python3 cry.py survey                 # measure all 388 vanilla cries -> reference/vanilla_stats.json
  python3 cry.py make specs/mynock.yaml # render -> out/<name>.wav (game format) + out/<name>_preview.wav + report
  python3 cry.py check out/mynock.wav --slot zubat
  python3 cry.py modes out/mynock.wav   # render every in-game cry mode (doubles, faint, growl...) to out/modes/
  python3 cry.py install specs/mynock.yaml   # write the cry over its slot in ../../game (same filename, same table slot)
"""
import argparse
import json
import pathlib
import sys

import numpy as np
import yaml

import gba
import synth

HERE = pathlib.Path(__file__).resolve().parent
GAME = HERE.parent.parent / 'game'
CRIES = GAME / 'sound' / 'direct_sound_samples' / 'cries'
OUT = HERE / 'out'
REF = HERE / 'reference' / 'vanilla_stats.json'


def measure(x, rate=gba.CRY_RATE):
    x = np.asarray(x, float)
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / rate)
    cs = np.cumsum(X ** 2)
    head = x[:int(gba.DOUBLES_SECONDS * rate)]
    return {
        'seconds': len(x) / rate,
        'peak': float(np.abs(x).max()),
        'rms': float(np.sqrt(np.mean(x ** 2))),
        'centroid_hz': float((X * f).sum() / X.sum()),
        'rolloff85_hz': float(f[np.searchsorted(cs, 0.85 * cs[-1])]),
        'head_peak_ratio': float(np.abs(head).max() / max(np.abs(x).max(), 1e-9)),
        'edge': float(max(abs(x[0]), abs(x[-1]))),
        'dc': float(x.mean()),
    }


def cmd_survey(_):
    rows = {}
    for p in sorted(CRIES.glob('*.wav')):
        x, r = gba.read_wav(p)
        assert r == gba.CRY_RATE, (p, r)
        rows[p.stem] = measure(x)
    keys = next(iter(rows.values())).keys()
    band = {k: dict(zip(['p5', 'p25', 'p50', 'p75', 'p95'],
                        np.percentile([v[k] for v in rows.values()], [5, 25, 50, 75, 95]).round(4).tolist()))
            for k in keys}
    REF.parent.mkdir(exist_ok=True)
    REF.write_text(json.dumps({'count': len(rows), 'bands': band, 'cries': rows}, indent=1))
    print(json.dumps(band, indent=1))


def load_ref():
    if not REF.exists():
        sys.exit('run `python3 cry.py survey` first')
    return json.loads(REF.read_text())


def check(x, rate, slot=None, verbose=True, dpcm_snr=None):
    """The gate. Returns (ok, lines). Hard rules fail; soft rules warn."""
    ref = load_ref()
    B = ref['bands']
    m = measure(x, rate)
    lines, ok = [], True

    def rule(hard, cond, msg):
        nonlocal ok
        if not cond and hard:
            ok = False
        lines.append(('PASS' if cond else ('FAIL' if hard else 'WARN')) + '  ' + msg)

    rule(True, rate == gba.CRY_RATE, f'sample rate {rate} == {gba.CRY_RATE}')
    rule(True, m['seconds'] <= gba.MAX_SECONDS, f"length {m['seconds']:.2f}s <= {gba.MAX_SECONDS:.2f}s (normal-mode hard cut)")
    rule(False, m['seconds'] <= B['seconds']['p95'] + 0.3, f"length {m['seconds']:.2f}s within vanilla range (95% are <= {B['seconds']['p95']:.2f}s)")
    rule(True, m['head_peak_ratio'] >= 0.6, f"identity in the first {gba.DOUBLES_SECONDS:.2f}s (doubles mode): head peak {m['head_peak_ratio']:.2f} of max >= 0.6")
    rule(False, m['peak'] >= B['peak']['p5'], f"peak {m['peak']:.2f} >= {B['peak']['p5']:.2f} (vanilla cries are mastered hot)")
    rule(True, 0.12 <= m['rms'] <= 0.40, f"loudness: rms {m['rms']:.3f} in [0.12, 0.40] (the whole vanilla set)")
    rule(False, B['rms']['p5'] <= m['rms'] <= B['rms']['p95'], f"loudness: rms {m['rms']:.3f} in the vanilla middle 90% [{B['rms']['p5']:.3f}, {B['rms']['p95']:.3f}]")
    rule(False, B['centroid_hz']['p5'] * 0.8 <= m['centroid_hz'] <= B['centroid_hz']['p95'] * 1.2,
         f"brightness (centroid) {m['centroid_hz']:.0f} Hz near vanilla band [{B['centroid_hz']['p5']:.0f}, {B['centroid_hz']['p95']:.0f}]")
    rule(False, m['edge'] <= 0.05, f"starts/ends at silence (edge {m['edge']:.3f} <= 0.05, no click)")
    if dpcm_snr is None:
        lv = gba.to_s8(x)
        dpcm_snr = gba.snr_db(lv, gba.dpcm_roundtrip(lv))
    snr = dpcm_snr
    rule(True, snr >= 10, f'survives DPCM compression: SNR {snr:.1f} dB >= 10 (>100 means the file is already DPCM-exact)')
    rule(False, snr >= 16, f'DPCM grit: SNR {snr:.1f} dB >= 16 (bright vanilla cries are gritty too)')
    if slot:
        o = ref['cries'].get(slot)
        if o:
            rule(False, 0.5 * o['seconds'] <= m['seconds'] <= 1.6 * o['seconds'] + 0.15,
                 f"length {m['seconds']:.2f}s vs the slot's original {slot}.wav {o['seconds']:.2f}s (0.5x-1.6x)")
    if verbose:
        print('\n'.join(lines))
    return ok, lines, m, snr


DPCM_TARGET_SNR = 20.0


def render_spec(spec, log=print):
    """Render, master, then fit the DPCM format. Returns (baked float audio, DPCM SNR).

    DPCM fit (CONSTRAINTS.md section 3): the cry format can move at most 64 levels per sample, so loud
    high-pitched sound smears into grit. We try the master with more and more high-shelf cut (and, last,
    a quieter target) until the optimal DPCM path is within DPCM_TARGET_SNR of the master. The optimal
    path is baked into the .wav, so the build's own encoder reproduces it exactly (vanilla cries are
    DPCM-exact files too)."""
    raw = synth.render(spec)
    m0 = dict(spec.get('master', {}))
    cache = {}

    def attempt(tilt, rms_scale):
        key = (tilt, rms_scale)
        if key not in cache:
            sp = dict(spec, master=dict(m0, tilt_db=tilt, rms=m0.get('rms', gba.TARGET_RMS) * rms_scale))
            lv = gba.to_s8(synth.master(raw, sp))
            dec = gba.dpcm_optimal(lv)
            cache[key] = (dec, gba.snr_db(lv, dec), tilt, rms_scale)
        return cache[key]

    best = None
    # Vanilla bright cries are quieter (rms ~0.15) and lean on the slew limit; dark ones are hot (rms ~0.25).
    # So: first ask for a clean fit at full loudness, then trade loudness, then tilt, then accept some grit.
    for need in (DPCM_TARGET_SNR, 16.0, 12.0):
        for rms_scale in (1.0, 0.85, 0.7, 0.6):
            for tilt in (m0.get('tilt_db', 0.0), -3.0, -6.0, -9.0):
                r = attempt(tilt, rms_scale)
                if best is None or r[1] > best[1]:
                    best = r
                if r[1] >= need:
                    best = r
                    break
            if best[1] >= need:
                break
        if best[1] >= need:
            break
    dec, snr, tilt, rms_scale = best
    log(f'   dpcm fit: tilt {tilt} dB, loudness x{rms_scale}, SNR {snr:.1f} dB')
    return dec.astype(float) / 128.0, snr


def cmd_make(a):
    spec = yaml.safe_load(open(a.spec))
    name = spec['name']
    OUT.mkdir(exist_ok=True)
    x, snr = render_spec(spec)
    gba.write_wav_u8(OUT / f'{name}.wav', x)
    pre = gba.play_in_game(gba.to_s8(x), 'normal')
    gba.write_wav_16(OUT / f'{name}_preview.wav', pre, gba.MIXER_RATE)
    print(f'== {name}  ({spec.get("slot")}.wav slot)  -> out/{name}.wav')
    ok, lines, m, snr = check(x, gba.CRY_RATE, spec.get('slot'), dpcm_snr=snr)
    (OUT / f'{name}.report.json').write_text(json.dumps({'ok': ok, 'checks': lines, 'measure': m, 'dpcm_snr': snr}, indent=1))
    return ok


def cmd_check(a):
    x, r = gba.read_wav(a.wav)
    ok, *_ = check(x, r, a.slot)
    sys.exit(0 if ok else 1)


def cmd_modes(a):
    x, r = gba.read_wav(a.wav)
    d = OUT / 'modes' / pathlib.Path(a.wav).stem
    d.mkdir(parents=True, exist_ok=True)
    for mode in gba.MODES:
        gba.write_wav_16(d / f'{mode}.wav', gba.play_in_game(gba.to_s8(x), mode), gba.MIXER_RATE)
    print('wrote', d)


def cmd_install(a):
    spec = yaml.safe_load(open(a.spec))
    src = OUT / f"{spec['name']}.wav"
    if not src.exists():
        sys.exit(f'make it first: python3 cry.py make {a.spec}')
    x, r = gba.read_wav(src)
    ok, *_ = check(x, r, spec['slot'], verbose=False)
    if not ok:
        sys.exit('check failed; not installing')
    dst = CRIES / f"{spec['slot']}.wav"
    dst.write_bytes(src.read_bytes())
    print(f'installed {src.name} -> {dst.relative_to(GAME.parent)} (same table slot; rename + data/cry_tables edits are a separate port step)')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='cmd', required=True)
    s.add_parser('survey')
    m = s.add_parser('make'); m.add_argument('spec', nargs='+')
    c = s.add_parser('check'); c.add_argument('wav'); c.add_argument('--slot')
    o = s.add_parser('modes'); o.add_argument('wav')
    i = s.add_parser('install'); i.add_argument('spec')
    a = p.parse_args()
    if a.cmd == 'make':
        okall = True
        for sp in a.spec:
            a1 = argparse.Namespace(spec=sp)
            okall &= cmd_make(a1)
        sys.exit(0 if okall else 1)
    {'survey': cmd_survey, 'check': cmd_check, 'modes': cmd_modes, 'install': cmd_install}[a.cmd](a)


if __name__ == '__main__':
    main()

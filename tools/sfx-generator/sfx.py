#!/usr/bin/env python3
"""sfx-generator CLI.

  python3 sfx.py survey                       # vanilla SE lengths/voices -> reference/vanilla_se.json
  python3 sfx.py make specs/blaster_bolt.yaml # -> out/<name>.wav (game format, 13379 Hz 8-bit)
                                              #    out/<name>_preview.wav (44.1 kHz, as heard: reverb + DAC)
  python3 sfx.py check out/blaster_bolt.wav
  python3 sfx.py install specs/blaster_bolt.yaml [--game DIR]   # wire it into the game (see README)
"""
import argparse
import json
import pathlib
import re
import struct
import sys

import numpy as np
import yaml

import gba
import synth

HERE = pathlib.Path(__file__).resolve().parent
GAME = HERE.parent.parent / 'game'
OUT = HERE / 'out'
REF = HERE / 'reference' / 'vanilla_se.json'


# ------------------------------------------------------------------ MIDI (read + write, no deps)

def _vlq(d, i):
    v = 0
    while True:
        b = d[i]
        i += 1
        v = (v << 7) | (b & 0x7F)
        if b < 0x80:
            return v, i


def midi_summary(path):
    d = open(path, 'rb').read()
    div = struct.unpack('>H', d[12:14])[0]
    i, tempo, end, progs, notes = 14, 500000, 0, set(), 0
    while i < len(d):
        ln = struct.unpack('>I', d[i + 4:i + 8])[0]
        td, i = d[i + 8:i + 8 + ln], i + 8 + ln
        j, t, rs = 0, 0, 0
        while j < len(td):
            dt, j = _vlq(td, j)
            t += dt
            b = td[j]
            if b == 0xFF:
                l, k = _vlq(td, j + 2)
                if td[j + 1] == 0x51:
                    tempo = int.from_bytes(td[k:k + l], 'big')
                j = k + l
            elif b in (0xF0, 0xF7):
                l, k = _vlq(td, j + 1)
                j = k + l
            else:
                if b & 0x80:
                    rs = b
                    j += 1
                n = 1 if (rs & 0xF0) in (0xC0, 0xD0) else 2
                if rs & 0xF0 == 0xC0:
                    progs.add(td[j])
                if rs & 0xF0 == 0x90 and td[j + 1]:
                    notes += 1
                j += n
            end = max(end, t)
    return {'seconds': end / div * tempo / 1e6, 'programs': sorted(progs), 'notes': notes}


def write_one_note_midi(path, seconds, hold=False):
    """Format-0 MIDI: program 0, one C4 (key 60 = the sample's native rate), velocity 127.
    mid2agb turns it into the .s the game links; the voicegroup gives program 0 the new sample."""
    div, tempo = 24, 500000                     # 24 ticks per beat at 120 bpm = 48 ticks/s
    ticks = max(1, int(np.ceil(seconds * 48)))

    def v(n):
        b = [n & 0x7F]
        n >>= 7
        while n:
            b.insert(0, (n & 0x7F) | 0x80)
            n >>= 7
        return bytes(b)
    ev = b'\x00\xFF\x51\x03' + tempo.to_bytes(3, 'big') + b'\x00\xC0\x00' + b'\x00\x90\x3C\x7F'
    ev += v(ticks if not hold else 48 * 60) + b'\x80\x3C\x00' + b'\x00\xFF\x2F\x00'
    data = b'MThd' + struct.pack('>IHHH', 6, 0, 1, div) + b'MTrk' + struct.pack('>I', len(ev)) + ev
    pathlib.Path(path).write_bytes(data)


# ------------------------------------------------------------------ survey + gate

def cmd_survey(_):
    cfg = {l.split(':')[0]: l.split(':', 1)[1].strip()
           for l in open(GAME / 'sound/songs/midi/midi.cfg') if l.startswith('se_')}
    rows = {}
    for f, opts in sorted(cfg.items()):
        s = midi_summary(GAME / 'sound/songs/midi' / f)
        s['voicegroup'] = re.search(r'-G(\S+)', opts).group(1)
        s['opts'] = opts
        rows[f[:-4]] = s
    secs = [r['seconds'] for r in rows.values()]
    band = dict(zip(['p5', 'p25', 'p50', 'p75', 'p95', 'max'],
                    [round(float(v), 3) for v in np.percentile(secs, [5, 25, 50, 75, 95, 100])]))
    REF.parent.mkdir(exist_ok=True)
    REF.write_text(json.dumps({'count': len(rows), 'seconds': band, 'se': rows}, indent=1))
    print(json.dumps(band))


def check(x, rate, spec=None, verbose=True):
    lines, ok = [], True

    def rule(hard, cond, msg):
        nonlocal ok
        ok &= cond or not hard
        lines.append(('PASS' if cond else ('FAIL' if hard else 'WARN')) + '  ' + msg)

    secs = len(x) / rate
    rule(True, rate == gba.MIXER_RATE, f'sample rate {rate} == {gba.MIXER_RATE} (the mixer rate; higher is thrown away)')
    rule(True, secs <= gba.SE_MAX_SECONDS, f'length {secs:.2f}s <= {gba.SE_MAX_SECONDS}s (longest vanilla SE)')
    rule(False, secs <= 3.2 or (spec or {}).get('loop'), f'length {secs:.2f}s <= 3.2s (95% of vanilla SEs are shorter)')
    pk = float(np.abs(x).max())
    rule(True, 0.5 <= pk <= 1.0, f'peak {pk:.2f} in [0.5, 1.0]')
    rule(False, abs(float(x.mean())) < 0.02, f'DC {x.mean():+.3f} ~ 0')
    if not (spec or {}).get('loop'):
        rule(False, max(abs(x[0]), abs(x[-1])) < 0.05, 'starts/ends at silence (no click)')
    kb = len(x) / 1024
    rule(False, kb <= 40, f'ROM cost {kb:.1f} KB <= 40 KB (8-bit at 13379 Hz = 13 KB/s)')
    if spec:
        # Hardware budget: what could really sound at once (CONSTRAINTS.md section 2).
        tl = [(float(L.get('at', 0)), synth.layer_end(L), L['type'], bool(L.get('sweep'))) for L in spec['layers']]
        worst = {}
        for t0, t1, kind, _ in tl:
            mid = [(a, b, k, s) for a, b, k, s in tl if a < t1 and b > t0]
            for k in ('square', 'wave', 'noise', 'pcm'):
                worst[k] = max(worst.get(k, 0), sum(1 for m in mid if m[2] == k))
        sweeps = sum(1 for _, _, k, s in tl if s)
        rule(True, worst.get('square', 0) <= 2, f"<= 2 square voices at once ({worst.get('square', 0)})")
        rule(True, worst.get('wave', 0) <= 1, f"<= 1 wave voice at once ({worst.get('wave', 0)})")
        rule(True, worst.get('noise', 0) <= 1, f"<= 1 noise voice at once ({worst.get('noise', 0)})")
        rule(True, worst.get('pcm', 0) <= 3, f"<= 3 pcm voices at once ({worst.get('pcm', 0)}; the mixer has 5, BGM needs some)")
        rule(True, sweeps <= 1 or worst.get('square', 0) <= 1, 'hardware sweep only on square 1')
    if verbose:
        print('\n'.join(lines))
    return ok, lines


# ------------------------------------------------------------------ make

def cmd_make(a):
    okall = True
    for p in a.spec:
        spec = yaml.safe_load(open(p))
        name = spec['name']
        OUT.mkdir(exist_ok=True)
        x, loop = synth.master(synth.render(spec), spec)
        gba.write_wav_u8(OUT / f'{name}.wav', x, loop=loop)
        x8 = gba.to_s8(x) / 128.0
        if loop:   # audition a loop by playing it three times through
            s, e = loop
            x8 = np.concatenate([x8[:e]] + [x8[s:e]] * 2)
        pre = gba.zoh_44k(gba.play_in_game(x8))
        gba.write_wav_16(OUT / f'{name}_preview.wav', pre, 44100)
        print(f"== {name}  ({spec.get('replaces') or 'net-new ' + spec['constant']})  {len(x) / gba.MIXER_RATE:.2f}s -> out/{name}.wav")
        ok, lines = check(x8 if not loop else x, gba.MIXER_RATE, spec)
        okall &= ok
    sys.exit(0 if okall else 1)


def cmd_check(a):
    x, r = gba.read_wav(a.wav)
    ok, _ = check(x, r)
    sys.exit(0 if ok else 1)


# ------------------------------------------------------------------ install

def install(spec, game):
    """Wire one SE into a game tree:
      sound/direct_sound_samples/sw_sfx/<name>.wav   the sample (built to .bin by audio_rules.mk)
      sound/direct_sound_data.inc                    DirectSoundWaveData_sw_<name>
      sound/voicegroups/sw_<name>.inc (+ voice_groups.inc)   one voice, program 0, native rate, no envelope
      sound/songs/midi/<se>.mid + midi.cfg           one C4 note on that voicegroup, -E -R50 like vanilla
      NET_NEW only: a free song id (the dummy_song_header slots 270-349) in song_table.inc + songs.h
    """
    game = pathlib.Path(game)
    name = spec['name']
    src = OUT / f'{name}.wav'
    x, r = gba.read_wav(src)
    secs = len(x) / r
    d = game / 'sound/direct_sound_samples/sw_sfx'
    d.mkdir(parents=True, exist_ok=True)
    (d / f'{name}.wav').write_bytes(src.read_bytes())

    dsd = game / 'sound/direct_sound_data.inc'
    t = dsd.read_text()
    label = f'DirectSoundWaveData_sw_{name}'
    if label not in t:
        t = t.rstrip('\n') + f'\n\n\t.align 2\n{label}::\n\t.incbin "sound/direct_sound_samples/sw_sfx/{name}.bin"\n'
        dsd.write_text(t)

    vg = game / f'sound/voicegroups/sw_{name}.inc'
    loop = bool(spec.get('loop'))
    voice = 'voice_directsound_no_resample' if not loop else 'voice_directsound'
    # attack 255 (instant), decay 0, sustain 255, release: 0 = cut for one-shots, 200 = short fade for loops
    vg.write_text(f'voice_group sw_{name}\n\t{voice} 60, 0, {label}, 255, 0, 255, {200 if loop else 0}\n')
    vgi = game / 'sound/voice_groups.inc'
    t = vgi.read_text()
    inc = f'.include "sound/voicegroups/sw_{name}.inc"'
    if inc not in t:
        vgi.write_text(t.rstrip('\n') + '\n' + inc + '\n')

    mid_dir = game / 'sound/songs/midi'
    cfg = mid_dir / 'midi.cfg'
    lines = cfg.read_text().splitlines()
    if spec.get('replaces'):
        se = spec['replaces'].lower()
        old = next(l for l in lines if l.startswith(se + '.mid:'))
        opts = re.sub(r'-G\S+', f'-G_sw_{name}', old.split(':', 1)[1].strip())
        lines = [f'{se}.mid:' + ' ' * max(1, 31 - len(se) - 5) + opts if l == old else l for l in lines]
    else:
        se = 'se_' + name
        songs_h = game / 'include/constants/songs.h'
        h = songs_h.read_text()
        const = spec['constant']
        if f'#define {const} ' not in h:
            used = {int(m) for m in re.findall(r'#define SE_\w+\s+(\d+)', h)}
            sid = next(i for i in range(270, 350) if i not in used)
            st = game / 'sound/song_table.inc'
            tl = st.read_text().splitlines()
            start = tl.index('gSongTable::') + 1
            assert 'dummy_song_header' in tl[start + sid], tl[start + sid]
            tl[start + sid] = f'\tsong {se}, MUSIC_PLAYER_SE1, 1'
            st.write_text('\n'.join(tl) + '\n')
            tag = '// Star Wars SFX (sfx-generator)'
            if tag not in h:
                h = h.replace('\n\n// Music\n', f'\n\n{tag}\n\n// Music\n', 1)
            h = h.replace('\n\n// Music\n', f'\n#define {const:<27} {sid}\n\n// Music\n', 1)
            songs_h.write_text(h)
        # ld_script.ld names every song object; a new song must be listed or the linker drops it.
        # New SEs go in a run right after se_sudowoodo_shake (the last vanilla SE), in install order.
        ld = game / 'ld_script.ld'
        lt = ld.read_text().split('\n')
        obj = f'sound/songs/midi/{se}.o(.rodata);'
        if not any(l.strip() == obj for l in lt):
            k = next(i for i, l in enumerate(lt) if l.strip() == 'sound/songs/midi/se_sudowoodo_shake.o(.rodata);')
            indent = lt[k][:len(lt[k]) - len(lt[k].lstrip())]
            ours = {f'sound/songs/midi/{l.split(".mid:")[0]}.o(.rodata);' for l in lines if '-G_sw_' in l}
            while lt[k + 1].strip() in ours:
                k += 1
            lt.insert(k + 1, indent + obj)
            ld.write_text('\n'.join(lt))
        if not any(l.startswith(se + '.mid:') for l in lines):
            lines.append(f'{se}.mid:' + ' ' * max(1, 31 - len(se) - 5) + f'-E -R50 -G_sw_{name} -V100 -P5')
    cfg.write_text('\n'.join(lines) + '\n')
    write_one_note_midi(mid_dir / f'{se}.mid', secs + 0.05, hold=loop)
    stale = mid_dir / f'{se}.s'
    if stale.exists():
        stale.unlink()
    return se


def cmd_install(a):
    for p in a.spec:
        spec = yaml.safe_load(open(p))
        if not (OUT / f"{spec['name']}.wav").exists():
            sys.exit(f'make it first: python3 sfx.py make {p}')
        se = install(spec, a.game)
        print(f"installed {spec['name']} -> {se} in {a.game}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='cmd', required=True)
    s.add_parser('survey')
    m = s.add_parser('make'); m.add_argument('spec', nargs='+')
    c = s.add_parser('check'); c.add_argument('wav')
    i = s.add_parser('install'); i.add_argument('spec', nargs='+'); i.add_argument('--game', default=str(GAME))
    a = p.parse_args()
    {'survey': cmd_survey, 'make': cmd_make, 'check': cmd_check, 'install': cmd_install}[a.cmd](a)


if __name__ == '__main__':
    main()

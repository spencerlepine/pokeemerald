#!/usr/bin/env python3
"""Hear cries from the real ROM: build a scratch copy of ../../game with the made cries installed and a
small test hook, then record each cry (and its vanilla original) out of mGBA.

  python3 romtest.py specs/*.yaml          -> out/rom/<name>.wav (new) and out/vanilla/<slot>.wav

Needs the play-tester setup (../play-tester/scripts/setup-ubuntu.sh: agbcc, mGBA 0.11, Xvfb). Nothing in
../../game is touched: the copy lives in $TMPDIR/cry-romtest. The hook (never committed) reads a mailbox at
0x0203FF00 (free EWRAM above the game's last symbol, 0x0203CF5C) that mGBA cheat codes write every frame,
and calls PlayCry_Normal with the in-battle reverb (50) set, so the recording is what a battle sounds like.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np
import yaml

HERE = pathlib.Path(__file__).resolve().parent
GAME = HERE.parent.parent / 'game'
PLAYTEST = HERE.parent / 'play-tester'
WORK = pathlib.Path(os.environ.get('TMPDIR', '/tmp')) / 'cry-romtest'
MGBA = pathlib.Path(os.environ.get('MGBA_PREFIX', '/opt/mgba-0.11')) / 'bin' / 'mgba'

HOOK = '''        {   // ROMTEST HOOK (scratch copy only, never committed)
            static u32 sLast;
            vu16 *mb = (vu16 *)0x0203FF00;
            u32 key = (mb[0] << 16) | mb[1];
            if (key != sLast && (mb[0] == 0xBEEF || mb[0] == 0xC0DE) && gMain.vblankCounter1 > (u32)mb[3])
            {
                sLast = key;
                if (mb[0] == 0xBEEF) m4aSongNumStart(mb[1]); else { m4aSoundMode(0x80 | 50); PlayCry_Normal(mb[1], 0); }
            }
            if (mb[2] == 1) m4aMPlayStop(&gMPlayInfo_BGM);
        }
'''


def prepare(fresh):
    if fresh or not (WORK / 'game').exists():
        shutil.rmtree(WORK, ignore_errors=True)
        WORK.mkdir(parents=True)
        shutil.copytree(GAME, WORK / 'game', symlinks=True)
    g = WORK / 'game'
    main = g / 'src/main.c'
    src = (GAME / 'src/main.c').read_text()
    anchor = '    for (;;)\n    {\n        ReadKeys();\n'
    assert anchor in src
    src = src.replace(anchor, anchor + HOOK, 1)
    for inc in ('#include "m4a.h"', '#include "sound.h"'):
        if inc not in src:
            src = src.replace('#include "main.h"', '#include "main.h"\n' + inc, 1)
    main.write_text(src)
    return g


def build(g):
    r = subprocess.run(['make', f'-j{os.cpu_count()}'], cwd=g, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-3000:] + r.stderr[-3000:])


def species_id(g, slot):
    h = (g / 'include/constants/species.h').read_text()
    m = re.search(rf'#define SPECIES_{slot.upper()}\s+(\d+)', h)
    return int(m.group(1))


def record(rom, magic, ident, seconds, out):
    env = dict(os.environ, SDL_AUDIODRIVER='disk', DISPLAY=os.environ.get('DISPLAY', ':97'),
               LD_LIBRARY_PATH=str(MGBA.parent.parent / 'lib'))
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        (t / 'c.cheats').write_text(f'# romtest\n8203FF00 {magic}\n8203FF02 {ident:04X}\n8203FF04 0001\n8203FF06 001E\n')
        env['SDL_DISKAUDIOFILE'] = str(t / 'out.raw')
        try:
            subprocess.run([str(MGBA), '-c', str(t / 'c.cheats'), str(rom)], env=env, timeout=seconds,
                           capture_output=True)
        except subprocess.TimeoutExpired:
            pass
        x = np.fromfile(t / 'out.raw', '<i2').reshape(-1, 2).mean(axis=1)   # SDL disk driver: s16 stereo 44.1k
    idx = np.where(np.abs(x) > 60)[0]
    s = e = idx[0]
    for i in idx:                       # first sound event: stop at a 0.35 s gap
        if i - e > 0.35 * 44100:
            break
        e = i
    y = x[max(0, s - 200):e + 400]
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(y.astype('<i2').tobytes())
    print(f'  {out.relative_to(HERE)}  {len(y) / 44100:.2f}s')


def ensure_display():
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':97'
        subprocess.Popen(['Xvfb', ':97', '-screen', '0', '640x480x24'], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)


def main(paths):
    ensure_display()
    specs = [yaml.safe_load(open(p)) for p in paths]
    g = prepare(fresh=False)
    for f in (GAME / 'sound/direct_sound_samples/cries').glob('*.wav'):   # start from vanilla cries
        shutil.copy2(f, g / 'sound/direct_sound_samples/cries' / f.name)
    build(g)
    print('vanilla:')
    for s in specs:
        record(g / 'pokeemerald.gba', 'C0DE', species_id(g, s['slot']), 4, HERE / 'out/vanilla' / f"{s['slot']}.wav")
    for s in specs:
        shutil.copy2(HERE / 'out' / f"{s['name']}.wav", g / 'sound/direct_sound_samples/cries' / f"{s['slot']}.wav")
    build(g)
    print('new:')
    for s in specs:
        record(g / 'pokeemerald.gba', 'C0DE', species_id(g, s['slot']), 4, HERE / 'out/rom' / f"{s['name']}.wav")


if __name__ == '__main__':
    main(sys.argv[1:])

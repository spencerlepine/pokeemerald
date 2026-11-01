#!/usr/bin/env python3
"""Hear SFX from the real ROM: build a scratch copy of ../../game with the made SFX installed (sfx.py
install, the same code path as a real install) and a small test hook, then record each SE out of mGBA.
For hot-swaps the vanilla SE is recorded first.

  python3 romtest.py specs/*.yaml          -> out/rom/<name>.wav (new) and out/vanilla/<se>.wav

Needs the play-tester setup (../play-tester/scripts/setup-ubuntu.sh: agbcc, mGBA 0.11, Xvfb). Nothing in
../../game is touched: the copy lives in $TMPDIR/sfx-romtest. The hook (never committed) reads a mailbox at
0x0203FF00 (free EWRAM above the game's last symbol, 0x0203CF5C) that mGBA cheat codes write every frame,
and calls m4aSongNumStart (SE songs set reverb 50 themselves, like in game).
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

import sfx

HERE = pathlib.Path(__file__).resolve().parent
GAME = HERE.parent.parent / 'game'
PLAYTEST = HERE.parent / 'play-tester'
WORK = pathlib.Path(os.environ.get('TMPDIR', '/tmp')) / 'sfx-romtest'
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


def song_id(g, const):
    h = (g / 'include/constants/songs.h').read_text()
    return int(re.search(rf'#define {const}\s+(\d+)', h).group(1))


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
    g = prepare(fresh=True)            # fresh copy: installs edit songs.h, song_table, ld_script
    build(g)
    swaps = [s for s in specs if s.get('replaces')]
    if swaps:
        print('vanilla:')
    for s in swaps:
        record(g / 'pokeemerald.gba', 'BEEF', song_id(g, s['replaces']), 4, HERE / 'out/vanilla' / f"{s['replaces'].lower()}.wav")
    for s in specs:
        sfx.install(s, g)
    prepare(fresh=False)               # re-apply the hook (install never touches main.c, this is a no-op guard)
    build(g)
    print('new:')
    for s in specs:
        sid = song_id(g, s['replaces'] if s.get('replaces') else s['constant'])
        secs = 6 if s.get('loop') else 4
        record(g / 'pokeemerald.gba', 'BEEF', sid, secs, HERE / 'out/rom' / f"{s['name']}.wav")


if __name__ == '__main__':
    main(sys.argv[1:])

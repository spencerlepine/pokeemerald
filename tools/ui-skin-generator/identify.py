"""Which palette files is the game showing right now?
Dumps the live palette RAM from the play-tester mGBA session and matches every 16-colour bank against the
converted palettes in game/build/assets (so run a build first).
    python3 identify.py [label]      # prints BG0-15 / OBJ0-15 -> best matching source palette + bank
"""
import glob, json, os, re, struct, subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
GAME = HERE.parent.parent / 'game'
LIVE = HERE.parent / 'play-tester' / 'scripts' / 'live.sh'
LUA = 'local t={} for i=0,511 do t[#t+1]=string.format("%04x", emu:read16(0x05000000+i*2)) end return table.concat(t)'

def pram():
    out = subprocess.run([str(LIVE), 'lua', LUA], capture_output=True, text=True, check=True).stdout
    h = json.loads(out)['data']['result']
    return [int(h[i:i + 4], 16) & 0x7fff for i in range(0, len(h), 4)]

def index():
    idx = {}
    for f in glob.glob(str(GAME / 'build/assets/**/*.gbapal'), recursive=True):
        d = open(f, 'rb').read(); c = [v & 0x7fff for v in struct.unpack('<%dH' % (len(d) // 2), d)]
        src = re.sub(r'(\.(png|pal|bin))[^/]*$', r'\1', os.path.relpath(f, GAME / 'build/assets'))
        for b in range(len(c) // 16): idx.setdefault(src, []).append(c[16 * b:16 * b + 16])
    return idx

def main():
    p = pram(); idx = index()
    for bank in range(32):
        cols = p[16 * bank:16 * bank + 16]
        if not any(cols[1:]): continue
        best = []
        for src, banks in idx.items():
            for b, sc in enumerate(banks):
                n = sum(1 for i in range(1, 16) if cols[i] == sc[i] and cols[i] not in (0,))
                nz = sum(1 for i in range(1, 16) if cols[i])
                if nz and n >= max(3, nz - 2): best.append((n, src, b))
        best.sort(key=lambda t: -t[0])
        name = ('BG%d' % bank) if bank < 16 else ('OBJ%d' % (bank - 16))
        hexes = ' '.join('%02x%02x%02x' % ((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3) for c in cols)
        print(f'{name:6} {hexes}')
        for n, src, b in best[:4]: print(f'         {n:2}/15  {src}  bank {b}')
        if not best: print('         ?  (no file match: C constant, .bin, or runtime-built palette)')

if __name__ == '__main__':
    main()

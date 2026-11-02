"""Phase 3: apply the Dune theme to the game's UI palettes.

Run from tools/ui-skin-generator:
    python3 apply.py            # (re)apply every family listed in DONE
    python3 apply.py --list     # print what each family touches, change nothing
    python3 apply.py --check    # exit 1 if any family file differs from what apply would write

Every palette is recomputed from its vanilla copy at VANILLA_REF (git), so the script is idempotent and a
rule change re-runs cleanly. Only palette colours change: .pal files are rewritten in place (same CRLF layout),
PNG files get a new PLTE chunk with every other byte kept, so pixel data and 4bpp output are identical.

Never touched: text colour indices (the game's text palette slots 1-9), type and contest-category chips
(graphics/types), creatures, items, maps, box wallpapers, HP bar colours, battle backgrounds.
"""
import os, re, subprocess, sys, struct, zlib, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
from dune import tx

VANILLA_REF = '5f04e4f8'   # last commit before any phase 3 palette edit
MAGENTA = {(248, 0, 248), (255, 0, 255)}
ALL = list(range(1, 16))
TEXT = list(range(1, 10))           # text colour slots
def but(*skip): return [i for i in ALL if i not in skip]
def rng(a, b): return list(range(a, b + 1))
def banks(*ns): return [16 * n + i for n in ns for i in range(16)]   # whole 16-colour palettes of a multi-palette PNG

# family -> [(path under game/, colour family for tx, indices to recolour)]
FAMILIES = {
  '1_text_windows': [
    ('graphics/text_window/message_box.png', 'ui', rng(13, 15)),     # overworld dialogue / sign frame
    *[(f'graphics/text_window/{n}.png', 'ui', ALL) for n in range(1, 21)],   # the 20 option frames
    *[(f'graphics/text_window/text_pal{n}.pal', 'ui', rng(10, 15)) for n in range(1, 5)],
    ('src/option_menu.c', 'ui', ['sOptionMenuBg_Pal[] = {RGB(17, 18, 31)}']),            # options backdrop
  ],
  '2_party_summary': [
    # party menu: 11 palettes; the slot colours are picked at runtime by id (src/data/party_menu.h).
    # HP bar green/yellow/red (57-58, 73-74, 89-90) and gender blue/red (59-60, 75-76) stay vanilla.
    ('graphics/party_menu/bg.png', 'ui', [i for i in banks(*range(11)) if i not in (57, 58, 59, 60, 73, 74, 75, 76, 89, 90)]),
    # summary screen: palettes 0-5 are panels and headers, 6-7 are text colours (kept)
    ('graphics/summary_screen/tiles.png', 'ui', banks(0, 1, 2, 3, 4, 5)),
    ('graphics/summary_screen/move_select.png', 'ui', ALL),
  ],
}
DONE = ['1_text_windows', '2_party_summary']

RGB_RE = re.compile(r'RGB\((\d+), *(\d+), *(\d+)\)')
def tx_rgb5(m, fam):
    r, g, b = (int(v) for v in m.groups())
    nr, ng, nb = tx((r << 3, g << 3, b << 3), fam)
    return 'RGB(%d, %d, %d)' % (nr >> 3, ng >> 3, nb >> 3)

def render_c(path, fam, snippets):
    """Hard-coded RGB() colours in C: each snippet is vanilla text that must occur exactly once."""
    text = vanilla(path).decode()
    for snip in snippets:
        assert text.count(snip) == 1, (path, snip)
        text = text.replace(snip, RGB_RE.sub(lambda m: tx_rgb5(m, fam), snip))
    return text.encode()

def vanilla(path):
    return subprocess.run(['git', '-C', str(REPO), 'show', f'{VANILLA_REF}:game/{path}'],
                          check=True, capture_output=True).stdout

def read_pal(data):
    lines = data.decode().split('\r\n') if b'\r\n' in data else data.decode().split('\n')
    n = int(lines[2]); return [tuple(int(v) for v in lines[3 + i].split()) for i in range(n)]

def write_pal(data, cols):
    lines = data.decode().replace('\r\n', '\n').split('\n')
    nl = '\r\n'   # .gitattributes checks .pal files out with CRLF
    for i, c in enumerate(cols): lines[3 + i] = '%d %d %d' % c
    return nl.join(lines).encode()

def png_chunks(data):
    i = 8
    while i < len(data):
        n, = struct.unpack('>I', data[i:i + 4]); t = data[i + 4:i + 8]
        yield i, t, data[i + 8:i + 8 + n]; i += 12 + n

def read_png_pal(data):
    for _, t, body in png_chunks(data):
        if t == b'PLTE': return [tuple(body[j:j + 3]) for j in range(0, len(body), 3)]
    raise ValueError('no PLTE')

def write_png_pal(data, cols):
    for off, t, body in png_chunks(data):
        if t == b'PLTE':
            new = bytes(v for c in cols for v in c)
            assert len(new) == len(body)
            chunk = struct.pack('>I', len(new)) + b'PLTE' + new + struct.pack('>I', zlib.crc32(b'PLTE' + new) & 0xffffffff)
            return data[:off] + chunk + data[off + 12 + len(body):]

def render(path, fam, idx):
    data = vanilla(path)
    png = path.endswith('.png')
    cols = (read_png_pal if png else read_pal)(data)
    # magenta slots are unused placeholders in vanilla files: leave them alone
    new = [tuple(tx(c, fam)) if i in idx and c not in MAGENTA else c for i, c in enumerate(cols)]
    return (write_png_pal if png else write_pal)(data, new), cols, new

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    bad = 0
    for fam_name in DONE if mode != '--list' else FAMILIES:
        for path, fam, idx in FAMILIES[fam_name]:
            dst = REPO / 'game' / path
            if path.endswith('.c'):
                out = render_c(path, fam, idx); old = new = []
                if mode == '--list':
                    print(f'{fam_name:18} {path:48} C colours: ' + '; '.join(
                        f'{s} -> {RGB_RE.sub(lambda m: tx_rgb5(m, fam), s)}' for s in idx)); continue
            else:
                out, old, new = render(path, fam, idx)
            changed = [i for i in range(len(old)) if old[i] != new[i]]
            if mode == '--list':
                print(f'{fam_name:18} {path:48} {len(changed):2} colours  ' +
                      ' '.join('%d:%02x%02x%02x>%02x%02x%02x' % (i, *old[i], *new[i]) for i in changed))
            elif mode == '--check':
                if dst.read_bytes() != out: print('differs:', path); bad = 1
                if path.endswith('.png'):   # pixel indices must match vanilla exactly
                    import io; from PIL import Image
                    a, b = Image.open(io.BytesIO(vanilla(path))), Image.open(dst)
                    if (a.mode, a.size, a.tobytes()) != (b.mode, b.size, b.tobytes()): print('PIXELS differ:', path); bad = 1
            else:
                if dst.read_bytes() != out: dst.write_bytes(out); print('wrote', path, len(changed) or '', 'colours')
    sys.exit(bad)

if __name__ == '__main__':
    main()

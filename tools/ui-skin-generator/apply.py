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

class Append:
    """Keep the file's vanilla colours and append Dune copies of the listed 16-colour banks (for palettes
    shared by chrome and by labels that must stay vanilla; the C side points the chrome at the new banks)."""
    def __init__(self, *bank_ids): self.banks = bank_ids

class Replace:
    """Exact text replacements in a C file (old must occur exactly once in the vanilla file)."""
    def __init__(self, *pairs): self.pairs = pairs

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
  '3_bag_pokeblock': [
    # scroll arrows, outline cursor and arrow cursor of every list menu (src/list_menu.c)
    ('graphics/interface/red.pal', 'ui', [1, 2]),
    # bag backdrop, stripes, list panel and pocket dots. Bank 1 is the bag's window palette: 1-11 and
    # 14-15 are text colours (kept); 12-13 repeat the backdrop stripes behind the pocket dots.
    ('graphics/bag/menu_male.pal', 'ui', banks(0) + [28, 29]),
    ('graphics/bag/menu_female.pal', 'ui', banks(0) + [28, 29]),
    ('graphics/bag/menu_pyramid.pal', 'ui', banks(0)),
    # Pokéblock case: backdrop and frames. 12-14 of every bank are the Pokéblock colour swatches (kept)
    ('graphics/pokeblock/menu.pal', 'ui', [1, 2, 3, 5, 7, 8]),
    # condition screen (also StarNAV condition): header and panels. graph.png 6-15 are the contest
    # colour circles, which the striped backdrop shares, so they stay vanilla.
    ('graphics/pokeblock/use_screen/mon_frame_pal.bin', 'ui', ALL),
    ('graphics/pokeblock/use_screen/graph.png', 'ui', [3, 4]),
    ('graphics/pokeblock/use_screen/condition.png', 'ui', [8, 9, 10, 11]),
  ],
  '4_pokedex': [
    # 6 BG palettes, bank 0 doubles as the dex sprite palette. Text uses slots 2, 3 and 15 (greys, kept by tx).
    ('graphics/pokedex/bg_hoenn.pal', 'ui', banks(0, 1, 2, 3, 4, 5)),
    ('graphics/pokedex/bg_national.pal', 'ui', banks(0, 1, 2, 3, 4, 5)),
    ('graphics/pokedex/search_results_bg.pal', 'ui', banks(0, 1, 2, 3, 4, 5)),
    ('graphics/pokedex/search_menu.pal', 'ui', banks(0, 1, 2, 3)),
    ('graphics/pokedex/cry_screen_bg.png', 'ui', ALL),
    ('graphics/pokedex/cry_meter.png', 'ui', ALL),
    ('graphics/pokedex/cry_meter_needle.png', 'ui', ALL),
    ('graphics/pokedex/area_unknown.png', 'ui', ALL),
    ('src/pokedex.c', 'ui', ['color = RGB(18, 28, 0);', 'color = RGB(15, 21, 0);']),   # cry play arrow
  ],
  '5_starnav': [
    ('graphics/pokenav/header.png', 'ui', ALL),            # top bar
    ('graphics/pokenav/message.png', 'ui', ALL),           # bottom help box
    ('graphics/pokenav/bg_dots.png', 'ui', ALL),           # dotted backdrop (all menu tints)
    ('graphics/pokenav/list_arrows.png', 'ui', ALL),
    # option bars: 4-6 are the bar fill shared by every option; 8-11 are each option's colour square,
    # which doubles as the Cool/Beauty/Cute/Smart/Tough colour, so they stay vanilla
    ('graphics/pokenav/options/options.pal', 'ui', [4, 5, 6, 20, 21, 22, 36, 37, 38, 52, 53, 54, 68, 69, 70]),
    # left headers: banks 0-4 stay vanilla for the contest-category headers; Dune copies go in 5-9 and the
    # menu headers (main, Hoenn map, condition, party, search, ribbons, match call) point at them
    ('graphics/pokenav/left_headers/palette.pal', 'ui', Append(0, 1, 2, 3, 4)),
    # condition graph (shares its striped backdrop colours with the contest circles, see pokeblock graph)
    ('graphics/pokenav/condition/graph.png', 'ui', [3, 4]),
    # condition search results, Match Call and ribbon lists: backdrops and frames; the list window
    # palettes only change their fill (slot 1), their text and gender colours stay
    ('graphics/pokenav/condition/search_results.png', 'ui', ALL),
    ('graphics/pokenav/condition/search_results_list.pal', 'ui', [1]),
    ('graphics/pokenav/match_call/ui.png', 'ui', ALL),
    ('graphics/pokenav/match_call/window.png', 'ui', ALL),
    ('graphics/pokenav/match_call/list_window.pal', 'ui', [1]),
    ('graphics/pokenav/match_call/options_cursor.png', 'ui', ALL),
    ('graphics/pokenav/ribbons/list_bg.png', 'ui', ALL),
    ('graphics/pokenav/ribbons/list_ui.pal', 'ui', [1]),
    ('graphics/pokenav/ribbons/mon_info.pal', 'ui', [1]),
    ('graphics/pokenav/ribbons/summary_bg.png', 'ui', ALL),
    ('src/pokenav_main_menu.c', 'ui', Replace(
        ('    [POKENAV_GFX_MAIN_MENU] = {\n        .data = gPokenavLeftHeaderMainMenu_Gfx,\n        .size = 0x20,\n        .tag = 3\n',
         '    [POKENAV_GFX_MAIN_MENU] = {\n        .data = gPokenavLeftHeaderMainMenu_Gfx,\n        .size = 0x20,\n        .tag = 8\n'),
        ('    [POKENAV_GFX_CONDITION_MENU] = {\n        .data = gPokenavLeftHeaderCondition_Gfx,\n        .size = 0x20,\n        .tag = 1\n',
         '    [POKENAV_GFX_CONDITION_MENU] = {\n        .data = gPokenavLeftHeaderCondition_Gfx,\n        .size = 0x20,\n        .tag = 6\n'),
        ('    [POKENAV_GFX_RIBBONS_MENU] = {\n        .data = gPokenavLeftHeaderRibbons_Gfx,\n        .size = 0x20,\n        .tag = 2\n',
         '    [POKENAV_GFX_RIBBONS_MENU] = {\n        .data = gPokenavLeftHeaderRibbons_Gfx,\n        .size = 0x20,\n        .tag = 7\n'),
        ('    [POKENAV_GFX_MATCH_CALL_MENU] = {\n        .data = gPokenavLeftHeaderMatchCall_Gfx,\n        .size = 0x20,\n        .tag = 4\n',
         '    [POKENAV_GFX_MATCH_CALL_MENU] = {\n        .data = gPokenavLeftHeaderMatchCall_Gfx,\n        .size = 0x20,\n        .tag = 9\n'),
        ('    [POKENAV_GFX_MAP_MENU_ZOOMED_OUT] = {\n        .data = gPokenavLeftHeaderHoennMap_Gfx,\n        .size = 0x20,\n        .tag = 0\n',
         '    [POKENAV_GFX_MAP_MENU_ZOOMED_OUT] = {\n        .data = gPokenavLeftHeaderHoennMap_Gfx,\n        .size = 0x20,\n        .tag = 5\n'),
        ('    [POKENAV_GFX_MAP_MENU_ZOOMED_IN] = {\n        .data = gPokenavLeftHeaderHoennMap_Gfx,\n        .size = 0x40,\n        .tag = 0\n',
         '    [POKENAV_GFX_MAP_MENU_ZOOMED_IN] = {\n        .data = gPokenavLeftHeaderHoennMap_Gfx,\n        .size = 0x40,\n        .tag = 5\n'),
        ('    [POKENAV_GFX_PARTY_MENU - POKENAV_GFX_SUBMENUS_START] = {\n        .data = gPokenavLeftHeaderParty_Gfx,\n        .tag = 1\n',
         '    [POKENAV_GFX_PARTY_MENU - POKENAV_GFX_SUBMENUS_START] = {\n        .data = gPokenavLeftHeaderParty_Gfx,\n        .tag = 6\n'),
        ('    [POKENAV_GFX_SEARCH_MENU - POKENAV_GFX_SUBMENUS_START] = {\n        .data = gPokenavLeftHeaderSearch_Gfx,\n        .tag = 1\n',
         '    [POKENAV_GFX_SEARCH_MENU - POKENAV_GFX_SUBMENUS_START] = {\n        .data = gPokenavLeftHeaderSearch_Gfx,\n        .tag = 6\n'),
    )),
  ],
  '6_pc_storage': [
    # box screen chrome: data panel, scrolling backdrop and buttons, party tray, box-choice popup,
    # waveform. Wallpapers, box title colours (tied to the wallpaper), hand cursor and text stay vanilla.
    ('graphics/pokemon_storage/interface.pal', 'ui', ALL),
    ('graphics/pokemon_storage/pkmn_data_gray.pal', 'ui', ALL),
    ('graphics/pokemon_storage/scrolling_bg.pal', 'ui', ALL),
    ('graphics/pokemon_storage/scrolling_bg_move_items.pal', 'ui', ALL),
    ('graphics/pokemon_storage/party_menu.pal', 'ui', ALL),
    ('graphics/pokemon_storage/box_selection_popup.pal', 'ui', ALL),
    ('graphics/pokemon_storage/waveform.png', 'ui', ALL),
  ],
  '7_battle_naming': [
    # battle message box (also egg hatch and trade): teal fill and red border go grey, never brown.
    # 1-10 are text colours of the battle windows (kept). Bank 1 is the action / move menu frame.
    ('graphics/battle_interface/textbox_0.pal', 'battle', rng(11, 15)),
    ('graphics/battle_interface/textbox_1.pal', 'battle', ALL),
    # naming screen: header bar is the backdrop (menu.pal slot 0), striped bg, page frames, buttons,
    # cursor. keyboard.pal 1-9 are text and gender colours (kept), 13-15 are the three keyboard fills.
    ('graphics/naming_screen/menu.pal', 'naming', [0] + ALL),
    ('graphics/naming_screen/page_swap_upper.pal', 'naming', rng(11, 15)),
    ('graphics/naming_screen/page_swap_lower.pal', 'naming', rng(11, 15)),
    ('graphics/naming_screen/page_swap_others.pal', 'naming', rng(11, 15)),
    ('graphics/naming_screen/buttons.pal', 'naming', ALL),
    ('graphics/naming_screen/cursor.pal', 'naming', [1, 2, 3]),
    ('graphics/naming_screen/keyboard.pal', 'naming', [13, 14, 15]),
  ],
  '8_card_shop': [
    # trainer card: the card colour marks the star rank (0 green, 1 bronze, 2 copper, 3 silver, 4 gold).
    # The two green-hued tiers go Dune (green -> sand, bronze -> taupe) and stay distinct; copper, silver and
    # gold already fit and keep their faces. Every tier gets the steel header label (0:7-8, 0:13) and steel
    # backdrop stripes (1:12-13). The pink female backdrop stays (a gender colour). Bank 2 and the card
    # text windows (banks 8, 15) are not touched.
    ('graphics/trainer_card/green.pal', 'ui', ALL + [28, 29]),
    ('graphics/trainer_card/bronze.pal', 'ui', ALL + [28, 29]),
    *[(f'graphics/trainer_card/{t}.pal', 'ui', [7, 8, 13, 28, 29]) for t in ('copper', 'silver', 'gold')],
    # shop: buy-list panel (stripes, frame) and the MONEY label
    ('graphics/shop/menu.png', 'ui', ALL),
  ],
  '8b_easychat_frontier': [
    # Easy Chat: backdrop/window (mode), the orange phrase frame, the green keyboard frame with its SELECT /
    # B-button labels, the button window sprite, cursors and scroll arrows. text.pal and title_text.pal are
    # text colours (the green word dashes and cyan title stay vanilla).
    ('graphics/easy_chat/mode.png', 'ui', ALL),
    ('graphics/easy_chat/text_input_frame_orange.pal', 'ui', ALL),
    ('graphics/easy_chat/text_input_frame_green.pal', 'ui', ALL),
    ('graphics/easy_chat/button_window.png', 'ui', ALL),
    ('graphics/easy_chat/rectangle_cursor.png', 'ui', ALL),
    ('graphics/easy_chat/triangle_cursor.png', 'ui', ALL),
    # Frontier Pass: bank 0 is the frame, header bar, plaques and red arrow; banks 1-5 are the small trainer
    # card by star rank (same rule as the trainer card); 6-7 are the Battle Frontier map (kept). Text windows
    # use bank 15 (the text window palette). Medals and player heads stay.
    ('graphics/frontier_pass/bg.png', 'ui', ALL + [16 + i for i in ALL] + [32 + i for i in ALL]
                                            + [16 * b + i for b in (3, 4, 5) for i in (7, 8, 13)]),
    ('graphics/frontier_pass/cursor.png', 'ui', ALL),
    ('graphics/frontier_pass/map_cursor.png', 'ui', ALL),
  ],
  '8c_berry_clock': [
    # berry tag: bank 0 is the panel and the flavour circle sprite (red -> gold); bank 4 slots 12-13 are the
    # blue backdrop stripes. Banks 1-3 (berry colour gradients) and the pink female stripes (bank 5) stay.
    ('graphics/bag/check_berry.pal', 'ui', ALL + [76, 77]),
    # berry blender: machine body, frame and the four player arrows (the red gems, one shared palette).
    # Particles, score symbols and the player-name text stay.
    ('graphics/berry_blender/center.png', 'ui', ALL),
    ('graphics/berry_blender/outer.png', 'ui', ALL),
    ('graphics/berry_blender/arrow.png', 'ui', ALL),
    # wall clock: only the teal backdrop (slot 9) and the matching prompt fill; the blue / pink face is the
    # player's gender colour and stays
    ('graphics/wallclock/male.pal', 'ui', [9]),
    ('graphics/wallclock/female.pal', 'ui', [9]),
    ('graphics/wallclock/text_prompt.pal', 'ui', [1]),
  ],
  '8d_contest': [
    # contest appeal screen: the four contestant panels (banks 5-7 rivals, 8 the player: slots 1-4 are the
    # fill and edge) and the blue move window (bank 0 slots 10, 13, 14). The hearts and applause meter,
    # the category label, the audience and the text colours stay vanilla.
    ('graphics/contest/interface.png', 'ui', [16 * b + i for b in (5, 6, 7, 8) for i in (1, 2, 3, 4)] + [10, 13, 14]),
  ],
}
DONE = ['1_text_windows', '2_party_summary', '3_bag_pokeblock', '4_pokedex', '5_starnav', '6_pc_storage', '7_battle_naming', '8_card_shop', '8b_easychat_frontier', '8c_berry_clock', '8d_contest']

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

def read_bin_pal(data):   # raw little-endian BGR555, as INCBIN'd palettes
    return [(((v) & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3)
            for v in struct.unpack('<%dH' % (len(data) // 2), data)]

def write_bin_pal(data, cols):
    old = struct.unpack('<%dH' % (len(data) // 2), data)
    return struct.pack('<%dH' % len(old), *[(o & 0x8000) | (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
                                             for o, (r, g, b) in zip(old, cols)])

def render_append(path, fam, spec):
    data = vanilla(path); cols = read_pal(data)
    new = cols + [tuple(tx(c, fam)) if 0 < i % 16 and c not in MAGENTA else c
                  for b in spec.banks for i, c in enumerate(cols[16 * b:16 * b + 16])]
    lines = data.decode().replace('\r\n', '\n').split('\n')
    head, n = lines[:2], len(new)
    body = ['%d %d %d' % c for c in new]
    return '\r\n'.join(head + [str(n)] + body + ['']).encode(), cols, new

def render(path, fam, idx):
    if isinstance(idx, Append): return render_append(path, fam, idx)
    data = vanilla(path)
    kind = path.rsplit('.', 1)[1]
    cols = {'png': read_png_pal, 'pal': read_pal, 'bin': read_bin_pal}[kind](data)
    # magenta slots are unused placeholders in vanilla files: leave them alone
    new = [tuple(tx(c, fam)) if i in idx and c not in MAGENTA else c for i, c in enumerate(cols)]
    return {'png': write_png_pal, 'pal': write_pal, 'bin': write_bin_pal}[kind](data, new), cols, new

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    bad = 0
    for fam_name in DONE if mode != '--list' else FAMILIES:
        for path, fam, idx in FAMILIES[fam_name]:
            dst = REPO / 'game' / path
            if isinstance(idx, Replace):
                text = vanilla(path).decode()
                for a, b in idx.pairs:
                    assert text.count(a) == 1, (path, a)
                    text = text.replace(a, b)
                out = text.encode(); old = new = []
                if mode == '--list':
                    print(f'{fam_name:18} {path:48} edits: ' + '; '.join(f'{a!r} -> {b!r}' for a, b in idx.pairs)); continue
            elif path.endswith('.c'):
                out = render_c(path, fam, idx); old = new = []
                if mode == '--list':
                    print(f'{fam_name:18} {path:48} C colours: ' + '; '.join(
                        f'{s} -> {RGB_RE.sub(lambda m: tx_rgb5(m, fam), s)}' for s in idx)); continue
            else:
                out, old, new = render(path, fam, idx)
            changed = [i for i in range(len(new)) if i >= len(old) or old[i] != new[i]]
            if mode == '--list':
                print(f'{fam_name:18} {path:48} {len(changed):2} colours  ' +
                      ' '.join('%d:%02x%02x%02x>%02x%02x%02x' % (i, *(old[i] if i < len(old) else (0, 0, 0)), *new[i]) for i in changed))
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

"""Build the v1 / mockup / v2 comparison page (one self-contained HTML file with the shots inlined).

    python3 gallery.py OUT.html

Rows are every screen that has an after-shot in after/v2; v1 comes from reference/v1, the mockup from
mockups/dune_v1. Screens grouped by the apply.py family that themes them.
"""
import base64, html, pathlib, re, sys
HERE = pathlib.Path(__file__).resolve().parent

GROUPS = [
    ('Text windows, start menu, options', r'^(00|01|05|06|4[23])'),
    ('Party and summary', r'^1[0-9]'),
    ('Pokédex', r'^2[0-9]'),
    ('Bag', r'^3[0-9]'),
    ('Trainer card', r'^4[01]'),
    ('StarNAV', r'^5[0-9]'),
    ('Pokéblock', r'^6[0-9]'),
    ('PC storage', r'^(8[0-9]|9[01])'),
    ('Shop and Easy Chat', r'^9[2-8]'),
    ('Battle', r'^b(0|1[01]|1[5-9]|2)'),
    ('Naming screen', r'^b1[2-4]'),
    ('Game Corner', r'^h0'),
    ('Frontier Pass and Battle Factory', r'^(h1[01]|h3[4-6])'),
    ('Berry Blender, berry tag, wall clock', r'^(h1[4-8]|h29)'),
    ('Contests', r'^h(19|2[0-8])'),
]

def uri(p):
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode() if p.exists() else ''

def label(name):
    return re.sub(r'^[0-9a-z]{2,3}_', '', name).replace('_', ' ')

def main(out):
    names = sorted(p.stem for p in (HERE / 'after/v2').glob('*.png'))
    used, sections, nav = set(), [], []
    for i, (title, pat) in enumerate(GROUPS):
        rows = [n for n in names if re.match(pat, n) and n not in used]
        if not rows: continue
        used.update(rows)
        sid = f'g{i}'
        nav.append(f'<a href="#{sid}">{html.escape(title)} <span>{len(rows)}</span></a>')
        body = []
        for n in rows:
            cells = []
            for kind, d in (('v1', 'reference/v1'), ('mockup', 'mockups/dune_v1'), ('v2', 'after/v2')):
                src = uri(HERE / d / f'{n}.png')
                cells.append(f'<figure><img src="{src}" alt="{kind} {html.escape(label(n))}" width="240" height="160" loading="lazy"><figcaption>{kind}</figcaption></figure>'
                             if src else f'<figure class="none"><div>no {kind} shot</div><figcaption>{kind}</figcaption></figure>')
            body.append(f'<article><h3><code>{html.escape(n.split("_")[0])}</code> {html.escape(label(n))}</h3><div class="trio">{"".join(cells)}</div></article>')
        sections.append(f'<section id="{sid}"><h2>{html.escape(title)}</h2>{"".join(body)}</section>')
    tpl = (HERE / 'gallery_template.html').read_text()
    page = tpl.replace('{{NAV}}', ''.join(nav)).replace('{{SECTIONS}}', ''.join(sections)).replace('{{COUNT}}', str(len(used)))
    pathlib.Path(out).write_text(page)
    left = [n for n in names if n not in used]
    print(f'{len(used)} screens written to {out}' + (f'; ungrouped: {left}' if left else ''))

if __name__ == '__main__':
    main(sys.argv[1])

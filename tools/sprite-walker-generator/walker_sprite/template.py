"""Template humans for batch walker drafting. Writes art/<name>.yaml for the walker tool."""
import sys, yaml
HEAD = {
 'down': [".....KKKKKK.....","...KKhhhbbbKK...","..KhhbbbbbbbdK..",".KhbbbbbbbbbbdK.",".KbbSbbbbbbSbdK.",
          ".KbSSSSSSSSSSdK.",".KdSKSSSSSSKSdK.",".KdsKsSSSSsKtdK.","..KtssSSSSsstK..","...KKKttttKKK..."],
 'up':   [".....KKKKKK.....","...KKhhhbbbKK...","..KhhbbbbbbbdK..",".KhbbbbbbbbbbdK.",".KbbbbbbbbbbbdK.",
          ".KbhbbbbbbbbbdK.",".KdbbbbbbbbbddK.",".KddbbbbbbbbddK.","..KddbbbbbbddK..","...KKKttttKKK..."],
 'left': ["......KKKKK.....","....KKhhhbbKK...","...KhhbbbbbbbdK.","..KhbbbbbbbbbdK.","..KbSSbbbbbbbdK.",
          ".KSSSSSSbbbbbdK.",".KSKSSSSbhbbdK..",".KSKSSStbbbddK..","..KtsstKddddK...","...KKttKKKK....."],
}
TORSO = {  # shoulders, chest (repeatable), belly, hands, hips
 'down': ["...KAAAAAAAaK...","..KAKAAAAAAKaK..","..KAKAAAAAaKcK..","..KSKAAAAAaKSK..","..KtKPPPPPpKtK.."],
 'up':   ["...KAAAAAAAaK...","..KAKAAAAAAKaK..","..KAKAAAAAaKcK..","..KSKAAAAAaKSK..","..KtKPPPPPpKtK.."],
 'left': ["....KAAAAaK.....","....KAKAAaK.....","....KAKAAaK.....","....KSKAAcK.....","....KtKPPpK....."],
}
LEGS = {
 'down': ["...KPPPKKPPpK...","...KPpK..KPpK...","...KooK..KooK...","...KKKK..KKKK..."],
 'up':   ["...KPPPKKPPpK...","...KPpK..KPpK...","...KooK..KooK...","...KKKK..KKKK..."],
 'left': ["....KPPPPpK.....","....KPpKPpK.....","....KooKooK.....","....KKKKKKK....."],
}
STEP = {
 'down_a': ('down', ["...KPpK..KooK...","...KooK..KKKK...","...KKKK........."]),
 'down_b': ('down', ["...KooK..KPpK...","...KKKK..KooK...",".........KKKK..."]),
 'up_a':   ('up',   ["...KPpK..KooK...","...KooK..KKKK...","...KKKK........."]),
 'up_b':   ('up',   ["...KooK..KPpK...","...KKKK..KooK...",".........KKKK..."]),
 'left_a': ('left', ["...KPpK.KPpK....","..KooK...KooK...","..KKKK...KKKK..."]),
 'left_b': ('left', ["....KPpPpK......","....KoooK.......","....KKKKK......."]),
}
def frame(d, adult):
    h, t, l = HEAD[d], TORSO[d], LEGS[d]
    torso = t[:2] + ([t[1]] if adult else []) + t[2:]
    legs = l[:2] + ([l[1]] if adult else []) + l[2:]
    return h + torso + legs + ["." * 16]
def build(c):
    frames = {}
    for d in ('down', 'up', 'left'):
        rows = frame(d, c.get('adult', False))
        top = 32 - len(rows)
        for y, r in c.get('edit', {}).get(d, {}).items():
            rows[y - top] = r
        for r in rows: assert len(r) == 16, (c['name'], d, r)
        frames[d] = rows
    for s, (b, rows) in STEP.items():
        rows = c.get('step', {}).get(s, rows)
        frames[s] = {'base': b, 'shift': 1, 'patch_y': 29, 'rows': rows}
    for f in frames.values():
        rs = f if isinstance(f, list) else f['rows']
        used = set(''.join(rs)) - {'.'}
        assert used <= set(c['legend']), (c['name'], used - set(c['legend']))
    out = f"name: {c['name']}\ndescription: \"{c['desc']}\"\nkit: person16x32\nreplaces: {c['replaces']}\n" \
          f"graphics_info: {c['gi']}\n# {c['note']}\npalette: {c['pal']}\npalette_tag: OBJ_EVENT_PAL_TAG_{c['pal'].upper()}\n\nlegend:\n"
    out += "".join(f"  \"{k}\": {v}\n" for k, v in c['legend'].items())
    out += "\nframes:\n"
    for k, f in frames.items():
        if isinstance(f, list):
            out += f"  {k}: |\n" + "".join(f"    {r}\n" for r in f)
        else:
            out += f"  {k}:\n    base: {f['base']}\n    shift: 1\n    patch_y: {f['patch_y']}\n    rows: |\n" + "".join(f"      {r}\n" for r in f['rows'])
    open(f"art/{c['name']}.yaml", "w").write(out)

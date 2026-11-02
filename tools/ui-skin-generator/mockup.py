"""Phase 2 UI-skin mockup: recolours the v1 reference screenshots into the Dune theme.
Run: python3 mockup.py   (from tools/ui-skin-generator). Pixels only; the game source is untouched.
Rules: greys/text kept; greens -> sand (light) or rust (mid); dark chrome -> dark steel; blues/purples -> steel;
saturated red -> gold; HP greens kept in party/battle/PC; battle message box -> grey; creatures, maps, box
wallpapers and the overworld are protected by per-screen rectangles."""
import colorsys, os, re, sys
from PIL import Image
import pathlib; HERE=pathlib.Path(__file__).parent; SRC=str(HERE/'reference/v1'); OUT=str(HERE/'mockups/dune_v1')
os.makedirs(OUT, exist_ok=True)
SAND, RUST, STEEL, GOLD = 0.09, 0.06, 0.58, 0.12
def g(v): return int(round(v*255/8)*8)
def hls(h,l,s): return tuple(g(v) for v in colorsys.hls_to_rgb(h,l,s))
def tx(rgb, fam):
    r,g_,b=[v/255 for v in rgb]; h,l,s=colorsys.rgb_to_hls(r,g_,b)
    if s<0.16: return rgb                                  # text, shadows, whites: keep
    if fam=='battle' and 0.44<=h<=0.56 and l<0.75: return hls(0.60,l,0.06)   # battle message box: grey
    if fam=='battle' and (h<0.05 or h>0.93) and s>0.5 and 0.35<l<0.65: return hls(0.60,l*0.75,0.08)  # its red border: dark grey
    if fam in('party','battle','pc','levelup') and 0.30<=h<=0.42 and s>0.45 and 0.4<l<0.75: return hls(0.36,l,s*0.75)  # HP green stays
    if l<0.30 and s>=0.16: return hls(STEEL, l, 0.18)                           # dark chrome -> dark steel
    if fam=='naming' and 0.22<=h<=0.52: return hls(STEEL, l, min(s*0.35,0.4))
    if 0.22<=h<=0.52:  return hls(SAND if l>0.6 else RUST, l, min(s*0.55,0.5))   # greens -> sand / rust
    if h<0.045 or h>0.93:
        if s>0.55 and l>0.35: return hls(GOLD, min(l+0.05,0.8), 0.85)             # saturated red -> gold
        return hls(RUST, l, min(s,0.5))
    if 0.52<h<=0.78: return hls(STEEL, l, min(s*0.35,0.4))                        # blues -> steel
    if 0.78<h<=0.93: return hls(STEEL, l, min(s*0.35,0.4))                        # purples -> steel
    if 0.045<=h<0.22: return hls(GOLD if s>0.6 else SAND, l, min(s*0.9,0.85))     # yellows/oranges -> gold/sand
    return hls(SAND,l,s*0.32)
# per-screen regions: ONLY = transform only inside; PROTECT = never touch
BOT=(0,112,240,160)
R={}
def rule(pat, only=None, protect=None, fam='ui'):
    R[re.compile(pat)]=(only or [], protect or [], fam)
rule(r'^00', fam='ui')
rule(r'^01', only=[(168,0,240,160)])
rule(r'^(05|06|80|h05)', only=[BOT,(0,0,90,24)])
rule(r'^25', only=[(168,0,240,160)])
rule(r'^43', only=[BOT,(0,0,120,112)])
rule(r'^(1[2-6]_|19g|h36)', protect=[(4,18,60,74)])
rule(r'^(1[0-9]_|b06|b07|h22)', protect=[(4,14,46,56),(90,0,126,160)], fam='party')
rule(r'^19[b-f]', protect=[(4,14,46,56),(90,0,126,160)], fam='levelup')
rule(r'^20', protect=[(56,28,122,110)])
rule(r'^21', protect=[(6,22,74,90)])
rule(r'^22', protect=[(0,16,240,128)])
rule(r'^23', protect=[(6,22,58,74)])
rule(r'^3[0-6]|^b08|^b09', protect=[(2,62,42,94)])
rule(r'^4[01]', protect=[(150,52,236,124)])
rule(r'^5[12]', protect=[(0,16,240,144)])
rule(r'^55_', protect=[(6,52,80,124)])
rule(r'^57[bc]', protect=[(8,112,44,150)])
rule(r'^59', protect=[(10,76,80,148)])
rule(r'^6[36]', protect=[(6,36,76,108)])
rule(r'^6[45]', protect=[(72,52,128,116)])
rule(r'^70', only=[(120,126,240,160),(0,144,240,160)])
rule(r'^72', only=[(0,0,116,26)])
rule(r'^81', only=[BOT,(0,0,104,60)])
rule(r'^82', only=[BOT,(0,0,116,90)])
rule(r'^(83|86|89)', protect=[(4,18,72,74),(88,24,240,160)], fam='pc')
rule(r'^84', protect=[(4,18,72,74),(88,24,160,160)], fam='pc')
rule(r'^85', protect=[(4,18,72,74),(88,24,172,160)], fam='pc')
rule(r'^87', protect=[(4,18,72,74),(98,30,140,160)], fam='pc')
rule(r'^90', only=[BOT,(0,0,100,60)])
rule(r'^91', only=[(120,0,240,160),(0,0,80,30),(0,96,120,160)], protect=[(8,56,42,92)])
rule(r'^92', only=[(120,0,240,160),(0,0,80,30),(0,96,120,160)], protect=[(8,56,42,92)])
rule(r'^9[345]', only=[(120,0,240,160),(0,0,80,30),(0,96,120,160)], protect=[(8,56,42,92)])
rule(r'^b(0[1-57]|1[0167]|2[01])', only=[BOT,(12,10,124,40),(124,66,240,106)], fam='battle')
rule(r'^b(19|22|23)', only=[BOT,(124,66,240,106)], fam='battle')
rule(r'^b18', only=[BOT], fam='battle')
rule(r'^b1[2-4]', protect=[(52,34,72,54)], fam='naming')
rule(r'^h0[1-4]', protect=[(36,36,152,116)])
rule(r'^h0[678]', protect=[(0,16,132,160),(136,58,240,160)])
rule(r'^h10', protect=[(118,22,240,98)])
rule(r'^h11', protect=[(0,16,152,122)])
rule(r'^h13', protect=[(60,8,182,100)])
rule(r'^h18', protect=[(34,46,78,82)])
rule(r'^h(19|20|21|30|31|32|33)', only=[BOT,(0,0,120,112)])
rule(r'^h2[3567]', only=[BOT,(160,0,240,112)])
rule(r'^h2[48]', protect=[(0,20,60,112)])
rule(r'^h29', protect=[(40,16,200,144)])
rule(r'^h3[45]', protect=[(4,18,72,84)])
# Type and contest-category label chips keep their vanilla colours (owner's call), on top of each screen's rule.
def _pal(path):
    L=open(path).read().split()[3:]; return [tuple(int(v) for v in L[i:i+3]) for i in range(0,48,3)]
CHIPCOL={tuple(v>>3 for v in c) for n in (1,2,3) for c in _pal(HERE/f'../../game/graphics/types/move_types_{n}.pal')}
def chip_px(c): return tuple(v>>3 for v in c) in CHIPCOL
CHIPS=[(re.compile(r'^12_'),[(118,48,194,62)]),
       (re.compile(r'^(1[3-6]_|19g|h36)'),[(64,32,100,96)])]
def inside(x,y,rs): return any(x0<=x<x1 and y0<=y<y1 for x0,y0,x1,y1 in rs)
def run(f):
    only,protect,fam,chips=[],[],'ui',[]
    for p,(o,pr,fm) in R.items():
        if p.match(f): only,protect,fam=o,pr,fm; break
    for p,rs in CHIPS:
        if p.match(f): chips=rs
    im=Image.open(f'{SRC}/{f}').convert('RGB'); px=im.load(); cache={}
    for y in range(im.height):
        for x in range(im.width):
            if protect and inside(x,y,protect): continue
            if only and not inside(x,y,only): continue
            if chips and inside(x,y,chips) and chip_px(px[x,y]): continue
            c=px[x,y]; k=(c,fam)
            if k not in cache: cache[k]=tx(c,fam)
            px[x,y]=cache[k]
    im.save(f'{OUT}/{f}')
files=sorted(f for f in os.listdir(SRC) if f.endswith('.png'))
for f in files: run(f)
print(len(files))

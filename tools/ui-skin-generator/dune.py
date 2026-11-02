"""Dune theme colour rule, shared by mockup.py (screenshots) and apply.py (game palettes).
tx(rgb, fam) -> rgb. fam picks screen-family exceptions (battle box grey, HP greens kept, naming steel)."""
import colorsys
SAND, RUST, STEEL, GOLD = 0.09, 0.06, 0.58, 0.12
def g(v): return min(int(round(v*255/8)*8), 248)
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

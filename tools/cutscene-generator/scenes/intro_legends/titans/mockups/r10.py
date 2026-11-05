import sys; sys.path.insert(0,'/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans')
import titan_gen as t
from concurrent.futures import ThreadPoolExecutor
S='/tmp/claude-0/-home-user/d213e348-4be7-55cb-95dd-5b2b404be070/scratchpad/r5/'
t.cc.CHECKPOINTS['sdxl']='urn:air:sdxl:checkpoint:civitai:112902@126688'  # DreamShaper XL alpha2
STYLE='bold cel-shaded creature illustration, thick clean black ink outlines, 3 flat shading tones with a strong light from the upper left, simple strong graphic shapes, exaggerated readable silhouette, video game key art, plain white background, '
NEG='photo, photorealistic, 3d render, gradient shading, fine texture, noise, tiny details, scenery, landscape, ground, text, watermark, multiple creatures, people'
P={'krayt':'colossal greater krayt dragon rearing up and roaring, broad flat shovel-shaped head, huge open jaws with rows of white fangs, small dark eye, horn crest, spiky ridge down the neck, curled tail, dark sandy brown, backlit',
   'sando':'colossal sando aqua monster lunging at the viewer, huge wide grinning mouth full of white teeth, small fierce eyes, thick webbed clawed arms spread, long tail curling up with a fin, grey-brown wrinkled hide',
   'exogorth':'colossal space slug worm rearing up, enormous round gaping mouth lined with long white fangs, dark red throat, thick ringed body, pale pink-grey'}
jobs=[(sp,d) for sp in P for d in (0.5,0.65,0.8)]
def run(j):
    sp,d=j; return t.i2i_xl(sp,S+f'init_{sp if sp!="exogorth" else "exo"}.png',STYLE+P[sp],NEG,denoise=d,n=2,tag='ill',lora=None,cfg=6)
with ThreadPoolExecutor(9) as ex: list(ex.map(run,jobs))

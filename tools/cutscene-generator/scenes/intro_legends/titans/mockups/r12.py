import sys; sys.path.insert(0,'/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans')
import titan_gen as t
from concurrent.futures import ThreadPoolExecutor
S='/tmp/claude-0/-home-user/d213e348-4be7-55cb-95dd-5b2b404be070/scratchpad/r5/'
t.cc.CHECKPOINTS['sdxl']='urn:air:sdxl:checkpoint:civitai:112902@126688'
STYLE='official monster art in the style of Ken Sugimori, anime cel shading, flat colors, 2-tone shading, clean thick dark outlines, simple bold readable shapes, no texture, white background, '
NEG='photo, realistic, 3d render, painterly, gradient, texture, noise, fur detail, scales detail, scenery, landscape, ground, text, watermark, multiple creatures, people'
P={'krayt':'colossal krayt dragon rearing up and roaring, broad flat head with a horn crest, wide open jaws with big white fangs, glowing yellow eye, row of bone-white spikes down the neck and back, curled tail, dark umber brown body with warm tan belly',
   'sando':'colossal sea monster lunging at the viewer, huge wide grinning mouth with red gums and big white teeth, yellow eyes, thick webbed claws spread, long tail curling up with a fin, olive grey-green body with cream belly',
   'exogorth':'colossal space slug worm rearing up, enormous round gaping mouth with pink-red gums and long white fangs, black throat, thick ringed body, pale grey-violet body'}
jobs=[(sp,d) for sp in P for d in (0.6,0.72)]
def run(j):
    sp,d=j; return t.i2i_xl(sp,S+f'init_{sp if sp!="exogorth" else "exo"}.png',STYLE+P[sp],NEG,denoise=d,n=2,tag='sug',lora=None,cfg=6)
with ThreadPoolExecutor(6) as ex: list(ex.map(run,jobs))

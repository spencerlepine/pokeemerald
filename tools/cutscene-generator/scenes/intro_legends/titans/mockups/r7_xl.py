import sys; sys.path.insert(0,'/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans')
import titan_gen as t
from concurrent.futures import ThreadPoolExecutor
S='/tmp/claude-0/-home-user/d213e348-4be7-55cb-95dd-5b2b404be070/scratchpad/r7/'
L='urn:air:sdxl:lora:civitai:579244@646044'
NEG='blurry, smooth gradient, photo, realistic, 3d render, noise, dithering, tiny details, text, watermark, background scenery, multiple creatures'
P={'krayt':'giant krayt dragon rearing up, long neck, wide open jaws with a row of white fangs, small yellow eye, ridged back spikes, curled tail, sandy brown',
   'sando':'giant sea monster lunging forward, wide grinning mouth full of white teeth, glowing eyes, webbed claws, long finned tail, grey-brown',
   'exogorth':'giant space slug worm rearing up, enormous open round mouth lined with white fangs, dark red throat, ringed wrinkled pink-grey body'}
jobs=[(sp,d) for sp in P for d in (0.35,0.5)]
def run(j):
    sp,d=j
    return t.i2i_xl(sp,S+f'init_{sp}.png','pixelart, pixel art, sprite, chunky big pixels, low detail, clean cel shading, 5 colours, bold black outline, '+P[sp]+', white background',NEG,denoise=d,n=2,tag='form',lora=L)
with ThreadPoolExecutor(6) as ex: list(ex.map(run,jobs))

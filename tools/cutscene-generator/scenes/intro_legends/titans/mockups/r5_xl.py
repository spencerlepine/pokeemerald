import sys; sys.path.insert(0,'/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans')
import titan_gen as t
from concurrent.futures import ThreadPoolExecutor
S='/tmp/claude-0/-home-user/d213e348-4be7-55cb-95dd-5b2b404be070/scratchpad/r5/'
NEG='blurry, smooth, photo, realistic, 3d render, gradient, noise, dithering, text, watermark, background scenery, ground, multiple creatures'
J=[('krayt','init_krayt.png','pixel art, 16-bit game sprite, giant krayt dragon rearing up, long neck, huge open toothy jaws, ridged spiky hide, curled tail, dark sandy brown, bold dark outline, flat cel shading, limited palette, white background'),
   ('sando','init_sando.png','pixel art, 16-bit game sprite, giant sea monster swimming toward the viewer, wide grinning toothy mouth, webbed clawed limbs, long tail with fin, grey-brown hide, bold dark outline, flat cel shading, limited palette, white background'),
   ('exogorth','init_exo.png','pixel art, 16-bit game sprite, giant space slug worm rising up, huge open mouth lined with rows of sharp teeth, wrinkled ringed pinkish-grey skin, bold dark outline, flat cel shading, limited palette, white background')]
L={'spr':'urn:air:sdxl:lora:civitai:579244@646044','sty':'urn:air:sdxl:lora:civitai:127929@140013'}
jobs=[(sp,S+i,'pixelart, sprite, '+p,0.6,k) for sp,i,p in J for k in L]
with ThreadPoolExecutor(6) as ex: list(ex.map(lambda j: t.i2i_xl(j[0],j[1],j[2],NEG,denoise=j[3],n=2,tag=j[4],lora=L[j[4]]),jobs))

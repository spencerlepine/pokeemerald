from form import draw; from r7 import src, ramp, acc
from PIL import Image
for sp in ['krayt','sando','exogorth']:
    s=draw(Image.open(src[sp]),64,48,ramp[sp],mix=0.55,scale=1)
    c=Image.new('RGBA',s.size,(255,255,255,255)); c.alpha_composite(s)
    c.convert('RGB').resize((1024,768),Image.NEAREST).save(f'r7/init_{sp}.png')

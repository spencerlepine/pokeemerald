import sys
from px import *
def make_init(im, h, out, x=None, y=4, W=144, H=96, grid=7, bg=(255,255,255)):
    k=h/im.height; s=im.resize((round(im.width*k),round(im.height*k)),Image.LANCZOS)
    c=Image.new('RGBA',(W,H),bg+(255,)); c.alpha_composite(s,((W-s.width)//2 if x is None else x,y))
    c.convert('RGB').resize((W*grid,H*grid),Image.NEAREST).save(out); return out
if __name__=='__main__':
    im=load_cut('web/cand/Krayt-dragon-mando.png',flip=True)
    make_init(im,118,'r3/init_krayt_B.png'); make_init(im,88,'r3/init_krayt_A.png')

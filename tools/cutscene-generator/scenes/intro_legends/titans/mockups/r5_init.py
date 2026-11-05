from px import *
from r3_x2 import wm
K=load_cut('web/cand/Krayt-dragon-mando.png',flip=True); Sd=load_cut('web/cand/SandoAquaMonster.webp')
def init(im,h,box_w,box_h,out,y=4,k=8):
    s=im.resize((round(im.width*h/im.height),h),Image.LANCZOS)
    c=Image.new('RGBA',(box_w,box_h),(255,255,255,255)); c.alpha_composite(s,((box_w-s.width)//2,y))
    c=c.convert('RGB').resize((box_w*k,box_h*k),Image.LANCZOS); c.save(out); print(out,c.size)
init(K,118,128,96,'r5/init_krayt.png')     # 1024x768, frame-crop window around the krayt
init(Sd,130,128,96,'r5/init_sando.png',y=-20)
init(wm,120,128,96,'r5/init_exo.png')

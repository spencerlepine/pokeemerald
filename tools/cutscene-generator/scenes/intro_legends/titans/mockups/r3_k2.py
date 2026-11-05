from px import *; from fin import finish
sand=bg_sand(); P=[]
im=load_cut('web/cand/Krayt-dragon-mando.png',flip=True)
def rot(im,deg):
    r=im.rotate(deg,resample=Image.BICUBIC,expand=True); a=np.array(r); ys,xs=np.where(a[...,3]>40)
    return r.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
def bury(spr, x, y, line):  # hide everything below a wavy dune line (scene y)
    a=np.array(spr).copy(); H,W=a.shape[:2]
    for cx in range(W):
        sy=line(x+cx)-y
        if sy<H: a[max(0,int(sy)):,cx,3]=0
    return Image.fromarray(a)
s=pixelize(im,h=118,colours=12); P.append(('K-a  film krayt, natural colour, feet off-frame',place(sand,s,(240-s.width)//2,4)))
r=rot(im,30); s=pixelize(r,w=232,h=120,colours=12); P.append((f'K-b  leaning across the frame ({s.width}x{s.height})',place(sand,s,4,4)))
s=pixelize(r,w=232,h=120,colours=12)
import math
line=lambda X: 74+4*math.sin(X/18)
P.append(('K-c  bursting out of the sand (body under the dunes)',place(sand,bury(s,4,4,line),4,4)))
s=pixelize(im,h=118,colours=10,gamma=1.9,contrast=1.2); P.append(('K-d  backlit, dark like Emerald\'s silhouettes',place(sand,s,(240-s.width)//2,4)))
s=pixelize(r,w=232,h=120,colours=10,gamma=1.9,contrast=1.2); P.append(('K-e  backlit and leaning across',place(sand,s,4,4)))
s=finish('/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/krayt/raw/20261105-042158_B_d0.35_s1251398483.png',colours=12)
P.append(('K-f  AI redraw of K-a (Civitai, denoise 0.35)',place(sand,s,48,0)))
sheet(P,'r3/krayt_round2.png')

from px import *
from PIL import ImageDraw
sky=bg_sky(); P=[]
src=Image.open('web/cand/ExogorthObstacleToken-RitR.png').convert('RGB')
W,H=src.size
worm=[(282,178),(300,166),(343,172),(352,120),(372,80),(405,62),(440,62),(472,78),(500,110),(515,160),(516,230),(503,268),(512,320),(526,400),(532,470),(522,505),(330,505),(316,440),(313,360),(318,292),(300,262),(286,232)]
rim=[(0,182),(40,140),(100,105),(160,88),(250,82),(340,92),(520,95),(640,100),(760,118),(863,150),(863,520),(0,520)]
def masked(polys):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    for p in polys: d.polygon(p,fill=255)
    im=src.convert('RGBA'); im.putalpha(m); a=np.array(im); ys,xs=np.where(a[...,3]>0)
    return im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
wm=masked([worm]); both=masked([worm,rim])
s=pixelize(wm,h=88,colours=12); P.append((f'X-g  the film slug, mouth open ({s.width}x{s.height})',place(sky,s,(240-s.width)//2,4)))
s=pixelize(both,h=88,colours=12); P.append((f'X-h  slug rising from its crater ({s.width}x{s.height})',place(sky,s,(240-s.width)//2,4)))
s=pixelize(both,w=232,colours=12); P.append((f'X-i  crater fills the width, slug cut at top? ({s.width}x{s.height})',place(sky,s,4,96-s.height+30)))
s=pixelize(both,h=88,colours=12,contrast=1.4,sat=1.3); P.append(('X-j  X-h with more contrast',place(sky,s,(240-s.width)//2,4)))
s=pixelize(both,h=88,colours=8,gamma=1.4,contrast=1.3); P.append(('X-k  X-h with 8 colours',place(sky,s,(240-s.width)//2,4)))
s=pixelize(wm,h=120,colours=12); P.append(('X-l  slug bigger, body cut by the frame',place(sky,s,(240-s.width)//2,4)))
sheet(P,'r3/exogorth_round2b.png')

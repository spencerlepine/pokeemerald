from mock import *
from r1b import colour, worm, comp, rock
sand, sea, sky = bg_sand(), bg_sea(), bg_sky()
PAD=4
def fit(img, pad=PAD, W=240, H=96):
    a=np.array(img); ys,xs=np.where(a[...,3]>0); img=Image.fromarray(a[ys.min():ys.max()+1,xs.min():xs.max()+1])
    s=min((W-2*pad)/img.width,(H-2*pad)/img.height)
    img=img.resize((round(img.width*s),round(img.height*s)),Image.NEAREST)
    return img,( (W-img.width)//2, H-pad-img.height ), s
P=[]
for name,sp,bg in [('GREATKRAYT','groudon',sand),('SANDO','kyogre',sea),('EXOGORTH','rayquaza',sky)]:
    im,xy,s=fit(colour(sp,1)); sl,_,_=fit(sil(sp,1))
    P.append((f'{name} silhouette, fit {s:.2f}x -> {im.width}x{im.height}',place(bg,sl,*xy)))
    P.append((f'{name} own colours, fit {s:.2f}x',place(bg,im,*xy)))
# Exogorth worm pose, fit
wm=worm([(200,70),(170,20),(120,8),(80,30),(60,62)],12,9,(240,96))
w=comp(rock(0.9),(178,46),wm); im,xy,s=fit(w)
P.append(('EXOGORTH alt: worm arching out of its rock, fit',place(sky,im,*xy)))
sheet(P,'r2/fit_frame.png')

from mock import *
sand, sea, sky = bg_sand(), bg_sea(), bg_sky()
def colour(species, scale, flip=False):
    im=Image.open(f'{G}/{species}/front.png').convert('RGBA'); a=np.array(im)
    key=a[0,0,:3]; m=~np.all(a[...,:3]==key,axis=-1)
    a[...,3]=np.where(m,255,0); ys,xs=np.where(m)
    im=Image.fromarray(a[ys.min():ys.max()+1,xs.min():xs.max()+1])
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((round(im.width*scale),round(im.height*scale)),Image.NEAREST)
P=[('K1 in its own colours (GREATKRAYT battle sprite, 2.4x)',place(sand,colour('groudon',2.4),40,1)),
   ('S1 in its own colours (SANDO battle sprite, 1.5x)',place(sea,colour('kyogre',1.5),76,0)),
   ('X2 in its own colours (EXOGORTH battle sprite, 1.75x)',place(sky,colour('rayquaza',1.75),74,0))]
# Exogorth worm poses: rock from the sprite + a tube body
def worm(pts, r0, r1, size):
    im=Image.new('L',size,0); d=ImageDraw.Draw(im)
    import math
    n=len(pts)
    path=[]
    for i in range(n-1):
        (x0,y0),(x1,y1)=pts[i],pts[i+1]
        for t in np.linspace(0,1,20): path.append((x0+(x1-x0)*t,y0+(y1-y0)*t))
    for k,(x,y) in enumerate(path):
        r=r0+(r1-r0)*k/len(path); d.ellipse((x-r,y-r,x+r,y+r),fill=255)
    return im
def rock(scale):
    return sil('rayquaza',scale)
def comp(rk, rxy, wm, col=(16,16,24)):
    out=Image.new('RGBA',(240,96)); out.paste(rk,rxy,rk)
    w=Image.new('RGBA',(240,96),col+(255,)); w.putalpha(wm); out.alpha_composite(w); return out
wm=worm([(200,70),(170,20),(120,8),(80,30),(60,62)],12,9,(240,96))
P.append(('X6 worm arching out of its rock (sketch)',place(sky,comp(rock(0.9),(178,46),wm),0,0)))
wm=worm([(120,110),(118,60),(105,25),(80,10)],16,12,(240,96))
P.append(('X7 worm rising out of the clouds, mouth open (sketch)',place(sky,comp(rock(0.01),(0,0),wm),0,0)))
wm=worm([(30,90),(70,40),(130,30),(170,60),(150,85),(110,80)],10,8,(240,96))
P.append(('X8 worm coiled like Emerald\'s Rayquaza (sketch)',place(sky,comp(rock(0.01),(0,0),wm),0,0)))
sheet(P,'r1/colour_and_exogorth_poses.png')

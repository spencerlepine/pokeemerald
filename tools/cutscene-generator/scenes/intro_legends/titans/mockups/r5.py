from cel import *; from mock import *
from r3_x2 import wm
sand,sea,sky=bg_sand(),bg_sea(),bg_sky()
K=load_cut('web/cand/Krayt-dragon-mando.png',flip=True); Sd=load_cut('web/cand/SandoAquaMonster.webp')
KR=hexs('#1e1410','#3a2a1e','#5a4430','#7c6244','#a08660','#c4ac80')
SR=hexs('#1a1c22','#33363c','#545450','#7a7466','#a49a84','#cfc4a8')
XR=hexs('#22161a','#46282c','#6e4440','#966a5e','#bc9282','#e0c0a8')
def sz(im,h): k=h/im.height; return round(im.width*k),h
def two(im,h,ramp,**kw):
    w,hh=sz(im,h//2); s=cel(im,w,hh,ramp,**kw); return s.resize((s.width*2,s.height*2),Image.NEAREST)
P=[]
k1=cel(K,*sz(K,118),KR,blur=3); P.append(('K1 cel 6 tones',place(sand,k1,(240-k1.width)//2,4)))
k2=cel(K,*sz(K,118),KR[:1]+KR[1:5],blur=4,gamma=1.3); P.append(('K2 cel 5 tones, darker',place(sand,k2,(240-k2.width)//2,4)))
k3=two(K,118,KR[:5],blur=3); P.append(('K3 2x chunky cel',place(sand,k3,(240-k3.width)//2,4)))
s1=cel(Sd,*sz(Sd,130),SR,blur=3); P.append(('S1 cel 6 tones',place(sea,s1,(240-s1.width)//2,-20)))
s2=cel(Sd,*sz(Sd,130),SR[1:],blur=4); P.append(('S2 cel 5 tones, softer',place(sea,s2,(240-s2.width)//2,-20)))
s3=two(Sd,130,SR[:5],blur=3); P.append(('S3 2x chunky cel',place(sea,s3,(240-s3.width)//2,-20)))
x1=cel(wm,*sz(wm,120),XR,blur=3); P.append(('X1 cel 6 tones',place(sky,x1,(240-x1.width)//2,4)))
x2=cel(wm,*sz(wm,120),XR[:1]+XR[2:],blur=4); P.append(('X2 cel 5 tones',place(sky,x2,(240-x2.width)//2,4)))
x3=two(wm,120,XR[:5],blur=3); P.append(('X3 2x chunky cel',place(sky,x3,(240-x3.width)//2,4)))
sheet(P,'r5/cel.png',cols=3)

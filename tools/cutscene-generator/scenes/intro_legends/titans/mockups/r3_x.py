from px import *
sky=bg_sky(); P=[]
im=white_cut('web/cand/SpaceSlug.webp')
a=np.array(im); ys,xs=np.where(a[...,3]>0); im=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
def rot(im,deg):
    r=im.rotate(deg,resample=Image.BICUBIC,expand=True); a=np.array(r); ys,xs=np.where(a[...,3]>40)
    return r.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
s=pixelize(im,h=88,colours=12); P.append((f'X-a  slug and its asteroid, fit height ({s.width}x{s.height})',place(sky,s,(240-s.width)//2,4)))
r=rot(im,-90); s=pixelize(r,w=232,h=88,colours=12); P.append((f'X-b  turned on its side, mouth left ({s.width}x{s.height})',place(sky,s,(240-s.width)//2,4)))
r=rot(im,-60); s=pixelize(r,w=232,h=110,colours=12); P.append((f'X-c  mouth lunging down-left ({s.width}x{s.height})',place(sky,s,(240-s.width)//2,2)))
s=pixelize(im,h=150,colours=12); P.append((f'X-d  close: the mouth, asteroid cut off',place(sky,s,(240-s.width)//2,96-4-s.height)))
r=rot(im,-90); s=pixelize(r,w=232,h=88,colours=10,gamma=1.7,contrast=1.2); P.append(('X-e  X-b darker, in shadow',place(sky,s,(240-s.width)//2,4)))
s=pixelize(r,w=232,h=88,colours=10,sat=0.4,contrast=1.2); P.append(('X-f  X-b grey like the ESB puppet',place(sky,s,(240-s.width)//2,4)))
sheet(P,'r3/exogorth_round2.png')

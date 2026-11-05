from px import *
sea=bg_sea(); P=[]
im=load_cut('web/cand/SandoAquaMonster.webp')
def rot(im,deg,flip=False):
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    r=im.rotate(deg,resample=Image.BICUBIC,expand=True); a=np.array(r); ys,xs=np.where(a[...,3]>40)
    return r.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
s=pixelize(im,h=88,colours=12); P.append((f'S-a  film model, fit height ({s.width}x{s.height})',place(sea,s,(240-s.width)//2,4)))
r=rot(im,-35); s=pixelize(r,w=232,h=110,colours=12); P.append((f'S-b  turned to swim left, tail up-right ({s.width}x{s.height})',place(sea,s,(240-s.width)//2,2)))
s=pixelize(im,h=160,colours=12); P.append((f'S-c  huge, tail out of frame ({s.width}x{s.height})',place(sea,s,(240-s.width)//2,96-4-s.height)))
s=pixelize(im,h=130,colours=12); P.append((f'S-d  bigger, lunging at camera ({s.width}x{s.height})',place(sea,s,(240-s.width)//2,-20)))
r=rot(im,-35); s=pixelize(r,w=232,h=110,colours=10,gamma=1.8,contrast=1.2,sat=0.7); P.append(('S-e  S-b murky and dark, like the film',place(sea,s,(240-s.width)//2,2)))
s=pixelize(r,w=232,h=110,colours=8,gamma=1.6,sat=1.0); 
a=np.array(s).astype(float); a[...,:3]=a[...,:3]*np.array([0.75,0.95,1.15]); s=Image.fromarray(a.clip(0,255).astype('uint8'))
P.append(('S-f  S-b tinted blue by the water',place(sea,s,(240-s.width)//2,2)))
sheet(P,'r3/sando_round2.png')

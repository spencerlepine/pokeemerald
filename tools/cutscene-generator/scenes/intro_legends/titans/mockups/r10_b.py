from illpx import illpx; from mock import *; import glob
from r10_px import pick, R, bgs
P1=[];P2=[];D=[]
for sp in pick:
    for k,sd in enumerate(pick[sp]):
        f=glob.glob(R+sp+f'/raw/*_ill_*{sd}.png')[0]
        im=Image.open(f).convert('RGB').resize((256,192),Image.LANCZOS)
        c=Image.new('RGB',(240,96),'white'); c.paste(im.crop((8,0,248,96*2)).resize((240,96)) if False else im.resize((128,96),Image.LANCZOS),(56,0))
        D.append((f'{sp.upper()} {k+1} drawing',np.array(c)))
        s1=illpx(f,w=128,h=96,colours=8,scale=1,min_island=3); s1.save(f'r10/{sp}_{k+1}_1x.png')
        P1.append((f'{sp.upper()} {k+1} at 1x',place(bgs[sp],s1,56,0)))
sheet([(l,Image.fromarray(a)) for l,a in D],'r10/drawings.png',cols=3)
sheet(P1,'r10/bold_1x.png',cols=3)

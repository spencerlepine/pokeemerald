from flatpx import flatpx; from mock import *; import glob
sand,sea,sky=bg_sand(),bg_sea(),bg_sky(); bgs={'krayt':sand,'sando':sea,'exogorth':sky}
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
pick={'krayt':['s654492847','s755866184','s755866185'],'sando':['s1634441755','s1778252833','s1778252834'],'exogorth':['s1492340030','s1492340031','s1087862444']}
P=[];P2=[]
for sp in pick:
    for k,sd in enumerate(pick[sp]):
        f=glob.glob(R+sp+f'/raw/*_sug*_*{sd}.png')[0]
        s=flatpx(f); s.save(f'r13/{sp}_{k+1}.png'); P.append((f'{sp.upper()} {k+1}',place(bgs[sp],s,56,0)))
        s2=flatpx(f,w=64,h=48,colours=8,min_island=2).resize((128,96),Image.NEAREST); P2.append((f'{sp.upper()} {k+1} 2x',place(bgs[sp],s2,56,0)))
sheet(P,'r13/flat_1x.png',cols=3); sheet(P2,'r13/flat_2x.png',cols=3)

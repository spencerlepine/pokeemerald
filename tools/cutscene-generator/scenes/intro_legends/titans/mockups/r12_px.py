from flatpx import flatpx; from mock import *; import glob
sand,sea,sky=bg_sand(),bg_sea(),bg_sky(); bgs={'krayt':sand,'sando':sea,'exogorth':sky}
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
pick={'krayt':['s654492846','s654492847','s1525162133'],'sando':['s248468301','s248468302','s1462913832'],'exogorth':['s1492340030','s1492340031','s1087862444']}
P=[];P2=[]
for sp in pick:
    for k,sd in enumerate(pick[sp]):
        f=glob.glob(R+sp+f'/raw/*_sug_*{sd}.png')[0]
        s=flatpx(f); s.save(f'r12/{sp}_{k+1}.png'); P.append((f'{sp.upper()} {k+1}',place(bgs[sp],s,56,0)))
        s2=flatpx(f,w=64,h=48,colours=8,min_island=2).resize((128,96),Image.NEAREST); P2.append((f'{sp.upper()} {k+1} 2x',place(bgs[sp],s2,56,0)))
sheet(P,'r12/flat_1x.png',cols=3); sheet(P2,'r12/flat_2x.png',cols=3)

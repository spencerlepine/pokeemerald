from snap import snap; from mock import *; import glob
sand,sea,sky=bg_sand(),bg_sea(),bg_sky(); bgs={'krayt':sand,'sando':sea,'exogorth':sky}
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
pick={'krayt':['s164032261','s164032262','s1515721086'],'sando':['s1883016185','s1883016186','s845721581'],'exogorth':['s1246053440','s1968321673','s1968321674']}
P=[]
for sp in pick:
    for k,sd in enumerate(pick[sp]):
        f=glob.glob(R+sp+f'/raw/*_xl512_*{sd}.png')[0]
        s=snap(f,colours=6,min_island=3,tooth_frac=2,eye_col=None)
        s.save(f'r8/{sp}_{k+1}.png')
        P.append((f'{sp.upper()} {k+1}',place(bgs[sp],s,56,0)))
sheet(P,'r8/pixel_round3.png',cols=3)

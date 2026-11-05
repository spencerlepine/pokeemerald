from mock import *; from fin import finish; import glob
sand,sea,sky=bg_sand(),bg_sea(),bg_sky()
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
bgs={'krayt':sand,'sando':sea,'exogorth':sky}
P=[]
for sp in ['krayt','sando','exogorth']:
    fs=sorted(glob.glob(R+sp+'/raw/*_spr_*.png'))
    for f in fs:
        s=finish(f,W=128,H=96,colours=15,outline=None)
        P.append((f'{sp} {f[-14:-4]} 1x',place(bgs[sp],s,56,0)))
    s=finish(fs[0],W=64,H=48,colours=10,outline=None).resize((128,96),Image.NEAREST)
    P.append((f'{sp} 2x chunky',place(bgs[sp],s,56,0)))
sheet(P,'r5/xl_in_scene.png',cols=3)

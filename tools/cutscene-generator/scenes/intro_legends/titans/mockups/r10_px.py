from illpx import illpx; from mock import *; import glob
sand,sea,sky=bg_sand(),bg_sea(),bg_sky(); bgs={'krayt':sand,'sando':sea,'exogorth':sky}
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
pick={'krayt':['s546600332','s885053392','s885053393'],'sando':['s728238143','s728238144','s768592872'],'exogorth':['s1966350048','s1966350049','s957363762']}
P=[]
for sp in pick:
    for k,sd in enumerate(pick[sp]):
        fs=glob.glob(R+sp+f'/raw/*_ill_*{sd}.png')
        if not fs: print('missing',sp,sd); continue
        s=illpx(fs[0]); s.save(f'r10/{sp}_{k+1}.png')
        P.append((f'{sp.upper()} {k+1}',place(bgs[sp],s,56,0)))
sheet(P,'r10/bold_round.png',cols=3)

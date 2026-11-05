from chunky import *; from mock import *
sand,sea,sky=bg_sand(),bg_sea(),bg_sky()
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
import glob
src={'krayt':sorted(glob.glob(R+'krayt/raw/*_spr_*.png'))[1],'sando':sorted(glob.glob(R+'sando/raw/*_spr_*.png'))[1],'exogorth':sorted(glob.glob(R+'exogorth/raw/*_spr_*.png'))[1]}
ramps={'krayt':[hexs('#2a1c14','#4a3424','#6e5236','#94764e','#b89c6c'),hexs('#24180f','#4c3420','#7a5a38','#a88a5c'),hexs('#1e140e','#5a4028','#9a7a50')],
       'sando':[hexs('#202428','#3c3e3e','#5e5c52','#867e6a','#ada188'),hexs('#1e2226','#45463f','#736c5a','#a29780'),hexs('#1c2024','#55554a','#958a72')],
       'exogorth':[hexs('#2a1418','#56282c','#86484a','#b0766c','#d6a690'),hexs('#2a1418','#64343a','#9c6460','#cc9c88'),hexs('#28141a','#7a4446','#c08c7c')]}
bgs={'krayt':sand,'sando':sea,'exogorth':sky}
P=[]
for sp in ['krayt','sando','exogorth']:
    im=Image.open(src[sp])
    for k,(rmp,sm,isl,lab) in enumerate([(ramps[sp][0],5,4,'5 tones'),(ramps[sp][1],9,8,'4 tones, flatter'),(ramps[sp][2],13,12,'3 tones, low poly')]):
        s=chunky(im,64,48,rmp,smooth=sm,min_island=isl)
        P.append((f'{sp.upper()} {k+1}: {lab}',place(bgs[sp],s,56,0)))
sheet(P,'r6/chunky_round2.png',cols=3)

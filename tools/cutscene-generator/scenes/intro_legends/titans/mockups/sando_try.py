from flatpx import flatpx; from mock import *; import glob
sea=bg_sea(); R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/sando/raw/'
P=[]
for sd in ['s1634441755','s1778252833','s1778252834','s1634441754']:
    f=glob.glob(R+f'*_sug2_*{sd}.png')[0]
    for sat in (0.9,):
        s=flatpx(f,colours=12,passes=2,sat=sat); s.save(f'final/sando_{sd}.png'); P.append((f'{sd} sat {sat}',place(sea,s,56,-6)))
sheet(P,'final/sando_try.png',cols=2)

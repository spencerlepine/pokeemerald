from flatpx import flatpx; from mock import *; import glob
sand,sea,sky=bg_sand(),bg_sea(),bg_sky()
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
F={'krayt':('s755866184',sand,56,0),'sando':('s1778252834',sea,56,-6),'exogorth':('s1492340030',sky,56,0)}
P=[];C=[]
for sp,(sd,bg,x,y) in F.items():
    f=glob.glob(R+sp+f'/raw/*_sug*_*{sd}.png')[0]
    s=flatpx(f,colours=12,passes=2,sat=0.9 if sp=='sando' else 1.15); s.save(f'final/{sp}.png')
    n=len({tuple(p[:3]) for p in np.array(s).reshape(-1,4) if p[3]})
    print(sp,'colours',n)
    P.append((f'{sp.upper()}',place(bg,s,x,y)))
    C.append(s)
sheet(P,'final/titans_in_scene.png',cols=1,scale=3)
o=Image.new('RGBA',(128*3*4+32,96*4),(210,210,210,255))
for k,i in enumerate(C): o.alpha_composite(i.resize((512,384),Image.NEAREST),(k*528,0))
o.save('final/titans_closeup_4x.png')

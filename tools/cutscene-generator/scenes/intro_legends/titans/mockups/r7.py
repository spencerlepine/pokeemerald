from form import draw; from cel import hexs; from mock import *; import glob
sand,sea,sky=bg_sand(),bg_sea(),bg_sky()
R='/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/titans/runs/'
src={sp:sorted(glob.glob(R+sp+'/raw/*_spr_*.png'))[1] for sp in ['krayt','sando','exogorth']}
ramp={'krayt':hexs('#2a1c14','#4e3826','#76583a','#a0805a','#c8aa80'),
      'sando':hexs('#1e2226','#3e413f','#646155','#8e8670','#bbb092'),
      'exogorth':hexs('#2a1418','#5a2a2e','#8c4e4c','#b87e70','#e0b49c')}
acc={'krayt':(232,222,196),'sando':(236,232,214),'exogorth':(244,232,214)}
bgs={'krayt':sand,'sando':sea,'exogorth':sky}
P=[]
for sp in ['krayt','sando','exogorth']:
    im=Image.open(src[sp])
    for k,(kw,lab) in enumerate([(dict(mix=0.55),'form + source values'),
                                (dict(mix=0.8),'mostly form, rounder'),
                                (dict(mix=0.6,accent=acc[sp]),'form + teeth/eye accents')]):
        s=draw(im,64,48,ramp[sp],**kw); P.append((f'{sp.upper()} {k+1}: {lab}',place(bgs[sp],s,56,0)))
sheet(P,'r7/form_round.png',cols=3)

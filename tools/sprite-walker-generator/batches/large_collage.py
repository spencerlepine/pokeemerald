import sys,yaml
sys.path.insert(0,'.')
from PIL import Image, ImageDraw
from walker_sprite import palette as palm
G='../../game/graphics/object_events/'
GR=(115,197,164)
def rgba_png(path, palfile=None):
    im=Image.open(path); idx=im.load()
    cols=[tuple(im.getpalette()[i*3:i*3+3]) for i in range(16)]
    if palfile: cols=palm.load_jasc(palfile)
    out=Image.new('RGBA',im.size,(0,0,0,0)); o=out.load()
    for y in range(im.height):
        for x in range(im.width):
            v=idx[x,y]
            if v: o[x,y]=tuple(cols[v])+(255,)
    return out
def gpal(n): return G+f'palettes/{n}.pal'
def tpal(n): return f'palettes/{n}.pal'
sheets=[('groudon','groudon',32),('kyogre','kyogre',32),('rayquaza','npc_3',64),('rayquaza_still','npc_3',64),
('lugia','lugia',32),('ho_oh','ho_oh',32),('deoxys','deoxys',32),('latias_latios','npc_2',32),
('regi','npc_2',32),('vigoroth','vigoroth',32),('poochyena','poochyena',32),('enemy_zigzagoon','enemy_zigzagoon',32)]
titles={'groudon':'GREATKRAYT (Groudon)','kyogre':'SANDO (Kyogre)','rayquaza':'EXOGORTH (Rayquaza)','rayquaza_still':'EXOGORTH still','lugia':'TIDEWING (Lugia)','ho_oh':'DAWNWING (Ho-Oh)','deoxys':'SHIFTSTAR (Deoxys)','latias_latios':'ASHLA / BOGAN (Latias/Latios)','regi':'WARDENS (Regirock/ice/steel)','vigoroth':'SLOTHFURY (Vigoroth)','poochyena':'MASSIFF (Poochyena)','enemy_zigzagoon':'SCURRIER large (Zigzagoon)'}
brendan=rgba_png(G+'pics/people/brendan/walking.png',gpal('brendan')).crop((0,0,16,32))
kael=rgba_png('../../wiki/art/graphics/object_events/pics/people/brendan/walking.png',tpal('kael')).crop((0,0,16,32))
Z=3
def strip(img,fs,people):
    pw=40 if people else 0
    n=img.width//fs
    s=Image.new('RGBA',(pw+n*(fs+4),fs),GR+(255,))
    if people:
        s.alpha_composite(people[0],(2,fs-32)); s.alpha_composite(people[1],(20,fs-32))
    for i in range(n):
        s.alpha_composite(img.crop((i*fs,0,(i+1)*fs,fs)),(pw+i*(fs+4),0))
    return s
blocks=[];W=1000;H=30
for name,vpal,fs in sheets:
    van=rgba_png(G+f'pics/pokemon/{name}.png',gpal(vpal))
    p=yaml.safe_load(open(f'art/{name}.yaml'))['palette']
    nw=rgba_png(f'output/{name}/{name}.png',tpal(p))
    extra=[]
    if name=='latias_latios': extra=[('BOGAN on npc_2',rgba_png(f'output/{name}/{name}.png',tpal('npc_2')))]
    if name=='regi': extra=[('ICEWARDEN npc_3',rgba_png(f'output/{name}/{name}.png',tpal('npc_3'))),('DURAWARDEN npc_4',rgba_png(f'output/{name}/{name}.png',tpal('npc_4')))]
    a=strip(van,fs,(brendan,kael)); b=strip(nw,fs,(brendan,kael))
    ex=[(l,strip(e,fs,None)) for l,e in extra]
    blocks.append((titles[name],a,b,ex))
    W=max(W,200+a.width*Z+20+sum(e.width*Z+12 for _,e in ex)); H+=20+2*a.height*Z+16
im=Image.new('RGB',(W,H),(24,24,30)); dr=ImageDraw.Draw(im)
dr.text((10,8),"Large companion mockups: original on top, new below, every frame at 3x. Left of each row: Brendan, then the new Kael, for scale.",fill=(220,220,220))
y=28
for t,a,b,ex in blocks:
    dr.text((10,y),t,fill=(245,245,245))
    dr.text((10,y+20+a.height*Z//2),"original",fill=(150,150,150)); dr.text((10,y+24+a.height*Z*3//2),"new",fill=(150,150,150))
    im.paste(a.resize((a.width*Z,a.height*Z),Image.NEAREST),(200,y+14))
    im.paste(b.resize((b.width*Z,b.height*Z),Image.NEAREST),(200,y+18+a.height*Z))
    x=200+b.width*Z+20
    for l,e in ex:
        dr.text((x,y+4+a.height*Z),l,fill=(200,200,200))
        im.paste(e.resize((e.width*Z,e.height*Z),Image.NEAREST),(x,y+18+a.height*Z)); x+=e.width*Z+12
    y+=20+2*a.height*Z+16
im.save(sys.argv[1]); print(im.size)

# SHIPPED 2026-11-02 (owner pick: "deep tuck, tails", variant 2, cloak wrapped over the whole upper body).
# Writes game/graphics/intro/scene_2/brendan.png and may.png: `python3 riders_v2.py --install`.
# This replaces the riders from riders.px.js; rebuilding intro_bike.px.js would put the old riders back.
# Hand-built speeder riders: capsule parts with outlines and side shading, plus hand-drawn heads.
import math, sys
from PIL import Image, ImageDraw
G='/home/user/pokeemerald/game/graphics/intro/scene_2/'
PAL=["#48b8a8","#483838","#888878","#c8c0e0","#f8f8f8","#d03830","#f87050","#303040",
     "#f8d898","#e0a088","#a06840","#58c8f8","#3878c0","#f0e0b8","#c0a070","#604028"]
PAL=[tuple(int(c[i:i+2],16) for i in (1,3,5)) for c in PAL]
# materials -> palette index
MAT={'kael':dict(N=12,n=11,O=15,H=10,h=15,K=8,k=9,E=1,W=4,w=3,x=2,V=15,v=7,P=3,p=2,B=10,b=15,C=14,c=10,D=13,S=10,s=15,G=7),
     'mira':dict(N=5,n=6,O=15,H=10,h=15,K=8,k=9,E=1,W=4,w=3,x=2,V=15,v=7,P=3,p=2,B=10,b=15,C=14,c=10,D=13,S=14,s=10,G=7)}
HEADS={
'kael':["...OOOOOO....",
        "..OHHHHHHOO..",
        ".OHHHHHHHHhO.",
        "ONNNNNNNNNNO.",
        "OnnnnNNNNNNO.",
        "OHKhKKHHHhhO.",
        "OKKKKKKHhhhO.",
        "OKEKKKKKHhO..",
        "OKEKKKkKHhO..",
        "OKKKKkkKkO...",
        ".OKkkkkkO....",
        "..OOOOOO....."],
'mira':["....OOOOO.OO.",
        "..OOHHHHHOHHO",
        ".OHHHHHHHHOhO",
        "ONNNNNNNNNNO.",
        "OnnnnNNNNNNO.",
        "OHKhKKHHHhhO.",
        "OKKKKKKHhhhO.",
        "OKEKKKKKHhO..",
        "OKEKKKkKHhhO.",
        "OKKKKkkKhhO..",
        ".OKkkkkkOhO..",
        "..OOOOOO.O..."],
}
# soft outline colour per material (selective outlining instead of one black line)
SOFT={'W':'x','w':'x','x':'x','P':'p','p':'p'}
def soft(m): return SOFT.get(m,'O')
def cap(mask,p0,p1,r):
    (x0,y0),(x1,y1)=p0,p1
    for y in range(64):
        for x in range(64):
            dx,dy=x1-x0,y1-y0; L=dx*dx+dy*dy
            t=0 if L==0 else max(0,min(1,((x-x0)*dx+(y-y0)*dy)/L))
            if math.hypot(x-(x0+t*dx),y-(y0+t*dy))<=r: mask.add((x,y))
    return mask
def poly(mask,pts):
    im=Image.new('1',(64,64),0); ImageDraw.Draw(im).polygon(pts,fill=1)
    for y in range(64):
        for x in range(64):
            if im.getpixel((x,y)): mask.add((x,y))
    return mask
class Canvas:
    def __init__(s): s.px={}
    def part(s,mask,light,shade,deep=None,shade_side=1,outline=True,band=None):
        # shade the side away from the light (right/bottom), outline the part's boundary
        for (x,y) in mask:
            nb=[(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
            edge=any(n not in mask for n in nb)
            if edge and outline: s.px[(x,y)]=deep or shade; continue
            m=light
            if (x+shade_side,y) not in mask or (x+2*shade_side,y) not in mask or (x,y+2) not in mask: m=shade
            if deep and ((x+shade_side,y+1) not in mask and (x,y+1) not in mask): m=deep
            s.px[(x,y)]=m
    def put(s,x,y,m): s.px[(x,y)]=m
    def head(s,who,x0,y0):
        for j,row in enumerate(HEADS[who]):
            for i,ch in enumerate(row):
                if ch!='.': s.px[(x0+i,y0+j)]=ch
    def outline_out(s):
        add={}
        for (x,y) in list(s.px):
            for n in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if n not in s.px: add[n]=soft(s.px[(x,y)])
        s.px.update(add)
    def img(s,who):
        im=Image.new('P',(64,64),0); im.putpalette(sum(PAL,()))
        for (x,y),m in s.px.items():
            if 0<=x<64 and 0<=y<64: im.putpixel((x,y),MAT[who][m])
        return im

def rider(who,v,f):
    """Racer tuck family. v: 1 tuck, 2 deep tuck with tails, 3 tuck head-up with long band tails."""
    bob=[0,0,1,1][f]; flap=f%2
    c=Canvas()
    if v==1:
        sh=(23,22); hip=(33,31); knee=(23,35); foot=(25,41); hand=(17,32); head=(15,10); tails=who=='mira'; band=4
    elif v==2:
        sh=(23,24); hip=(33,31); knee=(23,35); foot=(25,41); hand=(16,32); head=(13,13); tails=True; band=5
    else:
        sh=(23,21); hip=(33,31); knee=(23,35); foot=(25,41); hand=(17,32); head=(15,8); tails=who=='mira'; band=8
    def B(p): return (p[0],p[1]+bob)
    sh,hip,knee,foot,hand=map(B,(sh,hip,knee,foot,hand)); head=(head[0],head[1]+bob)
    body=set()
    # cloak / robe tails streaming behind (no line between them and the back)
    if tails:
        L=15+flap+(2 if v==2 else 0)
        poly(body,[(sh[0]+3,sh[1]-1),(sh[0]+8,sh[1]),(hip[0]+L,hip[1]-2-flap),(hip[0]+L-2,hip[1]+1),(hip[0]+2,hip[1]+2)])
        tailset=set(body)
    else: tailset=set()
    # far arm (behind)
    fa=set(); cap(fa,(sh[0]+3,sh[1]+1),(hand[0]+3,hand[1]-1),1.6); c.part(fa,*(('c','s') if v==2 else ('w','x')))
    # torso + tails as one shape: no outline on the back
    t=set(); cap(t,sh,hip,4.2); body|=t
    c.part(body,*(('C','c','s') if v==2 else ('W','w','x')),outline=False)
    if who=='mira' or v==2:
        cl=(who=='mira' or v==2)
        for p in tailset-t: c.px[p]= 'C' if cl else 'W'
        # shade the tails' lower edge
        for (x,y) in tailset-t:
            if (x,y+1) not in body or (x,y+2) not in body: c.px[(x,y)]='c' if cl else 'w'
    # crossover lapel
    for i in range(6 if v!=2 else 0): c.put(sh[0]+i//2, sh[1]+1+i, 'x')
    # belt
    bx,by=hip[0]-1,hip[1]-4
    for dx in range(-4,5):
        for dy in (0,1):
            p=(bx+dx-dy,by+dy)
            if p in t and v!=2: c.put(*p,'V' if dy==0 else 'v')
    # hood hanging down behind the neck (not worn)
    hd=set(); cap(hd,(sh[0]+2,sh[1]-1),(sh[0]+4,sh[1]+1),2.2)
    for p in hd:
        x,y=p
        c.px[p]='c' if ((x+1,y) not in hd or (x,y+1) not in hd) else ('D' if (x,y-1) not in hd else 'C')
    # near leg
    lg=set(); cap(lg,hip,knee,3.4); c.part(lg,'P','p')
    sn=set(); cap(sn,knee,(foot[0],foot[1]-3),2.6); c.part(sn,'P','p')
    bt=set(); cap(bt,(foot[0]+1,foot[1]-3),(foot[0],foot[1]),2.4); cap(bt,(foot[0]-3,foot[1]),(foot[0]+1,foot[1]),1.6); c.part(bt,'B','b')
    # near arm and glove
    ar=set(); elbow=((sh[0]+hand[0])//2+1,(sh[1]+hand[1])//2+2)
    cap(ar,(sh[0]-1,sh[1]+1),elbow,2.8); cap(ar,elbow,hand,2.3); c.part(ar,*(('C','c','s') if v==2 else ('W','w','x')))
    gl=set(); cap(gl,(hand[0]+1,hand[1]),(hand[0]-1,hand[1]),2.0); c.part(gl,'B','b')
    # head and bandana tails
    c.head(who,*head)
    tx,ty=head[0]+11,head[1]+3
    for i in range(band+flap):
        y=ty+ (i//3) + (1 if (i+flap)%4==0 else 0)
        c.put(tx+i,y,'N'); 
        if i<band-1: c.put(tx+i,y+1,'n' if i%2 else 'N')
    c.outline_out()
    return c.img(who)

def speeder(f):
    b=Image.open(G+'bicycle.png'); return b.crop((0,f*32,64,f*32+32))

def compose(who,v,f,bg=(232,200,144)):
    im=Image.new('RGB',(64,64),bg)
    def M(p):
        m=Image.new('L',p.size,0); m.putdata([255 if q else 0 for q in p.getdata()]); return m
    spm=M(speeder(f))
    im.paste(speeder(f).convert('RGB'),(0,24),spm)
    r=rider(who,v,f); rm=M(r)
    im.paste(r.convert('RGB'),(0,0),rm)
    return im

def install():
    for who,f in (('kael','brendan.png'),('mira','may.png')):
        pal=Image.open(G+f).getpalette()[:48]
        out=Image.new('P',(64,256),0); out.putpalette(pal)
        for fr in range(4): out.paste(rider(who,2,fr),(0,fr*64))
        out.save(G+f)

if __name__=='__main__' and '--install' in sys.argv:
    install(); sys.exit(0)
if __name__=='__main__':
    S=4
    out=Image.new('RGB',(64*S*4+30,(64*S+10)*6),(30,30,40))
    d=ImageDraw.Draw(out)
    y=0
    for v in (1,2,3):
        for who in ('kael','mira'):
            for f in range(4):
                out.paste(compose(who,v,f).resize((64*S,64*S),0),(f*(64*S+10),y))
            y+=64*S+10
    out.save(sys.argv[1] if len(sys.argv)>1 else 'sheet.png')

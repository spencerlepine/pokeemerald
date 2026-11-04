"""Redraw the StarNAV header: POKéMON NAVIGATOR -> STAR NAVIGATOR.

The header (graphics/pokenav/header.png + header.bin) is an image: its letters are tiles, not font text.
This rebuilds it from Emerald's header (read from git, commit b532c32e), reusing the header's own letters
(N A V I G A T O R, big and small) and a drawn S, then re-tiles it into the same 53 tiles.

    python3 starnav_header.py preview   # out/starnav_header.png (before above, after below)
    python3 starnav_header.py install   # writes ../../game/graphics/pokenav/header.png and header.bin
"""
import io, os, subprocess, sys
ROOT=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
VANILLA_REV='b532c32e'
def _git(path):
    return subprocess.run(['git','-C',ROOT,'show',f'{VANILLA_REV}:'+path],capture_output=True,check=True).stdout
from PIL import Image
import struct
def compose():
    im=Image.open(io.BytesIO(_git('game/graphics/pokenav/header.png')))
    tiles=[im.crop((i*8,0,i*8+8,8)) for i in range(im.size[0]//8)]
    e=struct.unpack('<1024H',_git('game/graphics/pokenav/header.bin'))
    out=Image.new('P',(256,256)); out.putpalette(im.getpalette())
    for i,v in enumerate(e):
        tl=tiles[v&0x3ff]
        if v>>10&1: tl=tl.transpose(Image.FLIP_LEFT_RIGHT)
        if v>>11&1: tl=tl.transpose(Image.FLIP_TOP_BOTTOM)
        out.paste(tl,((i%32)*8,(i//32)*8))
    return im,out,e

def segments(out,y0,y1,bg):
    px=out.load(); segs=[]; cur=None
    for x in range(256):
        ink=any(px[x,y]!=bg for y in range(y0,y1))
        if ink and cur is None: cur=x
        if not ink and cur is not None: segs.append((cur,x)); cur=None
    return segs

BIG_S=["#######","#######","##.....","##.....","##.....","##.....","#######","#######",".....##",".....##",".....##","#######","#######"]
def big_glyphs(out):
    px=out.load(); g={}
    for ch,x0 in zip("NAVIGATOR",range(96,168,8)):
        g[ch]=[[px[x,y] for x in range(x0,x0+8)] for y in range(0,16)]
    return g
def small_ink(out):
    px=out.load(); ink={}
    cols=[x for x in range(186,232) if any(px[x,y]==1 for y in range(180,189))]
    segs=[];cur=[cols[0]]
    for c in cols[1:]:
        if c==cur[-1]+1: cur.append(c)
        else: segs.append(cur); cur=[c]
    segs.append(cur)
    return segs

SMALL_S=["####","#...","#...","####","...#","...#","####"]
def build(top="STAR",bottom="STAR"):
    im,out,e=compose(); px=out.load()
    big=big_glyphs(out)
    # small ink glyphs
    segs=small_ink(out); sg={}
    for ch,s in zip("NAVIGATOR",segs):
        sg[ch]=["".join('#' if px[x,y]==1 else '.' for x in range(s[0],s[-1]+1)) for y in range(181,188)]
    sg['S']=SMALL_S
    new=out.copy(); np_=new.load()
    # top: clear text rows 0-15 cols 0-239 to bg 4 where text was (keep non-text colours? text area is plain bg)
    for x in range(16,176):
        for y in range(0,16): np_[x,y]=4
    x=24
    word=top+" NAVIGATOR"
    for ch in word:
        if ch==' ': x+=16; continue
        if ch=='S':
            for r,row in enumerate(BIG_S):
                for c,v in enumerate(row):
                    if v=='#': np_[x+c,3+r]=1
        else:
            for y in range(16):
                for c in range(8):
                    if big[ch][y][c]!=4: np_[x+c,y]=big[ch][y][c]
        x+=8
    # bottom: clear and render right-aligned to ink end 228
    for x in range(140,234):
        for y in range(179,190): np_[x,y]=4
    word=bottom+" NAVIGATOR"
    widths=[ (6 if ch==' ' else len(sg[ch][0])+1) for ch in word]
    total=sum(widths)-1
    x=228-total+1
    ink=set()
    for ch,w in zip(word,widths):
        if ch!=' ':
            for r,row in enumerate(sg[ch]):
                for c,v in enumerate(row):
                    if v=='#': ink.add((x+c,181+r))
        x+=w
    for (a,b) in ink:
        for (dx,dy) in ((1,0),(0,1)):
            if (a+dx,b+dy) not in ink: np_[a+dx,b+dy]=5
    for (a,b) in ink: np_[a,b]=1
    return im,new,e
def retile(im,new,e,n=53):
    tiles=[im.crop((i*8,0,i*8+8,8)) for i in range(im.size[0]//8)]
    newtiles=[tiles[0]]; keys={tiles[0].tobytes():0}
    ent=list(e)
    for i,v in enumerate(e):
        if v==0 and not (i//32 in (0,1,2,3,22,23)): continue
        t=new.crop(((i%32)*8,(i//32)*8,(i%32)*8+8,(i//32)*8+8))
        found=None
        for hf in (0,1):
            for vf in (0,1):
                tt=t
                if hf: tt=tt.transpose(Image.FLIP_LEFT_RIGHT)
                if vf: tt=tt.transpose(Image.FLIP_TOP_BOTTOM)
                k=tt.tobytes()
                if k in keys and found is None: found=(keys[k],hf,vf)
        if found is None:
            keys[t.tobytes()]=len(newtiles); newtiles.append(t); found=(len(newtiles)-1,0,0)
        ent[i]=(v&0xF000)|found[0]|(found[1]<<10)|(found[2]<<11)
    assert len(newtiles)<=n, len(newtiles)
    while len(newtiles)<n: newtiles.append(tiles[0])
    strip=Image.new('P',(8*n,8)); strip.putpalette(im.getpalette())
    for i,t in enumerate(newtiles): strip.paste(t,(i*8,0))
    return strip,struct.pack('<1024H',*ent),len(newtiles)


if __name__=='__main__':
    cmd=sys.argv[1] if len(sys.argv)>1 else 'preview'
    im,new,e=build()
    if cmd=='preview':
        _,old,_=compose()
        os.makedirs(os.path.join(os.path.dirname(__file__),'out'),exist_ok=True)
        sheet=Image.new('RGB',(240,384))
        sheet.paste(old.crop((0,0,240,192)).convert('RGB'),(0,0)); sheet.paste(new.crop((0,0,240,192)).convert('RGB'),(0,192))
        p=os.path.join(os.path.dirname(__file__),'out','starnav_header.png')
        sheet.resize((720,1152),Image.NEAREST).save(p); print(p)
    elif cmd=='install':
        strip,binb,n=retile(im,new,e)
        g=os.path.join(ROOT,'game','graphics','pokenav')
        strip.save(os.path.join(g,'header.png')); open(os.path.join(g,'header.bin'),'wb').write(binb)
        print('wrote header.png and header.bin,',n,'unique tiles')
    else: sys.exit(__doc__)

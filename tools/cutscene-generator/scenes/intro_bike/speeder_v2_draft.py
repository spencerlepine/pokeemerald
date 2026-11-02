import sys; sys.path.insert(0,'.')
import rider
from PIL import Image, ImageDraw
G=rider.G
BIKE=Image.open(G+'bicycle.png')
DY=[0,1,1,0]
def base(f): return BIKE.crop((0,f*32,64,f*32+32)).copy()
def P(im,x,y,c):
    if 0<=x<64 and 0<=y<32: im.putpixel((x,y),c)
def line(im,p0,p1,c,w=1):
    (x0,y0),(x1,y1)=p0,p1; n=max(abs(x1-x0),abs(y1-y0),1)
    for i in range(n+1):
        x=round(x0+(x1-x0)*i/n); y=round(y0+(y1-y0)*i/n)
        for k in range(w): P(im,x+k,y,c)
def strut(im,p0,p1):
    # metal strut: outline - light - outline, 3 px wide
    line(im,(p0[0]-1,p0[1]),(p1[0]-1,p1[1]),1); line(im,(p0[0]+1,p0[1]),(p1[0]+1,p1[1]),1); line(im,p0,p1,3)
def make(v,f):
    im=base(f); d=DY[f]
    # remove the old ground shadow (rows 28-31), keep the hull
    for y in range(28,32):
        for x in range(64):
            if im.getpixel((x,y))==15: im.putpixel((x,y),0)
    # bike-row of the hull bottom ~ 25+d ; skids reach row 29+d ; shadow on row 31
    for x in range(10,54,2): P(im,x,31,15)
    if v==1:   # two straight struts and a skid rail with a turned-up nose
        for sx in (24,44): strut(im,(sx,24+d),(sx,28+d))
        y=29+d
        line(im,(14,y-1),(50,y-1),1); line(im,(14,y+1),(50,y+1),1); line(im,(15,y),(50,y),3); P(im,51,y,1); P(im,14,y,1)
        line(im,(12,y-2),(13,y-1),1); P(im,13,y-2,1); P(im,12,y-1,3); P(im,11,y-2,1)
    elif v==2: # raked A-legs and a rail turned up at both ends
        y=29+d
        strut(im,(28,23+d),(22,y-1)); strut(im,(40,24+d),(46,y-1))
        line(im,(17,y-1),(50,y-1),1); line(im,(17,y+1),(50,y+1),1); line(im,(17,y),(50,y),2); line(im,(18,y),(49,y),3)
        for ex,s in ((16,-1),(51,1)):
            P(im,ex,y,1); P(im,ex,y-1,3); P(im,ex,y-2,1); P(im,ex-s,y-2,1); P(im,ex+s,y-1,1)
    else:      # three short landing legs with glowing repulsor pads
        for sx in (18,32,47):
            top=23+d if sx!=18 else 21+d
            strut(im,(sx,top),(sx,27+d))
            y=28+d
            line(im,(sx-3,y-1),(sx+3,y-1),1); line(im,(sx-2,y),(sx+2,y),11); P(im,sx-3,y,1); P(im,sx+3,y,1); line(im,(sx-2,y+1),(sx+2,y+1),12)
    # steering column from the nose up to the rider's hands (hand at frame (16,32+d) = bike row 8+d)
    hy=8+d
    if v==1:   # handlebar: column up from the nose, bar back into the gloves
        strut(im,(11,12+d),(12,hy-2))
        line(im,(10,hy-2),(16,hy-2),1); line(im,(10,hy),(16,hy),1); line(im,(10,hy-1),(16,hy-1),7); P(im,9,hy-1,1); P(im,10,hy-1,2)
    elif v==2: # yoke wheel seen edge-on, ahead of the hands, on a column from the nose
        strut(im,(10,12+d),(12,hy+1))
        cx=13
        for y in range(hy-5,hy+5):
            w=1 if abs(y-hy)>=3 else 2
            P(im,cx-w,y,1); P(im,cx+w,y,1)
            if w==2: P(im,cx-1,y,7); P(im,cx+1,y,2); P(im,cx,y,3)
            else: P(im,cx,y,7)
        P(im,cx,hy-6,1); P(im,cx,hy+5,1)
        line(im,(cx+2,hy),(16,hy),7)
    else:      # control stick: column with a kyber screen, grips into the gloves
        strut(im,(11,12+d),(12,hy))
        line(im,(8,hy-4),(13,hy-4),1); line(im,(8,hy-3),(13,hy-3),11); line(im,(8,hy-2),(13,hy-2),12); line(im,(8,hy-1),(13,hy-1),1)
        P(im,7,hy-3,1); P(im,7,hy-2,1); P(im,14,hy-3,1); P(im,14,hy-2,1)
        line(im,(13,hy),(16,hy),7); line(im,(13,hy+1),(16,hy+1),1); P(im,13,hy-1+1,1)
    return im
def compose(who,v,f,bg=(232,200,144)):
    im=Image.new('RGB',(64,64),bg)
    def M(p):
        m=Image.new('L',p.size,0); m.putdata([255 if q else 0 for q in p.getdata()]); return m
    b=make(v,f) if v else base(f); b.putpalette(BIKE.getpalette())
    im.paste(b.convert('RGB'),(0,24),M(b))
    r=rider.rider(who,2,f); im.paste(r.convert('RGB'),(0,0),M(r))
    return im
if __name__=='__main__':
    S=4
    labels=['Current','A: straight skids, handlebar','B: raked skids, yoke wheel','C: 3 legs + glow pads, stick']
    o=Image.new('RGB',(64*S*2+20+190,(64*S+10)*4),(30,30,40)); dr=ImageDraw.Draw(o)
    for v in range(4):
        y=v*(64*S+10); dr.text((6,y+128),labels[v],fill=(255,255,255))
        for k,w in enumerate(('kael','mira')):
            o.paste(compose(w,v,0).resize((64*S,64*S),0),(190+k*(64*S+20),y))
    o.save(sys.argv[1])

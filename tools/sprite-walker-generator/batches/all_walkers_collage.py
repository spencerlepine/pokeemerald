"""Every walker in the game (people + pokemon object events + net-new walkers), front and back frame: wiki art when ART_READY (green), else the game file (grey). Run from the repo root."""
import csv
from pathlib import Path
from PIL import Image, ImageDraw
W=Path('wiki'); G=Path('game')
ready={r['asset_id']:r['art_file'] for r in csv.DictReader(open(W/'mapping/art_ready.csv'))}
rows=[r for r in csv.DictReader(open(W/'database/pending_art.csv'))
      if (r['kind']=='object_events' and r['path'].split('/')[3] in ('people','pokemon')) or r['asset_id'].startswith('net:walker')]
items=[]
for r in rows:
    aid=r['asset_id']
    if aid in ready and (W/ready[aid]).exists(): src=W/ready[aid]; new=True
    elif r['path'] and (G/r['path']).exists(): src=G/r['path']; new=False
    else: continue
    name=r['sw_subject'] or r['sw_entity'] or aid
    fs=r['frame_size']
    im=Image.open(src)
    if fs: fw,fh=map(int,fs.split('x'))
    else: fw,fh=16,32
    if im.height!=fh: fh=im.height
    if im.width<fw: fw=im.width
    n=im.width//fw
    back=2 if n==6 else (1 if n>=3 else None)
    lab=(('/'.join(aid.split('/')[-2:]) if aid.split('/')[-2] in ('brendan','may') else aid.split('/')[-1]).replace('.png','') if not aid.startswith('net:') else aid[4:])
    items.append((r['path'].split('/')[3] if r['path'] else 'people', lab, name, im, fw, fh, back, new))
items.sort(key=lambda t:(t[0]!='people', max(t[4],t[5])>32, t[4]*t[5], t[1]))
S=3; CW=2*64*S//2+40; 
def tile(it):
    cat,lab,name,im,fw,fh,back,new=it
    rgba=im.convert('RGBA') if im.mode!='P' else None
    if im.mode=='P':
        im2=im.copy(); im2.info['transparency']=0; rgba=im2.convert('RGBA')
    fr=[rgba.crop((0,0,fw,fh))]+([rgba.crop((back*fw,0,back*fw+fw,fh))] if back is not None else [])
    return [f.resize((fw*S,fh*S),Image.NEAREST) for f in fr]
cols=10; cellw=2*max(32,1)*S+24; 
cells=[]
for it in items:
    fr=tile(it); w=sum(f.width for f in fr)+8*(len(fr)-1); h=max(f.height for f in fr)
    cells.append((it,fr,w,h))
# row-pack
maxw=2400; x=y=12; rowh=0; pos=[]
for it,fr,w,h in cells:
    cw=max(w,150)+16; ch=h+30
    if x+cw>maxw: x=12; y+=rowh; rowh=0
    pos.append((x,y)); x+=cw; rowh=max(rowh,ch)
H=y+rowh+12
img=Image.new('RGB',(maxw,H),(30,30,36)); d=ImageDraw.Draw(img)
for (it,fr,w,h),(x,y) in zip(cells,pos):
    cat,lab,name,im,fw,fh,back,new=it
    cw=max(w,150)
    d.rectangle((x-4,y-2,x+cw+4,y+h+26),fill=(112,192,160) if new else (150,150,150))
    xx=x+(cw-w)//2
    for f in fr:
        img.paste(f,(xx,y+h-f.height),f); xx+=f.width+8
    d.text((x,y+h+4),lab[:26],fill=(0,0,0) if new else (40,40,40))
img.save('tools/sprite-walker-generator/output/all_walkers_front_back.png')
print(len(items), sum(1 for i in items if i[7]), img.size)

import numpy as np
from PIL import Image
from chunky import cut_white, islands, mask_clean
def snap(path, w=64, h=48, colours=6, min_island=3, outline=(18,12,10), scale=2, keep_bright=True, tooth_frac=0.18, tooth_col=(240,232,212), eye_col=(250,200,60)):
    im=Image.open(path).convert('RGB'); a=np.array(im).astype(int); H,W=a.shape[:2]; g=W//w
    mb=cut_white(im)
    blk=a[:h*g,:w*g].reshape(h,g,w,g,3).transpose(0,2,1,3,4)[:,:,g//4:g-g//4,g//4:g-g//4].reshape(h,w,-1,3)
    nat=np.median(blk,axis=2).astype('uint8')
    full=a[:h*g,:w*g].reshape(h,g,w,g,3).transpose(0,2,1,3,4).reshape(h,w,-1,3)
    fl=full@np.array([0.3,0.59,0.11]); nl=nat@np.array([0.3,0.59,0.11])
    sat=full.max(-1)-full.min(-1)
    tooth=((fl>200).mean(-1)>=tooth_frac)&(nl<150)            # light specks in a dark cell: teeth, claws
    glow=(((sat>90)&(fl>120)).mean(-1)>=0.15)&(nl<170)       # saturated specks: eyes
    mask=mb[:h*g,:w*g].reshape(h,g,w,g).mean(axis=(1,3))>0.5
    mask=mask_clean(mask,6)
    px=nat[mask]
    q=Image.fromarray(px.reshape(-1,1,3)).quantize(colours,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    pal=np.array(q.getpalette()[:colours*3]).reshape(-1,3)
    ids=np.array(q).reshape(-1)
    # order by luminance so outline/merge logic is stable
    lum=pal@[0.3,0.59,0.11]; order=np.argsort(lum); rank=np.argsort(order)
    idx=np.zeros((h,w),int); idx[mask]=rank[ids]; pal=pal[order]
    brightest=colours-1
    keep=(idx==brightest) if keep_bright else np.zeros_like(mask)
    merged=islands(idx.copy(),mask,min_island)
    if keep_bright:  # teeth and glints are allowed to be tiny
        merged[keep]=brightest
    out=np.zeros((h,w,4),'uint8'); out[mask,:3]=pal[merged[mask]]; out[mask,3]=255
    out[mask&tooth,:3]=tooth_col
    if eye_col: out[mask&glow&~tooth,:3]=eye_col
    edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    out[edge,:3]=outline
    return Image.fromarray(out).resize((w*scale,h*scale),Image.NEAREST)

"""Flat cel drawing -> pixel sprite: page cut, shrink (box), quantise, merge islands (lightest kept), coloured outline."""
import numpy as np
from PIL import Image, ImageFilter
from chunky import cut_white, islands, mask_clean
def flatpx(path, w=128, h=96, colours=12, min_island=3, smooth=3, outline_mul=0.4, sat=1.15, contrast=1.08, keep_light=True, passes=1, outline=None, accent=(240,234,216), eye=None):
    from PIL import ImageEnhance
    im=Image.open(path).convert('RGB'); mb=cut_white(im,thr=226)
    sm=im.filter(ImageFilter.MedianFilter(smooth)) if smooth else im
    sm=ImageEnhance.Color(sm).enhance(sat); sm=ImageEnhance.Contrast(sm).enhance(contrast)
    rgb=np.array(sm.resize((w,h),Image.BOX))
    mask=np.array(Image.fromarray((mb*255).astype('uint8')).resize((w,h),Image.BOX))>127
    wn=np.array(im.resize((w,h),Image.BOX)).min(-1)>228; mask&=~wn
    mask=mask_clean(mask,8)
    q=Image.fromarray(rgb[mask].reshape(-1,1,3)).quantize(colours,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
    pal=np.array(q.getpalette()[:colours*3]).reshape(-1,3); ids=np.array(q).reshape(-1)
    order=np.argsort(pal@[0.3,0.59,0.11]); rank=np.argsort(order); pal=pal[order]
    idx=np.zeros((h,w),int); idx[mask]=rank[ids]
    light=(idx>=colours-1)&mask
    idx=islands(idx,mask,min_island)
    for _ in range(passes):  # straighten ragged shade borders: 3x3 majority (needs 5 of 9)
        p=np.pad(idx,1,mode='edge'); pm=np.pad(mask,1); new=idx.copy()
        for y in range(h):
            for x in range(w):
                if not mask[y,x]: continue
                win=p[y:y+3,x:x+3][pm[y:y+3,x:x+3]]; v,c=np.unique(win,return_counts=True)
                if c.max()>=5: new[y,x]=v[c.argmax()]
        idx=new
    idx=islands(idx,mask,min_island)
    if keep_light: idx[light]=colours-1
    out=np.zeros((h,w,4),'uint8'); out[mask,:3]=pal[idx[mask]]; out[mask,3]=255
    # teeth, claws, eye glints: bright specks of the drawing (any share of the cell) become one accent
    big=np.array(im.convert('L')); g=big.shape[1]//w
    cells=big[:h*g,:w*g].reshape(h,g,w,g).transpose(0,2,1,3).reshape(h,w,-1)
    spark=mask&((cells>215).mean(-1)>=0.2)&(rgb@np.array([0.3,0.59,0.11])<200)
    sat=np.array(im.convert('HSV'))[...,1]; vv=np.array(im.convert('HSV'))[...,2]
    sc=((sat>150)&(vv>170))[:h*g,:w*g].reshape(h,g,w,g).transpose(0,2,1,3).reshape(h,w,-1).mean(-1)>=0.3
    out[spark,:3]=accent
    if eye: out[mask&sc&~spark,:3]=eye
    edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    oc=tuple(int(c*outline_mul) for c in pal[0]) if outline is None else outline
    out[edge,:3]=oc
    return Image.fromarray(out)

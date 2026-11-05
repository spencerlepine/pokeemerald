"""Drawing -> clean GBA-style sprite: materials by colour, 3 hue-shifted tones each, merged islands,
coloured outline with a lit-edge highlight. No noise, no stray pixels."""
import colorsys
import numpy as np
from PIL import Image, ImageFilter
from chunky import cut_white, islands, mask_clean

def ramp_from(c, n=3, dark=0.55, light=1.3, hue_shift=0.04, val_mul=1.0):
    r,g,b=[x/255 for x in c]; h,s,v=colorsys.rgb_to_hsv(r,g,b); v*=val_mul
    out=[]
    for k in range(n):
        t=k/(n-1) if n>1 else 0.5          # 0 shadow .. 1 light
        f=dark+(light-dark)*t
        hh=(h+(-hue_shift if t<0.5 else hue_shift)*abs(t-0.5)*2)%1  # shadows cooler, lights warmer
        ss=min(1,s*(1.25-0.5*t)); vv=min(1,v*f)
        out.append(tuple(int(round(x*255)) for x in colorsys.hsv_to_rgb(hh,ss,vv)))
    return out

def matcel(path, w=128, h=96, materials=4, tones=3, min_island=4, smooth=5, keep_small=('light',),
           outline_dark=0.35, val_mul=1.0, rim=True, sat_mul=1.0, accent_light=235, crop=None):
    im=Image.open(path).convert('RGB')
    if crop: im=im.crop(crop)
    mb=cut_white(im,thr=226)
    sm=im.filter(ImageFilter.MedianFilter(smooth))
    rgb=np.array(sm.resize((w,h),Image.BOX)).astype(float)
    mask=np.array(Image.fromarray((mb*255).astype('uint8')).resize((w,h),Image.BOX))>127
    wn=np.array(im.resize((w,h),Image.BOX)).min(-1)>225; mask&=~wn
    mask=mask_clean(mask,8)
    # materials: cluster on a strongly smoothed copy so shading doesn't split a material
    big=np.array(im.filter(ImageFilter.MedianFilter(15)).resize((w,h),Image.BOX)).astype(float)
    q=Image.fromarray(big[mask].astype('uint8').reshape(-1,1,3)).quantize(materials,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    mat=np.full((h,w),-1); mat[mask]=np.array(q).reshape(-1)
    mat=islands(np.where(mask,mat,0),mask,min_island*2)
    lum=rgb@np.array([0.3,0.59,0.11])
    out=np.zeros((h,w,4),'uint8'); tone=np.zeros((h,w),int)
    ramps={}
    for m in np.unique(mat[mask]):
        sel=mask&(mat==m)
        mc=np.median(rgb[sel],axis=0)
        mc=np.clip(mc*np.array([1,1,1]),0,255)
        hsv=colorsys.rgb_to_hsv(*(mc/255)); mc=np.array(colorsys.hsv_to_rgb(hsv[0],min(1,hsv[1]*sat_mul),hsv[2]))*255
        ramps[m]=ramp_from(mc,tones,val_mul=val_mul)
        l=lum[sel]; qs=np.quantile(l,np.linspace(0,1,tones+1)[1:-1]) if sel.sum()>tones*3 else []
        tone[sel]=np.searchsorted(qs,l) if len(qs) else tones//2
    key=mat*10+tone; key[~mask]=-1
    key=islands(key,mask,min_island)
    for k in np.unique(key[mask]):
        m,t=divmod(k,10); out[mask&(key==k),:3]=ramps[m][t]
    out[mask,3]=255
    # teeth / eye glints: bright specks in the drawing stay as an off-white accent
    hi=np.array(im.resize((w,h),Image.BOX)).astype(float)@np.array([0.3,0.59,0.11])
    acc=mask&(hi>accent_light)
    out[acc,:3]=(244,236,214)
    edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    # coloured outline: darkest tone of the material, darkened
    for m in ramps:
        d=tuple(int(c*outline_dark) for c in ramps[m][0])
        out[edge&(mat==m),:3]=d
    if rim:  # light comes from the upper left: those edges get the light tone instead of the outline
        lit=edge&(np.roll(~mask,1,0)|np.roll(~mask,1,1))&~(np.roll(~mask,-1,0)|np.roll(~mask,-1,1))
        for m in ramps:
            out[lit&(mat==m)&(tone>=1),:3]=ramps[m][0]
    return Image.fromarray(out)

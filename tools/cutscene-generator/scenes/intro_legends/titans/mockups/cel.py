"""Cel-shaded pixel art from a cut-out reference: value bands on a hand-picked ramp, majority clean-up, outline."""
import numpy as np
from PIL import Image, ImageFilter
from px import load_cut

def hexs(*h): return [tuple(int(x[i:i+2],16) for i in (1,3,5)) for x in h]

def smooth_small(im, w, h):
    a=np.array(im).astype(float); al=a[...,3:]/255; a[...,:3]*=al
    pm=Image.fromarray(np.dstack([a[...,:3],a[...,3]]).clip(0,255).astype('uint8'),'RGBA')
    s=np.array(pm.resize((w,h),Image.LANCZOS)).astype(float)
    alpha=s[...,3]; rgb=s[...,:3]/np.maximum(alpha[...,None]/255,1e-3)
    return rgb.clip(0,255), alpha

def majority(idx, mask, it=2):
    H,W=idx.shape
    for _ in range(it):
        p=np.pad(idx,1,mode='edge'); pm=np.pad(mask,1)
        out=idx.copy()
        for y in range(H):
            for x in range(W):
                if not mask[y,x]: continue
                win=p[y:y+3,x:x+3][pm[y:y+3,x:x+3]]
                vals,c=np.unique(win,return_counts=True)
                if c.max()>=5 and vals[c.argmax()]!=idx[y,x]: out[y,x]=vals[c.argmax()]
        idx=out
    return idx

def cel(im, w, h, ramp, outline=(20,14,12), gamma=1.0, blur=0, light_bias=0.0, clean=2, selout=True, alpha_thr=110):
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    rgb,alpha=smooth_small(im,w,h); mask=alpha>alpha_thr
    lum=(0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2])/255
    lum=lum**gamma
    v=lum[mask]; n=len(ramp)
    qs=np.quantile(v,np.linspace(0,1,n+1)[1:-1]+light_bias)
    idx=np.zeros(lum.shape,int); idx[mask]=np.searchsorted(qs,v)
    idx=majority(idx,mask,clean)
    out=np.zeros((h,w,4),'uint8')
    pal=np.array(ramp)
    out[mask,:3]=pal[idx[mask]]; out[mask,3]=255
    edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    if selout:  # lit edges get a dark-ramp outline instead of black (selective outline)
        lit=edge&(idx>=n-2); out[edge,:3]=outline; out[lit,:3]=pal[1]
    else: out[edge,:3]=outline
    return Image.fromarray(out)

"""Form-shaded chunky pixel art: shade from the silhouette's volume (one light, upper left), mixed with the
source's own values, banded onto a 5-tone ramp, small islands merged, selective outline, accents kept."""
import numpy as np
from PIL import Image, ImageFilter
from chunky import cut_white, islands, mask_clean

def dist(mask, it=200):
    d=np.zeros(mask.shape,float); m=mask.copy()
    for _ in range(it):
        if not m.any(): break
        d+=m
        m=m&np.roll(m,1,0)&np.roll(m,-1,0)&np.roll(m,1,1)&np.roll(m,-1,1)
    return d

def form_shade(mask, light=(-0.6,-0.8,0.9), blur=2.0, power=0.5):
    h=dist(mask)**power
    hi=Image.fromarray((h/h.max()*255).astype('uint8')).filter(ImageFilter.GaussianBlur(blur))
    h=np.array(hi).astype(float)/255*np.sqrt(mask.sum()/np.pi)*0.6
    gy,gx=np.gradient(h)
    n=np.dstack([-gx,-gy,np.ones_like(h)]); n/=np.linalg.norm(n,axis=-1,keepdims=True)
    L=np.array(light,float); L/=np.linalg.norm(L)
    return (n@L).clip(0,1)

def draw(src, w, h, ramp, mix=0.6, up=4, min_island=4, dark_cut=0.18, light_cut=0.86, accent=None,
         outline=(18,12,10), rim=True, scale=2, smooth=5, light=(-0.6,-0.8,0.9)):
    im=src.convert('RGB'); mbig=cut_white(im)
    W,H=w*up,h*up
    m=np.array(Image.fromarray((mbig*255).astype('uint8')).resize((W,H),Image.BOX))>140
    sm=im.filter(ImageFilter.MedianFilter(smooth)) if smooth else im
    rgb=np.array(sm.resize((W,H),Image.LANCZOS)).astype(float)
    lum=(0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2])/255
    v=lum[m]; lo,hi=np.quantile(v,0.03),np.quantile(v,0.97); ln=((lum-lo)/(hi-lo+1e-6)).clip(0,1)
    sh=form_shade(m,light)
    t=mix*sh+(1-mix)*ln
    # down to native
    tn=np.array(Image.fromarray((t*255).astype('uint8')).resize((w,h),Image.BOX)).astype(float)/255
    lnn=np.array(Image.fromarray((ln*255).astype('uint8')).resize((w,h),Image.BOX)).astype(float)/255
    mask=np.array(Image.fromarray((m*255).astype('uint8')).resize((w,h),Image.BOX))>127
    mask=mask_clean(mask,6)
    n=len(ramp)
    vv=tn[mask]; qs=np.quantile(vv,np.linspace(0,1,n+1)[1:-1])
    idx=np.zeros((h,w),int); idx[mask]=np.searchsorted(qs,vv)
    # deep darks of the source (mouth, eye sockets, folds) stay darkest
    idx[mask&(lnn<dark_cut)]=0
    idx=islands(idx,mask,min_island)
    out=np.zeros((h,w,4),'uint8'); pal=np.array(ramp)
    out[mask,:3]=pal[idx[mask]]; out[mask,3]=255
    if accent is not None:  # small bright source spots (teeth, eye glints) as an accent colour
        acc=mask&(lnn>light_cut)&(idx<=1)
        out[acc,:3]=accent
    edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    out[edge,:3]=outline
    if rim:  # lit side of the outline gets the second-darkest tone (selective outline)
        lit=edge&(np.roll(~mask,1,0)|np.roll(~mask,1,1))&(idx>=n-2)
        out[lit,:3]=pal[1]
    s=Image.fromarray(out)
    return s.resize((w*scale,h*scale),Image.NEAREST)

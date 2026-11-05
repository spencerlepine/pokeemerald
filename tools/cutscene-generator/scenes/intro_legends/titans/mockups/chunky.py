"""2x chunky cel pixel art: smooth the source, band its values onto a ramp, merge small islands, outline."""
import numpy as np
from PIL import Image, ImageFilter
from cel import hexs

def cut_white(im, thr=232):
    a=np.array(im.convert('RGB')).astype(int); white=a.min(-1)>thr
    small=np.array(Image.fromarray(np.where(white,255,0).astype('uint8')).resize((white.shape[1]//4,white.shape[0]//4),Image.BOX))>250
    bg=np.zeros_like(small); bg[0]=small[0]; bg[-1]=small[-1]; bg[:,0]=small[:,0]; bg[:,-1]=small[:,-1]
    while True:
        n=(bg|np.roll(bg,1,0)|np.roll(bg,-1,0)|np.roll(bg,1,1)|np.roll(bg,-1,1))&small
        if (n==bg).all(): break
        bg=n
    big=np.array(Image.fromarray((bg*255).astype('uint8')).resize((white.shape[1],white.shape[0]),Image.NEAREST))>0
    return ~big

def islands(idx, mask, min_size):
    """Merge every same-tone region smaller than min_size into its most common neighbouring tone."""
    H,W=idx.shape
    changed=True
    while changed:
        changed=False; seen=np.zeros_like(mask)
        for y in range(H):
            for x in range(W):
                if not mask[y,x] or seen[y,x]: continue
                t=idx[y,x]; stack=[(y,x)]; reg=[]; seen[y,x]=1; nb={}
                while stack:
                    cy,cx=stack.pop(); reg.append((cy,cx))
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<H and 0<=nx<W and mask[ny,nx]:
                            if idx[ny,nx]==t and not seen[ny,nx]: seen[ny,nx]=1; stack.append((ny,nx))
                            elif idx[ny,nx]!=t: nb[idx[ny,nx]]=nb.get(idx[ny,nx],0)+1
                if len(reg)<min_size and nb:
                    new=max(nb,key=nb.get)
                    for cy,cx in reg: idx[cy,cx]=new
                    changed=True
    return idx

def mask_clean(mask, min_size=4):
    """Drop tiny islands of body and fill tiny holes."""
    from PIL import ImageDraw
    m=mask.copy()
    for val in (True,False):
        idx=np.where(m,1,0); idx2=islands(np.where(m,1,0)+0, np.ones_like(m), min_size)
        m=idx2==1
    return m

def chunky(src, w, h, ramp, smooth=6, min_island=4, gamma=1.0, outline=(18,12,10), scale=2, bias=0.0):
    """src: RGB on white, any size. w,h: native size before the 2x."""
    im=src.convert('RGB')
    mask_big=cut_white(im)
    sm=im.filter(ImageFilter.MedianFilter(2*(smooth//2)+1)) if smooth else im
    rgb=np.array(sm.resize((w,h),Image.LANCZOS)).astype(float)
    mask=np.array(Image.fromarray((mask_big*255).astype('uint8')).resize((w,h),Image.BOX))>140
    mask=mask_clean(mask,6)
    lum=((0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2])/255)**gamma
    v=lum[mask]; n=len(ramp)
    qs=np.quantile(v,np.clip(np.linspace(0,1,n+1)[1:-1]+bias,0.01,0.99))
    idx=np.zeros((h,w),int); idx[mask]=np.searchsorted(qs,v)
    idx=islands(idx,mask,min_island)
    out=np.zeros((h,w,4),'uint8'); pal=np.array(ramp)
    out[mask,:3]=pal[idx[mask]]; out[mask,3]=255
    edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    out[edge,:3]=outline
    s=Image.fromarray(out)
    return s.resize((w*scale,h*scale),Image.NEAREST)

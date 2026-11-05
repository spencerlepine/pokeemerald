"""Reference picture -> pixel sprite at scene size (no model): downscale, quantise, outline."""
import numpy as np
from PIL import Image, ImageFilter
from mock import *

def load_cut(path, flip=False, crop=None):
    im=Image.open(path).convert('RGBA')
    if crop: im=im.crop(crop)
    a=np.array(im); ys,xs=np.where(a[...,3]>40); im=im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im

def pixelize(im, w=None, h=None, colours=14, outline=(24,20,20), contrast=1.0, sat=1.0, gamma=1.0, keep_alpha=110):
    if w and h: k=min(w/im.width,h/im.height)
    elif h: k=h/im.height
    else: k=w/im.width
    tw,th=max(1,round(im.width*k)),max(1,round(im.height*k))
    # premultiplied resize to avoid halo
    a=np.array(im).astype(float); al=a[...,3:]/255; a[...,:3]*=al
    pm=Image.fromarray(np.dstack([a[...,:3],a[...,3]]).clip(0,255).astype('uint8'),'RGBA')
    s=np.array(pm.resize((tw,th),Image.LANCZOS)).astype(float)
    alpha=s[...,3]; rgb=s[...,:3]/np.maximum(alpha[...,None]/255,1e-3)
    mask=alpha>keep_alpha
    from PIL import ImageEnhance
    rgbim=Image.fromarray(rgb.clip(0,255).astype('uint8'))
    if contrast!=1: rgbim=ImageEnhance.Contrast(rgbim).enhance(contrast)
    if sat!=1: rgbim=ImageEnhance.Color(rgbim).enhance(sat)
    rgb=np.array(rgbim).astype(float)
    if gamma!=1: rgb=255*(rgb/255)**gamma
    px=rgb[mask]
    q=Image.fromarray(px.reshape(-1,1,3).clip(0,255).astype('uint8')).quantize(colours-1 if outline else colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    qc=np.array(q.convert('RGB')).reshape(-1,3)
    out=np.zeros((th,tw,4),'uint8'); out[mask,:3]=qc; out[mask,3]=255
    if outline:
        m=mask.copy(); edge=m & ~(np.roll(m,1,0)&np.roll(m,-1,0)&np.roll(m,1,1)&np.roll(m,-1,1))
        out[edge,:3]=outline
    # despeckle: lone pixels -> most common neighbour
    return Image.fromarray(out)

def white_cut(path, thr=235, min_px=400):
    """Cut a picture off a white page: flood the near-white from the border, keep big parts."""
    from PIL import ImageDraw
    im=Image.open(path).convert('RGB'); a=np.array(im).astype(int)
    white=(a.min(axis=-1)>thr)
    m=Image.fromarray((white*255).astype('uint8'))
    # flood fill near-white from every border pixel that is white
    seed=Image.new('L',m.size,0); W,H=m.size
    fill=np.zeros_like(white)
    mi=m.copy()
    for (x,y) in [(0,0),(W-1,0),(0,H-1),(W-1,H-1),(W//2,0),(W//2,H-1),(0,H//2),(W-1,H//2)]:
        if white[y,x]: ImageDraw.floodfill(mi,(x,y),128)
    bg=np.array(mi)==128
    alpha=np.where(bg,0,255).astype('uint8')
    out=np.dstack([a.astype('uint8'),alpha])
    return Image.fromarray(out,'RGBA')

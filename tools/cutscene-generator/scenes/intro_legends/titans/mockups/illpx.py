"""Drawing -> 2x chunky pixel art: cut the white page, smooth, shrink, 6 colours, merge islands, outline."""
import numpy as np
from PIL import Image, ImageFilter
from chunky import cut_white, islands, mask_clean
def illpx(path, w=64, h=48, colours=6, min_island=3, outline=(16,10,10), scale=2, smooth=3, keep_light=True):
    im=Image.open(path).convert('RGB'); mb=cut_white(im,thr=226)
    sm=im.filter(ImageFilter.MedianFilter(smooth))
    rgb=np.array(sm.resize((w,h),Image.BOX))
    mask=np.array(Image.fromarray((mb*255).astype('uint8')).resize((w,h),Image.BOX))>127
    # enclosed white pockets (under a tail, between legs) are background too
    wn=np.array(im.resize((w,h),Image.BOX)).min(-1)>225
    mask&=~wn
    mask=mask_clean(mask,6)
    q=Image.fromarray(rgb[mask].reshape(-1,1,3)).quantize(colours,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    pal=np.array(q.getpalette()[:colours*3]).reshape(-1,3); ids=np.array(q).reshape(-1)
    order=np.argsort(pal@[0.3,0.59,0.11]); rank=np.argsort(order); pal=pal[order]
    idx=np.zeros((h,w),int); idx[mask]=rank[ids]
    light=idx==colours-1
    idx=islands(idx,mask,min_island)
    if keep_light:  # teeth: the lightest colour may stay as single pixels
        # restore only light pixels sitting next to the darkest colour (fangs in a mouth)
        dk=(idx==0); near=np.roll(dk,1,0)|np.roll(dk,-1,0)|np.roll(dk,1,1)|np.roll(dk,-1,1)
        idx[light&near&mask]=colours-1
    out=np.zeros((h,w,4),'uint8'); out[mask,:3]=pal[idx[mask]]; out[mask,3]=255
    edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
    out[edge,:3]=outline
    return Image.fromarray(out).resize((w*scale,h*scale),Image.NEAREST)

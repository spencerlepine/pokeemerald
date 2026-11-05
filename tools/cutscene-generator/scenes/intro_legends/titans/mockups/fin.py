import numpy as np
from PIL import Image
def finish(path, W=144, H=96, colours=14, outline=(24,20,20), white=232):
    a=np.array(Image.open(path).convert('RGB')).astype(int)
    g=a.shape[1]//W
    a=a[:H*g,:W*g].reshape(H,g,W,g,3)
    c=a[:,g//4:g-g//4,:,g//4:g-g//4].transpose(0,2,1,3,4).reshape(H,W,-1,3)
    nat=np.median(c,axis=2).astype('uint8')
    bgm=np.all(nat>white,axis=-1)
    bg=np.zeros_like(bgm); bg[0]=bgm[0]; bg[-1]=bgm[-1]; bg[:,0]=bgm[:,0]; bg[:,-1]=bgm[:,-1]
    while True:
        n=bg|np.roll(bg,1,0)|np.roll(bg,-1,0)|np.roll(bg,1,1)|np.roll(bg,-1,1); n&=bgm
        if (n==bg).all(): break
        bg=n
    fg=~bg
    # drop specks: pixels with <2 fg neighbours
    nb=sum(np.roll(np.roll(fg,dy,0),dx,1) for dy in (-1,0,1) for dx in (-1,0,1))-fg
    fg&=nb>=2
    px=nat[fg]
    q=Image.fromarray(px.reshape(-1,1,3)).quantize(colours-1, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out=np.zeros((H,W,4),'uint8'); out[fg,:3]=np.array(q.convert('RGB')).reshape(-1,3); out[fg,3]=255
    if outline:
        m=fg; edge=m&~(np.roll(m,1,0)&np.roll(m,-1,0)&np.roll(m,1,1)&np.roll(m,-1,1)); edge[-1,:]&=False
        out[edge,:3]=outline
    return Image.fromarray(out)

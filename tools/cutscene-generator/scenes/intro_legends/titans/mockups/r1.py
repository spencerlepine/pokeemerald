from mock import *
sand, sea, sky = bg_sand(), bg_sea(), bg_sky()
def cutbelow(sp, ycut):
    a=np.array(sp); a[ycut:,:,3]=0; return Image.fromarray(a)
P=[]
P.append(('E  Emerald Groudon (for scale)', place(sand, emerald_crop('render_groudon',(118,123,289,215)), 26, 2)))
k=sil('groudon',2.4); P.append((f'K1  full body 2.4x ({k.width}x{k.height})', place(sand,k,40,1)))
k=sil('groudon',3.2); P.append((f'K2  big 3.2x, tail off-frame ({k.width}x{k.height})', place(sand,k,8,-14)))
k=sil('groudon',4.2); P.append((f'K3  head-and-neck close 4.2x', place(sand,k,-10,-8)))
k=sil('groudon',3.0); P.append((f'K4  sand-swimmer: body under the dunes 3.0x', place(sand,cutbelow(k,78),20,8)))
k=sil('groudon',1.8); P.append((f'K5  distant 1.8x ({k.width}x{k.height})', place(sand,k,70,20)))
sheet(P,'r1/krayt_sizes.png')
P=[]
P.append(('E  Emerald Kyogre (for scale)', place(sea, emerald_crop('render_kyogre',(112,80,240,176)), 70, 0)))
s=sil('kyogre',1.5); P.append((f'S1  full body 1.5x ({s.width}x{s.height})', place(sea,s,76,0)))
s=sil('kyogre',2.0); P.append((f'S2  2.0x, feet off-frame ({s.width}x{s.height})', place(sea,s,62,-14)))
s=sil('kyogre',2.8); P.append((f'S3  head close 2.8x', place(sea,s,30,-40)))
s=sil('kyogre',1.15); P.append((f'S4  small 1.15x, room for bubbles', place(sea,s,95,12)))
s=sil('kyogre',1.6,flip=True); P.append((f'S5  mirrored 1.6x, facing right', place(sea,s,70,-3)))
sheet(P,'r1/sando_sizes.png')
P=[]
a=np.array(Image.open(f'{R}/render_rayquaza.png').convert('RGB'))[32:128,0:240]
m=~((a[...,0]>200)&(a[...,1]<60)&(a[...,2]>200))&~np.all(a==a[2,2],axis=-1)
ray=Image.fromarray(a).convert('RGBA'); ray.putalpha(Image.fromarray((m*255).astype('uint8')))
P.append(('E  Emerald Rayquaza (for scale)', place(sky,ray,0,0)))
e=sil('rayquaza',1.4); P.append((f'X1  1.4x ({e.width}x{e.height})', place(sky,e,85,4)))
e=sil('rayquaza',1.75); P.append((f'X2  1.75x, fills the band ({e.width}x{e.height})', place(sky,e,74,0)))
e=sil('rayquaza',2.6); P.append(('X3  2.6x, rising out of the clouds', place(sky,cutbelow(e,110),60,-10)))
e=sil('rayquaza',3.6); P.append(('X4  mouth close-up 3.6x', place(sky,e,40,-60)))
e=sil('rayquaza',1.0); P.append(('X5  distant 1.0x', place(sky,e,150,8)))
sheet(P,'r1/exogorth_sizes.png')

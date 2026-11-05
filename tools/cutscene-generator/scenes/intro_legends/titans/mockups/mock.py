"""Round 1 silhouette mockups: size/position of the three titans in the real scene-3 window."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = '/tmp/claude-0/-home-user/d213e348-4be7-55cb-95dd-5b2b404be070/scratchpad'
G = '/home/user/pokeemerald/game/graphics/pokemon'
R = '/home/user/pokeemerald/tools/cutscene-generator/scenes/intro_legends/reference/emerald'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
MAG = (255, 0, 239)


def frame(i):
    return np.array(Image.open(f'{S}/frames/f{i:03d}.png').convert('RGB'))[32:128].copy()


def clean_tile(a, period):
    """Replace placeholder magenta with the same pixel one tile period away."""
    m = (a[..., 0] > 200) & (a[..., 1] < 60) & (a[..., 2] > 200)
    for dx in (period, -period, 2 * period, -2 * period):
        sh = np.roll(a, -dx, axis=1)
        shm = np.roll(m, -dx, axis=1)
        fix = m & ~shm
        a[fix] = sh[fix]
        m = m & ~fix
    return a


def bg_sand():
    return clean_tile(frame(22), 64)


def bg_sea():
    return clean_tile(frame(70), 64)


def bg_sky():
    a = frame(190)
    sky = a[5, 120].copy()
    cloud = a[95, 5].copy()
    # placeholder ring lives in x 90..160, y 14..82 of the window; clouds don't reach there except bottom
    sub = a[10:84, 88:162]
    m = np.all(sub == cloud, axis=-1)
    sub[m] = sky
    return a


def sil(species, scale, flip=False, col=(16, 16, 24)):
    im = Image.open(f'{G}/{species}/front.png').convert('RGBA')
    a = np.array(im)
    key = a[0, 0, :3]
    mask = ~np.all(a[..., :3] == key, axis=-1)
    if im.mode == 'RGBA' and a[..., 3].min() < 255:
        mask &= a[..., 3] > 0
    ys, xs = np.where(mask)
    mask = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    m = Image.fromarray((mask * 255).astype('uint8'))
    if flip:
        m = m.transpose(Image.FLIP_LEFT_RIGHT)
    m = m.resize((round(m.width * scale), round(m.height * scale)), Image.NEAREST)
    out = Image.new('RGBA', m.size, col + (255,))
    out.putalpha(m)
    return out


def emerald_crop(name, box):
    a = np.array(Image.open(f'{R}/{name}.png').convert('RGB'))
    x0, y0, x1, y1 = box
    c = a[y0:y1 + 1, x0:x1 + 1]
    m = ~((c[..., 0] > 200) & (c[..., 1] < 60) & (c[..., 2] > 200))
    im = Image.fromarray(c).convert('RGBA')
    im.putalpha(Image.fromarray((m * 255).astype('uint8')))
    return im


def place(bg, spr, x, y):
    im = Image.fromarray(bg).convert('RGBA')
    im.alpha_composite(spr, (0, 0)) if False else None
    layer = Image.new('RGBA', im.size)
    layer.paste(spr, (x, y), spr)
    im.alpha_composite(layer)
    return im.convert('RGB')


def sheet(panels, path, cols=2, scale=2):
    w, h = 240 * scale, 96 * scale
    rows = (len(panels) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + 12) + 12, rows * (h + 34) + 12), (24, 24, 28))
    d = ImageDraw.Draw(out)
    for k, (label, im) in enumerate(panels):
        x = 12 + (k % cols) * (w + 12)
        y = 12 + (k // cols) * (h + 34)
        d.text((x, y), label, fill=(240, 240, 240), font=FONT)
        out.paste(im.resize((w, h), Image.NEAREST), (x, y + 20))
    out.save(path)


def sprite_size(sp):
    return sp.size

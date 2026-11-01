import sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '.')
import ships
bg = Image.open('sys.argv[1]').convert('RGB')
font = ImageFont.load_default()
def sprite_rgba(mask, scale=1.0):
    m = mask if scale == 1 else mask.resize((max(1, int(64 * scale)), max(1, int(32 * scale))), Image.NEAREST)
    im = Image.new('RGBA', m.size, ships.COL + (255,)); im.putalpha(m); return im
cw, ch = 300, 345
out = Image.new('RGB', (cw * 5, ch * 2 + 30), (24, 24, 32)); d = ImageDraw.Draw(out)
for row, (title, group) in enumerate((('Hero ship options', ships.HERO), ('Imperial ship options', ships.IMP))):
    for i, (name, fn) in enumerate(group):
        mask = fn()
        pass
        x0, y0 = i * cw + 22, row * ch + 30
        d.text((x0, y0 - 18), f"{'AB'[row]}{i+1}. {name}", fill=(240, 240, 240), font=font)
        tile = Image.new('RGB', (64, 32), (200, 196, 210)); tile.paste(sprite_rgba(mask), (0, 0), sprite_rgba(mask))
        out.paste(tile.resize((256, 128), Image.NEAREST), (x0, y0))
        scene = bg.copy()
        for sc, pos in ((1.0, (88, 40)), (0.5, (30, 100)), (0.3, (180, 112))):
            s = sprite_rgba(mask, sc); scene.paste(s, pos, s)
        out.paste(scene.resize((256, 170), Image.NEAREST), (x0, y0 + 136))
d.text((10, ch * 2 + 8), "Top of each cell: the 64x32 sprite at 4x. Below: in scene 1 at full, half and 0.3 size (the sprite shrinks as it flies off).", fill=(200, 200, 200), font=font)
out.save('sys.argv[2]'); print(out.size)

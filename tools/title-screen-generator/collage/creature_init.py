"""Small-creature start images for the title collage: the wiki front pic shrunk to TARGET px tall on the creature model's
96x96 / 8x grid (768 canvas, white), so an image-to-image take at denoise ~0.6 comes back compact (the 64-cell takes
stood as tall as the people).   python3 creature_init.py OUT_DIR species...  """
import os, sys
from PIL import Image
WIKI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "wiki", "art", "graphics", "pokemon")
TARGET = 38

def init(species, out):
    im = Image.open(os.path.join(WIKI, species, "front.png"))
    a = im.point(lambda v: 0 if v == 0 else 255, "L")
    im = im.convert("RGBA"); im.putalpha(a)
    im = im.crop((0, 0, 64, 64)); im = im.crop(im.getbbox())
    k = TARGET / max(im.size)
    im = im.resize((max(1, round(im.size[0] * k)), max(1, round(im.size[1] * k))), Image.NEAREST)
    cell = Image.new("RGBA", (96, 96), (255, 255, 255, 255))
    cell.paste(im, ((96 - im.size[0]) // 2, 96 - 16 - im.size[1]), im)
    cell = cell.convert("RGB").resize((768, 768), Image.NEAREST)
    p = os.path.join(out, species + "_small_init.png"); cell.save(p); return p

if __name__ == "__main__":
    for sp in sys.argv[2:]:
        print(init(sp, sys.argv[1]))

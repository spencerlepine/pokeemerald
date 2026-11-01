"""Three logo variants: STAR WARS wordmark (original lettering) for the 256x64 logo BG."""
from PIL import Image
from glyphs import big_mask
from fx import *

def hexc(s):
    s = s.lstrip("#"); return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

def logo_steel():
    m = pad(big_mask("STAR WARS", 3, 5), 4)
    img = Image.new("RGBA", m.size, (0, 0, 0, 0))
    o1, o2 = dilate(m, 1), dilate(m, 2)
    paint(img, dilate(o2, 1), hexc("0a3a1e"))      # dark green halo
    paint(img, o2, hexc("38d870"))                  # kyber glow
    paint(img, o1, hexc("0c1428"))                  # navy outline
    gradient_fill(img, m, [hexc(c) for c in ("ffffff", "e8eef4", "c8d4e0", "a0b0c4", "7c8ca8", "98a8bc")])
    paint(img, edge(m, 0, -1), hexc("ffffff"))
    paint(img, edge(m, 0, 1), hexc("4c5c78"))
    return img

def logo_gold():
    m = pad(big_mask("STAR WARS", 3, 5), 5)
    img = Image.new("RGBA", m.size, (0, 0, 0, 0))
    o1 = dilate(m, 1)
    shadow = shift(dilate(m, 2), 2, 3)
    paint(img, shadow, hexc("080404"))
    paint(img, dilate(m, 2), hexc("5a2c08"))
    paint(img, o1, hexc("1c0c04"))
    gradient_fill(img, m, [hexc(c) for c in ("fff8c8", "ffe070", "f8c030", "e89818", "c87010", "a05008")])
    paint(img, edge(m, 0, -1), hexc("fffff0"))
    paint(img, edge(m, -1, 0), hexc("fff0a0"))
    paint(img, edge(m, 0, 1), hexc("6c3004"))
    return img

def logo_arch():
    m = pad(arch(big_mask("STAR WARS", 3, 5), 6), 4)
    img = Image.new("RGBA", m.size, (0, 0, 0, 0))
    paint(img, shift(dilate(m, 2), 1, 2), hexc("04081c"))
    paint(img, dilate(m, 2), hexc("1838a0"))
    paint(img, dilate(m, 1), hexc("081040"))
    gradient_fill(img, m, [hexc(c) for c in ("ffffff", "d8f4ff", "a8e0ff", "70c0f8", "4890e8", "3070d0")])
    paint(img, edge(m, 0, -1), hexc("ffffff"))
    paint(img, edge(m, 0, 1), hexc("203c98"))
    return img

VARIANTS = {"steel": logo_steel, "gold": logo_gold, "arch": logo_arch}

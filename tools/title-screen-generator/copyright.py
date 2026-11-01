"""Copyright lines: title-screen row (inside press_start.png, 160x8, outlined) and boot screen strip (intro/copyright.png, 312x8)."""
from PIL import Image
from glyphs import small_mask
from fx import paint, dilate, pad, edge
from logo import hexc

TITLE_ROW = {
    "fan-project": "@2026 FAN PROJECT",
    "not-for-sale": "FAN GAME * NOT FOR SALE",
    "name": "@2026 SPENCER LEPINE",
}
BOOT = {
    "name": "@2026 SPENCER LEPINE * A STAR WARS FAN GAME * NOT FOR SALE",
    "disclaimer": "FAN GAME * NOT AFFILIATED WITH LUCASFILM, NINTENDO OR GAME FREAK",
    "credit": "STAR WARS: KYBER * A FAN GAME BUILT ON THE POKEMON EMERALD DECOMP",
}


def title_row(text):
    m = pad(small_mask(text), 1)
    out = Image.new("RGBA", (160, 8), (0, 0, 0, 0))
    row = Image.new("RGBA", m.size, (0, 0, 0, 0))
    paint(row, dilate(m, 1), (0, 0, 0))
    paint(row, m, hexc("ffffff"))
    paint(row, edge(m, 0, 1), hexc("b4bdbd"))
    out.paste(row, ((160 - m.size[0]) // 2, 0), row)
    return out


def boot_strip(text):
    m = small_mask(text)
    out = Image.new("RGBA", (312, 8), (0, 0, 0, 0))
    row = Image.new("RGBA", m.size, (0, 0, 0, 0))
    paint(row, m, (255, 255, 255))
    out.paste(row, ((312 - m.size[0]) // 2, 1), row)
    return out

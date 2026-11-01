#!/usr/bin/env python3
"""Spectrogram contact sheet: each new cry next to the vanilla cry of its slot.

  python3 review.py specs/*.yaml   -> out/review.png
"""
import pathlib
import sys

import numpy as np
import yaml
from PIL import Image, ImageDraw

import gba

HERE = pathlib.Path(__file__).resolve().parent
CRIES = HERE.parent.parent / 'game' / 'sound' / 'direct_sound_samples' / 'cries'
PX_PER_S = 260
H = 150
LABEL_W = 120


def spectro(x, rate, seconds):
    n, hop = 256, 32
    x = np.pad(x, (0, max(0, int(seconds * rate) - len(x))))
    frames = [x[i:i + n] * np.hanning(n) for i in range(0, len(x) - n, hop)]
    S = np.abs(np.fft.rfft(np.array(frames), axis=1)).T
    S = 20 * np.log10(S + 1e-6)
    S = np.clip((S - S.max() + 60) / 60, 0, 1)
    img = Image.fromarray((255 * (1 - S[::-1])).astype(np.uint8)).resize((int(seconds * PX_PER_S), H))
    return img.convert('RGB')


def wave_img(x, rate, seconds):
    w = int(seconds * PX_PER_S)
    img = Image.new('RGB', (w, 40), 'white')
    d = ImageDraw.Draw(img)
    for px in range(w):
        a, b = int(px / PX_PER_S * rate), int((px + 1) / PX_PER_S * rate)
        seg = x[a:b]
        if len(seg):
            d.line([(px, 20 - seg.max() * 19), (px, 20 - seg.min() * 19)], fill=(40, 40, 160))
    return img


def main(paths):
    rows = []
    for p in paths:
        spec = yaml.safe_load(open(p))
        new, _ = gba.read_wav(HERE / 'out' / f"{spec['name']}.wav")
        old, _ = gba.read_wav(CRIES / f"{spec['slot']}.wav")
        rows.append((f"{spec['slot']} (vanilla)", old))
        rows.append((spec['name'].upper(), new))
    secs = max(len(x) for _, x in rows) / gba.CRY_RATE + 0.05
    W = LABEL_W + int(secs * PX_PER_S)
    sheet = Image.new('RGB', (W, len(rows) * (H + 46)), 'white')
    d = ImageDraw.Draw(sheet)
    for i, (label, x) in enumerate(rows):
        y = i * (H + 46)
        sheet.paste(wave_img(x, gba.CRY_RATE, secs), (LABEL_W, y))
        sheet.paste(spectro(x, gba.CRY_RATE, secs), (LABEL_W, y + 42))
        d.text((4, y + 4), label, fill='black')
        d.text((4, y + 20), f'{len(x) / gba.CRY_RATE:.2f}s', fill='gray')
        for k in (1000, 2000, 3000, 4000, 5000):
            yy = y + 42 + H - int(k / gba.NYQUIST * H)
            d.text((LABEL_W - 34, yy - 6), f'{k // 1000}k', fill='gray')
        if i % 2 == 1:
            d.line([(0, y + H + 44), (W, y + H + 44)], fill=(200, 0, 0), width=2)
    out = HERE / 'out' / 'review.png'
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    main(sys.argv[1:])

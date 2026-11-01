#!/usr/bin/env python3
"""Spectrogram contact sheet of rendered SFX (and, for hot-swaps, a ROM capture of the vanilla SE if
one exists in out/vanilla/<se>.wav).

  python3 review.py specs/*.yaml   -> out/review.png
"""
import pathlib
import sys

import numpy as np
import yaml
from PIL import Image, ImageDraw

import gba

HERE = pathlib.Path(__file__).resolve().parent
PX_PER_S = 300
H = 140
LABEL_W = 150


def spectro(x, rate, seconds):
    n, hop = 256, 24
    x = np.pad(x, (0, max(0, int(seconds * rate) - len(x)) + n))
    frames = np.array([x[i:i + n] * np.hanning(n) for i in range(0, int(seconds * rate), hop)])
    S = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1)).T + 1e-6)
    top = int(len(S) * min(1.0, 6700 / (rate / 2)))
    S = S[:top]
    S = np.clip((S - S.max() + 60) / 60, 0, 1)
    return Image.fromarray((255 * (1 - S[::-1])).astype(np.uint8)).resize((int(seconds * PX_PER_S), H)).convert('RGB')


def main(paths):
    rows = []
    for p in paths:
        spec = yaml.safe_load(open(p))
        x, r = gba.read_wav(HERE / 'out' / f"{spec['name']}.wav")
        if spec.get('replaces'):
            v = HERE / 'out' / 'vanilla' / f"{spec['replaces'].lower()}.wav"
            if v.exists():
                vx, vr = gba.read_wav(v)
                rows.append((f"{spec['replaces']} (ROM)", vx, vr))
        rows.append((spec['name'].upper(), x, r))
    secs = max(len(x) / r for _, x, r in rows) + 0.05
    W = LABEL_W + int(secs * PX_PER_S)
    sheet = Image.new('RGB', (W, len(rows) * (H + 8)), 'white')
    d = ImageDraw.Draw(sheet)
    for i, (label, x, r) in enumerate(rows):
        y = i * (H + 8)
        sheet.paste(spectro(x, r, secs), (LABEL_W, y))
        d.text((4, y + 4), label, fill='black')
        d.text((4, y + 20), f'{len(x) / r:.2f}s', fill='gray')
        for k in (1000, 3000, 5000):
            d.text((LABEL_W - 26, y + H - int(k / 6700 * H) - 6), f'{k // 1000}k', fill='gray')
    out = HERE / 'out' / 'review.png'
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    main(sys.argv[1:])

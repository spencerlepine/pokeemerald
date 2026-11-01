#!/usr/bin/env python3
"""Free: compare a species' latest takes side by side (front | back per take, 3x on battle green),
labelled with the raw files to pass to `refinish.py <sp> --pair FRONT BACK`.

    python takes.py altaria -n 4 --out /tmp/claude-0/takes_altaria.png
"""
import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from review import sprite, S, HERE

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("species"); ap.add_argument("-n", type=int, default=4); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fin = sorted((HERE / "runs" / a.species / "finished").glob("*_front_*"), key=lambda d: d.name, reverse=True)
    fin = [d for d in fin if (d / "front.png").exists() and (d / "back.png").exists()][: a.n]
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    sheet = Image.new("RGB", (2 * S + 24, len(fin) * (S + 40)), "white"); d = ImageDraw.Draw(sheet)
    for i, f in enumerate(fin):
        y = i * (S + 40)
        raw = HERE / "runs" / a.species / "raw"
        seed = f.name.split("_s")[-1]
        backs = sorted(p.name for p in raw.glob(f"*_back_s{seed}.png") if p.stem > f.name)
        d.text((4, y + 2), f"#{i+1} front {f.name}.png", fill="black", font=font)
        d.text((4, y + 18), f"   back {backs[0] if backs else '?'}", fill="black", font=font)
        sheet.paste(sprite(f / "front.png"), (0, y + 36)); sheet.paste(sprite(f / "back.png"), (S + 16, y + 36))
    sheet.save(a.out); print(a.out)

if __name__ == "__main__":
    main()

"""Film every style from out/capture.html (built for you).

    python3 capture.py [--out DIR] [--round N]     # DIR/round<N>/<n>_<style>.gif (a tour with zoom), DIR/<n>_<style>.png (out | in),
                                       # DIR/all_styles.png (every style, zoomed out and in)

The browser part is capture.js, run with node and the pre-installed Playwright Chromium. Frames are stepped by
hand (2 GBA frames each), so the GIFs play at real speed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import font  # noqa: E402

K = 3   # preview scale


def k(key, hold):
    return [f"SN.key('{key}')", hold, None]


# the scale styles start on Mos Eisley's corner of Tatooine; the galaxy style on Tatooine
TOUR_SCALE = ([["SN.goto(3, 6)", 10, None]] + [k("right", 6)] * 3 + [k("up", 6)] * 2 + [k("a", 30)] +
              [k("right", 8)] * 4 + [k("down", 8)] * 3 + [k("b", 30)] + [k("right", 5)] * 8 + [k("a", 30)] +
              [k("left", 8)] * 3 + [k("b", 24)])
TOUR_GALAXY = ([["SN.gotoPlanet('TATOOINE')", 20, None]] + [k("right", 14)] * 2 + [k("down", 14)] + [k("a", 36)] +
               [k("right", 8)] * 3 + [k("down", 8)] * 2 + [k("b", 24)] + [k("up", 14)] * 2 + [k("left", 14)] +
               [k("a", 36)] + [k("right", 8)] * 3 + [k("b", 24)])
STILLS_SCALE = [["SN.goto(6, 4)", 2, "out"], ["SN.key('a')", 12, "in"], ["SN.key('b')", 12, None]]
STILLS_GALAXY = [["SN.gotoPlanet('TATOOINE')", 2, "out"],
                 ["SN.key('a')", 12, None], ["SN.key('right'); SN.key('right'); SN.key('down')", 2, "in"],
                 ["SN.key('b')", 12, None]]


def main():
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else HERE / "out" / "previews"
    out.mkdir(parents=True, exist_ok=True)
    html = build.build(capture=True)
    styles = json.loads(html.read_text().split("window.STARNAV_DATA = ", 1)[1].split(";</script>", 1)[0])["styles"]
    rnd = int(sys.argv[sys.argv.index("--round") + 1]) if "--round" in sys.argv else max(s["round"] for s in styles)
    out = out / f"round{rnd}"
    out.mkdir(parents=True, exist_ok=True)
    picked = [(i, s) for i, s in enumerate(styles) if s["round"] == rnd]
    tours = []
    for n, (i, s) in enumerate(picked):
        galaxy = s["style"]["zoom"] == "planet"
        tours.append({"name": f"{n + 1}_{s['key']}", "style": i, "steps": TOUR_GALAXY if galaxy else TOUR_SCALE})
        tours.append({"name": f"{n + 1}_{s['key']}_stills", "style": i, "steps": STILLS_GALAXY if galaxy else STILLS_SCALE})
    frames = HERE / "out" / "frames"
    shutil.rmtree(frames, ignore_errors=True)
    tf = HERE / "out" / "tours.json"
    tf.write_text(json.dumps(tours))
    subprocess.run(["node", str(HERE / "capture.js"), str(html), str(frames), str(tf)], check=True)
    sheets = []
    for n, (i, s) in enumerate(picked):
        name = f"{n + 1}_{s['key']}"
        fs = sorted((frames / name).glob("*.png"))
        big = [Image.open(f).convert("RGB").resize((240 * K, 160 * K), Image.NEAREST) for f in fs]
        big[0].save(out / f"{name}.gif", save_all=True, append_images=big[1:], duration=33, loop=0)
        a = Image.open(frames / f"{name}_stills" / "out.png").convert("RGB")
        zin = Image.open(frames / f"{name}_stills" / "in.png").convert("RGB")
        pair = Image.new("RGB", (240 * K * 2 + 8 * K, 160 * K), (20, 24, 32))
        pair.paste(a.resize((240 * K, 160 * K), Image.NEAREST), (0, 0))
        pair.paste(zin.resize((240 * K, 160 * K), Image.NEAREST), (240 * K + 8 * K, 0))
        pair.save(out / f"{name}.png")
        sheets.append((s["style"]["title"], a, zin))
    # every style on one sheet, at 2x
    S = 2
    W, H = 240 * S, 160 * S
    sheet = Image.new("RGB", (W * 2 + 24, (H + 36) * len(sheets) + 8), (12, 14, 20))
    for j, (title, a, zin) in enumerate(sheets):
        y = 8 + j * (H + 36)
        lab = Image.new("RGB", (240, 14), (12, 14, 20))
        font.draw(lab, 0, 0, f"{j + 1} {title.upper()}   ZOOMED OUT  /  ZOOMED IN", (248, 208, 0), (96, 64, 0), "small")
        sheet.paste(lab.resize((480, 28), Image.NEAREST), (8, y))
        sheet.paste(a.resize((W, H), Image.NEAREST), (8, y + 30))
        sheet.paste(zin.resize((W, H), Image.NEAREST), (W + 16, y + 30))
    sheet = sheet.crop((0, 0, sheet.width, 8 + len(sheets) * (H + 36) + 16))
    sheet.save(out / "all_styles.png")
    print(out)


if __name__ == "__main__":
    main()

"""Build the StarNAV map mockups: the layers of each style and one self-contained player page.

    python3 build.py            # out/<style>/{map,chrome}.png (+ planets/), out/starnav_map.html
    python3 capture.py          # stills and zoom GIFs of every style from that page (Playwright)

Nothing in ../../game is built or changed: the page plays the screen in a browser, 240x160 at any scale.
"""
from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import font  # noqa: E402
from variants import ROUNDS, VIEW  # noqa: E402
from world import World  # noqa: E402

OUT = HERE / "out"

NOTES = {  # round 1 notes, shown under the tabs
    "holotable": "Holotable: a Rebel briefing hologram. One cyan hue on black with scanlines, gold corner brackets.",
    "atlas": "Star Atlas: every planet in its own colours, floating in space on gold hyperlanes. Closest to Emerald's map.",
    "imperial": "Imperial Tactical: a fleet display. Greys on black, the section grid shown, red marks and a crosshair.",
    "targeting": "Targeting Computer: the X-wing's amber screen in a rounded bezel, with a reticle cursor.",
    "galaxy": "Galaxy Chart: zoomed out is the galaxy, one globe per planet. A opens that planet's own map, B goes back.",
}


def uri(img):
    b = io.BytesIO()
    img.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def build(capture=False):
    world = World()
    secs = world.sections()
    styles = []
    for rnd, key, fn in [(r, k, f) for r in sorted(ROUNDS, reverse=True) for k, f in ROUNDS[r]]:
        r = fn(world)
        r["style"].setdefault("note", NOTES.get(key, ""))
        r["style"]["round"] = rnd
        d = OUT / f"round{rnd}" / key
        d.mkdir(parents=True, exist_ok=True)
        r["map"].save(d / "map.png")
        r["chrome"].save(d / "chrome.png")
        entry = {"key": key, "round": rnd, "map": uri(r["map"]), "chrome": uri(r["chrome"]), "style": r["style"]}
        if r.get("planets"):
            (d / "planets").mkdir(exist_ok=True)
            entry["planets"] = {}
            for p, v in r["planets"].items():
                v["img"].save(d / "planets" / (p.lower().replace(" ", "-") + ".png"))
                entry["planets"][p] = {"img": uri(v["img"]), "cells": v["cells"], "towns": v["towns"]}
                for row in v["cells"]:
                    for a in row:
                        if a and a not in secs["info"]:
                            raise SystemExit(f"unknown area {a}")
        styles.append(entry)
    data = {"view": list(VIEW), "fonts": font.export(), "cells": secs["cells"], "cell_planet": secs["cell_planet"],
            "info": secs["info"], "planets": {p: {"act": r["act"], "role": r["role"]} for p, r in world.planets.items()},
            "styles": styles, "capture": capture}
    page = (HERE / "player.html").read_text()
    page = page.replace("/*DATA*/", "window.STARNAV_DATA = " + json.dumps(data, separators=(",", ":")) + ";")
    page = page.replace("/*PLAYER*/", (HERE / "player.js").read_text())
    name = "capture.html" if capture else "starnav_map.html"
    (OUT / name).write_text(page)
    return OUT / name


if __name__ == "__main__":
    print(build(capture="--capture" in sys.argv))

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
from variants import STYLES, VIEW  # noqa: E402
from world import World  # noqa: E402

OUT = HERE / "out"


def uri(img):
    b = io.BytesIO()
    img.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def build(capture=False):
    world = World()
    secs = world.sections()
    styles = []
    for key, fn in STYLES:
        r = fn(world)
        d = OUT / key
        d.mkdir(parents=True, exist_ok=True)
        r["map"].save(d / "map.png")
        r["chrome"].save(d / "chrome.png")
        entry = {"key": key, "map": uri(r["map"]), "chrome": uri(r["chrome"]), "style": r["style"]}
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

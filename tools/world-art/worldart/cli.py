"""python -m worldart render <model.yaml>...   -> output/<name>/{sprite.png, review.png, meta.json}
python -m worldart budget <model.yaml>...      -> tiles and colours per object, no images"""
import argparse
import json
import os
import sys
import time

import numpy as np
from PIL import Image

from . import model as M, render as R, preview as P, tiles as T

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "output")


def _planet_of(obj):
    return os.path.basename(os.path.dirname(obj.path))


def render_one(path, preview_only=False, yaw=0.0):
    t0 = time.time()
    obj = M.Object(path)
    img, ind, warnings = R.render_object(obj, yaw)
    out = os.path.join(OUT, "preview-only" if preview_only else "", obj.name)
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, "sprite.png"))
    sheet = P.review_sheet(img, obj, _planet_of(obj))
    sheet.save(os.path.join(out, "review.png"))
    b = T.budget(ind, obj.palette)
    meta = {"name": obj.name, "description": obj.description, "cells": list(obj.cells),
            "footprint_rows": obj.footprint_rows(), "colliders_px": obj.foot_boxes(),
            "palette": [tuple(int(v) for v in c) for c in obj.palette[1:]], "budget": b, "warnings": warnings}
    if not preview_only:
        np.save(os.path.join(out, "indices.npy"), ind.astype(np.uint8))
        with open(os.path.join(out, "meta.json"), "w") as fh:
            json.dump(meta, fh, indent=1)
    for w in warnings:
        print("WARNING", w)
    print(f"{obj.name}: {obj.cells[0]}x{obj.cells[1]} cells, {b['unique_tiles']} unique tiles, "
          f"{b['colours']} colours{'' if b['bank_ok'] else ' (OVER 15)'}, {time.time() - t0:.1f}s -> {os.path.relpath(out, HERE)}/review.png")
    return obj, img, ind, meta


def main(argv=None):
    ap = argparse.ArgumentParser(prog="worldart")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("models", nargs="+")
    r.add_argument("--preview-only", action="store_true")
    r.add_argument("--yaw", type=float, default=0.0)
    c = sub.add_parser("compare")
    c.add_argument("models", nargs="+")
    b = sub.add_parser("budget")
    b.add_argument("models", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "render":
        for p in a.models:
            render_one(p, a.preview_only, a.yaw)
    elif a.cmd == "budget":
        for p in a.models:
            obj = M.Object(p)
            _, ind, _ = R.render_object(obj)
            print(obj.name, T.budget(ind, obj.palette))
    elif a.cmd == "compare":
        from . import compare as C
        for p in a.models:
            C.build(p)


if __name__ == "__main__":
    sys.exit(main())

"""Shared helpers for batch files: block() for patch rectangles, spec() to write art/<name>.yaml
in shade mode (D13) with step-frame patches generated from the stand patches. Importing this has
no side effects (unlike importing an older batch file, which rewrites its own specs).
"""
import yaml

P = "graphics/object_events/pics/people/"
STEPS = {"down": ("down_a", "down_b"), "up": ("up_a", "up_b"), "left": ("left_a", "left_b")}


def block(x, y, text):
    rows = text.strip("\n").split("\n")
    assert len({len(r) for r in rows}) == 1, rows
    assert x + len(rows[0]) <= 16, (x, rows[0])
    return {"x": x, "y": y, "rows": "\n".join(rows)}


def spec(name, gi, pal, replaces, desc, note, materials, legend, accept, base=None, remap=None,
         patches=None, frames=None, steps=None, kit="person16x32"):
    d = {"name": name, "description": desc, "kit": kit, "replaces": P + replaces,
         "graphics_info": gi, "notes": note, "palette": pal, "palette_tag": f"OBJ_EVENT_PAL_TAG_{pal.upper()}",
         "shade": True, "materials": materials, "legend": legend, "accept": accept}
    if base:
        d["base_sheet"] = P + base
        if remap:
            d["remap"] = remap
    fr = {}
    for stand, pts in (patches or {}).items():
        fr[stand] = {"patches": pts}
        for step in (() if kit.endswith("_still") else STEPS[stand]):
            fr[step] = {"patches": [{**p, "y": p["y"] + 1} for p in pts]}
    for k, g in (frames or {}).items():
        for r in g:
            assert len(r) == 16, (name, k, len(r), r)
        fr[k] = "\n".join(g) + "\n"
    for k, (b, py, rows) in (steps or {}).items():
        for r in rows:
            assert len(r) == 16, (name, k, len(r), r)
        fr[k] = {"base": b, "shift": 1, "patch_y": py, "rows": "\n".join(rows) + "\n"}
    d["frames"] = fr
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))



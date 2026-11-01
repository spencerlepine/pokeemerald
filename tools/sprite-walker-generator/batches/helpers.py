"""Shared helpers for batch files: block() for patch rectangles, spec() to write art/<name>.yaml
in shade mode (D13) with step-frame patches generated from the stand patches. Importing this has
no side effects (unlike importing an older batch file, which rewrites its own specs).
"""
import yaml

P = "graphics/object_events/pics/people/"
PK = "graphics/object_events/pics/pokemon/"
STEPS = {"down": ("down_a", "down_b"), "up": ("up_a", "up_b"), "left": ("left_a", "left_b")}
# kit -> (stand -> step frames that copy its patches, y offset of those step frames)
KIT_STEPS = {
    "person16x32": (STEPS, 1),
    "person16x16": (STEPS, 1),
    "flyer16x16": ({"down": ("down_a",), "up": ("up_a",), "left": ("left_a",)}, -1),
    "person16x32_bow": ({"down": ("bow",)}, 1),
}


def block(x, y, text):
    rows = text.strip("\n").split("\n")
    assert len({len(r) for r in rows}) == 1, rows
    assert x + len(rows[0]) <= 32, (x, rows[0])  # spec() checks it against the kit's width
    return {"x": x, "y": y, "rows": "\n".join(rows)}


def spec(name, gi, pal, replaces, desc, note, materials, legend, accept, base=None, remap=None,
         patches=None, frames=None, steps=None, kit="person16x32", root=P, step_patches=True):
    """root: folder of `replaces`/`base` under the game (P = people/; use PK for pokemon/).
    step_patches: copy each stand patch onto its step frames (moved by the kit's bob); turn it off
    or override a step frame through `patches` when the step frame needs its own art."""
    d = {"name": name, "description": desc, "kit": kit, "replaces": root + replaces,
         "graphics_info": gi, "notes": note, "palette": pal, "palette_tag": f"OBJ_EVENT_PAL_TAG_{pal.upper()}",
         "shade": True, "materials": materials, "legend": legend, "accept": accept}
    if base:
        d["base_sheet"] = root + base
        if remap:
            d["remap"] = remap
    fr = {}
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from walker_sprite.spec import KITS
    fw = KITS[kit]["frame"][0]
    for pts in (patches or {}).values():
        for p in pts:
            assert p["x"] + len(p["rows"].split("\n")[0]) <= fw, (name, p["x"], fw)
    smap, dy = KIT_STEPS.get(kit, ({}, 0))
    for stand, pts in (patches or {}).items():
        fr[stand] = {"patches": pts}
    for stand, pts in (patches or {}).items():
        for step in (smap.get(stand, ()) if step_patches else ()):
            if step not in (patches or {}):
                fr[step] = {"patches": [{**p, "y": p["y"] + dy} for p in pts]}
    for k, g in (frames or {}).items():
        for r in g:
            assert len(r) == fw, (name, k, len(r), r)
        fr[k] = "\n".join(g) + "\n"
    for k, (b, py, rows) in (steps or {}).items():
        for r in rows:
            assert len(r) == fw, (name, k, len(r), r)
        fr[k] = {"base": b, "shift": 1, "patch_y": py, "rows": "\n".join(rows) + "\n"}
    d["frames"] = fr
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))



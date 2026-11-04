"""Redrawn vanilla towns: their vanilla events moved onto the wiki layout by a hand-checked spec.

A redrawn town keeps every vanilla object, trigger and sign (scripts name objects by local id, so none is
removed), placed by `towns/<area-id>.yaml`:

  objects:   vanilla object (1-based, as local ids count) -> a yaml person's name (the object stands where the
             wiki puts that person), "=Name" (it is that person but stays where vanilla puts it: a script
             places it), a cell [x, y], or "keep" (vanilla cell, checked).
  coords:    vanilla trigger (0-based) -> a cell [x, y], or "drop".
  bgs:       vanilla sign or hidden item (0-based) -> a yaml sign's name, a cell, or "drop".
  sign_texts: yaml sign name -> text, for a wiki sign with no vanilla sign.
  patches:   script edits, each {old, new, file (default: the map's scripts.inc), count (default 1)}. A patch
             already applied (its new text present) is skipped, so the port can run again.
  movements: label -> steps, rewriting that movement in the map's scripts.inc: "D8 d7 r21 u ifr" is delay_8,
             7 x walk_down, 21 x walk_right, walk_up, walk_in_place_faster_right ("fr" is walk_fast_right, "Fr"
             walk_faster_right, "inv" set_invisible).
             Run again, it writes the same block.
  heal:      HEAL_LOCATION_X -> [x, y] (where the player stands after a blackout or fly).
  checks:    {movement: Label, from: [x, y], to: [x, y]}: the movement is walked on the new layout and
             reported if it crosses a solid cell or does not end at `to`.

Anything the spec leaves out keeps its vanilla cell and is checked; a person the spec does not match to a vanilla
object is a new one (events.py). Problems go to the port report.
"""
import copy
import json
import re

import yaml

from . import base as B, events as E

SPEC_DIR = B.HERE / "towns"
HEAL_JSON = "src/data/heal_locations.json"

STEP = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def load_spec(area):
    p = SPEC_DIR / f"{area.id}.yaml"
    return yaml.safe_load(p.read_text()) if p.exists() else None


def movement_steps(text, label):
    """The cells a movement walks, as (dx, dy) steps (jumps are 2 cells)."""
    m = re.search(rf"^{re.escape(label)}:+\n(.*?)^\s*step_end", text, re.M | re.S)
    if not m:
        return None
    out = []
    for line in m.group(1).splitlines():
        cmd = line.strip()
        if not cmd or cmd.startswith("@"):
            continue
        mm = re.match(r"(walk|walk_slow|walk_fast|walk_faster|walk_fastest|player_run|ride_water_current|slide|"
                      r"walk_slow_stairs|acro_wheelie_hop|acro_end_wheelie|acro_wheelie|walk_slower)_(up|down|left|right)$",
                      cmd)
        if mm and "in_place" not in cmd:
            out.append(STEP[mm.group(2)])
            continue
        mm = re.match(r"jump_(2_)?(up|down|left|right)$", cmd)
        if mm:
            dx, dy = STEP[mm.group(2)]
            n = 2 if mm.group(1) else 1
            out.append((dx * n, dy * n))
    return out


def walk(area, coll, doors, steps, start):
    x, y = start
    bad = []
    for dx, dy in steps:
        x, y = x + dx, y + dy
        # off the map is fine: a person walks out through an exit into the next map
        if (0 <= x < area.w and 0 <= y < area.h) and coll[y, x] and (x, y) not in doors:
            bad.append((x, y))
    return (x, y), bad


def person_index(area):
    """yaml person name (and "Name#2" for the second of a name) -> (person, nth)."""
    out, seen = {}, {}
    for p in area.people:
        seen[p["name"]] = seen.get(p["name"], 0) + 1
        n = seen[p["name"]]
        out[f"{p['name']}#{n}"] = (p, n)
        if n == 1:
            out[p["name"]] = (p, n)
    return out


def apply_patches(spec, a, problems):
    for pt in spec.get("patches") or []:
        path = B.GAME / (pt.get("file") or f"data/maps/{a.map_name}/scripts.inc")
        t = path.read_text()
        old, new, count = pt["old"], pt["new"], pt.get("count", 1)
        n = t.count(old)
        if new in t and (old not in new or n == count * new.count(old)):
            continue  # already applied
        if n == count:
            t = t.replace(old, new)
            B.write_text(path, t)
        else:
            problems.append(f"{a.id}: patch for {path.name} found {n} times (expected {count}): {old[:60]!r}")


DIRS = {"d": "down", "u": "up", "l": "left", "r": "right"}


def expand_steps(spec):
    """'D8 d7 r21 u ifr' -> movement commands."""
    out = []
    for tok in str(spec).split():
        m = re.match(r"^(if|f|F)?([durl])(\d*)$", tok)
        if m:
            cmd = {"if": "walk_in_place_faster_", "f": "walk_fast_", "F": "walk_faster_"}.get(m.group(1), "walk_")
            cmd += DIRS[m.group(2)]
            out += [cmd] * int(m.group(3) or 1)
        elif re.match(r"^D\d+$", tok):
            out.append(f"delay_{tok[1:]}")
        elif tok == "inv":
            out.append("set_invisible")
        else:
            raise ValueError(f"movement step {tok!r}")
    return out


def apply_movements(spec, a, problems):
    path = B.GAME / f"data/maps/{a.map_name}/scripts.inc"
    t = path.read_text()
    for label, steps in (spec.get("movements") or {}).items():
        m = re.search(rf"^{re.escape(label)}(:+)\n.*?^\s*step_end\n", t, re.M | re.S)
        if not m:
            problems.append(f"{a.id}: movement {label} not found")
            continue
        new = f"{label}{m.group(1)}\n" + "".join(f"\t{c}\n" for c in expand_steps(steps)) + "\tstep_end\n"
        t = t[:m.start()] + new + t[m.end():]
    B.write_text(path, t)


def heal_locations(world):
    """heal_locations.json from the vanilla one and every town spec's `heal`."""
    data = B.base_json(HEAL_JSON)
    for aid in world.scope:
        a = world.areas[aid]
        spec = load_spec(a) if a.mode == "redraw" and not a.new else None
        for hid, (x, y) in ((spec or {}).get("heal") or {}).items():
            for h in data["heal_locations"]:
                if h["id"] == hid:
                    h["x"], h["y"] = x, y
    B.write_json(B.GAME / HEAL_JSON, data)


def town_events(world, a, r, mj):
    """Move a redrawn town's vanilla events by its spec; returns problems."""
    problems = []
    spec = load_spec(a) or {}
    if not spec:
        problems.append(f"{a.id}: redrawn town with no spec (towns/{a.id}.yaml); vanilla events left in place")
    C = r["C"]
    doors = {(w.x, w.y) for w in world.warps[a.id] if w.to}
    base = B.base_map(a.replaces)
    people = person_index(a)
    matched = set()
    objs = copy.deepcopy(base.get("object_events") or [])
    sobj = {str(k): v for k, v in (spec.get("objects") or {}).items()}
    for i, o in enumerate(objs, 1):
        tgt = sobj.get(str(i), sobj.get(o.get("local_id", "-")))
        keep = False
        if isinstance(tgt, dict):
            name = tgt.get("person")
            if name not in people:
                problems.append(f"{a.id}: object {i} names {name!r}, not a person of the area")
            else:
                p, n = people[name]
                matched.add(f"{p['name']}#{n}")
            o["x"], o["y"] = tgt["at"]
        elif isinstance(tgt, str) and tgt != "keep":
            keep = tgt.startswith("=")
            name = tgt.lstrip("=")
            if name not in people:
                problems.append(f"{a.id}: object {i} names {name!r}, not a person of the area")
            else:
                p, n = people[name]
                matched.add(f"{p['name']}#{n}")
                if not keep:
                    o["x"], o["y"] = p["at"]
        elif isinstance(tgt, list):
            o["x"], o["y"] = tgt
        elif tgt == "keep":
            keep = True
        x, y = o["x"], o["y"]
        if not keep and (not (0 <= x < a.w and 0 <= y < a.h) or C.coll[y, x]):
            problems.append(f"{a.id}: object {i} ({o.get('script')}) on a solid or outside cell ({x},{y})")
    # people of the wiki with no vanilla object: new objects
    rows = world.people_rows
    path = B.GAME / "data/maps" / a.map_name / "scripts.inc"
    labels, _ = E.existing_labels(path)
    blk = E.Block(a.map_name, labels)
    taken = {(o["x"], o["y"]) for o in objs}
    counts = {}
    for p in a.people:
        counts[p["name"]] = counts.get(p["name"], 0) + 1
    seen = {}
    for p in a.people:
        seen[p["name"]] = seen.get(p["name"], 0) + 1
        n = seen[p["name"]]
        if f"{p['name']}#{n}" in matched:
            continue
        row = E.row_for(rows, a, p, n)
        if not row or (not row["lines"] and row.get("character") not in E.SERVICE_CHARACTERS):
            problems.append(f"{a.id}: {p['name']} is new here and has no lines in people.csv; says their name")
        key = E.key_of(p["name"], n, counts[p["name"]] > 1)
        label, trainer, flag = E.person_script(blk, key, row, p["name"].upper(), a)
        objs.append(E.new_object(a, C, p, row, label, trainer, flag, taken, problems))
    if len(objs) > 64:
        problems.append(f"{a.id}: {len(objs)} objects, the game holds 64")
    mj["object_events"] = objs
    # triggers
    coords = []
    scoord = {str(k): v for k, v in (spec.get("coords") or {}).items()}
    for i, c in enumerate(base.get("coord_events") or []):
        tgt = scoord.get(str(i))
        if tgt == "drop":
            continue
        c = dict(c)
        if isinstance(tgt, list):
            c["x"], c["y"] = tgt
        if not (0 <= c["x"] < a.w and 0 <= c["y"] < a.h) or C.coll[c["y"], c["x"]]:
            problems.append(f"{a.id}: trigger {i} ({c.get('script')}) on a solid or outside cell ({c['x']},{c['y']})")
        coords.append(c)
    mj["coord_events"] = coords
    # signs and hidden items
    signs = {s.get("name", ""): s for s in a.signs}
    used_signs = set()
    bgs = []
    sbg = {str(k): v for k, v in (spec.get("bgs") or {}).items()}
    for i, b in enumerate(base.get("bg_events") or []):
        tgt = sbg.get(str(i))
        if tgt == "drop":
            continue
        b = dict(b)
        if isinstance(tgt, str):
            if tgt in signs:
                b["x"], b["y"] = signs[tgt]["at"]
                used_signs.add(tgt)
            else:
                problems.append(f"{a.id}: bg event {i} names sign {tgt!r}, not a sign of the area")
        elif isinstance(tgt, list):
            b["x"], b["y"] = tgt
        if not (0 <= b["x"] < a.w and 0 <= b["y"] < a.h):
            problems.append(f"{a.id}: bg event {i} outside the map ({b['x']},{b['y']})")
        bgs.append(b)
    texts = spec.get("sign_texts") or {}
    for i, (name, s) in enumerate(signs.items(), 1):
        if name in used_signs:
            continue
        key = E.key_of(name or "Sign", i, True)
        t = blk.text(key, 1, texts.get(name) or f"{a.name.upper()}: {name}")
        lab = blk.script(blk.label("EventScript", key), f"\tmsgbox {t}, MSGBOX_SIGN\n\tend\n")
        bgs.append({"type": "sign", "x": s["at"][0], "y": s["at"][1], "elevation": 0,
                    "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY", "script": lab})
        if not texts.get(name):
            problems.append(f"{a.id}: sign {name!r} is new and has no text; shows its name")
    mj["bg_events"] = bgs
    E.write_block(path, blk)
    apply_patches(spec, a, problems)
    apply_movements(spec, a, problems)
    # movement checks on the new layout
    text = path.read_text()
    for ck in spec.get("checks") or []:
        src = (B.GAME / ck["file"]).read_text() if ck.get("file") else text
        steps = movement_steps(src, ck["movement"])
        if steps is None:
            problems.append(f"{a.id}: check: no movement {ck['movement']}")
            continue
        end, bad = walk(a, C.coll, doors, steps, ck["from"])
        if bad:
            problems.append(f"{a.id}: {ck['movement']} from {ck['from']} crosses solid cells {bad}")
        if ck.get("to") and list(end) != list(ck["to"]):
            problems.append(f"{a.id}: {ck['movement']} from {ck['from']} ends at {list(end)}, not {ck['to']}")
    return problems

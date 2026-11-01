"""Read the game source and record, for every VFX sheet, the contract a new drawing must keep.

For each PNG: size, bit depth, tile order (-mwidth/-mheight), frame size and frame count (from the
sprite templates' OAM shape and the anim tables), the frames each anim plays and for how long, the
palette it is drawn with (its own, a shared tag, a file, or set by code), who touches that palette at
runtime (blends, flashes, fades by index), and every move / field effect that loads it.

`python -m vfx catalog` writes corpus/catalog.json; everything else reads it through `load()`.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from PIL import Image

from .game import CORPUS, GAME, WIKI

INCGFX = re.compile(r'(\w+)\s*\[\]\s*=\s*INCGFX_U(?:8|16|32)\(\s*"([^"]+)"\s*,\s*"([^"]+)"(?:\s*,\s*"([^"]*)")?\s*\)')
TEMPLATE = re.compile(r'(?:static\s+)?const\s+struct\s+SpriteTemplate\s+(\w+)\s*=\s*\{(.*?)\};', re.S)
OAM = re.compile(r'(?:static\s+)?const\s+struct\s+OamData\s+(\w+)\s*=\s*\{(.*?)\};', re.S)
ANIMCMD = re.compile(r'(?:static\s+)?const\s+union\s+AnimCmd\s+(\w+)\s*\[\]\s*=\s*\{(.*?)\};', re.S)
ANIMTBL = re.compile(r'(?:static\s+)?const\s+union\s+AnimCmd\s*\*\s*const\s+(\w+)\s*\[\]\s*=\s*\{(.*?)\};', re.S)
FIELD = re.compile(r'\.(\w+)\s*=\s*([^,\n]+)')


def _strip_comments(s: str) -> str:
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return re.sub(r'//[^\n]*', '', s)


def _sources() -> dict[str, str]:
    out = {}
    for p in sorted((GAME / "src").rglob("*.[ch]")):
        out[str(p.relative_to(GAME))] = _strip_comments(p.read_text(encoding="utf-8", errors="replace"))
    for p in sorted((GAME / "include").rglob("*.h")):
        out[str(p.relative_to(GAME))] = _strip_comments(p.read_text(encoding="utf-8", errors="replace"))
    return out


def _png_info(rel: str) -> dict:
    p = GAME / rel
    if not p.exists():
        return {"exists": False}
    im = Image.open(p)
    with open(p, "rb") as f:
        head = f.read(26)
    return {"exists": True, "size": list(im.size), "mode": im.mode, "bitdepth": head[24]}


def _oam_sizes(src: dict[str, str]) -> dict[str, tuple[int, int]]:
    sizes = {}
    for text in src.values():
        for m in OAM.finditer(text):
            sh = re.search(r'SPRITE_SHAPE\((\d+)x(\d+)\)', m.group(2))
            if sh:
                sizes[m.group(1)] = (int(sh.group(1)), int(sh.group(2)))
    return sizes


def _oam_size(name: str, sizes: dict) -> tuple[int, int] | None:
    if name in sizes:
        return sizes[name]
    m = re.search(r'(\d+)x(\d+)$', name)
    return (int(m.group(1)), int(m.group(2))) if m else None


def _anims(src: dict[str, str]) -> tuple[dict, dict]:
    cmds, tables = {}, {}
    for text in src.values():
        for m in ANIMCMD.finditer(text):
            seq = []
            for c in re.finditer(r'ANIMCMD_(FRAME|JUMP|END|LOOP)\s*\(([^)]*)\)', m.group(2)):
                kind, args = c.group(1), c.group(2)
                if kind == "FRAME":
                    parts = [a.strip() for a in args.split(",")]
                    try:
                        off = int(parts[0], 0)
                        dur = int(parts[1], 0) if len(parts) > 1 else 1
                    except ValueError:
                        continue
                    seq.append({"tile": off, "dur": dur, "hflip": "hFlip" in args, "vflip": "vFlip" in args})
                elif kind == "JUMP":
                    seq.append({"jump": int(args.strip() or 0, 0)})
                elif kind == "LOOP":
                    seq.append({"loop": args.strip()})
                else:
                    seq.append({"end": True})
            cmds[m.group(1)] = seq
        for m in ANIMTBL.finditer(text):
            tables[m.group(1)] = re.findall(r'\b(\w+)\b', m.group(2))
    return cmds, tables


def _templates(src: dict[str, str]) -> list[dict]:
    out = []
    for f, text in src.items():
        for m in TEMPLATE.finditer(text):
            fields = {k: v.strip().lstrip("&") for k, v in FIELD.findall(m.group(2))}
            if not fields:   # positional initialiser
                parts = [p.strip().lstrip("&") for p in m.group(2).split(",")]
                keys = ["tileTag", "paletteTag", "oam", "anims", "images", "affineAnims", "callback"]
                fields = dict(zip(keys, parts))
            fields["name"], fields["file"] = m.group(1), f
            out.append(fields)
    return out


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _wiki_rows() -> dict[str, dict]:
    rows = {}
    p = WIKI / "database" / "pending_art.csv"
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            rows[r["path"]] = r
            rows[r["asset_id"]] = r
    return rows


# ------------------------------------------------------------------------------------------------
# battle animation sheets


def _script_blocks() -> dict[str, list[str]]:
    lines = (GAME / "data" / "battle_anim_scripts.s").read_text().split("\n")
    blocks, cur = {}, None
    for i, line in enumerate(lines):
        m = re.match(r'^(\w+):', line)
        if m:
            cur = m.group(1)
            blocks[cur] = []
            continue
        if cur:
            blocks[cur].append((i + 1, line))
    return blocks


def _resolve_users(blocks) -> tuple[dict, dict, dict]:
    """tag -> top-level anims that load it; template -> anims that create it; tag -> palette ops."""
    direct_tags, direct_tpl, calls, palops = {}, {}, {}, defaultdict(list)
    for k, lines in blocks.items():
        tags, tpls, cs = set(), set(), set()
        for ln, l in lines:
            code = l.split("@")[0]
            tags.update(re.findall(r'loadspritegfx\s+(ANIM_TAG_\w+)', code))
            m = re.match(r'\s*createsprite\s+(\w+)', code)
            if m:
                tpls.add(m.group(1))
            for w in re.findall(r'\b(\w+)\b', code):
                if w in blocks and w != k:
                    cs.add(w)
            if re.search(r'(blend|flash|palette|fade|color)', code, re.I):
                for t in re.findall(r'ANIM_TAG_\w+', code):
                    palops[t].append(f"data/battle_anim_scripts.s:{ln}: {code.strip()}")
        direct_tags[k], direct_tpl[k], calls[k] = tags, tpls, cs

    def resolve(k, seen, table):
        if k in seen:
            return set()
        seen.add(k)
        r = set(table[k])
        for c in calls[k]:
            r |= resolve(c, seen, table)
        return r

    tag_users, tpl_users = defaultdict(set), defaultdict(set)
    for k in blocks:
        if re.match(r'(Move|General|Special|Status)_', k):
            for t in resolve(k, set(), direct_tags):
                tag_users[t].add(k)
            for t in resolve(k, set(), direct_tpl):
                tpl_users[t].add(k)
    return tag_users, tpl_users, palops


def battle_anims(src, oams, cmds, tables, templates, wiki) -> list[dict]:
    g = src["src/graphics.c"]
    sym = {}
    for m in INCGFX.finditer(g):
        sym.setdefault(m.group(1), {"path": m.group(2), "ext": m.group(3), "opts": m.group(4) or ""})
    h = src["src/data/battle_anim.h"]
    pic = {}
    for m in re.finditer(r'\{\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+|\d+)\s*,\s*(ANIM_TAG_\w+)\s*\}', h):
        pic[m.group(3)] = (m.group(1), int(m.group(2), 0))
    pal = {}
    for m in re.finditer(r'\{\s*(\w+)\s*,\s*(ANIM_TAG_\w+)\s*\}', h):
        pal.setdefault(m.group(2), m.group(1))

    # concatenated sheets (ice_cube.4bpp = ice_cube_0..3.4bpp)
    rules = (GAME / "graphics_file_rules.mk").read_text()
    concat = {}
    for m in re.finditer(r'\$\(BTLANMSPRGFXDIR\)/(\w+)\.4bpp:((?:[^\n]*\\\n)*[^\n]*)', rules):
        parts = re.findall(r'\$\(BTLANMSPRGFXDIR\)/(\w+)\.4bpp', m.group(2))
        concat[m.group(1)] = parts

    blocks = _script_blocks()
    tag_users, tpl_users, palops = _resolve_users(blocks)

    # palette touched from C, by tag
    code_pal = defaultdict(list)
    for f, text in src.items():
        if not f.startswith("src/"):
            continue
        for m in re.finditer(r'IndexOfSpritePaletteTag\s*\(\s*(ANIM_TAG_\w+)\s*\)', text):
            code_pal[m.group(1)].append(f"{f}:{_line_of(text, m.start())}")

    tpl_by_tag = defaultdict(list)
    for t in templates:
        tag = t.get("tileTag", "")
        if tag.startswith("ANIM_TAG_"):
            tpl_by_tag[tag].append(t)

    file_tags = defaultdict(list)
    for tag, (s, nbytes) in pic.items():
        info = sym.get(s)
        if not info:
            continue
        path = info["path"]
        base = Path(path).stem
        if path.endswith(".4bpp") and base in concat:
            for p in concat[base]:
                file_tags[f"graphics/battle_anims/sprites/{p}.png"].append((tag, nbytes, s, concat[base]))
        else:
            file_tags[path.replace(".4bpp", ".png")].append((tag, nbytes, s, None))

    out = []
    seen = set()
    for path in sorted(set(file_tags) | {str(p.relative_to(GAME)) for p in (GAME / "graphics/battle_anims").rglob("*.png")}):
        if path in seen:
            continue
        seen.add(path)
        e = {"id": path[len("graphics/"):-4], "path": path, "kind": "battle_anims", **_png_info(path)}
        sub = path.split("/")[2]
        e["group"] = {"sprites": "battle_anim_sprite", "backgrounds": "battle_anim_bg", "masks": "battle_anim_mask",
                      "stat_change": "battle_anim_bg", "unused": "battle_anim_unused"}.get(sub, "battle_anim_sprite")
        tags = file_tags.get(path, [])
        e["tags"] = sorted({t for t, *_ in tags})
        e["concat_parts"] = tags[0][3] if tags and tags[0][3] else None
        e["bytes"] = tags[0][1] if tags else None
        info = sym.get(tags[0][2]) if tags else None
        e["gfx_opts"] = info["opts"] if info else ""
        mw = re.search(r'-mwidth (\d+)', e["gfx_opts"])
        mh = re.search(r'-mheight (\d+)', e["gfx_opts"])
        e["mwidth"], e["mheight"] = (int(mw.group(1)) if mw else 1), (int(mh.group(1)) if mh else 1)

        # templates, frames, anims
        tpls, sizes = [], defaultdict(int)
        for tag in e["tags"]:
            for t in tpl_by_tag[tag]:
                sz = _oam_size(t.get("oam", ""), oams)
                an = []
                for a in tables.get(t.get("anims", ""), []):
                    an.append({"name": a, "cmds": cmds.get(a, [])})
                users = sorted(tpl_users.get(t["name"], []))
                tpls.append({"name": t["name"], "file": t["file"], "tag": tag, "oam": t.get("oam"),
                             "frame": list(sz) if sz else None, "anims": an,
                             "affine": t.get("affineAnims"), "callback": t.get("callback"), "users": users})
                if sz:
                    sizes[sz] += 1 + len(users)
        e["templates"] = tpls
        if sizes:
            fw, fh = max(sizes, key=sizes.get)
            e["frame"] = [fw, fh]
            e["frame_sizes"] = [list(s) for s in sizes]
        elif e.get("size"):
            e["frame"] = e["size"][:]
            e["frame_sizes"] = [e["size"][:]]
        if e.get("size") and e.get("frame"):
            per = (e["frame"][0] // 8) * (e["frame"][1] // 8)
            tiles = (e["size"][0] // 8) * (e["size"][1] // 8)
            e["frame_slots"] = tiles // per if per else 1
            # a concatenated part starts after the tiles of the parts before it
            start = 0
            if e["concat_parts"]:
                for part in e["concat_parts"]:
                    if part == Path(path).stem:
                        break
                    pi = _png_info(f"graphics/battle_anims/sprites/{part}.png")
                    start += (pi["size"][0] // 8) * (pi["size"][1] // 8)
            e["tile_start"] = start
            used = set()
            for t in tpls:
                if t["frame"] != e["frame"]:
                    continue
                for a in t["anims"]:
                    for c in a["cmds"]:
                        if "tile" in c and start <= c["tile"] < start + tiles:
                            used.add((c["tile"] - start) // per)
            e["frames_used"] = sorted(used) or list(range(e["frame_slots"]))

        # palette contract
        ptag = e["tags"][0] if e["tags"] else None
        psym = pal.get(ptag) if ptag else None
        pinfo = sym.get(psym) if psym else None
        if pinfo:
            ppath = pinfo["path"]
            own = ppath == path or (e["concat_parts"] and Path(ppath).stem.rstrip("_0123456789") == Path(path).stem.rstrip("_0123456789"))
            shared = sorted({t for t, s2 in pal.items() if s2 == psym} - set(e["tags"]))
            e["palette"] = {"kind": "own" if own else "file", "source": ppath, "symbol": psym,
                            "shared_with_tags": shared}
        elif e["group"] in ("battle_anim_bg", "battle_anim_mask") or not e["tags"]:
            m = [s2 for s2, i in sym.items() if i["path"] == path and "gbapal" in i["ext"]]
            e["palette"] = {"kind": "own" if m else "code", "source": path if m else None, "symbol": m[0] if m else None,
                            "shared_with_tags": []}
        else:
            e["palette"] = {"kind": "unknown", "source": None, "symbol": None, "shared_with_tags": []}
        touched = []
        for tag in e["tags"]:
            touched += palops.get(tag, []) + [f"{x}: IndexOfSpritePaletteTag({tag})" for x in code_pal.get(tag, [])]
        e["palette"]["touched_by"] = touched

        users = set()
        for tag in e["tags"]:
            users |= tag_users.get(tag, set())
        e["users"] = sorted(users)
        w = wiki.get(path, {})
        e["wiki"] = {k: w.get(k, "") for k in ("asset_id", "art_status", "swap_kind", "sw_subject", "todo")}
        out.append(e)
    return out


# ------------------------------------------------------------------------------------------------
# field effects (overworld)

# Palettes the templates do not name (TAG_NONE) but the code sets: checked by hand in the source.
PALETTE_OVERRIDES = {
    "field_effects/pics/bird": {
        "kind": "player", "source": "graphics/object_events/palettes/brendan.pal",
        "alt_sources": ["graphics/object_events/palettes/may.pal"],
        "note": "CreateFlyBirdSprite sets oam.paletteNum = 0 (src/field_effect.c, ~line 3305): the bird is drawn "
                "with the PLAYER's bank, which differs for the boy and the girl. Use indices whose colours read "
                "right in both player palettes.",
    },
}


def field_effects(src, oams, cmds, tables, templates, wiki) -> list[dict]:
    g = src["src/data/object_events/object_event_graphics.h"]
    sym = {m.group(1): {"path": m.group(2), "ext": m.group(3), "opts": m.group(4) or ""} for m in INCGFX.finditer(g)}
    fx = src["src/data/field_effects/field_effect_objects.h"]
    pictables = {}
    for m in re.finditer(r'(?:static\s+)?const\s+struct\s+SpriteFrameImage\s+(\w+)\s*\[\]\s*=\s*\{(.*?)\};', fx, re.S):
        frames = []
        for f in re.finditer(r'overworld_frame\(\s*(\w+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', m.group(2)):
            frames.append({"pic": f.group(1), "w": int(f.group(2)) * 8, "h": int(f.group(3)) * 8, "index": int(f.group(4))})
        for f in re.finditer(r'obj_frame_tiles\(\s*(\w+)\s*\)', m.group(2)):
            frames.append({"pic": f.group(1), "w": None, "h": None, "index": 0, "whole": True})
        pictables[m.group(1)] = frames
    palsyms = {}
    for m in re.finditer(r'const\s+struct\s+SpritePalette\s+(\w+)\s*=\s*\{\s*(\w+)\s*,\s*(\w+)\s*\}', fx):
        palsyms[m.group(3)] = m.group(2)
    allsym = {}
    for f, text in src.items():
        for m in INCGFX.finditer(text):
            allsym.setdefault(m.group(1), {"path": m.group(2), "ext": m.group(3), "opts": m.group(4) or "", "file": f})
    fldtpl = [t for t in templates if t["file"] == "src/data/field_effects/field_effect_objects.h"]
    fe_src = src.get("src/field_effect.c", "") + src.get("src/fldeff_misc.c", "") + src.get("src/field_effect_helpers.c", "")

    out = []
    for p in sorted((GAME / "graphics/field_effects/pics").rglob("*.png")):
        path = str(p.relative_to(GAME))
        e = {"id": path[len("graphics/"):-4], "path": path, "kind": "field_effects", "group": "field_effect", **_png_info(path)}
        syms = [s for s, i in allsym.items() if i["path"] == path]
        e["symbols"] = syms
        info = allsym.get(syms[0]) if syms else None
        e["gfx_opts"] = info["opts"] if info else ""
        mw = re.search(r'-mwidth (\d+)', e["gfx_opts"])
        mh = re.search(r'-mheight (\d+)', e["gfx_opts"])
        e["mwidth"], e["mheight"] = (int(mw.group(1)) if mw else 1), (int(mh.group(1)) if mh else 1)
        tpls = []
        frame = None
        idxs = set()
        for t in fldtpl:
            imgs = pictables.get(t.get("images", ""), [])
            mine = [f for f in imgs if f["pic"] in syms]
            if not mine:
                continue
            sz = _oam_size(t.get("oam", ""), oams)
            for f in mine:
                if f.get("whole"):
                    f["w"], f["h"] = e["size"] if e.get("size") else (sz or (16, 16))
                frame = [f["w"], f["h"]]
                idxs.add(f["index"])
            an = [{"name": a, "cmds": cmds.get(a, [])} for a in tables.get(t.get("anims", ""), [])]
            ptag = t.get("paletteTag", "")
            tpls.append({"name": t["name"], "oam": t.get("oam"), "frame": list(sz) if sz else None,
                         "palette_tag": ptag, "anims": an, "callback": t.get("callback"),
                         "images": t.get("images")})
        e["templates"] = tpls
        if not frame and e.get("size"):
            frame = e["size"][:]
        e["frame"] = frame
        if e.get("size") and frame:
            e["frame_slots"] = (e["size"][0] * e["size"][1]) // (frame[0] * frame[1])
        e["frames_used"] = sorted(idxs)
        # palette
        ptags = sorted({t["palette_tag"] for t in tpls})
        pal = {"tags": ptags, "touched_by": []}
        if any(t.startswith("FLDEFF_PAL_TAG_") for t in ptags):
            t0 = [t for t in ptags if t.startswith("FLDEFF_PAL_TAG_")][0]
            ps = palsyms.get(t0)
            pi = allsym.get(ps) if ps else None
            users = [x for x in fldtpl if x.get("paletteTag") == t0]
            pal.update({"kind": "shared" if len(users) > 1 else "file", "source": pi["path"] if pi else None,
                        "shared_by": len(users)})
        elif ptags and all(t in ("TAG_NONE", "0xFFFF") for t in ptags):
            names = [x["name"] for x in tpls]
            hits = []
            for n in names:
                for m in re.finditer(r'\b' + re.escape(n.replace("gFieldEffectObjectTemplate_", "FLDEFFOBJ_").upper()) + r'\b', fe_src):
                    pass
            pal.update({"kind": "code", "source": None,
                        "note": "paletteTag TAG_NONE: the palette slot is set in code (often oam.paletteNum = 0, the player's bank)"})
        else:
            pal.update({"kind": "object_event", "source": None})
        if e["id"] in PALETTE_OVERRIDES:
            pal.update(PALETTE_OVERRIDES[e["id"]])
        e["palette"] = pal
        w = wiki.get(path, {})
        e["wiki"] = {k: w.get(k, "") for k in ("asset_id", "art_status", "swap_kind", "sw_subject", "todo")}
        out.append(e)
    return out


# ------------------------------------------------------------------------------------------------
# the simpler kinds: doors, weather, transitions, rotating gates


def simple_kind(folder: str, kind: str, group: str, wiki, frame=None) -> list[dict]:
    out = []
    for p in sorted((GAME / folder).rglob("*.png")):
        path = str(p.relative_to(GAME))
        e = {"id": path[len("graphics/"):-4], "path": path, "kind": kind, "group": group, **_png_info(path)}
        if frame and e.get("size"):
            fw, fh = frame(e["size"])
            e["frame"] = [fw, fh]
            e["frame_slots"] = (e["size"][0] * e["size"][1]) // (fw * fh)
        elif e.get("size"):
            e["frame"] = e["size"][:]
            e["frame_slots"] = 1
        e["mwidth"] = e["mheight"] = 1
        e["palette"] = {"kind": "file", "source": None, "touched_by": []}
        w = wiki.get(path, {})
        e["wiki"] = {k: w.get(k, "") for k in ("asset_id", "art_status", "swap_kind", "sw_subject", "todo")}
        out.append(e)
    return out


def build() -> dict:
    src = _sources()
    oams = _oam_sizes(src)
    cmds, tables = _anims(src)
    templates = _templates(src)
    wiki = _wiki_rows()
    entries = []
    entries += battle_anims(src, oams, cmds, tables, templates, wiki)
    entries += field_effects(src, oams, cmds, tables, templates, wiki)
    entries += simple_kind("graphics/door_anims", "door_anims", "door", wiki,
                           frame=lambda s: (s[0], s[1] // 3))
    entries += simple_kind("graphics/weather", "weather", "weather", wiki)
    entries += simple_kind("graphics/battle_transitions", "battle_transitions", "transition", wiki)
    entries += simple_kind("graphics/rotating_gates", "rotating_gates", "rotating_gate", wiki)
    cat = {"entries": {e["id"]: e for e in entries}}
    CORPUS.mkdir(parents=True, exist_ok=True)
    (CORPUS / "catalog.json").write_text(json.dumps(cat, indent=1))
    load.cache_clear()
    return cat


@lru_cache(maxsize=1)
def load() -> dict:
    p = CORPUS / "catalog.json"
    if not p.exists():
        return build()
    return json.loads(p.read_text())


def find(key: str) -> dict:
    """Look an entry up by id ('battle_anims/sprites/coin'), game path, file stem, or tag."""
    ents = load()["entries"]
    k = key.replace("graphics/", "").removesuffix(".png")
    if k in ents:
        return ents[k]
    hits = [e for e in ents.values() if e["id"].endswith("/" + k) or k in e.get("tags", [])]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise KeyError(f"no VFX sheet matches {key!r}")
    raise KeyError(f"{key!r} is ambiguous: " + ", ".join(h["id"] for h in hits))

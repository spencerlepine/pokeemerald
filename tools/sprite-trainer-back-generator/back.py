#!/usr/bin/env python3
"""Trainer back pics (the over-the-shoulder capture-pod throw) through Civitai's hosted generator.

One back pic is 4 frames of 64x64 (64x256 PNG, 4bpp) on the palette of the trainer's front pic.

    prep <trainer>        free. The vanilla 4 throw frames, recoloured onto the front pic's palette by the
                          colour map in jobs.json (plus optional paint ops: hair buns, hood), laid out as a
                          2x2 sheet of 128x128 native pixels, scaled 8x to 1024x1024 on the LoRA's own grid.
    gen <trainer>         paid. Image to image from the prep (SDXL + trainer LoRA 159333, same as the fronts),
                          one 1024x1024 image holding all four frames, so the frames stay one character.
                          --whatif prices it and spends nothing.
    finish <raw.png>      free. 8 px grid read back to 128x128 native, background off, split into 4 frames,
                          palette-enforcer `enforce --pal <front palette>` then `check`; 64x256 PNG,
                          4x preview, animated GIF and a battle mockup.
    sheet [<trainer>...]  free. One review sheet: front pic, the 4 back frames, battle mockup.

<trainer> is the back pic's file stem in game/graphics/trainers/back_pics/ (brendan, may, brendan_rs,
may_rs, wally, steven). The brief is that row's sw_subject in wiki/database/pending_art.csv; jobs.json
adds the look notes (written from the shipped front pic) and the colour map.
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import io
import json
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GAME = REPO / "game"
FRONT_TOOL = REPO / "tools" / "sprite-trainer-generator" / "civitai"
sys.path.insert(0, str(FRONT_TOOL))
import civitai_trainer as ct  # noqa: E402  (reuses http, model versions, grid reader, background cut)

WIKI_CSV = REPO / "wiki" / "database" / "pending_art.csv"
ENFORCER = REPO / "tools" / "palette-enforcer"
JOBS_FILE = HERE / "jobs.json"
RUNS = HERE / "runs"
REFS = HERE / "refs"

BACKS = GAME / "graphics" / "trainers" / "back_pics"
FRONTS = GAME / "graphics" / "trainers" / "front_pics"
SIZE = 1024          # 128 native px x 8: four 64x64 frames in a 2x2 sheet
NATIVE = 128
BG = (255, 255, 255)

PROMPT = ("solo, single character, pixel art sprite sheet of four frames, ({subject}:1.3), {desc}, "
          "(back view:1.4), (from behind:1.3), over the shoulder, upper body, seen from behind and to the left, "
          "throwing pose, empty hand, back of head, looking away, pixel art, game sprite, crisp dark outlines, "
          "gen3 battle back sprite, solid white background, simple background")
NEGATIVE = ("face, eyes, open mouth, mouth, teeth, front view, facing viewer, poke ball, pokeball, "
            "ball in hand, red ball, baseball cap, hat, "
            "generic pokemon trainer, scenery, detailed background, gradient background, floor, shadow, text, "
            "watermark, signature, frame, border, blurry, 3d, photo, realistic, painting, smooth shading")


# ----------------------------------------------------------------------------- briefs and palettes

def jobs() -> dict:
    return json.loads(JOBS_FILE.read_text())


def brief(trainer: str) -> dict:
    stem = Path(trainer).stem
    row = {}
    with WIKI_CSV.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["kind"] == "trainers" and r["subkind"] == "back_pics" and Path(r["path"]).stem == stem:
                row = r
    job = jobs().get(stem)
    if not job:
        sys.exit(f"{stem}: no entry in {ct.rel(JOBS_FILE)}")
    return {"stem": stem, "wiki_path": row.get("path"), "sw_subject": row.get("sw_subject"), **job}


def front_palette(stem: str) -> list[tuple[int, int, int]]:
    """The front pic's 16 colours: the shared .pal where the game has one, else the front PNG's own."""
    pal = GAME / "graphics" / "trainers" / "palettes" / f"{stem}.pal"
    im = Image.open(FRONTS / f"{stem}.png")
    p = im.getpalette()[:48]
    own = [tuple(p[i:i + 3]) for i in range(0, 48, 3)]
    if pal.exists():
        lines = pal.read_text().split()
        shared = [tuple(int(v) for v in lines[3 + 3 * i: 6 + 3 * i]) for i in range(16)]
        if shared[1:] == own[1:]:  # steven.pal is still the vanilla back colours; Leia's front owns its bank
            return shared
    return own


def write_pal(colours, dst: Path) -> Path:
    dst.write_text("JASC-PAL\r\n0100\r\n16\r\n" + "".join(f"{r} {g} {b}\r\n" for r, g, b in colours))
    return dst


# ----------------------------------------------------------------------------- prep (free)

def base_png(stem: str) -> Path:
    """The 4 frames the prep starts from: vanilla, or jobs.json "base" (another finished back pic, e.g.
    Mira from Kael's approved throw), whose palette indices "map" then refers to."""
    base = jobs().get(stem, {}).get("base")
    return HERE / base if base else BACKS / f"{stem}.png"


def vanilla_frames(stem: str) -> list[np.ndarray]:
    a = np.array(Image.open(base_png(stem)))
    return [a[64 * k: 64 * k + 64] for k in range(4)]


def recolour(stem: str, job: dict) -> list[Image.Image]:
    """Vanilla frames -> RGBA on the front palette. jobs.json "map" is {vanilla index: front index};
    unmapped vanilla indices keep their vanilla colour (flagged by prep). "paint" ops go on top:
    [frame or -1 for all, "ellipse"|"rect", x0, y0, x1, y1, front index, outline index or null]."""
    vpal = Image.open(base_png(stem)).getpalette()[:48]
    fpal = front_palette(stem)
    cmap = {int(k): v for k, v in job["map"].items()}
    out = []
    anchors = job.get("anchor") or auto_anchor(stem)
    job = {**job, "anchor": anchors}
    for k, fr in enumerate(vanilla_frames(stem)):
        rgba = np.zeros((64, 64, 4), np.uint8)
        for i in range(1, 16):
            m = fr == i
            if not m.any():
                continue
            col = fpal[cmap[i]] if i in cmap else tuple(vpal[3 * i: 3 * i + 3])
            rgba[m] = (*col, 255)
        # "regions": [{"box": [x0, y0, x1, y1] (frame 3 coords, moved by "anchor"), "map": {...}}]:
        # a different colour map inside a box (a bandana that shares its red with the top -> hair)
        for reg in job.get("regions", []):
            if "frames" in reg and k not in reg["frames"]:
                continue  # "frames": [k, ...] with an absolute box ("abs": true) for one frame's own spot
            dx, dy = (0, 0) if reg.get("abs") else job.get("anchor", {}).get(str(k), [0, 0])
            x0, y0, x1, y1 = reg["box"]
            box = np.zeros((64, 64), bool)
            box[max(0, y0 + dy): y1 + dy + 1, max(0, x0 + dx): x1 + dx + 1] = True
            for vi, fi in reg["map"].items():  # -1: erase to background
                rgba[box & (fr == int(vi))] = (0, 0, 0, 0) if fi < 0 else (*fpal[fi], 255)
        # "near": [{"of": [vanilla indices], "grow": n, "map": {...}}]: remap next to those pixels (hands
        # next to the glove colour keep their skin when the arms become sleeves)
        for nr in job.get("near", []):
            m = np.isin(fr, nr["of"])
            for _ in range(nr.get("grow", 2)):
                m = m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
            for vi, fi in nr["map"].items():
                rgba[m & (fr == int(vi))] = (*fpal[fi], 255)
        im = Image.fromarray(rgba, "RGBA")
        under = Image.new("RGBA", (64, 64), (0, 0, 0, 0))  # ops starting with "under" go behind the figure
        for op in job.get("paint", []):
            # [frame, "ellipse"|"rect", x0, y0, x1, y1, fill, line] or [frame, "polygon", [x, y, ...], fill, line];
            # prefix "under" (["under", frame, ...]) to draw behind the figure (a cloak behind the arms)
            d = ImageDraw.Draw(under if op[0] == "under" else im)
            op = op[1:] if op[0] == "under" else op
            f, shape = op[0], op[1]
            if f not in (-1, k):
                continue
            dx, dy = job.get("anchor", {}).get(str(k), [0, 0]) if f == -1 else (0, 0)
            if shape == "polygon":
                pts, fill, line = op[2], op[3], op[4]
                geom = [(pts[i] + dx, pts[i + 1] + dy) for i in range(0, len(pts), 2)]
            else:
                x0, y0, x1, y1, fill, line = op[2:8]
                geom = [x0 + dx, y0 + dy, x1 + dx, y1 + dy]
            kw = {"fill": (0, 0, 0, 0) if fill < 0 else (*fpal[fill], 255)}
            if line is not None:
                kw["outline"] = (*fpal[line], 255)
            {"ellipse": d.ellipse, "rect": d.rectangle, "polygon": d.polygon}[shape](geom, **kw)
        under.alpha_composite(im)
        out.append(under)
    return out


def auto_anchor(stem: str, rows: int = 40, reach: int = 12) -> dict:
    """Per frame, the (dx, dy) that best lays its head (top `rows` rows) over frame 3's, so a box or a
    paint op written in frame 3's coordinates lands on the same spot of the head in every frame."""
    fr = [f > 0 for f in vanilla_frames(stem)]
    ref = fr[3][:rows]
    out = {}
    for k in range(4):
        best = (1e9, 0, 0)
        for dy in range(-reach, reach + 1):
            for dx in range(-reach, reach + 1):
                sh = np.roll(np.roll(ref, dy, 0), dx, 1)
                cost = (sh != fr[k][:rows]).sum()
                best = min(best, (cost, dx, dy))
        out[str(k)] = [best[1], best[2]]
    return out


def cmd_prep(args):
    for t in args.trainer:
        b = brief(t)
        frames = recolour(b["stem"], b)
        sheet = Image.new("RGBA", (NATIVE, NATIVE), (*BG, 255))
        for k, fr in enumerate(frames):
            sheet.alpha_composite(fr, ((k % 2) * 64, (k // 2) * 64))
        REFS.mkdir(exist_ok=True)
        nat = REFS / f"{b['stem']}_prep.png"
        sheet.convert("RGB").save(nat)
        sheet.convert("RGB").resize((SIZE, SIZE), Image.NEAREST).save(REFS / f"{b['stem']}_prep_8x.png")
        unmapped = sorted({int(i) for fr in vanilla_frames(b["stem"]) for i in np.unique(fr)} - {0}
                          - {int(k) for k in b["map"]})
        print(f"prep {b['stem']} -> {ct.rel(nat)}" + (f"  (unmapped vanilla indices {unmapped})" if unmapped else ""))


# ----------------------------------------------------------------------------- generate (paid)

def cmd_gen(args) -> list[Path]:
    b = brief(args.trainer)
    init = REFS / f"{b['stem']}_prep_8x.png"
    if args.init:
        init = Path(args.init).resolve()
    if not init.exists():
        sys.exit(f"no prep: run `prep {b['stem']}` first")
    v = ct.pick_version(args.version)
    fam = ct.family(v)
    prompt = args.prompt or PROMPT.format(subject=b["subject"].lower(), desc=b["desc"])
    negative = ", ".join(x for x in (b.get("negative", ""), NEGATIVE) if x)
    denoise = args.denoise if args.denoise is not None else b.get("denoise", 0.5)
    strength = args.strength if args.strength is not None else b.get("strength", 0.75)
    seed = args.seed if args.seed is not None else random.randrange(1, 2**31 - 1)
    lora_air = v.get("air") or f"urn:air:{fam}:lora:civitai:{ct.LORA_MODEL_ID}@{v['id']}"
    im = Image.open(init).convert("RGB")
    if im.size != (SIZE, SIZE):
        im = im.resize((SIZE, SIZE), Image.NEAREST)
    buf = io.BytesIO(); im.save(buf, "PNG")
    step = {"$type": "imageGen", "input": {
        "engine": "comfy", "ecosystem": fam, "operation": "createVariant",
        "checkpointModel": args.checkpoint or ct.CHECKPOINTS[fam], "loras": {lora_air: strength},
        "image": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(),
        "denoiseStrength": denoise, "prompt": prompt, "negativePrompt": negative,
        "sampler": "euler_ancestral", "scheduler": "normal", "steps": args.steps, "cfgScale": args.cfg,
        "seed": seed, "clipSkip": 2, "width": SIZE, "height": SIZE, "quantity": args.n,
        "outputFormat": args.format}}
    workflow = {"steps": [step], "currencies": args.currency.split(",")}
    print(f"trainer  {b['stem']}  ({b['sw_subject']})\nprompt   {prompt}\n"
          f"seed {seed}  x{args.n}  denoise {denoise}  lora {strength}  init {ct.rel(init)}")
    url = f"{ct.ORCHESTRATOR}/v2/consumer/workflows"
    if args.whatif:
        r = ct.http("POST", url, params={"whatif": "true"}, json=workflow).json()
        print(f"whatif: {ct._cost(r)}  insufficientBuzz={r.get('transactions', {}).get('insufficientBuzz')}")
        return []
    r = ct.http("POST", url, json=workflow, timeout=240).json()
    wid = r["id"]
    print(f"submitted {wid}, cost {ct._cost(r)}")
    t0 = time.time()
    while True:
        s = ct.http("GET", f"{url}/{wid}").json()
        imgs = (s.get("steps") or [{}])[0].get("output", {}).get("images", [])
        if s.get("status") in ("failed", "expired", "canceled"):
            sys.exit(f"workflow {wid} {s.get('status')}:\n{json.dumps(s)[:2000]}")
        if s.get("status") == "succeeded" and imgs and all(i.get("available") for i in imgs):
            break
        if time.time() - t0 > args.timeout:
            sys.exit(f"timed out (status {s.get('status')}); workflow {wid}")
        time.sleep(3)
    out = RUNS / b["stem"] / "raw"
    out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    paths = []
    for i, img in enumerate(imgs):
        data = requests.get(img["url"], timeout=120); data.raise_for_status()
        sd = img.get("seed") or seed + i
        p = out / f"{stamp}_d{int(denoise * 100)}_s{sd}.png"
        Image.open(io.BytesIO(data.content)).convert("RGB").save(p)
        meta = {"trainer": b, "lora": v, "checkpoint": step["input"]["checkpointModel"], "prompt": prompt,
                "negative": negative, "seed": sd, "denoise": denoise, "strength": strength, "steps": args.steps,
                "cfg": args.cfg, "size": SIZE, "init": ct.rel(init), "format": args.format,
                "workflowId": wid, "cost": ct._cost(r), "generated": stamp}
        p.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"saved {ct.rel(p)}")
        paths.append(p)
    return paths


# ----------------------------------------------------------------------------- finish (free)

def read_native(raw: Path) -> Image.Image:
    """The 1024 image back on its 8 px grid (128x128). The prep is grid-aligned, so the period is 8."""
    a = np.asarray(Image.open(raw).convert("RGB"))
    period, px, py = ct.find_grid(a)
    if period != 8:
        px = py = 0  # the image drifted off the grid: fall back to the prep's own alignment
    g = a >> 3
    out = np.zeros((NATIVE, NATIVE, 3), np.uint8)
    for y in range(NATIVE):
        for x in range(NATIVE):
            c = g[min(py + y * 8 + 1, SIZE - 7): py + y * 8 + 7, min(px + x * 8 + 1, SIZE - 7): px + x * 8 + 7]
            v, n = np.unique(c.reshape(-1, 3), axis=0, return_counts=True)
            out[y, x] = v[n.argmax()] * 8
    return Image.fromarray(out, "RGB")


def cut_frame(nat: Image.Image, k: int, job: dict) -> Image.Image:
    """One 64x64 frame with its background removed. The figure runs off the frame's bottom edge (a back
    pic is cut at the waist), so the flood fill starts only from the top and side edges' white."""
    fr = nat.crop(((k % 2) * 64, (k // 2) * 64, (k % 2) * 64 + 64, (k // 2) * 64 + 64))
    pad = Image.new("RGB", (66, 65), BG)  # a white margin on top and sides only, so the fill can enter
    pad.paste(fr, (1, 1))
    cut = ct.knock_out_background(pad, pockets=not job.get("keep_pockets"))
    cut = ct.despeck(cut)
    return cut.crop((1, 1, 65, 65))


def mask_to_vanilla(fr: Image.Image, stem: str, k: int, grow: int) -> Image.Image:
    """Optional: drop pixels far outside the vanilla silhouette (stray marks between frames)."""
    v = vanilla_frames(stem)[k] > 0
    m = v.copy()
    for _ in range(grow):
        m = m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
    a = np.array(fr)
    a[~m, 3] = 0
    return Image.fromarray(a, "RGBA")


def finish(raw: Path, out: Path | None = None) -> Path:
    raw = raw.resolve()
    stem = raw.parent.parent.name
    job = brief(stem)
    out_dir = out or (raw.parent.parent / "finished" / raw.stem)
    out_dir.mkdir(parents=True, exist_ok=True)
    pal = write_pal(front_palette(stem), out_dir / "front.pal")
    nat = read_native(raw)
    nat.save(out_dir / "native.png")
    strip = Image.new("RGBA", (64, 256), (0, 0, 0, 0))
    for k in range(4):
        fr = cut_frame(nat, k, job)
        if job.get("silhouette_grow") is not None:
            fr = mask_to_vanilla(fr, stem, k, job["silhouette_grow"])
        strip.alpha_composite(fr, (0, 64 * k))
    rgba = out_dir / "back_rgba.png"
    strip.save(rgba)
    final = out_dir / f"{stem}.png"
    _run([sys.executable, "-m", "gba_palette", "enforce", str(rgba), str(final), "--bpp", "4", "--pal", str(pal)])
    if job.get("post_remap"):  # jobs.json {"from index": to index} on the finished pic (Kael's tunic -> whiter)
        p = Image.open(final)
        a = np.array(p)
        b = a.copy()
        for src, dst in job["post_remap"].items():
            b[a == int(src)] = dst
        sh = job.get("post_shade")  # {"light": i, "shade": j, "edge": [outline indices]}: put form back on
        if sh:  # a flat light area: light pixels with an outline or the edge below/right of them get the shade
            edge = np.isin(b, sh["edge"] + [0])
            near = np.zeros_like(edge)
            for d in range(1, sh.get("width", 1) + 1):
                near |= np.roll(edge, -d, 0) | np.roll(edge, -d, 1)
            b[(b == sh["light"]) & near & (np.isin(a, [sh["light"]] + [int(k) for k in job["post_remap"]]))] = sh["shade"]
        for k, kind, *xy, idx in job.get("post_edit", []):  # [frame, "line"|"fill_light", x0, y0, x1, y1, index]
            fr = Image.fromarray(b[64 * k: 64 * k + 64].copy(), "P")
            if kind == "line":
                ImageDraw.Draw(fr).line(xy, fill=idx)
                b[64 * k: 64 * k + 64] = np.array(fr)
            elif kind == "poly":  # xy = [[x, y, ...]], idx = [fill, outline]: redraw a shape by hand
                fr = Image.fromarray(b[64 * k: 64 * k + 64].copy(), "P")
                pts = xy[0]
                ImageDraw.Draw(fr).polygon([(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)],
                                           fill=idx[0], outline=idx[1])
                b[64 * k: 64 * k + 64] = np.array(fr)
            elif kind == "clear":  # idx = indices to erase to transparent inside the box
                x0, y0, x1, y1 = xy
                sub = b[64 * k + y0: 64 * k + y1 + 1, x0: x1 + 1]
                sub[np.isin(sub, idx)] = 0
            elif kind == "remap":  # idx is {from: to} inside the box (a skin-coloured patch -> strap brown)
                x0, y0, x1, y1 = xy
                sub = b[64 * k + y0: 64 * k + y1 + 1, x0: x1 + 1]
                src = sub.copy()
                for f_, t_ in idx.items():
                    sub[src == int(f_)] = t_
            else:  # the light colour inside a box -> idx (shade a flat patch)
                x0, y0, x1, y1 = xy
                sub = b[64 * k + y0: 64 * k + y1 + 1, x0: x1 + 1]
                sub[sub == job.get("post_shade", {}).get("light", 1)] = idx
        q = Image.fromarray(b, "P"); q.putpalette(p.getpalette()); q.info["transparency"] = 0
        q.save(final, transparency=0)
    ok = _run([sys.executable, "-m", "gba_palette", "check", str(final), "--pal", str(pal)], check=False) == 0
    img = Image.open(final)
    _on(img).resize((256, 1024), Image.NEAREST).save(out_dir / "back_4x.png")
    frames = [_on(img.crop((0, 64 * k, 64, 64 * k + 64))).resize((192, 192), Image.NEAREST) for k in range(4)]
    # vanilla timing: 0 (24), 1 (9), 2 (24), 0 (9), 3 (50) at 60 fps
    order = [(0, 24), (1, 9), (2, 24), (0, 9), (3, 50), (3, 40)]
    frames[0].save(out_dir / "throw.gif", save_all=True, append_images=[frames[i] for i, _ in order[1:]],
                   duration=[round(n * 1000 / 60) for _, n in order], loop=0, disposal=2)
    battle_mockup(stem, final, out_dir / "battle_mockup_3x.png")
    print(f"{raw.name}: {'PASS' if ok else 'FAIL'} -> {ct.rel(final)}")
    return final


def _on(fr: Image.Image, colour=(144, 200, 160)) -> Image.Image:
    """Sprite on a flat backdrop; an indexed image draws index 0 as transparent, as the GBA does."""
    a = np.array(fr.convert("RGBA"))
    if fr.mode == "P":
        a[np.array(fr) == 0, 3] = 0
    bg = Image.new("RGBA", fr.size, (*colour, 255))
    bg.alpha_composite(Image.fromarray(a, "RGBA"))
    return bg


def battle_mockup(stem: str, back: Path, dst: Path, scale: int = 3) -> Path:
    """Frames 0 (holding the pod) and 2 (throw) on the vanilla tall-grass battle, side by side, where the
    game draws a trainer back pic (64x64 centred at x 80, bottom under the text box at y 112), with the
    shipped MASSIFF front on the far pad (reuses sprite-creature-generator's battle renderer)."""
    sys.path.insert(0, str(REPO / "tools" / "sprite-creature-generator" / "civitai"))
    import civitai_creature as cc
    img = cc._sprite_rgba(back)
    mon = GAME / "graphics" / "pokemon" / "poochyena" / "front.png"
    full = Image.new("RGB", (240 * 2 + 8, 160), (30, 30, 30))
    for i, k in enumerate((0, 2)):
        scene = cc.battle_bg().convert("RGBA")
        if mon.exists():
            scene.alpha_composite(cc._sprite_rgba(mon), (144, 4))
        scene.alpha_composite(img.crop((0, 64 * k, 64, 64 * k + 64)), (48, 48 + 4))
        box = Image.new("RGBA", (240, 48), (40, 80, 104, 255))
        box.paste((248, 248, 248, 255), (4, 4, 236, 44))
        scene.alpha_composite(box, (0, 112))
        full.paste(scene.convert("RGB"), (i * 248, 0))
    full.resize((full.width * scale, full.height * scale), Image.NEAREST).save(dst)
    return dst


def _run(cmd, check=True) -> int:
    r = subprocess.run(cmd, cwd=ENFORCER, stdout=subprocess.DEVNULL if not check else None)
    if check and r.returncode:
        sys.exit(f"failed: {' '.join(cmd)}")
    return r.returncode


def cmd_finish(args):
    for p in args.raw:
        finish(Path(p), Path(args.out).resolve() if args.out else None)


def cmd_run(args):
    for p in cmd_gen(args):
        finish(p)


# ----------------------------------------------------------------------------- review sheet (free)

def cmd_sheet(args):
    """Rows of: front pic | 4 back frames (finished pick, else the prep) on battle green, 3x."""
    rows = []
    for t in args.trainer or list(jobs()):
        stem = Path(t).stem
        picks = sorted((RUNS / stem / "finished").glob(f"*/{stem}.png")) if not args.prep else []
        if args.only:
            picks = [p for p in picks if args.only in str(p)]
        srcs = picks[-args.last:] if picks else [None]
        for p in srcs:
            front = _on(Image.open(FRONTS / f"{stem}.png").convert("RGBA"), (144, 200, 160))
            a = np.array(Image.open(FRONTS / f"{stem}.png").convert("RGBA"))
            key = (a[..., :3] == a[0, 0, :3]).all(2)
            a[key, 3] = 0
            front = _on(Image.fromarray(a))
            if p is None:
                frames = [_on(f) for f in recolour(stem, brief(stem))]
                label = "prep"
            else:
                img = Image.open(p)
                frames = [_on(img.crop((0, 64 * k, 64, 64 * k + 64))) for k in range(4)]
                label = p.parent.name
            row = Image.new("RGBA", (64 * 5 + 16, 64 + 10), (30, 30, 30, 255))
            row.alpha_composite(front, (0, 0))
            for k, f in enumerate(frames):
                row.alpha_composite(f, (64 * (k + 1) + 16, 0))
            ImageDraw.Draw(row).text((2, 64), f"{stem} {label}"[:52], fill=(230, 230, 230, 255))
            rows.append(row)
    sheet = Image.new("RGBA", (rows[0].width, sum(r.height for r in rows)), (30, 30, 30, 255))
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y)); y += r.height
    dst = Path(args.out).resolve() if args.out else RUNS / "review_sheet.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    sheet.resize((sheet.width * args.scale, sheet.height * args.scale), Image.NEAREST).save(dst)
    print(f"sheet -> {dst}")


# ----------------------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep"); p.add_argument("trainer", nargs="+"); p.set_defaults(fn=cmd_prep)

    def gen_args(g):
        g.add_argument("trainer")
        g.add_argument("--init", help="start image instead of refs/<trainer>_prep_8x.png")
        g.add_argument("--denoise", type=float, help="0..1 (default: the job's, else 0.5)")
        g.add_argument("--strength", type=float, help="LoRA weight (default: the job's, else 0.75)")
        g.add_argument("--seed", type=int)
        g.add_argument("-n", type=int, default=1)
        g.add_argument("--version", help="LoRA version (default sdxl, as the fronts)")
        g.add_argument("--checkpoint")
        g.add_argument("--prompt")
        g.add_argument("--steps", type=int, default=25)
        g.add_argument("--cfg", type=float, default=5.0)
        g.add_argument("--format", choices=["jpeg", "png"], default="png")
        g.add_argument("--currency", default="green", help="Buzz account(s): green, blue, yellow")
        g.add_argument("--timeout", type=int, default=600)
        g.add_argument("--whatif", action="store_true")

    g = sub.add_parser("gen"); gen_args(g); g.set_defaults(fn=cmd_gen)
    r = sub.add_parser("run"); gen_args(r); r.set_defaults(fn=cmd_run)
    f = sub.add_parser("finish"); f.add_argument("raw", nargs="+"); f.add_argument("--out"); f.set_defaults(fn=cmd_finish)
    s = sub.add_parser("sheet"); s.add_argument("trainer", nargs="*"); s.add_argument("--prep", action="store_true")
    s.add_argument("--last", type=int, default=1, help="finished takes per trainer to show (newest)")
    s.add_argument("--only", help="only takes whose folder name contains this")
    s.add_argument("--scale", type=int, default=3); s.add_argument("--out")
    s.set_defaults(fn=cmd_sheet)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

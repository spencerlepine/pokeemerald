#!/usr/bin/env python3
"""Creature battle sprites (front + back) through Civitai's hosted generator (no local GPU).

Mirror of ../../sprite-trainer-generator/civitai/civitai_trainer.py, set up for the creature LoRA
"Pokemon Sprite PixelArt 768" (model 161280, SD 1.5, v2.1-beta by default).

Pipeline for one species:
    gen     prompt -> Civitai (SD 1.5 + creature LoRA) -> 768x768 originals in runs/<species>/raw/
            --view front (default) or back (the LoRA's `backside` tag); optional input image:
            --init IMG (image to image) or --control IMG (ControlNet, keeps the outline)
    finish  front + back raws -> 96 native (8x block vote) -> background off -> fit 64x64
            -> front: palette-enforcer enforce --colours 15 --write-pal normal.pal
            -> back:  palette-enforcer enforce --pal normal.pal   (one shared bank, as in vanilla)
            -> check both, 4x previews and a battle mockup
    run     gen front and back (same seed) then finish them as a pair

<species> is the species folder in game/graphics/pokemon/ (e.g. poochyena). Its brief (Star Wars
name, description, types, colour) comes from ../research/sw-creature-jobs.csv; jobs.json adds per-
species look notes, negatives and reference images.

The API key is read from CIVITAI_API_TOKEN, or from a git-ignored .env file next to this script.
It is never printed or written anywhere else.
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import io
import json
import os
import random
import re
import subprocess
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
import requests
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
GAME = REPO / "game"
JOBS_CSV = HERE.parent / "research" / "sw-creature-jobs.csv"
ENFORCER = REPO / "tools" / "palette-enforcer"
MODELS_CACHE = HERE / "models.json"
JOBS_FILE = HERE / "jobs.json"
RUNS = HERE / "runs"

LORA_MODEL_ID = 161280  # Pokemon Sprite PixelArt 768 (titansteng / sWizad)
PUBLIC_API = "https://civitai.com/api/v1"
ORCHESTRATOR = "https://orchestration.civitai.com"

# Base checkpoints by LoRA base model. The creature LoRA is SD 1.5 only; never load it on SDXL.
CHECKPOINTS = {
    "sdxl": "urn:air:sdxl:checkpoint:civitai:101055@128078",  # SDXL 1.0 base
    "sd1": "urn:air:sd1:checkpoint:civitai:4384@128713",      # DreamShaper 8
}

# The LoRA was trained on 96x96 sprites with BLIP captions plus tags: gen1..gen5 (style), backside,
# shiny, type tags (grasstype, firetype, ...), mega, gmax. No trigger word. `gen3` is our target.
# Unlike the trainer LoRA, "pokemon" is wanted here: it is what the captions call every subject.
# Pilot 2026-11-01 (abra, charmander): weighting the description and the body colour, and asking for
# muted colours, turned "rainbow" text-only takes into the described animal in its own colour.
PROMPT = ("{style}, {view}{types}({subject}:1.1), ({desc}:1.2), pokemon, single creature, full body, "
          "{pose}{colour}, limited palette, muted natural colours, pixel art, game sprite, "
          "crisp dark outlines, white background, simple background")
POSE = "facing left"
BACK_TAGS = "backside, back view, "
NEGATIVE = ("human, person, trainer, multiple creatures, two creatures, text, watermark, signature, "
            "frame, border, scenery, detailed background, gradient background, ground, shadow, "
            "cropped, cut off, blurry, 3d, photo, realistic, painting, smooth shading")
BACK_NEGATIVE = "face, eyes, front view, facing viewer, "
# Frame 2 of anim_front.png: vanilla's changes a median 72% of pixels (a real pose change: mouth open,
# limbs moved), so it is image to image from the picked front with an action added to the pose.
FRAME2 = "mouth wide open, roaring, lunging forward"

# The LoRA's own type tags (from the model page); other types fall back to plain words.
LORA_TYPES = {"grass", "fire", "flying", "dark", "bug", "ghost", "water", "electric", "psychic",
              "ice", "dragon", "fighting", "poison", "ground", "rock", "steel", "normal"}


# ----------------------------------------------------------------------------- key, http

def api_token() -> str:
    tok = os.environ.get("CIVITAI_API_TOKEN", "").strip()
    env = HERE / ".env"
    if not tok and env.exists():
        for line in env.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() == "CIVITAI_API_TOKEN":
                tok = v.strip().strip('"').strip("'")
    if not tok:
        sys.exit("No API key: set CIVITAI_API_TOKEN (Civitai > Account settings > API Keys), "
                 f"or put CIVITAI_API_TOKEN=... in {env.relative_to(REPO)} (git-ignored).")
    return tok


def http(method: str, url: str, *, auth: bool = True, **kw) -> requests.Response:
    headers = kw.pop("headers", {})
    if auth:
        headers["Authorization"] = f"Bearer {api_token()}"
    for attempt in range(4):
        try:
            r = requests.request(method, url, headers=headers, timeout=60, **kw)
        except requests.RequestException as e:
            if attempt == 3:
                sys.exit(f"{method} {url}: {e}")
            time.sleep(2 ** (attempt + 1))
            continue
        if r.status_code in (429, 502, 503, 504) and attempt < 3:
            time.sleep(2 ** (attempt + 1))
            continue
        if r.status_code >= 400:
            sys.exit(f"{method} {url} -> HTTP {r.status_code}\n{r.text[:2000]}")
        return r
    raise AssertionError


# ----------------------------------------------------------------------------- model versions

def cmd_models(args) -> dict:
    r = http("GET", f"{PUBLIC_API}/models/{LORA_MODEL_ID}", auth=False)
    m = r.json()
    versions = [{
        "id": v["id"],
        "name": v.get("name"),
        "baseModel": v.get("baseModel"),
        "trainedWords": v.get("trainedWords", []),
        "air": v.get("air"),
        "files": [{"name": f.get("name"), "sizeKB": f.get("sizeKB"),
                   "sha256": (f.get("hashes") or {}).get("SHA256")} for f in v.get("files", [])],
    } for v in m.get("modelVersions", [])]
    data = {"model": m.get("name"), "creator": (m.get("creator") or {}).get("username"),
            "license": {k: m.get(k) for k in ("allowCommercialUse", "allowDerivatives",
                                               "allowNoCredit", "allowDifferentLicense")},
            "fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "versions": versions}
    MODELS_CACHE.write_text(json.dumps(data, indent=2) + "\n")
    for v in versions:
        print(f"{v['id']:>8}  {v['baseModel']:<12} {v['name']}  trigger={v['trainedWords']}")
    print(f"cached -> {rel(MODELS_CACHE)}")
    return data


def pick_version(want: str | None) -> dict:
    data = json.loads(MODELS_CACHE.read_text()) if MODELS_CACHE.exists() else cmd_models(None)
    vs = data["versions"]
    if want and want.isdigit():
        hit = [v for v in vs if v["id"] == int(want)]
    else:
        key = (want or "v2").lower()
        hit = [v for v in vs if key in (v["name"] or "").lower()
               or key in (v["baseModel"] or "").lower().replace(" ", "")]
    if not hit:
        sys.exit(f"No LoRA version matches {want!r}; run `models` to list them.")
    return hit[0]


def family(v: dict) -> str:
    return "sdxl" if "xl" in (v["baseModel"] or "").lower() else "sd1"


# ----------------------------------------------------------------------------- briefs

def brief(species: str) -> dict:
    stem = Path(species).name.lower()
    row = {}
    if JOBS_CSV.exists():
        with JOBS_CSV.open(newline="") as f:
            for r in csv.DictReader(f):
                if r["species_folder"] == stem:
                    row = r
                    break
    jobs = json.loads(JOBS_FILE.read_text()) if JOBS_FILE.exists() else {}
    job = dict(jobs.get(stem, {}))
    pick = HERE / "refs" / "picks" / f"{stem}.json"  # refs.py pick (reference chosen per species)
    if pick.exists():
        job.update(json.loads(pick.read_text()))
    # Type tags only when jobs.json asks: on their own they pulled MASSIFF into a humanoid and gave
    # text-only takes rainbow colours.
    types = job.get("types", [])
    return {"stem": stem, "sw_name": row.get("sw_name"), "sw_basis": row.get("sw_basis"),
            "subject": job.get("subject") or (row.get("sw_name") or stem).lower(),
            "desc": job.get("desc") or row.get("description", "").split(". ")[0],
            "types": types, "colour": job.get("colour", row.get("body_color", "")),
            "style": job.get("style", "gen3"), "pose": job.get("pose", POSE),
            "negative": job.get("negative", ""), "init": job.get("init"),
            "control": job.get("control"), "denoise": job.get("denoise"),
            "flip": job.get("flip", False), "frame2": job.get("frame2", FRAME2),
            "shiny": job.get("shiny", {})}


def build_prompt(b: dict, view: str) -> str:
    types = "".join(f"{t}type, " if t in LORA_TYPES else f"{t} type, " for t in b["types"])
    p = PROMPT.format(style=b["style"], view=BACK_TAGS if view == "back" else "", types=types,
                      subject=b["subject"], desc=re.sub(r"\s*\([^)]*\)", "", b["desc"]).rstrip(".").replace(",", ""),
                      pose="seen from behind" if view == "back" else
                      f"{b['pose']}, {b['frame2']}" if view == "frame2" else b["pose"],
                      colour=f", ({b['colour']} body:1.3)" if b["colour"] else "")
    return ", ".join(s.strip() for s in p.split(",") if s.strip())


def _local(src: str) -> str:
    """jobs.json paths are relative to this folder; URLs and data URIs pass through."""
    if src.startswith(("http://", "https://", "data:")):
        return src
    return str(HERE / src) if (HERE / src).exists() else src


def image_ref(src: str, flip: bool = False) -> str:
    """URL as is (unless flipping); a local file becomes a data URI (the orchestrator stores it as
    a blob). Local images are flattened on white, padded square and sized to 768 like the model's
    own canvas; --flip mirrors them (vanilla fronts face left, most concept art faces right)."""
    if src.startswith(("http://", "https://")) and not flip:
        return src
    if src.startswith("data:"):
        return src
    if src.startswith(("http://", "https://")):
        r = requests.get(src, timeout=60)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content))
    else:
        im = Image.open(Path(src).expanduser().resolve())
    im = im.convert("RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    side = max(im.size)
    sq = Image.new("RGBA", (side, side), (255, 255, 255, 255))
    sq.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    resample = Image.NEAREST if side < 512 else Image.LANCZOS  # small sprites keep crisp pixels
    sq = sq.convert("RGB").resize((768, 768), resample)
    buf = io.BytesIO()
    sq.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ----------------------------------------------------------------------------- generate

def cmd_gen(args) -> list[Path]:
    b = brief(args.species)
    if args.style is not None:
        b["style"] = args.style
    v = pick_version(args.version)
    fam = family(v)
    prompt = args.prompt or build_prompt(b, args.view)
    negative = args.negative or ", ".join(x for x in (b["negative"], NEGATIVE) if x)
    if args.view == "back":
        negative = BACK_NEGATIVE + negative
    seed = args.seed if args.seed is not None else random.randrange(1, 2**31 - 1)
    lora_air = v.get("air") or f"urn:air:{fam}:lora:civitai:{LORA_MODEL_ID}@{v['id']}"
    init = args.init or (b["init"] if args.view == "front" else None)
    if args.view == "frame2" and not init:
        sys.exit("--view frame2 needs --init <the picked front's raw .png>")
    if args.cfg is None:
        args.cfg = 5.0 if init else 7.0
    params = {"prompt": prompt, "negativePrompt": negative,
              "scheduler": args.scheduler, "steps": args.steps, "cfgScale": args.cfg,
              "width": args.size, "height": args.size, "seed": seed, "clipSkip": 2}
    extra, refs = {}, {}
    model = args.checkpoint or CHECKPOINTS[fam]
    control = args.control or (b["control"] if args.view == "front" else None)
    if control:  # ControlNet keeps the reference's outline/pose; the LoRA redraws the style
        extra["controlNets"] = [{"preprocessor": args.control_type, "weight": args.control_weight,
                                 "image": image_ref(control, args.flip or b["flip"])}]
        refs["control"] = control
    if init:
        # Image to image goes through the imageGen step (ComfyUI engine, createVariant). The older
        # textToImage step stores a `sourceImage` but does not use it: on 2026-11-01 a back sent
        # with one came back byte-identical to the same prompt + seed without it (served from cache).
        refs["init"] = init if not init.startswith("data:") else "(data URI)"
        denoise = args.denoise or b["denoise"] or 0.45
        step = {"$type": "imageGen", "input": {
            "engine": "comfy", "ecosystem": fam, "operation": "createVariant",
            "checkpointModel": model, "loras": {lora_air: args.strength},
            "image": image_ref(_local(init), args.flip or b["flip"]), "denoiseStrength": denoise,
            "prompt": prompt, "negativePrompt": negative, "sampler": "euler_ancestral",
            "scheduler": "normal", "steps": args.steps, "cfgScale": args.cfg, "seed": seed,
            "clipSkip": 2, "width": args.size, "height": args.size, "quantity": args.n,
            "outputFormat": args.format, **extra}}
        params["denoise"] = denoise
    else:
        step = {"$type": "textToImage", "input": {
            "model": model, "additionalNetworks": {lora_air: {"type": "Lora", "strength": args.strength}},
            **params, **extra, "quantity": args.n, "outputFormat": args.format}}
    workflow = {"steps": [step], "currencies": args.currency.split(",")}
    print(f"species  {b['stem']}  ({b['sw_name']}, {args.view})\nlora     {v['name']} "
          f"[{v['baseModel']}] @{v['id']}\nprompt   {prompt}\nseed     {seed}  x{args.n}  ({args.format})"
          + (f"\nrefs     {refs}" if refs else ""))

    url = f"{ORCHESTRATOR}/v2/consumer/workflows"
    if args.whatif:
        r = http("POST", url, params={"whatif": "true"}, json=workflow).json()
        print(f"whatif: {_cost(r)}  insufficientBuzz={r.get('transactions', {}).get('insufficientBuzz')}")
        return []

    r = http("POST", url, json=workflow).json()
    wid = r["id"]
    print(f"submitted workflow {wid}, cost {_cost(r)}")

    t0 = time.time()
    while True:
        s = http("GET", f"{url}/{wid}").json()
        status = s.get("status")
        imgs = (s.get("steps") or [{}])[0].get("output", {}).get("images", [])
        if status in ("failed", "expired", "canceled"):
            sys.exit(f"workflow {wid} {status}:\n{json.dumps(s)[:2000]}")
        if status == "succeeded" and imgs and all(i.get("available") for i in imgs):
            break
        if time.time() - t0 > args.timeout:
            sys.exit(f"timed out after {args.timeout}s (status {status}); re-check workflow {wid}")
        time.sleep(3)

    out = RUNS / b["stem"] / "raw"
    out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    paths = []
    for i, im in enumerate(imgs):
        data = requests.get(im["url"], timeout=120)
        data.raise_for_status()
        sd = im.get("seed") or seed + i
        p = out / f"{stamp}_{args.view}_s{sd}.png"
        Image.open(io.BytesIO(data.content)).convert("RGB").save(p)
        meta = {"species": b, "view": args.view, "lora": v,
                "checkpoint": model, "step": step["$type"], "params": params, "refs": refs,
                "control": {"type": args.control_type, "weight": args.control_weight} if control else None,
                "strength": args.strength, "format": args.format, "seed": sd,
                "workflowId": wid, "jobId": im.get("jobId"), "cost": _cost(r), "generated": stamp}
        p.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"saved {rel(p)}")
        paths.append(p)
    return paths


def _cost(r: dict) -> str:
    tx = (r.get("transactions") or {}).get("list", [])
    return ", ".join(f"{t['amount']} {t['accountType']}" for t in tx) or "?"


# ----------------------------------------------------------------------------- finish
#
# Same reading-back approach as the trainer tool (the LoRA draws on an 8 px grid: 768 = 96 x 8):
#   1. find the grid and take each cell's majority colour from its centre     -> native ~96 px
#   2. flood-fill the background off from the border
#   3. k-means to 15 colours in CIELAB, farthest-first seeds (eyes and small accents keep a colour)
#   4. fit 64x64 (1:1 if it fits, trim thin edges, else drop near-duplicate rows/columns)
#   5. palette-enforcer, with the creature rules from ../README.md: no theme; the front makes
#      normal.pal (15 colours + transparent) and the back is mapped onto that same bank.

def find_grid(a: np.ndarray) -> tuple[int, int, int]:
    """(period, x phase, y phase) of the pixel-art grid, from edge-strength autocorrelation."""
    res = []
    for axis in (1, 0):
        d = np.abs(np.diff(a.astype(int), axis=axis)).sum(2).sum(1 - axis).astype(float)
        d -= d.mean()
        ac = np.array([(d[:-k] * d[k:]).mean() for k in range(4, 17)])
        period = 4 + int(np.argmax(ac >= 0.8 * ac.max()))  # smallest strong period, not a harmonic
        ph = [d[(np.arange(len(d)) % period) == r].sum() for r in range(period)]
        res.append((period, (int(np.argmax(ph)) + 1) % period))
    return res[0][0], res[0][1], res[1][1]


def native(img: Image.Image, period: int | None = None) -> tuple[Image.Image, int]:
    a = np.asarray(img.convert("RGB"))
    p, px, py = find_grid(a)
    if period:  # forced (the model's own 8x); keep the detected phase
        p = period
    g = a >> 3  # GBA 5-bit steps, so JPEG noise inside a cell collapses to one value
    m = 1 if p >= 6 else 0
    h, w = (a.shape[0] - py) // p, (a.shape[1] - px) // p
    out = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        for x in range(w):
            c = g[py + y * p + m: py + (y + 1) * p - m, px + x * p + m: px + (x + 1) * p - m].reshape(-1, 3)
            v, n = np.unique(c, axis=0, return_counts=True)
            out[y, x] = v[n.argmax()] * 8
    return Image.fromarray(out, "RGB"), p


def knock_out_background(img: Image.Image, tol: int = 40) -> Image.Image:
    """Flood-fill from the border through pixels near the border's median colour -> transparent."""
    a = np.array(img.convert("RGB")).astype(int)
    h, w, _ = a.shape
    bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    near = np.abs(a - bg).sum(2) <= tol
    seen = np.zeros((h, w), bool)
    dq = deque([(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)])
    while dq:
        y, x = dq.popleft()
        if 0 <= y < h and 0 <= x < w and not seen[y, x] and near[y, x]:
            seen[y, x] = True
            dq.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    return Image.fromarray(np.dstack([a, np.where(seen, 0, 255)]).astype(np.uint8), "RGBA")


def keep_main_blob(rgba: Image.Image, min_share: float = 0.04) -> Image.Image:
    """Drop stray specks and floor marks: keep 8-connected parts with at least min_share of the pixels."""
    a = np.array(rgba)
    m = a[..., 3] > 0
    lab = np.zeros(m.shape, int)
    sizes, n = {}, 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1
        lab[y, x] = n
        dq, cnt = deque([(y, x)]), 0
        while dq:
            cy, cx = dq.popleft()
            cnt += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        dq.append((ny, nx))
        sizes[n] = cnt
    total = m.sum()
    keep = [k for k, c in sizes.items() if c >= min_share * total] or [max(sizes, key=sizes.get)]
    a[~np.isin(lab, keep), 3] = 0
    return Image.fromarray(a, "RGBA")


def _lab(rgb: np.ndarray) -> np.ndarray:
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def quantise(rgba: Image.Image, k: int = 15, iters: int = 30) -> Image.Image:
    a = np.array(rgba)
    m = a[..., 3] > 0
    u, inv, cnt = np.unique(a[m][:, :3].astype(float), axis=0, return_inverse=True, return_counts=True)
    if len(u) <= k:
        return rgba
    lab, wt = _lab(u), np.sqrt(cnt)
    cen = [lab[np.argmax(cnt)]]
    for _ in range(k - 1):  # farthest-first seeds: rare but distinct colours get a centre
        d = np.min(((lab[:, None] - np.array(cen)[None]) ** 2).sum(2), 1) * wt
        cen.append(lab[np.argmax(d)])
    cen = np.array(cen)
    for _ in range(iters):
        lbl = np.argmin(((lab[:, None] - cen[None]) ** 2).sum(2), 1)
        for j in range(k):
            s = lbl == j
            if s.any():
                cen[j] = (lab[s] * cnt[s, None]).sum(0) / cnt[s].sum()
    lbl = np.argmin(((lab[:, None] - cen[None]) ** 2).sum(2), 1)
    rep = np.zeros((k, 3))
    for j in range(k):
        s = lbl == j
        if s.any():
            rep[j] = np.round((u[s] * cnt[s, None]).sum(0) / cnt[s].sum() / 8) * 8
    a[m, :3] = np.minimum(rep[lbl[inv.reshape(-1)]], 248).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def drop_lines(rgba: Image.Image, w: int, h: int) -> Image.Image:
    """Shrink pixel art by deleting the rows/columns that most nearly repeat their neighbour."""
    a = np.array(rgba).astype(int)
    for axis, target in ((0, h), (1, w)):
        while a.shape[axis] > target:
            d = np.abs(np.diff(a, axis=axis)).sum(2).sum(1 - axis)
            a = np.delete(a, int(np.argmin(d)) + 1, axis=axis)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def fit64(s: Image.Image, fit: str, size: int = 64, max_trim: int = 8) -> tuple[Image.Image, str]:
    s = s.crop(s.getbbox())
    if s.width <= size and s.height <= size:
        return s, "1:1"
    al = np.array(s)[..., 3] > 0
    if fit == "trim" or (fit == "auto" and max(s.width, s.height) - size <= max_trim):
        l, r = 0, s.width
        while r - l > size:  # shave the emptier edge column (thin tails/antennae go first)
            if al[:, l].sum() <= al[:, r - 1].sum():
                l += 1
            else:
                r -= 1
        t, b = 0, s.height
        while b - t > size:
            if al[t].sum() <= al[b - 1].sum():
                t += 1
            else:
                b -= 1
        return s.crop((l, t, r, b)), f"1:1, trimmed {s.width - (r - l)}x{s.height - (b - t)}"
    k = size / max(s.width, s.height)
    w, h = min(size, round(s.width * k)), min(size, round(s.height * k))
    return drop_lines(s, w, h), f"{s.width}x{s.height} -> {w}x{h} by dropping repeated lines"


def place(sprite: Image.Image, size: int = 64) -> Image.Image:
    """Bottom-centre in the 64x64 cell. The game's y_offset tables (README row 6) set the final height."""
    cell = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cell.paste(sprite, ((size - sprite.width) // 2, size - sprite.height), sprite)
    return cell


# Readability: Gen 3 sprites are detailed up close but read from across the room: big flat
# colour areas, few lone pixels. The owner found 15 colours of model texture "too detailed"
# (MASSIFF, 2026-11-01), so the finisher defaults to 12 colours plus one despeckle pass.
# Set from the CLI (--colours, --despeckle).
SIMPLIFY = {"colours": 12, "despeckle": 1}


def despeckle(rgba: Image.Image, passes: int = 1) -> Image.Image:
    """Repaint lone pixels (no 4-neighbour of the same colour, at least 3 opaque neighbours) with
    their most common neighbour colour. Outlines and the silhouette are left alone."""
    a = np.array(rgba)
    h, w, _ = a.shape
    for _ in range(passes):
        b = a.copy()
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if a[y, x, 3] == 0:
                    continue
                nb = [a[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
                if any((n == a[y, x]).all() for n in nb):
                    continue
                op = np.array([n for n in nb if n[3] > 0])
                if len(op) >= 3:
                    vals, cnt = np.unique(op, axis=0, return_counts=True)
                    b[y, x] = vals[cnt.argmax()]
        a = b
    return Image.fromarray(a, "RGBA")


def prepare(raw: Path, fit: str, period: int | None) -> tuple[Image.Image, Image.Image, str]:
    """raw 768 -> (64x64 RGBA cell, native figure, log line)."""
    nat, p = native(Image.open(raw).convert("RGB"), period)
    fig = knock_out_background(nat)
    if fig.getbbox() is None:
        sys.exit(f"{raw.name}: nothing left after background removal")
    fig = keep_main_blob(fig)
    k = SIMPLIFY["colours"]
    fig = quantise(fig.crop(fig.getbbox()), k)
    if SIMPLIFY["despeckle"]:
        fig = quantise(despeckle(fig, SIMPLIFY["despeckle"]), k)
    sprite, how = fit64(fig, fit)
    return place(sprite), fig, f"grid {p}px -> native {nat.width}, figure {fig.width}x{fig.height}, {how}"


def _enforce(rgba: Path, final: Path, pal: Path, own: bool) -> int:
    if own:  # the front owns the bank: 15 colours + transparent
        _run([sys.executable, "-m", "gba_palette", "enforce", str(rgba), str(final), "--bpp", "4",
              "--colours", str(SIMPLIFY["colours"]), "--write-pal", str(pal)])
    else:  # back and frame 2 use the same bank (one palette per species in the game)
        _run([sys.executable, "-m", "gba_palette", "enforce", str(rgba), str(final), "--bpp", "4",
              "--pal", str(pal)])
    return _run([sys.executable, "-m", "gba_palette", "check", str(final), "--pal", str(pal)], check=False)


def align_to(cell: Image.Image, ref: Image.Image, reach: int = 6) -> tuple[Image.Image, tuple[int, int]]:
    """Shift frame 2 so its body sits where the front's does (best alpha overlap), as vanilla does."""
    a, r = np.array(cell)[..., 3] > 0, np.array(ref)[..., 3] > 0
    best, at = -1, (0, 0)
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            sh = np.roll(np.roll(a, dy, 0), dx, 1)
            score = (sh & r).sum() - 0.5 * (sh ^ r).sum()
            if score > best:
                best, at = score, (dx, dy)
    out = Image.new("RGBA", cell.size, (0, 0, 0, 0))
    out.paste(cell, at, cell)  # paste clips negative offsets
    return out, at


def lunge(front: Path, dst: Path, reach: int = 3, hip: float = 0.62) -> Path:
    """Frame 2 without a model: the body above the hips leans forward (towards the left, the way
    fronts face) and dips 1 px, up to `reach` px at the head; legs and feet stay planted. Same
    pixels and palette as the front, so the two frames alternate without shimmer. Owner pick for
    MASSIFF (2026-11-01) over image-to-image frames, which redrew the texture and flickered."""
    f = Image.open(front)
    a = np.array(f)
    ys = np.nonzero(a)[0]
    top, bot = ys.min(), ys.max()
    legs = top + int((bot - top) * hip)
    out = np.zeros_like(a)
    for y in range(a.shape[0]):
        if y >= legs:
            dx, dy = 0, 0
        else:
            dx, dy = -int(round(1 + (reach - 1) * (legs - y) / max(1, legs - top))), 1
        if y + dy >= a.shape[0]:
            continue
        row = np.roll(a[y], dx)
        if dx < 0:
            row[dx:] = 0
        out[y + dy][row > 0] = row[row > 0]
    gy = np.arange(a.shape[0])[:, None]
    seam = (out == 0) & (a > 0) & (gy >= legs - 1) & (gy <= legs + 1)  # close the hip seam
    out[seam] = a[seam]
    im = Image.fromarray(out, "P")
    im.putpalette(f.getpalette())
    im.save(dst)
    return dst


def stack_anim(front: Path, frame2: Path, dst: Path, pal: Path) -> int:
    """anim_front.png: 64x128, frame 1 = front.png, frame 2 below, one indexed palette."""
    f1, f2 = Image.open(front), Image.open(frame2)
    a = np.vstack([np.array(f1), np.array(f2)])
    im = Image.fromarray(a.astype(np.uint8), "P")
    im.putpalette(f1.getpalette())
    im.save(dst)
    return _run([sys.executable, "-m", "gba_palette", "check", str(dst), "--pal", str(pal)], check=False)


def write_shiny(normal: Path, dst: Path, hue: float = 180, sat: float = 1.0, val: float = 1.0,
                keep_sat: float = 0.8) -> Path:
    """shiny.pal: same indices as normal.pal, colours recoloured. Hue is rotated (degrees) on the body
    colours; greys (s < 0.08), near-black outlines and the most saturated accents (eyes, mouth, s >=
    keep_sat) keep their colour, as vanilla shinies keep eyes and outlines. Values snap to GBA steps."""
    import colorsys
    pal = _jasc(normal)
    out = [pal[0]]
    for r, g, b in pal[1:]:
        h, s_, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s_ < 0.08 or v < 0.12 or s_ >= keep_sat:
            out.append((r, g, b))
            continue
        rgb = colorsys.hsv_to_rgb((h + hue / 360) % 1, min(1, s_ * sat), min(1, v * val))
        out.append(tuple(min(248, int(round(c * 255 / 8)) * 8) for c in rgb))
    dst.write_text("JASC-PAL\r\n0100\r\n16\r\n" + "".join(f"{r} {g} {b}\r\n" for r, g, b in out))
    return dst


def _with_pal(png: Path, pal: Path) -> Image.Image:
    im = Image.open(png).copy()
    im.putpalette([c for rgb in _jasc(pal) for c in rgb])
    a = np.array(im.convert("RGBA"))
    a[np.array(Image.open(png)) == 0, 3] = 0
    return Image.fromarray(a, "RGBA")


def finish(front_raw: Path, back_raw: Path | None, fit: str, period: int | None, out: Path | None,
           frame2_raw: Path | None = None, shiny: dict | None = None) -> Path:
    out_dir = out or front_raw.parent.parent / "finished" / f"{front_raw.stem}"
    out_dir.mkdir(parents=True, exist_ok=True)
    pal = out_dir / "normal.pal"
    results, cells = {}, {}
    use_lunge = str(frame2_raw) == "lunge"
    for view, raw in (("front", front_raw), ("back", back_raw), ("frame2", None if use_lunge else frame2_raw)):
        if raw is None:
            continue
        cell, fig, how = prepare(raw, fit, period)
        if view == "frame2":
            cell, at = align_to(cell, cells["front"])
            how += f", aligned to the front by {at}"
        cells[view] = cell
        fig.save(out_dir / f"{view}_native.png")
        rgba = out_dir / f"{view}_rgba.png"
        cell.save(rgba)
        final = out_dir / f"{view}.png"
        ok = _enforce(rgba, final, pal, own=view == "front")
        Image.open(final).convert("RGBA").resize((256, 256), Image.NEAREST).save(out_dir / f"{view}_4x.png")
        results[view] = final
        print(f"{view:<6} {raw.name}: {how}; {'PASS' if ok == 0 else 'FAIL'} -> {rel(final)}")
    if use_lunge:
        results["frame2"] = lunge(results["front"], out_dir / "frame2.png")
        ok = _run([sys.executable, "-m", "gba_palette", "check", str(results["frame2"]), "--pal", str(pal)], check=False)
        print(f"frame2 lunge from the front; {'PASS' if ok == 0 else 'FAIL'} -> {rel(results['frame2'])}")
    if "frame2" in results:
        anim = out_dir / "anim_front.png"
        ok = stack_anim(results["front"], results["frame2"], anim, pal)
        f1, f2 = np.array(Image.open(results["front"])), np.array(Image.open(results["frame2"]))
        change = ((f1 != f2) & ((f1 > 0) | (f2 > 0))).sum() / max(1, ((f1 > 0) | (f2 > 0)).sum())
        print(f"anim   frame 2 changes {change:.0%} of the figure (vanilla median 72%); "
              f"{'PASS' if ok == 0 else 'FAIL'} -> {rel(anim)}")
        frames = [Image.open(results[v]).convert("RGBA").resize((192, 192), Image.NEAREST) for v in ("front", "frame2")]
        frames[0].save(out_dir / "anim_front_3x.gif", save_all=True, append_images=frames[1:],
                       duration=[400, 400], loop=0, disposal=2)
    if shiny is not None:
        sp = write_shiny(pal, out_dir / "shiny.pal", **shiny)
        ok = _run([sys.executable, "-m", "gba_palette", "check", str(sp)], check=False)
        row = [_with_pal(results[v], p) for v in ("front", "back") if v in results for p in (pal, sp)]
        sheet = Image.new("RGBA", (64 * len(row), 64), (255, 255, 255, 255))
        for i, im in enumerate(row):
            sheet.alpha_composite(im, (64 * i, 0))
        sheet.resize((sheet.width * 4, 256), Image.NEAREST).save(out_dir / "shiny_compare_4x.png")
        print(f"shiny  {shiny}; {'PASS' if ok == 0 else 'FAIL'} -> {rel(sp)}")
    srcs = {k: rel(v) if isinstance(v, Path) else v
            for k, v in (("front", front_raw), ("back", back_raw), ("frame2", frame2_raw)) if v}
    (out_dir / "sources.json").write_text(json.dumps({**srcs, "shiny": shiny}, indent=2) + "\n")
    mock = battle_mockup(results.get("front"), results.get("back"), out_dir / "battle_mockup_3x.png")
    print(f"mockup -> {rel(mock)}")
    return out_dir


# ----------------------------------------------------------------------------- battle mockup

def _jasc(p: Path) -> list[tuple[int, int, int]]:
    lines = p.read_text().split()
    n = int(lines[2])
    return [tuple(int(x) for x in lines[3 + i * 3: 6 + i * 3]) for i in range(n)]


def battle_bg(env: str = "tall_grass") -> Image.Image:
    """240x160 render of a vanilla battle environment tilemap (map.bin over tiles.png, banks 2+)."""
    d = GAME / "graphics" / "battle_environment" / env
    tiles = np.array(Image.open(d / "tiles.png"))
    pal = _jasc(d / "palette.pal")
    m = np.frombuffer((d / "map.bin").read_bytes(), "<u2")[:1024].reshape(32, 32)  # first screenblock
    tw = tiles.shape[1] // 8
    out = np.zeros((m.shape[0] * 8, 32 * 8, 3), np.uint8)
    out[:] = pal[0]
    for ty in range(m.shape[0]):
        for tx in range(32):
            e = int(m[ty, tx])
            t, hf, vf, bank = e & 1023, e >> 10 & 1, e >> 11 & 1, e >> 12
            tile = tiles[(t // tw) * 8:(t // tw) * 8 + 8, (t % tw) * 8:(t % tw) * 8 + 8] & 15
            if hf:
                tile = tile[:, ::-1]
            if vf:
                tile = tile[::-1]
            base = max(0, bank - 2) * 16
            for y in range(8):
                for x in range(8):
                    if tile[y, x] or bank >= 2:
                        out[ty * 8 + y, tx * 8 + x] = pal[min(len(pal) - 1, base + tile[y, x])]
    return Image.fromarray(out[:160, :240], "RGB")


def _sprite_rgba(p: Path) -> Image.Image:
    """Indexed sprite -> RGBA with index 0 transparent (as the GBA draws it)."""
    im = Image.open(p)
    a = np.array(im.convert("RGBA"))
    if im.mode == "P":
        a[np.array(im) == 0, 3] = 0
    return Image.fromarray(a, "RGBA")


def battle_mockup(front: Path | None, back: Path | None, dst: Path, scale: int = 3) -> Path:
    """Approximate battle screen: opponent's front on the far pad, our back on the near one, text box."""
    try:
        scene = battle_bg().convert("RGBA")
    except Exception:  # noqa: BLE001  (no game checkout: plain backdrop)
        scene = Image.new("RGBA", (240, 160), (144, 200, 120, 255))
    if front:  # enemy mon: 64x64 cell centred at x=176; feet on the far pad
        scene.alpha_composite(_sprite_rgba(front), (144, 4))
    if back:  # player mon: 64x64 cell centred at x=72, bottom hidden by the text box like vanilla
        scene.alpha_composite(_sprite_rgba(back), (40, 48))
    box = Image.new("RGBA", (240, 48), (40, 80, 104, 255))
    box.paste((248, 248, 248, 255), (4, 4, 236, 44))
    scene.alpha_composite(box, (0, 112))
    scene.convert("RGB").resize((240 * scale, 160 * scale), Image.NEAREST).save(dst)
    return dst


# ----------------------------------------------------------------------------- prep (reference -> start image)

def cmd_prep(args):
    """Turn a concept/movie reference into a sprite-like start image for image to image: cut out,
    face left, small contrast lift, scale to ~60 px wide (vanilla fronts are a median 48x48, max 64),
    k-means to 12 colours, 1 px dark outline, centred on a white 96x96 canvas, then nearest-neighbour
    up to 768 so the model sees its own 8 px grid. Low denoise (0.4-0.55) from this keeps the real
    creature's shape and colours; the LoRA only redraws it as a sprite."""
    from PIL import ImageEnhance
    src = args.reference
    if src.startswith(("http://", "https://")):
        r = requests.get(src, timeout=60)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content))
    else:
        im = Image.open(src)
    im = im.convert("RGBA")
    if not (np.array(im)[..., 3] < 255).any():  # no alpha: knock out the background colour
        im = knock_out_background(im)
    im = im.crop(im.getbbox())
    if args.flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    rgb = ImageEnhance.Contrast(im.convert("RGB")).enhance(args.contrast)
    rgb = ImageEnhance.Color(rgb).enhance(args.saturation)
    im = Image.merge("RGBA", (*rgb.split(), im.split()[3]))
    k = min(args.width / im.width, 64 / im.height)
    s = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    a = np.array(s)
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
    s = quantise(Image.fromarray(a, "RGBA"), args.colours)
    a = np.array(s)
    m = a[..., 3] > 0
    pad = np.pad(m, 1)
    ring = ~m & (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:])
    a[ring] = (40, 32, 32, 255)
    s = Image.fromarray(a, "RGBA")
    canvas = Image.new("RGBA", (96, 96), (255, 255, 255, 255))
    canvas.alpha_composite(s, ((96 - s.width) // 2, (96 - s.height) // 2 + 6))
    out = Path(args.out) if args.out else HERE / "refs" / f"{Path(args.species).name}_prep.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").resize((768, 768), Image.NEAREST).save(out)
    print(f"prep {s.width}x{s.height} -> {rel(out)}  (use as jobs.json \"init\", denoise ~0.45)")


# ----------------------------------------------------------------------------- utils, cli

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def _run(cmd, check=True) -> int:
    r = subprocess.run(cmd, cwd=ENFORCER, stdout=subprocess.DEVNULL if not check else None)
    if check and r.returncode:
        sys.exit(f"failed: {' '.join(cmd)}")
    return r.returncode


def cmd_finish(args):
    shiny = None
    if args.shiny or args.shiny_hue is not None:
        shiny = dict(args.shiny_species and brief(args.shiny_species)["shiny"] or {})
        if args.shiny_hue is not None:
            shiny["hue"] = args.shiny_hue
        if args.shiny_sat is not None:
            shiny["sat"] = args.shiny_sat
    finish(Path(args.front).resolve(), Path(args.back).resolve() if args.back else None,
           args.fit, args.period, Path(args.out).resolve() if args.out else None,
           (args.frame2 if args.frame2 == "lunge" else Path(args.frame2).resolve()) if args.frame2 else None,
           shiny)


def cmd_run(args):
    """Front first; then each back starts from its own front, mirrored (image to image with the
    `backside` tag), so the back keeps the front's body and colours. Text-only backs came out as a
    different creature in the first test (Massiff, 2026-11-01)."""
    if args.seed is None:
        args.seed = random.randrange(1, 2**31 - 1)  # same seed for both views
    views = ["front", "back"] if args.view == "both" else [args.view]
    fronts, backs = [], []
    if "front" in views:
        fronts = cmd_gen(argparse.Namespace(**{**vars(args), "view": "front"}))
    if "back" in views:
        if fronts and not args.back_text_only:
            for f in fronts:
                a = {**vars(args), "view": "back", "n": 1, "init": image_ref(str(f), flip=True),
                     "denoise": args.back_denoise, "control": None, "flip": False}
                backs += cmd_gen(argparse.Namespace(**a))
        else:
            backs = cmd_gen(argparse.Namespace(**{**vars(args), "view": "back"}))
    if args.whatif:
        return
    for i, f in enumerate(fronts):
        finish(f, backs[i] if i < len(backs) else None, args.fit, args.period, None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models").set_defaults(fn=cmd_models)

    def gen_args(p, both=False):
        p.add_argument("species", help="species folder in game/graphics/pokemon (e.g. poochyena)")
        p.add_argument("--view", choices=["front", "back", "frame2"] + (["both"] if both else []),
                       default="both" if both else "front")
        p.add_argument("--version", help="LoRA version id, or a name word (v2, v1); default v2.1-beta")
        p.add_argument("--checkpoint", help="base checkpoint AIR (default: DreamShaper 8 for SD 1.5)")
        p.add_argument("--prompt", help="full prompt override")
        p.add_argument("--style", help="LoRA generation tag; default gen3 (gen1..gen5)")
        p.add_argument("--negative")
        p.add_argument("--init", help="image to image: URL or local file (concept art, a previous front)")
        p.add_argument("--denoise", type=float, help="with --init: 0..1, how far from the image (default 0.6)")
        p.add_argument("--flip", action="store_true", help="mirror the --init/--control image (fronts face left)")
        p.add_argument("--control", help="ControlNet reference: URL or local file")
        p.add_argument("--control-type", default="canny", help="ControlNet preprocessor (canny, lineart, ...)")
        p.add_argument("--control-weight", type=float, default=0.7)
        p.add_argument("--seed", type=int)
        p.add_argument("-n", type=int, default=1, help="images in this request (per view)")
        p.add_argument("--strength", type=float, default=0.9, help="LoRA weight")
        p.add_argument("--steps", type=int, default=25)
        p.add_argument("--cfg", type=float, help="CFG scale; default 5 with an input image, 7 without")
        p.add_argument("--scheduler", default="EulerA")
        p.add_argument("--size", type=int, default=768)
        p.add_argument("--timeout", type=int, default=600)
        p.add_argument("--format", choices=["jpeg", "png"], default="jpeg",
                       help="jpeg ~3 Buzz/image (block vote absorbs jpeg noise), png costs more")
        p.add_argument("--currency", default="blue",
                       help="Buzz account(s) to spend, comma list: blue (earned), yellow (bought)")
        p.add_argument("--whatif", action="store_true", help="price the job, spend nothing")

    def finish_args(p):
        p.add_argument("--fit", choices=["auto", "trim", "shrink"], default="auto",
                       help="auto: 1:1 if it fits, trim if only a thin edge sticks out, else shrink")
        p.add_argument("--period", type=int, help="force the pixel grid (the LoRA's is 8)")
        p.add_argument("--colours", type=int, default=12, help="sprite colours (max 15; default 12 for readability)")
        p.add_argument("--despeckle", type=int, default=1, help="lone-pixel cleanup passes (0 = off)")

    pp = sub.add_parser("prep", help="reference/concept image -> pixelated start image for --init")
    pp.add_argument("species"); pp.add_argument("reference", help="URL or file (movie still, concept art)")
    pp.add_argument("--flip", action="store_true", help="mirror (fronts face left)")
    pp.add_argument("--width", type=int, default=60)
    pp.add_argument("--colours", type=int, default=12)
    pp.add_argument("--contrast", type=float, default=1.35)
    pp.add_argument("--saturation", type=float, default=1.2)
    pp.add_argument("--out")
    pp.set_defaults(fn=cmd_prep)
    g = sub.add_parser("gen"); gen_args(g); g.set_defaults(fn=cmd_gen)
    f = sub.add_parser("finish")
    f.add_argument("front", help="raw front .png"); f.add_argument("back", nargs="?", help="raw back .png")
    f.add_argument("--out", help="output folder (default runs/<species>/finished/<front stem>/)")
    f.add_argument("--frame2", help="'lunge' (front leans forward, no Buzz) or a raw frame-2 .png from gen --view frame2; writes anim_front.png")
    f.add_argument("--shiny", action="store_true", help="write shiny.pal (settings from jobs.json via --species)")
    f.add_argument("--species", dest="shiny_species", help="species for jobs.json shiny settings")
    f.add_argument("--shiny-hue", type=float, help="shiny hue rotation in degrees (default 180)")
    f.add_argument("--shiny-sat", type=float, help="shiny saturation factor (default 1.0)")
    finish_args(f); f.set_defaults(fn=cmd_finish)
    r = sub.add_parser("run"); gen_args(r, both=True); finish_args(r)
    r.add_argument("--back-denoise", type=float, default=0.7,
                   help="back from the mirrored front: 0..1, higher redraws more (default 0.7)")
    r.add_argument("--back-text-only", action="store_true", help="back from the prompt alone, not the front"); r.set_defaults(fn=cmd_run)
    args = ap.parse_args()
    if hasattr(args, "colours") and args.cmd != "prep":
        SIMPLIFY.update(colours=min(15, args.colours), despeckle=args.despeckle)
    args.fn(args)


if __name__ == "__main__":
    main()

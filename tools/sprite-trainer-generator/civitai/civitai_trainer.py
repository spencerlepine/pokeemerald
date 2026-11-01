#!/usr/bin/env python3
"""Trainer front pics through Civitai's hosted generator (no local GPU).

Pipeline for one trainer:
    gen     prompt -> Civitai (SDXL + trainer LoRA 159333) -> 768x768 originals in runs/<trainer>/raw/
    finish  768 -> 96 (8x block vote) -> background off -> fit 64x64 -> palette-enforcer enforce + check

Subcommands
    models                     list the LoRA's versions (public API, no key) and cache them in models.json
    gen <trainer> [...]        submit a job; --whatif prices it without spending Buzz
    finish <raw.png> [...]     post-process one original into a game-legal 64x64 4bpp PNG
    run <trainer> [...]        gen then finish every image it returns

<trainer> is the front pic's file stem (e.g. magma_leader_maxie) or the wiki asset path. Its brief
(sw_subject) comes from ../../../wiki/database/pending_art.csv; extra look notes come from jobs.json.

The API key is read from CIVITAI_API_TOKEN, or from a git-ignored .env file next to this script.
It is never printed or written anywhere else.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import random
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
WIKI_CSV = REPO / "wiki" / "database" / "pending_art.csv"
ENFORCER = REPO / "tools" / "palette-enforcer"
MODELS_CACHE = HERE / "models.json"
JOBS_FILE = HERE / "jobs.json"
RUNS = HERE / "runs"

LORA_MODEL_ID = 159333  # Pokemon Trainer Sprite PixelArt (titansteng)
PUBLIC_API = "https://civitai.com/api/v1"
ORCHESTRATOR = "https://orchestration.civitai.com"

# Base checkpoints by LoRA base model. Override with --checkpoint.
CHECKPOINTS = {
    "sdxl": "urn:air:sdxl:checkpoint:civitai:101055@128078",  # SDXL 1.0 base
    "sd1": "urn:air:sd1:checkpoint:civitai:4384@128713",      # DreamShaper 8
}

# Reusable template: the subject leads (weighted) and the job's look notes describe the silhouette, so
# the LoRA supplies only the art style. "pokemon trainer" is deliberately absent; it pulls every subject
# toward a generic kid in a cap holding a Poke Ball. Per-job `pose` and `negative` extend it.
PROMPT = ("{trigger}{style}, ({subject}:1.3), {desc}, full body character sprite, {pose}, "
          "pixel art, game sprite, crisp dark outlines, solid white background, simple background{palette}")
POSE = "standing, facing left, three-quarter view"
NEGATIVE = ("poke ball, pokeball, holding ball, baseball cap, generic pokemon trainer, anime boy, "
            "scenery, detailed background, gradient background, floor, shadow, text, watermark, "
            "signature, frame, border, multiple characters, multiple views, character sheet, turnaround, duplicate, cropped, cut off feet, blurry, 3d, "
            "photo, realistic, painting, smooth shading")

# --view back: tested 2026-11-01 (Leia, seed 303682211). The LoRA does draw a clean back view, but
# full body and arms out, not the waist-up over-the-shoulder throw a back pic needs: concept only.
BACK_PROMPT = ("solo, single character, (back view:1.5), (from behind:1.4), (back of head:1.3), "
               "back turned to the viewer, looking away, ")
BACK_NEGATIVE = ("face, front view, facing viewer, eyes, side view, profile, multiple views, "
                 "character sheet, turnaround, two people, ")

# Faction theme -> words for the prompt (the prompt is a hint; enforce is the guarantee).
THEME_WORDS = {
    "imperial-order": "black, grey and red",
    "alliance-dawn": "orange, white and blue",
    "swamp-throne": "olive green, brown and gold",
}


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
        key = (want or "sdxl").lower()
        hit = [v for v in vs if key in (v["baseModel"] or "").lower().replace(" ", "")
               or key in (v["name"] or "").lower()]
    if not hit:
        sys.exit(f"No LoRA version matches {want!r}; run `models` to list them.")
    return hit[0]


def family(v: dict) -> str:
    return "sdxl" if "xl" in (v["baseModel"] or "").lower() else "sd1"


# ----------------------------------------------------------------------------- briefs

def brief(trainer: str) -> dict:
    stem = Path(trainer).stem
    row = {}
    if WIKI_CSV.exists():
        with WIKI_CSV.open(newline="") as f:
            for r in csv.DictReader(f):
                if r["kind"] == "trainers" and Path(r["path"]).stem == stem:
                    row = r
                    if r["subkind"] == "front_pics":
                        break
    jobs = json.loads(JOBS_FILE.read_text()) if JOBS_FILE.exists() else {}
    job = jobs.get(stem, {})
    subject = job.get("subject") or row.get("sw_subject") or stem.replace("_", " ")
    return {"stem": stem, "wiki_path": row.get("path"), "sw_subject": row.get("sw_subject"),
            "subject": subject, "desc": job.get("desc", ""), "theme": job.get("theme", "factions"),
            "style": job.get("style", ""), "pose": job.get("pose", POSE),
            "negative": job.get("negative", ""), "pair": bool(job.get("pair"))}


def build_prompt(b: dict, v: dict) -> str:
    trig = ", ".join(v.get("trainedWords") or [])
    p = PROMPT.format(trigger=(trig + ", ") if trig else "", style=b["style"],
                      subject=b["subject"].lower(), desc=b["desc"], pose=b["pose"],
                      palette=(", " + THEME_WORDS[b["theme"]]) if b["theme"] in THEME_WORDS else "")
    return ", ".join(s.strip() for s in p.split(",") if s.strip())


# ----------------------------------------------------------------------------- generate

def cmd_gen(args) -> list[Path]:
    b = brief(args.trainer)
    if args.style is not None:
        b["style"] = args.style
    v = pick_version(args.version)
    fam = family(v)
    prompt = args.prompt or build_prompt(b, v)
    base_neg = NEGATIVE.replace("multiple characters, ", "").replace("duplicate, ", "") if b["pair"] else NEGATIVE  # two-person pics
    negative = args.negative or ", ".join(x for x in (b["negative"], base_neg) if x)
    if args.view == "back":  # concept art for sprite-trainer-back-generator (full body, from behind)
        prompt = BACK_PROMPT + prompt.replace(POSE, "standing, raising one arm to throw")
        negative = BACK_NEGATIVE + negative
    seed = args.seed if args.seed is not None else random.randrange(1, 2**31 - 1)
    lora_air = v.get("air") or f"urn:air:{fam}:lora:civitai:{LORA_MODEL_ID}@{v['id']}"
    params = {"prompt": prompt, "negativePrompt": negative,
              "scheduler": args.scheduler, "steps": args.steps, "cfgScale": args.cfg,
              "width": args.size, "height": args.size, "seed": seed, "clipSkip": 2}
    # v2 workflows API. The v1 /consumer/jobs endpoint only spends yellow (bought) Buzz and answers
    # 403 "Insufficient Buzz" on an account that holds blue Buzz; v2 takes a `currencies` list.
    workflow = {
        "steps": [{"$type": "textToImage", "input": {
            "model": args.checkpoint or CHECKPOINTS[fam],
            "additionalNetworks": {lora_air: {"type": "Lora", "strength": args.strength}},
            **params, "quantity": args.n, "outputFormat": args.format}}],
        "currencies": args.currency.split(","),
    }
    print(f"trainer  {b['stem']}  ({b['sw_subject']})\nlora     {v['name']} [{v['baseModel']}] "
          f"@{v['id']}\nprompt   {prompt}\nseed     {seed}  x{args.n}  ({args.format})")

    url = f"{ORCHESTRATOR}/v2/consumer/workflows"
    if args.whatif:
        r = http("POST", url, params={"whatif": "true"}, json=workflow).json()
        print(f"whatif: {_cost(r)}  insufficientBuzz={r.get('transactions', {}).get('insufficientBuzz')}")
        q = (r["steps"][0].get("queuePosition") or {}) if r.get("steps") else {}
        if q:
            print(f"queue:  {q}")
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

    out = RUNS / (b["stem"] + ("_back" if args.view == "back" else "")) / "raw"
    out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    paths = []
    for i, im in enumerate(imgs):
        data = requests.get(im["url"], timeout=120)
        data.raise_for_status()
        sd = im.get("seed") or seed + i
        p = out / f"{stamp}_s{sd}.png"
        Image.open(__import__("io").BytesIO(data.content)).convert("RGB").save(p)
        meta = {"trainer": b, "lora": v, "checkpoint": workflow["steps"][0]["input"]["model"],
                "params": params, "strength": args.strength, "format": args.format, "seed": sd,
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
# The LoRA draws real pixel art on an 8 px grid (768 = 96 x 8, grid aligned to 0), at about the
# scale of the vanilla front pics (figures 41 wide x 58 tall median, 13-15 colours). So the finisher
# reads the art back at its own resolution instead of re-drawing it:
#   1. find the grid (period + phase) and take each cell's majority colour from its centre,
#      ignoring the cell borders where JPEG ringing lives          -> the native ~96 px sprite
#   2. flood-fill the background off from the border
#   3. k-means to 15 colours in CIELAB, seeded farthest-first so small but distinct areas (skin,
#      eyes, a saber, chest lights) keep a colour instead of being merged into the big darks
#   4. fit 64x64: 1:1 if it fits; trim a few thin edge columns (a saber tip); otherwise delete the
#      rows/columns that most nearly duplicate a neighbour, which keeps 1 px outlines and faces
#   5. palette-enforcer: snap to GBA steps, pull colours onto the theme only within Delta E 12

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


def native(img: Image.Image) -> tuple[Image.Image, int]:
    a = np.asarray(img.convert("RGB"))
    period, px, py = find_grid(a)
    g = a >> 3  # GBA 5-bit steps, so JPEG noise inside a cell collapses to one value
    m = 1 if period >= 6 else 0
    h, w = (a.shape[0] - py) // period, (a.shape[1] - px) // period
    out = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        for x in range(w):
            c = g[py + y * period + m: py + (y + 1) * period - m,
                  px + x * period + m: px + (x + 1) * period - m].reshape(-1, 3)
            v, n = np.unique(c, axis=0, return_counts=True)
            out[y, x] = v[n.argmax()] * 8
    return Image.fromarray(out, "RGB"), period


def knock_out_background(img: Image.Image, tol: int = 40) -> Image.Image:
    """Flood-fill from the border through pixels near the border's median colour -> transparent."""
    a = np.array(img.convert("RGB")).astype(int)
    h, w, _ = a.shape
    bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    near = np.abs(a - bg).sum(2) <= tol
    # plus pale neutral greys (vignettes/gradients in the corners); dark outlines stop the fill
    near |= (a.min(2) >= 200) & (a.max(2) - a.min(2) <= 16)
    seen = np.zeros((h, w), bool)
    dq = deque([(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)])
    while dq:
        y, x = dq.popleft()
        if 0 <= y < h and 0 <= x < w and not seen[y, x] and near[y, x]:
            seen[y, x] = True
            dq.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    return Image.fromarray(np.dstack([a, np.where(seen, 0, 255)]).astype(np.uint8), "RGBA")


def despeck(img: Image.Image, share: float = 0.04, light: int = 170) -> Image.Image:
    """Drop small detached islands of light pixels (white/grey background scraps the flood fill missed)."""
    a = np.array(img)
    op = a[..., 3] > 0
    h, w = op.shape
    seen = np.zeros_like(op)
    total = op.sum()
    for y in range(h):
        for x in range(w):
            if op[y, x] and not seen[y, x]:
                st, comp = [(y, x)], []
                seen[y, x] = True
                while st:
                    cy, cx = st.pop(); comp.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and op[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True; st.append((ny, nx))
                ys, xs = zip(*comp)
                if len(comp) < share * total and a[ys, xs, :3].min(1).mean() >= light:
                    a[ys, xs, 3] = 0
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
    if fit == "trim" or (fit == "auto" and s.height <= size and s.width - size <= max_trim):
        l, r = 0, s.width
        while r - l > size:  # shave the emptier edge column (thin protrusions go first)
            if al[:, l].sum() <= al[:, r - 1].sum():
                l += 1
            else:
                r -= 1
        top = max(0, s.height - size)  # never the feet
        return s.crop((l, top, r, s.height)), f"1:1, trimmed {s.width - (r - l)}x{top}"
    k = size / max(s.width, s.height)
    w, h = min(size, round(s.width * k)), min(size, round(s.height * k))
    return drop_lines(s, w, h), f"{s.width}x{s.height} -> {w}x{h} by dropping repeated lines"


def place(sprite: Image.Image, size: int = 64) -> Image.Image:
    """Bottom-centre in a size x size cell (vanilla trainers stand on the bottom row)."""
    cell = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cell.paste(sprite, ((size - sprite.width) // 2, size - sprite.height), sprite)
    return cell


def finish(raw: Path, theme: str, fit: str, free: int) -> Path:
    src = Image.open(raw).convert("RGB")
    out_dir = raw.parent.parent / ("finished" if fit == "auto" else f"finished_{fit}")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = raw.stem

    nat, period = native(src)
    fig = despeck(knock_out_background(nat))
    if fig.getbbox() is None:
        sys.exit(f"{raw.name}: nothing left after background removal")
    fig = quantise(fig.crop(fig.getbbox()))
    sprite, how = fit64(fig, fit)
    cell = place(sprite)

    fig.save(out_dir / f"{stem}_native.png")
    rgba = out_dir / f"{stem}_rgba.png"
    cell.save(rgba)
    final = out_dir / f"{stem}.png"
    pal = out_dir / f"{stem}.pal"
    cmd = [sys.executable, "-m", "gba_palette", "enforce", str(rgba), str(final), "--bpp", "4",
           "--theme", theme, "--free", str(free), "--write-pal", str(pal)]
    _run(cmd)
    ok = _run([sys.executable, "-m", "gba_palette", "check", str(final), "--theme", theme], check=False)
    Image.open(final).convert("RGBA").resize((256, 256), Image.NEAREST).save(out_dir / f"{stem}_4x.png")
    print(f"{raw.name}: grid {period}px -> native {nat.width}, figure {fig.width}x{fig.height}, {how}; "
          f"{'PASS' if ok == 0 else 'FAIL'} -> {rel(final)}")
    return final


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
    for p in args.raw:
        finish(Path(p).resolve(), args.theme, args.fit, args.free)


def cmd_run(args):
    paths = cmd_gen(args)
    theme = args.theme or brief(args.trainer)["theme"]
    for p in paths:
        finish(p, theme, args.fit, args.free)


# ----------------------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models").set_defaults(fn=cmd_models)

    def gen_args(p):
        p.add_argument("trainer")
        p.add_argument("--version", help="LoRA version id, or a base-model word (sdxl, sd1); default sdxl")
        p.add_argument("--checkpoint", help="base checkpoint AIR (default per base model)")
        p.add_argument("--prompt", help="full prompt override")
        p.add_argument("--view", choices=["front", "back"], default="front",
                       help="back: full-body back-view concept for sprite-trainer-back-generator (runs/<trainer>_back/)")
        p.add_argument("--style", help="gen1 or gen2 to force the old Game Boy look; default none (full colour, like the model previews)")
        p.add_argument("--negative")
        p.add_argument("--seed", type=int)
        p.add_argument("-n", type=int, default=1, help="images in this request")
        p.add_argument("--strength", type=float, default=0.75, help="LoRA weight; lower lets the subject through")
        p.add_argument("--steps", type=int, default=25)
        p.add_argument("--cfg", type=float, default=7.0)
        p.add_argument("--scheduler", default="EulerA")
        p.add_argument("--size", type=int, default=768)
        p.add_argument("--timeout", type=int, default=600)
        p.add_argument("--format", choices=["jpeg", "png"], default="jpeg",
                       help="jpeg costs ~2.5 Buzz/image, png ~4.5 (block vote absorbs jpeg noise)")
        p.add_argument("--currency", default="blue",
                       help="Buzz account(s) to spend, comma list: blue (earned), yellow (bought)")
        p.add_argument("--whatif", action="store_true", help="price the job, spend nothing")

    def finish_args(p):
        p.add_argument("--theme", help="palette theme id (default: jobs.json, else factions)")
        p.add_argument("--fit", choices=["auto", "trim", "shrink"], default="auto",
                       help="auto: 1:1 if it fits, trim if only a thin edge sticks out, else shrink")
        p.add_argument("--free", type=int, default=15,
                       help="colours allowed to stay off-theme (beyond Delta E 12); 15 keeps all shading")

    g = sub.add_parser("gen"); gen_args(g); g.set_defaults(fn=cmd_gen)
    f = sub.add_parser("finish"); f.add_argument("raw", nargs="+"); finish_args(f); f.set_defaults(fn=cmd_finish)
    r = sub.add_parser("run"); gen_args(r); finish_args(r); r.set_defaults(fn=cmd_run)
    args = ap.parse_args()
    if args.cmd == "finish" and not args.theme:
        args.theme = "factions"
    args.fn(args)


if __name__ == "__main__":
    main()

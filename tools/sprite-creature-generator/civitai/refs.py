#!/usr/bin/env python3
"""Find, compare and pick a concept-art reference for each creature (free: no Buzz).

The image-to-image start (`civitai_creature.py prep` -> jobs.json "init") decides most of how a
creature looks, so every species gets its reference picked on purpose before any paid run.

    python refs.py brief abra                      # the species' row: name, basis, description, colour
    python refs.py search "loth wolf"              # Wookieepedia page titles for a query
    python refs.py images "Loth-wolf"              # every image on that page, with size and alpha
    python refs.py sheet abra <url|title> ...      # download candidates, prep each, one review sheet
    python refs.py pick abra <url> [--flip] [--width 52] [--denoise 0.5] [--desc ...] [--colour ...]
                                                   # prep the pick to refs/abra_prep.png, write refs/picks/abra.json
    python refs.py sheet abra "<url>#crop=0.4,0.2,0.8,0.9"   # cut one creature out of a scene
    python refs.py pick abra none --desc ... --colour ...   # no usable art: text-only job (still written)
    python refs.py status                          # which species have a pick

`sheet` writes refs/candidates/<species>/sheet.png: per candidate the source image (on grey, so
transparency shows), its prep at the model's 96 px (what the model will start from) and 3x of that.
Candidates are numbered in the order given. Titles expand to that page's images (try "<Title>/Gallery" too: big pages keep most images there).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
JOBS_CSV = HERE.parent / "research" / "sw-creature-jobs.csv"
JOBS_FILE = HERE / "jobs.json"
CAND = HERE / "refs" / "candidates"
PICKS = HERE / "refs" / "picks"  # one file per species (agents work in parallel); merged over jobs.json
API = "https://starwars.fandom.com/api.php"
UA = {"User-Agent": "pokeemerald-sw sprite reference picker (fan project)"}
SKIP = re.compile(r"(logo|icon|symbol|map|card-?back|signature|\.svg|\.gif|\.ogg|\.webm|_?flag)", re.I)


def row(species: str) -> dict:
    with JOBS_CSV.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["species_folder"] == species:
                return r
    sys.exit(f"{species}: not in {JOBS_CSV.name}")


def wiki(**params) -> dict:
    params.update(format="json", formatversion=2)
    r = requests.get(API, params=params, headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()


def search(q: str, n: int = 10) -> list[str]:
    return [h["title"] for h in wiki(action="query", list="search", srsearch=q, srlimit=n)["query"]["search"]]


def page_images(title: str) -> list[dict]:
    q = wiki(action="query", titles=title, prop="images|pageimages", imlimit=100, pithumbsize=1000,
             redirects=1)["query"]
    pg = q["pages"][0]
    files = [i["title"] for i in pg.get("images", []) if not SKIP.search(i["title"])]
    lead = pg.get("thumbnail", {}).get("source")
    out = []
    for k in range(0, len(files), 40):
        info = wiki(action="query", titles="|".join(files[k:k + 40]), prop="imageinfo",
                    iiprop="url|size|mime", iiurlwidth=1000)["query"]["pages"]
        for p in info:
            ii = (p.get("imageinfo") or [{}])[0]
            if ii.get("mime") in ("image/png", "image/jpeg", "image/webp") and max(ii.get("width") or 0, ii.get("height") or 0) >= 250:
                out.append({"file": p["title"], "url": ii.get("thumburl") or ii["url"],
                            "w": ii.get("width"), "h": ii.get("height"), "mime": ii["mime"]})
    if lead:
        out.sort(key=lambda d: d["url"].split("/revision")[0] not in lead)
    return out


def fetch(url: str) -> Image.Image:
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGBA")


def has_alpha(im: Image.Image) -> bool:
    a = np.array(im)[..., 3]
    return (a < 250).mean() > 0.05


def local_copy(species: str, src: str) -> str:
    """URLs may end in #crop=x0,y0,x1,y1 (fractions of the image) to cut one creature out of a
    scene; the crop is saved under refs/candidates/<species>/ and that file is used instead."""
    if "#crop=" not in src:
        return src
    url, box = src.split("#crop=")
    im = fetch(url) if url.startswith("http") else Image.open(url).convert("RGBA")
    x0, y0, x1, y1 = (float(v) for v in box.split(","))
    im = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
    d = CAND / species
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"crop_{abs(hash(src)) % 10**8}.png"
    im.save(out)
    return str(out)


def prep(species: str, src: str, out: Path, flip=False, width=60) -> Path:
    src = local_copy(species, src)
    cmd = [sys.executable, str(HERE / "civitai_creature.py"), "prep", species, src, "--out", str(out),
           "--width", str(width)] + (["--flip"] if flip else [])
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return out


def cmd_brief(a):
    r = row(a.species)
    keys = ("species_folder", "emerald_name", "sw_name", "sw_kind", "sw_basis", "planet", "description",
            "datapad_text", "type1", "type2", "body_color", "egg_groups", "height_m", "vanilla_size_class")
    for k in keys:
        print(f"{k:18} {r.get(k)}")
    j = {**json.loads(JOBS_FILE.read_text()).get(a.species, {})}
    pf = PICKS / f"{a.species}.json"
    if pf.exists():
        j.update(json.loads(pf.read_text()))
    if j:
        print(f"{'jobs.json':18} {json.dumps(j)}")


def cmd_search(a):
    for t in search(a.query, a.n):
        print(t)


def cmd_images(a):
    for i in page_images(a.title):
        print(f"{i['w']}x{i['h']:<6} {i['mime'][6:]:5} {i['file']}\n    {i['url']}")


def cmd_sheet(a):
    urls = []
    for s in a.sources:
        if s.startswith(("http://", "https://")) or Path(s.split("#")[0]).exists():
            urls.append(s)
        else:
            urls += [i["url"] for i in page_images(s)][: a.per_page]
    d = CAND / a.species
    d.mkdir(parents=True, exist_ok=True)
    tiles, listing = [], []
    for n, u in enumerate(urls[: a.max], 1):
        try:
            lu = local_copy(a.species, u)
            im = fetch(lu) if lu.startswith("http") else Image.open(lu).convert("RGBA")
            alpha = has_alpha(im)
            p = prep(a.species, u, d / f"c{n}_prep.png", a.flip, a.width)
        except Exception as e:  # noqa: BLE001
            listing.append(f"c{n}: FAILED {e!s:.80}  {u}")
            continue
        src = Image.new("RGBA", im.size, (150, 150, 150, 255))
        src.alpha_composite(im)
        src.thumbnail((256, 256))
        pr = Image.open(p).convert("RGB").resize((96, 96), Image.NEAREST)
        t = Image.new("RGB", (256 + 8 + 288, 288 + 20), "white")
        t.paste(src.convert("RGB"), (0, 20))
        t.paste(pr.resize((288, 288), Image.NEAREST), (264, 20))
        ImageDraw.Draw(t).text((4, 4), f"c{n}  {im.width}x{im.height}  {'ALPHA' if alpha else 'no alpha'}", fill="black")
        tiles.append(t)
        listing.append(f"c{n}: {im.width}x{im.height} {'ALPHA' if alpha else 'no-alpha'}  {u}")
    if not tiles:
        sys.exit("no candidates")
    cols = 2
    rows_ = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tiles[0].width, rows_ * tiles[0].height), (220, 220, 220))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * t.width, (i // cols) * t.height))
    sheet.save(d / "sheet.png")
    (d / "candidates.txt").write_text("\n".join(listing) + "\n")
    print("\n".join(listing))
    print(f"sheet -> {d / 'sheet.png'}")


def cmd_pick(a):
    pf = PICKS / f"{a.species}.json"
    j = json.loads(pf.read_text()) if pf.exists() else {}
    if a.source != "none":
        out = HERE / "refs" / f"{a.species}_prep.png"
        prep(a.species, a.source, out, a.flip, a.width)
        j.update(init=f"refs/{a.species}_prep.png", init_source=a.source, flip=False,
                 denoise=a.denoise)
    else:
        for k in ("init", "init_source", "denoise"):
            j.pop(k, None)
    for k in ("subject", "desc", "colour", "negative", "frame2"):
        v = getattr(a, k)
        if v:
            j[k] = v
    if a.note:
        j["ref_note"] = a.note
    PICKS.mkdir(parents=True, exist_ok=True)
    pf.write_text(json.dumps(j, indent=2, ensure_ascii=False) + "\n")
    print(f"{a.species}: {json.dumps(j)}")


def cmd_status(a):
    with JOBS_CSV.open(newline="") as f:
        sp = [r["species_folder"] for r in csv.DictReader(f)]
    done = [s for s in sp if (PICKS / f"{s}.json").exists()]
    print(f"{len(done)}/{len(sp)} picked")
    if a.missing:
        print(" ".join(s for s in sp if s not in done))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("brief"); p.add_argument("species"); p.set_defaults(fn=cmd_brief)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("-n", type=int, default=10); p.set_defaults(fn=cmd_search)
    p = sub.add_parser("images"); p.add_argument("title"); p.set_defaults(fn=cmd_images)
    p = sub.add_parser("sheet"); p.add_argument("species"); p.add_argument("sources", nargs="+")
    p.add_argument("--flip", action="store_true"); p.add_argument("--width", type=int, default=60)
    p.add_argument("--per-page", type=int, default=6); p.add_argument("--max", type=int, default=8)
    p.set_defaults(fn=cmd_sheet)
    p = sub.add_parser("pick"); p.add_argument("species"); p.add_argument("source", help="image URL/file, or none")
    p.add_argument("--flip", action="store_true", help="mirror so the creature faces left")
    p.add_argument("--width", type=int, default=60, help="prep width in native px (small 40-46, medium 48-54, large 56-62)")
    p.add_argument("--denoise", type=float, default=0.5)
    for k in ("subject", "desc", "colour", "negative", "frame2", "note"):
        p.add_argument(f"--{k}")
    p.set_defaults(fn=cmd_pick)
    p = sub.add_parser("status"); p.add_argument("--missing", action="store_true"); p.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

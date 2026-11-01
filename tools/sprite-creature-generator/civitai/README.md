# sprite-creature-generator / civitai

Creature battle sprites (front + back, one shared palette) made with Civitai's **hosted** generator,
so no rented GPU is needed. A mirror of [`../../sprite-trainer-generator/civitai/`](../../sprite-trainer-generator/civitai/),
set up for the creature LoRA [Pokemon Sprite PixelArt 768](https://civitai.com/models/161280/pokemon-sprite-pixelart-768)
(model 161280, SD 1.5, version **v2.1-beta** `273148` by default) on DreamShaper 8, paid for in Buzz.

**Status:** first creature shipped 2026-11-01: MASSIFF (`poochyena`), round 2 pick A (denoise 0.40), approved by
the owner. Front, back and `normal.pal` are in the wiki at `wiki/art/graphics/pokemon/poochyena/` and marked
ART_READY; not copied into `game/` yet. Frame 2 (`anim_front.png`) and `shiny.pal` are still to make.

## Setup

Same as the trainer tool: `CIVITAI_API_TOKEN` in the environment, or a git-ignored `.env` here with
`CIVITAI_API_TOKEN=...`. Never commit it. `pip install -r requirements.txt` (requests, Pillow, numpy).

## Use

```bash
cd tools/sprite-creature-generator/civitai
python civitai_creature.py models                      # LoRA versions (no key needed)
python civitai_creature.py prep poochyena <movie still URL or file> --flip   # -> refs/poochyena_prep.png (free)
python civitai_creature.py run poochyena --whatif      # price front + back, spend nothing (3 + 3 Buzz)
python civitai_creature.py run poochyena               # front, then back from the mirrored front, then finish
python civitai_creature.py gen poochyena --view back --init runs/poochyena/raw/<front>.png --flip --denoise 0.65
python civitai_creature.py finish runs/poochyena/raw/<front>.png runs/poochyena/raw/<back>.png --out runs/poochyena/finished/pick1
```

`<species>` is the folder in `game/graphics/pokemon/`. The brief (Star Wars name, first sentence of the
description, types, body colour) comes from [`../research/sw-creature-jobs.csv`](../research/sw-creature-jobs.csv);
[`jobs.json`](jobs.json) overrides it per species:

```json
"poochyena": {
  "subject": "massiff",
  "desc": "spiky reptile hound on four legs, long crocodile snout ...",
  "types": [],
  "colour": "grey and brown",
  "negative": "humanoid, standing upright, arms, fur",
  "init": "refs/poochyena_prep.png",
  "init_source": "https://static.wikia.nocookie.net/starwars/images/b/ba/Massiff-Outlaws.png/...",
  "flip": false,
  "denoise": 0.45
}
```

- **The recommended way:** find a movie still or concept art of the real creature (Wookieepedia),
  run `prep` on it, and point `init` at the result. `prep` cuts it out, faces it left, scales it to
  ~60 px, cuts it to 12 colours with a 1 px dark outline on the model's own 96 px / 8x grid. Image to
  image at denoise 0.4-0.55 from that keeps the real creature's shape and colours, and the LoRA only
  redraws it as a sprite. Text-only and raw-photo starts gave "rainbow Pokemon" colours.
- `init` (URL or local file) is the start image for the front: image to image. `flip`
  mirrors it, since vanilla fronts face left and most concept art faces right. `denoise` 0..1: how far
  the model may move away from it.
- `control` (URL or file) is the same through ControlNet (`--control-type canny`, `--control-weight 0.7`).
- `types: []` turns the LoRA's type tags off. `darktype` alone turned the Massiff into a dark-type humanoid.

## What it does

| Step | Detail |
|---|---|
| `gen` | Prompt: `gen3`, `backside` for backs, the LoRA's type tags, the subject at weight 1.2, the description, "pokemon, single creature, full body, white background". Text-only jobs use the `textToImage` step; jobs with an input image use the `imageGen` step (`engine: comfy`, `operation: createVariant`, `image`, `denoiseStrength`). 768x768 jpeg, 25 steps, CFG 7, Euler a, clip skip 2, LoRA 0.9. Raw images + a `.json` of every setting go to `runs/<species>/raw/`. |
| `run` | The front first; then each back is made **from its own front, mirrored**, with the `backside` tag (denoise 0.65). `--back-text-only` makes it from the prompt alone. Same seed for both. |
| `finish` | Same reader as the trainer tool: 8 px grid block vote to the native 96x96, flood-fill the white off, keep the main body (drops stray specks), k-means to 15 colours in CIELAB, fit 64x64 (1:1, trim a thin edge, or drop near-duplicate lines), bottom-centre. Then the creature palette rules from [`../README.md`](../README.md#palette-required-palettesmd): front `enforce --bpp 4 --colours 15 --write-pal normal.pal` (no theme), back `enforce --pal normal.pal` so both share one bank, then `check --pal normal.pal` on both. Writes `front.png`, `back.png`, `normal.pal`, native and 4x previews, and `battle_mockup_3x.png` (a vanilla tall-grass battle backdrop with the front on the far pad and the back on the near one). |

## Findings from the first test (Massiff, 2026-11-01, 15 Buzz)

- The LoRA does not know "massiff"; the description carries the shape. With `darktype` and a short
  description it drew a red-and-black humanoid. A longer body description and `types: []` gave a
  spiky four-legged lizard.
- **The `textToImage` step ignores `sourceImage`.** It accepts and stores the image, but a back sent
  with one came back byte-identical to the same prompt and seed without it (a cache hit, 0 Buzz).
  Image to image works through `imageGen` (comfy, createVariant): the back made from the mirrored
  front kept the body, spines and colours.
- A text-only back (same prompt + `backside`) came out as a different, red creature. Hence `run`
  makes backs from the front.
- At denoise 0.65 the "back" is still mostly a mirrored side view; try 0.75-0.8 for a real over-the-
  shoulder view. The `backside` images the LoRA draws are cropped at the bottom like gen 4/5 backs.
- The front came out 92 px wide at native size, so it was shrunk to 64x46 by dropping lines.
  Vanilla fronts are a median 48x48; adding "small" or "compact" to the prompt should help.

## Round 2 (2026-11-01, 16 Buzz): image to image from a prepped reference

Owner feedback on round 1: "a weird rainbow Pokemon with high contrast colours", not the movie
creature. Round 2 started from `prep` of the Wookieepedia Massiff render instead, CFG 5:

| denoise | result |
|---|---|
| 0.40 | Keeps the movie shape and the grey snout / brown hide; the LoRA adds sprite shading and outlines. Closest to the film |
| 0.55 | More "game" detail (open red jaws, gold back plates), still clearly the same animal |
| 0.70-0.75 (back, from the mirrored front) | Same colours and body; the pose turns a little but is still mostly a mirrored side view |

All fronts read back 1:1 at 60x43 (the vanilla median is 48x48), 15 colours, and pass `check`.
Defaults now: denoise 0.45 and CFG 5 when there is an input image, back denoise 0.7.

## Not done yet

- A true from-behind back: neither text nor image to image from the front gives one yet. Options:
  a back reference image through `prep` (any rear-ish still), or ControlNet from a hand-made back
  silhouette. Vanilla backs are also larger than the front (median 1.22x area) and cut off by the
  text box; ours are the front's size.

Frame 2 (`anim_front.png`: image to image from the picked front), `shiny.pal`, and the placement data
(`y_offset`, elevation) in the README's table rows 2, 5 and 6-8.

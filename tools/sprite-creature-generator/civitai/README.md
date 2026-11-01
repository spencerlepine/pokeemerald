# sprite-creature-generator / civitai

Creature battle sprites (front + back, one shared palette) made with Civitai's **hosted** generator,
so no rented GPU is needed. A mirror of [`../../sprite-trainer-generator/civitai/`](../../sprite-trainer-generator/civitai/),
set up for the creature LoRA [Pokemon Sprite PixelArt 768](https://civitai.com/models/161280/pokemon-sprite-pixelart-768)
(model 161280, SD 1.5, version **v2.1-beta** `273148` by default) on DreamShaper 8, paid for in Buzz.

**Status:** first test done 2026-11-01 (Massiff, in the `poochyena` slot). Not approved yet;
nothing is installed into `game/`.

## Setup

Same as the trainer tool: `CIVITAI_API_TOKEN` in the environment, or a git-ignored `.env` here with
`CIVITAI_API_TOKEN=...`. Never commit it. `pip install -r requirements.txt` (requests, Pillow, numpy).

## Use

```bash
cd tools/sprite-creature-generator/civitai
python civitai_creature.py models                      # LoRA versions (no key needed)
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
  "init": "https://static.wikia.nocookie.net/starwars/images/b/ba/Massiff-Outlaws.png/...",
  "flip": true,
  "denoise": 0.7
}
```

- `init` (URL or local file) is a concept/reference image for the front: image to image. `flip`
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

## Not done yet

Frame 2 (`anim_front.png`: image to image from the picked front), `shiny.pal`, and the placement data
(`y_offset`, elevation) in the README's table rows 2, 5 and 6-8.

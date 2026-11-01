# sprite-trainer-generator / civitai

Trainer front pics made with Civitai's **hosted** generator, so no rented GPU is needed. It uses the
trainer LoRA [Pokémon Trainer Sprite PixelArt](https://civitai.com/models/159333/pokemon-trainer-sprite-pixelart)
(model 159333, SDXL version by default) on the SDXL 1.0 base checkpoint, paid for in Buzz.

**Status:** working end to end (first run 2026-11-01: 4 Vader candidates for 10 blue Buzz, all passed
`palette-enforcer check`). Runs are kept in `runs/<trainer>/`.

## Setup

1. Make a key: civitai.com, **Account settings, API Keys, Add API key**.
2. Give it to the script one of two ways. Never commit it.
   - an environment variable `CIVITAI_API_TOKEN` (the cloud environment's settings, or your shell), or
   - a file `tools/sprite-trainer-generator/civitai/.env` with the line `CIVITAI_API_TOKEN=...`
     (this folder's `.gitignore` excludes it).
3. `pip install -r requirements.txt` (requests, Pillow, numpy).

## Use

```bash
cd tools/sprite-trainer-generator/civitai
python civitai_trainer.py models                              # list LoRA versions + trigger words (no key needed)
python civitai_trainer.py gen magma_leader_maxie --whatif     # price the job, spend nothing
python civitai_trainer.py run magma_leader_maxie -n 2         # generate 2 and finish them
python civitai_trainer.py finish runs/magma_leader_maxie/raw/<file>.png --theme imperial-order
```

`<trainer>` is the front pic's file stem in `game/graphics/trainers/front_pics/`. The brief is that row's
`sw_subject` in `wiki/database/pending_art.csv`; [`jobs.json`](jobs.json) adds per-trainer look notes,
the faction theme and an optional style tag (`gen1` or `gen2`, off by default). Darth Vader is `magma_leader_maxie`.

## What it does

| Step | Detail |
|---|---|
| `gen` | Builds the prompt (LoRA trigger words, style tag, subject, look notes, "solid white background", theme colours), posts a `textToImage` job at 768x768 to the orchestrator, polls, downloads each image to `runs/<trainer>/raw/` with a `.json` of every setting (LoRA version and SHA256, checkpoint, prompt, seed, cost). |
| `finish` | 768 -> 96 by 8x8 block vote (most common colour per block, so edges stay crisp). Flood-fills the background off from the border. If the figure fits 64x64 it is bottom-centred as is; otherwise it is cropped from the 768 original and re-voted down to fit 64. Then `palette-enforcer enforce --bpp 4 --theme <faction> --free 6 --write-pal`, then `check`. Output in `runs/<trainer>/finished/`: indexed PNG, `.pal`, a 4x preview. |

Nothing is installed into `../../../game` by this script; the owner picks first.

## Cost

Jobs go through the v2 workflows API (`/v2/consumer/workflows`) with `currencies: ["blue"]`, so earned
(blue) Buzz pays. The v1 `/v1/consumer/jobs` endpoint only spends yellow Buzz and answered
`403 Insufficient Buzz` on a blue-only account. Measured whatif prices for SDXL at 768x768, 25 steps:

| -n | jpeg | png |
|---|---|---|
| 1 | 3 | 5 |
| 2 | 5 | 9 |
| 4 | 10 | 18 |

jpeg is the default; the 8x block vote absorbs its noise. `--whatif` shows the price before spending.

## Findings from the first run

- The checkpoint AIR `101055@128078` and LoRA `159333@443092` are accepted as is.
- The LoRA has no trigger words. The `gen1`/`gen2` tags force the old Game Boy look (the first run used
  `gen2`: maroon, skin-toned, Crystal-like). Leave the tag off for the full-colour look of the model previews;
  `--style gen2` brings it back.
- `--fit crop` keeps the native 8x pixel grid and reads crisper; `--fit scale` fills the 64 cell but
  re-votes at 7x or 9x and picks up stray pixels. Crop clips a figure wider than 64 (a lightsaber).

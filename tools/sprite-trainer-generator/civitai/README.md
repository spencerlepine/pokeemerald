# sprite-trainer-generator / civitai

Trainer front pics made with Civitai's **hosted** generator, so no rented GPU is needed. It uses the
trainer LoRA [Pokémon Trainer Sprite PixelArt](https://civitai.com/models/159333/pokemon-trainer-sprite-pixelart)
(model 159333, SDXL version by default) on the SDXL 1.0 base checkpoint, paid for in Buzz.

**Status:** script written and the finisher tested offline. Nothing has been generated yet: the cloud
environment the agents run in has to allow `civitai.com` and `orchestration.civitai.com`, and hold the key.

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
the faction theme and the style tag (`gen1` or `gen2`). Darth Vader is `magma_leader_maxie`.

## What it does

| Step | Detail |
|---|---|
| `gen` | Builds the prompt (LoRA trigger words, style tag, subject, look notes, "solid white background", theme colours), posts a `textToImage` job at 768x768 to the orchestrator, polls, downloads each image to `runs/<trainer>/raw/` with a `.json` of every setting (LoRA version and SHA256, checkpoint, prompt, seed, cost). |
| `finish` | 768 -> 96 by 8x8 block vote (most common colour per block, so edges stay crisp). Flood-fills the background off from the border. If the figure fits 64x64 it is bottom-centred as is; otherwise it is cropped from the 768 original and re-voted down to fit 64. Then `palette-enforcer enforce --bpp 4 --theme <faction> --free 6 --write-pal`, then `check`. Output in `runs/<trainer>/finished/`: indexed PNG, `.pal`, a 4x preview. |

Nothing is installed into `../../../game` by this script; the owner picks first.

## Cost

About 4-6 Buzz per SDXL image plus a 10 Buzz surcharge per request for non-members, so batch
candidates with `-n` in one request. `--whatif` shows the price before spending.

## Open questions (answer on the first real run)

- The checkpoint AIRs in `CHECKPOINTS` and the `/v1/consumer/jobs` request shape come from Civitai's
  Python SDK and could not be checked from the agent container. If a request is refused, the script
  prints the response body.
- Which works better at 64x64: the 96 crop or the rescale from 768 (`--fit crop|scale`).
- `gen1` vs `gen2` against the creature LoRA's `gen3` look.

# sprite-trainer-generator / civitai

Trainer front pics made with Civitai's **hosted** generator, so no rented GPU is needed. It uses the
trainer LoRA [Pokémon Trainer Sprite PixelArt](https://civitai.com/models/159333/pokemon-trainer-sprite-pixelart)
(model 159333, SDXL version by default) on the SDXL 1.0 base checkpoint, paid for in Buzz.

**Status:** DONE. Approved by the owner on 2026-11-01. First shipped sprite: Darth Vader
(`magma_leader_maxie`), stored in the wiki at `wiki/art/graphics/trainers/front_pics/` and marked
ART_READY; not copied into `game/` yet. Runs are kept in `runs/<trainer>/`.

## Batch (all trainers)

`batch.py` ran every pending trainer front pic on 2026-11-01 with no human review: 92 pics
(91 front pics + Prof. Korr's `birch_speech/birch.png`) are in `wiki/art/` as ART_READY, about 375
green Buzz in total. Each trainer gets one 1-image take; a take that fails the automatic checks
(palette `check`, grid found, size, colour count, no duplicate/turnaround figures, no leftover
background box, pair pics show two people) gets one retry. Each pick is committed on its own.

```bash
python batch.py --list                         # still pending
python batch.py --budget 300 -j 4              # run all pending, stop before 300 Buzz
python batch.py --redo --budget 20 may sailor  # regenerate named trainers even if ART_READY
python batch.py --refinish                     # re-run the free finisher on every auto-picked raw
```

Brendan, May, their R/S pics, Wally and Leia (steven) share their palette with the back pic: the
new `.pal` is in `wiki/art/graphics/trainers/palettes/`, and the back pics must adopt it.
Nothing is in `game/` yet.

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
python civitai_trainer.py finish runs/magma_leader_maxie/raw/<file>.png --theme imperial-order  # --fit auto|trim|shrink
```

`<trainer>` is the front pic's file stem in `game/graphics/trainers/front_pics/`. The brief is that row's
`sw_subject` in `wiki/database/pending_art.csv`; [`jobs.json`](jobs.json) adds per-trainer look notes,
the faction theme and an optional style tag (`gen1` or `gen2`, off by default). Darth Vader is `magma_leader_maxie`.

## What it does

| Step | Detail |
|---|---|
| `gen` | Builds the prompt (LoRA trigger words, style tag, subject, look notes, "solid white background", theme colours), posts a `textToImage` job at 768x768 to the orchestrator, polls, downloads each image to `runs/<trainer>/raw/` with a `.json` of every setting (LoRA version and SHA256, checkpoint, prompt, seed, cost). |
| `finish` | Reads the art back at its own resolution instead of re-drawing it. Finds the pixel grid (8 px, so 96x96 native), takes each cell's majority colour from its centre (skipping JPEG ringing at the cell edges), flood-fills the background off, then k-means to 15 colours in CIELAB with farthest-first seeds so small distinct areas (skin, eyes, saber, chest lights) keep a colour. Fit to 64x64: 1:1 if it fits; shave up to 8 thin edge columns (a saber tip); otherwise delete the rows and columns that most nearly repeat a neighbour, which keeps 1 px outlines and faces. Then `palette-enforcer enforce --bpp 4 --theme <faction>` (colours pulled onto the theme only within Delta E 12) and `check`. Output in `runs/<trainer>/finished/`: indexed PNG, `.pal`, the native-resolution figure, a 4x preview. |

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

## Writing a job (reusable prompt)

The prompt is a template (`PROMPT` in the script); a new character only needs a `jobs.json` entry:

```json
"magma_leader_maxie": {
  "subject": "Darth Vader",
  "desc": "tall imposing figure, black full-face helmet, ... red lightsaber",
  "negative": "visible face, skin, hair, hat",
  "theme": "imperial-order"
}
```

- `subject` leads the prompt at weight 1.3, so the character wins over the LoRA's trainer look.
- `desc` is the silhouette: body shape, height, headgear, clothes, held item. Write it for any body
  (a Wookiee: "huge furry humanoid, long brown fur all over, bandolier across chest, bowcaster").
- `negative` adds per-character exclusions (a masked character: "visible face, skin, hair").
- optional `pose` (default "standing, facing left, three-quarter view") and `style` (`gen1`/`gen2`).
- The template never says "pokemon trainer", and the shared negatives exclude Poke Balls, caps and
  "generic pokemon trainer"; with those in, every subject came out as a kid in a cap.
- LoRA strength defaults to 0.75 for the same reason.

## Findings from the first run

- The checkpoint AIR `101055@128078` and LoRA `159333@443092` are accepted as is.
- The LoRA has no trigger words. The `gen1`/`gen2` tags force the old Game Boy look (the first run used
  `gen2`: maroon, skin-toned, Crystal-like). Leave the tag off for the full-colour look of the model previews;
  `--style gen2` brings it back.
- Round 3 (prompt template above, 1 image, 3 Buzz) gave a recognisable Vader: helmet, mask, cape, saber.
- Downscaling: the first finisher block-voted the 768 down at a grid that did not always match the
  art (7x, 9x), quantised to 48 colours, then let the theme pull merge shades, so sprites ended with
  7-10 colours and lost faces and small details. Vanilla front pics use 13-15 colours with the figure
  about 41x58. The rewrite above keeps the art's own pixels (13-14 colours, Vader is 1:1).

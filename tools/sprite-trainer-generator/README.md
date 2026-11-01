# sprite-trainer-generator

**Status:** PENDING. Approach chosen; the tool is not built yet. The build waits on a rented GPU.
The earlier repaint/sculpt tool in this folder was scrapped (it did not work) and deleted; it is
in git history if anything needs recovering.

Draws **trainer battle front pics**: the full-body portrait of every opposing trainer, the player
and partners, plus the professor's intro portrait.

## What this tool makes

"SD" means a Stable Diffusion model run on a rented GPU; "Python" means a deterministic script
that runs anywhere.

| # | File | Size and format | Made by | Where it shows |
|---|---|---|---|---|
| 1 | `game/graphics/trainers/front_pics/<trainer>.png` (93 files) | 64x64, 1 frame, 4bpp; 15 colours + transparent | **SD** (trainer LoRA, front view) + Python finisher | Trainer battle intro, trainer card, Hall of Fame, Grand Arena (Battle Frontier) |
| 2 | Its palette | Taken from the PNG for most trainers. Brendan, May, their old R/S pics and Wally use a file in `game/graphics/trainers/palettes/` instead, which their back pic shares | **Python** | |
| 3 | `game/graphics/birch_speech/birch.png` | 64x64 still, palette from the PNG | **SD** + Python finisher | New-game intro (Prof. Korr) |
| 4 | Placement data: `gTrainerFrontPicCoords` in `game/src/data/trainer_graphics/front_pic_tables.h` | `size`, `y_offset` | **Python** (measured from 1) | Keeps the trainer on the ground line |

Notes on the art:

- Full body, standing, three-quarter facing the player's side (left), as in vanilla.
- Six pics show **two people** in one 64x64 cell (`twins`, `sis_and_bro`, `sr_and_jr`,
  `young_couple`, `old_couple`, `leader_tate_and_liza`); prompt and judge these as pairs.
- `birch_speech/shadow.png` and `unused_beauty.png` are kept as they are.

## Not made here

- Back pics (the player's and partners' over-the-shoulder capture-pod throw): a different view, size and animation.
- Overworld walking sprites of the same characters.

## Wiki rows

`pending_art.csv` kind `trainers`, subkind `front_pics` (93 rows), and kind `birch_speech`
`birch.png`. Each row's `sw_subject` is the brief (for example `aqua_admin_m` -> its Star Wars
trainer). Categories: B1, B4.

## Size: 96x96 model output vs the 64x64 game

The LoRA's native sprite is 96x96; Emerald's trainer pics are 64x64 and fill most of the cell.
Unlike creatures, cropping a 96 canvas will not work if the model draws trainers edge to edge, so
the finisher has to rescale (96 -> 64 is 1.5x, which breaks the pixel grid) and then clean up.
**Test first**: generate a few at 768, try (a) 8x -> 96 then crop if the figure fits 64, and
(b) 12x -> 64 directly; compare on one sheet.

## Model gaps to test

- **No documented `gen3` tag.** Try `gen2` and no tag; compare against the creature LoRA's `gen3`
  creatures on the same sheet so trainers and creatures read as one game.
- Starting prompt to try:

```
gen2, pokemon trainer sprite,
male trainer, standing, front view,
simple background
```

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind`; skip `KEEP*` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` the Emerald original, `suggested_path` the new name) and generates rows 1-4 above.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

---

# Research: trainer sprite pipeline (one-pager)

**Model:** Pokémon Trainer Sprite PixelArt by titansteng
([Civitai model 159333](https://civitai.com/models/159333/pokemon-trainer-sprite-pixelart)).
It is the trainer companion to the creature LoRA (Pokémon Sprite PixelArt 768) by the same
creator. Not yet downloaded or tested.

## 1. Overview

Generate original Star Wars trainer sprites that match the look of Generation 3 (Ruby, Sapphire,
Emerald) with a Stable Diffusion LoRA, run offline on a rented GPU. Generated sprites become
ordinary game assets; nothing is generated while the game runs. Generated images are candidates,
not approved assets: the owner picks.

## 2. Model information

| | |
|---|---|
| Model | Pokémon Trainer Sprite PixelArt |
| Creator | titansteng |
| Platform | Civitai (model 159333) |
| Architecture | Stable Diffusion 1.5 LoRA. An SDXL version also exists |
| File, size, SHA256 | Not recorded yet: write them here when the file is downloaded (Civitai was not reachable from the agent container) |
| Native sprite size | 96x96 (generate at 768x768, downsample 8x) |

**Compatibility:** load the SD 1.5 version only into an SD 1.5 pipeline, never SDXL. The SDXL
version is a different file; switching architecture does not add Gen 3 or back-view support.

### What the model supports (from its description)

| Feature | Support |
|---|---|
| Front-facing trainers | Yes |
| Generation 1 style (`gen1`) | Yes |
| Generation 2 style (`gen2`) | Yes |
| Generation 3 style | **Not documented** |
| Back-facing trainers | **Not documented**: no `backside` tag, unlike the creature LoRA |
| 96x96 native sprites | Yes |

The creature LoRA documents `gen3`; this one stops at `gen2`. If the game's trainers and creatures
must look like one set, **test both LoRAs side by side before committing** to this one (same
prompt style, same finisher, one sheet).

## 3. Infrastructure

Same as the creature pipeline: a temporary rented GPU (RunPod first; an RTX 3090 or 4090 is
enough for SD 1.5), ComfyUI as the inference interface, terminated as soon as outputs are
downloaded and verified. AWS EC2 or a hosted API are alternatives only if the API can load this
exact Civitai LoRA with strength, seed and resolution control. Cache the checkpoint and LoRA on
persistent storage; never leave an idle GPU running.

```
START GPU -> LOAD SD 1.5 CHECKPOINT + LORA -> RUN JOB LIST -> DOWNLOAD OUTPUTS
          -> VERIFY OUTPUTS AND METADATA -> TERMINATE GPU
```

## 4. Jobs, batches and metadata

Drive generation from a job list, not hand-written prompts. Each job: trainer id and wiki row,
description (the row's `sw_subject`), style tag, view (front or back), positive and negative
prompt, seed, LoRA strength, output name. Load the model once, run jobs in one queue, save every
image separately, track failures and retry only those. Vary seeds for candidates; fix the seed
when iterating on one trainer.

Record for every output: model and LoRA file and SHA256, base checkpoint, prompts, seed, LoRA
strength, sampler settings, resolution, finisher settings, timestamp. Keep the 768x768 originals
so a sprite can be reprocessed without paying for another generation. Keep originals, processed
images, approved sprites, metadata and saved ComfyUI workflows in separate folders.

## 5. Output processing (Python finisher)

1. Downsample 768 -> 96 (8x, nearest; test that pixel edges stay crisp).
2. Fit into the game's 64x64 cell (see "Size" above).
3. Remove the background as its own step (a white background is not transparency).
4. Quantise to the game's palette rules (15 colours + transparent).
5. Export indexed PNG (and `.pal` where the game uses one).

Review every sheet for silhouette, proportions, palette, alignment, pixel quality, background
artifacts and framing before it is shown to the owner.

## 6. Future extensibility

Keep the checkpoint, LoRA, strength, prompt templates, resolution, sampler and finisher swappable,
so the creature LoRA, the SDXL trainer LoRA or a LoRA trained on Emerald's own trainer pics can be
tried without rewriting the tool. No custom training is planned until this model is evaluated.

## 7. Licensing

Check the LoRA's licence and commercial-use terms before shipping its output. A public model does
not grant rights to Pokémon or Star Wars characters, names or designs.

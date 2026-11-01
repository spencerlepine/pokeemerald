# sprite-trainer-back-generator

**Status:** PENDING. The tool is not built yet, but every back pic has an approved-style **mockup**
in [`mockups/`](mockups/) to work from. The earlier repaint tool in this folder was scrapped (it
did not work) and deleted; it is in git history if anything needs recovering.

Draws **trainer battle back pics**: the player and partners seen over the shoulder, throwing a
capture pod when a battle starts.

## What this tool makes

"SD" means a Stable Diffusion model run on a rented GPU; "Python" means a deterministic script
that runs anywhere.

| # | File | Size and format | Made by | Notes |
|---|---|---|---|---|
| 1 | `game/graphics/trainers/back_pics/<trainer>.png` (6 files) | 64x256 = 4 frames of 64x64, 4bpp | Frame 1: **SD** (trainer LoRA, back view) + Python finisher. Frames 2-4: **SD img2img** from frame 1, or hand edit | Waist-up, seen from behind and to the left, larger than the front pic. Frames: holding the pod, wind-up, throw, arm down |
| 2 | Palette | `game/graphics/trainers/palettes/<trainer>.pal` for Brendan, May, their R/S pics, Wally and Steven | **Python** | Brendan, May, the R/S pics and Wally share this file with their **front** pic, so the back is quantised to the existing palette rather than a new one |
| 3 | Animation timing: `game/src/data/trainer_graphics/back_pic_anims.h` | frame order and durations | Kept vanilla | Only change it if the new frames need different timing |
| 4 | Placement data: `gTrainerBackPicCoords` in `game/src/data/trainer_graphics/back_pic_tables.h` | `size`, `y_offset` | **Python** | |

Who these are (from the wiki): `brendan` -> KAEL (player, boy), `may` -> MIRA (player, girl),
`wally` -> LUKE SKYWALKER (catching tutorial), `steven` -> LEIA ORGANA (multi-battle partner),
`brendan_rs` / `may_rs` (old Ruby/Sapphire pics of Kael and Mira). The FireRed link leftovers `red` /
`leaf` were deleted from the game.

## Not made here

- Front pics of the same characters (full-body portraits), including the front-pic half of the shared palettes.
- Overworld walking sprites.

## Wiki rows

`pending_art.csv` kind `trainers`, subkind `back_pics`: 6 rows, all to draw. Each row's `sw_subject` is the
brief. Category: B2.

## Characters to do, and their mockups

Six back pics. Each has one concept mockup: a 768x768 image from the trainer LoRA (model 159333,
SDXL version) with a back-view prompt, plus a `.json` beside it with the prompt, seed and settings.
[`mockups/mockups_sheet.png`](mockups/mockups_sheet.png) shows all six.

| Back pic | Character | Mockup | Notes |
|---|---|---|---|
| `brendan.png` | KAEL (player, boy) | [`mockups/brendan.png`](mockups/brendan.png) | Over-the-shoulder three-quarter back, arm out: closest to the back-pic pose |
| `may.png` | MIRA (player, girl) | [`mockups/may.png`](mockups/may.png) | Clean back view; buns read as one bun |
| `brendan_rs.png` | KAEL (old Ruby/Sapphire pic, link battles) | [`mockups/brendan_rs.png`](mockups/brendan_rs.png) | Three-quarter, more side than back |
| `may_rs.png` | MIRA (old Ruby/Sapphire pic, link battles) | [`mockups/may_rs.png`](mockups/may_rs.png) | Back view, hand on head |
| `wally.png` | LUKE SKYWALKER (catching tutorial) | [`mockups/wally.png`](mockups/wally.png) | Three-quarter back, lightsaber |
| `steven.png` | LEIA ORGANA (multi-battle partner) | [`mockups/steven.png`](mockups/steven.png) | Straight back view, arms out |

What the mockups are and are not: they fix each character's **back design** (hair from behind,
clothes, colours) in the game's pixel style. They are not back pics: they are full-body and small,
while a back pic is a large waist-up figure seen over the shoulder, in 4 throw frames, on the
palette it shares with the front pic. Building that is the job of this tool (below).

Back views from this LoRA work best for known characters (Leia, Luke came out first try); the
generic player kids took a stronger prompt: `solo, single character, (back view:1.5),
(from behind:1.4), (back of head:1.3), back turned to the viewer, looking away`, negatives `face,
front view, facing viewer, eyes, side view, profile, multiple views, character sheet, turnaround,
two people`, LoRA strength 0.6.

## Model gaps to test

The model does **not** document a back-view tag (the creature LoRA has `backside`; this one does
not), and it has no notion of animation frames.

1. **Back view.** Answered: yes (see the mockups). The original plain prompt idea, kept for reference:

```
pokemon trainer sprite,
male trainer, standing, back view,
facing away from camera,
simple background
```

   If it fails, fall back in order: img2img from the approved front pic with a back-view prompt;
   an image-edit model ("turn around, view from behind"); hand-drawing frame 1.
2. **Waist-up framing.** Vanilla back pics are cropped at the waist and drawn bigger than the
   front. Prompt for upper body / over the shoulder, or crop and scale a full-body render.
3. **The throw frames (2-4).** Not something the model can do in one call. Try img2img from
   frame 1 with the same seed and a pose word (`arm raised`, `throwing`), then map onto frame 1's
   palette; hand-fix as needed.
4. **No documented `gen3` tag**, as for the front pics: compare on one sheet with the creature
   LoRA's output before committing.

## Size: 96x96 model output vs the 64x64 game

The LoRA's native sprite is 96x96; each back-pic frame is 64x64. Test (a) 8x -> 96 then crop to
the waist-up 64x64 and (b) 12x -> 64 directly, and compare.

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** 4 frames of 64x64, 4bpp. The palette is **locked**: it is the file in
  `game/graphics/trainers/palettes/` shared with the front pic.
- **Theme (layer 2):** inherited from the front pic (the player is `alliance-dawn`).
- **Post-processing:** `enforce raw.png back.png --bpp 4 --key auto --pal game/graphics/trainers/palettes/<name>.pal`
  for every frame, then `check back.png --pal ...`. Never write a new palette here: it would recolour the front.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind`; skip `KEEP*` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` the Emerald original, `suggested_path` the new name) and generates rows 1, 2 and 4 above.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

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
4. Palette step (`../palette-enforcer`, rules in `../PALETTES.md`): `enforce` to 4bpp, 15 colours + transparent, onto
   the faction theme or the locked shared palette; it writes the indexed PNG (and `.pal` where the game uses one).
5. `check` the result; a failure is not shown to the owner and not installed.

Review every sheet for silhouette, proportions, palette, alignment, pixel quality, background
artifacts and framing before it is shown to the owner.

## 6. Future extensibility

Keep the checkpoint, LoRA, strength, prompt templates, resolution, sampler and finisher swappable,
so the creature LoRA, the SDXL trainer LoRA or a LoRA trained on Emerald's own trainer pics can be
tried without rewriting the tool. No custom training is planned until this model is evaluated.

## 7. Licensing

Check the LoRA's licence and commercial-use terms before shipping its output. A public model does
not grant rights to Pokémon or Star Wars characters, names or designs.

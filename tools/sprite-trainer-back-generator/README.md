# sprite-trainer-back-generator

**Status:** DONE (2026-11-02). `back.py` works end to end on Civitai's hosted generator (no GPU). All six
back pics are owner-approved, stored in `wiki/art/graphics/trainers/back_pics/` (ART_READY) and installed in
`game/graphics/trainers/back_pics/` (game_status DONE). The R/S slots are copies of Kael and Mira.

Draws **trainer battle back pics**: the player and partners seen over the shoulder, throwing a
capture pod when a battle starts. Each is 4 frames of 64x64 (a 64x256 PNG, 4bpp) on the **front
pic's palette**, so the back matches the shipped front.

| Back pic | Character |
|---|---|
| `brendan` | KAEL (player, boy) |
| `may` | MIRA (player, girl) |
| `brendan_rs` / `may_rs` | Kael and Mira, old Ruby/Sapphire pics (link battles) |
| `wally` | LUKE SKYWALKER (catching tutorial) |
| `steven` | LEIA ORGANA (multi-battle partner) |

## How it works

1. **`prep` (free).** Start from the vanilla 4 throw frames, so pose, framing, size and frame order
   are already right. Recolour them onto the front pic's palette with the `map` in [`jobs.json`](jobs.json)
   (vanilla index -> front index). `regions` remap inside a box (a hat band -> hair), and `paint`
   draws shapes (Leia's buns, Mira's hood, Mira R/S's scarf). Boxes are written in frame 3's
   coordinates and moved to each frame by an automatic head match (`anchor` overrides it).
   The 4 frames go in a 2x2 sheet: 128x128 native, 8x = 1024x1024, on the LoRA's own 8 px grid.
2. **`gen` (paid).** Image to image from the prep: SDXL + trainer LoRA 159333 (the same as the
   fronts), one 1024 image holds all four frames so they stay one character. Denoise 0.5 keeps the
   pose; 0.65 starts turning the head to the front; 0.35 keeps the prep's flat colours.
3. **`finish` (free).** Reads the 8 px grid back to 128x128, cuts the white off (the fill enters only
   from the top and sides: the figure runs off the bottom), splits the frames, then
   `palette-enforcer enforce --pal <front palette>` and `check`. Writes `<trainer>.png` (64x256),
   `back_4x.png`, `throw.gif` (vanilla timing) and `battle_mockup_3x.png`.

```bash
cd tools/sprite-trainer-back-generator
python3 back.py prep may                               # refs/may_prep.png (free)
python3 back.py sheet --prep may                       # look at it before spending
python3 back.py gen may --whatif                       # price: 6 Buzz (png), 4 (jpeg)
python3 back.py run may --denoise 0.5 --seed 1101      # gen + finish -> runs/may/finished/<take>/
python3 back.py sheet --only -1459 --last 2            # compare takes
```

The palette is the shared `game/graphics/trainers/palettes/<trainer>.pal` (Kael, Mira, R/S, Luke);
Leia's `steven.pal` is still the vanilla colours, so her front PNG's own bank is used.

## Round log (2026-11-02, 312 green Buzz)

- Test, Kael, denoise 0.35 / 0.5 / 0.65: 0.5 is the default.
- Round 1, all six, 2 seeds: Kael, Luke, Leia close. The vanilla hat band came out as a headband
  (fixed in the prep); "throwing a small ball" drew Poke Balls (prompt changed).
- Round 2: Luke and Leia picked. Mira's painted hood stayed a flat disc at 0.55-0.65.
- Round 3: Mira at 0.75 (reads as a hooded cloak; 0.85 lost the pose), Kael and Mira R/S with the
  face and collar cleaned up in the prep.

- Owner review 1: Luke and Leia approved. Kael's tunic whitened after the fact (`post_remap` in
  jobs.json: grey-blue shades -> white, free). Mira's hood scrapped: round 4 (24 Buzz) keeps the R/S
  head, hair and pose with a brown cloak painted behind the arms (`"under"` paint ops). Mira's hood
  settings are kept as `may_v1` in jobs.json.
- The R/S slots (`brendan_rs`, `may_rs`) only show in link battles with real Ruby/Sapphire carts, so
  they reuse the main Kael and Mira pics (front, back and palette) instead of their own art.

- Owner review 2: Kael still showed bare forearms, Mira faced the camera. Round 5 (30 Buzz): Kael's
  prep turns arm skin into white sleeves (`near` keeps the hands skin, per-frame `abs` boxes keep
  the face); Mira's prep turns the face into hair, so the model draws the back of her head.

- Owner review 3: Kael's take kept; `post_shade` puts form back on the whitened tunic, `post_edit`
  hand-fixes the white blob on the raised arm (frame 2) and turns the skin-coloured neck patch brown
  in frames 1, 3, 4. Mira restarted (rounds 6-7, 42 Buzz): `base` starts her prep from Kael's
  finished throw instead of vanilla May, recoloured to her palette, with a painted back of the head
  and a hood-down collar, at denoise 0.65-0.7.

- Owner review 4: Kael's frame 2 arm redrawn by hand (`post_edit` clear + lines: one clean raised
  sleeve). Mira's painted head did not turn and her arms broke where the cloak box cut them. Round 8
  (24 Buzz): base is Kael's fixed throw with the whole tunic recoloured to her cloak and a small hair
  tuft at the nape, so head turn and arms come from Kael's approved frames.

- Owner review 5: Mira C picked, two white specks on her arms recoloured to the cloak. Kael's frame 2
  goes back to the earlier arm and only the white block between arm and head is cleared.

Shipped picks: brendan `20261102-151756_d50_s1101_v4`, may `20261102-153424_d55_s1101_v2`,
wally `20261102-145726_d50_s1101`, steven `20261102-145729_d50_s1101`.

## Installed (2026-11-02)

- `game/graphics/trainers/back_pics/<trainer>.png` for all six; `brendan_rs` / `may_rs` are byte copies of
  `brendan` / `may`. The R/S front pics and `palettes/brendan_rs.pal`, `may_rs.pal` are copies of the main
  Kael and Mira ones too (owner: no separate R/S art), in `game/` and `wiki/art/`.
- No code changed. `gTrainerBackPicPalette_*` reads each back pic's own PNG palette, and that palette is the
  front pic's (enforced with `--pal`), so front and back match. `back_pic_anims.h` and
  `gTrainerBackPicCoords` stay vanilla (same 4 frames, same 64x64 size).
- The PNGs convert with the game's own `gbagfx` (`make graphics/trainers/back_pics/<trainer>.4bpp`). The full
  ROM was not linked in the agent container (no ARM toolchain there).

## Wiki rows

`pending_art.csv` kind `trainers`, subkind `back_pics`: 6 rows, all ART_READY and game_status DONE
(listed in `wiki/mapping/art_ready.csv`). Each row's `sw_subject` is the brief.

The concept mockups in [`mockups/`](mockups/) (full body, from the trainer LoRA) came before the
fronts were shipped; the backs follow the shipped fronts instead.

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

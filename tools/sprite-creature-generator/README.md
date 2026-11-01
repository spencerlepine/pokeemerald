# sprite-creature-generator

**Status:** PENDING. Approach researched and decided; the tool is not built yet. The build waits
on a rented GPU.

Draws a companion's **battle sprites**: the front, the second animation frame, the back, and the
battle palette (normal and shiny) all three share. Everything this tool writes uses one palette,
so it is drawn and quantised together in one pass. Anything that does not use that palette is
not made here.

## What this tool makes, per species

Files land in `game/graphics/pokemon/<species>/`. "SD" means a Stable Diffusion model run on a
rented GPU; "Python" means a deterministic script that runs anywhere.

| # | File | Size and format | Made by | Notes |
|---|---|---|---|---|
| 1 | `front.png` | 64x64, 4bpp, 15 colours + transparent | **SD** (sprite LoRA, `gen3`) + Python finisher | The main sprite. Opponent side of a battle, Datapad, summary, trade, evolution, Hall of Fame all reuse it |
| 2 | `anim_front.png` | 64x128: frame 1 (top) = `front.png`, frame 2 (bottom) = a second pose | **SD** img2img from the picked front + Python finisher | Vanilla's frame 2 changes a median 72% of pixels (mouth open, limbs moved), so it is a real redraw, not a bob. 339 of 385 vanilla species have frame 1 identical to `front.png` |
| 3 | `back.png` | 64x64, 4bpp, a subset of the front palette | **SD** (`backside` tag) + Python finisher | Your side of a battle. Drawn larger than the front (median 1.22x area) |
| 4 | `normal.pal` | JASC, 16 entries | **Python** | Shared by 1-3; the finisher maps the back and frame 2 onto the front's colours |
| 5 | `shiny.pal` | JASC, 16 entries, same index order as `normal.pal` | **Python** (hue shift), optionally guided by an SD `shiny` render | Same pixels, different colours |
| 6 | Battle placement data | `src/data/pokemon_graphics/front_pic_coordinates.h`, `back_pic_coordinates.h`, `enemy_mon_elevation.h` | **Python** (measured from 1 and 3) | `y_offset` so the sprite sits on the ground; elevation for floating creatures |
| 7 | Front animation choice | `sMonFrontAnimIdsTable` and `sMonAnimationDelayTable` in `src/pokemon.c`, `sSpeciesToBackAnimSet` in `src/pokemon_animation.c`, frame timing in `src/data/pokemon_graphics/front_pic_anims.h` | **Python** (pick a preset by body type) | Code-driven motion presets, not art; picked so the motion suits the new creature |
| 8 | Datapad size comparison | `pokemonScale` / `pokemonOffset` in `src/data/pokemon/pokedex_entries.h` | **Python** (from the front's content box and the creature's height) | |

Special forms are the same files per form, so this tool covers them with a `form` field on the
job: Unown's 28 letters (`unown/<letter>/`, one shared `normal.pal`) and Castform's 4 weathers
(`castform/<form>/`, each with its own palettes). Deoxys has one battle form in Emerald.

## Not made here

These belong to a creature too, but they use a different palette, size or method, so each has
its own tool (see the per-creature checklist in [`../README.md`](../README.md#one-creature-every-sprite)):

- Party / PC box icon (`icon.png`, 32x64, one of 3 shared icon palettes), including Unown's per-letter icons and Deoxys's `icon_speed*.png`.
- Datapad footprint (`footprint.png`, 16x16, 1 bit).
- The Egg (`egg/`: front, anim_front, hatch and shard sheets, icon, palette), Spinda's spot masks (`spinda/spots/`) and the `question_mark/` placeholder pics.
- The cry (audio).
- Sprites only some species have: overworld walkers, placed dolls, minigame actors, cutscene actors, battle transitions.

## Wiki rows

`pending_art.csv` kind `pokemon`, subkind = species folder (not `egg` or `question_mark`): rows for `front.png`, `anim_front.png`
and `back.png` (each species also has `icon.png` and `footprint.png` rows, which are not this
tool's). The wiki has no rows for `normal.pal`, `shiny.pal` or the data in rows 6-8; this tool
writes them anyway. Categories: A1, A2.

## Size: 96x96 model output vs the 64x64 game

The LoRA below is trained on 96x96 sprites (768x768 downsampled 8x); Emerald's battle sprites are
64x64. Gen 3 sprites are 64x64, so its `gen3` training images were most likely 64x64 sprites
padded to 96x96. If so, the finisher downsamples 8x to 96x96 and crops the central 64x64 with no
rescaling, which keeps the pixel grid. **Test this first** on a few `gen3` renders (check the
content box fits 64x64 and the grid is 8 px); if it fails, fall back to the research plan's own
LoRA trained on Emerald sprites at 12x or 16x.

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates rows 1-8 above.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

## Research

- The one-pager below: the chosen model (an SD 1.5 sprite LoRA) and running it on a rented GPU.
- [`research/`](research/): copied from the prototype repo (`emerald-art-pipeline-prototype`,
  which is no longer maintained). Measured facts on all 384 vanilla species
  ([`vanilla-stats.json`](research/vanilla-stats.json)), the Star Wars creature for every slot
  ([`sw-creature-jobs.csv`](research/sw-creature-jobs.csv)), the fuller plan with the hard problems
  (back views, frame 2) in [`EMERALD-PLAN.md`](research/EMERALD-PLAN.md), and web research with
  sources. Where it mentions the `creature_sprite` package or `creature64` spec, that is the
  prototype's hand-drawing tool, not ported here.

---

# Research: sprite generation pipeline (one-pager)

**Model:** Pokémon Sprite PixelArt 768 v2.1-beta

## 1. Overview

The project will use Pokémon Sprite PixelArt 768 v2.1-beta by titansteng as its primary AI model for
generating Pokémon-style game sprites.

The objective is to generate original Pokémon-style creatures that match the visual aesthetic of
Generation 3 (Pokémon Ruby, Sapphire, and Emerald).

We expect to generate approximately 100 initial sprites, with the possibility of generating
additional variations and replacements as the game develops.

This is an offline asset-generation workflow. Generated sprites become ordinary game assets and are
not generated dynamically while the game is running.

## 2. Model information

| | |
|---|---|
| Model | Pokémon Sprite PixelArt 768 v2.1-beta |
| Creator | titansteng |
| Platform | Civitai |
| Architecture | Stable Diffusion 1.5 LoRA |
| File | `pksp768_V2-1.safetensors` |
| File size | About 72.5 MB |
| SHA256 | `df8494a9ff9ae96b53ecbcd327aa14626c59d3f573423892a650f9f6c21ab418` |
| Training resolution | 96x96 sprite images |
| Recommended generation resolution | 768x768 |
| Recommended downsampling | 8x, giving 96x96 images |

**Compatibility requirement:** this LoRA requires a compatible Stable Diffusion 1.5 checkpoint. It
must not be loaded into an SDXL pipeline.

### Model capabilities

- Generation-specific sprite styles: `gen1`, `gen2`, `gen3`, `gen4`, `gen5`.
- Front-facing sprites.
- Backside sprites using `backside`.
- Shiny variants using `shiny`.
- Pokémon type conditioning, including `grasstype`, `firetype`, `flyingtype`, `darktype`, `bugtype`
  and `ghosttype`.
- Some Pokémon name recognition.
- Special form conditioning, including `mega` and `gmax`.

No special trigger word is required.

Generation 3 is our primary target. Use `gen3` consistently in generation prompts.

## 3. Infrastructure and model consumption

### Decision: temporary rented GPU

We will use rented GPU infrastructure rather than running inference on the game development machine
or maintaining a permanent GPU server. The initial workload is about 100 sprites, which does not
justify dedicated GPU infrastructure.

The intended approach:

1. Rent a GPU instance.
2. Install or launch an inference environment.
3. Download the required Stable Diffusion 1.5 checkpoint.
4. Download and load the Pokémon Sprite PixelArt 768 v2.1-beta LoRA.
5. Run the sprite-generation jobs in batches.
6. Download all generated assets.
7. Shut down and terminate the GPU instance.

The GPU should only exist when we are actively generating assets.

### Preferred infrastructure: RunPod

RunPod is the preferred initial provider:

- Simple GPU rental without managing an AWS account's GPU infrastructure.
- Hourly GPU billing.
- Temporary GPU instances that can be launched and terminated.
- Support for custom inference environments.
- Can run ComfyUI and custom generation workflows.
- Options for dedicated GPU instances and serverless GPU execution.

An RTX 3090 or RTX 4090 is a reasonable starting point. We do not need an expensive datacenter GPU
for this SD 1.5 workload. Benchmark actual generation performance before choosing a more expensive
GPU.

### Alternative: AWS EC2

EC2 GPU instances are acceptable if we later want generation integrated into our AWS environment.
EC2 supports on-demand GPU instances that can be stopped or terminated when not needed. It adds
setup work:

- GPU instance availability and quotas.
- AMI and NVIDIA driver configuration.
- Python and CUDA environment setup.
- Storage management.
- Security groups and SSH access.
- GPU instance pricing and regional availability.

For the initial workload, RunPod is preferred because it reduces infrastructure setup.

### Alternative: hosted inference API

A hosted API could be used if it supports loading and running our exact custom LoRA. Do not assume
a generic image-generation API supports arbitrary Civitai LoRAs. Before choosing one, verify:

- Custom SD 1.5 checkpoint support.
- Custom LoRA upload or model-reference support.
- LoRA strength configuration.
- Image resolution configuration.
- Seed configuration.
- Batch generation.
- Output image retrieval.
- Pricing per generation or per GPU execution time.

Compare the cost of API inference against renting a GPU before committing to an API-based design.

## 4. Inference environment

Use **ComfyUI** as the initial inference interface. It provides a visual workflow for loading Stable
Diffusion checkpoints, applying LoRAs, configuring generation parameters and producing images.

Intended stack:

- Stable Diffusion 1.5 checkpoint.
- Pokémon Sprite PixelArt 768 v2.1-beta LoRA.
- ComfyUI.
- GPU-backed inference.
- Automated job submission and output collection.

The pipeline should be reproducible and configurable. Avoid configuring each sprite by hand: once a
generation workflow is established, save it and reuse it for every job.

## 5. Generation workflow

Generation is driven by structured job definitions, not prompts scattered through the project. Each
job defines:

- Creature name or identifier.
- Creature description.
- Type.
- Generation style (`gen3`).
- Sprite direction (front or `backside`).
- Whether the sprite is shiny.
- Positive prompt.
- Negative prompt.
- Random or fixed seed.
- LoRA strength.
- Output filename.
- Output location.

Example prompt:

```
gen3, pokemon sprite, front battle sprite,
single creature, centered composition,
gameboy advance pokemon emerald art style,
96x96 pixel art, limited color palette,
crisp pixel edges, clean outlines,
white background, no shadows
```

Use 768x768 as the working resolution and downsample 8x to 96x96, keeping the model's recommended
resolution and downsampling workflow. Test the interpolation method so pixel edges stay crisp.

## 6. Batch generation

The system must generate many sprites without manual interaction per image (about 100 jobs at
first). The pipeline should:

1. Load the model and LoRA once.
2. Accept a list of generation jobs.
3. Process jobs sequentially or in controlled batches.
4. Save each generated image independently.
5. Record the generation settings for every output.
6. Track successful and failed jobs.
7. Retry failed jobs without regenerating successful outputs.
8. Keep all generated outputs until they have been downloaded.

Support multiple variations of a creature by changing the seed. Avoid unnecessary parallel GPU
processes: a single GPU worker with a job queue is enough for the initial workload.

## 7. Output processing

The model generates at 768x768; the intended sprite resolution is 96x96 (see "Size: 96x96 model output vs
the 64x64 game" above for getting to 64x64). The output step should:

1. Receive the generated image.
2. Crop or normalise the composition if needed.
3. Remove or replace the background where appropriate.
4. Downsample to 96x96.
5. Inspect the resulting pixel edges.
6. Export to PNG.
7. Save the final sprite in the project's asset directory.

Background removal is a separate step. Do not assume that asking for a white background produces
transparency.

Review final images for:

- Creature silhouette.
- Anatomical consistency.
- Colour palette.
- Sprite alignment.
- Pixel-art quality.
- Background artifacts.
- Consistent framing.

Generated images are not automatically approved game assets.

## 8. Asset organisation

Keep these separate:

- Original 768x768 generated images.
- Processed 96x96 images.
- Approved final game sprites.
- Generation metadata.
- Saved generation workflows.

Example layout (adapt to this tool's `art/` and `output/` folders when it is built):

```
assets/
  pokemon/
    generated/
      originals/
      processed/
      approved/
    metadata/
      generation-manifest.json
    workflows/
      pokemon-sprite-workflow.json
```

Keep the original generated images so sprites can be reprocessed without paying for another
generation. Only approved sprites are consumed by the game.

## 9. Reproducibility

Every generated sprite has enough metadata to reproduce or iterate on it. Record:

- Model name and version.
- LoRA filename and SHA256.
- Base checkpoint name and version.
- Prompt and negative prompt.
- Seed.
- LoRA strength.
- Sampling settings.
- Generation resolution.
- Output-processing settings.
- Generation timestamp.

Use fixed seeds when iterating on one creature, and different seeds for variations.

## 10. GPU lifecycle and cost management

GPU infrastructure is temporary; the pipeline must not depend on a continuously running GPU server.

```
START GPU INSTANCE
       |
       v
INITIALIZE INFERENCE ENVIRONMENT
       |
       v
DOWNLOAD / LOAD MODEL AND LORA
       |
       v
SUBMIT GENERATION JOBS
       |
       v
GENERATE SPRITES IN BATCHES
       |
       v
DOWNLOAD ALL OUTPUTS
       |
       v
VERIFY OUTPUTS AND METADATA
       |
       v
STOP / TERMINATE GPU INSTANCE
```

- Cache the model and inference workflow in persistent storage where practical, so a restart does
  not re-download everything.
- Do not leave an idle GPU instance running.
- Do not terminate the instance until all images and metadata are downloaded and verified.
- For the initial 100 sprites, prefer simplicity and low total cost over a sophisticated
  distributed platform.

## 11. Future extensibility

The infrastructure should not depend on this particular LoRA. It should be possible to change:

- Base checkpoint.
- LoRA.
- LoRA strength.
- Prompt templates.
- Image resolution.
- Sampling settings.
- Output-processing pipeline.

That lets us try other sprite models later without rewriting the system. We do not plan to train a
custom model or LoRA; first evaluate the existing model's output quality.

## 12. Licensing and usage

Before using generated sprites in a commercial game, verify the model's license and commercial-use
permissions. Also consider the separate intellectual-property implications of Pokémon names,
characters, designs and recognisable derivative content. An openly available model does not grant
rights to the underlying Pokémon IP.

## 13. Reference

| | |
|---|---|
| Selected model | Pokémon Sprite PixelArt 768 v2.1-beta |
| Creator | titansteng |
| Platform | Civitai |
| Model file | `pksp768_V2-1.safetensors` |
| Architecture | Stable Diffusion 1.5 LoRA |
| Primary target | Generation 3 sprite aesthetic |
| Primary infrastructure | Temporary RunPod GPU instance |
| Inference interface | ComfyUI |
| Initial workload | About 100 sprites |
| Final native resolution | 96x96 PNG from the model; 64x64 in the game (see "Size" above) |

**Architectural principle:** AI generation is an offline, development-time asset pipeline. The game
only consumes approved, processed sprite assets.

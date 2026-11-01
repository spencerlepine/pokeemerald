# sprite-creature-generator

**Status:** PENDING. Approach researched and decided (below); the tool is not built yet. The build
waits on a rented GPU.

Companion battle sprites: front (2-frame anim), back, normal and shiny palettes, egg/hatch and form extras.

## Scope in this repo

- **Categories:** A1, A2, A5
- **Wiki rows:** `pending_art.csv` kind `pokemon` (front, anim_front, back, palettes) for each species; 1,262 PNGs
- **Format in the game:** 64x64 front + 64x128 anim_front, 64x64 back, one 16-colour palette per species plus shiny

> **Open question:** the model below is trained on 96x96 sprites (768x768 downsampled 8x), but
> Emerald's battle sprites are 64x64 with a 16-colour palette. The output step must still get from
> 96x96 to the game format (crop the padding or rescale, then quantise to 16 colours). Test this
> before generating at scale.

To build later:

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.

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

The model generates at 768x768; the intended sprite resolution is 96x96 (see the open question at
the top about the game's 64x64 format). The output step should:

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
| Final native resolution | 96x96 PNG (game format is 64x64, see top) |

**Architectural principle:** AI generation is an offline, development-time asset pipeline. The game
only consumes approved, processed sprite assets.

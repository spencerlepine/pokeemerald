# Palettes: the rules every art tool enforces

Every tool that writes a PNG or `.pal` into `../game` follows this file. There are two layers, and a tool must
know both:

1. **The hardware** (what the GBA and the ROM can hold). Strict: a file that breaks it does not install.
2. **The chosen themes** (the palettes picked inside those limits, in
   [`../wiki/bible/PALETTE.md`](../wiki/bible/PALETTE.md)). The default target for new art; checked as warnings
   unless a tool locks it.

Both are enforced by one shared tool, [`palette-enforcer/`](palette-enforcer/), run as the **last post-processing
step** of every generator (diffusion model, img2img, script, hand edit): whatever made the pixels, `enforce` makes
them legal and `check` decides whether they install.

## Layer 1: the hardware (strict)

### The full range

| Rule | Value | Why it matters to a tool |
|---|---|---|
| Colour depth | 15-bit BGR555: 32 levels per channel, **32,768 colours** in all | Any of these can go in any palette slot. This is the whole space the art can draw from. |
| 8-bit to GBA | `gbagfx` keeps the top 5 bits of each channel (`v >> 3`) | `#FFD5B4` shows as `#F8D0B0`. New art writes values that are **multiples of 8 (0-248)** so the preview equals the game. Vanilla files are off-step; they are read with `--lenient`. |
| Same colour twice | Two entries that are equal after `>> 3` are one colour | A wasted slot; `check` warns. |
| One palette (bank) | **16 entries; index 0 is transparent** (or the backdrop colour for BG palette 0) | 4bpp art has **15 visible colours**. |
| Palette RAM | 16 BG banks + 16 OBJ banks = 512 entries | At most **480 visible colours on one screen** (+ backdrop), and only if every bank is in use. |
| 8bpp art | One 256-entry bank (255 visible) | Rare in Emerald: title logo and banner, intro scene 3 actors, Rayquaza scene, region maps, roulette wheel, berry blender, frontier pass, trade (17 files). |
| 1bpp art | Ink or empty, no palette of its own | Footprints, Spinda spot masks, fonts. |
| Greyscale PNGs | The grey level is the pixel index; colours come from a `.pal` loaded elsewhere | Some fonts, masks and UI (`wallclock/hand.png`); only the index range is checked. |
| Tiles | 8x8; tile sheets 128 px wide; sizes multiples of 8 | `check --tile`. |
| Fades and weather | Screen fades, drought and rain tint every loaded palette at runtime | Keep some headroom: a sprite that only reads in its brightest colours washes out in drought. |

### Which bank an asset gets (the per-asset limit)

The real limit for a tool is usually not 15 colours, but **whose 15 colours**. Many assets share a bank, so their
palette is locked and the tool may only choose indices.

| Asset (category) | Depth | Palette | Locked? | `enforce` / `check` flags |
|---|---|---|---|---|
| Creature front, frame 2, back (A1, A2) | 4bpp | own `normal.pal`, shared by all three pics | no: the front picks it, frame 2 and the back are mapped onto it | front: `--colours 15`; back/frame 2: `--pal normal.pal` |
| Creature shiny (A1) | - | `shiny.pal`, **same indices** as `normal.pal` | indices locked | recolour the `.pal` only, never the pixels |
| Creature icons (A3) | 4bpp | one of 3 shared `icon_palettes/icon_palette_{0,1,2}.pal` | **yes** | `--pal icon_palette_N.pal` (pick the N with the best fit) |
| Footprints (A4), Spinda spots (A5) | 1bpp | none | - | `--bpp 1` |
| People walkers (B3), creature walkers (A6), dolls (C4) | 4bpp | shared NPC banks `npc_1..4` (OBJ slots 2-5), player, or a special tag | **yes** for NPC banks | `--pal npc_N.pal` |
| Trainer fronts (B1), Prof. Korr (B4) | 4bpp | own palette from the PNG; Brendan/May/Wally/Steven use `trainers/palettes/*.pal` shared with their back pic | shared ones locked | `--colours 15` or `--pal` |
| Trainer backs (B2) | 4bpp | `trainers/palettes/*.pal` | **yes** | `--pal` |
| Items, fruit, decorations (C1-C3) | 4bpp | own palette per icon | no | `--colours 15` |
| Capture pods, type labels (C5, C6) | 4bpp | small shared sets | mostly | `--pal` where shared |
| Overworld tilesets (D1, D2) | 4bpp | BG banks **0-5 primary, 6-12 secondary**; 13-15 belong to the UI (14 standard window, 15 dialogue) | per tileset; animations reuse the tileset's banks | every tile in one 16-colour bank: `--pal` per bank |
| Doors, field effects, field objects, weather (D3-D6) | 4bpp | OBJ banks loaded by tag; many reuse NPC or tileset colours | often | `--pal` where shared |
| Battle backgrounds (E1) | 4bpp | a few BG banks per environment | no | `--colours 15` per bank |
| Move animations, transitions (E3, E4) | 4bpp | small OBJ/BG palettes; some animations fade or cycle entries by index | indices that code touches are locked | `--pal` when code touches entries |
| UI screens (D7, D8, E2, F, H) | 4bpp (a few 8bpp) | one or more BG banks per screen; text uses 3 entries (fill, shadow, background) | the text entries | `--pal` for shared frames |
| Title, intro, credits, story scenes (G) | 4bpp / 8bpp | per scene; code palette-cycles some entries (intro scene 2 swaps BG 9 and 10) | cycled entries | the cutscene tool's `pal: [16 colours]` |

When unsure, open the vanilla file the row replaces: its PNG palette and its `.pal` are the contract. Keep the same
bank, the same number of entries, and the same index meaning (ramps, transparent, cycled entries).

## Layer 2: the chosen themes (the default target)

[`../wiki/bible/PALETTE.md`](../wiki/bible/PALETTE.md) is the source of truth. `palette-enforcer` reads its tables
directly (nothing is copied), so a change in the wiki is enforced on the next run. List them with
`python -m gba_palette themes -v` (from `palette-enforcer/`):

| Theme id | From the wiki section | Use it for |
|---|---|---|
| `kyber-gold` | Title screen and logo | Title screen, logo, version banner, boot/copyright screens, Kyber branding |
| `alliance-dawn` | Rebel Alliance | Player, rivals, Rebel trainers and NPCs, Rebel bases |
| `imperial-order` | Galactic Empire | Imperial trainers, troopers, Imperial bases and ships |
| `swamp-throne` | Hutt Cartel | Hutt Cartel trainers, Hutt palaces, Sabacc Den accents |
| `hyperspace-console` | HUD and menus: surfaces and text | Every menu and HUD surface and its text |
| `status-and-accents` | HUD and menus: status and accents | Cursor (gold only), HP, EXP, holo accents |
| `battle-backdrop` | Battle backdrop | Battle backgrounds behind creatures |
| group `hud` | `hyperspace-console` + `status-and-accents` | All UI screens |
| group `factions` | the three faction themes | Mixed crowds, faction-neutral NPCs |

Rules that come with the themes (from the wiki's "Rules of thumb"): creatures pop and chrome recedes; never put
creatures on the darkest menu colours; three-colour text; gold is the only selection colour.

**Creatures have no theme.** Each companion keeps its own 15 colours (layer 1 only); the themes are for people,
places, UI and branding.

**Shared banks win over themes.** A walker on `npc_4` can only use `npc_4`'s colours, whatever its faction. To
give a faction its own colours there, the theme must first be put into a bank (a new NPC palette tag), which is a
decision for the owner, not a tool.

**New places need a theme first.** Planet and biome palettes (Tatooine desert, Hoth snow, Mustafar lava...) are not
in the wiki yet. Before `tile-generator` (or any tool) makes a new place, it adds a `## Planet: <name>` section to
`../wiki/bible/PALETTE.md` with GBA-step values and roles, in the same table format, so it becomes a theme id.

## The enforcement step (every generator)

```bash
cd tools/palette-enforcer
# 1. post-process the raw render (RGB/RGBA from a model, a script or a hand edit)
python -m gba_palette enforce raw.png out.png --bpp 4 --key auto \
    [--pal locked.pal | --theme <id> [--strict-theme | --free N]] [--write-pal out.pal]
# 2. the gate: exit 1 on any hardware error (or theme error with --strict-theme)
python -m gba_palette check out.png [--pal locked.pal] [--theme <id>] [--tile]
# 3. only then install into ../game
```

`enforce` does, in order: transparency to index 0 (alpha or `--key`), snap to GBA steps, pick the palette (locked
`--pal` keeps its indices; `--theme` pulls each colour onto the theme within `--tolerance`, and beyond it allows at
most `--free` off-theme colours, `--strict-theme` none), map every pixel to the nearest colour in CIELAB without
dithering, and write the indexed PNG at the exact bit depth.

Requirements for a tool:

- Its pipeline ends with `enforce` (or produces indexed pixels against a known palette, as the walker and cutscene
  tools do) and **refuses to install a file that fails `check`**.
- It names, in its README, the layer-1 format and bank of every asset it writes, and the layer-2 theme (or "none:
  creature" / "none: audio").
- Generators with a prompt (diffusion, LoRA) also put the theme in the prompt ("limited palette, gold and black"),
  but the prompt is a hint: `enforce` is the guarantee.
- Vanilla files kept as they are pass with `check --lenient`. `python -m gba_palette audit ../../game/graphics --lenient`
  passes today (5,291 files); keep it passing.

## Status per tool

| Tool | Layer 1 (hardware) | Layer 2 (theme) | Enforcement |
|---|---|---|---|
| `palette-enforcer` | defines it | reads the wiki | the shared tool |
| `sprite-walker-generator` | locked NPC/player banks; draws indices | optional `theme:` in the spec (warnings) | **wired**: `build` reports the gate, `install` refuses a failure |
| `title-screen-generator` | 8bpp logo/banner, 4bpp creature | `kyber-gold` | **wired**: `ship.py` runs the gate after writing |
| `cutscene-generator` | `gba()` checks every target against its palette; off-step `pal` colours are truncated with a warning | per scene (`kyber-gold`, factions, new planet themes) | **wired**: `scripts/rom-preview.sh` runs `audit` on the scene output first |
| `sprite-creature-generator` | own 4bpp bank shared by front/frame 2/back; shiny same indices | none (creature) | to build: Python finisher calls `enforce` |
| `sprite-trainer-generator`, `sprite-trainer-back-generator` | own bank, or shared `trainers/palettes` | faction theme by trainer class | to build: finisher calls `enforce` |
| `sprite-creature-icon-generator` | 3 locked icon banks | none (creature) | to build: `enforce --pal icon_palette_N.pal` |
| `sprite-creature-footprint-generator` | 1bpp | none | to build: `enforce --bpp 1` |
| `sprite-creature-extras-generator` | egg: own bank; spots: 1bpp | none | to build |
| `sprite-icon-generator` | own bank per icon; shared pod/type sets | `hud` accents for type labels; otherwise none | to build |
| `tile-generator` | BG banks 0-5 / 6-12, 13-15 reserved | a planet theme per biome; `battle-backdrop` | to build: theme first, then `enforce --pal` per bank |
| `vfx-generator` | OBJ banks by tag, cycled entries locked | sabers from the faction themes; weather per planet | to build |
| `ui-skin-generator` | screen banks, 3-colour text | `hud` (strict for surfaces and text) | to build: `enforce --theme hud` |
| `play-tester`, `music-generator`, `sfx-generator`, `cry-generator` | n/a (no art) | n/a | n/a |

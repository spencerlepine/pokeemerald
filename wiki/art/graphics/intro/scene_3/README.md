# Intro scene 3 titans: follow-up task (HUMAN-TODO)

**Status (2026-11-01):** GREATKRAYT, SANDO and the EXOGORTH are **not drawn yet**. The game shows the
project placeholder sprite (the magenta circle with a slash from `z-day/.dev/assets/16x16-placeholder-image-sprite.png`,
scaled up) where each creature stands, so the opening plays end to end. The rest of scene 3 is in the game:
the capture pod (`pokeball.png`) and the sand and sea backgrounds (`legend_bg.png`). The clouds, lightning,
bubbles and Rayquaza's orb are still Emerald's.

Rows in `database/pending_art.csv` (each one's `art_notes` points here):

| File | Becomes | In the game now |
|---|---|---|
| `graphics/intro/scene_3/groudon.png` + `groudon.bin` | GREATKRAYT (land titan) | placeholder |
| `graphics/intro/scene_3/kyogre.png` + `kyogre.bin` | SANDO (sea titan) | placeholder |
| `graphics/intro/scene_3/rayquaza.png` + `rayquaza.bin` | the EXOGORTH | placeholder on the light sky band |

## The subjects (from the wiki)

- **GREATKRAYT** (Groudon): "Titan of the land, the eldest greater krayt dragon" (`entities.csv`, `species:groudon`;
  canon source: Greater krayt dragon). The canon page describes the species with a long neck, a whip-like tail,
  horns, sharp teeth and five pairs of legs, swimming through sand on Tatooine.
- **SANDO** (Kyogre): the sea titan Jabba wakes (`bible/STORY.md`, Act 6).
- **EXOGORTH** (Rayquaza): lives in the asteroid field (ASTEROID SPIRE) and calms the other two (`bible/STORY.md`).

## How Emerald's scene is built (what the art has to fit)

Code: `game/src/intro.c`, `Task_Scene3_*`. Art pipeline: `tools/cutscene-generator/scenes/intro_legends/`
(`intro_legends.px.js`; the placeholder section is marked).

- **Groudon and Kyogre are affine (rotate/zoom) backgrounds**: 8bpp tiles, a 512x512 map with one byte per
  tile, no tile flips, **at most 256 unique tiles** for the whole sheet. Pixels index the scene's 256-color
  `bg.pal`: Groudon uses bank 1 (indices 16-31), Kyogre bank 2 (32-47).
- **Each creature appears three times on its map, in three poses.** The camera jumps between the copies to
  animate (Groudon: neutral, head up roaring, crouched; Kyogre: three fin and body positions). The copies
  share most of their tiles, which is how three poses fit in 256 tiles. Pixel boxes of Emerald's copies:
  - Groudon: (293,1)-(465,87), (118,123)-(289,215), (39,354)-(209,431)
  - Kyogre: about (112,80)-(240,176), (112,336)-(240,424), (368,344)-(496,424)
- **The glow is a palette pulse**: entry 15 of bank 1 (Groudon) or bank 2 (Kyogre) is stepped through
  bank 15 (blue to red) by the code. Anything drawn in that index lights up.
- **The camera is letterboxed** to 240x96 (`Task_Scene3_NarrowWindow`) and zooms in on one spot at the end
  of each creature's turn (Groudon's eye, Kyogre's eye). Groudon's floating rocks and Kyogre's bubbles are
  sprites placed at fixed screen positions (`sGroudonRockData`, `sKyogreBubbleData`).
- **Rayquaza is a 4bpp text background** in bank 5 (`rayquaza.png` + `rayquaza.bin`), drawn on a light sky band
  (rows 32-127, index 13). The code flashes bank 5 entries 8, 12, 13 and 14 and dims the whole bank
  (`Task_RayquazaAttack`, the orb sprite in `misc.png`).
- Emerald's art is silhouette-style: Groudon is solid black with thin blue vein lines and a white eye;
  Kyogre is black with red lines. Look at the originals below.

## Originals kept for reference

`tools/cutscene-generator/scenes/intro_legends/reference/emerald/`:

- `raw/`: Emerald's own files (`groudon.png/.bin`, `kyogre.png/.bin`, `rayquaza.png/.bin`, `bg.pal`, and the rest of scene 3).
- `render_*.png`: each map drawn out with its real palette (magenta = transparent).
- `poses_groudon_top_kyogre_bottom_2x.png`: the three poses of each creature side by side.
- `emerald_scene3_rom_realspeed.gif` and `emerald_scene3_rom_contact_sheet.png`: the scene as Emerald plays it.

They are also in git history (any commit before `1124dd64`).

## History

- Round 1 (`1124dd64`): GREATKRAYT as a black silhouette with blue veins. Owner: "those monster sprites are just
  horrible ... you need to draw way better art".
- Round 2 (`36226f14`): GREATKRAYT redrawn with full volume shading. Owner: "it's too detailed and it's too
  shaded. It just doesn't fit the style of the art like see how the other one is so simplistic and it's kinda
  like a silhouette."
- 2026-11-01: placeholders in, titans parked as this follow-up task. Captures of both rounds are in
  `tools/cutscene-generator/scenes/intro_legends/review/`.

## Tools on hand

- `tools/cutscene-generator`: `gba(..., { affine: ... })` writes an affine 8bpp sheet + map within the 256-tile
  budget; `scripts/rom-capture.sh` records the real ROM as a real-speed GIF.
- `tools/cutscene-generator/scripts/creature-from-image.py`: turns a picture on a plain background into a
  16-color sheet placed at the three pose anchors (untested on real creature art).
- `tools/sprite-trainer-generator/civitai/`: the hosted image generator (needs the Civitai network and key in
  the session's environment, and costs Buzz).

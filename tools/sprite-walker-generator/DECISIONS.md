# sprite-walker-generator: decisions and why

Why this tool is built the way it is. Read it before changing the tool; don't re-litigate a
decision without new evidence, and add new ones at the bottom (decision + reason). Format facts
are in `README.md`.

## Goal

Draw the Star Wars replacement art for the pokeemerald fork (list: `../../wiki/database/pending_art.csv`,
every image is `PENDING_ART`) at scale with AI, and have every
output drop into the game unchanged: right size, right frame layout, right palette indices,
and Emerald's hand-pixelled look.

## D1. Pipeline choice: LLM + Python tool first; diffusion LoRA deferred (2026-10-31)

Two options were on the table:

1. **LLM + Python tool.** The LLM writes the sprite as data, a tool renders, enforces and
   checks it, and the LLM iterates from the previews.
2. **Stable Diffusion LoRA** trained on Emerald art, plus a finisher (the design in
   `spencerlepine/black` `.docs/2D-SPRITE-LoRA-PIPELINE-DESIGN.md` and
   `WALKER-SPRITE-PIPELINE-DESIGN.md`, written for Pokémon Black).

We start with option 1. Reasons:

- **Size decides it.** A walker frame is 16x32 with ~226 opaque pixels, a tile is 8x8, an item
  icon 24x24. At that size every pixel is a deliberate choice, which is where an LLM writing
  an index grid is strong and where diffusion is weakest (it paints at 1024 px and has to be
  snapped down, which is what the Black design's whole finisher exists to repair).
- **The constraints are exact, not stylistic.** Shared 16-colour NPC palettes, fixed frame
  order, feet on row 30. A grid of palette indices meets them by construction.
- **Option 2's guard rails are option 1's tool.** Any LoRA output still needs palette
  snapping, layout, lint and previews. Building those first is not throwaway work; it becomes
  the LoRA finisher if we ever need one.
- **Data is thin for a LoRA here.** Emerald has 90 people walkers. The Black design had 758
  walker sets and still chose diffusion only for keyframes.
- **No GPU or SD setup exists yet**, so option 2 cannot be tested now.

When to revisit: if the 64x64 categories (Pokémon fronts/backs, trainer pics: about 400
species + 101 trainers) fail human review with option 1. Larger, painterly sprites are where
diffusion has a real edge.

## D2. The LLM writes palette-index grids, not RGB and not code (2026-10-31)

A sprite is a YAML spec (`art/<name>.yaml`): a `legend` mapping one character
to one palette index, and one 16-wide text grid per frame. Reasons: it is impossible to leave
the palette; the grid is readable and diffable; the LLM sees exactly what it is placing.

## D3. Hand-placed 2D grids, not z-day's 3D-model renderer (2026-10-31)

z-day's `characters/body-sheets` tool ray-marches a text-defined 3D model into sprites. It
works for z-day's 24-32 px chibi with many directions and animations. For Emerald we do not
use it: Emerald walkers are 3 directions x 3 poses of hand-pixelled 16x32 art, and a render
does not read as hand-drawn at that size (the Black walker design reached the same
conclusion). What we did keep from z-day: text-file sources, a fixed shared palette, a build
command that writes the game files plus previews, and "look at every image you produce".

## D4. Step frames are derived from the stand frames (2026-10-31)

A spec frame can be `base: <frame>, shift: 1, patch_y: N, rows: ...`: copy a frame, bob it
down 1 px as Emerald does, and redraw only the legs/arms rows. Or `mirror_of: <frame>`. This
cuts the drawing to 3 stand frames plus a few rows per step and keeps the body identical
across frames, which is what stops walk cycles from wobbling.

## D5. Lint against measured Emerald, not against taste (2026-10-31)

`build` errors on format breaks (size, >15 colours) and warns when a style
metric falls outside the 5th-95th percentile of the 90 vanilla walkers (`corpus/`). These are
warnings, not errors: a big armoured character may legitimately be wider than any Emerald
NPC. Each accepted deviation is noted in the sprite's spec.

## D6. Characters keep a shared NPC palette; switch palettes before adding one (2026-10-31)

Walkers share four 16-colour NPC palettes. Adding palettes costs OBJ palette slots at runtime,
so a new character first picks the vanilla NPC palette that already has its colours, and the
spec's `palette_tag` moves it there (`install` edits `.paletteTag`/`.paletteSlot`). Vader moves
from Maxie's `NPC_2` (reds) to `NPC_4` (blue-blacks + greys, the palette of Steven and the Aqua
grunts). Recolouring the four NPC palettes themselves is a project-wide art-direction decision
for later (e.g. desert tones for Tatooine).

## D7. "Black" clothing uses Emerald's blue-grey ramp (2026-10-31)

First Vader draft used the near-black `8 16 32` as the armour base: outline and armour merged
into one blob. Emerald draws dark clothes as a blue-grey ramp (`57 74 98` base, `106 139 172`
highlight, `8 16 32` shadow) inside a pure black outline. The second draft follows that and
reads as a helmet at 1x.

## Prototype 1 result: Vader walker (2026-10-31)

`output/vader/vader.png` replaces `team_magma/maxie.png`. Verified: 9 frames, 2304 bytes of 4bpp
through pokeemerald's own gbagfx with an identical round trip; `install` into a scratch copy
of pokeemerald changes only the PNG and Maxie's two palette lines. Not verified: an actual ROM
build (no ARM toolchain in the cloud container).

Known gaps, by the linter and by eye:

- Bulkier than any Emerald NPC (area 274 vs p95 252): cape plus helmet flare. Accepted for
  Vader for now; human to judge.
- Only 9 colours vs Emerald's 10-15, and few single-pixel accents (`orphans` 0.07 vs
  0.10-0.23): reads flatter than vanilla sprites, which use more small highlights.
- Step frames change 40% of pixels vs Emerald's ~70%: arms barely swing under the cape.
- Up view is a plain dome + cape with little detail.

Owner reviewed it as about 90% there; the helmet was redrawn (next section).

## Helmet variants (2026-10-31)

Owner feedback on prototype 1: "about 90% there, the helmet looks a little odd". Three variants
change only the helmet rows (10-19) of the stand frames; body and step frames are inherited.
Review sheet: `output/vader-helmet-variants.png` (`python -m walker_sprite compare`).

- `vader_a`: round dome, pinch at the temples, skirt flaring past the shoulders. Best
  silhouette, especially from behind.
- `vader_b`: original helmet plus face detail (lit brow ridge, grey cheeks, grill triangle).
  Reads most as Vader's mask from the front.
- `vader_c`: smaller helmet (12 wide, starts row 11) so shoulders show. Closest to vanilla
  proportions, and the only variant inside every size range of the corpus.

A first pass of A (pointed dome) and B (whole face plate in grey) was discarded before review:
the cone read as a hood and the grey plate as one big ring.

**Picked: A** (owner, 2026-10-31). `art/vader.yaml` is now variant A; B and C
were removed from the repo (they live in git history and in the comparison sheet). For later
helmeted characters, start from A's shape language: round dome, pinch at the temples, flare
past the shoulders, big dark lenses, grey grill.

## D8. The tool enforces; a human judges likeness (2026-10-31)

What the tool guarantees by construction or check: size, frame order, palette indices, colour
count, gbagfx round trip, and Emerald's measurable style ranges. What it cannot judge: whether
the character reads as *that* character, and taste calls (helmet shape, proportions). Those
stay with a human, but cheaply: the LLM produces 2-4 variants of the uncertain part, the human
picks from a `compare` sheet, and the pick plus the reason is recorded here so later sprites
inherit it instead of being asked again.

## D9. This tool is standalone (2026-10-31)

Owner: "each tool is standalone... Each tool will be its own thing and have its own pipeline."
This folder holds everything the tool needs: its Python package, `requirements.txt`, this
decision log, the format facts (`README.md`), its corpus, `art/` and `output/`. Nothing is
imported or read from outside it except a pokeemerald checkout (`EMERALD_DIR`). Code it has in
common with other art tools (spec parsing, palette rules, gbagfx verify, metrics) is a copy
trimmed to what this category uses, so this tool can be changed or rewritten on its own.

## Owner review of batches 0-1 (2026-11-01): rejected

Artist, Beauty and the first two passes of batch 1 (black belt, boys 1-3, bug catcher) were drawn
from scratch as index grids. Owner: "horrible... when you compare them side-by-side they look
nothing alike. The Pokémon one is way better." Also: cel shading and the top-down perspective
matter and must be checked by the tool, and the LLM must iterate on its own work until it is
close before asking for the last 5%. Artist and Beauty were un-marked in the wiki; Vader stays
(approved earlier, but it would score 30/100 under the new rules; see D11).

## D8. Style is measured and gated, not described (2026-11-01)

`STYLE.md` records what the 90 vanilla sheets actually do, with numbers. The build prints a
0-100 STYLE SCORE over 11 rules (coloured outlines, four skin tones, full ramps, shadow weight,
hair rows above the eyes, eye row, head width, height, step change, orphans, inner black), each
bound to the corpus quartiles. Nothing goes to the owner under 90 or with a FAIL the vanilla
sheet does not share. The report also scores the vanilla sheet being replaced, because some
vanilla sheets are outliers themselves (bug catcher's straw hat is drawn in skin tones).

## D9. Coloured outlines (2026-11-01)

The first drafts outlined everything in pure black. Vanilla outlines each material in the dark
tone of its own ramp; black is 18% of outline pixels on the median sheet and goes on eyes, soles
and creases. This was the biggest single reason the drafts looked like stickers.

## D10. Compose from vanilla sheets first; draw from scratch last (2026-11-01)

Emerald's artists reused bodies with new heads and palettes. The spec now supports
`base_sheet`, `recolor`, `parts` (regions of another vanilla sheet, following each frame's bob)
and per-frame patches. A generic NPC row (most of the 253 object_events rows) is a recolour,
a palette move and a small prop; it scores 95-100 by construction and keeps the walk cycle.
Hand-drawn grids remain for silhouettes no vanilla sheet has, and they are the ones to score
hardest. `corpus/parts.png` is the catalogue to pick from.

## D11. Vader is grandfathered, flagged for a redo (2026-11-01)

Approved before the style rules existed; fails outline, skin and perspective rules (score 30).
Suggest redrawing him under D9/D10 (compose from a vanilla body, keep the approved helmet
silhouette, recolour outlines to the navy ramp) and re-approving.

## D12. `accept:` — a rule may be waived, with a printed reason (2026-11-01)

A spec can list style rules it knowingly breaks (`accept: {height: "Yoda is a small species"}`).
The build still measures them and prints the reason next to the score, so a reviewer sees what
was waived and why instead of a silent pass.

## D13. Form shading is learned from Emerald, not hand-painted (2026-11-01)

Batch 2 v1 was rejected ("elementary... don't follow the art style... can't tell who they are").
Flat fills with a dark outline are what made them elementary: every vanilla walker shades each
volume (light on top, mid, dark underneath, outline in the ramp's darkest tone) and the first
drafts did none of that. Hand-placing tones for 9 frames x 15 colours is where the LLM kept
failing, so the tool now does it.

`walker_sprite/shade.py` learns a tone table from all 90 vanilla people sheets: for every opaque
pixel it records a local key (its material's skin-ness, the distance to its region's edge in
four directions capped at 3, and what lies beyond each edge: transparency, another material,
or black) and the tone the artist used. Re-shading vanilla sheets from their regions alone
gives the right tone 73% of the time (always-mid: 30%; held-out sheets: 64%), and
`corpus/shader-check.png` shows the re-shaded sheets are hard to tell from the originals.

A spec in shade mode (`shade: true`) draws *regions*, not colours: letters mapped by
`materials:` to a ramp (`s a b c`), white or black; distinct letters are distinct volumes even
on the same ramp (a sleeve against a torso); `legend:` holds only hard pixels (eyes, lights).
A vanilla body can be used as regions (`base_sheet` + `remap`) and new heads or props patched
in. `python -m walker_sprite shader` rebuilds the table; `regions <png>` prints any sheet as
letters to start from.

## D14. What the table cannot do, and the knobs added for it (2026-11-01)

Tried and measured on the same vanilla set:

- A purely rule-based volume shader (outline ring + top 40% light + bottom row dark) scores
  51% against vanilla and over-outlines every volume boundary. Rejected as the default, kept
  as an opt-in: a material written `c!` is shaded by the rules. Used for flat garments the
  corpus has no local match for (Yoda's robe, Dexter's apron and trousers).
- A hybrid (table outlines, positional interior) scores 60-63%. Rejected.
- Minimum-support back-off in the table changes nothing on held-out sheets. Rejected.

Knobs that did help the alien drafts: `skin-b` shades a ramp with the face statistics
(bald green or grey heads were turning to mud under the hair/cloth statistics; the four face
tones collapse onto three with shade folded into mid); `w/c` gives white an outline in ramp c's
dark tone (vanilla white shirts are edged, a white region on its own is not); a despeckle pass
removes single odd pixels the local keys leave next to eyes and corners.

Where batch 2 v3 still falls short of vanilla: identity at 16 px rests on two or three
silhouette cues per character, and a deep-cut character (Dexter) has none that survive. Big
single-material heads are smooth now but featureless; vanilla heads get their structure from a
hair/face split, which Yoda's dome/face volumes imitate. The owner judges the rest.

## D15. Round volumes are cel-shaded in concentric bands (2026-11-01)

Owner: "how come it's not using cel shading on rounded heads?" The learned table only sees 3 px
around each pixel, so on a big head it returns mid almost everywhere: a flat disc with an
outline. Vanilla bald heads (Spenser, Sidney, the Gentleman) are shaded in bands from the
silhouette inwards: outline, a base ring that turns to shade on the lower half, and a light
core pushed up toward the light; in the side view the core leans to the face and the far back
darkens. A material written with `@` (`s@`, `skin-a@`, `c@`) is shaded that way
(`shade.shade_round`); eyes and tattoos inside the head do not break the bands. Applied to the
shipped Yoda, Dexter, Maul, Zuckuss and Tarfful heads, which were re-shipped.

## D16. Use the palette: a colour budget rule, glints and detail ramps (2026-11-01)

Owner, comparing Maul and Zuckuss with vanilla Sidney and Spenser: "I don't think you actually
use as many colours as you could have." Measured: vanilla walkers use a median of 13 of the 15
colours in the facing-down frame (p25 12); the shipped drafts used 8-11. New style rule
`colours_used` (min p25, weight 15). Ways to reach it without leaving the palette: round skin
volumes get a 1-2 px white glint on the crown (as vanilla bald heads do); details go on ramps
the body does not use (Yoda's cord on ramp a and tunic on the skin ramp, Maul's horns in skin
light/outline and a yellow belt, Zuckuss's tunic on the skin ramp, Tarfful's studded steel
bandolier in all three ramp-a tones plus a tan pouch, Dexter's wattle on the skin ramp).
All five re-shipped at 12-14 colours.

## D17. Forms: `%` material flag for big sprites

Emerald's 32x32 and 64x64 sprites (legendaries, Vigoroth, the player's bikes) are stacks of
overlapping forms: crown, snout, jaw, shoulders, back, belly, each leg, wing tiers. Each form has its
own 1 px outline in its ramp's darkest tone, is lit on its top and shaded along its bottom, and the
form behind darkens where the one in front overlaps it. The `@` shader bands from the outer silhouette
only, so a big body came out as one flat fill with an outline (the first large mockups).

`%` (e.g. `c%`, `skin-a%`) shades a letter as a form: its distance is measured from anything that is
not its own volume, so touching forms each get an outline and a lit top inside the silhouette; forms
6 px or taller also darken their bottom third (lit from above and in front, the top-down camera).
`@` is unchanged, so every shipped 16x32 sprite rebuilds identically.

Refined after the first large redraw: hard detail pixels inside a form belong to it (a 1 px crease or
glint no longer grows a dark ring); where two forms touch, the one declared later in `materials` is in
front and owns the outline, the one behind keeps its own tones to the boundary; and 3-tone ramps use
their dark tone for the bottom band (the D13 table shader used the mid tone there).

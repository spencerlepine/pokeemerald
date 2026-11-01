# Emerald walker style, measured

What makes a 16x32 walker read as Emerald art. Every number below is measured on the 90 vanilla
people sheets (`python -m walker_sprite corpus` rebuilds `corpus/people16x32.json`), and the
`score` command checks a new sprite against each rule. Read this before drawing a pixel; it is
what the first drafts got wrong (owner: "they look nothing alike, the Pokémon one is way better").

## 1. Outlines are coloured, not black

Emerald outlines each material in the **darkest tone of that material's ramp**: skin is outlined
in index 4 (dark red-brown), a blue shirt in index 10, hair in index 13. Pure black (15) is only
18% of outline pixels on the median sheet (p95: 61%), and it goes on eyes, shoe soles, and the
deepest creases. Share of all outline pixels, corpus-wide:

| index | 13 (ramp C dark) | 15 black | 4 (skin dark) | 10 (ramp B dark) | 7 (ramp A dark) | everything else |
|---|---|---|---|---|---|---|
| share | 22% | 22% | 21% | 15% | 13% | 7% |

A sprite outlined 100% in black looks like a sticker. This is the single biggest difference.

## 2. Every material is a full 3-tone ramp, shaded from above

The four NPC palettes have the same layout: 1-4 skin (light, base, shade, outline), 5-7 ramp A,
8-10 ramp B, 11-13 ramp C (each light, mid, dark), 14 white, 15 black. Vanilla uses **all 4 skin
tones** on every sheet and **all 3 tones** of every ramp it touches (median 3, p5 2).

Tone weights inside a ramp, averaged over the corpus: light 17-27%, mid 31-34%, **dark 41-52%**.
Shadow dominates because the light comes from straight above (the camera is above and in front):
the top of the hair / hat / shoulders is light, the bottom of every shape is dark, and the torso
row directly under the chin is in shadow.

## 3. Top-down three-quarter perspective

The camera looks down at about 45 degrees. Consequences that must be drawn, not implied:

- **You see the top of the head.** On a facing-down sprite the hair starts 2-8 rows (median 5)
  above the first skin row, with the eyes on row 7 (p5 4, p95 10) counted from the top of the
  sprite. Hair takes a third of the sprite and shows its crown highlight.
- **Hat brims and shoulders are ellipses** seen from above, wider than the head and drawn with a
  light top edge and dark underside.
- **The body is foreshortened:** head 14 wide and ~10 rows, torso ~6 rows, legs 2-4 rows. The
  whole figure is 18-21 rows tall (median 20), 14-16 wide, standing on row 30.
- **The facing-up frame shows the back of the head** (all hair, no face) and the collar; the
  facing-left frame shows one eye near the front of the face, the hair wrapping the back, and
  the near arm in front of the body.

## 4. Face

Two eyes, each a 1-wide, 2-tall black bar (index 15) with 2 skin pixels between them, on the
lower half of the face; a 1-px skin-shade (3) row under the face for the chin; no mouth. Skin
light (1) sits above the eyes and on the nose line, base (2) fills, shade (3) under the chin and
on the far side, outline (4) around.

## 5. Legs and the walk

Legs are two stubs 2-3 wide, outlined in the trouser-dark tone, with shoes in a dark ramp tone
or black. Step frames bob the **whole body down 1 px**, swing one leg forward (it gets 1 row
longer) and the other back, and move the arms; about 70% of the pixels change between a step
and the stand (p5 62%). Walk cycles that only move feet look frozen.

## 6. Reuse, as Emerald did

Emerald's artists reused bodies: many NPCs share a torso and legs with a new head, hair and
palette. The best way to match the style is to do the same: start from the vanilla sheet the
row replaces (`base_sheet:`), swap in a head or body from another vanilla sheet (`parts:`),
remap ramps (`recolor:`), and hand-draw only what is new (props, helmets, insignia) with
coloured outlines and full ramps. Draw from scratch only for silhouettes no vanilla sheet has
(droids, Hutts, Yoda), and score those hardest.

## 7. Worked example: the vanilla Youngster (NPC_1), facing down

```
row  0123456789ABCDEF   notes
12   .....AAAAAA.....   A = 10, dark blue: the hat's outline (ramp B dark), not black
13   ...A98888889A...   8/9 = ramp B light/mid: crown of the cap is lit from above
14   ..A9888888889A..
15   ..A9988998899A..
16   ..A9999CC9999A..   9 (mid) takes over lower on the cap; C = 12, the badge
17   ..DA99CCCC99AD..   D = 13, hair dark, peeking under the brim at the sides
18   .41DDAAAAAADD24.   brim: a dark ellipse row; 4/1/2 = skin outline, light, base (ears)
19   .42D11F11F11D24.   eyes F = black, 1-wide, skin light (1) beside them
20   ..4322F11F2234..   eye bars are 2 tall; 3 = skin shade at the cheeks
21   ...4332222334...   chin row in shade, outlined in 4
22   ..439333333934..   collar: 9 (ramp B mid) with skin shade under the chin
23   ..448E4444E844..   shoulders: 4 (dark) edges, E = white shirt highlight
24   .4224EEEEEE4224.   arms are skin: outline 4, base 2
25   .43348EEEE84334.   shirt lit at the top, 8 (ramp B light) at the cuffs
26   ..44A988889A44..   belt in ramp B, outlined in A (10)
27   ...AAAAAAAAAA...   trouser top: dark row (shadow under the shirt)
28   ...D42344324D...   shorts in skin? no: legs are skin 2/3/4; D = 13 outlines the shoes
29   ...DCCCDDCCCD...   shoes C = 12 ramp C mid
30   ....DDD..DDD....   soles D = 13, standing on row 30
```

Count the pure black: 8 pixels, all eyes. Count the ramps: skin 1/2/3/4, ramp B 8/9/10, ramp C
12/13, white. That is the recipe.

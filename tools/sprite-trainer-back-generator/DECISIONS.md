# sprite-trainer-back-generator: decisions and why

Read before changing the tool; add new ones at the bottom (decision + reason).

## D1. Standalone, copied from the front-pic tool (2026-11-01)

As every art tool (front tool D10): its own package, corpus, art and output. `palette.py`,
`metrics.py` and `rig.py` are copies of `sprite-trainer-generator`'s, so the same layer
vocabulary works on both and a spec author learns it once.

## D2. Back pics are repaints of vanilla back pics (2026-11-01)

The front tool's D8/D9 carry over: shape-built figures were rated "about 70%", repaints of a
close vanilla pic "perfect". The four vanilla throws are the only back-view throwing
animations there are, and each of our four back pics has an exact vanilla counterpart
(player boy, player girl, Wally, Steven), so every back pic repaints its own vanilla strip.
One remap covers all four frames, and because the vanilla head is the same drawing moved per
frame (`shifts`), head edits are written once with a per-frame `shift`.

## D3. Front and back share one palette, index for index (2026-11-01)

Found in the game, not chosen: `back_pic_tables.h` gives each back pic the front pic's palette
symbol, built from `graphics/trainers/palettes/<name>.pal` (Brendan, May, Wally) or from the
front pic PNG (Steven). So the back spec carries the front spec's `palette` and `legend`
unchanged, `build` errors on a mismatch with the paired front, and `install` writes the
`.pal` where there is one. The front tool's `install` writes the same `.pal` (its own README).

## Round 1 (2026-11-01)

Kael and Mira (the walker look: Kael's blue headband with knot tails and sand tunic, Mira's
rust-wrapped buns and headwrap with a rust tabard), Luke (matching the approved Luke front:
blond, spike trimmed, white tunic) and Leia (Steven's big hair trimmed to a smaller head with a
coiled side bun, black suit -> white gown). With new front pics for Kael and Mira. Sheets
`output/round1-backs.png`, `output/round1-throws.gif`. Awaiting the owner's review.

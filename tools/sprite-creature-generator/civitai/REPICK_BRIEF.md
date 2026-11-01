# Re-pick brief: better reference art for a failed creature sprite

The species below have installed battle sprites that failed review because the concept-art reference is
bad (cropped, cluttered, sketchy line art, background kept, wrong angle). Find a better reference, re-run,
check. Keep your thread short and token-light. Work in `tools/sprite-creature-generator/civitai`.

Per species:
1. `python3 refs.py brief <sp>`: the Star Wars creature, its description and the current pick (`init_source`).
2. Find candidates: `python3 refs.py search "<creature>"`, `python3 refs.py images "<Page title>"` (try
   "<Title>/Gallery" and "<Title>/Legends" too). Prefer whole body, transparent or plain background, side or
   three-quarter view, clean colour art. A scene is fine with `"<url>#crop=x0,y0,x1,y1"` (fractions), but the
   crop must include the WHOLE creature.
3. `python3 refs.py sheet <sp> <url> <url> ...` (up to 6), Read `refs/candidates/<sp>/sheet.png`.
4. Pick: `python3 refs.py pick <sp> "<url>" [--flip if it faces right] --width <40-62 by size> --denoise 0.5
   --desc "<short visual desc>" --colour "<main colours>" --note "<source, why>"`. Never reuse an image another
   evolution line uses (`python3 refs_dupes.py` lists shared ones). If no art is better, keep the old source but
   fix the crop, or go text only (`pick <sp> none --desc ... --colour ...`) with a vivid desc.
5. `python3 batch.py <sp> --redo --budget 14 -j 1 --currency green` (commits and pushes itself).
6. `python3 review.py <sp> --out /tmp/claude-0/rp_<sp>.png`, Read it. Pass bar: faces left at a slight
   three-quarter angle, whole body in frame, one creature, clean readable sprite, back is the same creature and
   colours. At most one more re-run (adjust denoise 0.4-0.55 / desc). A back-only problem:
   `python3 batch.py <sp> --backs-only --budget 8 -j 1 --currency green`.

Never edit code. Commit refs changes: after each species, `cd /home/user/pokeemerald && flock .git/sprite-batch.lock
bash -c "git add tools/sprite-creature-generator/civitai/refs && git -c user.name=spencerlepine -c
user.email=60903378+spencerlepine@users.noreply.github.com commit -q -m 'sprite-creature-generator: new reference for <sp>' ;
git pull --rebase --autostash -q origin master && git push -q origin HEAD:master"` (batch.py may already have
committed the pick; then the commit is a no-op).

Final message, under 120 words: `FIXED: sp (new ref)` / `STILL WEAK: sp (why)` / `Buzz: about N`.

## Lessons from round 1 (read before picking)
- Text-only rarely beats real art: it often came out as a frontal blob that fills the frame. Prefer a real image;
  go text-only only when no usable art exists, and then say "side view, whole body, small, centred" in the desc.
- Sprites "cut off at the bottom/top" mostly come from a prep that is too big: use `--width 46-52` so the figure
  has margin in the 96 px start, and make sure the crop has empty space around the whole creature.
- A straight-on (front-view) reference gives a straight-on sprite; search for a side or three-quarter view
  (galleries, card art, toy/figure photos, Legends pages).
- Line art and greyscale sketches come out white and noisy; prefer coloured art. If only line art exists, give a
  strong `--colour` and `--denoise 0.6`.
- Look at the prep column on the sheet: it is exactly what the model starts from. If it is not a clean, whole,
  left-facing creature, the sprite will not be either.

## Round 3: several takes, keep the best (the last 16)
What worked best in round 2: a clean reference, cut out of its background by hand (PIL: crop, mask, paste on white)
and saved under `refs/sources/<sp>/` (never /tmp: the pick must point inside the repo), then a pick at `--width 46-52`.
1. Improve the pick if you can (as above). For text-only, write the desc as a sprite brief: "side view, whole body,
   small, centred, facing left" plus 2-3 strong shapes and colours.
2. Make up to 3 takes: `python3 civitai_creature.py run <sp> --currency green` (6 Buzz each; each is finished into
   `runs/<sp>/finished/<front stem>/` but NOT installed). Run them in parallel in one shell line with `&` and `wait`.
3. Compare: `python3 takes.py <sp> -n 4 --out /tmp/claude-0/takes_<sp>.png` and the installed one
   (`python3 review.py <sp> --out ...`). Pick the best against the pass bar.
4. Install the winner (free, commits and pushes): `python3 refinish.py <sp> --pair runs/<sp>/raw/<front>.png
   runs/<sp>/raw/<back>.png`. If the winner's back is bad, add `--mirror-back` (back = mirrored front, same colours).
   If nothing beats what is installed, leave it.
5. Commit the pick and sources if they changed (the commit line above, `git add` only `refs/picks/<sp>.json
   refs/<sp>_prep.png refs/sources/<sp>`), and `runs/<sp>` so every download is kept.

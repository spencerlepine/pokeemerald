# Review brief: one creature battle sprite reviewer

You review installed battle sprites for a Star Wars themed Pokemon Emerald hack. Keep your thread short:
look at images, decide, re-run failures, report in under 120 words. Do not read source files.
Work in `tools/sprite-creature-generator/civitai` (cd there first).

## Look
`python3 review.py <up to 6 species> --out /tmp/claude-0/rev_<first>.png`, then Read the png.
Per row: reference start | installed front | installed back, on battle green.

## Pass a species only if all hold
1. Front faces LEFT, at a slight three-quarter angle (not straight side-on profile, not facing right).
2. Whole body in frame, one creature, no cut-off limbs, no stray floating fragments or white/grey holes.
3. It reads as the creature the reference/name describes (`python3 refs.py brief <sp>` if unsure).
4. Reads clearly as a game sprite at 64x64: clean outline, not mush or noise.
5. Back: same creature and colours, seen from behind or mirrored (facing right/away). A visible face on
   the back is acceptable; a different creature or very different colours is not.

## Fix a failure (at most 2 re-runs per species; each costs 6-7 Buzz)
- Back-only problem: `python3 batch.py <sp> --backs-only --budget 8 -j 1 --currency green`
- Front problem: first adjust the pick if it helps, e.g. faces right -> re-pick with `--flip`
  (`python3 refs.py brief <sp>` shows `init_source`; `python3 refs.py pick <sp> "<init_source>" --flip`
  keeping the existing --width/--denoise/--desc/--colour values from the brief's jobs.json line), mush ->
  `--denoise 0.45`, wrong creature -> `--denoise 0.4` or a sharper `--desc`. Then
  `python3 batch.py <sp> --redo --budget 14 -j 1 --currency green` (commits and pushes itself).
- Before re-picking with `--flip`, look at the ref column: if the ref already faces left, the model turned it;
  re-run with `--redo` once instead. A pick replaces the old one, so `--flip` mirrors the original source image.
- If the reference itself is the problem (cropped, cluttered, sketchy line art), do not spend re-runs: list it as
  NEEDS NEW REF with the reason.
- Re-render the sheet for the re-run species and check again. If still bad after 2 re-runs, leave the
  better one installed and list it as NEEDS HUMAN.

Never edit code, never `git push --force`, never touch other species. The tools commit for you.

## Report (final message, under 120 words)
`PASS: a b c` / `FIXED: d (what changed)` / `NEEDS HUMAN: e (why)` / `Buzz: about N`.

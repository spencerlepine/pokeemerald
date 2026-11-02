# sprite-creature-footprint-generator

Companion Datapad footprints (category A4): a 16x16, 1-bit print on each Datapad entry. **Engine: Python**,
no image model.

```sh
python3 footprint.py treecko mudkip --out out   # a few
python3 footprint.py --all --out out            # every footprint row in the wiki (386)
python3 footprint.py --sheet types.png          # every foot type at 3 sizes, for review
```

## How a print is made

1. `feet.csv` gives each species a foot type, picked by hand from its Star Wars brief (`note` says why when
   it isn't obvious). Change a row there to change a print.
2. The size comes from the creature's approved battle front (bigger front, bigger print, scale 0.5-1.0).
3. Organic prints (`paw`, `hoof`, `round`, `foot`, `hand`) are hand-drawn pixel grids in `grids.py`, at sizes
   S, M and L. The rest (`claw`, `talon`, `webbed`, `bug`, `spider`, `droid`, `tread`, `wheel`, `root`,
   `slime`, `suction`) are drawn from shapes on a 16-unit grid in `footprint.py`, supersampled 8x and
   thresholded. `none` is a blank print (floaters, fish, serpents, flyers that never land); 115 species.
4. Saved as a 1-bit indexed PNG with the vanilla palette (white paper, grey ink), then `palette-enforcer`
   `check --bpp 1`.

| Type | For |
|---|---|
| paw | dogs, cats, foxes, rodents, tookas |
| claw | lizards, crocodiles, dragons, krayts, dewbacks, tauntauns |
| talon | birds and fowl |
| webbed | amphibians, swamp ducks, worrts, porgs |
| hoof | banthas' cousins with split hooves: nerfs, shaaks, eopies, fawns, reeks |
| round | heavy padded feet: banthas, rontos, turtles, sando |
| foot | two-legged walkers with bare feet |
| hand | knuckle-walkers: gundarks, rancors, mogus, monkey-lizards |
| bug, spider | insects (leg dots); spider and crab droids (spikes) |
| droid, tread, wheel | battle and protocol droids; astromechs and tank droids; mouse droids and droidekas |
| root, slime, suction | walking plants; slugs and sludge; tentacles |

## Outputs

`out/graphics/pokemon/<species>/footprint.png` (git-ignored), copied to `../../wiki/art/` and listed in
`../../wiki/mapping/art_ready.csv` (386 rows, ART_READY on 2026-11-02). The `question_mark` placeholder print
is kept vanilla (`keep`).

## Install (not done yet)

Copy each `footprint.png` into `../../game/graphics/pokemon/<species>/`; `footprint_table.h` needs no change.
Then set `game_status` DONE.

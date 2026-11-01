# Move effects concept (2026-11-01)

Status: **approved by the owner on 2026-11-01** (direction, storyboards, renames, first chunk). Applied to
`mapping/moves.csv`, `mapping/vfx.csv` and `mapping/audio.csv` the same day (section 7 lists every sound). The game
is unchanged until each chunk ships. Tool: `tools/vfx-generator/`.

## 0. What went wrong so far

The first batches of the VFX tool swapped a prop for another prop (coin → credit chip, pencil → stylus) and
kept the Pokémon choreography. That is a sticker, not an effect. Emerald's good animations are *staged*:
HYPER BEAM dims the arena, shakes the attacker, loops a rising sound, fires 26 waves of orbs, blinds the
target white, and restores the lights. THUNDER inverts the whole screen four times. CRUNCH fades to a dark
backdrop before the jaws close. The prop is the least important part.

So this document audits the moveset first and designs each effect as a **storyboard**: wind-up, delivery,
impact, aftermath, with its sound. Art is drawn last, and only the art the storyboard needs.

## 1. Rules for every effect

1. **Four beats.** Wind-up (the attacker does something, 10-30 frames), delivery (the thing crosses the
   screen), impact (the target reacts: shake, flash, slide, fall), aftermath (smoke, scorch, lights back up).
   A 40-power jab gets two short beats; a 150-power signature gets all four and 120+ frames.
2. **The arena reacts.** Big moves dim the backdrop (`simple_palette_blend` on `F_PAL_BG`), shake the ground
   (`AnimTask_HorizontalShake` of both platforms), invert the screen for a frame (`invert_screen_color`) or
   swap the backdrop (`fadetobg`). Emerald does this on ~60 moves; we do it on every signature move.
3. **The bodies react.** Targets shake (`ShakeMon`, `ShakeMonInPlace`, `ShakeTargetInPattern`), slide
   (`TranslateMonElliptical`), lift, squash (`ScaleMonAndRestore`, `StretchTargetUp`), flash white
   (`BlendMonInAndOut`), go grey (`set_grayscale_pal`), leave afterimages (`TraceMonBlended`). Attackers
   lunge (`WindUpLunge`), rear up (`RotateMonSpriteToSide`), rise (`TranslateMonElliptical` up).
4. **Sound is half the effect.** Every beat has an SE with pan (`playsewithpan`, `loopsewithpan`,
   `createsoundtask` for a looped sweep from attacker to target). `sfx-generator` already shipped
   SE_BLASTER_BOLT, SE_SABER_IGNITE, SE_SABER_HUM, SE_HYPERSPACE_JUMP, SE_VADER_BREATH, SE_ASTROMECH_CHATTER;
   SE_FORCE_PUSH, SE_FORCE_LIGHTNING, SE_FORCE_CHOKE, SE_SABER_SWING, SE_SABER_CLASH, SE_ION_CANNON,
   SE_TURBOLASER, SE_VIBROBLADE, SE_SLICER_SPIKE are mapped and specced but not made.
5. **Three visual languages**, so the player reads a move before the text box does:
   - **The Force** (FORCE type, 28 moves): no projectiles. Pressure, lift, ripple, afterimage. Light side is
     blue-white with a cold ring; dark side is red-violet with a black vignette. One new backdrop,
     `BG_FORCE`, replaces `BG_PSYCHIC` and re-skins 17 moves in one go.
   - **Tech** (blasters, ion, turbolaser, droid repair, scanners): hard edges, muzzle flash, red/green
     bolts, HUD brackets, sparks, astromech chirps.
   - **Beasts** (fire, water, claws, bites, roars, powders): **Emerald's own animations stay.** A massiff
     biting is a massiff biting. These are ~230 moves and they are already good.
6. **Names fit in 12 characters** (`MOVE_NAME_LENGTH`), stats, types and effects never change (HOTSWAP rule).

## 2. The engine's toolbox (no new art needed)

| Trick | Script / task | Used by (vanilla) |
|---|---|---|
| Dim or tint the backdrop | `simple_palette_blend selector=F_PAL_BG` / `complex_palette_blend` | HYPER BEAM, SHOCK WAVE, FRENZY PLANT |
| Dim or tint one battler | `AnimTask_BlendBattleAnimPal F_PAL_TARGET`, `blend_color_cycle` | HYPER BEAM impact, PSYCHIC wind-up |
| Invert the screen for N frames | `invert_screen_color` | THUNDER |
| White-out | `AnimTask_BlendBattleAnimPal F_PAL_BG ... RGB_WHITE`, `AnimTask_FadeScreenToWhite` | EXPLOSION, SELF-DESTRUCT |
| Swap the backdrop (with a scrolling one) | `fadetobg BG_X` + `AnimTask_StartSlidingBg` | THUNDER, EXTREME SPEED (high-speed streaks), COSMIC POWER |
| Shake the whole arena | `AnimTask_HorizontalShake` ×2 (platforms + battlers) | EARTHQUAKE, MAGNITUDE |
| Shake a battler (various) | `ShakeMon`, `ShakeMon2`, `ShakeMonInPlace`, `ShakeTargetInPattern`, `ShakeTargetBasedOnMovePowerOrDmg` | 300+ moves |
| Slide / lift / orbit a battler | `TranslateMonElliptical(RespectSide)`, `StretchTargetUp`, `SlideOffScreen` | SEISMIC TOSS, SKY UPPERCUT, FLY |
| Squash / grow a battler | `ScaleMonAndRestore`, `GrowAndShrink`, `SwitchOutShrinkMon` | PSYCHIC, GROWTH |
| Lean / spin a battler | `RotateMonSpriteToSide`, `RotateMonToSideAndRestore` | BIDE, ROLLOUT |
| Afterimages | `TraceMonBlended` | DOUBLE TEAM, AGILITY |
| Flash a battler white / colour | `BlendMonInAndOut`, `flash_anim_tag_with_color` | FORESIGHT, HYPER BEAM orbs |
| Grey out | `set_grayscale_pal` / `set_original_pal` | SKETCH |
| Lunge | `WindUpLunge` | TACKLE family |
| Alpha-blended sprites | `monbg` + `setalpha` | most beam moves |
| Hitsplats (4 kinds) | `create_basic_hitsplat_sprite` etc. | every contact move |
| Two-turn moves | `choosetwoturnanim`, `jumpifmoveturn` | SKY ATTACK, SKULL BASH, SOLAR BEAM |
| Looped, panned sound | `loopsewithpan`, `createsoundtask SoundTask_LoopSEAdjustPanning` | HYPER BEAM |

Hard limits to design inside: 2-3 spare sprite palettes during an animation (so a signature move gets at most
2-3 new sheets with their own palette; the rest must share or be recolours of vanilla tags), a 64-sprite OAM,
~16 KB of sprite VRAM free for animation tiles, backdrop swaps are one 240x160 tileset + 16-colour palette
each. New *tasks* (anything a `createvisualtask` line names) are C code; the list above is what exists today,
and it covers every storyboard below. Where a storyboard needs a new task it says so.

## 3. The audit

354 moves. 19 are HM/TM-only or special and keep their animation (CUT and STRENGTH are field moves too).

| Tier | Count | What | What we do |
|---|---|---|---|
| **S: signature** | 12 | The moves that *are* Star Wars: sabers, blasters, the Force, ion, turbolaser | Full storyboard, new script, 1-3 new sheets each, new SE |
| **A: the Force** | 28 | Every FORCE-type move | One shared backdrop + palette language; the 8 attacking ones get a short storyboard; status ones get a sound + tint pass |
| **B: Pokémon in-jokes** | 14 | Moves whose name or prop is a Pokémon gag (SKETCH, MILK DRINK, EGG BOMB, KINESIS, PAY DAY...) | Rename and re-stage, no prop swaps |
| **C: tech re-stage** | 9 | Moves droids use that read as magic today (CONVERSION, RECYCLE, LOCK-ON, BATON PASS...) | Rename where needed, re-stage with HUD / sparks / beams |
| **D: beasts** | ~290 | Everything else | Keep. Later polish pass on the 8 backdrop moves and the status animations |

### Tier S: signature storyboards

Frame counts are at 60 fps. "Shake 0,8,N" means `AnimTask_ShakeMon` with x=0, y=8, N frames.

#### S1. SABER SLASH (net-new, clone of SLASH, Normal 70)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Ignite | 0-18 | Backdrop dims to 60 %. A blade sprite (8x48, 3 frames extending) snaps out beside the attacker. **Blue when the attacker is on the player's side, red when it is the opponent's** (`jumpretfalse` on `AnimTask_IsTargetPlayerSide`, two palettes). | SE_SABER_IGNITE, then SE_SABER_HUM looping |
| Lunge | 18-30 | `WindUpLunge` pulls the attacker back 4 px then throws it 12 px toward the target. | hum continues |
| Slash | 30-38 | Two crossing glow arcs (64x64, 4 frames, alpha-blended) over the target; frame 2 of the arc inverts the screen for 1 frame. | SE_SABER_SWING |
| Impact | 38-60 | Target flashes white (BlendMonInAndOut), shakes 0,8,12; a scorch-mark sprite (32x16) sits on the target and fades over 20 frames. Hitsplat. | SE_M_RAZOR_WIND for the bite of the hit |
| Retract | 60-72 | Blade retracts (3 frames reversed), hum stops, backdrop restores. | hum stop, short SE_SABER_IGNITE tail |

New art: blade (2 palettes), arcs, scorch. 3 sheets. Reuses: hitsplat.

#### S2. BLASTER SHOT (net-new, clone of SWIFT, Normal 60, never misses)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Aim | 0-8 | A small HUD bracket (16x16, 2 frames) blinks on the target once. | SE_M_LOCK_ON-style chirp (reuse) |
| Fire ×5 | 8-48 | Every 8 frames: a muzzle flash (16x16, 2 frames) pops at the attacker's front and a red bolt (24x8, affine-rotated to the firing line) crosses in 10 frames. Bolts are offset ±6 px so they fan. | SE_BLASTER_BOLT per bolt |
| Impact ×5 | 18-58 | Each bolt ends in an impact spark (16x16, 3 frames) at a random point on the target; small shake 0,2,4 per hit; the last hit shakes 0,6,10. | SE_M_SWIFT hit (reuse) per impact |
| Aftermath | 58-70 | Three smoke puffs drift up from the target (reuse ANIM_TAG_SMOKE / "sMudSmoke" style), target tints 20 % black for 10 frames. | – |

New art: bolt + muzzle flash (one sheet), impact spark. 2 sheets. Also the overworld raid cutscenes reuse the bolt.

#### S3. FORCE PUSH (PSYCHIC, Force 90)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Gather | 0-24 | `fadetobg BG_FORCE` (new: deep indigo with a slow radial ripple scroll). The attacker rears (`RotateMonSpriteToSide` 8 px) and a cold-white ring (reuse ANIM_TAG_THIN_RING, tinted) shrinks onto it. | low wind-up (SE_M_PSYBEAM reversed feel: reuse SE_M_CHARGE) |
| Push | 24-40 | Three expanding rings leave the attacker toward the target, alpha 8/8, 6 frames apart. The arena shakes horizontally 2 px. | SE_FORCE_PUSH |
| Impact | 40-70 | Target slides back 20 px in 6 frames (`TranslateMonElliptical`), squashes to 90 % (`ScaleMonAndRestore`), two dust puffs at its feet (reuse mud/sand tag), shakes 0,6,20, then slides back to its spot over 20 frames. | SE_M_TAKE_DOWN thud |
| Settle | 70-90 | Backdrop restores. | – |

New art: `BG_FORCE` tileset + palette (used by all 17 Force moves). 1 asset. Rings, dust reused.

#### S4. FORCE CHOKE (net-new, clone of CRUNCH, Dark 80)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Reach | 0-20 | `fadetobg BG_FORCE`, then the backdrop tints red-black (dark side). The attacker leans in 6 px. | SE_FORCE_CHOKE (strained hum, loops) |
| Lift | 20-50 | Target rises 14 px over 30 frames (`TranslateMonElliptical` with a flat ellipse) and leans back 10°. A faint red grip ring (24x16, 2 frames, alpha) hovers at its neck. | hum |
| Squeeze | 50-90 | Target shakes in place (`ShakeMonInPlace` 1,0,40) and darkens 40 %; the grip ring pulses 3× (scale 1.0 → 0.8). Every pulse: 1-frame screen invert. | hum + 3 short SE_M_BIND squeezes |
| Drop | 90-110 | Grip ring vanishes, target falls back 14 px in 4 frames and shakes 0,8,8 (the floor hit), dust puffs. Backdrop restores. | SE_M_TAKE_DOWN thud, hum stops |

New art: grip ring. 1 sheet. New task: none (lift is an elliptical translate with ry=0). Vader's companions and
the dark-side Trials use this; it should feel wrong and strong.

#### S5. FORCE BOLT (SHOCK WAVE, Electric 60, never misses)

Force lightning from the fingertips. The vanilla SHOCK WAVE already does half of this (charging particles, a
growing orb, a progressing bolt, a flash on the target).

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Charge | 0-24 | `BG_FORCE` tinted red-black. Charging particles (vanilla task) collapse into the attacker. | SE_M_CHARGE |
| Arcs | 24-60 | Three blue-white forked arcs (new 64x32 sheet, 3 frames, replaces the single lightning sprite) fan from attacker to target, redrawn every 4 frames with a different frame so they crawl. Screen inverts for 1 frame at 24, 36, 48. | SE_FORCE_LIGHTNING loop |
| Impact | 60-84 | Target flashes white twice, shakes in pattern (`ShakeTargetInPattern` 30, 3), goes 50 % black for 12 frames, small sparks crawl on it (reuse ANIM_TAG_SPARK). | SE_M_TRI_ATTACK2 |
| Smoke | 84-100 | Two smoke wisps rise from the target. Backdrop restores. | – |

New art: forked arcs. 1 sheet.

#### S6. FORCE STORM (PSYCHO BOOST, Force 140, the biggest Force move)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Rise | 0-40 | `BG_FORCE` scrolling faster; the attacker rises 16 px and the arena shakes 1 px continuously. Debris sprites (reuse rock fragments and leaves) orbit the attacker (vanilla `AnimTask_... Orbit` tasks from PETAL DANCE / COSMIC POWER). | rising SE_M_COSMIC_POWER |
| Burst | 40-56 | Screen white-out 8 frames; a 64x64 shockwave (new, 4 frames) expands from the attacker; debris flies outward. | SE_M_EXPLOSION |
| Impact | 56-90 | Target thrown back 24 px, shakes 0,10,24, squashes to 85 %; the arena shakes 4 px. | SE_M_TAKE_DOWN |
| Fall | 90-120 | Attacker drops back 16 px (the recoil, matching the stat drop), backdrop restores slowly. | – |

New art: shockwave. 1 sheet.

#### S7. TURBOLASER (HYPER BEAM, Normal 150, recharge)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Charge | 0-50 | Backdrop to black (vanilla). Green energy gathers at the attacker: vanilla orbs tag, `flash_anim_tag_with_color` green instead of red. Attacker shakes 0,4,50. | SE_TURBOLASER charge (rising) |
| Fire | 50-110 | A green beam of 32x16 segments (new sheet, 2 frames alternating so it crackles) streams attacker → target, with a thin white core. The arena shakes 3 px for the whole burst. Target blinds to white (vanilla). | SE_TURBOLASER loop, panned |
| Impact | 70-110 | Explosion sprites (reuse ANIM_TAG_EXPLOSION) pop on the target every 6 frames; target shakes 0,6,50. | SE_M_EXPLOSION ×3 |
| Recharge | 110-130 | Beam stops, smoke on the target, lights up. | – |

New art: beam segments + core (one sheet, the existing `turbolaser.yaml` prototype). The current vanilla orb
stream is replaced, not reskinned, because `orbs.png` is shared by 12 moves.

#### S8. ION CANNON (ZAP CANNON, Electric 100, paralyses)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Charge | 0-20 | Blue sparks (vanilla spark tag, blue-tinted) gather at the attacker. | SE_M_THUNDER_WAVE (vanilla) |
| Shot | 20-50 | The ion orb (batch 1 art, kept) crosses with a trailing afterimage (two extra orbs at alpha). | SE_ION_CANNON |
| Ionise | 50-100 | Screen inverts 1 frame. Target flashes **blue-white 3×** (`BlendMonInAndOut` with RGB(20,28,31)), sparks crawl over it, it shakes in place 40 frames, then goes grey for 10 frames (ionised = disabled). | SE_M_THUNDERBOLT2 then a dying crackle |
| Fade | 100-116 | Colour returns. | – |

New art: none beyond batch 1. Script + sound only.

#### S9. MIND TRICK (CONFUSION, Force 50, confuses)

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Wave | 0-20 | `BG_FORCE`. The attacker sways once (`SwayMon`). | SE_M_CONFUSE_RAY |
| Doubt | 20-60 | A blended ghost copy of the target (`TraceMonBlended`) drifts 12 px left and snaps back, then right; the real target sways. The backdrop ripple speeds up. | soft SE_M_SUPERSONIC loop |
| Hit | 60-72 | Target shakes 0,4,8. Backdrop restores. | – |

New art: none. Script only.

#### S10. DETONATE (EXPLOSION, Normal 250) and SELF-DESTRUCT

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Arm | 0-60 (DETONATE) / 0-30 (SELF-DESTRUCT) | A thermal detonator (16x16, 2 frames: light off / on) drops from the attacker to its feet and bounces once. Its light blinks faster and faster. | 5 accelerating beeps (new SE_DETONATOR_BEEP, or reuse SE_PIN) |
| Boom | 60-120 | The vanilla explosion script runs unchanged (it is already great: red tint, 5 shakes, white-out). | vanilla |

New art: detonator. 1 sheet. Script: prepend the arm beat.

#### S11. TARGET LOCK (LOCK-ON) and MIND READER

| Beat | Frames | Screen | Sound |
|---|---|---|---|
| Scan | 0-40 | A Rebel targeting-computer box (the vanilla reticle redrawn as four HUD corner brackets, 2 frames) closes on the target from 1.5× to 1×; a horizontal scan line (alpha bar, 64x4) sweeps the target top to bottom. | 3 slow comlink chirps (SE_COMLINK_CALL swap) |
| Lock | 40-60 | Brackets turn red and flash 3×; target flashes white once. | one high lock tone (SE_M_LOCK_ON) |

New art: brackets + scan line. 1 sheet.

#### S12. VIBROBLADE (CUT, Normal 50) and SELF REPAIR (SOFT-BOILED, heals)

- **VIBROBLADE:** the cut slice becomes a buzzing blade streak (32x32, 3 frames with motion blur). Two quick
  strokes 6 frames apart, each with a 1-frame screen shake of 1 px, target shakes 0,3,10. SE_VIBROBLADE.
  New art: streak. 1 sheet.
- **SELF REPAIR** (FX-6 / 2-1B medical droids, so this is the *droid* heal): the attacker greys out 20 %
  (powered down), a welding-arm sprite (24x24, 2 frames) taps three points on it with spark bursts (reuse
  ANIM_TAG_SPARK), then colour floods back (`set_original_pal`) with the vanilla blue healing ring.
  SE_ASTROMECH_CHATTER then SE_M_RECOVER... vanilla `HealingEffect2`. New art: arm. 1 sheet.

### Tier A: the Force (28 moves)

One shared language, applied in one pass once `BG_FORCE` exists:

- **Backdrop:** every move that calls `SetPsychicBackground` (15 scripts: PSYCHIC, PSYBEAM, CONFUSION,
  KINESIS, TELEPORT, HYPNOSIS, AGILITY, MEDITATE, BARRIER, REFLECT, LIGHT SCREEN, AMNESIA, DREAM EATER,
  MIRROR COAT, CALM MIND...) plus LUSTER PURGE and PSYCHO BOOST switches to `BG_FORCE`.
- **Side:** light-side moves tint the backdrop blue; dark-side moves (FORCE CHOKE, FORCE BOLT, FORCE STORM,
  BOGAN PURGE, NIGHTMARE, DREAM EATER) tint it red-black.
- **Sound:** a Force "hum" family from `sfx-generator` (SE_FORCE_PUSH exists as a spec; add SE_FORCE_HUM, a
  short rising tone, for every status Force move so they stop using SE_M_PSYBEAM).

| Move | Now | Then |
|---|---|---|
| FORCE WAVE (psybeam) | rainbow beam | a blue pulse train (vanilla psybeam rings recoloured), target sways |
| FORCE PULSE (psywave) | orbiting orbs | three afterimages of the attacker fan out and collapse into the target |
| FORCE SENSE (extrasensory) | distortion | the vanilla distortion task, blue tint, plus the target flinch shake |
| FORCE VISION (future sight) | eye | a translucent copy of the target (`TraceMonBlended`) hangs 8 px above it, then snaps down (the vision hit script `General_FutureSightHit` gets the Force burst) |
| FORCE FOCUS (psych-up) | glow | attacker rises 4 px, afterimage, blue ring |
| TELEKINESIS (kinesis) | bent spoon + stars | **no object**: the target lifts 8 px, wobbles (`SwayMon`), and drops (accuracy down) |
| ASHLA MIST / BOGAN PURGE (latias / latios) | mist ball / luster purge | keep the vanilla shapes, blue (ASHLA) and red-violet (BOGAN) palettes, `BG_FORCE` |
| MIRROR COAT, BARRIER, REFLECT, LIGHT SCREEN | vanilla | vanilla with the blue tint and the hum |
| TELEPORT | vanilla | add a 1-frame screen invert and SE_HYPERSPACE_JUMP (short) |
| HYPNOSIS, MEDITATE, AGILITY, AMNESIA, CALM MIND, COSMIC POWER, REST, TRICK, ROLE PLAY, SKILL SWAP, IMPRISON, MAGIC COAT, DREAM EATER | vanilla | vanilla, backdrop + tint + hum only |

### Tier B: Pokémon in-jokes (14 moves)

The question for each: is it a creature behaviour (keep) or a Pokémon gag (fix)?

| Move | Learned by | Problem | Proposal (≤12 chars) | Effect |
|---|---|---|---|---|
| SKETCH | PAINTKIT (smeargle) only, level 1 | A painter copying a move with a pencil | **HOLOSCAN** | A blue scan line sweeps the target, which greys out briefly; a hologram copy of it (`TraceMonBlended`, blue) materialises next to the attacker and dissolves. SE_ASTROMECH_CHATTER. (Suggest recasting PAINTKIT as a probe droid; the owner's call, out of this doc's scope.) |
| MILK DRINK | SHAAK (miltank) + egg moves | Moomoo milk | **GRAZE** (applied; BLUE MILK stays as the alternative) | The shaak dips its head twice (`RotateMonSpriteToSide` down), chomp shake, a green sprout puff; then the vanilla heal ring. SE_M_BITE ×2, vanilla heal. No jug. (Alternative: keep **BLUE MILK** with the same staging, no jug.) |
| SOFT-BOILED | FX-6 / 2-1B units (chansey line) | an egg | **SELF REPAIR** (already mapped) | Tier S12 |
| EGG BOMB | WROSHYR (exeggutor), LUCKEGG line | a thrown egg | **SEED BOMB** (already mapped) | Lob a seed pod (16x16, the vanilla egg redrawn green) in a high arc; the vanilla 5-explosion impact stays |
| PAY DAY | TUSKCAT (meowth) | coins | **CREDIT TOSS** (already mapped) | Batch 1 chips are fine *as the prop*; the staging adds a sharper throw (3 chips fanned) and a credit-counter chime (SE_M_PAY_DAY stays) |
| KINESIS | MISTWEAVER / MISTSAGE (kadabra line) | bent spoon | **TELEKINESIS** (already mapped) | Tier A |
| FORESIGHT / ODOR SLEUTH | 10+ lines | magnifying glass | **AURA SIGHT** / keep ODOR SLEUTH | Tier S11's scan line over the target, then the target flashes white; no object. ODOR SLEUTH keeps its sniff (a beast). |
| BATON PASS | 6 lines | a Poké Ball flies off | keep name | The capture-pod recall beam: the attacker is drawn up in a white beam (reuse the vanilla pod-return effect, `Special_SwitchOutPlayerMon`), pod sprite = batch 1 **capture pod** (sheet `sprites/pokeball.png`) |
| METRONOME | 20+ lines | finger wag | keep name | Replace the finger with a spinning sabacc dial (16x16, 4 frames) and the thought bubble; SE_M_METRONOME stays |
| CONVERSION / CONVERSION 2 | 3PO / TC units (porygon line) | type change | **RECONFIGURE** / **COUNTERCODE** | The droid greys out, a column of green data glyphs (8x8 tiles scrolling, new sheet) runs down it, colour floods back in the new type's tint. SE_ASTROMECH_CHATTER |
| TRANSFORM | SHIFTBLOB (ditto) | – | keep | vanilla (it is a shapeshifter) |
| SPLASH | COLOFRY (magikarp) | – | keep (**FLOP** optional) | vanilla |
| SWEET KISS / LOVELY KISS / ATTRACT / CHARM | many | hearts | keep | kid-friendly creature behaviour; vanilla |
| BELLY DRUM / TEETER DANCE / SWORDS DANCE | many | – | keep | Wookiee-style chest beats are exactly right; vanilla |

### Tier C: tech re-stage (9 moves)

| Move | Learned by | Then |
|---|---|---|
| LOCK-ON → TARGET LOCK, MIND READER | droids, VULTURE | Tier S11 |
| RECYCLE | droids, scavengers | A small cargo-crate icon? No: the attacker sparks once and a green "OK" tick HUD (8x8) pops; SE_ASTROMECH_CHATTER |
| CHARGE | electric droids and beasts | vanilla particles, add a rising capacitor whine (SE_M_CHARGE stays) and a 1-frame invert at the end |
| SONIC BLAST (sonic boom) | VULTURE, CACKLER | vanilla rings, add the arena shake 2 px |
| SIGNAL BEAM | droids, bugs | vanilla, no change |
| TRI ATTACK | 3PO unit, GONK | vanilla (three elements), no change |
| SUBSTITUTE (General_Substitute*) | many | **HOLO-DECOY**: the substitute doll becomes a flickering blue hologram silhouette on a projector disc (sheet `substitute.png` front + back, 32x32 ×2, alpha-blended by the existing substitute code; flicker = 2-frame anim). SE_M_ATTRACT → SE_ASTROMECH_CHATTER |
| Special_BallThrow / capture | – | the **capture pod** art and SE_POD_* swaps are the icon tool's and sfx tool's rows; the throw script stays |
| SWITCH OUT / SEND OUT | – | pod beam stays; pod art from the icon tool |

### Tier D: beasts (keep)

Everything else keeps Emerald's animation. Optional later polish, in this order: the 8 BG_GHOST moves get a
"SPIRIT" backdrop (the Force-ghost shimmer: the vanilla ghost backdrop recoloured blue-green), SACRED FIRE /
BLAST BURN / HYDRO CANNON / FRENZY PLANT get the arena shake, and the status animations (poison, burn,
paralysis, sleep, freeze, confusion) get an SE pass.

## 4. The three art languages, measured

So the drawn sheets stay consistent across chunks:

| Language | Palette ramps (`PALETTE.md` themes) | Edge | Motion |
|---|---|---|---|
| Force, light | `kyber-blue` whites → `#58C8F8` → `#2878D8`, rims in `#183888` | soft (alpha-blended rings), no black | slow in, snap out |
| Force, dark | `#F8E0F8` → `#D040A0` → `#701060`, rims `#280838` | soft, black vignette on the backdrop | slow, pulsing |
| Saber | blade core `#F8F8F8`, blue `#60B0FF` / red `#FF4040`, glow halo at alpha 8/8 | hard core, soft halo | 3-frame extend, arcs 4 frames |
| Blaster / tech | bolt red `#FF3020` core `#FFE0C0`; green for TURBOLASER `#40FF60` core `#E0FFE0`; HUD `#40E0FF` | hard | fast (8-10 frame crossings) |
| Smoke / scorch | the vanilla `mud_sand` greys, scorch `#282020` | – | fade over 20 frames |

## 5. What the tool must grow

Today `vfx-generator` draws sheets. For storyboards it needs, in order:

1. **`script` layer:** a storyboard YAML (beats → script lines) that emits a `Move_X:` block for
   `data/battle_anim_scripts.s` with validated macro names and arguments, and a `patch` command that replaces
   the block in place (and adds the `.4byte` entry for a net-new move). Reuses the existing tag plumbing for
   new sheets (the 104 never-loaded tags are free slots).
2. **SE hooks:** `sfx-generator` makes the missing SEs (SE_FORCE_PUSH, SE_FORCE_LIGHTNING, SE_FORCE_CHOKE,
   SE_SABER_SWING, SE_ION_CANNON, SE_TURBOLASER, SE_VIBROBLADE, +SE_FORCE_HUM, SE_DETONATOR_BEEP); the script
   layer refuses an SE constant that does not exist in `songs.h`.
3. **`BG_FORCE`:** one backdrop tileset + palette + the `gBattleAnimBackgroundTable` entry (same plumbing as
   `BG_THUNDER`).
4. **ROM filming stays the judge.** The mock-up preview is dropped for storyboards: the real thing takes 4
   minutes per move and shows every blend, shake and sound.
5. **Chunks of 3**, each: storyboard → script + art + SE → ROM film → review GIF for the owner → approve →
   install into `game/` and the wiki.

## 6. Proposed first chunk

**SABER SLASH, BLASTER SHOT, FORCE PUSH.** One of each language, and together they build everything the rest
needs: new sheets with new tags (saber), affine projectiles and multi-hit timing (blaster), `BG_FORCE` and
battler motion (push), three SEs, and the script layer itself. Chunk 2: FORCE CHOKE, FORCE BOLT, TURBOLASER.
Chunk 3: ION CANNON, DETONATE, TARGET LOCK. Chunk 4: the Tier A pass and the Tier B renames.

Batch 1 and 2 art: the ion orb, credit chips and the capture pod stay as props inside their storyboards; the
milk jug, macrobinoculars and stylus are scrapped (their specs move to `art/rejected/`).

## 7. Sound audit (every effect's sounds, with their wiki rows)

Generated from `mapping/moves.csv` (the `SE:` list in each note) and `mapping/audio.csv`. **Vanilla** = an Emerald SE that
already exists and is kept (a hot-swapped one is shown with its Emerald row); **net-new** = a `net:se-*` row in
`mapping/audio.csv` for `sfx-generator` to make (status in `database/pending_audio.csv`). No effect uses a sound outside
these two columns.

| Move | Vanilla SEs (kept) | Net-new SEs (wiki row) |
|---|---|---|
| AGILITY | – | SE_FORCE_HUM (`net:se-force-hum`) |
| AMNESIA | – | SE_FORCE_HUM (`net:se-force-hum`) |
| ASHLA MIST | SE_M_HAZE | SE_FORCE_HUM (`net:se-force-hum`) |
| AURA SIGHT | SE_M_DETECT | SE_HOLOSCAN (`net:se-holoscan`) |
| BARRIER | – | SE_FORCE_HUM (`net:se-force-hum`) |
| BATON PASS | SE_POD_THROW (`audio:SE_BALL_THROW`), SE_M_BATON_PASS | – |
| BLASTER SHOT | – | SE_TARGET_LOCK (`net:se-target-lock`), SE_BLASTER_BOLT (`net:se-blaster-bolt`), SE_BLASTER_IMPACT (`net:se-blaster-impact`) |
| BOGAN PURGE | SE_M_PSYBEAM | SE_FORCE_HUM (`net:se-force-hum`) |
| CALM MIND | – | SE_FORCE_HUM (`net:se-force-hum`) |
| CHARGE | SE_M_CHARGE | – |
| COSMIC POWER | – | SE_FORCE_HUM (`net:se-force-hum`) |
| COUNTERCODE | – | SE_HOLOSCAN (`net:se-holoscan`), SE_ASTROMECH_CHATTER (`net:se-astromech`) |
| CREDIT TOSS | SE_M_RAZOR_WIND2, SE_M_PAY_DAY | – |
| DETONATE | SE_M_EXPLOSION | SE_DETONATOR_BEEP (`net:se-detonator-beep`) |
| DREAM EATER | – | SE_FORCE_HUM (`net:se-force-hum`) |
| FORCE BOLT | SE_M_CHARGE, SE_M_TRI_ATTACK2 | SE_FORCE_LIGHTNING (`net:se-force-lightning`) |
| FORCE CHOKE | SE_M_BIND, SE_M_TAKE_DOWN | SE_FORCE_CHOKE (`net:se-force-choke`) |
| FORCE FOCUS | – | SE_FORCE_HUM (`net:se-force-hum`) |
| FORCE PULSE | – | SE_FORCE_HUM (`net:se-force-hum`) |
| FORCE PUSH | SE_M_CHARGE, SE_M_TAKE_DOWN | SE_FORCE_PUSH (`net:se-force-push`) |
| FORCE SENSE | – | SE_FORCE_HUM (`net:se-force-hum`) |
| FORCE STORM | SE_M_EXPLOSION, SE_M_TAKE_DOWN | SE_FORCE_STORM (`net:se-force-storm`) |
| FORCE VISION | – | SE_FORCE_HUM (`net:se-force-hum`) |
| FORCE WAVE | SE_M_PSYBEAM | SE_FORCE_HUM (`net:se-force-hum`) |
| GRAZE | SE_M_BITE, SE_M_MILK_DRINK | – |
| HOLOSCAN | – | SE_HOLOSCAN (`net:se-holoscan`), SE_ASTROMECH_CHATTER (`net:se-astromech`) |
| HYPNOSIS | – | SE_FORCE_HUM (`net:se-force-hum`) |
| IMPRISON | – | SE_FORCE_HUM (`net:se-force-hum`) |
| ION CANNON | SE_M_THUNDER_WAVE, SE_M_THUNDERBOLT2 | SE_ION_CANNON (`net:se-ion-cannon`) |
| LIGHT SCREEN | – | SE_FORCE_HUM (`net:se-force-hum`) |
| MAGIC COAT | – | SE_FORCE_HUM (`net:se-force-hum`) |
| MEDITATE | – | SE_FORCE_HUM (`net:se-force-hum`) |
| METRONOME | SE_M_METRONOME | – |
| MIND READER | SE_M_LOCK_ON | SE_TARGET_LOCK (`net:se-target-lock`) |
| MIND TRICK | SE_M_CONFUSE_RAY, SE_M_SUPERSONIC | SE_FORCE_HUM (`net:se-force-hum`) |
| MIRROR COAT | – | SE_FORCE_HUM (`net:se-force-hum`) |
| NIGHTMARE | – | SE_FORCE_HUM (`net:se-force-hum`) |
| RECONFIGURE | – | SE_HOLOSCAN (`net:se-holoscan`), SE_ASTROMECH_CHATTER (`net:se-astromech`) |
| RECYCLE | – | SE_ASTROMECH_CHATTER (`net:se-astromech`) |
| REFLECT | – | SE_FORCE_HUM (`net:se-force-hum`) |
| REST | – | SE_FORCE_HUM (`net:se-force-hum`) |
| ROLE PLAY | – | SE_FORCE_HUM (`net:se-force-hum`) |
| SABER SLASH | SE_M_RAZOR_WIND | SE_SABER_IGNITE (`net:se-saber-ignite`), SE_SABER_HUM (`net:se-saber-hum`), SE_SABER_SWING (`net:se-saber-swing`), SE_SABER_RETRACT (`net:se-saber-retract`) |
| SEED BOMB | SE_M_TAIL_WHIP, SE_M_SELF_DESTRUCT | – |
| SELF DESTRUCT | SE_M_SELF_DESTRUCT | SE_DETONATOR_BEEP (`net:se-detonator-beep`) |
| SELF REPAIR | SE_M_MILK_DRINK | SE_ASTROMECH_CHATTER (`net:se-astromech`), SE_WELD_SPARK (`net:se-weld-spark`) |
| SKILL SWAP | – | SE_FORCE_HUM (`net:se-force-hum`) |
| SONIC BLAST | SE_M_SUPERSONIC | – |
| SUBSTITUTE | – | SE_HOLO_FLICKER (`net:se-holo-flicker`) |
| TARGET LOCK | SE_M_LOCK_ON | SE_TARGET_LOCK (`net:se-target-lock`) |
| TELEKINESIS | – | SE_FORCE_HUM (`net:se-force-hum`) |
| TELEPORT | SE_M_TELEPORT | SE_HYPERSPACE_JUMP (`net:se-hyperspace-jump`) |
| TRICK | – | SE_FORCE_HUM (`net:se-force-hum`) |
| TURBOLASER | SE_M_EXPLOSION | SE_TURBOLASER_CHARGE (`net:se-turbolaser-charge`), SE_TURBOLASER (`net:se-turbolaser`) |
| VIBROBLADE | – | SE_VIBROBLADE (`net:se-vibroblade`) |

27 net-new SE rows in total (`net:se-*`): 6 are already made and installed by `sfx-generator` (SE_ASTROMECH_CHATTER,
SE_BLASTER_BOLT, SE_HYPERSPACE_JUMP, SE_SABER_HUM, SE_SABER_IGNITE, SE_VADER_BREATH); the rest are `NEEDS_PLACEHOLDER` for the
follow-up sound task. Overworld-only sounds (TIE flyby, alarm, slicer spike, saber clash) are in the same table but are not
move effects.

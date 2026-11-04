#!/usr/bin/env bash
# Screenshot the UI in the modern ROM (make modern), headless, one scenario per run.
#   scripts/ui-check.sh boot          # once: new game to the truck, saves out/ui/overworld.ss0
#   scripts/ui-check.sh sign_outer    # Sealed Vault outer room sign  -> out/ui/sign_outer.png
#   scripts/ui-check.sh sign_inner    # inner room "WE OWE ALL TO THE COMPANION" sign
#   scripts/ui-check.sh regirock      # also regice, registeel: 40 frames of the battle wipe
#   scripts/ui-check.sh tour          # party, items, flags; start menu, party, summary, bag, StarNAV, DATAPAD, card, save, options
#   scripts/ui-check.sh battle        # with a party: a wild battle's action menu
# Usage: scripts/ui-check.sh SCENARIO [timeout seconds]
cd "$(dirname "$0")/.." && source scripts/env.sh
export PLAYTEST_OUT=$PLAYTEST_ROOT/out/ui; mkdir -p $PLAYTEST_OUT
export SCENARIO=$1 PLAYTEST_ROOT
ROM=${UI_ROM:-$REPO_ROOT/game/pokeemerald_modern.gba}  # UI_ROM=.../pokeemerald.gba uses the agbcc build
while read -r addr _ name; do export "SYM_$name=$addr"; done < <(arm-none-eabi-nm "${ROM%.gba}.elf" | grep -wE "gSaveBlock1Ptr|gSaveBlock2Ptr|gPlayerParty|gPlayerPartyCount|gMain|CB2_Overworld|CB2_LoadMap|CB2_IntroCrawl|sLastSelectedPokemon|gObjectEvents")
rm -f $PLAYTEST_OUT/DONE
setsid xvfb-run -a /opt/mgba-0.11/bin/mgba-qt --script $PLAYTEST_ROOT/lua/examples/ui-check.lua -l 0 "$ROM" > $PLAYTEST_OUT/mgba_$1.log 2>&1 &
PID=$!
for _ in $(seq 1 ${2:-240}); do [ -f $PLAYTEST_OUT/DONE ] && break; sleep 1; done
kill -- -$PID 2>/dev/null; sleep 1
ls $PLAYTEST_OUT | grep -c png; [ -f $PLAYTEST_OUT/DONE ] && echo DONE || echo TIMEOUT

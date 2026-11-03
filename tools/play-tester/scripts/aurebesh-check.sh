#!/usr/bin/env bash
# Check the Aurebesh signs and warden wipes in the modern ROM (make modern), headless, one scenario per run.
#   scripts/aurebesh-check.sh boot          # once: new game to the truck, saves out/aurebesh/overworld.ss0
#   scripts/aurebesh-check.sh sign_outer    # Sealed Vault outer room sign  -> out/aurebesh/sign_outer.png
#   scripts/aurebesh-check.sh sign_inner    # inner room "WE OWE ALL TO THE COMPANION" sign
#   scripts/aurebesh-check.sh regirock      # also regice, registeel: 40 frames of the battle wipe
# Usage: scripts/aurebesh-check.sh SCENARIO [timeout seconds]
cd "$(dirname "$0")/.." && source scripts/env.sh
export PLAYTEST_OUT=$PLAYTEST_ROOT/out/aurebesh; mkdir -p $PLAYTEST_OUT
export SCENARIO=$1
ROM=$REPO_ROOT/game/pokeemerald_modern.gba
rm -f $PLAYTEST_OUT/DONE
setsid xvfb-run -a /opt/mgba-0.11/bin/mgba-qt --script $PLAYTEST_ROOT/lua/examples/aurebesh-check.lua -l 0 "$ROM" > $PLAYTEST_OUT/mgba_$1.log 2>&1 &
PID=$!
for _ in $(seq 1 ${2:-240}); do [ -f $PLAYTEST_OUT/DONE ] && break; sleep 1; done
kill -- -$PID 2>/dev/null; sleep 1
ls $PLAYTEST_OUT | grep -c png; [ -f $PLAYTEST_OUT/DONE ] && echo DONE || echo TIMEOUT

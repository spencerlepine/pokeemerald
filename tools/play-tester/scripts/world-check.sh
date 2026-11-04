#!/usr/bin/env bash
# Screenshot spots of the ported world (agbcc build), headless. Run `UI_ROM=... scripts/ui-check.sh boot` first.
#   scripts/world-check.sh SPOTS_FILE [timeout]    SPOTS_FILE lines: name group num x y [KEYS like DOWN3 A]
# Shots and log.txt land in out/world/.
cd "$(dirname "$0")/.." && source scripts/env.sh
export PLAYTEST_OUT=$PLAYTEST_ROOT/out/world; mkdir -p $PLAYTEST_OUT; rm -f $PLAYTEST_OUT/*.png $PLAYTEST_OUT/log.txt
export WORLD_SPOTS=$(realpath "$1") PLAYTEST_ROOT
ROM=${UI_ROM:-$REPO_ROOT/game/pokeemerald.gba}
while read -r addr _ name; do export "SYM_$name=$addr"; done < <(arm-none-eabi-nm "${ROM%.gba}.elf" | grep -wE "gSaveBlock1Ptr|gMain|CB2_LoadMap|gMapHeader")
# the save block's vars follow its flags, whose size moves with MAX_TRAINERS_COUNT
FC=$(printf '#include "constants/opponents.h"\n#include "constants/flags.h"\nFLAGS_COUNT\n' | cpp -P -I $REPO_ROOT/game/include - 2>/dev/null | tail -1)
export SB1_VARS=$(python3 -c "n=0x1270+(($FC)+7)//8; print(n+(n&1))")
rm -f $PLAYTEST_OUT/DONE
setsid xvfb-run -a /opt/mgba-0.11/bin/mgba-qt --script $PLAYTEST_ROOT/lua/examples/world-check.lua -l 0 "$ROM" > $PLAYTEST_OUT/mgba.log 2>&1 &
PID=$!
for _ in $(seq 1 ${2:-300}); do [ -f $PLAYTEST_OUT/DONE ] && break; sleep 1; done
kill -- -$PID 2>/dev/null; sleep 1
[ -f $PLAYTEST_OUT/DONE ] && echo DONE || echo TIMEOUT; cat $PLAYTEST_OUT/log.txt

#!/usr/bin/env bash
# From a fresh boot (no .sav next to the ROM), mash A (START every 8th tap) through the title,
# Birch's speech and naming until gMain.callback2 == CB2_Overworld. Lands in the moving truck.
# Then saves savestates/out: $PLAYTEST_OUT/truck.ss0. Took ~35 taps in testing.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
L=scripts/live.sh
cb2() { $L lua 'return string.format("%08x", emu:read32(0x030022c4))' 2>/dev/null | grep -o '"result": "[0-9a-f]*"' | cut -d'"' -f4; }
for i in $(seq 1 200); do
  if [ $((i % 8)) -eq 0 ]; then k=START; else k=A; fi
  $L tap "$k" 4 >/dev/null 2>&1
  [ "$(cb2)" = "08085e5d" ] && { echo "overworld after $i taps"; break; }
done
sleep 2
$L lua "return emu:saveStateFile(\"$PLAYTEST_OUT/truck.ss0\")"
$L shot "$PLAYTEST_OUT/overworld.png"

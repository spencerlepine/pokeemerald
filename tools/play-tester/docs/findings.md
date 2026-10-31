# Findings log (2026-10-31, Ubuntu 24.04, 4 cores, no GPU)

Chronological notes from the end-to-end verification. Times are UTC.

## Round 1: build, launch, screenshot

- **21:53** Cloned the repo. The decomp is in `game/`, so all build commands run there.
- **21:56** `apt install build-essential binutils-arm-none-eabi git libpng-dev`. No devkitARM is needed on
  Ubuntu (`game/INSTALL.md` Linux section, matching `.github/workflows/build.yml`). agbcc came from
  `pret/agbcc` via `./build.sh && ./install.sh ../game`.
- **21:58** `apt install mgba-qt mgba-sdl` gives mGBA **0.10.2** in `/usr/games`. Lua is compiled in
  (`libmgba.so` exports `lua_*`), but neither binary has a `--script` option.
- **21:59** Read all three MCP servers. `mgba-mcp` and `mgba-live-mcp` both launch
  `mgba-qt --script <bridge>.lua <rom>`. `mcp-mgba` expects you to load `bridge.lua` from
  Tools → Scripting in the GUI. `mgba-live-mcp`'s README says stock 0.10.5 was rejected for lacking
  `--script` and pins mGBA `543a197582c30364584d773a974d7f991892fa43` (0.11.0-dev).
- **22:00** The first mGBA source build failed in CMake because Ubuntu 24.04's `libzip-dev` CMake config
  references `/usr/bin/zipcmp`, which isn't installed. Building with `-DUSE_LIBZIP=OFF` fixed it.
- **22:01** ROM built: `make -j4` took 1m16s and produced `game/pokeemerald.gba` with
  sha1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7`, which matches `rom.sha1`.
- **22:02** mGBA 0.11.0 installed to `/opt/mgba-0.11`. `mgba-qt --help` lists `--script FILE`. The SDL
  `mgba` still has no `--script`.
- **22:03** First headless screenshots: `xvfb-run -a mgba-qt --script shot.lua -l 0 rom`. The frame
  callback calls `emu:screenshot()` at frames 300/900/1800 and gives 240×160 PNGs. 1800 frames took
  about 43 s (roughly 42 fps).
- **22:04** `emu:quit()` was unreliable, so we write a DONE marker and kill the process. `pkill -f mgba-qt` in
  the same shell line killed my own shell (exit 144).
- **22:05** Tested `mgba-mcp` through a real MCP stdio client: 9 tools.
  `mgba_read_range 0x080000A0` returned `POKEMON EMER`, and `mgba_run_sequence` with START reached the title.
  Bugs: `mgba_run` has a fixed 30 s timeout and no argument to change it, so `frames: 1800` fails. The freeze
  detector assumes 40 GB sprites, so it reported a false "Freeze detected" on GBA. It hard-codes `mgba-qt` on PATH.
- **22:07** Tested `mgba-live-mcp` (19 tools) with a long-lived `Xvfb :99`. Across separate calls:
  screenshot, START (skips the intro), START, A on New Game reached Birch. `read-range` returned the ROM
  title, and `run-lua emu:write8(0x02000000,0x5A)` read back 90.

## Round 2: savestates, teleport, party

- Addresses come from `make syms` → `game/pokeemerald.sym` (identical to vanilla Emerald because the ROM is).
- **New Game → overworld**: mash A with START every 8th tap and poll `gMain.callback2` until
  it equals `CB2_Overworld|1` (`0x08085e5d`). It took 35 taps and landed in the moving truck (map 25.40).
  Name "AA", ¥3000 (decrypted with `SaveBlock2.encryptionKey`, which confirmed the key handling).
- **Savestates**: `emu:saveStateFile(path)` / `emu:loadStateFile(path)` round-trip map, position and
  party, and `saveStateSlot/loadStateSlot` work too. `mgba-live-cli start --savestate file.ss0` restores the
  whole state in a new process. A state is about 33 KB.
- **Teleport**: write `SaveBlock1.location` (group, num, warpId=-1, x, y) and `pos`, then set
  `gMain.callback2 = CB2_LoadMap|1`. The map reloads in about a second and the player can walk.
  Tested truck → Littleroot (0.9), Sootopolis (0.7) and Ever Grande (0.8).
  - Raw x/y ignores collision: (31,30) in Sootopolis put the player on the gym roof.
  - `E.teleportToWarp` reads `gMapGroups → MapHeader.events → warps[i]` from ROM and lands on a door.
    Ever Grande warp 1 = Pokémon Center (27,48).
  - Story vars are not updated (e.g. leaving the truck this way skips the move-in scene).
- **Party**: build `struct Pokemon` from scratch. Header, then four 12-byte substructs ordered by
  `personality % 24` (table in `GetSubstruct`, `src/pokemon.c`), XOR'd with `personality ^ otId`, plus a
  u16 checksum of the plaintext, `hasSpecies` bit, and plaintext battle stats at +0x50.
  Injected Rayquaza Lv50 (exp 156250, Slow) and Torchic Lv5 (exp 135, Medium Slow).
  The party menu, summary (nature, OT, met data) and FLY option all render. **Using a Rare Candy from the bag
  levelled the injected Torchic to 6**, so the game's own code decrypts and re-encrypts our data.
- **Money / items / flags**: money = value XOR key. Items pocket slots are `{u16 id, u16 qty ^ (key & 0xFFFF)}`.
  Rare Candy = 68. Flags are bit-addressed at SaveBlock1+0x1270. Setting `FLAG_SYS_POKEMON_GET` (0x860)
  shows POKéMON in the start menu, and badges 0x867–0x86E show as "BADGES 8" on the save screen.
- **In-game SAVE** writes `pokeemerald.sav` next to the ROM. After a fresh process boot, CONTINUE shows 8 badges
  and lands where we saved.
- **Input drift**: blind multi-tap sequences lost taps during fades and menu transitions. Pause about 2 s between
  taps, or screenshot or poll `callback2` before the next step.

## Not done

Forcing battles, RNG seeding (`gRngValue` @ `0x03005d80`), PC boxes, story var fix-ups, headed mode,
macOS, and `dmang-dev/mcp-mgba`.

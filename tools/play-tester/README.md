# play-tester: Emerald Control Agent

Headless mGBA harness for driving the `game/` ROM from an agent or script. It
launches the ROM, steps frames, presses buttons, takes screenshots, saves and
loads savestates, and reads and writes game memory (teleport, party, money,
items, flags). There are **no changes to the game source**.

This folder is the standalone context for the next agent. Everything here was
run end to end on Ubuntu 24.04 (4 cores, no GPU, no display) on 2026-10-31.

## Status

| Capability | Status | How |
| --- | --- | --- |
| Build ROM, byte-identical (`sha1 f3ae0881…`) | ✅ | apt `binutils-arm-none-eabi` + pret `agbcc` + `make` in `game/` |
| Headless launch + PNG screenshot | ✅ | mGBA 0.11-dev Qt frontend under Xvfb with `--script` |
| MCP control, persistent session | ✅ | [`penandlim/mgba-live-mcp`](https://github.com/penandlim/mgba-live-mcp) (19 tools) |
| MCP control, one-shot | ✅ with bugs | [`struktured-labs/mgba-mcp`](https://github.com/struktured-labs/mgba-mcp) |
| Button input across calls, reach overworld from boot | ✅ | `scripts/new-game-to-overworld.sh` (~35 taps, ~13 s) |
| Savestates (file, slot, launch-from) | ✅ | `emu:saveStateFile/loadStateFile`, `live.sh up <state>` |
| Teleport to any map (x/y or onto a door warp) | ✅ | `E.teleport`, `E.teleportToWarp` in `lua/emerald.lua` |
| Build encrypted party Pokémon from scratch | ✅ | `E.writeMon` / `E.readMon` (the game levels them with Rare Candy) |
| Money, bag items, flags/badges | ✅ | `E.setMoney`, `E.addItem`, `E.setFlag` |
| In-game SAVE → CONTINUE on reboot | ✅ | `.sav` written next to the ROM |
| Force battle, RNG seeding, PC boxes, story vars | ❌ not tried | see "Next steps" |
| Headed mode, macOS | ❌ not tried | |

Screenshots of every row are in `screenshots/`.

## Quick start (Ubuntu)

```bash
cd tools/play-tester
scripts/setup-ubuntu.sh            # one time, ~10-15 min: apt deps, agbcc, ROM, mGBA 0.11 -> /opt/mgba-0.11, MCP servers -> .deps/
scripts/smoke-screenshot.sh        # one-shot headless boot -> out/frame_{300,900,1800}.png

scripts/live.sh up                 # persistent session on Xvfb :99 (session id "emerald")
scripts/new-game-to-overworld.sh   # mash through New Game -> out/truck.ss0, out/overworld.png
scripts/live.sh luafile lua/emerald.lua                                 # load helpers (global E persists)
scripts/live.sh luafile lua/examples/give-party-money-items-badges.lua  # Rayquaza Lv50 + Torchic, 8 badges, ¥999999, Rare Candy x99
scripts/live.sh lua 'E.teleportToWarp(0, 8, 1); return "ok"'           # Ever Grande, Pokémon Center door
scripts/live.sh tap DOWN 16
scripts/live.sh shot out/now.png
scripts/live.sh lua 'return emu:saveStateFile("'$PWD'/out/mine.ss0")'
scripts/live.sh down
```

Or skip the intro entirely: `scripts/live.sh up savestates/evergrande-party-badges-money.ss0`.

`source scripts/env.sh` sets everything the tools need: `ROM`, the mGBA path,
`DISPLAY`, the Qt/SDL env and `out/`. Override `ROM=` to point at another build.

### Use as an MCP server

After setup, register the persistent server with your MCP client. It needs a
running X display, so start `Xvfb :99` first (`scripts/live.sh up` does that, then `down`).

```json
{
  "mcpServers": {
    "mgba": {
      "command": "<repo>/tools/play-tester/.deps/mgba-live-mcp/.venv/bin/mgba-live-mcp",
      "env": {
        "DISPLAY": ":99",
        "LD_LIBRARY_PATH": "/opt/mgba-0.11/lib",
        "QT_QPA_PLATFORM": "xcb",
        "LIBGL_ALWAYS_SOFTWARE": "1",
        "SDL_AUDIODRIVER": "dummy"
      }
    }
  }
}
```

Pass `mgba_path: "/opt/mgba-0.11/bin/mgba-qt"` and `rom: "<repo>/game/pokeemerald.gba"`
to `mgba_live_start` (`fast: true` speeds it up). Then call `mgba_live_run_lua` once with
`file: "<repo>/tools/play-tester/lua/emerald.lua"`, and call `E.*` from later `mgba_live_run_lua`
calls (`code: "E.teleportToWarp(0, 8, 1)"`).
`mcp/test_mgba_live_mcp_list_tools.py` checks that the server answers over stdio.

## Layout

```
README.md                 this file (start here)
docs/one-pager.md         the original design one-pager, annotated with corrections
docs/findings.md          chronological run log: every bug, workaround and number measured
scripts/env.sh            shared env (source it)
scripts/setup-ubuntu.sh   one-time install + build
scripts/smoke-screenshot.sh   headless one-shot boot + screenshots
scripts/live.sh           persistent session wrapper (up/down/lua/luafile/tap/shot/cli)
scripts/new-game-to-overworld.sh  boot -> New Game -> overworld, saves out/truck.ss0
lua/emerald.lua           runtime helpers: teleport, warps, flags, money, items, party build/read
lua/examples/             status, raw teleport, party/money/badges, one-shot screenshot scripts
mcp/                      MCP stdio smoke tests for both servers
savestates/               ready-made states (see savestates/README.md)
screenshots/              evidence for each verified capability
.deps/ (gitignored)       agbcc, mGBA source, MCP server clones
out/   (gitignored)       run output
```

## Things that will bite you

1. **Released mGBA cannot do this.** 0.10.x (Ubuntu apt 0.10.2, Homebrew/macOS 0.10.5) has Lua but no
   `--script` flag, and every MCP server loads its bridge with `mgba-qt --script`. Build 0.11-dev
   (the setup script pins commit `543a197`). Only the Qt frontend has `--script`, not SDL.
2. **Headless means Qt + Xvfb**, with `QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 SDL_AUDIODRIVER=dummy`.
   `SDL_VIDEODRIVER=dummy` is irrelevant. It runs at about 42 fps real time without a GPU.
3. **Ubuntu 24.04 libzip CMake bug** breaks mGBA's configure (`/usr/bin/zipcmp` missing). Use `-DUSE_LIBZIP=OFF`.
4. **`emu:quit()` is unreliable.** One-shot runs write a DONE file and the wrapper kills the process group.
   Don't `pkill -f mgba-qt` from a shell whose own command line contains `mgba-qt` (it kills itself).
5. **mgba-live-mcp session ids linger after stop** (`session_exists`). `mgba-live-cli status --all` archives
   dead ones; `live.sh` does this for you.
6. **mgba-mcp (one-shot) bugs:** `mgba_run` has a hard 30 s timeout (≈1200 frames max here), its freeze
   detector assumes 40 Game Boy sprites (false "Freeze detected" on GBA), and every call reboots the ROM.
7. **Blind input drifts.** Taps during fades/menu transitions get dropped. Screenshot or check
   `gMain.callback2` between steps (`0x08085e5d` = `CB2_Overworld`, meaning in the overworld).
8. **Raw x/y teleports ignore collision** (see the gym roof screenshot). `E.teleportToWarp` lands on a door from
   the ROM's warp table, which is always walkable.
9. **Story state isn't touched by teleport.** Skipped cutscenes stay unplayed and their vars keep their old values. Set them
   via `vars` (SaveBlock1 +0x139C) or start from a savestate taken after the scene.
10. **Addresses are build-specific.** `lua/emerald.lua` hard-codes addresses from the vanilla-identical build.
    The moment `game/` changes, run `make syms` and refresh them from `game/pokeemerald.sym`
    (`gSaveBlock1Ptr`, `gSaveBlock2Ptr`, `gPlayerParty`, `gPlayerPartyCount`, `gMain`, `CB2_LoadMap`, `gMapGroups`).
    The savestates also become invalid then.

## Memory map used

| Symbol | Address | Notes |
| --- | --- | --- |
| `gSaveBlock1Ptr` | `0x03005d8c` | → pos +0x00, location (WarpData) +0x04, money +0x490 (XOR key), Items pocket +0x560, flags +0x1270, vars +0x139C |
| `gSaveBlock2Ptr` | `0x03005d90` | → name +0x00, gender +0x08, trainer id +0x0A, encryptionKey +0xAC |
| `gPlayerPartyCount` | `0x020244e9` | u8 |
| `gPlayerParty` | `0x020244ec` | 6 × 100-byte `struct Pokemon` |
| `gMain` | `0x030022c0` | callback2 at +4. Writing `CB2_LoadMap\|1` reloads the map from `SaveBlock1.location` |
| `CB2_LoadMap` | `0x08085fcc` | thumb |
| `gMapGroups` | `0x08486578` | ROM: group → map header → events → warps |
| flags | `FLAG_SYS_POKEMON_GET 0x860`, `FLAG_BADGE01..08_GET 0x867..0x86E` | bit index into SaveBlock1 flags |

Struct layouts come from `game/include/global.h`, `game/include/pokemon.h` and
`game/include/global.fieldmap.h`. Map ids come from `game/include/constants/map_groups.h`
(`MAP_X = num | group << 8`).

## Next steps (suggested)

- Wrap `lua/emerald.lua` as named MCP tools (`teleport`, `give_pokemon`, `set_flag`…) instead of raw `run_lua`.
- Load addresses from `pokeemerald.sym` at startup so the tool survives source changes.
- Force a wild/trainer battle, seed `gRngValue` (`0x03005d80`), set story vars after teleports.
- Try headed mode on a real display, and macOS (needs an mGBA 0.11 nightly there too).

Palettes ([`../PALETTES.md`](../PALETTES.md)): not applicable, this tool writes no art. Its screenshots are the way to
see palettes in the real game (fades, weather tints and slot clashes do not show in a tool's preview).

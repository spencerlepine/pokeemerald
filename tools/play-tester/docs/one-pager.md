# Emerald Control Agent (One-Pager)

> This is the original design one-pager. Lines starting with **⚠ Correction** were added on
> 2026-10-31 after building and running it end to end on Ubuntu 24.04. See `../README.md` for the
> working setup and `findings.md` for the full log.

Standalone agent for launching a built `pokeemerald.gba` ROM, taking screenshots, stepping the emulator, and mutating runtime game state. Supports both headed and headless modes. Designed to be driven by an LLM or scripts via MCP (or a thin wrapper).

## Goal

Load a once-built `pokeemerald.gba`, provide reliable screenshot + frame-step control, and allow runtime state modification (teleport, flags, party, etc.) without rebuilding the ROM for every experiment.

## Architecture

```
[Agent / LLM / Script]
        ↕ MCP (or thin Python/Node wrapper)
[mGBA process]  ←── Lua scripting + memory API
        ↕
pokeemerald.gba (built once)
```

- **Core engine**: mGBA (accuracy + mature Lua + CLI support)
- **Control plane**: existing MCP servers (`mgba-mcp`, `mgba-live-mcp`, `mcp-mgba`) or a thin custom wrapper
- **Headless support**: `xvfb` (Linux) or SDL dummy driver

## Modes

| Mode     | How                                      | Use case                       |
|----------|------------------------------------------|--------------------------------|
| Headed   | Normal mGBA window + MCP attached        | Visual debugging, play-testing |
| Headless | `xvfb-run` / SDL dummy + frame stepping  | Automated screenshots, agents  |

Both modes expose the same tool surface.

> **⚠ Correction:** Headless has to be the **Qt** frontend under Xvfb. Only `mgba-qt` has `--script`, so the SDL dummy driver route doesn't apply. Working env: `QT_QPA_PLATFORM=xcb SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1`. Expect about 42 fps real time without a GPU. Headed mode was not tested.

## Runtime Capabilities (no source changes required)

Via mGBA Lua / memory API the agent can:

- Load ROM + optional savestate
- Advance N frames (or run until condition)
- Press / hold / release buttons
- Take PNG screenshot (full screen or region)
- Read/write arbitrary memory (8/16/32-bit or ranges)
- Save/load savestates
- Execute arbitrary Lua snippets
- Query current frame count, pause/resume, soft reset

**Game-state modifications that work purely at runtime** (addresses/structures known from the decomp):

- Teleport (player X/Y + map/warp IDs)
- Change party, levels, items, money, badges
- Set/clear flags and variables
- Force battle or skip intro
- Manipulate RNG seed for reproducibility

Most “go somewhere and take a screenshot” workflows need **zero** source changes.

> **⚠ Verified:** Savestates, teleport, party (built from scratch, encrypted), levels, items, money, badges/flags and button input all work with zero source changes. Not yet tried: forcing a battle, RNG seeding, a true intro skip (we mash through New Game in about 13 s instead). Pitfalls: party data is encrypted and checksummed; money and item quantities are XOR'd with `encryptionKey`; raw x/y teleports ignore collision; teleporting doesn't update story vars.

## When Source Modifications Are Needed

Only for things the runtime memory surface cannot cleanly provide:

- Brand-new systems or UI
- Permanent debug menus / cheats that survive soft resets more cleanly
- Changes that run before memory is fully initialized
- Performance-critical hooks that would be too slow via repeated Lua memory writes

Start with pure runtime control. Patch the decomp only if you hit a hard limit.

## Minimal Tool Surface

```
start(rom, mode="headless"|"headed", savestate=None)
step(frames=1)
press(buttons, hold_frames=1)
screenshot(path or return bytes)
read_memory(addr, size)
write_memory(addr, value or bytes)
run_lua(code)
save_state / load_state
status() → frame, running, etc.
```

> **⚠ Mapping to mgba-live-mcp:** start → `mgba_live_start` (`rom`, `savestate`, `mgba_path`, `fast`); press → `mgba_live_input_tap/set/clear`; screenshot → `mgba_live_get_view` / `mgba_live_export_screenshot` / `*_and_view`; read_memory → `mgba_live_read_memory/read_range`; run_lua → `mgba_live_run_lua` (`code` or `file`); status → `mgba_live_status`. There is no dedicated write_memory, save_state or load_state tool. Use run_lua with `emu:write8/16/32` and `emu:saveStateFile/loadStateFile`. Frame stepping isn't a tool either: the session free-runs at the fps target, so "step" means wait, or use a Lua frame callback.

## Prerequisites & Dependencies

### 1. Built ROM (`pokeemerald.gba`)

You must build this once from source. The pret decompilation produces a byte-identical ROM.

- **Repo**: https://github.com/pret/pokeemerald
- **High-level steps**:
  1. Install the GBA toolchain (devkitARM / devkitPro)
  2. Build and install `agbcc` (the compiler the decomp expects)
  3. Clone pokeemerald, run `./build_tools.sh`, then `make`
- **Linux**: Follow the Linux section of `INSTALL.md` (apt packages + devkitARM)
- **macOS**: Follow the macOS section of `INSTALL.md` (Homebrew + devkitPro pacman)
- Output: `pokeemerald.gba` in the project root

You only need to do this once (or when you deliberately change the source).

> **⚠ Correction:** In this repo the decomp is in `game/`, and the ROM lands at `game/pokeemerald.gba`. On Debian/Ubuntu `INSTALL.md` uses **no devkitARM**: `apt install build-essential binutils-arm-none-eabi git libpng-dev` is enough. `./build_tools.sh` is deprecated (it prints "run make tools"), and plain `make` builds the tools itself. agbcc: `git clone https://github.com/pret/agbcc && cd agbcc && ./build.sh && ./install.sh ../game`. `make -j4` took 1m16s and the sha1 matched `rom.sha1`.

### 2. mGBA Emulator

The runtime engine.

- **Official site / releases**: https://mgba.io/ or https://github.com/mgba-emu/mgba
- **Linux**:
  - Many distros: `sudo apt install mgba-qt` (or `mgba-sdl`)
  - Or build from source / grab AppImage / flatpak
- **macOS**:
  - Homebrew: `brew install mgba`
  - Or download the official `.dmg` / app bundle from the releases page
- Verify: `mgba --version` or open the GUI and confirm it launches

Lua scripting support is built-in on modern builds.

> **⚠ Correction:** No released mGBA works for automation. 0.10.x (Ubuntu apt = 0.10.2, Homebrew/macOS = 0.10.5) has Lua but **no `--script` CLI flag**, and the MCP servers launch `mgba-qt --script bridge.lua rom.gba`. Build 0.11-dev from source (pinned commit `543a197`, with `-DENABLE_SCRIPTING=ON -DUSE_LUA=5.4 -DBUILD_QT=ON -DUSE_LIBZIP=OFF`), or use a 0.11 nightly. On Ubuntu the apt binaries also live in `/usr/games` (not on root's PATH), and the SDL one is named `mgba`.

### 3. Headless Support (optional but recommended)

- **Linux**: `xvfb` (`sudo apt install xvfb`) so you can run `xvfb-run mgba ...`
- **macOS**: Usually not needed for basic headed use; for true headless you can use SDL dummy drivers or run under a virtual display if required
- Alternative: set `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy` environment variables

> **⚠ Correction:** See the Modes note. Use `xvfb-run -a mgba-qt …` for one-shot runs, or a long-lived `Xvfb :99` + `DISPLAY=:99` for persistent sessions (`mgba-live-mcp` does not start Xvfb itself).

### 4. MCP Server or Control Wrapper

Pick one (or write a thin equivalent):

- `struktured-labs/mgba-mcp` — headless-friendly, screenshot + memory + Lua
- `penandlim/mgba-live-mcp` — persistent live session style
- `dmang-dev/mcp-mgba` — Lua-bridge style

Or implement the minimal tool surface above yourself in Python/Node talking to mGBA’s Lua socket / scripting interface.

> **⚠ Correction:** Use **mgba-live-mcp**. It's the only one of the three that keeps one emulator alive across calls, which separate press/step/screenshot calls need. `mgba-mcp` is one-shot: every call reboots the ROM, `mgba_run` has a hard 30 s timeout, and its freeze detector is Game Boy-centric. `mcp-mgba` loads its bridge through the GUI menu (not tested). All three need mGBA 0.11-dev.

### 5. Runtime Language (for the agent / wrapper)

- Python 3.11+ **or** Node.js 20+ (depending on which MCP server or wrapper you choose)
- Standard package managers (`pip` / `uv` / `npm` / `pnpm`)

No other exotic system libraries are required beyond what mGBA already needs (SDL, libpng, etc., which the package managers pull in).

> **⚠ Note:** Building mGBA 0.11 needs Qt5 dev packages, Lua 5.4 dev, SQLite, epoxy and CMake (see `scripts/setup-ubuntu.sh`). The MCP servers use `uv` (Python 3.11+; tested with 3.13).

## What Is Intentionally Out of Scope for v1

- Building the ROM inside the agent
- Full debugger / GDB integration
- Multi-instance or link-cable
- Automatic memory-map discovery (hard-code the known Emerald structures first)

## Bottom Line

You do **not** need to modify the game source for the core loop (launch → step → screenshot → teleport → screenshot). Runtime memory writes + frame control via mGBA are sufficient and already well-supported by the existing MCP ecosystem. Source changes are an optional later optimization, not a prerequisite.

This gives you a clean, reusable “Emerald Control Agent” that can be driven by an LLM or scripts today.

> **⚠ Verified, with one caveat:** True for the whole loop, including teleport, party and savestates, once you use an mGBA 0.11-dev build. Hard-coded addresses are only valid while `game/` matches vanilla. Re-read them from `game/pokeemerald.sym` after any source change.

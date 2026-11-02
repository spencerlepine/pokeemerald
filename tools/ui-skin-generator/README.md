# ui-skin-generator

**Status:** phase 2 (mockups) in progress. The game source is untouched.

| Path | What it is |
|---|---|
| `reference/v1/` | 155 in-game captures of every themed UI (headless mGBA, native 240x160) plus `00_text_window_frames_1-20.png`, the 20 frame styles drawn from `game/graphics/text_window/`. |
| `mockup.py` | Recolours `reference/v1/` into `mockups/dune_v1/` with the Dune theme (`wiki/bible/PALETTE.md`, "HUD and menus: Dune"). Hue-family rules plus per-screen rectangles that protect creatures, maps, box wallpapers and the overworld. |
| `mockups/dune_v1/` | The current mockup of every screen. Regenerate with `python3 mockup.py`. |
| `TODO.md` | Phase 3 scope (the real tiles, tilemaps and palettes). |

Owner decisions so far (2026-11-02): direction B "Dune" (light sand surfaces, rust frames, steel for former blues,
gold for selection); the battle message box stays grey, never brown; icons are redrawn by the owner later
(`PENDING_ART` rows in `wiki/database/pending_art.csv`); box wallpapers and the region map keep their textures.

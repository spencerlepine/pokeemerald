# Color palette

The chosen color themes for the title screen, factions and menus: layer 2 of the art rules in
[`../../tools/PALETTES.md`](../../tools/PALETTES.md) (layer 1 is the GBA hardware). The art tools read this file directly
through `tools/palette-enforcer` (`python -m gba_palette themes -v` lists the theme ids), so a change here is what they
enforce on their next run. Themes are the default target: off-theme colours are warnings unless a tool locks a theme
(menus use `hud` strictly). Preview with dummy components: [Kyber Palette Preview](https://claude.ai/artifact/TJKX2LyGSftXXA3TKymuBW).

Format the tools rely on: one `##` section per theme (the theme id is its heading after the colon, slugged), a table
whose rows hold the hex in backticks, and the role in the last column. New places get their own section,
`## Planet: <name>`, before any tool draws them.

Every hex value is GBA-safe (each channel is a multiple of 8, so it maps exactly to the GBA's 15-bit color).
Roles: **primary** is the main color, **secondary** and **tertiary** support it, **accent** is used sparingly, **neutral** fills the rest.

To extend: add a row to the right table (or a new `##` section for a new theme), keep values in steps of 8, and give it a role. `python -m gba_palette themes` (in `tools/palette-enforcer`) fails if a value is off a step.

## Title screen and logo: Kyber Gold

Classic black and yellow. Gold carries the logo, space stays nearly black, one cold kyber blue accent.

| Color | Hex | RGB | Role |
|---|---|---|---|
| Logo Gold | `#F8D000` | 248, 208, 0 | primary |
| Void Black | `#080808` | 8, 8, 8 | secondary |
| Deep Space | `#101828` | 16, 24, 40 | tertiary |
| Kyber Blue | `#58C8F8` | 88, 200, 248 | accent |
| Gold Highlight | `#F8F0A0` | 248, 240, 160 | neutral |
| Gold Shadow | `#B88800` | 184, 136, 0 | neutral |
| Gold Outline | `#604000` | 96, 64, 0 | neutral |
| Star White | `#F8F8F0` | 248, 248, 240 | neutral |
| Star Dim | `#7880A0` | 120, 128, 160 | neutral |

## Rebel Alliance (protagonist): Alliance Dawn

Warm, worn earth tones with flight-suit orange.

| Color | Hex | RGB | Role |
|---|---|---|---|
| Flight Orange | `#E86818` | 232, 104, 24 | primary |
| Tatooine Sand | `#D8B880` | 216, 184, 128 | secondary |
| Base Olive | `#687040` | 104, 112, 64 | tertiary |
| Starbird Red | `#C83028` | 200, 48, 40 | accent |
| Rebel Cream | `#F0E8D0` | 240, 232, 208 | neutral |
| Worn Khaki | `#988060` | 152, 128, 96 | neutral |
| Leather Brown | `#584030` | 88, 64, 48 | neutral |
| Saber Blue | `#50A0F8` | 80, 160, 248 | accent |

## Galactic Empire (antagonist): Imperial Order

Cold greys, black and white with a single red.

| Color | Hex | RGB | Role |
|---|---|---|---|
| Durasteel | `#606870` | 96, 104, 112 | primary |
| Trooper White | `#F0F0F0` | 240, 240, 240 | secondary |
| Command Black | `#101010` | 16, 16, 16 | tertiary |
| Signal Red | `#C02020` | 192, 32, 32 | accent |
| Steel Light | `#A8B0B8` | 168, 176, 184 | neutral |
| Fleet Navy | `#304050` | 48, 64, 80 | neutral |
| Console Green | `#60B070` | 96, 176, 112 | neutral |
| Saber Red | `#F83030` | 248, 48, 48 | accent |

## Hutt Cartel (second villain team): Swamp Throne

Swamp green, tarnished gold and rust, so it never reads as Rebel or Empire.

| Color | Hex | RGB | Role |
|---|---|---|---|
| Swamp Slime | `#88A040` | 136, 160, 64 | primary |
| Hutt Gold | `#D0A030` | 208, 160, 48 | secondary |
| Bog Green | `#485018` | 72, 80, 24 | tertiary |
| Rust | `#985030` | 152, 80, 48 | accent |
| Smoke Brown | `#403830` | 64, 56, 48 | neutral |
| Old Parchment | `#F0E0B0` | 240, 224, 176 | neutral |

## HUD and menus: Hyperspace Console (surfaces and text)

Dark blue-grey menus instead of Emerald's white boxes. Greys lean slightly blue so they read as cockpit metal.

| Color | Hex | RGB | Role |
|---|---|---|---|
| Space | `#080810` | 8, 8, 16 | surface |
| Base | `#101820` | 16, 24, 32 | surface |
| Panel | `#182030` | 24, 32, 48 | surface |
| Panel Raised | `#283040` | 40, 48, 64 | surface |
| Border | `#485868` | 72, 88, 104 | surface |
| Select Row | `#284058` | 40, 64, 88 | surface |
| Text | `#E8E8E0` | 232, 232, 224 | text |
| Text Shadow | `#303840` | 48, 56, 64 | text |
| Text Dim | `#98A0B0` | 152, 160, 176 | text |
| Text Disabled | `#586070` | 88, 96, 112 | text |

## HUD and menus: status and accents

Gold is the only cursor/selection color everywhere. Warning yellow is for HP and status only, never selection.

| Color | Hex | RGB | Role |
|---|---|---|---|
| Cursor Gold | `#F8D000` | 248, 208, 0 | accent |
| Holo Cyan | `#68D0F0` | 104, 208, 240 | accent |
| HP Good | `#48D060` | 72, 208, 96 | status |
| HP Warn | `#F8C030` | 248, 192, 48 | status |
| HP Critical | `#F04838` | 240, 72, 56 | status |
| EXP Blue | `#48A0F8` | 72, 160, 248 | status |

## Battle backdrop (behind creatures)

Mid-tones, so dark sprite outlines stay visible.

| Color | Hex | RGB | Role |
|---|---|---|---|
| Arena Sky | `#384858` | 56, 72, 88 | backdrop |
| Arena Floor | `#687888` | 104, 120, 136 | backdrop |
| Arena Pad | `#98A8B0` | 152, 168, 176 | backdrop |

One theme per planet, generated from the approved tile-generator recipes: the colours each recipe gives the shared outdoor tileset (General). Regenerate after a recipe changes.

## Planet: Tatooine: Twin Suns

Ground green -> Tatooine sand; canopies -> dusty scrub olive; roof reds and peaches -> adobe clay; dirt -> warm sand-brown; sand yellows and water kept; cool outline greys kept. Generated from `tools/tile-generator/recipes/tatooine.yaml` (recoloured General banks).

| Color | Hex | RGB | Role |
|---|---|---|---|
| Ground | `#D8C088` | 216, 192, 136 | primary |
| Ground Shade | `#C0A878` | 192, 168, 120 | secondary |
| Tall Grass | `#B09868` | 176, 152, 104 | neutral |
| Canopy Light | `#C8C080` | 200, 192, 128 | neutral |
| Canopy | `#908048` | 144, 128, 72 | tertiary |
| Canopy Dark | `#585028` | 88, 80, 40 | neutral |
| Path | `#E0A878` | 224, 168, 120 | neutral |
| Sand | `#F0C890` | 240, 200, 144 | neutral |
| Sand Light | `#F8E0B0` | 248, 224, 176 | neutral |
| Rock | `#987070` | 152, 112, 112 | neutral |
| Rock Dark | `#604050` | 96, 64, 80 | neutral |
| Water | `#5088D0` | 80, 136, 208 | accent |
| Water Light | `#80A8D8` | 128, 168, 216 | accent |
| Water Deep | `#004888` | 0, 72, 136 | neutral |

## Planet: Hoth: Ice Field

Ground -> packed snow (cold white-blue); canopies -> frosted dark evergreen; dirt/sand -> trampled grey snow; rock -> blue-grey ice rock; roofs keep a warm accent so towns read. Generated from `tools/tile-generator/recipes/hoth.yaml` (recoloured General banks).

| Color | Hex | RGB | Role |
|---|---|---|---|
| Ground | `#D8E8F0` | 216, 232, 240 | primary |
| Ground Shade | `#C0D0D8` | 192, 208, 216 | secondary |
| Tall Grass | `#B0C0C8` | 176, 192, 200 | neutral |
| Canopy Light | `#78B0B0` | 120, 176, 176 | neutral |
| Canopy | `#407878` | 64, 120, 120 | tertiary |
| Canopy Dark | `#204848` | 32, 72, 72 | neutral |
| Path | `#88A8C0` | 136, 168, 192 | neutral |
| Sand | `#C0D8E8` | 192, 216, 232 | neutral |
| Sand Light | `#E0F0F8` | 224, 240, 248 | neutral |
| Rock | `#987070` | 152, 112, 112 | neutral |
| Rock Dark | `#604050` | 96, 64, 80 | neutral |
| Water | `#78A8D0` | 120, 168, 208 | accent |
| Water Light | `#A0C0E0` | 160, 192, 224 | accent |
| Water Deep | `#386088` | 56, 96, 136 | neutral |

## Planet: Sullust: Ash and Ember

Ground -> warm charcoal ash; canopies -> scorched dark olive; dirt -> rust-brown cinder; sand -> pale ash drifts; water -> sulphur-teal hot springs. Generated from `tools/tile-generator/recipes/sullust.yaml` (recoloured General banks).

| Color | Hex | RGB | Role |
|---|---|---|---|
| Ground | `#786860` | 120, 104, 96 | primary |
| Ground Shade | `#685850` | 104, 88, 80 | secondary |
| Tall Grass | `#584840` | 88, 72, 64 | neutral |
| Canopy Light | `#988060` | 152, 128, 96 | neutral |
| Canopy | `#604828` | 96, 72, 40 | tertiary |
| Canopy Dark | `#302008` | 48, 32, 8 | neutral |
| Path | `#D07068` | 208, 112, 104 | neutral |
| Sand | `#C8B0A8` | 200, 176, 168 | neutral |
| Sand Light | `#D8C8C0` | 216, 200, 192 | neutral |
| Rock | `#987070` | 152, 112, 112 | neutral |
| Rock Dark | `#604050` | 96, 64, 80 | neutral |
| Water | `#009898` | 0, 152, 152 | accent |
| Water Light | `#60B0B0` | 96, 176, 176 | accent |
| Water Deep | `#005058` | 0, 80, 88 | neutral |

## Planet: Sullust Lava Fields: Magma Flow

Sullust ash fields with lava flows instead of water. Water frames are reused as lava frames (same animation). Generated from `tools/tile-generator/recipes/sullust-lava.yaml` (recoloured General banks).

| Color | Hex | RGB | Role |
|---|---|---|---|
| Ground | `#786860` | 120, 104, 96 | primary |
| Ground Shade | `#685850` | 104, 88, 80 | secondary |
| Tall Grass | `#584840` | 88, 72, 64 | neutral |
| Canopy Light | `#988060` | 152, 128, 96 | neutral |
| Canopy | `#604828` | 96, 72, 40 | tertiary |
| Canopy Dark | `#302008` | 48, 32, 8 | neutral |
| Path | `#D07068` | 208, 112, 104 | neutral |
| Sand | `#C8B0A8` | 200, 176, 168 | neutral |
| Sand Light | `#D8C8C0` | 216, 200, 192 | neutral |
| Rock | `#987070` | 152, 112, 112 | neutral |
| Rock Dark | `#604050` | 96, 64, 80 | neutral |
| Water | `#E07818` | 224, 120, 24 | accent |
| Water Light | `#F8A830` | 248, 168, 48 | accent |
| Water Deep | `#880000` | 136, 0, 0 | neutral |

## Planet: Endor: Forest Moon

Deep cool forest. Ground -> dark moss; canopies -> deep blue-green; dirt -> rich redwood-brown loam; wood (fortree huts) -> redwood bark; water -> dark forest stream. Generated from `tools/tile-generator/recipes/endor.yaml` (recoloured General banks).

| Color | Hex | RGB | Role |
|---|---|---|---|
| Ground | `#709868` | 112, 152, 104 | primary |
| Ground Shade | `#588058` | 88, 128, 88 | secondary |
| Tall Grass | `#487048` | 72, 112, 72 | neutral |
| Canopy Light | `#50A868` | 80, 168, 104 | neutral |
| Canopy | `#006838` | 0, 104, 56 | tertiary |
| Canopy Dark | `#003810` | 0, 56, 16 | neutral |
| Path | `#C07058` | 192, 112, 88 | neutral |
| Sand | `#D89878` | 216, 152, 120 | neutral |
| Sand Light | `#F0B090` | 240, 176, 144 | neutral |
| Rock | `#987070` | 152, 112, 112 | neutral |
| Rock Dark | `#604050` | 96, 64, 80 | neutral |
| Water | `#186890` | 24, 104, 144 | accent |
| Water Light | `#5888A0` | 88, 136, 160 | accent |
| Water Deep | `#003050` | 0, 48, 80 | neutral |

## Planet: Dagobah: Bog

Murky, low-contrast, grey-green. Ground -> bog moss; canopies -> gnarl-tree olive grey; dirt -> mud; stone -> mossy grey; water -> opaque swamp green. Generated from `tools/tile-generator/recipes/dagobah.yaml` (recoloured General banks).

| Color | Hex | RGB | Role |
|---|---|---|---|
| Ground | `#788868` | 120, 136, 104 | primary |
| Ground Shade | `#687050` | 104, 112, 80 | secondary |
| Tall Grass | `#586040` | 88, 96, 64 | neutral |
| Canopy Light | `#909060` | 144, 144, 96 | neutral |
| Canopy | `#585830` | 88, 88, 48 | tertiary |
| Canopy Dark | `#283010` | 40, 48, 16 | neutral |
| Path | `#987858` | 152, 120, 88 | neutral |
| Sand | `#A89880` | 168, 152, 128 | neutral |
| Sand Light | `#B8B098` | 184, 176, 152 | neutral |
| Rock | `#504838` | 80, 72, 56 | neutral |
| Rock Dark | `#604050` | 96, 64, 80 | neutral |
| Water | `#386040` | 56, 96, 64 | accent |
| Water Light | `#607860` | 96, 120, 96 | accent |
| Water Deep | `#002008` | 0, 32, 8 | neutral |

## Planet: Kamino: Storm Sea

Storm-grey ocean, white-grey platforms. Ground -> wet grey deck; canopies -> grey kelp; water -> dark slate storm sea; wood (log bridges) -> pale durasteel. Generated from `tools/tile-generator/recipes/kamino.yaml` (recoloured General banks).

| Color | Hex | RGB | Role |
|---|---|---|---|
| Ground | `#98A8B0` | 152, 168, 176 | primary |
| Ground Shade | `#889098` | 136, 144, 152 | secondary |
| Tall Grass | `#788088` | 120, 128, 136 | neutral |
| Canopy Light | `#70A0A0` | 112, 160, 160 | neutral |
| Canopy | `#386868` | 56, 104, 104 | tertiary |
| Canopy Dark | `#183838` | 24, 56, 56 | neutral |
| Path | `#A8B8C0` | 168, 184, 192 | neutral |
| Sand | `#D0E0E8` | 208, 224, 232 | neutral |
| Sand Light | `#E8F8F8` | 232, 248, 248 | neutral |
| Rock | `#889090` | 136, 144, 144 | neutral |
| Rock Dark | `#505860` | 80, 88, 96 | neutral |
| Water | `#306070` | 48, 96, 112 | accent |
| Water Light | `#607888` | 96, 120, 136 | accent |
| Water Deep | `#002038` | 0, 32, 56 | neutral |

## Rules of thumb

- **Creatures pop, chrome recedes.** Menus stay low saturation, so the only saturated things on screen are creatures, HP and the gold cursor.
- **Never put creatures on the darkest menu colors.** Sprite outlines (around `#202020`) vanish on Space and Panel. Battle backdrops use the mid-tone arena colors.
- **Three-color font.** GBA text is fill, shadow and background: use Text, Text Shadow and the panel it sits on.
- **Contrast.** Text on Panel, Base and Select Row is 8:1 or better; Text Dim on Panel is 6.2:1. HP Critical on Panel is 4.4:1, fine for bars but not small text. Text Disabled is dim on purpose.
- **16 colors per palette.** A GBA palette holds 15 colors plus transparent. The HUD surfaces, text and status colors fit one menu palette.
- **Mood only.** The references (Imperial Style Guide, Galactic Style Guide articles) were used for mood. These palettes are original.

# Color palette

A loose color reference for the title screen, factions and menus. It is a starting point for art, not a strict contract,
and nothing here is wired into `../game`. Preview with dummy components: [Kyber Palette Preview](https://claude.ai/artifact/TJKX2LyGSftXXA3TKymuBW).

Every hex value is GBA-safe (each channel is a multiple of 8, so it maps exactly to the GBA's 15-bit color).
Roles: **primary** is the main color, **secondary** and **tertiary** support it, **accent** is used sparingly, **neutral** fills the rest.

To extend: add a row to the right table (or a new `##` section for a new theme), keep values in steps of 8, and give it a role.

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

## Rules of thumb

- **Creatures pop, chrome recedes.** Menus stay low saturation, so the only saturated things on screen are creatures, HP and the gold cursor.
- **Never put creatures on the darkest menu colors.** Sprite outlines (around `#202020`) vanish on Space and Panel. Battle backdrops use the mid-tone arena colors.
- **Three-color font.** GBA text is fill, shadow and background: use Text, Text Shadow and the panel it sits on.
- **Contrast.** Text on Panel, Base and Select Row is 8:1 or better; Text Dim on Panel is 6.2:1. HP Critical on Panel is 4.4:1, fine for bars but not small text. Text Disabled is dim on purpose.
- **16 colors per palette.** A GBA palette holds 15 colors plus transparent. The HUD surfaces, text and status colors fit one menu palette.
- **Mood only.** The references (Imperial Style Guide, Galactic Style Guide articles) were used for mood. These palettes are original.

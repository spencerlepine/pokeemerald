#include "global.h"
#include "battle.h"
#include "title_screen.h"
#include "sprite.h"
#include "gba/m4a_internal.h"
#include "clear_save_data_menu.h"
#include "decompress.h"
#include "event_data.h"
#include "intro.h"
#include "intro_crawl.h"
#include "util.h"
#include "m4a.h"
#include "main.h"
#include "main_menu.h"
#include "palette.h"
#include "reset_rtc_screen.h"
#include "berry_fix_program.h"
#include "sound.h"
#include "sprite.h"
#include "task.h"
#include "scanline_effect.h"
#include "gpu_regs.h"
#include "trig.h"
#include "graphics.h"
#include "constants/rgb.h"
#include "constants/songs.h"

enum {
    TAG_VERSION = 1000,
    TAG_PRESS_START_COPYRIGHT,
    TAG_LOGO_SHINE,
    TAG_COLLAGE_FIRST, // one tag per collage figure from here on (src/data/title_screen_collage.h)
};

#define VERSION_BANNER_RIGHT_TILEOFFSET 64
#define VERSION_BANNER_LEFT_X 88
#define VERSION_BANNER_RIGHT_X 152
#define VERSION_BANNER_Y 2
#define VERSION_BANNER_Y_GOAL 56
#define START_BANNER_X 128

#define CLEAR_SAVE_BUTTON_COMBO (B_BUTTON | SELECT_BUTTON | DPAD_UP)
#define RESET_RTC_BUTTON_COMBO (B_BUTTON | SELECT_BUTTON | DPAD_LEFT)
#define BERRY_UPDATE_BUTTON_COMBO (B_BUTTON | SELECT_BUTTON)
#define A_B_START_SELECT (A_BUTTON | B_BUTTON | START_BUTTON | SELECT_BUTTON)

static void MainCB2(void);
static void Task_TitleScreenPhase1(u8);
static void Task_TitleScreenPhase2(u8);
static void Task_TitleScreenPhase3(u8);
static void Task_TitleScreenCrawlOut(u8);
static void StartTitleScreenCrawlOut(u8);
static void CB2_GoToMainMenu(void);
static void CB2_GoToClearSaveDataScreen(void);
static void CB2_GoToResetRtcScreen(void);
static void CB2_GoToBerryFixScreen(void);
static void CB2_GoToCopyrightScreen(void);
static void UpdateLegendaryMarkingColor(u8);

static void SpriteCB_VersionBannerLeft(struct Sprite *sprite);
static void SpriteCB_VersionBannerRight(struct Sprite *sprite);
static void SpriteCB_PressStartCopyrightBanner(struct Sprite *sprite);
static void SpriteCB_PokemonLogoShine(struct Sprite *sprite);
static void SpriteCB_CollageFigure(struct Sprite *sprite);

// const rom data
static const u16 sUnusedUnknownPal[] = INCGFX_U16("graphics/title_screen/unused.pal", ".gbapal");

static const u32 sTitleScreenRayquazaGfx[] = INCGFX_U32("graphics/title_screen/rayquaza.png", ".4bpp.lz");
static const u32 sTitleScreenRayquazaTilemap[] = INCGFX_U32("graphics/title_screen/rayquaza.bin", ".lz");
static const u32 sTitleScreenLogoShineGfx[] = INCGFX_U32("graphics/title_screen/logo_shine.png", ".4bpp.lz");
static const u32 sTitleScreenCloudsGfx[] = INCGFX_U32("graphics/title_screen/clouds.png", ".4bpp.lz");

// Character collage (tools/title-screen-generator/collage): Rebels on the left, the Empire on the right, standing
// behind the logo (BG2) and the foreground ridge (BG0, rayquaza.png), in front of the clouds. Each figure is one
// Sprite drawn as subsprites, with its own OBJ palette (slots 1-7), and slides in from its side of the screen.
static const struct OamData sOamData_CollageFigure =
{
    .y = 0,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(8x8),
    .size = SPRITE_SIZE(8x8),
    .priority = 2,
};

#include "data/title_screen_collage.h"



// Used to blend "Emerald Version" as it passes over over the Pokémon banner.
// Also used by the intro to blend the Game Freak name/logo in and out as they appear and disappear
const u16 gTitleScreenAlphaBlend[64] =
{
    BLDALPHA_BLEND(16, 0),
    BLDALPHA_BLEND(16, 1),
    BLDALPHA_BLEND(16, 2),
    BLDALPHA_BLEND(16, 3),
    BLDALPHA_BLEND(16, 4),
    BLDALPHA_BLEND(16, 5),
    BLDALPHA_BLEND(16, 6),
    BLDALPHA_BLEND(16, 7),
    BLDALPHA_BLEND(16, 8),
    BLDALPHA_BLEND(16, 9),
    BLDALPHA_BLEND(16, 10),
    BLDALPHA_BLEND(16, 11),
    BLDALPHA_BLEND(16, 12),
    BLDALPHA_BLEND(16, 13),
    BLDALPHA_BLEND(16, 14),
    BLDALPHA_BLEND(16, 15),
    BLDALPHA_BLEND(15, 16),
    BLDALPHA_BLEND(14, 16),
    BLDALPHA_BLEND(13, 16),
    BLDALPHA_BLEND(12, 16),
    BLDALPHA_BLEND(11, 16),
    BLDALPHA_BLEND(10, 16),
    BLDALPHA_BLEND(9, 16),
    BLDALPHA_BLEND(8, 16),
    BLDALPHA_BLEND(7, 16),
    BLDALPHA_BLEND(6, 16),
    BLDALPHA_BLEND(5, 16),
    BLDALPHA_BLEND(4, 16),
    BLDALPHA_BLEND(3, 16),
    BLDALPHA_BLEND(2, 16),
    BLDALPHA_BLEND(1, 16),
    BLDALPHA_BLEND(0, 16),
    [32 ... 63] = BLDALPHA_BLEND(0, 16)
};

static const struct OamData sVersionBannerLeftOamData =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_8BPP,
    .shape = SPRITE_SHAPE(64x32),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(64x32),
    .tileNum = 0,
    .priority = 0,
    .paletteNum = 0,
    .affineParam = 0,
};

static const struct OamData sVersionBannerRightOamData =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_8BPP,
    .shape = SPRITE_SHAPE(64x32),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(64x32),
    .tileNum = 0,
    .priority = 0,
    .paletteNum = 0,
    .affineParam = 0,
};

static const union AnimCmd sVersionBannerLeftAnimSequence[] =
{
    ANIMCMD_FRAME(0, 30),
    ANIMCMD_END,
};

static const union AnimCmd sVersionBannerRightAnimSequence[] =
{
    ANIMCMD_FRAME(VERSION_BANNER_RIGHT_TILEOFFSET, 30),
    ANIMCMD_END,
};

static const union AnimCmd *const sVersionBannerLeftAnimTable[] =
{
    sVersionBannerLeftAnimSequence,
};

static const union AnimCmd *const sVersionBannerRightAnimTable[] =
{
    sVersionBannerRightAnimSequence,
};

static const struct SpriteTemplate sVersionBannerLeftSpriteTemplate =
{
    .tileTag = TAG_VERSION,
    .paletteTag = TAG_VERSION,
    .oam = &sVersionBannerLeftOamData,
    .anims = sVersionBannerLeftAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_VersionBannerLeft,
};

static const struct SpriteTemplate sVersionBannerRightSpriteTemplate =
{
    .tileTag = TAG_VERSION,
    .paletteTag = TAG_VERSION,
    .oam = &sVersionBannerRightOamData,
    .anims = sVersionBannerRightAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_VersionBannerRight,
};

static const struct CompressedSpriteSheet sSpriteSheet_EmeraldVersion[] =
{
    {
        .data = gTitleScreenEmeraldVersionGfx,
        .size = 0x1000,
        .tag = TAG_VERSION
    },
    {},
};

static const struct OamData sOamData_CopyrightBanner =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(32x8),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(32x8),
    .tileNum = 0,
    .priority = 0,
    .paletteNum = 0,
    .affineParam = 0,
};

static const union AnimCmd sAnim_PressStart_0[] =
{
    ANIMCMD_FRAME(1, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_PressStart_1[] =
{
    ANIMCMD_FRAME(5, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_PressStart_2[] =
{
    ANIMCMD_FRAME(9, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_PressStart_3[] =
{
    ANIMCMD_FRAME(13, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_PressStart_4[] =
{
    ANIMCMD_FRAME(17, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_Copyright_0[] =
{
    ANIMCMD_FRAME(21, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_Copyright_1[] =
{
    ANIMCMD_FRAME(25, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_Copyright_2[] =
{
    ANIMCMD_FRAME(29, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_Copyright_3[] =
{
    ANIMCMD_FRAME(33, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_Copyright_4[] =
{
    ANIMCMD_FRAME(37, 4),
    ANIMCMD_END,
};

// The "Press Start" and copyright graphics are each 5 32x8 segments long
#define NUM_PRESS_START_FRAMES 5
#define NUM_COPYRIGHT_FRAMES 5

static const union AnimCmd *const sStartCopyrightBannerAnimTable[NUM_PRESS_START_FRAMES + NUM_COPYRIGHT_FRAMES] =
{
    sAnim_PressStart_0,
    sAnim_PressStart_1,
    sAnim_PressStart_2,
    sAnim_PressStart_3,
    sAnim_PressStart_4,
    [NUM_PRESS_START_FRAMES] =
    sAnim_Copyright_0,
    sAnim_Copyright_1,
    sAnim_Copyright_2,
    sAnim_Copyright_3,
    sAnim_Copyright_4,
};

static const struct SpriteTemplate sStartCopyrightBannerSpriteTemplate =
{
    .tileTag = TAG_PRESS_START_COPYRIGHT,
    .paletteTag = TAG_PRESS_START_COPYRIGHT,
    .oam = &sOamData_CopyrightBanner,
    .anims = sStartCopyrightBannerAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_PressStartCopyrightBanner,
};

static const struct CompressedSpriteSheet sSpriteSheet_PressStart[] =
{
    {
        .data = gTitleScreenPressStartGfx,
        .size = 0x520,
        .tag = TAG_PRESS_START_COPYRIGHT
    },
    {},
};

static const struct SpritePalette sSpritePalette_PressStart[] =
{
    {
        .data = gTitleScreenPressStartPal,
        .tag = TAG_PRESS_START_COPYRIGHT
    },
    {},
};

static const struct OamData sPokemonLogoShineOamData =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(64x64),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(64x64),
    .tileNum = 0,
    .priority = 0,
    .paletteNum = 0,
    .affineParam = 0,
};

static const union AnimCmd sPokemonLogoShineAnimSequence[] =
{
    ANIMCMD_FRAME(0, 4),
    ANIMCMD_END,
};

static const union AnimCmd *const sPokemonLogoShineAnimTable[] =
{
    sPokemonLogoShineAnimSequence,
};

static const struct SpriteTemplate sPokemonLogoShineSpriteTemplate =
{
    .tileTag = TAG_LOGO_SHINE,
    .paletteTag = TAG_PRESS_START_COPYRIGHT,
    .oam = &sPokemonLogoShineOamData,
    .anims = sPokemonLogoShineAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_PokemonLogoShine,
};

static const struct CompressedSpriteSheet sPokemonLogoShineSpriteSheet[] =
{
    {
        .data = sTitleScreenLogoShineGfx,
        .size = 0x800,
        .tag = TAG_LOGO_SHINE
    },
    {},
};

// Task data for the main title screen tasks (Task_TitleScreenPhase#)
#define tCounter    data[0]
#define tSkipToNext data[1]
#define tPointless  data[2] // Incremented but never used to do anything.
#define tBg2Y       data[3]
#define tBg1Y       data[4]

// Sprite data for sVersionBannerLeftSpriteTemplate / sVersionBannerRightSpriteTemplate
#define sAlphaBlendIdx data[0]
#define sParentTaskId  data[1]

static void SpriteCB_VersionBannerLeft(struct Sprite *sprite)
{
    if (gTasks[sprite->sParentTaskId].tSkipToNext)
    {
        sprite->oam.objMode = ST_OAM_OBJ_NORMAL;
        sprite->y = VERSION_BANNER_Y_GOAL;
    }
    else
    {
        if (sprite->y != VERSION_BANNER_Y_GOAL)
            sprite->y++;
        if (sprite->sAlphaBlendIdx != 0)
            sprite->sAlphaBlendIdx--;
        SetGpuReg(REG_OFFSET_BLDALPHA, gTitleScreenAlphaBlend[sprite->sAlphaBlendIdx]);
    }
}

static void SpriteCB_VersionBannerRight(struct Sprite *sprite)
{
    if (gTasks[sprite->sParentTaskId].tSkipToNext)
    {
        sprite->oam.objMode = ST_OAM_OBJ_NORMAL;
        sprite->y = VERSION_BANNER_Y_GOAL;
    }
    else
    {
        if (sprite->y != VERSION_BANNER_Y_GOAL)
            sprite->y++;
    }
}

// Sprite data for SpriteCB_PressStartCopyrightBanner
#define sAnimate data[0]
#define sTimer   data[1]

static void SpriteCB_PressStartCopyrightBanner(struct Sprite *sprite)
{
    if (sprite->sAnimate == TRUE)
    {
        // Alternate between hidden and shown every 16th frame
        if (++sprite->sTimer & 16)
            sprite->invisible = FALSE;
        else
            sprite->invisible = TRUE;
    }
    else
    {
        sprite->invisible = FALSE;
    }
}

static void CreatePressStartBanner(s16 x, s16 y)
{
    u8 i;
    u8 spriteId;

    x -= 64;
    for (i = 0; i < NUM_PRESS_START_FRAMES; i++, x += 32)
    {
        spriteId = CreateSprite(&sStartCopyrightBannerSpriteTemplate, x, y, 0);
        StartSpriteAnim(&gSprites[spriteId], i);
        gSprites[spriteId].sAnimate = TRUE;
    }
}

static void CreateCopyrightBanner(s16 x, s16 y)
{
    u8 i;
    u8 spriteId;

    x -= 64;
    for (i = 0; i < NUM_COPYRIGHT_FRAMES; i++, x += 32)
    {
        spriteId = CreateSprite(&sStartCopyrightBannerSpriteTemplate, x, y, 0);
        StartSpriteAnim(&gSprites[spriteId], i + NUM_PRESS_START_FRAMES);
    }
}

#undef sAnimate
#undef sTimer

// Collage figures: see sOamData_CollageFigure and src/data/title_screen_collage.h
#define sCollageTimer   data[0]
#define sCollageLeaving data[1]
#define sCollageFigure  data[2]

static void LoadCollageGraphics(void)
{
    u32 i;

    for (i = 0; i < COLLAGE_FIGURE_COUNT; i++)
    {
        LoadCompressedSpriteSheet(&sCollageFigures[i].sheet);
        LoadPalette(sCollageFigures[i].pal, OBJ_PLTT_ID(sCollageFigures[i].palSlot), PLTT_SIZE_4BPP);
    }
}

static void CreateCollageFigures(void)
{
    u32 i;

    for (i = 0; i < COLLAGE_FIGURE_COUNT; i++)
    {
        const struct CollageFigure *fig = &sCollageFigures[i];
        u8 spriteId = CreateSprite(&sCollageSpriteTemplates[i], fig->x, fig->y, fig->subpriority);
        struct Sprite *sprite;

        if (spriteId == MAX_SPRITES)
            continue;
        sprite = &gSprites[spriteId];
        sprite->oam.paletteNum = fig->palSlot;
        SetSubspriteTables(sprite, fig->subsprites);
        sprite->subspriteMode = SUBSPRITES_IGNORE_PRIORITY; // every piece takes the figure's OBJ priority (2)
        sprite->sCollageFigure = i;
        sprite->sCollageTimer = 0;
        sprite->sCollageLeaving = FALSE;
        sprite->x2 = fig->dir * sCollageSlide[0];
    }
}

// Slide in from the figure's side (back row first, ease-out), and back out when the title screen
// hands over to the opening crawl (accelerating, off screen in 16 frames).
static void SpriteCB_CollageFigure(struct Sprite *sprite)
{
    const struct CollageFigure *fig = &sCollageFigures[sprite->sCollageFigure];
    s32 k;

    if (!sprite->sCollageLeaving)
    {
        k = sprite->sCollageTimer - fig->delay;
        if (k < 0)
            k = 0;
        if (k >= COLLAGE_SLIDE_FRAMES)
            k = COLLAGE_SLIDE_FRAMES;
        else
            sprite->sCollageTimer++;
        sprite->x2 = fig->dir * sCollageSlide[k];
    }
    else if (sprite->sCollageTimer < 16)
    {
        sprite->sCollageTimer++;
        sprite->x2 = fig->dir * ((sprite->sCollageTimer * sprite->sCollageTimer * 15) / 16);
    }
    else
    {
        sprite->invisible = TRUE;
    }
}

// Defines for SpriteCB_PokemonLogoShine
enum {
    SHINE_MODE_SINGLE_NO_BG_COLOR,
    SHINE_MODE_DOUBLE,
    SHINE_MODE_SINGLE,
};

#define SHINE_SPEED  4

#define sMode     data[0]
#define sBgColor  data[1]

static void SpriteCB_PokemonLogoShine(struct Sprite *sprite)
{
    if (sprite->x < DISPLAY_WIDTH + 32)
    {
        // In any mode except SHINE_MODE_SINGLE_NO_BG_COLOR the background
        // color will change, in addition to the shine sprite moving.
        if (sprite->sMode != SHINE_MODE_SINGLE_NO_BG_COLOR)
        {
            u16 backgroundColor;

            if (sprite->x < DISPLAY_WIDTH / 2)
            {
                // Brighten background color
                if (sprite->sBgColor < 31)
                    sprite->sBgColor++;
                if (sprite->sBgColor < 31)
                    sprite->sBgColor++;
            }
            else
            {
                // Darken background color
                if (sprite->sBgColor != 0)
                    sprite->sBgColor--;
                if (sprite->sBgColor != 0)
                    sprite->sBgColor--;
            }

            backgroundColor = _RGB(sprite->sBgColor, sprite->sBgColor, sprite->sBgColor);

            // Flash the background for 4 frames of movement: Kyber Blue #58C8F8, the title theme's accent
            // (wiki/bible/PALETTE.md); Emerald flashed green here. Otherwise use the updating color.
            if (sprite->x == DISPLAY_WIDTH / 2 + (3 * SHINE_SPEED)
             || sprite->x == DISPLAY_WIDTH / 2 + (4 * SHINE_SPEED)
             || sprite->x == DISPLAY_WIDTH / 2 + (5 * SHINE_SPEED)
             || sprite->x == DISPLAY_WIDTH / 2 + (6 * SHINE_SPEED))
                gPlttBufferFaded[0] = RGB(11, 25, 31);
            else
                gPlttBufferFaded[0] = backgroundColor;
        }

        sprite->x += SHINE_SPEED;
    }
    else
    {
        // Sprite has moved fully offscreen
        gPlttBufferFaded[0] = RGB_BLACK;
        DestroySprite(sprite);
    }
}

static void SpriteCB_PokemonLogoShine_Fast(struct Sprite *sprite)
{
    if (sprite->x < DISPLAY_WIDTH + 32)
        sprite->x += SHINE_SPEED * 2;
    else
        DestroySprite(sprite);
}

static void StartPokemonLogoShine(u8 mode)
{
    u8 spriteId;

    switch (mode)
    {
    case SHINE_MODE_SINGLE_NO_BG_COLOR:
    case SHINE_MODE_SINGLE:
        // Create one regular shine sprite.
        // If mode is SHINE_MODE_SINGLE it will also change the background color.
        spriteId = CreateSprite(&sPokemonLogoShineSpriteTemplate, 0, 68, 0);
        gSprites[spriteId].oam.objMode = ST_OAM_OBJ_WINDOW;
        gSprites[spriteId].sMode = mode;
        break;
    case SHINE_MODE_DOUBLE:
        // Create an invisible sprite with mode set to update the background color
        spriteId = CreateSprite(&sPokemonLogoShineSpriteTemplate, 0, 68, 0);
        gSprites[spriteId].oam.objMode = ST_OAM_OBJ_WINDOW;
        gSprites[spriteId].sMode = mode;
        gSprites[spriteId].invisible = TRUE;

        // Create two faster shine sprites
        spriteId = CreateSprite(&sPokemonLogoShineSpriteTemplate, 0, 68, 0);
        gSprites[spriteId].callback = SpriteCB_PokemonLogoShine_Fast;
        gSprites[spriteId].oam.objMode = ST_OAM_OBJ_WINDOW;

        spriteId = CreateSprite(&sPokemonLogoShineSpriteTemplate, -80, 68, 0);
        gSprites[spriteId].callback = SpriteCB_PokemonLogoShine_Fast;
        gSprites[spriteId].oam.objMode = ST_OAM_OBJ_WINDOW;
        break;
    }
}

#undef sMode
#undef sBgColor

static void VBlankCB(void)
{
    ScanlineEffect_InitHBlankDmaTransfer();
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
    SetGpuReg(REG_OFFSET_BG1VOFS, gBattle_BG1_Y);
}

void CB2_InitTitleScreen(void)
{
    switch (gMain.state)
    {
    default:
    case 0:
        SetVBlankCallback(NULL);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 0);
        *((u16 *)PLTT) = RGB_WHITE;
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        SetGpuReg(REG_OFFSET_BG2CNT, 0);
        SetGpuReg(REG_OFFSET_BG1CNT, 0);
        SetGpuReg(REG_OFFSET_BG0CNT, 0);
        SetGpuReg(REG_OFFSET_BG2HOFS, 0);
        SetGpuReg(REG_OFFSET_BG2VOFS, 0);
        SetGpuReg(REG_OFFSET_BG1HOFS, 0);
        SetGpuReg(REG_OFFSET_BG1VOFS, 0);
        SetGpuReg(REG_OFFSET_BG0HOFS, 0);
        SetGpuReg(REG_OFFSET_BG0VOFS, 0);
        DmaFill16(3, 0, (void *)VRAM, VRAM_SIZE);
        DmaFill32(3, 0, (void *)OAM, OAM_SIZE);
        DmaFill16(3, 0, (void *)(PLTT + 2), PLTT_SIZE - 2);
        ResetPaletteFade();
        gMain.state = 1;
        break;
    case 1:
        // bg2
        LZ77UnCompVram(gTitleScreenPokemonLogoGfx, (void *)(BG_CHAR_ADDR(0)));
        LZ77UnCompVram(gTitleScreenPokemonLogoTilemap, (void *)(BG_SCREEN_ADDR(9)));
        LoadPalette(gTitleScreenBgPalettes, BG_PLTT_ID(0), 15 * PLTT_SIZE_4BPP);
        // bg0: the foreground ridge the collage figures stand behind (was Rayquaza)
        LZ77UnCompVram(sTitleScreenRayquazaGfx, (void *)(BG_CHAR_ADDR(2)));
        LZ77UnCompVram(sTitleScreenRayquazaTilemap, (void *)(BG_SCREEN_ADDR(26)));
        // bg1
        LZ77UnCompVram(sTitleScreenCloudsGfx, (void *)(BG_CHAR_ADDR(3)));
        LZ77UnCompVram(gTitleScreenCloudsTilemap, (void *)(BG_SCREEN_ADDR(27)));
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        FreeAllSpritePalettes();
        gReservedSpritePaletteCount = 9;
        LoadCompressedSpriteSheet(&sSpriteSheet_EmeraldVersion[0]);
        LoadCompressedSpriteSheet(&sSpriteSheet_PressStart[0]);
        LoadCompressedSpriteSheet(&sPokemonLogoShineSpriteSheet[0]);
        LoadPalette(gTitleScreenEmeraldVersionPal, OBJ_PLTT_ID(0), PLTT_SIZE_4BPP);
        LoadSpritePalette(&sSpritePalette_PressStart[0]);
        LoadCollageGraphics();
        gMain.state = 2;
        break;
    case 2:
    {
        u8 taskId = CreateTask(Task_TitleScreenPhase1, 0);

        gTasks[taskId].tCounter = 256;
        gTasks[taskId].tSkipToNext = FALSE;
        gTasks[taskId].tPointless = -16;
        gTasks[taskId].tBg2Y = -32;
        gMain.state = 3;
        break;
    }
    case 3:
        BeginNormalPaletteFade(PALETTES_ALL, 1, 16, 0, RGB_WHITEALPHA);
        SetVBlankCallback(VBlankCB);
        gMain.state = 4;
        break;
    case 4:
        PanFadeAndZoomScreen(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2, 0x100, 0);
        SetGpuReg(REG_OFFSET_BG2X_L, -29 * 256);
        SetGpuReg(REG_OFFSET_BG2X_H, -1);
        SetGpuReg(REG_OFFSET_BG2Y_L, -32 * 256);
        SetGpuReg(REG_OFFSET_BG2Y_H, -1);
        SetGpuReg(REG_OFFSET_WIN0H, 0);
        SetGpuReg(REG_OFFSET_WIN0V, 0);
        SetGpuReg(REG_OFFSET_WIN1H, 0);
        SetGpuReg(REG_OFFSET_WIN1V, 0);
        SetGpuReg(REG_OFFSET_WININ, WININ_WIN0_BG_ALL | WININ_WIN0_OBJ | WININ_WIN1_BG_ALL | WININ_WIN1_OBJ);
        SetGpuReg(REG_OFFSET_WINOUT, WINOUT_WIN01_BG_ALL | WINOUT_WIN01_OBJ | WINOUT_WINOBJ_ALL);
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG2 | BLDCNT_EFFECT_LIGHTEN);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 12);
        // BG0 (ridge) is priority 1 like the logo, so it covers the collage figures (OBJ priority 2)
        SetGpuReg(REG_OFFSET_BG0CNT, BGCNT_PRIORITY(1) | BGCNT_CHARBASE(2) | BGCNT_SCREENBASE(26) | BGCNT_16COLOR | BGCNT_TXT256x256);
        SetGpuReg(REG_OFFSET_BG1CNT, BGCNT_PRIORITY(2) | BGCNT_CHARBASE(3) | BGCNT_SCREENBASE(27) | BGCNT_16COLOR | BGCNT_TXT256x256);
        SetGpuReg(REG_OFFSET_BG2CNT, BGCNT_PRIORITY(1) | BGCNT_CHARBASE(0) | BGCNT_SCREENBASE(9) | BGCNT_256COLOR | BGCNT_AFF256x256);
        EnableInterrupts(INTR_FLAG_VBLANK);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1
                                    | DISPCNT_OBJ_1D_MAP
                                    | DISPCNT_BG2_ON
                                    | DISPCNT_OBJ_ON
                                    | DISPCNT_WIN0_ON
                                    | DISPCNT_OBJWIN_ON);
        m4aSongNumStart(MUS_TITLE);
        gMain.state = 5;
        break;
    case 5:
        if (!UpdatePaletteFade())
        {
            StartPokemonLogoShine(SHINE_MODE_SINGLE_NO_BG_COLOR);
            ScanlineEffect_InitWave(0, DISPLAY_HEIGHT, 4, 4, 0, SCANLINE_EFFECT_REG_BG1HOFS, TRUE);
            SetMainCallback2(MainCB2);
        }
        break;
    }
}

static void MainCB2(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

// Shine the Pokémon logo two more times, and fade in the version banner
static void Task_TitleScreenPhase1(u8 taskId)
{
    // Skip to next phase when A, B, Start, or Select is pressed
    if (JOY_NEW(A_B_START_SELECT) || gTasks[taskId].tSkipToNext)
    {
        gTasks[taskId].tSkipToNext = TRUE;
        gTasks[taskId].tCounter = 0;
    }

    if (gTasks[taskId].tCounter != 0)
    {
        u16 frameNum = gTasks[taskId].tCounter;
        if (frameNum == 176)
            StartPokemonLogoShine(SHINE_MODE_DOUBLE);
        else if (frameNum == 64)
            StartPokemonLogoShine(SHINE_MODE_SINGLE);

        gTasks[taskId].tCounter--;
    }
    else
    {
        u8 spriteId;

        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1 | DISPCNT_OBJ_1D_MAP | DISPCNT_BG2_ON | DISPCNT_OBJ_ON);
        SetGpuReg(REG_OFFSET_WININ, 0);
        SetGpuReg(REG_OFFSET_WINOUT, 0);
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_OBJ | BLDCNT_EFFECT_BLEND | BLDCNT_TGT2_ALL);
        SetGpuReg(REG_OFFSET_BLDALPHA, BLDALPHA_BLEND(16, 0));
        SetGpuReg(REG_OFFSET_BLDY, 0);

        // Create left side of version banner
        spriteId = CreateSprite(&sVersionBannerLeftSpriteTemplate, VERSION_BANNER_LEFT_X, VERSION_BANNER_Y, 0);
        gSprites[spriteId].sAlphaBlendIdx = ARRAY_COUNT(gTitleScreenAlphaBlend);
        gSprites[spriteId].sParentTaskId = taskId;

        // Create right side of version banner
        spriteId = CreateSprite(&sVersionBannerRightSpriteTemplate, VERSION_BANNER_RIGHT_X, VERSION_BANNER_Y, 0);
        gSprites[spriteId].sParentTaskId = taskId;

        gTasks[taskId].tCounter = 144;
        gTasks[taskId].func = Task_TitleScreenPhase2;
    }
}

#undef sParentTaskId
#undef sAlphaBlendIdx

// Create "Press Start" and copyright banners, and slide Pokémon logo up
static void Task_TitleScreenPhase2(u8 taskId)
{
    u32 yPos;

    // Skip to next phase when A, B, Start, or Select is pressed
    if (JOY_NEW(A_B_START_SELECT) || gTasks[taskId].tSkipToNext)
    {
        gTasks[taskId].tSkipToNext = TRUE;
        gTasks[taskId].tCounter = 0;
    }

    if (gTasks[taskId].tCounter != 0)
    {
        gTasks[taskId].tCounter--;
    }
    else
    {
        gTasks[taskId].tSkipToNext = TRUE;
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG1 | BLDCNT_EFFECT_BLEND | BLDCNT_TGT2_BG0 | BLDCNT_TGT2_BD);
        SetGpuReg(REG_OFFSET_BLDALPHA, BLDALPHA_BLEND(6, 15));
        SetGpuReg(REG_OFFSET_BLDY, 0);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1
                                    | DISPCNT_OBJ_1D_MAP
                                    | DISPCNT_BG0_ON
                                    | DISPCNT_BG1_ON
                                    | DISPCNT_BG2_ON
                                    | DISPCNT_OBJ_ON);
        CreatePressStartBanner(START_BANNER_X, 108);
        CreateCopyrightBanner(START_BANNER_X, 148);
        CreateCollageFigures();
        gTasks[taskId].tBg1Y = 0;
        gTasks[taskId].func = Task_TitleScreenPhase3;
    }

    if (!(gTasks[taskId].tCounter & 3) && gTasks[taskId].tPointless != 0)
        gTasks[taskId].tPointless++;
    if (!(gTasks[taskId].tCounter & 1) && gTasks[taskId].tBg2Y != 0)
        gTasks[taskId].tBg2Y++;

    // Slide Pokémon logo up
    yPos = gTasks[taskId].tBg2Y * 256;
    SetGpuReg(REG_OFFSET_BG2Y_L, yPos);
    SetGpuReg(REG_OFFSET_BG2Y_H, yPos / 0x10000);

    gTasks[taskId].data[5] = 15; // Unused
    gTasks[taskId].data[6] = 6;  // Unused
}

// Clouds, ridge and the character collage are up; process main title screen input
static void Task_TitleScreenPhase3(u8 taskId)
{
    if ((JOY_NEW(A_BUTTON) || JOY_NEW(START_BUTTON)) && IntroCrawl_ShouldPlay())
    {
        // First boot with no save: send the logo off into space, then the opening crawl.
        // The crawl theme starts now, on the logo, like the film's main title.
        IntroCrawl_StartMusic();
        StartTitleScreenCrawlOut(taskId);
    }
    else if (JOY_NEW(A_BUTTON) || JOY_NEW(START_BUTTON))
    {
        FadeOutBGM(4);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_WHITEALPHA);
        SetMainCallback2(CB2_GoToMainMenu);
    }
    else if (JOY_HELD(CLEAR_SAVE_BUTTON_COMBO) == CLEAR_SAVE_BUTTON_COMBO)
    {
        SetMainCallback2(CB2_GoToClearSaveDataScreen);
    }
    else if (JOY_HELD(RESET_RTC_BUTTON_COMBO) == RESET_RTC_BUTTON_COMBO
      && CanResetRTC() == TRUE)
    {
        FadeOutBGM(4);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        SetMainCallback2(CB2_GoToResetRtcScreen);
    }
    else if (JOY_HELD(BERRY_UPDATE_BUTTON_COMBO) == BERRY_UPDATE_BUTTON_COMBO)
    {
        FadeOutBGM(4);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        SetMainCallback2(CB2_GoToBerryFixScreen);
    }
    else
    {
        SetGpuReg(REG_OFFSET_BG2Y_L, 0);
        SetGpuReg(REG_OFFSET_BG2Y_H, 0);
        if (++gTasks[taskId].tCounter & 1)
        {
            gTasks[taskId].tBg1Y++;
            gBattle_BG1_Y = gTasks[taskId].tBg1Y / 2;
            gBattle_BG1_X = 0;
        }
        UpdateLegendaryMarkingColor(gTasks[taskId].tCounter);
        if ((gMPlayInfo_BGM.status & 0xFFFF) == 0)
        {
            BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_WHITEALPHA);
            SetMainCallback2(CB2_GoToCopyrightScreen);
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Hand-off to the opening crawl (intro_crawl.c), first boot only.
// The character collage slides back out to the sides while the clouds (BG1) blend out, then the
// foreground ridge (BG0) sinks below the bottom edge. Only then do the logo (BG2, affine) and the
// KYBER VERSION banner (OBJ) shrink away into the distance and darken. What is left is the night
// backdrop, which the crawl keeps on screen.
// BG1 is still pointed at screen 28 (intro_crawl.c keeps showing it): it is built from BG0's plain
// sky tiles, and since BG0 now holds only the ridge (no gradient), every row falls back to BG0's
// blank tile 0, so the crawl starts on the flat backdrop the title screen shows.
// ---------------------------------------------------------------------------------------------

#define CRAWL_OUT_LOGO_FRAMES   180  // logo shrink, after the creature and clouds are gone
#define CRAWL_OUT_CENTER_X      120  // screen point the logo shrinks towards
#define CRAWL_OUT_CENTER_Y      56
#define CRAWL_OUT_LOGO_TEX_X    (-29) // BG2X the title screen draws the logo with
#define CRAWL_OUT_RECEDE        15   // 1/scale grows by this/256 per frame (logo is ~1/11 size at the end)
#define CRAWL_OUT_LOGO_FADE_AT  100  // logo frame the logo starts darkening
#define CRAWL_OUT_CLOUDS_END    12   // clouds fully blended out by this frame
#define CRAWL_OUT_CREATURE_END  40   // ridge (and collage) gone by this frame; the logo starts shrinking here
#define CRAWL_OUT_FRAMES        (CRAWL_OUT_CREATURE_END + CRAWL_OUT_LOGO_FRAMES)
#define CRAWL_OUT_SKY_SCREEN    28   // screen block for the cloudless gradient map (intro_crawl.c uses it too)
#define CRAWL_OUT_SKY_CHARBASE  2    // BG0's tiles (the ridge; tile 0 is blank)
#define CRAWL_OUT_RIDGE_DROP    24   // px the ridge sinks while the collage leaves

#define tOutFrame data[5]

// BG0 tile (map entry) drawn only in the gradient's colours (palette 14 indices 4-10, see
// tools/title-screen-generator/bg_round.py), so it holds no part of the creature.
static bool8 IsPlainSkyTile(u16 entry)
{
    const u8 *tile = (const u8 *)(BG_CHAR_ADDR(CRAWL_OUT_SKY_CHARBASE) + (entry & 0x3FF) * 32);
    u16 i;

    for (i = 0; i < 32; i++)
    {
        u8 lo = tile[i] & 0xF;
        u8 hi = tile[i] >> 4;
        if (lo < 4 || lo > 10 || hi < 4 || hi > 10)
            return FALSE;
    }
    return TRUE;
}

static void StartTitleScreenCrawlOut(u8 taskId)
{
    u16 i;

    for (i = 0; i < MAX_SPRITES; i++)
    {
        struct Sprite *sprite = &gSprites[i];
        if (!sprite->inUse)
            continue;
        if (sprite->template == &sStartCopyrightBannerSpriteTemplate)
        {
            // "Press Start" and copyright go straight away
            sprite->callback = SpriteCallbackDummy;
            sprite->invisible = TRUE;
        }
        else if (sprite->callback == SpriteCB_CollageFigure)
        {
            // The collage slides back out to the sides
            sprite->sCollageLeaving = TRUE;
            sprite->sCollageTimer = 0;
        }
        else if (sprite->template == &sVersionBannerLeftSpriteTemplate
              || sprite->template == &sVersionBannerRightSpriteTemplate)
        {
            // The version banner shrinks with the logo
            sprite->oam.affineMode = ST_OAM_AFFINE_NORMAL;
            sprite->oam.matrixNum = 0;
        }
    }
    SetOamMatrix(0, 0x100, 0, 0, 0x100);
    gTasks[taskId].tOutFrame = 0;
    gTasks[taskId].func = Task_TitleScreenCrawlOut;
}

static void Task_TitleScreenCrawlOut(u8 taskId)
{
    s32 frame = gTasks[taskId].tOutFrame;
    s32 logoFrame = (frame > CRAWL_OUT_CREATURE_END) ? frame - CRAWL_OUT_CREATURE_END : 0;
    s32 invScale = 0x100 + logoFrame * CRAWL_OUT_RECEDE; // texture px per screen px, 8.8
    s32 bgX, bgY;
    u16 i;

    // Logo: scale BG2 about CRAWL_OUT_CENTER
    bgX = ((CRAWL_OUT_CENTER_X + CRAWL_OUT_LOGO_TEX_X) << 8) - invScale * CRAWL_OUT_CENTER_X;
    bgY = (CRAWL_OUT_CENTER_Y << 8) - invScale * CRAWL_OUT_CENTER_Y;
    SetGpuReg(REG_OFFSET_BG2PA, invScale);
    SetGpuReg(REG_OFFSET_BG2PD, invScale);
    SetGpuReg(REG_OFFSET_BG2X_L, bgX);
    SetGpuReg(REG_OFFSET_BG2X_H, bgX >> 16);
    SetGpuReg(REG_OFFSET_BG2Y_L, bgY);
    SetGpuReg(REG_OFFSET_BG2Y_H, bgY >> 16);

    // Version banner: same scale, and slide each half towards the centre
    SetOamMatrix(0, invScale, 0, 0, invScale);
    for (i = 0; i < MAX_SPRITES; i++)
    {
        struct Sprite *sprite = &gSprites[i];
        if (sprite->inUse && sprite->oam.affineMode == ST_OAM_AFFINE_NORMAL)
        {
            sprite->x2 = ((sprite->x - CRAWL_OUT_CENTER_X) * 0x100) / invScale - (sprite->x - CRAWL_OUT_CENTER_X);
            sprite->y2 = ((sprite->y - CRAWL_OUT_CENTER_Y) * 0x100) / invScale - (sprite->y - CRAWL_OUT_CENTER_Y);
        }
    }

    // Darken the logo (BG palettes 0-13, skipping the backdrop colour) and the banner (OBJ palette 0)
    if (logoFrame >= CRAWL_OUT_LOGO_FADE_AT)
    {
        u8 coeff = ((logoFrame - CRAWL_OUT_LOGO_FADE_AT) * 16) / (CRAWL_OUT_LOGO_FRAMES - CRAWL_OUT_LOGO_FADE_AT);
        BlendPalette(BG_PLTT_ID(0) + 1, 14 * 16 - 1, coeff, RGB_BLACK);
        BlendPalette(OBJ_PLTT_ID(0), 16, coeff, RGB_BLACK);
    }

    // Clouds: keep drifting while BG1's blend weight drops from 6 to 0
    if (frame < CRAWL_OUT_CLOUDS_END)
    {
        if (++gTasks[taskId].tCounter & 1)
        {
            gTasks[taskId].tBg1Y++;
            gBattle_BG1_Y = gTasks[taskId].tBg1Y / 2;
        }
        SetGpuReg(REG_OFFSET_BLDALPHA, BLDALPHA_BLEND(6 - (frame * 6) / CRAWL_OUT_CLOUDS_END, 15));
    }
    else if (frame == CRAWL_OUT_CLOUDS_END)
    {
        // Clouds are invisible now. Point BG1 at the gradient with the creature taken out:
        // each tile row of BG0 is filled with one of its own plain-gradient tiles.
        u16 *src = (u16 *)BG_SCREEN_ADDR(26);
        u16 *dst = (u16 *)BG_SCREEN_ADDR(CRAWL_OUT_SKY_SCREEN);
        u16 x, y, sky = src[0];

        ScanlineEffect_Stop();
        for (y = 0; y < 32; y++)
        {
            if (y < DISPLAY_HEIGHT / 8)
            {
                for (x = 0; x < 32; x++)
                {
                    if (IsPlainSkyTile(src[y * 32 + x]))
                    {
                        sky = src[y * 32 + x];
                        break;
                    }
                }
            }
            for (x = 0; x < 32; x++)
                dst[y * 32 + x] = sky;
        }
        gBattle_BG1_X = 0;
        gBattle_BG1_Y = 0;
        SetGpuReg(REG_OFFSET_BG1HOFS, 0);
        SetGpuReg(REG_OFFSET_BLDALPHA, BLDALPHA_BLEND(0, 16));
        SetGpuReg(REG_OFFSET_BG1CNT, BGCNT_PRIORITY(2) | BGCNT_CHARBASE(CRAWL_OUT_SKY_CHARBASE) | BGCNT_SCREENBASE(CRAWL_OUT_SKY_SCREEN) | BGCNT_16COLOR | BGCNT_TXT256x256);
    }
    else if (frame <= CRAWL_OUT_CREATURE_END)
    {
        u8 eva;
        // The ridge (BG0) sinks below the bottom edge
        SetGpuReg(REG_OFFSET_BG0VOFS, -(((frame - CRAWL_OUT_CLOUDS_END) * CRAWL_OUT_RIDGE_DROP) / (CRAWL_OUT_CREATURE_END - CRAWL_OUT_CLOUDS_END)));
        // Cross-fade the (now blank) sky screen (BG1) over BG0; the ridge sinks meanwhile
        eva = ((frame - CRAWL_OUT_CLOUDS_END) * 16) / (CRAWL_OUT_CREATURE_END - CRAWL_OUT_CLOUDS_END);
        SetGpuReg(REG_OFFSET_BLDALPHA, BLDALPHA_BLEND(eva, 16 - eva));
        if (frame == CRAWL_OUT_CREATURE_END)
        {
            SetGpuReg(REG_OFFSET_BLDCNT, 0);
            SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1 | DISPCNT_OBJ_1D_MAP | DISPCNT_BG1_ON | DISPCNT_BG2_ON | DISPCNT_OBJ_ON);
            SetGpuReg(REG_OFFSET_BG0VOFS, 0);
        }
    }

    if (++gTasks[taskId].tOutFrame > CRAWL_OUT_FRAMES)
    {
        // Logo is a speck and fully dark: drop it and hand over to the crawl
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1 | DISPCNT_BG1_ON);
        SetGpuReg(REG_OFFSET_BG2PA, 0x100);
        SetGpuReg(REG_OFFSET_BG2PD, 0x100);
        DestroyTask(taskId);
        SetMainCallback2(CB2_InitIntroCrawl);
    }
}

#undef tOutFrame

static void CB2_GoToMainMenu(void)
{
    if (!UpdatePaletteFade())
        SetMainCallback2(CB2_InitMainMenu);
}

static void CB2_GoToCopyrightScreen(void)
{
    if (!UpdatePaletteFade())
        SetMainCallback2(CB2_InitCopyrightScreenAfterTitleScreen);
}

static void CB2_GoToClearSaveDataScreen(void)
{
    if (!UpdatePaletteFade())
        SetMainCallback2(CB2_InitClearSaveDataScreen);
}

static void CB2_GoToResetRtcScreen(void)
{
    if (!UpdatePaletteFade())
        SetMainCallback2(CB2_InitResetRtcScreen);
}

static void CB2_GoToBerryFixScreen(void)
{
    if (!UpdatePaletteFade())
    {
        m4aMPlayAllStop();
        SetMainCallback2(CB2_InitBerryFixProgram);
    }
}

static void UpdateLegendaryMarkingColor(u8 frameNum)
{
    if ((frameNum % 4) == 0) // Change color every 4th frame
    {
        s32 intensity = Cos(frameNum, Q_8_8(0.5)) + Q_8_8(0.5);
        u32 r = 31 - Q_8_8_TO_INT(intensity * 31);
        u32 g = 31 - Q_8_8_TO_INT(intensity * 22);
        u32 b = 12;

        u16 color = RGB(r, g, b);
        LoadPalette(&color, BG_PLTT_ID(14) + 15, sizeof(color));
   }
}

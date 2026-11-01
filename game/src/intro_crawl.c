// One-time opening crawl, shown after the title screen when there is no save file.
//
// The title screen (title_screen.c) shrinks the logo away and fades out the creature and clouds,
// leaving only the deep-space gradient on BG1. It then hands off to CB2_InitIntroCrawl, which:
//   BG0  text BG    the "Skip intro? YES / NO" dialog (standard window frame + YES/NO menu)
//   BG1  text BG    the deep-space gradient, left in VRAM by the title screen (charblock 2, screen 28)
//   BG2  affine     the crawl. 8bpp, 512x512 with wraparound. Every scanline gets its own affine
//                   scale/offset through an HBlank DMA, which tilts the text back into the distance.
//                   An HBlank IRQ darkens the far lines so the text fades out near the horizon.
//
// The text is printed with the game's own font into a scratch window that is never put on screen,
// then converted from 4bpp to 8bpp tiles into a ring of 16 tile rows (8 text lines) on BG2.
// Lines are drawn into the ring just before they scroll in at the bottom.
//
// A, B or Start (the buttons that advance dialogue in text.c, plus Start) pauses the crawl and asks
// "Skip intro?" with the cursor on NO. NO / B resumes, YES fades out to the main menu.

#include "global.h"
#include "intro_crawl.h"
#include "bg.h"
#include "gpu_regs.h"
#include "main.h"
#include "main_menu.h"
#include "menu.h"
#include "palette.h"
#include "save.h"
#include "sound.h"
#include "sprite.h"
#include "task.h"
#include "text.h"
#include "text_window.h"
#include "window.h"
#include "constants/rgb.h"
#include "constants/songs.h"
#include "scanline_effect.h"
#include "title_screen.h"
#include "util.h"

// Set to a song constant once the crawl theme exists. MUS_NONE plays nothing.
#define CRAWL_MUSIC MUS_NONE

// Screen layout
#define CRAWL_TOP           60   // first scanline the crawl is drawn on (WIN0 hides BG2 above this)
#define CRAWL_HORIZON       30   // vanishing line: scale = CRAWL_SCALE_K / (y - CRAWL_HORIZON)
#define CRAWL_SCALE_K       71   // texture px per screen px is 0.55 at the bottom line, 2.4 at the top
#define CRAWL_FADE_LINES    32   // lines below CRAWL_TOP over which the text darkens to black
#define CRAWL_SPEED         34   // texture px per frame, 8.8 fixed point (about one text line per 2 s)
#define CRAWL_END_HOLD      60   // frames to wait after the last line has gone

// Text ring on BG2
#define CRAWL_TEX_W_TILES   15                       // 120px of text per line
#define CRAWL_TEX_CENTER_X  (CRAWL_TEX_W_TILES * 4)  // texture x shown at the screen's centre
#define CRAWL_RING_ROWS     16                       // tile rows in the ring (16 * 15 + 1 = 241 tiles)
#define CRAWL_LINE_H        16                       // texture px per text line (2 tile rows)
#define CRAWL_RING_H        (CRAWL_RING_ROWS * 8)

// VRAM
#define CRAWL_BG2_CHARBASE  0
#define CRAWL_BG2_SCREEN    30  // 512x512 affine map: screens 30-31
#define CRAWL_BG1_CHARBASE  2   // must match title_screen.c
#define CRAWL_BG1_SCREEN    28  // must match title_screen.c
#define CRAWL_BG0_CHARBASE  1
#define CRAWL_BG0_SCREEN    29

// Palettes
#define CRAWL_TEXT_COLOR    RGB(30, 25, 6)    // crawl yellow
#define CRAWL_SHADOW_COLOR  RGB(17, 13, 2)
#define FRAME_PAL           13
#define TEXT_PAL            15                 // 14 is the gradient (title screen)

// BG0 tiles
#define FRAME_TILE          2
enum {
    WIN_MSG,
    WIN_SCRATCH,
};

struct CrawlLineRegs
{
    s16 pa, pb, pc, pd;
    s32 x, y;
};

// One entry per scanline, plus one: the HBlank DMA after line 159 also reads an entry.
#define CRAWL_NUM_LINES (DISPLAY_HEIGHT + 1)

static EWRAM_DATA struct CrawlLineRegs sLineRegs[2][CRAWL_NUM_LINES] = {0};
static EWRAM_DATA s16 sLineScale[DISPLAY_HEIGHT] = {0};
static EWRAM_DATA s32 sLineDepth[DISPLAY_HEIGHT] = {0};   // 8.8, texture px from the bottom line
static EWRAM_DATA u8 sLineFade[CRAWL_NUM_LINES] = {0};
static EWRAM_DATA u16 sTileBuffer[CRAWL_TEX_W_TILES * 32] = {0};
static EWRAM_DATA s32 sScroll = 0;      // texture y at the bottom scanline, 8.8
static EWRAM_DATA s32 sDepth = 0;       // texture px between the bottom and top scanline, 8.8
static EWRAM_DATA u8 sReadyBuffer = 0;  // buffer the next VBlank hands to the DMA
static EWRAM_DATA u16 sNextLine = 0;    // next text line to draw into the ring
static EWRAM_DATA bool8 sPlayedThisBoot = FALSE;

static void CB2_IntroCrawl(void);
static void VBlankCB_IntroCrawl(void);
static void HBlankCB_IntroCrawl(void);
static void Task_IntroCrawl(u8 taskId);
static void Task_IntroCrawlAskSkip(u8 taskId);
static void Task_IntroCrawlSkipChoice(u8 taskId);
static void Task_IntroCrawlFadeOut(u8 taskId);
static void Task_IntroCrawlExit(u8 taskId);
static void BuildLineRegs(void);
static void DrawRingLine(u16 line);

// ---------------------------------------------------------------------------------------------
// Text. Each entry is one centred line, at most 120px wide in FONT_NORMAL (about 20 characters;
// wrapped with the font's glyph widths). An empty string is a blank line. Set ~2 BBY, see
// wiki/bible/STORY.md. No apostrophes: the charmap has none for the normal font.
// ---------------------------------------------------------------------------------------------

static const u8 sText_L00[] = _("EPISODE I");
static const u8 sText_L01[] = _("");
static const u8 sText_L02[] = _("THE OUTER RIM");
static const u8 sText_L03[] = _("");
static const u8 sText_L04[] = _("It is a time of fear.");
static const u8 sText_L05[] = _("Seventeen years after");
static const u8 sText_L06[] = _("the fall of the Jedi,");
static const u8 sText_L07[] = _("the EMPIRE rules the");
static const u8 sText_L08[] = _("Core worlds, and many");
static const u8 sText_L09[] = _("families flee to the");
static const u8 sText_L10[] = _("distant OUTER RIM.");
static const u8 sText_L11[] = _("");
static const u8 sText_L12[] = _("Far from the Emperor,");
static const u8 sText_L13[] = _("the dark lord VADER");
static const u8 sText_L14[] = _("and the crime lord");
static const u8 sText_L15[] = _("JABBA are each");
static const u8 sText_L16[] = _("hunting an ancient");
static const u8 sText_L17[] = _("titan with the power");
static const u8 sText_L18[] = _("to reshape whole");
static const u8 sText_L19[] = _("planets.");
static const u8 sText_L20[] = _("");
static const u8 sText_L21[] = _("On the desert world of");
static const u8 sText_L22[] = _("TATOOINE, a young");
static const u8 sText_L23[] = _("newcomer steps off a");
static const u8 sText_L24[] = _("cargo freighter,");
static const u8 sText_L25[] = _("unaware that the");
static const u8 sText_L26[] = _("Force has other");
static const u8 sText_L27[] = _("plans....");

static const u8 *const sCrawlLines[] =
{
    sText_L00, sText_L01, sText_L02, sText_L03, sText_L04, sText_L05,
    sText_L06, sText_L07, sText_L08, sText_L09, sText_L10, sText_L11,
    sText_L12, sText_L13, sText_L14, sText_L15, sText_L16, sText_L17,
    sText_L18, sText_L19, sText_L20, sText_L21, sText_L22, sText_L23,
    sText_L24, sText_L25, sText_L26, sText_L27,
};

static const u8 sText_SkipIntro[] = _("Skip intro?");

// ---------------------------------------------------------------------------------------------

static const struct BgTemplate sBgTemplates[] =
{
    {
        .bg = 0,
        .charBaseIndex = CRAWL_BG0_CHARBASE,
        .mapBaseIndex = CRAWL_BG0_SCREEN,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0,
    },
};

static const struct WindowTemplate sWindowTemplates[] =
{
    [WIN_MSG] = {
        .bg = 0,
        .tilemapLeft = 3,
        .tilemapTop = 15,
        .width = 24,
        .height = 4,
        .paletteNum = TEXT_PAL,
        .baseBlock = 20,
    },
    // Never shown: the crawl text is printed here, then copied into BG2's 8bpp ring.
    [WIN_SCRATCH] = {
        .bg = 0,
        .tilemapLeft = 0,
        .tilemapTop = 0,
        .width = CRAWL_TEX_W_TILES,
        .height = 2,
        .paletteNum = TEXT_PAL,
        .baseBlock = 120,
    },
    DUMMY_WIN_TEMPLATE
};

static const struct WindowTemplate sYesNoTemplate =
{
    .bg = 0,
    .tilemapLeft = 21,
    .tilemapTop = 9,
    .width = 5,
    .height = 4,
    .paletteNum = TEXT_PAL,
    .baseBlock = 160,
};

// bg, fg, shadow: indices into BG palette 0, which BG2 reads as 8bpp.
static const u8 sCrawlTextColors[] = {0, 1, 2};

bool8 IntroCrawl_ShouldPlay(void)
{
    return gSaveFileStatus == SAVE_STATUS_EMPTY && !sPlayedThisBoot;
}

void CB2_InitIntroCrawl(void)
{
    u16 i;
    u16 *map;

    switch (gMain.state)
    {
    case 0:
        // The title screen left BG1 (gradient) on screen. Keep it up and build everything else
        // behind it, so the hand-off has no blank frame.
        sPlayedThisBoot = TRUE;
        SetVBlankCallback(NULL);
        SetHBlankCallback(NULL);
        DmaStop(0);
        ResetTasks();
        ResetSpriteData();
        FreeAllSpritePalettes();
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1 | DISPCNT_BG1_ON);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 0);
        SetGpuReg(REG_OFFSET_BG0HOFS, 0);
        SetGpuReg(REG_OFFSET_BG0VOFS, 0);
        SetGpuReg(REG_OFFSET_BG1HOFS, 0);
        SetGpuReg(REG_OFFSET_BG1VOFS, 0);
        DmaFill32(3, 0, (void *)OAM, OAM_SIZE);
        DmaFill16(3, 0, (void *)BG_CHAR_ADDR(CRAWL_BG2_CHARBASE), BG_CHAR_SIZE);
        DmaFill16(3, 0, (void *)BG_CHAR_ADDR(CRAWL_BG0_CHARBASE), BG_CHAR_SIZE);
        DmaFill16(3, 0, (void *)BG_SCREEN_ADDR(CRAWL_BG0_SCREEN), BG_SCREEN_SIZE);
        gMain.state++;
        break;
    case 1:
        // BG2 map: 64x64 one-byte entries (512x512px, so the text's wrapped copies stay off
        // screen even on the far lines). Map rows r and r + 16 share a ring row, so the texture
        // repeats every 128px vertically. Columns 15+ use blank tile 0.
        map = (u16 *)BG_SCREEN_ADDR(CRAWL_BG2_SCREEN);
        for (i = 0; i < 64 * 64 / 2; i++)
        {
            u16 row = (i * 2) / 64;
            u16 col = (i * 2) % 64;
            u16 lo = 0, hi = 0;

            if (col < CRAWL_TEX_W_TILES)
                lo = 1 + (row % CRAWL_RING_ROWS) * CRAWL_TEX_W_TILES + col;
            if (col + 1 < CRAWL_TEX_W_TILES)
                hi = 1 + (row % CRAWL_RING_ROWS) * CRAWL_TEX_W_TILES + col + 1;
            map[i] = lo | (hi << 8);
        }
        gMain.state++;
        break;
    case 2:
        ResetBgsAndClearDma3BusyFlags(0);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1 | DISPCNT_BG1_ON); // ResetBgs hid every BG
        InitBgsFromTemplates(1, sBgTemplates, ARRAY_COUNT(sBgTemplates));
        InitWindows(sWindowTemplates);
        DeactivateAllTextPrinters();
        LoadWindowGfx(WIN_MSG, 0, FRAME_TILE, BG_PLTT_ID(FRAME_PAL));
        LoadPalette(gStandardMenuPalette, BG_PLTT_ID(TEXT_PAL), PLTT_SIZE_4BPP);
        {
            u16 colors[2];
            colors[0] = CRAWL_TEXT_COLOR;
            colors[1] = CRAWL_SHADOW_COLOR;
            LoadPalette(colors, BG_PLTT_ID(0) + 1, sizeof(colors));
        }
        gMain.state++;
        break;
    case 3:
        sScroll = -8 * 256;
        sNextLine = 0;
        BuildLineRegs();
        // Line darkening: full black at the top line, clear CRAWL_FADE_LINES lines lower.
        for (i = 0; i < CRAWL_NUM_LINES; i++)
        {
            if (i < CRAWL_TOP)
                sLineFade[i] = 16;
            else if (i < CRAWL_TOP + CRAWL_FADE_LINES)
                sLineFade[i] = 16 - ((i - CRAWL_TOP) * 16) / CRAWL_FADE_LINES;
            else
                sLineFade[i] = 0;
        }
        SetGpuReg(REG_OFFSET_BG0CNT, BGCNT_PRIORITY(0) | BGCNT_CHARBASE(CRAWL_BG0_CHARBASE) | BGCNT_SCREENBASE(CRAWL_BG0_SCREEN) | BGCNT_16COLOR | BGCNT_TXT256x256);
        SetGpuReg(REG_OFFSET_BG1CNT, BGCNT_PRIORITY(2) | BGCNT_CHARBASE(CRAWL_BG1_CHARBASE) | BGCNT_SCREENBASE(CRAWL_BG1_SCREEN) | BGCNT_16COLOR | BGCNT_TXT256x256);
        SetGpuReg(REG_OFFSET_BG2CNT, BGCNT_PRIORITY(1) | BGCNT_CHARBASE(CRAWL_BG2_CHARBASE) | BGCNT_SCREENBASE(CRAWL_BG2_SCREEN) | BGCNT_256COLOR | BGCNT_WRAP | BGCNT_AFF512x512);
        SetGpuReg(REG_OFFSET_WIN0H, WIN_RANGE(0, DISPLAY_WIDTH));
        SetGpuReg(REG_OFFSET_WIN0V, WIN_RANGE(CRAWL_TOP, DISPLAY_HEIGHT));
        SetGpuReg(REG_OFFSET_WININ, WININ_WIN0_ALL);
        SetGpuReg(REG_OFFSET_WINOUT, WINOUT_WIN01_BG0 | WINOUT_WIN01_BG1 | WINOUT_WIN01_OBJ);
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG2 | BLDCNT_EFFECT_DARKEN);
        SetGpuReg(REG_OFFSET_BLDY, 0);
        gMain.state++;
        break;
    case 4:
        SetVBlankCallback(VBlankCB_IntroCrawl);
        SetHBlankCallback(HBlankCB_IntroCrawl);
        EnableInterrupts(INTR_FLAG_VBLANK | INTR_FLAG_HBLANK);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_1 | DISPCNT_BG0_ON | DISPCNT_BG1_ON | DISPCNT_BG2_ON | DISPCNT_WIN0_ON);
        if (CRAWL_MUSIC != MUS_NONE)
            PlayBGM(CRAWL_MUSIC);
        CreateTask(Task_IntroCrawl, 0);
        gMain.state = 0;
        SetMainCallback2(CB2_IntroCrawl);
        break;
    }
}

static void CB2_IntroCrawl(void)
{
    RunTasks();
    RunTextPrinters();
    UpdatePaletteFade();
    DoScheduledBgTilemapCopiesToVram();
}

static void VBlankCB_IntroCrawl(void)
{
    struct CrawlLineRegs *regs = sLineRegs[sReadyBuffer];

    DmaStop(0);
    // HBlank DMA does not run during VBlank, so the first scanline is set by hand and the DMA
    // starts from the second entry.
    REG_BG2PA = regs[0].pa;
    REG_BG2PB = regs[0].pb;
    REG_BG2PC = regs[0].pc;
    REG_BG2PD = regs[0].pd;
    REG_BG2X = regs[0].x;
    REG_BG2Y = regs[0].y;
    REG_BLDY = sLineFade[0];
    DmaSet(0, &regs[1], &REG_BG2PA, ((DMA_ENABLE | DMA_START_HBLANK | DMA_REPEAT | DMA_32BIT | DMA_DEST_RELOAD | DMA_SRC_INC) << 16) | (sizeof(struct CrawlLineRegs) / 4));
    TransferPlttBuffer();
}

static void HBlankCB_IntroCrawl(void)
{
    u16 next = REG_VCOUNT + 1;

    if (next < DISPLAY_HEIGHT)
        REG_BLDY = sLineFade[next];
}

// Precompute each scanline's scale and its texture distance from the bottom scanline.
static void BuildLineRegs(void)
{
    s32 y;
    s32 depth = 0;

    for (y = DISPLAY_HEIGHT - 1; y >= 0; y--)
    {
        s32 line = (y < CRAWL_TOP) ? CRAWL_TOP : y;
        sLineScale[y] = (CRAWL_SCALE_K * 256) / (line - CRAWL_HORIZON);
        if (y < DISPLAY_HEIGHT - 1 && y >= CRAWL_TOP)
            depth += sLineScale[y + 1];
        sLineDepth[y] = depth;
    }
    sDepth = sLineDepth[CRAWL_TOP];
}

// Fill the back buffer with this frame's scroll and hand it to the next VBlank.
static void UpdateLineRegs(void)
{
    u8 buf = sReadyBuffer ^ 1;
    struct CrawlLineRegs *regs = sLineRegs[buf];
    s32 y;

    for (y = 0; y < CRAWL_NUM_LINES; y++)
    {
        s32 src = (y < DISPLAY_HEIGHT) ? y : DISPLAY_HEIGHT - 1;
        s32 scale = sLineScale[src];

        regs[y].pa = scale;
        regs[y].pb = 0;
        regs[y].pc = 0;
        regs[y].pd = scale;
        regs[y].x = (CRAWL_TEX_CENTER_X << 8) - scale * (DISPLAY_WIDTH / 2);
        // Text runs downwards in the texture, so going up the screen goes back in the texture.
        regs[y].y = sScroll - sLineDepth[src];
    }
    sReadyBuffer = buf;
}

// Print one text line with the normal font and copy it into its two ring rows as 8bpp tiles.
static void DrawRingLine(u16 line)
{
    const u8 *src;
    u16 *dst;
    u16 r, t, i;

    FillWindowPixelBuffer(WIN_SCRATCH, PIXEL_FILL(0));
    if (line < ARRAY_COUNT(sCrawlLines))
    {
        s32 width = GetStringWidth(FONT_NORMAL, sCrawlLines[line], 0);
        s32 x = (CRAWL_TEX_W_TILES * 8 - width) / 2;
        if (x < 0)
            x = 0;
        AddTextPrinterParameterized3(WIN_SCRATCH, FONT_NORMAL, x, 1, sCrawlTextColors, TEXT_SKIP_DRAW, sCrawlLines[line]);
    }

    src = gWindows[WIN_SCRATCH].tileData;
    for (r = 0; r < 2; r++)
    {
        u16 ringRow = (line * 2 + r) % CRAWL_RING_ROWS;

        // 4bpp (two pixels per byte, low nibble first) -> 8bpp (one byte per pixel)
        for (t = 0; t < CRAWL_TEX_W_TILES; t++)
        {
            for (i = 0; i < 32; i++)
            {
                u8 b = *src++;
                sTileBuffer[t * 32 + i] = (b & 0xF) | ((b >> 4) << 8);
            }
        }
        dst = (u16 *)(BG_CHAR_ADDR(CRAWL_BG2_CHARBASE) + (1 + ringRow * CRAWL_TEX_W_TILES) * 64);
        CpuCopy16(sTileBuffer, dst, sizeof(sTileBuffer));
    }
}

// Ring slot of line k was last used by line k - 8, which must be past the top of the screen.
static bool8 CanDrawNextLine(void)
{
    s32 slotFreeAt = (sNextLine * CRAWL_LINE_H - CRAWL_RING_H + CRAWL_LINE_H) * 256 + sDepth;
    return sScroll >= slotFreeAt;
}

static bool8 CrawlFinished(void)
{
    s32 end = (ARRAY_COUNT(sCrawlLines) * CRAWL_LINE_H + CRAWL_LINE_H) * 256 + sDepth;
    return sScroll >= end;
}

#define tState  data[0]
#define tTimer  data[1]
#define tPaused data[2]

static void AdvanceCrawl(u8 taskId)
{
    if (!gTasks[taskId].tPaused)
        sScroll += CRAWL_SPEED;
    // Blank lines past the end keep the ring clean.
    if (sNextLine < ARRAY_COUNT(sCrawlLines) + CRAWL_RING_ROWS / 2 && CanDrawNextLine())
        DrawRingLine(sNextLine++);
    UpdateLineRegs();
}

static void Task_IntroCrawl(u8 taskId)
{
    AdvanceCrawl(taskId);

    if (CrawlFinished())
    {
        if (++gTasks[taskId].tTimer >= CRAWL_END_HOLD)
            gTasks[taskId].func = Task_IntroCrawlFadeOut;
    }
    else if (JOY_NEW(A_BUTTON | B_BUTTON | START_BUTTON))
    {
        PlaySE(SE_SELECT);
        gTasks[taskId].tPaused = TRUE;
        gTasks[taskId].func = Task_IntroCrawlAskSkip;
    }
}

static void Task_IntroCrawlAskSkip(u8 taskId)
{
    AdvanceCrawl(taskId);
    DrawStdFrameWithCustomTileAndPalette(WIN_MSG, FALSE, FRAME_TILE, FRAME_PAL);
    FillWindowPixelBuffer(WIN_MSG, PIXEL_FILL(1));
    AddTextPrinterParameterized(WIN_MSG, FONT_NORMAL, sText_SkipIntro, 0, 1, 0, NULL);
    PutWindowTilemap(WIN_MSG);
    CopyWindowToVram(WIN_MSG, COPYWIN_FULL);
    CreateYesNoMenu(&sYesNoTemplate, FRAME_TILE, FRAME_PAL, 1); // cursor starts on NO
    gTasks[taskId].func = Task_IntroCrawlSkipChoice;
}

static void Task_IntroCrawlSkipChoice(u8 taskId)
{
    AdvanceCrawl(taskId);
    switch (Menu_ProcessInputNoWrapClearOnChoose())
    {
    case 0: // YES
        ClearStdWindowAndFrame(WIN_MSG, TRUE);
        gTasks[taskId].func = Task_IntroCrawlFadeOut;
        break;
    case 1: // NO
    case MENU_B_PRESSED:
        ClearStdWindowAndFrame(WIN_MSG, TRUE);
        gTasks[taskId].tPaused = FALSE;
        gTasks[taskId].func = Task_IntroCrawl;
        break;
    }
}

static void Task_IntroCrawlFadeOut(u8 taskId)
{
    AdvanceCrawl(taskId);
    if (CRAWL_MUSIC != MUS_NONE)
        FadeOutBGM(4);
    BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
    gTasks[taskId].func = Task_IntroCrawlExit;
}

static void Task_IntroCrawlExit(u8 taskId)
{
    AdvanceCrawl(taskId);
    if (!gPaletteFade.active)
    {
        SetHBlankCallback(NULL);
        SetVBlankCallback(NULL);
        DisableInterrupts(INTR_FLAG_HBLANK);
        DmaStop(0);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        SetGpuReg(REG_OFFSET_BLDY, 0);
        SetGpuReg(REG_OFFSET_WININ, 0);
        SetGpuReg(REG_OFFSET_WINOUT, 0);
        SetGpuReg(REG_OFFSET_WIN0H, 0);
        SetGpuReg(REG_OFFSET_WIN0V, 0);
        REG_BG2PA = 0x100;
        REG_BG2PB = 0;
        REG_BG2PC = 0;
        REG_BG2PD = 0x100;
        REG_BG2X = 0;
        REG_BG2Y = 0;
        FreeAllWindowBuffers();
        DestroyTask(taskId);
        SetMainCallback2(CB2_InitMainMenu);
    }
}

// ---------------------------------------------------------------------------------------------
// "A long time ago in a galaxy far, far away...."
// Played between the end of the intro movie (the white flash after the sun scene) and the title
// screen. Not played when the intro is skipped: skipping goes straight to the title screen
// (MainCB2_Intro in intro.c), and this screen itself takes no input.
// White fades down to dark space, the blue text fades in, holds, fades out, then the title screen.
// ---------------------------------------------------------------------------------------------

#define GALAXY_BG_COLOR       RGB(1, 1, 3)
#define GALAXY_TEXT_COLOR     RGB(9, 22, 30)    // the movie's pale blue
#define GALAXY_SHADOW_COLOR   RGB(3, 9, 15)
#define GALAXY_FROM_WHITE     2                 // palette fade delay: white -> space
#define GALAXY_TEXT_FADE      32                // frames for the text to fade in / out
#define GALAXY_TEXT_HOLD      200
#define GALAXY_END_HOLD       30
#define GALAXY_PAL            15

static const u8 sText_GalaxyLine1[] = _("A long time ago in a galaxy far,");
static const u8 sText_GalaxyLine2[] = _("far away....");

static const struct BgTemplate sGalaxyBgTemplates[] =
{
    {
        .bg = 0,
        .charBaseIndex = 0,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0,
    },
};

static const struct WindowTemplate sGalaxyWindowTemplates[] =
{
    {
        .bg = 0,
        .tilemapLeft = 1,
        .tilemapTop = 7,
        .width = 28,
        .height = 5,
        .paletteNum = GALAXY_PAL,
        .baseBlock = 1,
    },
    DUMMY_WIN_TEMPLATE
};

// bg, fg, shadow in palette GALAXY_PAL
static const u8 sGalaxyTextColors[] = {1, 2, 3};

static void CB2_GalaxyFarAway(void);
static void VBlankCB_GalaxyFarAway(void);
static void Task_GalaxyFarAway(u8 taskId);

void CB2_InitGalaxyFarAway(void)
{
    u16 pal[4];
    s32 w1, w2, x;

    SetVBlankCallback(NULL);
    SetHBlankCallback(NULL);
    SetGpuReg(REG_OFFSET_DISPCNT, 0);
    SetGpuReg(REG_OFFSET_BG0HOFS, 0);
    SetGpuReg(REG_OFFSET_BG0VOFS, 0);
    SetGpuReg(REG_OFFSET_WININ, 0);
    SetGpuReg(REG_OFFSET_WINOUT, 0);
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetGpuReg(REG_OFFSET_BLDALPHA, 0);
    SetGpuReg(REG_OFFSET_BLDY, 0);
    ScanlineEffect_Stop();
    DmaFill16(3, 0, (void *)VRAM, VRAM_SIZE);
    DmaFill32(3, 0, (void *)OAM, OAM_SIZE);
    DmaFill16(3, 0, (void *)PLTT, PLTT_SIZE);
    ResetPaletteFade();
    ResetTasks();
    ResetSpriteData();
    FreeAllSpritePalettes();
    ResetBgsAndClearDma3BusyFlags(0);
    InitBgsFromTemplates(0, sGalaxyBgTemplates, ARRAY_COUNT(sGalaxyBgTemplates));
    InitWindows(sGalaxyWindowTemplates);
    DeactivateAllTextPrinters();

    // The text starts in the background colour (invisible) and is blended in by the task.
    pal[0] = GALAXY_BG_COLOR;
    pal[1] = GALAXY_BG_COLOR;
    pal[2] = GALAXY_BG_COLOR;
    pal[3] = GALAXY_BG_COLOR;
    LoadPalette(&pal[0], BG_PLTT_ID(0), sizeof(pal[0]));
    LoadPalette(pal, BG_PLTT_ID(GALAXY_PAL), sizeof(pal));

    // Two lines, left-aligned like the film, the block centred in the window
    w1 = GetStringWidth(FONT_NORMAL, sText_GalaxyLine1, 0);
    w2 = GetStringWidth(FONT_NORMAL, sText_GalaxyLine2, 0);
    x = (28 * 8 - (w1 > w2 ? w1 : w2)) / 2;
    if (x < 0)
        x = 0;
    FillWindowPixelBuffer(0, PIXEL_FILL(1));
    AddTextPrinterParameterized3(0, FONT_NORMAL, x, 4, sGalaxyTextColors, TEXT_SKIP_DRAW, sText_GalaxyLine1);
    AddTextPrinterParameterized3(0, FONT_NORMAL, x, 20, sGalaxyTextColors, TEXT_SKIP_DRAW, sText_GalaxyLine2);
    PutWindowTilemap(0);
    CopyWindowToVram(0, COPYWIN_FULL);

    // Carry on from the intro's white flash
    BlendPalettes(PALETTES_ALL, 16, RGB_WHITE);
    BeginNormalPaletteFade(PALETTES_ALL, GALAXY_FROM_WHITE, 16, 0, RGB_WHITE);
    FadeOutBGM(4);

    SetGpuReg(REG_OFFSET_BG0CNT, BGCNT_PRIORITY(0) | BGCNT_CHARBASE(0) | BGCNT_SCREENBASE(31) | BGCNT_16COLOR | BGCNT_TXT256x256);
    SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_0 | DISPCNT_BG0_ON);
    EnableInterrupts(INTR_FLAG_VBLANK);
    SetVBlankCallback(VBlankCB_GalaxyFarAway);
    CreateTask(Task_GalaxyFarAway, 0);
    SetMainCallback2(CB2_GalaxyFarAway);
}

static void CB2_GalaxyFarAway(void)
{
    RunTasks();
    UpdatePaletteFade();
    DoScheduledBgTilemapCopiesToVram();
}

static void VBlankCB_GalaxyFarAway(void)
{
    TransferPlttBuffer();
}

static u16 MixColor(u16 from, u16 to, u8 level)
{
    s32 r = GET_R(from) + ((GET_R(to) - GET_R(from)) * level) / 16;
    s32 g = GET_G(from) + ((GET_G(to) - GET_G(from)) * level) / 16;
    s32 b = GET_B(from) + ((GET_B(to) - GET_B(from)) * level) / 16;
    return RGB(r, g, b);
}

// level 0 = text invisible (background colour), 16 = full blue
static void SetGalaxyTextLevel(u8 level)
{
    u16 pal[2];
    pal[0] = MixColor(GALAXY_BG_COLOR, GALAXY_TEXT_COLOR, level);
    pal[1] = MixColor(GALAXY_BG_COLOR, GALAXY_SHADOW_COLOR, level);
    LoadPalette(pal, BG_PLTT_ID(GALAXY_PAL) + 2, sizeof(pal));
}

static void Task_GalaxyFarAway(u8 taskId)
{
    s16 *timer = &gTasks[taskId].tTimer;

    switch (gTasks[taskId].tState)
    {
    case 0: // white -> space
        if (!gPaletteFade.active)
        {
            *timer = 0;
            gTasks[taskId].tState++;
        }
        break;
    case 1: // text fades in
        ++*timer;
        SetGalaxyTextLevel((*timer * 16) / GALAXY_TEXT_FADE);
        if (*timer >= GALAXY_TEXT_FADE)
        {
            *timer = 0;
            gTasks[taskId].tState++;
        }
        break;
    case 2: // hold
        if (++*timer >= GALAXY_TEXT_HOLD)
        {
            *timer = 0;
            gTasks[taskId].tState++;
        }
        break;
    case 3: // text fades out
        ++*timer;
        SetGalaxyTextLevel(16 - (*timer * 16) / GALAXY_TEXT_FADE);
        if (*timer >= GALAXY_TEXT_FADE)
        {
            *timer = 0;
            gTasks[taskId].tState++;
        }
        break;
    case 4: // a beat of empty space, then the title screen
        if (++*timer >= GALAXY_END_HOLD)
        {
            SetVBlankCallback(NULL);
            FreeAllWindowBuffers();
            DestroyTask(taskId);
            SetMainCallback2(CB2_InitTitleScreen);
        }
        break;
    }
}

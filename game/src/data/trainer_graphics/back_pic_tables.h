const struct MonCoords gTrainerBackPicCoords[] =
{
    [TRAINER_BACK_PIC_BRENDAN] = {.size = 8, .y_offset = 4},
    [TRAINER_BACK_PIC_MAY] = {.size = 8, .y_offset = 4},
    [TRAINER_BACK_PIC_RUBY_SAPPHIRE_BRENDAN] = {.size = 8, .y_offset = 4},
    [TRAINER_BACK_PIC_RUBY_SAPPHIRE_MAY] = {.size = 8, .y_offset = 4},
    [TRAINER_BACK_PIC_WALLY] = {.size = 8, .y_offset = 4},
    [TRAINER_BACK_PIC_STEVEN] = {.size = 8, .y_offset = 4},
};

// this table goes functionally unused, since none of these pics are compressed
// and the place they would get extracted to gets overwritten later anyway
// the casts are so they'll play nice with the strict struct definition
const struct CompressedSpriteSheet gTrainerBackPicTable[] =
{
    [TRAINER_BACK_PIC_BRENDAN] = {
        .data = (const u32 *)gTrainerBackPic_Brendan,
        .size = TRAINER_PIC_SIZE * ARRAY_COUNT(gTrainerBackPicTable_Brendan),
        .tag = TRAINER_BACK_PIC_BRENDAN,
    },
    [TRAINER_BACK_PIC_MAY] = {
        .data = (const u32 *)gTrainerBackPic_May,
        .size = TRAINER_PIC_SIZE * ARRAY_COUNT(gTrainerBackPicTable_May),
        .tag = TRAINER_BACK_PIC_MAY,
    },
    [TRAINER_BACK_PIC_RUBY_SAPPHIRE_BRENDAN] = {
        .data = (const u32 *)gTrainerBackPic_RubySapphireBrendan,
        .size = TRAINER_PIC_SIZE * ARRAY_COUNT(gTrainerBackPicTable_RubySapphireBrendan),
        .tag = TRAINER_BACK_PIC_RUBY_SAPPHIRE_BRENDAN,
    },
    [TRAINER_BACK_PIC_RUBY_SAPPHIRE_MAY] = {
        .data = (const u32 *)gTrainerBackPic_RubySapphireMay,
        .size = TRAINER_PIC_SIZE * ARRAY_COUNT(gTrainerBackPicTable_RubySapphireMay),
        .tag = TRAINER_BACK_PIC_RUBY_SAPPHIRE_MAY,
    },
    [TRAINER_BACK_PIC_WALLY] = {
        .data = (const u32 *)gTrainerBackPic_Wally,
        .size = TRAINER_PIC_SIZE * ARRAY_COUNT(gTrainerBackPicTable_Wally),
        .tag = TRAINER_BACK_PIC_WALLY,
    },
    [TRAINER_BACK_PIC_STEVEN] = {
        .data = (const u32 *)gTrainerBackPic_Steven,
        .size = TRAINER_PIC_SIZE * ARRAY_COUNT(gTrainerBackPicTable_Steven),
        .tag = TRAINER_BACK_PIC_STEVEN,
    },
};

#define TRAINER_BACK_PAL(trainerPic, pal) [TRAINER_BACK_PIC_##trainerPic] = {pal, TRAINER_BACK_PIC_##trainerPic}

const struct CompressedSpritePalette gTrainerBackPicPaletteTable[] =
{
    TRAINER_BACK_PAL(BRENDAN, gTrainerBackPicPalette_Brendan),
    TRAINER_BACK_PAL(MAY, gTrainerBackPicPalette_May),
    TRAINER_BACK_PAL(RUBY_SAPPHIRE_BRENDAN, gTrainerBackPicPalette_RubySapphireBrendan),
    TRAINER_BACK_PAL(RUBY_SAPPHIRE_MAY, gTrainerBackPicPalette_RubySapphireMay),
    TRAINER_BACK_PAL(WALLY, gTrainerBackPicPalette_Wally),
    TRAINER_BACK_PAL(STEVEN, gTrainerBackPicPalette_Steven),
};

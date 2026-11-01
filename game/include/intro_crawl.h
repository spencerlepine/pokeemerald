#ifndef GUARD_INTRO_CRAWL_H
#define GUARD_INTRO_CRAWL_H

// TRUE when the opening crawl should play after the title screen: no save file yet,
// and it has not played since power-on.
bool8 IntroCrawl_ShouldPlay(void);
void CB2_InitIntroCrawl(void);

// "A long time ago in a galaxy far, far away...." between the intro movie and the title screen
void CB2_InitGalaxyFarAway(void);

#endif // GUARD_INTRO_CRAWL_H

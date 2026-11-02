"""The blockout terrain legend: one character per 16x16 map cell, drawn as flat grey placeholder tiles.

Only what the player's movement cares about is told apart. What the cell will look like (sand, snow,
durasteel) belongs to the area's planet and comes later with the art.
"""

# char: (name, walkable, grey fill, description)
TERRAIN = {
    ".": ("ground", True, (206, 206, 206), "open ground the player walks on"),
    ":": ("path", True, (236, 236, 236), "path, street or plaza: the signal the player follows"),
    '"': ("wild", True, (168, 168, 168), "wild encounter ground (tall grass, scrub, ash, ferns)"),
    "~": ("water", False, (140, 150, 164), "water: surf only"),
    "=": ("bridge", True, (190, 180, 168), "raised walkway: bridge, platform, catwalk (a level above the ground)"),
    "T": ("nature", False, (206, 206, 206), "edge nature that blocks: trees, rocks, bushes"),
    "#": ("cliff", False, (104, 104, 104), "cliff, wall or rock face"),
    "v": ("ledge-s", True, (206, 206, 206), "ledge, jump down to the south"),
    "<": ("ledge-w", True, (206, 206, 206), "ledge, jump down to the west"),
    ">": ("ledge-e", True, (206, 206, 206), "ledge, jump down to the east"),
    "^": ("ledge-n", True, (206, 206, 206), "ledge, jump down to the north"),
    "H": ("ladder", True, (176, 160, 140), "ladder or stairs between levels (tree platforms, cliffs)"),
    "x": ("blocked", False, (150, 150, 150), "blocked, not yet decided (left over from a vanilla import)"),
    "_": ("floor", True, (222, 222, 222), "indoor floor"),
    "|": ("wall", False, (90, 90, 90), "indoor wall"),
}

PINK = (255, 79, 191)          # every sprite and event placeholder: people, items, signs, triggers
PINK_DARK = (150, 20, 110)
OUTLINE = (46, 46, 46)


def walkable(ch):
    return TERRAIN.get(ch, TERRAIN["x"])[1]

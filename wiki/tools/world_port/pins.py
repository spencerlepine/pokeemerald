"""What a per-area copy of a vanilla secondary tileset must keep where it is.

  - Metatile ids named in include/constants/metatile_labels.h (doors, puzzles, scripted changes): scripts and C
    code place them by id, so their tiles stay.
  - Tile slots a tile animation writes to (src/tileset_anims.c), for the tileset's own animation callback.
"""
import re
from collections import defaultdict

from . import base as B

_LABELS = None
_ANIMS = None
_CALLBACKS = None


def labels():
    """secondary tileset header (gTileset_X) -> set of labelled metatile ids."""
    global _LABELS
    if _LABELS is None:
        _LABELS = defaultdict(set)
        cur = None
        for line in (B.BASE_GAME / "include/constants/metatile_labels.h").read_text().splitlines():
            m = re.match(r"//\s*(gTileset_\w+)", line)
            if m:
                cur = m.group(1)
                continue
            m = re.match(r"#define\s+METATILE_\w+\s+(0x[0-9A-Fa-f]+|\d+)", line)
            if m and cur:
                _LABELS[cur].add(int(m.group(1), 0))
    return _LABELS


def callbacks():
    """gTileset_X -> its init callback name (or NULL)."""
    global _CALLBACKS
    if _CALLBACKS is None:
        hdr = (B.BASE_GAME / "src/data/tilesets/headers.h").read_text()
        _CALLBACKS = {}
        for m in re.finditer(r"const struct Tileset (gTileset_\w+) =\s*\{(.*?)\};", hdr, re.S):
            c = re.search(r"\.callback = (\w+)", m.group(2))
            _CALLBACKS[m.group(1)] = c.group(1) if c else "NULL"
    return _CALLBACKS


def anim_slots():
    """Animation set name (the X in TilesetAnim_X) -> secondary tile slots (0-511) its animation writes."""
    global _ANIMS
    if _ANIMS is None:
        text = (B.BASE_GAME / "src/tileset_anims.c").read_text()
        vdests = {}
        for m in re.finditer(r"u16 \*const (\w+_VDests)\[\] = \{(.*?)\};", text, re.S):
            vdests[m.group(1)] = [int(n) for n in re.findall(r"NUM_TILES_IN_PRIMARY \+ (\d+)", m.group(2))]
        # which animation set calls which QueueAnimTiles function
        calls = defaultdict(set)
        for m in re.finditer(r"static void TilesetAnim_(\w+)\(u16 timer\)\s*\{(.*?)\n\}", text, re.S):
            for f in re.findall(r"(QueueAnimTiles_\w+)\(", m.group(2)):
                calls[m.group(1)].add(f)
        funcs = {}
        for m in re.finditer(r"static void (QueueAnimTiles_\w+)\([^)]*\)\s*\{(.*?)\n\}", text, re.S):
            funcs[m.group(1)] = m.group(2)
        _ANIMS = {}
        for name, fs in calls.items():
            slots = set()
            for f in fs:
                for c in re.finditer(r"AppendTilesetAnimToBuffer\(([^;]*)\);", funcs.get(f, "")):
                    args = c.group(1)
                    size = re.search(r"(\d+) \* TILE_SIZE_4BPP", args)
                    n = int(size.group(1)) if size else 4
                    offs = [int(o) for o in re.findall(r"NUM_TILES_IN_PRIMARY \+ (\d+)", args)]
                    for vd, vals in vdests.items():
                        if vd in args:
                            offs += vals
                    for o in offs:
                        slots |= set(range(o, o + n))
            _ANIMS[name] = slots
    return _ANIMS


def reserved_slots(header):
    """Tile slots the secondary's animation callback writes to."""
    cb = callbacks().get(header, "NULL")
    if not cb.startswith("InitTilesetAnim_"):
        return set()
    text = (B.BASE_GAME / "src/tileset_anims.c").read_text()
    m = re.search(rf"void {cb}\(void\)\s*\{{(.*?)\n\}}", text, re.S)
    if not m:
        return set()
    a = re.search(r"sSecondaryTilesetAnimCallback = TilesetAnim_(\w+);", m.group(1))
    return anim_slots().get(a.group(1), set()) if a else set()

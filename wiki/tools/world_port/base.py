"""The vanilla game data the world port starts from, and shared paths.

The port rewrites map, layout and tileset files in ../game. So that a second run gives the same result, it
always starts from the game as it was before the port: the files under BASE_PATHS at commit BASE, extracted
once into a cache folder (`wiki/tools/world_port/.base/`, not committed). Everything the port reads about
vanilla maps comes from there; everything it writes goes to ../game.

Script files (`data/maps/*/scripts.inc`) are the exception: other tools edit their text, so the port edits
them in place, with patches that can run twice.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIKI = HERE.parents[1]
ROOT = WIKI.parent
GAME = ROOT / "game"
WORLD = WIKI / "world"
MAPPING = WIKI / "mapping"
DATABASE = WIKI / "database"
TOOLS = ROOT / "tools"

# The last commit before the world port touched ../game's maps, layouts and tilesets (2026-11-04).
BASE = "c663bddf"
BASE_PATHS = ["game/data/maps", "game/data/layouts", "game/data/tilesets", "game/src/data/tilesets",
              "game/src/graphics.c", "game/include", "game/src/data/heal_locations.json",
              "game/src/data/wild_encounters.json", "game/src/data/region_map", "game/src/tileset_anims.c"]
CACHE = HERE / ".base"
BASE_GAME = CACHE / "game"


def ensure_base():
    """Extract the vanilla files once (git archive of BASE)."""
    stamp = CACHE / "STAMP"
    if stamp.exists() and stamp.read_text().strip() == BASE:
        return BASE_GAME
    CACHE.mkdir(parents=True, exist_ok=True)
    tar = subprocess.run(["git", "-C", str(ROOT), "archive", BASE] + BASE_PATHS, check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(CACHE)], input=tar, check=True)
    stamp.write_text(BASE + "\n")
    return BASE_GAME


def use_base_for_tools():
    """Point the tile-generator and blockout readers at the vanilla snapshot (they read EMERALD_DIR / GAME)."""
    ensure_base()
    os.environ["EMERALD_DIR"] = str(BASE_GAME)
    for p in (TOOLS / "tile-generator", TOOLS / "blockout"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    from blockout import vanilla as V
    V.GAME = BASE_GAME
    return V


def base_map(name):
    return json.loads((BASE_GAME / "data/maps" / name / "map.json").read_text())


def base_json(rel):
    return json.loads((BASE_GAME / rel).read_text())


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
        return True
    return False


def write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)
        return True
    return False


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
        return True
    return False

"""Where things are: the game checkout, the wiki, the shared palette-enforcer, this tool's folders."""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # tools/vfx-generator
TOOLS = HERE.parent
REPO = TOOLS.parent
GAME = Path(os.environ.get("EMERALD_DIR", REPO / "game")).resolve()
WIKI = REPO / "wiki"
WIKI_ART = WIKI / "art"
ART = HERE / "art"            # specs
OUT = HERE / "output"         # built sheets and previews (committed: they are the review material)
CORPUS = HERE / "corpus"      # measured vanilla data (catalog.json, style.json)
ENFORCER = TOOLS / "palette-enforcer"

if str(ENFORCER) not in sys.path:
    sys.path.insert(0, str(ENFORCER))


def game_path(rel: str | Path) -> Path:
    return GAME / rel


def src_text(rel: str) -> str:
    return (GAME / rel).read_text(encoding="utf-8", errors="replace")


def rel_to_game(p: Path) -> str:
    return str(Path(p).resolve().relative_to(GAME))

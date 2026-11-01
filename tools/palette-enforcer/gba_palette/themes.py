"""Layer 2 of tools/PALETTES.md: the project's chosen palettes, read from the wiki.

The source of truth is wiki/bible/PALETTE.md. Every `## Heading` with a table whose rows hold a
backticked `#RRGGBB` is a theme. Nothing is copied here, so editing the wiki changes what the
tools enforce on the next run.

Theme ids are the heading slugged: the part after the colon if there is one, parentheses dropped.
  "## Title screen and logo: Kyber Gold"                  -> kyber-gold
  "## HUD and menus: Hyperspace Console (surfaces and text)" -> hyperspace-console
  "## Battle backdrop (behind creatures)"                 -> battle-backdrop
Groups (below) bundle themes that are always used together.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .core import Colour, on_step, parse_hex

REPO = Path(__file__).resolve().parents[3]
PALETTE_MD = REPO / "wiki" / "bible" / "PALETTE.md"

GROUPS = {
    # every menu / HUD screen: surfaces + text + status colours
    "hud": ["hyperspace-console", "status-and-accents"],
    # the three story factions
    "factions": ["alliance-dawn", "imperial-order", "swamp-throne"],
}


@dataclass
class Swatch:
    name: str
    colour: Colour
    role: str


@dataclass
class Theme:
    id: str
    title: str
    swatches: list[Swatch] = field(default_factory=list)

    @property
    def colours(self) -> list[Colour]:
        return [s.colour for s in self.swatches]


def slug(heading: str) -> str:
    h = heading.split(":", 1)[1] if ":" in heading else heading
    h = re.sub(r"\(.*?\)", "", h)
    return re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")


def load(path: str | Path = PALETTE_MD) -> dict[str, Theme]:
    themes: dict[str, Theme] = {}
    cur: Theme | None = None
    for line in Path(path).read_text().splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            cur = Theme(slug(title), title)
            continue
        if cur is None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        hexes = [re.search(r"#[0-9A-Fa-f]{6}", c) for c in cells]
        at = next((i for i, m in enumerate(hexes) if m), None)
        if at is None:
            continue
        role = cells[-1] if len(cells) > at + 1 else ""
        cur.swatches.append(Swatch(cells[0], parse_hex(hexes[at].group(0)), role))
        themes.setdefault(cur.id, cur)
    return themes


def resolve(names: list[str], path: str | Path = PALETTE_MD) -> list[Colour]:
    """Colours for a list of theme ids or group names, deduplicated, in order."""
    themes = load(path)
    out: list[Colour] = []
    for n in names:
        ids = GROUPS.get(n, [n])
        for i in ids:
            if i not in themes:
                raise KeyError(f"unknown theme {i!r}; known: {', '.join(sorted(themes))}, groups: {', '.join(GROUPS)}")
            for c in themes[i].colours:
                if c not in out:
                    out.append(c)
    return out


def lint(path: str | Path = PALETTE_MD) -> list[str]:
    """Problems in the wiki palette itself (every swatch must be on a GBA step)."""
    errs = []
    for t in load(path).values():
        for s in t.swatches:
            if not on_step(s.colour):
                errs.append(f"{t.id}: {s.name} {s.colour} is not on a GBA step (channels must be multiples of 8)")
    return errs

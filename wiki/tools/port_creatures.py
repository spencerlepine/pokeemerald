#!/usr/bin/env python3
"""Port every creature into ../game from the wiki, and list every creature asset in one table.

Steps (run all with no argument, or name some):

  species  The net-new species in the free old-Unown slots (mapping/new_species.csv): species info (copied
           from `copies`, with the row's stats, types and colour), learnsets, egg moves, names, pics, palettes,
           icon, footprint, coordinates, animations, cry, the Datapad entry and the alias constant. A species
           with its own art in art/graphics/pokemon/<name>/ uses it; otherwise it borrows `art_from`'s art with
           a tinted battle palette (graphics/pokemon/<name>/normal.pal, made once, never overwritten).
  dex      The Datapad: the new species go after DEOXYS in both lists (regional and national, numbers in
           new_species.csv), the alphabetical order is rebuilt from the Star Wars names, and the new species
           are sorted into the weight and height orders. tools/port_sizes.py owns the sizes after that (run it next).
  moves    The net-new moves (mapping/new_moves.csv: a clone of an existing move with a new name, description
           and animation) and the learnset swaps in mapping/move_learnsets.csv (level-up learnsets, trainer
           parties and Grand Arena sets).
  assets   Installs the approved creature art and cries that are still only in the wiki: party icons and the
           3 icon banks (gMonIconPaletteIndices from the icon tool's csv), footprints, and the cries in
           mapping/audio_ready.csv (added to mapping/audio_done.csv). Battle pics already in the game are
           marked DONE.
  check    Writes database/creatures.csv: one row per species slot with the state of every asset in ../game.

Run tools/port_names.py afterwards (names and Datapad text), then tools/mark_audio_done.py. Idempotent: a second
run changes nothing. Standard library only.
"""
import argparse
import colorsys
import csv
import filecmp
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT.parent / "game"
MAP = ROOT / "mapping"
DB = ROOT / "database"
ART = ROOT / "art"
TOOLS = ROOT.parent / "tools"


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write_csv(path, cols, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


class Src:
    """A game source file edited in memory and written once, only if it changed."""
    open_files = {}

    def __init__(self, rel):
        self.rel, self.path = rel, GAME / rel
        self.text = self.orig = self.path.read_text(encoding="utf-8")

    @classmethod
    def get(cls, rel):
        if rel not in cls.open_files:
            cls.open_files[rel] = cls(rel)
        return cls.open_files[rel]

    @classmethod
    def save_all(cls, dry):
        changed = [s.rel for s in cls.open_files.values() if s.text != s.orig]
        if not dry:
            for s in cls.open_files.values():
                if s.text != s.orig:
                    s.path.write_text(s.text, encoding="utf-8")
                    s.orig = s.text
        return changed


def const_of(species_id):
    """species:ho-oh -> HO_OH"""
    return species_id.split(":", 1)[1].upper().replace("-", "_")


def folder_of(species_id):
    """species:ho-oh -> ho_oh (the folder in graphics/pokemon)"""
    return species_id.split(":", 1)[1].replace("-", "_")


def camel(name):
    """WYYYSCHOKK -> Wyyyschokk, HO_OH -> HoOh (symbol names)"""
    return "".join(p.capitalize() for p in re.split(r"[_\- ]", name.lower()) if p)


# ---------------------------------------------------------------- tables
def table_span(text, decl):
    """(start, end) of the body of the table whose declaration matches `decl` (end = the closing '};')."""
    m = re.search(decl, text)
    if not m:
        raise SystemExit(f"table not found: {decl}")
    start = text.index("{", m.end() - 1) + 1
    end = text.index("\n};", start)
    return start, end


def find_entry(text, span, key):
    """Line span (start, end incl. newline) of the one-line entry for `key` (a regex) inside `span`."""
    m = re.compile(r"^[ \t]*" + key + r".*\n", re.M).search(text, span[0], span[1] + 1)
    return (m.start(), m.end()) if m else None


def get_line(rel, decl, key):
    s = Src.get(rel)
    e = find_entry(s.text, table_span(s.text, decl), key)
    return s.text[e[0]:e[1]] if e else None


def set_line(rel, decl, key, line):
    """Replace the entry for `key` in the table, or add it before the table's end."""
    s = Src.get(rel)
    span = table_span(s.text, decl)
    e = find_entry(s.text, span, key)
    line = line.rstrip("\n") + "\n"
    if e:
        s.text = s.text[:e[0]] + line + s.text[e[1]:]
    else:
        s.text = s.text[:span[1] + 1] + line + s.text[span[1] + 1:]


def del_line(rel, decl, key):
    s = Src.get(rel)
    e = find_entry(s.text, table_span(s.text, decl), key)
    if e:
        s.text = s.text[:e[0]] + s.text[e[1]:]


def block_span(text, key, span=None):
    """Span of a multi-line `[SPECIES_X] = ...` entry: from its line to the next entry or the table end."""
    lo, hi = span or (0, len(text))
    m = re.compile(r"^    \[" + key + r"\]\s*=.*\n", re.M).search(text, lo, hi)
    if not m:
        return None
    nxt = re.compile(r"^    \[SPECIES_\w+\]|^\};|^    egg_moves\(", re.M).search(text, m.end())
    end = nxt.start() if nxt else len(text)
    return m.start(), end


def get_block(rel, key):
    s = Src.get(rel)
    b = block_span(s.text, key)
    return s.text[b[0]:b[1]].rstrip() + "\n" if b else None


def set_block(rel, key, block):
    s = Src.get(rel)
    b = block_span(s.text, key)
    if not b:
        raise SystemExit(f"{rel}: no entry for {key}")
    s.text = s.text[:b[0]] + block.rstrip() + "\n\n" + s.text[b[1]:]


def managed(rel, tag, body, anchor_after=None, anchor_before=None, comment="//"):
    """Write `body` between BEGIN/END marker lines (made on first run after/before an anchor regex)."""
    s = Src.get(rel)
    begin = f"{comment} BEGIN {tag} (wiki/tools/port_creatures.py)\n"
    end = f"{comment} END {tag}\n"
    block = begin + body + end
    if begin in s.text:
        a = s.text.index(begin)
        b = s.text.index(end, a) + len(end)
        s.text = s.text[:a] + block + s.text[b:]
    elif anchor_after:
        m = re.search(anchor_after, s.text, re.M)
        if not m:
            raise SystemExit(f"{rel}: anchor not found: {anchor_after}")
        s.text = s.text[:m.end()] + block + s.text[m.end():]
    else:
        m = re.search(anchor_before, s.text, re.M)
        if not m:
            raise SystemExit(f"{rel}: anchor not found: {anchor_before}")
        s.text = s.text[:m.start()] + block + s.text[m.start():]


# ---------------------------------------------------------------- palettes
def read_pal(path):
    lines = path.read_text().split()
    n = int(lines[2])
    return [tuple(int(x) for x in lines[3 + i * 3:6 + i * 3]) for i in range(n)]


def write_pal(path, cols):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("JASC-PAL\r\n0100\r\n%d\r\n" % len(cols)
                    + "".join("%d %d %d\r\n" % c for c in cols))


def snap5(c):
    return tuple(min(248, (v // 8) * 8) for v in c)


def tint_palette(src, tint):
    """A placeholder battle palette: the borrowed creature's colours pulled toward the new species' colour.
    `dark` = red-black, `light` = blue-white, `#RRGGBB` = that colour's hue. Index 0 (transparent) is kept."""
    cols = read_pal(src)
    out = [cols[0]]
    for c in cols[1:]:
        h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
        if tint == "dark":
            h, s, l = 0.0, max(s, 0.55), l * 0.7
        elif tint == "light":
            h, s, l = 0.58, s * 0.6, min(1.0, l * 1.15 + 0.08)
        else:
            th, tl, ts = colorsys.rgb_to_hls(*(int(tint[i:i + 2], 16) / 255 for i in (1, 3, 5)))
            h, s, l = th, (s + ts) / 2, l * 0.6 + tl * 0.4
        out.append(snap5(tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))))
    return out


# ---------------------------------------------------------------- species
def load_new_species():
    _, rows = read_csv(MAP / "new_species.csv")
    for r in rows:
        r["slot_key"] = r["slot"].removeprefix("SPECIES_")          # OLD_UNOWN_E
        r["sym"] = camel(r["sw_name"])                               # Wyyyschokk
        r["folder"] = r["sw_name"].lower()                           # wyyyschokk
        r["src"] = const_of(r["copies"])                             # ARIADOS
        r["art"] = const_of(r["art_from"])                           # ARIADOS
        r["art_sym"] = camel(const_of(r["art_from"]))                # Ariados
        r["cry"] = const_of(r["cry_from"])
        own = ART / "graphics/pokemon" / r["folder"]
        r["own"] = {f: (own / f).exists() for f in
                    ("front.png", "anim_front.png", "back.png", "normal.pal", "shiny.pal", "icon.png", "footprint.png")}
    return rows


def port_species(rows, stats):
    gfx_lines, ext_lines, anim_lines = [], [], []
    for r in rows:
        k, name, sym, art, asym = r["slot_key"], r["sw_name"], r["sym"], r["art"], r["art_sym"]
        tag = f"{name}: placeholder = {art}"
        own = r["own"]
        pics_own = own["front.png"] and own["anim_front.png"] and own["back.png"]
        g = f"graphics/pokemon/{r['folder']}"

        # palette: own art, else a tinted copy of the borrowed creature's palette (made once)
        pal = GAME / g / "normal.pal"
        if own["normal.pal"]:
            pal.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ART / g / "normal.pal", pal)
        elif not pal.exists():
            write_pal(pal, tint_palette(GAME / "graphics/pokemon" / folder_of(r["art_from"]) / "normal.pal", r["tint"]))
            stats["placeholder palette made"] += 1
        gfx_lines.append(f'const u32 gMonPalette_{sym}[] = INCGFX_U32("{g}/normal.pal", ".gbapal.lz");\n')
        ext_lines.append(f"extern const u32 gMonPalette_{sym}[];\n")
        pics = {"front": f"gMonFrontPic_{asym}", "back": f"gMonBackPic_{asym}",
                "still": f"gMonStillFrontPic_{asym}", "shiny": f"gMonShinyPalette_{asym}",
                "icon": f"gMonIcon_{asym}", "foot": f"gMonFootprint_{asym}"}
        if pics_own:
            for f in ("front.png", "anim_front.png", "back.png"):
                shutil.copyfile(ART / g / f, GAME / g / f)
            gfx_lines += [f'const u32 gMonStillFrontPic_{sym}[] = INCGFX_U32("{g}/front.png", ".4bpp.lz");\n',
                          f'const u32 gMonBackPic_{sym}[] = INCGFX_U32("{g}/back.png", ".4bpp.lz");\n']
            anim_lines.append(f'const u32 gMonFrontPic_{sym}[] = INCGFX_U32("{g}/anim_front.png", ".4bpp.lz");\n')
            ext_lines += [f"extern const u32 gMonFrontPic_{sym}[];\n", f"extern const u32 gMonBackPic_{sym}[];\n",
                          f"extern const u32 gMonStillFrontPic_{sym}[];\n"]
            pics.update(front=f"gMonFrontPic_{sym}", back=f"gMonBackPic_{sym}", still=f"gMonStillFrontPic_{sym}")
        if own["shiny.pal"]:
            shutil.copyfile(ART / g / "shiny.pal", GAME / g / "shiny.pal")
            gfx_lines.append(f'const u32 gMonShinyPalette_{sym}[] = INCGFX_U32("{g}/shiny.pal", ".gbapal.lz");\n')
            ext_lines.append(f"extern const u32 gMonShinyPalette_{sym}[];\n")
            pics["shiny"] = f"gMonShinyPalette_{sym}"
        if own["icon.png"]:
            shutil.copyfile(ART / g / "icon.png", GAME / g / "icon.png")
            gfx_lines.append(f'const u8 gMonIcon_{sym}[] = INCGFX_U8("{g}/icon.png", ".4bpp");\n')
            ext_lines.append(f"extern const u8 gMonIcon_{sym}[];\n")
            pics["icon"] = f"gMonIcon_{sym}"
        if own["footprint.png"]:
            shutil.copyfile(ART / g / "footprint.png", GAME / g / "footprint.png")
            gfx_lines.append(f'const u8 gMonFootprint_{sym}[] = INCGFX_U8("{g}/footprint.png", ".1bpp");\n')
            ext_lines.append(f"extern const u8 gMonFootprint_{sym}[];\n")
            pics["foot"] = f"gMonFootprint_{sym}"
        note = f"  // {name}" + ("" if pics_own else f": placeholder art = {art}")

        PG = "src/data/pokemon_graphics/"
        set_line(PG + "front_pic_table.h", r"gMonFrontPicTable\[\]", rf"SPECIES_SPRITE\({k}\s*,",
                 f"    SPECIES_SPRITE({k}, {pics['front']}),{note}")
        set_line(PG + "back_pic_table.h", r"gMonBackPicTable\[\]", rf"SPECIES_SPRITE\({k}\s*,",
                 f"    SPECIES_SPRITE({k}, {pics['back']}),{note}")
        set_line(PG + "still_front_pic_table.h", r"gMonStillFrontPicTable\[\]", rf"SPECIES_SPRITE\({k}\s*,",
                 f"    SPECIES_SPRITE({k}, {pics['still']}),{note}")
        set_line(PG + "palette_table.h", r"gMonPaletteTable\[\]", rf"SPECIES_PAL\({k}\s*,",
                 f"    SPECIES_PAL({k}, gMonPalette_{sym}),  // {name}")
        set_line(PG + "shiny_palette_table.h", r"gMonShinyPaletteTable\[\]", rf"SPECIES_SHINY_PAL\({k}\s*,",
                 f"    SPECIES_SHINY_PAL({k}, {pics['shiny']}),{note}")
        set_line(PG + "footprint_table.h", r"gMonFootprintTable\[\]", rf"\[SPECIES_{k}\]",
                 f"    [SPECIES_{k}] = {pics['foot']},{note}")
        set_line("src/pokemon_icon.c", r"gMonIconTable\[\]", rf"\[SPECIES_{k}\]",
                 f"    [SPECIES_{k}] = {pics['icon']},{note}")
        # copied from the borrowed creature: placement, animations, icon bank, elevation
        for rel, decl in ((PG + "front_pic_coordinates.h", r"gMonFrontPicCoords\[\]"),
                          (PG + "back_pic_coordinates.h", r"gMonBackPicCoords\[\]"),
                          (PG + "front_pic_anims.h", r"gMonFrontAnimsPtrTable\[\]"),
                          ("src/pokemon_animation.c", r"sSpeciesToBackAnimSet\[\]"),
                          (PG + "enemy_mon_elevation.h", r"gEnemyMonElevation\[NUM_SPECIES\]")):
            copy_entry(rel, decl, rf"\[SPECIES_{art}\]", rf"\[SPECIES_{k}\]", f"[SPECIES_{art}]", f"[SPECIES_{k}]", note)
        icon_idx = None
        if own["icon.png"]:
            icon_idx = icon_bank(r["folder"])
        if icon_idx is None:
            copy_entry("src/pokemon_icon.c", r"gMonIconPaletteIndices\[\]", rf"\[SPECIES_{art}\]",
                       rf"\[SPECIES_{k}\]", f"[SPECIES_{art}]", f"[SPECIES_{k}]", note)
        else:
            set_line("src/pokemon_icon.c", r"gMonIconPaletteIndices\[\]", rf"\[SPECIES_{k}\]",
                     f"    [SPECIES_{k}] = {icon_idx},  // {name}")
        for decl in (r"sMonFrontAnimIdsTable\[", r"sMonAnimationDelayTable\["):
            copy_entry("src/pokemon.c", decl, rf"\[SPECIES_{art} - 1\]", rf"\[SPECIES_{k} - 1\]",
                       f"[SPECIES_{art} - 1]", f"[SPECIES_{k} - 1]", note)

        # data copied from `copies`, with this species' stats, types and colour
        src = r["src"]
        info = get_block("src/data/pokemon/species_info.h", f"SPECIES_{src}")
        info = info.replace(f"[SPECIES_{src}]", f"[SPECIES_{k}]", 1)
        info = re.sub(r"\[SPECIES_\w+\] =[^\n]*", f"[SPECIES_{k}] = // {name}: net-new, data copied from {src}"
                      f" (mapping/new_species.csv)", info, count=1)
        for field, col in (("baseHP", "hp"), ("baseAttack", "attack"), ("baseDefense", "defense"),
                           ("baseSpeed", "speed"), ("baseSpAttack", "sp_attack"), ("baseSpDefense", "sp_defense")):
            info = re.sub(rf"(\.{field}\s*=\s*)\d+", rf"\g<1>{int(r[col])}", info)
        info = re.sub(r"\.types = \{[^}]*\}", f".types = {{ TYPE_{r['type1']}, TYPE_{r['type2']} }}", info)
        info = re.sub(r"\.bodyColor = \w+", f".bodyColor = BODY_COLOR_{r['body_color']}", info)
        set_block("src/data/pokemon/species_info.h", f"SPECIES_{k}", info)
        copy_entry("src/data/pokemon/level_up_learnset_pointers.h", r"gLevelUpLearnsets\[",
                   rf"\[SPECIES_{src}\]", rf"\[SPECIES_{k}\]", f"[SPECIES_{src}]", f"[SPECIES_{k}]",
                   f"  // {name}: learnset of {src}")
        tm = get_block("src/data/pokemon/tmhm_learnsets.h", f"SPECIES_{src}")
        set_block("src/data/pokemon/tmhm_learnsets.h", f"SPECIES_{k}",
                  tm.replace(f"[SPECIES_{src}]", f"[SPECIES_{k}]", 1).rstrip()
                  .replace("{ .learnset = {", f"{{ .learnset = {{ // {name}: TMs and HMs of {src}", 1))
        egg_moves(r, stats)
        evolution(r)
        set_line("src/data/text/species_names.h", r"gSpeciesNames\[", rf"\[SPECIES_{k}\]",
                 f'    [SPECIES_{k}] = _("{name}"),')
        stats["species ported"] += 1

    managed("src/data/graphics/pokemon.h", "net-new species", "".join(gfx_lines),
            anchor_before=r"^const u32 gMonPalette_Aurareaver\[\]")
    managed("include/graphics.h", "net-new species", "".join(ext_lines),
            anchor_before=r"^extern const u32 gMonPalette_Aurareaver\[\];")
    managed("src/anim_mon_front_pics.c", "net-new species", "".join(anim_lines), anchor_after=r"\Z")
    # the hand-written lines for the first three forms (2026-11-03) are now inside the managed blocks
    for rel, pat in (("src/data/graphics/pokemon.h", r"^const u32 gMonPalette_(Aurareaver|Kathwarden|Whillguard)\[\].*// .*placeholder tint\n"),
                     ("include/graphics.h", r"^extern const u32 gMonPalette_(Aurareaver|Kathwarden|Whillguard)\[\];\n(?![\s\S]*END net-new)")):
        s = Src.get(rel)
        s.text = re.sub(pat, "", s.text, flags=re.M)
    aliases = "".join(f"#define {r['constant']} {r['slot']} // net-new (mapping/new_species.csv)\n" for r in rows)
    s = Src.get("include/constants/species.h")
    s.text = re.sub(r"^#define SPECIES_(AURAREAVER|KATHWARDEN|WHILLGUARD) SPECIES_OLD_UNOWN_\w // net-new light/dark form \(old Unown slot\)\n",
                    "", s.text, flags=re.M)
    s.text = s.text.replace("#define SPECIES_OLD_UNOWN_Z 276\n\n\n", "#define SPECIES_OLD_UNOWN_Z 276\n\n")
    managed("include/constants/species.h", "net-new species", aliases, anchor_before=r"^#define SPECIES_TREECKO ")
    s.text = s.text.replace("// END net-new species\n#define SPECIES_TREECKO", "// END net-new species\n\n#define SPECIES_TREECKO")
    cries = "".join(f"    if (species == {r['slot']} - 1) // {r['sw_name']} uses {r['cry']}'s cry until it has its own\n"
                    f"        species = SPECIES_{r['cry']} - 1;\n" for r in rows if not own_cry(r))
    s = Src.get("src/pokemon.c")
    s.text = re.sub(r"    if \(species == SPECIES_OLD_UNOWN_\w - 1\) // \w+ uses \w+'s cry until it has its own\n"
                    r"        species = SPECIES_\w+ - 1;\n", "", s.text)
    managed("src/pokemon.c", "net-new species cries", cries, anchor_after=r"^u16 SpeciesToCryId\(u16 species\)\n\{\n",
            comment="    //")


def own_cry(r):
    return False  # net-new cries are NEEDS_PLACEHOLDER (mapping/audio.csv net:cry-*); none is made yet


def copy_entry(rel, decl, src_key, dst_key, src_tok, dst_tok, note):
    line = get_line(rel, decl, src_key)
    if line is None:
        del_line(rel, decl, dst_key)  # the borrowed creature has no entry (e.g. no elevation): neither does this one
        return
    line = re.sub(r"\s*//.*$", "", line.rstrip("\n"))
    line = re.sub(re.escape(src_tok) + r"\s*=", dst_tok + " =", line, count=1)
    set_line(rel, decl, dst_key, line + note)


def icon_bank(folder):
    p = TOOLS / "sprite-creature-icon-generator/icon_palette_indices.csv"
    for r in read_csv(p)[1]:
        if r.get("species") in (folder, f"species:{folder}"):
            return int(r["bank"])
    return None


def egg_moves(r, stats):
    """A species that does not evolve hatches into itself: give it the egg moves of the copied line's base."""
    rel = "src/data/pokemon/egg_moves.h"
    s = Src.get(rel)
    evo = Src.get("src/data/pokemon/evolution.h").text
    base = r["src"]
    for _ in range(3):
        m = re.search(rf"\[SPECIES_(\w+)\]\s*=\s*\{{[^\n]*SPECIES_{base}\}}", evo)
        if not m:
            break
        base = m.group(1)
    k = r["slot_key"]
    if r["evolves_from"]:  # a branch form: its eggs hatch into the first stage of its line
        s.text = re.sub(rf"    egg_moves\({k},.*?\),\n\n", "", s.text, flags=re.S)
        return
    m = re.search(rf"    egg_moves\({base},(.*?)\),\n", s.text, re.S)
    new = f"    egg_moves({k},{m.group(1)}),\n" if m else ""
    old = re.search(rf"    egg_moves\({k},.*?\),\n\n?", s.text, re.S)
    if old:
        s.text = s.text[:old.start()] + (new + "\n" if new else "") + s.text[old.end():]
    elif new:
        end = s.text.index("    EGG_MOVES_TERMINATOR")
        s.text = s.text[:end] + new + "\n" + s.text[end:]
        stats["egg moves"] += 1


def evolution(r):
    if not r["evolves_from"]:
        return
    evo = Src.get("src/data/pokemon/evolution.h").text
    pre = const_of(r["evolves_from"])
    if not re.search(rf"\[SPECIES_{pre}\][^\]]*?EVO_ITEM, {r['evo_item']}, {r['constant']}", evo, re.S):
        raise SystemExit(f"evolution.h: {pre} has no {r['evo_item']} evolution into {r['constant']}; add it by hand")


# ---------------------------------------------------------------- dex
def port_dex(rows, stats):
    rel = "include/constants/pokedex.h"
    s = Src.get(rel)
    dex = [r["slot_key"] for r in sorted(rows, key=lambda r: int(r["national_dex"]))]
    for prefix, last, count in (("NATIONAL_DEX", "DEOXYS", "NATIONAL_DEX_COUNT "),
                                ("HOENN_DEX", "DEOXYS", "HOENN_DEX_COUNT")):
        for k in dex:
            s.text = s.text.replace(f"    {prefix}_{k},\n", "", 1)
        new = "".join(f"    {prefix}_{k},\n" for k in dex)
        tag = f"    // Star Wars net-new species in the {'national' if prefix == 'NATIONAL_DEX' else 'regional'} Datapad (wiki/mapping/new_species.csv)\n"
        s.text = s.text.replace("    // Star Wars net-new species, in the Datapad (wiki/mapping/new_species.csv)\n", "")
        s.text = s.text.replace(tag, "")
        a = s.text.index(f"    {prefix}_{last},\n") + len(f"    {prefix}_{last},\n")
        s.text = s.text[:a] + tag + new + s.text[a:]
        s.text = re.sub(rf"#define {count}\s*\w+", f"#define {count} {prefix}_{dex[-1]}"
                        if prefix == "NATIONAL_DEX" else f"#define {count} {prefix}_{dex[-1]}", s.text)
    # check the numbers the csv promises
    nat = re.search(r"enum \{\n    NATIONAL_DEX_NONE,(.*?)\};", s.text, re.S).group(1)
    hoe = re.search(r"enum \{\n    HOENN_DEX_NONE,(.*?)\};", s.text, re.S).group(1)
    natl = re.findall(r"NATIONAL_DEX_(\w+),", nat)
    hoel = re.findall(r"HOENN_DEX_(\w+),", hoe)
    for r in rows:
        if natl.index(r["slot_key"]) + 1 != int(r["national_dex"]) or hoel.index(r["slot_key"]) + 1 != int(r["regional_dex"]):
            raise SystemExit(f"dex numbers of {r['sw_name']} do not match new_species.csv")

    # entries and text
    ent = Src.get("src/data/pokemon/pokedex_entries.h")
    txt = Src.get("src/data/pokemon/pokedex_text.h")
    for r in rows:
        k, sym = r["slot_key"], r["sym"]
        src = get_block_dex(ent.text, f"NATIONAL_DEX_{r['art']}")
        scale = {f: re.search(rf"\.{f} = (-?\d+)", src).group(1)
                 for f in ("pokemonScale", "pokemonOffset", "trainerScale", "trainerOffset")}
        cat = re.search(r'\.categoryName = _\("([^"]*)"\)', src).group(1)
        old = get_block_dex(ent.text, f"NATIONAL_DEX_{k}")
        if old:
            cat = re.search(r'\.categoryName = _\("([^"]*)"\)', old).group(1)  # port_names.py owns the category
            # port_sizes.py owns the size screen: keep its scales once the entry exists
            scale = {f: re.search(rf"\.{f} = (-?\d+)", old).group(1) for f in scale}
        block = (f"    [NATIONAL_DEX_{k}] = // {r['sw_name']} (mapping/new_species.csv)\n    {{\n"
                 f'        .categoryName = _("{cat}"),\n'
                 f"        .height = {round(float(r['height_m']) * 10)},\n"
                 f"        .weight = {round(float(r['weight_kg']) * 10)},\n"
                 f"        .description = g{sym}PokedexText,\n"
                 + "".join(f"        .{f} = {v},\n" for f, v in scale.items()) + "    },\n")
        if old:
            a = ent.text.index(old)
            ent.text = ent.text[:a] + block + ent.text[a + len(old):]
        else:
            end = ent.text.rindex("\n};")
            ent.text = ent.text[:end] + "\n\n" + block.rstrip("\n") + ent.text[end:]
        if f"g{sym}PokedexText[]" not in txt.text:
            txt.text = txt.text.rstrip("\n") + f'\n\nconst u8 g{sym}PokedexText[] = _(\n    "{r["sw_name"]}");\n'
        stats["datapad entry"] += 1
    port_orders(rows)


def get_block_dex(text, key):
    m = re.search(rf"^    \[{key}\] =[^\n]*\n    \{{.*?\n    \}},\n", text, re.S | re.M)
    return m.group(0) if m else None


def port_orders(rows):
    """Alphabetical order from the Star Wars names; the new species sorted into weight and height."""
    names = dict(re.findall(r'\[SPECIES_(\w+)\] = _\("([^"]*)"\)', Src.get("src/data/text/species_names.h").text))
    nat_enum = re.search(r"enum \{\n    NATIONAL_DEX_NONE,(.*?)\};", Src.get("include/constants/pokedex.h").text, re.S)
    nat = re.findall(r"NATIONAL_DEX_(\w+),", nat_enum.group(1))
    count = nat.index(re.search(r"#define NATIONAL_DEX_COUNT\s+NATIONAL_DEX_(\w+)",
                                Src.get("include/constants/pokedex.h").text).group(1)) + 1
    in_dex, out = nat[:count], nat[count:]
    o = Src.get("src/data/pokemon/pokedex_orders.h")
    alpha = sorted(in_dex, key=lambda c: (names.get(c, c).upper(), c))
    body = "".join(f"    NATIONAL_DEX_{c},\n" for c in out + alpha)
    o.text = re.sub(r"(const u16 gPokedexOrder_Alphabetical\[\] =\n\{\n).*?(\};)",
                    lambda m: m.group(1) + "    // the old-Unown slots outside the Datapad first, then A-Z by Star Wars name"
                    " (wiki/tools/port_creatures.py)\n" + body + m.group(2), o.text, count=1, flags=re.S)
    ent = Src.get("src/data/pokemon/pokedex_entries.h").text
    hw = {k: (int(h), int(w)) for k, h, w in re.findall(
        r"\[NATIONAL_DEX_(\w+)\] =[^\n]*\n    \{\n[^}]*?\.height = (\d+),\n\s*\.weight = (\d+),", ent)}
    for order, idx in (("Weight", 1), ("Height", 0)):
        m = re.search(rf"(const u16 gPokedexOrder_{order}\[\] =\n\{{\n)(.*?)(\}};)", o.text, re.S)
        cur = [c for c in re.findall(r"NATIONAL_DEX_(\w+)", m.group(2)) if c not in [r["slot_key"] for r in rows]]
        cur += [r["slot_key"] for r in rows]
        cur.sort(key=lambda c: (hw[c][idx], nat.index(c)))  # the same order port_sizes.py writes
        o.text = o.text[:m.start(2)] + "".join(f"    NATIONAL_DEX_{c},\n" for c in cur) + o.text[m.end(2):]


# ---------------------------------------------------------------- moves
def port_moves(stats):
    _, moves = read_csv(MAP / "new_moves.csv")
    hdr = Src.get("include/constants/moves.h")
    last = int(re.search(r"#define MOVES_COUNT (\d+)", hdr.text).group(1))
    for mv in moves:
        c = mv["constant"]
        clone = mv["clone_of"]
        if not re.search(rf"#define {c} \d+", hdr.text):
            hdr.text = hdr.text.replace(f"\n#define MOVES_COUNT {last}", f"#define {c} {last}\n\n#define MOVES_COUNT {last + 1}")
            hdr.text = hdr.text.replace(f"#define {c} {last}\n\n#define MOVES_COUNT", f"#define {c} {last}\n\n#define MOVES_COUNT")
            last += 1
            stats["move added"] += 1
        bm = "src/data/battle_moves.h"
        data = get_block_any(bm, clone)
        set_block_any(bm, c, re.sub(r"\[MOVE_\w+\] =", f"// Star Wars net-new: same data as {clone} (wiki/mapping/new_moves.csv)\n    [{c}] =", data, count=1))
        cm = "src/data/contest_moves.h"
        set_block_any(cm, c, get_block_any(cm, clone).replace(f"[{clone}]", f"[{c}]", 1))
        set_line("src/data/text/move_names.h", r"gMoveNames\[", rf"\[{c}\]", f'    [{c}] = _("{mv["sw_name"]}"),')
        d = "src/data/text/move_descriptions.h"
        sym = "s" + camel(c.removeprefix("MOVE_")) + "Description"
        s = Src.get(d)
        lines = mv["description"].split("\\n")
        body = "".join(f'    "{x}\\n"\n' for x in lines[:-1]) + f'    "{lines[-1]}");\n'
        if f"{sym}[]" in s.text:
            s.text = re.sub(rf"(static const u8 {sym}\[\] = _\(\n).*?\);\n", lambda m: m.group(1) + body, s.text, flags=re.S)
        else:
            a = s.text.index("const u8 *const gMoveDescriptionPointers")
            s.text = s.text[:a] + f"static const u8 {sym}[] = _(\n{body}\n" + s.text[a:]
        set_line(d, r"gMoveDescriptionPointers\[", rf"\[{c} - 1\]", f"    [{c} - 1] = {sym},")
        # the animation table: one .4byte per move, in order, before Move_COUNT
        a = Src.get("data/battle_anim_scripts.s")
        if f"\t.4byte {mv['animation']}\n" not in a.text:
            a.text = re.sub(r"\t\.4byte Move_COUNT @[^\n]*\n",
                            f"\t.4byte {mv['animation']}\n\t.4byte Move_COUNT @ cannot be reached, because last move is {mv['sw_name']}\n",
                            a.text, count=1)
    # order check: animation entries after Move_PSYCHO_BOOST follow the move numbers
    a = Src.get("data/battle_anim_scripts.s").text
    tail = re.findall(r"\t\.4byte (Move_\w+)", a[a.index("\t.4byte Move_PSYCHO_BOOST"):a.index("\t.4byte Move_COUNT @")])
    nums = sorted((int(n), c) for c, n in re.findall(r"#define (MOVE_\w+) (\d+)", Src.get("include/constants/moves.h").text)
                  if 354 <= int(n) < last)
    want = ["Move_" + c.removeprefix("MOVE_") for _, c in nums]
    if tail != want:
        raise SystemExit(f"battle_anim_scripts.s move table out of order: {tail} vs {want}")
    port_learnsets(stats)


def get_block_any(rel, key):
    s = Src.get(rel)
    m = re.search(rf"^    \[{key}\] =\n    \{{.*?\n    \}},\n", s.text, re.S | re.M)
    if not m:
        raise SystemExit(f"{rel}: no block for {key}")
    return m.group(0)


def set_block_any(rel, key, block):
    s = Src.get(rel)
    block = block.rstrip("\n") + "\n"
    m = re.search(rf"(^    // Star Wars net-new: same data[^\n]*\n)?^    \[{key}\] =\n    \{{.*?\n    \}},\n", s.text, re.S | re.M)
    if m:
        s.text = s.text[:m.start()] + "    " + block.lstrip(" ") + s.text[m.end():]
    else:
        end = s.text.index("\n};", s.text.index(f"[MOVE_PSYCHO_BOOST]"))
        s.text = s.text[:end] + "\n\n    " + block.lstrip(" ").rstrip("\n") + s.text[end:]


def port_learnsets(stats):
    _, rows = read_csv(MAP / "move_learnsets.csv")
    ptr = Src.get("src/data/pokemon/level_up_learnset_pointers.h").text
    lv = Src.get("src/data/pokemon/level_up_learnsets.h")
    tp = Src.get("src/data/trainer_parties.h")
    fr = Src.get("src/data/battle_frontier/battle_frontier_mons.h")
    for r in rows:
        sp = const_of(r["species"])
        ls = re.search(rf"\[SPECIES_{sp}\] = (s\w+LevelUpLearnset)", ptr).group(1)
        m = re.search(rf"static const u16 {ls}\[\] = \{{.*?\}};", lv.text, re.S)
        new = re.sub(rf"(LEVEL_UP_MOVE\(\s*\d+, ){r['replaces']}\)", rf"\g<1>{r['new_move']})", m.group(0))
        if new != m.group(0):
            stats["learnset swap"] += 1
        lv.text = lv.text[:m.start()] + new + lv.text[m.end():]
        # trainer parties: a member of this species with a custom move set
        def swap(mm):
            return mm.group(0).replace(r["replaces"] + ",", r["new_move"] + ",").replace(
                r["replaces"] + "}", r["new_move"] + "}")
        n0 = tp.text
        tp.text = re.sub(rf"\.species = SPECIES_{sp},[^}}]*?\.moves = \{{[^}}]*\}}", swap, tp.text)
        stats["trainer moves swapped"] += tp.text != n0
        n0 = fr.text
        fr.text = re.sub(rf"\.species = SPECIES_{sp},[^}}]*?\.moves = \{{[^}}]*\}}", swap, fr.text)
        stats["frontier moves swapped"] += fr.text != n0


# ---------------------------------------------------------------- assets
def port_assets(stats, dry):
    pal_dir = ART / "graphics/pokemon/icon_palettes"
    copied = 0
    for p in sorted((ART / "graphics/pokemon").rglob("*")):
        if not p.is_file():
            continue
        g = GAME / p.relative_to(ART)
        if p.name in ("icon.png", "footprint.png") or p.parent == pal_dir:
            if not g.exists():
                continue  # a net-new species' own art: port_species installs it
            if not filecmp.cmp(p, g, shallow=False):
                if not dry:
                    shutil.copyfile(p, g)
                copied += 1
    stats["icons, banks and footprints copied"] += copied
    # gMonIconPaletteIndices from the icon tool's csv
    _, idx = read_csv(TOOLS / "sprite-creature-icon-generator/icon_palette_indices.csv")
    for r in idx:
        sp = r["species"].removeprefix("species:")
        key = {"unown/a": "UNOWN", "castform/normal": "CASTFORM"}.get(sp, sp.upper().replace("/", "_"))
        if "/" in sp and key == sp.upper().replace("/", "_"):
            continue  # other Unown letters and Castform forms share the base entry
        rel = "src/pokemon_icon.c"
        cur = get_line(rel, r"gMonIconPaletteIndices\[\]", rf"\[SPECIES_{key}\]")
        if cur is None:
            continue
        new = re.sub(r"=\s*\d+", f"= {int(r['bank'])}", cur, count=1)
        if new != cur:
            set_line(rel, r"gMonIconPaletteIndices\[\]", rf"\[SPECIES_{key}\]", new)
            stats["icon banks set"] += 1
    # Unown letters' entries follow unown/a
    s = Src.get("src/pokemon_icon.c")
    a = re.search(r"\[SPECIES_UNOWN\] = (\d)", s.text).group(1)
    s.text = re.sub(r"(\[SPECIES_UNOWN_[B-Z_A-Z]+\] = )\d", rf"\g<1>{a}", s.text)
    s.text = re.sub(r"(\[SPECIES_UNOWN_(?:EMARK|QMARK)\] = )\d", rf"\g<1>{a}", s.text)
    # cries
    _, ready = read_csv(MAP / "audio_ready.csv")
    dcols, done = read_csv(MAP / "audio_done.csv")
    have = {d["asset_id"] for d in done}
    for r in ready:
        if not r["asset_id"].startswith("cry:"):
            continue
        src = ROOT / r["audio_file"]
        rel = r["audio_file"].removeprefix("audio/")
        dst = GAME / rel
        if not dst.exists():
            stats["cry slot missing"] += 1
            continue
        if not filecmp.cmp(src, dst, shallow=False):
            if not dry:
                shutil.copyfile(src, dst)
            stats["cries installed"] += 1
        if r["asset_id"] not in have:
            name = r["notes"].split(";")[0]
            done.append({"asset_id": r["asset_id"], "made_by": "cry-generator", "game_file": rel,
                         "notes": f"{name} ({r['spec']}); same cry slot and file name; installed by tools/port_creatures.py",
                         "called_by": ""})
            have.add(r["asset_id"])
    if not dry:
        write_csv(MAP / "audio_done.csv", dcols, done)


def mark_art_done(stats, dry):
    """game_status DONE for every creature art row whose wiki file is in ../game byte for byte."""
    cols, art = read_csv(DB / "pending_art.csv")
    pcols, port = read_csv(DB / "game_port.csv")
    port_by = {p["wiki_id"]: p for p in port if p["table"] == "pending_art.csv"}
    for a in art:
        if a["kind"] not in ("pokemon", "object_events") or a["art_status"] != "ART_READY":
            continue
        if a["kind"] == "object_events" and "/pokemon/" not in a["path"]:
            continue
        w, g = ART / a["path"], GAME / a["path"]
        ok = w.exists() and g.exists() and filecmp.cmp(w, g, shallow=False)
        if ok and a["game_status"] != "DONE":
            a["game_status"] = "DONE"
            stats["art rows marked DONE"] += 1
            if a["asset_id"] in port_by:
                port_by[a["asset_id"]]["game_status"] = "DONE"
    if not dry:
        write_csv(DB / "pending_art.csv", cols, art)
        write_csv(DB / "game_port.csv", pcols, port)


# ---------------------------------------------------------------- check
def check(stats):
    """database/creatures.csv: every species slot and the state of each of its assets in ../game."""
    sp_h = (GAME / "include/constants/species.h").read_text()
    slots = [(c, int(n)) for c, n in re.findall(r"#define SPECIES_(\w+) (\d+)", sp_h) if 0 < int(n) <= 411]
    names = dict(re.findall(r'\[SPECIES_(\w+)\] = _\("([^"]*)"\)', (GAME / "src/data/text/species_names.h").read_text()))
    _, wiki = read_csv(MAP / "species.csv")
    wiki = {const_of(r["emerald_id"]): r for r in wiki}
    _, newsp = read_csv(MAP / "new_species.csv")
    newsp = {r["slot"].removeprefix("SPECIES_"): r for r in newsp}
    pdx = (GAME / "include/constants/pokedex.h").read_text()
    natl = re.findall(r"NATIONAL_DEX_(\w+),", re.search(r"enum \{\n    NATIONAL_DEX_NONE,(.*?)\};", pdx, re.S).group(1))
    hoel = re.findall(r"HOENN_DEX_(\w+),", re.search(r"enum \{\n    HOENN_DEX_NONE,(.*?)\};", pdx, re.S).group(1))
    ncount = natl.index(re.search(r"#define NATIONAL_DEX_COUNT\s+NATIONAL_DEX_(\w+)", pdx).group(1)) + 1
    hcount = hoel.index(re.search(r"#define HOENN_DEX_COUNT\s+HOENN_DEX_(\w+)", pdx).group(1)) + 1
    ent = (GAME / "src/data/pokemon/pokedex_entries.h").read_text()
    _, art = read_csv(DB / "pending_art.csv")
    art_by = {}
    for a in art:
        m = re.match(r"graphics/pokemon/([^/]+)/(?:[^/]+/)?(front|back|anim_front|icon|footprint)\.png$", a["path"])
        if m:
            art_by.setdefault((m.group(1), m.group(2)), []).append(a)
    _, audio = read_csv(DB / "pending_audio.csv")
    cry_by = {a["asset_id"]: a for a in audio if a["asset_id"].startswith("cry:")}
    wild = set()
    for r in read_csv(DB / "encounters.csv")[1]:
        wild.add(r.get("sw_species", "").removeprefix("species:"))
    trainers = (GAME / "src/data/trainer_parties.h").read_text()
    rows = []
    for c, n in sorted(slots, key=lambda x: x[1]):
        if c.startswith("OLD_UNOWN_") and c not in newsp:
            continue
        w = wiki.get(c, {})
        new = newsp.get(c)
        folder = new["sw_name"].lower() if new else c.lower()
        st = {}
        for part in ("front", "back", "anim_front", "icon", "footprint"):
            rs = art_by.get((c.lower(), part), [])
            if new:
                st[part] = "PLACEHOLDER" if not (ART / "graphics/pokemon" / folder / f"{part}.png").exists() else "OWN"
            elif not rs:
                st[part] = "NO_ROW"
            else:
                st[part] = "DONE" if all(x["game_status"] == "DONE" for x in rs) else rs[0]["art_status"]
        cid = f"cry:{c.lower()}"
        cry = cry_by.get(cid)
        cry_state = ("PLACEHOLDER" if new else (cry["game_status"] if cry and cry["audio_status"] == "DONE"
                                                else (cry["audio_status"] if cry else "NO_ROW")))
        nd = natl.index(c) + 1 if c in natl else ""
        hd = hoel.index(c) + 1 if c in hoel else ""
        sid = new["emerald_id"] if new else (w.get("emerald_id") or f"species:{c.lower().replace('_', '-')}")
        rows.append({
            "species_id": sid, "constant": f"SPECIES_{c}", "species_index": n,
            "sw_name": (new or w).get("sw_name", ""), "game_name": names.get(c, ""),
            "name_in_game": "DONE" if names.get(c, "") == (new or w).get("sw_name", "") else "TODO",
            "kind": "NET_NEW" if new else "HOTSWAP",
            "national_dex": nd if nd and nd <= ncount else "", "regional_dex": hd if hd and hd <= hcount else "",
            "datapad_entry": "DONE" if re.search(rf"\[NATIONAL_DEX_{c}\] =", ent) and nd and nd <= ncount else "",
            "front": st["front"], "anim_front": st["anim_front"], "back": st["back"], "icon": st["icon"],
            "footprint": st["footprint"], "cry": cry_state,
            "wild": "yes" if sid.removeprefix("species:") in wild else "",
            "trainers": "yes" if re.search(rf"SPECIES_{c}\b", trainers) else "",
            "placeholder_from": new["art_from"] if new else "",
        })
    cols = list(rows[0].keys())
    write_csv(DB / "creatures.csv", cols, rows)
    stats["creatures.csv rows"] = len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("steps", nargs="*", default=["species", "dex", "moves", "assets", "check"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    from collections import Counter
    stats = Counter()
    rows = load_new_species()
    if "assets" in a.steps:  # first: the new species copy the icon bank of the creature they borrow from
        port_assets(stats, a.dry_run)
    if "species" in a.steps:
        port_species(rows, stats)
    if "dex" in a.steps:
        port_dex(rows, stats)
    if "moves" in a.steps:
        port_moves(stats)
    changed = Src.save_all(a.dry_run)
    if "assets" in a.steps:
        mark_art_done(stats, a.dry_run)
    if "check" in a.steps:
        check(stats)
    print(", ".join(f"{k}: {v}" for k, v in sorted(stats.items())))
    print("changed:" if changed else "no source changes", *changed, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())

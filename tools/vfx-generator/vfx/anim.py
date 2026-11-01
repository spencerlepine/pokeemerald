"""Storyboards: a move effect as script + sprite kit + sound, patched into the game.

A storyboard (art/moves/<name>.yaml) names:
  host:      the `Move_X:` label in data/battle_anim_scripts.s whose block it replaces
  kit:       art specs (art/<sheet>.yaml, `new:` sheets) that become ANIM_TAGs; the first sheet owns the
             palette, the others say `palette: {mode: kit}` and are locked to it (one palette per move)
  templates: sprite templates generated into src/battle_anim_sw_<name>.c (OAM shape from the sheet's
             frame, anim tables from slot lists, a callback from the engine)
  script:    the animation script lines (the game's own macro language); every tag, task, template and
             SE is checked against the game source and this kit; a net-new SE that is not made yet is
             replaced by its wiki placeholder (mapping/audio.csv placeholder_from) with a comment
  code:      optional C (static sprite callbacks) appended to the generated file; templates may name them

`patches(game, kits)` returns {relative path: new text} for a game tree: tag constants, pic/palette table
entries, INCGFX lines, extern declarations, the generated C file and the replaced script block. Every
inserted chunk is wrapped in `vfx:<name>:begin/end` markers, so applying twice is safe.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from .game import GAME, HERE, WIKI
from .spec import load_spec

MOVES_DIR = HERE / "art" / "moves"
ART_DIR = HERE / "art"
SHAPES = {(8, 8), (16, 16), (32, 32), (64, 64), (16, 8), (32, 8), (32, 16), (64, 32), (8, 16), (8, 32), (16, 32), (32, 64)}


# ----------------------------------------------------------------------------- game symbols

class GameSymbols:
    """Everything a script line may name, read from the game source once."""

    def __init__(self, game: Path = GAME):
        self.game = game

    @property
    @lru_cache(maxsize=None)
    def macros(self) -> set[str]:
        t = (self.game / "asm/macros/battle_anim_script.inc").read_text()
        return set(re.findall(r"^\s*\.macro\s+(\w+)", t, re.M))

    @property
    @lru_cache(maxsize=None)
    def tags(self) -> dict[str, int]:
        t = (self.game / "include/constants/battle_anim.h").read_text()
        return {m.group(1): int(m.group(2)) for m in re.finditer(r"#define (ANIM_TAG_\w+)\s+\(ANIM_SPRITES_START \+ (\d+)\)", t)}

    @property
    @lru_cache(maxsize=None)
    def bgs(self) -> dict[str, int]:
        t = (self.game / "include/constants/battle_anim.h").read_text()
        return {m.group(1): int(m.group(2)) for m in re.finditer(r"#define (BG_\w+)\s+(\d+)", t)}

    @property
    @lru_cache(maxsize=None)
    def tasks(self) -> set[str]:
        out = set()
        for f in (self.game / "src").glob("battle_anim*.c"):
            out |= set(re.findall(r"^void ((?:AnimTask|SoundTask)_\w+)\(u8 \w+\)", f.read_text(), re.M))
        return out

    @property
    @lru_cache(maxsize=None)
    def templates(self) -> set[str]:
        out = set()
        for f in (self.game / "src").glob("*.c"):
            out |= set(re.findall(r"const struct SpriteTemplate (g\w+SpriteTemplate)\b", f.read_text()))
        return out

    @property
    @lru_cache(maxsize=None)
    def callbacks(self) -> set[str]:
        t = (self.game / "include/battle_anim.h").read_text()
        return set(re.findall(r"^void (\w+)\(struct Sprite \*sprite\);", t, re.M))

    @property
    @lru_cache(maxsize=None)
    def ses(self) -> set[str]:
        t = (self.game / "include/constants/songs.h").read_text()
        return set(re.findall(r"#define (SE_\w+)\s", t))

    @property
    @lru_cache(maxsize=None)
    def script_labels(self) -> set[str]:
        t = (self.game / "data/battle_anim_scripts.s").read_text()
        return set(re.findall(r"^(\w+):", t, re.M))


@lru_cache(maxsize=None)
def se_placeholders() -> dict[str, tuple[str, str]]:
    """net-new SE constant -> (placeholder SE constant, wiki row id), from mapping/audio.csv."""
    out = {}
    p = WIKI / "mapping" / "audio.csv"
    if not p.exists():
        return out
    for r in csv.DictReader(open(p, encoding="utf-8", newline="")):
        if r["asset_id"].startswith("net:se-") and r.get("sw_constant"):
            ph = (r.get("placeholder_from") or "").removeprefix("audio:")
            out[r["sw_constant"]] = (ph, r["asset_id"])
    return out


# ----------------------------------------------------------------------------- kit

def _camel(name: str) -> str:
    return "".join(w.capitalize() for w in re.split(r"[_\-]", name))


@dataclass
class KitSheet:
    name: str              # art spec stem
    spec: dict
    tag: str               # ANIM_TAG_...
    png_out: Path | None = None    # built sheet (output/<name>/<file>.png)
    path: str = ""         # graphics/... path inside the game
    size: tuple[int, int] = (0, 0)
    frame: tuple[int, int] = (0, 0)
    owns_palette: bool = True

    @property
    def gfx_sym(self) -> str:
        return "gBattleAnimSpriteGfx_SW_" + _camel(self.name)

    @property
    def pal_sym(self) -> str:
        return "gBattleAnimSpritePal_SW_" + _camel(self.name)

    @property
    def nbytes(self) -> int:
        return self.size[0] * self.size[1] // 2

    @property
    def tiles_per_frame(self) -> int:
        return (self.frame[0] // 8) * (self.frame[1] // 8)


@dataclass
class Storyboard:
    name: str
    story: dict
    sheets: list[KitSheet]
    path: Path
    notes: list[str] = field(default_factory=list)

    @property
    def host(self) -> str:
        return self.story["host"]

    def sheet(self, name: str) -> KitSheet:
        for s in self.sheets:
            if s.name == name:
                return s
        raise KeyError(f"{self.name}: kit has no sheet {name!r}")


def load_story(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists() and (MOVES_DIR / f"{path}.yaml").exists():
        p = MOVES_DIR / f"{path}.yaml"
    st = yaml.safe_load(p.read_text())
    st.setdefault("name", p.stem)
    st["_path"] = str(p)
    for k in ("host", "kit", "script"):
        if k not in st:
            raise ValueError(f"{p}: storyboard needs `{k}`")
    return st


def build_kit(st: dict, run_pipeline=True) -> Storyboard:
    """Build every sheet of the kit through the drawing pipeline (sheet, gate, style score, card)."""
    from .pipeline import run
    sheets: list[KitSheet] = []
    first_png: Path | None = None
    first_ramps: dict = {}
    notes = []
    for i, item in enumerate(st["kit"]):
        name = item if isinstance(item, str) else item["sheet"]
        tag = (item.get("tag") if isinstance(item, dict) else None) or "ANIM_TAG_SW_" + name.upper()
        spec = load_spec(ART_DIR / f"{name}.yaml")
        if not spec.get("new"):
            raise ValueError(f"{name}: kit sheets must be `new:` sheets (one palette per move)")
        pal = spec.get("palette") or {}
        owns = True
        if pal.get("mode") == "kit":
            if first_png is None:
                raise ValueError(f"{name}: `palette: {{mode: kit}}` needs an earlier sheet that owns the palette")
            ramps = dict(first_ramps)
            ramps.update({k: [int(x) for x in v] for k, v in (pal.get("ramps") or {}).items()})
            spec["palette"] = {"mode": "locked", "source": str(first_png), "ramps": ramps}
            owns = False
        ks = KitSheet(name=name, spec=spec, tag=tag, path=spec["new"]["path"], size=tuple(spec["new"]["size"]),
                      frame=tuple(spec["new"].get("frame", spec["new"]["size"])), owns_palette=owns)
        if ks.frame not in SHAPES:
            raise ValueError(f"{name}: frame {ks.frame} is not an OBJ shape; use one of {sorted(SHAPES)}")
        if ks.size[0] != ks.frame[0]:
            raise ValueError(f"{name}: sheet width must equal the frame width (slots stack vertically)")
        if run_pipeline:
            r = run(spec)
            ks.png_out = r["built"].png
            notes += [f"[{name}] " + l for l in r["lines"] if l.startswith(("WARN", "palette gate", "STYLE SCORE"))]
            if first_png is None:
                first_png = ks.png_out
                first_ramps = dict(r["built"].pal.ramps)
        else:
            ks.png_out = HERE / "output" / name / Path(ks.path).name
            if not ks.png_out.exists():
                raise ValueError(f"{name}: not built yet (output/{name}); run without --no-build")
            if first_png is None:
                first_png = ks.png_out
        sheets.append(ks)
    return Storyboard(name=st["name"], story=st, sheets=sheets, path=Path(st["_path"]), notes=notes)


# ----------------------------------------------------------------------------- templates -> C

def _oam(ks: KitSheet, t: dict) -> str:
    affine = {"off": "AffineOff", "normal": "AffineNormal", "double": "AffineDouble"}[t.get("affine", "off")]
    obj = "ObjBlend" if t.get("blend") else "ObjNormal"
    return f"gOamData_{affine}_{obj}_{ks.frame[0]}x{ks.frame[1]}"


def _anim_cmds(ks: KitSheet, anim: list, loop: bool) -> list[str]:
    out = []
    for fr in anim:
        if isinstance(fr, dict):
            slot, dur = fr["slot"], fr.get("dur", 4)
            flags = [k for k in ("hflip", "vflip") if fr.get(k)]
        else:
            slot, dur = fr[0], fr[1]
            flags = [{"h": "hflip", "v": "vflip"}[c] for c in (fr[2] if len(fr) > 2 else "")]
        extra = "".join(f", .{ 'hFlip' if f == 'hflip' else 'vFlip'} = TRUE" for f in flags)
        out.append(f"ANIMCMD_FRAME({slot * ks.tiles_per_frame}, {dur}{extra})")
    out.append("ANIMCMD_JUMP(0)" if loop else "ANIMCMD_END")
    return out


def c_file(sb: Storyboard, syms: GameSymbols) -> str:
    """src/battle_anim_sw_<name>.c: anim tables and sprite templates of the kit."""
    lines = ["// generated by tools/vfx-generator (storyboard %s); do not edit by hand" % sb.name,
             '#include "global.h"', '#include "battle_anim.h"', '#include "sprite.h"',
             '#include "constants/battle_anim.h"', '#include "battle.h"', '#include "trig.h"', ""]
    code = (sb.story.get("code") or "").strip("\n")
    own_cbs = set(re.findall(r"^static void (\w+)\(struct Sprite \*\w*\)\s*$", code, re.M))
    if code:
        lines += [f"static void {c}(struct Sprite *);" for c in sorted(own_cbs)] + [""]
    for tname, t in (sb.story.get("templates") or {}).items():
        if not re.fullmatch(r"g\w+SpriteTemplate", tname):
            raise ValueError(f"{sb.name}: template name {tname!r} must look like gXxxSpriteTemplate")
        ks = sb.sheet(t["sheet"])
        pal_tag = sb.sheet(t["palette"]).tag if t.get("palette") else ks.tag
        cb = t.get("callback", "AnimSpriteOnMonPos")
        if cb not in syms.callbacks and cb not in own_cbs:
            raise ValueError(f"{sb.name}: {tname}: callback {cb} is not declared in include/battle_anim.h")
        anims = t.get("anims") or ([t["anim"]] if t.get("anim") else [])
        base = tname.removeprefix("g").removesuffix("SpriteTemplate")
        if anims:
            names = []
            for i, an in enumerate(anims):
                nm = f"sAnim_{base}_{i}"
                names.append(nm)
                lines.append(f"static const union AnimCmd {nm}[] =")
                lines.append("{")
                lines += ["    " + c + "," for c in _anim_cmds(ks, an, bool(t.get("loop")))]
                lines.append("};\n")
            lines.append(f"static const union AnimCmd *const sAnimTable_{base}[] =")
            lines.append("{")
            lines += [f"    {n}," for n in names]
            lines.append("};\n")
            anim_table = f"sAnimTable_{base}"
        else:
            anim_table = "gDummySpriteAnimTable"
        aff = t.get("affine_anims", "gDummySpriteAffineAnimTable")
        if isinstance(aff, list):
            names = []
            for i, an in enumerate(aff):
                nm = f"sAffine_{base}_{i}"
                names.append(nm)
                lines.append(f"static const union AffineAnimCmd {nm}[] =")
                lines.append("{")
                for fr in an:
                    if isinstance(fr, str):
                        lines.append("    " + fr + ",")
                    else:
                        xs, ys, rot, dur = fr
                        lines.append(f"    AFFINEANIMCMD_FRAME({xs}, {ys}, {rot}, {dur}),")
                if not (an and isinstance(an[-1], str)):
                    lines.append("    AFFINEANIMCMD_END,")
                lines.append("};\n")
            lines.append(f"static const union AffineAnimCmd *const sAffineTable_{base}[] =")
            lines.append("{")
            lines += [f"    {n}," for n in names]
            lines.append("};\n")
            aff = f"sAffineTable_{base}"
        lines += [f"const struct SpriteTemplate {tname} =", "{",
                  f"    .tileTag = {ks.tag},", f"    .paletteTag = {pal_tag},", f"    .oam = &{_oam(ks, t)},",
                  f"    .anims = {anim_table},", "    .images = NULL,", f"    .affineAnims = {aff},",
                  f"    .callback = {cb},", "};\n"]
    if code:
        lines += ["// storyboard callbacks (story `code:`)", code, ""]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- script

_TOKEN = re.compile(r"\b(ANIM_TAG_\w+|(?:AnimTask|SoundTask)_\w+|g\w+SpriteTemplate|SE_\w+|BG_\w+)\b")


def script_block(sb: Storyboard, syms: GameSymbols, kits: list[Storyboard] | None = None) -> tuple[str, list[str]]:
    """The `Host:` block. Returns (text, notes). Unknown symbols raise; net-new SEs get their placeholder."""
    kits = kits or [sb]
    kit_tags = {s.tag for k in kits for s in k.sheets}
    kit_tpls = {t for k in kits for t in (k.story.get("templates") or {})}
    kit_bgs = {b for k in kits for b in (k.story.get("bgs") or {})}
    ph = se_placeholders()
    notes, out = [], [f"{sb.host}:"]
    labels = {sb.host}
    raw = sb.story["script"].rstrip("\n").split("\n")
    for ln in raw:
        s = ln.split("@", 1)[0].rstrip()
        if not s.strip():
            if ln.strip().startswith("@"):
                out.append("\t" + ln.strip())
            continue
        if re.match(r"^\w+:\s*$", s):
            labels.add(s.strip()[:-1])
            out.append(s.strip())
            continue
        cmd = s.split()[0]
        if cmd not in syms.macros:
            raise ValueError(f"{sb.name}: unknown script command {cmd!r} in: {ln.strip()}")
        for tok in _TOKEN.findall(s):
            if tok.startswith("ANIM_TAG_") and tok not in syms.tags and tok not in kit_tags:
                raise ValueError(f"{sb.name}: unknown tag {tok}")
            if tok.startswith(("AnimTask_", "SoundTask_")) and tok not in syms.tasks:
                raise ValueError(f"{sb.name}: unknown task {tok} (new tasks are C work)")
            if tok.endswith("SpriteTemplate") and tok not in syms.templates and tok not in kit_tpls:
                raise ValueError(f"{sb.name}: unknown sprite template {tok}")
            if tok.startswith("BG_") and tok not in syms.bgs and tok not in kit_bgs:
                raise ValueError(f"{sb.name}: unknown backdrop {tok}")
            if tok.startswith("SE_") and tok not in syms.ses:
                if tok in ph and ph[tok][0] in syms.ses:
                    s = re.sub(r"\b" + tok + r"\b", ph[tok][0], s) + f"\t@ placeholder for {tok} ({ph[tok][1]})"
                    notes.append(f"SE {tok} is not made yet: {ph[tok][0]} plays instead (wiki {ph[tok][1]})")
                else:
                    raise ValueError(f"{sb.name}: unknown sound {tok} (no wiki placeholder either)")
        out.append("\t" + s.strip())
    if out[-1].strip() != "end":
        out.append("\tend")
    # jumps/calls to labels must exist (in this block or the game)
    for ln in out:
        m = re.match(r"\t(?:goto|call|jumpargeq|jumpreteq|jumprettrue|jumpretfalse|jumpifcontest|jumpifmoveturn|choosetwoturnanim)\s+(.*)", ln)
        if m:
            for lbl in re.findall(r"\b([A-Za-z_]\w*)\b", m.group(1)):
                if lbl[0].isupper() and lbl not in labels and lbl not in syms.script_labels and not lbl.isupper():
                    raise ValueError(f"{sb.name}: jump to unknown label {lbl}")
    return "\n".join(out) + "\n", notes


# ----------------------------------------------------------------------------- patches

MARK = {"c": ("// vfx:{n}:begin", "// vfx:{n}:end"), "s": ("@ vfx:{n}:begin", "@ vfx:{n}:end")}


def _strip_marked(text: str, name: str, kind: str) -> str:
    b, e = (m.format(n=name) for m in MARK[kind])
    return re.sub(re.escape(b) + r".*?" + re.escape(e) + r"\n?", "", text, flags=re.S)


def _marked(name: str, kind: str, body: str) -> str:
    b, e = (m.format(n=name) for m in MARK[kind])
    return f"{b}\n{body.rstrip()}\n{e}\n"


def _insert_before_table_end(text: str, table_sym: str, chunk: str) -> str:
    i = text.index(table_sym)
    j = text.index("\n};", i)
    return text[:j + 1] + chunk + text[j + 1:]


def replace_block(script: str, host: str, block: str, name: str) -> str:
    """Replace the host's block (label up to the next Move_/General_/Status_/Special_ label)."""
    m = re.search(r"^" + re.escape(host) + r":\n", script, re.M)
    if not m:
        raise ValueError(f"script label {host} not found")
    nxt = re.search(r"^(?:Move|General|Status|Special)_\w+:\n", script[m.end():], re.M)
    end = m.end() + (nxt.start() if nxt else len(script) - m.end())
    old = script[m.start():end]
    # sub-labels we drop must not be used elsewhere
    for lbl in re.findall(r"^(\w+):", old, re.M):
        if lbl != host and re.search(r"\b" + lbl + r"\b", script[:m.start()] + script[end:]):
            raise ValueError(f"{host}: its helper label {lbl} is used by other scripts; give the storyboard its own labels")
    marked = _marked(name, "s", block)
    return script[:m.start()] + marked + "\n" + script[end:]


def patches(game: Path, kits: list[Storyboard], syms: GameSymbols | None = None) -> tuple[dict[str, str], list[str]]:
    """{relative path: new file text} for all kits together (tags are numbered in order)."""
    syms = syms or GameSymbols(game)
    files: dict[str, str] = {}
    notes: list[str] = []

    def get(rel):
        if rel not in files:
            files[rel] = (game / rel).read_text() if (game / rel).exists() else ""
        return files[rel]

    next_idx = max(syms.tags.values()) + 1
    next_bg = max(syms.bgs.values()) + 1
    for sb in kits:
        n = sb.name
        # constants
        defs = []
        for ks in sb.sheets:
            if ks.tag in syms.tags:
                raise ValueError(f"{n}: tag {ks.tag} already exists in the game")
            defs.append(f"#define {ks.tag:<36}(ANIM_SPRITES_START + {next_idx})")
            next_idx += 1
        bg_defs = []
        for bg in (sb.story.get("bgs") or {}):
            bg_defs.append(f"#define {bg} {next_bg}")
            next_bg += 1
        t = _strip_marked(get("include/constants/battle_anim.h"), n, "c")
        last = list(re.finditer(r"^#define ANIM_TAG_\w+\s+\(ANIM_SPRITES_START \+ \d+\)\n", t, re.M))[-1]
        t = t[:last.end()] + _marked(n, "c", "\n".join(defs)) + t[last.end():]
        if bg_defs:
            lastbg = list(re.finditer(r"^#define BG_\w+ \d+\n", t, re.M))[-1]
            t = t[:lastbg.end()] + _marked(n + ":bg", "c", "\n".join(bg_defs)) + t[lastbg.end():]
        files["include/constants/battle_anim.h"] = t
        # tables
        t = _strip_marked(_strip_marked(get("src/data/battle_anim.h"), n, "c"), n + ":pal", "c")
        t = _strip_marked(t, n + ":bg", "c")
        pic = "\n".join(f"    {{{ks.gfx_sym}, 0x{ks.nbytes:04X}, {ks.tag}}}," for ks in sb.sheets)
        t = _insert_before_table_end(t, "gBattleAnimPicTable[] =", _marked(n, "c", pic))
        pal = "\n".join(f"    {{{(ks if ks.owns_palette else sb.sheets[0]).pal_sym}, {ks.tag}}}," for ks in sb.sheets)
        t = _insert_before_table_end(t, "gBattleAnimPaletteTable[] =", _marked(n + ":pal", "c", pal))
        bgs = sb.story.get("bgs") or {}
        if bgs:
            rows = "\n".join(f"    [{bg}] = {{gBattleAnimBgImage_SW_{_camel(b['name'])}, gBattleAnimBgPalette_SW_{_camel(b['name'])}, gBattleAnimBgTilemap_SW_{_camel(b['name'])}}},"
                             for bg, b in bgs.items())
            t = _insert_before_table_end(t, "gBattleAnimBackgroundTable[] =", _marked(n + ":bg", "c", rows))
        files["src/data/battle_anim.h"] = t
        # graphics
        inc = [f'const u32 {ks.gfx_sym}[] = INCGFX_U32("{ks.path}", ".4bpp.lz");' for ks in sb.sheets]
        inc += [f'const u32 {ks.pal_sym}[] = INCGFX_U32("{ks.path}", ".gbapal.lz");' for ks in sb.sheets if ks.owns_palette]
        ext = [f"extern const u32 {ks.gfx_sym}[];" for ks in sb.sheets]
        ext += [f"extern const u32 {ks.pal_sym}[];" for ks in sb.sheets if ks.owns_palette]
        for bg, b in bgs.items():
            cm = _camel(b["name"])
            inc += [f'const u32 gBattleAnimBgImage_SW_{cm}[] = INCGFX_U32("{b["path"]}.png", ".4bpp.lz");',
                    f'const u32 gBattleAnimBgPalette_SW_{cm}[] = INCGFX_U32("{b["path"]}.png", ".gbapal.lz");',
                    f'const u32 gBattleAnimBgTilemap_SW_{cm}[] = INCGFX_U32("{b["path"]}.bin", ".lz");']
            ext += [f"extern const u32 gBattleAnimBgImage_SW_{cm}[];", f"extern const u32 gBattleAnimBgPalette_SW_{cm}[];",
                    f"extern const u32 gBattleAnimBgTilemap_SW_{cm}[];"]
        files["src/graphics.c"] = _strip_marked(get("src/graphics.c"), n, "c").rstrip("\n") + "\n" + _marked(n, "c", "\n".join(inc))
        files["include/graphics.h"] = _strip_marked(get("include/graphics.h"), n, "c").rstrip("\n") + "\n" + _marked(n, "c", "\n".join(ext))
        # templates and script
        files[f"src/battle_anim_sw_{n}.c"] = c_file(sb, syms)
        block, bn = script_block(sb, syms, kits)
        notes += bn
        s = get("data/battle_anim_scripts.s")
        if f"@ vfx:{n}:begin" in s:
            raise ValueError(f"{n}: the script already has this storyboard applied; start from a clean tree")
        files["data/battle_anim_scripts.s"] = replace_block(s, sb.host, block, n)
    return files, notes


def installs(kits: list[Storyboard]) -> dict[str, Path]:
    """Sheet (and backdrop) files to copy into the game: {relative path: built file}."""
    out = {}
    for sb in kits:
        for ks in sb.sheets:
            if ks.png_out is None:
                raise ValueError(f"{sb.name}: kit not built")
            out[ks.path] = ks.png_out
        for bg, b in (sb.story.get("bgs") or {}).items():
            built = HERE / "output" / sb.name / "bg" / (Path(b["path"]).name + ".png")
            out[b["path"] + ".png"] = built
            out[b["path"] + ".bin"] = built.with_suffix(".bin")
    return out

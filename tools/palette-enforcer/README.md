# palette-enforcer

**Status: DONE.** The shared palette gate and post-processor for every art tool. The rules it enforces are in
[`../PALETTES.md`](../PALETTES.md): layer 1 is the GBA hardware, layer 2 the themes in
[`../../wiki/bible/PALETTE.md`](../../wiki/bible/PALETTE.md) (read directly, nothing copied).

```bash
cd tools/palette-enforcer
pip install -r requirements.txt            # pillow, numpy

python -m gba_palette themes -v            # every wiki theme and group, and lint the wiki values
python -m gba_palette enforce raw.png out.png --bpp 4 --key auto --theme alliance-dawn --free 4 --write-pal out.pal
python -m gba_palette check out.png --theme alliance-dawn          # the gate: exit 1 on any error
python -m gba_palette check walker.png --pal ../sprite-walker-generator/palettes/npc_2.pal
python -m gba_palette audit ../../game/graphics --lenient          # every PNG and .pal in a folder
python -m unittest discover -s tests
```

| Command | Does |
|---|---|
| `enforce SRC DST` | Any RGB/RGBA image to a legal indexed PNG: transparency to index 0 (alpha or `--key #hex` / `auto`), snap to GBA steps, then the palette: `--pal X.pal` maps onto a locked bank (indices kept), `--theme ID` pulls colours onto a theme (within `--tolerance`, default Delta E 12; beyond it at most `--free N` stay off-theme; `--strict-theme` none), otherwise median-cut to `--colours N` (default all the depth allows). Nearest colour in CIELAB, no dithering. Writes `--bpp 1/2/4/8` exactly; `--write-pal` writes the JASC file. Runs `check` on the result. |
| `check FILE...` | Errors: not indexed, too many colours or indices for the depth, colours off GBA steps (warnings with `--lenient`), pixels that disagree with `--pal`, size not a multiple of 8 (`--tile`), off-theme colours with `--strict-theme`. Warnings: duplicate GBA colours, off-theme colours. `.pal` files: whole 16-entry banks, steps, duplicates. |
| `audit DIR` | `check` on every PNG and `.pal` under a folder, failures only (`-v` adds warnings). |
| `themes` | The wiki's themes, ids and groups (`hud`, `factions`); fails if a wiki value is off-step. |

From Python (what a tool's own post-processing calls):

```python
import sys; sys.path.insert(0, "../palette-enforcer")
from gba_palette import check, core, enforce, themes

img, pal = enforce.enforce(Image.open("raw.png"), bpp=4, theme=themes.resolve(["imperial-order"]), free=3)
enforce.save(img, "out.png", 4)
rep = check.check_png("out.png", theme=themes.resolve(["imperial-order"]))
if not rep.ok: raise SystemExit("\n".join(rep.lines()))
```

Who calls it today: `sprite-walker-generator` (`build`, `install`), `title-screen-generator` (`ship.py`),
`cutscene-generator` (`scripts/rom-preview.sh`). Every tool still to be built calls it at the end of its pipeline
(see the status table in `../PALETTES.md`).

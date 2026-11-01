"""Design-loop viewer: python batches/view.py <name> [vanilla_sheet_stem ...] [--out DIR]
Renders art/<name>.yaml's stand frames (and a step frame) at 10x next to vanilla stand frames,
so the drawer can judge shading and silhouette pixel by pixel. Writes <out>/<name>.png
(default output/<name>/design.png)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from walker_sprite.spec import load, game_dir
from walker_sprite.sheet import spec_palette, read_frames
from walker_sprite.palette import load_jasc
from walker_sprite.preview import rgba_frame, BG
Z = 10
name = sys.argv[1]
TOOL = Path(__file__).resolve().parents[1]
sp = load(TOOL / "art" / f"{name}.yaml")
cols = spec_palette(sp)
panels = []
for fn in [f for f in ("down", "up", "left", "down_a", "left_a") if f in sp.frames]:
    panels.append(rgba_frame(sp.frames[fn], cols))
g = game_dir()
for v in sys.argv[2:]:
    frs, _ = read_frames(g / f"graphics/object_events/pics/people/{v}.png")
    pal = load_jasc(g / "graphics/object_events/palettes/npc_1.pal") if v not in ("fat_man",) else load_jasc(g / "graphics/object_events/palettes/npc_3.pal")
    # guess palette: try each and pick the one listed in graphics_info? keep simple: npc_1
    for i in (0, 1, 2):
        panels.append(rgba_frame(frs[i], pal))
W = sum(p.width + 2 for p in panels) * Z
im = Image.new("RGB", (W, 32 * Z), BG)
x = 0
for p in panels:
    big = p.resize((p.width * Z, p.height * Z), Image.NEAREST)
    im.paste(big, (x, 0), big)
    x += (p.width + 2) * Z
out = TOOL / "output" / name / "design.png"
out.parent.mkdir(parents=True, exist_ok=True)
im.crop((0, 8 * Z, W, 32 * Z)).save(out)
print(out)

"""python -m unittest discover -s tests   (from tools/palette-enforcer/)"""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from gba_palette import check, core, enforce, themes  # noqa: E402


def render(seed=0, size=32):
    """A noisy RGBA 'model output' with a transparent corner."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size]
    a = np.zeros((size, size, 4), np.uint8)
    a[..., 0], a[..., 1], a[..., 2] = (x * 7) % 256, (y * 5 + 30) % 256, ((x + y) * 3) % 256
    a[..., :3] = np.clip(a[..., :3].astype(int) + rng.integers(-5, 6, (size, size, 3)), 0, 255)
    a[..., 3] = 255
    a[:4, :4, 3] = 0
    return Image.fromarray(a, "RGBA")


class Core(unittest.TestCase):
    def test_snap(self):
        self.assertEqual(core.snap((255, 3, 12)), (248, 0, 16))
        self.assertTrue(core.on_step(core.snap((123, 45, 67))))

    def test_truncate_matches_gbagfx(self):
        self.assertEqual(core.truncate((255, 213, 7)), (248, 208, 0))


class Themes(unittest.TestCase):
    def test_wiki_palette_parses_and_is_legal(self):
        ts = themes.load()
        for tid in ["kyber-gold", "alliance-dawn", "imperial-order", "swamp-throne",
                    "hyperspace-console", "status-and-accents", "battle-backdrop"]:
            self.assertIn(tid, ts)
        self.assertEqual(themes.lint(), [])

    def test_groups(self):
        self.assertGreater(len(themes.resolve(["hud"])), 10)


class Enforce(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def run_enforce(self, **kw):
        out = self.tmp / "o.png"
        src = self.tmp / "in.png"
        render().save(src)
        enforce.enforce_file(src, out, **kw)
        return out

    def test_default_is_legal_4bpp(self):
        out = self.run_enforce(bpp=4)
        self.assertEqual(core.png_bit_depth(out), 4)
        rep = check.check_png(out)
        self.assertTrue(rep.ok, rep.lines())
        im = Image.open(out)
        self.assertEqual(im.getpixel((0, 0)), 0)  # transparent corner -> index 0

    def test_strict_theme_uses_only_theme_colours(self):
        th = themes.resolve(["kyber-gold"])
        out = self.run_enforce(bpp=4, theme=th, free=0)
        rep = check.check_png(out, theme=th, strict_theme=True, tolerance=0)
        self.assertTrue(rep.ok, rep.lines())

    def test_locked_palette_keeps_indices(self):
        pal = core.load_jasc(HERE.parents[1] / "sprite-walker-generator" / "palettes" / "npc_1.pal")
        out = self.run_enforce(bpp=4, pal=pal)
        rep = check.check_png(out, pal=pal, strict_step=False)
        self.assertTrue(rep.ok, rep.lines())

    def test_1bpp_and_8bpp(self):
        self.assertTrue(check.check_png(self.run_enforce(bpp=1)).ok)
        out = self.run_enforce(bpp=8)
        self.assertEqual(core.png_bit_depth(out), 8)
        self.assertTrue(check.check_png(out).ok)


class Gate(unittest.TestCase):
    def test_rgb_fails(self):
        p = Path(tempfile.mkdtemp()) / "rgb.png"
        render().convert("RGB").save(p)
        self.assertFalse(check.check_png(p).ok)

    def test_off_step_fails_unless_lenient(self):
        p = Path(tempfile.mkdtemp()) / "x.png"
        im = Image.new("P", (8, 8), 1)
        im.putpalette([0, 0, 0, 255, 213, 180] + [0] * 42)
        im.save(p, bits=4)
        self.assertFalse(check.check_png(p).ok)
        self.assertTrue(check.check_png(p, strict_step=False).ok)


if __name__ == "__main__":
    unittest.main()

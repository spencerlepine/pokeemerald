import { test } from "node:test";
import assert from "node:assert/strict";
import { Img } from "../src/core/image.ts";
import { pack } from "../src/core/color.ts";
import {
  encodeIndexed4, indexImage, newTileset, packCells, parsePal, renderScreen, tileScreen, unpackCells, imageTiles,
} from "../src/gba/gba.ts";
import { decodePng } from "../src/gba/pngread.ts";
import { loadSource } from "../src/node/load.ts";

const PAL = parsePal(["#000000", "#f80000", "#00f800", "#0000f8"], "test");

function sample(w: number, h: number): Img {
  const img = new Img(w, h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const v = (x * 7 + y * 3 + ((x >> 3) ^ (y >> 4))) % 5;
    if (v) img.set(x, y, PAL[Math.min(3, v)]);
  }
  return img;
}

test("BG screens round-trip through tiles + tilemap, with flip dedup", () => {
  const img = sample(256, 256);
  const idx = indexImage(img, PAL, "t");
  // mirror the right half so flips have something to find
  for (let y = 0; y < 256; y++) for (let x = 128; x < 256; x++) idx[y * 256 + x] = idx[y * 256 + 255 - x];
  const ts = newTileset();
  const map = tileScreen({ w: 256, h: 256, idx }, ts, 3);
  assert.ok(ts.tiles.length < 1024 / 2 + 2, `flip dedup: ${ts.tiles.length} tiles`);
  assert.equal(map[0] >> 12, 3);
  const back = renderScreen(ts.tiles, map, [PAL, PAL, PAL, PAL]);
  for (let i = 0; i < idx.length; i++) assert.equal(back.data[i] !== 0, idx[i] !== 0);
});

test("4bpp PNG encodes and decodes the same indices", () => {
  const idx = new Uint8Array(16 * 8).map((_, i) => i % 16);
  const d = decodePng(encodeIndexed4({ w: 16, h: 8, idx }, parsePal(Array(16).fill(0).map((_, i) => `#${(i * 8).toString(16).padStart(2, "0")}0000`), "p")));
  assert.deepEqual([...d.idx!], [...idx]);
});

test("off-palette colors are reported with coordinates", () => {
  const img = new Img(8, 8);
  img.set(2, 3, pack(100, 2, 250));
  assert.throws(() => indexImage(img, PAL, "x"), /2,3/);
});

test("OBJ cells pack to 1D tile order and unpack back", () => {
  const idx = indexImage(sample(64, 32), PAL, "t");
  const cells = [[32, 32], [16, 32], [16, 32]];
  const packed = packCells({ w: 64, h: 32, idx }, cells);
  // the 32x32 cell's 16 tiles come first, row-major within the cell
  assert.deepEqual([...imageTiles(packed)[4]], [...imageTiles({ w: 64, h: 32, idx })[8]]);
  assert.deepEqual([...unpackCells(packed, cells).idx], [...idx]);
});

test("small integers are palette indices", () => {
  const p = loadSource(`use(["#000000", "#f80000", "#00f800"]); sprite("a", { w: 2, h: 1 }, px(0, 0, 2), px(1, 0, "1"))`);
  const img = p.image("a");
  assert.equal(img.data[0], pack(0, 248, 0));
  assert.equal(img.data[1], pack(248, 0, 0));
});

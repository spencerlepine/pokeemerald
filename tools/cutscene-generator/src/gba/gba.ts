// GBA formats: 15-bit colors, 16-color palettes (JASC .pal), 4bpp 8x8 tiles, text-BG tilemaps.
// Everything the game's build (gbagfx) reads, so tool output drops into ../../game unchanged.
import { deflateSync, crc32 } from "node:zlib";
import { type Color, channels, pack, toHex, TRANSPARENT } from "../core/color.ts";
import { PxError } from "../core/errors.ts";
import { Img } from "../core/image.ts";

/** The color the GBA actually shows: 5 bits per channel, expanded back to 8 the way gbagfx/mGBA do. */
export function gbaColor(c: Color): Color {
  const [r, g, b] = channels(c);
  const e = (v: number) => ((v >> 3) << 3) | (v >> 5);
  return pack(e(r), e(g), e(b));
}

/** 15-bit BGR555 value. */
export function bgr555(c: Color): number {
  const [r, g, b] = channels(c);
  return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10);
}

export function readJasc(text: string, name = "pal"): Color[] {
  const lines = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  if (lines[0] !== "JASC-PAL") throw new PxError(`${name}: not a JASC palette`);
  const n = Number(lines[2]);
  return lines.slice(3, 3 + n).map((l) => {
    const [r, g, b] = l.split(/\s+/).map(Number);
    return pack(r, g, b);
  });
}

/** JASC palette exactly as the game's files are written (CRLF, 16 entries). */
export function writeJasc(colors: Color[]): string {
  const rows = ["JASC-PAL", "0100", String(colors.length), ...colors.map((c) => channels(c).slice(0, 3).join(" "))];
  return rows.join("\r\n") + "\r\n";
}

export function parsePal(list: (string | number)[], what: string): Color[] {
  if (!Array.isArray(list) || list.length < 1 || list.length > 16) throw new PxError(`${what}: pal must list 1-16 colors (index 0 = transparent)`);
  const out = list.map((c) => {
    if (typeof c === "number") return c >>> 0;
    const h = c.startsWith("#") ? c.slice(1) : c;
    if (!/^[0-9a-fA-F]{6}$/.test(h)) throw new PxError(`${what}: bad palette color '${c}' (use "#rrggbb")`);
    return pack(parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16));
  });
  while (out.length < 16) out.push(pack(0, 0, 0));
  return out;
}

/**
 * RGBA image -> palette indices. Transparent pixels (and pixels equal to entry 0) become 0.
 * Every other pixel must match a palette entry as a GBA color; offenders are listed.
 */
export function indexImage(img: Img, pal: Color[], what: string): Uint8Array {
  const look = new Map<number, number>();
  pal.forEach((c, i) => { if (i > 0 && !look.has(bgr555(c))) look.set(bgr555(c), i); });
  const zero = bgr555(pal[0]);
  const idx = new Uint8Array(img.w * img.h);
  const bad = new Map<string, string[]>();
  for (let i = 0; i < img.data.length; i++) {
    const c = img.data[i];
    if (c === TRANSPARENT) continue;
    const k = bgr555(c), j = look.get(k);
    if (j !== undefined) idx[i] = j;
    else if (k !== zero) {
      const hx = toHex(c), at = bad.get(hx) ?? [];
      if (at.length < 3) at.push(`${i % img.w},${Math.floor(i / img.w)}`);
      bad.set(hx, at);
    }
  }
  if (bad.size) {
    const list = [...bad].slice(0, 8).map(([h, at]) => `${h} at ${at.join(" ")}`).join("; ");
    throw new PxError(`${what}: ${bad.size} color(s) not in its 16-color palette: ${list}`);
  }
  return idx;
}

export interface Indexed { w: number; h: number; idx: Uint8Array }

/** A 4bpp tile: 64 indices. */
export type Tile = Uint8Array;

function tileAt(im: Indexed, tx: number, ty: number): Tile {
  const t = new Uint8Array(64);
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) t[y * 8 + x] = im.idx[(ty * 8 + y) * im.w + tx * 8 + x];
  return t;
}

function flipTile(t: Tile, h: boolean, v: boolean): Tile {
  const o = new Uint8Array(64);
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) o[y * 8 + x] = t[(v ? 7 - y : y) * 8 + (h ? 7 - x : x)];
  return o;
}

const key = (t: Tile) => Buffer.from(t).toString("latin1");

export interface Tileset {
  tiles: Tile[];
  index: Map<string, number>;
}

export function newTileset(blankFirst = true): Tileset {
  const ts: Tileset = { tiles: [], index: new Map() };
  if (blankFirst) addTile(ts, new Uint8Array(64));
  return ts;
}

function addTile(ts: Tileset, t: Tile): number {
  ts.tiles.push(t);
  ts.index.set(key(t), ts.tiles.length - 1);
  return ts.tiles.length - 1;
}

/**
 * Cut a 256x256 (or 512 wide/tall) indexed BG into tiles, sharing `ts` with other screens.
 * Returns the text-mode screen entries (tile | hflip<<10 | vflip<<11 | pal<<12), in GBA
 * screen-block order (32x32 blocks).
 */
export function tileScreen(im: Indexed, ts: Tileset, palSlot: number, flips = true): Uint16Array {
  if (im.w % 256 || im.h % 256) throw new PxError(`a BG screen must be 256x256 (or a multiple), got ${im.w}x${im.h}`);
  const bw = im.w / 256, bh = im.h / 256;
  const map = new Uint16Array(bw * bh * 1024);
  for (let by = 0; by < bh; by++) for (let bx = 0; bx < bw; bx++) for (let ty = 0; ty < 32; ty++) for (let tx = 0; tx < 32; tx++) {
    const t = tileAt(im, bx * 32 + tx, by * 32 + ty);
    let entry = -1;
    for (const [h, v] of flips ? [[false, false], [true, false], [false, true], [true, true]] : [[false, false]]) {
      const hit = ts.index.get(key(h || v ? flipTile(t, h, v) : t));
      if (hit !== undefined) { entry = hit | (h ? 0x400 : 0) | (v ? 0x800 : 0); break; }
    }
    if (entry < 0) entry = addTile(ts, t);
    map[(by * bw + bx) * 1024 + ty * 32 + tx] = entry | (palSlot << 12);
  }
  return map;
}

/** Lay tiles out as an image `cols` tiles wide (the game's tiles PNGs are 16 tiles = 128 px wide). */
export function tilesImage(tiles: Tile[], cols = 16): Indexed {
  const rows = Math.max(1, Math.ceil(tiles.length / cols));
  const im: Indexed = { w: cols * 8, h: rows * 8, idx: new Uint8Array(cols * 8 * rows * 8) };
  tiles.forEach((t, n) => {
    const tx = n % cols, ty = Math.floor(n / cols);
    for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) im.idx[(ty * 8 + y) * im.w + tx * 8 + x] = t[y * 8 + x];
  });
  return im;
}

/** Split an indexed image into tiles, row-major (how gbagfx reads a tiles PNG). */
export function imageTiles(im: Indexed): Tile[] {
  const out: Tile[] = [];
  for (let ty = 0; ty < im.h / 8; ty++) for (let tx = 0; tx < im.w / 8; tx++) out.push(tileAt(im, tx, ty));
  return out;
}

/**
 * Render a text-mode BG screen (1024 entries per 256x256 block) to RGBA. Index 0 is transparent.
 * `banks[n]` is BG palette n (16 colors); missing banks fall back to `banks[0]`.
 */
export function renderScreen(tiles: Tile[], map: Uint16Array, banks: Color[][], blocksW = 1): Img {
  const blocks = map.length / 1024, blocksH = Math.ceil(blocks / blocksW);
  const img = new Img(256 * blocksW, 256 * blocksH);
  for (let b = 0; b < blocks; b++) for (let i = 0; i < 1024; i++) {
    const e = map[b * 1024 + i], t = tiles[e & 0x3ff];
    if (!t) continue;
    const hf = e & 0x400, vf = e & 0x800, pal = banks[e >> 12] ?? banks[0];
    const ox = (b % blocksW) * 256 + (i % 32) * 8, oy = Math.floor(b / blocksW) * 256 + Math.floor(i / 32) * 8;
    for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) {
      const v = t[(vf ? 7 - y : y) * 8 + (hf ? 7 - x : x)];
      if (v) img.set(ox + x, oy + y, gbaColor(pal[v]));
    }
  }
  return img;
}

/** Indexed image -> RGBA with index 0 transparent, colors as the GBA shows them. */
export function renderIndexed(im: Indexed, pal: Color[]): Img {
  const img = new Img(im.w, im.h);
  for (let i = 0; i < im.idx.length; i++) if (im.idx[i]) img.data[i] = gbaColor(pal[im.idx[i]]);
  return img;
}

function chunk(type: string, data: Buffer): Buffer {
  const head = Buffer.alloc(8);
  head.writeUInt32BE(data.length, 0);
  head.write(type, 4, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([head.subarray(4), data])) >>> 0, 0);
  return Buffer.concat([head, data, crc]);
}

/** 4-bit indexed PNG with a 16-entry PLTE, the format of the game's 4bpp art. */
export function encodeIndexed4(im: Indexed, pal: Color[]): Buffer {
  if (pal.length !== 16) throw new PxError("4bpp PNG needs a 16-color palette");
  const rowLen = Math.ceil(im.w / 2) + 1, raw = Buffer.alloc(rowLen * im.h);
  for (let y = 0; y < im.h; y++) for (let x = 0; x < im.w; x++) {
    const v = im.idx[y * im.w + x] & 15, o = y * rowLen + 1 + (x >> 1);
    raw[o] |= x & 1 ? v : v << 4;
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(im.w, 0);
  ihdr.writeUInt32BE(im.h, 4);
  ihdr[8] = 4;
  ihdr[9] = 3;
  const plte = Buffer.alloc(48);
  pal.forEach((c, i) => { const [r, g, b] = channels(c); plte[i * 3] = r; plte[i * 3 + 1] = g; plte[i * 3 + 2] = b; });
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk("IHDR", ihdr), chunk("PLTE", plte),
    chunk("IDAT", deflateSync(raw, { level: 9 })), chunk("IEND", Buffer.alloc(0)),
  ]);
}

export function mapBytes(map: Uint16Array): Buffer {
  const b = Buffer.alloc(map.length * 2);
  map.forEach((v, i) => b.writeUInt16LE(v, i * 2));
  return b;
}

export function readMap(buf: Buffer): Uint16Array {
  const m = new Uint16Array(buf.length >> 1);
  for (let i = 0; i < m.length; i++) m[i] = buf.readUInt16LE(i * 2);
  return m;
}

/** Valid OBJ sizes (shape x size). */
export const OBJ_SIZES = ["8x8", "16x16", "32x32", "64x64", "16x8", "32x8", "32x16", "64x32", "8x16", "8x32", "16x32", "32x64"];

/**
 * OBJ cells and 1D mapping. gbagfx reads a sheet's tiles row-major over the whole PNG, and a
 * w x h sprite uses that many consecutive tiles. When a sheet holds sprites narrower than the PNG
 * (Emerald's trees_small.png: a 32x32 at tile 0, 16x32s at tiles 16 and 24) the PNG looks
 * scrambled. Cells are given left to right as [w, h]; `packCells` turns a readable strip into the
 * game's layout and `unpackCells` turns the game's layout back into a readable strip.
 */
export function packCells(im: Indexed, cells: number[][]): Indexed {
  const tiles: Tile[] = [];
  let x0 = 0;
  for (const [w, h] of cells) {
    for (let ty = 0; ty < h / 8; ty++) for (let tx = 0; tx < w / 8; tx++) tiles.push(tileAt(im, x0 / 8 + tx, ty));
    x0 += w;
  }
  const out = tilesImage(tiles, im.w / 8);
  if (out.h < im.h) { const full = new Uint8Array(im.w * im.h); full.set(out.idx); return { w: im.w, h: im.h, idx: full }; }
  return out;
}

export function unpackCells(im: Indexed, cells: number[][]): Indexed {
  const tiles = imageTiles(im), h = Math.max(...cells.map((c) => c[1])), w = cells.reduce((a, c) => a + c[0], 0);
  const out: Indexed = { w, h, idx: new Uint8Array(w * h) };
  let n = 0, x0 = 0;
  for (const [cw, ch] of cells) {
    for (let ty = 0; ty < ch / 8; ty++) for (let tx = 0; tx < cw / 8; tx++) {
      const t = tiles[n++];
      if (t) for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) out.idx[(ty * 8 + y) * w + x0 + tx * 8 + x] = t[y * 8 + x];
    }
    x0 += cw;
  }
  return out;
}

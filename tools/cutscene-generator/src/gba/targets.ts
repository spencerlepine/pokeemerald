// gba() targets -> game files, and ref() -> game files as images. Paths are relative to the
// game root (the folder with the Makefile), e.g. "graphics/intro/scene_2/trees.png".
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Color } from "../core/color.ts";
import { PxError, wrap } from "../core/errors.ts";
import { Img } from "../core/image.ts";
import type { GbaTarget, Project } from "../core/project.ts";
import {
  encodeIndexed4, gbaColor, packCells, unpackCells, type Indexed, imageTiles, indexImage, mapBytes, newTileset, OBJ_SIZES, parsePal, readJasc,
  readMap, renderIndexed, renderScreen, tileScreen, tilesImage, writeJasc,
} from "./gba.ts";
import { decodePng } from "./pngread.ts";

/** ../../game from this tool's folder. */
export function defaultGameDir(): string {
  return resolve(dirname(fileURLToPath(import.meta.url)), "../../../../game");
}

// ------------------------------------------------------------------ reading game files

/** The 16-color palette of a game PNG, or of a .pal file. */
export function readPalette(gameDir: string, path: string): Color[] {
  const abs = resolve(gameDir, path);
  if (!existsSync(abs)) throw new PxError(`no such game file: ${path}`);
  if (path.endsWith(".pal")) return readJasc(readFileSync(abs, "utf8"), path);
  const d = decodePng(readFileSync(abs), path);
  if (!d.plte) throw new PxError(`${path} is not an indexed PNG`);
  return d.plte.slice(0, 16);
}

/**
 * Load a game image the way the game shows it. Options:
 * - map: tilemap .bin; the PNG is then a tileset and the result is the screen (256x256 per block).
 * - screen: which 32x32 block of the map (default 0); "all" stacks every block vertically.
 * - pal: a .pal / .png path to color with instead of the PNG's own palette (e.g. the sunset palette);
 *   palSlot: the BG palette number the map's entries use for that palette (others fall back to it).
 * - frame: [w, h, n] cut frame n out of a vertical strip (OBJ sheets).
 * - cells: [[w, h], ...] the sheet holds several sprites in 1D tile order (see packCells).
 * - transparent: false keeps index 0 opaque.
 */
export function loadRef(gameDir: string, path: string, opts: Record<string, unknown>): Img {
  const abs = resolve(gameDir, path);
  if (!existsSync(abs)) throw new PxError(`no such game file: ${path} (game dir ${gameDir})`);
  const d = decodePng(readFileSync(abs), path);
  if (!d.idx || !d.plte) return new Img(d.w, d.h, d.rgba);
  const pal = typeof opts.pal === "string" ? readPalette(gameDir, opts.pal) : d.plte.slice(0, 16);
  while (pal.length < 16) pal.push(0);
  let im: Indexed = { w: d.w, h: d.h, idx: d.idx.map((v) => v & 15) };
  if (Array.isArray(opts.cells)) im = unpackCells(im, opts.cells as number[][]);
  let img: Img;
  if (typeof opts.map === "string") {
    const map = readMap(readFileSync(resolve(gameDir, opts.map)));
    const blocks = map.length / 1024, tiles = imageTiles(im);
    const banks: Color[][] = Array.from({ length: 16 }, () => pal);
    if (opts.screen === "all") img = renderScreen(tiles, map, banks, 1);
    else {
      const s = Number(opts.screen ?? 0);
      if (!(s >= 0 && s < blocks)) throw new PxError(`${opts.map} has ${blocks} screen block(s), asked for ${s}`);
      img = renderScreen(tiles, map.subarray(s * 1024, (s + 1) * 1024), banks);
    }
  } else img = renderIndexed(im, pal);
  if (opts.transparent === false) {
    const back = gbaColor(pal[0]);
    for (let i = 0; i < img.data.length; i++) if (!img.data[i]) img.data[i] = back;
  }
  if (Array.isArray(opts.frame)) {
    const [fw, fh, n = 0] = opts.frame as number[];
    return img.sub(0, n * fh, fw, fh);
  }
  return img;
}

// ------------------------------------------------------------------ writing game files

export interface GbaReport {
  lines: string[];
  errors: PxError[];
  written: string[];
}

/** Write every gba() target under outDir (mirroring the game's paths). */
export function writeGba(p: Project, outDir: string): GbaReport {
  const r: GbaReport = { lines: [], errors: [], written: [] };
  const put = (path: string, data: Buffer | string) => {
    const abs = join(outDir, path);
    mkdirSync(dirname(abs), { recursive: true });
    writeFileSync(abs, data);
    r.written.push(path);
  };
  for (const t of p.gbaTargets) {
    try { r.lines.push(runTarget(p, t, put)); } catch (e) { r.errors.push(wrap(e).within(`gba '${t.path}'`, t.loc)); }
  }
  return r;
}

function pal16(t: GbaTarget): Color[] {
  if (!Array.isArray(t.opts.pal)) throw new PxError(`gba '${t.path}': needs pal: [16 colors] (index 0 = transparent)`);
  return parsePal(t.opts.pal as string[], `gba '${t.path}'`);
}

function names(v: unknown): string[] {
  return (Array.isArray(v) ? v : [v]).filter((x): x is string => typeof x === "string");
}

function runTarget(p: Project, t: GbaTarget, put: (path: string, d: Buffer | string) => void): string {
  const o = t.opts, pal = pal16(t), what = `gba '${t.path}'`;
  const used = (idx: Uint8Array[]) => { const s = new Set<number>(); for (const a of idx) for (const v of a) if (v) s.add(v); return s.size; };

  if (t.path.endsWith(".pal")) {
    put(t.path, writeJasc(pal));
    return `${t.path}  palette, ${pal.length} colors`;
  }

  if (o.bg !== undefined) {
    // One tileset shared by every listed screen; the map file holds the screens back to back.
    const screens = names(o.bg), slot = Number(o.palSlot ?? 0);
    if (!screens.length) throw new PxError(`${what}: bg: ["scene", ...] lists the 256x256 screens`);
    const ts = newTileset(o.blank !== false);
    const maps: Uint16Array[] = [], idxs: Uint8Array[] = [];
    for (const n of screens) {
      const img = p.image(n);
      const im = { w: img.w, h: img.h, idx: indexImage(img, pal, `${what} screen '${n}'`) };
      idxs.push(im.idx);
      maps.push(tileScreen(im, ts, slot, o.flips !== false));
    }
    const max = Number(o.tiles ?? 512);
    if (ts.tiles.length > max) throw new PxError(`${what}: ${ts.tiles.length} unique tiles, budget is ${max} (simplify, or reuse more tiles)`);
    const tiles = tilesImage(ts.tiles, Number(o.cols ?? 16));
    put(t.path, encodeIndexed4(tiles, pal));
    if (typeof o.map !== "string") throw new PxError(`${what}: bg targets need map: "path/to/map.bin"`);
    const all = new Uint16Array(maps.reduce((a, m) => a + m.length, 0));
    let at = 0;
    for (const m of maps) { all.set(m, at); at += m.length; }
    put(o.map, mapBytes(all));
    return `${t.path}  BG tiles: ${ts.tiles.length} unique 8x8 tiles (budget ${max}), ${used(idxs)} colors; ${o.map}: ${screens.length} screen(s), palette slot ${slot}`;
  }

  if (o.obj !== undefined || o.image !== undefined) {
    // OBJ sheet: frames stacked vertically (anims expand to their frames), or one plain image.
    const list = names(o.obj ?? o.image), frames: Img[] = [];
    for (const n of list) {
      const def = p.assets.get(n);
      if (def?.kind === "anim") frames.push(...p.frames(n).map((f) => f.img));
      else frames.push(p.image(n));
    }
    if (!frames.length) throw new PxError(`${what}: nothing to write`);
    const fw = frames[0].w, fh = frames[0].h;
    for (const f of frames) if (f.w !== fw || f.h !== fh) throw new PxError(`${what}: frames differ in size (${fw}x${fh} vs ${f.w}x${f.h})`);
    if (o.obj !== undefined && !OBJ_SIZES.includes(`${fw}x${fh}`)) throw new PxError(`${what}: ${fw}x${fh} is not a GBA OBJ size (${OBJ_SIZES.join(", ")})`);
    if (fw % 8 || fh % 8) throw new PxError(`${what}: size must be a multiple of 8, got ${fw}x${fh}`);
    const sheet = new Img(fw, fh * frames.length);
    frames.forEach((f, i) => sheet.blit(f, 0, i * fh));
    let idx = indexImage(sheet, pal, what);
    if (Array.isArray(o.cells)) idx = packCells({ w: sheet.w, h: sheet.h, idx }, o.cells as number[][]).idx;
    put(t.path, encodeIndexed4({ w: sheet.w, h: sheet.h, idx }, pal));
    const tiles = new Set(imageTiles({ w: sheet.w, h: sheet.h, idx }).map((x) => Buffer.from(x).toString("latin1")));
    return `${t.path}  ${o.obj !== undefined ? "OBJ" : "image"} ${fw}x${fh} x ${frames.length} frame(s), ${used([idx])} colors, ${tiles.size} unique tiles`;
  }

  throw new PxError(`${what}: say what to write: bg: [screens] + map, obj: anim/sprite, image: sprite, or a .pal path`);
}

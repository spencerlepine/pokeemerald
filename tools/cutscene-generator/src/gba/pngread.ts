// Minimal PNG decoder for the game's art: indexed (1/2/4/8 bit), gray, RGB and RGBA, 8-bit
// channels, no interlacing. Enough to read every PNG under game/graphics.
import { inflateSync } from "node:zlib";
import { pack } from "../core/color.ts";
import { PxError } from "../core/errors.ts";

export interface DecodedPng {
  w: number;
  h: number;
  /** Palette indices (indexed PNGs only). */
  idx?: Uint8Array;
  /** PLTE as packed opaque colors (indexed PNGs only). */
  plte?: number[];
  /** RGBA pixels; index 0 of an indexed PNG is decoded as written (opaque unless tRNS says otherwise). */
  rgba: Uint32Array;
}

export function decodePng(buf: Buffer, name = "png"): DecodedPng {
  if (buf.readUInt32BE(0) !== 0x89504e47) throw new PxError(`${name}: not a PNG`);
  let p = 8, w = 0, h = 0, depth = 0, ctype = 0, interlace = 0;
  const idat: Buffer[] = [];
  let plte: number[] | undefined, trns: Buffer | undefined;
  while (p < buf.length) {
    const len = buf.readUInt32BE(p), type = buf.toString("ascii", p + 4, p + 8), data = buf.subarray(p + 8, p + 8 + len);
    if (type === "IHDR") { w = data.readUInt32BE(0); h = data.readUInt32BE(4); depth = data[8]; ctype = data[9]; interlace = data[12]; }
    else if (type === "PLTE") { plte = []; for (let i = 0; i + 2 < data.length; i += 3) plte.push(pack(data[i], data[i + 1], data[i + 2])); }
    else if (type === "tRNS") trns = Buffer.from(data);
    else if (type === "IDAT") idat.push(data);
    else if (type === "IEND") break;
    p += 12 + len;
  }
  if (interlace) throw new PxError(`${name}: interlaced PNGs are not supported`);
  const chans = { 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 }[ctype];
  if (!chans) throw new PxError(`${name}: unsupported PNG color type ${ctype}`);
  if (ctype !== 3 && ctype !== 0 && depth !== 8) throw new PxError(`${name}: only 8-bit channels are supported`);
  const bpp = Math.max(1, (chans * depth) >> 3), stride = Math.ceil((w * chans * depth) / 8);
  const raw = inflateSync(Buffer.concat(idat)), out = Buffer.alloc(stride * h);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)], src = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1));
    const row = out.subarray(y * stride, (y + 1) * stride), prev = y ? out.subarray((y - 1) * stride, y * stride) : undefined;
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? row[x - bpp] : 0, b = prev ? prev[x] : 0, c = prev && x >= bpp ? prev[x - bpp] : 0;
      let v = src[x];
      if (f === 1) v += a;
      else if (f === 2) v += b;
      else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) { const pp = a + b - c, pa = Math.abs(pp - a), pb = Math.abs(pp - b), pc = Math.abs(pp - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      row[x] = v & 255;
    }
  }
  const rgba = new Uint32Array(w * h);
  const sample = (y: number, x: number) => {
    const bit = x * depth, byte = out[y * stride + (bit >> 3)];
    return (byte >> (8 - depth - (bit & 7))) & ((1 << depth) - 1);
  };
  if (ctype === 3 || ctype === 0) {
    const idx = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) idx[y * w + x] = sample(y, x);
    if (ctype === 0) {
      const max = (1 << depth) - 1;
      for (let i = 0; i < idx.length; i++) { const g = Math.round((idx[i] * 255) / max); rgba[i] = pack(g, g, g); }
      return { w, h, rgba };
    }
    const pl = plte ?? [];
    for (let i = 0; i < idx.length; i++) {
      const c = pl[idx[i]] ?? 0, a = trns && idx[i] < trns.length ? trns[idx[i]] : 255;
      rgba[i] = a === 0 ? 0 : ((c & 0xffffff00) | a) >>> 0;
    }
    return { w, h, idx, plte: pl, rgba };
  }
  for (let i = 0; i < w * h; i++) {
    const y = Math.floor(i / w), x = i % w, r = out[y * stride + x * chans];
    if (ctype === 2) rgba[i] = pack(r, out[y * stride + x * chans + 1], out[y * stride + x * chans + 2]);
    else if (ctype === 4) { const a = out[y * stride + x * 2 + 1]; rgba[i] = a ? pack(r, r, r, a) : 0; }
    else { const a = out[y * stride + x * 4 + 3]; rgba[i] = a ? pack(r, out[y * stride + x * 4 + 1], out[y * stride + x * 4 + 2], a) : 0; }
  }
  return { w, h, rgba };
}

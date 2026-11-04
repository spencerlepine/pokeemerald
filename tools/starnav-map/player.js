// StarNAV map player: draws one 240x160 GBA screen per frame from the layers build.py made.
// D-pad / arrows move, A (Z, Enter) zooms in, B (X, Esc) zooms out, 1-5 pick the style.
// window.SN exposes setStyle / key / step / canvas for capture.py.
(function () {
  const DATA = window.STARNAV_DATA;
  const W = 240, H = 160, CELL = 8;
  const VIEW = DATA.view; // [x, y, w, h]
  const canvas = document.getElementById("screen");
  const ctx = canvas.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  const fonts = DATA.fonts;
  const images = {};
  let pending = 0;

  function load(key, src) {
    pending++;
    const im = new Image();
    im.onload = () => { pending--; if (!pending && SN.onready) SN.onready(); };
    im.src = src;
    images[key] = im;
  }
  DATA.styles.forEach((s, i) => {
    load(i + ":map", s.map);
    load(i + ":chrome", s.chrome);
    if (s.planets) for (const p in s.planets) load(i + ":planet:" + p, s.planets[p].img);
  });

  const st = { style: 0, zoom: 0, t: 0, anim: 8, cx: 4, cy: 8, planet: "TATOOINE", pcx: 0, pcy: 0 };
  const S = () => DATA.styles[st.style];
  const CW = 28, CH = 15;

  function rgb(c) { return c ? "rgb(" + c[0] + "," + c[1] + "," + c[2] + ")" : null; }
  function px(x, y, c, w, h) { ctx.fillStyle = rgb(c); ctx.fillRect(x, y, w || 1, h || 1); }

  function textWidth(t, f) { const g = fonts[f]; let w = 0; for (const ch of t) w += (g[ch] || [3])[0]; return w; }
  function text(x, y, t, f, ink, shadow, align) {
    const g = fonts[f];
    if (align === "right") x -= textWidth(t, f);
    if (align === "center") x -= Math.floor(textWidth(t, f) / 2);
    for (const ch of t) {
      const gl = g[ch]; if (!gl) { x += 3; continue; }
      const [w, rows] = gl;
      rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) {
        if (r[i] === "1") px(x + i, y + j, ink); else if (r[i] === "2" && shadow) px(x + i, y + j, shadow);
      } });
      x += w;
    }
  }

  // ---- what is under the cursor
  function section() {
    const s = S();
    if (s.style.zoom === "planet") {
      if (st.zoom === 0) return { id: null, planet: st.planet };
      const p = s.planets[st.planet];
      const id = (p.cells[st.pcy] || [])[st.pcx];
      return { id, planet: st.planet };
    }
    const id = (DATA.cells[st.cy] || [])[st.cx];
    const planet = (DATA.cell_planet[st.cy] || [])[st.cx];
    return { id, planet };
  }

  // ---- camera: map pixel at the top-left of the window, and scale
  function camera() {
    const s = S();
    const [, , vw, vh] = VIEW;
    if (s.style.zoom === "planet") return { x: 0, y: 0, k: 1 };
    const k = 1 + (st.zoom ? Math.min(1, st.anim / 8) : 1 - Math.min(1, st.anim / 8));
    const mx = st.cx * CELL + 4, my = st.cy * CELL + 4;
    let x = mx - vw / (2 * k), y = my - vh / (2 * k);
    x = Math.max(0, Math.min(224 - vw / k, x));
    y = Math.max(0, Math.min(120 - vh / k, y));
    return { x, y, k };
  }

  function drawMap() {
    const s = S();
    const [vx, vy, vw, vh] = VIEW;
    ctx.save();
    ctx.beginPath(); ctx.rect(vx, vy, vw, vh); ctx.clip();
    if (s.style.zoom === "planet" && st.zoom) {
      // planet opens: grows out of its globe for 8 frames
      const im = images[st.style + ":planet:" + st.planet];
      const t = Math.min(1, st.anim / 8);
      const [gx, gy] = s.style.galaxy[st.planet];
      const w = 224 * t, h = 120 * t;
      const x = vx + gx + (0 - gx) * t, y = vy + gy + (0 - gy) * t;
      if (t < 1) ctx.drawImage(images[st.style + ":map"], vx, vy);
      ctx.fillStyle = "rgb(8,8,16)"; if (t >= 1) ctx.fillRect(vx, vy, vw, vh);
      ctx.drawImage(im, Math.round(x), Math.round(y), Math.round(w), Math.round(h));
    } else {
      const c = camera();
      const im = images[st.style + ":map"];
      ctx.drawImage(im, c.x, c.y, vw / c.k, vh / c.k, vx, vy, vw, vh);
    }
    ctx.restore();
  }

  function cursor() {
    const s = S(); const cur = s.style.cursor;
    const [vx, vy, vw, vh] = VIEW;
    const blink = Math.floor(st.t / 16) % 2 === 0;
    const col = blink ? cur.col : cur.col2;
    let x, y, n;
    if (s.style.zoom === "planet") {
      if (!st.zoom) {   // ring around the globe
        const [gx, gy] = s.style.galaxy[st.planet];
        const r = s.style.radius[st.planet] + 3 + (blink ? 0 : 1);
        ctx.save(); ctx.beginPath(); ctx.rect(vx, vy, vw, vh); ctx.clip();
        for (let a = 0; a < 64; a++) {
          if (a % 8 > 4) continue;
          const ang = a / 64 * Math.PI * 2 + st.t / 40;
          px(Math.round(vx + gx + Math.cos(ang) * r - 0.5), Math.round(vy + gy + Math.sin(ang) * r - 0.5), cur.ring);
        }
        ctx.restore();
        return;
      }
      if (st.anim < 8) return;
      x = vx + st.pcx * CELL; y = vy + st.pcy * CELL; n = CELL;
    } else {
      const c = camera();
      x = vx + Math.round((st.cx * CELL - c.x) * c.k); y = vy + Math.round((st.cy * CELL - c.y) * c.k); n = Math.round(CELL * c.k);
    }
    const k = cur.kind;
    if (k === "box") {
      ctx.strokeStyle = rgb(col); ctx.lineWidth = 1; ctx.strokeRect(x - 0.5, y - 0.5, n + 1, n + 1);
      ctx.strokeStyle = "rgb(8,8,8)"; ctx.strokeRect(x - 1.5, y - 1.5, n + 3, n + 3);
    } else if (k === "brackets") {
      const L = Math.max(3, n / 3), o = blink ? 1 : 2;
      [[x - o, y - o, 1, 1], [x + n - 1 + o, y - o, -1, 1], [x - o, y + n - 1 + o, 1, -1], [x + n - 1 + o, y + n - 1 + o, -1, -1]]
        .forEach(([a, b, sx, sy]) => { for (let i = 0; i < L; i++) { px(a + sx * i, b, cur.col); px(a, b + sy * i, cur.col); } });
    } else if (k === "crosshair") {
      ctx.save(); ctx.beginPath(); ctx.rect(vx, vy, vw, vh); ctx.clip();
      for (let i = vx; i < vx + vw; i += 2) px(i, y + n / 2, [136, 24, 24]);
      for (let j = vy; j < vy + vh; j += 2) px(x + n / 2, j, [136, 24, 24]);
      ctx.restore();
      ctx.strokeStyle = rgb(col); ctx.strokeRect(x - 0.5, y - 0.5, n + 1, n + 1);
      px(x + n / 2, y + n / 2, cur.col2);
    } else if (k === "reticle") {
      const m = blink ? 2 : 3;
      ctx.strokeStyle = rgb(cur.col2);
      for (let i = 0; i < 3; i++) {
        px(x - m - i, y + n / 2, cur.col); px(x + n - 1 + m + i, y + n / 2, cur.col);
        px(x + n / 2, y - m - i, cur.col); px(x + n / 2, y + n - 1 + m + i, cur.col);
      }
      [[x, y], [x + n - 1, y], [x, y + n - 1], [x + n - 1, y + n - 1]].forEach(([a, b]) => px(a, b, cur.col2));
    }
  }

  function panel(sec) {
    // zoomed in: a card in the corner with the area's kind and what is there
    const s = S(); const pa = s.style.panel;
    if (!st.zoom || st.anim < 8 || !sec.id) return;
    const info = DATA.info[sec.id]; if (!info) return;
    const tags = [];
    if (info.bacta) tags.push("BACTA");
    if (info.market) tags.push("MARKET");
    if (info.hangar) tags.push("HANGAR");
    if (info.arena) tags.push("ARENA");
    const line1 = info.kind;
    const line2 = tags.join(" ");
    const w = Math.max(textWidth(line1, "small"), textWidth(line2, "small")) + 10;
    const h = line2 ? 26 : 16;
    const [vx, vy, vw, vh] = VIEW;
    // keep the card away from the cursor
    let curY = s.style.zoom === "planet" ? vy + st.pcy * CELL : vy + (st.cy * CELL - camera().y) * 2;
    const x = vx + vw - w - 3, y = curY > vy + vh / 2 ? vy + 3 : vy + vh - h - 3;
    px(x, y, pa.fill, w, h);
    ctx.strokeStyle = rgb(pa.edge); ctx.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1);
    text(x + 5, y + 2, line1, "small", pa.dim, null);
    if (line2) text(x + 5, y + 12, line2, "small", pa.ink, pa.shadow);
  }

  function header(sec) {
    const s = S(); const n = s.style.name, sub = s.style.sub;
    const name = sec.id ? DATA.info[sec.id].name : (sec.planet ? sec.planet : s.style.empty);
    if (name) text(n.x, n.y, name, n.font, n.ink, n.shadow, n.align);
    const p = sec.planet ? (sec.id ? sec.planet : (s.style.zoom === "planet" ? planetLine(sec.planet) : "")) : "";
    if (p) text(sub.x, sub.y, p, sub.font, sub.ink, sub.shadow, sub.align);
  }
  function planetLine(p) { const r = DATA.planets[p]; return r ? (r.role === "post" ? "POST-GAME" : "ACT " + r.act) : ""; }

  function draw() {
    ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
    drawMap();
    ctx.drawImage(images[st.style + ":chrome"], 0, 0);
    const sec = section();
    cursor();
    header(sec);
    panel(sec);
  }

  // ---- input
  function move(dx, dy) {
    const s = S();
    if (s.style.zoom === "planet") {
      if (st.zoom) {
        st.pcx = Math.max(0, Math.min(27, st.pcx + dx)); st.pcy = Math.max(0, Math.min(14, st.pcy + dy));
        return;
      }
      // galaxy: jump to the nearest planet that way
      const [x0, y0] = s.style.galaxy[st.planet];
      let best = null;
      for (const p in s.style.galaxy) {
        if (p === st.planet) continue;
        const [x, y] = s.style.galaxy[p];
        const along = (x - x0) * dx + (y - y0) * dy;
        if (along <= 0) continue;
        const across = Math.abs((x - x0) * dy) + Math.abs((y - y0) * dx);
        const score = along + across * 2;
        if (!best || score < best[0]) best = [score, p];
      }
      if (best) st.planet = best[1];
      return;
    }
    st.cx = Math.max(0, Math.min(CW - 1, st.cx + dx)); st.cy = Math.max(0, Math.min(CH - 1, st.cy + dy));
  }
  function zoom(on) {
    const s = S();
    if (on === !!st.zoom) return;
    if (on && s.style.zoom === "planet") {
      const p = s.planets[st.planet]; if (!p) return;
      const towns = Object.values(p.towns);
      const c = towns[0] || [14, 7];
      st.pcx = c[0]; st.pcy = c[1];
    }
    st.zoom = on ? 1 : 0; st.anim = 0;
  }
  const SN = window.SN = {
    canvas, state: st,
    setStyle(i) { st.style = i; st.zoom = 0; st.anim = 8; },
    key(k) {
      if (k === "left") move(-1, 0); else if (k === "right") move(1, 0);
      else if (k === "up") move(0, -1); else if (k === "down") move(0, 1);
      else if (k === "a") zoom(true); else if (k === "b") zoom(false);
    },
    goto(cx, cy) { st.cx = cx; st.cy = cy; },
    gotoPlanet(p) { st.planet = p; },
    step(n) { for (let i = 0; i < (n || 1); i++) { st.t++; st.anim++; } draw(); },
    draw,
  };
  const keys = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down", z: "a", Z: "a", Enter: "a", x: "b", X: "b", Escape: "b" };
  window.addEventListener("keydown", (e) => {
    if (keys[e.key]) { SN.key(keys[e.key]); e.preventDefault(); }
    if (e.key >= "1" && e.key <= "5") { SN.setStyle(+e.key - 1); if (window.onStyle) window.onStyle(); }
  });
  if (!DATA.capture) {
    SN.onready = () => { const loop = () => { SN.step(1); requestAnimationFrame(loop); }; loop(); };
  }
})();

// Drives out/capture.html in the pre-installed Playwright Chromium and writes raw 240x160 frames.
// Called by capture.py: node capture.js <capture.html> <frames dir> <tours.json>
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
(async () => {
  const [html, dir, toursFile] = process.argv.slice(2);
  const tours = JSON.parse(fs.readFileSync(toursFile, "utf8"));
  const b = await chromium.launch();
  const page = await b.newPage();
  await page.goto("file://" + path.resolve(html));
  await page.waitForFunction("window.SN && SN.canvas");
  await page.waitForTimeout(500);
  const save = async (file) => {
    const url = await page.evaluate("SN.canvas.toDataURL('image/png')");
    fs.writeFileSync(file, Buffer.from(url.split(",")[1], "base64"));
  };
  for (const t of tours) {   // {name, style, steps: [[js, hold, still?]]}
    const d = path.join(dir, t.name);
    fs.mkdirSync(d, { recursive: true });
    await page.evaluate(`SN.setStyle(${t.style})`);
    let n = 0;
    for (const [js, hold, still] of t.steps) {
      if (js) await page.evaluate(js);
      for (let i = 0; i < hold; i += 2) {
        await page.evaluate("SN.step(2)");
        if (!still) await save(path.join(d, String(n++).padStart(4, "0") + ".png"));
      }
      if (still) await save(path.join(d, still + ".png"));
    }
  }
  await b.close();
})();

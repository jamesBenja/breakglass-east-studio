// Rasterise drawings/v05/*.svg -> .png at 1.5x (the scale used for the committed PNGs).
// Usage: node model/rasterise_v05_drawings.js [name-filter]
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const dir = path.join(__dirname, '..', 'drawings', 'v05'); const filt = process.argv[2] || '';
  const b = await chromium.launch();
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg') && f.includes(filt))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8'); const m = svg.match(/width="(\d+)" height="(\d+)"/);
    const p = await b.newPage({ viewport: { width: +m[1], height: +m[2] }, deviceScaleFactor: 1.5 });
    await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await p.screenshot({ path: path.join(dir, f.replace('.svg', '.png')), clip: { x: 0, y: 0, width: +m[1], height: +m[2] } });
    await p.close(); console.log('png', f);
  }
  await b.close();
})();

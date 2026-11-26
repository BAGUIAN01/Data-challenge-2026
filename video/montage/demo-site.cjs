// node demo-site.cjs out_dir : records a short tour of the live site (screencast frames with their timestamps).
// A visible cursor is drawn in the page (the real one is not captured); clicks show a ring.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const out = process.argv[2];
  fs.mkdirSync(out + '/raw', { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1.2 });
  await p.goto('https://kalantigui-decrochage.vercel.app/', { waitUntil: 'networkidle', timeout: 60000 });
  await p.addStyleTag({ content: `
    #vc { position: fixed; left: 0; top: 0; width: 34px; height: 34px; z-index: 99999; pointer-events: none; transform: translate(800px, 450px); transition: none; }
    #vc svg { filter: drop-shadow(0 2px 3px rgba(0,0,0,.35)); }
    .vr { position: fixed; width: 20px; height: 20px; margin: -10px 0 0 -10px; border-radius: 50%; border: 4px solid #FDCD2F; z-index: 99998; pointer-events: none; animation: vr .55s ease-out forwards; }
    @keyframes vr { from { transform: scale(.4); opacity: 1; } to { transform: scale(3.2); opacity: 0; } }` });
  await p.evaluate(() => {
    const c = document.createElement('div');
    c.id = 'vc';
    c.innerHTML = '<svg viewBox="0 0 24 24" width="34" height="34"><path d="M4 2l16 9-7 2 4 8-3 1.5-4-8-6 5z" fill="#13294B" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.body.appendChild(c);
    addEventListener('mousemove', (e) => { c.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 2}px)`; }, true);
    addEventListener('mousedown', (e) => { const r = document.createElement('div'); r.className = 'vr'; r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; document.body.appendChild(r); setTimeout(() => r.remove(), 700); }, true);
  });
  const cdp = await p.context().newCDPSession(p);
  const frames = [];
  let t0 = null;
  cdp.on('Page.screencastFrame', async (f) => {
    const ts = f.metadata.timestamp;
    if (t0 === null) t0 = ts;
    const name = `raw/s${String(frames.length).padStart(5, '0')}.jpg`;
    fs.writeFileSync(out + '/' + name, Buffer.from(f.data, 'base64'));
    frames.push([name, ts - t0]);
    await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  const marks = [];
  const mark = (k) => marks.push([k, Date.now()]);
  const start = Date.now();
  const move = async (x, y, steps = 28) => { await p.mouse.move(x, y, { steps }); };
  const center = async (loc) => { const bb = await loc.boundingBox(); return [bb.x + bb.width / 2, bb.y + bb.height / 2]; };
  mark('start');
  await p.mouse.move(820, 500);
  await p.waitForTimeout(1200);
  // 1. the forecast year
  let [x, y] = await center(p.getByRole('button', { name: '26/27' }));
  await move(x, y); await p.waitForTimeout(150); mark('annee'); await p.mouse.click(x, y); await p.waitForTimeout(1500);
  // 2. a region: Koulsé, its panel, then down to "Sur quoi agir"
  [x, y] = await center(p.locator('path[aria-label="Koulsé : ouvrir l\'aperçu"]'));
  await move(x, y + 20); await p.waitForTimeout(250); mark('koulse'); await p.mouse.click(x, y + 20); await p.waitForTimeout(2200);
  await move(250, 520, 22); await p.waitForTimeout(300);
  mark('scroll');
  for (let i = 0; i < 14; i++) { await p.mouse.wheel(0, 45); await p.waitForTimeout(60); }
  await p.waitForTimeout(2200);
  // 3. back to the map, then another region: Goulmou + Sirba + Tapoa
  [x, y] = await center(p.getByText('Carte', { exact: true }).first());
  await move(x, y); await p.waitForTimeout(150); mark('retour'); await p.mouse.click(x, y); await p.waitForTimeout(1600);
  [x, y] = await center(p.locator('path[aria-label="Goulmou + Sirba + Tapoa : ouvrir l\'aperçu"]'));
  await move(x, y); await p.waitForTimeout(250); mark('est'); await p.mouse.click(x, y); await p.waitForTimeout(2200);
  await move(250, 520, 22); await p.waitForTimeout(300);
  for (let i = 0; i < 14; i++) { await p.mouse.wheel(0, 45); await p.waitForTimeout(60); }
  await p.waitForTimeout(2200);
  mark('fin');
  await cdp.send('Page.stopScreencast');
  await p.waitForTimeout(300);
  fs.writeFileSync(out + '/frames.json', JSON.stringify({ frames, marks: marks.map(([k, t]) => [k, (t - start) / 1000]) }));
  console.log(frames.length, 'frames over', frames.length ? frames[frames.length - 1][1].toFixed(2) : 0, 's');
  await b.close();
})();

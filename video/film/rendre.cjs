// node rendre.cjs frames_dir [fps] [from] [to] : every frame of the film as a JPEG
const { chromium } = require('playwright');
(async () => {
  const [dir, fps = 30, from = 0, to] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e)));
  await p.goto('file://' + __dirname + '/film.html'); await p.evaluate(() => document.fonts.ready);
  const end = to ? +to : await p.evaluate(() => SC.end);
  const n0 = Math.round(+from * fps), n1 = Math.round(end * fps);
  for (let n = n0; n < n1; n++) {
    await p.evaluate((t) => window.render(t), n / fps);
    await p.screenshot({ path: `${dir}/f${String(n).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 94, clip: { x: 0, y: 0, width: 1920, height: 1080 } });
  }
  if (errs.length) console.log(errs.slice(0, 5).join('\n'));
  console.log('frames', n0, n1);
  await b.close();
})();

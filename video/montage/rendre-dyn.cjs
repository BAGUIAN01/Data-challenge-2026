// node rendre-dyn.cjs work_dir [stills t1,t2]: every frame of the dynamic edit (or a few stills)
const { chromium } = require('playwright');
(async () => {
  const [work, stills] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e)));
  await p.goto('file://' + work + '/dyn.html'); await p.evaluate(() => document.fonts.ready);
  const T = await p.evaluate(() => window.DURATION);
  const list = stills ? stills.split(',').map(Number) : [...Array(Math.round(T * 30)).keys()].map((n) => n / 30);
  const dir = work + (stills ? '/stills' : '/out');
  require('fs').mkdirSync(dir, { recursive: true });
  for (const [i, t] of list.entries()) {
    await p.evaluate((t) => window.render(t), t);
    await p.screenshot({ path: `${dir}/${stills ? 's' + t : 'f' + String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93 });
  }
  if (errs.length) console.log(errs.slice(0, 5).join('\n'));
  console.log('duration', T, 'frames', list.length);
  await b.close();
})();

// node stills.cjs out_dir t1,t2,... : renders chosen instants to PNG for checking
const { chromium } = require('playwright');
(async () => {
  const [out, list] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e))); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + __dirname + '/film.html'); await p.evaluate(() => document.fonts.ready);
  for (const t of list.split(',').map(Number)) {
    await p.evaluate((t) => window.render(t), t);
    await p.locator('#film').screenshot({ path: `${out}/t${String(t).replace('.', '_')}.png` });
  }
  if (errs.length) console.log(errs.join('\n'));
  await b.close();
})();

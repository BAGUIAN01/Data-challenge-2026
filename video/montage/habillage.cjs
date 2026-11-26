const { chromium } = require('playwright');
(async () => {
  const out = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + __dirname + '/habillage.html'); await p.evaluate(() => document.fonts.ready);
  for (const id of ['fond', 'bandeau', 'bandeau2']) await p.locator('#' + id).screenshot({ path: `${out}/${id}.png`, omitBackground: true });
  await b.close();
})();

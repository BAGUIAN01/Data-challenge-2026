const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + __dirname + '/demo-cadre.html'); await p.evaluate(() => document.fonts.ready);
  await p.locator('#f').screenshot({ path: process.argv[2] }); await b.close(); })();

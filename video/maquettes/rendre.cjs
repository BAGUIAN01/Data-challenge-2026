const { chromium } = require('playwright');
(async () => {
  const [html, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + html); await p.evaluate(() => document.fonts.ready);
  const n = await p.locator('section.f').count();
  for (let i = 0; i < n; i++) await p.locator('section.f').nth(i).screenshot({ path: `${out}/m${i + 1}.png` });
  await b.close();
})();

const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file:///home/user/data-challenge-2026/rapport/rapport_defi1.html', { waitUntil: 'networkidle' });
  await p.pdf({ path: '/home/user/data-challenge-2026/rapport/rapport_defi1.pdf', format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font:7.5pt Inter,sans-serif;color:#7d8799;padding:0 16mm;display:flex;justify-content:space-between"><span>Anticiper le risque de décrochage scolaire · Défi 1</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '15mm', bottom: '16mm', left: '16mm', right: '16mm' } });
  await b.close();
})();

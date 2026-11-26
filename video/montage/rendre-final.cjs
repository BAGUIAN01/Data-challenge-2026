// node rendre-final.cjs work_dir from to : renders frames [from, to) of work/plan.json, each from the face page or the film
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [work, from, to] = process.argv.slice(2);
  const P = JSON.parse(fs.readFileSync(work + '/plan.json')); const plan = P.frames, caps = P.caps;
  const b = await chromium.launch();
  const open = async (url) => { const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); await p.goto(url); await p.evaluate(() => document.fonts.ready); return p; };
  const dyn = await open('file://' + work + '/dyn.html');
  const film = await open('file://' + path.resolve(__dirname, '../film/film.html'));
  const dir = work + '/final';
  fs.mkdirSync(dir, { recursive: true });
  const n1 = Math.min(plan.length, +(to || plan.length));
  for (let n = +(from || 0); n < n1; n++) {
    const [which, t, T] = plan[n];
    const p = which === 'dyn' ? dyn : film;
    await p.evaluate((t) => window.render(t), t);
    if (which === 'film') await film.evaluate(([caps, T]) => { window.CAPMODE = true; window.caption(caps, T); }, [caps, T]);
    await p.screenshot({ path: `${dir}/f${String(n).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93 });
  }
  console.log('frames', from, n1);
  await b.close();
})();

// Check the app on a small phone (360 px, touch): it behaves like an app, not a web page.
//   - no horizontal scroll, on every tab;
//   - the map's labels never overlap (the ones that would are hidden until the user zooms in);
//   - a region opens on top, the phone's back gesture closes it, and so does a swipe from the edge;
//   - the bottom sheet rests at one of its three heights after a drag;
//   - no error in the console.
// Sabotage: VERIF_SABOTAGE=1 widens the cards, enlarges the map labels after they were placed, stops
// screens from adding history entries, breaks the edge swipe and the sheet's handle: each of the six
// controls but the console one must then FAIL.
// Needs a production build (npm run build) and Playwright (npm i -D playwright). No database needed.
import { spawn } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const PORT = 3101, BASE = `http://localhost:${PORT}`;
const SABOTAGE = process.env.VERIF_SABOTAGE === "1";
const resultats = [];

function controle(nom, ok, detail = "") {
  resultats.push({ nom, ok });
  console.log(`${ok ? "OK   " : "ÉCHEC"} ${nom}${detail ? ` : ${detail}` : ""}`);
}

const env = { ...process.env };
delete env.DATABASE_URL;
const serveur = spawn("npx", ["next", "start", "-p", String(PORT)], { env, detached: true, stdio: "ignore" });
for (let i = 0; i < 60; i++) {
  try { if ((await fetch(BASE)).ok) break; } catch { /* not up yet */ }
  await new Promise((r) => setTimeout(r, 500));
}

const navigateur = await chromium.launch();
const page = await (await navigateur.newContext({ viewport: { width: 360, height: 760 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 })).newPage();
if (SABOTAGE) {
  await page.addInitScript(() => {
    history.pushState = () => {};
    // The edge swipe never sees the finger go down.
    window.addEventListener("pointerdown", (e) => { if (e.target.closest?.(".screen.pushed")) e.stopPropagation(); }, true);
  });
}
const erreurs = [];
page.on("pageerror", (e) => erreurs.push(`${e}${process.env.VERIF_DETAIL ? `\n${e.stack}` : ""}`));
// A 503 from /api/ without a database is expected (the app says so on screen); anything else counts.
page.on("console", (m) => { if (m.type() === "error" && !(m.text().startsWith("Failed to load resource") && /\/api\//.test(m.location().url ?? ""))) erreurs.push(m.text()); });

// The shell never scrolls the page (overflow hidden): a too-wide element would be CUT, not scrollable.
// So the check measures how far the visible content goes past the right edge of the screen.
// Sabotage of the page itself (styles are lost on reload: applied again after each one).
const saboter = async () => {
  if (SABOTAGE) await page.addStyleTag({ content: ".card{min-width:420px}.carte-svg text{font-size:90px!important}.sheet{pointer-events:none}" });
};
const debordement = () => page.evaluate(() => {
  const els = [...document.querySelectorAll(".tab:not([hidden]) .card, .tab:not([hidden]) .row, .tab:not([hidden]) .group, .tabbar, .banner, .ftop")];
  const droite = Math.max(document.documentElement.scrollWidth, ...els.map((e) => e.getBoundingClientRect().right));
  return Math.max(0, Math.round(droite - innerWidth));
});
try {
  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.getByText("Où agir en premier").first().waitFor();
  await page.waitForTimeout(800);
  await saboter();
  await page.waitForTimeout(300);

  // Horizontal scroll on every tab. A check that throws would hide the next ones: errors are counted.
  const largeurs = [];
  try {
    for (const onglet of ["Carte", "Régions", "Alertes", "Plus"]) {
      await page.locator(".tabbar button", { hasText: onglet }).click({ timeout: 5000 });
      await page.waitForTimeout(250);
      largeurs.push(`${onglet} ${await debordement()}`);
    }
  } catch (e) { largeurs.push(`erreur : ${e.message.split("\n")[0]}`); }
  controle("Aucun défilement horizontal, sur les quatre onglets", largeurs.length === 4 && largeurs.every((l) => l.endsWith(" 0")), largeurs.join(", "));

  // Map labels: drawn ones do not overlap.
  await page.locator(".tabbar button", { hasText: "Carte" }).click({ timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(300);
  const chevauchements = await page.evaluate(() => {
    const r = [...document.querySelectorAll(".carte-svg text")].map((t) => ({ n: t.textContent, b: t.getBoundingClientRect() }));
    const c = [];
    for (let i = 0; i < r.length; i++) for (let j = i + 1; j < r.length; j++) {
      const a = r[i].b, b = r[j].b;
      if (a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top) c.push(`${r[i].n} / ${r[j].n}`);
    }
    return { n: r.length, c };
  });
  controle("Les noms de la carte ne se chevauchent pas", chevauchements.n >= 8 && chevauchements.c.length === 0,
    `${chevauchements.n} noms affichés${chevauchements.c.length ? `, chevauchements : ${chevauchements.c.join(", ")}` : ""}`);

  // A region on top; the phone's back gesture closes it AND the app stays open.
  let ok = false, detail = "";
  try {
    await page.locator(".tabbar button", { hasText: "Régions" }).click({ timeout: 5000 });
    await page.locator("#t-regions .group .row", { hasText: "Yaadga" }).click({ timeout: 5000 });
    await page.locator("#t-regions .screen.pushed.in h1", { hasText: "Yaadga" }).waitFor({ timeout: 5000 });
    await page.goBack({ timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(600);
    const resteDansApp = page.url().startsWith(BASE) && (await page.locator(".tabbar").count()) === 1;
    const ferme = (await page.locator("#t-regions .screen.pushed").count()) === 0;
    ok = resteDansApp && ferme;
    detail = ok ? "" : resteDansApp ? "l'écran est resté ouvert" : `le retour a quitté l'application (${page.url()})`;
    if (!resteDansApp) { await page.goto(BASE, { waitUntil: "networkidle" }); await page.waitForTimeout(500); await saboter(); }
  } catch (e) { detail = e.message.split("\n")[0]; }
  controle("Une région s'ouvre par-dessus ; le retour du téléphone la ferme", ok, detail);

  // Swipe from the left edge closes the screen.
  ok = false; detail = "";
  try {
    await page.locator(".tabbar button", { hasText: "Régions" }).click({ timeout: 5000 });
    await page.locator("#t-regions .group .row").first().click({ timeout: 5000 });
    await page.locator("#t-regions .screen.pushed.in").waitFor({ timeout: 5000 });
    await page.waitForTimeout(500);
    const cdp = await page.context().newCDPSession(page);
    const point = (x) => [{ x, y: 400, id: 1 }];
    await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: point(6) });
    for (const x of [40, 90, 150, 210, 260]) { await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: point(x) }); await page.waitForTimeout(16); }
    await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await page.waitForTimeout(700);
    const resteDansApp = page.url().startsWith(BASE) && (await page.locator(".tabbar").count()) === 1;
    const ferme = (await page.locator("#t-regions .screen.pushed").count()) === 0;
    ok = resteDansApp && ferme;
    detail = ok ? "" : resteDansApp ? "l'écran est resté ouvert" : `le glissement a quitté l'application (${page.url()})`;
    if (!resteDansApp) { await page.goto(BASE, { waitUntil: "networkidle" }); await page.waitForTimeout(500); await saboter(); }
  } catch (e) { detail = e.message.split("\n")[0]; }
  controle("Un glissement depuis le bord gauche ferme l'écran", ok, detail);

  // The sheet rests at one of its heights after a drag.
  ok = false; detail = "";
  try {
    await page.locator(".tabbar button", { hasText: "Carte" }).click({ timeout: 5000 });
    await page.waitForTimeout(300);
    const tete = await page.locator(".sh-head").boundingBox();
    const cdp = await page.context().newCDPSession(page);
    const y0 = tete.y + 30, pt = (y) => [{ x: 180, y, id: 1 }];
    await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: pt(y0) });
    for (let k = 1; k <= 8; k++) { await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: pt(y0 - k * 30) }); await page.waitForTimeout(30); }
    await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await page.waitForTimeout(600);
    const cran = await page.locator(".sheet").getAttribute("data-cran");
    ok = cran === "mi" || cran === "haut";
    detail = `hauteur de repos : ${cran}`;
  } catch (e) { detail = e.message.split("\n")[0]; }
  controle("La feuille du bas suit le doigt et se pose à une hauteur de repos", ok, detail);

  controle("Aucune erreur dans la console", erreurs.length === 0, erreurs.slice(0, 3).join(" | "));
} finally {
  await navigateur.close();
  try { process.kill(-serveur.pid, "SIGTERM"); } catch { /* stopped */ }
}
const echecs = resultats.filter((r) => !r.ok).length;
console.log(echecs ? `\n${echecs} contrôle(s) en échec sur ${resultats.length}.` : `\nLes ${resultats.length} contrôles passent.`);
process.exit(echecs ? 1 : 0);

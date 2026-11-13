// Check, in a real browser on a phone screen, that the app works with the SERVER STOPPED (cutting
// the browser's network is not enough: the service worker would still reach the server).
//   1. first visit online: the service worker keeps the app, the device database gets the data;
//   2. server stopped: the app opens and says it is offline; a region opens from its address
//      (#region/NORD), the other tabs open, the PDF fiche is served, and a field entry is saved on
//      the device, shown at once, and counted as waiting for the network;
//   3. server restarted: the entry leaves for the database, exactly once (idempotency key).
// Sabotage: VERIF_SABOTAGE=1 blocks the service worker; the check must then FAIL at step 2.
// Needs a production build (npm run build), DATABASE_URL, and Playwright (npm i -D playwright).
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { sql } from "../lib/serveur/db.js";

const require = createRequire(import.meta.url);
const { chromium, devices } = require("playwright");
const PORT = 3100, BASE = `http://localhost:${PORT}`;
const SABOTAGE = process.env.VERIF_SABOTAGE === "1";
const resultats = [];

function controle(nom, ok, detail = "") {
  resultats.push({ nom, ok });
  console.log(`${ok ? "OK   " : "ÉCHEC"} ${nom}${detail ? ` : ${detail}` : ""}`);
}

async function demarrer() {
  const p = spawn("npx", ["next", "start", "-p", String(PORT)], { env: process.env, detached: true, stdio: "ignore" });
  for (let i = 0; i < 60; i++) {
    try { if ((await fetch(BASE)).ok) return p; } catch { /* not up yet */ }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error("le serveur ne démarre pas");
}

async function arreter(p) {
  try { process.kill(-p.pid, "SIGTERM"); } catch { /* already stopped */ }
  for (let i = 0; i < 40; i++) {
    try { await fetch(BASE); } catch { return; }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error("le serveur ne s'arrête pas");
}

const etatBandeau = (page) => page.locator(".banner").getAttribute("data-etat");

const navigateur = await chromium.launch();
const contexte = await navigateur.newContext({ ...devices["iPhone 13"], serviceWorkers: SABOTAGE ? "block" : "allow" });
const page = await contexte.newPage();
let serveur = await demarrer();
let clientId = null;
try {
  // 1. First visit, online.
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  if (!SABOTAGE) {
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.reload({ waitUntil: "networkidle" });
  }
  await page.getByText("Où agir en premier").first().waitFor();
  const jeuLocal = await page.evaluate(() => new Promise((res) => {
    const r = indexedDB.open("tableau-de-bord-decrochage");
    r.onsuccess = () => { const q = r.result.transaction("jeu").objectStore("jeu").get("courant"); q.onsuccess = () => res(q.result?.source ?? null); };
    r.onerror = () => res(null);
  }));
  controle("Première visite : données reçues de la base et enregistrées sur l'appareil", (await etatBandeau(page)) === "a-jour" && jeuLocal === "serveur",
    `bandeau ${await etatBandeau(page)}, source ${jeuLocal}`);

  // 2. Server stopped.
  await arreter(serveur);
  serveur = null;
  let ok = false, detail = "";
  try {
    await page.goto("about:blank");
    await page.goto(BASE + "/#region/NORD", { waitUntil: "load", timeout: 15000 });
    await page.locator('.screen.pushed.in h1', { hasText: "Yaadga" }).waitFor({ timeout: 10000 });
    await page.waitForFunction(() => document.querySelector(".banner")?.dataset.etat === "hors-ligne", null, { timeout: 15000 });
    ok = (await page.locator(".banner").innerText()).startsWith("Hors ligne");
    detail = ok ? "" : "le bandeau ne dit pas « Hors ligne »";
  } catch (e) { detail = e.message.split("\n")[0]; }
  controle("Serveur arrêté : l'application s'ouvre sur une région (#region/NORD) et dit qu'elle est hors ligne", ok, detail);

  ok = false; detail = "";
  try {
    await page.goBack();
    await page.locator(".screen.pushed").waitFor({ state: "detached", timeout: 5000 });
    await page.evaluate(() => { location.hash = "#region/CENTRENORD"; });
    await page.locator('.screen.pushed.in h1', { hasText: "Koulsé" }).waitFor({ timeout: 5000 });
    await page.goBack();
    await page.locator(".screen.pushed").waitFor({ state: "detached", timeout: 5000 });
    for (const [onglet, attendu] of [["Régions", "Matrice de priorité"], ["Alertes", "Calendrier d'alerte"], ["Plus", "Synchronisation"]]) {
      await page.locator(".tabbar button", { hasText: onglet }).click();
      await page.locator(".tab:not([hidden])").getByText(attendu).first().waitFor({ timeout: 5000 });
    }
    ok = true;
  } catch (e) { detail = e.message.split("\n")[0]; }
  controle("Serveur arrêté : retour arrière, lien vers une autre région, puis les onglets Régions, Alertes et Plus s'ouvrent", ok, detail);

  let pdf = 0;
  try { pdf = await page.evaluate(async () => (await fetch("/fiches/NORD.pdf")).status); } catch { /* counted below */ }
  controle("Serveur arrêté : la fiche PDF est servie", pdf === 200, `statut ${pdf}`);

  let saisieOk = false;
  try {
    await page.locator(".tabbar button", { hasText: "Alertes" }).click();
    await page.getByRole("button", { name: "Nouvelle saisie" }).click();
    await page.locator("select.sel").selectOption("NORD");
    await page.locator("#saisie-ecoles").fill("1500");
    await page.getByRole("button", { name: "Enregistrer" }).click();
    await page.locator(".snack.in", { hasText: "enregistré sur ce téléphone" }).waitFor({ timeout: 5000 });
    await page.locator("#t-alertes .row", { hasText: "1 500 écoles" }).first().waitFor({ timeout: 5000 });
    saisieOk = (await page.locator(".banner").innerText()).includes("1 saisie en attente d'envoi");
    clientId = await page.evaluate(() => new Promise((res) => {
      const r = indexedDB.open("tableau-de-bord-decrochage");
      r.onsuccess = () => {
        const q = r.result.transaction("saisies").objectStore("saisies").getAll();
        q.onsuccess = () => res(q.result.find((s) => s.cle === "NORD" && s.ecoles_ouvertes === 1500 && s.statut === "en_attente")?.client_id ?? null);
      };
    }));
  } catch (e) { console.log("   ", e.message.split("\n")[0]); }
  controle("Serveur arrêté : une saisie est enregistrée sur l'appareil, visible, et attend le réseau", saisieOk && Boolean(clientId));

  // 3. Server restarted: the entry leaves, once (after the cancel window).
  serveur = await demarrer();
  if (clientId) {
    await page.reload({ waitUntil: "networkidle" });
    await page.waitForFunction(() => !document.querySelector(".banner")?.innerText.includes("en attente"), null, { timeout: 20000 }).catch(() => {});
    // Send the same entry again, as a device would after a cut in the middle of a send.
    await page.evaluate(async (id) => fetch("/api/saisies", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ saisies: [{ client_id: id, cle: "NORD", annee: "2025-2026", ecoles_ouvertes: 1500, saisi_le: new Date().toISOString() }] }) }), clientId);
    const db = sql();
    const [{ n }] = await db`SELECT count(*)::int AS n FROM saisie_ecoles WHERE client_id = ${clientId}`;
    await db.end();
    controle("Réseau revenu : la saisie est arrivée dans la base, une seule fois", n === 1, `${n} ligne(s)`);
  } else controle("Réseau revenu : la saisie est arrivée dans la base, une seule fois", false, "pas de saisie à envoyer");
} finally {
  if (serveur) await arreter(serveur);
  await navigateur.close();
}
const echecs = resultats.filter((r) => !r.ok).length;
console.log(echecs ? `\n${echecs} contrôle(s) en échec sur ${resultats.length}.` : `\nLes ${resultats.length} contrôles passent.`);
process.exit(echecs ? 1 : 0);

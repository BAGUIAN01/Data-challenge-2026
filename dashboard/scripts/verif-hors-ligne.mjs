// Check, in a real browser, that the dashboard works with the SERVER STOPPED (cutting the browser's
// network is not enough: the service worker would still reach the server).
//   1. first visit online: the service worker keeps the pages, the device database gets the data;
//   2. server stopped: every page opens (including ones never visited), says it is offline, the PDF
//      fiche downloads, and a field entry is saved on the device and shown at once;
//   3. server restarted: the entry leaves for the database, exactly once (idempotency key).
// Sabotage: VERIF_SABOTAGE=1 blocks the service worker; the check must then FAIL at step 2.
// Needs a production build (npm run build), DATABASE_URL, and Playwright (npm i -D playwright).
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { sql } from "../lib/serveur/db.js";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
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

const navigateur = await chromium.launch();
const contexte = await navigateur.newContext({ serviceWorkers: SABOTAGE ? "block" : "allow" });
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
  await page.getByText("Données").first().waitFor();
  controle("Première visite : données reçues et enregistrées sur l'appareil",
    (await page.locator(".bandeau").innerText()).includes("enregistrées sur cet appareil"));

  // 2. Server stopped.
  await arreter(serveur);
  serveur = null;
  for (const [url, attendu] of [["/region/NORD", "Yaadga"], ["/priorites", "Matrice de priorité"], ["/alertes", "Calendrier d'alerte"],
    ["/methode", "Méthode et limites"], ["/", "Où agir en premier"]]) {
    let ok = false, detail = "";
    try {
      await page.goto(BASE + url, { waitUntil: "load", timeout: 15000 });
      await page.locator("h1", { hasText: attendu }).waitFor({ timeout: 10000 });
      ok = (await page.locator(".bandeau").innerText()).startsWith("Sans réseau");
      detail = ok ? "" : "le bandeau ne dit pas « Sans réseau »";
    } catch (e) { detail = e.message.split("\n")[0]; }
    controle(`Serveur arrêté : ${url} s'ouvre et le dit`, ok, detail);
  }
  let pdf = 0;
  try { pdf = await page.evaluate(async () => (await fetch("/fiches/NORD.pdf")).status); } catch { /* counted below */ }
  controle("Serveur arrêté : la fiche PDF se télécharge", pdf === 200, `statut ${pdf}`);

  let saisieOk = false;
  try {
    await page.goto(BASE + "/alertes", { waitUntil: "load", timeout: 15000 });
    await page.locator("select").first().selectOption("NORD");
    await page.locator('input[type="number"]').fill("1500");
    await page.getByRole("button", { name: "Enregistrer" }).click();
    await page.getByText("enregistrée sur cet appareil").waitFor({ timeout: 5000 });
    saisieOk = (await page.locator(".bandeau").innerText()).includes("attend le réseau");
    clientId = await page.evaluate(() => new Promise((res) => {
      const r = indexedDB.open("tableau-de-bord-decrochage");
      r.onsuccess = () => {
        const q = r.result.transaction("saisies").objectStore("saisies").getAll();
        q.onsuccess = () => res(q.result.find((s) => s.cle === "NORD" && s.ecoles_ouvertes === 1500)?.client_id ?? null);
      };
    }));
  } catch (e) { console.log("   ", e.message.split("\n")[0]); }
  controle("Serveur arrêté : une saisie est enregistrée sur l'appareil, visible, et attend le réseau", saisieOk && Boolean(clientId));

  // 3. Server restarted: the entry leaves, once.
  serveur = await demarrer();
  if (clientId) {
    await page.reload({ waitUntil: "networkidle" });
    await page.waitForFunction(() => !document.querySelector(".bandeau")?.innerText.includes("attend le réseau"), null, { timeout: 15000 }).catch(() => {});
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

// Check: the shape guard accepts the published data set and refuses every broken body that once
// crashed the app (truncated, foreign, missing threshold, region without series).
import { readFileSync } from "node:fs";
import { jeuValide } from "../lib/valider-jeu.js";

const bon = JSON.parse(readFileSync(new URL("../public/data/tableau_de_bord.json", import.meta.url), "utf8"));
const copie = () => structuredClone(bon);
const cas = [
  ["jeu publié", bon, true],
  ["corps vide", {}, false],
  ["null", null, false],
  ["corps étranger", { pas: "le bon format" }, false],
  ["JSON tronqué (régions vides)", { jeu: { regions: [] } }, false],
  ["sans version", (() => { const j = copie(); delete j.version; return j; })(), false],
  ["sans seuil national", (() => { const j = copie(); delete j.seuils.tap_national; return j; })(), false],
  ["sans carte", (() => { const j = copie(); delete j.carte; return j; })(), false],
  ["région sans série tap", (() => { const j = copie(); delete j.regions[3].tap; return j; })(), false],
  ["région sans probabilités", (() => { const j = copie(); j.regions[0].probabilites = null; return j; })(), false],
];
let echecs = 0;
for (const [nom, jeu, attendu] of cas) {
  const ok = jeuValide(jeu) === attendu;
  if (!ok) echecs++;
  console.log(`${ok ? "ok   " : "ÉCHEC"} ${nom} : ${attendu ? "accepté" : "refusé"} attendu`);
}
if (echecs) { console.error(`ÉCHEC : ${echecs} cas.`); process.exit(1); }
console.log("OK : le garde accepte le jeu publié et refuse les corps cassés.");

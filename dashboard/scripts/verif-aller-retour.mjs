// Check: the active version read back from the database (as the API serves it) is exactly the
// exported file. Any lost, added or changed value is listed and the check fails.
import { readFileSync } from "node:fs";
import { sql } from "../lib/serveur/db.js";
import { lireJeuActif } from "../lib/serveur/jeu-donnees.js";

function aplatir(o, prefixe = "", sortie = {}) {
  if (o !== null && typeof o === "object") {
    for (const [k, v] of Object.entries(o)) aplatir(v, prefixe ? `${prefixe}.${k}` : k, sortie);
    if (Object.keys(o).length === 0) sortie[prefixe] = Array.isArray(o) ? "[]" : "{}";
  } else sortie[prefixe] = o;
  return sortie;
}

const fichier = JSON.parse(readFileSync(new URL("../public/data/tableau_de_bord.json", import.meta.url), "utf8"));
const db = sql();
const base = await lireJeuActif(db);
await db.end();
if (!base) {
  console.error("ÉCHEC : aucune version active dans la base.");
  process.exit(1);
}
const a = aplatir(fichier), b = aplatir(base);
const cles = new Set([...Object.keys(a), ...Object.keys(b)]);
const ecarts = [...cles].filter((k) => a[k] !== b[k]);
console.log(`${cles.size} valeurs comparées entre le fichier exporté et la base (version ${base.version}).`);
if (ecarts.length) {
  for (const k of ecarts.slice(0, 20)) console.error(`  écart ${k} : fichier=${JSON.stringify(a[k])} base=${JSON.stringify(b[k])}`);
  console.error(`ÉCHEC : ${ecarts.length} écart(s).`);
  process.exit(1);
}
console.log("OK : la base rend exactement le fichier exporté.");

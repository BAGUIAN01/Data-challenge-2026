// Load the exported data set (public/data/tableau_de_bord.json) into the database and make it the
// active version. Runs in one transaction: the dashboard never sees a half-loaded version.
// Field entries (saisie_ecoles) are not touched.
import { readFileSync } from "node:fs";
import { sql } from "../lib/serveur/db.js";
import { versLignes } from "../lib/serveur/jeu-donnees.js";

const jeu = JSON.parse(readFileSync(new URL("../public/data/tableau_de_bord.json", import.meta.url), "utf8"));
const l = versLignes(jeu);
const db = sql();
await db.begin(async (tx) => {
  await tx`DELETE FROM jeu_donnees WHERE version = ${l.jeu.version}`; // cascades to the region tables
  await tx`INSERT INTO jeu_donnees (version, genere_le, parametres) VALUES (${l.jeu.version}, ${l.jeu.genere_le}, ${tx.json(l.jeu.parametres)})`;
  await tx`INSERT INTO region ${tx(l.region.map((r) => ({ ...r, prevision_2025_26: tx.json(r.prevision_2025_26) })))}`;
  for (const table of ["indicateur", "alerte", "facteur", "texte"]) {
    for (let i = 0; i < l[table].length; i += 500) await tx`INSERT INTO ${tx(table)} ${tx(l[table].slice(i, i + 500))}`;
  }
  await tx`UPDATE jeu_donnees SET actif = false WHERE actif AND version <> ${l.jeu.version}`;
  await tx`UPDATE jeu_donnees SET actif = true WHERE version = ${l.jeu.version}`;
});
const [n] = await db`SELECT (SELECT count(*) FROM region WHERE version = ${l.jeu.version}) AS regions,
  (SELECT count(*) FROM indicateur WHERE version = ${l.jeu.version}) AS indicateurs`;
console.log(`Version ${l.jeu.version} chargée et active : ${n.regions} régions, ${n.indicateurs} valeurs.`);
await db.end();

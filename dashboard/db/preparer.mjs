// Run before the build on the host (Vercel: "vercel-build"). With a database declared (DATABASE_URL or
// POSTGRES_URL, set by the Neon integration), apply the schema and load the exported data set, so that
// every deployment puts the data in the database without any manual step. Field entries are kept.
// A failure stops the build: a deployment whose database could not be filled must not go live
// silently (the previous deployment stays in place, and the build log says why).
import { spawnSync } from "node:child_process";
import { NOMS_VARIABLE, nomVariableBase } from "../lib/serveur/db.js";

const nom = nomVariableBase();
if (!nom) {
  console.log(`Base en ligne non configurée (aucune des variables ${NOMS_VARIABLE.join(", ")}) : `
    + "l'application utilisera les données publiées avec elle, et les saisies resteront sur les appareils.");
} else {
  console.log(`Base en ligne : ${nom}. Schéma, puis chargement des données.`);
  for (const script of ["db/appliquer-schema.mjs", "db/seed.mjs"]) {
    const r = spawnSync(process.execPath, [script], { stdio: "inherit", env: process.env });
    if (r.status !== 0) {
      console.error(`Échec de ${script} : la base n'a pas pu être remplie. Vérifiez la variable ${nom} dans les réglages du projet.`);
      process.exit(r.status ?? 1);
    }
  }
}

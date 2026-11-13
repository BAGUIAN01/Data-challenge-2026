// Run before the build on the host (Vercel: "vercel-build"). With a database (DATABASE_URL, e.g. set
// by the Neon integration), apply the schema and load the exported data set, so that a deployment
// is ready without any manual step. Without a database, nothing to do: the app uses the data set
// shipped with it and keeps field entries on the device.
import { spawnSync } from "node:child_process";

if (!process.env.DATABASE_URL) {
  console.log("Pas de DATABASE_URL : base en ligne non configurée, l'application utilisera les données publiées avec elle.");
} else {
  for (const script of ["db/appliquer-schema.mjs", "db/seed.mjs"]) {
    const r = spawnSync(process.execPath, [script], { stdio: "inherit", env: process.env });
    if (r.status !== 0) process.exit(r.status ?? 1);
  }
}

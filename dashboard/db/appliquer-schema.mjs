// Apply db/schema.sql to the database (DATABASE_URL or POSTGRES_URL, see lib/serveur/db.js). Idempotent.
import { readFileSync } from "node:fs";
import { sql } from "../lib/serveur/db.js";

const db = sql();
await db.unsafe(readFileSync(new URL("./schema.sql", import.meta.url), "utf8"));
console.log("Schéma appliqué.");
await db.end();

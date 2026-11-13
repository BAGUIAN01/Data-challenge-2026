// Apply db/schema.sql to the database named by DATABASE_URL (idempotent).
import { readFileSync } from "node:fs";
import { sql } from "../lib/serveur/db.js";

const db = sql();
await db.unsafe(readFileSync(new URL("./schema.sql", import.meta.url), "utf8"));
console.log("Schéma appliqué.");
await db.end();

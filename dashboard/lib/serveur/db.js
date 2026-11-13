// Server-side PostgreSQL client (Neon in production). One pooled client per process.
import postgres from "postgres";

// Names under which the host may declare the database. Our own .env uses DATABASE_URL; Vercel's Neon
// integration sets DATABASE_URL and POSTGRES_URL (pooled) and their unpooled twins. First one set wins.
export const NOMS_VARIABLE = ["DATABASE_URL", "POSTGRES_URL", "DATABASE_URL_UNPOOLED", "POSTGRES_URL_NON_POOLING"];

export function nomVariableBase() {
  return NOMS_VARIABLE.find((n) => process.env[n]) ?? null;
}

export function baseConfiguree() {
  return nomVariableBase() !== null;
}

// postgres.js sends every URL parameter it does not know to the server as a setting. Neon's
// connection strings carry channel_binding=require, which the server then refuses ("unrecognized
// configuration parameter"): the parameter is removed, TLS stays required below.
export function urlNettoyee(url) {
  try {
    const u = new URL(url);
    u.searchParams.delete("channel_binding");
    return u.toString();
  } catch {
    return url;
  }
}

let client = null;

export function sql() {
  if (!client) {
    const nom = nomVariableBase();
    if (!nom) throw new Error(`Base non configurée : aucune des variables ${NOMS_VARIABLE.join(", ")}`);
    const url = urlNettoyee(process.env[nom]);
    // Neon requires TLS; a local database (tests) usually does not.
    const local = /@(localhost|127\.0\.0\.1)[:/]/.test(url) || url.includes("host=/");
    // Notices ("already exists, skipping" when the idempotent schema runs again) are not errors.
    client = postgres(url, { ssl: local ? false : "require", max: 5, idle_timeout: 20, prepare: false, onnotice: () => {} });
  }
  return client;
}

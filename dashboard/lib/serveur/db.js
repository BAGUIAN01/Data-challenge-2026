// Server-side PostgreSQL client (Neon in production). One pooled client per process.
import postgres from "postgres";

let client = null;

export function baseConfiguree() {
  return Boolean(process.env.DATABASE_URL);
}

export function sql() {
  if (!client) {
    const url = process.env.DATABASE_URL;
    if (!url) throw new Error("DATABASE_URL absent");
    // Neon requires TLS; a local database (tests) usually does not.
    const local = /@(localhost|127\.0\.0\.1)[:/]/.test(url) || url.includes("host=/");
    // Notices ("already exists, skipping" when the idempotent schema runs again) are not errors.
    client = postgres(url, { ssl: local ? false : "require", max: 5, idle_timeout: 20, prepare: false, onnotice: () => {} });
  }
  return client;
}

// Field entries: number of schools open at the start of the school year, per region.
// POST receives a batch from a device's outbox; client_id is the idempotency key, so a batch sent
// twice (network cut after the server wrote it) is stored once. GET returns the latest entry per
// region and year, so that every device sees the entries made on the others.
import { baseConfiguree, sql } from "@/lib/serveur/db";

export const dynamic = "force-dynamic";

const ENTETES = { "Cache-Control": "no-store" };
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const ANNEE = /^20\d\d-20\d\d$/;

function indisponible() {
  return Response.json({ erreur: "base_non_configuree", message: "La base en ligne n'est pas configurée : les saisies restent sur l'appareil." },
    { status: 503, headers: ENTETES });
}

export async function GET() {
  if (!baseConfiguree()) return indisponible();
  try {
    const lignes = await sql()`
      SELECT DISTINCT ON (cle, annee) client_id, cle, annee, ecoles_ouvertes, saisi_le
      FROM saisie_ecoles ORDER BY cle, annee, saisi_le DESC`;
    return Response.json({ saisies: lignes }, { headers: ENTETES });
  } catch (e) {
    console.error("lecture des saisies", e);
    return Response.json({ erreur: "base_injoignable", message: "La base en ligne ne répond pas." }, { status: 503, headers: ENTETES });
  }
}

export async function POST(req) {
  if (!baseConfiguree()) return indisponible();
  let corps;
  try {
    corps = await req.json();
  } catch {
    return Response.json({ erreur: "corps_invalide", message: "Requête illisible." }, { status: 400, headers: ENTETES });
  }
  const saisies = Array.isArray(corps?.saisies) ? corps.saisies.slice(0, 200) : [];
  try {
    const db = sql();
    const [actif] = await db`SELECT version FROM jeu_donnees WHERE actif`;
    const connues = new Set(actif ? (await db`SELECT cle FROM region WHERE version = ${actif.version}`).map((r) => r.cle) : []);
    const valides = [], rejetees = [];
    for (const s of saisies) {
      const n = Number(s?.ecoles_ouvertes);
      const date = new Date(s?.saisi_le);
      if (UUID.test(s?.client_id ?? "") && connues.has(s?.cle) && ANNEE.test(s?.annee ?? "")
        && Number.isInteger(n) && n >= 0 && n <= 100000 && !Number.isNaN(date.getTime())) {
        valides.push({ client_id: s.client_id, cle: s.cle, annee: s.annee, ecoles_ouvertes: n, saisi_le: date });
      } else rejetees.push(s?.client_id ?? null);
    }
    if (valides.length) {
      await db`INSERT INTO saisie_ecoles ${db(valides)} ON CONFLICT (client_id) DO NOTHING`;
    }
    // Already-stored entries count as received: the device can mark them as sent.
    return Response.json({ recues: valides.map((s) => s.client_id), rejetees }, { headers: ENTETES });
  } catch (e) {
    console.error("enregistrement des saisies", e);
    return Response.json({ erreur: "base_injoignable", message: "La base en ligne ne répond pas : les saisies restent sur l'appareil." },
      { status: 503, headers: ENTETES });
  }
}

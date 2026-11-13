// GET /api/donnees: the active data set, read from the database (Neon in production).
// Without a database the dashboard still works: the client falls back to the data on the device,
// then to the snapshot shipped with the app. The 503 body says why, in French, for the banner.
import { baseConfiguree, sql } from "@/lib/serveur/db";
import { lireJeuActif } from "@/lib/serveur/jeu-donnees";

export const dynamic = "force-dynamic";

const ENTETES = { "Cache-Control": "no-store" };

export async function GET() {
  if (!baseConfiguree()) {
    return Response.json({ erreur: "base_non_configuree", message: "La base en ligne n'est pas configurée sur ce serveur." },
      { status: 503, headers: ENTETES });
  }
  try {
    const jeu = await lireJeuActif(sql());
    if (!jeu) {
      return Response.json({ erreur: "aucune_version", message: "Aucune version des données n'est encore publiée dans la base." },
        { status: 503, headers: ENTETES });
    }
    return Response.json(jeu, { headers: ENTETES });
  } catch (e) {
    console.error("lecture des données", e);
    return Response.json({ erreur: "base_injoignable", message: "La base en ligne ne répond pas." }, { status: 503, headers: ENTETES });
  }
}

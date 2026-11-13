// Turn the exported JSON into table rows (seed) and the tables back into the same JSON (API).
// The two directions live side by side so they cannot drift apart; scripts/verif-aller-retour.mjs
// checks that tables -> JSON gives back exactly the exported file.

const SERIES = ["tap", "tap_f", "tap_g", "eleves", "ecoles", "incidents"];
const TEXTES = { fait: "faits", levier: "leviers", levier_facteur: "leviers_facteurs" };

export function versLignes(jeu) {
  const { version, genere_le, regions, ...parametres } = jeu;
  const lignes = { jeu: { version, genere_le, parametres }, region: [], indicateur: [], alerte: [], facteur: [], texte: [] };
  for (const r of regions) {
    lignes.region.push({
      version, cle: r.cle, nom: r.nom, ancienne: r.ancienne, codes: r.codes, type: r.type, profil: r.profil,
      priorite: r.priorite, enfants_hors_cm2: r.enfants_hors_cm2, prevision_2025_26: r.prevision_2025_26,
    });
    for (const s of SERIES) {
      const annees = s === "incidents" ? parametres.annees_violence : parametres.annees;
      r[s].forEach((valeur, rang) => lignes.indicateur.push({ version, cle: r.cle, indicateur: s, annee: annees[rang], rang, valeur }));
    }
    for (const [periode, probabilite] of Object.entries(r.probabilites)) {
      lignes.alerte.push({ version, cle: r.cle, periode, probabilite });
    }
    for (const [facteur, f] of Object.entries(r.facteurs)) {
      lignes.facteur.push({ version, cle: r.cle, facteur, valeur: f.valeur, niveau: f.niveau });
    }
    for (const [genre, champ] of Object.entries(TEXTES)) {
      r[champ].forEach((contenu, rang) => lignes.texte.push({ version, cle: r.cle, genre, rang, contenu }));
    }
  }
  return lignes;
}

export function depuisLignes({ jeu, region, indicateur, alerte, facteur, texte }) {
  const parCle = new Map(region.map((r) => [r.cle, {
    cle: r.cle, nom: r.nom, ancienne: r.ancienne, codes: r.codes, type: r.type, profil: r.profil,
    priorite: Number(r.priorite), enfants_hors_cm2: Number(r.enfants_hors_cm2), prevision_2025_26: r.prevision_2025_26,
    ...Object.fromEntries(SERIES.map((s) => [s, []])),
    probabilites: {}, facteurs: {}, faits: [], leviers: [], leviers_facteurs: [],
  }]));
  for (const i of indicateur) parCle.get(i.cle)[i.indicateur][Number(i.rang)] = i.valeur === null ? null : Number(i.valeur);
  for (const a of alerte) parCle.get(a.cle).probabilites[a.periode] = Number(a.probabilite);
  for (const f of facteur) {
    parCle.get(f.cle).facteurs[f.facteur] = { valeur: f.valeur === null ? null : Number(f.valeur), niveau: Number(f.niveau) };
  }
  for (const t of [...texte].sort((a, b) => a.rang - b.rang)) parCle.get(t.cle)[TEXTES[t.genre]].push(t.contenu);
  const genere = jeu.genere_le instanceof Date ? jeu.genere_le.toISOString().slice(0, 10) : String(jeu.genere_le).slice(0, 10);
  return { ...jeu.parametres, version: jeu.version, genere_le: genere, regions: [...parCle.values()].sort((a, b) => a.cle.localeCompare(b.cle)) };
}

export async function lireJeuActif(sql) {
  const [jeu] = await sql`SELECT version, genere_le, parametres FROM jeu_donnees WHERE actif`;
  if (!jeu) return null;
  const v = jeu.version;
  const [region, indicateur, alerte, facteur, texte] = await Promise.all([
    sql`SELECT * FROM region WHERE version = ${v}`,
    sql`SELECT cle, indicateur, rang, valeur FROM indicateur WHERE version = ${v}`,
    sql`SELECT cle, periode, probabilite FROM alerte WHERE version = ${v}`,
    sql`SELECT cle, facteur, valeur, niveau FROM facteur WHERE version = ${v}`,
    sql`SELECT cle, genre, rang, contenu FROM texte WHERE version = ${v}`,
  ]);
  return depuisLignes({ jeu, region, indicateur, alerte, facteur, texte });
}

// Pupils expected from the number of schools open at the start of the year (decision D13).
// Relation learned on 2016/17-2024/25: change in log pupils = constante + pente x change in log schools.
// Tested on years the model never saw: mean error 4.2 % against 8.6 % for "same as last year".
// The test covers ONE year ahead of the last statistical yearbook (2024/25); further ahead the
// estimate is given without a measured range, and the screen says so.

export const DERNIERE_ANNEE = "2024-2025";

// School years a field entry can be made for.
export const ANNEES_SAISIE = ["2025-2026", "2026-2027"];

export function anneesDepuisAnnuaire(annee) {
  return Number(annee.slice(0, 4)) - Number(DERNIERE_ANNEE.slice(0, 4));
}

export function estimerEffectifs({ region, nowcast, annee, ecolesOuvertes }) {
  const n = anneesDepuisAnnuaire(annee);
  const ecolesRef = region.ecoles.at(-1);
  const elevesRef = region.eleves.at(-1);
  if (!(ecolesOuvertes > 0) || !(ecolesRef > 0) || n < 1) return null;
  const dlog = n * nowcast.constante + nowcast.pente * Math.log(ecolesOuvertes / ecolesRef);
  const centrale = elevesRef * Math.exp(dlog);
  const mesuree = n === 1;
  const marge = nowcast.erreur_pct / 100;
  return {
    centrale: Math.round(centrale),
    basse: mesuree ? Math.round(centrale * (1 - marge)) : null,
    haute: mesuree ? Math.round(centrale * (1 + marge)) : null,
    variationPct: (Math.exp(dlog) - 1) * 100,
    mesuree,
    ecolesRef,
    elevesRef,
  };
}

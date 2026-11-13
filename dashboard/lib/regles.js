// Rules shared by every screen, written once: risk tier, priorities, map layers, region order.
// The risk shown everywhere is the reference model (it sets the priorities, decision D12); the
// September alert comes second, as an update.

export const risque = (r) => r.probabilites.ref_2026_27;
export const alerteSeptembre = (r) => r.probabilites.sept_2026_27;

export function niveau(p, seuils) {
  return p >= seuils.risque_eleve ? "élevé" : p >= seuils.risque_moyen ? "moyen" : "faible";
}

export const PRIORITES = {
  1: { libelle: "Priorité 1", sous: "agir maintenant" },
  2: { libelle: "Priorité 2", sous: "veille renforcée" },
  3: { libelle: "Priorité 3", sous: "consolider" },
};

// Exposure tier of a factor: 1 = among the 4 most exposed regions, 3 = among the 4 least exposed.
export const EXPOSITION = { 1: "forte", 2: "moyenne", 3: "faible" };

// Global score (scripts/score_global.py): 100 x (0.5 x risk + 0.5 x share of children who do not
// complete primary). Computed once in the analysis, read here from the data set.
export const scoreGlobal = (jeu, r) => jeu?.score_global?.par_region?.[r.cle] ?? null;
export const niveauScore = (s) => (s >= 50 ? "élevé" : s >= 25 ? "moyen" : "faible");
export const ZONES_SCORE = [[0, 25, "faible", "var(--z1)"], [25, 50, "moyen", "var(--z2)"], [50, 100, "élevé", "var(--z3)"]];

// Most urgent first: priority, then the global score (when the data set has it), then the lowest completion.
export function trierRegions(regions, jeu) {
  const s = (r) => scoreGlobal(jeu, r) ?? 0;
  return [...regions].sort((a, b) => a.priorite - b.priorite || s(b) - s(a) || a.tap.at(-1) - b.tap.at(-1));
}

// Map layers share one ordinal blue ramp: class 1 (darkest in light mode) is the most worrying.
export function couches(jeu) {
  const seuils = jeu.seuils;
  const nat = seuils.tap_national.toLocaleString("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const score = jeu.score_global
    ? { score: { nom: "Score", valeur: (r) => `${scoreGlobal(jeu, r)} %`, classe: (r) => { const s = scoreGlobal(jeu, r) ?? 0; return s >= 50 ? 1 : s >= 25 ? 2 : 3; }, legende: ["Score de 50 et plus", "25 à 49", "Moins de 25"] } }
    : {};
  return {
    ...score,
    risque: {
      nom: "Risque",
      valeur: (r) => `${risque(r)} %`,
      classe: (r) => (risque(r) >= seuils.risque_eleve ? 1 : risque(r) >= seuils.risque_moyen ? 2 : 3),
      legende: ["Risque élevé", "Moyen", "Faible"],
    },
    priorite: { nom: "Priorité", valeur: (r) => `P${r.priorite}`, classe: (r) => r.priorite, legende: ["Priorité 1, agir maintenant", "Priorité 2", "Priorité 3"] },
    achevement: {
      nom: "Achèvement",
      valeur: (r) => `${Math.round(r.tap.at(-1))} %`,
      classe: (r) => (r.tap.at(-1) < 35 ? 1 : r.tap.at(-1) < seuils.tap_national ? 2 : 3),
      legende: ["Achèvement sous 35 %", `35 à ${nat} %`, `${nat} % et plus`],
    },
  };
}

// Pupil estimates carry a +/- 4.2 % error: units would be false precision.
export const centaine = (v) => (v === null || v === undefined ? v : Math.round(v / 100) * 100);

export const signe = (v) => (v > 0 ? "+" : v < 0 ? "−" : "");

// Dominant background factor of a region, what to act on (scripts/facteur_dominant.py): read from the
// data set. null when the data set does not carry it; dominant is null when no factor stands out.
export function facteurDominant(jeu, r) {
  const f = jeu?.facteur_dominant?.par_region?.[r.cle];
  if (!f) return null;
  const def = (id) => jeu.facteurs_def.find((d) => d.id === id) ?? null;
  return { ...f, def: f.dominant ? def(f.dominant) : null, defSecond: f.second ? def(f.second) : null };
}

// Plain name of a factor for "agir sur …".
export const NOM_ACTION = { violence: "l'insécurité", deplaces: "l'accueil des déplacés", pauvrete: "la pauvreté", faim: "la faim",
  meres: "l'instruction des mères", grossesses: "les grossesses précoces", prescolaire: "le préscolaire" };


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

// Most urgent first: priority, then the lowest completion rate.
export function trierRegions(regions) {
  return [...regions].sort((a, b) => a.priorite - b.priorite || a.tap.at(-1) - b.tap.at(-1));
}

// Map layers share one ordinal blue ramp: class 1 (darkest in light mode) is the most worrying.
export function couches(seuils) {
  const nat = seuils.tap_national.toLocaleString("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  return {
    priorite: { nom: "Priorité", classe: (r) => r.priorite, legende: ["Priorité 1, agir maintenant", "Priorité 2", "Priorité 3"] },
    risque: {
      nom: "Risque",
      classe: (r) => (risque(r) >= seuils.risque_eleve ? 1 : risque(r) >= seuils.risque_moyen ? 2 : 3),
      legende: ["Risque élevé", "Moyen", "Faible"],
    },
    achevement: {
      nom: "Achèvement",
      classe: (r) => (r.tap.at(-1) < 35 ? 1 : r.tap.at(-1) < seuils.tap_national ? 2 : 3),
      legende: ["Achèvement sous 35 %", `35 à ${nat} %`, `${nat} % et plus`],
    },
  };
}

// Pupil estimates carry a +/- 4.2 % error: units would be false precision.
export const centaine = (v) => (v === null || v === undefined ? v : Math.round(v / 100) * 100);

export const signe = (v) => (v > 0 ? "+" : v < 0 ? "−" : "");

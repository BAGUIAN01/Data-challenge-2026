// French number and date formatting, shared by every screen.
const cache = new Map();

function nf(nd) {
  if (!cache.has(nd)) cache.set(nd, new Intl.NumberFormat("fr-FR", { minimumFractionDigits: nd, maximumFractionDigits: nd }));
  return cache.get(nd);
}

export function fr(v, nd = 0) {
  return v === null || v === undefined || Number.isNaN(v) ? "—" : nf(nd).format(v);
}

export function pct(v, nd = 0) {
  return v === null || v === undefined ? "—" : `${fr(v, nd)} %`;
}

export function dateFr(v) {
  if (!v) return "—";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v) : d.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

export function dateHeureFr(v) {
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString("fr-FR", { day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" });
}

// Risk tiers of the probability of a drop in pupils (decision D12): label, icon, CSS class.
export function niveauRisque(p, seuils) {
  if (p >= seuils.risque_eleve) return { libelle: "Élevé", icone: "⚠", classe: "risque-eleve" };
  if (p >= seuils.risque_moyen) return { libelle: "Moyen", icone: "!", classe: "risque-moyen" };
  return { libelle: "Faible", icone: "✓", classe: "risque-faible" };
}

export const PRIORITES = {
  1: { libelle: "Priorité 1", sous: "agir maintenant" },
  2: { libelle: "Priorité 2", sous: "veille renforcée" },
  3: { libelle: "Priorité 3", sous: "consolider" },
};

export const NIVEAUX_FACTEUR = { 1: "Forte", 2: "Moyenne", 3: "Faible" };

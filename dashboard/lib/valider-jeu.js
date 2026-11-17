// Shape check of a data set, shared by the client (server body, device copy, snapshot) and the API.
// A data set that fails it is never saved on the device nor shown: the screens read these fields
// without guards, so a truncated or foreign body would crash the whole app.
const SERIES = ["tap", "tap_f", "tap_g", "eleves", "ecoles", "incidents"];

const estObjet = (x) => x !== null && typeof x === "object" && !Array.isArray(x);

export function jeuValide(j) {
  if (!estObjet(j) || !j.version) return false;
  if (!Array.isArray(j.annees) || !j.annees.length || !Array.isArray(j.annees_violence)) return false;
  if (!estObjet(j.seuils) || typeof j.seuils.tap_national !== "number") return false;
  if (!estObjet(j.national) || !estObjet(j.carte) || !j.carte.regions) return false;
  if (!Array.isArray(j.regions) || j.regions.length < 1) return false;
  return j.regions.every((r) => estObjet(r) && typeof r.cle === "string" && typeof r.nom === "string"
    && SERIES.every((s) => Array.isArray(r[s]))
    && estObjet(r.probabilites) && estObjet(r.facteurs)
    && Array.isArray(r.faits) && Array.isArray(r.leviers));
}

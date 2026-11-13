"use client";
// Field entry: schools open at the start of the year -> expected pupils (computed on the device).
// The entry is saved on the device at once, shown at once, and sent when the network answers.
import { useState } from "react";
import { derniereSaisie, useDonnees } from "./DonneesProvider";
import { dateHeureFr, fr, pct } from "@/lib/format";
import { anneesDepuisAnnuaire, estimerEffectifs } from "@/lib/prevision-effectifs";

export const ANNEES_SAISIE = ["2025-2026", "2026-2027"];

export function Estimation({ jeu, region, annee, ecoles }) {
  const e = estimerEffectifs({ region, nowcast: jeu.nowcast, annee, ecolesOuvertes: ecoles });
  if (!e) return null;
  return (
    <div className="resultat">
      <div className="resultat-valeur">≈ {fr(e.centrale)} élèves en {annee.replace("-", "/")}</div>
      <div>
        {e.variationPct >= 0 ? "+" : "−"}{fr(Math.abs(e.variationPct), 1)} % par rapport à 2024/25 ({fr(e.elevesRef)} élèves,
        {" "}{fr(e.ecolesRef)} écoles).
      </div>
      {e.mesuree ? (
        <div className="discret">
          Erreur moyenne mesurée sur les années passées : ± {fr(jeu.nowcast.erreur_pct, 1)} %, soit de {fr(e.basse)} à {fr(e.haute)} élèves
          (contre ± {fr(jeu.nowcast.erreur_persistance_pct, 1)} % en reprenant les effectifs de l'année d'avant).
        </div>
      ) : (
        <div className="discret">
          Estimation à {anneesDepuisAnnuaire(annee)} ans de l'annuaire 2024/25 : la méthode n'a été vérifiée qu'à un an. Fourchette non mesurée,
          à prendre comme un ordre de grandeur.
        </div>
      )}
    </div>
  );
}

export default function SaisieEcoles({ jeu, region, compact = false }) {
  const { saisies, ajouterSaisie, serveur } = useDonnees();
  const [annee, setAnnee] = useState(ANNEES_SAISIE[0]);
  const [valeur, setValeur] = useState("");
  const [message, setMessage] = useState(null);
  const derniere = derniereSaisie(saisies, region.cle, annee);
  const nombre = Number(valeur);
  const valide = valeur !== "" && Number.isInteger(nombre) && nombre > 0 && nombre < 100000;

  async function enregistrer(e) {
    e.preventDefault();
    if (!valide) return;
    const s = await ajouterSaisie({ cle: region.cle, annee, ecoles_ouvertes: nombre });
    setValeur("");
    setMessage(`Saisie de ${fr(s.ecoles_ouvertes)} écoles enregistrée sur cet appareil.`);
  }

  return (
    <div>
      {!compact && <h3>Écoles ouvertes à la rentrée : estimer les effectifs</h3>}
      <form className="saisie" onSubmit={enregistrer}>
        <label className="champ">
          Année scolaire
          <select value={annee} onChange={(e) => setAnnee(e.target.value)}>
            {ANNEES_SAISIE.map((a) => <option key={a} value={a}>{a.replace("-", "/")}</option>)}
          </select>
        </label>
        <label className="champ">
          Écoles ouvertes ({region.nom})
          <input type="number" inputMode="numeric" min="1" step="1" value={valeur} placeholder={fr(region.ecoles.at(-1))}
            onChange={(e) => { setValeur(e.target.value); setMessage(null); }} />
        </label>
        <button type="submit" disabled={!valide}>Enregistrer</button>
      </form>
      {valide && <Estimation jeu={jeu} region={region} annee={annee} ecoles={nombre} />}
      {message && <p className="statut-saisie" role="status">{message}</p>}
      {!valide && derniere && (
        <>
          <Estimation jeu={jeu} region={region} annee={annee} ecoles={derniere.ecoles_ouvertes} />
          <p className="statut-saisie">
            Dernière saisie : {fr(derniere.ecoles_ouvertes)} écoles, le {dateHeureFr(derniere.saisi_le)} ·{" "}
            {derniere.statut === "envoyee" ? "envoyée à la base en ligne" :
              serveur === "sans_base" ? "gardée sur cet appareil (base en ligne non configurée)" : "sur cet appareil, part au retour du réseau"}
          </p>
        </>
      )}
      {!valide && !derniere && (
        <p className="statut-saisie">
          Aucune saisie pour {annee.replace("-", "/")}. En 2024/25, l'annuaire comptait {fr(region.ecoles.at(-1))} écoles.
        </p>
      )}
    </div>
  );
}

export function resumeSaisie(jeu, region, saisies, annee) {
  const d = derniereSaisie(saisies, region.cle, annee);
  if (!d) return null;
  const e = estimerEffectifs({ region, nowcast: jeu.nowcast, annee, ecolesOuvertes: d.ecoles_ouvertes });
  return e && { ...e, saisie: d, texte: `${fr(d.ecoles_ouvertes)} écoles → ≈ ${fr(e.centrale)} élèves (${e.variationPct >= 0 ? "+" : "−"}${pct(Math.abs(e.variationPct), 1)})` };
}

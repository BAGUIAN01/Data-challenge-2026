"use client";
import { useState } from "react";
import { useDonnees } from "../DonneesProvider";
import SaisieEcoles, { ANNEES_SAISIE, resumeSaisie } from "../SaisieEcoles";
import { AvecDonnees, Risque, trierRegions } from "./communs";
import { fr } from "@/lib/format";

export default function PageAlertes() {
  const { saisies } = useDonnees();
  const [cle, setCle] = useState(null);
  return (
    <AvecDonnees>
      {(jeu) => {
        const regions = trierRegions(jeu.regions);
        const region = regions.find((r) => r.cle === cle) ?? regions[0];
        const v = jeu.validation;
        return (
          <>
            <h1>Calendrier d'alerte</h1>
            <p className="sous-titre">Plus l'information arrive, mieux on anticipe. Chaque étape a été testée sur des années que les modèles n'avaient pas vues.</p>
            <ol className="etapes">
              <li><strong>Fin septembre</strong><br />Violence de l'année, dont juillet-septembre : alerte de rentrée par région (fiabilité AUC {fr(v.auc_septembre, 2)}).</li>
              <li><strong>Début janvier</strong><br />On ajoute la violence d'octobre à décembre : l'alerte est mise à jour, des mois avant l'annuaire (AUC {fr(v.auc_janvier, 2)}).</li>
              <li><strong>Dès que les écoles ouvertes sont comptées</strong><br />Les effectifs de l'année, avec une erreur divisée par deux (± {fr(jeu.nowcast.erreur_pct, 1)} % contre ± {fr(jeu.nowcast.erreur_persistance_pct, 1)} %).</li>
            </ol>
            <section className="carte-bloc" style={{ marginTop: "1rem" }}>
              <h2>Probabilité d'une baisse des effectifs de plus de 5 %</h2>
              <div className="defile">
                <table>
                  <thead>
                    <tr><th>Région</th><th>2025/26, alerte de janvier</th><th>2026/27, alerte de septembre</th><th>2026/27, référence</th></tr>
                  </thead>
                  <tbody>
                    {[...regions].sort((a, b) => b.probabilites.sept_2026_27 - a.probabilites.sept_2026_27).map((r) => (
                      <tr key={r.cle}>
                        <td><a href={`/region/${r.cle}`}>{r.nom}</a></td>
                        <td><Risque p={r.probabilites.janv_2025_26} seuils={jeu.seuils} /></td>
                        <td><Risque p={r.probabilites.sept_2026_27} seuils={jeu.seuils} /></td>
                        <td><Risque p={r.probabilites.ref_2026_27} seuils={jeu.seuils} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="discret">
                Élevé : 40 % ou plus · Moyen : 15 à 39 % · Faible : moins de 15 %. Ces probabilités classent bien les régions mais restent approximatives :
                on lit des niveaux, pas des pourcentages exacts.
              </p>
            </section>
            <section className="carte-bloc">
              <h2>Saisir les écoles ouvertes à la rentrée</h2>
              <p className="discret">
                Le calcul se fait sur cet appareil. La saisie est enregistrée tout de suite, même sans réseau, et part vers la base en ligne au retour du réseau.
              </p>
              <label className="champ" style={{ marginBottom: "0.75rem" }}>
                Région
                <select value={region.cle} onChange={(e) => setCle(e.target.value)}>
                  {regions.map((r) => <option key={r.cle} value={r.cle}>{r.nom}</option>)}
                </select>
              </label>
              <SaisieEcoles key={region.cle} jeu={jeu} region={region} compact />
            </section>
            <section className="carte-bloc">
              <h2>Les saisies de toutes les régions</h2>
              <div className="defile">
                <table>
                  <thead><tr><th>Région</th>{ANNEES_SAISIE.map((a) => <th key={a}>{a.replace("-", "/")}</th>)}</tr></thead>
                  <tbody>
                    {regions.map((r) => (
                      <tr key={r.cle}>
                        <td>{r.nom}</td>
                        {ANNEES_SAISIE.map((a) => {
                          const res = resumeSaisie(jeu, r, saisies, a);
                          return (
                            <td key={a}>
                              {res ? (
                                <>
                                  {res.texte}
                                  <div className="discret">{res.saisie.statut === "envoyee" ? "envoyée" : "en attente du réseau"}</div>
                                </>
                              ) : <span className="discret">aucune saisie</span>}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        );
      }}
    </AvecDonnees>
  );
}

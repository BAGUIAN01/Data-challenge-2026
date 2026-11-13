"use client";
import Carte from "../Carte";
import { AvecDonnees, BadgePriorite, Risque, Tuile, trierRegions } from "./communs";
import { fr, pct, PRIORITES } from "@/lib/format";

export default function PageCarte() {
  return (
    <AvecDonnees>
      {(jeu) => {
        const regions = trierRegions(jeu.regions);
        const p1 = regions.filter((r) => r.priorite === 1);
        const total = regions.reduce((s, r) => s + r.enfants_hors_cm2, 0);
        const enfantsP1 = p1.reduce((s, r) => s + r.enfants_hors_cm2, 0);
        const sept = [...regions].sort((a, b) => b.probabilites.sept_2026_27 - a.probabilites.sept_2026_27)[0];
        const janv = [...regions].sort((a, b) => b.probabilites.janv_2025_26 - a.probabilites.janv_2025_26)[0];
        return (
          <>
            <h1>Où agir en premier à la rentrée 2026/27</h1>
            <p className="sous-titre">
              Priorité 1 : un taux d'achèvement sous la moyenne nationale <strong>et</strong> un risque de baisse des effectifs qui monte.
              Touchez une région pour ouvrir sa fiche.
            </p>
            <div className="grille-tuiles">
              <Tuile libelle="Régions en priorité 1" valeur={p1.length}
                sous={`${fr(enfantsP1)} enfants qui n'atteignent pas le CM2, soit ${pct((enfantsP1 / total) * 100)} du total`} />
              <Tuile libelle="Taux d'achèvement national 2024/25" valeur={pct(jeu.seuils.tap_national, 1)}
                sous={`${pct(jeu.national.tap[0], 1)} en 2015/16`} />
              <Tuile libelle="Alerte de septembre 2026/27" valeur={sept.nom}
                sous={`${pct(sept.probabilites.sept_2026_27)} de risque de baisse des effectifs`} />
              <Tuile libelle="Alerte de janvier 2025/26, avant l'annuaire" valeur={janv.nom}
                sous={`${pct(janv.probabilites.janv_2025_26)} de risque que les effectifs aient baissé`} />
            </div>
            <div className="deux-colonnes">
              <section className="carte-bloc" aria-labelledby="t-carte">
                <h2 id="t-carte">Les 13 régions, par priorité</h2>
                <Carte jeu={jeu} />
                <p className="discret">
                  13 anciennes régions, affichées sous leurs noms de 2025 : trois d'entre elles ont été coupées en 2025 et sont montrées en groupes
                  (par exemple « Goulmou + Sirba + Tapoa »), faute de données par province.
                </p>
              </section>
              <section aria-labelledby="t-liste">
                <h2 id="t-liste">La liste</h2>
                {[1, 2, 3].map((p) => (
                  <div key={p} style={{ marginBottom: "1rem" }}>
                    <h3>{PRIORITES[p].libelle} : {PRIORITES[p].sous}</h3>
                    <ul className="liste-regions">
                      {regions.filter((r) => r.priorite === p).map((r) => (
                        <li key={r.cle}>
                          <a href={`/region/${r.cle}`}>
                            <div className="ligne-region"><strong>{r.nom}</strong><BadgePriorite p={r.priorite} /></div>
                            <div className="discret">
                              Achèvement {pct(r.tap.at(-1), 1)} · {fr(r.enfants_hors_cm2)} enfants hors CM2
                            </div>
                            <div className="discret">Risque 2026/27 : <Risque p={r.probabilites.ref_2026_27} seuils={jeu.seuils} /></div>
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </section>
            </div>
          </>
        );
      }}
    </AvecDonnees>
  );
}

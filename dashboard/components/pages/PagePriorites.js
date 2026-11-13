"use client";
import Matrice from "../Matrice";
import { AvecDonnees, BadgePriorite, Risque, trierRegions } from "./communs";
import { fr, pct } from "@/lib/format";

export default function PagePriorites() {
  return (
    <AvecDonnees>
      {(jeu) => {
        const v = jeu.validation, s = jeu.seuils;
        return (
          <>
            <h1>Matrice de priorité 2026/27</h1>
            <p className="sous-titre">
              Deux critères, fixés à l'avance : le <strong>retard</strong> (taux d'achèvement sous la moyenne nationale, {pct(s.tap_national, 1)}) et le
              <strong> risque qui monte</strong> (probabilité de baisse des effectifs de plus de 5 %, calculée sur la violence d'octobre 2025 à septembre 2026).
            </p>
            <section className="carte-bloc">
              <Matrice jeu={jeu} />
              <p className="discret">
                Rejouée sur 2019/20 à 2023/24 avec seulement l'information de chaque année, la priorité 1 désignait {v.matrice_regions_pct} % des régions
                mais contenait {v.matrice_baisses_pct} % des fortes baisses de l'année suivante et {v.matrice_perdus_pct} % des élèves perdus.
                Elle ne voit pas les réouvertures d'écoles décidées par l'État.
              </p>
            </section>
            <section className="carte-bloc">
              <h2>Le tableau</h2>
              <div className="defile">
                <table>
                  <thead>
                    <tr>
                      <th>Région</th><th>Priorité</th><th className="nombre">Achèvement 2024/25</th>
                      <th>Risque 2026/27 (référence)</th><th>Alerte de septembre</th><th className="nombre">Enfants hors CM2</th><th>Profil</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trierRegions(jeu.regions).map((r) => (
                      <tr key={r.cle}>
                        <td><a href={`/region/${r.cle}`}>{r.nom}</a></td>
                        <td><BadgePriorite p={r.priorite} /></td>
                        <td className="nombre">{pct(r.tap.at(-1), 1)}</td>
                        <td><Risque p={r.probabilites.ref_2026_27} seuils={s} /></td>
                        <td><Risque p={r.probabilites.sept_2026_27} seuils={s} /></td>
                        <td className="nombre">{fr(r.enfants_hors_cm2)}</td>
                        <td>{r.profil}</td>
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

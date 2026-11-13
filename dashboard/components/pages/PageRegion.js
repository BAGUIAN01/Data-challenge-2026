"use client";
import BarresIncidents from "../BarresIncidents";
import CourbeTap from "../CourbeTap";
import SaisieEcoles from "../SaisieEcoles";
import { AvecDonnees, BadgePriorite, Risque, Tuile } from "./communs";
import { fr, NIVEAUX_FACTEUR, pct, PRIORITES } from "@/lib/format";

function valeurFacteur(def, v) {
  if (v === null) return "—";
  if (def.id === "violence") return `${fr(v)} / an`;
  if (def.id === "grossesses") return `${fr(v)} ‰`;
  return pct(v, 1);
}

export default function PageRegion({ cle }) {
  return (
    <AvecDonnees>
      {(jeu) => {
        const r = jeu.regions.find((x) => x.cle === cle);
        if (!r) return <p>Région inconnue. <a href="/">Retour à la carte</a></p>;
        const p = r.probabilites;
        return (
          <>
            <p className="discret"><a href="/">← Carte</a></p>
            <h1>{r.nom}</h1>
            <p className="sous-titre">
              Ancienne région : {r.ancienne} · Profil 2015-2025 : {r.profil} · <BadgePriorite p={r.priorite} /> {PRIORITES[r.priorite].sous}
            </p>
            <div className="grille-tuiles">
              <Tuile libelle="Taux d'achèvement 2024/25" valeur={pct(r.tap.at(-1), 1)} sous={`National : ${pct(jeu.seuils.tap_national, 1)}`} />
              <Tuile libelle="Enfants qui n'atteignent pas le CM2" valeur={fr(r.enfants_hors_cm2)} sous="estimation 2024/25, ordre de grandeur" />
              <Tuile libelle="Risque de baisse des effectifs 2026/27" valeur={<Risque p={p.sept_2026_27} seuils={jeu.seuils} />}
                sous={`Alerte de septembre (référence : ${p.ref_2026_27} %)`} />
              <Tuile libelle="Alerte de janvier 2025/26" valeur={<Risque p={p.janv_2025_26} seuils={jeu.seuils} />}
                sous="avant la publication de l'annuaire" />
            </div>
            <div className="deux-colonnes">
              <section className="carte-bloc">
                <h2>Taux d'achèvement du primaire (%)</h2>
                <CourbeTap jeu={jeu} region={r} />
                <p className="discret">
                  Prévision 2025/26 : {pct(r.prevision_2025_26.centrale, 1)} (de {pct(r.prevision_2025_26.basse, 1)} à {pct(r.prevision_2025_26.haute, 1)}),
                  fourchette tirée des erreurs passées de la règle « comme l'an passé ».
                </p>
              </section>
              <section className="carte-bloc">
                <h2>Ce qu'il faut retenir</h2>
                <ul className="puces">{r.faits.map((f, i) => <li key={i}>{f}</li>)}</ul>
                <h2 style={{ marginTop: "1rem" }}>Leviers proposés</h2>
                <ul className="puces">
                  {r.leviers.map((f, i) => <li key={`l${i}`}>{f}</li>)}
                  {r.leviers_facteurs.map((f, i) => <li key={`f${i}`}>{f}</li>)}
                </ul>
              </section>
            </div>
            <div className="deux-colonnes">
              <section className="carte-bloc">
                <h2>Incidents sécuritaires par année scolaire</h2>
                <BarresIncidents jeu={jeu} region={r} />
                <p className="discret">ACLED, d'octobre à septembre. La violence sert à l'alerte ; elle n'explique pas tout le recul.</p>
              </section>
              <section className="carte-bloc">
                <h2>Les causes de fond</h2>
                <div className="defile">
                  <table>
                    <thead><tr><th>Facteur</th><th className="nombre">Valeur</th><th>Exposition</th></tr></thead>
                    <tbody>
                      {jeu.facteurs_def.map((d) => {
                        const f = r.facteurs[d.id];
                        return (
                          <tr key={d.id}>
                            <td>{d.libelle}</td>
                            <td className="nombre">{valeurFacteur(d, f.valeur)}</td>
                            <td><span className={`badge prio-${f.niveau}`}>{NIVEAUX_FACTEUR[f.niveau]}</span></td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <p className="discret">
                  Exposition comparée aux 13 régions : forte = parmi les 4 régions les plus exposées, faible = parmi les 4 moins exposées. Violence : incidents par an (2021/22 à 2024/25). Pour le CEP et le préscolaire, une valeur basse expose davantage. Le CEP n'est pas un signal de risque :
                  là où peu d'élèves arrivent au bout, ceux qui restent réussissent mieux.
                </p>
              </section>
            </div>
            <section className="carte-bloc">
              <SaisieEcoles jeu={jeu} region={r} />
            </section>
            <p>
              <a href={`/fiches/${r.cle}.pdf`} download>Télécharger la fiche d'une page (PDF)</a>
            </p>
          </>
        );
      }}
    </AvecDonnees>
  );
}

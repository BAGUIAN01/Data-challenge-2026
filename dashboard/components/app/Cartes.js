"use client";
// The figure cards. Each one carries its context: a scale, a comparison, a range or a history.
// Colour only where it means something (the blue ramp, a decline); text stays in text colours.
import { useState } from "react";
import { Fourchette, Matrice } from "./Graphes";
import { Chevron } from "./icones";
import { fr } from "@/lib/format";
import { estimerEffectifs } from "@/lib/prevision-effectifs";
import { centaine, couches, facteurDominant, risque, scoreGlobal, signe } from "@/lib/regles";

const pctFr = (v, d = 1) => `${fr(v, d)} %`;

// The global score of the 13 regions, ranked. It sums up both forms of dropout; the priority
// stays the rule for targeting (it did better on the past, shown on the Régions tab).
export function CarteScore({ jeu, onOuvrir }) {
  if (!jeu.score_global) return null;
  const C = couches(jeu).score, n = jeu.regions.filter((r) => (scoreGlobal(jeu, r) ?? 0) >= 50).length;
  const rangs = [...jeu.regions].sort((a, b) => (scoreGlobal(jeu, b) ?? 0) - (scoreGlobal(jeu, a) ?? 0));
  return (
    <section className="card" aria-label="Score global de décrochage">
      <div className="ch"><b>Score global de décrochage</b><span>sur 100</span></div>
      <div className="kpi"><b className="num">{n}</b><span className="u">régions sur 13 à 50 ou plus</span></div>
      {/* Ranked bars: one row per region, the whole row opens it. Ticks at 25 and 50 mark the tiers. */}
      <ol className="rang" aria-label="Les 13 régions, du score le plus haut au plus bas">
        {rangs.map((r) => {
          const v = scoreGlobal(jeu, r) ?? 0;
          return (
            <li key={r.cle}>
              <button onClick={() => onOuvrir(r.cle)} aria-label={`${r.nom}, score ${v} sur 100`}>
                <span className="rang-nom">{r.nom}</span>
                <span className="rang-piste"><i style={{ width: `${v}%`, background: `var(--c${C.classe(r)})` }} /></span>
                <b className="num">{v}</b>
              </button>
            </li>
          );
        })}
      </ol>
      <p className="foot">Moitié risque de chute des effectifs, moitié part d'enfants qui n'achèvent pas le primaire.</p>
    </section>
  );
}

// What to act on, across the country: the regions grouped by their dominant background factor.
// The lever itself is on each region's page; here, only the factor and its regions.
export function CarteActions({ jeu, onOuvrir }) {
  if (!jeu.facteur_dominant) return null;
  const groupes = new Map();
  for (const r of [...jeu.regions].sort((a, b) => (scoreGlobal(jeu, b) ?? 0) - (scoreGlobal(jeu, a) ?? 0))) {
    const k = facteurDominant(jeu, r)?.dominant ?? "aucun";
    if (!groupes.has(k)) groupes.set(k, []);
    groupes.get(k).push(r);
  }
  const ordre = [...groupes.entries()].sort((a, b) => (a[0] === "aucun") - (b[0] === "aucun") || b[1].length - a[1].length);
  const def = (id) => jeu.facteurs_def.find((d) => d.id === id);
  return (
    <section className="card" aria-label="Sur quoi agir">
      <div className="ch"><b>Sur quoi agir</b><span>facteur dominant</span></div>
      <div className="agir">
        {ordre.map(([k, rs]) => (
          <div key={k} className="agir-l">
            <b>{k === "aucun" ? "Rien ne ressort" : def(k)?.libelle}</b>
            <span className="puces">{rs.map((r) => <button key={r.cle} className="puce" onClick={() => onOuvrir(r.cle)}>{r.nom}</button>)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

// The country in two figures, no chart: the charts live on each region's page.
export function CartePays({ jeu, nbSaisies, onSaisies }) {
  const e = jeu.national.eleves, tap = jeu.national.tap, n = e.length - 1, d = (e[n] / e[n - 1] - 1) * 100;
  return (
    <section className="card" aria-label="Le pays">
      <div className="ch"><b>Le pays</b><span>{jeu.annees[n]}</span></div>
      <div className="duo">
        <div><b className="num">{fr(e[n])}</b><span>élèves au primaire</span><em className="num">{signe(d)}{fr(Math.abs(d), 1)} % sur un an</em></div>
        <div><b className="num">{pctFr(tap[n])}</b><span>achèvent le primaire</span><em className="num down">{signe(tap[n] - tap[0])}{fr(Math.abs(tap[n] - tap[0]), 1)} pts depuis {jeu.annees[0]}</em></div>
      </div>
      <button className="inrow" onClick={onSaisies}>Écoles ouvertes saisies<b>{nbSaisies} région{nbSaisies > 1 ? "s" : ""} sur 13</b><Chevron /></button>
    </section>
  );
}

// Expected pupils from a count of open schools (decision D13): a measured range at one year from the
// last yearbook, an order of magnitude beyond.
export function BlocEstimation({ jeu, region, annee, ecoles }) {
  const e = estimerEffectifs({ region, nowcast: jeu.nowcast, annee, ecolesOuvertes: ecoles });
  if (!e) return null;
  const kpi = (
    <div className="kpi"><b className="num">≈ {fr(centaine(e.centrale))}</b>
      <span className={`d num${e.variationPct < 0 ? " down" : ""}`}>{signe(e.variationPct)}{fr(Math.abs(e.variationPct), 1)} % depuis 2024/25</span></div>
  );
  const base = `${fr(ecoles)} écoles ouvertes, contre ${fr(e.ecolesRef)} dans l'annuaire 2024/25.`;
  if (!e.mesuree) {
    return <>{kpi}<p className="foot">{base} À deux ans de l'annuaire, la méthode n'a pas été vérifiée : un ordre de grandeur, sans fourchette.</p></>;
  }
  const lo = centaine(e.basse), hi = centaine(e.haute), dans = e.elevesRef >= lo && e.elevesRef <= hi;
  return (
    <>
      {kpi}
      <Fourchette c={centaine(e.centrale)} lo={lo} hi={hi} reference={e.elevesRef} refLabel={`${fr(e.elevesRef)} en 2024/25`} />
      <p className="foot">
        {base} Fourchette : ± {fr(jeu.nowcast.erreur_pct, 1)} %, l'erreur moyenne sur les années passées.
        {" "}{dans ? "2024/25 y reste : la baisse est probable, pas certaine." : "2024/25 en sort : l'écart est net."}
      </p>
    </>
  );
}

export function CarteMatrice({ jeu, onOuvrir }) {
  const [lu, setLu] = useState(null);
  const C = couches(jeu).priorite, r = lu && jeu.regions.find((x) => x.cle === lu);
  return (
    <section className="card">
      <div className="ch"><b>Matrice de priorité</b><span>{r ? `${r.nom} · ${pctFr(r.tap.at(-1))} · ${risque(r)} %` : "Toucher un point"}</span></div>
      <Matrice regions={jeu.regions} seuils={jeu.seuils} couleur={(x) => `var(--c${C.classe(x)})`} lu={lu} onLire={setLu} onOuvrir={onOuvrir} />
      <p className="foot">
        À gauche, l'achèvement 2024/25 sous la moyenne du pays ({pctFr(jeu.seuils.tap_national)}) ; en haut, un risque de baisse élevé
        (40 % ou plus). Le coin grisé, c'est la priorité 1.
      </p>
    </section>
  );
}

export function CarteCalendrier({ jeu }) {
  const v = jeu.validation;
  return (
    <section className="card">
      <div className="ch"><b>Calendrier d'alerte</b><span>rentrée <span className="nw">2026-2027</span></span></div>
      <div className="tl">
        <div className="done"><i /><div><b>Fin septembre · alerte de rentrée</b>
          <span>Violence de l'année, dont juillet à septembre. Fiabilité {fr(v.auc_septembre, 2)} (1 = parfait, 0,5 = hasard).</span></div></div>
        <div className="now"><i /><div><b>En cours · écoles ouvertes</b>
          <span>Dès qu'elles sont comptées : les élèves de l'année, erreur ± {fr(jeu.nowcast.erreur_pct, 1)} % au lieu de ± {fr(jeu.nowcast.erreur_persistance_pct, 1)} %.</span></div></div>
        <div><i /><div><b>Début janvier · mise à jour</b><span>On ajoute la violence d'octobre à décembre. Fiabilité {fr(v.auc_janvier, 2)}.</span></div></div>
      </div>
    </section>
  );
}

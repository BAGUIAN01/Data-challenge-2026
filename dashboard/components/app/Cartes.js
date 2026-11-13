"use client";
// The figure cards. Each one carries its context: a scale, a comparison, a range or a history.
// Colour only where it means something (the blue ramp, a decline); text stays in text colours.
import { useState } from "react";
import { Bande, Courbe, Echelle, Fourchette, Matrice, Pile } from "./Graphes";
import { Chevron } from "./icones";
import { fr } from "@/lib/format";
import { estimerEffectifs } from "@/lib/prevision-effectifs";
import { alerteSeptembre, centaine, couches, niveau, niveauScore, PRIORITES, risque, scoreGlobal, signe, ZONES_SCORE } from "@/lib/regles";

const pctFr = (v, d = 1) => `${fr(v, d)} %`;

export function CarteRisque({ jeu, region: r, onOuvrir }) {
  const p = risque(r), s = alerteSeptembre(r), n = niveau(p, jeu.seuils);
  const Tag = onOuvrir ? "button" : "section";
  return (
    <Tag className="card" onClick={onOuvrir} aria-label={onOuvrir ? `Risque de baisse, ${r.nom} : ouvrir la région` : undefined}>
      <div className="ch"><b>Risque de baisse</b><span>Rentrée <span className="nw">2026-2027</span>{onOuvrir && <Chevron />}</span></div>
      <div className="kpi"><b className="num">{p} %</b><span className="u">risque {n}</span></div>
      <Echelle p={p} p2={s} seuils={jeu.seuils} actif={n} label={`${p} %, risque ${n} ; alerte de septembre ${s} %`} />
      <p className="foot">
        Probabilité d'une baisse des effectifs de plus de 5 %. {s !== p && <>Le rond : l'alerte de septembre, {s} %. </>}
        On lit des niveaux, pas des pourcentages exacts.
      </p>
    </Tag>
  );
}

export function CartePriorites({ jeu, onFiltre }) {
  const c = [1, 2, 3].map((p) => jeu.regions.filter((r) => r.priorite === p).length), v = jeu.validation;
  return (
    <section className="card" aria-label="Où agir en premier">
      <div className="ch"><b>Où agir en premier</b><span>13 régions</span></div>
      <div className="kpi"><b className="num">{c[0]}</b><span className="u">régions en priorité 1</span></div>
      <Pile parts={c.map((n, i) => ({ n, c: `var(--c${i + 1})` }))} label={c.map((n, i) => `priorité ${i + 1} : ${n}`).join(", ")} />
      <div className="leg">
        {c.map((n, i) => (
          <button key={i} onClick={() => onFiltre(`p${i + 1}`)}>
            <i className="m" style={{ "--c": `var(--c${i + 1})` }} />{PRIORITES[i + 1].libelle}, {PRIORITES[i + 1].sous}<b className="num">{n}</b><Chevron />
          </button>
        ))}
      </div>
      <p className="foot">
        Priorité 1 : achèvement sous la moyenne du pays ({pctFr(jeu.seuils.tap_national)}) et risque élevé. Rejouée sur le passé, elle désignait
        {" "}{v.matrice_regions_pct} % des régions et contenait {v.matrice_baisses_pct} % des fortes baisses.
      </p>
    </section>
  );
}

// The global score of the 13 regions on one strip. It sums up both forms of dropout; the priority
// stays the rule for targeting (it did better on the past, and the card says so).
export function CarteScore({ jeu, onOuvrir }) {
  const [lu, setLu] = useState(null);
  if (!jeu.score_global) return null;
  const C = couches(jeu).score, n = jeu.regions.filter((r) => (scoreGlobal(jeu, r) ?? 0) >= 50).length;
  const r = lu && jeu.regions.find((x) => x.cle === lu);
  return (
    <section className="card" aria-label="Score global de décrochage">
      <div className="ch"><b>Score global de décrochage</b><span>{r ? `${r.nom} · ${scoreGlobal(jeu, r)}/100` : "Toucher un point"}</span></div>
      <div className="kpi"><b className="num">{n}</b><span className="u">régions à 50 ou plus, sur 100</span></div>
      <Bande points={jeu.regions.map((x) => ({ id: x.cle, nom: x.nom, v: scoreGlobal(jeu, x) ?? 0, c: `var(--c${C.classe(x)})` }))}
        seuils={jeu.seuils} zones={ZONES_SCORE} lu={lu} onLire={setLu} onOuvrir={onOuvrir} />
      <p className="foot">Moitié risque de chute des effectifs (la violence), moitié part d'enfants qui n'achèvent pas le primaire : le brutal et le lent.</p>
    </section>
  );
}

export function CarteBande({ jeu, onOuvrir }) {
  const [lu, setLu] = useState(null);
  const C = couches(jeu).risque, n = jeu.regions.filter((r) => risque(r) >= jeu.seuils.risque_eleve).length;
  const r = lu && jeu.regions.find((x) => x.cle === lu);
  return (
    <section className="card" aria-label="Où le risque monte">
      <div className="ch"><b>Où le risque monte</b><span>{r ? `${r.nom} · ${risque(r)} %` : "Toucher un point"}</span></div>
      <div className="kpi"><b className="num">{n}</b><span className="u">régions en risque élevé</span></div>
      <Bande points={jeu.regions.map((x) => ({ id: x.cle, nom: x.nom, v: risque(x), c: `var(--c${C.classe(x)})` }))}
        seuils={jeu.seuils} lu={lu} onLire={setLu} onOuvrir={onOuvrir} />
      <p className="foot">Chaque point est une région, placée selon sa probabilité de baisse en 2026/27.</p>
    </section>
  );
}

export function CarteElevesPays({ jeu, nbSaisies, onSaisies }) {
  const [lu, setLu] = useState(null);
  const v = jeu.national.eleves, n = v.length - 1, i = lu ?? n, d = (v[n] / v[n - 1] - 1) * 100;
  return (
    <section className="card">
      <div className="ch"><b>Combien d'élèves</b><span>{jeu.annees[i]}</span></div>
      <div className="kpi"><b className="num">{fr(v[i])}</b><span className="u">au primaire</span>
        <span className="d num">{signe(d)}{fr(Math.abs(d), 1)} % sur un an</span></div>
      <Courbe annees={jeu.annees} series={[{ v, c: "var(--fg)" }]} fmt={(x) => fr(x)} bas lu={lu} onLire={setLu} label="Élèves du primaire, de 2015/16 à 2024/25" />
      <button className="inrow" onClick={onSaisies}>Écoles ouvertes saisies<b>{nbSaisies} région{nbSaisies > 1 ? "s" : ""} sur 13</b><Chevron /></button>
    </section>
  );
}

export function CarteTapPays({ jeu }) {
  const [lu, setLu] = useState(null);
  const v = jeu.national.tap, n = v.length - 1, i = lu ?? n, tot = jeu.regions.reduce((s, r) => s + r.enfants_hors_cm2, 0);
  return (
    <section className="card">
      <div className="ch"><b>Achèvement du primaire</b><span>{jeu.annees[i]}</span></div>
      <div className="kpi"><b className="num">{pctFr(v[i])}</b><span className="u">au pays</span>
        <span className="d num down">{signe(v[n] - v[0])}{fr(Math.abs(v[n] - v[0]), 1)} pts depuis {jeu.annees[0]}</span></div>
      <Courbe annees={jeu.annees} series={[{ v, c: "var(--fg)" }]} y0={0} y1={100} fmt={(x) => pctFr(x)} lu={lu} onLire={setLu} label="Taux d'achèvement du pays" />
      <p className="foot">Enfants qui n'atteignent pas le CM2 : environ {fr(tot)}, en additionnant les 13 régions (estimation 2024/25, ordre de grandeur).</p>
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

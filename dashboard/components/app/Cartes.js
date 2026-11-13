"use client";
// The figure cards. Each one carries its context: a scale, a comparison, a range or a history.
// Colour only where it means something (the blue ramp, a decline); text stays in text colours.
import { useState } from "react";
import { Bande, Colonnes, Courbe, Echelle, Fourchette, Matrice, Pile } from "./Graphes";
import { Chevron } from "./icones";
import { fr } from "@/lib/format";
import { estimerEffectifs } from "@/lib/prevision-effectifs";
import { alerteSeptembre, centaine, couches, EXPOSITION, niveau, PRIORITES, risque, signe } from "@/lib/regles";

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

export function CarteBande({ jeu, onOuvrir }) {
  const [lu, setLu] = useState(null);
  const C = couches(jeu.seuils).risque, n = jeu.regions.filter((r) => risque(r) >= jeu.seuils.risque_eleve).length;
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

export function CarteTapRegion({ jeu, region: r }) {
  const [lu, setLu] = useState(null);
  const n = jeu.annees.length - 1, pv = r.prevision_2025_26, prevue = lu === n + 1;
  const i = lu === null || prevue ? n : lu;
  return (
    <section className="card">
      <div className="ch"><b>Achèvement du primaire</b><span>{prevue ? "25/26 prévision" : jeu.annees[i]}</span></div>
      <div className="kpi">
        <b className="num">{prevue ? `≈ ${pctFr(pv.centrale)}` : pctFr(r.tap[i])}</b>
        <span className="u">{prevue ? `${fr(pv.basse, 1)} à ${pctFr(pv.haute)}` : `pays ${pctFr(jeu.national.tap[i])}`}</span>
      </div>
      <Courbe annees={jeu.annees} series={[{ v: jeu.national.tap, c: "var(--nat)" }, { v: r.tap, c: "var(--fg)" }]} y0={0} y1={100}
        fmt={(x) => pctFr(x)} prev={pv} lu={lu} onLire={setLu} label={`Taux d'achèvement de ${r.nom} et du pays`} />
      <div className="lg">
        <span><i style={{ "--c": "var(--fg)" }} />{r.nom}</span><span><i style={{ "--c": "var(--nat)" }} />Burkina Faso</span>
        <span><i className="bx" style={{ "--c": "var(--band2)" }} />Prévision 2025/26</span>
      </div>
      <p className="foot">
        Prévision 2025/26 : {fr(pv.basse, 1)} à {pctFr(pv.haute)}. Le classement des régions change peu d'une année à l'autre
        (corrélation de rang {fr(jeu.validation.rang_tap, 2)}).
      </p>
    </section>
  );
}

export function CarteGenre({ jeu, region: r }) {
  const f = r.tap_f.at(-1), g = r.tap_g.at(-1), max = Math.max(f, g, 1);
  return (
    <section className="card">
      <div className="ch"><b>Filles et garçons</b><span>Achèvement {jeu.annees.at(-1)}</span></div>
      <div className="cmp">
        <span>Filles</span><span className="trk"><i style={{ "--c": "var(--fg)", width: `${(f / max) * 100}%` }} /></span><b className="num">{pctFr(f)}</b>
        <span>Garçons</span><span className="trk"><i style={{ "--c": "var(--z3)", width: `${(g / max) * 100}%` }} /></span><b className="num">{pctFr(g)}</b>
      </div>
      <p className="foot">
        {Math.abs(f - g) < 1 ? "Filles et garçons achèvent à peu près autant."
          : f > g ? `Les garçons achèvent moins : ${fr(f - g, 1)} points d'écart.` : `Les filles achèvent moins : ${fr(g - f, 1)} points d'écart.`}
      </p>
    </section>
  );
}

export function CarteViolence({ jeu, region: r }) {
  const [lu, setLu] = useState(null);
  const v = r.incidents, n = v.length - 1, i = lu ?? n, d = v[n] - v[n - 1];
  return (
    <section className="card">
      <div className="ch"><b>Violence</b><span>{lu === null ? "oct. 2025 – sept. 2026" : jeu.annees_violence[i]}</span></div>
      <div className="kpi"><b className="num">{fr(v[i])}</b><span className="u">incidents</span>
        {lu === null && <span className="d num">{signe(d)}{fr(Math.abs(d))} sur un an</span>}</div>
      <Colonnes valeurs={v} annees={jeu.annees_violence} lu={lu} onLire={setLu} label={`Incidents de sécurité par année scolaire, ${r.nom}`} />
      <p className="foot">Incidents de sécurité par année scolaire, d'octobre à septembre (ACLED). La violence sert à l'alerte ; elle n'explique pas tout le recul.</p>
    </section>
  );
}

function valeurFacteur(def, v) {
  if (v === null || v === undefined) return "—";
  if (def.id === "violence") return `${fr(v)} incidents par an`;
  if (def.id === "grossesses") return `${fr(v)} pour 1 000 filles de 15-19 ans`;
  return `${fr(v, 1)} ${def.unite === "%" ? "%" : def.unite}`;
}

export function CarteFacteurs({ jeu, region: r }) {
  return (
    <section className="card">
      <div className="ch"><b>Ce qui pèse sur la scolarité</b><span>Exposition</span></div>
      {jeu.facteurs_def.map((def) => {
        const f = r.facteurs[def.id];
        if (!f) return null;
        return (
          <div className="fx" key={def.id}>
            <b>{def.libelle}</b><span>{valeurFacteur(def, f.valeur)}</span>
            <div className="tier" aria-label={`exposition ${EXPOSITION[f.niveau]}`}>
              {EXPOSITION[f.niveau]}<span className="bars3">{[1, 2, 3].map((k) => <i key={k} className={k <= 4 - f.niveau ? "on" : ""} />)}</span>
            </div>
          </div>
        );
      })}
      <p className="foot">
        Forte : parmi les 4 régions les plus exposées ; faible : parmi les 4 moins exposées. Pour le CEP et le préscolaire, une valeur basse expose
        davantage. Ces facteurs expliquent les écarts entre régions ; ils n'améliorent pas la prévision.
      </p>
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

export function CarteEstimation({ jeu, region, saisie }) {
  if (!saisie) {
    return (
      <section className="card">
        <div className="ch"><b>Élèves attendus</b><span>aucune saisie</span></div>
        <p className="para">
          Comptez les écoles ouvertes à la rentrée : les élèves de l'année se calculent sur ce téléphone, avec une erreur moyenne
          de ± {fr(jeu.nowcast.erreur_pct, 1)} %.
        </p>
      </section>
    );
  }
  return (
    <section className="card">
      <div className="ch"><b>Élèves attendus</b><span>{saisie.annee.replace("-", "/")} · {saisie.statut === "en_attente" ? "en attente d'envoi" : "envoyée"}</span></div>
      <BlocEstimation jeu={jeu} region={region} annee={saisie.annee} ecoles={saisie.ecoles_ouvertes} />
    </section>
  );
}

export function CarteMatrice({ jeu, onOuvrir }) {
  const [lu, setLu] = useState(null);
  const C = couches(jeu.seuils).priorite, r = lu && jeu.regions.find((x) => x.cle === lu);
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

"use client";
// The region screen, written as an analyst's brief, in the order of the challenge: the prediction
// first (risk of a drop in 2026/27, completion forecast 2025/26, expected pupils), then the situation
// placed among the 13 regions, then what drives the risk, the findings and the levers.
import { useEffect, useState } from "react";
import { Colonnes, Courbe, Fourchette } from "./Graphes";
import { fr } from "@/lib/format";
import { estimerEffectifs } from "@/lib/prevision-effectifs";
import { alerteSeptembre, centaine, EXPOSITION, facteurDominant, niveau, niveauScore, NOM_ACTION, PRIORITES, risque, scoreGlobal, signe } from "@/lib/regles";

const pct = (v, d = 1) => `${fr(v, d)} %`;
// What each factor's value measures, in a few words.
const SOUS_FACTEUR = { violence: "incidents par an, 2021/22 à 2024/25", grossesses: "naissances pour 1 000 filles de 15-19 ans",
  cep: "taux de réussite à l'examen", prescolaire: "taux brut de préscolarisation" };
const rangFr = (n) => (n === 1 ? "1er" : `${n}e`);

// Rank of the region among the 13, 1 = the most worrying (sens: "bas" if a low value worries).
function rang(regions, valeur, r, sens) {
  const v = valeur(r);
  return 1 + regions.filter((x) => (sens === "bas" ? valeur(x) < v : valeur(x) > v)).length;
}

// The 13 regions on one line: grey dots, this region dark, an optional reference tick.
function Bande13({ valeurs, choisie, reference, min, max, label }) {
  const X = (v) => `${(((v - min) / (max - min || 1)) * 100).toFixed(2)}%`;
  return (
    <div className="strip" role="img" aria-label={label}>
      {valeurs.map((v, i) => <i key={i} style={{ left: X(v) }} />)}
      {reference !== undefined && <i className="ref" style={{ left: X(reference) }} />}
      <i className="sel" style={{ left: X(choisie) }} />
    </div>
  );
}

function Repere({ titre, sous, valeur, droite, bande }) {
  return (
    <div className="rep">
      <div className="rep-l"><b>{titre}</b>{sous && <span>{sous}</span>}</div>
      <div className="rep-v num">{valeur}</div>
      <div className="rep-r">{droite}</div>
      {bande}
    </div>
  );
}

function verdict(jeu, r) {
  const sous = r.tap.at(-1) < jeu.seuils.tap_national, n = niveau(risque(r), jeu.seuils), s = scoreGlobal(jeu, r);
  const fd = facteurDominant(jeu, r);
  const action = fd?.dominant ? ` Agir d'abord sur ${NOM_ACTION[fd.dominant] ?? fd.def?.libelle.toLowerCase()}.` : "";
  return `Risque ${n} de baisse des effectifs en 2026/27 (${risque(r)} %), achèvement ${sous ? "sous" : "au-dessus de"} la moyenne du pays.${s === null ? "" : action}`;
}

// 1. The global score: one number, its two halves, and where the region stands among the 13.
function BlocScore({ jeu, r }) {
  const R = jeu.regions, s = scoreGlobal(jeu, r), w = jeu.score_global.poids_risque;
  const brutal = 100 * w * (risque(r) / 100), lent = 100 * (1 - w) * (1 - r.tap.at(-1) / 100);
  return (
    <section className="sec">
      <h2>Score global de risque<span>{rangFr(rang(R, (x) => scoreGlobal(jeu, x) ?? 0, r, "haut"))} sur 13 · {niveauScore(s)}</span></h2>
      <div className="chiffre chiffre-xl num">{s}<span> / 100</span></div>
      <div className="decomp" role="img" aria-label={`Score ${s} : ${fr(brutal, 0)} viennent du risque de chute, ${fr(lent, 0)} des enfants qui n'achèvent pas`}>
        <i style={{ width: `${brutal}%`, background: "var(--fg)" }} /><i style={{ width: `${lent}%`, background: "var(--z3)" }} />
      </div>
      <div className="lg">
        <span><i className="bx" style={{ "--c": "var(--fg)" }} />Chute des effectifs (violence) : {fr(brutal, 0)}</span>
        <span><i className="bx" style={{ "--c": "var(--z3)" }} />Enfants qui n'achèvent pas : {fr(lent, 0)}</span>
      </div>
    </section>
  );
}

// 2. What to act on: the dominant background factor, its lever, and the weight of every factor.
function BlocAction({ jeu, r }) {
  const fd = facteurDominant(jeu, r);
  const toutes = Object.values(jeu.facteur_dominant.par_region).flatMap((x) => Object.values(x.contributions));
  const m = Math.max(...toutes.map(Math.abs)) || 1;
  const lignes = Object.entries(fd.contributions).sort((a, b) => b[1] - a[1]).slice(0, 4);
  const def = (id) => jeu.facteurs_def.find((d) => d.id === id);
  return (
    <section className="sec">
      <h2>Sur quoi agir<span>facteur dominant</span></h2>
      {fd.def ? (
        <div className="action">
          <b>{fd.def.libelle}</b>
          {fd.def.levier && <p>{fd.def.levier}</p>}
          {fd.defSecond && <span>Ensuite : {fd.defSecond.libelle.toLowerCase()}.</span>}
        </div>
      ) : <p className="lecture">Aucun facteur de fond n'est au-dessus de la moyenne des 13 régions : consolider ce qui marche.</p>}
      <div className="contrib" role="img" aria-label={`Poids des facteurs pour ${r.nom}`}>
        {lignes.map(([id, v]) => (
          <div key={id} className={id === fd.dominant ? "on" : ""}>
            <span>{def(id)?.libelle ?? id}</span>
            <span className="axe"><i style={{ [v >= 0 ? "left" : "right"]: "50%", width: `${(Math.abs(v) / m) * 50}%`, background: v < 0 ? "var(--z2)" : id === fd.dominant ? "var(--fg)" : "var(--z3)" }} /></span>
          </div>
        ))}
      </div>
      <p className="lecture">Les 4 facteurs qui pèsent le plus ; à droite du trait, plus exposé que la moyenne des 13 régions.</p>
    </section>
  );
}

export default function FicheRegion({ jeu, r, saisies, onMethode }) {
  const n = jeu.annees.length - 1, nat = jeu.national;
  const [luTap, setLuTap] = useState(null);
  const [luInc, setLuInc] = useState(null);
  // Opening animation, year by year (2015/16 onwards): both charts draw themselves; « Rejouer » restarts.
  const nV = r.incidents.length - 1, [pas, setPas] = useState(0), [tour, setTour] = useState(0);
  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { setPas(nV); return undefined; }
    setPas(0);
    const t = setInterval(() => setPas((p) => { if (p >= nV) { clearInterval(t); return p; } return p + 1; }), 280);
    return () => clearInterval(t);
  }, [tour, nV]);
  const anime = pas < nV;
  const pv = r.prevision_2025_26, prevue = !anime && luTap === n + 1, iT = anime ? Math.min(pas, n) : luTap ?? n;
  const lectureTap = prevue ? `2025/26 prévu · ${fr(pv.basse, 1)} à ${pct(pv.haute)}` : `${jeu.annees[iT]} · ${pct(r.tap[iT])} · pays ${pct(nat.tap[iT])}`;
  const iI = anime ? pas : luInc ?? r.incidents.length - 1;
  const saisie = saisies.filter((s) => s.cle === r.cle).sort((a, b) => String(b.saisi_le).localeCompare(String(a.saisi_le)))[0];
  const est = saisie && estimerEffectifs({ region: r, nowcast: jeu.nowcast, annee: saisie.annee, ecolesOuvertes: saisie.ecoles_ouvertes });
  const leviers = r.leviers.concat(r.leviers_facteurs).slice(0, 3);
  return (
    <div className="fiche">
      <p className="sub"><i className="m" style={{ "--c": `var(--c${r.priorite})` }} />{PRIORITES[r.priorite].libelle} · {PRIORITES[r.priorite].sous} · ancienne {r.ancienne}</p>

      {scoreGlobal(jeu, r) !== null && <BlocScore jeu={jeu} r={r} />}
      {facteurDominant(jeu, r) && <BlocAction jeu={jeu} r={r} />}

      <section className="sec">
        <h2>Achèvement<span className="num">{lectureTap}</span></h2>
        <Courbe annees={jeu.annees} series={[{ v: nat.tap, c: "var(--nat)" }, { v: r.tap, c: "var(--fg)" }]} y0={0} y1={100} fmt={(x) => pct(x)}
          prev={pv} lu={anime ? null : luTap} onLire={anime ? undefined : setLuTap} jusqua={anime ? pas : null} label={`Taux d'achèvement de ${r.nom} et du pays, et prévision 2025/26`} />
        <div className="lg"><span><i style={{ "--c": "var(--fg)" }} />{r.nom}</span><span><i style={{ "--c": "var(--nat)" }} />Pays</span>
          <span><i className="bx" style={{ "--c": "var(--band2)" }} />Prévision</span></div>
      </section>

      <section className="sec">
        <h2>Violence<span className="num">{jeu.annees_violence[iI]} · {fr(r.incidents[iI])} incidents</span></h2>
        <Colonnes valeurs={r.incidents} annees={jeu.annees_violence} lu={anime ? null : luInc} onLire={anime ? undefined : setLuInc} jusqua={anime ? pas : null} label={`Incidents de sécurité par année scolaire, ${r.nom}`} />
        <button className="rejouer" onClick={() => setTour((x) => x + 1)}>{anime ? `Année ${jeu.annees_violence[pas]}…` : "Rejouer les années"}</button>
      </section>

      {est && (
        <section className="sec">
          <h2>Élèves attendus<span>{saisie.annee.replace("-", "/")}</span></h2>
          <div className="chiffre num">≈ {fr(centaine(est.centrale))}</div>
          <p className={`lecture${est.variationPct < 0 ? " down" : ""}`}>{signe(est.variationPct)}{fr(Math.abs(est.variationPct), 1)} % depuis 2024/25</p>
        </section>
      )}

      <section className="sec">
        <h2>Leviers</h2>
        <ol className="liste-num">{leviers.map((f, i) => <li key={i}>{f}</li>)}</ol>
      </section>

      <p className="lecture sources"><button className="lien" onClick={onMethode}>Méthode, sources et limites</button></p>
    </div>
  );
}

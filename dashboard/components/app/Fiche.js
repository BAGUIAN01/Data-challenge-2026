"use client";
// The region screen, written as an analyst's brief, in the order of the challenge: the prediction
// first (risk of a drop in 2026/27, completion forecast 2025/26, expected pupils), then the situation
// placed among the 13 regions, then what drives the risk, the findings and the levers.
import { useState } from "react";
import { Colonnes, Courbe, Fourchette } from "./Graphes";
import { fr } from "@/lib/format";
import { estimerEffectifs } from "@/lib/prevision-effectifs";
import { alerteSeptembre, centaine, EXPOSITION, niveau, PRIORITES, risque, signe } from "@/lib/regles";

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
  const sous = r.tap.at(-1) < jeu.seuils.tap_national, n = niveau(risque(r), jeu.seuils);
  return `Risque ${n} de baisse des effectifs en 2026/27 (${risque(r)} %), achèvement ${sous ? "sous" : "au-dessus de"} la moyenne du pays.`;
}

export default function FicheRegion({ jeu, r, saisies, onMethode }) {
  const R = jeu.regions, n = jeu.annees.length - 1, nat = jeu.national;
  const [luTap, setLuTap] = useState(null);
  const [luInc, setLuInc] = useState(null);
  const p = risque(r), sept = alerteSeptembre(r);
  const evol = (x) => (x.eleves.at(-1) / x.eleves.at(-2) - 1) * 100;
  const ecart = (x) => x.tap_f.at(-1) - x.tap_g.at(-1);
  const inc = (x) => x.incidents.at(-1);
  const maxHors = Math.max(...R.map((x) => x.enfants_hors_cm2)), maxInc = Math.max(...R.map(inc));
  const mEvol = Math.max(...R.map((x) => Math.abs(evol(x)))), mEcart = Math.max(...R.map((x) => Math.abs(ecart(x))));
  const saisie = saisies.filter((s) => s.cle === r.cle).sort((a, b) => String(b.saisi_le).localeCompare(String(a.saisi_le)))[0];
  const est = saisie && estimerEffectifs({ region: r, nowcast: jeu.nowcast, annee: saisie.annee, ecolesOuvertes: saisie.ecoles_ouvertes });
  const pv = r.prevision_2025_26;
  // Readings of the two charts (a finger on the chart moves them).
  const iT = luTap ?? n, prevue = luTap === n + 1;
  const lectureTap = prevue ? `25/26, prévision · ${fr(pv.basse, 1)} à ${pct(pv.haute)}` : `${jeu.annees[iT]} · ${pct(r.tap[iT])} · pays ${pct(nat.tap[iT])}`;
  const iI = luInc ?? r.incidents.length - 1;
  const lectureInc = `${jeu.annees_violence[iI]} · ${fr(r.incidents[iI])} incidents`;

  return (
    <div className="fiche">
      <p className="sub">Ancienne région : {r.ancienne} · profil 2015-2025 : {r.profil.toLowerCase()}</p>
      <div className="verdict" style={{ "--c": `var(--c${r.priorite})` }}>
        <b><i className="m" />{PRIORITES[r.priorite].libelle} · {PRIORITES[r.priorite].sous}</b>
        <span>{verdict(jeu, r)}</span>
      </div>

      <section className="sec">
        <h2>Prévision<span>rang sur 13 : 1 = le plus préoccupant</span></h2>
        <Repere titre="Risque de baisse des effectifs" sous={`2026/27 · ${niveau(p, jeu.seuils)} · alerte de septembre ${sept} % · mise à jour début janvier`} valeur={`${p} %`}
          droite={`${rangFr(rang(R, risque, r, "haut"))}/13`}
          bande={<Bande13 valeurs={R.map(risque)} choisie={p} reference={jeu.seuils.risque_eleve} min={0} max={100}
            label={`Risque des 13 régions ; seuil élevé ${jeu.seuils.risque_eleve} %`} />} />
        <Repere titre="Achèvement prévu" sous={`2025/26 · ${fr(pv.basse, 1)} à ${pct(pv.haute)} · pays ${pct(jeu.seuils.tap_national)} en 2024/25`} valeur={`≈ ${pct(pv.centrale)}`}
          droite={`${rangFr(rang(R, (x) => x.prevision_2025_26.centrale, r, "bas"))}/13`}
          bande={<Bande13 valeurs={R.map((x) => x.prevision_2025_26.centrale)} choisie={pv.centrale} reference={jeu.seuils.tap_national} min={0} max={100}
            label={`Achèvement prévu des 13 régions ; ${r.nom} ${pct(pv.centrale)}`} />} />
        {est ? (
          <Repere titre="Élèves attendus" sous={`${saisie.annee.replace("-", "/")} · ${fr(saisie.ecoles_ouvertes)} écoles ouvertes · ${signe(est.variationPct)}${fr(Math.abs(est.variationPct), 1)} % depuis 2024/25`}
            valeur={`≈ ${fr(centaine(est.centrale))}`} droite=""
            bande={est.mesuree ? <div className="rep-plein"><Fourchette c={centaine(est.centrale)} lo={centaine(est.basse)} hi={centaine(est.haute)} reference={est.elevesRef} refLabel={`${fr(est.elevesRef)} en 2024/25`} /></div>
              : <p className="lecture rep-plein">À deux ans de l'annuaire : ordre de grandeur, sans fourchette.</p>} />
        ) : (
          <Repere titre="Élèves attendus" sous={`dès que les écoles ouvertes sont saisies · ± ${fr(jeu.nowcast.erreur_pct, 1)} %`} valeur="—" droite="" />
        )}
      </section>

      <section className="sec">
        <h2>Achèvement du primaire<span className="num">{lectureTap}</span></h2>
        <Courbe annees={jeu.annees} series={[{ v: nat.tap, c: "var(--nat)" }, { v: r.tap, c: "var(--fg)" }]} y0={0} y1={100} fmt={(x) => pct(x)}
          prev={pv} lu={luTap} onLire={setLuTap} label={`Taux d'achèvement de ${r.nom} et du pays, et prévision 2025/26`} />
        <div className="lg"><span><i style={{ "--c": "var(--fg)" }} />{r.nom}</span><span><i style={{ "--c": "var(--nat)" }} />Burkina Faso</span>
          <span><i className="bx" style={{ "--c": "var(--band2)" }} />Prévision 2025/26</span></div>
      </section>

      <section className="sec">
        <h2>Situation<span>2024/25, dernier annuaire</span></h2>
        <Repere titre="Achèvement du primaire" sous={`pays ${pct(jeu.seuils.tap_national)}`} valeur={pct(r.tap.at(-1))}
          droite={`${rangFr(rang(R, (x) => x.tap.at(-1), r, "bas"))}/13`}
          bande={<Bande13 valeurs={R.map((x) => x.tap.at(-1))} choisie={r.tap.at(-1)} reference={jeu.seuils.tap_national} min={0} max={100}
            label={`Achèvement des 13 régions ; ${r.nom} ${pct(r.tap.at(-1))}`} />} />
        <Repere titre="Enfants qui n'atteignent pas le CM2" sous="ordre de grandeur" valeur={fr(r.enfants_hors_cm2)}
          droite={`${rangFr(rang(R, (x) => x.enfants_hors_cm2, r, "haut"))}/13`}
          bande={<Bande13 valeurs={R.map((x) => x.enfants_hors_cm2)} choisie={r.enfants_hors_cm2} min={0} max={maxHors * 1.04} label="Enfants hors CM2 des 13 régions" />} />
        <Repere titre="Élèves au primaire" sous={`${signe(evol(r))}${fr(Math.abs(evol(r)), 1)} % sur un an`} valeur={fr(r.eleves.at(-1))}
          droite={`${rangFr(rang(R, evol, r, "bas"))}/13`}
          bande={<Bande13 valeurs={R.map(evol)} choisie={evol(r)} reference={0} min={-mEvol * 1.1} max={mEvol * 1.1} label="Évolution des effectifs des 13 régions sur un an" />} />
        <Repere titre="Écart filles − garçons" sous={`achèvement · filles ${pct(r.tap_f.at(-1))}, garçons ${pct(r.tap_g.at(-1))}`}
          valeur={`${signe(ecart(r))}${fr(Math.abs(ecart(r)), 1)} pt`} droite=""
          bande={<Bande13 valeurs={R.map(ecart)} choisie={ecart(r)} reference={0} min={-mEcart * 1.1} max={mEcart * 1.1} label="Écart filles moins garçons des 13 régions" />} />
      </section>

      <section className="sec">
        <h2>Violence, signal de l'alerte<span className="num">{lectureInc}</span></h2>
        <Colonnes valeurs={r.incidents} annees={jeu.annees_violence} lu={luInc} onLire={setLuInc} label={`Incidents de sécurité par année scolaire, ${r.nom}`} />
        <p className="lecture">Incidents de sécurité d'octobre à septembre (ACLED) : {fr(inc(r))} en 2025/26, {signe(inc(r) - r.incidents.at(-2))}{fr(Math.abs(inc(r) - r.incidents.at(-2)))} sur un an,
          {" "}{rangFr(rang(R, inc, r, "haut"))} sur 13. C'est la violence qui fait l'alerte.</p>
      </section>

      <section className="sec">
        <h2>Ce qui pèse en fond<span>exposition parmi les 13</span></h2>
        {jeu.facteurs_def.map((def) => {
          const f = r.facteurs[def.id];
          if (!f || f.valeur === null) return null;
          const vals = R.map((x) => x.facteurs[def.id]?.valeur).filter((v) => v !== null && v !== undefined);
          const unite = def.id === "violence" ? " par an" : def.id === "grossesses" ? " ‰" : " %";
          return (
            <Repere key={def.id} titre={def.libelle} sous={SOUS_FACTEUR[def.id] ?? def.unite}
              valeur={`${fr(f.valeur, def.id === "violence" || def.id === "grossesses" ? 0 : 1)}${unite}`} droite={EXPOSITION[f.niveau]}
              bande={<Bande13 valeurs={vals} choisie={f.valeur} min={Math.min(0, ...vals)} max={Math.max(...vals) * 1.04} label={`${def.libelle} des 13 régions`} />} />
          );
        })}
        <p className="lecture">Forte : parmi les 4 régions les plus exposées. Pour le CEP et le préscolaire, une valeur basse expose davantage. Ces facteurs expliquent les écarts ; ils n'améliorent pas la prévision.</p>
      </section>

      <section className="sec">
        <h2>Constats</h2>
        <ol className="liste-num">{r.faits.map((f, i) => <li key={i}>{f}</li>)}</ol>
      </section>

      <section className="sec">
        <h2>Leviers</h2>
        <ol className="liste-num">{r.leviers.concat(r.leviers_facteurs).map((f, i) => <li key={i}>{f}</li>)}</ol>
      </section>

      <p className="lecture sources">
        Sources : DGESS (données du Data Challenge Burkina 2026) ; ACLED, Cadre Harmonisé, EDS, CONASUR via HDX ; INSD (EHCVM 2021). Aucune donnée personnelle.
        {" "}<button className="lien" onClick={onMethode}>Méthode et limites</button>
      </p>
    </div>
  );
}

"use client";
// Map of the 13 former regions, coloured by priority (ordinal blue ramp). SVG paths come from the
// export (projected there), so the map needs no tiles and works without network.
import { useRef, useState } from "react";
import { fr, pct, PRIORITES } from "@/lib/format";
import useLargeur from "./useLargeur";

// Label nudges in map units, for the small central regions whose labels would collide.
const DECALAGE = { CENTRE: [0, 2], PLATEAUCENTRAL: [16, 18], CENTRESUD: [0, 10], CENTREOUEST: [-14, 0], CENTREEST: [10, 8], SAHEL: [-6, 14] };

function lignes(nom) {
  return nom.split(" + ").flatMap((p, i, a) => (i < a.length - 1 ? [`${p} +`] : [p]));
}

export default function Carte({ jeu, mesure = "priorite" }) {
  const conteneur = useRef(null);
  const [survol, setSurvol] = useState(null);
  const { largeur, hauteur, regions: formes } = jeu.carte;
  const rendu = useLargeur(conteneur);
  const taille = Math.min(20, Math.max(12, (12.5 * (largeur + 12)) / rendu));
  const petit = { CENTRE: 0.85, PLATEAUCENTRAL: 0.85 };

  function montrer(region, evt) {
    const boite = conteneur.current.getBoundingClientRect();
    const cible = evt.currentTarget.getBoundingClientRect();
    const x = evt.clientX ? evt.clientX - boite.left : cible.left + cible.width / 2 - boite.left;
    const y = evt.clientY ? evt.clientY - boite.top : cible.top + cible.height / 2 - boite.top;
    setSurvol({ region, x, y });
  }

  return (
    <div className="viz" ref={conteneur}>
      <svg viewBox={`-6 -6 ${largeur + 12} ${hauteur + 12}`} role="img"
        aria-label="Carte des 13 régions colorées par priorité ; le détail est dans la liste sous la carte.">
        {jeu.regions.map((r) => {
          const f = formes[r.cle];
          return (
            <a key={r.cle} href={`/region/${r.cle}`} className="cible" aria-label={`${r.nom} : ${PRIORITES[r.priorite].libelle}`}
              onPointerMove={(e) => montrer(r, e)} onPointerLeave={() => setSurvol(null)}
              onFocus={(e) => montrer(r, e)} onBlur={() => setSurvol(null)}>
              <path d={f.d} fill={`var(--prio-${r.priorite})`} stroke={survol?.region.cle === r.cle ? "var(--ink)" : "var(--surface)"}
                strokeWidth={survol?.region.cle === r.cle ? 3 : 2} strokeLinejoin="round" />
            </a>
          );
        })}
        {jeu.regions.map((r) => {
          const f = formes[r.cle];
          const [dx, dy] = DECALAGE[r.cle] ?? [0, 0];
          const l = lignes(r.nom);
          const t = taille * (petit[r.cle] ?? 1);
          return (
            <text key={r.cle} x={f.lx + dx} y={f.ly + dy - ((l.length - 1) * t) / 2} textAnchor="middle" pointerEvents="none"
              style={{ fill: `var(--prio-${r.priorite}-txt)`, fontSize: t, fontWeight: 600 }}>
              {l.map((s, i) => <tspan key={i} x={f.lx + dx} dy={i ? t * 1.1 : 0}>{s}</tspan>)}
            </text>
          );
        })}
      </svg>
      {survol && (
        <div className="infobulle" style={{ left: survol.x, top: survol.y }}>
          <div><strong>{survol.region.nom}</strong> <span className="discret">({survol.region.ancienne})</span></div>
          <div className="ib-ligne">{PRIORITES[survol.region.priorite].libelle} : {PRIORITES[survol.region.priorite].sous}</div>
          <div className="ib-ligne">Taux d'achèvement 2024/25 : <b>{pct(survol.region.tap.at(-1), 1)}</b></div>
          <div className="ib-ligne">Probabilité de baisse 2026/27 : <b>{pct(survol.region.probabilites.ref_2026_27)}</b></div>
          <div className="ib-ligne">Enfants hors CM2 : <b>{fr(survol.region.enfants_hors_cm2)}</b></div>
        </div>
      )}
      <div className="legende" aria-hidden="true">
        {[1, 2, 3].map((p) => (
          <span key={p}><i className="cle-carre" style={{ background: `var(--prio-${p})` }} />{PRIORITES[p].libelle} : {PRIORITES[p].sous}</span>
        ))}
      </div>
    </div>
  );
}

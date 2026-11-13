"use client";
// Priority matrix: completion rate 2024/25 (x) against the probability of a drop in pupils in
// 2026/27 (y, reference model D12). Dots coloured by priority; each dot has a 24 px hit area.
import { useRef, useState } from "react";
import { fr, pct, PRIORITES } from "@/lib/format";
import useLargeur from "./useLargeur";

const M = { g: 44, d: 12, h: 14, b: 44 };
// Label offsets (px, anchor) set by hand so that close dots do not collide.
const ETIQ = {
  SAHEL: [0, 18, "middle"], EST: [-4, -12, "middle"], CENTRENORD: [8, -10, "start"], BOUCLEDUMOUHOUN: [0, 18, "middle"],
  NORD: [0, -12, "middle"], CENTREEST: [10, 4, "start"], CASCADES: [-10, 4, "end"], HAUTSBASSINS: [10, 4, "start"],
  SUDOUEST: [6, -10, "start"], PLATEAUCENTRAL: [-10, 4, "end"], CENTRESUD: [0, -12, "middle"], CENTREOUEST: [10, 10, "start"],
  CENTRE: [0, -12, "middle"],
};

export default function Matrice({ jeu }) {
  const conteneur = useRef(null);
  const [survol, setSurvol] = useState(null);
  const L = useLargeur(conteneur);
  const H = Math.round(Math.min(440, Math.max(320, L * 0.66)));
  const s = jeu.seuils;
  const x = (v) => M.g + (v / 100) * (L - M.g - M.d);
  const y = (v) => H - M.b - (v / 100) * (H - M.h - M.b);
  const pos = (e) => {
    const b = conteneur.current.getBoundingClientRect(), t = e.currentTarget.getBoundingClientRect();
    return { x: t.left + t.width / 2 - b.left, y: t.top - b.top };
  };
  return (
    <div className="viz" ref={conteneur}>
      <svg viewBox={`0 0 ${L} ${H}`} role="img" aria-label="Matrice de priorité ; les valeurs sont dans le tableau.">
        {[0, 20, 40, 60, 80, 100].map((v) => (
          <g key={v}>
            <line x1={M.g} x2={L - M.d} y1={y(v)} y2={y(v)} stroke="var(--grid)" />
            <text x={M.g - 8} y={y(v) + 4} textAnchor="end">{v}</text>
            <text x={x(v)} y={H - M.b + 18} textAnchor="middle">{v}</text>
          </g>
        ))}
        <line x1={x(s.tap_national)} x2={x(s.tap_national)} y1={y(0)} y2={y(100)} stroke="var(--axis)" strokeDasharray="5 4" strokeWidth="1.5" />
        <text x={x(s.tap_national) + 6} y={y(100) + 12}>Moyenne nationale ({fr(s.tap_national, 1)} %)</text>
        <line x1={M.g} x2={L - M.d} y1={y(s.risque_eleve)} y2={y(s.risque_eleve)} stroke="var(--axis)" strokeDasharray="5 4" strokeWidth="1.5" />
        <text x={L - M.d} y={y(s.risque_eleve) - 6} textAnchor="end">Risque élevé (≥ {s.risque_eleve} %)</text>
        <line x1={M.g} x2={L - M.d} y1={y(s.risque_moyen)} y2={y(s.risque_moyen)} stroke="var(--axis)" strokeDasharray="2 4" />
        <text x={L - M.d} y={y(s.risque_moyen) - 6} textAnchor="end">Risque moyen (≥ {s.risque_moyen} %)</text>
        <text x={(M.g + L - M.d) / 2} y={H - 6} textAnchor="middle">Taux d'achèvement 2024/25 (%) : à gauche, plus de retard</text>
        <text transform={`translate(14 ${(M.h + H - M.b) / 2}) rotate(-90)`} textAnchor="middle">Probabilité de baisse 2026/27 (%)</text>
        {jeu.regions.map((r) => {
          const cx = x(r.tap.at(-1)), cy = y(r.probabilites.ref_2026_27);
          const [dx, dy, ancre] = ETIQ[r.cle] ?? [10, 4, "start"];
          const actif = survol?.region.cle === r.cle;
          return (
            <a key={r.cle} href={`/region/${r.cle}`} className="cible" aria-label={`${r.nom}, ${PRIORITES[r.priorite].libelle}`}
              onPointerEnter={(e) => setSurvol({ region: r, ...pos(e) })} onPointerLeave={() => setSurvol(null)}
              onFocus={(e) => setSurvol({ region: r, ...pos(e) })} onBlur={() => setSurvol(null)}>
              <circle cx={cx} cy={cy} r="14" fill="transparent" />
              <circle cx={cx} cy={cy} r={actif ? 8 : 6.5} fill={`var(--prio-${r.priorite})`} stroke="var(--surface)" strokeWidth="2" />
              <text x={cx + dx} y={cy + dy} textAnchor={ancre} style={{ fill: "var(--ink)", fontSize: 12 }}>{r.nom}</text>
            </a>
          );
        })}
      </svg>
      {survol && (
        <div className="infobulle" style={{ left: survol.x, top: survol.y }}>
          <div><strong>{survol.region.nom}</strong></div>
          <div className="ib-ligne">{PRIORITES[survol.region.priorite].libelle} : {PRIORITES[survol.region.priorite].sous}</div>
          <div className="ib-ligne">Taux d'achèvement : <b>{pct(survol.region.tap.at(-1), 1)}</b></div>
          <div className="ib-ligne">Probabilité de baisse : <b>{pct(survol.region.probabilites.ref_2026_27)}</b></div>
        </div>
      )}
      <div className="legende" aria-hidden="true">
        {[1, 2, 3].map((p) => (
          <span key={p}><i className="cle-carre" style={{ background: `var(--prio-${p})`, borderRadius: "50%" }} />{PRIORITES[p].libelle} : {PRIORITES[p].sous}</span>
        ))}
      </div>
    </div>
  );
}

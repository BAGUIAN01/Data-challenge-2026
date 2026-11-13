"use client";
// Completion rate of a region against the national rate, 2015/16-2024/25, with the cautious
// forecast for 2025/26 (range measured on past errors). Crosshair: hover or focus a year.
import { useRef, useState } from "react";
import { pct } from "@/lib/format";
import useLargeur from "./useLargeur";

const M = { g: 34, d: 14, h: 12, b: 28 };

export default function CourbeTap({ jeu, region }) {
  const conteneur = useRef(null);
  const [i, setI] = useState(null);
  const L = useLargeur(conteneur);
  const H = Math.round(Math.min(300, Math.max(200, L * 0.5)));
  const tous = L >= 520;
  const annees = [...jeu.annees, "25/26"];
  const n = annees.length;
  const x = (k) => M.g + (k / (n - 1)) * (L - M.g - M.d);
  const y = (v) => H - M.b - (v / 100) * (H - M.h - M.b);
  const chemin = (vals) => vals.map((v, k) => `${k ? "L" : "M"}${x(k).toFixed(1)},${y(v).toFixed(1)}`).join("");
  const p = region.prevision_2025_26;
  const dernier = n - 2;
  const bande = `M${x(dernier)},${y(region.tap.at(-1))}L${x(n - 1)},${y(p.haute)}L${x(n - 1)},${y(p.basse)}Z`;
  const largeurPas = (L - M.g - M.d) / (n - 1);
  return (
    <div className="viz" ref={conteneur} onPointerLeave={() => setI(null)}>
      <div className="legende">
        <span><i className="cle-ligne" style={{ borderColor: "var(--serie-1)" }} />{region.nom}</span>
        <span><i className="cle-ligne tirets" style={{ borderColor: "var(--nat)" }} />Burkina Faso</span>
        <span><i className="cle-carre" style={{ background: "var(--bande)" }} />Prévision 2025/26 et sa fourchette</span>
      </div>
      <svg viewBox={`0 0 ${L} ${H}`} role="img" aria-label={`Taux d'achèvement de ${region.nom} de 2015/16 à 2024/25, comparé au national.`}>
        {[0, 25, 50, 75, 100].map((v) => (
          <g key={v}>
            <line x1={M.g} x2={L - M.d} y1={y(v)} y2={y(v)} stroke="var(--grid)" />
            <text x={M.g - 6} y={y(v) + 4} textAnchor="end">{v}</text>
          </g>
        ))}
        {annees.map((a, k) => (tous || k % 2 === 0 || k === n - 1) && <text key={a} x={x(k)} y={H - 8} textAnchor="middle">{a}</text>)}
        <path d={bande} fill="var(--bande)" />
        <path d={`M${x(dernier)},${y(region.tap.at(-1))}L${x(n - 1)},${y(p.centrale)}`} stroke="var(--serie-1)" strokeWidth="2" strokeDasharray="4 4" fill="none" />
        <path d={chemin(jeu.national.tap)} stroke="var(--nat)" strokeWidth="2" strokeDasharray="6 4" fill="none" />
        <path d={chemin(region.tap)} stroke="var(--serie-1)" strokeWidth="2" fill="none" />
        {region.tap.map((v, k) => <circle key={k} cx={x(k)} cy={y(v)} r="4" fill="var(--serie-1)" stroke="var(--surface)" strokeWidth="2" />)}
        <text x={x(dernier)} y={y(Math.max(region.tap.at(-1), p.haute)) - 10} textAnchor="middle" style={{ fill: "var(--ink)", fontWeight: 600 }}>{pct(region.tap.at(-1), 1)}</text>
        {i !== null && <line x1={x(i)} x2={x(i)} y1={y(100)} y2={y(0)} stroke="var(--axis)" />}
        {annees.map((a, k) => (
          <rect key={a} x={x(k) - largeurPas / 2} y={M.h} width={largeurPas} height={H - M.h - M.b} fill="transparent"
            tabIndex={0} className="cible" aria-label={`Année ${a}`} onPointerEnter={() => setI(k)} onFocus={() => setI(k)} onBlur={() => setI(null)} />
        ))}
      </svg>
      {i !== null && (
        <div className="infobulle" style={{ left: `${(x(i) / L) * 100}%`, top: `${(M.h / H) * 100 + 8}%`, transform: "translate(-50%, 0)" }}>
          <div><strong>{annees[i]}</strong></div>
          {i < n - 1 ? (
            <>
              <div className="ib-ligne"><i className="cle-ligne" style={{ borderColor: "var(--serie-1)" }} /><b>{pct(region.tap[i], 1)}</b> {region.nom}</div>
              <div className="ib-ligne"><i className="cle-ligne tirets" style={{ borderColor: "var(--nat)" }} /><b>{pct(jeu.national.tap[i], 1)}</b> national</div>
            </>
          ) : (
            <div className="ib-ligne">Prévision : <b>{pct(p.centrale, 1)}</b> (de {pct(p.basse, 1)} à {pct(p.haute, 1)})</div>
          )}
        </div>
      )}
    </div>
  );
}

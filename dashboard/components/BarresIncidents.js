"use client";
// Security incidents per school year (ACLED, October to September). One bar per year; hover or
// focus a bar for its value; the largest and the last year are labelled directly.
import { useRef, useState } from "react";
import { fr } from "@/lib/format";
import useLargeur from "./useLargeur";

const M = { g: 36, d: 6, h: 18, b: 28 };

function barre(x, y, l, h) {
  const r = Math.min(4, h, l / 2);
  return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + l - r}Q${x + l},${y} ${x + l},${y + r}V${y + h}Z`;
}

export default function BarresIncidents({ jeu, region }) {
  const conteneur = useRef(null);
  const [i, setI] = useState(null);
  const L = useLargeur(conteneur);
  const H = Math.round(Math.min(220, Math.max(170, L * 0.36)));
  const tous = L >= 560;
  const vals = region.incidents;
  const max = Math.max(10, ...vals.filter((v) => v !== null));
  const pas = Math.ceil(max / 4 / 10) * 10 || 10;
  const haut = pas * 4;
  const n = vals.length;
  const larg = (L - M.g - M.d) / n;
  const y = (v) => H - M.b - (v / haut) * (H - M.h - M.b);
  const kmax = vals.indexOf(Math.max(...vals));
  return (
    <div className="viz" ref={conteneur}>
      <svg viewBox={`0 0 ${L} ${H}`} role="img" aria-label={`Incidents sécuritaires par année scolaire, ${region.nom}.`}>
        {[0, 1, 2, 3, 4].map((k) => (
          <g key={k}>
            <line x1={M.g} x2={L - M.d} y1={y(k * pas)} y2={y(k * pas)} stroke="var(--grid)" />
            <text x={M.g - 6} y={y(k * pas) + 4} textAnchor="end">{fr(k * pas)}</text>
          </g>
        ))}
        {vals.map((v, k) => {
          const x0 = M.g + k * larg + 1, l = larg - 2, h = v ? (H - M.b) - y(v) : 0;
          return (
            <g key={k}>
              {h > 0 && <path d={barre(x0, y(v), l, h)} fill="var(--serie-2)" opacity={i === null || i === k ? 1 : 0.55} />}
              {(k === kmax || k === n - 1) && v !== null && <text x={x0 + l / 2} y={y(v) - 5} textAnchor="middle" style={{ fill: "var(--ink)" }}>{fr(v)}</text>}
              {(tous || k % 2 === 0 || k === n - 1) && <text x={x0 + l / 2} y={H - 8} textAnchor="middle">{jeu.annees_violence[k]}</text>}
              <rect x={x0 - 1} y={M.h} width={larg} height={H - M.h - M.b} fill="transparent" tabIndex={0} className="cible"
                aria-label={`${jeu.annees_violence[k]} : ${v ?? "inconnu"} incidents`}
                onPointerEnter={() => setI(k)} onPointerLeave={() => setI(null)} onFocus={() => setI(k)} onBlur={() => setI(null)} />
            </g>
          );
        })}
      </svg>
      {i !== null && (
        <div className="infobulle" style={{ left: `${((M.g + (i + 0.5) * larg) / L) * 100}%`, top: `${(y(vals[i] ?? 0) / H) * 100}%` }}>
          <div className="ib-ligne"><b>{fr(vals[i])}</b> incidents</div>
          <div className="ib-ligne">oct. 20{jeu.annees_violence[i].slice(0, 2)} à sept. 20{jeu.annees_violence[i].slice(3)}</div>
        </div>
      )}
    </div>
  );
}

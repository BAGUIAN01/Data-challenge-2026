"use client";
// Small charts, drawn at the real width of their card (one SVG unit = one pixel). A finger on a chart
// reads a value: the card shows it in its header (onLire), there is no floating tooltip.
import { useRef } from "react";
import useLargeur from "../useLargeur";
import { fr } from "@/lib/format";

// Scrub: nearest index under the pointer; released, the reading goes back to the default.
function useLecture(n, x, onLire) {
  const actif = useRef(false);
  const lire = (e) => {
    const g = e.currentTarget.getBoundingClientRect().left, px = e.clientX - g;
    let best = 0;
    for (let i = 1; i < n; i++) if (Math.abs(x(i) - px) < Math.abs(x(best) - px)) best = i;
    onLire?.(best);
  };
  return {
    onPointerDown: (e) => { actif.current = true; lire(e); },
    onPointerMove: (e) => { if (actif.current || e.pointerType === "mouse") lire(e); },
    onPointerUp: () => { actif.current = false; onLire?.(null); },
    onPointerLeave: () => { actif.current = false; onLire?.(null); },
    onPointerCancel: () => { actif.current = false; onLire?.(null); },
  };
}

// Line chart. series: [{ v: [...], c: css colour }], the LAST series is the main one.
// y0/y1: fixed scale (percentages); otherwise fitted to the data. prev: {centrale, basse, haute}
// drawn one step after the last year. bas: label the lowest point of the main series.
export function Courbe({ annees, series, y0, y1, fmt, prev, bas, lu, onLire, label, jusqua = null }) {
  const ref = useRef(null);
  const W = useLargeur(ref, 300);
  const H = 128, pr = 50, pt = 8, pb = 20, last = annees.length - 1, n = annees.length + (prev ? 1 : 0);
  const vals = series.flatMap((s) => s.v).concat(prev ? [prev.basse, prev.haute] : []);
  let lo = y0 ?? Math.min(...vals), hi = y1 ?? Math.max(...vals);
  if (y0 === undefined) { const m = (hi - lo) * 0.15; lo -= m * (bas ? 3 : 1); hi += m; }
  const x = (i) => (i * (W - pr)) / (n - 1), y = (v) => pt + (1 - (v - lo) / (hi - lo)) * (H - pt - pb);
  const chemin = (vs) => vs.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join("");
  const principale = series.at(-1).v;
  // jusqua: the year reached by the opening animation; the lines are drawn up to it.
  const k = jusqua === null ? last : Math.min(jusqua, last), fini = k === last;
  const fins = series.map((s) => ({ y: y(s.v[k]), t: fmt(s.v[k]), fort: s === series.at(-1) }));
  if (fins.length === 2 && Math.abs(fins[0].y - fins[1].y) < 16) {
    const m = (fins[0].y + fins[1].y) / 2, s = fins[1].y >= fins[0].y ? 1 : -1;
    fins[1].y = m + 8 * s; fins[0].y = m - 8 * s;
  }
  const xe = fini ? (prev ? x(n - 1) : x(last)) : x(k);
  const iMin = bas && fini ? principale.indexOf(Math.min(...principale)) : -1;
  const lecture = useLecture(n, x, onLire);
  return (
    <div className="chart" ref={ref}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
        {y0 !== undefined
          ? [0, 50, 100].map((g) => <line key={g} className="gl" x1="0" x2={W - pr} y1={y(g)} y2={y(g)} />)
          : <line className="gl" x1="0" x2={W - pr} y1={H - pb} y2={H - pb} />}
        {prev && fini && (
          <>
            <rect x={x(n - 1) - 7} y={y(prev.haute)} width="14" height={y(prev.basse) - y(prev.haute)} rx="7" fill="var(--band2)" />
            <line x1={x(last)} y1={y(principale[last])} x2={x(n - 1)} y2={y(prev.centrale)} stroke="var(--fg)" strokeWidth="1.5" strokeDasharray="3 3" />
            <circle cx={x(n - 1)} cy={y(prev.centrale)} r="3.5" fill="var(--card)" stroke="var(--fg)" strokeWidth="1.5" />
          </>
        )}
        {series.map((s, i) => <path key={i} className="ln" stroke={s.c} d={chemin(s.v.slice(0, k + 1))} />)}
        <circle cx={x(k)} cy={y(principale[k])} r="3.5" fill="var(--fg)" />
        {iMin >= 0 && iMin !== last && (
          <>
            <circle cx={x(iMin)} cy={y(principale[iMin])} r="3" fill="var(--fg)" />
            <text className="ax" x={x(iMin)} y={y(principale[iMin]) + 16} textAnchor="middle">{fmt(principale[iMin])} en {annees[iMin]}</text>
          </>
        )}
        {fins.map((f, i) => <text key={i} className="el" x={xe + 10} y={f.y + 4} style={{ fill: f.fort ? "var(--fg)" : "var(--fg-3)" }}>{f.t}</text>)}
        <text className="ax" x="0" y={H - 3}>{annees[0]}</text>
        <text className="ax" x={x(last)} y={H - 3} textAnchor={prev ? "middle" : "end"}>{annees[last]}</text>
        {prev && <text className="ax" x={x(n - 1) + 4} y={H - 3}>25/26</text>}
        {lu !== null && lu !== undefined && <line className="sl" x1={x(lu)} x2={x(lu)} y1={pt} y2={H - pb} />}
        <rect x="-8" y="0" width={W - pr + 16} height={H} fill="transparent" {...lecture} />
      </svg>
    </div>
  );
}

// Column chart (incidents per school year); the last year is the dark column.
export function Colonnes({ valeurs, annees, lu, onLire, label, jusqua = null }) {
  const ref = useRef(null);
  const W = useLargeur(ref, 300);
  const H = 118, pb = 20, pt = 18, n = valeurs.length, max = Math.max(...valeurs, 1), gap = 2, bw = (W - gap * (n - 1)) / n;
  const h = (v) => ((H - pt - pb) * v) / max, cx = (i) => i * (bw + gap) + bw / 2;
  const k = jusqua === null ? n - 1 : Math.min(jusqua, n - 1), vus = valeurs.slice(0, k + 1), im = vus.indexOf(Math.max(...vus));
  const lecture = useLecture(n, cx, onLire);
  return (
    <div className="chart" ref={ref}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
        {vus.map((v, i) => {
          const hh = Math.max(1.5, h(v)), X = i * (bw + gap), r = Math.min(3, hh, bw / 2);
          return <path key={i} d={`M${X} ${H - pb}V${H - pb - hh + r}q0 ${-r} ${r} ${-r}h${bw - 2 * r}q${r} 0 ${r} ${r}V${H - pb}z`}
            fill={i === k ? "var(--fg)" : "var(--z3)"} />;
        })}
        <line className="gl" x1="0" x2={W} y1={H - pb} y2={H - pb} />
        {im !== k && <text className="ax" x={cx(im)} y={H - pb - h(vus[im]) - 5} textAnchor="middle">{fr(vus[im])}</text>}
        <text className="el" x={cx(k)} y={H - pb - h(valeurs[k]) - 5} textAnchor="middle" style={{ fill: "var(--fg)" }}>{fr(valeurs[k])}</text>
        <text className="ax" x="0" y={H - 3}>{annees[0]}</text>
        <text className="ax" x={W} y={H - 3} textAnchor="end">{annees[n - 1]}</text>
        {lu !== null && lu !== undefined && <line className="sl" x1={cx(lu)} x2={cx(lu)} y1={pt} y2={H - pb} />}
        <rect x="0" y="0" width={W} height={H} fill="transparent" {...lecture} />
      </svg>
    </div>
  );
}

// Zones of the risk scale, as flex parts of 0-100.
export function zonesRisque(seuils) {
  return [[0, seuils.risque_moyen, "faible", "var(--z1)"], [seuils.risque_moyen, seuils.risque_eleve, "moyen", "var(--z2)"], [seuils.risque_eleve, 100, "élevé", "var(--z3)"]];
}

// Probability on its scale; p2 (optional) is a second reading shown as a ring.
export function Echelle({ p, p2, seuils, actif, label, zones }) {
  const z = zones ?? zonesRisque(seuils);
  return (
    <div className="scale" role="img" aria-label={label}>
      <div className="zs">{z.map(([a, b, , c]) => <i key={a} style={{ flex: b - a, background: c }} />)}</div>
      {p2 !== undefined && p2 !== p && <i className="mk2" style={{ left: `${p2}%` }} />}
      {p !== undefined && <i className="mk" style={{ left: `${p}%` }} />}
      <div className="zl">{z.map(([a, b, l]) => <span key={a} style={{ flex: `${b - a} 0 0` }} className={actif === l ? "on" : ""}>{l}</span>)}</div>
    </div>
  );
}

// The 13 regions on one strip: dots stacked upward when they would touch.
export function Bande({ points, seuils, zones, lu, onLire, onOuvrir }) {
  const ref = useRef(null);
  const W = useLargeur(ref, 300);
  const d = 13;
  const pts = points.map((p) => ({ ...p, x: (p.v / 100) * W })).sort((a, b) => a.x - b.x);
  const places = [];
  for (const p of pts) { let k = 0; while (places.some((q) => q.k === k && Math.abs(q.x - p.x) < d)) k++; p.k = k; places.push(p); }
  const H = (Math.max(0, ...pts.map((p) => p.k)) + 1) * d + 2;
  const proche = (e) => { const x = e.clientX - ref.current.getBoundingClientRect().left; return pts.reduce((b, p) => (Math.abs(p.x - x) < Math.abs(b.x - x) ? p : b)); };
  const depart = useRef(null);
  return (
    <div className="swarm"
      onPointerDown={(e) => { depart.current = e.clientX; onLire(proche(e).id); }}
      onPointerMove={(e) => { if (depart.current !== null || e.pointerType === "mouse") onLire(proche(e).id); }}
      onPointerUp={(e) => { if (depart.current !== null && Math.abs(e.clientX - depart.current) < 8) onOuvrir(proche(e).id); depart.current = null; }}
      onPointerLeave={() => { depart.current = null; onLire(null); }}>
      <div className="dots" ref={ref} style={{ height: H }}>
        {pts.map((p) => <i key={p.id} className={lu === p.id ? "on" : ""} style={{ left: p.x, top: H - 12 - p.k * d, "--c": p.c }} title={p.nom} />)}
      </div>
      <Echelle seuils={seuils} zones={zones} />
    </div>
  );
}

// Forecast with its measured range, and the reference value placed on the same strip.
export function Fourchette({ c, lo, hi, reference: valRef, refLabel }) {
  const a0 = Math.min(lo, valRef), a1 = Math.max(hi, valRef), pad = (a1 - a0) * 0.08, A = a0 - pad, B = a1 + pad;
  const X = (v) => `${(((v - A) / (B - A)) * 100).toFixed(2)}%`, fin = (valRef - A) / (B - A) > 0.5;
  return (
    <div className="range" role="img" aria-label={`Fourchette de ${fr(lo)} à ${fr(hi)} ; ${refLabel}`}>
      <i className="tr" />
      <i className="bd" style={{ left: X(lo), width: `calc(${X(hi)} - ${X(lo)})` }} />
      <i className="ly" style={{ left: X(valRef) }} />
      <i className="pt" style={{ left: X(c) }} />
      <span className="lb lo num" style={{ left: X(lo) }}>{fr(lo)}</span>
      <span className="lb hi num" style={{ left: X(hi) }}>{fr(hi)}</span>
      <span className={`lb lyl num${fin ? " end" : ""}`} style={{ left: X(valRef) }}>{refLabel}</span>
    </div>
  );
}

// Stacked bar of parts (counts), 2 px gaps.
export function Pile({ parts, label }) {
  return (
    <div className="stack" role="img" aria-label={label}>
      {parts.map((p, i) => <i key={i} style={{ "--c": p.c, flex: p.n }} />)}
    </div>
  );
}

// Priority matrix: completion rate (x) against the probability of a drop (y). The top-left
// quarter is priority 1. A finger reads the nearest region.
export function Matrice({ regions, seuils, couleur, lu, onLire, onOuvrir }) {
  const ref = useRef(null);
  const W = useLargeur(ref, 300);
  const H = Math.round(Math.min(300, Math.max(220, W * 0.72))), g = 30, b = 26, t = 8, dr = 8;
  const x = (v) => g + (v / 100) * (W - g - dr), y = (v) => t + (1 - v / 100) * (H - t - b);
  const pts = regions.map((r) => ({ id: r.cle, nom: r.nom, X: x(r.tap.at(-1)), Y: y(r.probabilites.ref_2026_27), c: couleur(r) }));
  const proche = (e) => {
    const bb = ref.current.getBoundingClientRect(), px = e.clientX - bb.left, py = e.clientY - bb.top;
    return pts.reduce((m, p) => (Math.hypot(p.X - px, p.Y - py) < Math.hypot(m.X - px, m.Y - py) ? p : m));
  };
  const depart = useRef(null);
  return (
    <div className="chart" ref={ref}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Matrice de priorité : achèvement et risque de chaque région"
        onPointerDown={(e) => { depart.current = [e.clientX, e.clientY]; onLire(proche(e).id); }}
        onPointerMove={(e) => { if (depart.current || e.pointerType === "mouse") onLire(proche(e).id); }}
        onPointerUp={(e) => { if (depart.current && Math.hypot(e.clientX - depart.current[0], e.clientY - depart.current[1]) < 8) onOuvrir(proche(e).id); depart.current = null; }}
        onPointerLeave={() => { depart.current = null; onLire(null); }}>
        <rect x={g} y={t} width={x(seuils.tap_national) - g} height={y(seuils.risque_eleve) - t} fill="var(--band)" rx="4" />
        {[0, 50, 100].map((v) => (
          <g key={v}>
            <line className="gl" x1={g} x2={W - dr} y1={y(v)} y2={y(v)} />
            <text className="ax" x={g - 6} y={y(v) + 4} textAnchor="end">{v}</text>
            <text className="ax" x={x(v)} y={H - 6} textAnchor={v === 0 ? "start" : v === 100 ? "end" : "middle"}>{v} %</text>
          </g>
        ))}
        <line x1={x(seuils.tap_national)} x2={x(seuils.tap_national)} y1={t} y2={H - b} stroke="var(--fg-3)" strokeDasharray="4 4" />
        <line x1={g} x2={W - dr} y1={y(seuils.risque_eleve)} y2={y(seuils.risque_eleve)} stroke="var(--fg-3)" strokeDasharray="4 4" />
        <text className="ax" x={g + 6} y={t + 14}>priorité 1</text>
        {pts.map((p) => (
          <circle key={p.id} cx={p.X} cy={p.Y} r={lu === p.id ? 8 : 6} fill={p.c} stroke={lu === p.id ? "var(--fg)" : "var(--card)"} strokeWidth="2" />
        ))}
      </svg>
    </div>
  );
}

// Score year by year, ending on the forecast. Past points were each computed with their own year's
// information only; the last one is the forecast (dashed segment, open dot, its value written).
// Tiers 25 and 50 are faint bands; a dark ring marks a year when pupils did drop by more than 5 %.
export function Trajectoire({ annees, score, chute, lu, onLire, label, jusqua = null }) {
  const ref = useRef(null);
  const W = useLargeur(ref, 300);
  const H = 150, pr = 44, pt = 14, pb = 20, n = annees.length, last = n - 1;
  const x = (i) => 6 + (i * (W - pr - 6)) / (n - 1), y = (v) => pt + (1 - v / 100) * (H - pt - pb);
  const k = jusqua === null ? last : Math.min(jusqua, last);
  const lecture = useLecture(n, x, onLire);
  if (k < 0) return <div className="chart" ref={ref}><svg width={W} height={H} role="img" aria-label={label} /></div>;
  const passe = score.slice(0, Math.min(k, last - 1) + 1);
  const d = passe.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join("");
  const prevu = k === last;
  return (
    <div className="chart" ref={ref}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
        <rect x="0" y={y(100)} width={W - pr} height={y(50) - y(100)} fill="var(--z3)" opacity=".45" />
        <rect x="0" y={y(50)} width={W - pr} height={y(25) - y(50)} fill="var(--z2)" opacity=".45" />
        <text className="ax" x={W - pr + 6} y={y(50) + 4}>50</text>
        <text className="ax" x={W - pr + 6} y={y(25) + 4}>25</text>
        <line className="gl" x1="0" x2={W - pr} y1={y(0)} y2={y(0)} />
        <path className="ln" stroke="var(--fg)" d={d} />
        {passe.map((v, i) => (chute[i] === 1
          ? <circle key={i} cx={x(i)} cy={y(v)} r="5.5" fill="var(--card)" stroke="var(--bad-txt)" strokeWidth="2" />
          : <circle key={i} cx={x(i)} cy={y(v)} r="2.5" fill="var(--fg)" />))}
        {prevu && (
          <g className="prevu">
            <line x1={x(last - 1)} y1={y(score[last - 1])} x2={x(last)} y2={y(score[last])} stroke="var(--fg)" strokeWidth="2" strokeDasharray="4 4" />
            <circle className="pouls" cx={x(last)} cy={y(score[last])} r="9" fill="var(--c1)" opacity=".18" />
            <circle cx={x(last)} cy={y(score[last])} r="5" fill="var(--card)" stroke="var(--fg)" strokeWidth="2" />
            <text className="el" x={x(last)} y={y(score[last]) - 12} textAnchor="middle" style={{ fill: "var(--fg)" }}>{score[last]}</text>
          </g>
        )}
        {!prevu && <text className="el" x={x(k) + 8} y={y(score[k]) + 4} style={{ fill: "var(--fg)" }}>{score[k]}</text>}
        <text className="ax" x={x(0)} y={H - 3} textAnchor="start">{annees[0]}</text>
        <text className="ax" x={x(last)} y={H - 3} textAnchor="middle" style={{ fontWeight: 600, fill: "var(--fg)" }}>{annees[last]} prévu</text>
        {lu !== null && lu !== undefined && <line className="sl" x1={x(lu)} x2={x(lu)} y1={pt} y2={H - pb} />}
        <rect x="-8" y="0" width={W - pr + 16} height={H} fill="transparent" {...lecture} />
      </svg>
    </div>
  );
}

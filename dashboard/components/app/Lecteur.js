"use client";
// Year player of the map: one card with a play button, the year in large type and a track that
// ends on the forecast. Playing moves the map continuously (values interpolated between years,
// a short rest on each year); a finger on the track scrubs, and lets go on the nearest year.
// The map is driven through its api (no re-render of the app on each frame).
import { useCallback, useEffect, useRef, useState } from "react";

const PAR_ANNEE = 1100; // ms per year while playing
const doux = (u) => u * u * (3 - 2 * u); // slows near each year: the eye can read it

export default function Lecteur({ traj, carte }) {
  const annees = traj.annees, n = annees.length, fin = n - 1;
  const [t, setT] = useState(fin), [joue, setJoue] = useState(false);
  const tRef = useRef(fin), raf = useRef(0), piste = useRef(null), glisse = useRef(false);
  const reduit = () => typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Score of a region at a position t (0 .. n-1), interpolated between two years.
  const valeur = useCallback((tt) => (r) => {
    const s = traj.par_region[r.cle]?.score;
    if (!s) return null;
    const i = Math.min(Math.floor(tt), fin), u = tt - i;
    return i >= fin ? s[fin] : s[i] + (s[i + 1] - s[i]) * u;
  }, [traj, fin]);

  const poser = useCallback((tt) => {
    if (!Number.isFinite(tt)) return;
    tRef.current = tt; setT(tt);
    carte.current?.fixer(tt >= fin ? null : valeur(tt)); // at the forecast the map is back on its own data
  }, [carte, valeur, fin]);

  const arreter = useCallback(() => { cancelAnimationFrame(raf.current); setJoue(false); }, []);
  const jouer = useCallback(() => {
    cancelAnimationFrame(raf.current);
    setJoue(true);
    const p0 = tRef.current >= fin ? 0 : tRef.current, t0 = performance.now();
    const pas = (now) => {
      const p = Math.min(fin, p0 + (now - t0) / PAR_ANNEE);
      const i = Math.floor(p);
      poser(p >= fin ? fin : reduit() ? i : i + doux(p - i));
      if (p < fin) raf.current = requestAnimationFrame(pas); else setJoue(false);
    };
    raf.current = requestAnimationFrame(pas);
  }, [fin, poser]);

  // Glide to a year (after a tap or when the finger lets go).
  const aller = useCallback((cible) => {
    cancelAnimationFrame(raf.current);
    const de = tRef.current, t0 = performance.now(), ms = reduit() ? 0 : 350;
    const pas = (now) => {
      const u = ms ? Math.min(1, (now - t0) / ms) : 1;
      poser(de + (cible - de) * doux(u));
      if (u < 1) raf.current = requestAnimationFrame(pas);
    };
    raf.current = requestAnimationFrame(pas);
  }, [poser]);

  const position = (e) => {
    const b = piste.current.getBoundingClientRect();
    if (!b.width) return tRef.current;
    return Math.max(0, Math.min(fin, ((e.clientX - b.left) / b.width) * fin));
  };
  const surDown = (e) => { arreter(); glisse.current = true; e.currentTarget.setPointerCapture?.(e.pointerId); poser(position(e)); };
  const surMove = (e) => { if (glisse.current) poser(position(e)); };
  const surUp = () => { if (!glisse.current) return; glisse.current = false; aller(Math.round(tRef.current)); };
  const surTouche = (e) => {
    const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
    if (!d) return;
    e.preventDefault(); arreter(); aller(Math.max(0, Math.min(fin, Math.round(tRef.current) + d)));
  };

  // First visit of the session: play once, so the forecast is seen arriving.
  useEffect(() => {
    let deja = false;
    try { deja = sessionStorage.getItem("annees-vues") === "1"; sessionStorage.setItem("annees-vues", "1"); } catch { /* private mode */ }
    if (deja || reduit()) return undefined;
    const h = setTimeout(jouer, 1500);
    return () => clearTimeout(h);
  }, [jouer]);
  useEffect(() => () => cancelAnimationFrame(raf.current), []);

  const iAff = Math.round(t), prevu = iAff === fin, pc = (x) => `${(x / fin) * 100}%`;
  return (
    <div className={`lecteur${prevu ? " est-prevu" : ""}${joue ? " joue" : ""}`}>
      <button className="lect-jouer" onClick={joue ? arreter : jouer} aria-label={joue ? "Mettre en pause" : "Animer les années"} title={joue ? "Pause" : "Animer les années"}>
        {joue ? <svg viewBox="0 0 14 14" aria-hidden="true"><rect x="3" y="2" width="3" height="10" rx="1" /><rect x="8" y="2" width="3" height="10" rx="1" /></svg>
          : <svg viewBox="0 0 14 14" aria-hidden="true"><path d="M4 2.2v9.6a.6.6 0 0 0 .9.5l7.6-4.8a.6.6 0 0 0 0-1L4.9 1.7a.6.6 0 0 0-.9.5z" /></svg>}
      </button>
      <span className="lect-an num" aria-live="polite">{annees[iAff]}{prevu && <em>prévu</em>}</span>
      <div className="lect-piste" ref={piste} role="slider" tabIndex={0} aria-label="Année affichée sur la carte"
        aria-valuemin={0} aria-valuemax={fin} aria-valuenow={iAff} aria-valuetext={`${annees[iAff]}${prevu ? ", prévision" : ""}`}
        onPointerDown={surDown} onPointerMove={surMove} onPointerUp={surUp} onPointerCancel={surUp} onKeyDown={surTouche}>
        <div className="lect-rail"><i className="lect-passe" style={{ width: pc(Math.min(t, fin - 1)) }} /><i className="lect-futur" style={{ left: pc(fin - 1) }} /></div>
        {annees.map((a, i) => (
          <button key={a} className={`lect-cran${i <= t + 0.01 ? " vu" : ""}${i === fin ? " fin" : ""}`} style={{ left: pc(i) }} tabIndex={-1}
            aria-label={a} onPointerDown={(e) => e.stopPropagation()} onClick={() => { arreter(); aller(i); }} />
        ))}
        <i className="lect-bouton" style={{ left: pc(t) }} />
      </div>
    </div>
  );
}

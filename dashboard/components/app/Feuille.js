"use client";
// Bottom sheet over the map, on a phone: three resting heights, dragged with the finger like the
// phone's own maps. While it is not fully open, a drag anywhere on it moves the sheet; fully open,
// its content scrolls, and pulling down from the top closes it again. On a large screen the sheet
// is a plain side panel (CSS) and none of this applies.
import { useEffect, useRef, useState } from "react";

export const CRANS = ["bas", "mi", "haut"];
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const grandEcran = () => matchMedia("(min-width: 900px)").matches;

export function hauteurCran(c, H) {
  return c === "bas" ? 214 : c === "mi" ? Math.round(H * 0.58) : H - 8;
}

export default function Feuille({ cran, setCran, tete, children, defilement }) {
  const ref = useRef(null), dedans = useRef(null);
  const [H, setH] = useState(700);
  const geste = useRef(null), vientDeTirer = useRef(false);

  useEffect(() => {
    const parent = ref.current.parentElement;
    const ro = new ResizeObserver(() => setH(parent.clientHeight || 700));
    ro.observe(parent);
    return () => ro.disconnect();
  }, []);
  useEffect(() => { if (cran !== "haut" && dedans.current) dedans.current.scrollTop = 0; }, [cran]);
  useEffect(() => { if (defilement && dedans.current) dedans.current.scrollTop = 0; }, [defilement]);

  useEffect(() => {
    const f = ref.current, d = dedans.current;
    const debut = (y, cible) => {
      if (grandEcran()) return;
      geste.current = { y0: y, y, h0: f.getBoundingClientRect().height, t: performance.now(), v: 0, mode: null,
        tete: Boolean(cible.closest(".sh-head")), graphe: Boolean(cible.closest(".chart, .swarm")) };
    };
    const bouge = (y, ev) => {
      const g = geste.current;
      if (!g) return;
      const dy = y - g.y0;
      if (!g.mode) {
        if (Math.abs(dy) < 6) return;
        const cran = f.dataset.cran;
        g.mode = g.tete || cran !== "haut" || (dy > 0 && d.scrollTop <= 0) ? "tirer" : "defiler";
        if (g.mode === "tirer") f.style.transition = "none";
      }
      if (g.mode !== "tirer") return;
      if (ev?.cancelable) ev.preventDefault();
      const now = performance.now();
      g.v = (y - g.y) / Math.max(1, now - g.t); g.y = y; g.t = now;
      f.style.height = `${clamp(g.h0 - dy, 150, hauteurCran("haut", f.parentElement.clientHeight))}px`;
    };
    const fin = () => {
      const g = geste.current;
      geste.current = null;
      if (!g || g.mode !== "tirer") return;
      f.style.transition = "";
      vientDeTirer.current = true;
      setTimeout(() => { vientDeTirer.current = false; }, 60);
      const Hp = f.parentElement.clientHeight, h = f.getBoundingClientRect().height, i = CRANS.indexOf(f.dataset.cran);
      const c = Math.abs(g.v) > 0.45 ? CRANS[clamp(i + (g.v < 0 ? 1 : -1), 0, 2)]
        : CRANS.reduce((b, k) => (Math.abs(hauteurCran(k, Hp) - h) < Math.abs(hauteurCran(b, Hp) - h) ? k : b), "bas");
      f.style.height = "";
      setCran(c);
    };
    const tStart = (e) => debut(e.touches[0].clientY, e.target);
    const tMove = (e) => bouge(e.touches[0].clientY, e);
    const pDown = (e) => { if (e.pointerType === "mouse" && !e.target.closest(".chart, .swarm, input, select")) debut(e.clientY, e.target); };
    const pMove = (e) => { if (e.pointerType === "mouse") bouge(e.clientY, null); };
    const pUp = (e) => { if (e.pointerType === "mouse") fin(); };
    const clic = (e) => { if (vientDeTirer.current) { e.stopPropagation(); e.preventDefault(); } };
    const roue = (e) => {
      if (grandEcran() || f.dataset.cran === "haut" || e.deltaY <= 0) return;
      e.preventDefault();
      setCran(CRANS[CRANS.indexOf(f.dataset.cran) + 1]);
    };
    f.addEventListener("touchstart", tStart, { passive: true });
    f.addEventListener("touchmove", tMove, { passive: false });
    f.addEventListener("touchend", fin);
    f.addEventListener("touchcancel", fin);
    f.addEventListener("pointerdown", pDown);
    window.addEventListener("pointermove", pMove);
    window.addEventListener("pointerup", pUp);
    f.addEventListener("click", clic, true);
    f.addEventListener("wheel", roue, { passive: false });
    return () => {
      f.removeEventListener("touchstart", tStart);
      f.removeEventListener("touchmove", tMove);
      f.removeEventListener("touchend", fin);
      f.removeEventListener("touchcancel", fin);
      f.removeEventListener("pointerdown", pDown);
      window.removeEventListener("pointermove", pMove);
      window.removeEventListener("pointerup", pUp);
      f.removeEventListener("click", clic, true);
      f.removeEventListener("wheel", roue);
    };
  }, [setCran]);

  const basculer = (e) => { if (!e.target.closest("button") && !grandEcran()) setCran(cran === "bas" ? "mi" : "bas"); };
  return (
    <div className="sheet" ref={ref} data-cran={cran} style={{ height: hauteurCran(cran, H) }}>
      <div className="sh-head" onClick={basculer}><i className="grab" /><div className="sh-row">{tete}</div></div>
      <div className="sh-in" ref={dedans}>{children}</div>
    </div>
  );
}

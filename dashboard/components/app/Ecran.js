"use client";
// One screen of the app: navigation bar (back button named after the previous screen), large title
// that folds into the bar on scroll, content, optional bottom action bar. A pushed screen slides in
// from the right and can be closed by swiping from the left edge, like the phone's own apps.
import { useEffect, useRef, useState } from "react";
import { Retour } from "./icones";

export default function Ecran({ titre, retour, onRetour, onGlisseRetour, pousse = false, sortant = false, couvert = false, barre, children, id, className = "" }) {
  const ref = useRef(null);
  const [dedans, setDedans] = useState(!pousse);
  const [solide, setSolide] = useState(false);

  useEffect(() => {
    if (!pousse) return;
    let r2 = 0;
    const r1 = requestAnimationFrame(() => { r2 = requestAnimationFrame(() => setDedans(true)); });
    return () => { cancelAnimationFrame(r1); cancelAnimationFrame(r2); };
  }, [pousse]);

  // Swipe from the left edge. The screen underneath follows the finger.
  useEffect(() => {
    if (!pousse) return;
    const s = ref.current;
    let g = null;
    const dessous = () => {
      let p = s.previousElementSibling;
      while (p && !p.classList.contains("screen")) p = p.previousElementSibling;
      return p;
    };
    const down = (e) => {
      const r = s.getBoundingClientRect();
      if (e.clientX - r.left > 26 || !s.classList.contains("in") || e.button > 0) return;
      g = { x: e.clientX, t: performance.now(), w: r.width, dx: 0, id: e.pointerId, sous: dessous() };
      s.setPointerCapture(e.pointerId);
    };
    const move = (e) => {
      if (!g || e.pointerId !== g.id) return;
      g.dx = Math.max(0, e.clientX - g.x);
      s.style.transition = "none"; s.style.transform = `translateX(${g.dx}px)`;
      if (g.sous) { g.sous.style.transition = "none"; g.sous.style.transform = `translateX(${-28 + (g.dx / g.w) * 28}%)`; }
    };
    const up = () => {
      if (!g) return;
      const v = g.dx / Math.max(1, performance.now() - g.t), part = g.dx > g.w * 0.35 || (v > 0.45 && g.dx > 40);
      const sous = g.sous;
      g = null;
      // Inline styles win over the classes until React has re-rendered: no jump back mid-way.
      s.style.transition = "";
      s.style.transform = part ? "translateX(100%)" : "";
      if (sous) {
        sous.style.transition = "";
        sous.style.transform = part ? "none" : "";
        if (part) setTimeout(() => { sous.style.transform = ""; }, 480);
      }
      if (part) onGlisseRetour?.();
    };
    s.addEventListener("pointerdown", down);
    s.addEventListener("pointermove", move);
    s.addEventListener("pointerup", up);
    s.addEventListener("pointercancel", up);
    return () => {
      s.removeEventListener("pointerdown", down);
      s.removeEventListener("pointermove", move);
      s.removeEventListener("pointerup", up);
      s.removeEventListener("pointercancel", up);
    };
  }, [pousse, onGlisseRetour]);

  const classes = ["screen", pousse && "pushed", pousse && dedans && !sortant && "in", couvert && "covered", barre && "has-bar", className].filter(Boolean).join(" ");
  return (
    <div className={classes} ref={ref} data-ecran={id} aria-hidden={couvert || sortant || undefined}>
      <header className={`nb${solide ? " solid" : ""}`}>
        {retour ? <button className="nb-back" onClick={onRetour}><Retour /><span>{retour}</span></button> : <span />}
        <span className="nb-t">{titre}</span><span />
      </header>
      <div className="sc" onScroll={(e) => setSolide(e.currentTarget.scrollTop > 36)}>
        <h1 className="lt">{titre}</h1>
        {children}
      </div>
      {barre && <div className="bar">{barre}</div>}
    </div>
  );
}

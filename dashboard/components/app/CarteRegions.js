"use client";
// Map of the 13 regions (paths projected by the export: no tiles, works without network).
// Gestures of a phone map: one finger pans, two fingers pinch, a double tap zooms in, the wheel
// zooms under the pointer. Labels that would touch are hidden until the user zooms in.
// The map is drawn imperatively (a pan redraws every frame); React only passes the layer, the
// selected region and framing commands.
import { useEffect, useRef } from "react";

const NS = "http://www.w3.org/2000/svg";
// Label nudges in map units, for the small central regions (same as the former map).
const DECALAGE = { CENTRE: [0, 2], PLATEAUCENTRAL: [16, 18], CENTRESUD: [0, 10], CENTREOUEST: [-14, 0], CENTREEST: [10, 8], SAHEL: [10, -30] };
const lignesNom = (nom) => nom.split(" + ").flatMap((p, i, a) => (i < a.length - 1 ? [`${p} +`] : [p]));
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  parent?.appendChild(e);
  return e;
}

export default function CarteRegions({ jeu, classe, valeur, selection, onChoisir, commande, marges, barres = null, apiExterne = null }) {
  const svgRef = useRef(null);
  const etat = useRef({ classe, valeur, selection, onChoisir, marges });
  etat.current.classe = classe;
  etat.current.valeur = valeur;
  etat.current.barres = barres;
  etat.current.selection = selection;
  etat.current.onChoisir = onChoisir;
  etat.current.marges = marges;
  const api = useRef(null);

  useEffect(() => {
    const svg = svgRef.current, { largeur: L, hauteur: Hc, regions: GEO } = jeu.carte;
    const R = jeu.regions, s = etat.current;
    svg.innerHTML = "";
    const gReg = el("g", {}, svg), gSel = el("g", { "pointer-events": "none" }, svg), gLab = el("g", { "pointer-events": "none" }, svg), gBar = el("g", { "pointer-events": "none" }, svg);
    // Bar heights move from what is shown to the new values (growth from 0 at first, then year to year).
    let depart = {}, arrivee = {}, avance = 1, pousseAnim = 0;
    // fixe: values set from outside frame by frame (the year player); they win over the tween.
    let fixe = null;
    const classeDe = (r) => { if (!fixe) return s.classe(r); const v = fixe(r); return v >= 50 ? 1 : v >= 25 ? 2 : 3; };
    const montre = (r) => { if (fixe) { const v = fixe(r); return Number.isFinite(v) ? v : 0; } const b = arrivee[r.cle] ?? s.barres(r) ?? 0, a = depart[r.cle] ?? b; return a + (b - a) * avance; };
    let vb = { x: 0, y: 0, w: L, h: Hc }, glisse = false, anim = 0;
    for (const r of R) {
      const p = el("path", { d: GEO[r.cle].d, "stroke-linejoin": "round", "data-cle": r.cle, tabindex: 0, role: "button", "aria-label": `${r.nom} : ouvrir l'aperçu` }, gReg);
      p.addEventListener("click", () => { if (!glisse) s.onChoisir(r.cle); });
      p.addEventListener("keydown", (e) => { if (e.key === "Enter") s.onChoisir(r.cle); });
    }
    const boites = {};
    for (const p of gReg.children) { const b = p.getBBox(); boites[p.dataset.cle] = [b.x, b.y, b.width, b.height]; }
    const ordre = [...R].sort((a, b) => boites[b.cle][2] * boites[b.cle][3] - boites[a.cle][2] * boites[a.cle][3]);

    function render() {
      const W = svg.clientWidth;
      if (!W) return;
      svg.setAttribute("viewBox", `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
      const k = vb.w / W, sel = s.selection;
      const enBarres = Boolean(s.barres);
      for (const p of gReg.children) {
        p.style.fill = `var(--c${classeDe(R.find((r) => r.cle === p.dataset.cle))})`;
        p.setAttribute("stroke", "var(--land)");
        p.setAttribute("stroke-width", 1.5 * k);
      }
      gSel.innerHTML = "";
      if (sel) el("path", { d: GEO[sel].d, fill: "none", stroke: "var(--fg)", "stroke-width": 2.5 * k, "stroke-linejoin": "round" }, gSel);
      gLab.innerHTML = ""; gBar.innerHTML = "";
      if (enBarres) {
        // One bar per region, standing on its label point; height = the value (0-100), front bars last.
        const etiquettes = [];
        const w = (W < 600 ? 12 : 16) * k, Hm = (W < 600 ? 56 : 110) * k; // shorter on a phone, under the controls
        for (const r of [...R].sort((a, b) => GEO[a.cle].ly - GEO[b.cle].ly)) {
          const f = GEO[r.cle], [dx, dy] = DECALAGE[r.cle] ?? [0, 0], v = Math.round(montre(r)), h = Math.max(2 * k, (montre(r) / 100) * Hm);
          const x0 = f.lx + dx, y0 = f.ly + dy;
          el("ellipse", { cx: x0, cy: y0, rx: w * 0.75, ry: w * 0.28, fill: "rgba(0,0,0,.25)" }, gBar);
          el("rect", { x: x0 - w / 2, y: y0 - h, width: w, height: h, rx: w * 0.25, fill: `var(--c${classeDe(r)})`, stroke: "#fff", "stroke-width": 2 * k }, gBar);
          if (montre(r) > 1) etiquettes.push({ x: x0, y: y0 - h - 6 * k, v, cle: r.cle });
        }
        // Values are drawn last, over every bar: the selected region first, then the tallest bars;
        // a value that would overlap one already placed is left out (its bar still shows it).
        const fs = 12 * k, pris = [];
        etiquettes.sort((a, b) => (b.cle === sel) - (a.cle === sel) || b.v - a.v);
        for (const e of etiquettes) {
          const txt = `${e.v} %`, lw = txt.length * fs * 0.6, bx = [e.x - lw / 2 - 2 * k, e.y - fs, e.x + lw / 2 + 2 * k, e.y + 2 * k];
          if (pris.some((q) => bx[0] < q[2] && bx[2] > q[0] && bx[1] < q[3] && bx[3] > q[1])) continue;
          pris.push(bx);
          const tx = el("text", { x: e.x, y: e.y, "text-anchor": "middle" }, gBar);
          tx.style.cssText = `font-size:${fs}px;fill:var(--fg);stroke:#fff;stroke-width:${3.5 * k}px`;
          tx.textContent = txt;
        }
        // Region names, as on the colour map, written just under the foot of each bar. The full-height
        // bars and their values are reserved first; a name that would cross one of them, or another
        // name, is left out (biggest regions first, the selected one always).
        const tn = (W < 600 ? 13 : 14) * k, mn = 2 * k, pris2 = [];
        for (const r of R) {
          const f = GEO[r.cle], [dx, dy] = DECALAGE[r.cle] ?? [0, 0], v = s.barres(r) ?? 0, hp = Math.max(2 * k, (v / 100) * Hm);
          pris2.push([f.lx + dx - w / 2, f.ly + dy - hp - 6 * k - fs, f.lx + dx + w / 2, f.ly + dy]);
        }
        for (const r of [...ordre].sort((a, b) => (b.cle === sel) - (a.cle === sel))) {
          const f = GEO[r.cle], [dx, dy] = DECALAGE[r.cle] ?? [0, 0], l = lignesNom(r.nom);
          const tx = el("text", { x: f.lx + dx, y: f.ly + dy + w * 0.35 + tn, "text-anchor": "middle", "data-etiquette": r.cle }, gLab);
          // Dark text on a white halo: readable on every class colour, light or dark.
          tx.style.cssText = `font-size:${tn}px;font-weight:700;fill:var(--fg);stroke:var(--card);stroke-width:${3.5 * k}px;stroke-linejoin:round;paint-order:stroke`;
          l.forEach((x, i) => { const ts = el("tspan", { x: f.lx + dx, dy: i ? tn * 1.12 : 0 }, tx); ts.textContent = x; });
          const bb = tx.getBBox(), q = [bb.x - mn, bb.y - mn, bb.x + bb.width + mn, bb.y + bb.height + mn];
          if (r.cle !== sel && pris2.some((p) => q[0] < p[2] && q[2] > p[0] && q[1] < p[3] && q[3] > p[1])) tx.remove(); else pris2.push(q);
        }
        return;
      }
      const t = 12 * k, m = 3 * k, places = [];
      for (const r of [...ordre].sort((a, b) => (b.cle === sel) - (a.cle === sel))) {
        const f = GEO[r.cle], [dx, dy] = DECALAGE[r.cle] ?? [0, 0], v = s.valeur?.(r), l = v ? [...lignesNom(r.nom), v] : lignesNom(r.nom), c = s.classe(r);
        const taille = t * (["CENTRE", "PLATEAUCENTRAL"].includes(r.cle) ? 0.88 : 1);
        const tx = el("text", { x: f.lx + dx, y: f.ly + dy - ((l.length - 1) * taille) / 2, "text-anchor": "middle", "data-etiquette": r.cle }, gLab);
        tx.style.cssText = `font-size:${taille}px;fill:var(--c${c}-t);stroke:var(--c${c});stroke-width:${2.5 * k}px`;
        l.forEach((x, i) => {
          const ts = el("tspan", { x: f.lx + dx, dy: i ? taille * 1.15 : 0 }, tx); ts.textContent = x;
          if (v && i === l.length - 1) ts.setAttribute("style", "font-weight:700"); // the value, under the name
        });
        const boite = () => { const bb = tx.getBBox(); return [bb.x - m, bb.y - m, bb.x + bb.width + m, bb.y + bb.height + m]; };
        const touche = (q) => places.some((p) => q[0] < p[2] && q[2] > p[0] && q[1] < p[3] && q[3] > p[1]);
        let q = boite();
        if (touche(q) && v) {
          // No room for the name: keep the value alone, centred on the region.
          tx.textContent = ""; tx.setAttribute("y", f.ly + dy);
          const ts = el("tspan", { x: f.lx + dx }, tx); ts.textContent = v; ts.setAttribute("style", "font-weight:700");
          q = boite();
        }
        if (touche(q)) tx.remove(); else places.push(q);
      }
    }
    // Viewbox that fits a box in the visible part of the map (between the controls and the sheet).
    function cible(box, marge = 1.06) {
      const W = svg.clientWidth, H = svg.clientHeight, { haut, bas } = s.marges(), visH = Math.max(120, H - haut - bas);
      const [x, y, w, h] = box, z = Math.max(w / (W - 12), h / visH) * marge, cx = x + w / 2, cy = y + h / 2;
      // Pinned under the controls when there is height to spare (a phone is limited by its width):
      // the free space goes to the bottom, the map sits close to the bars' headroom.
      const hPx = h / z, centre = haut + Math.min(visH, hPx) / 2;
      return { x: cx - (W / 2) * z, y: cy - centre * z, w: W * z, h: H * z };
    }
    function aller(to, ms = 420) {
      cancelAnimationFrame(anim);
      if (matchMedia("(prefers-reduced-motion: reduce)").matches) { vb = { ...to }; render(); return; }
      const from = { ...vb }, t0 = performance.now();
      const pas = (t) => {
        const u = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - u, 3);
        for (const kk of ["x", "y", "w", "h"]) vb[kk] = from[kk] + (to[kk] - from[kk]) * e;
        render();
        if (u < 1) anim = requestAnimationFrame(pas);
      };
      anim = requestAnimationFrame(pas);
    }
    function zoomer(cx, cy, f) {
      const B = svg.getBoundingClientRect(), k = vb.w / B.width, px = vb.x + (cx - B.left) * k, py = vb.y + (cy - B.top) * k;
      const w = clamp(vb.w * f, L * 0.12, L * 1.8), k2 = w / B.width;
      return { x: px - (cx - B.left) * k2, y: py - (cy - B.top) * k2, w, h: (w * B.height) / B.width };
    }

    // Gestures.
    const doigts = new Map();
    let geste = null, dernierTap = { t: 0, x: 0, y: 0 };
    const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y), milieu = (a, b) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 });
    const surDown = (e) => {
      doigts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      cancelAnimationFrame(anim);
      if (doigts.size === 1) {
        const now = performance.now();
        if (now - dernierTap.t < 300 && Math.hypot(e.clientX - dernierTap.x, e.clientY - dernierTap.y) < 30) {
          aller(zoomer(e.clientX, e.clientY, 0.5), 300); dernierTap.t = 0; glisse = true; geste = null; return;
        }
        dernierTap = { t: now, x: e.clientX, y: e.clientY };
        geste = { type: "pan", x: e.clientX, y: e.clientY, vb: { ...vb } }; glisse = false;
      } else if (doigts.size === 2) {
        const [a, b] = [...doigts.values()];
        geste = { type: "pinch", d0: dist(a, b), m0: milieu(a, b), vb: { ...vb } }; glisse = true;
      }
    };
    const surMove = (e) => {
      if (!doigts.has(e.pointerId)) return;
      doigts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      const B = svg.getBoundingClientRect();
      if (geste?.type === "pan") {
        const dx = e.clientX - geste.x, dy = e.clientY - geste.y;
        if (Math.hypot(dx, dy) > 6) glisse = true;
        if (!glisse) return;
        const k = geste.vb.w / B.width;
        vb.x = geste.vb.x - dx * k; vb.y = geste.vb.y - dy * k; render();
      } else if (geste?.type === "pinch" && doigts.size >= 2) {
        const [a, b] = [...doigts.values()], m = milieu(a, b);
        const w = clamp((geste.vb.w * geste.d0) / Math.max(10, dist(a, b)), L * 0.12, L * 1.8);
        const k0 = geste.vb.w / B.width, k = w / B.width, px = geste.vb.x + (geste.m0.x - B.left) * k0, py = geste.vb.y + (geste.m0.y - B.top) * k0;
        vb = { x: px - (m.x - B.left) * k, y: py - (m.y - B.top) * k, w, h: (w * B.height) / B.width }; render();
      }
    };
    const surUp = (e) => {
      if (!doigts.delete(e.pointerId)) return;
      if (doigts.size === 1 && geste?.type === "pinch") { const [p] = [...doigts.values()]; geste = { type: "pan", x: p.x, y: p.y, vb: { ...vb } }; }
      else if (!doigts.size) { geste = null; setTimeout(() => { glisse = false; }, 0); }
    };
    const surRoue = (e) => { e.preventDefault(); vb = zoomer(e.clientX, e.clientY, e.deltaY > 0 ? 1.15 : 1 / 1.15); render(); };
    svg.addEventListener("pointerdown", surDown);
    window.addEventListener("pointermove", surMove);
    window.addEventListener("pointerup", surUp);
    window.addEventListener("pointercancel", surUp);
    svg.addEventListener("wheel", surRoue, { passive: false });
    const ro = new ResizeObserver(() => {
      const W = svg.clientWidth, H = svg.clientHeight;
      if (!W) return;
      const cy = vb.y + vb.h / 2; vb.h = (vb.w * H) / W; vb.y = cy - vb.h / 2; render();
    });
    ro.observe(svg);

    api.current = {
      render,
      pays: () => aller(cible([0, 0, L, Hc], 1.0)),
      region: (cle) => aller(cible(boites[cle], 1.6)),
      immediat: () => { vb = cible([0, 0, L, Hc], 1.0); render(); },
      // Bars move to the current values: from 0 the first time, from what is shown afterwards.
      fixer: (fn) => { fixe = fn; if (!fn) { depart = { ...arrivee }; avance = 1; } render(); },
      pousser: () => {
        const premier = !Object.keys(arrivee).length;
        depart = Object.fromEntries(R.map((r) => [r.cle, premier ? 0 : montre(r)]));
        arrivee = Object.fromEntries(R.map((r) => [r.cle, s.barres(r) ?? 0]));
        if (matchMedia("(prefers-reduced-motion: reduce)").matches) { avance = 1; render(); return; }
        const t0 = performance.now(), ms = premier ? 700 : 450;
        cancelAnimationFrame(pousseAnim);
        const pas = (t) => { const u = Math.min(1, (t - t0) / ms); avance = 1 - Math.pow(1 - u, 3); render(); if (u < 1) pousseAnim = requestAnimationFrame(pas); };
        avance = 0; pousseAnim = requestAnimationFrame(pas);
      },
    };
    if (apiExterne) apiExterne.current = api.current;
    requestAnimationFrame(() => api.current?.immediat());
    return () => {
      cancelAnimationFrame(anim);
      ro.disconnect();
      window.removeEventListener("pointermove", surMove);
      window.removeEventListener("pointerup", surUp);
      window.removeEventListener("pointercancel", surUp);
      svg.removeEventListener("pointerdown", surDown);
      svg.removeEventListener("wheel", surRoue);
      api.current = null;
    };
  }, [jeu]);

  useEffect(() => { api.current?.render(); }, [classe, valeur, selection]);
  useEffect(() => { if (barres) api.current?.pousser(); else api.current?.render(); }, [barres]);
  useEffect(() => {
    if (!commande?.n) return;
    if (commande.type === "region") api.current?.region(commande.cle);
    else api.current?.pays();
  }, [commande]);

  return <svg ref={svgRef} className="carte-svg" role="application" aria-label="Carte des 13 régions ; la liste des régions est dans l'onglet Régions" />;
}

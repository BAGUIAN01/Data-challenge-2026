// window.render(t): draws the frame at t seconds. Pure function of t, so any frame renders on its own. Version 2.
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const p = (t, a, d) => clamp((t - a) / d);
const out = (x) => 1 - Math.pow(1 - x, 4);
const inout = (x) => (x < 0.5 ? 8 * x ** 4 : 1 - Math.pow(-2 * x + 2, 4) / 2);
const back = (x) => { const c1 = 1.70158, c3 = c1 + 1; return x <= 0 ? 0 : x >= 1 ? 1 : 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a, b, q) => { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * q)).join(",")})`; };
const NAVY = "#13294B", SUN = "#FDCD2F", PAPER = "#F6F1E7", DEEP = "#1b3a66", EDGE = "#2c4f82";

function word(el, t, at, leave = 1e9, dy = 46) {
  if (el.parentElement.classList.contains("m")) {
    const h = el.offsetHeight * 1.1, q = out(p(t, at, 0.55)), r = inout(p(t, leave, 0.4));
    el.style.opacity = t < at ? 0 : 1;
    el.style.transform = `translateY(${(1 - q) * h - r * h}px)`;
    return;
  }
  const q = out(p(t, at, 0.45)), r = out(p(t, leave, 0.3));
  el.style.opacity = q * (1 - r);
  el.style.transform = `translateY(${(1 - q) * dy - r * 30}px)`;
}

// the camera over the map: scale, focus point, tilt; keyframes eased one into the next
const SX = (x) => STAGE.left + (x + 10) * SCALE, SY = (y) => STAGE.top + (y + 10) * SCALE;
const RP = (k) => { const r = REGIONS.find((r) => r.k === k); return [SX(r.lx), SY(r.ly)]; };
const MID = [640, 560], NE = [824, 451];
const KF = [
  [0, 1, ...NE, 0], [SC.off - 0.2, 1, ...NE, 0], [SC.off + 2.6, 1.24, ...NE, 0], [SC.titre - 0.01, 1.24, ...NE, 0],
  [SC.titre, 1, ...MID, 0], [SC.montre, 1, ...MID, 0], [SC.montre + 1.4, 1.02, ...MID, 16], [SC.bulles, 1.03, ...MID, 16],
  [SC.bulles + 2.8, 1.1, ...RP("CENTRENORD"), 14], [SC.previent, 1.1, ...RP("CENTRENORD"), 14],
  [SC.previent + 0.8, 1.05, ...RP("CENTRENORD"), 20], [SC.agir, 1.14, ...RP("CENTRENORD"), 20],
  [SC.agir + 0.6, 1.0, ...MID, 26], [SC.tags, 1.0, ...MID, 26],
  [SC.tags + 0.5, 1.07, ...RP("NORD"), 26], [SC.tags + 1.4, 1.07, ...RP("SAHEL"), 26], [SC.tags + 2.3, 1.07, ...RP("CENTRENORD"), 26],
  [SC.tags + 3.2, 1.04, 640, 640, 26], [SC.outil, 1.04, 640, 640, 26],
];
function camera(t) {
  let k = 0;
  while (k < KF.length - 1 && t >= KF[k + 1][0]) k++;
  const A = KF[k], B = KF[Math.min(k + 1, KF.length - 1)];
  const q = B[0] > A[0] ? inout(clamp((t - A[0]) / (B[0] - A[0]))) : 0;
  return A.slice(1).map((v, i) => v + (B[i + 1] - v) * q);
}
function slam(el, t, at, origin = "0% 60%") {
  const q = out(p(t, at, 0.28));
  el.style.opacity = q;
  el.style.transform = `scale(${1.7 - 0.7 * q})`;
  el.style.transformOrigin = origin;
}
function pop(el, t, at, base = "") {
  const q = back(p(t, at, 0.45));
  el.style.opacity = clamp(q * 1.6);
  el.style.transform = `${base} scale(${q})`;
}

const R = Object.fromEntries(REGIONS.map((r) => [r.k, r]));
const byLight = [...REGIONS].sort((a, b) => b.tapv - a.tapv).map((r) => r.k);
const byRisk = [...REGIONS].sort((a, b) => (b.hi - a.hi) || a.lx - b.lx).map((r) => r.k);
const byWest = [...REGIONS].sort((a, b) => a.lx - b.lx).map((r) => r.k);
const dots = $$(".dot").map((el) => ({ el, a: +el.dataset.a, o: +el.dataset.o }));
const bubs = $$(".bub");
const rings = $$(".ring");
const tags = $$(".tag");
const leads = $$(".lead").map((el) => ({ el, i: +el.dataset.i, x1: +el.getAttribute("x1"), y1: +el.getAttribute("y1"), x2: +el.getAttribute("x2"), y2: +el.getAttribute("y2") }));
const leadp = $$(".leadp");
rings.forEach((g) => g.querySelectorAll(":scope > circle").forEach((c) => { c.setAttribute("cx", g.dataset.x); c.setAttribute("cy", g.dataset.y); }));

// A region changes colour quickly (0.18 s) with a small bounce, so it never shows a muddy in-between for long.
function swap(k, t, at, from, to) {
  const q = p(t, at, 0.18);
  return { fill: q <= 0 ? from : q >= 1 ? to : mix(from, to, q), bump: 1 + 0.05 * Math.sin(Math.PI * p(t, at, 0.35)) };
}
function region(k, t) {
  const r = R[k];
  if (t < SC.titre) return { fill: DEEP, bump: 1, op: 1 };
  if (t < SC.previent) {
    // it shows: each region drops in with its own colour, lightest first
    const q = out(p(t, SC.montre + 0.2 + byLight.indexOf(k) * 0.11, 0.45));
    return { fill: r.tap, bump: 0.86 + 0.14 * back(p(t, SC.montre + 0.2 + byLight.indexOf(k) * 0.11, 0.45)), op: q };
  }
  if (t < SC.agir) return { ...swap(k, t, SC.previent + 0.25 + byRisk.indexOf(k) * 0.07, r.tap, r.risk), op: 1 };
  return { ...swap(k, t, SC.agir + 0.2 + byWest.indexOf(k) * 0.05, r.risk, r.p1 ? SUN : "#dfe6ef"), op: 1 };
}
function regionStroke(t) {
  if (t < SC.titre) return EDGE;
  if (t < SC.previent) return "#ffffff";
  if (t < SC.agir) return mix("#ffffff", EDGE, p(t, SC.previent, 0.5));
  return mix(EDGE, "#ffffff", p(t, SC.agir, 0.5));
}

function slide(el, t, inAt, outAt) {
  const show = t >= inAt && t < outAt;
  el.style.display = show ? "block" : "none";
  if (show) el.style.transform = `translateX(${(1 - out(p(t, inAt, 0.5))) * 1920}px)`;
  return show;
}
function iris(el, t, inAt, outAt) {
  const show = t >= inAt && t < outAt;
  el.style.display = show ? "block" : "none";
  if (show) el.style.clipPath = `circle(${out(p(t, inAt, 0.55)) * 1150}px at 50% 50%)`;
  return show;
}

window.render = function (t) {
  // ── background and the map stage
  let bg = NAVY;
  if (t >= SC.montre) bg = PAPER;
  if (t >= SC.previent) bg = mix(PAPER, NAVY, out(p(t, SC.previent, 0.5)));
  if (t >= SC.agir) bg = mix(NAVY, PAPER, out(p(t, SC.agir, 0.5)));
  $("#bg").style.background = bg;
  const map = $("#map");
  const qm = out(p(t, 0, 0.7));
  // opening: the camera closes in on the north and east while schools switch off, then lets go
  map.style.opacity = qm;
  const [cs, fx, fy, rx] = camera(t);
  const mc = $("#mapcam");
  mc.style.transformOrigin = `${fx}px ${fy}px`;
  mc.style.transform = `perspective(2400px) rotateX(${rx}deg) scale(${cs * (0.96 + 0.04 * qm)})`;
  // the solid base under the country: dark on the night scenes, warm on paper, built up as the regions arrive
  const night = t < SC.montre ? 1 : t < SC.previent ? 1 - out(p(t, SC.montre, 0.5)) : t < SC.agir ? out(p(t, SC.previent, 0.5)) : 1 - out(p(t, SC.agir, 0.5));
  const slab = mix("#c2b8a3", "#0a1830", night);
  $("#base").style.opacity = t < SC.titre ? 1 : t < SC.previent ? out(p(t, SC.montre + 0.2, 1.6)) : 1;
  $$(".slab").forEach((g) => g.setAttribute("fill", slab));
  const st = regionStroke(t);
  for (const r of REGIONS) {
    const el = document.getElementById("r-" + r.k), s = region(r.k, t);
    el.setAttribute("fill", s.fill); el.setAttribute("stroke", st);
    el.style.opacity = s.op; el.style.transform = `scale(${s.bump})`;
  }

  // schools: they light up, then the closed ones go out (an empty ring and a brief flash)
  $("#dots").style.display = t < SC.titre ? "" : "none";
  if (t < SC.titre) for (const d of dots) {
    let r = 3.2 * back(p(t, 0.4 + d.a * 1.8, 0.35)), fill = SUN, stroke = "none";
    if (d.o >= 0) {
      const at = SC.off + d.o * 2.2, q = p(t, at, 0.25);
      if (q > 0) {
        const flash = Math.sin(Math.PI * q);
        r = 3.2 + 3.5 * flash;
        fill = q < 1 ? mix("#ffffff", "#13294B", q) : "#13294B";
        stroke = mix("#ffffff", "#7f95b8", q);
      }
    }
    d.el.setAttribute("r", Math.max(0, r).toFixed(2));
    d.el.setAttribute("fill", fill);
    d.el.setAttribute("stroke", stroke);
    d.el.setAttribute("stroke-width", 1.3);
  }
  bubs.forEach((b, i) => {
    const q = back(p(t, SC.bulles + i * 0.25, 0.42)) * (1 - out(p(t, SC.previent, 0.3)));
    b.setAttribute("r", (+b.dataset.r * Math.max(0, q)).toFixed(2));
  });
  $$(".bl").forEach((g, i) => {
    const q = back(p(t, SC.bulles + 1.4 + i * 0.3, 0.4)) * (1 - out(p(t, SC.previent, 0.3)));
    g.setAttribute("opacity", clamp(q * 1.5)); g.style.transformBox = "fill-box"; g.style.transformOrigin = "center"; g.style.transform = `scale(${Math.max(0, q)})`;
  });
  $("#rings").style.display = t >= SC.previent && t < SC.agir + 0.4 ? "" : "none";
  $("#rings").style.opacity = 1 - out(p(t, SC.agir, 0.35));
  rings.forEach((g, i) => {
    const bq = back(p(t, SC.alertes + i * 0.2, 0.4));
    g.querySelector(".badge").setAttribute("transform", `translate(${g.dataset.x},${g.dataset.y}) scale(${bq})`);
    [...g.querySelectorAll(":scope > circle")].forEach((c, k) => {
      const s = t - (SC.alertes + 0.2) - k * 0.4;
      if (s < 0) { c.setAttribute("r", 0); return; }
      const ph = (s % 1.2) / 1.2;
      c.setAttribute("r", (18 + ph * 48).toFixed(1));
      c.setAttribute("opacity", ((1 - ph) * 0.9).toFixed(2));
    });
  });
  $$(".ex").forEach((g, j) => { g.style.opacity = t < SC.agir ? 0 : out(p(t, SC.lift + j * 0.2, 0.5)); });
  $$(".lift").forEach((el, j) => {
    const q = t < SC.agir ? 0 : out(p(t, SC.lift + j * 0.2, 0.5));
    el.style.opacity = q;
    el.setAttribute("transform", `translate(0,${-10 * q})`);
  });
  const tagOn = t >= SC.tags - 0.1 && t < SC.outil + 0.6;
  tags.forEach((el, i) => { el.style.display = tagOn ? "flex" : "none"; pop(el, t, SC.tags + i * 0.9); });
  leads.forEach((l) => {
    const q = out(p(t, SC.tags + l.i * 0.9 + 0.15, 0.45));
    l.el.style.display = tagOn ? "" : "none";
    l.el.setAttribute("x2", l.x1 + (l.x2 - l.x1) * q);
    l.el.setAttribute("y2", l.y1 + (l.y2 - l.y1) * q);
  });
  leadp.forEach((c) => { c.style.display = tagOn ? "" : "none"; c.setAttribute("r", 7 * back(p(t, SC.tags + c.dataset.i * 0.9 + 0.5, 0.3))); });

  // ── the words beside the map
  const w1 = $$("#t1 .w");
  $("#t1").style.display = t < SC.tard + 0.6 ? "" : "none";
  word(w1[0], t, 0.7); slam(w1[1], t, SC.off + 0.1); word(w1[2], t, SC.off + 1.1); word(w1[3], t, SC.off + 1.7);
  const w4 = $$("#t4 .w"), L4 = SC.previent;
  $("#t4").style.display = t >= SC.montre && t < SC.previent + 0.4 ? "" : "none";
  word(w4[0], t, SC.montre + 0.3, L4); word(w4[1], t, SC.montre + 0.5, L4); word(w4[2], t, SC.montre + 0.8, L4);
  word(w4[3], t, SC.montre + 1.6, L4); word(w4[4], t, SC.bulles + 0.4, L4);
  const w5 = $$("#t5 .w"), L5 = SC.agir;
  $("#t5").style.display = t >= SC.previent && t < SC.agir + 0.4 ? "" : "none";
  word(w5[0], t, SC.previent + 0.5, L5); word(w5[1], t, SC.previent + 0.8, L5); word(w5[2], t, SC.previent + 1.2, L5);
  word(w5[3], t, SC.sep, L5); word(w5[4], t, SC.jan, L5);
  const w6 = $$("#t6 .w");
  $("#t6").style.display = t >= SC.agir ? "" : "none";
  word(w6[0], t, SC.agir + 0.6); word(w6[1], t, SC.agir + 1.0); word(w6[2], t, SC.agir + 1.5);

  // ── too late: the calendar. No month is named for the report: "months later".
  if (slide($("#s2"), t, SC.tard, SC.titre + 0.6)) {
    word($("#s2a"), t, SC.tard + 0.4); word($("#s2b"), t, SC.rapport + 0.2);
    const cur = $("#pgcur"), qc = out(p(t, SC.tard + 0.3, 0.5));
    cur.style.opacity = qc;
    cur.style.transform = `translateY(${(1 - qc) * -80}px) rotate(${-2 * qc}deg)`;
    const nflip = MONTHS.length, dt = (SC.rapport - SC.flip) / nflip;
    const n = t < SC.flip ? 0 : Math.min(nflip, Math.floor((t - SC.flip) / dt) + 1);
    const pgm = $("#pgm");
    pgm.textContent = n === 0 ? "Septembre" : n === nflip ? "Des mois plus tard" : "";
    pgm.className = "pg-h" + (n === nflip ? " later" : "");
    $("#pgr").style.display = n === 0 ? "" : "none";
    const doc = $("#pgdoc");
    doc.style.display = n === nflip ? "flex" : "none";
    pop(doc, t, SC.rapport);
    const fly = $("#pgfly"), flying = t >= SC.flip && t < SC.rapport;
    fly.style.display = flying ? "" : "none";
    if (flying) {
      const k = Math.floor((t - SC.flip) / dt), lq = ((t - SC.flip) % dt) / dt;
      $("#pgflym").textContent = k === 0 ? "Septembre" : "";
      fly.style.transform = `rotate(-2deg) rotateX(${lq * 115}deg) translateY(${-lq * 40}px)`;
      fly.style.opacity = 1 - lq * 0.6;
    }
    const sq = out(p(t, SC.stamp, 0.2)), stamp = $("#stamp");
    stamp.style.opacity = sq;
    stamp.style.transform = `rotate(-14deg) scale(${2.4 - 1.4 * sq})`;
    const s = t - SC.stamp - 0.2, amp = s > 0 ? 18 * Math.exp(-s * 8) : 0;
    $("#s2").style.transform += ` translate(${amp * Math.sin(t * 95)}px, ${amp * Math.cos(t * 71)}px)`;
  }

  // ── title (opens like a door, leaves sliding left onto the map)
  const s3 = $("#s3");
  if (iris(s3, t, SC.titre, SC.montre + 0.5)) {
    if (t >= SC.montre) { s3.style.clipPath = "none"; s3.style.transform = `translateX(${-out(p(t, SC.montre, 0.5)) * 1920}px)`; }
    else s3.style.transform = "";
    pop($("#logo"), t, SC.titre + 0.3);
    const w3 = $$("#s3 .w");
    word(w3[0], t, SC.titre + 0.6); word(w3[1], t, SC.titre + 1.0); word(w3[2], t, SC.titre + 1.3);
  }

  // ── the tool: the camera closes in on the offline banner
  if (slide($("#s7"), t, SC.outil, SC.fin + 0.6)) {
    word($("#s7t"), t, SC.outil + 0.3);
    const ql = out(p(t, SC.outil + 0.2, 0.6));
    $("#lap").style.transform = `translateX(${(1 - ql) * -1300}px)`;
    $("#lapimg").style.transform = `scale(${1 + 0.08 * out(p(t, SC.outil + 0.5, 3))})`;
    const qp = out(p(t, SC.phone, 0.6));
    $("#pho").style.transform = `translateY(${(1 - qp) * 760}px)`;
    $("#plane").style.opacity = t >= SC.avion ? 1 : 0;
    pop($("#avion"), t, SC.avion, "translateX(-100%)");
    $("#avion").style.opacity = +$("#avion").style.opacity * (1 - out(p(t, SC.zoom + 0.6, 0.3)) * (1 - out(p(t, SC.papier - 0.4, 0.4))));
    $("#pho2").style.opacity = out(p(t, SC.avion + 0.25, 0.3));
    const zin = inout(p(t, SC.zoom, 1.0)), zout = inout(p(t, SC.papier - 0.4, 0.7));
    const zoom = 1 + 1.6 * zin * (1 - zout);
    $("#s7in").style.transform = `scale(${zoom})`;
    const ring = $("#ringoff");
    ring.style.opacity = out(p(t, SC.zoom + 1.0, 0.3)) * (1 - out(p(t, SC.papier - 0.5, 0.3)));
    word($("#s7c"), t, SC.zoom + 1.1, SC.papier - 0.5);
    $("#s7c").style.transform = `translateX(-50%) ${$("#s7c").style.transform}`;
    $("#s7t").style.opacity = (t < SC.zoom ? +$("#s7t").style.opacity : 1) * (1 - zin * (1 - zout));
    const qf = out(p(t, SC.papier, 0.6));
    $("#fic").style.transform = `translateX(${(1 - qf) * 700}px) rotate(${3 + (1 - qf) * 12}deg)`;
  }

  // ── the end (the door closes)
  if (iris($("#s8"), t, SC.fin, 1e9)) {
    const w8 = $$("#s8 .w");
    word(w8[0], t, SC.fin + 0.4); slam(w8[1], t, SC.fin + 1.0, "50% 60%");
    const qe = out(p(t, SC.logo, 0.6));
    $("#s8t").style.transform = `translateY(${-210 * qe}px) scale(${1 - 0.25 * qe})`;
    const end = $("#end");
    end.style.opacity = qe;
    end.style.transform = `translateY(${(1 - qe) * 60}px)`;
  }
  $("#gt").setAttribute("seed", Math.floor(t * 30) % 17 + 1);
  if (t >= SC.tard && t < SC.titre + 0.6) $("#dp").src = `img/dp/${String(Math.floor(t * 24) % 26).padStart(2, "0")}.png`;
  $("#fade").style.opacity = Math.max(1 - p(t, 0, 0.35), p(t, SC.end - 0.6, 0.6));
};
window.render(0);

// window.render(t): draws the frame at t seconds. Pure function of t, so any frame renders on its own.
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const p = (t, a, d) => clamp((t - a) / d);
const out = (x) => 1 - Math.pow(1 - x, 4);
const back = (x) => { const c1 = 1.70158, c3 = c1 + 1; return x <= 0 ? 0 : x >= 1 ? 1 : 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a, b, q) => { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * q)).join(",")})`; };
const NAVY = "#13294B", SUN = "#FDCD2F", PAPER = "#F6F1E7", DEEP = "#1b3a66", EDGE = "#2c4f82";

// a word that rises in at `at` and leaves at `leave`
function word(el, t, at, leave = 1e9, dy = 46) {
  const q = out(p(t, at, 0.45)), r = out(p(t, leave, 0.3));
  el.style.opacity = q * (1 - r);
  el.style.transform = `translateY(${(1 - q) * dy - r * 30}px)`;
}
function slam(el, t, at) {
  const q = out(p(t, at, 0.28));
  el.style.opacity = q;
  el.style.transform = `scale(${1.7 - 0.7 * q})`;
  el.style.transformOrigin = "0% 60%";
}
function pop(el, t, at, base = "") {
  const q = back(p(t, at, 0.45));
  el.style.opacity = clamp(q * 1.6);
  el.style.transform = `${base} scale(${q})`;
}

const R = Object.fromEntries(REGIONS.map((r) => [r.k, r]));
const byLight = [...REGIONS].sort((a, b) => b.tapv - a.tapv).map((r) => r.k);
const P1 = REGIONS.filter((r) => r.p1).map((r) => r.k);
const dots = $$(".dot").map((el) => ({ el, a: +el.dataset.a, o: +el.dataset.o }));
const bubs = $$(".bub");
const rings = $$(".ring");
const tags = $$(".tag");
const leads = $$(".lead").map((el) => ({ el, i: +el.dataset.i, x1: +el.getAttribute("x1"), y1: +el.getAttribute("y1"), x2: +el.getAttribute("x2"), y2: +el.getAttribute("y2") }));
rings.forEach((g) => g.querySelectorAll("circle").forEach((c, k) => { if (k < 3) { c.setAttribute("cx", g.dataset.x); c.setAttribute("cy", g.dataset.y); } }));

function regionFill(k, t) {
  const r = R[k];
  if (t < SC.titre) return DEEP;
  if (t < SC.previent) return mix("#e7e1d4", r.tap, out(p(t, SC.montre + 0.4 + byLight.indexOf(k) * 0.2, 0.5)));
  if (t < SC.agir) return mix(r.tap, r.risk, out(p(t, SC.previent + 0.2 + (r.hi ? 0.5 : 0), 0.6)));
  return mix(r.risk, r.p1 ? SUN : "#dfe6ef", out(p(t, SC.agir + 0.1, 0.5)));
}
function regionStroke(t) {
  if (t < SC.titre) return EDGE;
  if (t < SC.previent) return "#ffffff";
  if (t < SC.agir) return mix("#ffffff", EDGE, p(t, SC.previent, 0.5));
  return mix(EDGE, "#ffffff", p(t, SC.agir, 0.5));
}

function panelX(el, t, inAt, outAt) {
  // slides in from the right at inAt; shown until outAt
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
  // ── background and the map stage (schools, then it shows, warns, says what to do)
  let bg = NAVY;
  if (t >= SC.montre) bg = PAPER;
  if (t >= SC.previent) bg = mix(PAPER, NAVY, out(p(t, SC.previent, 0.5)));
  if (t >= SC.agir) bg = mix(NAVY, PAPER, out(p(t, SC.agir, 0.5)));
  $("#bg").style.background = bg;
  const map = $("#map");
  const qm = out(p(t, 0, 0.7));
  map.style.opacity = qm;
  map.style.transform = `scale(${0.96 + 0.04 * qm})`;
  const st = regionStroke(t);
  for (const r of REGIONS) { const el = document.getElementById("r-" + r.k); el.setAttribute("fill", regionFill(r.k, t)); el.setAttribute("stroke", st); }

  // schools
  $("#dots").style.display = t < SC.titre ? "" : "none";
  if (t < SC.titre) for (const d of dots) {
    let r = 3.2 * back(p(t, 0.5 + d.a * 2.2, 0.35)), c = SUN;
    if (d.o >= 0) { const q = out(p(t, 3.7 + d.o * 1.9, 0.3)); c = mix(SUN, "#3a5582", q); r = r - 1.3 * q; }
    d.el.setAttribute("r", Math.max(0, r).toFixed(2));
    d.el.setAttribute("fill", c);
  }
  // sudden drops: the bubbles, smallest first
  bubs.forEach((b, i) => {
    const q = back(p(t, SC.bulles + i * 0.28, 0.42)) * (1 - out(p(t, SC.previent, 0.4)));
    b.setAttribute("r", (+b.dataset.r * Math.max(0, q)).toFixed(2));
  });
  // risk: rings and badges
  $("#rings").style.display = t >= SC.previent && t < SC.agir + 0.4 ? "" : "none";
  $("#rings").style.opacity = 1 - out(p(t, SC.agir, 0.35));
  rings.forEach((g, i) => {
    const bq = back(p(t, SC.previent + 1.4 + i * 0.2, 0.4));
    const badge = g.querySelector(".badge");
    badge.setAttribute("transform", `translate(${g.dataset.x},${g.dataset.y}) scale(${bq})`);
    [...g.querySelectorAll(":scope > circle")].forEach((c, k) => {
      const s = t - (SC.previent + 1.6) - k * 0.4;
      if (s < 0) { c.setAttribute("r", 0); return; }
      const ph = (s % 1.2) / 1.2;
      c.setAttribute("r", (18 + ph * 48).toFixed(1));
      c.setAttribute("opacity", ((1 - ph) * 0.9).toFixed(2));
    });
  });
  // what to do: the priority regions rise
  $$(".ex").forEach((g, j) => { g.style.opacity = t < SC.agir ? 0 : out(p(t, SC.agir + 0.6 + j * 0.22, 0.5)); });
  $$(".lift").forEach((el, j) => {
    const q = t < SC.agir ? 0 : out(p(t, SC.agir + 0.6 + j * 0.22, 0.5));
    el.style.opacity = q;
    el.setAttribute("transform", `translate(0,${-10 * q})`);
  });
  tags.forEach((el, i) => { el.style.display = t >= SC.tags - 0.1 && t < SC.outil + 0.6 ? "flex" : "none"; pop(el, t, SC.tags + i * 1.0); });
  leads.forEach((l) => {
    const q = out(p(t, SC.tags + l.i * 1.0 + 0.15, 0.5));
    l.el.style.display = t >= SC.tags && t < SC.outil + 0.6 ? "" : "none";
    l.el.setAttribute("x2", l.x1 + (l.x2 - l.x1) * q);
    l.el.setAttribute("y2", l.y1 + (l.y2 - l.y1) * q);
  });

  // ── the words beside the map
  const w1 = $$("#t1 .w");
  $("#t1").style.display = t < SC.tard + 0.6 ? "" : "none";
  word(w1[0], t, 0.8); word(w1[1], t, 1.1); slam(w1[2], t, 3.7); word(w1[3], t, 4.7); word(w1[4], t, 5.4);
  const w4 = $$("#t4 .w");
  $("#t4").style.display = t >= SC.montre && t < SC.previent + 0.4 ? "" : "none";
  const L4 = SC.previent;
  word(w4[0], t, 17.4, L4); word(w4[1], t, 17.7, L4); word(w4[2], t, 18.0, L4); word(w4[3], t, 18.9, L4); word(w4[4], t, 22.0, L4);
  const w5 = $$("#t5 .w");
  $("#t5").style.display = t >= SC.previent && t < SC.agir + 0.4 ? "" : "none";
  const L5 = SC.agir;
  word(w5[0], t, 27.6, L5); word(w5[1], t, 27.9, L5); word(w5[2], t, 28.3, L5); word(w5[3], t, 31.0, L5); word(w5[4], t, 32.5, L5);
  const w6 = $$("#t6 .w");
  $("#t6").style.display = t >= SC.agir ? "" : "none";
  word(w6[0], t, 37.6); word(w6[1], t, 38.0); slam(w6[2], t, 38.6);

  // ── 2 · too late: the calendar
  if (panelX($("#s2"), t, SC.tard, SC.titre + 0.6)) {
    word($("#s2a"), t, 7.5); word($("#s2b"), t, SC.rapport + 0.15);
    const cur = $("#pgcur");
    const qc = out(p(t, 7.4, 0.5));
    cur.style.opacity = qc;
    cur.style.transform = `translateY(${(1 - qc) * -80}px) rotate(${-2 * qc}deg)`;
    const n = t < SC.flip ? 0 : Math.min(MONTHS.length, Math.floor((t - SC.flip) / 0.25) + 1);
    $("#pgm").textContent = n === 0 ? "Septembre" : MONTHS[n - 1];
    $("#pgr").style.display = n === 0 ? "" : "none";
    const doc = $("#pgdoc");
    doc.style.display = n === MONTHS.length ? "flex" : "none";
    pop(doc, t, SC.rapport);
    const fly = $("#pgfly");
    const flying = t >= SC.flip && t < SC.flip + MONTHS.length * 0.25;
    fly.style.display = flying ? "" : "none";
    if (flying) {
      const k = Math.floor((t - SC.flip) / 0.25), lq = ((t - SC.flip) % 0.25) / 0.25;
      $("#pgflym").textContent = k === 0 ? "Septembre" : MONTHS[k - 1];
      fly.style.transform = `rotate(-2deg) rotateX(${lq * 115}deg) translateY(${-lq * 40}px)`;
      fly.style.opacity = 1 - lq * 0.6;
    }
    const sq = out(p(t, SC.stamp, 0.2));
    const stamp = $("#stamp");
    stamp.style.opacity = sq;
    stamp.style.transform = `rotate(-14deg) scale(${2.4 - 1.4 * sq})`;
    const s = t - SC.stamp - 0.2;
    const amp = s > 0 ? 16 * Math.exp(-s * 9) : 0;
    $("#s2").style.transform += ` translate(${amp * Math.sin(t * 95)}px, ${amp * Math.cos(t * 71)}px)`;
  }

  // ── title
  const s3 = $("#s3");
  const s3show = iris(s3, t, SC.titre, SC.montre + 0.5);
  if (s3show) {
    if (t >= SC.montre) { s3.style.clipPath = "none"; s3.style.transform = `translateX(${-out(p(t, SC.montre, 0.5)) * 1920}px)`; }
    else s3.style.transform = "";
    pop($("#logo"), t, 13.4);
    const w3 = $$("#s3 .w");
    word(w3[0], t, 13.8); word(w3[1], t, 14.3); word(w3[2], t, 14.7);
  }

  // ── the tool
  if (panelX($("#s7"), t, SC.outil, SC.fin + 0.6)) {
    word($("#s7t"), t, 47.4);
    const ql = out(p(t, 47.3, 0.6));
    $("#lap").style.transform = `translateX(${(1 - ql) * -1300}px)`;
    $("#lapimg").style.transform = `scale(${1 + 0.12 * out(p(t, 48, 7))})`;
    const qp = out(p(t, 48.6, 0.6));
    $("#pho").style.transform = `translateY(${(1 - qp) * 760}px)`;
    $("#plane").style.opacity = t >= SC.avion ? 1 : 0;
    pop($("#avion"), t, SC.avion, "translateX(-50%)");
    $("#pho2").style.opacity = out(p(t, SC.avion + 0.25, 0.4));
    const qf = out(p(t, SC.papier, 0.6));
    $("#fic").style.transform = `translateX(${(1 - qf) * 700}px) rotate(${3 + (1 - qf) * 12}deg)`;
  }

  // ── the end
  if (iris($("#s8"), t, SC.fin, 1e9)) {
    const w8 = $$("#s8 .w");
    word(w8[0], t, 55.4); slam(w8[1], t, 56.0);
    w8[1].style.transformOrigin = "50% 60%";
    const qe = out(p(t, SC.logo, 0.6));
    $("#s8t").style.transform = `translateY(${-210 * qe}px) scale(${1 - 0.25 * qe})`;
    const end = $("#end");
    end.style.opacity = qe;
    end.style.transform = `translateY(${(1 - qe) * 60}px)`;
  }
  $("#fade").style.opacity = Math.max(1 - p(t, 0, 0.35), p(t, SC.end - 0.6, 0.6));
};
window.render(0);

// window.render(t): async, draws the frame at t seconds (waits for the camera frame to decode).
const $ = (s) => document.querySelector(s);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const p = (t, a, d) => clamp((t - a) / d);
const out = (x) => 1 - Math.pow(1 - x, 4);
const inout = (x) => (x < 0.5 ? 8 * x ** 4 : 1 - Math.pow(-2 * x + 2, 4) / 2);
const back = (x) => { const c1 = 1.70158, c3 = c1 + 1; return x <= 0 ? 0 : x >= 1 ? 1 : 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };

const I = CFG.intro, FPS = CUT.fps;
const SEG = CUT.segments.map((s) => ({ ...s, a: I + s.from / FPS, b: I + s.to / FPS }));
const T = I + CUT.frames / FPS;
window.DURATION = T;

function rise(el, t, at, leave = 1e9, dy = 50) {
  const q = out(p(t, at, 0.45)), r = out(p(t, leave, 0.25));
  el.style.opacity = q * (1 - r);
  el.style.transform = `translateY(${(1 - q) * dy}px) translateX(${-r * 80}px)`;
}
function card(el, t, at, leave) {
  const bar = el.querySelector(".bar"), box = el.querySelector(".box");
  bar.style.width = `${420 * out(p(t, at, 0.3))}px`;
  const q = out(p(t, at + 0.15, 0.45));
  box.style.clipPath = `inset(0 ${100 * (1 - q)}% 0 0 round 28px)`;
  const r = out(p(t, leave, 0.25));
  el.style.opacity = 1 - r;
  el.style.transform = `translateX(${-r * 90}px)`;
}

let lastSrc = "";
window.render = async function (t) {
  // background: the dotted grid drifts, the outline of the country turns slowly
  $("#grid").style.transform = `translate(${(t * 14) % 44}px, ${(t * 9) % 44}px)`;
  $("#bf").style.transform = `translate(${Math.sin(t * 0.4) * 30}px, ${Math.cos(t * 0.3) * 20}px) rotate(${-4 + t * 0.35}deg)`;

  // opening sting: the logo pops, the team name rises, then both fly to the corner
  const sq = back(p(t, 0.15, 0.5)), leave = inout(p(t, I - 0.4, 0.45));
  $("#sb").style.transform = `scale(${sq})`;
  const st = $("#st"), sw = out(p(t, 0.4, 0.45));
  st.style.opacity = sw; st.style.transform = `translateY(${(1 - sw) * 40}px)`;
  const sting = $("#sting");
  sting.style.display = t < I + 0.1 ? "flex" : "none";
  sting.style.opacity = 1 - leave;
  sting.style.transform = `translate(${leave * 640}px, ${-leave * 420}px) scale(${1 - 0.7 * leave})`;
  const bug = $("#bug");
  bug.style.opacity = out(p(t, I - 0.1, 0.3));

  // the camera window enters, then follows the cuts: a punch-in per segment, a slow push inside each one
  const cam = $("#cam"), ce = back(p(t, I - 0.25, 0.6));
  cam.style.opacity = clamp(ce * 2);
  cam.style.transform = `scale(${0.88 + 0.12 * ce}) rotate(${-3 * (1 - ce)}deg)`;
  const n = clamp(Math.floor((t - I) * FPS), 0, CUT.frames - 1);
  const k = SEG.findIndex((s) => n >= s.from && n < s.to);
  const s = SEG[Math.max(0, k)];
  const punch = (CFG.punch || [])[Math.max(0, k)] || (k % 2 ? 1.18 : 1.0);
  const push = 1 + 0.045 * p(t, s.a, s.b - s.a);
  const bump = 1 + 0.035 * (1 - out(p(t, s.a, 0.2))) * (k > 0 ? 1 : 0);
  const ci = $("#ci");
  ci.style.transform = `scale(${punch * push * bump})`;
  $("#flash").style.opacity = k > 0 ? 0.28 * (1 - p(t, s.a, 0.12)) : 0;
  const src = CAM + "c" + String(n).padStart(5, "0") + ".jpg";
  if (src !== lastSrc) { ci.src = src; lastSrc = src; await ci.decode(); }

  // the words beside, each on the word that says it (EV: times on the edited timeline, from the transcript)
  const EV = CFG.ev || {}, end = T;
  const mateAt = EV.mate ?? EV.coequipier ?? end;  // my card stays until the teammate's name is said
  $("#p0").style.display = t < mateAt + 0.3 ? "" : "none";
  const h = $("#p0 .hello"), hq = back(p(t, EV.bonjour - 0.05, 0.4)), hu = inout(p(t, EV.nom - 0.2, 0.4));
  h.style.opacity = clamp(hq * 1.5) * (1 - out(p(t, mateAt - 0.15, 0.25)));
  h.style.transform = `translateY(${-150 * hu}px) scale(${(0.7 + 0.3 * hq) * (1 - 0.3 * hu)})`;
  h.style.transformOrigin = "0% 50%";
  card($("#c0"), t, EV.nom - 0.15, mateAt - 0.15);
  const t0 = $("#t0"), tq = out(p(t, (EV.titre ?? EV.nom + 0.6) - 0.05, 0.35));
  t0.style.opacity = tq; t0.style.transform = `translateY(${(1 - tq) * 16}px)`;
  $("#p1").style.display = t >= mateAt - 0.15 && t < end + 1 ? "" : "none";
  card($("#c1"), t, mateAt - 0.2, (EV.equipe ?? 1e9) - 0.1);
  for (const [id, at] of [["#n1", mateAt - 0.1], ["#t1", EV.mateTitre ?? (EV.mate ?? mateAt) + 0.7]]) {
    const el = $(id), q = out(p(t, at - 0.05, 0.35));
    el.style.opacity = q; el.style.transform = `translateY(${(1 - q) * 16}px)`;
  }
  const PH = CFG.phrases || [];
  const inPhrase = PH.some((ph) => t >= ph.ev[0] - 0.2 && t < (ph.evEnd ?? 1e9));
  const teamOn = EV.equipe !== undefined && t >= EV.equipe - 0.1 && t < (EV.equipeFin ?? 1e9);
  $("#p2").style.display = teamOn && !inPhrase ? "" : "none";
  document.querySelectorAll(".p3").forEach((panel) => {
    const ph = PH[+panel.dataset.k];
    const on = t >= ph.ev[0] - 0.2 && t < (ph.evEnd ?? 1e9);
    panel.style.display = on ? "" : "none";
    panel.querySelectorAll(".lw").forEach((el, i) => {
      const at = (ph.ev[i] ?? 1e9) - 0.05, q = out(p(t, at, 0.55));
      el.style.transform = `translateY(${(1 - q) * 140}px)`;
      el.style.opacity = t < at ? 0 : 1;
    });
  });
  if (EV.equipe !== undefined) {
    const b2 = $("#b2"), bq = out(p(t, EV.equipe, 0.3));
    b2.style.opacity = bq; b2.style.transform = `scale(${1.5 - 0.5 * bq})`; b2.style.transformOrigin = "0% 60%";
    const verbs = [EV.cartographier, EV.predire, EV.agir];
    document.querySelectorAll(".chip").forEach((c, i) => {
      const q = back(p(t, (verbs[i] ?? EV.equipe + 0.8 + i * 0.55) - 0.05, 0.45));
      c.style.opacity = clamp(q * 1.5);
      c.style.transform = `translateX(${(1 - q) * -70}px) scale(${0.8 + 0.2 * q})`;
    });
  }

  $("#prog").style.width = `${1920 * clamp(t / T)}px`;
};

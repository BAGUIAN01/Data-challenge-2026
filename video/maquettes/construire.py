"""Six key frames (styleframes) for the face-camera video's illustrations. No figures on screen: maps, shapes, words."""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.path import Path as MPath

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
D = json.load(open(ROOT / "preparation_jury" / "deck" / "donnees.json", encoding="utf-8"))
MAP = D["carte"]
REG = {r["cle"]: r for r in D["regions"]}
W, H = float(MAP["largeur"]), float(MAP["hauteur"])

# Kalantigui film palette
SUN, NIGHT, PAPER, INKC, RED, ORANGE = "#FDCD2F", "#13294B", "#F6F1E7", "#0E1A2E", "#E5484D", "#F59E0B"
BLUES = ["#13294B", "#1f4f8f", "#3d7cc9", "#8fb6e3", "#d7e6f6"]
LEVER = {"violence": ("Continuité éducative", "book"), "deplaces": ("Classes passerelles", "bridge"),
         "grossesses": ("Maintien des filles", "venus"), "pauvrete": ("Cantines scolaires", "food")}
ICON = {
    "book": '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
    "bridge": '<path d="M2 18h20"/><path d="M4 18v-4"/><path d="M20 18v-4"/><path d="M2 14c3-6 17-6 20 0"/><path d="M8 18v-5"/><path d="M16 18v-5"/>',
    "venus": '<circle cx="12" cy="9" r="6"/><path d="M12 15v7"/><path d="M9 19h6"/>',
    "food": '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>',
    "plane": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "alert": '<path d="m21.7 18-8-14a2 2 0 0 0-3.5 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
}


def icon(name, size, color, stroke=2.2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


def polys(d):
    out = []
    for part in re.findall(r"M[^M]+", d):
        pts = [tuple(map(float, p.split(","))) for p in re.findall(r"-?\d+\.?\d*,-?\d+\.?\d*", part)]
        out.append(np.array(pts))
    return out


def norm(s):
    return re.sub(r"[^A-Z]", "", s.upper().replace("É", "E"))


# Schools as dots: as many per region as schools at its peak, closed in the share closed at its worst (real data).
panel = pd.read_csv(ROOT / "depots/03_transformation/Biiga_03-transformation_D1_engineer_panel-region-annee_v1.csv")
panel["k"] = panel.region.map(norm)
peak = panel.groupby("k").ecoles.max()
typo = pd.read_csv(ROOT / "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p2-typologie-regions_v1.csv")
closed = dict(zip(typo.region.map(norm), -typo["ecoles_pire_chute_%"] / 100))


def school_dots(per=0.065, seed=7):
    rng = np.random.default_rng(seed)
    out = []
    for cle, g in MAP["regions"].items():
        ps = polys(g["d"])
        allp = np.vstack(ps)
        paths = [MPath(p) for p in ps]
        n = int(peak[cle] * per)
        share = closed.get(cle, 0)
        pts = []
        while len(pts) < n:
            x, y = rng.uniform(allp[:, 0].min(), allp[:, 0].max()), rng.uniform(allp[:, 1].min(), allp[:, 1].max())
            if any(p.contains_point((x, y)) for p in paths):
                pts.append((x, y))
        k_off = int(round(n * share))
        for i, (x, y) in enumerate(pts):
            out.append((x, y, i < k_off))
    return out


def base_map(width, fill, stroke="#ffffff", sw=1.6, extra="", under=""):
    o = [f'<svg viewBox="-10 -10 {W + 20} {H + 20}" width="{width}" xmlns="http://www.w3.org/2000/svg">', under]
    for cle, g in MAP["regions"].items():
        o.append(f'<path d="{g["d"]}" fill="{fill(REG[cle])}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')
    o.append(extra + "</svg>")
    return "".join(o)


def pip(dark):
    c = "#ffffff" if dark else NIGHT
    return f'''<div class="pip {'d' if dark else ''}"><svg viewBox="0 0 100 80" width="100%" height="100%"><circle cx="50" cy="34" r="15" fill="{c}" opacity=".35"/>
<path d="M18 80c4-20 18-28 32-28s28 8 32 28z" fill="{c}" opacity=".35"/></svg><span>ta vidéo</span></div>'''


def frame(n, bg, body, dark, label):
    return f'<section class="f {bg}"><div class="lab">{n} · {label}</div>{body}{pip(dark)}</section>'


# ---------------------------------------------------------------- 1. schools switch off
def f1():
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.4 if off else 3.2}" fill="{"#4d6690" if off else SUN}"/>'
                   for x, y, off in school_dots())
    m = base_map(1120, lambda r: "#1b3a66", stroke="#2c4f82", sw=1.4, extra=dots)
    body = f'''<div class="map l1">{m}</div>
<div class="t r1"><b>Des écoles<br><em>ferment.</em></b><span>Des enfants quittent la classe.</span><div class="key1"><p><i class="on"></i>école ouverte</p><p><i></i>école fermée</p></div></div>'''
    return frame(1, "night", body, True, "Le problème")


# ---------------------------------------------------------------- 2. too late
def f2():
    months = ["Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars"]
    pages = "".join(f'<div class="pg" style="--i:{i}"><div class="pg-h">{m}</div><div class="pg-b"></div></div>' for i, m in enumerate(months))
    body = f'''<div class="t l2"><b>On l'apprend…</b></div>
<div class="cal">{pages}<div class="pg top"><div class="pg-h">Septembre</div><div class="pg-b"><span>RENTRÉE</span></div></div>
<div class="stamp">TROP TARD</div></div>'''
    return frame(2, "sun", body, False, "Le problème")


# ---------------------------------------------------------------- 3. it shows
def tap_fill(r):
    t = r["tap"]
    return BLUES[0] if t < 20 else BLUES[1] if t < 40 else BLUES[2] if t < 60 else BLUES[3] if t < 75 else BLUES[4]


def f3():
    circ = ""
    for cle, g in MAP["regions"].items():
        v = REG[cle]["pire_baisse"]
        if v <= -5:
            rr = 44 * (abs(v) / 47.4) ** 0.5
            circ += f'<circle cx="{g["lx"]}" cy="{g["ly"]}" r="{rr:.1f}" fill="{SUN}" stroke="{NIGHT}" stroke-width="2.5"/>'
    m = base_map(1060, tap_fill, extra=circ)
    body = f'''<div class="map l3">{m}</div>
<div class="t r3"><small>1 · IL MONTRE</small><b>Où les enfants<br>décrochent.</b>
<div class="chips"><p class="chip lent"><i></i>Lent</p><p class="chip brutal"><i></i>Brutal</p></div></div>'''
    return frame(3, "paper", body, False, "La solution")


# ---------------------------------------------------------------- 4. it warns
def f4():
    def fill(r):
        p = r["probas"]["ref_2026_27"]
        return RED if p >= 40 else ORANGE if p >= 15 else "#1b3a66"
    rings, alerts = "", ""
    for cle, g in MAP["regions"].items():
        p = REG[cle]["probas"]["ref_2026_27"]
        if p >= 40:
            for k, op in ((26, .9), (40, .5), (54, .22)):
                rings += f'<circle cx="{g["lx"]}" cy="{g["ly"]}" r="{k}" fill="none" stroke="#ffffff" stroke-width="2.4" opacity="{op}"/>'
            alerts += f'<g transform="translate({float(g["lx"]) - 14},{float(g["ly"]) - 14}) scale(1.15)"><circle cx="12" cy="12" r="15" fill="#ffffff"/>' \
                      f'<g fill="none" stroke="{RED}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{ICON["alert"]}</g></g>'
    m = base_map(1100, fill, stroke="#2c4f82", sw=1.6, extra=rings + alerts)
    body = f'''<div class="map l4">{m}</div>
<div class="t r4"><small>2 · IL PRÉVIENT</small><b>Le risque,<br><em>avant la rentrée.</em></b>
<div class="cal2"><p>Septembre<i>on alerte</i></p><p>Janvier<i>on confirme</i></p></div></div>'''
    return frame(4, "night", body, True, "La solution")


# ---------------------------------------------------------------- 5. what to do
def f5():
    p1 = [c for c in MAP["regions"] if REG[c]["priorite"] == 1]
    under = "".join(f'<path d="{MAP["regions"][c]["d"]}" transform="translate(0,{k})" fill="#c99a12" stroke="#c99a12" stroke-width="1.6"/>'
                    for k in (12, 9, 6, 3) for c in p1)
    lifted = "".join(f'<path d="{MAP["regions"][c]["d"]}" fill="{SUN}" stroke="{NIGHT}" stroke-width="2"/>' for c in p1)
    m = base_map(1000, lambda r: "#dfe6ef" if r["priorite"] != 1 else "none", stroke="#ffffff", sw=1.6, extra=under + lifted)
    pos = {"SAHEL": (760, 150), "NORD": (300, 215), "CENTRENORD": (700, 330), "EST": (830, 560), "BOUCLEDUMOUHOUN": (150, 520)}
    tags = ""
    for c in p1:
        name, ic = LEVER[REG[c]["dominant"]]
        x, y = pos[c]
        tags += f'<div class="tag5" style="left:{x}px;top:{y}px">{icon(ic, 34, NIGHT)}<b>{name}</b><span>{REG[c]["ancienne"]}</span></div>'
    body = f'''<div class="map l5">{m}</div>{tags}
<div class="t r5"><small>3 · IL DIT QUOI FAIRE</small><b>Où agir.<br><em>Sur quoi.</em></b></div>'''
    return frame(5, "paper", body, False, "La solution")


# ---------------------------------------------------------------- 6. offline
def f6():
    body = f'''<div class="lap"><div class="lap-s"><img src="img/bureau.jpg"></div><div class="lap-b"></div></div>
<div class="pho"><div class="pho-bar">{icon("plane", 26, "#ffffff")}<span>Mode avion</span></div><img src="img/carte.jpg"></div>
<div class="t r6"><b>Même<br>sans<br>internet.</b><div class="dev6"><p>Ordinateur</p><p>Téléphone</p><p>Papier</p></div></div>'''
    return frame(6, "sun", body, False, "L'outil")


CSSX = """
@font-face { font-family: Jakarta; src: url(fonts/PlusJakartaSans.woff2); font-weight: 200 700; }
@font-face { font-family: Jakarta; src: url(fonts/PlusJakartaSans-800.woff2); font-weight: 800 900; }
@font-face { font-family: Inter; src: url(fonts/Inter.woff2); font-weight: 100 900; }
* { box-sizing: border-box; } body { margin: 0; background: #444; }
.f { width: 1920px; height: 1080px; position: relative; overflow: hidden; font-family: Inter; }
.night { background: #13294B; color: #fff; } .sun { background: #FDCD2F; color: #13294B; } .paper { background: #F6F1E7; color: #13294B; }
.lab { position: absolute; left: 70px; top: 46px; font: 800 18px Jakarta; letter-spacing: .16em; text-transform: uppercase; opacity: .55; }
.pip { position: absolute; right: 56px; bottom: 56px; width: 400px; height: 250px; border-radius: 28px; border: 6px solid #13294B; background: #fff; overflow: hidden; }
.pip.d { border-color: #fff; background: #0c1c36; } .pip span { position: absolute; left: 18px; top: 12px; font: 800 16px Jakarta; letter-spacing: .1em; text-transform: uppercase; opacity: .6; }
.map { position: absolute; } .t { position: absolute; }
.t b { display: block; font: 800 104px/1.02 Jakarta; letter-spacing: -.02em; } .t em { font-style: normal; }
.t small { display: block; font: 800 22px Jakarta; letter-spacing: .16em; margin-bottom: 20px; } .t span { display: block; font: 600 34px Inter; margin-top: 26px; opacity: .8; }
.night .t em { color: #FDCD2F; } .paper .t em { color: #1f4f8f; } .sun .t em { color: #fff; -webkit-text-stroke: 0; }
.l1 { left: 40px; top: 120px; } .key1 { display: flex; gap: 28px; margin-top: 36px; } .key1 p { margin: 0; display: flex; align-items: center; gap: 12px; font: 600 24px Inter; opacity: .85; } .key1 i { width: 16px; height: 16px; border-radius: 50%; background: #4d6690; } .key1 i.on { background: #FDCD2F; } .r1 { left: 1180px; top: 250px; }
.l2 { left: 120px; top: 380px; } .l2 b { font-size: 120px; }
.cal { position: absolute; left: 1060px; top: 250px; width: 620px; height: 640px; }
.pg { position: absolute; inset: 0; background: #fff; border-radius: 26px; box-shadow: 0 10px 0 #13294B; transform: translate(calc(var(--i) * 10px), calc(var(--i) * -10px)) rotate(calc(var(--i) * 1.2deg)); }
.pg:not(.top) .pg-h { color: transparent; } .pg-h { background: #13294B; color: #fff; font: 800 52px Jakarta; padding: 30px 40px; border-radius: 26px 26px 0 0; }
.pg-b { height: 470px; display: flex; align-items: center; justify-content: center; background-image: linear-gradient(#e7e1d4 2px, transparent 2px), linear-gradient(90deg, #e7e1d4 2px, transparent 2px); background-size: 74px 74px; background-position: 30px 30px; }
.pg.top { transform: rotate(-3deg); opacity: 1; } .pg.top .pg-b span { background: #FDCD2F; font: 800 44px Jakarta; padding: 14px 30px; border-radius: 14px; }
.stamp { position: absolute; left: -140px; top: 420px; transform: rotate(-14deg); border: 10px solid #E5484D; color: #E5484D; font: 900 96px Jakarta; padding: 6px 34px; border-radius: 22px; background: rgba(255,255,255,.88); letter-spacing: .02em; }
.l3 { left: 60px; top: 150px; } .r3 { left: 1170px; top: 220px; }
.chips { display: flex; gap: 18px; margin-top: 40px; } .chip { margin: 0; display: flex; align-items: center; gap: 14px; font: 800 36px Jakarta; background: #fff; padding: 14px 26px; border-radius: 999px; }
.chip i { width: 34px; height: 34px; border-radius: 50%; } .chip.lent i { background: linear-gradient(90deg, #13294B 0 33%, #3d7cc9 33% 66%, #d7e6f6 66%); } .chip.brutal i { background: #FDCD2F; border: 3px solid #13294B; }
.l4 { left: 40px; top: 140px; } .r4 { left: 1180px; top: 220px; }
.cal2 { display: flex; gap: 18px; margin-top: 40px; } .cal2 p { margin: 0; font: 800 30px Jakarta; background: rgba(255,255,255,.1); border-radius: 18px; padding: 16px 24px; }
.cal2 i { display: block; font: 600 22px Inter; font-style: normal; color: #FDCD2F; margin-top: 4px; }
.l5 { left: 120px; top: 160px; } .r5 { left: 1330px; top: 300px; }
.tag5 { position: absolute; display: flex; align-items: center; gap: 12px; background: #fff; border-radius: 18px; padding: 12px 18px 12px 14px; box-shadow: 0 6px 0 #13294B; border: 3px solid #13294B; }
.tag5 b { font: 800 26px Jakarta; } .tag5 span { position: absolute; left: 14px; top: -26px; font: 800 15px Jakarta; letter-spacing: .1em; text-transform: uppercase; color: #13294B; opacity: .7; }
.lap { position: absolute; left: 120px; top: 190px; width: 1060px; } .lap-s { background: #13294B; border-radius: 26px 26px 6px 6px; padding: 22px 22px 28px; } .lap-s img { display: block; width: 100%; border-radius: 6px; }
.lap-b { height: 30px; margin: 0 -60px; background: #0E1A2E; border-radius: 3px 3px 24px 24px; clip-path: polygon(0 0, 100% 0, 96% 100%, 4% 100%); }
.pho { position: absolute; left: 980px; top: 330px; width: 300px; background: #13294B; border-radius: 44px; padding: 14px; box-shadow: 0 14px 0 rgba(19,41,75,.25); }
.pho img { display: block; width: 100%; border-radius: 32px; } .pho-bar { position: absolute; left: 50%; top: -34px; transform: translateX(-50%); display: flex; align-items: center; gap: 10px; background: #E5484D; color: #fff; font: 800 22px Jakarta; padding: 12px 22px; border-radius: 999px; white-space: nowrap; }
.r6 { left: 1370px; top: 150px; } .r6 b { font-size: 100px; } .dev6 { display: flex; flex-direction: column; gap: 12px; margin-top: 34px; } .dev6 p { margin: 0; align-self: flex-start; background: #13294B; color: #fff; font: 800 28px Jakarta; padding: 12px 24px; border-radius: 999px; }
"""


def build():
    pages = [f1(), f2(), f3(), f4(), f5(), f6()]
    (HERE / "maquettes.html").write_text(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSSX}</style></head><body>{"".join(pages)}</body></html>', encoding="utf-8")


if __name__ == "__main__":
    build()

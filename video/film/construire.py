"""The animated part of the face-camera video (phase 2): one HTML page whose window.render(t) draws the frame at t seconds.
No figures on screen. Every map state comes from the region data (deck/donnees.json, the panel, the typology)."""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import qrcode
from matplotlib.path import Path as MPath

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from plan import SCENES, URL  # noqa: E402

D = json.load(open(ROOT / "preparation_jury" / "deck" / "donnees.json", encoding="utf-8"))
MAP = D["carte"]
REG = {r["cle"]: r for r in D["regions"]}
W, H = float(MAP["largeur"]), float(MAP["hauteur"])

# the map stage: same place for every map scene, so the map "travels" from one idea to the next
STAGE = {"left": 90, "top": 150, "width": 1080}
SCALE = STAGE["width"] / (W + 20)


def px(x, y):
    return STAGE["left"] + (x + 10) * SCALE, STAGE["top"] + (y + 10) * SCALE


def norm(s):
    return re.sub(r"[^A-Z]", "", s.upper().replace("É", "E"))


def polys(d):
    return [np.array([tuple(map(float, p.split(","))) for p in re.findall(r"-?\d+\.?\d*,-?\d+\.?\d*", part)])
            for part in re.findall(r"M[^M]+", d)]


# ---------------------------------------------------------------- data for the map states
panel = pd.read_csv(ROOT / "depots/03_transformation/Biiga_03-transformation_D1_engineer_panel-region-annee_v1.csv")
peak = panel.assign(k=panel.region.map(norm)).groupby("k").ecoles.max()
typo = pd.read_csv(ROOT / "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p2-typologie-regions_v1.csv")
closed = dict(zip(typo.region.map(norm), -typo["ecoles_pire_chute_%"] / 100))


def school_dots(per=0.065, seed=7):
    """As many dots per region as schools at its peak; the share switched off is its real share closed at its worst."""
    rng = np.random.default_rng(seed)
    out = []
    for cle, g in MAP["regions"].items():
        ps = polys(g["d"])
        allp = np.vstack(ps)
        paths = [MPath(p) for p in ps]
        n = int(peak[cle] * per)
        pts = []
        while len(pts) < n:
            x, y = rng.uniform(allp[:, 0].min(), allp[:, 0].max()), rng.uniform(allp[:, 1].min(), allp[:, 1].max())
            if any(p.contains_point((x, y)) for p in paths):
                pts.append((x, y))
        k_off = int(round(n * closed.get(cle, 0)))
        out += [(x, y, i < k_off) for i, (x, y) in enumerate(pts)]
    return out


def tap_fill(t):
    return "#13294B" if t < 20 else "#1f4f8f" if t < 40 else "#3d7cc9" if t < 60 else "#8fb6e3" if t < 75 else "#d7e6f6"


def risk_fill(p):
    return "#F2673A" if p >= 40 else "#F5A524" if p >= 15 else "#1b3a66"


LEVER = {"violence": ("Continuité éducative", "book"), "deplaces": ("Classes passerelles", "bridge"),
         "grossesses": ("Maintien des filles", "venus"), "pauvrete": ("Cantines scolaires", "food")}
ICON = {
    "book": '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
    "bridge": '<path d="M2 18h20"/><path d="M4 18v-4"/><path d="M20 18v-4"/><path d="M2 14c3-6 17-6 20 0"/><path d="M8 18v-5"/><path d="M16 18v-5"/>',
    "venus": '<circle cx="12" cy="9" r="6"/><path d="M12 15v7"/><path d="M9 19h6"/>',
    "food": '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>',
    "plane": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "alert": '<path d="m21.7 18-8-14a2 2 0 0 0-3.5 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "doc": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M8 13h8"/><path d="M8 17h8"/><path d="M8 9h2"/>',
}


def icon(name, size, color, stroke=2.2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


def qr_svg(url):
    q = qrcode.QRCode(border=0, box_size=1)
    q.add_data(url)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg viewBox="0 0 {n} {n}" width="230" height="230" shape-rendering="crispEdges"><g fill="#13294B">{rects}</g></svg>'


# ---------------------------------------------------------------- the page
def build():
    regions = []
    for cle, g in MAP["regions"].items():
        r = REG[cle]
        regions.append({"k": cle, "tap": tap_fill(r["tap"]), "tapv": r["tap"], "risk": risk_fill(r["probas"]["ref_2026_27"]),
                        "hi": r["probas"]["ref_2026_27"] >= 40, "p1": r["priorite"] == 1, "lx": float(g["lx"]), "ly": float(g["ly"]),
                        "drop": r["pire_baisse"]})
    paths = "".join(f'<path id="r-{cle}" d="{g["d"]}" stroke-linejoin="round"/>' for cle, g in MAP["regions"].items())
    p1 = [c for c in MAP["regions"] if REG[c]["priorite"] == 1]
    extr = "".join(f'<g class="ex" data-k="{c}">' + "".join(f'<path d="{MAP["regions"][c]["d"]}" transform="translate(0,{k})" fill="#c99a12" stroke="#c99a12" stroke-width="1.6"/>' for k in (12, 9, 6, 3)) + "</g>" for c in p1)
    lifted = "".join(f'<path class="lift" data-k="{c}" d="{MAP["regions"][c]["d"]}" fill="#FDCD2F" stroke="#13294B" stroke-width="2"/>' for c in p1)
    rng = np.random.default_rng(3)
    dots = school_dots()
    order = np.argsort([x + rng.uniform(0, 260) for x, y, off in dots])
    rank = np.empty(len(dots)); rank[order] = np.arange(len(dots)) / len(dots)
    offs = [i for i, d in enumerate(dots) if d[2]]
    off_rank = {i: k / max(1, len(offs) - 1) for k, i in enumerate(sorted(offs, key=lambda i: dots[i][1] - 0.6 * dots[i][0]))}
    dot_svg = "".join(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="0" data-a="{rank[i]:.3f}" data-o="{off_rank.get(i, -1):.3f}"/>' for i, (x, y, off) in enumerate(dots))
    bub = "".join(f'<circle class="bub" cx="{r["lx"]}" cy="{r["ly"]}" r="0" data-r="{44 * (abs(r["drop"]) / 47.4) ** 0.5:.1f}" fill="#FDCD2F" stroke="#13294B" stroke-width="2.5"/>'
                  for r in sorted(regions, key=lambda r: r["drop"], reverse=True) if r["drop"] <= -5)
    rings = "".join(f'<g class="ring" data-x="{r["lx"]}" data-y="{r["ly"]}">' + "".join('<circle r="0" fill="none" stroke="#ffffff" stroke-width="2.4"/>' for _ in range(3))
                    + f'<g class="badge" transform="translate({r["lx"]},{r["ly"]})"><circle r="17" fill="#ffffff"/><g transform="translate(-13.2,-13.6) scale(1.1)" fill="none" stroke="#F2673A" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{ICON["alert"]}</g></g></g>'
                    for r in regions if r["hi"])
    # one tag per lever, with a thin line to each of its regions
    groups = {}
    for c in p1:
        groups.setdefault(REG[c]["dominant"], []).append(c)
    def at(c):
        return px(float(MAP["regions"][c]["lx"]), float(MAP["regions"][c]["ly"]))
    nx, ny = at("NORD"); sx, sy = at("SAHEL"); cx, cy = at("CENTRENORD"); ex, ey = at("EST"); bx, by = at("BOUCLEDUMOUHOUN")
    tag_at = {"pauvrete": (nx - 420, ny - 150), "deplaces": (sx - 60, sy - 190), "grossesses": (cx + 10, cy + 60),
              "violence": ((bx + ex) / 2 - 190, max(by, ey) + 150)}
    tags, leads = "", ""
    for i, lev in enumerate(["pauvrete", "deplaces", "grossesses", "violence"]):
        name, ic = LEVER[lev]
        tx, ty = tag_at[lev]
        tags += f'<div class="tag" data-i="{i}" style="left:{tx:.0f}px;top:{ty:.0f}px">{icon(ic, 42, "#13294B")}<b>{name}</b></div>'
        for c in groups[lev]:
            x, y = at(c)
            leads += f'<line class="lead" data-i="{i}" x1="{tx + 190:.0f}" y1="{ty + 38:.0f}" x2="{x:.1f}" y2="{y:.1f}"/><circle class="leadp" data-i="{i}" cx="{x:.1f}" cy="{y:.1f}" r="7"/>'
    months = ["", "", "", "", "", ""]
    outline = "".join(f'<path d="{g["d"]}"/>' for g in MAP["regions"].values())
    base = "".join(f'<g class="slab" transform="translate(0,{k})">{outline}</g>' for k in (10, 8, 6, 4, 2))
    big = sorted([r for r in regions if r["drop"] <= -25], key=lambda r: r["drop"])
    blab = "".join(f'<g transform="translate({r["lx"]},{r["ly"] + 44 * (abs(r["drop"]) / 47.4) ** 0.5 + 18})"><g class="bl" data-i="{i}">'
                   f'<rect x="-{len(REG[r["k"]]["ancienne"]) * 5.6 + 12:.0f}" y="-14" width="{len(REG[r["k"]]["ancienne"]) * 11.2 + 24:.0f}" height="28" rx="14" fill="#13294B"/>'
                   f'<text text-anchor="middle" y="6" fill="#fff" font-family="Jakarta" font-weight="800" font-size="16">{REG[r["k"]]["ancienne"]}</text></g></g>' for i, r in enumerate(big))
    page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{(HERE / "film.css").read_text()}</style></head><body>
<div id="film">
  <div id="bg"></div>
  <div id="mapcam">
  <svg id="map" viewBox="-10 -10 {W + 20} {H + 20}" style="left:{STAGE["left"]}px;top:{STAGE["top"]}px;width:{STAGE["width"]}px">
    <g id="base">{base}</g><g id="regions">{paths}</g><g id="dots">{dot_svg}</g><g id="extr">{extr}</g><g id="lifted">{lifted}</g><g id="bubs">{bub}</g><g id="rings">{rings}</g><g id="blab">{blab}</g>
  </svg>
  <svg id="leads" viewBox="0 0 1920 1080">{leads}</svg>{tags}
  </div>
  <div class="txt" id="t1"><b><span class="m"><span class="w">Des écoles</span></span><br><em class="w">ferment.</em></b>
    <p class="w">Des enfants quittent la classe.</p><div class="key w" style="display:none"><i class="on"></i>école ouverte<i></i>école fermée</div></div>
  <div class="txt" id="t4"><small class="w">1 · IL MONTRE</small><b><span class="m"><span class="w">Où les enfants</span></span><br><span class="m"><span class="w">décrochent.</span></span></b>
    <div class="chips"><div class="chip w" id="lent"><i></i>Lent</div><div class="chip w" id="brutal"><i></i>Brutal</div></div></div>
  <div class="txt" id="t5"><small class="w">2 · IL PRÉVIENT</small><b><span class="m"><span class="w">Le risque,</span></span><br><span class="m"><em class="w">avant la rentrée.</em></span></b>
    <div class="cal2"><div class="w" id="sep">Septembre<i>on alerte</i></div><div class="w" id="jan">Janvier<i>on confirme</i></div></div></div>
  <div class="txt" id="t6"><small class="w">3 · IL DIT QUOI FAIRE</small><b><span class="m"><span class="w">Où agir.</span></span><br><span class="m"><em class="w">Sur quoi.</em></span></b></div>

  <div class="panel" id="s2"><img id="dp" src="img/dp/00.png">
    <div class="s2t"><p class="w" id="s2a">Septembre :<br><b>il faut décider.</b></p><p class="w" id="s2b">Le rapport arrive…</p></div>
    <div class="cal"><div class="pg back" style="--i:2"></div><div class="pg back" style="--i:1"></div>
      <div class="pg" id="pgcur"><div class="pg-h" id="pgm">Septembre</div><div class="pg-b"><span id="pgr">RENTRÉE</span>
        <div id="pgdoc">{icon("doc", 150, "#13294B", 1.6)}<b>Le rapport</b></div></div></div>
      <div class="pg fly" id="pgfly"><div class="pg-h" id="pgflym">Septembre</div><div class="pg-b"></div></div>
      <div class="stamp" id="stamp">TROP TARD</div></div>
  </div>
  <div class="panel" id="s3"><div class="logo" id="logo"><img src="../maquettes/img/logo-mark.png"></div>
    <div class="s3t"><span class="m"><b class="w">Kalantigui</b></span><span class="m"><p class="w">Anticiper le décrochage,</p></span><span class="m"><p class="w"><em>région par région.</em></p></span></div></div>
  <div class="panel" id="s7">
    <div id="s7in"><div class="dev" id="lap"><div class="lab7">Ordinateur</div><div class="lap-s"><div class="lap-in"><img src="../maquettes/img/bureau.jpg" id="lapimg"></div></div><div class="lap-b"></div></div>
    <div class="dev" id="pho"><div class="lab7">Téléphone</div><div class="pho-f"><div class="pho-sb"><span>9:41</span><i id="plane">{icon("plane", 22, "#13294B", 2.4)}</i></div>
      <div class="pho-sc"><img src="../maquettes/img/carte.jpg" id="pho1"><img src="../maquettes/img/hors-ligne.jpg" id="pho2"></div></div>
      <div class="avion" id="avion">{icon("plane", 26, "#ffffff")}<span>Mode avion</span></div></div>
    <div class="dev" id="fic"><div class="lab7">Papier</div><img src="../maquettes/img/fiche-1.png"></div>
    <div id="ringoff"></div></div>
    <div class="s7t w" id="s7t">Même <em>sans internet.</em></div>
    <div class="s7c w" id="s7c">L'appli répond quand même.</div>
  </div>
  <div class="panel" id="s8">
    <div class="s8t" id="s8t"><span class="m"><b class="w">Avant la rentrée.</b></span><b class="w"><em>Pas après.</em></b></div>
    <div class="end" id="end"><div class="logo sm"><img src="../maquettes/img/logo-mark.png"></div>
      <div class="end-t"><b>Kalantigui · Décrochage</b><p>Équipe Biiga · Data Challenge Burkina</p><p class="url">{URL}</p></div>
      <div class="qr">{qr_svg("https://" + URL)}</div></div>
  </div>
  <div id="vig"></div>
  <svg id="grain" width="1920" height="1080"><filter id="gn"><feTurbulence id="gt" type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="1"/><feColorMatrix type="saturate" values="0"/></filter><rect width="1920" height="1080" filter="url(#gn)"/></svg>
  <div id="fade"></div>
</div>
<script>const STAGE = {json.dumps(STAGE)}; const SCALE = {SCALE}; const SC = {json.dumps(SCENES)}; const REGIONS = {json.dumps(regions)}; const MONTHS = {json.dumps(months)};</script>
<script>{(HERE / "film.js").read_text()}</script></body></html>'''
    (HERE / "film.html").write_text(page, encoding="utf-8")
    print("film.html", len(page) // 1024, "ko,", len(dots), "écoles,", sum(d[2] for d in dots), "éteintes")


if __name__ == "__main__":
    build()

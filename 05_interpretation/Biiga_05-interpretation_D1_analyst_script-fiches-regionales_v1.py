"""One-page regional sheet (A4) for a regional director: situation, trend, risk, levers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import os
import sys
import unicodedata

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from pypdf import PdfWriter
import json
import shutil
import textwrap

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]
SHORT = [y[2:4] + "/" + y[7:] for y in YEARS]
BLUE, BAND, NAT = "#2a78d6", "#b7d3f6", "#c3c2b7"
INK, INK2, MUTED, GRID, SURFACE, TILE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb", "#f0efec"
RISK = {"élevé": ("#d03b3b", "⚠"), "moyen": ("#fab219", "!"), "faible": ("#0ca30c", "✓")}
LEVERS = {
    "Effondrement": [
        "Rouvrir de façon sécurisée et ouvrir des espaces temporaires d'apprentissage (chantier 2 du ministère).",
        "Réinscrire les élèves déplacés là où ils vivent maintenant.",
    ],
    "Choc puis reprise partielle": [
        "Accompagner le retour : suivre les élèves revenus dans les écoles rouvertes, organiser le rattrapage.",
        "Offrir une passerelle aux enfants sortis de l'école (centres SSA/P, chantier 9).",
    ],
    "Érosion": [
        "Chercher les causes hors insécurité : visites dans les écoles où les effectifs du CM1-CM2 baissent.",
        "Suivre chaque année les sorties en cours de cycle, avant qu'elles ne deviennent des abandons.",
    ],
    "Stabilité / accueil": [
        "Garder des places pour les élèves déplacés accueillis (classes, enseignants).",
        "Maintenir le suivi annuel : la région n'est pas à l'abri d'un recul.",
    ],
}


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


def fr(v, nd=0, sign=False):
    s = f"{v:+,.{nd}f}" if sign else f"{v:,.{nd}f}"
    return s.replace(",", " ").replace(".", ",")


def pts(v):
    return f"{fr(v, 1, True)} point" + ("s" if abs(v) >= 2 else "")


def load():
    p = pd.read_csv(chemins.path("panel_region_annee_2025.csv"))
    p["cle"] = p.region.map(key)
    fc = pd.read_csv(chemins.path("P9_prevision_2025_26_alerte.csv"))
    fc["cle"] = fc.cle.astype(str)
    ex = pd.read_csv(chemins.path("P1_sorties_excedentaires.csv"))
    ex["cle"] = ex.iloc[:, 0].map(key)
    typology = pd.read_csv(chemins.path("P2_typologie_regions.csv"))
    typology["cle"] = typology.region.map(key)
    prob = pd.read_csv(chemins.path("P11_probabilites_alerte.csv"))
    acled = pd.read_csv(chemins.path("acled_region_annee.csv"))
    pov = pd.read_csv(chemins.path("pauvrete_ehcvm_2021_regions.csv"))
    pov["cle"] = pov.region.map(key)
    return p, fc, ex, typology, prob, acled, pov


def risk_level(pct):
    return "élevé" if pct >= 40 else ("moyen" if pct >= 15 else "faible")


def tile(fig, x, y, w, h, value, label, sub):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.008",
                                      transform=fig.transFigure, facecolor=TILE, edgecolor="none"))
    fig.text(x + 0.012, y + h - 0.016, label, fontsize=7.6, color=INK2, va="top")
    fig.text(x + 0.012, y + h * 0.42, value, fontsize=16, color=INK, va="center", fontweight="bold")
    fig.text(x + 0.012, y + 0.010, sub, fontsize=7, color=INK2, va="bottom")


def content(region_key, data):
    p, fc, ex, typology, prob, acled, pov = data
    r = p[p.cle == region_key].set_index("annee").loc[YEARS]
    n = p[p.region == "NATIONAL"].set_index("annee").loc[YEARS]
    name25, old = r.region_2025.iloc[0], r.region.iloc[0].title().replace("Du", "du")
    f = fc[fc.cle == region_key].iloc[0]
    e = ex[ex.cle == region_key].iloc[0]
    t = typology[typology.cle == region_key].iloc[0]
    profile = {1: "Choc puis reprise partielle", 2: "Effondrement", 3: "Érosion", 4: "Stabilité / accueil"}[int(t.groupe_k4)]
    pr26 = float(prob.set_index("region_2025").loc[name25, "rentrée 2026/27"])
    level = risk_level(pr26)
    inc = acled[acled.cle == region_key].set_index("annee").incidents
    poverty = float(pov.set_index("cle").loc[region_key, "incidence_pauvrete_2021_pct"])

    tap0, tap1, tap21 = r.TAP_T.iloc[0], r.TAP_T.iloc[-1], r.TAP_T.loc["2021-2022"]
    el_max, el_now = r.eleves_T.max(), r.eleves_T.iloc[-1]
    ec_worst = (r.ecoles / r.ecoles.cummax() - 1).min() * 100
    g, fgl = r.TAP_G.iloc[-1], r.TAP_F.iloc[-1]
    inc24, inc25 = inc.get("2024-2025", np.nan), inc.get("2025-2026", np.nan)

    facts = [f"Le taux d'achèvement est passé de {fr(tap0, 1)} % en 2015/16 à {fr(tap1, 1)} % en 2024/25 "
             f"({pts(tap1 - tap0)}), contre {fr(n.TAP_T.iloc[-1], 1)} % au niveau national."]
    if ec_worst <= -30:
        facts.append(f"Jusqu'à {fr(-ec_worst)} % des écoles ont été perdues au pire moment de la crise.")
    elif tap1 - tap21 <= -8:
        closed = ("sans fermeture d'écoles" if -ec_worst < 1 else
                  f"sans fermeture massive d'écoles (au plus {fr(-ec_worst)} % fermées en même temps)")
        facts.append(f"Le recul ({pts(tap1 - tap21)} depuis 2021/22) s'est produit {closed} : "
                     "l'insécurité n'explique pas tout.")
    if not np.isnan(inc25) and max(inc24, inc25) < 30:
        facts.append(f"Les incidents sécuritaires restent rares : {fr(inc24)} entre oct. 2024 et sept. 2025, "
                     f"{fr(inc25)} entre oct. 2025 et sept. 2026.")
    elif not np.isnan(inc25) and inc24 > 0:
        trend = "ont presque doublé" if inc25 >= 1.8 * inc24 else ("ont augmenté" if inc25 > 1.10 * inc24 else
                                                                  ("ont baissé" if inc25 < 0.90 * inc24 else "sont stables"))
        facts.append(f"Les incidents sécuritaires {trend} : {fr(inc24)} entre oct. 2024 et sept. 2025, "
                     f"{fr(inc25)} entre oct. 2025 et sept. 2026.")
    gap = fgl - g
    who = "les garçons achèvent moins que les filles" if gap > 1 else (
        "les filles achèvent moins que les garçons" if gap < -1 else "garçons et filles achèvent autant")
    facts.append(f"En 2024/25, {who} ({fr(g, 1)} % contre {fr(fgl, 1)} %).")
    levers = list(LEVERS[profile])
    if profile == "Stabilité / accueil":
        levers = []
        if e.cumul_17_18_a_23_24 < 0:
            levers.append("Région d'accueil : garder des places pour les élèves déplacés (classes, enseignants).")
        if tap1 < 60:
            levers.append(f"Achèvement stable mais modeste ({fr(tap1, 1)} %) : leviers structurels (cantines endogènes, "
                          "chantier 5 ; suivi des élèves en retard d'âge).")
        if tap1 - tap21 <= -8:
            levers.append(f"Comprendre le recul récent ({pts(tap1 - tap21)} depuis 2021/22) : visites dans les écoles "
                          "où les effectifs du CM1-CM2 baissent.")
        levers.append("Maintenir le suivi annuel : la région n'est pas à l'abri d'un recul.")
    if level == "élevé":
        levers.append("Risque élevé pour 2026/27 : préparer dès maintenant un plan de continuité (lieux de repli, "
                      "enseignants mobiles, liste des élèves à suivre).")
    return {k: v for k, v in locals().items() if k in ('r', 'n', 'name25', 'old', 'f', 'e', 't', 'profile', 'pr26', 'level', 'inc', 'poverty', 'tap0', 'tap1', 'tap21', 'el_max', 'el_now', 'ec_worst', 'g', 'fgl', 'inc24', 'inc25', 'facts', 'levers')}


C1, C2, C3 = "#104281", "#3987e5", "#86b6ef"
FG, FG2, FG3, LINE, EDGE, CARD, BAD, NATC = "#0f172a", "#475569", "#7d8799", "#e3e7ed", "#cfd5de", "#f4f6f9", "#b42318", "#b9c2cf"
Z2, Z3 = "#dfe4eb", "#c3cbd7"
PRIORITY_LABELS = {1: ("Priorité 1", "agir maintenant"), 2: ("Priorité 2", "veille renforcée"), 3: ("Priorité 3", "consolider")}
ACTION_NAME = {"violence": "l'insécurité", "deplaces": "l'accueil des déplacés", "pauvrete": "la pauvreté", "faim": "la faim",
              "meres": "l'instruction des mères", "grossesses": "les grossesses précoces", "prescolaire": "le préscolaire"}


def _style():
    plt.rcParams.update({"font.family": ["Inter"], "font.size": 9, "axes.edgecolor": EDGE,
                         "axes.labelcolor": FG2, "xtick.color": FG3, "ytick.color": FG3, "pdf.fonttype": 42})


def _card(fig, x, y, w, h):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, facecolor=CARD, edgecolor="none", zorder=-5))


def _clean_axes(ax):
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(length=0, labelsize=7.5)
    ax.set_facecolor("none")


def score_color(v):
    return C1 if v >= 50 else (C2 if v >= 25 else C3)


def make(region_key, dataset, out):
    _style()
    R = {r["cle"]: r for r in dataset["regions"]}
    r, sg, fd_entry = R[region_key], dataset["score_global"], dataset["facteur_dominant"]["par_region"][region_key]
    defs = {d["id"]: d for d in dataset["facteurs_def"]}
    dominant = fd_entry["dominant"]
    s = sg["par_region"][region_key]
    p = r["probabilites"]["ref_2026_27"]
    tap = r["tap"][-1]
    rank = 1 + sum(1 for k, v in sg["par_region"].items() if v > s)
    sudden, slow = 50 * p / 100, 50 * (1 - tap / 100)
    tier = "élevé" if s >= 50 else ("moyen" if s >= 25 else "faible")

    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    L, W = 0.06, 0.88

    fig.text(L, 0.968, "FICHE RÉGIONALE · RISQUE DE DÉCROCHAGE AU PRIMAIRE · RENTRÉE 2026/27", fontsize=7.5, color=FG3, va="top", fontweight="bold")
    fig.text(L, 0.950, r["nom"], fontsize=25, fontweight="bold", color=FG, va="top")
    label_text, subtitle = PRIORITY_LABELS[r["priorite"]]
    fig.patches.append(FancyBboxPatch((L, 0.9035), 0.012, 0.0085, boxstyle="round,pad=0,rounding_size=0.002",
                                      transform=fig.transFigure, facecolor=[C1, C2, C3][r["priorite"] - 1], edgecolor="none"))
    fig.text(L + 0.018, 0.912, f"{label_text} · {subtitle} · ancienne région {r['ancienne']}", fontsize=9.5, color=FG2, va="top")

    y0, h0 = 0.745, 0.145
    _card(fig, L, y0, W, h0)
    fig.text(L + 0.025, y0 + h0 - 0.02, "Score global de risque", fontsize=10.5, fontweight="bold", color=FG, va="top")
    fig.text(L + W - 0.025, y0 + h0 - 0.02, f"{rank}{'re' if rank == 1 else 'e'} sur 13 · {tier}", fontsize=8.5, color=FG3, va="top", ha="right")
    fig.text(L + 0.025, y0 + 0.058, f"{s}", fontsize=40, fontweight="bold", color=score_color(s), va="baseline")
    fig.text(L + 0.025 + 0.041 * len(str(s)) + 0.012, y0 + 0.058, "/ 100", fontsize=13, color=FG3, va="baseline")
    bx, bw, by = L + 0.30, W - 0.325, y0 + 0.075
    fig.patches.append(FancyBboxPatch((bx, by), bw, 0.016, boxstyle="round,pad=0,rounding_size=0.004", transform=fig.transFigure, facecolor="white", edgecolor="none"))
    fig.patches.append(FancyBboxPatch((bx, by), bw * sudden / 100, 0.016, boxstyle="round,pad=0,rounding_size=0.004", transform=fig.transFigure, facecolor=FG, edgecolor="none"))
    fig.patches.append(FancyBboxPatch((bx + bw * sudden / 100, by), bw * slow / 100, 0.016, boxstyle="round,pad=0,rounding_size=0.004", transform=fig.transFigure, facecolor=Z3, edgecolor="none"))
    for yq, col in [(by - 0.0195, FG), (by - 0.0365, Z3)]:
        fig.patches.append(FancyBboxPatch((bx, yq), 0.009, 0.0065, boxstyle="round,pad=0,rounding_size=0.0015",
                                          transform=fig.transFigure, facecolor=col, edgecolor="none"))
    fig.text(bx + 0.016, by - 0.012, f"Chute des effectifs (violence) : {fr(sudden)}", fontsize=8.2, color=FG, va="top")
    fig.text(bx + 0.016, by - 0.029, f"Enfants qui n'achèvent pas le primaire : {fr(slow)}", fontsize=8.2, color="#8a94a5", va="top")
    fig.text(L + 0.025, y0 + 0.018, f"Moitié risque de chute des effectifs ({fr(p)} %), moitié part d'enfants qui n'achèvent pas ({fr(100 - tap, 1)} %).",
             fontsize=7.8, color=FG3)

    y1, h1 = 0.585, 0.145
    _card(fig, L, y1, W, h1)
    fig.text(L + 0.025, y1 + h1 - 0.02, "Sur quoi agir", fontsize=10.5, fontweight="bold", color=FG, va="top")
    if dominant:
        fig.text(L + W - 0.025, y1 + h1 - 0.02, "poids de chaque facteur", fontsize=8.5, color=FG3, va="top", ha="right")
    if dominant:
        fig.text(L + 0.025, y1 + h1 - 0.047, f"Agir sur {ACTION_NAME[dominant]}", fontsize=14, fontweight="bold", color=FG, va="top")
        lever = textwrap.wrap(defs[dominant]["levier"], 52)
        for i, ln in enumerate(lever[:3]):
            fig.text(L + 0.025, y1 + h1 - 0.075 - i * 0.016, ln, fontsize=9, color=FG2, va="top")
        if fd_entry["second"]:
            fig.text(L + 0.025, y1 + 0.018, f"Ensuite : {ACTION_NAME[fd_entry['second']]}", fontsize=8.5, color=FG3)
    else:
        fig.text(L + 0.025, y1 + h1 - 0.047, "Aucun facteur au-dessus de la moyenne", fontsize=13, fontweight="bold", color=FG, va="top")
        fig.text(L + 0.025, y1 + h1 - 0.075, "Consolider ce qui marche.", fontsize=9, color=FG2, va="top")
    top = sorted(fd_entry["contributions"].items(), key=lambda kv: -kv[1])[:4] if dominant else []
    mx = max(abs(v) for _, v in fd_entry["contributions"].items()) or 1
    for i, (fid, v) in enumerate(top):
        yy = y1 + h1 - 0.052 - i * 0.022
        fig.text(L + 0.49, yy, defs[fid]["libelle"], fontsize=8.2, color=FG2, va="center")
        fig.patches.append(FancyBboxPatch((L + 0.68, yy - 0.004), 0.15, 0.008, boxstyle="round,pad=0,rounding_size=0.003", transform=fig.transFigure, facecolor="white", edgecolor="none"))
        if v > 0:
            fig.patches.append(FancyBboxPatch((L + 0.68, yy - 0.004), 0.15 * v / mx, 0.008, boxstyle="round,pad=0,rounding_size=0.003",
                                              transform=fig.transFigure, facecolor=FG if fid == dominant else C3, edgecolor="none"))

    tr = sg["trajectoire"]
    year_labels, sc, ch = tr["annees"], tr["par_region"][region_key]["score"], tr["par_region"][region_key]["chute"]
    y2, h2 = 0.375, 0.19
    _card(fig, L, y2, W, h2)
    fig.text(L + 0.025, y2 + h2 - 0.02, "Le score, année par année", fontsize=10.5, fontweight="bold", color=FG, va="top")
    fig.text(L + W - 0.025, y2 + h2 - 0.02, f"{year_labels[-1]} prévu : {sc[-1]}", fontsize=9, color=C1, va="top", ha="right", fontweight="bold")
    ax = fig.add_axes([L + 0.04, y2 + 0.062, W - 0.10, h2 - 0.105])
    n = len(year_labels)
    ax.axhspan(50, 100, color=Z3, alpha=.45, lw=0)
    ax.axhspan(25, 50, color=Z2, alpha=.45, lw=0)
    ax.plot(range(n - 1), sc[:-1], color=FG, lw=2, solid_capstyle="round", zorder=3)
    ax.plot([n - 2, n - 1], sc[-2:], color=FG, lw=2, ls=(0, (3, 3)), zorder=3)
    for i in range(n - 1):
        if ch[i] == 1:
            ax.scatter(i, sc[i], s=70, facecolor="white", edgecolor=BAD, linewidth=2, zorder=4)
        else:
            ax.scatter(i, sc[i], s=14, color=FG, zorder=4)
    ax.scatter(n - 1, sc[-1], s=200, color=C1, alpha=.18, lw=0, zorder=3)
    ax.scatter(n - 1, sc[-1], s=60, facecolor="white", edgecolor=C1, linewidth=2.2, zorder=5)
    ax.annotate(f"{sc[-1]}", (n - 1, sc[-1]), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=10, fontweight="bold", color=C1)
    ax.set_xlim(-0.3, n - 0.7)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50])
    ax.set_xticks(range(n))
    ax.set_xticklabels(year_labels[:-1] + [f"{year_labels[-1]}\nprévu"], fontsize=7.5)
    ax.get_xticklabels()[-1].set_color(C1)
    ax.get_xticklabels()[-1].set_fontweight("bold")
    _clean_axes(ax)
    fig.text(L + 0.025, y2 + 0.013, "Cercle rouge : chute des effectifs de plus de 5 % observée cette année-là   ·   chaque point est calculé avec ce qu'on savait cette année-là",
             fontsize=7.3, color=FG3)

    y3, h3 = 0.185, 0.17
    wl = 0.52
    _card(fig, L, y3, wl, h3)
    _card(fig, L + wl + 0.015, y3, W - wl - 0.015, h3)
    fig.text(L + 0.025, y3 + h3 - 0.02, "Achèvement du primaire", fontsize=10, fontweight="bold", color=FG, va="top")
    fig.text(L + wl - 0.02, y3 + h3 - 0.02, f"{fr(tap, 1)} % en 24/25", fontsize=8.5, color=FG3, va="top", ha="right")
    for xl, col, region_name in [(L + 0.025, FG, r["nom"]), (L + 0.30, NATC, "Pays")]:
        fig.patches.append(FancyBboxPatch((xl, y3 + h3 - 0.0465), 0.02, 0.0022, boxstyle="round,pad=0,rounding_size=0.001",
                                          transform=fig.transFigure, facecolor=col, edgecolor="none"))
        fig.text(xl + 0.026, y3 + h3 - 0.04, region_name, fontsize=7.8, color=FG2, va="top")
    ax = fig.add_axes([L + 0.035, y3 + 0.035, wl - 0.10, h3 - 0.095])
    xs = range(len(dataset["annees"]))
    ax.plot(xs, dataset["national"]["tap"], color=NATC, lw=1.8, label="Pays")
    ax.plot(xs, r["tap"], color=FG, lw=2.2, label=r["nom"])
    pv = r["prevision_2025_26"]
    k = len(dataset["annees"])
    ax.vlines(k, pv["basse"], pv["haute"], color=Z3, lw=7)
    ax.plot([k - 1, k], [r["tap"][-1], pv["centrale"]], color=FG, lw=1.5, ls=(0, (3, 3)))
    ax.scatter(k, pv["centrale"], s=26, facecolor="white", edgecolor=FG, lw=1.5, zorder=4)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 50, 100])
    ax.set_xticks([0, k - 1, k])
    ax.set_xticklabels([dataset["annees"][0], dataset["annees"][-1], "25/26\nprévu"], fontsize=7.5)
    ax.grid(axis="y", color=LINE, lw=.6)
    _clean_axes(ax)
    xv = L + wl + 0.015
    fig.text(xv + 0.02, y3 + h3 - 0.02, "Violence", fontsize=10, fontweight="bold", color=FG, va="top")
    fig.text(L + W - 0.02, y3 + h3 - 0.02, "incidents / an", fontsize=8.5, color=FG3, va="top", ha="right")
    ax = fig.add_axes([xv + 0.02, y3 + 0.03, W - wl - 0.055, h3 - 0.09])
    inc = r["incidents"]
    ax.bar(range(len(inc)), inc, color=[C3] * (len(inc) - 1) + [FG], width=.72)
    ax.annotate(fr(inc[-1]), (len(inc) - 1, inc[-1]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8, fontweight="bold", color=FG)
    ax.set_xticks([0, len(inc) - 1])
    ax.set_xticklabels([dataset["annees_violence"][0], dataset["annees_violence"][-1]], fontsize=7.5)
    ax.set_yticks([])
    _clean_axes(ax)

    y4 = 0.168
    fig.text(L, y4, "Leviers", fontsize=10.5, fontweight="bold", color=FG, va="top")
    lever_texts = (r["leviers"] + r["leviers_facteurs"])[:3]
    yy = y4 - 0.022
    for i, lv in enumerate(lever_texts):
        lines = textwrap.wrap(lv, 105)
        fig.text(L, yy, f"{i + 1}", fontsize=9, fontweight="bold", color=C1, va="top")
        for j, ln in enumerate(lines[:2]):
            fig.text(L + 0.02, yy - j * 0.0145, ln, fontsize=8.6, color=FG, va="top")
        yy -= 0.0145 * min(2, len(lines)) + 0.006
    notes = ["Score = 100 × (0,5 × probabilité de chute des effectifs + 0,5 × part d'enfants qui n'achèvent pas). "
             "Il résume ; la priorité de la matrice reste la règle pour cibler."]
    if "+" in r["nom"]:
        notes.append(f"Région coupée en 2025 ({r['nom']}) : les données ne permettent pas de séparer ses parties.")
    yy = min(yy - 0.004, 0.058)
    for ln in notes:
        fig.text(L, yy, ln, fontsize=6.8, color=FG3, va="top")
        yy -= 0.012
    fig.text(L, 0.025, "Sources : DGESS (données du Data Challenge Burkina) ; ACLED, INSD et IGB via HDX ; INSD, EHCVM 2021. "
             "Calculs de l'équipe, novembre 2026.", fontsize=6.5, color=FG3)
    assert yy > 0.03, f"la fiche {r['nom']} déborde : réduire le texte"
    slug = key(r["nom"]).lower()
    fig.savefig(chemins.fiche(slug, "pdf"))
    fig.savefig(chemins.fiche(slug, "png"), dpi=110)
    plt.close(fig)
    return slug, r["nom"]


def main():
    out = chemins.folder("05_interpretation/fiches")
    os.makedirs(out, exist_ok=True)
    dataset = json.load(open("dashboard/public/data/tableau_de_bord.json", encoding="utf-8"))
    keys = sys.argv[1:] or [r["cle"] for r in sorted(dataset["regions"], key=lambda r: -dataset["score_global"]["par_region"][r["cle"]])]
    os.makedirs("dashboard/public/fiches", exist_ok=True)
    booklet = PdfWriter()
    for k in keys:
        slug, region_name = make(k, dataset, out)
        shutil.copy2(chemins.fiche(slug, "pdf"), f"dashboard/public/fiches/{k}.pdf")
        booklet.append(chemins.fiche(slug, "pdf"))
        print("fiche :", region_name)
    if not sys.argv[1:]:
        booklet.write(chemins.path("fiches_regionales_13.pdf"))
        print("livret : 05_interpretation/Biiga_05-interpretation_D1_analyst_fiches-regionales-13_v1.pdf (régions de la plus urgente à la moins urgente)")


if __name__ == "__main__":
    main()

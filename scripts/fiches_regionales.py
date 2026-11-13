"""One-page regional sheet (A4) for a regional director: situation, trend, risk, levers.

Every figure comes from the analysis tables of analyse/; the text is built by
fixed rules from those figures (no free text, no language model), so each
sentence can be traced back to a number.

Usage: python fiches_regionales.py [CLE ...]   e.g. NORD ; no argument = all 13 regions.
Writes analyse/fiches/fiche_<nom>.pdf and .png.
"""
import os
import sys
import unicodedata

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

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
    """Points of percentage, with the French agreement: singular below 2."""
    return f"{fr(v, 1, True)} point" + ("s" if abs(v) >= 2 else "")


def load():
    p = pd.read_csv("analyse/panel_region_annee_2025.csv")
    p["cle"] = p.region.map(key)
    fc = pd.read_csv("analyse/P9_prevision_2025_26_alerte.csv")
    fc["cle"] = fc.cle.astype(str)
    ex = pd.read_csv("analyse/P1_sorties_excedentaires.csv")
    ex["cle"] = ex.iloc[:, 0].map(key)
    typo = pd.read_csv("analyse/P2_typologie_regions.csv")
    typo["cle"] = typo.region.map(key)
    prob = pd.read_csv("analyse/P11_probabilites_alerte.csv")
    acled = pd.read_csv("analyse/acled_region_annee.csv")
    pov = pd.read_csv("data/externe_propre/pauvrete_ehcvm_2021_regions.csv")
    pov["cle"] = pov.region.map(key)
    return p, fc, ex, typo, prob, acled, pov


def risk_level(pct):
    return "élevé" if pct >= 40 else ("moyen" if pct >= 15 else "faible")


def tile(fig, x, y, w, h, value, label, sub):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.008",
                                      transform=fig.transFigure, facecolor=TILE, edgecolor="none"))
    fig.text(x + 0.012, y + h - 0.016, label, fontsize=7.6, color=INK2, va="top")
    fig.text(x + 0.012, y + h * 0.42, value, fontsize=16, color=INK, va="center", fontweight="bold")
    fig.text(x + 0.012, y + 0.010, sub, fontsize=7, color=INK2, va="bottom")


def contenu(cle, data):
    """Numbers, key facts and levers of one region: shared by the PDF fiche and the dashboard export."""
    p, fc, ex, typo, prob, acled, pov = data
    r = p[p.cle == cle].set_index("annee").loc[YEARS]
    n = p[p.region == "NATIONAL"].set_index("annee").loc[YEARS]
    name25, old = r.region_2025.iloc[0], r.region.iloc[0].title().replace("Du", "du")
    f = fc[fc.cle == cle].iloc[0]
    e = ex[ex.cle == cle].iloc[0]
    t = typo[typo.cle == cle].iloc[0]
    profile = {1: "Choc puis reprise partielle", 2: "Effondrement", 3: "Érosion", 4: "Stabilité / accueil"}[int(t.groupe_k4)]
    pr26 = float(prob.set_index("region_2025").loc[name25, "rentrée 2026/27"])
    level = risk_level(pr26)
    inc = acled[acled.cle == cle].set_index("annee").incidents
    poverty = float(pov.set_index("cle").loc[cle, "incidence_pauvrete_2021_pct"])

    tap0, tap1, tap21 = r.TAP_T.iloc[0], r.TAP_T.iloc[-1], r.TAP_T.loc["2021-2022"]
    el_max, el_now = r.eleves_T.max(), r.eleves_T.iloc[-1]
    ec_worst = (r.ecoles / r.ecoles.cummax() - 1).min() * 100
    g, fgl = r.TAP_G.iloc[-1], r.TAP_F.iloc[-1]
    inc24, inc25 = inc.get("2024-2025", np.nan), inc.get("2025-2026", np.nan)

    # Rule-built key facts: each sentence comes from one number above.
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
        # The host-region lever only where the region gains pupils from elsewhere (negative excess exits).
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


def make(cle, data, out):
    c = contenu(cle, data)
    (r, n, name25, old, f, e, t, profile, pr26, level, inc, poverty, tap0, tap1, tap21, el_max, el_now, ec_worst, g, fgl, inc24, inc25, facts, levers) = (c[k] for k in ('r', 'n', 'name25', 'old', 'f', 'e', 't', 'profile', 'pr26', 'level', 'inc', 'poverty', 'tap0', 'tap1', 'tap21', 'el_max', 'el_now', 'ec_worst', 'g', 'fgl', 'inc24', 'inc25', 'facts', 'levers'))

    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor(SURFACE)
    fig.text(0.06, 0.965, "FICHE RÉGIONALE · DÉCROCHAGE SCOLAIRE AU PRIMAIRE", fontsize=8, color=MUTED, va="top")
    fig.text(0.06, 0.945, name25, fontsize=24, fontweight="bold", color=INK, va="top")
    fig.text(0.06, 0.902, f"Ancienne région : {old}   ·   Profil 2015-2025 : {profile}", fontsize=9.5, color=INK2, va="top")
    col, icon = RISK[level]
    fig.patches.append(FancyBboxPatch((0.62, 0.903), 0.32, 0.05, boxstyle="round,pad=0,rounding_size=0.01",
                                      transform=fig.transFigure, facecolor="none", edgecolor=col, linewidth=2))
    fig.text(0.635, 0.94, f"{icon}  Risque 2026/27 : {level.upper()}", fontsize=10.5, fontweight="bold", color=INK, va="top")
    fig.text(0.635, 0.919, f"Baisse des effectifs > 5 % : {fr(pr26)} % (indicatif)", fontsize=7,
             color=INK2, va="top")

    tw, gap_ = 0.205, 0.0167
    tiles = [
        (f"{fr(tap1, 1)} %", "Taux d'achèvement 2024/25", f"{pts(tap1 - tap0)} depuis 2015/16"),
        (f"≈ {fr(f.enfants_hors_CM2_estimes)}", "Enfants ≈ 11 ans hors CM2", "estimation, population INSD 2024"),
        (f"{fr(el_now)}", "Élèves du primaire 2024/25",
         "au plus haut depuis 2015/16" if el_now >= el_max else f"{fr((el_now / el_max - 1) * 100, 0, True)} % par rapport au maximum"),
        (f"{fr(e.cumul_17_18_a_23_24)}", "Sorties en excès 2017-2025", "élèves sortis plus que d'habitude")
        if e.cumul_17_18_a_23_24 >= 0 else
        (f"{fr(-e.cumul_17_18_a_23_24)}", "Élèves reçus en plus 2017-2025", "région d'accueil : moins de sorties que d'habitude"),
    ]
    for i, (v, l, s) in enumerate(tiles):
        tile(fig, 0.06 + i * (tw + gap_), 0.785, tw, 0.095, v, l, s)

    ax = fig.add_axes([0.08, 0.56, 0.52, 0.19])
    x = np.arange(10)
    ax.plot(x, n.TAP_T.values, color=NAT, linewidth=1.8, label="Burkina Faso")
    ax.plot(x, r.TAP_T.values, color=BLUE, linewidth=2.2, marker="o", markersize=3.5, label=name25)
    ax.vlines(10, f.fourchette_basse, f.fourchette_haute, color=BAND, linewidth=8)
    ax.scatter([10], [f.prevision_25_26], color=BLUE, s=22, zorder=3, edgecolor=SURFACE)
    ax.annotate(f"2025/26 (prévision)\n{fr(f.fourchette_basse)}–{fr(f.fourchette_haute)} %", (10, f.fourchette_haute),
                xytext=(0, 6), textcoords="offset points", ha="center", fontsize=6.8, color=INK2)
    ax.set_xticks(list(x) + [10])
    ax.set_xticklabels(SHORT + ["25/26"], fontsize=6.5, rotation=0)
    ax.set_ylim(0, max(100, f.fourchette_haute + 12))
    ax.set_title("Taux d'achèvement du primaire (%)", fontsize=9.5, loc="left", fontweight="bold")
    for a in [ax]:
        a.grid(color=GRID, linewidth=0.6)
        a.set_axisbelow(True)
        for s in ["top", "right"]:
            a.spines[s].set_visible(False)
        a.tick_params(colors=MUTED, labelsize=7)
    ax.legend(loc="lower left", fontsize=7, frameon=False)

    ax2 = fig.add_axes([0.68, 0.56, 0.26, 0.19])
    yrs = [f"{y}-{y + 1}" for y in range(2015, 2026)]
    vals = [inc.get(y, 0) for y in yrs]
    ax2.bar(range(len(yrs)), vals, color=[BLUE if y != "2025-2026" else INK for y in yrs], width=0.7)
    ax2.set_xticks(range(0, len(yrs), 2))
    ax2.set_xticklabels([yrs[i][2:4] + "/" + yrs[i][7:] for i in range(0, len(yrs), 2)], fontsize=6.5)
    ax2.set_title("Incidents sécuritaires (ACLED)\nd'octobre à septembre", fontsize=9, loc="left", fontweight="bold")
    ax2.annotate(fr(vals[-1]), (len(yrs) - 1, vals[-1]), xytext=(0, 3), textcoords="offset points", ha="center",
                 fontsize=7, color=INK)
    ax2.grid(axis="y", color=GRID, linewidth=0.6)
    ax2.set_axisbelow(True)
    for s in ["top", "right"]:
        ax2.spines[s].set_visible(False)
    ax2.tick_params(colors=MUTED, labelsize=7)

    import textwrap

    def block(y_top, title, lines):
        """Draw a titled box sized to its wrapped lines; return the y where the next block can start."""
        wrapped = [textwrap.wrap(ln, 112) for ln in lines]
        n_rows = sum(len(w) for w in wrapped)
        height = 0.048 + n_rows * 0.0165 + len(lines) * 0.004
        fig.patches.append(FancyBboxPatch((0.06, y_top - height), 0.88, height, boxstyle="round,pad=0,rounding_size=0.008",
                                          transform=fig.transFigure, facecolor=TILE, edgecolor="none"))
        fig.text(0.08, y_top - 0.014, title, fontsize=10, fontweight="bold", color=INK, va="top")
        yy = y_top - 0.042
        for wl in wrapped:
            for j, w in enumerate(wl):
                fig.text(0.085 if j == 0 else 0.1, yy, ("•  " if j == 0 else "") + w, fontsize=8.4, color=INK, va="top")
                yy -= 0.0165
            yy -= 0.004
        return y_top - height - 0.015

    y_next = block(0.505, "Ce qu'il faut retenir", facts)
    y_next = block(y_next, "Leviers proposés", levers)
    assert y_next > 0.125, f"la fiche {name25} déborde : réduire le texte"
    notes = [f"Pauvreté 2021 : {fr(poverty, 1)} % de la population sous le seuil (INSD, EHCVM 2021).",
             "La prévision 2025/26 reprend le taux 2024/25 ; sa fourchette à 80 % a couvert 73 % des cas passés.",
             "Le niveau de risque classe bien les régions (AUC 0,83 hors échantillon) ; la probabilité est indicative."]
    if "+" in name25:
        notes.insert(0, f"Région coupée en 2025 ({name25}) : les données ne permettent pas de séparer ses parties.")
    yy = min(0.12, y_next)
    for ln in notes:
        fig.text(0.06, yy, ln, fontsize=7, color=INK2, va="top")
        yy -= 0.015
    fig.text(0.06, 0.035, "Sources : DGESS (données du Data Challenge Burkina) ; ACLED, INSD et IGB via HDX ; INSD, EHCVM 2021. "
             "Calculs de l'équipe, novembre 2026.", fontsize=6.5, color=MUTED)
    slug = key(name25).lower()
    fig.savefig(f"{out}/fiche_{slug}.pdf")
    fig.savefig(f"{out}/fiche_{slug}.png", dpi=110)
    plt.close(fig)
    return slug


def main():
    out = "analyse/fiches"
    os.makedirs(out, exist_ok=True)
    data = load()
    keys = sys.argv[1:] or sorted(data[0][data[0].region != "NATIONAL"].cle.unique())
    for k in keys:
        print("fiche :", make(k, data, out))


if __name__ == "__main__":
    main()

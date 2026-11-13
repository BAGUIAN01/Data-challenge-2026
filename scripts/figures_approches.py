"""Figures for the two forecasting approaches that work: nowcast from open schools, cohort pipeline.

Usage: python figures_approches.py   (run from the project root, after approches_prevision.py and solution_prevision.py)
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # validated categorical order
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK, "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})


def fr(x, dec=1):
    """French number: thin space for thousands, decimal comma."""
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


def header(fig, main, sub):
    fig.text(0.01, 0.985, main, fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.01, 0.94, sub, fontsize=9.5, color=INK2, va="top")
    fig.text(0.01, 0.01, "Source : données du Data Challenge Burkina (DGESS), 2015/16 à 2024/25. Calculs de l'équipe.",
             fontsize=7.5, color=MUTED)


def nowcast():
    a = pd.read_csv("analyse/P12_nowcast_ecoles.csv")
    mean = a[a.annee == "moyenne"].iloc[0]
    a = a[a.annee != "moyenne"]
    x = np.arange(len(a))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 5.2))
    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.08, right=0.97)
    ax.bar(x - w / 2, a["effectifs_persistance_%"], w, color=SERIES[0], label="« Comme l'an passé »")
    ax.bar(x + w / 2, a["effectifs_ecoles_%"], w, color=SERIES[1], label="À partir des écoles ouvertes à la rentrée")
    for xi, v1, v2 in zip(x, a["effectifs_persistance_%"], a["effectifs_ecoles_%"]):
        ax.annotate(fr(v1), (xi - w / 2, v1), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8,
                    color=INK2)
        ax.annotate(fr(v2), (xi + w / 2, v2), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8,
                    color=INK2)
    ax.set_xticks(x, a.annee)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Erreur moyenne sur les effectifs régionaux (%)")
    ax.set_xlabel("Année prédite (pente apprise sur les années précédentes seulement)")
    ax.legend(loc="upper left", fontsize=8.5)
    header(fig, "Connaître les écoles ouvertes à la rentrée divise l'erreur par deux",
           f"Erreur moyenne sur les effectifs des 13 régions : {fr(mean['effectifs_ecoles_%'])} % contre "
           f"{fr(mean['effectifs_persistance_%'])} %. Le gain est le plus fort l'année du choc (22/23).\n"
           "Il ne vaut que pour les effectifs : sur le taux d'achèvement, aucun gain.")
    fig.savefig("analyse/figures/13_prevision_ecoles_ouvertes.png", dpi=200)
    plt.close(fig)


def cohorts():
    c = pd.read_csv("analyse/P12_cohortes_national.csv")
    pr = pd.read_csv("analyse/P12_projection_CM2.csv").iloc[0]
    x = list(range(len(c)))
    fig, ax = plt.subplots(figsize=(9, 5.4))
    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.09, right=0.84)
    ax.plot(x, c.CP1 / 1000, color=SERIES[0], marker="o", markersize=4.5, linewidth=2, label="CP1")
    ax.plot(x, c.CM2 / 1000, color=SERIES[1], marker="o", markersize=4.5, linewidth=2.4, label="CM2")
    nx = len(c)
    ax.plot([nx - 1, nx], [c.CM2.iloc[-1] / 1000, pr.central / 1000], color=SERIES[1], linewidth=2.4, linestyle="--")
    ax.errorbar([nx], [pr.central / 1000], yerr=[[(pr.central - pr.bas) / 1000], [(pr.haut - pr.central) / 1000]],
                fmt="o", color=SERIES[1], markerfacecolor=SURFACE, markersize=6, capsize=4, linewidth=1.4)
    ax.annotate(f"25/26 : ≈ {fr(pr.central / 1000, 0)} 000\n(de {fr(pr.bas / 1000, 0)} 000 à {fr(pr.haut / 1000, 0)} 000)",
                (nx, pr.central / 1000), xytext=(10, 0), textcoords="offset points", va="center", fontsize=8.5,
                color=INK2, annotation_clip=False)
    ax.annotate("CP1", (nx - 1, c.CP1.iloc[-1] / 1000), xytext=(8, 0), textcoords="offset points", va="center",
                fontsize=9, color=SERIES[0], fontweight="bold")
    ax.annotate("CM2", (0, c.CM2.iloc[0] / 1000), xytext=(-8, 0), textcoords="offset points", va="center", ha="right",
                fontsize=9, color=SERIES[1], fontweight="bold", annotation_clip=False)
    ax.set_xticks(x + [nx], list(c.annee) + ["25/26"])
    ax.set_xlim(-0.6, nx + 0.4)
    ax.set_ylim(0, 850)
    ax.set_ylabel("Élèves (milliers), public et privé")
    header(fig, "Le nombre d'élèves en CM2 devrait remonter en 2025/26",
           "Projection : élèves de CM1 en 2024/25 (441 000) × dernier taux de passage au CM2 (86 %). Fourchette : pire et meilleur\n"
           "passage observés ; elle n'a tenu que 4 années sur 7. Hors nouveau choc, et ce n'est pas un taux d'achèvement.")
    fig.savefig("analyse/figures/14_projection_cohortes.png", dpi=200)
    plt.close(fig)




PRIO = {1: ("Priorité 1 : agir maintenant", "#104281"), 2: ("Priorité 2 : veille renforcée", "#3987e5"),
        3: ("Priorité 3 : consolider", "#b7d3f6")}
# Label offsets in points (dx, dy, horizontal alignment), set by hand to avoid collisions.
LABEL = {"Liptako + Soum": (0, -13, "center"), "Goulmou + Sirba + Tapoa": (-4, 10, "center"),
         "Koulsé": (6, 8, "left"), "Bankui + Sourou": (0, -13, "center"), "Yaadga": (0, 9, "center"),
         "Nakambé": (8, 0, "left"), "Tannounyan": (-8, 0, "right"), "Guiriko": (8, 2, "left"),
         "Djôrô": (4, 9, "left"), "Oubri": (-8, 0, "right"), "Nazinon": (0, 9, "center"),
         "Nando": (8, -3, "left"), "Kadiogo": (0, 9, "center")}


def matrix():
    m = pd.read_csv("analyse/P13_matrice_priorite_2026_27.csv")
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(top=0.80, bottom=0.11, left=0.09, right=0.97)
    tap_nat = 51.6
    ax.axvline(tap_nat, color=AXIS, linewidth=1.2, linestyle="--", zorder=1)
    ax.axhline(40, color=AXIS, linewidth=1.2, linestyle="--", zorder=1)
    ax.axhline(15, color=GRID, linewidth=1.0, linestyle=":", zorder=1)
    ax.text(tap_nat + 1, 99, "Moyenne nationale (51,6 %)", fontsize=8, color=MUTED, va="top")
    ax.text(99, 41, "Risque élevé (≥ 40 %)", fontsize=8, color=MUTED, ha="right", va="bottom")
    ax.text(99, 16, "Risque moyen (≥ 15 %)", fontsize=8, color=MUTED, ha="right", va="bottom")
    for k, (lab, col) in PRIO.items():
        s = m[m.priorite == k]
        ax.scatter(s.TAP_24_25, s.probabilite_baisse_2026_27 * 100, s=90, color=col, edgecolor=INK2,
                   linewidth=0.6, label=lab, zorder=3)
    for _, r in m.iterrows():
        dx, dy, ha = LABEL[r.region_2025]
        ax.annotate(r.region_2025, (r.TAP_24_25, r.probabilite_baisse_2026_27 * 100), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, va="center", fontsize=8.5, color=INK)
    ax.set_xlim(0, 100)
    ax.set_ylim(-4, 100)
    ax.set_xlabel("Taux d'achèvement du primaire 2024/25 (%) : plus c'est à gauche, plus le retard est grand")
    ax.set_ylabel("Probabilité d'une baisse des effectifs > 5 % (%)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.93), fontsize=8.5)
    header(fig, "Où agir en premier à la rentrée 2026/27",
           "Priorité 1 = retard d'achèvement ET risque qui monte : 5 régions, 63 % des enfants qui n'atteignent pas le CM2.\n"
           "Rejouée sur 2019-2024, elle désignait 35 % des régions, mais 71 % des fortes baisses de l'année suivante.")
    fig.texts[-1].set_text("Sources : données du Data Challenge Burkina (DGESS) ; ACLED (HDX). Probabilité : régression "
                           "logistique sur la violence d'oct. 2025 à sept. 2026. Calculs de l'équipe.")
    fig.savefig("analyse/figures/15_matrice_priorite_2026_27.png", dpi=200)
    plt.close(fig)




COLS = [("violence", "Violence", "incidents_moy", "{:.0f}"), ("deplaces", "Déplacés\naccueillis", None, "{:.0f} %"),
        ("pauvrete", "Pauvreté", None, "{:.0f} %"), ("faim", "Faim", None, "{:.0f} %"),
        ("meres", "Femmes sans\ninstruction", None, "{:.0f} %"), ("grossesses", "Grossesses\nprécoces", None, "{:.0f} ‰"),
        ("cep", "Réussite\nau CEP", None, "{:.0f} %"), ("prescolaire", "Préscolaire", None, "{:.0f} %")]
TIER_COL = {1: "#104281", 2: "#8db8ee", 3: "#eef4fc"}


def factors():
    pr = pd.read_csv("analyse/P14_profil_facteurs.csv")
    n_rows, n_cols = len(pr), len(COLS)
    fig, ax = plt.subplots(figsize=(10, 7.6))
    fig.subplots_adjust(top=0.80, bottom=0.135, left=0.23, right=0.98)
    for i, (_, r) in enumerate(pr.iterrows()):
        for j, (f, _, disp, fmt) in enumerate(COLS):
            tier = int(r[f + "_niveau"])
            ax.add_patch(plt.Rectangle((j, i), 0.96, 0.92, color=TIER_COL[tier], linewidth=0))
            v = r[disp] if disp else r[f]
            ax.text(j + 0.48, i + 0.46, fr(v, 0).join(fmt.split("{:.0f}")) if "{:.0f}" in fmt else fmt.format(v),
                    ha="center", va="center", fontsize=8.5, color=SURFACE if tier == 1 else INK)
    ax.set_xlim(0, n_cols)
    ax.set_ylim(n_rows, 0)
    ax.set_xticks([j + 0.48 for j in range(n_cols)], [c[1] for c in COLS], fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.46 for i in range(n_rows)],
                  [f"{r.region_2025}  (P{int(r.priorite)})" for _, r in pr.iterrows()], fontsize=9)
    ax.tick_params(length=0)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=TIER_COL[1], label="Parmi les 4 régions les plus exposées"),
                       Patch(color=TIER_COL[2], label="Intermédiaire"),
                       Patch(color=TIER_COL[3], label="Parmi les 4 moins exposées")],
              loc="upper center", bbox_to_anchor=(0.45, -0.01), ncol=3, fontsize=8.5)
    header(fig, "Le décrochage n'a pas qu'une cause : profil de chaque région",
           "Régions classées par priorité (P1 à P3), puis par taux d'achèvement. Pour le CEP et le préscolaire, une valeur basse\n"
           "expose davantage. Djôrô, en priorité 3, cumule pourtant deux fragilités de fond : instruction des femmes et grossesses précoces.")
    fig.texts[-1].set_text("Grossesses précoces : naissances pour 1 000 filles de 15-19 ans. Faim : population en phase 3 ou plus.\n"
                           "Sources : DGESS (CEP 22/23-24/25, préscolaire 24/25) ; ACLED (incidents/an, 21/22-24/25) ; CONASUR 2022 ; "
                           "INSD EHCVM 2021 ; Cadre Harmonisé (21/22-23/24) ; EDS 2021.")
    fig.savefig("analyse/figures/16_profil_facteurs.png", dpi=200)
    plt.close(fig)


def calendar_fig():
    r = pd.read_csv("analyse/P16_signaux_fins.csv").set_index("variante")
    a = pd.read_csv("analyse/P16_alertes_calendrier.csv").set_index("region")
    stages = [("Total de l'année écoulée\n(référence, D12)", r.loc["Référence : violence (niveau, escalade)", "AUC"], "#b7d3f6"),
              ("Fin septembre :\n+ violence de juillet-septembre", r.loc["F2 + juillet-septembre", "AUC"], "#3987e5"),
              ("Début janvier :\n+ violence d'octobre-décembre", r.loc["F3 + rentrée (oct.-déc.)", "AUC"], "#104281")]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    fig.subplots_adjust(top=0.78, bottom=0.12, left=0.08, right=0.97)
    x = range(len(stages))
    ax.bar(x, [s[1] for s in stages], color=[s[2] for s in stages], width=0.55)
    for i, (_, v, _) in enumerate(stages):
        ax.annotate(fr(v, 2), (i, v), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=10, color=INK)
    ax.axhline(0.5, color=AXIS, linestyle="--", linewidth=1)
    ax.text(-0.42, 0.51, "Hasard (0,5)", fontsize=8, color=MUTED, ha="left", va="bottom")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fr(v, 1)))
    ax.set_xticks(list(x), [s[0] for s in stages], fontsize=9)
    ax.set_ylim(0, 1)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("AUC hors échantillon (1 = parfait)")
    top = a["2025/26, alerte de janvier (oct.-déc. 2025 connus)"].idxmax()
    header(fig, "Plus l'information arrive, mieux on anticipe les baisses d'effectifs",
           "Annoncer une baisse de plus de 5 % des effectifs d'une région, 65 prédictions sur des années non vues. Gains modestes\n"
           f"et peu de cas (14 baisses) : à confirmer. Alerte de janvier pour 2025/26, avant l'annuaire : {top} en tête "
           f"({fr(a.loc[top].iloc[0], 0)} %).")
    fig.texts[-1].set_text("Sources : données du Data Challenge Burkina (DGESS) ; ACLED par province et par mois (HDX). Calculs de l'équipe.")
    fig.savefig("analyse/figures/17_calendrier_alerte.png", dpi=200)
    plt.close(fig)


def main():
    nowcast()
    cohorts()
    matrix()
    factors()
    calendar_fig()
    print("5 figures écrites")


if __name__ == "__main__":
    main()

"""Figures for the machine learning comparison and the risk ranking for 2026/27.

Usage: python figures_ml.py   (run from the project root, after machine_learning.py)
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # validated categorical order, adjacent pairs
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
TIERS = [(40, "Risque élevé (≥ 40 %)", "#104281"), (15, "Risque moyen (15-39 %)", "#3987e5"),
         (0, "Risque faible (< 15 %)", "#b7d3f6")]
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK, "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})


def header(fig, main, sub):
    fig.text(0.01, 0.985, main, fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.01, 0.94, sub, fontsize=9.5, color=INK2, va="top")
    fig.text(0.01, 0.01, "Sources : données du Data Challenge Burkina (DGESS) ; ACLED (HDX) ; INSD, EHCVM 2021. "
             "Calculs de l'équipe.", fontsize=7.5, color=MUTED)


def main():
    reg = pd.read_csv("analyse/P11_ml_regression.csv")
    reg = reg[reg.annee_predite != "moyenne"]
    cols = ["Comme l'an passé", "Ridge (linéaire régularisé)", "Forêt aléatoire", "Gradient boosting"]
    short = ["Comme l'an passé", "Ridge", "Forêt aléatoire", "Gradient boosting"]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.08, right=0.80)
    for c, col in zip(cols, SERIES):
        lw = 2.6 if c == "Comme l'an passé" else 1.8
        ax.plot(reg.annee_predite, reg[c], color=col, marker="o", markersize=5, linewidth=lw, label=c)
    # End labels, pushed apart so that close values do not overlap (minimum gap in data units).
    ends = sorted(((reg[c].iloc[-1], s) for c, s in zip(cols, short)))
    placed = []
    for v, s in ends:
        y = max(v, placed[-1] + 0.28) if placed else v
        placed.append(y)
        ax.annotate(s, (len(reg) - 1, v), xytext=(len(reg) - 1 + 0.08, y), textcoords="data", va="center",
                    fontsize=8.5, color=INK2, annotation_clip=False)
    ax.set_ylim(0, None)
    ax.set_ylabel("Erreur moyenne sur la variation du TAP (points)")
    ax.set_xlabel("Année prédite (modèles entraînés sur les années précédentes seulement)")
    ax.legend(loc="upper left", fontsize=8.5)
    header(fig, "L'apprentissage automatique ne bat pas « comme l'an passé »",
           "Erreur moyenne : 4,23 points pour la règle simple, contre 4,54 à 4,79 pour les trois modèles. Ils font un peu mieux\n"
           "l'année du choc (22/23), nettement moins bien l'année des réouvertures (23/24).")
    fig.savefig("analyse/figures/11_ml_regression.png", dpi=200)
    plt.close(fig)

    pr = pd.read_csv("analyse/P11_probabilites_alerte.csv").sort_values("rentrée 2026/27")
    fig, ax = plt.subplots(figsize=(9, 5.6))
    fig.subplots_adjust(top=0.80, bottom=0.12, left=0.24, right=0.95)
    colors = [next(c for t, _, c in TIERS if v >= t) for v in pr["rentrée 2026/27"]]
    ax.barh(pr.region_2025, pr["rentrée 2026/27"], color=colors, height=0.62)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 100)
    for i, v in enumerate(pr["rentrée 2026/27"]):
        if v >= 15:
            ax.annotate(f"{v:.0f} %", (v, i), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.5,
                        color=INK2)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=l) for _, l, c in TIERS], loc="lower right", fontsize=8.5)
    ax.set_xlabel("Probabilité d'une baisse des effectifs de plus de 5 % en 2026/27")
    header(fig, "Où le risque monte pour 2026/27",
           "Régression logistique sur la violence d'oct. 2025 à sept. 2026. Elle classe bien les régions (AUC 0,83 hors échantillon),\n"
           "mais ses probabilités sont approximatives : on lit des niveaux de risque, pas des pourcentages exacts.")
    fig.savefig("analyse/figures/12_risque_2026_27.png", dpi=200)
    plt.close(fig)
    print("2 figures écrites")


if __name__ == "__main__":
    main()

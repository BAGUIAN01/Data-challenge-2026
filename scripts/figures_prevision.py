"""Figures for the cautious forecast, the escalation alert and the hypothesis test.

Usage: python figures_prevision.py   (run from the project root, after prevision_hypothese.py)
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

BLUE, BAND, WARN = "#2a78d6", "#b7d3f6", "#fab219"
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK, "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})


def fr(v, nd=0):
    return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")


def header(fig, main, sub):
    fig.text(0.01, 0.985, main, fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.01, 0.94, sub, fontsize=9.5, color=INK2, va="top")
    fig.text(0.01, 0.01, "Sources : données du Data Challenge Burkina (DGESS) ; ACLED et INSD via HDX ; "
             "INSD, EHCVM 2021. Calculs de l'équipe.", fontsize=7.5, color=MUTED)


def main():
    fc = pd.read_csv("analyse/P9_prevision_2025_26_alerte.csv").sort_values("TAP_24_25", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6.4))
    fig.subplots_adjust(top=0.82, bottom=0.12, left=0.20, right=0.80)
    y = np.arange(len(fc))
    ax.hlines(y, fc.fourchette_basse, fc.fourchette_haute, color=BAND, linewidth=7, zorder=1,
              label="Fourchette à 80 % pour 2025/26")
    ax.scatter(fc.TAP_24_25, y, s=46, color=BLUE, edgecolor=SURFACE, linewidth=1.5, zorder=3,
               label="TAP 2024/25 = prévision 2025/26")
    ax.set_yticks(y)
    ax.set_yticklabels(fc.region_2025)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Taux d'achèvement du primaire (%)")
    for i, (_, r) in enumerate(fc.iterrows()):
        ax.text(101.5, i, f"{fr(r.enfants_hors_CM2_estimes)}", va="center", fontsize=8.5, color=INK2,
                transform=ax.get_yaxis_transform() if False else ax.transData, clip_on=False)
        if r.alerte_2026_27:
            ax.annotate("⚠ alerte 2026/27", (r.fourchette_haute, i), xytext=(8, 0), textcoords="offset points",
                        va="center", fontsize=8.5, color=INK, fontweight="bold")
            ax.scatter([r.fourchette_haute + 1.2], [i], s=0)  # keeps the label inside the drawing area
    ax.text(101.5, len(fc) - 0.2, "Enfants ≈ 11 ans\nhors CM2 (est.)", fontsize=8, color=INK2, va="bottom",
            clip_on=False)
    ax.legend(loc="lower left", fontsize=8.5)
    header(fig, "Anticiper : prévision prudente 2025/26 et alerte d'escalade",
           "La prévision reprend le taux 2024/25 ; la fourchette vient des variations passées (elle a couvert 73 % des cas,\n"
           "46 % l'année du choc). Alerte : incidents d'oct. 2025 à sept. 2026 ≥ 1,5 fois ceux de l'année d'avant, et ≥ 30.")
    fig.savefig("analyse/figures/09_prevision_alerte.png", dpi=200)
    plt.close(fig)

    cs = pd.read_csv("analyse/P10_hypothese_transversale.csv")
    names = pd.read_csv("analyse/panel_region_annee_2025.csv").drop_duplicates("region").set_index("region").region_2025
    fig, ax = plt.subplots(figsize=(9, 6.2))
    fig.subplots_adjust(top=0.82, bottom=0.12, left=0.10, right=0.96)
    size = 20 + cs.incidents_21_24 / 3
    ax.scatter(cs.pauvrete_2021, cs.variation_TAP, s=size, color=BLUE, alpha=0.8, edgecolor=SURFACE, linewidth=1.5)
    offsets = {"SAHEL": (-10, 8, "right"), "CENTRE-EST": (-8, 6, "right"), "HAUTS-BASSINS": (8, -10, "left"),
               "SUD-OUEST": (-8, 6, "right"), "PLATEAU CENTRAL": (8, -10, "left")}
    for _, r in cs.iterrows():
        dx, dy, ha = offsets.get(r.region, (7, 4, "left"))
        ax.annotate(names[r.region], (r.pauvrete_2021, r.variation_TAP), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8, color=INK2, ha=ha)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fr(v, 1)))
    ax.axhline(0, color=AXIS, linewidth=0.8)
    ax.set_xlabel("Pauvreté 2021 (% de la population sous le seuil, EHCVM)")
    ax.set_ylabel("Variation du taux d'achèvement 2021/22 → 2024/25 (points)")
    for v, lab in [(50, "50"), (500, "500"), (1200, "1 200")]:
        ax.scatter([], [], s=20 + v / 3, color=BLUE, alpha=0.8, label=f"{lab} incidents")
    ax.legend(loc="lower left", fontsize=8.5, title="Incidents 2021-2024", title_fontsize=8.5, labelspacing=1.2)
    header(fig, "Aucun effet de cumul insécurité × pauvreté détecté à l'échelle régionale",
           "Toutes les régions reculent, riches ou pauvres. Sur le panel de 104 régions-années, l'interaction insécurité × pauvreté\n"
           "n'est pas significative (IC 95 % de −0,38 à +0,25) et prédit moins bien que la règle « comme l'an passé ».")
    fig.savefig("analyse/figures/10_hypothese_insecurite_pauvrete.png", dpi=200)
    plt.close(fig)
    print("2 figures écrites")


if __name__ == "__main__":
    main()

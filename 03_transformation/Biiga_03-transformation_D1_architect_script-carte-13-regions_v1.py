"""Build the map layer of the 13 former regions and draw a first map."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import sys
import unicodedata

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

INK, INK2, MUTED, SURFACE, EDGE = "#0b0b0b", "#52514e", "#898781", "#fcfcfb", "#fcfcfb"
ORDINAL = ["#86b6ef", "#3987e5", "#256abf", "#104281"]
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
PROFILES = {
    4: "Stabilité, régions d'accueil",
    3: "Érosion sans fermetures massives",
    1: "Choc puis reprise partielle",
    2: "Effondrement",
}


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


OUTSIDE = {"Kadiogo": (-1.9, 1.15), "Oubri": (1.25, -2.15), "Nazinon": (0.1, -1.15)}


NUDGE = {"Liptako + Soum": (0.0, 0.45), "Nakambé": (0.5, -0.1)}


def label(ax, row, txt, dark):
    p = row.geometry.representative_point()
    dx, dy = NUDGE.get(row.region_2025, (0, 0))
    p = type(p)(p.x + dx, p.y + dy)
    off = OUTSIDE.get(row.region_2025)
    if off:
        ax.annotate(txt, xy=(p.x, p.y), xytext=(p.x + off[0], p.y + off[1]), ha="center", va="center",
                    fontsize=6.5, color=INK, linespacing=1.05,
                    arrowprops=dict(arrowstyle="-", color=INK2, linewidth=0.6))
    else:
        ax.text(p.x, p.y, txt, ha="center", va="center", fontsize=6.5, linespacing=1.05,
                color="#ffffff" if dark else INK)


def main():
    adm1, ref_path, out = sys.argv[1], sys.argv[2], sys.argv[3].rstrip("/")
    ref = pd.read_csv(ref_path)
    g = gpd.read_file(adm1)[["adm1_pcode", "geometry"]].merge(
        ref[["code_nouvelle_region", "code_ancienne_region", "ancienne_region", "cle_presco"]],
        left_on="adm1_pcode", right_on="code_nouvelle_region")
    labels = ref.groupby("cle_presco").nouvelle_region.agg(lambda n: " + ".join(sorted(n)))
    r13 = g.dissolve(by=["code_ancienne_region", "ancienne_region", "cle_presco"]).reset_index()
    r13["region_2025"] = r13.cle_presco.map(labels)
    r13 = r13[["code_ancienne_region", "ancienne_region", "region_2025", "cle_presco", "geometry"]]
    assert len(r13) == 13, len(r13)
    light = r13.copy()
    light["geometry"] = light.geometry.simplify(0.005, preserve_topology=True)
    light.to_file(chemins.path("regions_13.geojson"), driver="GeoJSON")

    typology = pd.read_csv(chemins.path("P2_typologie_regions.csv"))
    typology["cle_presco"] = typology.region.map(key)
    m = light.merge(typology[["cle_presco", "TAP_2024_25", "groupe_k4"]], on="cle_presco", how="left")
    assert m.TAP_2024_25.notna().all()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.4))
    fig.patch.set_facecolor(SURFACE)
    fig.subplots_adjust(top=0.84, bottom=0.20, left=0.01, right=0.99, wspace=0.04)
    bins = [0, 20, 30, 40, 50, 60, 70, 100]
    m["classe"] = pd.cut(m.TAP_2024_25, bins, labels=False, include_lowest=True)
    ramp = SEQUENTIAL[::-1]
    ax = axes[0]
    m.plot(ax=ax, color=[ramp[int(c)] for c in m.classe], edgecolor=EDGE, linewidth=1.2)
    for _, row in m.iterrows():
        txt = f"{row.region_2025.replace(' + ', ' +\n')}\n{row.TAP_2024_25:.0f} %"
        label(ax, row, txt, dark=row.classe <= 3)
    ax.set_title("Taux d'achèvement du primaire 2024/25 (plus foncé = plus faible)", fontsize=10.5, loc="left",
                 color=INK, fontweight="bold")
    ax.legend(handles=[Patch(color=ramp[i], label=f"{bins[i]}–{bins[i + 1]} %") for i in range(len(bins) - 1)],
              loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=4, fontsize=7.5, frameon=False)
    ax.axis("off")
    order = list(PROFILES)
    ax = axes[1]
    m.plot(ax=ax, color=[ORDINAL[order.index(int(k))] for k in m.groupe_k4], edgecolor=EDGE, linewidth=1.2)
    for _, row in m.iterrows():
        label(ax, row, row.region_2025.replace(" + ", " +\n"), dark=order.index(int(row.groupe_k4)) >= 1)
    ax.set_title("Profil de trajectoire 2015/16 → 2024/25", fontsize=10.5, loc="left", color=INK, fontweight="bold")
    ax.legend(handles=[Patch(color=ORDINAL[i], label=PROFILES[k]) for i, k in enumerate(order)],
              loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=7.5, frameon=False)
    ax.axis("off")
    fig.text(0.01, 0.97, "Où le décrochage est le plus fort : 13 régions, noms de 2025", fontsize=13,
             fontweight="bold", color=INK, va="top")
    fig.text(0.01, 0.925, "Les trois anciennes régions coupées en 2025 restent groupées : les données ne permettent pas "
             "de les séparer.", fontsize=9.5, color=INK2, va="top")
    fig.text(0.01, 0.02, "Sources : données du Data Challenge Burkina (DGESS) ; limites administratives IGB 2025 (HDX). "
             "Calculs de l'équipe.", fontsize=7.5, color=MUTED)
    fig.savefig(chemins.path("08_carte_profils_achevement.png"), dpi=200)
    print("13 régions écrites dans 03_transformation/Biiga_03-transformation_D1_architect_carte-13-regions_v1.geojson ; carte écrite.")


if __name__ == "__main__":
    main()

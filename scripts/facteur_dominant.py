"""Dominant factor of each region: what to act on."""
import numpy as np
import pandas as pd

FACTEURS = {
    "violence": ("Violence", True), "deplaces": ("Déplacés", True), "pauvrete": ("Pauvreté", True), "faim": ("Faim", True),
    "meres": ("Femmes sans instruction", True), "grossesses": ("Grossesses précoces", True), "prescolaire": ("Préscolaire", False),
}


def main():
    prof = pd.read_csv("analyse/P14_profil_facteurs.csv").set_index("region_2025")
    corr = pd.read_csv("analyse/P14_facteurs_correlations.csv")
    poids = {}
    for fid, (debut, _) in FACTEURS.items():
        ligne = corr[corr.facteur.str.startswith(debut)]
        assert len(ligne) == 1, (fid, ligne)
        poids[fid] = abs(float(ligne.TAP_2024_25.iloc[0]))
    contrib = pd.DataFrame(index=prof.index)
    for fid, (_, haut_expose) in FACTEURS.items():
        x = prof[fid].astype(float)
        z = (x - x.mean()) / x.std(ddof=0)
        contrib[fid] = poids[fid] * (z if haut_expose else -z)
    contrib = contrib.round(2)
    dom = contrib.idxmax(axis=1).where(contrib.max(axis=1) > 0)
    second = contrib.apply(lambda r: r.sort_values(ascending=False).index[1] if r.sort_values(ascending=False).iloc[1] > 0 else None, axis=1)
    out = contrib.assign(dominant=dom, second=second)
    print("Poids (|corrélation avec l'achèvement 2024/25|) :", {k: round(v, 2) for k, v in poids.items()})
    print(out.to_string())
    print("\nRégions par facteur dominant :", out.dominant.value_counts(dropna=False).to_dict())
    out.to_csv("analyse/P19_facteur_dominant.csv")


if __name__ == "__main__":
    main()

"""Dominant factor of each region: what to act on."""
import numpy as np
import pandas as pd

FACTOR_SPECS = {
    "violence": ("Violence", True), "deplaces": ("Déplacés", True), "pauvrete": ("Pauvreté", True), "faim": ("Faim", True),
    "meres": ("Femmes sans instruction", True), "grossesses": ("Grossesses précoces", True), "prescolaire": ("Préscolaire", False),
}


def main():
    prof = pd.read_csv("analyse/P14_profil_facteurs.csv").set_index("region_2025")
    corr = pd.read_csv("analyse/P14_facteurs_correlations.csv")
    weights = {}
    for fid, (label_prefix, _) in FACTOR_SPECS.items():
        row_line = corr[corr.facteur.str.startswith(label_prefix)]
        assert len(row_line) == 1, (fid, row_line)
        weights[fid] = abs(float(row_line.TAP_2024_25.iloc[0]))
    contrib = pd.DataFrame(index=prof.index)
    for fid, (_, high_exposed) in FACTOR_SPECS.items():
        x = prof[fid].astype(float)
        z = (x - x.mean()) / x.std(ddof=0)
        contrib[fid] = weights[fid] * (z if high_exposed else -z)
    contrib = contrib.round(2)
    dominant = contrib.idxmax(axis=1).where(contrib.max(axis=1) > 0)
    second = contrib.apply(lambda r: r.sort_values(ascending=False).index[1] if r.sort_values(ascending=False).iloc[1] > 0 else None, axis=1)
    out = contrib.assign(dominant=dominant, second=second)
    print("Poids (|corrélation avec l'achèvement 2024/25|) :", {k: round(v, 2) for k, v in weights.items()})
    print(out.to_string())
    print("\nRégions par facteur dominant :", out.dominant.value_counts(dropna=False).to_dict())
    out.to_csv("analyse/P19_facteur_dominant.csv")


if __name__ == "__main__":
    main()

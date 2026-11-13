"""Write out the risk model as a formula and check it against the probabilities shown in the app."""
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, "scripts")
import anticipation_fine
import solution_prevision

warnings.filterwarnings("ignore")
NOMS = {"l_inc": "ln(1 + incidents de l'année scolaire)", "d_l_inc": "escalade : écart du terme précédent avec l'année d'avant",
        "l_late": "ln(1 + incidents de juillet à septembre)", "l_rentree": "ln(1 + incidents d'octobre à décembre)"}
MODELES = [("Référence (D12), rentrée 2026/27", anticipation_fine.SETS["Référence : violence (niveau, escalade)"], "2025-2026", "2026/27, référence (D12)"),
           ("Alerte de septembre, rentrée 2026/27", anticipation_fine.SETS["F2 + juillet-septembre"], "2025-2026", "2026/27, alerte de septembre (juil.-sept. 2026 connus)"),
           ("Alerte de janvier, rentrée 2025/26", anticipation_fine.SETS["F3 + rentrée (oct.-déc.)"], "2024-2025", "2025/26, alerte de janvier (oct.-déc. 2025 connus)")]


def main():
    p = solution_prevision.build()
    f, _ = anticipation_fine.features("data/raw/externe/hdx_acled/acled_political_violence_month_year.xlsx",
                    "data/raw/externe/hdx_acled/acled_civilian_targeting_month_year.xlsx")
    d = p.merge(f.drop(columns=["incidents"]), on=["cle", "annee"], how="left")
    d["y_drop"] = (d.y_eleves < np.log(0.95)).astype(float)
    d.loc[d.y_eleves.isna(), "y_drop"] = np.nan
    d = d.dropna(subset=sorted({c for v in anticipation_fine.SETS.values() for c in v}) + ["y_drop"])
    acled = pd.read_csv("analyse/acled_region_annee.csv").sort_values(["cle", "annee"])
    acled["l_inc"] = np.log1p(acled.incidents)
    acled["d_l_inc"] = acled.l_inc - acled.groupby("cle").l_inc.shift()
    cur = acled.merge(f.drop(columns=["incidents"]), on=["cle", "annee"], how="left")
    affiche = pd.read_csv("analyse/P16_alertes_calendrier.csv").set_index("region")
    n25 = pd.read_csv("analyse/panel_region_annee_2025.csv").drop_duplicates("region").set_index("region").region_2025
    nom = d.drop_duplicates("cle").set_index("cle").region.map(n25)
    lignes = []
    print(f"Apprentissage : {len(d)} couples région × année, {int(d.y_drop.sum())} baisses de plus de 5 %.\n")
    for titre, cols, annee, colonne in MODELES:
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(d[cols], d.y_drop)
        sc, lr = m.named_steps["standardscaler"], m.named_steps["logisticregression"]
        b = lr.coef_[0] / sc.scale_
        b0 = lr.intercept_[0] - (lr.coef_[0] * sc.mean_ / sc.scale_).sum()
        print(f"{titre}\n  logit(p) = {b0:+.4f}" + "".join(f" {bj:+.4f} × {c}" for bj, c in zip(b, cols)))
        for c in cols:
            print(f"    {c} = {NOMS[c]}")
        x = cur[(cur.annee == annee) & cur.cle.isin(nom.index)].set_index("cle")
        z = b0 + (x[cols].values * b).sum(axis=1)
        pr = pd.Series(100 / (1 + np.exp(-z)), index=nom.reindex(x.index).values).round()
        ecart = (pr - affiche[colonne].reindex(pr.index)).abs().max()
        print(f"  vérification : écart maximal avec les probabilités affichées = {ecart:.0f} point(s) sur {len(pr)} régions\n")
        lignes.append({"modele": titre, "constante": round(b0, 4), **{c: round(v, 4) for c, v in zip(cols, b)},
                       "ecart_max_points": int(ecart), "observations": len(d), "baisses": int(d.y_drop.sum())})
    pd.DataFrame(lignes).to_csv("analyse/P17_formule_risque.csv", index=False)


if __name__ == "__main__":
    main()

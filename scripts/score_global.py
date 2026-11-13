"""Global score: one number per region that combines the two forms of dropout."""
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, "scripts")
import solution_prevision

warnings.filterwarnings("ignore")
POIDS = 0.5


def score(prob, tap):
    return 100 * (POIDS * prob + (1 - POIDS) * (1 - tap / 100))


def rejouer(p):
    nat = pd.read_csv("analyse/panel_region_annee.csv").query("region == 'NATIONAL'").set_index("annee").TAP_T
    d = p.dropna(subset=["l_inc", "d_l_inc", "y_eleves"]).copy()
    d["y_drop"] = (d.y_eleves < np.log(0.95)).astype(int)
    d["lost"] = np.maximum(0, d.eleves_T * (1 - np.exp(d.y_eleves)))
    years = sorted(d.annee.unique())
    tests = []
    for ty in years[3:]:
        tr, te = d[d.annee < ty], d[d.annee == ty].copy()
        if tr.y_drop.nunique() < 2:
            continue
        mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(tr[["l_inc", "d_l_inc"]], tr.y_drop)
        te["prob"] = mdl.predict_proba(te[["l_inc", "d_l_inc"]])[:, 1]
        te["prio"] = [solution_prevision.priority(t, nat[ty], pr) for t, pr in zip(te.TAP_T, te.prob)]
        te["score"] = score(te.prob, te.TAP_T)
        te["retard"] = 100 - te.TAP_T
        te["annee_t"] = solution_prevision.SHORT[ty]
        tests.append(te)
    t = pd.concat(tests)
    rows = []
    for nom, col in [("Score global", "score"), ("Risque seul (violence)", "prob"), ("Achèvement seul", "retard")]:
        pris_b = pris_l = 0
        for _, g in t.groupby("annee_t"):
            k = int((g.prio == 1).sum())
            top = g.nlargest(k, col)
            pris_b += top.y_drop.sum(); pris_l += top.lost.sum()
        rows.append({"mesure": nom, "AUC_baisse_t+1": roc_auc_score(t.y_drop, t[col]),
                     "baisses_prises_%": 100 * pris_b / t.y_drop.sum(), "eleves_perdus_pris_%": 100 * pris_l / t.lost.sum()})
    p1 = t.prio == 1
    rows.append({"mesure": "Matrice (priorité 1)", "AUC_baisse_t+1": np.nan,
                 "baisses_prises_%": 100 * t.y_drop[p1].sum() / t.y_drop.sum(), "eleves_perdus_pris_%": 100 * t.lost[p1].sum() / t.lost.sum()})
    r = pd.DataFrame(rows)
    print(f"Rejoué sur {t.annee_t.nunique()} années, {len(t)} régions-années, {int(t.y_drop.sum())} fortes baisses ; "
          f"à chaque année, autant de régions en tête que la matrice en met en priorité 1 ({int(p1.sum())} au total).")
    print(r.round(2).to_string(index=False))
    r.round(3).to_csv("analyse/P18_score_global_rejoue.csv", index=False)
    sens = []
    for w in [0.3, 0.4, 0.5, 0.6, 0.7]:
        s = 100 * (w * t.prob + (1 - w) * (1 - t.TAP_T / 100))
        sens.append({"poids_risque": w, "AUC_baisse_t+1": roc_auc_score(t.y_drop, s)})
    print("\nSensibilité au poids du risque (pour information, le poids reste 0,5) :")
    print(pd.DataFrame(sens).round(3).to_string(index=False))


def trajectoire(p):
    nat = pd.read_csv("analyse/panel_region_annee.csv").query("region == 'NATIONAL'").set_index("annee").TAP_T
    d = p.copy()
    d["y_drop"] = np.where(d.y_eleves.isna(), np.nan, (d.y_eleves < np.log(0.95)).astype(float))
    lab = d.dropna(subset=["l_inc", "d_l_inc", "y_eleves"])
    years = sorted(d.annee.unique())
    out = []
    for ty in years:
        tr = lab[lab.annee < ty]
        te = d[(d.annee == ty)].dropna(subset=["l_inc", "d_l_inc", "TAP_T"])
        if len(tr) < 30 or tr.y_drop.nunique() < 2 or te.empty:
            continue
        mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(tr[["l_inc", "d_l_inc"]], tr.y_drop)
        prob = mdl.predict_proba(te[["l_inc", "d_l_inc"]])[:, 1]
        y0 = int(ty[:4]) + 1
        cible = solution_prevision.SHORT[f"{y0}-{y0 + 1}"]
        for (_, row), pr in zip(te.iterrows(), prob):
            out.append({"cle": row.cle, "annee_cible": cible, "probabilite": round(pr, 3),
                        "score": round(score(pr, row.TAP_T)), "chute_observee": row.y_drop})
    t = pd.DataFrame(out)
    print(f"\nTrajectoire : {t.annee_cible.nunique()} années rejouées ({', '.join(sorted(t.annee_cible.unique()))}), puis 2026/27.")
    t.to_csv("analyse/P18_score_global_trajectoire.csv", index=False)


def score_2026():
    m = pd.read_csv("analyse/P13_matrice_priorite_2026_27.csv").set_index("region_2025")
    cal = pd.read_csv("analyse/P16_alertes_calendrier.csv").set_index("region")
    prob = cal["2026/27, référence (D12)"] / 100
    m["probabilite_baisse_2026_27"] = prob.reindex(m.index)
    m["score_global"] = score(m.probabilite_baisse_2026_27, m.TAP_24_25).round()
    m = m.sort_values("score_global", ascending=False)
    print("\nScore global, rentrée 2026/27 :")
    print(m[["TAP_24_25", "probabilite_baisse_2026_27", "priorite", "score_global"]].to_string())
    m[["TAP_24_25", "probabilite_baisse_2026_27", "priorite", "score_global"]].to_csv("analyse/P18_score_global_2026_27.csv")


def main():
    pd.set_option("display.width", 200)
    p = solution_prevision.build()
    rejouer(p)
    score_2026()
    trajectoire(p)


if __name__ == "__main__":
    main()

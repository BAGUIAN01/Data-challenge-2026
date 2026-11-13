"""Do the non-security factors help to predict? Tests fixed before running."""
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, "scripts")
from solution_prevision import SHORT, build, key

warnings.filterwarnings("ignore")
DHS_NAMES = {"Boucle de Mouhoun": "BOUCLEDUMOUHOUN", "Centre (including Ouagadougou)": "CENTRE",
             "Hauts Bassins": "HAUTSBASSINS"}


def dhs_rounds():
    out = []
    for f, ind, col in [("select-education-indicators_subnational_bfa.csv", "Women with no education", "meres"),
                        ("mics-indicators_subnational_bfa.csv", "Age specific fertility rate: 15-19", "grossesses")]:
        d = pd.read_csv("data/raw/externe/hdx_dhs/" + f)
        d = d[(d.Indicator == ind) & d.SurveyYear.isin([2010, 2014, 2017, 2021]) & (d.CharacteristicLabel != "Ouagadougou")]
        d = d.drop_duplicates(["SurveyYear", "CharacteristicLabel"])
        d = d.assign(cle=d.CharacteristicLabel.map(lambda s: DHS_NAMES.get(s, key(s))), var=col)
        out.append(d[["cle", "SurveyYear", "var", "Value"]])
    w = pd.concat(out).pivot_table(index=["cle", "SurveyYear"], columns="var", values="Value").reset_index()
    assert w.groupby("SurveyYear").cle.nunique().eq(13).all()
    return w


def data():
    p = build()
    food = pd.read_csv("data/externe_propre/faim_cadre_harmonise_region_annee.csv")
    p = p.merge(food[["cle", "annee", "faim_phase3plus_pct"]], on=["cle", "annee"], how="left")
    p["faim"] = p.faim_phase3plus_pct / 10
    p = p.sort_values(["cle", "annee"])
    p["d_faim"] = p.faim - p.groupby("cle").faim.shift()
    w = dhs_rounds()
    start = p.annee.str[:4].astype(int)
    p["dhs_round"] = [max([y for y in [2010, 2014, 2017, 2021] if y <= s - 2]) for s in start]
    p = p.merge(w.rename(columns={"SurveyYear": "dhs_round"}), on=["cle", "dhs_round"], how="left")
    g = p.groupby("cle")
    p["y_drop"] = (p.y_eleves < np.log(0.95)).astype(float)
    p.loc[p.y_eleves.isna(), "y_drop"] = np.nan
    p["y_dTAP3"] = g.TAP_T.shift(-3) - p.TAP_T
    return p


SETS = {
    "Violence": ["l_inc", "d_l_inc"],
    "Violence + faim": ["l_inc", "d_l_inc", "faim", "d_faim"],
    "Violence + fond": ["l_inc", "d_l_inc", "meres", "grossesses"],
    "Violence + faim + fond": ["l_inc", "d_l_inc", "faim", "d_faim", "meres", "grossesses"],
    "Fond seul": ["meres", "grossesses"],
}


def t1(p):
    d = p.dropna(subset=["y_drop", "faim", "d_faim", "l_inc", "d_l_inc", "meres", "grossesses"])
    years = sorted(d.annee.unique())
    preds, truth = {k: [] for k in SETS}, []
    for ty in years[2:]:
        tr, te = d[d.annee < ty], d[d.annee == ty]
        if tr.y_drop.nunique() < 2:
            continue
        truth += list(te.y_drop)
        for k, cols in SETS.items():
            m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(tr[cols], tr.y_drop)
            preds[k] += list(m.predict_proba(te[cols])[:, 1])
    rows = [{"modele": k, "AUC": roc_auc_score(truth, v), "Brier": brier_score_loss(truth, v)} for k, v in preds.items()]
    rows.append({"modele": "Aucun modèle (taux de base)", "AUC": 0.5,
                 "Brier": brier_score_loss(truth, np.full(len(truth), np.mean(truth)))})
    r = pd.DataFrame(rows)
    print(f"=== T1. Baisse des effectifs > 5 % l'année suivante ({len(truth)} prédictions, {int(sum(truth))} baisses) ===")
    print(r.round(3).to_string(index=False))
    r.round(3).to_csv("analyse/P15_alerte_facteurs.csv", index=False)


def regress(p, target, horizon, label):
    cols_all = ["faim", "d_faim", "l_inc", "d_l_inc", "meres", "grossesses"]
    d = p.dropna(subset=[target] + cols_all)
    years = sorted(d.annee.unique())
    rows = []
    for i, ty in enumerate(years):
        tr = d[d.annee.map(years.index) <= i - horizon]
        if len(tr) < 26:
            continue
        te = d[d.annee == ty]
        row = {"annee_t": SHORT[ty], "Comme aujourd'hui": np.abs(te[target]).mean()}
        for k, cols in SETS.items():
            X = np.column_stack([np.ones(len(tr))] + [tr[c] for c in cols])
            b = np.linalg.lstsq(X, tr[target], rcond=None)[0]
            Xt = np.column_stack([np.ones(len(te))] + [te[c] for c in cols])
            row[k] = np.abs(te[target] - Xt @ b).mean()
        rows.append(row)
    r = pd.DataFrame(rows)
    r.loc[len(r)] = ["moyenne"] + list(r.iloc[:, 1:].mean())
    print(f"\n=== {label} : erreur absolue moyenne (points de TAP) ===")
    print(r.round(2).to_string(index=False))
    base = r.iloc[-1]["Comme aujourd'hui"]
    print("  gain par rapport à « comme aujourd'hui » : " +
          " ; ".join(f"{k} {(1 - r.iloc[-1][k] / base) * 100:+.0f} %" for k in SETS))
    return r


def main():
    pd.set_option("display.width", 220)
    p = data()
    t1(p)
    regress(p, "y_dTAP", 1, "T2. Variation du taux d'achèvement l'année suivante").round(2).to_csv(
        "analyse/P15_TAP_un_an.csv", index=False)
    regress(p, "y_dTAP3", 3, "T3. Variation du taux d'achèvement à trois ans").round(2).to_csv(
        "analyse/P15_TAP_trois_ans.csv", index=False)


if __name__ == "__main__":
    main()

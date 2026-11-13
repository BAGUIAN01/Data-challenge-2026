"""Machine learning put in competition with simple rules, on years the models never saw."""
import unicodedata
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
SEED = 2026
YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]
SHORT = {y: y[2:4] + "/" + y[7:] for y in YEARS + ["2025-2026", "2026-2027"]}
LABELS = {
    "TAP_T": "Taux d'achèvement", "dTAP": "Variation du TAP (année écoulée)", "IPS_TAP": "Parité filles/garçons du TAP",
    "TBS_T": "Taux brut de scolarisation", "TBA_T": "Taux brut d'admission", "CEP_T": "Réussite au CEP",
    "dlog_eleves": "Variation des effectifs", "dlog_ecoles": "Variation du nombre d'écoles",
    "dlog_cp1": "Variation des entrées en CP1", "part_public": "Part des écoles publiques",
    "sorties_prev": "Sorties apparentes (année écoulée)", "l_inc": "Incidents (log)",
    "d_l_inc": "Escalade des incidents", "l_morts": "Morts (log)", "pauvrete": "Pauvreté 2021",
}


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


def build():
    panel = pd.read_csv("analyse/panel_region_annee.csv")
    p = panel[panel.region != "NATIONAL"].copy()
    p["cle"] = p.region.map(key)
    acled = pd.read_csv("analyse/acled_region_annee.csv")
    pov = pd.read_csv("data/externe_propre/pauvrete_ehcvm_2021_regions.csv")
    pov["cle"] = pov.region.map(key)
    p = p.merge(acled, on=["cle", "annee"], how="left").merge(
        pov[["cle", "incidence_pauvrete_2021_pct"]], on="cle", how="left").sort_values(["region", "annee"])
    g = p.groupby("region")
    p["dTAP"] = p.TAP_T - g.TAP_T.shift()
    p["dlog_cp1"] = np.log(p.nouveaux_CP1_T / g.nouveaux_CP1_T.shift())
    p["part_public"] = p.ecoles_publiques / p.ecoles
    p["sorties_prev"] = g.sorties_app.shift()
    p["l_inc"] = np.log1p(p.incidents)
    p["d_l_inc"] = p.l_inc - g.l_inc.shift()
    p["l_morts"] = np.log1p(p.morts)
    p["pauvrete"] = p.incidence_pauvrete_2021_pct
    p["y_dTAP"] = g.TAP_T.shift(-1) - p.TAP_T
    p["y_drop"] = (np.log(g.eleves_T.shift(-1) / p.eleves_T) < np.log(0.95)).astype(float)
    p.loc[g.eleves_T.shift(-1).isna(), "y_drop"] = np.nan
    p["rule"] = ((p.incidents >= 1.5 * g.incidents.shift()) & (p.incidents >= 30)).astype(float)
    return p


FEATURES = list(LABELS)


def main():
    pd.set_option("display.width", 200)
    p = build()
    data = p.dropna(subset=FEATURES + ["y_dTAP", "y_drop"]).copy()
    years = sorted(data.annee.unique())
    tests = years[3:]
    print(f"Observations utilisables : {len(data)} (13 régions × {len(years)} années) ; "
          f"années testées : {SHORT[tests[0]]} à {SHORT[tests[-1]]} (prédiction de l'année suivante)")

    reg_models = {
        "Ridge (linéaire régularisé)": lambda: make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "Forêt aléatoire": lambda: RandomForestRegressor(n_estimators=500, min_samples_leaf=5, max_features=0.5,
                                                          random_state=SEED),
        "Gradient boosting": lambda: GradientBoostingRegressor(n_estimators=200, max_depth=2, learning_rate=0.05,
                                                               subsample=0.8, random_state=SEED),
    }
    rows, imp_rows = [], []
    for ty in tests:
        tr, te = data[data.annee < ty], data[data.annee == ty]
        row = {"annee_predite": SHORT[years[years.index(ty) + 1]] if ty != years[-1] else "24/25",
               "Comme l'an passé": np.abs(te.y_dTAP).mean()}
        for name, mk in reg_models.items():
            mdl = mk().fit(tr[FEATURES], tr.y_dTAP)
            row[name] = np.abs(te.y_dTAP - mdl.predict(te[FEATURES])).mean()
            if name == "Forêt aléatoire":
                pi = permutation_importance(mdl, te[FEATURES], te.y_dTAP, scoring="neg_mean_absolute_error",
                                            n_repeats=30, random_state=SEED)
                imp_rows.append(pd.Series(pi.importances_mean, index=FEATURES))
        rows.append(row)
    reg = pd.DataFrame(rows)
    reg.loc[len(reg)] = ["moyenne"] + list(reg.iloc[:, 1:].mean())
    reg.round(2).to_csv("analyse/P11_ml_regression.csv", index=False)
    print("\n=== 1. Variation du taux d'achèvement l'année suivante : erreur absolue moyenne (points) ===")
    print(reg.round(2).to_string(index=False))
    base = reg.iloc[-1]["Comme l'an passé"]
    for name in reg_models:
        print(f"  {name:30s} gain par rapport à « comme l'an passé » : {(1 - reg.iloc[-1][name] / base) * 100:+.0f} %")
    imp = pd.concat(imp_rows, axis=1).mean(axis=1).sort_values(ascending=False)
    imp = pd.DataFrame({"variable": [LABELS[i] for i in imp.index], "importance_points": imp.values})
    imp.round(3).to_csv("analyse/P11_importance.csv", index=False)
    print("\nImportance des variables (forêt aléatoire, permutation sur les années testées ; "
          "points d'erreur gagnés quand la variable est connue) :")
    print(imp.head(8).round(3).to_string(index=False))

    clf_models = {
        "Logistique, violence seule": (["l_inc", "d_l_inc"],
                                       lambda: make_pipeline(StandardScaler(), LogisticRegression(C=1.0))),
        "Logistique, toutes variables": (FEATURES,
                                         lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=2000))),
        "Forêt aléatoire": (FEATURES, lambda: RandomForestClassifier(n_estimators=500, min_samples_leaf=5,
                                                                    max_features=0.5, random_state=SEED)),
    }
    preds = {n: [] for n in clf_models}
    truth, rule = [], []
    for ty in tests:
        tr, te = data[data.annee < ty], data[data.annee == ty]
        truth += list(te.y_drop)
        rule += list(te.rule)
        for name, (cols, mk) in clf_models.items():
            if tr.y_drop.nunique() < 2:
                preds[name] += [tr.y_drop.mean()] * len(te)
                continue
            mdl = mk().fit(tr[cols], tr.y_drop)
            preds[name] += list(mdl.predict_proba(te[cols])[:, 1])
    truth, rule = np.array(truth), np.array(rule)
    out = []
    pos = truth.sum()
    out.append({"modele": "Règle d'escalade (D7)", "AUC": roc_auc_score(truth, rule), "Brier": np.nan,
                "alertes": int(rule.sum()), "baisses_annoncees": int((rule * truth).sum()),
                "precision_%": (rule * truth).sum() / max(rule.sum(), 1) * 100, "rappel_%": (rule * truth).sum() / pos * 100})
    for name, pr in preds.items():
        pr = np.array(pr)
        flag = pr >= 0.5
        out.append({"modele": name, "AUC": roc_auc_score(truth, pr), "Brier": brier_score_loss(truth, pr),
                    "alertes": int(flag.sum()), "baisses_annoncees": int((flag * truth).sum()),
                    "precision_%": (flag * truth).sum() / max(flag.sum(), 1) * 100, "rappel_%": (flag * truth).sum() / pos * 100})
    out.append({"modele": "Aucun modèle (taux de base)", "AUC": 0.5,
                "Brier": brier_score_loss(truth, np.full(len(truth), truth.mean())), "alertes": 0, "baisses_annoncees": 0,
                "precision_%": np.nan, "rappel_%": 0})
    clf = pd.DataFrame(out)
    clf.round(3).to_csv("analyse/P11_ml_classification.csv", index=False)
    print(f"\n=== 2. Baisse des effectifs de plus de 5 % l'année suivante ({len(truth)} prédictions hors échantillon, "
          f"{int(pos)} baisses réelles) ===")
    print(clf.round(3).to_string(index=False))
    print("AUC : 0,5 = hasard, 1 = parfait. Brier : plus bas = probabilités plus justes. Seuil d'alerte des modèles : 50 %.")

    cols, mk = clf_models["Logistique, violence seule"]
    final = mk().fit(data[cols], data.y_drop)
    acled = pd.read_csv("analyse/acled_region_annee.csv").sort_values(["cle", "annee"])
    acled["l_inc"] = np.log1p(acled.incidents)
    acled["d_l_inc"] = acled.l_inc - acled.groupby("cle").l_inc.shift()
    names = p.drop_duplicates("cle").set_index("cle")
    n25 = pd.read_csv("analyse/panel_region_annee_2025.csv").drop_duplicates("region").set_index("region").region_2025
    res = []
    for yr, label in [("2024-2025", "rentrée 2025/26"), ("2025-2026", "rentrée 2026/27")]:
        cur = acled[acled.annee == yr].set_index("cle")
        cur = cur[cur.index.isin(names.index)]
        prob = final.predict_proba(cur[cols])[:, 1]
        for c, pr, inc in zip(cur.index, prob, cur.incidents):
            res.append({"region_2025": n25[names.loc[c, "region"]], "periode": label, "incidents": int(inc),
                        "probabilite_baisse_%": round(pr * 100)})
    res = pd.DataFrame(res).pivot_table(index="region_2025", columns="periode", values="probabilite_baisse_%")
    res = res.sort_values("rentrée 2026/27", ascending=False)
    res.to_csv("analyse/P11_probabilites_alerte.csv")
    print("\nProbabilité d'une baisse des effectifs de plus de 5 % (logistique, violence seule, entraînée sur 2015-2025) :")
    print(res.to_string())


if __name__ == "__main__":
    main()

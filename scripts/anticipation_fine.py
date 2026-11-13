"""Finer violence signals for anticipation, from ACLED by province and month."""
import sys
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, "scripts")
from solution_prevision import SHORT, build, key

warnings.filterwarnings("ignore")
SEED = 2026
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], start=1)}


def monthly(path):
    a = pd.read_excel(path, sheet_name="Data")
    a["cle"] = a.Admin1.map(key)
    a["m"] = a.Month.map(MONTHS)
    a["start"] = np.where(a.m >= 10, a.Year, a.Year - 1)
    return a


def features(path_pv, path_civ):
    a = monthly(path_pv)
    a["any"] = (a.Events > 0).astype(int)
    sy = a.groupby(["cle", "start"]).agg(incidents=("Events", "sum"), extent=("any", "mean")).reset_index()
    late = a[a.m.isin([7, 8, 9])].groupby(["cle", "Year"]).Events.sum().rename("late").reset_index()
    late["start"] = late.Year - 1
    rent = a[a.m.isin([10, 11, 12])].groupby(["cle", "Year"]).Events.sum().rename("rentree").reset_index()
    rent["start"] = rent.Year - 1
    c = monthly(path_civ).groupby(["cle", "start"]).Events.sum().rename("civils").reset_index()
    f = sy.merge(late[["cle", "start", "late"]], on=["cle", "start"], how="left") \
        .merge(rent[["cle", "start", "rentree"]], on=["cle", "start"], how="left") \
        .merge(c, on=["cle", "start"], how="left")
    f["annee"] = f.start.astype(str) + "-" + (f.start + 1).astype(str)
    for col in ["incidents", "late", "rentree", "civils"]:
        f["l_" + col] = np.log1p(f[col])
    g = gpd.read_file("data/ref/regions_13.geojson")
    name_col = next(c for c in g.columns if g[c].astype(str).map(key).isin(f.cle.unique()).sum() >= 13)
    g["cle"] = g[name_col].map(key)
    g = g.set_index("cle")
    nb = {k: [j for j in g.index if j != k and g.geometry[k].buffer(0.01).intersects(g.geometry[j])] for k in g.index}
    wide = f.pivot(index="start", columns="cle", values="l_incidents")
    lag = pd.DataFrame({k: wide[v].mean(axis=1) for k, v in nb.items()})
    lag = lag.stack().rename("l_voisins").reset_index().rename(columns={"level_1": "cle"})
    f = f.merge(lag, on=["start", "cle"], how="left").sort_values(["cle", "start"])
    gg = f.groupby("cle")
    for col in ["extent", "l_civils", "l_voisins"]:
        f["d_" + col] = f[col] - gg[col].shift()
    return f.drop(columns=["start"]), nb


SETS = {
    "Référence : violence (niveau, escalade)": ["l_inc", "d_l_inc"],
    "F1 + étendue": ["l_inc", "d_l_inc", "extent", "d_extent"],
    "F2 + juillet-septembre": ["l_inc", "d_l_inc", "l_late"],
    "F3 + rentrée (oct.-déc.)": ["l_inc", "d_l_inc", "l_rentree"],
    "F4 civils (au lieu de tout)": ["l_civils", "d_l_civils"],
    "F5 + voisins": ["l_inc", "d_l_inc", "l_voisins", "d_l_voisins"],
}


def main():
    pd.set_option("display.width", 220)
    p = build()
    f, nb = features("data/raw/externe/hdx_acled/acled_political_violence_month_year.xlsx",
                     "data/raw/externe/hdx_acled/acled_civilian_targeting_month_year.xlsx")
    print("Voisins :", {k: len(v) for k, v in nb.items()})
    d = p.merge(f.drop(columns=["incidents"]), on=["cle", "annee"], how="left")
    d["y_drop"] = (d.y_eleves < np.log(0.95)).astype(float)
    d.loc[d.y_eleves.isna(), "y_drop"] = np.nan
    cols = sorted({c for v in SETS.values() for c in v})
    d = d.dropna(subset=cols + ["y_drop"])
    years = sorted(d.annee.unique())
    preds, truth, num = {k: [] for k in SETS}, [], {k: [] for k in SETS}
    yrs = []
    for ty in years[3:]:
        tr, te = d[d.annee < ty], d[d.annee == ty]
        if tr.y_drop.nunique() < 2:
            continue
        truth += list(te.y_drop)
        yrs += [ty] * len(te)
        for k, c in SETS.items():
            m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(tr[c], tr.y_drop)
            preds[k] += list(m.predict_proba(te[c])[:, 1])
            X = np.column_stack([np.ones(len(tr))] + [tr[x] for x in c])
            b = np.linalg.lstsq(X, tr.y_eleves, rcond=None)[0]
            num[k] += list(np.column_stack([np.ones(len(te))] + [te[x] for x in c]) @ b)
    truth = np.array(truth)
    real = d.set_index("annee").loc[sorted(set(yrs))].y_eleves.values
    base = np.array(preds[list(SETS)[0]])
    rng = np.random.default_rng(SEED)
    idx = [rng.integers(0, len(truth), len(truth)) for _ in range(5000)]
    rows = []
    for k, pr in preds.items():
        pr = np.array(pr)
        gains = [roc_auc_score(truth[i], pr[i]) - roc_auc_score(truth[i], base[i]) for i in idx
                 if 0 < truth[i].sum() < len(i)]
        lo, hi = np.percentile(gains, [5, 95])
        e = np.abs(real - np.array(num[k])).mean() * 100
        rows.append({"variante": k, "AUC": roc_auc_score(truth, pr), "gain_AUC": roc_auc_score(truth, pr) - roc_auc_score(truth, base),
                     "IC90_gain": f"[{lo:+.3f} ; {hi:+.3f}]", "erreur_effectifs_%": e})
    rows.append({"variante": "« Comme l'an passé » (effectifs)", "AUC": np.nan, "gain_AUC": np.nan, "IC90_gain": "",
                 "erreur_effectifs_%": np.abs(real).mean() * 100})
    rows.append({"variante": "F6 combinaison (moitié modèle, moitié « comme l'an passé »)", "AUC": np.nan,
                 "gain_AUC": np.nan, "IC90_gain": "",
                 "erreur_effectifs_%": np.abs(real - 0.5 * np.array(num[list(SETS)[0]])).mean() * 100})
    r = pd.DataFrame(rows)
    print(f"\n=== Baisse > 5 % à la prochaine rentrée ({len(truth)} prédictions, {int(truth.sum())} baisses, "
          f"années {SHORT[min(yrs)]} à {SHORT[max(yrs)]}) et variation des effectifs ===")
    print(r.round(3).to_string(index=False))
    r.round(4).to_csv("analyse/P16_signaux_fins.csv", index=False)
    f.to_csv("analyse/P16_signaux_region_annee.csv", index=False)

    yrs = np.array(yrs)
    per = []
    for ty in sorted(set(yrs)):
        s = yrs == ty
        if 0 < truth[s].sum() < s.sum():
            per.append({"annee_t": SHORT[ty], "baisses": int(truth[s].sum()),
                        **{k.split(" ")[0]: roc_auc_score(truth[s], np.array(v)[s]) for k, v in preds.items()
                           if k.startswith(("Référence", "F2", "F3"))}})
    print("\nAUC par année (années avec au moins une baisse et une non-baisse) :")
    print(pd.DataFrame(per).round(2).to_string(index=False))
    calendar(d, f)


def calendar(d, f):
    n25 = pd.read_csv("analyse/panel_region_annee_2025.csv").drop_duplicates("region").set_index("region").region_2025
    names = d.drop_duplicates("cle").set_index("cle").region.map(n25)
    acled = pd.read_csv("analyse/acled_region_annee.csv").sort_values(["cle", "annee"])
    acled["l_inc"] = np.log1p(acled.incidents)
    acled["d_l_inc"] = acled.l_inc - acled.groupby("cle").l_inc.shift()
    cur = acled.merge(f.drop(columns=["incidents"]), on=["cle", "annee"], how="left")
    out = {}
    for label, cols, base_year in [("2025/26, alerte de janvier (oct.-déc. 2025 connus)", SETS["F3 + rentrée (oct.-déc.)"], "2024-2025"),
                                   ("2026/27, alerte de septembre (juil.-sept. 2026 connus)", SETS["F2 + juillet-septembre"], "2025-2026"),
                                   ("2026/27, référence (D12)", SETS["Référence : violence (niveau, escalade)"], "2025-2026")]:
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(d[cols], d.y_drop)
        x = cur[(cur.annee == base_year) & cur.cle.isin(names.index)].set_index("cle")
        assert x[cols].notna().all().all(), (label, x[cols])
        out[label] = pd.Series(m.predict_proba(x[cols])[:, 1] * 100, index=x.index).round()
    res = pd.DataFrame(out).set_index(names.reindex(pd.DataFrame(out).index)).sort_values(
        "2026/27, alerte de septembre (juil.-sept. 2026 connus)", ascending=False)
    print("\nProbabilité d'une baisse des effectifs de plus de 5 % (%) :")
    print(res.to_string())
    res.to_csv("analyse/P16_alertes_calendrier.csv")


if __name__ == "__main__":
    main()

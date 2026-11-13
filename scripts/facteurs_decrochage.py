"""Which drivers of dropout, besides insecurity, show up in the data? By former region (13)."""
import unicodedata

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

SEED = 2026
N_BOOT = 5000


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


FACTORS = {
    "violence": ("Violence (incidents, moyenne 21/22-24/25, log)", True),
    "deplaces": ("Déplacés accueillis (% de la population, 2022)", True),
    "pauvrete": ("Pauvreté (incidence 2021)", True),
    "faim": ("Faim (phase 3+, moyenne 21/22-23/24)", True),
    "meres": ("Femmes sans instruction (2021)", True),
    "grossesses": ("Grossesses précoces (fécondité 15-19 ans, 2021)", True),
    "cep": ("Réussite au CEP (moyenne 22/23-24/25)", False),
    "prescolaire": ("Préscolaire (taux brut 2024/25)", False),
}


def regions():
    p = pd.read_csv("analyse/panel_region_annee.csv")
    p = p[p.region != "NATIONAL"].copy()
    p["cle"] = p.region.map(key)
    t = pd.read_csv("data/tidy/presco_tidy.csv")
    pre = t[(t.table == "P5") & (t.sexe == "T") & (t.annee == "2024-2025") & (t.region != "NATIONAL")]
    pre = pre.assign(cle=pre.region.map(key)).set_index("cle").valeur
    acled = pd.read_csv("analyse/acled_region_annee.csv")
    acled["l_inc"] = np.log1p(acled.incidents)
    food = pd.read_csv("data/externe_propre/faim_cadre_harmonise_region_annee.csv")
    eds = pd.read_csv("data/externe_propre/eds_2021_regions.csv").set_index("cle")
    pdi = pd.read_csv("data/externe_propre/pdi_conasur_2022_regions.csv").set_index("cle")
    pov = pd.read_csv("data/externe_propre/pauvrete_ehcvm_2021_regions.csv")
    pov = pov.assign(cle=pov.region.map(key)).set_index("cle").incidence_pauvrete_2021_pct
    tap = p.pivot(index="cle", columns="annee", values="TAP_T")
    cep = p.pivot(index="cle", columns="annee", values="CEP_T")
    r = pd.DataFrame({
        "region": p.drop_duplicates("cle").set_index("cle").region,
        "TAP_avant_crise": tap[["2015-2016", "2016-2017", "2017-2018"]].mean(axis=1),
        "TAP_2024_25": tap["2024-2025"],
        "violence": acled[acled.annee.isin(["2021-2022", "2022-2023", "2023-2024", "2024-2025"])]
        .groupby("cle").l_inc.mean(),
        "deplaces": pdi.pdi_pct_population, "pauvrete": pov,
        "faim": food[food.annee.isin(["2021-2022", "2022-2023", "2023-2024"])].groupby("cle").faim_phase3plus_pct.mean(),
        "meres": eds.meres_sans_instruction_pct, "grossesses": eds.fecondite_15_19_pour_mille,
        "cep": cep[["2022-2023", "2023-2024", "2024-2025"]].mean(axis=1), "prescolaire": pre,
    })
    r["recul_TAP"] = r.TAP_2024_25 - r.TAP_avant_crise
    r["incidents_moy"] = acled[acled.annee.isin(["2021-2022", "2022-2023", "2023-2024", "2024-2025"])] \
        .groupby("cle").incidents.mean()
    assert r.notna().all().all(), r[r.isna().any(axis=1)]
    return r, p, acled, food


def partial_rank(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    if ex.std() == 0 or ey.std() == 0:
        return np.nan
    return np.corrcoef(ex, ey)[0, 1]


def level(r):
    print("=== 1. Quels facteurs vont avec un faible taux d'achèvement ? (13 régions, corrélation de rang) ===")
    rng = np.random.default_rng(SEED)
    n = len(r)
    boots = [rng.integers(0, n, n) for _ in range(N_BOOT)]
    rows = []
    for f, (label, _) in FACTORS.items():
        row = {"facteur": label}
        for out in ["TAP_avant_crise", "TAP_2024_25", "recul_TAP"]:
            row[out] = spearmanr(r[f], r[out])[0]
        if f != "violence":
            row["TAP_2024_25_sans_violence"] = partial_rank(r[f].values, r.TAP_2024_25.values, r.violence.values)
            row["recul_sans_violence"] = partial_rank(r[f].values, r.recul_TAP.values, r.violence.values)
            vals = []
            for b in boots:
                s = r.iloc[b]
                if s[f].nunique() > 2 and s.violence.nunique() > 2 and s.TAP_2024_25.nunique() > 2:
                    vals.append(partial_rank(s[f].values, s.TAP_2024_25.values, s.violence.values))
            lo, hi = np.nanpercentile(vals, [5, 95])
            row["IC90_sans_violence"] = f"[{lo:+.2f} ; {hi:+.2f}]"
        rows.append(row)
    out = pd.DataFrame(rows)
    print(out.round(2).to_string(index=False))
    print("Lecture : une corrélation négative = plus le facteur est fort, plus le taux d'achèvement est bas. "
          "« sans violence » = une fois retiré ce que la violence explique déjà. IC90 : bootstrap sur les régions.")
    out.round(3).to_csv("analyse/P14_facteurs_correlations.csv", index=False)
    print("\nCorrélations entre facteurs (rang) :")
    print(r[list(FACTORS)].corr(method="spearman").round(2).to_string())


def fe_fit(df, y, year_fe):
    df = df.reset_index(drop=True)
    X = pd.get_dummies(df.cle, drop_first=False, dtype=float)
    if year_fe:
        X = X.join(pd.get_dummies(df.annee, drop_first=True, dtype=float))
    X = X.assign(l_inc=df.l_inc.values, faim10=df.faim10.values)
    beta = np.linalg.lstsq(X.values, df[y].values, rcond=None)[0]
    return dict(zip(X.columns, beta))


def fe_row(d, y, year_fe, rng, n_boot=2000):
    b = fe_fit(d, y, year_fe)
    keys = d.cle.unique()
    bs = []
    for _ in range(n_boot):
        pick = rng.choice(keys, len(keys))
        s = pd.concat([d[d.cle == k].assign(cle=f"{k}_{i}") for i, k in enumerate(pick)])
        bs.append(fe_fit(s, y, year_fe))
    ci = {v: np.percentile([x[v] for x in bs], [5, 95]) for v in ["l_inc", "faim10"]}
    return {"resultat": y, "effets_annee": year_fe, "regions": len(keys),
            "violence_coef": b["l_inc"], "violence_IC90": f"[{ci['l_inc'][0]:+.3f} ; {ci['l_inc'][1]:+.3f}]",
            "faim_+10pts_coef": b["faim10"], "faim_IC90": f"[{ci['faim10'][0]:+.3f} ; {ci['faim10'][1]:+.3f}]"}


def panel(p, acled, food):
    print("\n=== 2. La faim fait-elle bouger l'école au-delà de la violence ? (panel 2014/15-2023/24, effets fixes) ===")
    d = p.merge(acled[["cle", "annee", "l_inc"]], on=["cle", "annee"]).merge(
        food[["cle", "annee", "faim_phase3plus_pct"]], on=["cle", "annee"])
    d["faim10"] = d.faim_phase3plus_pct / 10
    d["log_eleves"] = np.log(d.eleves_T)
    rng = np.random.default_rng(SEED)
    rows = []

    for y, unit in [("TAP_T", "points de TAP"), ("log_eleves", "log des effectifs")]:
        for year_fe in [False, True]:
            rows.append(fe_row(d, y, year_fe, rng) | {"unite": unit})
    out = pd.DataFrame(rows)
    print(out.round(3).to_string(index=False))
    within = d.assign(f=d.faim10 - d.groupby("cle").faim10.transform("mean"),
                      v=d.l_inc - d.groupby("cle").l_inc.transform("mean"))
    print(f"Corrélation faim / violence au sein des régions : {np.corrcoef(within.f, within.v)[0, 1]:.2f} "
          f"({len(d)} observations)")
    out.round(4).to_csv("analyse/P14_faim_panel.csv", index=False)
    return d


def robustness(d):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    print("\n=== 2 bis. Contrôles du résultat sur la faim ===")
    top = d[d.annee >= "2019-2020"].groupby("cle").l_inc.mean().nlargest(4).index
    calm = d[~d.cle.isin(top)]
    rng = np.random.default_rng(SEED)
    rows = [fe_row(calm, "TAP_T", fe, rng) for fe in [False, True]]
    print(f"(a) Sans les 4 régions les plus touchées ({', '.join(sorted(top))}) :")
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    pd.DataFrame(rows).round(4).to_csv("analyse/P14_faim_regions_calmes.csv", index=False)

    d = d.sort_values(["cle", "annee"]).copy()
    g = d.groupby("cle")
    d["d_l_inc"] = d.l_inc - g.l_inc.shift()
    d["d_faim10"] = d.faim10 - g.faim10.shift()
    d["y_drop"] = (np.log(g.eleves_T.shift(-1) / d.eleves_T) < np.log(0.95)).astype(float)
    d.loc[g.eleves_T.shift(-1).isna(), "y_drop"] = np.nan
    data = d.dropna(subset=["d_l_inc", "d_faim10", "y_drop"])
    years = sorted(data.annee.unique())
    sets = {"Violence (niveau, escalade)": ["l_inc", "d_l_inc"], "Faim (niveau, hausse)": ["faim10", "d_faim10"],
            "Violence et faim": ["l_inc", "d_l_inc", "faim10", "d_faim10"]}
    preds, truth = {k: [] for k in sets}, []
    for ty in years[3:]:
        tr, te = data[data.annee < ty], data[data.annee == ty]
        if tr.y_drop.nunique() < 2:
            continue
        truth += list(te.y_drop)
        for k, cols in sets.items():
            m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(tr[cols], tr.y_drop)
            preds[k] += list(m.predict_proba(te[cols])[:, 1])
    print(f"(b) Annoncer une baisse des effectifs > 5 % l'année suivante ({len(truth)} prédictions hors échantillon, "
          f"{int(sum(truth))} baisses, années {years[3]} à {years[-1]}) :")
    for k, pr in preds.items():
        print(f"  {k:30s} AUC {roc_auc_score(truth, pr):.2f}")


def profile(r):
    print("\n=== 3. Profil des facteurs par région (1 = parmi les 4 plus exposées) ===")
    prio = pd.read_csv("analyse/P13_matrice_priorite_2026_27.csv")
    n25 = pd.read_csv("analyse/panel_region_annee_2025.csv").drop_duplicates("region").set_index("region").region_2025
    r = r.assign(region_2025=r.region.map(n25))
    r = r.merge(prio[["region_2025", "priorite"]], on="region_2025").set_index("region_2025")
    tiers = pd.DataFrame(index=r.index)
    for f, (_, up) in FACTORS.items():
        rank = r[f].rank(ascending=not up, method="min")
        tiers[f] = np.where(rank <= 4, 1, np.where(rank >= 10, 3, 2))
    tiers["nb_facteurs_forts"] = (tiers[list(FACTORS)] == 1).sum(axis=1)
    out = r[["priorite", "TAP_2024_25", "incidents_moy"] + list(FACTORS)].join(tiers.rename(columns={f: f + "_niveau" for f in FACTORS}))
    out = out.sort_values(["priorite", "TAP_2024_25"])
    show = out[["priorite", "TAP_2024_25", "nb_facteurs_forts"] + [f + "_niveau" for f in FACTORS]]
    print(show.to_string())
    out.round(2).to_csv("analyse/P14_profil_facteurs.csv")


def main():
    pd.set_option("display.width", 250)
    r, p, acled, food = regions()
    level(r)
    d = panel(p, acled, food)
    robustness(d)
    profile(r)


if __name__ == "__main__":
    main()

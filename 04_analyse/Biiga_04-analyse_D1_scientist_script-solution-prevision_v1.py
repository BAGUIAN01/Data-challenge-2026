"""Search for a regional forecast that works, with the candidate list fixed before running."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import unicodedata

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]
SHORT = {f"{y}-{y + 1}": f"{str(y)[2:]}/{str(y + 1)[2:]}" for y in range(2014, 2028)}


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


def ols(x, y):
    X = np.column_stack([np.ones(len(x[0]))] + [np.asarray(c, float) for c in x])
    return np.linalg.lstsq(X, np.asarray(y, float), rcond=None)[0]


def pred(beta, x):
    X = np.column_stack([np.ones(len(x[0]))] + [np.asarray(c, float) for c in x])
    return X @ beta


def build():
    p = pd.read_csv(chemins.path("panel_region_annee.csv"))
    p = p[p.region != "NATIONAL"].copy()
    p["cle"] = p.region.map(key)
    acled = pd.read_csv(chemins.path("acled_region_annee.csv"))
    p = p.merge(acled, on=["cle", "annee"], how="left").sort_values(["region", "annee"])
    g = p.groupby("region")
    p["l_inc"] = np.log1p(p.incidents)
    p["d_l_inc"] = p.l_inc - g.l_inc.shift()
    p["dTAP"] = p.TAP_T - g.TAP_T.shift()
    p["sorties_prev"] = g.sorties_app.shift()
    p["y_eleves"] = g.dlog_eleves.shift(-1)
    p["y_ecoles"] = g.dlog_ecoles.shift(-1)
    p["y_dTAP"] = g.TAP_T.shift(-1) - p.TAP_T
    return p


def where(p):
    print("=== 1. OÙ sera le risque l'an prochain ? Stabilité du classement des régions ===")
    rows = []
    for i in range(1, 10):
        a = p[p.annee == YEARS[i - 1]].set_index("region")
        b = p[p.annee == YEARS[i]].set_index("region")
        low_a = set(a.TAP_T.nsmallest(4).index)
        low_b = set(b.TAP_T.nsmallest(4).index)
        row = {"annee": SHORT[YEARS[i]], "rang_TAP": spearmanr(a.TAP_T, b.TAP_T.loc[a.index])[0],
               "4_plus_bas_retrouves": len(low_a & low_b)}
        if i >= 2:
            sa, sb = a.sorties_app.dropna(), b.sorties_app.dropna()
            common = sa.index.intersection(sb.index)
            if len(common) > 5:
                row["rang_sorties"] = spearmanr(sa.loc[common], sb.loc[common])[0]
        rows.append(row)
    r = pd.DataFrame(rows)
    print(r.round(2).to_string(index=False))
    print(f"Moyennes : rang du TAP {r.rang_TAP.mean():.2f} ; 4 régions les plus basses retrouvées "
          f"{r['4_plus_bas_retrouves'].mean():.1f} sur 4 ; rang des sorties {r.rang_sorties.mean():.2f}")
    r.round(3).to_csv(chemins.path("P13_stabilite_classement.csv"), index=False)


def how_many(p):
    print("\n=== 2. COMBIEN d'élèves l'an prochain ? Erreur absolue moyenne sur la variation (%) ===")
    d = p.dropna(subset=["y_eleves", "y_ecoles", "dlog_eleves", "dlog_ecoles", "l_inc", "d_l_inc"])
    years = sorted(d.annee.unique())
    rows, preds = [], []
    for ty in years[3:]:
        tr, te = d[d.annee < ty], d[d.annee == ty]
        out = {"B0 comme l'an passé": np.zeros(len(te)), "B1 même variation": te.dlog_eleves.values}
        b = ols([tr.l_inc, tr.d_l_inc], tr.y_eleves)
        out["E1 violence"] = pred(b, [te.l_inc, te.d_l_inc])
        b = ols([tr.l_inc, tr.d_l_inc, tr.dlog_eleves], tr.y_eleves)
        out["E2 violence + rebond"] = pred(b, [te.l_inc, te.d_l_inc, te.dlog_eleves])
        bs = ols([tr.l_inc, tr.d_l_inc, tr.dlog_ecoles], tr.y_ecoles)
        bp = ols([tr.y_ecoles], tr.y_eleves)
        out["E3 violence → écoles → élèves"] = pred(bp, [pred(bs, [te.l_inc, te.d_l_inc, te.dlog_ecoles])])
        row = {"annee_predite": SHORT[years[years.index(ty) + 1]] if ty != years[-1] else "24/25"}
        row.update({k: np.abs(te.y_eleves.values - v).mean() * 100 for k, v in out.items()})
        rows.append(row)
        for k, v in out.items():
            preds.append(pd.DataFrame({"annee": ty, "region": te.region.values, "modele": k, "prevu": v,
                                       "reel": te.y_eleves.values}))
    r = pd.DataFrame(rows)
    r.loc[len(r)] = ["moyenne"] + list(r.iloc[:, 1:].mean())
    print(r.round(2).to_string(index=False))
    base = r.iloc[-1]["B0 comme l'an passé"]
    for c in r.columns[2:]:
        print(f"  {c:32s} gain par rapport à « comme l'an passé » : {(1 - r.iloc[-1][c] / base) * 100:+.0f} %")
    r.round(2).to_csv(chemins.path("P13_effectifs_modeles.csv"), index=False)
    allp = pd.concat(preds)
    big = allp[np.abs(allp.reel) > np.log(1.05)]
    print(f"\nSens de la variation quand elle dépasse 5 % ({big.region.nunique()} régions, "
          f"{len(big) // allp.modele.nunique()} cas) :")
    for k, gk in big.groupby("modele", sort=False):
        if k.startswith("B0"):
            continue
        print(f"  {k:32s} sens juste {(np.sign(gk.prevu) == np.sign(gk.reel)).mean() * 100:.0f} %")
    allp.to_csv(chemins.path("P13_effectifs_predictions.csv"), index=False)
    return d


def how_much(p):
    print("\n=== 3. DE COMBIEN bougera le taux d'achèvement ? Erreur absolue moyenne (points) ===")
    d = p.dropna(subset=["y_dTAP", "dTAP", "d_l_inc"])
    years = sorted(d.annee.unique())
    rows = []
    for ty in years[3:]:
        tr, te = d[d.annee < ty], d[d.annee == ty]
        row = {"annee_predite": SHORT[years[years.index(ty) + 1]] if ty != years[-1] else "24/25",
               "B0 comme l'an passé": np.abs(te.y_dTAP).mean()}
        b = ols([tr.dTAP], tr.y_dTAP)
        row["T1 retour partiel"] = np.abs(te.y_dTAP - pred(b, [te.dTAP])).mean()
        b = ols([tr.dTAP, tr.d_l_inc], tr.y_dTAP)
        row["T2 retour + escalade"] = np.abs(te.y_dTAP - pred(b, [te.dTAP, te.d_l_inc])).mean()
        rows.append(row)
    r = pd.DataFrame(rows)
    r.loc[len(r)] = ["moyenne"] + list(r.iloc[:, 1:].mean())
    print(r.round(2).to_string(index=False))
    r.round(2).to_csv(chemins.path("P13_TAP_modeles.csv"), index=False)


def priority(tap, tap_nat, prob):
    if tap < tap_nat and prob >= 0.40:
        return 1
    if tap < tap_nat or prob >= 0.15:
        return 2
    return 3


def backtest_matrix(p):

    print("\n=== 4. La matrice de priorité, rejouée sur le passé (année t -> ce qui arrive en t+1) ===")
    nat = pd.read_csv(chemins.path("panel_region_annee.csv")).query("region == 'NATIONAL'").set_index("annee").TAP_T
    d = p.dropna(subset=["l_inc", "d_l_inc", "y_eleves"]).copy()
    d["y_drop"] = (d.y_eleves < np.log(0.95)).astype(int)
    d["lost"] = np.maximum(0, d.eleves_T * (1 - np.exp(d.y_eleves)))
    years = sorted(d.annee.unique())
    rows = []
    for ty in years[3:]:
        tr, te = d[d.annee < ty], d[d.annee == ty].copy()
        if tr.y_drop.nunique() < 2:
            continue
        mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(tr[["l_inc", "d_l_inc"]], tr.y_drop)
        te["prob"] = mdl.predict_proba(te[["l_inc", "d_l_inc"]])[:, 1]
        te["prio"] = [priority(t, nat[ty], pr) for t, pr in zip(te.TAP_T, te.prob)]
        p1 = te.prio == 1
        rows.append({"annee_t": SHORT[ty], "regions_P1": int(p1.sum()), "baisses_t+1": int(te.y_drop.sum()),
                     "baisses_dans_P1": int(te.y_drop[p1].sum()), "eleves_perdus_t+1": round(te.lost.sum()),
                     "perdus_dans_P1": round(te.lost[p1].sum()),
                     "baisses_P1_ou_P2": int(te.y_drop[te.prio <= 2].sum())})
    r = pd.DataFrame(rows)
    print(r.to_string(index=False))
    share_regions = r.regions_P1.sum() / (13 * len(r))
    share_drops = r["baisses_dans_P1"].sum() / r["baisses_t+1"].sum()
    share_lost = r.perdus_dans_P1.sum() / r["eleves_perdus_t+1"].sum()
    missed = r["baisses_t+1"].sum() - r.baisses_P1_ou_P2.sum()
    print(f"Priorité 1 = {share_regions:.0%} des régions-années, mais {share_drops:.0%} des fortes baisses de l'année "
          f"suivante et {share_lost:.0%} des élèves perdus. Baisses hors priorités 1 et 2 : {missed} sur "
          f"{r['baisses_t+1'].sum()}.")
    r.to_csv(chemins.path("P13_matrice_rejouee.csv"), index=False)


def matrix_2026(p):
    print("\n=== 5. Matrice de priorité pour la rentrée 2026/27 ===")
    prob = pd.read_csv(chemins.path("P11_probabilites_alerte.csv")).set_index("region_2025")["rentrée 2026/27"] / 100
    p9 = pd.read_csv(chemins.path("P9_prevision_2025_26_alerte.csv")).set_index("region_2025")
    tap_nat = pd.read_csv(chemins.path("panel_region_annee.csv")).query(
        "region == 'NATIONAL' and annee == '2024-2025'").TAP_T.iloc[0]
    m = pd.DataFrame({"TAP_24_25": p9.TAP_24_25, "probabilite_baisse_2026_27": prob.reindex(p9.index),
                      "enfants_hors_CM2": p9.enfants_hors_CM2_estimes, "profil": p9.profil})
    m["priorite"] = [priority(t, tap_nat, pr) for t, pr in zip(m.TAP_24_25, m.probabilite_baisse_2026_27)]
    m = m.sort_values(["priorite", "TAP_24_25"])
    print(m.to_string())
    tot = m.enfants_hors_CM2.sum()
    for k, g in m.groupby("priorite"):
        print(f"Priorité {k} : {len(g)} régions, {g.enfants_hors_CM2.sum():,.0f} enfants hors CM2 "
              f"({g.enfants_hors_CM2.sum() / tot:.0%})")
    m.to_csv(chemins.path("P13_matrice_priorite_2026_27.csv"))


def main():
    pd.set_option("display.width", 220)
    p = build()
    where(p)
    how_many(p)
    how_much(p)
    backtest_matrix(p)
    matrix_2026(p)


if __name__ == "__main__":
    main()

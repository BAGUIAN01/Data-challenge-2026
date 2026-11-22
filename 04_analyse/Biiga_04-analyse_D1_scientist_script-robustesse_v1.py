"""Robustness of the retained alert: the "like last year" baseline, the 5 % threshold, the log of violence."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 2026
ml = chemins.module("machine_learning")


def sample():
    p = ml.build()
    g = p.groupby("region")
    p["change_next"] = g.eleves_T.shift(-1) / p.eleves_T - 1
    p["inc_prev"] = g.incidents.shift()
    p["d_raw"] = p.incidents - p.inc_prev
    p["drop_last_year"] = (p.dlog_eleves < np.log(0.95)).astype(float)
    return p, p.dropna(subset=ml.FEATURES + ["y_dTAP", "y_drop", "d_raw"]).copy()


def replay(d, target, cols):
    years = sorted(d.annee.unique())
    truth, pred = [], []
    for ty in years[3:]:
        tr, te = d[d.annee < ty], d[d.annee == ty]
        truth += list(te[target])
        if tr[target].nunique() < 2:
            pred += [tr[target].mean()] * len(te)
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(tr[cols], tr[target])
        pred += list(m.predict_proba(te[cols])[:, 1])
    return np.array(truth), np.array(pred)


def column(d, col):
    """Same rows, in the same order, as replay(): year by year."""
    years = sorted(d.annee.unique())
    return np.concatenate([d[d.annee == ty][col].values for ty in years[3:]])


def main():
    pd.set_option("display.width", 200)
    p, d = sample()
    truth, logit = replay(d, "y_drop", ["l_inc", "d_l_inc"])
    last = column(d, "drop_last_year")
    change = -column(d, "dlog_eleves")
    first = (truth == 1) & (last == 0)
    rows = [("Hasard", 0.5), ("« Comme l'an passé » : forte baisse l'an passé (baseline)", roc_auc_score(truth, last)),
            ("« Comme l'an passé » : ampleur de la variation de l'an passé", roc_auc_score(truth, change)),
            ("Logistique, niveau + escalade de la violence (retenue)", roc_auc_score(truth, logit))]
    base = pd.DataFrame(rows, columns=["approche", "AUC"])
    base.round(3).to_csv(chemins.path("P20_baseline_alerte.csv"), index=False)
    print(f"=== 1. La baseline « comme l'an passé » ({len(truth)} prévisions, {int(truth.sum())} fortes baisses) ===")
    print(base.round(3).to_string(index=False))
    print(f"Fortes baisses précédées d'une forte baisse l'an passé : {int((last * truth).sum())} sur {int(truth.sum())}. "
          f"Chutes sans précédent : {int(first.sum())}, dont {int((logit[first] >= 0.40).sum())} signalées à 40 % ou plus par le modèle retenu.")

    rows = []
    for s in (0.03, 0.05, 0.07, 0.10, 0.15):
        e = p.copy()
        e["y_s"] = (e.change_next < -s).astype(float)
        e.loc[e.change_next.isna(), "y_s"] = np.nan
        e = e.dropna(subset=ml.FEATURES + ["y_dTAP", "y_drop"])
        t, pr = replay(e, "y_s", ["l_inc", "d_l_inc"])
        rows.append({"seuil_forte_baisse": f"plus de {s * 100:.0f} %", "baisses_apprentissage": int(e.y_s.sum()),
                     "baisses_testees": int(t.sum()), "AUC": round(roc_auc_score(t, pr), 3)})
    thr = pd.DataFrame(rows)
    thr.to_csv(chemins.path("P20_seuil_baisse.csv"), index=False)
    print("\n=== 2. Le seuil de forte baisse : même modèle, même test ===")
    print(thr.to_string(index=False))

    variants = {"ln(1 + incidents) et escalade en ln (retenu)": ["l_inc", "d_l_inc"], "incidents bruts et hausse brute": ["incidents", "d_raw"],
                "ln(1 + incidents) seul": ["l_inc"], "escalade en ln seule": ["d_l_inc"]}
    preds = {k: replay(d, "y_drop", c)[1] for k, c in variants.items()}
    rows = [{"variables": k, "AUC": round(roc_auc_score(truth, v), 3), "Brier": round(brier_score_loss(truth, v), 3)} for k, v in preds.items()]
    a, b = preds["ln(1 + incidents) et escalade en ln (retenu)"], preds["incidents bruts et hausse brute"]
    rng = np.random.default_rng(SEED)
    gaps = []
    for _ in range(5000):
        i = rng.integers(0, len(truth), len(truth))
        if 0 < truth[i].sum() < len(i):
            gaps.append(roc_auc_score(truth[i], b[i]) - roc_auc_score(truth[i], a[i]))
    lo, hi = np.percentile(gaps, [5, 95])
    logs = pd.DataFrame(rows)
    logs["ecart_AUC_brut_moins_ln_IC90"] = ["", f"[{lo:+.3f} ; {hi:+.3f}]", "", ""]
    logs.to_csv(chemins.path("P20_logarithme.csv"), index=False)
    print("\n=== 3. Le logarithme de la violence : même modèle, même test ===")
    print(logs.to_string(index=False))
    print(f"Écart d'AUC bruts − ln : {roc_auc_score(truth, b) - roc_auc_score(truth, a):+.3f}, IC 90 % [{lo:+.3f} ; {hi:+.3f}] : non démontré.")


if __name__ == "__main__":
    main()

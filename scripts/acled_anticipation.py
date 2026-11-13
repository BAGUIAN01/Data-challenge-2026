"""Does insecurity (ACLED) help anticipate next year's figures, beyond "same as last year"?

ACLED political-violence events (HDX, by former province and month) are summed by
former region and school year, October to September: violence between two school
censuses is known before the next one. For each region and year t, we predict the
change from t to t+1 of three figures (completion rate, log pupils, log schools)
from the violence of school year t, with a model trained on earlier years only.

Writes analyse/acled_region_annee.csv and analyse/P8_anticipation_acled.csv.
Usage: python acled_anticipation.py <acled.xlsx> analyse/panel_region_annee.csv analyse/
"""
import sys
import unicodedata

import numpy as np
import pandas as pd

MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


def school_year(year, month):
    start = year if month >= 10 else year - 1  # October to September
    return f"{start}-{start + 1}"


def main():
    acled = pd.read_excel(sys.argv[1], sheet_name="Data")
    panel = pd.read_csv(sys.argv[2])
    out = sys.argv[3].rstrip("/")

    acled["annee"] = [school_year(y, MONTHS[m]) for y, m in zip(acled.Year, acled.Month)]
    acled["cle"] = acled.Admin1.map(key)
    a = acled.groupby(["cle", "annee"])[["Events", "Fatalities"]].sum().reset_index()
    a.columns = ["cle", "annee", "incidents", "morts"]
    a.to_csv(f"{out}/acled_region_annee.csv", index=False)

    p = panel[panel.region != "NATIONAL"].copy()
    p["cle"] = p.region.map(key)
    missing = set(p.cle) - set(a.cle)
    if missing:
        raise SystemExit(f"Régions sans données ACLED : {missing}")
    p = p.merge(a, on=["cle", "annee"], how="left").sort_values(["region", "annee"])
    g = p.groupby("region")
    p["l_inc"] = np.log1p(p.incidents)
    p["d_l_inc"] = p.l_inc - g.l_inc.shift()
    p["l_morts"] = np.log1p(p.morts)
    targets = {
        "TAP (points)": p.groupby("region").TAP_T.shift(-1) - p.TAP_T,
        "élèves (log)": np.log(g.eleves_T.shift(-1) / p.eleves_T),
        "écoles (log)": np.log(g.ecoles.shift(-1) / p.ecoles),
    }
    feats = ["l_inc", "d_l_inc", "l_morts"]
    rows = []
    for tname, y in targets.items():
        m = p.assign(y=y).dropna(subset=feats + ["y"])
        years = sorted(m.annee.unique())
        print(f"\n=== {tname} : corrélations avec la variation de l'année suivante (n = {len(m)}) ===")
        for f in feats:
            print(f"  {f:8s} r = {np.corrcoef(m[f], m.y)[0, 1]:+.2f}")
        for ty in years[3:]:  # at least 3 years of training
            tr, te = m[m.annee < ty], m[m.annee == ty]
            X = np.c_[np.ones(len(tr)), tr[feats].values]
            coef, *_ = np.linalg.lstsq(X, tr.y.values, rcond=None)
            pred = np.c_[np.ones(len(te)), te[feats].values] @ coef
            scale = 100 if "log" in tname else 1  # log changes reported in %
            rows.append({"cible": tname, "annee_de_depart": ty,
                         "erreur_persistance": np.abs(te.y).mean() * scale,
                         "erreur_avec_ACLED": np.abs(te.y - pred).mean() * scale})
    res = pd.DataFrame(rows)
    res["gain_%"] = (1 - res.erreur_avec_ACLED / res.erreur_persistance) * 100
    res.round(2).to_csv(f"{out}/P8_anticipation_acled.csv", index=False)
    pd.set_option("display.width", 200)
    print("\n=== Validation sur années non vues (erreur absolue moyenne ; log en %) ===")
    print(res.round(2).to_string(index=False))
    print("\nMoyenne par cible :")
    print(res.groupby("cible")[["erreur_persistance", "erreur_avec_ACLED"]].mean().assign(
        gain_pct=lambda x: (1 - x.erreur_avec_ACLED / x.erreur_persistance) * 100).round(2).to_string())


if __name__ == "__main__":
    main()

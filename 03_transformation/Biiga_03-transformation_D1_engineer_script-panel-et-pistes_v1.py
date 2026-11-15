"""Analyses behind each avenue ("piste") for Défi 1, from the challenge data only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import sys

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]
SHORT = {y: y[2:4] + "/" + y[7:] for y in YEARS}
BASELINE = ["2015-2016", "2016-2017"]


def panel(d):
    keep = {"E1": "eleves", "E5": "nouveaux_CP1", "E6": "TBA", "E7": "TBS", "E8": "TAP", "E9": "CEP"}
    x = d[d.table.isin(keep) & (d.statut == "Total")].copy()
    x["var"] = x.table.map(keep) + "_" + x.sexe
    p = x.pivot_table(index=["region", "annee"], columns="var", values="valeur")
    schools = d[(d.table == "E13")].pivot_table(index=["region", "annee"], columns="statut", values="valeur")
    p["ecoles"] = schools["Total"]
    p["ecoles_publiques"] = schools["Public"]
    p["IPS_TAP"] = d[d.table == "E12"].set_index(["region", "annee"]).valeur
    return p.reset_index()


def main():
    d = pd.read_csv(sys.argv[1])
    out = sys.argv[2].rstrip("/")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    p = panel(d)
    p = p.sort_values(["region", "annee"]).reset_index(drop=True)
    g = p.groupby("region")
    p["sorties_app"] = 1 - (g.eleves_T.shift(-1) - g.nouveaux_CP1_T.shift(-1)) / p.eleves_T
    p["dlog_eleves"] = np.log(p.eleves_T / g.eleves_T.shift())
    p["dlog_ecoles"] = np.log(p.ecoles / g.ecoles.shift())
    p["pop6_impl"] = p.nouveaux_CP1_T / (p.TBA_T / 100)
    p.to_csv(chemins.path("panel_region_annee.csv"), index=False)
    reg = p[p.region != "NATIONAL"].copy()
    nat = p[p.region == "NATIONAL"].set_index("annee")

    print("\n=== P1. Sorties en excès par rapport à l'habitude de la région ===")
    base = reg[reg.annee.isin(BASELINE)].groupby("region").sorties_app.mean()
    reg["sorties_base"] = reg.region.map(base)
    e4 = d[(d.table == "E4") & d.statut.isin(["Public", "Prive"]) & (d.sexe == "T")]
    cm2 = e4[e4.niveau == "CM2"].groupby("annee").valeur.sum() / e4[e4.niveau != "Total"].groupby("annee").valeur.sum()
    reg["part_CM2_nat"] = reg.annee.map(cm2)
    cm2_base = cm2[BASELINE].mean()
    reg["exces_brut"] = (reg.sorties_app - reg.sorties_base) * reg.eleves_T
    reg["exces_eleves"] = (reg.sorties_app - reg.sorties_base - (reg.part_CM2_nat - cm2_base)) * reg.eleves_T
    print("Part nationale du CM2 dans les effectifs (%) :", (cm2 * 100).round(1).rename(SHORT).to_dict())
    ex = reg.dropna(subset=["exces_eleves"]).pivot_table(index="region", columns="annee", values="exces_eleves")
    ex.columns = [SHORT[c] + "→" for c in ex.columns]
    ex["cumul_17_18_a_23_24"] = ex.iloc[:, 2:].sum(axis=1)
    ex["part_eleves_2017_18_%"] = (ex["cumul_17_18_a_23_24"] /
                                  reg[reg.annee == "2017-2018"].set_index("region").eleves_T * 100)
    ex["sorties_base_%"] = base * 100
    raw_part = reg.dropna(subset=["exces_brut"])
    ex["cumul_sans_correction_CM2"] = raw_part[raw_part.annee >= "2017-2018"].groupby("region").exces_brut.sum()
    ex = ex.sort_values("cumul_17_18_a_23_24", ascending=False)
    ex.round(1).to_csv(chemins.path("P1_sorties_excedentaires.csv"))
    print(ex[["sorties_base_%", "cumul_sans_correction_CM2", "cumul_17_18_a_23_24", "part_eleves_2017_18_%"]].round(1).to_string())
    print(f"Somme des 13 régions : {ex.cumul_17_18_a_23_24.sum():,.0f} élèves (les départs vers une autre région"
          " apparaissent en plus au départ et en moins à l'arrivée, ils s'annulent dans la somme)".replace(",", " "))

    print("\n=== P2. Typologie des trajectoires régionales (classification ascendante de Ward, 4 indicateurs centrés réduits) ===")
    w = reg.pivot_table(index="region", columns="annee", values=["eleves_T", "ecoles", "TAP_T"])
    feat = pd.DataFrame({
        "TAP_2024_25": w["TAP_T"]["2024-2025"],
        "TAP_variation_pts": w["TAP_T"]["2024-2025"] - w["TAP_T"]["2015-2016"],
        "ecoles_pire_chute_%": ((w["ecoles"] / w["ecoles"].cummax(axis=1) - 1).min(axis=1) * 100),
        "eleves_pire_chute_%": ((w["eleves_T"] / w["eleves_T"].cummax(axis=1) - 1).min(axis=1) * 100),
    })
    z = (feat - feat.mean()) / feat.std()
    lk = linkage(z.values, method="ward")
    for k in (3, 4):
        feat[f"groupe_k{k}"] = fcluster(lk, k, criterion="maxclust")
    feat["exces_cumule"] = ex["cumul_17_18_a_23_24"]
    feat = feat.sort_values(["groupe_k4", "TAP_2024_25"])
    feat.round(1).to_csv(chemins.path("P2_typologie_regions.csv"))
    print(feat.round(1).to_string())

    print("\n=== P3. Contributions régionales au recul national du TAP (21/22 -> 24/25) ===")
    sh = reg.pivot_table(index="region", columns="annee", values="pop6_impl")
    wts = sh / sh.sum()
    tap = reg.pivot_table(index="region", columns="annee", values="TAP_T")
    recon = (wts * tap).sum()
    chk = pd.DataFrame({"TAP_national_publie": nat.TAP_T, "TAP_reconstitue_ponderations_pop6": recon}).round(1)
    chk.index = [SHORT[i] for i in chk.index]
    print("Vérification : moyenne des TAP régionaux pondérée par la population de 6 ans implicite")
    print(chk.T.to_string())
    a, b = "2021-2022", "2024-2025"
    contrib = (wts[b] * tap[b] - wts[a] * tap[a]).rename("contribution_pts").to_frame()
    contrib["TAP_21_22"] = tap[a]
    contrib["TAP_24_25"] = tap[b]
    contrib["poids_21_22_%"] = wts[a] * 100
    contrib["poids_24_25_%"] = wts[b] * 100
    contrib["part_du_recul_%"] = contrib.contribution_pts / contrib.contribution_pts.sum() * 100
    contrib = contrib.sort_values("contribution_pts")
    contrib.round(2).to_csv(chemins.path("P3_contributions_recul_TAP.csv"))
    print(contrib.round(2).to_string())
    print(f"Total reconstitué : {contrib.contribution_pts.sum():.1f} points ; publié : {nat.TAP_T[b] - nat.TAP_T[a]:.1f} points")

    print("\n=== P4. Entrée et sortie du cycle, national ===")
    e2 = d[(d.table == "E2") & (d.sexe == "T")].pivot_table(index="annee", columns="statut", values="valeur")
    e3 = d[(d.table == "E3") & (d.sexe == "T")].pivot_table(index="annee", columns="milieu", values="valeur")
    e4 = d[(d.table == "E4") & d.statut.isin(["Public", "Prive"]) & (d.sexe == "T")]
    gr = e4.groupby(["niveau", "annee"]).valeur.sum().unstack("annee")
    flow = pd.DataFrame({
        "nouveaux_CP1": nat.nouveaux_CP1_T, "TBA_%": nat.TBA_T, "TAP_%": nat.TAP_T,
        "CP1": gr.loc["CP1"], "CM2": gr.loc["CM2"],
        "public": e2["Public"], "prive": e2["Prive"], "urbain": e3["Urbain"], "rural": e3["Rural"],
    })
    flow["CM2_sur_CP1_5ans_avant_%"] = flow.CM2 / flow.CP1.shift(5) * 100
    flow.index = [SHORT[i] for i in flow.index]
    flow.round(1).to_csv(chemins.path("P4_entree_sortie_national.csv"))
    print(flow.round(1).to_string())

    print("\n=== P5. Achèvement des garçons et des filles ===")
    tg = reg.pivot_table(index="region", columns="annee", values="TAP_G")
    tf = reg.pivot_table(index="region", columns="annee", values="TAP_F")
    gen = pd.DataFrame({
        "TAP_G_21_22": tg[a], "TAP_G_24_25": tg[b], "recul_G_pts": tg[b] - tg[a],
        "TAP_F_21_22": tf[a], "TAP_F_24_25": tf[b], "recul_F_pts": tf[b] - tf[a],
        "ecart_F_moins_G_24_25": tf[b] - tg[b],
    }).sort_values("ecart_F_moins_G_24_25")
    gen.round(1).to_csv(chemins.path("P5_genre.csv"))
    print(gen.round(1).to_string())

    print("\n=== P6. Anticiper le TAP de l'année suivante : validation sur années non vues ===")
    reg = reg.sort_values(["region", "annee"])
    gg = reg.groupby("region")
    reg["TAP_next"] = gg.TAP_T.shift(-1)
    reg["dTAP"] = reg.TAP_T - gg.TAP_T.shift()
    reg["dlog_ecoles_lag"] = reg.dlog_ecoles
    reg["dlog_eleves_lag"] = reg.dlog_eleves
    feats = ["dlog_ecoles_lag", "dlog_eleves_lag", "dTAP"]
    m = reg.dropna(subset=feats + ["TAP_next"]).copy()
    m["y"] = m.TAP_next - m.TAP_T
    rows = []
    test_years = sorted(m.annee.unique())[2:]
    for ty in test_years:
        tr, te = m[m.annee < ty], m[m.annee == ty]
        X = np.c_[np.ones(len(tr)), tr[feats].values]
        coef, *_ = np.linalg.lstsq(X, tr.y.values, rcond=None)
        pred = np.c_[np.ones(len(te)), te[feats].values] @ coef
        drift = tr.y.mean()
        rows.append({"annee_predite": SHORT[YEARS[YEARS.index(ty) + 1]], "n_train": len(tr),
                     "erreur_persistance": np.abs(te.y).mean(),
                     "erreur_tendance_moyenne": np.abs(te.y - drift).mean(),
                     "erreur_regression": np.abs(te.y - pred).mean()})
    pv = pd.DataFrame(rows)
    pv.loc["moyenne"] = ["toutes", np.nan] + list(pv.iloc[:, 2:].mean())
    pv.round(2).to_csv(chemins.path("P6_prevision.csv"), index=False)
    print(pv.round(2).to_string(index=False))
    allX = np.c_[np.ones(len(m)), m[feats].values]
    coef_all, *_ = np.linalg.lstsq(allX, m.y.values, rcond=None)
    print("Coefficients sur toutes les années (variation du TAP l'année suivante, en points) :",
          dict(zip(["constante"] + feats, np.round(coef_all, 2))))
    r = np.corrcoef(m.dlog_ecoles_lag, m.y)[0, 1]
    print(f"Corrélation entre la variation des écoles une année et la variation du TAP l'année suivante : r = {r:.2f} (n = {len(m)})")

    print("\n=== P7. Scénarios de réouverture (élasticité élèves / écoles estimée sur les 13 régions) ===")
    z2 = reg.dropna(subset=["dlog_eleves", "dlog_ecoles"])
    slope = np.polyfit(z2.dlog_ecoles, z2.dlog_eleves, 1)[0]
    last = reg[reg.annee == "2024-2025"].set_index("region")
    ref = reg[reg.annee == "2021-2022"].set_index("region")
    mx = reg.groupby("region").ecoles.max()
    sc = pd.DataFrame({"ecoles_max": mx, "ecoles_21_22": ref.ecoles, "ecoles_24_25": last.ecoles,
                       "eleves_24_25": last.eleves_T})
    sc["A_ecoles_a_rouvrir"] = (sc.ecoles_21_22 - sc.ecoles_24_25).clip(lower=0)
    sc["A_eleves_en_plus"] = (sc.eleves_24_25 * ((sc.ecoles_24_25 + sc.A_ecoles_a_rouvrir) / sc.ecoles_24_25) ** slope
                              - sc.eleves_24_25).round()
    sc["B_ecoles_a_rouvrir"] = (sc.ecoles_max - sc.ecoles_24_25).clip(lower=0)
    sc["B_eleves_en_plus"] = (sc.eleves_24_25 * (sc.ecoles_max / sc.ecoles_24_25) ** slope - sc.eleves_24_25).round()
    sc = sc[sc.B_ecoles_a_rouvrir > 0].sort_values("B_ecoles_a_rouvrir", ascending=False)
    sc.to_csv(chemins.path("P7_scenarios_reouverture.csv"))
    print(f"élasticité = {slope:.2f}")
    print(sc.to_string())
    print(f"Scénario A (niveau 21/22) : {int(sc.A_ecoles_a_rouvrir.sum())} écoles, {int(sc.A_eleves_en_plus.sum())} élèves")
    print(f"Scénario B (niveau maximal) : {int(sc.B_ecoles_a_rouvrir.sum())} écoles, {int(sc.B_eleves_en_plus.sum())} élèves")


if __name__ == "__main__":
    main()

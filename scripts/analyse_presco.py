"""First descriptive analysis of the challenge data for Défi 1 (school dropout)."""
import sys

import numpy as np
import pandas as pd

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]
SHORT = {y: y[2:4] + "/" + y[7:] for y in YEARS}


def get(d, table, sex="T", status="Total", **f):
    x = d[(d.table == table) & (d.sexe == sex) & (d.statut == status)]
    for k, v in f.items():
        x = x[x[k] == v]
    return x


def wide(x, index="region"):
    return x.pivot_table(index=index, columns="annee", values="valeur")[YEARS]


def main():
    d = pd.read_csv(sys.argv[1])
    out = sys.argv[2].rstrip("/")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)

    nat = pd.DataFrame({
        "eleves_primaire": wide(get(d, "E1", region="NATIONAL")).iloc[0],
        "ecoles_primaires": wide(get(d, "E13", region="NATIONAL")).iloc[0],
        "nouveaux_CP1": wide(get(d, "E5", region="NATIONAL")).iloc[0],
        "TBS_%": wide(get(d, "E7", region="NATIONAL")).iloc[0],
        "TAP_%": wide(get(d, "E8", region="NATIONAL")).iloc[0],
        "TAP_garcons_%": wide(get(d, "E8", sex="G", region="NATIONAL")).iloc[0],
        "TAP_filles_%": wide(get(d, "E8", sex="F", region="NATIONAL")).iloc[0],
        "reussite_CEP_%": wide(get(d, "E9", region="NATIONAL")).iloc[0],
    })
    nat.index = [SHORT[y] for y in nat.index]
    nat.to_csv(f"{out}/A_tendances_nationales.csv")
    print("\n=== A. Tendances nationales (primaire) ===")
    print(nat.round(1).to_string())

    pupils = wide(get(d, "E1")).drop("NATIONAL")
    sch = wide(get(d, "E13")).drop("NATIONAL")
    tap = wide(get(d, "E8")).drop("NATIONAL")
    drawdown = (pupils / pupils.cummax(axis=1) - 1).min(axis=1)
    reg = pd.DataFrame({
        "eleves_max": pupils.max(axis=1).astype(int),
        "annee_max": pupils.idxmax(axis=1).map(SHORT),
        "eleves_2024_25": pupils["2024-2025"].astype(int),
    })
    reg["pire_chute_%"] = (drawdown * 100).round(1)
    reg["annee_pire_chute"] = (pupils / pupils.cummax(axis=1) - 1).idxmin(axis=1).map(SHORT)
    reg["2024_25_vs_max_%"] = ((reg.eleves_2024_25 / reg.eleves_max - 1) * 100).round(1)
    reg["ecoles_max"] = sch.max(axis=1).astype(int)
    reg["ecoles_2024_25"] = sch["2024-2025"].astype(int)
    reg["ecoles_vs_max_%"] = ((reg.ecoles_2024_25 / reg.ecoles_max - 1) * 100).round(1)
    reg["TAP_15_16"] = tap["2015-2016"]
    reg["TAP_21_22"] = tap["2021-2022"]
    reg["TAP_24_25"] = tap["2024-2025"]
    reg["TAP_ecart_pts"] = (tap["2024-2025"] - tap["2015-2016"]).round(1)
    reg = reg.sort_values("TAP_ecart_pts")
    reg.to_csv(f"{out}/B_choc_et_reprise_par_region.csv")
    print("\n=== B. Choc et reprise par région (primaire) ===")
    print(reg.to_string())

    ni = wide(get(d, "E5")).drop("NATIONAL")
    nat_e = wide(get(d, "E1", region="NATIONAL")).iloc[0]
    nat_ni = wide(get(d, "E5", region="NATIONAL")).iloc[0]
    ex = pd.DataFrame(index=pupils.index)
    for t0, t1 in zip(YEARS[:-1], YEARS[1:]):
        ex[SHORT[t0] + "→" + SHORT[t1]] = ((1 - (pupils[t1] - ni[t1]) / pupils[t0]) * 100).round(1)
    ex.loc["NATIONAL"] = [round((1 - (nat_e[t1] - nat_ni[t1]) / nat_e[t0]) * 100, 1) for t0, t1 in zip(YEARS[:-1], YEARS[1:])]
    ex.to_csv(f"{out}/C_sorties_apparentes_par_region.csv")
    print("\n=== C. Sorties apparentes (% des élèves d'une année absents l'année suivante, hors nouveaux CP1) ===")
    print("    inclut les fins de CM2 normales, les abandons et les départs nets vers d'autres régions")
    print(ex.to_string())

    e4 = d[(d.table == "E4") & d.statut.isin(["Public", "Prive"]) & (d.niveau != "Total")]
    g = e4.groupby(["sexe", "niveau", "annee"]).valeur.sum().unstack("annee")[YEARS]
    grades = ["CP1", "CP2", "CE1", "CE2", "CM1", "CM2"]
    rows = []
    for sx in ["G", "F", "T"]:
        for a, b in zip(grades[:-1], grades[1:]):
            r = [g.loc[(sx, b), t1] / g.loc[(sx, a), t0] for t0, t1 in zip(YEARS[:-1], YEARS[1:])]
            rows.append([sx, f"{a}→{b}"] + [round(v * 100, 1) for v in r])
    flows = pd.DataFrame(rows, columns=["sexe", "passage"] + [SHORT[t1] for t1 in YEARS[1:]])
    flows.to_csv(f"{out}/D_passages_apparents_par_niveau.csv", index=False)
    print("\n=== D. Passages apparents d'un niveau au suivant, national (effectif niveau+1 l'année t+1 / effectif niveau l'année t, en %) ===")
    print(flows[flows.sexe == "T"].to_string(index=False))
    surv = []
    for k in range(5):
        t0, t5 = YEARS[k], YEARS[k + 5]
        surv.append({"cohorte_CP1": SHORT[t0], "CM2_en": SHORT[t5],
                     **{f"survie_apparente_{sx}_%": round(g.loc[(sx, "CM2"), t5] / g.loc[(sx, "CP1"), t0] * 100, 1)
                        for sx in ["G", "F", "T"]}})
    surv = pd.DataFrame(surv)
    surv.to_csv(f"{out}/D_survie_apparente_CP1_CM2.csv", index=False)
    print("\nSurvie apparente CP1 -> CM2 cinq ans plus tard (effectif CM2 / effectif CP1) :")
    print(surv.to_string(index=False))

    ips = wide(get(d, "E12")).round(2)
    ips.columns = [SHORT[c] for c in ips.columns]
    tapg = wide(get(d, "E8", sex="G"))["2024-2025"]
    tapf = wide(get(d, "E8", sex="F"))["2024-2025"]
    gender = pd.DataFrame({"TAP_garcons_24_25": tapg, "TAP_filles_24_25": tapf,
                           "IPS_TAP_15_16": ips["15/16"], "IPS_TAP_24_25": ips["24/25"]}).sort_values("IPS_TAP_24_25")
    gender.to_csv(f"{out}/E_parite_achevement.csv")
    print("\n=== E. Parité filles/garçons de l'achèvement (IPS du TAP : >1 = filles devant) ===")
    print(gender.to_string())

    dl_e = np.log(pupils[YEARS[1:]].values / pupils[YEARS[:-1]].values).ravel()
    dl_s = np.log(sch[YEARS[1:]].values / sch[YEARS[:-1]].values).ravel()
    slope, intercept = np.polyfit(dl_s, dl_e, 1)
    r2 = np.corrcoef(dl_s, dl_e)[0, 1] ** 2
    print("\n=== F. Écoles en moins et élèves en moins (variations annuelles, 13 régions x 9 années) ===")
    print(f"pente = {slope:.2f} (1 % d'écoles en moins va avec {slope:.2f} % d'élèves en moins), R² = {r2:.2f}, n = {len(dl_e)}")

    err = []
    for t0, t1 in zip(YEARS[:-1], YEARS[1:]):
        e_ = (tap[t1] - tap[t0]).abs()
        err.append({"annee_predite": SHORT[t1], "erreur_moyenne_pts": round(e_.mean(), 2), "erreur_max_pts": round(e_.max(), 1),
                    "region_erreur_max": e_.idxmax()})
    err = pd.DataFrame(err)
    err.to_csv(f"{out}/G_persistance_TAP.csv", index=False)
    print("\n=== G. Règle « comme l'an passé » appliquée au TAP régional : erreur absolue (points) ===")
    print(err.to_string(index=False))
    print(f"erreur moyenne sur toutes les années : {err.erreur_moyenne_pts.mean():.2f} points")


if __name__ == "__main__":
    main()

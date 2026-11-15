"""Two forecasting approaches not tried before, tested on years the models never saw."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import numpy as np
import pandas as pd

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]
SHORT = {y: y[2:4] + "/" + y[7:] for y in YEARS}


def main():
    pd.set_option("display.width", 200)
    p = pd.read_csv(chemins.path("panel_region_annee.csv"))
    reg = p[p.region != "NATIONAL"].sort_values(["region", "annee"]).copy()
    g = reg.groupby("region")
    reg["dTAP"] = reg.TAP_T - g.TAP_T.shift()
    d = reg.dropna(subset=["dlog_eleves", "dlog_ecoles", "dTAP"])

    print("=== A. Prévoir l'année en cours dès qu'on connaît les écoles ouvertes à la rentrée ===")
    rows = []
    for ty in sorted(d.annee.unique())[2:]:
        tr, te = d[d.annee < ty], d[d.annee == ty]
        b1, b0 = np.polyfit(tr.dlog_ecoles, tr.dlog_eleves, 1)
        c1, c0 = np.polyfit(tr.dlog_ecoles, tr.dTAP, 1)
        rows.append({
            "annee": SHORT[ty],
            "effectifs_persistance_%": np.abs(te.dlog_eleves).mean() * 100,
            "effectifs_ecoles_%": np.abs(te.dlog_eleves - (b0 + b1 * te.dlog_ecoles)).mean() * 100,
            "TAP_persistance_pts": np.abs(te.dTAP).mean(),
            "TAP_ecoles_pts": np.abs(te.dTAP - (c0 + c1 * te.dlog_ecoles)).mean(),
        })
    a = pd.DataFrame(rows)
    a.loc[len(a)] = ["moyenne"] + list(a.iloc[:, 1:].mean())
    print(a.round(2).to_string(index=False))
    m = a.iloc[-1]
    print(f"Effectifs : erreur {m['effectifs_ecoles_%']:.1f} % contre {m['effectifs_persistance_%']:.1f} % "
          f"(gain {(1 - m['effectifs_ecoles_%'] / m['effectifs_persistance_%']) * 100:.0f} %) ; "
          f"TAP : {m['TAP_ecoles_pts']:.2f} contre {m['TAP_persistance_pts']:.2f} points "
          f"(gain {(1 - m['TAP_ecoles_pts'] / m['TAP_persistance_pts']) * 100:.0f} %)")

    print("\n=== B. Filière des cohortes (national) : le CM2 de demain est dans le CM1 d'aujourd'hui ===")
    t = pd.read_csv(chemins.path("presco_tidy.csv"))
    e4 = t[(t.table == "E4") & t.statut.isin(["Public", "Prive"]) & (t.sexe == "T")]
    gr = e4.groupby(["niveau", "annee"]).valeur.sum().unstack("annee")[YEARS]
    nat = p[p.region == "NATIONAL"].set_index("annee").loc[YEARS]
    rows = []
    for i in range(2, 10):
        y0, y1, ym = YEARS[i - 1], YEARS[i], YEARS[i - 2]
        rate = gr.loc["CM2", y0] / gr.loc["CM1", ym]
        cm2_hat = gr.loc["CM1", y0] * rate
        tap_hat = nat.TAP_T[y0] * cm2_hat / gr.loc["CM2", y0]
        rows.append({"annee": SHORT[y1], "CM2_reel": gr.loc["CM2", y1], "CM2_filiere": round(cm2_hat),
                     "err_CM2_filiere_%": abs(cm2_hat / gr.loc["CM2", y1] - 1) * 100,
                     "err_CM2_persistance_%": abs(gr.loc["CM2", y0] / gr.loc["CM2", y1] - 1) * 100,
                     "TAP_reel": nat.TAP_T[y1], "TAP_filiere": tap_hat,
                     "err_TAP_filiere": abs(tap_hat - nat.TAP_T[y1]), "err_TAP_persistance": abs(nat.TAP_T[y0] - nat.TAP_T[y1])})
    b = pd.DataFrame(rows)
    print(b.round(1).to_string(index=False))
    print("Moyennes :", b[["err_CM2_filiere_%", "err_CM2_persistance_%", "err_TAP_filiere", "err_TAP_persistance"]]
          .mean().round(2).to_dict())
    rows = []
    for i in range(3, 10):
        y0, y2 = YEARS[i - 2], YEARS[i]
        r1 = gr.loc["CM1", y0] / gr.loc["CE2", YEARS[i - 3]]
        r2 = gr.loc["CM2", y0] / gr.loc["CM1", YEARS[i - 3]]
        cm2_hat = gr.loc["CE2", y0] * r1 * r2
        rows.append({"annee": SHORT[y2], "err_filiere_2ans_%": abs(cm2_hat / gr.loc["CM2", y2] - 1) * 100,
                     "err_persistance_2ans_%": abs(gr.loc["CM2", y0] / gr.loc["CM2", y2] - 1) * 100})
    c = pd.DataFrame(rows)
    print("\nDeux ans à l'avance (CM2), erreur moyenne :", c.iloc[:, 1:].mean().round(1).to_dict())
    rate = gr.loc["CM2", "2024-2025"] / gr.loc["CM1", "2023-2024"]
    r1 = gr.loc["CM1", "2024-2025"] / gr.loc["CE2", "2023-2024"]
    print(f"\nProjection : CM2 2025/26 ≈ {gr.loc['CM1', '2024-2025'] * rate:,.0f} (CM1 2024/25 = "
          f"{gr.loc['CM1', '2024-2025']:,.0f}, passage {rate:.1%}) ; CM2 2024/25 = {gr.loc['CM2', '2024-2025']:,.0f}")
    print(f"             CM2 2026/27 ≈ {gr.loc['CE2', '2024-2025'] * r1 * rate:,.0f} (à partir du CE2 2024/25)")
    print("Entrées en CP1 :", {SHORT[y]: int(gr.loc['CP1', y]) for y in YEARS[-4:]})
    a.round(2).to_csv(chemins.path("P12_nowcast_ecoles.csv"), index=False)
    b.round(2).to_csv(chemins.path("P12_filiere_un_an.csv"), index=False)
    robustness(gr, nat)


def robustness(gr, nat):
    print("\n=== C. Solidité de la projection du CM2, et ce qu'annoncent les grandes cohortes de CP1 ===")
    transition = pd.Series({YEARS[i]: gr.loc["CM2", YEARS[i]] / gr.loc["CM1", YEARS[i - 1]] for i in range(1, 10)})
    print("Passage du CM1 au CM2 :", {SHORT[y]: f"{v:.1%}" for y, v in transition.items()})
    rows = []
    for i in range(3, 10):
        y0, y1 = YEARS[i - 1], YEARS[i]
        known = transition.loc[:y0]
        lo, hi = gr.loc["CM1", y0] * known.min(), gr.loc["CM1", y0] * known.max()
        mid = gr.loc["CM1", y0] * known.iloc[-1]
        real = gr.loc["CM2", y1]
        rows.append({"annee": SHORT[y1], "bas": round(lo), "central": round(mid), "haut": round(hi), "reel": real,
                     "dans_fourchette": lo <= real <= hi,
                     "sens_annonce": "hausse" if mid > gr.loc["CM2", y0] else "baisse",
                     "sens_reel": "hausse" if real > gr.loc["CM2", y0] else "baisse"})
    r = pd.DataFrame(rows)
    print(r.to_string(index=False))
    print(f"Fourchette tenue {r.dans_fourchette.sum()} fois sur {len(r)} ; sens juste {(r.sens_annonce == r.sens_reel).sum()} "
          f"fois sur {len(r)}")
    cm1 = gr.loc["CM1", "2024-2025"]
    proj = {"bas": cm1 * transition.min(), "central": cm1 * transition.iloc[-1], "haut": cm1 * transition.max()}
    print(f"CM2 2025/26 : {proj['central']:,.0f} [{proj['bas']:,.0f} ; {proj['haut']:,.0f}] contre "
          f"{gr.loc['CM2', '2024-2025']:,.0f} en 2024/25 ; même le pire passage observé ({transition.min():.1%}, année du choc) "
          f"donne {proj['bas'] / gr.loc['CM2', '2024-2025'] - 1:+.1%}")
    den = gr.loc["CM2"] / (nat.TAP_T / 100)
    print("Variation du dénominateur implicite du TAP (CM2 / TAP) :",
          {SHORT[y]: f"{v:+.1%}" for y, v in (den / den.shift() - 1).dropna().items()})
    surv = pd.Series({YEARS[i]: gr.loc["CM2", YEARS[i]] / gr.loc["CP1", YEARS[i - 5]] for i in range(5, 10)})
    print("Survie apparente CP1 -> CM2 (5 ans plus tard) :", {SHORT[y]: f"{v:.1%}" for y, v in surv.items()})
    print("National, taux brut d'admission :", {SHORT[y]: round(v) for y, v in nat.TBA_T.items()})
    long_rows = []
    for y in ["2022-2023", "2023-2024", "2024-2025"]:
        arrival = f"{int(y[:4]) + 5}-{int(y[:4]) + 6}"
        cp1 = gr.loc["CP1", y]
        long_rows.append({"cohorte_CP1": SHORT[y], "en_CM2": arrival[2:4] + "/" + arrival[7:], "CP1": int(cp1),
                          "CM2_survie_recente": round(cp1 * surv.iloc[-1]), "CM2_survie_max": round(cp1 * surv.max())})
    lr = pd.DataFrame(long_rows)
    print("Scénario, pas une prévision (survie récente / meilleure survie observée) :")
    print(lr.to_string(index=False))
    out = pd.DataFrame({"annee": [SHORT[y] for y in YEARS], "CM2": gr.loc["CM2"].values, "CP1": gr.loc["CP1"].values})
    out.to_csv(chemins.path("P12_cohortes_national.csv"), index=False)
    pd.DataFrame([{"annee": "25/26", **{k: round(v) for k, v in proj.items()}}]).to_csv(
        chemins.path("P12_projection_CM2.csv"), index=False)
    r.to_csv(chemins.path("P12_filiere_fourchette.csv"), index=False)
    lr.to_csv(chemins.path("P12_scenario_cohortes_CP1.csv"), index=False)


if __name__ == "__main__":
    main()

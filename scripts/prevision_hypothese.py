"""Finish the analysis on the data we have: cautious forecast, escalation alert, hypothesis test.

A. Forecast of the completion rate (TAP) for 2025-26: "same as last year", with an
   80 % band taken from past one-year changes; the band's coverage is checked on
   years it was not built on.
B. Escalation alert from ACLED: incidents of the school year before the census at
   least 1.5 times those of the year before, and at least 30. Thresholds set before
   looking at the outcome; their past record is reported as it is.
C. Hypothesis "insecurity x poverty": does violence hurt completion more where
   poverty is high? Additive vs interaction model, coefficient with a bootstrap by
   region, and out-of-sample errors.
D. Attacks on education (Insecurity Insight): do they announce school closures
   better than all violence?

Usage: python prevision_hypothese.py   (run from the project root)
"""
import unicodedata

import numpy as np
import pandas as pd

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]
SHORT = {y: y[2:4] + "/" + y[7:] for y in YEARS + ["2025-2026", "2026-2027"]}
EN = {"Central-East": "Centre-Est", "Central-North": "Centre-Nord", "Central-South": "Centre-Sud",
      "Central-West": "Centre-Ouest", "East": "Est", "North": "Nord", "Upper-Basins": "Hauts-Bassins",
      "Waterfalls": "Cascades", "Central-Plateau": "Plateau-Central", "South-West": "Sud-Ouest"}
RNG = np.random.default_rng(2026)


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


def school_year(dt):
    start = dt.year if dt.month >= 10 else dt.year - 1
    return f"{start}-{start + 1}"


def main():
    pd.set_option("display.width", 220)
    panel = pd.read_csv("analyse/panel_region_annee.csv")
    p = panel[panel.region != "NATIONAL"].copy()
    p["cle"] = p.region.map(key)
    names2025 = pd.read_csv("analyse/panel_region_annee_2025.csv").drop_duplicates("region").set_index("region").region_2025
    acled = pd.read_csv("analyse/acled_region_annee.csv")
    pov = pd.read_csv("data/externe_propre/pauvrete_ehcvm_2021_regions.csv")
    pov["cle"] = pov.region.map(key)
    p = p.merge(acled, on=["cle", "annee"], how="left").merge(
        pov[["cle", "incidence_pauvrete_2021_pct"]], on="cle", how="left").sort_values(["region", "annee"])
    assert p.incidents.notna().all() and p.incidence_pauvrete_2021_pct.notna().all()
    g = p.groupby("region")
    p["dTAP_next"] = g.TAP_T.shift(-1) - p.TAP_T
    p["dlog_eleves_next"] = np.log(g.eleves_T.shift(-1) / p.eleves_T)
    p["dlog_ecoles_next"] = np.log(g.ecoles.shift(-1) / p.ecoles)
    p["l_inc"] = np.log1p(p.incidents)

    # ---------------- A. Cautious forecast with an 80 % band ----------------
    print("=== A. Prévision du TAP 2025/26 : « comme l'an passé » avec fourchette à 80 % ===")
    ch = p.dropna(subset=["dTAP_next"])
    cover = []
    for ty in YEARS[3:-1]:  # band built only on changes observed before the predicted year
        past = ch[ch.annee < ty].dTAP_next
        lo, hi = past.quantile(0.10), past.quantile(0.90)
        test = ch[ch.annee == ty]
        inside = ((test.dTAP_next >= lo) & (test.dTAP_next <= hi)).mean()
        cover.append({"annee_predite": SHORT[YEARS[YEARS.index(ty) + 1]], "n_passe": len(past),
                      "bas": round(lo, 1), "haut": round(hi, 1), "couverture_%": round(inside * 100)})
    cover = pd.DataFrame(cover)
    print(cover.to_string(index=False))
    print(f"Couverture moyenne : {cover['couverture_%'].mean():.0f} % (attendu : 80 %)")
    lo, hi = ch.dTAP_next.quantile(0.10), ch.dTAP_next.quantile(0.90)
    pop = pd.read_csv("data/raw/externe/hdx_cod_ps/bfa_admpop_adm2_2024.csv", encoding="utf-8-sig")
    pop["cle"] = pop.ADM1_FR.map(key)
    pop11 = (pop.groupby("cle").T_10_14.sum() / 5).rename("enfants_11_ans_approx")  # one fifth of the 10-14 group
    last = p[p.annee == "2024-2025"].set_index("cle")
    fc = pd.DataFrame({
        "region": last.region, "region_2025": last.region.map(names2025),
        "TAP_24_25": last.TAP_T, "prevision_25_26": last.TAP_T,
        "fourchette_basse": (last.TAP_T + lo).clip(lower=0), "fourchette_haute": last.TAP_T + hi,
    }).join(pop11)
    fc["enfants_hors_CM2_estimes"] = ((1 - fc.TAP_24_25 / 100).clip(lower=0) * fc.enfants_11_ans_approx).round(-2)
    print(f"Fourchette appliquée : {lo:+.1f} à {hi:+.1f} points autour du TAP 2024/25")

    # ---------------- B. Escalation alert ----------------
    print("\n=== B. Alerte d'escalade (incidents ≥ 1,5 × l'année d'avant, et ≥ 30) ===")
    p["inc_prev"] = g.incidents.shift()
    p["alerte"] = (p.incidents >= 1.5 * p.inc_prev) & (p.incidents >= 30)
    hist = p.dropna(subset=["dlog_eleves_next", "inc_prev"])
    drop = hist.dlog_eleves_next < np.log(0.95)
    a, n = hist.alerte, len(hist)
    print(f"Historique ({n} régions-années) : {int(a.sum())} alertes ; "
          f"baisse d'effectifs de plus de 5 % l'année suivante dans {int((a & drop).sum())} cas sur {int(a.sum())} "
          f"({(a & drop).sum() / max(a.sum(), 1) * 100:.0f} %), contre {(~a & drop).sum() / (~a).sum() * 100:.0f} % sans alerte.")
    print(f"Baisses de plus de 5 % précédées d'une alerte : {int((a & drop).sum())} sur {int(drop.sum())}")
    print(hist[a][["region", "annee", "inc_prev", "incidents", "dlog_eleves_next"]].assign(
        variation_eleves_pct=lambda x: ((np.exp(x.dlog_eleves_next) - 1) * 100).round(1)).drop(
        columns="dlog_eleves_next").to_string(index=False))
    full = acled.copy()
    full = full.sort_values(["cle", "annee"])
    full["inc_prev"] = full.groupby("cle").incidents.shift()
    full["alerte"] = (full.incidents >= 1.5 * full.inc_prev) & (full.incidents >= 30)
    for yr, label in [("2024-2025", "rentrée 2025/26"), ("2025-2026", "rentrée 2026/27")]:
        cur = full[full.annee == yr].set_index("cle")
        col = f"incidents_{SHORT[yr].replace('/', '_')}"
        fc[col] = cur.incidents
        fc[f"alerte_{label.split()[1].replace('/', '_')}"] = cur.alerte
    fc["profil"] = None
    typo = pd.read_csv("analyse/P2_typologie_regions.csv")
    typo["cle"] = typo.region.map(key)
    prof = {1: "Choc puis reprise partielle", 2: "Effondrement", 3: "Érosion", 4: "Stabilité / accueil"}
    fc["profil"] = typo.set_index("cle").groupe_k4.map(prof)
    fc = fc.sort_values("TAP_24_25")
    fc.round(1).to_csv("analyse/P9_prevision_2025_26_alerte.csv")
    print("\n--- Tableau de prévision et d'alerte ---")
    print(fc.drop(columns=["region", "enfants_11_ans_approx"]).round(1).to_string())

    # ---------------- C. Hypothesis: insecurity x poverty ----------------
    print("\n=== C. Hypothèse : l'insécurité pèse-t-elle plus là où la pauvreté est forte ? ===")
    m = p.dropna(subset=["dTAP_next"]).copy()
    m["pauv"] = (m.incidence_pauvrete_2021_pct - m.incidence_pauvrete_2021_pct.mean()) / 10  # per 10 points
    m["inc_c"] = m.l_inc - m.l_inc.mean()
    m["inter"] = m.inc_c * m.pauv

    def fit(df, cols):
        X = np.c_[np.ones(len(df)), df[cols].values]
        return np.linalg.lstsq(X, df.dTAP_next.values, rcond=None)[0]

    add, inter = ["inc_c", "pauv"], ["inc_c", "pauv", "inter"]
    b_add, b_int = fit(m, add), fit(m, inter)
    regions = m.region.unique()
    boots = []
    for _ in range(2000):  # resample whole regions: years of one region are not independent
        pick = RNG.choice(regions, size=len(regions), replace=True)
        bs = pd.concat([m[m.region == r] for r in pick])
        boots.append(fit(bs, inter))
    boots = np.array(boots)
    names = ["constante", "insécurité (log incidents, centré)", "pauvreté (par 10 points)", "insécurité × pauvreté"]
    print("Modèle avec interaction, variation du TAP l'année suivante (points) :")
    for i, nme in enumerate(names):
        lo_b, hi_b = np.percentile(boots[:, i], [2.5, 97.5])
        print(f"  {nme:38s} {b_int[i]:+6.2f}   IC 95 % [{lo_b:+.2f} ; {hi_b:+.2f}]")
    rows = []
    for ty in sorted(m.annee.unique())[3:]:
        tr, te = m[m.annee < ty], m[m.annee == ty]
        for name_, cols in [("additif", add), ("interaction", inter)]:
            b = fit(tr, cols)
            pred = np.c_[np.ones(len(te)), te[cols].values] @ b
            rows.append({"modele": name_, "annee": ty, "erreur": np.abs(te.dTAP_next - pred).mean()})
        rows.append({"modele": "comme l'an passé", "annee": ty, "erreur": np.abs(te.dTAP_next).mean()})
    oos = pd.DataFrame(rows).groupby("modele").erreur.mean().round(2)
    print("Erreur moyenne sur années non vues (points) :", oos.to_dict())
    # Cross-section 2021-22 -> 2024-25: the shock period, poverty measured just before it
    cs = p[p.annee.isin(["2021-2022", "2024-2025"])].pivot_table(index="region", columns="annee", values="TAP_T")
    cs["variation_TAP"] = cs["2024-2025"] - cs["2021-2022"]
    inc = p[p.annee.isin(["2021-2022", "2022-2023", "2023-2024"])].groupby("region").incidents.sum()
    cs = cs.join(inc.rename("incidents_21_24")).join(pov.set_index("region").incidence_pauvrete_2021_pct.rename("pauvrete_2021"))
    cs = cs.sort_values("variation_TAP")
    cs.round(1).to_csv("analyse/P10_hypothese_transversale.csv")
    print("\nVue transversale 2021/22 → 2024/25 :")
    print(cs.round(1).to_string())
    print(f"r(variation TAP, pauvreté) = {np.corrcoef(cs.variation_TAP, cs.pauvrete_2021)[0, 1]:+.2f} ; "
          f"r(variation TAP, log incidents) = {np.corrcoef(cs.variation_TAP, np.log1p(cs.incidents_21_24))[0, 1]:+.2f} (n = 13)")

    # ---------------- D. Attacks on education vs all violence ----------------
    print("\n=== D. Attaques contre l'éducation (Insecurity Insight) ===")
    e = pd.read_excel("data/raw/externe/hdx_insecurity_insight/education_in_danger_2017_2026.xlsx")
    print(f"{len(e)} incidents ; région non renseignée : {int(e['Admin 1'].isna().sum())}")
    e = e.dropna(subset=["Admin 1"])
    e["cle"] = e["Admin 1"].map(lambda x: key(EN.get(x, x)))
    e["annee"] = pd.to_datetime(e.Date).map(school_year)
    ea = e.groupby(["cle", "annee"]).size().rename("attaques_education")
    q = p.join(ea, on=["cle", "annee"])
    q["attaques_education"] = q.attaques_education.fillna(0)
    q = q[(q.annee >= "2016-2017")].dropna(subset=["dlog_ecoles_next"])
    for col in ["attaques_education", "incidents"]:
        r = np.corrcoef(np.log1p(q[col]), q.dlog_ecoles_next)[0, 1]
        print(f"  r(log {col} d'une année, variation des écoles l'année suivante) = {r:+.2f} (n = {len(q)})")


if __name__ == "__main__":
    main()

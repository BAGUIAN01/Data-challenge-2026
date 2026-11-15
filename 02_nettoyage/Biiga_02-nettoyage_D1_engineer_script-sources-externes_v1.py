"""Clean the public sources on non-security drivers of dropout, by former region (13)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import unicodedata

import pandas as pd

RAW = chemins.raw("externe/")


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


DHS_NAMES = {"Boucle de Mouhoun": "BOUCLEDUMOUHOUN", "Centre (including Ouagadougou)": "CENTRE",
             "Hauts Bassins": "HAUTSBASSINS"}


def food():
    df = pd.read_excel(RAW + "hdx_cadre_harmonise/cadre_harmonise_caf_ipc_mars26.xlsx")
    b = df[(df.adm0_name == "Burkina Faso") & (df.usethisperiod == "Y")].copy()
    b["cle"] = b.adm1_name.map(key)
    start = b.reference_year - (b.reference_label != "Sep-Dec").astype(int)
    b["annee"] = start.astype(str) + "-" + (start + 1).astype(str)
    per = b.groupby(["cle", "annee", "reference_label"])[["phase35", "population"]].sum().reset_index()
    per["pct"] = per.phase35 / per.population * 100
    out = per.groupby(["cle", "annee"]).agg(faim_phase3plus_pct=("pct", "mean"), periodes=("pct", "size"),
                                             population_ch=("population", "max")).reset_index()
    out = out[out.annee >= "2014-2015"]
    assert out.cle.nunique() == 13, sorted(out.cle.unique())
    out.round(2).to_csv(chemins.path("faim_cadre_harmonise_region_annee.csv"), index=False)
    with open(chemins.path("faim_cadre_harmonise_region_annee.SOURCE.txt"), "w") as f:
        f.write("# Source : Cadre Harmonisé (CILSS / RPCA), consolidation HDX « cadre-harmonise », fichier "
                "cadre_harmonise_caf_ipc_mars26.xlsx, licence CC BY. Provinces sommées par ancienne région. "
                "Indicateur : part de la population en phase 3 ou plus, moyenne des périodes d'une année scolaire "
                "(sept.-déc. de t, janv.-mai et juin-août de t+1). Le Burkina n'apparaît plus après juin-août 2024 : "
                "dernière année scolaire couverte 2023-2024 (sans sept.-déc. 2024).\n")
    return out


def families():
    rows = []
    for f in ["select-education-indicators_subnational_bfa.csv", "mics-indicators_subnational_bfa.csv"]:
        d = pd.read_csv(RAW + "hdx_dhs/" + f)
        rows.append(d[d.SurveyYear.astype(str) == "2021"])
    d = pd.concat(rows)
    names = {"Women with no education": "meres_sans_instruction_pct",
             "Age specific fertility rate: 15-19": "fecondite_15_19_pour_mille",
             "Gender parity index for net primary school attendance": "ipp_frequentation_primaire"}
    d = d[d.Indicator.isin(names) & (d.CharacteristicLabel != "Ouagadougou")].drop_duplicates(
        ["Indicator", "CharacteristicLabel"])
    d["cle"] = d.CharacteristicLabel.map(lambda s: DHS_NAMES.get(s, key(s)))
    out = d.pivot_table(index="cle", columns="Indicator", values="Value").rename(columns=names).reset_index()
    assert len(out) == 13, out.cle.tolist()
    out.to_csv(chemins.path("eds_2021_regions.csv"), index=False)
    with open(chemins.path("eds_2021_regions.SOURCE.txt"), "w") as f:
        f.write("# Source : Enquête démographique et de santé 2021 (INSD / The DHS Program), indicateurs régionaux, "
                "HDX « dhs-subnational-data-for-burkina-faso ». « Centre » = ligne « Centre (including Ouagadougou) ». "
                "« meres_sans_instruction_pct » = femmes de 15-49 ans sans instruction. Limite : la collecte n'a pas "
                "couvert toutes les zones d'insécurité (Sahel, Est notamment).\n")
    return out


def displaced(food_df):
    x = pd.read_excel(RAW + "hdx_pdi_conasur/situation_pdi_31122022.xlsx", "STATISTIQUES")
    x = x.rename(columns={x.columns[0]: "region", x.columns[1]: "pdi"}).dropna(subset=["pdi"])
    x = x[pd.to_numeric(x.pdi, errors="coerce").notna() & (x.region != "BURKINA FASO")]
    x["cle"] = x.region.map(key)
    pop = food_df[food_df.annee == "2022-2023"].set_index("cle").population_ch
    x["pdi_pct_population"] = x.pdi.astype(float) / x.cle.map(pop) * 100
    assert len(x) == 13 and x.pdi_pct_population.notna().all()
    x[["cle", "pdi", "pdi_pct_population"]].round(2).to_csv(chemins.path("pdi_conasur_2022_regions.csv"), index=False)
    with open(chemins.path("pdi_conasur_2022_regions.SOURCE.txt"), "w") as f:
        f.write("# Source : CONASUR, enregistrement des personnes déplacées internes, situation au 31 décembre 2022, "
                "feuille STATISTIQUES (HDX « situation-des-personnes-deplacees-internes », licence CC BY). Déplacés "
                "comptés dans la région d'ACCUEIL. Dénominateur : population du Cadre Harmonisé 2022. Dernière série "
                "régionale publiée ; le gouvernement a cessé la publication en 2023.\n")
    return x


def main():
    f = food()
    print("Faim (phase 3+, %) :")
    print(f.pivot(index="cle", columns="annee", values="faim_phase3plus_pct").round(1).to_string())
    print(families().round(1).to_string(index=False))
    print(displaced(f).round(1).to_string(index=False))


if __name__ == "__main__":
    main()

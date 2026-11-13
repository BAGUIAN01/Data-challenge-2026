"""Build the region and province correspondence tables from the official boundaries.

Source: Institut Géographique du Burkina (IGB), administrative boundaries v03,
valid from 2025-08-01, published on HDX (dataset cod-ab-bfa). The file gives,
for each of the 17 regions and 47 provinces, its former code and name.

Usage: python referentiel_officiel.py data/raw/externe/hdx_cod_ab/bfa_admin_boundaries.xlsx data/ref/
"""
import sys
import unicodedata

import pandas as pd

SOURCE = "IGB, limites administratives v03 (valides au 2025-08-01), HDX cod-ab-bfa"


def key(name):
    """Accent- and case-insensitive key: 'Plateau-Central' == 'PLATEAU CENTRAL'."""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


def main():
    src, out = sys.argv[1], sys.argv[2].rstrip("/")
    a1 = pd.read_excel(src, sheet_name="bfa_admin1")
    a2 = pd.read_excel(src, sheet_name="bfa_admin2")

    reg = a1[["adm1_pcode_old", "adm1_name_old", "adm1_pcode", "adm1_name1"]].rename(columns={
        "adm1_pcode_old": "code_ancienne_region", "adm1_name_old": "ancienne_region",
        "adm1_pcode": "code_nouvelle_region", "adm1_name1": "nouvelle_region"})
    n_new = reg.groupby("code_ancienne_region").code_nouvelle_region.transform("nunique")
    reg["type"] = n_new.map(lambda n: "renommage" if n == 1 else f"scission en {n}")
    reg["cle_presco"] = reg.ancienne_region.map(key)
    reg["source"] = SOURCE
    reg = reg.sort_values(["ancienne_region", "nouvelle_region"])
    reg.to_csv(f"{out}/regions_13_17.csv", index=False)

    prov = a2[["adm2_pcode_old", "adm2_name_old", "adm2_pcode", "adm2_name1", "adm1_pcode", "adm1_name1"]].rename(columns={
        "adm2_pcode_old": "code_ancienne_province", "adm2_name_old": "ancienne_province",
        "adm2_pcode": "code_nouvelle_province", "adm2_name1": "nouvelle_province",
        "adm1_pcode": "code_nouvelle_region", "adm1_name1": "nouvelle_region"})
    prov = prov.merge(reg[["code_nouvelle_region", "code_ancienne_region", "ancienne_region"]],
                      on="code_nouvelle_region", how="left")
    prov["changement"] = [
        "inchangée" if o == n else ("scindée" if (prov.code_ancienne_province == co).sum() > 1 else "renommée")
        for o, n, co in zip(prov.ancienne_province, prov.nouvelle_province, prov.code_ancienne_province)]
    prov["source"] = SOURCE
    prov = prov.sort_values("code_nouvelle_province")
    prov.to_csv(f"{out}/provinces_45_47.csv", index=False)

    print(reg.drop(columns=["source", "cle_presco"]).to_string(index=False))
    print()
    print(prov[prov.changement != "inchangée"][["ancienne_province", "nouvelle_province", "nouvelle_region", "changement"]]
          .to_string(index=False))
    print(f"\n{len(reg)} régions, {len(prov)} provinces ({prov.code_ancienne_province.nunique()} anciennes)")


if __name__ == "__main__":
    main()

"""Add the 2025 region names to the challenge data (13 former regions -> 17 new ones)."""
import sys
import unicodedata

import pandas as pd


def key(name):
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.upper() if ch.isalnum())


def main():
    ref = pd.read_csv(sys.argv[1])
    groups = ref.groupby("cle_presco").agg(
        region_2025=("nouvelle_region", lambda n: " + ".join(sorted(n))),
        codes_2025=("code_nouvelle_region", lambda c: " + ".join(sorted(c))),
        type_2025=("type", "first"),
    )
    groups.loc["NATIONAL"] = ["Burkina Faso", "BF", "national"]
    d = pd.read_csv(sys.argv[2])
    k = d.region.map(lambda r: "NATIONAL" if r == "NATIONAL" else key(r))
    unknown = sorted(set(d.region[~k.isin(groups.index)]))
    if unknown:
        raise SystemExit(f"Régions absentes de la table de correspondance : {unknown}")
    d = d.assign(_cle=k).join(groups, on="_cle").drop(columns="_cle")
    pos = d.columns.get_loc("region") + 1
    for i, col in enumerate(["region_2025", "codes_2025", "type_2025"]):
        d.insert(pos + i, col, d.pop(col))
    d.to_csv(sys.argv[3], index=False)
    print(groups.to_string())
    print(f"\n{len(d)} lignes écrites dans {sys.argv[3]}")


if __name__ == "__main__":
    main()

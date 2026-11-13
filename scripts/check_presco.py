"""Consistency checks on the tidy challenge data. Prints a report in French.

Each check says what it compares, how many cases it tested and lists the
failures. A check that tested nothing says so: an empty check proves nothing.

Usage: python check_presco.py data/tidy/presco_tidy.csv
"""
import sys

import pandas as pd

COUNT_TABLES = ["P1", "P2", "P3", "P4", "P7", "P8", "E1", "E2", "E3", "E4", "E5", "E13"]
RATE_IPS = [("E6", "E10", "TBA"), ("E7", "E11", "TBS"), ("E8", "E12", "TAP"), ("P5", "P6", "TBS préscolaire")]


def section(title):
    print(f"\n=== {title} ===")


def report(name, tested, failures, show=8):
    status = "OK" if tested and failures.empty else ("RIEN TESTÉ" if not tested else f"{len(failures)} ÉCART(S)")
    print(f"- {name} : {tested} cas testés -> {status}")
    if tested and not failures.empty:
        print(failures.head(show).to_string(index=False))


def main():
    d = pd.read_csv(sys.argv[1])
    keys = ["table", "region", "statut", "milieu", "niveau", "annee"]

    section("1. Garçons + filles = total (tableaux d'effectifs)")
    c = d[d.table.isin(COUNT_TABLES)].pivot_table(index=keys, columns="sexe", values="valeur").dropna()
    if {"G", "F", "T"} <= set(c.columns):
        c = c.dropna(subset=["G", "F", "T"])
        # ⚠️ c.T is the transpose, not the "T" column: always c["T"].
        bad = c.loc[(c["G"] + c["F"] - c["T"]).abs() > 0.5].reset_index()
        bad["ecart"] = bad["G"] + bad["F"] - bad["T"]
        report("G + F = T", len(c), bad[keys + ["G", "F", "T", "ecart"]])

    section("2. Somme des régions = national")
    for t in ["P1", "P7", "P8", "E1", "E5", "E13"]:
        x = d[(d.table == t)]
        reg = x[x.region != "NATIONAL"].groupby(["statut", "sexe", "annee"]).valeur.sum()
        nat = x[x.region == "NATIONAL"].set_index(["statut", "sexe", "annee"]).valeur
        j = pd.concat([reg.rename("somme_regions"), nat.rename("national")], axis=1).dropna()
        j["ecart"] = j.somme_regions - j.national
        report(f"{t} ({x.indicateur.iloc[0]})", len(j), j[j.ecart.abs() > 0.5].reset_index())

    section("3. Le même total national dans les différents tableaux")
    def nat(t, **f):
        x = d[(d.table == t) & (d.sexe == "T")]
        for k, v in f.items():
            x = x[x[k] == v]
        return x.groupby("annee").valeur.sum()
    pairs = {
        "primaire : régions (E1) / statut (E2)": (nat("E1", region="NATIONAL"), nat("E2", statut="Total")),
        "primaire : régions (E1) / milieu (E3)": (nat("E1", region="NATIONAL"), nat("E3", milieu="Total")),
        "primaire : régions (E1) / niveaux (E4)": (nat("E1", region="NATIONAL"), nat("E4", statut="Total", niveau="Total")),
        "préscolaire : régions (P1) / statut (P2)": (nat("P1", region="NATIONAL"), nat("P2", statut="Total")),
        "préscolaire : régions (P1) / milieu (P3)": (nat("P1", region="NATIONAL"), nat("P3", milieu="Total")),
        "préscolaire : régions (P1) / niveaux (P4)": (nat("P1", region="NATIONAL"), nat("P4", statut="Total", niveau="Total")),
    }
    for name, (a, b) in pairs.items():
        j = pd.concat([a.rename("A"), b.rename("B")], axis=1).dropna()
        j["ecart"] = j.A - j.B
        report(name, len(j), j[j.ecart.abs() > 0.5].reset_index())

    section("4. Somme des statuts et des niveaux = total")
    for t, parts in [("E2", ["Public", "Prive"]), ("E13", ["Public", "Prive"]),
                     ("P2", ["Public", "Prive", "Communautaire"]), ("P7", ["Public", "Prive", "Communautaire"]),
                     ("P8", ["Public", "Prive", "Communautaire"])]:
        x = d[d.table == t]
        s = x[x.statut.isin(parts)].groupby(["region", "sexe", "annee"]).valeur.sum()
        tot = x[x.statut == "Total"].set_index(["region", "sexe", "annee"]).valeur
        j = pd.concat([s.rename("somme"), tot.rename("total")], axis=1).dropna()
        j["ecart"] = j.somme - j.total
        report(f"{t} : statuts", len(j), j[j.ecart.abs() > 0.5].reset_index())
    x = d[(d.table == "E4") & (d.statut.isin(["Public", "Prive"]))]
    s = x[x.niveau != "Total"].groupby(["statut", "sexe", "annee"]).valeur.sum()
    tot = x[x.niveau == "Total"].set_index(["statut", "sexe", "annee"]).valeur
    j = pd.concat([s.rename("somme"), tot.rename("total")], axis=1).dropna()
    j["ecart"] = j.somme - j.total
    report("E4 : CP1 + ... + CM2 = total", len(j), j[j.ecart.abs() > 0.5].reset_index())

    section("5. Indice de parité = taux filles / taux garçons")
    for rt, it, name in RATE_IPS:
        r = d[d.table == rt].pivot_table(index=["region", "annee"], columns="sexe", values="valeur")
        ips = d[d.table == it].set_index(["region", "annee"]).valeur.rename("IPS_publie")
        j = pd.concat([(r.F / r.G).rename("F_sur_G"), ips], axis=1).dropna()
        j["ecart"] = (j.F_sur_G - j.IPS_publie).round(3)
        report(f"{name} ({rt} / {it}), tolérance 0,02", len(j), j[j.ecart.abs() > 0.02].reset_index())

    section("6. Lignes recopiées d'une région à l'autre (mêmes valeurs G, F, T la même année)")
    tested, found = 0, []
    for (t, yr), x in d[d.region != "NATIONAL"].groupby(["table", "annee"]):
        g = x.groupby(["region", "statut", "niveau", "milieu"]).valeur.apply(lambda v: tuple(sorted(v.round(6))))
        tested += len(g)
        dup = g[g.duplicated(keep=False) & g.map(lambda v: any(abs(z) > 0 for z in v) and len(v) > 0)]
        for vec, grp in dup.groupby(dup):
            regs = sorted(set(i[0] for i in grp.index))
            if len(regs) > 1 and len(vec) >= 2:
                found.append({"table": t, "annee": yr, "regions": " = ".join(regs), "valeurs": vec[:3]})
    report("valeurs identiques entre régions", tested, pd.DataFrame(found))

    section("7. Sauts de plus de 40 % d'une année à l'autre (effectifs et écoles par région)")
    x = d[d.table.isin(["P1", "E1", "E5", "E13"]) & (d.sexe == "T") & (d.statut == "Total")].sort_values("annee")
    x = x.assign(prev=x.groupby(["table", "region"]).valeur.shift())
    x["variation_%"] = ((x.valeur / x.prev - 1) * 100).round(1)
    jumps = x[x["variation_%"].abs() > 40][["table", "indicateur", "region", "annee", "prev", "valeur", "variation_%"]]
    report("variations > 40 %", int(x.prev.notna().sum()), jumps, show=40)

    section("8. Taux hors de l'ordre de grandeur attendu")
    lim = {"TAP": 100, "TBS": 130, "TBA": 130, "reussite_CEP": 100}
    r = d[d.indicateur.isin(lim) & (d.cycle == "primaire")]
    over = r[r.apply(lambda z: z.valeur > lim[z.indicateur], axis=1)]
    report("TAP > 100, TBS ou TBA > 130, CEP > 100", len(r), over[["table", "indicateur", "region", "sexe", "annee", "valeur"]], show=20)


if __name__ == "__main__":
    main()

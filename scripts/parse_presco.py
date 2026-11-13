"""Turn the challenge's Presco.txt export into one tidy CSV.

Presco.txt is an Excel sheet saved as tab-separated text: 21 tables
(preschool 1-8, primary 1-13) separated by empty rows, some titles shifted
to column X, and stray "2017" cells. Each table is located by its line range
(checked by hand against the file) and read with one of three layouts:

  wide  - one row per label, values in G/F/T triplets per year
  long  - one row per label and sex (GARCONS/FILLES/TOTAL), one column per year
  plain - one row per label, one column per year, no sex

Output columns: table, cycle, indicateur, unite, region, statut, milieu,
niveau, sexe, annee, valeur.  Years are school years "2015-2016" ... "2024-2025".

Usage: python parse_presco.py data/raw/Presco.txt data/tidy/presco_tidy.csv
"""
import csv
import re
import sys

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]  # the 10 school years covered

# (id, cycle, indicateur, unite, first line, last line, layout, label columns) - lines are 1-based.
TABLES = [
    ("P1", "prescolaire", "effectifs", "eleves", 1, 17, "wide", ["region"]),
    ("P2", "prescolaire", "effectifs", "eleves", 19, 25, "wide", ["statut"]),
    ("P3", "prescolaire", "effectifs", "eleves", 27, 33, "wide", ["milieu"]),
    ("P4", "prescolaire", "effectifs", "eleves", 36, 52, "wide", ["statut", "niveau"]),
    ("P5", "prescolaire", "TBS", "%", 55, 72, "wide", ["region"]),
    ("P6", "prescolaire", "IPS_TBS", "ratio F/G", 75, 90, "plain", ["region"]),
    ("P7", "prescolaire", "structures", "structures", 93, 147, "plain", ["region", "statut"]),
    ("P8", "prescolaire", "salles", "salles", 150, 204, "plain", ["region", "statut"]),
    ("E1", "primaire", "effectifs", "eleves", 206, 250, "long", ["region"]),
    ("E2", "primaire", "effectifs", "eleves", 276, 286, "long", ["statut"]),
    ("E3", "primaire", "effectifs", "eleves", 349, 359, "long", ["milieu"]),
    ("E4", "primaire", "effectifs", "eleves", 447, 493, "long", ["statut", "niveau"]),
    ("E5", "primaire", "nouveaux_inscrits_CP1", "eleves", 562, 605, "long", ["region"]),
    ("E6", "primaire", "TBA", "%", 641, 657, "wide", ["region"]),
    ("E7", "primaire", "TBS", "%", 701, 717, "wide", ["region"]),
    ("E8", "primaire", "TAP", "%", 809, 825, "wide", ["region"]),
    ("E9", "primaire", "reussite_CEP", "%", 894, 937, "long", ["region"]),
    ("E10", "primaire", "IPS_TBA", "ratio F/G", 1061, 1076, "plain", ["region"]),
    ("E11", "primaire", "IPS_TBS", "ratio F/G", 1189, 1204, "plain", ["region"]),
    ("E12", "primaire", "IPS_TAP", "ratio F/G", 1314, 1329, "plain", ["region"]),
    ("E13", "primaire", "ecoles", "ecoles", 1417, 1460, "plain", ["region", "statut"]),
]

SEX = {"G": "G", "F": "F", "T": "T", "GARCONS": "G", "FILLES": "F", "TOTAL": "T",
       "GARÇONS": "G"}
NATIONAL = {"TOTAL GÉNÉRAL", "TOTAL GENERAL", "NATIONAL", "BURKINA FASO", "TOTAL"}
HEADERS = {"REGION", "RÉGION", "RÉGIONS", "REGIONS", "STATUT", "MILIEU"}


def number(cell):
    """'1 477 806' -> 1477806.0, '1,1760' -> 1.176; empty -> None. Raises on anything else."""
    c = cell.replace(" ", "").replace(" ", "").replace(",", ".").strip()
    if c == "":
        return None
    if not re.fullmatch(r"-?\d+(\.\d+)?", c):
        raise ValueError(f"not a number: {cell!r}")
    return float(c)


def is_number(cell):
    try:
        return number(cell) is not None
    except ValueError:
        return False


def norm_region(name):
    n = name.strip().upper()
    if n in NATIONAL:
        return "NATIONAL"
    return "HAUTS-BASSINS" if n == "HAUT-BASSINS" else n


def norm_label(kind, value):
    v = value.strip()
    if kind == "region":
        return norm_region(v)
    if kind == "statut":
        return {"PUBLIC": "Public", "PRIVÉ": "Prive", "PRIVE": "Prive", "COMMUNAUTAIRE": "Communautaire",
                "TOTAL": "Total"}.get(v.upper(), v)
    if kind == "milieu":
        return {"URBAIN": "Urbain", "RURAL": "Rural", "INDETERMINÉ": "Indetermine",
                "INDETERMINE": "Indetermine", "TOTAL GÉNÉRAL": "Total", "NATIONAL": "Total"}.get(v.upper(), v)
    return v


def labels_from_row(cells, kinds, carried):
    """Read the label columns, carrying forward blank ones (merged cells in Excel)."""
    out = {}
    for i, kind in enumerate(kinds):
        raw = cells[i].strip() if i < len(cells) else ""
        out[kind] = raw if raw else carried.get(kind, "")
    # "Total X" rows: a subtotal for X, or the grand total.
    first = kinds[0]
    raw0 = cells[0].strip() if cells else ""
    if raw0.upper().startswith("TOTAL ") and raw0.upper() not in NATIONAL:
        rest = raw0[6:]
        if first == "region":
            out["region"], out[kinds[1]] = rest, "Total"
        else:  # "Total Public" in a statut table
            out[first], out[kinds[1]] = rest, "Total"
    elif raw0.upper() in NATIONAL:
        out[first] = "NATIONAL" if first == "region" else "Total"
        for k in kinds[1:]:
            if not (cells[kinds.index(k)].strip() if kinds.index(k) < len(cells) else ""):
                out[k] = "Total"
    return out


def parse(path):
    text = open(path, encoding="utf-8", newline="").read()
    lines = text.split("\r\n")
    rows = []
    for tid, cycle, ind, unit, a, b, layout, kinds in TABLES:
        block = [lines[i].split("\t") for i in range(a - 1, b)]
        carried = {}
        if layout == "wide":
            gft = next(i for i, r in enumerate(block) if [c.strip() for c in r[:6]].count("G") >= 1
                       and any(c.strip() == "F" for c in r))
            start = next(j for j, c in enumerate(block[gft]) if c.strip() == "G")
            ntrip = sum(1 for c in block[gft][start:] if c.strip() == "G")
            years = YEARS[-ntrip:]
            for r in block[gft + 1:]:
                if not any(c.strip() for c in r):
                    continue
                lab = labels_from_row(r, kinds, carried)
                carried = {k: v for k, v in lab.items()}
                for t, year in enumerate(years):
                    for s, sex in enumerate("GFT"):
                        j = start + 3 * t + s
                        v = number(r[j]) if j < len(r) else None
                        if v is not None:
                            rows.append((tid, cycle, ind, unit, lab, sex, year, v))
        else:
            nlab = len(kinds) + (1 if layout == "long" else 0)
            for r in block:
                cells = [c.strip() for c in r]
                vals = cells[nlab:nlab + 10]
                if not cells or len(vals) < 10 or not all(is_number(v) for v in vals):
                    continue  # title, header ("2015-2016" is not a number) or stray cell
                if cells[0].upper() in HEADERS or (layout == "long" and cells[len(kinds)].upper() == "SEXE"):
                    continue  # header row whose year labels ("2016") look like numbers
                lab = labels_from_row(cells, kinds, carried)
                carried = {k: v for k, v in lab.items()}
                if layout == "long":
                    sraw = cells[len(kinds)].upper() or carried.get("_sexe", "")
                    sex = SEX.get(sraw)
                    if sex is None:
                        raise ValueError(f"{tid}: unknown sex label {cells[len(kinds)]!r}")
                else:
                    sex = "T"
                for year, v in zip(YEARS, vals):
                    rows.append((tid, cycle, ind, unit, lab, sex, year, number(v)))
    return rows


def main():
    src, dst = sys.argv[1], sys.argv[2]
    rows = parse(src)
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["table", "cycle", "indicateur", "unite", "region", "statut", "milieu", "niveau",
                    "sexe", "annee", "valeur"])
        for tid, cycle, ind, unit, lab, sex, year, v in rows:
            region = norm_label("region", lab["region"]) if "region" in lab else "NATIONAL"
            statut = norm_label("statut", lab.get("statut", "")) or "Total"
            milieu = norm_label("milieu", lab.get("milieu", "")) or "Total"
            niveau = lab.get("niveau", "") or "Total"
            if niveau.upper() == "TOTAL":
                niveau = "Total"
            w.writerow([tid, cycle, ind, unit, region, statut, milieu, niveau, sex, year,
                        int(v) if v.is_integer() else v])
    print(f"{len(rows)} valeurs écrites dans {dst}")


if __name__ == "__main__":
    main()

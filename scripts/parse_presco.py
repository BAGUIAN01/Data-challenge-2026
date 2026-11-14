"""Turn the challenge's Presco.txt export into one tidy CSV."""
import csv
import glob
import os
import re
import sys

import openpyxl

YEARS = [f"{y}-{y + 1}" for y in range(2015, 2025)]

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
    out = {}
    for i, kind in enumerate(kinds):
        raw = cells[i].strip() if i < len(cells) else ""
        out[kind] = raw if raw else carried.get(kind, "")
    first = kinds[0]
    raw0 = cells[0].strip() if cells else ""
    if raw0.upper().startswith("TOTAL ") and raw0.upper() not in NATIONAL:
        rest = raw0[6:]
        if first == "region":
            out["region"], out[kinds[1]] = rest, "Total"
        else:
            out[first], out[kinds[1]] = rest, "Total"
    elif raw0.upper() in NATIONAL:
        out[first] = "NATIONAL" if first == "region" else "Total"
        for k in kinds[1:]:
            if not (cells[kinds.index(k)].strip() if kinds.index(k) < len(cells) else ""):
                out[k] = "Total"
    return out


def xlsx_lines(path):
    """The platform's .xlsx, read as the tab-separated export it comes from: one line per row, same layout."""
    book = openpyxl.load_workbook(path, data_only=True)
    sheet = book.worksheets[0]
    lines = []
    for row in sheet.iter_rows():
        cells = []
        for c in row:
            v = c.value
            if v is None:
                cells.append("")
            elif isinstance(v, float) and "%" in (c.number_format or ""):
                cells.append(f"{v * 100:.1f}")
            elif isinstance(v, float) and v.is_integer():
                cells.append(str(int(v)))
            else:
                cells.append(str(v))
        lines.append("\t".join(cells))
    return lines


def find_source(path):
    """Presco.txt, or else the challenge .xlsx placed in the same folder."""
    if os.path.exists(path):
        return path
    found = sorted(glob.glob(os.path.join(os.path.dirname(path) or ".", "*.xlsx")))
    if not found:
        raise SystemExit(f"Fichier du challenge introuvable : placer {path} ou le fichier .xlsx de la plateforme dans {os.path.dirname(path)}/")
    return found[0]


def parse(path):
    if path.lower().endswith(".xlsx"):
        lines = xlsx_lines(path)
    else:
        lines = open(path, encoding="utf-8", newline="").read().split("\r\n")
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
                    continue
                if cells[0].upper() in HEADERS or (layout == "long" and cells[len(kinds)].upper() == "SEXE"):
                    continue
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
    src, dst = find_source(sys.argv[1]), sys.argv[2]
    print("fichier du challenge lu :", src)
    rows = parse(src)
    known = {(r[0], r[4].get("region", ""), r[5], r[6]): r[7] for r in rows}
    checks = [(("E1", "TOTAL GENERAL", "T", "2024-2025"), 3308096), (("E8", "TOTAL GENERAL", "T", "2024-2025"), 51.6)]
    for key_, expected in checks:
        got = next((v for k, v in known.items() if k[0] == key_[0] and norm_label("region", k[1]) == "NATIONAL" and k[2:] == key_[2:]), None)
        if got is None or abs(got - expected) > 0.05:
            raise SystemExit(f"Lecture incorrecte du fichier du challenge ({key_[0]} {key_[3]} : {got} au lieu de {expected}). "
                             "Enregistrer le fichier depuis Excel en « Texte (séparateur : tabulation) » sous data/raw/Presco.txt.")
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["table", "cycle", "indicateur", "unite", "region", "statut", "milieu", "niveau",
                    "sexe", "annee", "valeur"])
        for tid, cycle, ind, unit, lab, sex, year, v in rows:
            region = norm_label("region", lab["region"]) if "region" in lab else "NATIONAL"
            status = norm_label("statut", lab.get("statut", "")) or "Total"
            area = norm_label("milieu", lab.get("milieu", "")) or "Total"
            tier = lab.get("niveau", "") or "Total"
            if tier.upper() == "TOTAL":
                tier = "Total"
            w.writerow([tid, cycle, ind, unit, region, status, area, tier, sex, year,
                        int(v) if v.is_integer() else v])
    print(f"{len(rows)} valeurs écrites dans {dst}")


if __name__ == "__main__":
    main()

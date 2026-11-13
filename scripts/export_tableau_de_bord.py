"""Export everything the dashboard shows into one JSON file: dashboard/public/data/tableau_de_bord.json.

The same file seeds the Neon database (dashboard/db/seed.mjs) and is bundled with the app as the
offline snapshot. Key facts and levers come from scripts/fiches_regionales.py (one rule, two outputs:
the PDF fiche and the dashboard). The map is projected here into SVG paths, so the dashboard needs
no map tiles and works without network.

Usage: python export_tableau_de_bord.py (from the project root, after all analysis scripts).
"""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
import fiches_regionales as fiches  # noqa: E402

OUT = "dashboard/public/data/tableau_de_bord.json"
YEARS = fiches.YEARS
SHORT = fiches.SHORT
FACTORS = [  # id, label, unit, higher value means more exposed, lever when among the 4 most exposed
    ("violence", "Violence", "incidents par an", True, "Continuité éducative : écoles délocalisées, enseignement à distance, radio."),
    ("deplaces", "Déplacés accueillis", "% de la population", True, "Places d'accueil, classes passerelles, inscription sans pièces."),
    ("pauvrete", "Pauvreté", "% de la population", True, "Cantines scolaires, aides aux familles liées à la scolarité, fournitures."),
    ("faim", "Faim (phase 3 ou plus)", "% de la population", True, "Cantines scolaires pendant la soudure."),
    ("meres", "Femmes sans instruction", "% des 15-49 ans", True, "Alphabétisation des mères, associations de mères éducatrices."),
    ("grossesses", "Grossesses précoces", "naissances pour 1 000 filles de 15-19 ans", True, "Maintien des filles à l'école, lutte contre le mariage d'enfants."),
    ("cep", "Réussite au CEP", "%", False, None),
    ("prescolaire", "Préscolaire", "taux brut, %", False, "Préscolaire communautaire."),
]


def num(v, nd=1):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else round(float(v), nd)


def project(geom, lon0, lat_max, k):
    """Equirectangular projection scaled by cos(latitude): good enough for a country of this size."""
    c = math.cos(math.radians(12.3))
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    parts = []
    for poly in polys:
        pts = [((x - lon0) * c * k, (lat_max - y) * k) for x, y in poly.exterior.coords]
        parts.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(parts)


def carte():
    g = gpd.read_file("data/ref/regions_13.geojson")
    g["geometry"] = g.geometry.simplify(0.01, preserve_topology=True)
    lon0, lat0, lon1, lat1 = g.total_bounds
    k = 100
    out = {}
    for _, r in g.iterrows():
        p = r.geometry.representative_point()
        out[r.cle_presco] = {"d": project(r.geometry, lon0, lat1, k),
                             "lx": round((p.x - lon0) * math.cos(math.radians(12.3)) * k, 1),
                             "ly": round((lat1 - p.y) * k, 1)}
    w = (lon1 - lon0) * math.cos(math.radians(12.3)) * k
    return {"largeur": round(w, 1), "hauteur": round((lat1 - lat0) * k, 1), "regions": out}


def formule_risque():
    """The risk models as formulas, in original units (scripts/formule_risque.py, checked there against
    the probabilities shown): logit(p) = constante + sum of coefficient x variable."""
    f = pd.read_csv("analyse/P17_formule_risque.csv")
    cles = {"Référence": "reference", "Alerte de septembre": "septembre", "Alerte de janvier": "janvier"}
    out = {"observations": int(f.observations.iloc[0]), "baisses": int(f.baisses.iloc[0])}
    for _, r in f.iterrows():
        k = next(v for c, v in cles.items() if r.modele.startswith(c))
        out[k] = {c: float(r[c]) for c in ["constante", "l_inc", "d_l_inc", "l_late", "l_rentree"] if c in r and pd.notna(r[c])}
    return out


def score_global():
    """Global score per region and its replay on the past (scripts/score_global.py). Stored with the
    data set's parameters: one computation (Python), read as is by the app and the database."""
    s = pd.read_csv("analyse/P18_score_global_2026_27.csv").set_index("region_2025").score_global
    names = {v: k for k, v in fiches.load()[0].drop_duplicates("cle").set_index("cle").region_2025.items()}
    rj = pd.read_csv("analyse/P18_score_global_rejoue.csv").set_index("mesure")
    return {"poids_risque": 0.5, "par_region": {names[n]: int(v) for n, v in s.items()},
            "rejoue": {"auc_score": round(float(rj.loc["Score global", "AUC_baisse_t+1"]), 2),
                       "auc_risque": round(float(rj.loc["Risque seul (violence)", "AUC_baisse_t+1"]), 2),
                       "baisses_score_pct": round(float(rj.loc["Score global", "baisses_prises_%"])),
                       "baisses_matrice_pct": round(float(rj.loc["Matrice (priorité 1)", "baisses_prises_%"])),
                       "perdus_score_pct": round(float(rj.loc["Score global", "eleves_perdus_pris_%"])),
                       "perdus_matrice_pct": round(float(rj.loc["Matrice (priorité 1)", "eleves_perdus_pris_%"]))}}


def main():
    data = fiches.load()
    p = data[0]
    nat = p[p.region == "NATIONAL"].set_index("annee").loc[YEARS]
    keys = sorted(p[p.region != "NATIONAL"].cle.unique())
    names = p.drop_duplicates("cle").set_index("cle").region_2025
    prio = pd.read_csv("analyse/P13_matrice_priorite_2026_27.csv").set_index("region_2025")
    prof = pd.read_csv("analyse/P14_profil_facteurs.csv").set_index("region_2025")
    cal = pd.read_csv("analyse/P16_alertes_calendrier.csv").set_index("region")
    cal.columns = ["janv_2025_26", "sept_2026_27", "ref_2026_27"]
    acled = pd.read_csv("analyse/acled_region_annee.csv")
    sy = [f"{y}-{y + 1}" for y in range(2015, 2026)]
    nowc = pd.read_csv("analyse/P12_nowcast_ecoles.csv").set_index("annee").loc["moyenne"]
    d = p[p.region != "NATIONAL"].dropna(subset=["dlog_eleves", "dlog_ecoles"])
    slope, const = np.polyfit(d.dlog_ecoles, d.dlog_eleves, 1)
    tap_nat = float(nat.TAP_T.iloc[-1])

    regions = []
    Path("dashboard/public/fiches").mkdir(parents=True, exist_ok=True)
    for cle in keys:
        c = fiches.contenu(cle, data)
        r, f, name = c["r"], c["f"], c["name25"]
        # The one-page PDF fiche, offered for download in the dashboard (kept offline too).
        shutil.copy2(f"analyse/fiches/fiche_{fiches.key(name).lower()}.pdf", f"dashboard/public/fiches/{cle}.pdf")
        pr, pf, ca = prio.loc[name], prof.loc[name], cal.loc[name]
        inc = acled[acled.cle == cle].set_index("annee").incidents.reindex(sy)
        facteurs = {fid: {"valeur": num(pf["incidents_moy"] if fid == "violence" else pf[fid]),
                          "niveau": int(pf[f"{fid}_niveau"])} for fid, *_ in FACTORS}
        lev_f = [lev for fid, _, _, _, lev in FACTORS if lev and facteurs[fid]["niveau"] == 1]
        regions.append({
            "cle": cle, "nom": name, "ancienne": c["old"], "codes": r.codes_2025.iloc[0], "type": r.type_2025.iloc[0],
            "profil": c["profile"], "priorite": int(pr.priorite),
            "tap": [num(v) for v in r.TAP_T], "tap_f": [num(v) for v in r.TAP_F], "tap_g": [num(v) for v in r.TAP_G],
            "eleves": [int(v) for v in r.eleves_T], "ecoles": [int(v) for v in r.ecoles],
            "incidents": [None if np.isnan(v) else int(v) for v in inc],
            "prevision_2025_26": {"centrale": num(f.prevision_25_26), "basse": num(f.fourchette_basse),
                                  "haute": num(f.fourchette_haute)},
            "enfants_hors_cm2": int(f.enfants_hors_CM2_estimes),
            "probabilites": {"janv_2025_26": int(ca.janv_2025_26), "sept_2026_27": int(ca.sept_2026_27),
                             "ref_2026_27": int(ca.ref_2026_27)},
            "facteurs": facteurs, "faits": c["facts"], "leviers": c["levers"], "leviers_facteurs": lev_f,
        })
    payload = {
        "annees": SHORT, "annees_violence": [y[2:4] + "/" + y[7:] for y in sy],
        "national": {"tap": [num(v) for v in nat.TAP_T], "eleves": [int(v) for v in nat.eleves_T]},
        "seuils": {"tap_national": round(tap_nat, 1), "risque_eleve": 40, "risque_moyen": 15},
        "nowcast": {"pente": round(float(slope), 4), "constante": round(float(const), 4),
                    "erreur_pct": round(float(nowc["effectifs_ecoles_%"]), 1),
                    "erreur_persistance_pct": round(float(nowc["effectifs_persistance_%"]), 1)},
        "validation": {"rang_tap": 0.97, "auc_reference": 0.83, "auc_septembre": 0.85, "auc_janvier": 0.88,
                       "matrice_regions_pct": 35, "matrice_baisses_pct": 71, "matrice_perdus_pct": 69},
        "facteurs_def": [{"id": fid, "libelle": lab, "unite": u, "haut_expose": up} for fid, lab, u, up, _ in FACTORS],
        "formule_risque": formule_risque(),
        "score_global": score_global(),
        "carte": carte(),
        "regions": regions,
    }
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["version"] = hashlib.sha256(body.encode()).hexdigest()[:12]
    payload["genere_le"] = pd.Timestamp.today().strftime("%Y-%m-%d")
    with open(OUT, "w") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(regions)} régions, version {payload['version']}, {len(json.dumps(payload)) / 1e3:.0f} ko -> {OUT}")


if __name__ == "__main__":
    main()

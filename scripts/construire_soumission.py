"""Build the files to upload on the challenge platform: three categories, at most 20 files, no team name."""
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "soumission"
# Words that must not appear anywhere (team, members, brand): one per line in a local, git-ignored file.
_WORDS_FILE = ROOT / ".noms_interdits"
FORBIDDEN = re.compile("(?i)" + "|".join(re.escape(m.strip()) for m in _WORDS_FILE.read_text().splitlines() if m.strip())) if _WORDS_FILE.exists() else None

TABLES = [
    ("A_tendances_nationales", "Tendances nationales 2015/16-2024/25"),
    ("B_choc_et_reprise_par_region", "Choc et reprise des effectifs par région"),
    ("C_sorties_apparentes_par_region", "Sorties apparentes par région et par année"),
    ("D_passages_apparents_par_niveau", "Passages apparents d'un niveau au suivant (national)"),
    ("D_survie_apparente_CP1_CM2", "Survie apparente du CP1 au CM2 (national)"),
    ("E_parite_achevement", "Parité filles / garçons de l'achèvement"),
    ("G_persistance_TAP", "Persistance du taux d'achèvement d'une année à l'autre"),
    ("P1_sorties_excedentaires", "Sorties en excès par rapport à 2015-2018"),
    ("P2_typologie_regions", "Quatre profils de régions (classification de Ward)"),
    ("P3_contributions_recul_TAP", "Contribution des régions au recul de l'achèvement national"),
    ("P4_entree_sortie_national", "Entrées en CP1 et fin de cycle, national"),
    ("P5_genre", "Achèvement des garçons et des filles"),
    ("P6_prevision", "Prévision « comme l'an passé » sur années non vues"),
    ("P7_scenarios_reouverture", "Scénarios de réouverture d'écoles"),
    ("P8_anticipation_acled", "La violence prévoit-elle mieux que « comme l'an passé » ?"),
    ("P9_prevision_2025_26_alerte", "Prévision 2025/26 avec fourchette, et alerte d'escalade"),
    ("P10_hypothese_transversale", "Test de l'hypothèse insécurité × pauvreté"),
    ("P10_attaques_education_region_annee", "Attaques contre l'éducation par région et année (agrégat)"),
    ("P11_ml_regression", "Apprentissage automatique : variation de l'achèvement"),
    ("P11_ml_classification", "Apprentissage automatique : baisse des effectifs de plus de 5 %"),
    ("P11_importance", "Importance des variables (forêt aléatoire)"),
    ("P11_probabilites_alerte", "Probabilités de baisse 2025/26 et 2026/27"),
    ("P12_nowcast_ecoles", "Effectifs prévus à partir des écoles ouvertes"),
    ("P12_filiere_un_an", "Filière des cohortes, un an à l'avance"),
    ("P12_filiere_fourchette", "Filière des cohortes : fourchette et sens"),
    ("P12_projection_CM2", "Projection du CM2 en 2025/26"),
    ("P12_cohortes_national", "CP1 et CM2, national"),
    ("P12_scenario_cohortes_CP1", "Scénario : cohortes de CP1 jusqu'au CM2"),
    ("P13_stabilite_classement", "Stabilité du classement des régions"),
    ("P13_effectifs_modeles", "Effectifs : modèles contre « comme l'an passé »"),
    ("P13_effectifs_predictions", "Effectifs : prédictions détaillées"),
    ("P13_TAP_modeles", "Achèvement : modèles contre « comme l'an passé »"),
    ("P13_matrice_rejouee", "Matrice de priorité rejouée sur le passé"),
    ("P13_matrice_priorite_2026_27", "Matrice de priorité 2026/27"),
    ("P14_facteurs_correlations", "Facteurs et achèvement : corrélations"),
    ("P14_profil_facteurs", "Profil des facteurs de chaque région"),
    ("P14_faim_panel", "Faim et violence : panel à effets fixes"),
    ("P14_faim_regions_calmes", "Contrôle : les 9 régions les moins touchées"),
    ("P15_alerte_facteurs", "Les autres facteurs aident-ils l'alerte ?"),
    ("P15_TAP_un_an", "Les facteurs aident-ils à prévoir l'achèvement à un an ?"),
    ("P15_TAP_trois_ans", "… et à trois ans ?"),
    ("P16_signaux_fins", "Signaux fins de violence : six variantes testées"),
    ("P16_signaux_region_annee", "Signaux de violence par région et année"),
    ("P16_alertes_calendrier", "Calendrier d'alerte : référence, septembre, janvier"),
    ("P17_formule_risque", "Formule du risque, vérifiée contre les probabilités affichées"),
    ("P18_score_global_2026_27", "Score global 2026/27 de chaque région"),
    ("P18_score_global_rejoue", "Score global rejoué sur le passé"),
    ("P18_score_global_trajectoire", "Score de chaque région année par année"),
    ("P19_facteur_dominant", "Facteur dominant de chaque région"),
]
# Challenge naming rule without the team part (blind review): ETAPE_DEFI_ROLE_description_vN.
VERSION = 1
UPLOAD_NAMES = {'documentation/rapport.pdf': '05-interpretation_D1_analyst_rapport',
    'documentation/fiches_regionales.pdf': '05-interpretation_D1_analyst_fiches-regionales',
    'documentation/formule_du_risque.md': '04-analyse_D1_scientist_formule-risque',
    'documentation/journal_des_decisions.md': '04-analyse_D1_scientist_journal-decisions',
    'code/cahier_02_nettoyage.ipynb': '02-nettoyage_D1_engineer_cahier-nettoyage',
    'code/cahier_03_transformation.ipynb': '03-transformation_D1_architect_cahier-transformation',
    'code/cahier_04a_analyse_descriptive.ipynb': '04-analyse_D1_analyst_cahier-analyse-descriptive',
    'code/cahier_04b_modeles.ipynb': '04-analyse_D1_scientist_cahier-modeles',
    'code/cahier_05_interpretation.ipynb': '05-interpretation_D1_analyst_cahier-interpretation',
    'code/tableau_de_bord.zip': '05-interpretation_D1_analyst_tableau-de-bord',
    'code/projet_complet.zip': '05-interpretation_D1_scientist_projet-complet',
    'donnees/priorites_2026_27.csv': '05-interpretation_D1_analyst_priorites-2026-27',
    'donnees/resultats_analyse.xlsx': '04-analyse_D1_scientist_resultats-analyse',
    'donnees/donnees_tableau_de_bord.json': '05-interpretation_D1_analyst_donnees-tableau-de-bord',
    'donnees/donnees_transformees.zip': '03-transformation_D1_engineer_donnees-transformees',
    'donnees/donnees_nettoyees.zip': '02-nettoyage_D1_engineer_donnees-nettoyees'}
ACTION_NAME = {"violence": "l'insécurité", "deplaces": "l'accueil des déplacés", "pauvrete": "la pauvreté", "faim": "la faim",
              "meres": "l'instruction des mères", "grossesses": "les grossesses précoces", "prescolaire": "le préscolaire"}


def zip_files(dest, files):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in files:
            z.write(ROOT / src, arc)


def git_archive(dest, subpath=None):
    cmd = ["git", "archive", "--format=zip", "-o", str(dest), "HEAD"] + ([subpath] if subpath else [])
    subprocess.run(cmd, cwd=ROOT, check=True)


def priorities(dataset):
    sg, fd = dataset["score_global"], dataset["facteur_dominant"]["par_region"]
    defs = {d["id"]: d for d in dataset["facteurs_def"]}
    lines_out = []
    for r in dataset["regions"]:
        f = fd[r["cle"]]
        lines_out.append({
            "region_2025": r["nom"], "ancienne_region": r["ancienne"], "score_global_2026_27": sg["par_region"][r["cle"]],
            "probabilite_chute_effectifs_pct": r["probabilites"]["ref_2026_27"], "alerte_septembre_pct": r["probabilites"]["sept_2026_27"],
            "taux_achevement_2024_25_pct": r["tap"][-1], "priorite": r["priorite"],
            "agir_sur": ACTION_NAME[f["dominant"]] if f["dominant"] else "aucun facteur au-dessus de la moyenne : consolider",
            "levier": defs[f["dominant"]]["levier"] if f["dominant"] else "Consolider ce qui marche.",
            "ensuite": ACTION_NAME[f["second"]] if f["second"] else "",
            "enfants_hors_cm2_estimes": int(round(r["enfants_hors_cm2"], -2)),
        })
    return pd.DataFrame(lines_out).sort_values(["priorite", "score_global_2026_27"], ascending=[True, False])


def workbook(dest):
    with pd.ExcelWriter(dest, engine="openpyxl") as w:
        pd.DataFrame(TABLES, columns=["feuille", "contenu"]).to_excel(w, sheet_name="lisez-moi", index=False)
        for name, _ in TABLES:
            pd.read_csv(ROOT / "analyse" / f"{name}.csv").to_excel(w, sheet_name=name[:31], index=False)


def main():
    dataset = json.load(open(ROOT / "dashboard/public/data/tableau_de_bord.json", encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    D, C, T = OUT / "donnees", OUT / "code", OUT / "documentation"
    for d in (D, C, T):
        d.mkdir(parents=True)

    priorities(dataset).to_csv(D / "priorites_2026_27.csv", index=False)
    shutil.copy2(ROOT / "dashboard/public/data/tableau_de_bord.json", D / "donnees_tableau_de_bord.json")
    workbook(D / "resultats_analyse.xlsx")
    zip_files(D / "donnees_nettoyees.zip", [
        ("data/tidy/presco_tidy.csv", "donnees_challenge_propres.csv"),
        ("analyse/controles_qualite.txt", "controles_qualite.txt"),
        ("docs/sources_donnees.csv", "sources_donnees.csv"),
    ] + [(f"data/externe_propre/{p.name}", p.name) for p in sorted((ROOT / "data/externe_propre").iterdir())])
    zip_files(D / "donnees_transformees.zip", [
        ("analyse/panel_region_annee_2025.csv", "panel_region_annee.csv"),
        ("analyse/acled_region_annee.csv", "violence_acled_region_annee.csv"),
        ("analyse/P16_signaux_region_annee.csv", "signaux_violence_region_annee.csv"),
        ("analyse/P10_attaques_education_region_annee.csv", "attaques_education_region_annee.csv"),
        ("data/ref/regions_13_17.csv", "correspondance_regions_13_17.csv"),
        ("data/ref/provinces_45_47.csv", "correspondance_provinces_45_47.csv"),
        ("data/ref/regions_13.geojson", "carte_13_regions.geojson"),
        ("docs/dictionnaire_variables.md", "dictionnaire_variables.md"),
    ])

    git_archive(C / "projet_complet.zip")
    git_archive(C / "tableau_de_bord.zip", "dashboard")
    for i, notebook in enumerate(sorted((ROOT / "notebooks").glob("*.ipynb")), 1):
        shutil.copy2(notebook, C / f"cahier_{notebook.name}")

    shutil.copy2(ROOT / "rapport/rapport_defi1.pdf", T / "rapport.pdf")
    shutil.copy2(ROOT / "analyse/fiches_regionales_13.pdf", T / "fiches_regionales.pdf")
    shutil.copy2(ROOT / "analyse/formule_risque.md", T / "formule_du_risque.md")
    shutil.copy2(ROOT / "docs/journal_decisions.md", T / "journal_des_decisions.md")
    shutil.copy2(ROOT / "docs/LISEZ-MOI_soumission.md", T / "LISEZ-MOI.md")

    for old_name, name in UPLOAD_NAMES.items():
        f = OUT / old_name
        f.rename(f.with_name(f"{name}_v{VERSION}{f.suffix}"))
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    if (ROOT / "fiche_de_la_solution.md").exists():
        shutil.copy2(ROOT / "fiche_de_la_solution.md", OUT / "fiche_de_la_solution.md")
    print(f"{len(files)} fichiers (20 au plus), {sum(p.stat().st_size for p in files) / 1e6:.1f} Mo")
    for p in files:
        print(f"  {p.relative_to(OUT)}  {p.stat().st_size / 1e6:.2f} Mo")
    assert len(files) <= 20 and all(p.stat().st_size < 50e6 for p in files)
    if FORBIDDEN is None:
        print("liste .noms_interdits absente : contrôle d'anonymat non fait")
        return
    hits = []
    for p in files:
        texts = []
        if p.suffix == ".zip":
            with zipfile.ZipFile(p) as z:
                texts = [(f"{p.name}!/{n}", z.read(n)) for n in z.namelist() if not n.endswith((".png", ".xlsx", ".pdf", "/"))]
        elif p.suffix != ".pdf" and p.suffix != ".xlsx":
            texts = [(p.name, p.read_bytes())]
        else:
            r = subprocess.run(["pdftotext", str(p), "-"], capture_output=True) if p.suffix == ".pdf" else None
            texts = [(p.name, r.stdout)] if r else []
        for name, data in texts:
            for m in set(x.lower() for x in FORBIDDEN.findall(data.decode("utf-8", "ignore"))):
                hits.append((m, name))
    if FORBIDDEN.search(" ".join(p.name for p in files)):
        hits.append(("nom de fichier", "?"))
    print("traces d'identité :", sorted(set(hits)) or "aucune")


if __name__ == "__main__":
    main()

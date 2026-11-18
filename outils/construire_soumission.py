"""Build the files to upload on the challenge platform: three categories, at most 20 files.

Default: files named with the team, ÉQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN, as in the repository.
With --anonyme: no team name in names or contents (blind review), and the presentation is left out."""
import base64
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pymupdf
from PIL import Image

import chemins

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
OUT = ROOT / "soumission"
EXTERNAL_CLEAN = [k for k in chemins.FILES if chemins.FILES[k].startswith("02_nettoyage/") and k.split(".")[0] in
                  ("eds_2021_regions", "faim_cadre_harmonise_region_annee", "pauvrete_ehcvm_2021_regions", "pdi_conasur_2022_regions")]
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
ANONYMOUS = "--anonyme" in sys.argv
# Challenge naming rule: EQUIPE_ETAPE_DEFI_ROLE_description_vN (team part dropped with --anonyme).
VERSION = 1
UPLOAD_NAMES = {'documentation/rapport.pdf': '05-interpretation_D1_analyst_rapport',
    'documentation/presentation.pdf': '05-interpretation_D1_analyst_presentation',
    'documentation/fiches_regionales.pdf': '05-interpretation_D1_analyst_fiches-regionales',
    'documentation/formule_du_risque.md': '04-analyse_D1_scientist_formule-risque',
    'documentation/journal_des_decisions.md': '04-analyse_D1_scientist_journal-decisions',
    'code/notebook_02_nettoyage.ipynb': '02-nettoyage_D1_engineer_notebook-nettoyage',
    'code/notebook_03_transformation.ipynb': '03-transformation_D1_architect_notebook-transformation',
    'code/notebook_04a_analyse_descriptive.ipynb': '04-analyse_D1_analyst_notebook-analyse-descriptive',
    'code/notebook_04b_modeles.ipynb': '04-analyse_D1_scientist_notebook-modeles',
    'code/notebook_05_interpretation.ipynb': '05-interpretation_D1_analyst_notebook-interpretation',
    'code/tableau_de_bord.zip': '05-interpretation_D1_analyst_tableau-de-bord',
    'code/projet_complet.zip': '05-interpretation_D1_scientist_projet-complet',
    'donnees/priorites_2026_27.csv': '05-interpretation_D1_analyst_priorites-2026-27',
    'donnees/resultats_analyse.xlsx': '04-analyse_D1_scientist_resultats-analyse',
    'donnees/donnees_tableau_de_bord.json': '05-interpretation_D1_analyst_donnees-tableau-de-bord',
    'donnees/donnees_transformees.zip': '03-transformation_D1_engineer_donnees-transformees',
    'donnees/donnees_nettoyees.zip': '02-nettoyage_D1_engineer_donnees-nettoyees'}
STEP = re.compile(r"(0[1-5])-([a-z]+)_D1_")
ACTION_NAME = {"violence": "l'insécurité", "deplaces": "l'accueil des déplacés", "pauvrete": "la pauvreté", "faim": "la faim",
              "meres": "l'instruction des mères", "grossesses": "les grossesses précoces", "prescolaire": "le préscolaire"}


TEAM = "Biiga"
TEXT = (".py", ".md", ".txt", ".csv", ".json", ".geojson", ".tex", ".js", ".mjs", ".css", ".sql", ".ipynb", ".webmanifest", ".html", ".toml", ".yml", ".yaml")


def anonymous(text):
    """For the blind review: no team prefix in names or paths, and no line that names the team."""
    if not ANONYMOUS:
        return text
    text = text.replace(f"{TEAM}_", "")
    return "\n".join(l for l in text.split("\n") if TEAM.lower() not in l.lower() and not (FORBIDDEN and FORBIDDEN.search(l)))


def put(z, src, arc):
    if not ANONYMOUS:
        z.write(src, arc)
        return
    arc = arc.replace(f"{TEAM}_", "")
    if str(src).endswith(TEXT):
        text = Path(src).read_text(encoding="utf-8")
        if TEAM.lower() in text.lower() or (FORBIDDEN and FORBIDDEN.search(text)):
            z.writestr(arc, anonymous(text))
            return
    z.write(src, arc)


def zip_files(dest, files):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in files:
            put(z, ROOT / src, arc)


# Left out of the project archive: what the code regenerates, or what is uploaded on its own.
REGENERATED = re.compile(r"^(0[2-5]_[a-z]+/.*\.ipynb$|.*/(figures|fiches|captures)/.*\.(png|pdf)$|.*\.pdf$)")


def git_archive(dest, subpath=None, light=False):
    files = subprocess.run(["git", "ls-files"] + ([subpath] if subpath else []), cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in filter(None, files):
            if not (light and REGENERATED.match(f)):
                put(z, ROOT / f, f)


def light_notebook(src, dest, width=820, quality=55):
    """Same notebook, figures shown as JPEG at screen size: the file stays small enough to upload."""
    nb = json.load(open(src, encoding="utf-8"))
    for cell in nb["cells"]:
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            if "image/png" in data:
                im = Image.open(io.BytesIO(base64.b64decode(data.pop("image/png")))).convert("RGB")
                im.thumbnail((width, width * 3))
                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
                data["image/jpeg"] = base64.b64encode(buf.getvalue()).decode()
                out.get("metadata", {}).pop("image/png", None)
    Path(dest).write_text(json.dumps(json.loads(anonymous(json.dumps(nb, ensure_ascii=False, indent=1))), ensure_ascii=False, indent=1), encoding="utf-8")


def light_pdf(src, dest, max_side=1600, quality=70):
    """Same PDF, its JPEG images re-encoded smaller (uploads fail above about 1 MB). Image objects are
    replaced one by one: rewriting them with the library's own helper broke the slides' patterns."""
    d = pymupdf.open(src)
    for xref in range(1, d.xref_length()):
        if d.xref_get_key(xref, "Subtype")[1] != "/Image" or d.xref_get_key(xref, "Filter")[1] != "/DCTDecode":
            continue
        raw = d.xref_stream_raw(xref)
        im = Image.open(io.BytesIO(raw))
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True)
        if buf.tell() >= len(raw):
            continue
        d.update_stream(xref, buf.getvalue(), compress=False)
        for key, value in (("Filter", "/DCTDecode"), ("Width", im.width), ("Height", im.height), ("Length", buf.tell())):
            d.xref_set_key(xref, key, str(value))
    d.save(dest, garbage=1, deflate=True)


def copy_text(src, dest):
    Path(dest).write_text(anonymous(Path(src).read_text(encoding="utf-8")), encoding="utf-8")


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
            pd.read_csv(chemins.path(f"{name}.csv")).to_excel(w, sheet_name=name[:31], index=False)


def main():
    dataset = json.load(open(ROOT / "dashboard/public/data/tableau_de_bord.json", encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    D, C, T = OUT / "donnees", OUT / "code", OUT / "documentation"
    for d in (D, C, T):
        d.mkdir(parents=True)

    priorities(dataset).to_csv(chemins.path("priorites_2026_27.csv"), index=False)
    shutil.copy2(chemins.path("priorites_2026_27.csv"), D / "priorites_2026_27.csv")
    shutil.copy2(ROOT / "dashboard/public/data/tableau_de_bord.json", D / "donnees_tableau_de_bord.json")
    workbook(D / "resultats_analyse.xlsx")
    zip_files(D / "donnees_nettoyees.zip", [
        (chemins.rel("presco_tidy.csv"), "donnees_challenge_propres.csv"),
        (chemins.rel("controles_qualite.txt"), "controles_qualite.txt"),
        (chemins.rel("sources_donnees.csv"), "sources_donnees.csv"),
    ] + [(chemins.rel(k), k) for k in sorted(EXTERNAL_CLEAN)])
    zip_files(D / "donnees_transformees.zip", [
        (chemins.rel("panel_region_annee_2025.csv"), "panel_region_annee.csv"),
        (chemins.rel("acled_region_annee.csv"), "violence_acled_region_annee.csv"),
        (chemins.rel("P16_signaux_region_annee.csv"), "signaux_violence_region_annee.csv"),
        (chemins.rel("P10_attaques_education_region_annee.csv"), "attaques_education_region_annee.csv"),
        (chemins.rel("regions_13_17.csv"), "correspondance_regions_13_17.csv"),
        (chemins.rel("provinces_45_47.csv"), "correspondance_provinces_45_47.csv"),
        (chemins.rel("regions_13.geojson"), "carte_13_regions.geojson"),
        (chemins.rel("dictionnaire_variables.md"), "dictionnaire_variables.md"),
    ])

    git_archive(C / "projet_complet.zip", light=True)
    git_archive(C / "tableau_de_bord.zip", "dashboard")
    for key in ("02_nettoyage.ipynb", "03_transformation.ipynb", "04a_analyse_descriptive.ipynb", "04b_modeles.ipynb", "05_interpretation.ipynb"):
        light_notebook(chemins.path(key), C / f"notebook_{key}")

    shutil.copy2(chemins.path("rapport.pdf"), T / "rapport.pdf")
    if not ANONYMOUS:  # the slides carry the team name on every page
        light_pdf(ROOT / "05_interpretation" / f"{TEAM}_05-interpretation_D1_analyst_presentation_v1.pdf", T / "presentation.pdf")
    shutil.copy2(chemins.path("fiches_regionales_13.pdf"), T / "fiches_regionales.pdf")
    copy_text(chemins.path("formule_risque.md"), T / "formule_du_risque.md")
    copy_text(chemins.path("journal_decisions.md"), T / "journal_des_decisions.md")
    copy_text(HERE / "soumission_LISEZ-MOI_soumission.md", T / "LISEZ-MOI_documentation.md")
    copy_text(HERE / "soumission_LISEZ-MOI_code.txt", C / "LISEZ-MOI_code.txt")
    shutil.copy2(HERE / "soumission_LISEZ-MOI_donnees.csv", D / "LISEZ-MOI_donnees.csv")

    prefix = "" if ANONYMOUS else f"{TEAM}_"
    for old_name, name in UPLOAD_NAMES.items():
        f = OUT / old_name
        if f.exists():
            f.rename(f.with_name(f"{prefix}{name}_v{VERSION}{f.suffix}"))
    # Laid out by step, as in the repository (02_nettoyage/ ... 05_interpretation/); the READMEs at the top.
    for f in [p for p in OUT.rglob("*") if p.is_file()]:
        m = STEP.search(f.name)
        folder = OUT / f"{m[1]}_{m[2]}" if m else OUT
        folder.mkdir(exist_ok=True)
        f.rename(folder / f.name)
    for d in (D, C, T):
        d.rmdir()
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    if (ROOT / "fiche_de_la_solution.md").exists():
        shutil.copy2(ROOT / "fiche_de_la_solution.md", OUT / "fiche_de_la_solution.md")
    print(f"{len(files)} fichiers (20 au plus), {sum(p.stat().st_size for p in files) / 1e6:.1f} Mo")
    for p in files:
        print(f"  {p.relative_to(OUT)}  {p.stat().st_size / 1e6:.2f} Mo")
    assert len(files) <= 20 and all(p.stat().st_size < 50e6 for p in files)
    heavy = [p.name for p in files if p.stat().st_size > 1e6]
    print("au-dessus de 1 Mo :", heavy or "aucun")
    if not ANONYMOUS:
        print(f"nom d'équipe gardé ({TEAM}_…) ; --anonyme pour une version sans nom")
        return
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

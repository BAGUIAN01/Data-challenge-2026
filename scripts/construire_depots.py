"""Build the challenge deposits: one folder per step, files named EQUIPE_ETAPE_DEFI_ROLE_description_vN.

Rule from the challenge document (section 5): EQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN, for example
E07_02-nettoyage_D1_engineer_effectifs-primaire-propres_v2.csv ; one file = one step ; no space
and no accent in names ; numbered versions ; a short LISEZ-MOI saying what each deposit holds.

Writes depots/01_collecte ... depots/05_interpretation, a LISEZ-MOI.txt in each, one at the root,
and depots/<TEAM>_D1_depots_v<N>.zip. The full project archive (git HEAD) goes to step 5 so that
the solution can be run again. Usage: python construire_depots.py [TEAM] [VERSION]
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

TEAM = sys.argv[1] if len(sys.argv) > 1 else "Biiga"
VERSION = int(sys.argv[2]) if len(sys.argv) > 2 else 1
DEFI = "D1"
OUT = Path("depots")
STEPS = {"01": ("01_collecte", "01-collecte", "Collecte"), "02": ("02_nettoyage", "02-nettoyage", "Nettoyage"),
         "03": ("03_transformation", "03-transformation", "Transformation"),
         "04": ("04_analyse", "04-analyse", "Analyse"), "05": ("05_interpretation", "05-interpretation",
                                                                "Interprétation et visualisation")}
ROLES = {"engineer": "Data Engineer", "architect": "Data Architect", "analyst": "Data Analyst",
         "scientist": "Data Scientist"}
NAME_RE = re.compile(rf"^{TEAM}_0[1-5]-[a-z]+_{DEFI}_(engineer|architect|analyst|scientist)_[a-z0-9-]+_v\d+\.[a-z0-9]+$")

# Tables gathered in one workbook per role: (csv stem, what it holds).
WB_ANALYST = [
    ("A_tendances_nationales", "Tendances nationales 2015/16-2024/25"),
    ("B_choc_et_reprise_par_region", "Choc et reprise des effectifs par région"),
    ("C_sorties_apparentes_par_region", "Sorties apparentes par région et par année"),
    ("D_passages_apparents_par_niveau", "Passages apparents d'un niveau au suivant (national)"),
    ("D_survie_apparente_CP1_CM2", "Survie apparente du CP1 au CM2 (national)"),
    ("E_parite_achevement", "Parité filles / garçons de l'achèvement"),
    ("G_persistance_TAP", "Persistance du taux d'achèvement d'une année à l'autre"),
    ("P1_sorties_excedentaires", "Sorties en excès par rapport à 2015-2018, corrigées de la part nationale du CM2"),
    ("P2_typologie_regions", "Quatre profils de régions (classification de Ward)"),
    ("P3_contributions_recul_TAP", "Contribution des régions au recul du taux d'achèvement national"),
    ("P4_entree_sortie_national", "Entrées en CP1 et fin de cycle, national"),
    ("P5_genre", "Achèvement des garçons et des filles"),
    ("P6_prevision", "Prévision « comme l'an passé » sur années non vues"),
    ("P7_scenarios_reouverture", "Scénarios de réouverture d'écoles"),
]
WB_SCIENTIST = [
    ("P8_anticipation_acled", "La violence (ACLED) prévoit-elle mieux que « comme l'an passé » ?"),
    ("P9_prevision_2025_26_alerte", "Prévision 2025/26 avec fourchette mesurée, et alerte d'escalade"),
    ("P10_hypothese_transversale", "Test de l'hypothèse insécurité × pauvreté"),
    ("P11_ml_regression", "Apprentissage automatique : variation du taux d'achèvement"),
    ("P11_ml_classification", "Apprentissage automatique : baisse des effectifs de plus de 5 %"),
    ("P11_importance", "Importance des variables (forêt aléatoire)"),
    ("P11_probabilites_alerte", "Probabilités de baisse 2025/26 et 2026/27 (logistique, violence seule)"),
    ("P12_nowcast_ecoles", "Effectifs prévus à partir des écoles ouvertes à la rentrée"),
    ("P12_filiere_un_an", "Filière des cohortes, un an à l'avance"),
    ("P12_filiere_fourchette", "Filière des cohortes : fourchette et sens de la variation"),
    ("P12_projection_CM2", "Projection du CM2 en 2025/26"),
    ("P12_cohortes_national", "CP1 et CM2, national"),
    ("P12_scenario_cohortes_CP1", "Scénario : cohortes de CP1 jusqu'au CM2"),
    ("P13_stabilite_classement", "Stabilité du classement des régions d'une année à l'autre"),
    ("P13_effectifs_modeles", "Effectifs : modèles contre « comme l'an passé »"),
    ("P13_effectifs_predictions", "Effectifs : prédictions détaillées"),
    ("P13_TAP_modeles", "Taux d'achèvement : modèles contre « comme l'an passé »"),
    ("P13_matrice_rejouee", "Matrice de priorité rejouée sur le passé"),
    ("P14_facteurs_correlations", "Facteurs et taux d'achèvement : corrélations de rang"),
    ("P14_faim_panel", "Faim et violence : panel à effets fixes"),
    ("P14_faim_regions_calmes", "Contrôle : les 9 régions les moins touchées"),
    ("P15_alerte_facteurs", "Les facteurs autres que la violence aident-ils l'alerte ?"),
    ("P15_TAP_un_an", "Les facteurs aident-ils à prévoir le taux d'achèvement à un an ?"),
    ("P15_TAP_trois_ans", "... et à trois ans ?"),
    ("P16_signaux_fins", "Signaux fins de violence : six variantes testées"),
]
RAW_ANALYST = ["resultats_analyse.txt", "resultats_pistes.txt"]
RAW_SCIENTIST = ["resultats_acled.txt", "resultats_prevision_hypothese.txt", "resultats_machine_learning.txt",
                 "resultats_approches_prevision.txt", "resultats_solution_prevision.txt",
                 "resultats_facteurs_decrochage.txt", "resultats_prevision_facteurs.txt",
                 "resultats_anticipation_fine.txt"]
FIG = "analyse/figures/"
FIGS_ANALYST = ["01_entree_vs_fin_de_cycle", "02_achevement_par_region", "03_sorties_en_exces",
                "04_ecoles_et_eleves", "05_contributions_recul_achevement", "06_garcons_filles", "07_prevision"]
FIGS_SCIENTIST = ["09_prevision_alerte", "10_hypothese_insecurite_pauvrete", "11_ml_regression",
                  "13_prevision_ecoles_ouvertes", "14_projection_cohortes"]

# (step, role, description, source or builder, what it holds, produced by)
MANIFEST = [
    ("01", "engineer", "presco-brut", "data/raw/Presco.txt", "Fichier du challenge, tel que reçu (21 tableaux, 13 régions, 2015/16-2024/25)", "Organisateurs (DGESS)"),
    ("01", "engineer", "sources-donnees", "docs/sources_donnees.csv", "Liste des sources : producteur, publication, année, adresse, licence, usage, et si le brut est déposé", "Équipe"),
    ("01", "engineer", "limites-igb-2025", "data/raw/externe/hdx_cod_ab/bfa_admin_boundaries.xlsx", "Limites administratives IGB v03 (2025) : codes et noms anciens et nouveaux", "IGB / OCHA (HDX), CC BY-IGO"),
    ("01", "engineer", "population-provinces-2024", "data/raw/externe/hdx_cod_ps/bfa_admpop_adm2_2024.csv", "Population 2024 par province, sexe et âge (projections)", "INSD / UNFPA (HDX), CC BY-IGO"),
    ("01", "engineer", "cadre-harmonise-provinces", "data/raw/externe/hdx_cadre_harmonise/cadre_harmonise_caf_ipc_mars26.xlsx", "Cadre Harmonisé : population par phase d'insécurité alimentaire, par province, 2014-2024", "CILSS / RPCA (HDX), CC BY"),
    ("01", "engineer", "deplaces-conasur-2022", "data/raw/externe/hdx_pdi_conasur/situation_pdi_31122022.xlsx", "Déplacés internes enregistrés au 31/12/2022, par région et commune d'accueil", "CONASUR (HDX), CC BY"),
    ("02", "engineer", "presco-propre", "data/tidy/presco_tidy.csv", "Données du challenge en tableau long : 6 621 valeurs, 11 colonnes, aucune valeur modifiée", "lecture-presco"),
    ("02", "engineer", "journal-nettoyage", "docs/journal_nettoyage.md", "Ce qui a été corrigé, signalé ou gardé, et pourquoi", "Équipe"),
    ("02", "engineer", "controles-qualite", "analyse/controles_qualite.txt", "Résultat des 8 contrôles de cohérence (totaux, parité, doublons, sauts, valeurs hors norme)", "controles-presco"),
    ("02", "engineer", "lecture-presco", "scripts/parse_presco.py", "Script de lecture du fichier du challenge (nom d'origine : parse_presco.py)", "Équipe"),
    ("02", "engineer", "controles-presco", "scripts/check_presco.py", "Script des contrôles de cohérence (check_presco.py)", "Équipe"),
    ("02", "engineer", "preparation-sources-externes", "scripts/prepare_facteurs.py", "Script de nettoyage de la faim, de l'EDS et des déplacés (prepare_facteurs.py)", "Équipe"),
    ("02", "engineer", "pauvrete-ehcvm-2021-regions", "data/externe_propre/pauvrete_ehcvm_2021_regions.csv", "Pauvreté par région, EHCVM 2021, tableau 3-2", "INSD, recopié par l'équipe"),
    ("02", "engineer", "faim-cadre-harmonise-regions", "data/externe_propre/faim_cadre_harmonise_region_annee.csv", "Part de la population en phase 3 ou plus, par région et année scolaire", "preparation-sources-externes"),
    ("02", "engineer", "eds-2021-regions", "data/externe_propre/eds_2021_regions.csv", "Femmes sans instruction, grossesses précoces, parité de fréquentation, par région (EDS 2021)", "preparation-sources-externes"),
    ("02", "engineer", "deplaces-conasur-2022-regions", "data/externe_propre/pdi_conasur_2022_regions.csv", "Déplacés accueillis par région, en nombre et en % de la population", "preparation-sources-externes"),
    ("03", "architect", "dictionnaire-variables", "docs/dictionnaire_variables.md", "Dictionnaire des variables de toutes les tables", "Équipe"),
    ("03", "architect", "parcours-donnees", "docs/parcours_donnees.md", "Schéma des données, parcours étape par étape, stockage, accès, contrôles", "Équipe"),
    ("03", "architect", "correspondance-regions-13-17", "data/ref/regions_13_17.csv", "Correspondance officielle 13 anciennes ↔ 17 nouvelles régions", "referentiel-officiel"),
    ("03", "architect", "correspondance-provinces-45-47", "data/ref/provinces_45_47.csv", "Correspondance officielle 45 anciennes ↔ 47 nouvelles provinces", "referentiel-officiel"),
    ("03", "architect", "carte-13-regions", "data/ref/regions_13.geojson", "Contours des 13 anciennes régions, reconstitués depuis les 17 nouvelles", "carte-13-regions (script)"),
    ("03", "architect", "referentiel-officiel", "scripts/referentiel_officiel.py", "Script de la correspondance officielle (referentiel_officiel.py)", "Équipe"),
    ("03", "architect", "regions-2025", "scripts/regions_2025.py", "Script qui ajoute les noms de 2025 (regions_2025.py)", "Équipe"),
    ("03", "architect", "carte-13-regions", "scripts/carte_13_regions.py", "Script du fond de carte des 13 régions et de la carte de l'achèvement (carte_13_regions.py)", "Équipe"),
    ("03", "engineer", "presco-propre-regions-2025", "data/tidy/presco_tidy_regions2025.csv", "Données propres avec les noms et codes de 2025", "regions-2025"),
    ("03", "engineer", "panel-region-annee", "analyse/panel_region_annee.csv", "Une ligne par région et par année : effectifs, taux, écoles, sorties apparentes, variations", "analyse-pistes (04)"),
    ("03", "engineer", "panel-region-annee-2025", "analyse/panel_region_annee_2025.csv", "Le même panel, avec les noms de 2025", "regions-2025"),
    ("03", "engineer", "violence-acled-region-annee", "analyse/acled_region_annee.csv", "Incidents et morts par région et par année scolaire (agrégat d'ACLED)", "violence-acled (04)"),
    ("03", "engineer", "signaux-violence-region-annee", "analyse/P16_signaux_region_annee.csv", "Signaux fins par région et par année : étendue, juillet-septembre, rentrée, civils, voisins", "anticipation-fine (04)"),
    ("04", "analyst", "indicateurs-descriptifs", ("workbook", WB_ANALYST), "Classeur des indicateurs descriptifs (A à G, P1 à P7), une feuille par tableau", "analyse-descriptive, analyse-pistes"),
    ("04", "analyst", "synthese-donnees", "analyse/synthese_donnees.md", "Ce que disent les données du challenge", "Équipe"),
    ("04", "analyst", "pistes-defi1", "analyse/pistes_defi1.md", "Les pistes d'analyse et leurs résultats", "Équipe"),
    ("04", "analyst", "figures-analyse", ("figures", FIGS_ANALYST), "Figures 01 à 07 : entrée et fin de cycle, achèvement, sorties, écoles, contributions, genre, prévision", "figures-pistes"),
    ("04", "analyst", "sorties-brutes-analyse", ("concat", RAW_ANALYST), "Sorties brutes des scripts d'analyse", "analyse-descriptive, analyse-pistes"),
    ("04", "analyst", "analyse-descriptive", "scripts/analyse_presco.py", "Script d'analyse descriptive (analyse_presco.py)", "Équipe"),
    ("04", "analyst", "analyse-pistes", "scripts/analyse_pistes.py", "Script des pistes P1 à P7 ; construit aussi le panel (analyse_pistes.py)", "Équipe"),
    ("04", "analyst", "figures-pistes", "scripts/figures_pistes.py", "Script des figures 01 à 07 (figures_pistes.py)", "Équipe"),
    ("04", "scientist", "resultats-modeles", ("workbook", WB_SCIENTIST), "Classeur des résultats des modèles (P8 à P16), une feuille par tableau", "scripts du Data Scientist"),
    ("04", "scientist", "journal-decisions", "docs/journal_decisions.md", "Les 17 décisions : ce qui a été décidé, pourquoi, et ce qu'on en écarte", "Équipe"),
    ("04", "scientist", "anticipation-et-hypothese", "analyse/anticipation_et_hypothese.md", "Prévision prudente, alerte d'escalade, test de l'hypothèse", "Équipe"),
    ("04", "scientist", "apprentissage-automatique", "analyse/machine_learning.md", "Apprentissage automatique contre règles simples", "Équipe"),
    ("04", "scientist", "autres-approches-prevision", "analyse/autres_approches_prevision.md", "Écoles ouvertes à la rentrée ; filière des cohortes", "Équipe"),
    ("04", "scientist", "facteurs-decrochage", "analyse/facteurs_decrochage.md", "Les causes autres que l'insécurité, et leur valeur pour prévoir", "Équipe"),
    ("04", "scientist", "figures-modeles", ("figures", FIGS_SCIENTIST), "Figures 09, 10, 11, 13, 14 : prévision, hypothèse, apprentissage automatique, écoles ouvertes, cohortes", "figures-prevision, figures-ml, figures-solution"),
    ("04", "scientist", "sorties-brutes-modeles", ("concat", RAW_SCIENTIST), "Sorties brutes de tous les modèles, dans l'ordre", "scripts du Data Scientist"),
    ("04", "scientist", "violence-acled", "scripts/acled_anticipation.py", "Agrégat ACLED et test de la violence pour prévoir (acled_anticipation.py)", "Équipe"),
    ("04", "scientist", "prevision-hypothese", "scripts/prevision_hypothese.py", "Prévision 2025/26, alerte, test de l'hypothèse (prevision_hypothese.py)", "Équipe"),
    ("04", "scientist", "apprentissage-automatique", "scripts/machine_learning.py", "Ridge, forêt aléatoire, gradient boosting, logistique (machine_learning.py)", "Équipe"),
    ("04", "scientist", "approches-prevision", "scripts/approches_prevision.py", "Écoles ouvertes et filière des cohortes (approches_prevision.py)", "Équipe"),
    ("04", "scientist", "solution-prevision", "scripts/solution_prevision.py", "Où, combien, matrice de priorité (solution_prevision.py)", "Équipe"),
    ("04", "scientist", "facteurs-decrochage", "scripts/facteurs_decrochage.py", "Facteurs autres que l'insécurité (facteurs_decrochage.py)", "Équipe"),
    ("04", "scientist", "prevision-facteurs", "scripts/prevision_facteurs.py", "Les facteurs aident-ils à prévoir ? (prevision_facteurs.py)", "Équipe"),
    ("04", "scientist", "anticipation-fine", "scripts/anticipation_fine.py", "Signaux fins de violence et calendrier d'alerte (anticipation_fine.py)", "Équipe"),
    ("04", "scientist", "eloignement-ecoles-methode", "scripts/eloignement_ecoles.py", "Méthode prête pour mesurer l'éloignement des écoles (OpenStreetMap, WorldPop), testée sur données simulées, non appliquée", "Équipe"),
    ("04", "scientist", "figures-prevision", "scripts/figures_prevision.py", "Script des figures 09 et 10 (figures_prevision.py)", "Équipe"),
    ("04", "scientist", "figures-ml", "scripts/figures_ml.py", "Script des figures 11 et 12 (figures_ml.py)", "Équipe"),
    ("04", "scientist", "environnement-python", "requirements.txt", "Versions des bibliothèques Python utilisées", "Équipe"),
    ("05", "analyst", "fiches-regionales-13", "analyse/fiches_regionales_13.pdf", "Une fiche d'une page par région, pour un directeur régional", "fiches-regionales"),
    ("05", "analyst", "carte-achevement-profils", FIG + "08_carte_profils_achevement.png", "Carte : taux d'achèvement 2024/25 et profils des régions", "carte-13-regions (03)"),
    ("05", "analyst", "matrice-priorite-2026-27", FIG + "15_matrice_priorite_2026_27.png", "Où agir en premier à la rentrée 2026/27", "figures-solution"),
    ("05", "analyst", "matrice-priorite-2026-27", "analyse/P13_matrice_priorite_2026_27.csv", "Matrice de priorité 2026/27 : taux d'achèvement, probabilité de baisse, enfants hors CM2, priorité", "solution-prevision (04)"),
    ("05", "analyst", "profil-facteurs-regions", FIG + "16_profil_facteurs.png", "Profil des facteurs de chaque région", "figures-solution"),
    ("05", "analyst", "profil-facteurs-regions", "analyse/P14_profil_facteurs.csv", "Valeurs et niveaux d'exposition par facteur et par région", "facteurs-decrochage (04)"),
    ("05", "analyst", "fiches-regionales", "scripts/fiches_regionales.py", "Script des fiches régionales (fiches_regionales.py)", "Équipe"),
    ("05", "analyst", "figures-solution", "scripts/figures_approches.py", "Script des figures 13 à 17 (figures_approches.py)", "Équipe"),
    ("05", "scientist", "solution-anticipation", "analyse/solution_anticipation.md", "La solution : où agir, où le risque monte, combien d'enfants, calendrier d'alerte", "Équipe"),
    ("05", "scientist", "alertes-calendrier", "analyse/P16_alertes_calendrier.csv", "Alerte de janvier 2025/26 et alerte de septembre 2026/27, par région", "anticipation-fine (04)"),
    ("05", "scientist", "calendrier-alerte", FIG + "17_calendrier_alerte.png", "Plus l'information arrive, mieux on anticipe", "figures-solution"),
    ("05", "scientist", "risque-2026-27", FIG + "12_risque_2026_27.png", "Probabilité de baisse des effectifs en 2026/27, par région", "figures-ml (04)"),
    ("05", "scientist", "prevision-2025-26", "analyse/P9_prevision_2025_26_alerte.csv", "Prévision 2025/26 du taux d'achèvement avec fourchette, enfants hors CM2, alertes", "prevision-hypothese (04)"),
    ("05", "scientist", "projet-complet-relancable", ("archive", None), "Le projet complet, pour tout relancer (code, données propres, résultats, documentation ; données brutes dans 01_collecte)", "Équipe"),
]


def name(step, role, desc, ext):
    n = f"{TEAM}_{STEPS[step][1]}_{DEFI}_{role}_{desc}_v{VERSION}.{ext}"
    assert NAME_RE.match(n), n
    return n


def build(src, dest):
    if isinstance(src, str):
        shutil.copy2(src, dest)
        return
    kind, arg = src
    if kind == "workbook":
        with pd.ExcelWriter(dest) as xw:
            pd.DataFrame(arg, columns=["feuille", "contenu"]).to_excel(xw, sheet_name="lisez-moi", index=False)
            for stem, _ in arg:
                assert len(stem) <= 31, stem
                pd.read_csv(f"analyse/{stem}.csv").to_excel(xw, sheet_name=stem, index=False)
    elif kind == "figures":
        imgs = [Image.open(f"{FIG}{f}.png").convert("RGB") for f in arg]
        imgs[0].save(dest, save_all=True, append_images=imgs[1:], resolution=200)
    elif kind == "concat":
        with open(dest, "w") as out:
            for f in arg:
                out.write(f"\n{'=' * 100}\n=== analyse/{f}\n{'=' * 100}\n")
                out.write(Path("analyse", f).read_text())
    elif kind == "archive":
        subprocess.run(["git", "archive", "--format=zip", "-o", str(dest), "HEAD"], check=True)


def ext_of(src):
    if isinstance(src, str):
        return Path(src).suffix.lstrip(".")
    return {"workbook": "xlsx", "figures": "pdf", "concat": "txt", "archive": "zip"}[src[0]]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    rows = []
    for step, role, desc, src, what, by in MANIFEST:
        folder = OUT / STEPS[step][0]
        folder.mkdir(parents=True, exist_ok=True)
        n = name(step, role, desc, ext_of(src))
        assert not (folder / n).exists(), f"nom en double : {n}"
        build(src, folder / n)
        rows.append({"step": step, "role": role, "file": n, "what": what, "by": by,
                     "src": src if isinstance(src, str) else src[0], "size": (folder / n).stat().st_size})
    files = pd.DataFrame(rows)
    sources = {p.stem.replace(".SOURCE", ""): p.read_text().strip() for p in Path("data/externe_propre").glob("*.SOURCE.txt")}
    for step, (folder, _, title) in STEPS.items():
        f = files[files.step == step]
        lines = [f"LISEZ-MOI - Équipe {TEAM} - Défi 1 - Étape {step} : {title}", "",
                 f"Ce dépôt contient {len(f)} fichiers. Nom : EQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN.", ""]
        for role in ROLES:
            fr_ = f[f.role == role]
            if fr_.empty:
                continue
            lines.append(f"--- {ROLES[role]} ---")
            for _, r in fr_.iterrows():
                lines += [f"* {r.file}", f"  {r.what}", f"  Produit par : {r.by}", ""]
        if step == "02":
            lines += ["--- Sources des fichiers externes nettoyés ---"] + [f"* {k} : {v.lstrip('# ')}" for k, v in sorted(sources.items())] + [""]
        if step == "01":
            lines += ["Non déposés, et pourquoi : voir la colonne « brut_depose » de la liste des sources",
                      "(ACLED : redistribution interdite par ses conditions ; EDS : conditions du DHS Program ;",
                      "limites détaillées : 110 Mo, remplacées par la carte des 13 régions en 03_transformation).", ""]
        (OUT / folder / "LISEZ-MOI.txt").write_text("\n".join(lines))
    root = [f"LISEZ-MOI - Équipe {TEAM} - Data Challenge Burkina, édition Éducation 2026", "",
            "Défi 1 : cartographie et anticipation du risque de décrochage scolaire par région.", "",
            "Nom des fichiers : EQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN (un fichier = une étape).", "",
            "Les dépôts :"]
    for step, (folder, _, title) in STEPS.items():
        f = files[files.step == step]
        root.append(f"* {folder} : {title} - {len(f)} fichiers ({', '.join(ROLES[r] for r in ROLES if r in set(f.role))})")
    root += ["", "Par où commencer :",
             f"* 05_interpretation : {TEAM}_05-interpretation_{DEFI}_scientist_solution-anticipation_v{VERSION}.md (la solution)",
             f"  et {TEAM}_05-interpretation_{DEFI}_analyst_fiches-regionales-13_v{VERSION}.pdf (une page par région).",
             f"* 04_analyse : {TEAM}_04-analyse_{DEFI}_scientist_journal-decisions_v{VERSION}.md (chaque choix et ses limites).", "",
             "Pour tout relancer : décompresser le projet complet (05_interpretation), placer le fichier du challenge",
             "(01_collecte, presco-brut) sous data/raw/Presco.txt, puis suivre l'ordre des commandes du README.md.",
             "Les scripts sont aussi déposés un par un, à l'étape où ils servent ; leur nom d'origine est indiqué.", "",
             "Aucune donnée personnelle. Toutes les sources sont citées (01_collecte, liste des sources)."]
    (OUT / "LISEZ-MOI.txt").write_text("\n".join(root))
    # Zip outside the folder being zipped, then move it in; the inventory is written last, outside the zip.
    tmp = shutil.make_archive(f"{TEAM}_{DEFI}_depots_v{VERSION}", "zip", root_dir=OUT, base_dir=".")
    z = shutil.move(tmp, OUT / Path(tmp).name)
    files.to_csv(OUT / "inventaire.csv", index=False)
    print(files.groupby(["step", "role"]).size().to_string())
    print(f"{len(files)} fichiers, {files['size'].sum() / 1e6:.1f} Mo ; archive : {z}")


if __name__ == "__main__":
    main()

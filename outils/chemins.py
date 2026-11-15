"""Where every file of the project lives: TEAM_STEP_CHALLENGE_ROLE_description_vN, one entry per file."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "01_collecte" / "brut"

# Logical name (the file's original name) -> its place in the step folders.
FILES = {
    "A_tendances_nationales.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_a-tendances-nationales_v1.csv",
    "B_choc_et_reprise_par_region.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_b-choc-et-reprise-par-region_v1.csv",
    "C_sorties_apparentes_par_region.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_c-sorties-apparentes-par-region_v1.csv",
    "D_passages_apparents_par_niveau.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_d-passages-apparents-par-niveau_v1.csv",
    "D_survie_apparente_CP1_CM2.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_d-survie-apparente-cp1-cm2_v1.csv",
    "E_parite_achevement.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_e-parite-achevement_v1.csv",
    "G_persistance_TAP.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_g-persistance-tap_v1.csv",
    "P10_attaques_education_region_annee.csv": "03_transformation/Biiga_03-transformation_D1_engineer_attaques-education-region-annee_v1.csv",
    "P10_hypothese_transversale.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p10-hypothese-transversale_v1.csv",
    "P11_importance.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p11-importance_v1.csv",
    "P11_ml_classification.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p11-ml-classification_v1.csv",
    "P11_ml_regression.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p11-ml-regression_v1.csv",
    "P11_probabilites_alerte.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p11-probabilites-alerte_v1.csv",
    "P12_cohortes_national.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p12-cohortes-national_v1.csv",
    "P12_filiere_fourchette.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p12-filiere-fourchette_v1.csv",
    "P12_filiere_un_an.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p12-filiere-un-an_v1.csv",
    "P12_nowcast_ecoles.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p12-nowcast-ecoles_v1.csv",
    "P12_projection_CM2.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p12-projection-cm2_v1.csv",
    "P12_scenario_cohortes_CP1.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p12-scenario-cohortes-cp1_v1.csv",
    "P13_TAP_modeles.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p13-tap-modeles_v1.csv",
    "P13_effectifs_modeles.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p13-effectifs-modeles_v1.csv",
    "P13_effectifs_predictions.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p13-effectifs-predictions_v1.csv",
    "P13_matrice_priorite_2026_27.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p13-matrice-priorite-2026-27_v1.csv",
    "P13_matrice_rejouee.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p13-matrice-rejouee_v1.csv",
    "P13_stabilite_classement.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p13-stabilite-classement_v1.csv",
    "P14_facteurs_correlations.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p14-facteurs-correlations_v1.csv",
    "P14_faim_panel.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p14-faim-panel_v1.csv",
    "P14_faim_regions_calmes.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p14-faim-regions-calmes_v1.csv",
    "P14_profil_facteurs.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p14-profil-facteurs_v1.csv",
    "P15_TAP_trois_ans.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p15-tap-trois-ans_v1.csv",
    "P15_TAP_un_an.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p15-tap-un-an_v1.csv",
    "P15_alerte_facteurs.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p15-alerte-facteurs_v1.csv",
    "P16_alertes_calendrier.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p16-alertes-calendrier_v1.csv",
    "P16_signaux_fins.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p16-signaux-fins_v1.csv",
    "P16_signaux_region_annee.csv": "03_transformation/Biiga_03-transformation_D1_engineer_signaux-violence-region-annee_v1.csv",
    "P17_formule_risque.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p17-formule-risque_v1.csv",
    "P18_score_global_2026_27.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p18-score-global-2026-27_v1.csv",
    "P18_score_global_rejoue.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p18-score-global-rejoue_v1.csv",
    "P18_score_global_trajectoire.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p18-score-global-trajectoire_v1.csv",
    "P19_facteur_dominant.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p19-facteur-dominant_v1.csv",
    "P1_sorties_excedentaires.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p1-sorties-excedentaires_v1.csv",
    "P2_typologie_regions.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p2-typologie-regions_v1.csv",
    "P3_contributions_recul_TAP.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p3-contributions-recul-tap_v1.csv",
    "P4_entree_sortie_national.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p4-entree-sortie-national_v1.csv",
    "P5_genre.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p5-genre_v1.csv",
    "P6_prevision.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p6-prevision_v1.csv",
    "P7_scenarios_reouverture.csv": "04_analyse/resultats/Biiga_04-analyse_D1_analyst_p7-scenarios-reouverture_v1.csv",
    "P8_anticipation_acled.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p8-anticipation-acled_v1.csv",
    "P9_prevision_2025_26_alerte.csv": "04_analyse/resultats/Biiga_04-analyse_D1_scientist_p9-prevision-2025-26-alerte_v1.csv",
    "acled_region_annee.csv": "03_transformation/Biiga_03-transformation_D1_engineer_violence-acled-region-annee_v1.csv",
    "anticipation_et_hypothese.md": "04_analyse/Biiga_04-analyse_D1_scientist_anticipation-et-hypothese_v1.md",
    "autres_approches_prevision.md": "04_analyse/Biiga_04-analyse_D1_scientist_autres-approches-prevision_v1.md",
    "controles_qualite.txt": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_controles-qualite_v1.txt",
    "facteurs_decrochage.md": "04_analyse/Biiga_04-analyse_D1_scientist_facteurs-decrochage_v1.md",
    "fiche_bankuisourou.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-bankuisourou_v1.pdf",
    "fiche_bankuisourou.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-bankuisourou_v1.png",
    "fiche_djoro.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-djoro_v1.pdf",
    "fiche_djoro.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-djoro_v1.png",
    "fiche_goulmousirbatapoa.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-goulmousirbatapoa_v1.pdf",
    "fiche_goulmousirbatapoa.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-goulmousirbatapoa_v1.png",
    "fiche_guiriko.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-guiriko_v1.pdf",
    "fiche_guiriko.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-guiriko_v1.png",
    "fiche_kadiogo.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-kadiogo_v1.pdf",
    "fiche_kadiogo.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-kadiogo_v1.png",
    "fiche_koulse.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-koulse_v1.pdf",
    "fiche_koulse.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-koulse_v1.png",
    "fiche_liptakosoum.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-liptakosoum_v1.pdf",
    "fiche_liptakosoum.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-liptakosoum_v1.png",
    "fiche_nakambe.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-nakambe_v1.pdf",
    "fiche_nakambe.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-nakambe_v1.png",
    "fiche_nando.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-nando_v1.pdf",
    "fiche_nando.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-nando_v1.png",
    "fiche_nazinon.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-nazinon_v1.pdf",
    "fiche_nazinon.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-nazinon_v1.png",
    "fiche_oubri.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-oubri_v1.pdf",
    "fiche_oubri.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-oubri_v1.png",
    "fiche_tannounyan.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-tannounyan_v1.pdf",
    "fiche_tannounyan.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-tannounyan_v1.png",
    "fiche_yaadga.pdf": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-yaadga_v1.pdf",
    "fiche_yaadga.png": "05_interpretation/fiches/Biiga_05-interpretation_D1_analyst_fiche-yaadga_v1.png",
    "fiches_regionales_13.pdf": "05_interpretation/Biiga_05-interpretation_D1_analyst_fiches-regionales-13_v1.pdf",
    "01_entree_vs_fin_de_cycle.png": "04_analyse/figures/Biiga_04-analyse_D1_analyst_figure-01-entree-vs-fin-de-cycle_v1.png",
    "02_achevement_par_region.png": "04_analyse/figures/Biiga_04-analyse_D1_analyst_figure-02-achevement-par-region_v1.png",
    "03_sorties_en_exces.png": "04_analyse/figures/Biiga_04-analyse_D1_analyst_figure-03-sorties-en-exces_v1.png",
    "04_ecoles_et_eleves.png": "04_analyse/figures/Biiga_04-analyse_D1_analyst_figure-04-ecoles-et-eleves_v1.png",
    "05_contributions_recul_achevement.png": "04_analyse/figures/Biiga_04-analyse_D1_analyst_figure-05-contributions-recul-achevement_v1.png",
    "06_garcons_filles.png": "04_analyse/figures/Biiga_04-analyse_D1_analyst_figure-06-garcons-filles_v1.png",
    "07_prevision.png": "04_analyse/figures/Biiga_04-analyse_D1_analyst_figure-07-prevision_v1.png",
    "08_carte_profils_achevement.png": "03_transformation/figures/Biiga_03-transformation_D1_architect_figure-08-carte-profils-achevement_v1.png",
    "09_prevision_alerte.png": "04_analyse/figures/Biiga_04-analyse_D1_scientist_figure-09-prevision-alerte_v1.png",
    "10_hypothese_insecurite_pauvrete.png": "04_analyse/figures/Biiga_04-analyse_D1_scientist_figure-10-hypothese-insecurite-pauvrete_v1.png",
    "11_ml_regression.png": "04_analyse/figures/Biiga_04-analyse_D1_scientist_figure-11-ml-regression_v1.png",
    "12_risque_2026_27.png": "04_analyse/figures/Biiga_04-analyse_D1_scientist_figure-12-risque-2026-27_v1.png",
    "13_prevision_ecoles_ouvertes.png": "05_interpretation/figures/Biiga_05-interpretation_D1_analyst_figure-13-prevision-ecoles-ouvertes_v1.png",
    "14_projection_cohortes.png": "05_interpretation/figures/Biiga_05-interpretation_D1_analyst_figure-14-projection-cohortes_v1.png",
    "15_matrice_priorite_2026_27.png": "05_interpretation/figures/Biiga_05-interpretation_D1_analyst_figure-15-matrice-priorite-2026-27_v1.png",
    "16_profil_facteurs.png": "05_interpretation/figures/Biiga_05-interpretation_D1_analyst_figure-16-profil-facteurs_v1.png",
    "17_calendrier_alerte.png": "05_interpretation/figures/Biiga_05-interpretation_D1_analyst_figure-17-calendrier-alerte_v1.png",
    "formule_risque.md": "04_analyse/Biiga_04-analyse_D1_scientist_formule-risque_v1.md",
    "machine_learning.md": "04_analyse/Biiga_04-analyse_D1_scientist_apprentissage-automatique_v1.md",
    "panel_region_annee.csv": "03_transformation/Biiga_03-transformation_D1_engineer_panel-region-annee_v1.csv",
    "panel_region_annee_2025.csv": "03_transformation/Biiga_03-transformation_D1_engineer_panel-region-annee-2025_v1.csv",
    "pistes_defi1.md": "04_analyse/Biiga_04-analyse_D1_analyst_pistes-defi1_v1.md",
    "solution_anticipation.md": "05_interpretation/Biiga_05-interpretation_D1_scientist_solution-anticipation_v1.md",
    "synthese_donnees.md": "04_analyse/Biiga_04-analyse_D1_analyst_synthese-donnees_v1.md",
    "eds_2021_regions.SOURCE.txt": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_eds-2021-regions-source_v1.txt",
    "eds_2021_regions.csv": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_eds-2021-regions_v1.csv",
    "faim_cadre_harmonise_region_annee.SOURCE.txt": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_faim-cadre-harmonise-region-annee-source_v1.txt",
    "faim_cadre_harmonise_region_annee.csv": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_faim-cadre-harmonise-region-annee_v1.csv",
    "pauvrete_ehcvm_2021_regions.SOURCE.txt": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_pauvrete-ehcvm-2021-regions-source_v1.txt",
    "pauvrete_ehcvm_2021_regions.csv": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_pauvrete-ehcvm-2021-regions_v1.csv",
    "pdi_conasur_2022_regions.SOURCE.txt": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_pdi-conasur-2022-regions-source_v1.txt",
    "pdi_conasur_2022_regions.csv": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_pdi-conasur-2022-regions_v1.csv",
    "provinces_45_47.csv": "03_transformation/Biiga_03-transformation_D1_architect_correspondance-provinces-45-47_v1.csv",
    "regions_13.geojson": "03_transformation/Biiga_03-transformation_D1_architect_carte-13-regions_v1.geojson",
    "regions_13_17.csv": "03_transformation/Biiga_03-transformation_D1_architect_correspondance-regions-13-17_v1.csv",
    "priorites_2026_27.csv": "05_interpretation/Biiga_05-interpretation_D1_analyst_priorites-2026-27_v1.csv",
    "presco_tidy.csv": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_donnees-challenge-propres_v1.csv",
    "presco_tidy_regions2025.csv": "03_transformation/Biiga_03-transformation_D1_engineer_donnees-challenge-regions-2025_v1.csv",
    "01_audit_donnees.md": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_audit-donnees_v1.md",
    "dictionnaire_variables.md": "03_transformation/Biiga_03-transformation_D1_architect_dictionnaire-variables_v1.md",
    "journal_decisions.md": "04_analyse/Biiga_04-analyse_D1_scientist_journal-decisions_v1.md",
    "journal_nettoyage.md": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_journal-nettoyage_v1.md",
    "note_intention_defi1.md": "01_collecte/Biiga_01-collecte_D1_analyst_note-intention_v1.md",
    "parcours_donnees.md": "03_transformation/Biiga_03-transformation_D1_architect_parcours-donnees_v1.md",
    "sources_donnees.csv": "01_collecte/Biiga_01-collecte_D1_engineer_sources-donnees_v1.csv",
    "02_nettoyage.ipynb": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_cahier-nettoyage_v1.ipynb",
    "03_transformation.ipynb": "03_transformation/Biiga_03-transformation_D1_architect_cahier-transformation_v1.ipynb",
    "04a_analyse_descriptive.ipynb": "04_analyse/Biiga_04-analyse_D1_analyst_cahier-analyse-descriptive_v1.ipynb",
    "04b_modeles.ipynb": "04_analyse/Biiga_04-analyse_D1_scientist_cahier-modeles_v1.ipynb",
    "05_interpretation.ipynb": "05_interpretation/Biiga_05-interpretation_D1_analyst_cahier-interpretation_v1.ipynb",
    "app_bureau.png": "05_interpretation/captures/Biiga_05-interpretation_D1_analyst_capture-bureau_v1.png",
    "app_carte.png": "05_interpretation/captures/Biiga_05-interpretation_D1_analyst_capture-carte_v1.png",
    "app_hors_ligne.png": "05_interpretation/captures/Biiga_05-interpretation_D1_analyst_capture-hors-ligne_v1.png",
    "app_region_action.png": "05_interpretation/captures/Biiga_05-interpretation_D1_analyst_capture-region-action_v1.png",
    "app_region_haut.png": "05_interpretation/captures/Biiga_05-interpretation_D1_analyst_capture-region-haut_v1.png",
    "app_region_score.png": "05_interpretation/captures/Biiga_05-interpretation_D1_analyst_capture-region-score_v1.png",
    "rapport.tex": "05_interpretation/Biiga_05-interpretation_D1_analyst_rapport_v1.tex",
    "rapport.pdf": "05_interpretation/Biiga_05-interpretation_D1_analyst_rapport_v1.pdf"
}

# The project's scripts, by module name -> file.
MODULES = {
    "acled_anticipation": "03_transformation/Biiga_03-transformation_D1_engineer_script-violence-acled_v1.py",
    "analyse_pistes": "03_transformation/Biiga_03-transformation_D1_engineer_script-panel-et-pistes_v1.py",
    "analyse_presco": "04_analyse/Biiga_04-analyse_D1_analyst_script-analyse-descriptive_v1.py",
    "anticipation_fine": "04_analyse/Biiga_04-analyse_D1_scientist_script-anticipation-fine_v1.py",
    "approches_prevision": "04_analyse/Biiga_04-analyse_D1_scientist_script-approches-prevision_v1.py",
    "carte_13_regions": "03_transformation/Biiga_03-transformation_D1_architect_script-carte-13-regions_v1.py",
    "check_presco": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-controles-coherence_v1.py",
    "eloignement_ecoles": "04_analyse/Biiga_04-analyse_D1_scientist_script-eloignement-ecoles_v1.py",
    "export_tableau_de_bord": "05_interpretation/Biiga_05-interpretation_D1_analyst_script-export-tableau-de-bord_v1.py",
    "facteur_dominant": "04_analyse/Biiga_04-analyse_D1_scientist_script-facteur-dominant_v1.py",
    "facteurs_decrochage": "04_analyse/Biiga_04-analyse_D1_scientist_script-facteurs-decrochage_v1.py",
    "fiches_regionales": "05_interpretation/Biiga_05-interpretation_D1_analyst_script-fiches-regionales_v1.py",
    "figures_approches": "05_interpretation/Biiga_05-interpretation_D1_analyst_script-figures-solution_v1.py",
    "figures_ml": "04_analyse/Biiga_04-analyse_D1_scientist_script-figures-apprentissage_v1.py",
    "figures_pistes": "04_analyse/Biiga_04-analyse_D1_analyst_script-figures-pistes_v1.py",
    "figures_prevision": "04_analyse/Biiga_04-analyse_D1_scientist_script-figures-prevision_v1.py",
    "formule_risque": "04_analyse/Biiga_04-analyse_D1_scientist_script-formule-risque_v1.py",
    "machine_learning": "04_analyse/Biiga_04-analyse_D1_scientist_script-apprentissage-automatique_v1.py",
    "parse_presco": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-lecture-challenge_v1.py",
    "prepare_facteurs": "02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-sources-externes_v1.py",
    "prevision_facteurs": "04_analyse/Biiga_04-analyse_D1_scientist_script-prevision-facteurs_v1.py",
    "prevision_hypothese": "04_analyse/Biiga_04-analyse_D1_scientist_script-prevision-hypothese_v1.py",
    "referentiel_officiel": "03_transformation/Biiga_03-transformation_D1_architect_script-referentiel-regions_v1.py",
    "regions_2025": "03_transformation/Biiga_03-transformation_D1_architect_script-noms-regions-2025_v1.py",
    "score_global": "04_analyse/Biiga_04-analyse_D1_scientist_script-score-global_v1.py",
    "solution_prevision": "04_analyse/Biiga_04-analyse_D1_scientist_script-solution-prevision_v1.py"
}


def path(key):
    return str(ROOT / FILES[key])


def rel(key):
    """Path from the project root, for messages and command lines."""
    return FILES[key]


def raw(rel=""):
    return str(RAW / rel) + ("/" if rel.endswith("/") else "")


def folder(name):
    return str(ROOT / name)


def fiche(slug, ext):
    return str(ROOT / "05_interpretation" / "fiches" / f"Biiga_05-interpretation_D1_analyst_fiche-{slug}_v1.{ext}")


def module(name):
    """Import a project script by its module name, whatever its file name."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / MODULES[name])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

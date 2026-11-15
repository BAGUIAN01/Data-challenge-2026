# Parcours des données

## Le schéma

Toutes les données se rejoignent sur deux clés :
- **la région** : les 13 anciennes, avec une clé sans accents (`cle`) ;
- **l'année scolaire** : d'octobre à septembre.

La correspondance officielle de l'IGB relie ces 13 régions aux 17 de 2025, pour l'affichage.

```
                      ┌──────────────────────────────┐
                      │  regions_13_17 (IGB 2025)    │  13 anciennes ↔ 17 nouvelles régions
                      └──────────────┬───────────────┘
                                     │ cle
┌───────────────────┐   ┌────────────┴─────────────┐   ┌──────────────────────────────┐
│ presco_tidy       │──▶│ panel_region_annee       │◀──│ acled_region_annee           │
│ (challenge, long) │   │ 13 régions × 10 années   │   │ (violence, année scolaire)   │
└───────────────────┘   └────────────┬─────────────┘   └──────────────────────────────┘
                                     │ cle + annee
        ┌────────────────────────────┼─────────────────────────────┐
        ▼                            ▼                             ▼
  faim (Cadre Harmonisé)   EDS 2010-2021 (fond)          pauvreté 2021, déplacés 2022
  région × année           région × enquête              région
```

## Le parcours, étape par étape

| Étape | Entrée | Script | Sortie |
| --- | --- | --- | --- |
| **1. Collecte** | Fichier du challenge ; sources HDX et INSD | (téléchargements, voir `01_collecte/Biiga_01-collecte_D1_engineer_sources-donnees_v1.csv`) | `01_collecte/brut/` (non versionné) |
| **2. Nettoyage** | `Presco.txt` | `Biiga_02-nettoyage_D1_engineer_script-lecture-challenge_v1.py`, `Biiga_02-nettoyage_D1_engineer_script-controles-coherence_v1.py` | `02_nettoyage/Biiga_02-nettoyage_D1_engineer_donnees-challenge-propres_v1.csv`, `02_nettoyage/Biiga_02-nettoyage_D1_engineer_controles-qualite_v1.txt` |
| | Sources externes brutes | `Biiga_02-nettoyage_D1_engineer_script-sources-externes_v1.py` | `02_nettoyage/*.csv` |
| **3. Transformation** | Limites IGB | `Biiga_03-transformation_D1_architect_script-referentiel-regions_v1.py`, `Biiga_03-transformation_D1_architect_script-noms-regions-2025_v1.py`, `Biiga_03-transformation_D1_architect_script-carte-13-regions_v1.py` | `data/ref/`, fichiers « 2025 », `regions_13.geojson` |
| | `presco_tidy.csv` | `Biiga_03-transformation_D1_engineer_script-panel-et-pistes_v1.py` | `03_transformation/Biiga_03-transformation_D1_engineer_panel-region-annee_v1.csv` |
| | ACLED | `Biiga_03-transformation_D1_engineer_script-violence-acled_v1.py`, `Biiga_04-analyse_D1_scientist_script-anticipation-fine_v1.py` | `03_transformation/Biiga_03-transformation_D1_engineer_violence-acled-region-annee_v1.csv`, `03_transformation/Biiga_03-transformation_D1_engineer_signaux-violence-region-annee_v1.csv` |
| **4. Analyse** | Panel et sources | `Biiga_04-analyse_D1_analyst_script-analyse-descriptive_v1.py`, `Biiga_03-transformation_D1_engineer_script-panel-et-pistes_v1.py`, `Biiga_04-analyse_D1_scientist_script-prevision-hypothese_v1.py`, `Biiga_04-analyse_D1_scientist_script-apprentissage-automatique_v1.py`, `Biiga_04-analyse_D1_scientist_script-approches-prevision_v1.py`, `Biiga_04-analyse_D1_scientist_script-solution-prevision_v1.py`, `Biiga_04-analyse_D1_scientist_script-facteurs-decrochage_v1.py`, `Biiga_04-analyse_D1_scientist_script-prevision-facteurs_v1.py`, `Biiga_04-analyse_D1_scientist_script-anticipation-fine_v1.py` | `analyse/P*.csv`, `analyse/resultats_*.txt`, notes `analyse/*.md` |
| **5. Interprétation** | Résultats | `figures_*.py`, `Biiga_05-interpretation_D1_analyst_script-fiches-regionales_v1.py` | `04_analyse/figures/`, `05_interpretation/fiches/`, `05_interpretation/Biiga_05-interpretation_D1_analyst_fiches-regionales-13_v1.pdf` |
| | Résultats | `Biiga_05-interpretation_D1_analyst_script-export-tableau-de-bord_v1.py` | `dashboard/public/data/tableau_de_bord.json` (jeu de données du tableau de bord, et fiches PDF copiées) |
| **6. Mise en service** | Jeu de données exporté | `dashboard/db/seed.mjs` | Base **Neon** : tables `jeu_donnees`, `region`, `indicateur`, `alerte`, `facteur`, `texte` ; saisies du terrain dans `saisie_ecoles` |

L'ordre exact des commandes est dans le `README.md`.

## Stockage et accès

- **Dépôt de code privé.** On y trouve le code, les données nettoyées, les résultats et la documentation.
- **Données brutes hors du dépôt** (`01_collecte/brut/`, ignoré par git) :
  - les données du challenge sont réservées au concours ;
  - les conditions d'ACLED interdisent de redistribuer ses données.

  `01_collecte/brut/LISEZ-MOI.md` indique où récupérer chaque fichier.
- **Base en ligne : Neon (PostgreSQL).** Une seule version des données est active à la fois. Les saisies du terrain sont gardées d'une version à l'autre, avec une clé (`client_id`) qui empêche les doublons.
- **Base de l'appareil : IndexedDB.** L'application lit toujours d'abord l'appareil, ce qui la rend utilisable sans réseau. Les saisies y attendent le réseau.
- **Aucune donnée personnelle.** Toutes les données sont des agrégats régionaux ou provinciaux.
- **Traçabilité :**
  - chaque source externe nettoyée a son `.SOURCE.txt` ;
  - chaque décision est datée dans `04_analyse/Biiga_04-analyse_D1_scientist_journal-decisions_v1.md` ;
  - chaque correction est dans `02_nettoyage/Biiga_02-nettoyage_D1_engineer_journal-nettoyage_v1.md`.

## Contrôles qui arrêtent la chaîne

Une erreur arrête le script au lieu de passer en silence :
- une cellule non numérique là où on attend un nombre ;
- une région absente de la correspondance ;
- une source externe qui ne couvre pas les 13 régions ;
- une donnée manquante pour une région au moment de calculer une alerte.

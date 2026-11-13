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
| **1. Collecte** | Fichier du challenge ; sources HDX et INSD | (téléchargements, voir `docs/sources_donnees.csv`) | `data/raw/` (non versionné) |
| **2. Nettoyage** | `Presco.txt` | `parse_presco.py`, `check_presco.py` | `data/tidy/presco_tidy.csv`, `analyse/controles_qualite.txt` |
| | Sources externes brutes | `prepare_facteurs.py` | `data/externe_propre/*.csv` |
| **3. Transformation** | Limites IGB | `referentiel_officiel.py`, `regions_2025.py`, `carte_13_regions.py` | `data/ref/`, fichiers « 2025 », `regions_13.geojson` |
| | `presco_tidy.csv` | `analyse_pistes.py` | `analyse/panel_region_annee.csv` |
| | ACLED | `acled_anticipation.py`, `anticipation_fine.py` | `analyse/acled_region_annee.csv`, `analyse/P16_signaux_region_annee.csv` |
| **4. Analyse** | Panel et sources | `analyse_presco.py`, `analyse_pistes.py`, `prevision_hypothese.py`, `machine_learning.py`, `approches_prevision.py`, `solution_prevision.py`, `facteurs_decrochage.py`, `prevision_facteurs.py`, `anticipation_fine.py` | `analyse/P*.csv`, `analyse/resultats_*.txt`, notes `analyse/*.md` |
| **5. Interprétation** | Résultats | `figures_*.py`, `fiches_regionales.py` | `analyse/figures/`, `analyse/fiches/`, `analyse/fiches_regionales_13.pdf` |
| | Résultats | `export_tableau_de_bord.py` | `dashboard/public/data/tableau_de_bord.json` (jeu de données du tableau de bord, et fiches PDF copiées) |
| **6. Mise en service** | Jeu de données exporté | `dashboard/db/seed.mjs` | Base **Neon** : tables `jeu_donnees`, `region`, `indicateur`, `alerte`, `facteur`, `texte` ; saisies du terrain dans `saisie_ecoles` |

L'ordre exact des commandes est dans le `README.md`.

## Stockage et accès

- **Dépôt de code privé.** On y trouve le code, les données nettoyées, les résultats et la documentation.
- **Données brutes hors du dépôt** (`data/raw/`, ignoré par git) :
  - les données du challenge sont réservées au concours ;
  - les conditions d'ACLED interdisent de redistribuer ses données.

  `data/raw/LISEZ-MOI.md` indique où récupérer chaque fichier.
- **Base en ligne : Neon (PostgreSQL).** Une seule version des données est active à la fois. Les saisies du terrain sont gardées d'une version à l'autre, avec une clé (`client_id`) qui empêche les doublons.
- **Base de l'appareil : IndexedDB.** L'application lit toujours d'abord l'appareil, ce qui la rend utilisable sans réseau. Les saisies y attendent le réseau.
- **Aucune donnée personnelle.** Toutes les données sont des agrégats régionaux ou provinciaux.
- **Traçabilité :**
  - chaque source externe nettoyée a son `.SOURCE.txt` ;
  - chaque décision est datée dans `docs/journal_decisions.md` ;
  - chaque correction est dans `docs/journal_nettoyage.md`.

## Contrôles qui arrêtent la chaîne

Une erreur arrête le script au lieu de passer en silence :
- une cellule non numérique là où on attend un nombre ;
- une région absente de la correspondance ;
- une source externe qui ne couvre pas les 13 régions ;
- une donnée manquante pour une région au moment de calculer une alerte.

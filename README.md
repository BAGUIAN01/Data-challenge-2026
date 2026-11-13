# Data-challenge-2026

Data Challenge Burkina, édition Éducation 2026. **Défi 1 : cartographie et anticipation du risque de décrochage scolaire par région.**

## Ce que contient le dépôt

| Dossier | Contenu |
| --- | --- |
| `scripts/` | Le code Python de toutes les étapes : lecture des données, contrôles, analyses, modèles, figures, fiches |
| `analyse/` | Résultats : tableaux (`P1_` à `P16_`), notes d'analyse (`*.md`), sorties brutes (`resultats_*.txt`), figures, fiches régionales |
| `docs/` | Flux de travail, audit des données, journal des décisions (D1 à D17), note d'intention |
| `data/tidy/` | Données du challenge remises en tableau long |
| `data/ref/` | Correspondance 13 / 17 régions et fond de carte des 13 régions |
| `data/externe_propre/` | Sources externes nettoyées, chacune avec sa source |
| `data/raw/` | Données brutes, **non versionnées** : voir `data/raw/LISEZ-MOI.md` |

## Où lire les résultats

1. `analyse/solution_anticipation.md` : la solution (où agir, où le risque monte, combien d'enfants, calendrier d'alerte).
2. `analyse/facteurs_decrochage.md` : les causes autres que l'insécurité.
3. `analyse/autres_approches_prevision.md` et `analyse/machine_learning.md` : ce qui prévoit et ce qui ne prévoit pas.
4. `docs/journal_decisions.md` : chaque décision, sa raison et ses limites.
5. `analyse/fiches_regionales_13.pdf` : une page par région.

## Recalculer

Les commandes se lancent depuis la racine du dépôt (Python 3.13) :

```bash
pip install -r requirements.txt
```

Placer ensuite les données brutes dans `data/raw/` (voir `data/raw/LISEZ-MOI.md`), puis lancer les étapes dans cet ordre.

**1. Données du challenge**

```bash
python scripts/parse_presco.py data/raw/Presco.txt data/tidy/presco_tidy.csv
python scripts/check_presco.py data/tidy/presco_tidy.csv
python scripts/analyse_presco.py data/tidy/presco_tidy.csv analyse/
```

**2. Référentiel des régions**

```bash
python scripts/referentiel_officiel.py data/raw/externe/hdx_cod_ab/bfa_admin_boundaries.xlsx data/ref/
python scripts/regions_2025.py data/ref/regions_13_17.csv data/tidy/presco_tidy.csv data/tidy/presco_tidy_regions2025.csv
```

**3. Panel, violence, carte**

```bash
python scripts/analyse_pistes.py data/tidy/presco_tidy.csv analyse/
python scripts/regions_2025.py data/ref/regions_13_17.csv analyse/panel_region_annee.csv analyse/panel_region_annee_2025.csv
python scripts/acled_anticipation.py data/raw/externe/hdx_acled/acled_political_violence_month_year.xlsx analyse/panel_region_annee.csv analyse/
python scripts/figures_pistes.py data/tidy/presco_tidy.csv analyse/ analyse/figures/
python scripts/carte_13_regions.py data/raw/externe/hdx_cod_ab/geojson/bfa_admin1.geojson data/ref/regions_13_17.csv analyse/
```

**4. Prévision et modèles**

```bash
python scripts/prevision_hypothese.py
python scripts/figures_prevision.py
python scripts/machine_learning.py
python scripts/figures_ml.py
python scripts/approches_prevision.py
python scripts/solution_prevision.py
```

**5. Autres facteurs et alertes**

```bash
python scripts/prepare_facteurs.py
python scripts/facteurs_decrochage.py
python scripts/prevision_facteurs.py
python scripts/anticipation_fine.py
python scripts/figures_approches.py
```

**6. Fiches régionales**

```bash
python scripts/fiches_regionales.py
```

Chaque script décrit en tête ce qu'il fait, ce qu'il lit et ce qu'il écrit.

**7. Dépôts du challenge** (dossiers `01_collecte` à `05_interpretation`, noms `EQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN`, LISEZ-MOI)

```bash
python scripts/construire_depots.py Biiga 1
```

Le résultat va dans `depots/`, qui n'est pas suivi par git.

## Principes

- **Chaque modèle est testé sur des années qu'il n'a pas vues**, contre la règle « comme l'an passé ».
- **Les listes de modèles sont fixées avant de lancer les tests.**
- **Ce qui ne marche pas est dit**, avec ses chiffres.
- **Toute donnée externe est citée** (`data/externe_propre/*.SOURCE.txt`).
- **Aucune donnée personnelle.**

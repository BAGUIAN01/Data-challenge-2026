# Data-challenge-2026

Data Challenge Burkina, édition Éducation 2026. **Défi 1 : cartographie et anticipation du risque de décrochage scolaire par région.**

## Ce que contient le dépôt

| Dossier | Contenu |
| --- | --- |
| `notebooks/` | **Le code de chaque étape en cahiers Jupyter, déjà exécutés** (02 nettoyage, 03 transformation, 04a analyse descriptive, 04b modèles, 05 interprétation) |
| `scripts/` | Les mêmes étapes en scripts Python, dont les cahiers sont construits |
| `rapport/` | **Le rapport** (`rapport_defi1.pdf`, LaTeX), avec sa source et les captures du tableau de bord |
| `analyse/` | Résultats : tableaux (`P1_` à `P19_`), notes d'analyse (`*.md`), sorties brutes (`resultats_*.txt`), figures, fiches régionales |
| `docs/` | Flux de travail, audit des données, journal des décisions (D1 à D21), note d'intention |
| `data/tidy/` | Données du challenge remises en tableau long |
| `data/ref/` | Correspondance 13 / 17 régions et fond de carte des 13 régions |
| `data/externe_propre/` | Sources externes nettoyées, chacune avec sa source |
| `data/raw/` | Données brutes, **non versionnées** : voir `data/raw/LISEZ-MOI.md` |
| `dashboard/` | **Le tableau de bord** : application de téléphone Next.js local-first (fonctionne sans réseau), au niveau des 13 régions, base Neon. Voir `dashboard/README.md` |
| `maquettes/` | La maquette de l'application, avant le code |

## Où lire les résultats

1. `rapport/rapport_defi1.pdf` : le rapport (10 pages).
2. Le tableau de bord : code dans `dashboard/`, voir `dashboard/README.md` ; il est aussi en ligne (lien donné dans la fiche de la solution).
3. `analyse/solution_anticipation.md` : la solution (où agir, où le risque monte, combien d'enfants, calendrier d'alerte).
4. `analyse/facteurs_decrochage.md` : les causes autres que l'insécurité.
5. `analyse/autres_approches_prevision.md` et `analyse/machine_learning.md` : ce qui prévoit et ce qui ne prévoit pas.
6. `analyse/formule_risque.md` : la formule du risque, le score global et le facteur dominant, avec des exemples calculés à la main.
7. `docs/journal_decisions.md` : chaque décision, sa raison et ses limites.
8. `analyse/fiches_regionales_13.pdf` : une page par région.

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
python scripts/formule_risque.py
python scripts/score_global.py
python scripts/facteur_dominant.py
python scripts/figures_approches.py
```

**6. Tableau de bord** (jeu de données, puis base Neon et application : voir `dashboard/README.md`)

```bash
python scripts/export_tableau_de_bord.py
```

**7. Fiches régionales** (après le jeu de données : la fiche le lit, elle dit donc les mêmes chiffres que l'application)

```bash
python scripts/fiches_regionales.py
```

**Ou tout d'un coup, en cahiers Jupyter** (un par étape, dans `notebooks/`, déjà exécutés : résultats et figures visibles sans rien lancer) :

```bash
python scripts/construire_notebooks.py
```

Les cahiers reprennent le code des scripts, étape par étape ; les relancer redonne exactement les mêmes résultats.

**8. Rapport** (LaTeX, XeLaTeX ; lit les mêmes données que l'application)

```bash
python rapport/construire_rapport.py
```

**9. Soumission** (fichiers prêts à téléverser, rangés comme sur la plateforme : données, code, documentation ; 20 fichiers au plus, aucun nom d'équipe)

```bash
python scripts/construire_soumission.py
```

Le résultat va dans `soumission/`, qui n'est pas suivi par git.

## Principes

- **Chaque modèle est testé sur des années qu'il n'a pas vues**, contre la règle « comme l'an passé ».
- **Les listes de modèles sont fixées avant de lancer les tests.**
- **Ce qui ne marche pas est dit**, avec ses chiffres.
- **Toute donnée externe est citée** (`data/externe_propre/*.SOURCE.txt`).
- **Aucune donnée personnelle.**

# Défi 1 · Anticiper le risque de décrochage scolaire, région par région

Burkina Faso, rentrée 2026/27 · 13 régions · données agrégées, aucune donnée personnelle.

## Noms des fichiers

`ÉTAPE_DÉFI_RÔLE_description_vN` : l'étape où le fichier est produit (02-nettoyage à 05-interpretation), le défi (D1), le rôle (engineer, architect, analyst, scientist), ce qu'il contient, sa version. Le nom de l'équipe n'y figure pas, pour l'évaluation à l'aveugle.

Chaque catégorie a son LISEZ-MOI : `LISEZ-MOI_documentation.md` (ce fichier, vue d'ensemble), `LISEZ-MOI_code.txt` (code : cahiers, application, relance) et `LISEZ-MOI_donnees.csv` (données : un fichier par ligne, avec son contenu).

## Par où commencer

1. **`05-interpretation_D1_analyst_rapport_v1.pdf`** (catégorie Documentation) : le rapport (10 pages). Le besoin, les données, la méthode et ses formules, les résultats 2026/27, l'outil, les limites.
2. **Le tableau de bord en ligne** : son lien est donné dans la fiche de la solution. Il s'ouvre sur téléphone comme sur ordinateur et fonctionne sans réseau.
3. **`05-interpretation_D1_analyst_priorites-2026-27_v1.csv`** (catégorie Données) : le résultat en un tableau, une ligne par région (score, risque, priorité, sur quoi agir, levier).

## Ce que contient chaque fichier

### Documentation

| Fichier | Contenu |
| --- | --- |
| `05-interpretation_D1_analyst_rapport_v1.pdf` | Le rapport complet |
| `05-interpretation_D1_analyst_fiches-regionales_v1.pdf` | Une page par région, pour un directeur régional, de la plus urgente à la moins urgente |
| `04-analyse_D1_scientist_formule-risque_v1.md` | Les formules du risque, du score global et du facteur dominant, avec des exemples calculés à la main |
| `04-analyse_D1_scientist_journal-decisions_v1.md` | Les 21 décisions de méthode : ce qui a été décidé, pourquoi, et ce qui a été écarté |
| `LISEZ-MOI_documentation.md` | Ce fichier |

### Code

| Fichier | Contenu |
| --- | --- |
| `LISEZ-MOI_code.txt` | Ce que contient chaque fichier de code, et comment tout relancer |
| `02-nettoyage_D1_engineer_cahier-nettoyage_v1.ipynb` | Lecture du fichier du challenge, contrôles de cohérence, sources externes |
| `03-transformation_D1_architect_cahier-transformation_v1.ipynb` | Correspondance des régions, panel région × année, violence, carte |
| `04-analyse_D1_analyst_cahier-analyse-descriptive_v1.ipynb` | Ce que montrent les données, figures 01 à 07 |
| `04-analyse_D1_scientist_cahier-modeles_v1.ipynb` | Risque de chute, alertes, apprentissage automatique, facteurs, formule, score global, facteur dominant |
| `05-interpretation_D1_analyst_cahier-interpretation_v1.ipynb` | Figures de la solution, données du tableau de bord, fiches régionales |
| `05-interpretation_D1_analyst_tableau-de-bord_v1.zip` | Le code de l'application (Next.js, fonctionne sans réseau) ; voir son `README.md` |
| `05-interpretation_D1_scientist_projet-complet_v1.zip` | Tout le projet, pour tout relancer : scripts, données traitées, tableaux de résultats, source LaTeX du rapport, application. Les cahiers, les figures et les PDF n'y sont pas : le code les régénère, et ils sont fournis à part |

Les cahiers sont **déjà exécutés** : les résultats et les figures se lisent sans rien lancer (figures allégées pour le dépôt). Relancés dans le projet complet, ils redonnent exactement les mêmes résultats.

### Données

| Fichier | Contenu |
| --- | --- |
| `LISEZ-MOI_donnees.csv` | Ce que contient chaque fichier de données, y compris l'intérieur des archives, et d'où il vient |
| `05-interpretation_D1_analyst_priorites-2026-27_v1.csv` | **Le résultat final** : par région, score 2026/27, probabilité de chute des effectifs, alerte de septembre, achèvement, priorité, facteur dominant, levier, enfants hors CM2 |
| `04-analyse_D1_scientist_resultats-analyse_v1.xlsx` | Tous les tableaux de résultats (A à G, P1 à P19), une feuille par tableau ; la feuille `lisez-moi` dit ce que contient chacune |
| `05-interpretation_D1_analyst_donnees-tableau-de-bord_v1.json` | Tout ce qu'affiche le tableau de bord, en un fichier |
| `03-transformation_D1_engineer_donnees-transformees_v1.zip` | Le panel région × année (la table de base des modèles), la violence par région et année, les correspondances 13/17 régions et 45/47 provinces, la carte des 13 régions, le dictionnaire des variables |
| `02-nettoyage_D1_engineer_donnees-nettoyees_v1.zip` | Les données du challenge en tableau propre, le résultat des contrôles de cohérence, les sources externes nettoyées (pauvreté, faim, EDS, déplacés), chacune avec sa source, et la liste de toutes les sources (producteur, publication, année, licence) |

Seules les données traitées sont fournies. Les données brutes viennent du challenge ou de sources publiques, toutes citées dans la liste des sources ; celles d'ACLED ne sont pas redistribuables, et notre agrégat par région et par année est fourni.

## Pour tout relancer

1. Décompresser `05-interpretation_D1_scientist_projet-complet_v1.zip`.
2. Placer les données brutes comme l'indique `data/raw/LISEZ-MOI.md`.
3. Installer les dépendances : `pip install -r requirements.txt`.
4. Lancer `python scripts/construire_notebooks.py`, ou suivre l'ordre des commandes du `README.md`.

# Défi 1 · Anticiper le risque de décrochage scolaire, région par région

Burkina Faso, rentrée 2026/27 · 13 régions · données agrégées, aucune donnée personnelle.

## Noms des fichiers

`ÉQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN` : l'équipe (Biiga), l'étape où le fichier est produit (02-nettoyage à 05-interpretation), le défi (D1), le rôle (engineer, architect, analyst, scientist), ce qu'il contient, sa version.

Les fichiers sont rangés par étape, comme dans le dépôt : `02_nettoyage/`, `03_transformation/`, `04_analyse/`, `05_interpretation/` (la collecte, étape 01, est décrite dans la liste des sources, jointe aux données nettoyées). La présentation est à la racine, pour commencer par elle. Sur la plateforme, chacun va dans sa catégorie (Données, Code, Documentation), indiquée plus bas.

Chaque catégorie a son LISEZ-MOI : `LISEZ-MOI_documentation.md` (ce fichier, vue d'ensemble), `LISEZ-MOI_code.txt` (code : notebooks, application, relance) et `LISEZ-MOI_donnees.csv` (données : un fichier par ligne, avec son contenu).

## Par où commencer

1. **`Biiga_05-interpretation_D1_analyst_presentation_v1.pdf`** (catégorie Documentation) : la présentation (11 diapositives). Cartographier, anticiper, agir : la carte du décrochage, les régions en alerte pour 2026/27, le levier de chaque région, l'outil.
2. **`Biiga_05-interpretation_D1_analyst_rapport_v1.pdf`** (catégorie Documentation) : le rapport (11 pages). Le besoin, les données, la méthode et ses formules, les résultats 2026/27, l'outil, les limites.
3. **Le tableau de bord en ligne** : son lien est donné dans la fiche de la solution. Il s'ouvre sur téléphone comme sur ordinateur et fonctionne sans réseau.
4. **`Biiga_05-interpretation_D1_analyst_priorites-2026-27_v1.csv`** (catégorie Données) : le résultat en un tableau, une ligne par région (score, risque, priorité, sur quoi agir, levier).

## Ce que contient chaque fichier

### Documentation

| Fichier | Contenu |
| --- | --- |
| `Biiga_05-interpretation_D1_analyst_presentation_v1.pdf` | La présentation : cartographier, anticiper, agir (11 diapositives) |
| `Biiga_05-interpretation_D1_analyst_rapport_v1.pdf` | Le rapport complet |
| `Biiga_05-interpretation_D1_analyst_fiches-regionales_v1.pdf` | Une page par région, pour un directeur régional, de la plus urgente à la moins urgente |
| `Biiga_04-analyse_D1_scientist_formule-risque_v1.md` | Les formules du risque, du score global et du facteur dominant, avec des exemples calculés à la main |
| `Biiga_04-analyse_D1_scientist_journal-decisions_v1.md` | Les 21 décisions de méthode : ce qui a été décidé, pourquoi, et ce qui a été écarté |
| `LISEZ-MOI_documentation.md` | Ce fichier |

### Code

| Fichier | Contenu |
| --- | --- |
| `LISEZ-MOI_code.txt` | Ce que contient chaque fichier de code, et comment tout relancer |
| `Biiga_02-nettoyage_D1_engineer_notebook-nettoyage_v1.ipynb` | Lecture du fichier du challenge, contrôles de cohérence, sources externes |
| `Biiga_03-transformation_D1_architect_notebook-transformation_v1.ipynb` | Correspondance des régions, panel région × année, violence, carte |
| `Biiga_04-analyse_D1_analyst_notebook-analyse-descriptive_v1.ipynb` | Ce que montrent les données, figures 01 à 07 |
| `Biiga_04-analyse_D1_scientist_notebook-modeles_v1.ipynb` | Risque de chute, alertes, apprentissage automatique, facteurs, formule, score global, facteur dominant |
| `Biiga_05-interpretation_D1_analyst_notebook-interpretation_v1.ipynb` | Figures de la solution, données du tableau de bord, fiches régionales |
| `Biiga_05-interpretation_D1_analyst_tableau-de-bord_v1.zip` | Le code de l'application (Next.js, fonctionne sans réseau) ; voir son `README.md` |
| `Biiga_05-interpretation_D1_scientist_projet-complet_v1.zip` | Tout le projet, pour tout relancer : scripts, données traitées, tableaux de résultats, source LaTeX du rapport, application. Les notebooks, les figures et les PDF n'y sont pas : le code les régénère, et ils sont fournis à part |

Les notebooks sont **déjà exécutés** : les résultats et les figures se lisent sans rien lancer (figures allégées pour le dépôt). Relancés dans le projet complet, ils redonnent exactement les mêmes résultats.

### Données

| Fichier | Contenu |
| --- | --- |
| `LISEZ-MOI_donnees.csv` | Ce que contient chaque fichier de données, y compris l'intérieur des archives, et d'où il vient |
| `Biiga_05-interpretation_D1_analyst_priorites-2026-27_v1.csv` | **Le résultat final** : par région, score 2026/27, probabilité de chute des effectifs, alerte de septembre, achèvement, priorité, facteur dominant, levier, enfants hors CM2 |
| `Biiga_04-analyse_D1_scientist_resultats-analyse_v1.xlsx` | Tous les tableaux de résultats (A à G, P1 à P19), une feuille par tableau ; la feuille `lisez-moi` dit ce que contient chacune |
| `Biiga_05-interpretation_D1_analyst_donnees-tableau-de-bord_v1.json` | Tout ce qu'affiche le tableau de bord, en un fichier |
| `Biiga_03-transformation_D1_engineer_donnees-transformees_v1.zip` | Le panel région × année (la table de base des modèles), la violence par région et année, les correspondances 13/17 régions et 45/47 provinces, la carte des 13 régions, le dictionnaire des variables |
| `Biiga_02-nettoyage_D1_engineer_donnees-nettoyees_v1.zip` | Les données du challenge en tableau propre, le résultat des contrôles de cohérence, les sources externes nettoyées (pauvreté, faim, EDS, déplacés), chacune avec sa source, et la liste de toutes les sources (producteur, publication, année, licence) |

Seules les données traitées sont fournies. Les données brutes viennent du challenge ou de sources publiques, toutes citées dans la liste des sources ; celles d'ACLED ne sont pas redistribuables, et notre agrégat par région et par année est fourni.

## Pour tout relancer

1. Décompresser `Biiga_05-interpretation_D1_scientist_projet-complet_v1.zip`.
2. Ajouter les données brutes, qui ne sont pas fournies (seules les données traitées le sont) :
   - le fichier du challenge : le télécharger dans l'espace challenge et le placer tel quel dans `01_collecte/brut/` ;
   - les sources publiques : les télécharger aux adresses données dans `01_collecte/brut/LISEZ-MOI.md`, et les placer aux chemins indiqués.
3. Installer les dépendances : `pip install -r requirements.txt`.
4. Lancer `python outils/construire_notebooks.py`. Chaque dossier d'étape (`01_collecte` à `05_interpretation`) a son `LISEZ-MOI.md`, qui décrit ses fichiers.

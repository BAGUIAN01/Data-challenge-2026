# Défi 1 · Anticiper le risque de décrochage scolaire, région par région

Burkina Faso, rentrée 2026/27 · 13 régions · données agrégées, aucune donnée personnelle.

## Par où commencer

1. **`documentation/rapport.pdf`** : le rapport (10 pages). Le besoin, les données, la méthode et ses formules, les résultats 2026/27, l'outil, les limites.
2. **Le tableau de bord en ligne** : <https://kalantigui-decrochage.vercel.app>. Il s'ouvre sur téléphone comme sur ordinateur et fonctionne sans réseau.
3. **`donnees/priorites_2026_27.csv`** : le résultat en un tableau, une ligne par région (score, risque, priorité, sur quoi agir, levier).

## Ce que contient chaque fichier

### Documentation

| Fichier | Contenu |
| --- | --- |
| `rapport.pdf` | Le rapport complet |
| `fiches_regionales.pdf` | Une page par région, pour un directeur régional, de la plus urgente à la moins urgente |
| `formule_du_risque.md` | Les formules du risque, du score global et du facteur dominant, avec des exemples calculés à la main |
| `journal_des_decisions.md` | Les 21 décisions de méthode : ce qui a été décidé, pourquoi, et ce qui a été écarté |
| `LISEZ-MOI.md` | Ce fichier |

### Code

| Fichier | Contenu |
| --- | --- |
| `cahier_02_nettoyage.ipynb` | Lecture du fichier du challenge, contrôles de cohérence, sources externes |
| `cahier_03_transformation.ipynb` | Correspondance des régions, panel région × année, violence, carte |
| `cahier_04a_analyse_descriptive.ipynb` | Ce que montrent les données, figures 01 à 07 |
| `cahier_04b_modeles.ipynb` | Risque de chute, alertes, apprentissage automatique, facteurs, formule, score global, facteur dominant |
| `cahier_05_interpretation.ipynb` | Figures de la solution, données du tableau de bord, fiches régionales |
| `tableau_de_bord.zip` | Le code de l'application (Next.js, fonctionne sans réseau) ; voir son `README.md` |
| `projet_complet.zip` | Tout le projet, pour tout relancer : scripts, cahiers, données propres, rapport, application |

Les cahiers sont **déjà exécutés** : les résultats et les figures se lisent sans rien lancer. Relancés dans le projet complet, ils redonnent exactement les mêmes résultats.

### Données

| Fichier | Contenu |
| --- | --- |
| `priorites_2026_27.csv` | **Le résultat final** : par région, score 2026/27, probabilité de chute des effectifs, alerte de septembre, achèvement, priorité, facteur dominant, levier, enfants hors CM2 |
| `resultats_analyse.xlsx` | Tous les tableaux de résultats (A à G, P1 à P19), une feuille par tableau ; la feuille `lisez-moi` dit ce que contient chacune |
| `donnees_tableau_de_bord.json` | Tout ce qu'affiche le tableau de bord, en un fichier |
| `donnees_transformees.zip` | Le panel région × année (la table de base des modèles), la violence par région et année, les correspondances 13/17 régions et 45/47 provinces, la carte des 13 régions, le dictionnaire des variables |
| `donnees_nettoyees.zip` | Les données du challenge en tableau propre, le résultat des contrôles de cohérence, les sources externes nettoyées (pauvreté, faim, EDS, déplacés), chacune avec sa source |
| `donnees_collectees.zip` | Les sources externes brutes (population 2024, Cadre harmonisé, déplacés CONASUR, limites IGB 2025) et la liste des sources avec leurs licences |

Les données brutes d'ACLED ne sont pas redistribuées, conformément à leurs conditions ; seul notre agrégat par région et par année est fourni.

## Pour tout relancer

1. Décompresser `projet_complet.zip`.
2. Placer les données brutes comme l'indique `data/raw/LISEZ-MOI.md`.
3. Installer les dépendances : `pip install -r requirements.txt`.
4. Lancer `python scripts/construire_notebooks.py`, ou suivre l'ordre des commandes du `README.md`.

# Défi 1 · Anticiper le risque de décrochage scolaire, région par région

**Équipe Biiga** · Burkina Faso, rentrée 2026/27 · 13 régions · données agrégées, aucune donnée personnelle.

**Tableau de bord en ligne : <https://kalantigui-decrochage.vercel.app>**

## Par où commencer

1. **`Biiga_05-interpretation_D1_analyst_presentation_v1.pdf`** (à la racine) : la présentation, 11 diapositives. Cartographier, anticiper, agir : la carte du décrochage, les régions en alerte pour 2026/27, le levier de chaque région, l'outil.
2. **Le tableau de bord** (lien ci-dessus) : il s'ouvre sur téléphone comme sur ordinateur et fonctionne sans réseau.
3. **`05_interpretation/Biiga_05-interpretation_D1_analyst_rapport_v1.pdf`** : le rapport, 11 pages. Le besoin, les données, la méthode et ses formules, les résultats 2026/27, l'outil, les limites.
4. **`05_interpretation/Biiga_05-interpretation_D1_analyst_priorites-2026-27_v1.csv`** : le résultat en un tableau, une ligne par région (score, risque, priorité, sur quoi agir, levier).

## Rangement et noms

Les fichiers sont rangés comme dans le dépôt : un dossier par étape (`02_nettoyage/` à `05_interpretation/`) et `dashboard/` pour l'application. La collecte (étape 01) est décrite dans la liste des sources, jointe aux données nettoyées.

Chaque fichier suit le modèle `ÉQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN` : l'équipe (Biiga), l'étape où il est produit, le défi (D1), le rôle (engineer, architect, analyst, scientist), ce qu'il contient, sa version.

Sur la plateforme, chaque fichier va dans la catégorie indiquée ci-dessous (Documentation, Code ou Données).

## Le tableau de bord

Pour le décideur, avant chaque rentrée : où agir en premier, où le risque monte, combien d'enfants sont en jeu et sur quoi agir dans chaque région.

- **La carte du score** 2026/27 par région, avec un lecteur des années (de 2020/21 à la prévision 2026/27) et ce qui change d'une année à l'autre.
- **Une page par région** : son score et sa trajectoire, sur quoi agir (facteur dominant et levier), l'achèvement, la fiche imprimable.
- **Sans réseau** : les données restent sur l'appareil ; l'application s'ouvre et se consulte hors ligne, et la saisie du terrain (écoles ouvertes à la rentrée) part au retour du réseau.

Le code : `dashboard/Biiga_05-interpretation_D1_analyst_tableau-de-bord_v1.zip` (Next.js). Pour le lancer : `npm install`, puis `npm run build`, puis `npm start`, et ouvrir <http://localhost:3000>. Sans base de données, l'application utilise les données publiées avec elle. Détails dans le `README.md` de l'archive.

## Ce que contient chaque fichier

### Documentation

| Fichier | Contenu |
| --- | --- |
| `Biiga_05-interpretation_D1_analyst_presentation_v1.pdf` | La présentation : cartographier, anticiper, agir (11 diapositives) |
| `LISEZ-MOI.md` | Ce fichier |
| `05_interpretation/Biiga_05-interpretation_D1_analyst_rapport_v1.pdf` | Le rapport complet |
| `05_interpretation/Biiga_05-interpretation_D1_analyst_fiches-regionales_v1.pdf` | Une page par région, pour un directeur régional, de la plus urgente à la moins urgente |
| `04_analyse/Biiga_04-analyse_D1_scientist_formule-risque_v1.md` | Les formules du risque, du score global et du facteur dominant, avec des exemples calculés à la main |
| `04_analyse/Biiga_04-analyse_D1_scientist_journal-decisions_v1.md` | Les 21 décisions de méthode : ce qui a été décidé, pourquoi, et ce qui a été écarté |

### Code

| Fichier | Contenu |
| --- | --- |
| `dashboard/Biiga_05-interpretation_D1_analyst_tableau-de-bord_v1.zip` | Le code du tableau de bord (Next.js, fonctionne sans réseau) |
| `02_nettoyage/Biiga_02-nettoyage_D1_engineer_notebook-nettoyage_v1.ipynb` | Lecture du fichier du challenge, 8 contrôles de cohérence, nettoyage des sources externes |
| `03_transformation/Biiga_03-transformation_D1_architect_notebook-transformation_v1.ipynb` | Correspondance 13 / 17 régions, panel région × année, agrégat de violence (ACLED), carte des 13 régions |
| `04_analyse/Biiga_04-analyse_D1_analyst_notebook-analyse-descriptive_v1.ipynb` | Ce que montrent les données, figures 01 à 07 |
| `04_analyse/Biiga_04-analyse_D1_scientist_notebook-modeles_v1.ipynb` | Risque de chute des effectifs, alertes de septembre et de janvier, apprentissage automatique, facteurs, formule du risque, score global, facteur dominant |
| `05_interpretation/Biiga_05-interpretation_D1_analyst_notebook-interpretation_v1.ipynb` | Figures de la solution, données du tableau de bord, fiches régionales |
| `05_interpretation/Biiga_05-interpretation_D1_scientist_projet-complet_v1.zip` | Tout le projet, pour tout relancer : scripts, données traitées, tableaux de résultats, source LaTeX du rapport, application. Les notebooks, les figures et les PDF n'y sont pas : le code les régénère, et ils sont fournis à part |

Les notebooks sont **déjà exécutés** : résultats et figures se lisent sans rien lancer (figures allégées en JPEG pour le dépôt). Chacun commence par une cellule qui contient tous ses imports ; chaque étape y est un script du projet, découpé en cellules. Le code est en anglais (fonctions, variables) ; les textes lus par l'utilisateur sont en français.

### Données

| Fichier | Contenu |
| --- | --- |
| `05_interpretation/Biiga_05-interpretation_D1_analyst_priorites-2026-27_v1.csv` | **Le résultat final**, une ligne par région : `region_2025`, `ancienne_region`, `score_global_2026_27` (0 à 100), `probabilite_chute_effectifs_pct`, `alerte_septembre_pct`, `taux_achevement_2024_25_pct`, `priorite` (1 agir maintenant, 2 veille renforcée, 3 consolider), `agir_sur` (facteur dominant), `levier`, `ensuite` (deuxième facteur), `enfants_hors_cm2_estimes` |
| `05_interpretation/Biiga_05-interpretation_D1_analyst_donnees-tableau-de-bord_v1.json` | Tout ce qu'affiche le tableau de bord, en un fichier |
| `04_analyse/Biiga_04-analyse_D1_scientist_resultats-analyse_v1.xlsx` | Tous les tableaux de résultats (A à G, P1 à P19), une feuille par tableau ; la feuille `lisez-moi` dit ce que contient chacune |
| `03_transformation/Biiga_03-transformation_D1_engineer_donnees-transformees_v1.zip` | Les données transformées (détail ci-dessous) |
| `02_nettoyage/Biiga_02-nettoyage_D1_engineer_donnees-nettoyees_v1.zip` | Les données nettoyées et la liste des sources (détail ci-dessous) |

**Dans `Biiga_03-transformation_D1_engineer_donnees-transformees_v1.zip`**

| Fichier | Contenu | Produit par |
| --- | --- | --- |
| `panel_region_annee.csv` | LA TABLE DE BASE DES MODÈLES : une ligne par région et par année (2015/16 à 2024/25), effectifs, taux, écoles, sorties apparentes, variations, noms 2025 | notebook 03 (transformation) |
| `violence_acled_region_annee.csv` | Incidents et morts par région et par année scolaire (octobre à septembre), agrégés depuis ACLED | notebook 03 |
| `signaux_violence_region_annee.csv` | Signaux plus fins de violence par région et année : étendue, juillet-septembre, rentrée, civils, voisins | notebook 04b |
| `attaques_education_region_annee.csv` | Attaques contre l'éducation par région et année scolaire, agrégées depuis Insecurity Insight | notebook 04b |
| `correspondance_regions_13_17.csv` | Correspondance officielle entre les 13 anciennes et les 17 nouvelles régions (IGB 2025) | notebook 03 |
| `correspondance_provinces_45_47.csv` | Correspondance officielle entre les 45 anciennes et les 47 nouvelles provinces | notebook 03 |
| `carte_13_regions.geojson` | Contours des 13 anciennes régions, reconstitués depuis les 17 nouvelles | notebook 03 |
| `dictionnaire_variables.md` | Le dictionnaire des variables de toutes les tables | — |

**Dans `Biiga_02-nettoyage_D1_engineer_donnees-nettoyees_v1.zip`**

| Fichier | Contenu | Produit par |
| --- | --- | --- |
| `donnees_challenge_propres.csv` | Les données du challenge (DGESS) en tableau long : une ligne par tableau, région, année, sexe, statut, niveau ; 6 621 valeurs, aucune modifiée | notebook 02 (nettoyage) |
| `controles_qualite.txt` | Résultat des 8 contrôles de cohérence (sommes, parité, doublons, sauts, valeurs hors norme) | notebook 02 |
| `sources_donnees.csv` | La liste de toutes les sources : producteur, publication, année, adresse, licence, ce qui est fourni | — |
| `pauvrete_ehcvm_2021_regions.csv` | Pauvreté par région (INSD, EHCVM 2021), avec sa fiche source (.SOURCE.txt) | notebook 02 |
| `faim_cadre_harmonise_region_annee.csv` | Part de la population en phase 3 ou plus d'insécurité alimentaire, par région et année scolaire (Cadre harmonisé) | notebook 02 |
| `eds_2021_regions.csv` | Femmes sans instruction et grossesses précoces par région (EDS 2021) | notebook 02 |
| `pdi_conasur_2022_regions.csv` | Déplacés accueillis par région, en nombre et en part de la population (CONASUR, fin 2022) | notebook 02 |

Seules les données traitées sont fournies. Les données brutes viennent du challenge ou de sources publiques, toutes citées dans `sources_donnees.csv` ; celles d'ACLED ne sont pas redistribuables, et notre agrégat par région et par année est fourni.

## Pour tout relancer (Python 3.13)

1. Décompresser `05_interpretation/Biiga_05-interpretation_D1_scientist_projet-complet_v1.zip`.
2. Ajouter les données brutes, qui ne sont pas fournies :
   - le fichier du challenge : le télécharger dans l'espace challenge et le placer tel quel dans `01_collecte/brut/` ;
   - les sources publiques : les télécharger aux adresses données dans `01_collecte/brut/LISEZ-MOI.md`, et les placer aux chemins indiqués.
3. `pip install -r requirements.txt`
4. `python outils/construire_notebooks.py` : les cinq notebooks sont relancés dans l'ordre des étapes et redonnent exactement les mêmes résultats. Chaque dossier d'étape a son `LISEZ-MOI.md`, qui décrit ses fichiers.

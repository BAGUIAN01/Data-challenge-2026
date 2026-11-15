# Journal de nettoyage

*Scripts : `02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-lecture-challenge_v1.py` (lecture), `02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-controles-coherence_v1.py` (contrôles, sortie `02_nettoyage/Biiga_02-nettoyage_D1_engineer_controles-qualite_v1.txt`), `02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-sources-externes_v1.py` (sources externes).*

## 1. Le fichier du challenge (`Presco.txt`)

**Ce qu'on a reçu.** Une feuille Excel enregistrée en texte séparé par des tabulations. Elle contient 21 tableaux :
- 8 pour le préscolaire (P1 à P8) ;
- 13 pour le primaire (E1 à E13) ;
- couvrant 13 régions et l'ensemble du pays, de 2015/16 à 2024/25.

| Problème rencontré | Ce qu'on a fait | Pourquoi |
| --- | --- | --- |
| Les tableaux se suivent, séparés par des lignes vides ; certains titres sont décalés en colonne X, et des cellules « 2017 » isolées traînent | Chaque tableau est repéré par ses lignes, vérifiées à la main, puis lu selon sa forme. Trois formes existent : garçons-filles-total en colonnes, sexe en lignes, ou sans sexe | Une lecture automatique « au premier tableau trouvé » mélangeait les tableaux |
| Lignes d'en-tête répétées (« RÉGION », « STATUT », « SEXE ») et années écrites comme des nombres | Lignes d'en-tête ignorées ; seules les cellules numériques sont lues comme des valeurs | Sinon, les en-têtes entraient dans les données comme des chiffres |
| Nombres écrits « 1 477 806 » (espaces, parfois insécables) ou « 1,1760 » (virgule décimale) | Espaces retirés, virgule changée en point. Toute cellule qui n'est pas un nombre arrête la lecture | Aucune valeur n'est avalée en silence |
| Cellules fusionnées dans Excel : le libellé n'apparaît que sur la première ligne | Le libellé est reporté sur les lignes suivantes | Sinon, des lignes restaient sans région ni statut |
| Région écrite « HAUT-BASSINS » dans certains tableaux | Uniformisée en « HAUTS-BASSINS » | Une même région sous deux noms se compte deux fois |
| Le total national porte plusieurs noms (« TOTAL GÉNÉRAL », « BURKINA FASO », « NATIONAL », « TOTAL ») | Tous ramenés à « NATIONAL » | Un seul nom pour le pays |
| Lignes « Total Public » ou « Total + région » (sous-totaux) | Gardées, avec la valeur « Total » dans la colonne détaillée | Permet de vérifier que les détails font bien le total |
| Libellés de statut et de milieu en capitales et avec accents | Uniformisés (Public, Prive, Communautaire ; Urbain, Rural, Indetermine) | Noms stables pour les jointures |

**Résultat :** `02_nettoyage/Biiga_02-nettoyage_D1_engineer_donnees-challenge-propres_v1.csv`, **6 621 valeurs**. Chaque ligne est une valeur, décrite par 11 colonnes : tableau, cycle, indicateur, unité, région, statut, milieu, niveau, sexe, année scolaire, valeur.

## 2. Les contrôles de cohérence (`02_nettoyage/Biiga_02-nettoyage_D1_engineer_controles-qualite_v1.txt`)

| Contrôle | Résultat |
| --- | --- |
| Garçons + filles = total | 827 cas, **tous justes** |
| Somme des régions = total national (effectifs, CP1, écoles, structures, salles) | **Tous justes** |
| Le même total national dans les tableaux par région, par statut, par milieu et par niveau | **Tous justes** |
| Somme des statuts et des niveaux = total | **Tous justes** |
| Indice de parité publié = taux des filles / taux des garçons | 559 sur 560 justes. **Écart :** préscolaire, Centre, 2019/20 (1,00 publié, 0,91 recalculé) |
| Lignes recopiées d'une région à l'autre | **1 cas :** taux de préscolarisation 2019/20, Sahel identique à Sud-Ouest |
| Sauts de plus de 40 % d'une année à l'autre | 30 cas, presque tous expliqués par les fermetures (Sahel 2018/19, Boucle du Mouhoun 2022/23), les réouvertures (2023/24) ou les petits effectifs du préscolaire |
| Taux hors de l'ordre de grandeur attendu | 15 cas : taux d'admission de 131 à 146 % (Nord, Centre, Plateau Central) ; taux d'achèvement des filles du Centre au-dessus de 100 % |

## 3. Ce qu'on a corrigé, et ce qu'on a gardé tel quel

**Aucune valeur n'a été modifiée.** Les anomalies sont signalées et contournées :

- **Préscolaire 2019/20, Sahel = Sud-Ouest.** Il s'agit probablement d'une ligne recopiée à la source. Aucune analyse n'utilise cette année : le seul usage du taux de préscolarisation, dans le profil des facteurs, prend 2024/25.
- **Parité du préscolaire, Centre, 2019/20.** Aucune analyse n'utilise la parité du préscolaire. L'écart est signalé, sans correction.
- **Taux d'admission au-delà de 100 %.** Ce n'est pas une erreur de saisie : la population de référence est une projection qui ignore les déplacements. D'où la décision D4 : les effectifs sont préférés aux taux quand les deux sont possibles.
- **Sauts de plus de 40 %.** Ils sont gardés : ce sont les chocs qu'on cherche à mesurer.

## 4. Les sources externes (`02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-sources-externes_v1.py`, `02_nettoyage/`)

| Source | Nettoyage |
| --- | --- |
| Régions 2025 (IGB) | Correspondance 13 / 17 régions et 45 / 47 provinces tirée des **anciens codes officiels**, pas des noms (`03_transformation/Biiga_03-transformation_D1_architect_script-referentiel-regions_v1.py`) |
| ACLED | Provinces sommées par ancienne région, mois regroupés par **année scolaire** (octobre à septembre), pas par année civile |
| Cadre Harmonisé | Provinces sommées par ancienne région. On ne garde que les périodes marquées « à utiliser », puis on fait la moyenne des périodes d'une année scolaire |
| EDS (2010 à 2021) | Noms de régions alignés sur ceux du challenge (« Boucle de Mouhoun », « Hauts Bassins »). Ouagadougou est retiré : la ligne « Centre » l'inclut déjà |
| CONASUR | Ligne du total national retirée. Les déplacés sont rapportés à la population de la région |
| Pauvreté (INSD) | Tableau 3-2 recopié. Pour les Cascades, le texte du rapport donne 36,7 % et le tableau 36,9 % : on garde le tableau |

**Rapprochement des noms.** Toutes les jointures entre sources passent par une clé sans accents, sans espaces ni tirets (« CENTRE-NORD » devient « CENTRENORD »). Chaque script vérifie que les 13 régions sont présentes, et s'arrête sinon.

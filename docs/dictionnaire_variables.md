# Dictionnaire des variables

**Cases vides :** elles sont voulues. Une variation (`dlog_*`, `d_*`, `sorties_app`) n'existe pas pour la première année d'une série, faute d'année précédente ; une cible de l'année suivante (`y_*`) ou un signal de rentrée (`late`, `rentree`) n'existe pas encore pour la dernière.

**Conventions communes :**
- **Année scolaire** : « 2015-2016 » à « 2024-2025 », d'octobre à septembre. Ce n'est pas l'année civile.
- **Région** : les 13 anciennes régions, en capitales, telles que dans le fichier du challenge, plus « NATIONAL ».
- **Clé de jointure (`cle`)** : le nom de la région sans accents, sans espaces ni tirets, par exemple `CENTRENORD`.

## `data/tidy/presco_tidy.csv` : les données du challenge en tableau long (6 621 lignes)

| Variable | Type | Valeurs | Définition |
| --- | --- | --- | --- |
| `table` | texte | P1 à P8, E1 à E13 | Tableau d'origine dans `Presco.txt` (P = préscolaire, E = primaire) |
| `cycle` | texte | prescolaire, primaire | Cycle d'enseignement |
| `indicateur` | texte | effectifs, nouveaux_inscrits_CP1, TBA, TBS, TAP, reussite_CEP, IPS_TBA, IPS_TBS, IPS_TAP, ecoles, structures, salles | Ce qui est mesuré |
| `unite` | texte | eleves, %, ratio F/G, ecoles, structures, salles | Unité de `valeur` |
| `region` | texte | 13 régions et NATIONAL | Ancienne région |
| `statut` | texte | Public, Prive, Communautaire, Total | Statut de l'établissement |
| `milieu` | texte | Urbain, Rural, Indetermine, Total | Milieu |
| `niveau` | texte | CP1 à CM2, niveaux du préscolaire, Total | Classe |
| `sexe` | texte | G, F, T | Garçons, filles, total |
| `annee` | texte | 2015-2016 à 2024-2025 | Année scolaire |
| `valeur` | nombre | | La valeur publiée, sans aucune modification |

**Définitions des indicateurs :**
- **TBA** (taux brut d'admission) : nouveaux inscrits en CP1 / population de 6 ans, en %.
- **TBS** (taux brut de scolarisation) : élèves / population de 6 à 11 ans, en %.
- **TAP** (taux d'achèvement du primaire) : nouveaux entrants en CM2 / population de 11 ans, en %.
- **IPS** (indice de parité) : taux des filles / taux des garçons.

Les populations de référence sont des projections, qui ignorent les déplacements.

`data/tidy/presco_tidy_regions2025.csv` : le même tableau, avec trois colonnes en plus après `region`. Ce sont celles du tableau suivant.

## `data/ref/regions_13_17.csv` : correspondance officielle entre anciennes et nouvelles régions

| Variable | Définition |
| --- | --- |
| `code_ancienne_region`, `ancienne_region` | Code et nom IGB d'avant 2025 (13 régions) |
| `code_nouvelle_region`, `nouvelle_region` | Code et nom IGB de 2025 (17 régions) |
| `type` | « renommage », « scission en 2 » ou « scission en 3 » |
| `cle_presco` | Clé de jointure vers les données du challenge |
| `source` | IGB, limites administratives v03, valides au 1er août 2025 |

Dans les fichiers « 2025 », les trois colonnes ajoutées sont :
- **`region_2025`** : nom affiché, par exemple « Goulmou + Sirba + Tapoa » ;
- **`codes_2025`** ;
- **`type_2025`**.

`data/ref/provinces_45_47.csv` : la même correspondance pour les provinces. `data/ref/regions_13.geojson` : les contours des 13 anciennes régions, reconstitués en fusionnant les 17 nouvelles par leur ancien code.

## `analyse/panel_region_annee.csv` : une ligne par région et par année (140 lignes)

| Variable | Définition |
| --- | --- |
| `region`, `annee` | Région et année scolaire |
| `eleves_G`, `eleves_F`, `eleves_T` | Élèves du primaire (tableau E1) |
| `nouveaux_CP1_G/F/T` | Nouveaux inscrits en CP1 (E5) |
| `TBA_*`, `TBS_*`, `TAP_*`, `CEP_*` | Taux d'admission, de scolarisation, d'achèvement, réussite au CEP, par sexe (E6 à E9) |
| `IPS_TAP` | Parité filles / garçons du TAP (E12) |
| `ecoles`, `ecoles_publiques` | Écoles primaires, dont publiques (E13) |
| `sorties_app` | **Sorties apparentes** = 1 − (élèves de l'année suivante − nouveaux CP1 de l'année suivante) / élèves de l'année. Elle utilise l'année suivante : **jamais utilisée pour prévoir cette année-là** |
| `dlog_eleves`, `dlog_ecoles` | Variation (en logarithme) des élèves et des écoles par rapport à l'année d'avant |
| `pop6_impl` | Population de 6 ans implicite = nouveaux CP1 / (TBA / 100) |

## `analyse/acled_region_annee.csv` : la violence par région et par année scolaire

| Variable | Définition |
| --- | --- |
| `cle`, `annee` | Région (clé) et année scolaire (octobre à septembre) |
| `incidents` | Nombre d'événements de violence politique (ACLED), toutes provinces de la région |
| `morts` | Nombre de morts rapportés |

`analyse/P16_signaux_region_annee.csv` ajoute les signaux fins :
- **`extent`** : part des mois-provinces touchés ;
- **`late`** : incidents de juillet à septembre ;
- **`rentree`** : incidents d'octobre à décembre de l'année suivante ;
- **`civils`** : attaques contre les civils ;
- **`l_voisins`** : violence moyenne des régions voisines, en logarithme.

## `data/externe_propre/` : les sources externes nettoyées

| Fichier | Variables |
| --- | --- |
| `pauvrete_ehcvm_2021_regions.csv` | `incidence_pauvrete_2021_pct`, `profondeur_pct`, `severite_pct`, `consommation_par_personne_fcfa` |
| `faim_cadre_harmonise_region_annee.csv` | `faim_phase3plus_pct` (part de la population en phase 3 ou plus, moyenne des périodes de l'année scolaire) ; `periodes` ; `population_ch` |
| `eds_2021_regions.csv` | `meres_sans_instruction_pct` (femmes de 15 à 49 ans sans instruction) ; `fecondite_15_19_pour_mille` (naissances pour 1 000 filles de 15 à 19 ans) ; `ipp_frequentation_primaire` |
| `pdi_conasur_2022_regions.csv` | `pdi` (déplacés accueillis au 31/12/2022) ; `pdi_pct_population` |

Chaque fichier a son `.SOURCE.txt`.

## Les tableaux de résultats (`analyse/P*.csv`)

| Préfixe | Contenu |
| --- | --- |
| A à G, P1 à P7 | Indicateurs descriptifs, sorties en excès, profils, contributions, genre, scénarios de réouverture |
| P8 à P10 | Violence et prévision ; fourchette 2025/26 ; hypothèse insécurité × pauvreté |
| P11 | Apprentissage automatique ; probabilités de baisse |
| P12 | Écoles ouvertes à la rentrée ; filière des cohortes |
| P13 | Stabilité du classement ; matrice de priorité 2026/27 |
| P14, P15 | Facteurs autres que l'insécurité ; leur valeur pour prévoir |
| P16 | Signaux fins ; calendrier d'alerte |

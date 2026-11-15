# Données brutes : à télécharger et à placer ici

Ce dossier n'est pas suivi par git :
- **les données du challenge** sont réservées au concours ;
- **les conditions d'utilisation d'ACLED** interdisent de redistribuer ses données ;
- **certains fichiers sont volumineux** (limites administratives : 110 Mo).

Les données brutes ne sont pas fournies : seules les données traitées le sont. Pour tout recalculer, télécharger les fichiers ci-dessous et les placer ainsi, dans `01_collecte/brut/` :

| Chemin | Contenu | Source |
| --- | --- | --- |
| le fichier `.xlsx` du challenge, tel quel (ou son export texte `Presco.txt`) | Données statistiques préscolaire et primaire 2016-2025 (DGESS), 13 régions | Espace challenge, equation.africadataentry.com |
| `externe/hdx_cod_ab/bfa_admin_boundaries.xlsx` et `externe/hdx_cod_ab/geojson/bfa_admin1.geojson` | Limites administratives IGB, v03 (2025) | https://data.humdata.org/dataset/cod-ab-bfa |
| `externe/hdx_cod_ps/bfa_admpop_adm2_2024.csv` | Population 2024 par province | https://data.humdata.org/dataset/cod-ps-bfa |
| `externe/hdx_acled/acled_political_violence_month_year.xlsx` et `acled_civilian_targeting_month_year.xlsx` | Violence par province et par mois | https://data.humdata.org/dataset/burkina-faso-acled-conflict-data |
| `externe/hdx_insecurity_insight/education_in_danger_2017_2026.xlsx` | Attaques contre l'éducation | https://data.humdata.org/organization/insecurity-insight |
| `externe/hdx_cadre_harmonise/cadre_harmonise_caf_ipc_mars26.xlsx` | Insécurité alimentaire par province | https://data.humdata.org/dataset/cadre-harmonise |
| `externe/hdx_dhs/*.csv` | Indicateurs régionaux EDS (éducation, MICS) | https://data.humdata.org/dataset/dhs-subnational-data-for-burkina-faso |
| `externe/hdx_pdi_conasur/situation_pdi_31122022.xlsx` | Déplacés internes par région, au 31/12/2022 | https://data.humdata.org/dataset/situation-des-personnes-deplacees-internes |
| `externe/insd_ehcvm/` | Diagnostic de la pauvreté EHCVM 2021 (tableau 3-2) | INSD, insd.bf |

**Les versions nettoyées des sources externes sont versionnées** dans `02_nettoyage/`. Chaque fichier y est accompagné d'un `.SOURCE.txt`.

Le fichier du challenge est lu directement (`02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-lecture-challenge_v1.py`) : le `.xlsx` de la plateforme s'il est seul dans `01_collecte/brut/`, ou `Presco.txt`. La lecture vérifie deux chiffres connus (3 308 096 élèves et 51,6 % d'achèvement en 2024/25) et s'arrête avec un message clair s'ils ne sont pas retrouvés.

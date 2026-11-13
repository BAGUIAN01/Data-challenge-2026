# Données brutes (non versionnées)

Ce dossier n'est pas suivi par git :
- **les données du challenge** sont réservées au concours ;
- **les conditions d'utilisation d'ACLED** interdisent de redistribuer ses données ;
- **certains fichiers sont volumineux** (limites administratives : 110 Mo).

Pour tout recalculer, placer les fichiers ainsi :

| Chemin | Contenu | Source |
| --- | --- | --- |
| `Presco.txt` | Données du Data Challenge Burkina 2026 (préscolaire et primaire, 13 régions, 2015/16-2024/25) | Organisateurs du challenge |
| `externe/hdx_cod_ab/bfa_admin_boundaries.xlsx` et `externe/hdx_cod_ab/geojson/bfa_admin1.geojson` | Limites administratives IGB, v03 (2025) | HDX `cod-ab-bfa` |
| `externe/hdx_cod_ps/bfa_admpop_adm2_2024.csv` | Population 2024 par province | HDX `cod-ps-bfa` |
| `externe/hdx_acled/acled_political_violence_month_year.xlsx` et `acled_civilian_targeting_month_year.xlsx` | Violence par province et par mois | HDX `burkina-faso-acled-conflict-data` |
| `externe/hdx_insecurity_insight/education_in_danger_2017_2026.xlsx` | Attaques contre l'éducation | HDX (Insecurity Insight) |
| `externe/hdx_cadre_harmonise/cadre_harmonise_caf_ipc_mars26.xlsx` | Insécurité alimentaire par province | HDX `cadre-harmonise` |
| `externe/hdx_dhs/*.csv` | Indicateurs régionaux EDS (éducation, MICS) | HDX `dhs-subnational-data-for-burkina-faso` |
| `externe/hdx_pdi_conasur/situation_pdi_31122022.xlsx` | Déplacés internes par région, au 31/12/2022 | HDX `situation-des-personnes-deplacees-internes` |
| `externe/insd_ehcvm/` | Diagnostic de la pauvreté EHCVM 2021 (tableau 3-2) | INSD |

**Les versions nettoyées des sources externes sont versionnées** dans `data/externe_propre/`. Chaque fichier y est accompagné d'un `.SOURCE.txt`.

# Étape 3 · Transformation

Le passage des 13 aux 17 régions, le panel région × année qui sert de base aux modèles, la violence par région et par année, la carte.

Noms des fichiers : `ÉQUIPE_ÉTAPE_DÉFI_RÔLE_description_vN`.

| Fichier | Rôle | Contenu |
| --- | --- | --- |
| `Biiga_03-transformation_D1_architect_notebook-transformation_v1.ipynb` | architect | **Le notebook Jupyter de l'étape**, déjà exécuté |
| `Biiga_03-transformation_D1_architect_carte-13-regions_v1.geojson` | architect | Contours des 13 anciennes régions (GeoJSON) |
| `Biiga_03-transformation_D1_architect_correspondance-provinces-45-47_v1.csv` | architect | Correspondance officielle 45 anciennes / 47 nouvelles provinces |
| `Biiga_03-transformation_D1_architect_correspondance-regions-13-17_v1.csv` | architect | Correspondance officielle 13 anciennes / 17 nouvelles régions |
| `Biiga_03-transformation_D1_architect_dictionnaire-variables_v1.md` | architect | Le dictionnaire des variables de toutes les tables |
| `Biiga_03-transformation_D1_architect_parcours-donnees_v1.md` | architect | Le parcours des données, étape par étape : schéma, stockage, contrôles |
| `Biiga_03-transformation_D1_engineer_attaques-education-region-annee_v1.csv` | engineer | Attaques contre l'éducation par région et par année (agrégat) |
| `Biiga_03-transformation_D1_engineer_donnees-challenge-regions-2025_v1.csv` | engineer | Les données propres, avec les noms et codes de 2025 |
| `Biiga_03-transformation_D1_engineer_panel-region-annee-2025_v1.csv` | engineer | Le même panel, avec les noms de 2025 |
| `Biiga_03-transformation_D1_engineer_panel-region-annee_v1.csv` | engineer | **La table de base des modèles** : une ligne par région et par année |
| `Biiga_03-transformation_D1_engineer_signaux-violence-region-annee_v1.csv` | engineer | Signaux plus fins de violence par région et par année |
| `Biiga_03-transformation_D1_engineer_violence-acled-region-annee_v1.csv` | engineer | Incidents et morts par région et par année scolaire (agrégat d'ACLED) |
| `Biiga_03-transformation_D1_architect_script-carte-13-regions_v1.py` | architect | Script : reconstitue les contours des 13 anciennes régions |
| `Biiga_03-transformation_D1_architect_script-noms-regions-2025_v1.py` | architect | Script : ajoute les noms de 2025 aux données |
| `Biiga_03-transformation_D1_architect_script-referentiel-regions_v1.py` | architect | Script : correspondance officielle 13 / 17 régions et 45 / 47 provinces |
| `Biiga_03-transformation_D1_engineer_script-panel-et-pistes_v1.py` | engineer | Script : construit le panel région × année (et les pistes P1 à P7) |
| `Biiga_03-transformation_D1_engineer_script-violence-acled_v1.py` | engineer | Script : agrège la violence (ACLED) par région et par année scolaire |

| Dossier | Contenu |
| --- | --- |
| `figures/` | Les figures de l'étape |

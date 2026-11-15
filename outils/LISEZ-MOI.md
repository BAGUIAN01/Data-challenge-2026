# Outils

Ce qui construit les livrables à partir des étapes. Ces fichiers ne font pas partie de l'analyse.

| Fichier | Rôle |
| --- | --- |
| `chemins.py` | Le registre des chemins : où vit chaque fichier du projet. Les scripts lui demandent leurs chemins, et il charge les scripts entre eux. |
| `construire_notebooks.py` | Construit et exécute les cinq cahiers Jupyter, un par étape, à partir des scripts : `python outils/construire_notebooks.py` |
| `construire_rapport.py` | Construit le rapport (LaTeX, XeLaTeX) à partir des données du tableau de bord : `python outils/construire_rapport.py` |
| `construire_soumission.py` | Prépare les fichiers à déposer sur la plateforme, rangés par catégorie et anonymisés pour l'évaluation à l'aveugle : `python outils/construire_soumission.py` |
| `epurer.py` | Retire les commentaires d'un fichier Python |
| `soumission_LISEZ-MOI_*` | Les LISEZ-MOI des trois catégories de la soumission |

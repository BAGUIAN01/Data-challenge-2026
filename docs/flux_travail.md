# Flux de travail — Défi 1, décrochage scolaire

On ne passe à une étape que lorsque la précédente a passé son **contrôle de sortie**. Chaque étape produit un dépôt du challenge et une partie de la documentation de 15 pages.

```
 0 Cadrer ─► 1 Auditer ─► 2 Juger la faisabilité ─► 3 Explorer ─► 4 Construire les indicateurs
                                                                            │
 9 Communiquer ◄─ 8 Rendre reproductible ◄─ 7 Traduire en décisions ◄─ 6 Évaluer ◄─ 5 Modéliser
 
 Tout au long : journal des décisions · journal de l'IA · contrôles
```

| # | Étape | Question | Ce qu'on produit | Contrôle de sortie | Dépôt / partie de la doc. |
| --- | --- | --- | --- | --- | --- |
| 0 | **Cadrer** | Quelle décision veut-on éclairer, pour qui, et comment saura-t-on que ça marche ? | Question reformulée, décideur visé, critères de réussite chiffrés | La question tient en une phrase ; le critère de réussite est mesurable (ex. : battre « comme l'an passé ») | Partie 1 |
| 1 | **Auditer les données** | Qu'a-t-on réellement, et que vaut-il ? | Inventaire (source, maille, période, variables) ; contrôles de cohérence ; comparaison aux publications ; biais connus | Chaque source est datée et citée ; les totaux concordent ; les anomalies sont listées | `01_collecte`, partie 2 |
| 2 | **Juger la faisabilité** | Que peut-on faire, ne pas faire, et que faudrait-il ? | Grille « peut / indicateur de substitution / ne peut pas / il faut » pour chaque attente du défi | Chaque attente du défi a un statut et une justification | Parties 2 et 6 |
| 3 | **Explorer** | Que disent les données ? | Une figure par question, avec son constat et sa limite | Chaque figure répond à une question écrite à l'avance | `04_analyse`, partie 5 |
| 4 | **Construire les indicateurs** | Comment mesurer ce qui n'est pas mesuré directement ? | Définitions et formules ; dictionnaire des variables ; panel propre | Chaque indicateur est vérifié sur un cas connu et sur un sabotage | `02_nettoyage`, `03_transformation`, partie 3 |
| 5 | **Modéliser** | Peut-on expliquer et anticiper ? | Règle de référence d'abord, puis modèle simple, puis apprentissage automatique ; test de l'hypothèse | Validation sur des années non vues ; aucun modèle retenu s'il ne bat pas la référence | `04_analyse`, partie 4 |
| 6 | **Évaluer** | Où et quand le modèle se trompe-t-il ? | Erreurs par région et par année ; incertitude ; ce qui réfuterait l'hypothèse | Les limites sont écrites avant les résultats | Partie 5 |
| 7 | **Traduire en décisions** | Que doit faire un directeur régional ? | Carte des profils, provinces ou régions prioritaires, scénarios, fiches d'une page | Chaque alerte a un levier ; chiffres en nombre d'enfants | `05_interpretation`, partie 6 |
| 8 | **Rendre reproductible** | Quelqu'un d'autre peut-il tout relancer ? | Scripts dans l'ordre, LISEZ-MOI, noms de dépôts normalisés, tableau de bord hors connexion | Une seule commande refait tout, depuis les données brutes | Tous les dépôts, partie 7 |
| 9 | **Communiquer** | Le jury comprend-il en 5 minutes ? | Documentation de 15 pages ; présentation de la finale | Un lecteur extérieur résume la solution en une phrase | Documentation, finale |

**Tout au long du travail :**
- **un journal des décisions** : ce qu'on a choisi, pourquoi, et ce qu'on a écarté ;
- **un journal de l'IA**, exigé par le règlement : ce qui a été demandé, ce qui a été gardé, ce qui a été vérifié à la main ;
- **aucune donnée personnelle**, et prudence sur les cartes liées à la sécurité.

---

## Grille de faisabilité du Défi 1 (étape 2), avec les données actuelles

| Attente du défi | Avec Presco seul | Statut | Ce qu'il faut pour bien faire |
| --- | --- | --- | --- |
| Mesurer le décrochage | Pas d'abandons ni de redoublants | **Substitut** : taux d'achèvement, sorties en excès, survie apparente | Annuaires DGESS avec redoublants et abandons (Data Pack ?) |
| Par région | 13 anciennes régions, 10 ans | **Faisable** | — |
| Par province | Absent | **Impossible** pour l'instant | Annuaires provinciaux (Data Pack) ; table de correspondance des noms |
| 17 nouvelles régions | Les anciennes et les nouvelles ne se recoupent pas | **Impossible** sans les provinces | Données provinciales ; correspondance provinces → nouvelles régions |
| Par sexe | Oui | **Faisable** | — |
| Primaire / post-primaire | Primaire seulement | **Partiel** | Données du post-primaire (autre ministère) |
| Cartographier | Indicateurs par région ; pas de fond de carte | **Faisable** dès qu'on a le fond de carte | Limites des 13 régions (portail HDX ou Data Pack) |
| Expliquer (causes) | Seulement les fermetures d'écoles | **Partiel** : une relation n'est pas une cause | Incidents (ACLED), déplacés (OCHA/CONASUR), pauvreté (EHCVM), population (INSD) |
| Anticiper | Ne bat pas « comme l'an passé » (4,1 points d'erreur) | **Impossible avec Presco seul** (mesuré) | Signaux qui précèdent le choc : incidents, déplacements |
| Tester l'hypothèse « insécurité × précarité » | Pas de mesure de la précarité | **À compléter** | Pauvreté par région ou province (EHCVM, INSD) |
| Scénarios de décision | Relation écoles / élèves (R² = 0,87) | **Faisable**, ordre de grandeur | Nombre d'écoles fermées par zone (OCHA, Data Pack) pour l'actualiser |
| Taux corrigés des déplacements | Taux faussés (taux d'admission de 142 %) | **Signalé**, non corrigé | Population réelle (INSD, OCHA) |

---

## Où on en est

| Étape | État | Ce qui manque |
| --- | --- | --- |
| 0 Cadrer | ◐ fait dans la note d'intention | À mettre à jour avec la réalité des données : 13 régions, taux d'achèvement comme mesure |
| 1 Auditer | ◐ Presco audité (toutes les sommes concordent) | Comparer aux annuaires publiés ; inventaire du Data Pack |
| 2 Faisabilité | ◐ grille ci-dessus | La compléter après lecture du Data Pack |
| 3 Explorer | ● 7 pistes, 7 figures | — |
| 4 Indicateurs | ◐ calculés | Dictionnaire des variables ; contrôles sur un cas connu et sur un sabotage |
| 5 Modéliser | ◐ règle de référence et régression simple | Variables extérieures ; test de l'hypothèse |
| 6 Évaluer | ◐ erreurs par année | Erreurs par région ; incertitude |
| 7 Décisions | ◐ profils et scénarios | Carte, fiches régionales |
| 8 Reproductible | ◐ scripts relançables | Arborescence et noms de dépôts du challenge ; LISEZ-MOI ; tableau de bord |
| 9 Communiquer | ○ | Documentation de 15 pages ; journal de l'IA |

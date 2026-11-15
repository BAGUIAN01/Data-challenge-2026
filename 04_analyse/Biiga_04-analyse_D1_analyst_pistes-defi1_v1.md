# Défi 1 — Les pistes d'analyse avec les données du challenge

Toutes les données viennent du fichier du challenge (préscolaire et primaire, 13 anciennes régions, 2015/16 à 2024/25). Les chiffres sont reproductibles avec les scripts du dossier `scripts/` :
- `Biiga_03-transformation_D1_engineer_script-panel-et-pistes_v1.py` pour les tableaux ;
- `Biiga_04-analyse_D1_analyst_script-figures-pistes_v1.py` pour les graphiques.

Les tableaux complets sont dans `analyse/`, sous les noms `P1_` à `P7_`, ainsi que le panel `panel_region_annee.csv`.

Contrôle préalable : toutes les sommes des données concordent. Voir `controles_qualite.txt`.

---

## Piste 1 — Mesurer le décrochage avec ce que l'on a

**Question.** Les données ne donnent ni les abandons ni les redoublants. Comment mesurer les pertes ?

**Méthode.** Trois indicateurs, du plus direct au plus construit :
1. **Le taux d'achèvement du primaire**, fourni par région et par sexe.
2. **La survie apparente, au niveau national** : l'effectif du CM2 rapporté à celui du CP1 cinq ans plus tôt.
3. **Les sorties en excès, par région.**
   - Pour chaque région et chaque année, les élèves d'une année qui ne sont plus là l'année suivante (hors nouveaux inscrits au CP1).
   - On retire le niveau habituel de la région, mesuré en 2015/16 et 2016/17.
   - On retire aussi la part due aux fins de CM2 normales : la part du CM2 dans les effectifs est passée de 12,5 % à 13,9 %, puis est retombée à 10,7 %.

**Résultats.**
- La survie apparente passe de 74,1 % (cohorte entrée en CP1 en 2015/16) à 55,7 % (cohorte de 2019/20).
- **798 000 élèves** sont sortis en plus de l'habitude entre 2017/18 et 2024/25, en cumul net sur les 13 régions :
  - Boucle du Mouhoun : 134 000 ;
  - Nord : 129 000 ;
  - Est : 123 000 ;
  - Centre-Nord : 118 000 ;
  - Sahel : 76 000.
- Le Centre est négatif (−54 000) : c'est une région d'accueil.

![Sorties en excès](figures/03_sorties_en_exces.png)

**Apport au défi.** Un chiffre en **nombre d'élèves** par région, directement utilisable pour répartir des moyens.

**Limites.**
- Un élève déplacé compte comme une sortie dans sa région d'origine et comme une entrée dans sa région d'accueil. Dans la somme nationale, les deux s'annulent.
- La correction des fins de CM2 suppose que la part du CM2 évolue partout comme au niveau national, car il n'y a pas de niveaux par région.

---

## Piste 2 — Cartographier : quatre profils de régions

**Question.** Toutes les régions décrochent-elles de la même manière ?

**Méthode.** Classification ascendante (méthode de Ward) sur quatre indicateurs centrés et réduits :
- le taux d'achèvement en 2024/25 ;
- son évolution depuis 2015/16 ;
- la pire chute du nombre d'écoles ;
- la pire chute du nombre d'élèves.

**Résultats.**

| Profil | Régions | Signature |
| --- | --- | --- |
| **Effondrement** | Sahel, Est | achèvement de 11 % et 16,5 % ; jusqu'à 90 % et 68 % des écoles perdues |
| **Choc puis reprise partielle** | Centre-Nord, Boucle du Mouhoun | 42 % et 54 % des écoles perdues au pire moment ; achèvement en recul de 18 points |
| **Érosion sans fermetures massives** | Nord, Centre-Est, Cascades | achèvement en recul de 8 à 20 points ; écoles perdues : 15 à 23 % au pire |
| **Stabilité, régions d'accueil** | Centre, Centre-Ouest, Centre-Sud, Hauts-Bassins, Plateau-Central, Sud-Ouest | achèvement stable ou en hausse depuis 2015/16 |

![Achèvement par région](figures/02_achevement_par_region.png)

**Apport au défi.** C'est la cartographie demandée, et chaque profil appelle un levier différent :
- effondrement : réouverture sécurisée et dispositifs d'urgence ;
- choc puis reprise : accompagner le retour des élèves ;
- érosion : agir sur ce qui fait abandonner en cours de cycle ;
- accueil : capacité d'accueil des élèves déplacés.

**Limite.** La carte se trace sur les **13 anciennes régions** : ce sont les données.

---

## Piste 3 — Qui fait reculer l'achèvement national ?

**Question.** Le taux national perd 10,4 points de 2021/22 à 2024/25. Est-ce seulement l'insécurité ?

**Méthode.** On décompose le taux national en moyenne pondérée des taux régionaux. Le poids de chaque région est sa population de 6 ans, déduite des nouveaux inscrits et du taux d'admission. Cette reconstitution retrouve le taux publié à 0,5 point près, chaque année.

**Résultats.**
- Les cinq régions en crise (Est, Sahel, Centre-Nord, Boucle du Mouhoun, Nord) n'expliquent que **55 %** du recul.
- Le Centre-Ouest et les Hauts-Bassins, sans fermetures massives, en expliquent chacun environ 10 %.
- **Toutes les régions reculent sur la période.**

![Contributions](figures/05_contributions_recul_achevement.png)

**Apport au défi.** Une partie du décrochage dépasse l'insécurité. C'est exactement ce que doit tester l'hypothèse de la note : la précarité aggrave-t-elle l'effet de l'insécurité, ou agit-elle seule ?

**Limite.** Les données ne disent pas ce qui fait reculer l'achèvement dans les régions calmes. Deux causes possibles, à vérifier : l'effet retardé de la fermeture des écoles en 2020 (COVID) sur les cohortes, et l'arrivée d'élèves déplacés plus âgés.

---

## Piste 4 — L'entrée repart, la fin de cycle ne suit pas

**Question.** Les effectifs sont au plus haut en 2024/25. Pourquoi l'achèvement est-il au plus bas ?

**Résultats** (national, indice 100 en 2015/16) :
- les nouveaux inscrits au CP1 sont à 127 ;
- les élèves du primaire, à 115 ;
- **les élèves de CM2, à 101.**

Les autres évolutions vont dans le même sens :
- **Statut** : le privé passe de 559 000 à 917 000 élèves (+64 %). Le public dépasse à peine son niveau de 2021/22 et reste sous son maximum de 2017/18 (2,56 millions).
- **Milieu** : l'urbain passe de 783 000 à 1,21 million d'élèves (+54 %). Le rural est au même niveau qu'en 2015/16, mais 12 % sous son maximum de 2017/18.
- **Passages d'un niveau au suivant** : le passage apparent du CM1 au CM2 tombe à 86 % en 2024/25, contre 91 à 98 % avant la crise.

![Entrée et fin de cycle](figures/01_entree_vs_fin_de_cycle.png)

**Apport au défi.** Le problème n'est plus l'entrée à l'école, c'est le **maintien jusqu'au CM2**. Cela oriente les leviers :
- accompagner le retour des élèves dans les écoles rouvertes (chantier 2 du ministère) ;
- développer les passerelles pour les enfants plus âgés (chantier 9) ;
- suivre de près le milieu rural.

**Limite.** Les données par niveau ne sont que nationales : on ne peut pas localiser cette perte de fin de cycle par région.

---

## Piste 5 — Garçons et filles

**Résultats.**
- En 2024/25, les garçons achèvent moins que les filles **partout sauf au Sahel** (écart de −0,7 point).
- Les écarts les plus forts sont dans le Centre-Ouest (13,5 points), le Plateau-Central (12,3 points) et les Hauts-Bassins (11,3 points).
- Les deux sexes ont reculé depuis 2021/22, dans toutes les régions.

![Garçons et filles](figures/06_garcons_filles.png)

**Apport au défi.** Au primaire, le **risque pèse plus sur les garçons**. Les filles le sont surtout au Sahel, et probablement après le primaire, mais les données ne couvrent pas le post-primaire. La note insistait sur les filles : à nuancer en finale.

---

## Piste 6 — Anticiper

**Question.** Peut-on prévoir le taux d'achèvement de l'année suivante ?

**Méthode.** Chaque année est prédite par un modèle entraîné uniquement sur les années précédentes. Trois prévisions sont comparées :
1. **« comme l'an passé »** ;
2. **la tendance moyenne** ;
3. **une régression** sur les signaux de l'année : variation des écoles, variation des effectifs, variation du taux.

**Résultats.**

| Méthode | Erreur moyenne |
| --- | --- |
| « Comme l'an passé » | 4,11 points |
| Tendance moyenne | 4,11 points |
| Régression | **4,58 points** |

- La régression fait moins bien que la règle simple.
- Les fermetures d'une année n'annoncent pas l'achèvement de la suivante : r = 0,12.
- L'erreur culmine en 2022/23 (7,2 points) : le choc n'était pas prévisible avec ces données.

![Prévision](figures/07_prevision.png)

**Apport au défi.** C'est un résultat honnête et utile. **Pour anticiper, il faut des signaux extérieurs qui précèdent le choc** : incidents sécuritaires (ACLED) et déplacements de population (CONASUR). C'est la justification directe de la méthode de la note. Le score à battre est connu : **4,1 points d'erreur moyenne**.

**Limite.** On ne dispose que de 104 observations (régions × années) : il faut des modèles simples et explicables.

---

## Piste 7 — Scénarios pour décider

**Question.** Que rapporterait la réouverture des écoles ?

**Méthode.** Sur 117 variations annuelles, 1 % d'écoles en moins va avec **0,78 % d'élèves en moins** (R² = 0,87). On applique ce rapport à deux scénarios.

![Écoles et élèves](figures/04_ecoles_et_eleves.png)

**Résultats.**

| Scénario | Écoles à rouvrir | Élèves attendus en plus |
| --- | --- | --- |
| A — retour au niveau de 2021/22 | 757, dont 303 au Centre-Nord | environ 148 000, dont 62 000 au Centre-Nord |
| B — retour au niveau maximal de chaque région | 2 976, dont 850 au Sahel et 751 dans l'Est | environ 570 000 |

Le scénario B est un **ordre de grandeur** : il sort largement des variations observées.

**Apport au défi.** C'est l'outil de décision : où rouvrir en priorité, et pour combien d'élèves.

**Limite.** Cette relation n'est pas une cause démontrée : une école fermée ne déclare plus d'élèves. Elle mesure la reprise attendue si les élèves reviennent comme ils sont partis.

---

## Ce que les données imposent à la solution

| Prévu dans la note | Adapté aux données |
| --- | --- |
| Abandon par cohorte et par région | Taux d'achèvement, sorties en excès et survie apparente (pistes 1 et 4) |
| 17 régions et 47 provinces | 13 anciennes régions |
| Insécurité, précarité, éloignement | À ajouter depuis l'extérieur (ACLED, CONASUR, EHCVM) : indispensable pour anticiper (piste 6) |
| Test de l'hypothèse multiplicative | Sur le panel de 130 observations : l'insécurité frappe-t-elle plus fort là où la précarité est élevée ? |
| Un levier par région | Les quatre profils de la piste 2 et les scénarios de la piste 7 |

## Prochaines étapes proposées

1. **Récupérer les données extérieures**, par ancienne région et par année (2015 à 2025) : incidents ACLED, déplacés CONASUR, pauvreté EHCVM.
2. **Construire le modèle d'anticipation** et le comparer à « comme l'an passé ».
3. **Tracer la carte des quatre profils.** Il faut le fond de carte des 13 anciennes régions, disponible sur le portail HDX.
4. **Rédiger une fiche d'une page par région** et monter le tableau de bord hors connexion.

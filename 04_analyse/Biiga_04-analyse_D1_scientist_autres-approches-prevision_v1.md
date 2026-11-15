# Défi 1 — Deux approches de prévision qui marchent, chacune dans son domaine

*Scripts : `04_analyse/Biiga_04-analyse_D1_scientist_script-approches-prevision_v1.py` (sorties brutes : `analyse/resultats_approches_prevision.txt`, tableaux `P12_*`) et `05_interpretation/Biiga_05-interpretation_D1_analyst_script-figures-solution_v1.py`.*

## Point de départ

Prévoir **à l'aveugle** la variation de l'an prochain ne marche pas. Dans les tests précédents, aucun modèle ne bat « comme l'an passé » :
- signaux internes ;
- violence ACLED ;
- interaction insécurité × pauvreté ;
- Ridge, forêt aléatoire et gradient boosting.

Deux approches reposent sur une autre logique : utiliser une information **connue avant les statistiques**, ou la **mécanique des classes**. Elles ont été testées avec le même protocole, sur des années que les modèles n'ont pas vues.

## A. Prévoir les effectifs dès qu'on connaît les écoles ouvertes à la rentrée

**Idée.** Le nombre d'écoles qui fonctionnent en octobre est suivi par l'administration en cours d'année. L'annuaire statistique, lui, sort des mois plus tard. On apprend sur les années passées le lien entre « variation des écoles » et « variation des élèves ». On l'applique ensuite à l'année à prévoir.

**Résultat** (13 régions, 7 années de test, pente apprise sur les années antérieures seulement) :

| | Erreur moyenne |
| --- | --- |
| « Comme l'an passé » | 8,6 % des effectifs |
| **À partir des écoles ouvertes** | **4,2 %** (−51 %) |

- Le gain est le plus fort l'année du choc : 5,5 % contre 15,4 % en 2022/23. L'approche capte donc les fermetures, que les autres modèles ratent.
- Elle perd une seule année sur sept (2020/21).
- **Aucun gain sur le taux d'achèvement** : 3,97 points d'erreur contre 3,95.
- **Le lien est stable.** Sur toute la période, 10 % d'écoles en moins correspondent à environ 7,8 % d'élèves en moins (corrélation 0,93). La pente apprise varie entre 0,68 et 0,93 d'une année à l'autre, sauf la première (0,37, apprise sur deux années seulement).

**Ce que ça change.** Ce test valide, hors échantillon, le mécanisme des scénarios de réouverture (tableau P7 : 757 écoles rouvertes, environ 148 000 élèves). On peut donc répondre à une question de décideur : « si on rouvre tant d'écoles dans telle région, combien d'élèves retrouve-t-on ? »

**Limite.** On a testé avec le nombre d'écoles de l'annuaire. En usage réel, il faut le compte des écoles ouvertes tenu en cours d'année, par exemple celui du suivi de l'éducation en situation d'urgence. Ce compte n'est pas dans les données du challenge. Sans lui, pas de prévision 2025/26 par région.

![Écoles ouvertes](figures/13_prevision_ecoles_ouvertes.png)

## B. La filière des cohortes : le CM2 de demain est dans le CM1 d'aujourd'hui

**Idée.** Les élèves de CM2 l'an prochain sont, pour l'essentiel, les CM1 de cette année. On applique le dernier taux de passage observé. Les niveaux de classe ne sont publiés qu'au **national** : l'approche ne se fait pas par région.

**Résultats sur les années passées :**

| Horizon | Filière | « Comme l'an passé » |
| --- | --- | --- |
| CM2, un an avant | 5,4 % | 5,3 % |
| CM2, deux ans avant | **9,1 %** | 10,7 % |
| Taux d'achèvement, un an avant | 3,8 points | **2,3 points** |

**Lecture :**
- **En niveau, un an à l'avance**, la filière ne bat pas la règle simple.
- **Deux ans à l'avance**, elle fait un peu mieux, sur 7 années seulement.
- **Elle ne se traduit pas en taux d'achèvement.** Le dénominateur implicite du taux (élèves de CM2 / taux) bouge de −3 % à +10 % d'une année à l'autre, pour des raisons absentes des données : projections de population, redoublants.

**Ce qu'elle apporte quand même : le sens de la prochaine variation.** En 2024/25, il y avait 441 000 élèves en CM1 pour 354 000 en CM2.

| | CM2 2025/26 |
| --- | --- |
| Projection (dernier passage, 86,2 %) | **≈ 380 000**, soit +7 % |
| Pire passage observé (81,8 %, année du choc) | ≈ 361 000, soit +2 % |
| Meilleur passage observé (98,1 %) | ≈ 433 000 |

- **Bilan passé.** Le sens a été juste 5 années sur 7, et la fourchette n'a tenu que 4 fois sur 7.
- **Les deux erreurs de sens** (2021/22 et 2024/25) suivaient l'annonce d'une hausse faible (+1,7 %). Cette fois, la hausse annoncée est de +7 %.
- **Conclusion prudente :** le nombre d'élèves en CM2 devrait remonter en 2025/26, sauf nouveau choc. C'est une tendance probable, pas un chiffre garanti.

![Cohortes](figures/14_projection_cohortes.png)

## C. Ce qu'annoncent les grandes cohortes de CP1 (scénario, pas une prévision)

**Les entrées en CP1 sont au plus haut :**
- 711 000 élèves en 2023/24 ;
- 772 000 en 2024/25, contre 586 000 en 2022/23.

**Ce n'est pas une anomalie d'âge.** Le taux brut d'admission national est revenu à 100-101 %, son niveau d'avant la crise (100 à 105 % en 2015-2018). C'est la croissance de la population plus le retour après les fermetures.

**La survie apparente du CP1 au CM2 s'est effondrée** : de 74 % (CM2 2020/21) à 56 % (CM2 2024/25). C'est l'indicateur national le plus direct du décrochage dans ces données.

**Scénario pour les cohortes à venir :**

| Cohorte CP1 | Arrive en CM2 | Si la survie reste à 56 % | Si elle revient à 74 % |
| --- | --- | --- | --- |
| 2023/24 (711 000) | 2028/29 | ≈ 396 000 | ≈ 527 000 |
| 2024/25 (772 000) | 2029/30 | ≈ 430 000 | ≈ 572 000 |

**L'écart entre les deux colonnes, environ 140 000 enfants pour la seule cohorte 2024/25, mesure l'enjeu du décrochage pour cette génération.** Ce sont les élèves qui entrent aujourd'hui à l'école. Agir sur leur maintien dans les cinq prochaines années est la cible d'anticipation la plus concrète que ces données permettent.

## Ce qu'on retient

1. **Prévoir à l'aveugle** la variation de l'an prochain reste hors de portée. La règle « comme l'an passé » et sa fourchette restent la référence (décisions D6 et D11).
2. **Prévoir les effectifs** est possible dès qu'on connaît les écoles ouvertes à la rentrée : l'erreur est divisée par deux. C'est un outil de **prévision conditionnelle** pour le ministère, qui dispose de cette information.
3. **Le sens de la variation du CM2** se lit dans le CM1 : remontée probable en 2025/26.
4. **L'enjeu à cinq ans** se chiffre : selon que la survie reste basse ou remonte, la génération entrée en CP1 en 2024/25 comptera environ 430 000 ou 572 000 élèves en CM2.

# La formule du risque de baisse des effectifs

Le risque affiché par le tableau de bord est **la probabilité que les effectifs du primaire d'une région baissent de plus de 5 % l'année suivante**. Une baisse de plus de 5 % des effectifs est le signal de décrochage retenu : il n'y a ni abandons ni redoublants dans les données (décision D3).

C'est une régression logistique apprise sur la violence seule (décisions D12 et D17). Coefficients calculés par `scripts/formule_risque.py`, enregistrés dans `analyse/P17_formule_risque.csv`.

## La formule de référence (rentrée 2026/27)

$$
p = \frac{1}{1 + e^{-z}}
$$

$$
z = -5{,}7659 + 0{,}9814 \cdot \ln(1 + I_t) + 0{,}8626 \cdot \big[\ln(1 + I_t) - \ln(1 + I_{t-1})\big]
$$

- $I_t$ : incidents de sécurité de la région pendant l'année scolaire $t$, d'octobre à septembre (ACLED, violence politique) ;
- $I_{t-1}$ : les mêmes incidents l'année scolaire d'avant ;
- le premier terme mesure le **niveau** de la violence, le second son **escalade**.

On peut l'écrire sans crochets : $z = -5{,}7659 + 1{,}8440 \cdot \ln(1 + I_t) - 0{,}8626 \cdot \ln(1 + I_{t-1})$.

**Exemple, Yaadga (ancienne région du Nord).** On a $I_t = 250$ incidents d'octobre 2025 à septembre 2026, et $I_{t-1} = 131$ l'année d'avant.
- $\ln(251) = 5{,}525$ ; $\ln(132) = 4{,}883$ ; l'escalade vaut $0{,}643$.
- $z = -5{,}766 + 0{,}9814 \times 5{,}525 + 0{,}8626 \times 0{,}643 = 0{,}211$.
- $p = 1 / (1 + e^{-0{,}211}) = 55\ \%$ : c'est le chiffre affiché.

## Les deux mises à jour du calendrier d'alerte (D17)

| Modèle | $z$ |
| --- | --- |
| Alerte de septembre (juillet à septembre connus) | $-5{,}8035 + 0{,}4232 \ln(1+I_t) + 0{,}9158\,\Delta + 0{,}7915 \ln(1+J_t)$ |
| Alerte de janvier (octobre à décembre connus) | $-6{,}4210 + 0{,}3290 \ln(1+I_t) + 0{,}9519\,\Delta + 1{,}0732 \ln(1+R_{t+1})$ |

Les symboles :
- $\Delta = \ln(1+I_t) - \ln(1+I_{t-1})$, l'escalade ;
- $J_t$ : les incidents de juillet à septembre, juste avant la rentrée ;
- $R_{t+1}$ : les incidents d'octobre à décembre de l'année qui commence.

## Comment elle a été apprise

- **Données** : 104 couples région × année (13 régions, 2016/17 à 2023/24), dont 19 baisses de plus de 5 %.
- **Méthode** : régression logistique de scikit-learn (C = 1, variables centrées réduites pendant l'apprentissage). Les coefficients sont ramenés aux unités d'origine : $\beta_j = b_j / \sigma_j$ et $\beta_0 = b_0 - \sum_j b_j \mu_j / \sigma_j$.
- **Fiabilité, sur des années que le modèle n'avait pas vues** : AUC de 0,83 pour la référence, 0,85 avec l'alerte de septembre, 0,88 avec l'alerte de janvier (1 = parfait, 0,5 = hasard).
- **Vérification** : la formule redonne, pour les 13 régions et les trois modèles, exactement les probabilités affichées (écart maximal : 0 point).

## Ce qu'on en fait

| Niveau de risque | Probabilité |
| --- | --- |
| Élevé | 40 % ou plus |
| Moyen | de 15 à 39 % |
| Faible | moins de 15 % |

La priorité croise ce risque avec le taux d'achèvement 2024/25 ($TAP$), comparé à la moyenne du pays (51,6 %) :

| Priorité | Règle |
| --- | --- |
| 1, agir maintenant | $TAP < 51{,}6\ \%$ **et** $p \geq 40\ \%$ |
| 2, veille renforcée | $TAP < 51{,}6\ \%$ **ou** $p \geq 15\ \%$, sans être en priorité 1 |
| 3, consolider | les autres régions |

Ces probabilités classent bien les régions, mais restent approximatives (Brier 0,166 contre 0,169 pour le taux de base) : on lit des niveaux, pas des pourcentages exacts.

## Le score global : les deux formes de décrochage en un chiffre

$$
\text{score} = 100 \times \Big( 0{,}5 \cdot p + 0{,}5 \cdot \big(1 - \tfrac{TAP}{100}\big) \Big)
$$

- $p$ : la probabilité de chute des effectifs (la formule ci-dessus). Elle mesure le décrochage **brutal**, porté par la violence.
- $1 - TAP/100$ : la part d'enfants qui n'achèvent pas le primaire. Elle mesure le décrochage **lent** : pauvreté, faim, grossesses précoces, instruction des mères.
- **Les poids** (moitié, moitié) ont été fixés avant le test. Les bornes sont fixes (0 et 1) : le score d'une région ne dépend que de ses propres données.

**Exemple, Yaadga.** $p = 0{,}55$ et $TAP = 46{,}4\ \%$, donc score $= 100 \times (0{,}5 \times 0{,}55 + 0{,}5 \times 0{,}536) = 54$. Yaadga est 4e sur 13.

Les cinq régions en tête du score (Goulmou + Sirba + Tapoa 66, Liptako + Soum 65, Koulsé 60, Yaadga 54, Bankui + Sourou 52) sont exactement les cinq régions en priorité 1. Calcul : `scripts/score_global.py`, résultats dans `analyse/P18_*.csv`.

**Rejoué sur le passé** (2019/20 à 2023/24, avec seulement l'information de chaque année) :

| Mesure | AUC, chute de l'année suivante | Fortes baisses repérées | Élèves perdus repérés |
| --- | --- | --- | --- |
| Score global | 0,80 | 64 % | 65 % |
| Risque seul | 0,83 | 64 % | 65 % |
| Achèvement seul | 0,72 | 71 % | 69 % |
| Priorité 1 de la matrice | — | 71 % | 69 % |

Pour comparer à égalité, on retient chaque année autant de régions que la matrice en met en priorité 1.

**Ce qu'on en retient : le score résume, il ne cible pas mieux.** Il est affiché comme résumé lisible. Pour cibler, la règle reste la priorité de la matrice : sur le passé, elle repère plus de fortes baisses et plus d'élèves perdus.

Changer le poids du risque entre 0,3 et 0,7 fait varier l'AUC de 0,77 à 0,81. Ce test est donné pour information : il n'a pas servi à choisir le poids.

## Le facteur dominant : sur quoi agir

Pour chaque région, on cherche le facteur de fond qui pèse le plus. Pour un facteur $f$ et une région $r$ :

$$
\text{poids}(r, f) = |\rho_f| \times z_{r,f}
$$

- $z_{r,f}$ : l'écart de la région à la moyenne des 13 régions, en écarts-types. Il est orienté pour qu'une valeur positive veuille dire **plus exposé** ; pour le préscolaire, c'est une valeur basse qui expose.
- $|\rho_f|$ : la force du lien du facteur avec l'achèvement 2024/25 sur les 13 régions (`analyse/P14_facteurs_correlations.csv`).

| Facteur | Violence | Femmes sans instruction | Déplacés | Faim | Grossesses précoces | Pauvreté | Préscolaire |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $\lvert\rho_f\rvert$ | 0,92 | 0,85 | 0,83 | 0,72 | 0,72 | 0,69 | 0,55 |

Le **facteur dominant** est celui qui a le plus grand poids. L'action proposée est le levier de ce facteur ; le deuxième poids donne la suite. Si aucun poids n'est positif, la région n'a aucun facteur au-dessus de la moyenne : on consolide. Le CEP est laissé de côté, car ce n'est pas un signal de risque (effet de sélection, décision D15).

| Facteur dominant | Régions | Levier |
| --- | --- | --- |
| Violence | Goulmou + Sirba + Tapoa, Bankui + Sourou, Nakambé | Continuité éducative : écoles délocalisées, enseignement à distance, radio |
| Grossesses précoces | Koulsé, Tannounyan, Djôrô | Maintien des filles à l'école, lutte contre le mariage d'enfants |
| Déplacés | Liptako + Soum | Places d'accueil, classes passerelles, inscription sans pièces |
| Pauvreté | Yaadga | Cantines scolaires, aides aux familles, fournitures |
| Préscolaire | Nazinon | Préscolaire communautaire |
| Aucun au-dessus de la moyenne | Guiriko, Oubri, Nando, Kadiogo | Consolider |

Calcul : `scripts/facteur_dominant.py`, résultats dans `analyse/P19_facteur_dominant.csv`.

Ce facteur **explique et oriente l'action, il ne prévoit pas** (décision D16). Avec 13 régions, c'est une lecture d'orientation : le deuxième facteur est souvent proche du premier, et l'écran donne les deux.

## Les deux autres prévisions de l'application

- **Élèves de l'année, à partir des écoles ouvertes à la rentrée** (D13) : $\ln(E_{t+n}/E_{2024/25}) = 0{,}0197\,n + 0{,}7784 \cdot \ln(O_{t+n}/O_{2024/25})$.
  - $E$ : les élèves ;
  - $O$ : les écoles ouvertes ;
  - $n$ : le nombre d'années depuis l'annuaire 2024/25.

  L'erreur moyenne est de ± 4,2 % à un an, contre ± 8,6 % en reprenant les effectifs de l'année d'avant.
- **Taux d'achèvement 2025/26** (D14) : celui de 2024/25 (« comme l'an passé »). Aucun modèle testé ne fait mieux. La fourchette est tirée des erreurs passées de cette règle.

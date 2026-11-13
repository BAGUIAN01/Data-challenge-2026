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

## Les deux autres prévisions de l'application

- **Élèves de l'année, à partir des écoles ouvertes à la rentrée** (D13) : $\ln(E_{t+n}/E_{2024/25}) = 0{,}0197\,n + 0{,}7784 \cdot \ln(O_{t+n}/O_{2024/25})$.
  - $E$ : les élèves ;
  - $O$ : les écoles ouvertes ;
  - $n$ : le nombre d'années depuis l'annuaire 2024/25.

  L'erreur moyenne est de ± 4,2 % à un an, contre ± 8,6 % en reprenant les effectifs de l'année d'avant.
- **Taux d'achèvement 2025/26** (D14) : celui de 2024/25 (« comme l'an passé »). Aucun modèle testé ne fait mieux. La fourchette est tirée des erreurs passées de cette règle.

# Défi 1 — Anticiper et tester l'hypothèse (fin de l'analyse)

*Script : `04_analyse/Biiga_04-analyse_D1_scientist_script-prevision-hypothese_v1.py` (sorties brutes : `analyse/resultats_prevision_hypothese.txt`). Figures : `04_analyse/Biiga_04-analyse_D1_scientist_script-figures-prevision_v1.py`.*

## 1. Prévision prudente du taux d'achèvement pour 2025/26

**Pourquoi 2025/26 ?** Les données s'arrêtent en 2024/25 ; or nous sommes en novembre 2026. L'annuaire a donc **au moins un an de retard**, ce qui est exactement le problème posé dans la note d'intention. La prévision comble ce trou.

**Méthode.**
- La prévision reprend le taux de 2024/25, puisque c'est la règle qu'aucun modèle n'a battue (pistes 6 et 8).
- La **fourchette à 80 %** est faite des variations observées d'une année à l'autre, entre −6,5 et +4,4 points.

**Fiabilité mesurée.** Construite chaque fois sur les seules années passées, la fourchette a contenu la valeur réelle **73 % du temps**, pour 80 % visés. Elle n'en a contenu que **46 % l'année du choc** (2022/23). Elle est donc un peu trop étroite, et on le dit.

**Volume.** Dans chaque région, on estime le nombre d'enfants d'environ 11 ans qui n'atteignent pas le CM2 : (1 − taux d'achèvement) × population de 11 ans (INSD 2024). Au total, cela fait **environ 292 000 enfants**. Le classement par volume n'est pas le classement par taux :

| Rang | Région | Enfants qui n'atteignent pas le CM2 |
| --- | --- | --- |
| 1 | Goulmou + Sirba + Tapoa | environ 50 600 |
| 2 | Koulsé | environ 42 000 |
| 3 | Bankui + Sourou | environ 35 300 |

Liptako + Soum, au taux le plus bas, n'arrive qu'en 4e position (environ 28 200), parce que sa population est plus petite.

![Prévision et alerte](figures/09_prevision_alerte.png)

## 2. Alerte d'escalade de la violence

**Règle**, fixée avant de regarder le résultat : une région est en alerte quand les incidents ACLED d'octobre à septembre sont **au moins 1,5 fois** ceux de l'année d'avant, **et au moins 30**.

**Bilan historique** (104 régions-années) :

| | Après une alerte | Sans alerte |
| --- | --- | --- |
| Part des cas suivis d'une baisse d'effectifs de plus de 5 % | **55 %** (12 cas sur 22) | **9 %** |

Sur les 19 fortes baisses d'effectifs observées, **12 avaient été précédées d'une alerte**.

**Ce que ça veut dire.** L'alerte ne prédit pas un chiffre : la prévision chiffrée ne bat pas « comme l'an passé ». Elle **désigne bien les régions à surveiller** : une baisse y est environ 6 fois plus fréquente.

**Alertes actuelles**, pour la rentrée 2026/27, calculées sur les incidents d'octobre 2025 à septembre 2026 :
- **Yaadga** : 131 puis 250 incidents. C'est une région du profil « érosion », déjà en recul de 20 points.
- **Guiriko** : 24 puis 39 incidents. Région stable jusqu'ici.

Aucune alerte n'était levée pour la rentrée 2025/26.

## 3. Hypothèse « insécurité × pauvreté »

Panel de 104 régions-années. La variable expliquée est la variation du taux d'achèvement l'année suivante. Les intervalles viennent d'un bootstrap par région (2 000 tirages).

| Terme | Effet (points) | Intervalle de confiance à 95 % | Lecture |
| --- | --- | --- | --- |
| Insécurité (log des incidents) | **−1,01** | [−1,41 ; −0,62] | **Effet net** : plus de violence, plus de recul l'année suivante |
| Pauvreté (par tranche de 10 points) | −0,18 | [−0,56 ; +0,33] | Pas d'effet détecté |
| Insécurité × pauvreté | +0,14 | [−0,38 ; +0,25] | **Pas d'effet de cumul détecté** |

Erreur moyenne sur les années non vues :

| Modèle | Erreur moyenne |
| --- | --- |
| « Comme l'an passé » | 4,11 points |
| Modèle additif | 4,24 points |
| Modèle avec interaction | 4,46 points |

**Conclusion.** À l'échelle régionale, l'hypothèse de renforcement n'est **pas confirmée**. Comme la note l'avait prévu, nous le disons. En revanche, l'insécurité a un effet propre et net.

En vue transversale (2021/22 à 2024/25), **toutes les régions reculent, riches ou pauvres**. Le Centre-Ouest et le Centre-Sud perdent environ 12 points sans violence notable. Une partie du recul de l'achèvement a une **cause nationale** que ces données ne permettent pas d'identifier.

![Hypothèse](figures/10_hypothese_insecurite_pauvrete.png)

**Limites.**
- Il n'y a que 13 régions.
- La pauvreté n'est connue qu'en 2021, et elle est en partie une conséquence de la crise : le Sahel a gagné 32 points de pauvreté depuis 2018.
- Ce sont des corrélations écologiques, pas des comportements individuels.
- Le facteur « éloignement » de la note n'a pas pu être mesuré.

## 4. Attaques contre l'éducation (Insecurity Insight)

Les données comptent 188 incidents de 2017 à 2026. Elles annoncent **moins bien** les fermetures d'écoles de l'année suivante que l'ensemble de la violence :

| Indicateur | Corrélation avec la variation des écoles l'année suivante |
| --- | --- |
| Attaques contre l'éducation | r = −0,23 |
| Ensemble des incidents ACLED | r = −0,32 |

Elles ne sont gardées que comme contexte.

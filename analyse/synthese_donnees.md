# Données du challenge — première analyse (Défi 1)

Fichier analysé : `data/raw/Presco.txt`. Les chiffres ci-dessous sont reproductibles avec les scripts de `scripts/` :
- `parse_presco.py` transforme le fichier en tableau propre ;
- `check_presco.py` contrôle sa cohérence ;
- `analyse_presco.py` produit les tableaux de `analyse/`.

## 1. Ce que contiennent les données

21 tableaux, de 2015/2016 à 2024/2025 (10 années), sur les **13 anciennes régions**.

| Cycle | Tableaux |
| --- | --- |
| Préscolaire | effectifs par région, statut, milieu et niveau ; taux brut de scolarisation et parité ; structures et salles par région et statut |
| Primaire | effectifs par région et sexe, par statut, par milieu ; effectifs par niveau (CP1 à CM2), **au niveau national seulement** ; nouveaux inscrits au CP1, taux brut d'admission, taux brut de scolarisation, **taux d'achèvement**, réussite au CEP et parités, par région et sexe ; nombre d'écoles par région et statut |

Ce qui manque : les redoublants, les abandons, les provinces, le post-primaire, et les effectifs par niveau et par région.

## 2. Qualité des données

Toutes les sommes concordent :
- garçons + filles = total, sur 827 cas ;
- somme des régions = national ;
- même total national d'un tableau à l'autre ;
- somme des statuts et des niveaux = total ;
- indices de parité = taux des filles divisé par taux des garçons.

Anomalies relevées :
- **Préscolaire, taux de scolarisation 2019/2020** : le Sahel et le Sud-Ouest ont exactement les mêmes valeurs. C'est une ligne recopiée. L'indice de parité du Centre vaut 1,00 cette année-là, alors que le calcul donne 0,91.
- **Taux d'admission au-dessus de 130 %** dans le Nord (142 % en 2023/2024), le Centre et le Plateau-Central, et **taux d'achèvement des filles au-dessus de 100 %** dans le Centre. Les populations de référence (projections) ne suivent pas les déplacements : dans les régions d'accueil, les taux sont gonflés, et dans les régions de départ, ils sont probablement écrasés. **Les effectifs bruts sont plus fiables que les taux.**
- **Préscolaire 2024/2025** : forte hausse dans plusieurs régions, cohérente avec le chantier du ministère. Le document des chantiers annonce 2 501 structures, et c'est exactement le total du tableau 7 pour 2024/2025.

## 3. Ce que disent les données

1. **Le choc de 2022/2023.** Au niveau national :
   - les effectifs du primaire passent de 3 174 946 à 2 835 544 (−10,7 %) ;
   - le nombre d'écoles, de 14 427 à 12 780 ;
   - le taux brut de scolarisation, de 85,8 % à 74,4 %.
2. **L'entrée repart, l'achèvement s'effondre.** En 2024/2025, les effectifs atteignent un record (3 308 096), de même que les nouveaux inscrits au CP1 (768 940). Mais le taux d'achèvement tombe à son plus bas niveau de la décennie, 51,6 %, contre 62,0 % en 2021/2022. Chez les garçons, il est de 47,7 %.
3. **La survie apparente du CP1 au CM2** (effectif du CM2 rapporté à celui du CP1 cinq ans plus tôt) passe de 74,1 % pour la cohorte entrée en 2015/2016 à 55,7 % pour celle de 2019/2020. Chez les garçons, elle va de 65,3 % à 49,2 % ; chez les filles, de 83,7 % à 62,7 %.
4. **Cinq régions décrochent nettement :**

   | Région | Taux d'achèvement | Écoles |
   | --- | --- | --- |
   | Est | 40,2 % → 16,5 % | −59 % |
   | Sahel | 11,1 % en 2024/2025 | −82 %, il en reste 187 |
   | Centre-Nord | 45,9 % → 27,7 % | — |
   | Boucle du Mouhoun | 55,1 % → 37,2 % | — |
   | Nord | 66,9 % → 46,4 % | — |

   Le Centre, les Hauts-Bassins, le Centre-Ouest et le Centre-Sud se maintiennent ou progressent. Ce sont des régions d'accueil.
5. **Les écoles fermées expliquent l'essentiel des variations d'effectifs.** Sur 117 variations annuelles (13 régions sur 9 ans), 1 % d'écoles en moins va avec 0,78 % d'élèves en moins (R² = 0,87). La composante « choc » domine.
6. **En primaire, ce sont surtout les garçons qui n'achèvent pas.** L'indice de parité du taux d'achèvement vaut 1,16 au niveau national (les filles sont devant), et 1,30 dans le Centre-Nord. La seule exception est le Sahel (0,94), où les filles sont derrière.
7. **Repère pour la prévision.** La règle « comme l'an passé » appliquée au taux d'achèvement régional se trompe en moyenne de 3,75 points. L'erreur monte à 7,2 points en 2022/2023, et jusqu'à 21,5 points dans la Boucle du Mouhoun. Notre modèle devra faire mieux.
8. **Piste à vérifier.** Le passage apparent du CM1 au CM2 tombe à 86 % en 2024/2025, contre 91 à 98 % avant la crise (2022/2023 mis à part). Les pertes semblent se déplacer vers la fin du cycle.

## 4. Conséquences pour la méthode de la note

| Ce que la note prévoyait | Avec ces données |
| --- | --- |
| Taux d'abandon par cohorte, par région | Impossible : il n'y a ni redoublants ni niveaux par région. On le remplace par le taux d'achèvement et les sorties apparentes (par région), et par la survie apparente (au niveau national). |
| 17 régions et 47 provinces | Impossible : seulement les 13 anciennes régions. L'analyse se fait sur 13 régions, et on le dit. |
| Correction par les rapports de rentrée | Absents des données. Le nombre d'écoles sert d'indicateur du choc. |
| Test de l'hypothèse multiplicative | Faisable sur 130 observations (région × année). L'insécurité varie dans le temps ; la précarité et l'éloignement varient peu. Le test porte donc sur l'interaction : l'insécurité fait-elle plus de dégâts là où la précarité est forte ? |
| Prévision face à « comme l'an passé » | Faisable : 10 années permettent de tester sur des années non vues. L'objectif à battre est de 3,75 points d'erreur moyenne. |
| Insécurité, précarité, éloignement | À ajouter depuis l'extérieur : ACLED par région et par année, pauvreté EHCVM par région, distance aux écoles. |

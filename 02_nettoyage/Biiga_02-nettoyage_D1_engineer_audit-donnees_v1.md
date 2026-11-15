# Étape 1 — Audit des données : ce qu'on a, ce qu'on a vu, ce qu'on peut en faire

*Données principales du challenge : « Données statistiques préscolaire et primaire 2016-2025 » (source : DGESS, ministère de l'Éducation nationale), reçues sous la forme du fichier `Presco.txt`.*
*Tous les contrôles sont reproductibles : `02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-lecture-challenge_v1.py`, puis `02_nettoyage/Biiga_02-nettoyage_D1_engineer_script-controles-coherence_v1.py`.*

---

## 1. Ce qu'on a

### Le fichier

| Élément | Constat |
| --- | --- |
| Format | Feuille Excel exportée en texte, colonnes séparées par des tabulations, encodage UTF-8, fin de ligne Windows |
| Taille | 71 475 octets, 1 569 lignes, dont 1 019 vides |
| Contenu | **21 tableaux** : 8 pour le préscolaire, 13 pour le primaire |
| Période | 10 années scolaires, de 2015/2016 à 2024/2025 |
| Territoire | **13 anciennes régions** et le niveau national ; aucune province |
| Après mise à plat | **6 621 valeurs**, une ligne par valeur (`02_nettoyage/Biiga_02-nettoyage_D1_engineer_donnees-challenge-propres_v1.csv`) |

### Les 21 tableaux

| Code | Cycle | Indicateur | Ventilé par | Maille |
| --- | --- | --- | --- | --- |
| P1 | Préscolaire | Effectifs | sexe | région |
| P2 | Préscolaire | Effectifs | sexe, statut (public, privé, communautaire) | national |
| P3 | Préscolaire | Effectifs | sexe, milieu — **2017/18 à 2024/25 seulement** | national |
| P4 | Préscolaire | Effectifs | sexe, statut, section (petite, moyenne, grande) | national |
| P5 | Préscolaire | Taux brut de scolarisation (%) | sexe | région |
| P6 | Préscolaire | Indice de parité du taux brut de scolarisation | — | région |
| P7 | Préscolaire | Nombre de structures | statut | région |
| P8 | Préscolaire | Nombre de salles de classe | statut | région |
| E1 | Primaire | Effectifs | sexe | région |
| E2 | Primaire | Effectifs | sexe, statut (public, privé) | national |
| E3 | Primaire | Effectifs | sexe, milieu (urbain, rural) | national |
| E4 | Primaire | Effectifs | sexe, statut, **niveau (CP1 à CM2)** | **national** |
| E5 | Primaire | Nouveaux inscrits au CP1 | sexe | région |
| E6 | Primaire | Taux brut d'admission (%) | sexe | région |
| E7 | Primaire | Taux brut de scolarisation (%) | sexe | région |
| E8 | Primaire | **Taux d'achèvement du primaire (%)** | sexe | région |
| E9 | Primaire | Taux de réussite au CEP (%) | sexe | région |
| E10 | Primaire | Indice de parité du taux brut d'admission | — | région |
| E11 | Primaire | Indice de parité du taux brut de scolarisation | — | région |
| E12 | Primaire | Indice de parité du taux d'achèvement | — | région |
| E13 | Primaire | Nombre d'écoles | statut | région |

### Ce que mesurent les indicateurs

Ce sont les définitions usuelles de l'UNESCO, reprises par la DGESS. Elles sont **à confirmer dans les annuaires de la DGESS**.

| Indicateur | Définition |
| --- | --- |
| Taux brut d'admission (TBA) | nouveaux inscrits au CP1 ÷ population ayant l'âge officiel d'entrée (6 ans) |
| Taux brut de scolarisation (TBS) | effectif total du cycle ÷ population ayant l'âge officiel du cycle (6 à 11 ans au primaire) |
| Taux d'achèvement du primaire (TAP) | nouveaux entrants au CM2 (hors redoublants) ÷ population ayant l'âge théorique du CM2 (11 ans) |
| Indice de parité (IPS) | valeur des filles ÷ valeur des garçons ; au-dessus de 1, les filles sont devant |

Ces trois taux ont **une population projetée au dénominateur**. C'est important pour la suite, voir la section 2.3.

### Ce qui manque

- les **redoublants** et les **abandons** ;
- les **provinces** ;
- le **post-primaire** ;
- les **effectifs par niveau et par région** : par niveau, il n'y a que le chiffre national ;
- les **populations** par âge, nécessaires pour recalculer les taux.

---

## 2. Ce qu'on a vu

### 2.1 Le format : des pièges de lecture, pas des erreurs de chiffres

| Constat | Ce qu'on en a fait |
| --- | --- |
| 1 019 lignes vides entre les tableaux | Chaque tableau est repéré par ses lignes de début et de fin, vérifiées à la main |
| 6 titres décalés dans la 24e colonne (E1, E2, E8, E9, E11, E12) | On lit le titre où qu'il soit |
| 13 cellules isolées contenant « 2017 », restes de la feuille d'origine | Ignorées : elles ne sont rattachées à aucun tableau |
| En-têtes coupés sur deux lignes (P4, P5, E1) | Les années sont déduites du nombre de colonnes, puis contrôlées |
| Années notées de 5 façons : « 2016 », « 2015/16 », « 2015-16 », « 2015-2016 », « 2015/2016 » | Une seule forme, « 2015-2016 ». Au préscolaire, l'en-tête « 2016 » désigne l'année 2015/2016, qui se termine en 2016. |
| Le titre du tableau du CEP annonce « de 2015 à 2025 », mais il n'y a que 10 colonnes (sessions 2016 à 2025) | Rattachées aux années 2015/2016 à 2024/2025 |
| « HAUT-BASSINS » à deux endroits, « HAUTS-BASSINS » ailleurs | Harmonisé en « HAUTS-BASSINS » |
| Le national s'appelle « NATIONAL », « Burkina Faso », « Total général » ou « TOTAL » | Harmonisé en « NATIONAL » |
| Milieu « indeterminé » au préscolaire, sur 3 années | Gardé tel quel, et signalé |
| Deux numérotations (préscolaire 1 à 8, primaire 1 à 13) | Codes uniques P1 à P8 et E1 à E13 |
| Nombres écrits « 1 477 806 » ou « 1,176 » | Espaces retirés, virgule convertie en point |

### 2.2 La cohérence interne : bonne

| Contrôle | Cas testés | Résultat |
| --- | --- | --- |
| Garçons + filles = total (tableaux d'effectifs) | 827 | ✅ tous justes |
| Somme des régions = national (P1, P7, P8, E1, E5, E13) | 140 | ✅ tous justes |
| Même total national d'un tableau à l'autre (6 comparaisons) | 58 | ✅ tous justes |
| Somme des statuts = total (E2, E13, P2, P7, P8) | 460 | ✅ tous justes |
| Somme des niveaux CP1 à CM2 = total (E4) | 60 | ✅ tous justes |
| Indice de parité = taux des filles ÷ taux des garçons (primaire) | 420 | ✅ tous justes |
| Indice de parité du préscolaire (P5 / P6) | 140 | ⚠️ 1 écart : Centre 2019/20, 1,00 publié contre 0,91 calculé |
| Lignes recopiées d'une région à l'autre | 2 990 | ⚠️ 1 cas : préscolaire, taux de scolarisation 2019/20, **Sahel = Sud-Ouest** |

### 2.3 La vraisemblance : les taux sont faussés par les déplacements

- **15 taux impossibles ou anormaux** :
  - taux d'admission au-dessus de 130 % dans le Nord (jusqu'à 146 % chez les garçons), le Centre et le Plateau-Central ;
  - taux d'achèvement des filles au-dessus de 100 % dans le Centre (101,2 % et 102,6 %).
- **Explication la plus probable.** Les populations de référence sont des projections qui ne suivent pas les déplacements. Dans les régions d'accueil, il y a plus d'élèves que la population prévue, et les taux sont gonflés. Dans les régions de départ, ils sont probablement écrasés.
- **Conséquence.** Les **effectifs** (des comptages) sont plus fiables que les **taux** (des rapports à une population projetée). On privilégie les indicateurs construits sur les effectifs. Les taux sont utilisés en le disant.

### 2.4 Les ruptures : réelles, pas des erreurs

Sur 504 variations annuelles d'effectifs et d'écoles, **30 dépassent 40 %**. Elles s'expliquent toutes :

- **Chocs sécuritaires** : Sahel en 2018/19 (écoles −50 %, élèves −47 %), Boucle du Mouhoun en 2022/23 (−41 %).
- **Réouvertures** en 2023/24 : Sahel (élèves +57 %), Est (nouveaux inscrits +86 %).
- **Préscolaire 2024/25** : forte hausse dans plusieurs régions. Elle est cohérente avec le chantier du ministère : le tableau P7 donne 2 501 structures en 2024/25, le chiffre exact annoncé dans le document des chantiers 2030.

### 2.5 Ce qui n'est pas encore contrôlé

- **Comparaison aux publications d'origine** (annuaires DGESS), comme le demande le règlement. **À faire**, à partir des annuaires publiés.
- **Les définitions exactes des indicateurs**, à vérifier dans les annuaires de la DGESS.

### 2.6 Ce que les données montrent déjà

Le détail est dans `04_analyse/Biiga_04-analyse_D1_analyst_pistes-defi1_v1.md`.

1. **Le choc de 2022/23** : 10,7 % d'élèves en moins et 1 647 écoles en moins au niveau national.
2. **L'entrée repart, l'achèvement chute.** En 2024/25, les effectifs et les entrées en CP1 sont au plus haut, mais le taux d'achèvement est au plus bas : 51,6 %, contre 62,0 % en 2021/22.
3. **Sur 100 élèves entrés en CP1, 56 atteignent le CM2**, contre 74 pour la cohorte de 2015/16.
4. **Quatre profils de régions** : effondrement (Sahel, Est), choc puis reprise (Centre-Nord, Boucle du Mouhoun), érosion (Nord, Centre-Est, Cascades), stabilité ou accueil (6 régions).
5. **Le recul touche toutes les régions.** Les 5 régions en crise n'en expliquent que 55 %.
6. **Au primaire, les garçons achèvent moins que les filles**, sauf au Sahel.

---

## 2 bis. Les sources complémentaires (portail HDX)

Les données du challenge sont la seule base fournie : il n'y a pas d'autre « Data Pack ». Le document du challenge autorise les données publiques complémentaires. Nous avons retenu :

| Source | Contenu | Usage | Constat |
| --- | --- | --- | --- |
| Limites administratives IGB, v03, valides au 01/08/2025 (`cod-ab-bfa`) | 17 régions, 47 provinces, 351 communes, avec les **anciens codes et noms** | Correspondance officielle entre 13 et 17 régions ; fonds de carte (les 13 régions sont reconstituées en fusionnant les nouvelles par leur ancien code) | 10 régions sont simplement renommées et gardent leur code. 3 sont coupées : Boucle du Mouhoun → Bankui et Sourou ; Est → Goulmou, Sirba et Tapoa ; Sahel → Liptako et Soum. |
| Population 2024 par province (INSD, `cod-ps-bfa`) | 45 provinces, par sexe et par tranche de 5 ans | Poids et clés de répartition, si besoin | Projections : elles ignorent les déplacements |
| ACLED, violence politique (`burkina-faso-acled-conflict-data`) | Incidents et morts, par ancienne province et par mois, de 1997 au 6 novembre 2026 | Mesure de l'insécurité par région et par année scolaire (d'octobre à septembre) | Explique en partie le décrochage (r = −0,34 avec l'évolution de l'achèvement l'année suivante), mais ne bat pas « comme l'an passé » pour prévoir |
| Insecurity Insight, attaques contre l'éducation | Incidents de 2017 à 2026 | Contexte (décision D10) | Annoncent moins bien les fermetures que l'ensemble des incidents |
| Cadre Harmonisé (`cadre-harmonise`) | Population par phase d'insécurité alimentaire, par province, de 2014 à la soudure 2024 | Faim par région et par année scolaire (D15) | Accompagne le mieux le recul dans le temps ; le Burkina n'y figure plus après 2024 |
| EDS 2021 (`dhs-subnational-data-for-burkina-faso`) | Indicateurs régionaux : instruction des femmes, fécondité à 15-19 ans | Causes de fond (D15) | Collecte incomplète dans les zones d'insécurité |
| CONASUR, déplacés internes (`situation-des-personnes-deplacees-internes`) | Déplacés par région d'accueil au 31 décembre 2022 | Pression des déplacements (D15) | Dernière série régionale publiée |

Voir aussi `04_analyse/Biiga_04-analyse_D1_scientist_journal-decisions_v1.md`, décisions D1 à D18.

---

## 3. Ce qu'on peut et ce qu'on ne peut pas faire avec ces données

| Attente du Défi 1 | Avec ces données | Verdict | Ce qu'il faudrait |
| --- | --- | --- | --- |
| Décrire l'évolution par région, par sexe, sur 10 ans | Oui | ✅ **Faisable** | — |
| Mesurer le décrochage | Pas d'abandons ni de redoublants | 🟡 **Par substitut** : taux d'achèvement, sorties en excès, survie apparente du CP1 au CM2 | Redoublants et abandons par niveau et par zone |
| Classer et cartographier les régions | Indicateurs par région ; limites officielles IGB | ✅ **Fait** : carte des 13 régions sous leurs noms de 2025 | — |
| Travailler par province | Indicateurs scolaires absents par province | ❌ **Impossible** pour l'école ; l'insécurité, elle, est connue par province (ACLED) | Annuaires par province |
| Passer aux 17 nouvelles régions | 10 régions sont simplement renommées ; 3 groupes restent indivisibles | 🟡 **13 unités** (décision D1) | Données par province pour séparer les 3 groupes |
| Couvrir le post-primaire | Absent | ❌ **Impossible** | Statistiques du post-primaire |
| Localiser les pertes par niveau (CM1, CM2…) | Niveaux au niveau national seulement | 🟡 **National uniquement** | Effectifs par niveau et par région |
| Expliquer les causes | Fermetures d'écoles et incidents (ACLED) | 🟡 **Partiel** : ce sont des relations, pas des causes démontrées | Déplacés, pauvreté |
| **Anticiper** l'année suivante | Testé avec et sans ACLED : rien ne bat « comme l'an passé » (4,2 points d'erreur moyenne) | 🟡 **Prévision prudente** (« comme l'an passé » avec une fourchette) **et alerte d'escalade** (décision D6) | Une information sur les réouvertures prévues |
| Tester « insécurité × précarité » | L'insécurité est mesurée (ACLED) ; la précarité ne l'est pas | ❌ **Incomplet** | Pauvreté par région (EHCVM, INSD) |
| Corriger les taux faussés par les déplacements | Pas de population réelle | ❌ **Signalé, non corrigé** | Population par âge et par zone (INSD), déplacés (OCHA) |
| Scénarios de réouverture d'écoles | Relation écoles / élèves (R² = 0,87) | 🟡 **Ordre de grandeur** | Écoles fermées par zone, à jour (OCHA, ministère) |

---

## 4. État des besoins en données

| Donnée | Ce qu'elle débloque | État |
| --- | --- | --- |
| Correspondance anciennes et nouvelles régions et provinces | Les noms de 2025 ; les 13 unités | ✅ **Obtenue** : IGB 2025 (HDX) |
| Fonds de carte | La carte | ✅ **Obtenu** : IGB 2025 (HDX) |
| Incidents sécuritaires par zone et par mois | Expliquer ; alerte d'escalade | ✅ **Obtenus** : ACLED (HDX) |
| Population par âge et par province | Poids, clés de répartition | ✅ **Obtenue** : INSD 2024 (HDX), sous forme de projections |
| Annuaires DGESS **par province**, avec **redoublants et abandons** | La vraie mesure du décrochage ; les provinces ; les 17 régions | ❌ **Non disponible** : limite assumée (décision D1) |
| Écoles fermées et élèves déplacés par zone et par date | Mesurer le choc ; corriger les sorties ; **prévoir les effectifs de l'année (erreur divisée par deux, D13)** | ❌ Non trouvé par zone, ni sur HDX ni dans la presse (recherche du 13/11) ; chiffres nationaux seulement |
| Pauvreté par région | Tester « insécurité × précarité » | ✅ **Obtenue** : INSD, EHCVM 2021 |
| Faim, famille, déplacés par région | Causes autres que l'insécurité | ✅ **Obtenus** : Cadre Harmonisé, EDS 2021, CONASUR (D15) |
| Orpaillage, travail des enfants, mariage précoce, distance à l'école, cantines, écoles à cycle incomplet | Les autres causes connues du décrochage | ❌ Pas de série publique par région |
| Annuaires publiés, pour comparer nos totaux | La règle « vérifiez vos totaux » | 🟡 À chercher : publications de la DGESS et de l'INSD |

**En une phrase :** les données du challenge, complétées par les sources publiques de HDX, permettent de **décrire, cartographier et expliquer en partie** le décrochage sur 13 régions, avec une **anticipation prudente** dont la fiabilité est mesurée. Les **provinces**, les **17 régions séparées** et la **mesure directe de l'abandon** restent hors d'atteinte.

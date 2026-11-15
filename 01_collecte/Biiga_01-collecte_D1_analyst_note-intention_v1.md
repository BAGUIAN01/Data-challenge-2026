# Note d'intention — Défi 1 : décrochage scolaire

## Titre

Anticiper le décrochage scolaire au Burkina Faso : insécurité, précarité, éloignement, région par région

## Problématique éducative visée

Le décrochage scolaire désigne la sortie de l'école avant la fin d'un cycle. Au Burkina Faso, où la scolarité est obligatoire de 6 à 16 ans depuis la loi de 2007, le défi consiste à localiser ce risque région par région et à l'anticiper assez tôt pour orienter les décisions.

Trois approches existent, et aucune ne suffit.

Les annuaires statistiques mesurent l'abandon par la méthode des cohortes de l'UNESCO, en comparant deux rentrées successives :

Taux d'abandon = 1 − (promus + redoublants à la rentrée suivante) ÷ inscrits de l'année

Ce taux n'est connu qu'après les décisions de l'année suivante. Il compte aussi comme abandons, dans leur zone d'origine, les élèves déplacés réinscrits ailleurs, et ne voit les écoles fermées que si elles restent recensées.

Le suivi de l'éducation en situation d'urgence mesure, lui, le choc :

Élèves touchés = somme des effectifs des écoles fermées

On sait ainsi que 5 336 écoles étaient fermées en février 2024 (IIEP-UNESCO, 2024) et que 432 181 élèves ont été réinscrits entre 2023 et 2025 (MEBAPLN, 2026). On ignore en revanche quels élèves manquent encore.

Les systèmes d'alerte précoce, enfin, estiment le risque élève par élève :

Risque d'un élève = f(absences, notes, retard d'âge, situation familiale)

Au Guatemala et au Honduras, ces modèles repèrent environ 80 % des élèves qui décrocheront à l'entrée du secondaire (Adelman et al., 2018). Au Pérou, la plateforme Alerta Escuela n'a pourtant été consultée que par 7 % des écoles concernées (Banque mondiale). Surtout, ces systèmes reposent sur un identifiant unique par élève. Au Burkina, le Fichier national des élèves n'en est qu'à sa phase pilote, conduite dans deux provinces auprès de 202 808 élèves, et sa généralisation est prévue d'ici 2030 (MEBAPLN, 2026).

Quant aux causes, les études menées au Burkina ont examiné l'éloignement de l'école (programme BRIGHT, Kazianga et al., 2013) et la précarité (cantines et transferts conditionnels, Kazianga et al., 2012 ; Akresh et al., 2013), mais séparément, avant la crise, et sur l'inscription plutôt que sur le maintien.

Il manque donc une alerte disponible avant la rentrée, construite à partir de données agrégées, et qui relie l'insécurité aux causes plus anciennes. D'où notre question : pour le primaire et le post-primaire, en distinguant filles et garçons, peut-on désigner avant chaque rentrée les zones où le risque est le plus élevé, et expliquer pourquoi ?

Pour y répondre, nous empruntons le cadre de l'analyse des risques, où le risque naît de la rencontre d'un aléa et d'une vulnérabilité (Wisner et al., 2004). Ici, l'aléa est l'insécurité, la vulnérabilité tient à la précarité et à l'éloignement. D'où l'hypothèse :

Risque d'une zone = Insécurité × Précarité × Éloignement de l'école

Chaque facteur vaut 1 là où il est absent, si bien qu'une zone calme garde son décrochage ordinaire. Si l'hypothèse est juste, un modèle qui additionne les facteurs prédira moins bien. C'est ce que nous testerons.

## Piste de solution proposée

Notre démarche reprend, dans l'ordre, les limites relevées.

Nous commençons par corriger la mesure de l'abandon, pour tenir compte des déplacements et des écoles fermées :

Abandon corrigé = abandon calculé − déplacés réinscrits ailleurs + élèves des écoles fermées non rescolarisés

Les rapports de rentrée transmis aux directions provinciales comptent les élèves déplacés accueillis par chaque école, ce qui permet d'estimer le deuxième terme là où ils sont disponibles. Ils indiquent aussi combien d'élèves affectés en 6e sont effectivement présents, une mesure directe de la perte à l'entrée du post-primaire, connue dès la rentrée. Le dernier terme, lui, n'étant pas observé directement, nous l'encadrons entre deux bornes, et le résultat est donné sous forme de fourchette. Le calcul se fait par niveau, par sexe et par zone, sur le découpage actuel en 17 régions et 47 provinces.

Nous testons ensuite l'hypothèse, en mesurant chaque facteur par zone :

Insécurité = incidents sécuritaires sur douze mois (ACLED)

Précarité = taux de pauvreté des ménages (EHCVM)

Éloignement = distance à l'école la plus proche (OpenStreetMap, WorldPop)

Le nombre de décrocheurs attendus dans une zone s'écrit alors :

Décrocheurs attendus = élèves inscrits × risque de la zone

Deux modèles de Poisson, l'un additif, l'autre multiplicatif, sont comparés sur des années qui n'ont pas servi à les estimer. Ils sont estimés séparément pour les filles et pour les garçons.

Pour anticiper, nous comparons notre prévision à la règle la plus simple, qui reconduit les chiffres de l'année précédente :

Gain de prévision = erreur de la règle « comme l'an passé » − erreur de notre prévision

Un modèle d'apprentissage automatique est mis en concurrence avec le modèle statistique et n'est retenu que s'il fait mieux. Ses prévisions sont expliquées facteur par facteur. L'insécurité ne pouvant pas se prévoir, nous la traitons par des scénarios de fermeture et de réouverture d'écoles.

Enfin, dans chaque région, le facteur dominant oriente la réponse, en cohérence avec les chantiers du ministère à l'horizon 2030 : réouvertures et accueil des élèves déplacés lorsque l'insécurité domine, cantines endogènes et transferts conditionnels lorsque c'est la précarité, classes de proximité et affectation d'enseignants lorsque c'est l'éloignement. L'expérience internationale va dans ce sens. Au Guatemala, un système d'alerte relié à des actions dans les écoles a réduit l'abandon de 4 % à l'entrée du secondaire (Vazquez et al., 2021), alors qu'au Pérou, l'effort pour accroître l'usage de la plateforme n'a pas fait baisser l'abandon. Nous privilégions donc un modèle explicable, un outil utilisable sans connexion et une réponse jointe à chaque alerte.

Le travail débouchera sur une carte du risque exprimée en nombre d'enfants, une liste de provinces prioritaires, une fiche d'une page par région et un tableau de bord consultable hors connexion. Il s'adapte au niveau de détail des données fournies et n'utilise que des données agrégées. Lorsque le Fichier national des élèves sera généralisé, la même méthode pourra être appliquée à l'échelle de l'école, puis de l'élève.

## Sources des données utilisées

Nous partirons des jeux de données anonymisés fournis par le challenge, complétés par les annuaires statistiques de l'éducation et de l'INSD, les rapports sur l'éducation en situation d'urgence, le recensement général de la population de 2019, les enquêtes EHCVM et EDS 2021, les données du CONASUR sur les personnes déplacées, celles d'ACLED sur les incidents sécuritaires, ainsi qu'OpenStreetMap et WorldPop pour la localisation des écoles et de la population.

Adelman M., Haimovich F., Ham A., Vazquez E. (2018). Predicting school dropout with administrative data: new evidence from Guatemala and Honduras. Education Economics.
Banque mondiale. Blog Education, systèmes d'alerte précoce et Alerta Escuela (Pérou).
IIEP-UNESCO (2024). Données d'éducation en situation d'urgence, Burkina Faso.
Akresh R., de Walque D., Kazianga H. (2013). Cash transfers and child schooling. Banque mondiale, WPS 6340.
Kazianga H., de Walque D., Alderman H. (2012). Educational and child labour impacts of two food-for-education schemes. Journal of African Economies.
Kazianga H., Levy D., Linden L., Sloan M. (2013). The effects of girl-friendly schools: evidence from the BRIGHT program in Burkina Faso. AEJ: Applied Economics.
MEBAPLN (2026). 14 chantiers pour l'école burkinabè à l'horizon 2030.
Vazquez E., Haimovich F., Adelman M. (2021). Scalable early warning systems for school dropout prevention. Banque mondiale.
Wisner B., Blaikie P., Cannon T., Davis I. (2004). At Risk. Routledge.

## Valeur ajoutée et impact attendu

La principale contribution est de fournir une alerte avant la rentrée, au moment où se décident les cantines, les affectations d'enseignants et les réouvertures, alors que le taux d'abandon actuel n'arrive qu'après. Exprimé en nombre d'enfants, le risque peut servir directement à répartir des moyens, et chaque région reçoit avec lui sa cause dominante et le levier correspondant.

L'hypothèse de cumul sera vérifiée sur les données. Si elle se confirme, elle modifie l'ordre des priorités. Si elle est rejetée, le résultat reste utile, puisqu'il indique que les facteurs peuvent être traités séparément. Et si les données ne permettent pas de trancher, nous le dirons.

Conçu pour fonctionner sans connexion, l'outil reste utilisable dans les zones où le risque est le plus fort, et il prépare le passage au suivi individuel prévu par le ministère.

Pendant le challenge, l'impact se mesurera de deux manières : la part des abandons d'une année test qui se trouvait dans les provinces que nous aurions désignées, comparée au classement par nombre d'abandons de l'année précédente, et le gain de prévision par rapport à la règle « comme l'an passé ». Après adoption, les actions gagneraient à être déployées par vagues, les provinces pas encore couvertes servant de témoins : une simple comparaison entre provinces ciblées et non ciblées ferait paraître en progrès des provinces qui, parties de très haut, auraient de toute façon baissé. S'y ajoute la part des élèves retrouvés dans les écoles rouvertes.

## Contribution du membre 1

Équipe d'une seule personne, qui assure l'ensemble du travail, de la préparation des données à la restitution des résultats.

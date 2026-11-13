"""Build the final report (HTML, then PDF through Chromium) from the dashboard data set and the figures."""
import json
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
jeu = json.load(open(RACINE / "dashboard/public/data/tableau_de_bord.json", encoding="utf-8"))
R = jeu["regions"]
sg, fd, val, defs = jeu["score_global"], jeu["facteur_dominant"]["par_region"], jeu["validation"], {d["id"]: d for d in jeu["facteurs_def"]}
NOM_ACTION = {"violence": "l'insécurité", "deplaces": "l'accueil des déplacés", "pauvrete": "la pauvreté", "faim": "la faim",
              "meres": "l'instruction des mères", "grossesses": "les grossesses précoces", "prescolaire": "le préscolaire"}
PRIO = {1: "1 · agir maintenant", 2: "2 · veille renforcée", 3: "3 · consolider"}
C = {1: "#104281", 2: "#3987e5", 3: "#86b6ef"}


def fr(v, d=0):
    return f"{v:,.{d}f}".replace(",", " ").replace(".", ",")


def cls(s):
    return 1 if s >= 50 else 2 if s >= 25 else 3


ordre = sorted(R, key=lambda r: (r["priorite"], -sg["par_region"][r["cle"]]))
tr = sg["trajectoire"]
lignes_resultats = "".join(
    f"<tr><td><b>{r['nom']}</b><br><span class='p'>ancienne {r['ancienne']}</span></td>"
    f"<td class='n'><span class='pastille' style='background:{C[cls(sg['par_region'][r['cle']])]}'>{sg['par_region'][r['cle']]}</span></td>"
    f"<td class='n'>{r['probabilites']['ref_2026_27']} %</td><td class='n'>{fr(r['tap'][-1], 1)} %</td>"
    f"<td>{PRIO[r['priorite']]}</td>"
    f"<td>{('Agir sur ' + NOM_ACTION[fd[r['cle']]['dominant']]) if fd[r['cle']]['dominant'] else 'Rien ne ressort : consolider'}</td>"
    f"<td class='n'>{fr(round(r['enfants_hors_cm2'], -2))}</td></tr>"
    for r in ordre)
mouv = sorted(((r, tr["par_region"][r["cle"]]["score"]) for r in R), key=lambda x: x[1][-2] - x[1][-1])
hausses = ", ".join(f"{r['nom']} ({s[-2]} → {s[-1]})" for r, s in reversed(mouv) if s[-1] - s[-2] >= 3)
total_hors = sum(r["enfants_hors_cm2"] for r in R)
p1_hors = sum(r["enfants_hors_cm2"] for r in R if r["priorite"] == 1)
poids = "".join(f"<td>{defs[k]['libelle'].replace(' (phase 3 ou plus)', '')}</td>" for k in
                ["violence", "meres", "deplaces", "faim", "grossesses", "pauvrete", "prescolaire"])
vpoids = "".join(f"<td class='n'>{v}</td>" for v in ["0,92", "0,85", "0,83", "0,72", "0,72", "0,69", "0,55"])
nat = jeu["national"]
FIG = "../analyse/figures/"

html = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Anticiper le risque de décrochage scolaire</title>
<style>
@page {{ size: A4; margin: 15mm 16mm 16mm; }}
:root {{ --fg:#0f172a; --fg2:#475569; --fg3:#7d8799; --line:#e3e7ed; --card:#f4f6f9; --c1:#104281; --c2:#3987e5; --c3:#86b6ef; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; font: 10pt/1.5 Inter, system-ui, sans-serif; color: var(--fg); -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1 {{ font-size: 23pt; line-height: 1.12; letter-spacing: -.02em; margin: 0 0 6pt; }}
h2 {{ font-size: 14.5pt; margin: 0 0 6pt; padding-top: 2pt; letter-spacing: -.01em; break-after: avoid; }}
h2 .num {{ color: var(--c1); margin-right: 6pt; }}
h3 {{ font-size: 11pt; margin: 11pt 0 3pt; break-after: avoid; }}
p {{ margin: 0 0 6pt; }}
ul {{ margin: 0 0 6pt; padding-left: 15pt; }} li {{ margin: 1.5pt 0; }}
.sur {{ font-size: 8pt; letter-spacing: .08em; text-transform: uppercase; color: var(--fg3); font-weight: 600; margin-bottom: 8pt; }}
.chapo {{ font-size: 11pt; color: var(--fg2); margin-bottom: 12pt; }}
section {{ break-before: page; }}
section.suite {{ break-before: auto; margin-top: 14pt; }}
.cadre {{ background: var(--card); border-radius: 8pt; padding: 10pt 12pt; margin: 8pt 0; break-inside: avoid; }}
.cadre.bleu {{ background: #eaf1fb; }}
.cles {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8pt; margin: 10pt 0; }}
.cles div {{ background: var(--card); border-radius: 8pt; padding: 8pt 10pt; }}
.cles b {{ display: block; font-size: 17pt; letter-spacing: -.02em; color: var(--c1); }}
.cles span {{ font-size: 8.5pt; color: var(--fg2); line-height: 1.3; display: block; }}
table {{ width: 100%; border-collapse: collapse; margin: 6pt 0 8pt; font-size: 8.8pt; break-inside: avoid; }}
th {{ text-align: left; font-weight: 600; color: var(--fg2); border-bottom: 1.2pt solid var(--fg); padding: 3pt 5pt; font-size: 8.3pt; }}
td {{ border-bottom: .6pt solid var(--line); padding: 3.2pt 5pt; vertical-align: top; }}
td.n, th.n {{ text-align: right; white-space: nowrap; }}
td .p {{ color: var(--fg3); font-size: 7.8pt; }}
.pastille {{ display: inline-block; min-width: 22pt; text-align: center; color: #fff; font-weight: 700; border-radius: 4pt; padding: 0 4pt; }}
.formule {{ font: 600 11pt/1.6 "Inter", sans-serif; background: #fff; border: 1pt solid var(--line); border-radius: 6pt; padding: 7pt 10pt; margin: 6pt 0; text-align: center; }}
.formule small {{ display: block; font-weight: 400; font-size: 8.5pt; color: var(--fg2); }}
figure {{ margin: 8pt 0 10pt; break-inside: avoid; }}
figure img {{ width: 100%; display: block; border-radius: 4pt; }}
figcaption {{ font-size: 8.3pt; color: var(--fg2); margin-top: 4pt; }}
.ecrans {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8pt; align-items: start; }}
.ecrans img {{ border: .6pt solid var(--line); border-radius: 8pt; }}
.deux {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; align-items: start; }}
.note {{ font-size: 8.3pt; color: var(--fg3); }}
.decomp {{ display: flex; height: 12pt; border-radius: 3pt; overflow: hidden; margin: 4pt 0; }}
</style></head><body>

<div class="sur">Data Challenge Burkina 2026 · Éducation · Défi 1</div>
<h1>Anticiper le risque de décrochage scolaire, région par région</h1>
<p class="chapo">Une carte du risque pour la rentrée 2026/27, une alerte qui se précise au fil de l'année, un levier par région, et un outil qui fonctionne sans réseau.</p>

<div class="cles">
  <div><b>5 régions</b><span>où agir maintenant (priorité 1), sur 13</span></div>
  <div><b>≈ {fr(round(p1_hors, -3))}</b><span>enfants n'atteignent pas le CM2 dans ces 5 régions ({round(100 * p1_hors / total_hors)} % du pays)</span></div>
  <div><b>0,83 → 0,88</b><span>fiabilité de l'alerte (AUC), d'avant la rentrée à janvier, sur des années jamais vues</span></div>
  <div><b>71 %</b><span>des fortes baisses d'effectifs repérées à l'avance, en ciblant 35 % des régions</span></div>
</div>

<figure><img src="img/app_bureau.png"><figcaption>Le tableau de bord : la carte du score de risque 2026/27 (couleur et barre par région), les régions où agir et ce qui change par rapport à 2025/26.</figcaption></figure>

<h3>En bref</h3>
<ul>
<li><b>Le décrochage prend deux formes.</b> Brutale : les effectifs chutent quand la violence ferme les écoles. Lente : une part croissante d'enfants n'achève pas le primaire (51,6 % d'achèvement au pays en 2024/25, contre 62,0 % en 2021/22).</li>
<li><b>Un score de 0 à 100 réunit les deux</b> : moitié probabilité de chute des effectifs, prévue à partir de la violence, moitié part d'enfants qui n'achèvent pas.</li>
<li><b>Un facteur dominant par région</b> dit sur quoi agir : insécurité, déplacés, pauvreté, grossesses précoces, instruction des mères, préscolaire.</li>
<li><b>Tout est vérifié sur des années que les modèles n'avaient pas vues</b>, contre la règle « comme l'an passé ». Ce qui ne marche pas est dit, avec ses chiffres.</li>
</ul>

<section>
<h2><span class="num">1</span>Le besoin</h2>
<p>Un décideur ne demande pas « de combien de points le taux d'achèvement va-t-il bouger ». Avant chaque rentrée, quand se décident les réouvertures, les cantines et les affectations d'enseignants, il demande :</p>
<ol><li><b>où agir</b> en premier ;</li><li><b>où la situation va s'aggraver</b> ;</li><li><b>combien d'enfants</b> sont en jeu, et <b>sur quoi agir</b> dans chaque région.</li></ol>
<p>Les outils existants arrivent trop tard ou voient mal. Le taux d'abandon par cohorte n'est connu qu'après la rentrée suivante, et il compte comme abandons les élèves déplacés réinscrits ailleurs. Le suivi de l'éducation en urgence compte les écoles fermées (5 336 en février 2024), mais pas les élèves qui manquent encore. Les systèmes d'alerte élève par élève supposent un identifiant unique, encore en phase pilote au Burkina.</p>
<div class="cadre bleu"><b>Trois contraintes ont guidé la conception.</b>
<ul style="margin-top:4pt"><li><b>Des données agrégées</b>, par région et par année, sans aucune donnée personnelle.</li>
<li><b>Une alerte avant la rentrée</b>, et non un constat après l'annuaire.</li>
<li><b>Un outil utilisable sans réseau</b>, puisque le risque est le plus fort là où la connexion manque.</li></ul></div>

<h2 style="margin-top:14pt"><span class="num">2</span>Les données</h2>
<h3>Les données du challenge</h3>
<p>21 tableaux de la DGESS, de 2015/16 à 2024/25, sur les <b>13 anciennes régions</b> : effectifs, écoles, nouveaux inscrits, taux de scolarisation, d'admission, d'achèvement, réussite au CEP, par sexe. <b>Il n'y a ni redoublants, ni abandons, ni provinces, ni effectifs par niveau et par région.</b> Le décrochage se mesure donc par deux signaux observables : la <b>chute des effectifs</b> d'une année sur l'autre et le <b>taux d'achèvement</b>.</p>
<p><b>Contrôles de cohérence</b> (8 contrôles) : toutes les sommes concordent (garçons + filles, régions = national, statuts, niveaux). Deux anomalies sont signalées et traitées : une ligne recopiée au préscolaire 2019/20, et des taux au-dessus de 100 % dans les régions d'accueil, où les projections de population ignorent les déplacements. <b>Les effectifs bruts sont plus fiables que les taux.</b></p>
<h3>Les sources externes</h3>
<table><tr><th>Source</th><th>Ce qu'elle apporte</th><th>Dans le dépôt</th></tr>
<tr><td>ACLED (via HDX)</td><td>Incidents de violence par province et par mois, 1997 à 2026</td><td>agrégat par région et année (brut non redistribuable)</td></tr>
<tr><td>IGB, via OCHA</td><td>Limites administratives 2025 : correspondance 13 / 17 régions et 45 / 47 provinces</td><td>table et carte des 13 régions</td></tr>
<tr><td>INSD (cod-ps)</td><td>Population 2024 par province</td><td>brut</td></tr>
<tr><td>Cadre harmonisé</td><td>Population en phase 3 ou plus d'insécurité alimentaire</td><td>brut et agrégat</td></tr>
<tr><td>EDS 2021</td><td>Femmes sans instruction, grossesses précoces</td><td>valeurs régionales</td></tr>
<tr><td>INSD, EHCVM 2021</td><td>Pauvreté par région</td><td>tableau recopié</td></tr>
<tr><td>CONASUR</td><td>Personnes déplacées accueillies, fin 2022</td><td>brut et agrégat</td></tr>
<tr><td>Insecurity Insight</td><td>Attaques contre l'éducation</td><td>agrégat par région et année</td></tr></table>
<p><b>13 ou 17 régions ?</b> Le découpage de 2025 compte 17 régions, mais les données du challenge n'en connaissent que 13. Le travail se fait sur les 13 anciennes régions, affichées sous leur nom de 2025 (par exemple « Goulmou + Sirba + Tapoa » pour l'ancien Est), grâce à la correspondance officielle de l'IGB. Une région coupée en 2025 garde un seul score : les données ne permettent pas de séparer ses parties, et l'outil le dit.</p>
</section>

<section class="suite">
<h2><span class="num">3</span>Ce que montrent les données</h2>
<div class="deux">
<div>
<p><b>Le choc de 2022/23.</b> Les effectifs du primaire passent de 3 174 946 à 2 835 544 (−10,7 %), les écoles de 14 427 à 12 780.</p>
<p><b>L'entrée repart, l'achèvement s'effondre.</b> En 2024/25, les effectifs battent un record (3 308 096), mais l'achèvement tombe à 51,6 %, son plus bas de la décennie. Les garçons achèvent moins que les filles (47,7 %).</p>
<p><b>Les écoles fermées expliquent l'essentiel des variations d'effectifs</b> : 1 % d'écoles en moins va avec 0,78 % d'élèves en moins (R² = 0,87, 117 variations).</p>
<p><b>Cinq régions décrochent nettement</b> : l'Est (achèvement de 40,2 % à 16,5 %), le Sahel (11,1 %), le Centre-Nord, la Boucle du Mouhoun et le Nord. Le Centre, les Hauts-Bassins, le Centre-Ouest et le Centre-Sud tiennent : ce sont des régions d'accueil.</p>
<p><b>Le retard est très persistant</b> : la corrélation de rang de l'achèvement d'une année à l'autre vaut {fr(val['rang_tap'], 2)}. La carte de cette année désigne de façon fiable les régions de l'an prochain.</p>
</div>
<figure style="margin-top:0"><img src="{FIG}08_carte_profils_achevement.png"><figcaption>Figure 1. Taux d'achèvement 2024/25 et profils d'évolution des régions.</figcaption></figure>
</div>

</section>

<section>
<h2><span class="num">4</span>La méthode</h2>
<p>Une seule règle de conduite : <b>chaque modèle est testé sur des années qu'il n'a pas vues</b>, contre la règle la plus simple, « comme l'an passé », et la liste des modèles est fixée avant de lancer les tests.</p>
<h3>4.1 Le risque de chute des effectifs : une formule à trois paramètres</h3>
<p>On prévoit, pour chaque région, la probabilité que les élèves du primaire baissent de <b>plus de 5 %</b> à la rentrée suivante, à partir d'une seule source : les incidents de violence de l'année scolaire qui se termine (octobre à septembre). C'est une régression logistique :</p>
<div class="formule">z = −5,77 + 0,98 × ln(1 + I) + 0,86 × [ ln(1 + I) − ln(1 + I<sub>précédent</sub>) ] &nbsp;&nbsp;·&nbsp;&nbsp; p = 1 / (1 + e<sup>−z</sup>)
<small>I : incidents de l'année ; le premier terme mesure le niveau de la violence, le second son escalade. Le logarithme traduit qu'un passage de 0 à 50 incidents pèse plus que de 500 à 550.</small></div>
<p><b>Comment elle a appris.</b> 104 cas (13 régions × 8 années, 2016/17 à 2023/24), dont 19 fortes baisses. Les trois nombres sont ceux qui séparent le mieux les années de chute des autres. <b>Exemple, Yaadga</b> : 250 incidents contre 131 l'année d'avant, donc z = −5,77 + 0,98 × 5,53 + 0,86 × 0,64 = 0,21, et p = 55 %.</p>
<p><b>Comment on l'a vérifiée.</b> Le passé est rejoué année par année : pour prévoir 2019/20, le modèle n'apprend que sur les années d'avant, et ainsi de suite. Sur ces années jamais vues :</p>
<table><tr><th>Modèle (forte baisse l'an prochain)</th><th class="n">AUC</th><th class="n">Baisses annoncées</th></tr>
<tr><td><b>Logistique, violence seule (retenu)</b></td><td class="n"><b>0,83</b></td><td class="n"><b>64 %</b></td></tr>
<tr><td>Forêt aléatoire, toutes variables</td><td class="n">0,78</td><td class="n">64 %</td></tr>
<tr><td>Logistique, toutes variables</td><td class="n">0,75</td><td class="n">57 %</td></tr>
<tr><td>Règle d'escalade simple</td><td class="n">0,68</td><td class="n">50 %</td></tr>
<tr><td>Aucun modèle (hasard)</td><td class="n">0,50</td><td class="n">—</td></tr></table>
<p class="note">AUC : sur une paire « une région qui chute, une qui ne chute pas », part des cas où le modèle donne le risque le plus haut à la bonne région. Les probabilités classent bien mais restent approximatives (Brier 0,166 contre 0,169 pour le taux de base) : on lit des niveaux (élevé à partir de 40 %, moyen à partir de 15 %), pas des pourcentages exacts.</p>

<h3>4.2 L'alerte se précise au fil de l'année</h3>
<p>ACLED donne la violence par mois. Six signaux plus fins ont été testés ; deux gagnent, et tous deux portent sur le <b>moment</b> de la violence, pas sur sa quantité :</p>
<table><tr><th>Quand</th><th>Ce qu'on ajoute</th><th class="n">AUC</th></tr>
<tr><td>Avant la rentrée</td><td>violence de l'année et son escalade</td><td class="n">{fr(val['auc_reference'], 2)}</td></tr>
<tr><td>Fin septembre</td><td>+ violence de juillet à septembre</td><td class="n">{fr(val['auc_septembre'], 2)}</td></tr>
<tr><td>Début janvier</td><td>+ violence d'octobre à décembre, pendant la rentrée</td><td class="n">{fr(val['auc_janvier'], 2)}</td></tr></table>
<p class="note">Écartés : part du territoire touchée (0,79), violence des régions voisines (0,81), attaques contre l'éducation, qui annoncent moins bien les fermetures que l'ensemble des incidents.</p>
</section>

<section>
<h3 style="margin-top:0">4.3 Le score global : les deux formes de décrochage en un chiffre</h3>
<div class="formule">score = 100 × ( 0,5 × p + 0,5 × (1 − TAP / 100) )
<small>p : probabilité de chute (décrochage brutal, la violence) · 1 − TAP/100 : part d'enfants qui n'achèvent pas le primaire en 2024/25 (décrochage lent). Les poids (moitié, moitié) sont fixés avant tout test ; les bornes sont fixes, si bien que le score d'une région ne dépend que de ses propres données.</small></div>
<div class="deux">
<div><p><b>Exemple, Yaadga</b> : p = 0,55 et TAP = 46,4 %, donc score = 50 × 0,55 + 50 × 0,536 = <b>54</b>.</p>
<div class="decomp"><i style="width:27.5%;background:#0f172a"></i><i style="width:26.8%;background:#c3cbd7"></i><i style="flex:1;background:#eef1f5"></i></div>
<p class="note">27,5 points viennent de la chute probable, 26,8 des enfants qui n'achèvent pas.</p>
<p><b>Extrêmes</b> : Goulmou + Sirba + Tapoa 66 (49 % de risque, 16,5 % d'achèvement) ; Kadiogo 7 (1 % et 87,5 %).</p></div>
<div><table><tr><th>Rejoué 2019/20-2023/24</th><th class="n">AUC</th><th class="n">Baisses</th><th class="n">Élèves perdus</th></tr>
<tr><td>Score global</td><td class="n">{fr(sg['rejoue']['auc_score'], 2)}</td><td class="n">{sg['rejoue']['baisses_score_pct']} %</td><td class="n">{sg['rejoue']['perdus_score_pct']} %</td></tr>
<tr><td>Risque seul</td><td class="n">{fr(sg['rejoue']['auc_risque'], 2)}</td><td class="n">64 %</td><td class="n">65 %</td></tr>
<tr><td><b>Matrice, priorité 1</b></td><td class="n">—</td><td class="n"><b>{sg['rejoue']['baisses_matrice_pct']} %</b></td><td class="n"><b>{sg['rejoue']['perdus_matrice_pct']} %</b></td></tr></table>
<p class="note">À nombre de régions égal. <b>Le score résume, il ne cible pas mieux</b> : il est affiché comme lecture d'ensemble, et la matrice de priorité reste la règle pour cibler.</p></div></div>

<h3>4.4 La matrice de priorité</h3>
<table><tr><th>Priorité</th><th>Règle</th></tr>
<tr><td><b>1 · agir maintenant</b></td><td>achèvement sous la moyenne du pays (51,6 %) <b>et</b> risque élevé (p ≥ 40 %)</td></tr>
<tr><td><b>2 · veille renforcée</b></td><td>achèvement sous la moyenne <b>ou</b> risque au moins moyen (p ≥ 15 %)</td></tr>
<tr><td><b>3 · consolider</b></td><td>les autres régions</td></tr></table>
<p>Rejouée sur le passé avec la seule information de chaque année, la priorité 1 désignait {val['matrice_regions_pct']} % des régions mais contenait <b>{val['matrice_baisses_pct']} % des fortes baisses</b> de l'année suivante et {val['matrice_perdus_pct']} % des élèves perdus. Aucune forte baisse n'est tombée en priorité 3.</p>

<h3>4.5 Sur quoi agir : le facteur dominant</h3>
<p>Pour chaque facteur de fond, on mesure l'écart de la région à la moyenne des 13 (en écarts-types, orienté pour qu'une valeur positive signifie « plus exposé »), pondéré par la force du lien du facteur avec l'achèvement :</p>
<div class="formule">poids(région, facteur) = |corrélation du facteur avec l'achèvement| × écart de la région</div>
<table><tr><th>Facteur</th>{poids}</tr><tr><td>Poids</td>{vpoids}</tr></table>
<p>Le facteur au plus grand poids est le <b>facteur dominant</b>, et son levier est proposé ; le deuxième donne la suite. Le CEP est écarté (effet de sélection). Ce facteur <b>explique et oriente l'action, il ne prévoit pas</b> : ajoutés au modèle de risque, la faim et les facteurs de fond font baisser l'alerte (AUC 0,76 contre 0,82).</p>
</section>

<section>
<h3 style="margin-top:0">4.6 Combien d'élèves : les écoles ouvertes à la rentrée</h3>
<p>Prévoir les effectifs à l'aveugle ne marche pas : toutes les approches testées font moins bien que « comme l'an passé », car elles ratent les réouvertures, qui sont des décisions de l'État. <b>Dès que le nombre d'écoles ouvertes à la rentrée est connu, l'erreur est divisée par deux</b> ({fr(jeu['nowcast']['erreur_pct'], 1)} % contre {fr(jeu['nowcast']['erreur_persistance_pct'], 1)} %) :</p>
<div class="formule">ln(élèves / élèves 2024/25) = 0,0197 × n + 0,7784 × ln(écoles ouvertes / écoles 2024/25)</div>
<p>Le tableau de bord permet de saisir ce nombre sur le terrain, même sans réseau, et affiche aussitôt les élèves attendus.</p>
<div class="deux">
<figure><img src="{FIG}13_prevision_ecoles_ouvertes.png"><figcaption>Figure 2. Prévision des effectifs à partir des écoles ouvertes.</figcaption></figure>
<figure><img src="{FIG}17_calendrier_alerte.png"><figcaption>Figure 3. Le calendrier d'alerte : septembre, puis janvier.</figcaption></figure>
</div>
<h3>4.7 Ce qui a été testé et n'a pas été retenu</h3>
<ul>
<li><b>L'hypothèse « insécurité × pauvreté »</b> : la violence ferait plus de dégâts là où la pauvreté est forte. Non confirmée à l'échelle régionale (le modèle multiplicatif ne bat pas l'additif) ; l'insécurité a en revanche un effet propre et net.</li>
<li><b>L'apprentissage automatique</b> (Ridge, forêt aléatoire, gradient boosting) : sur la variation de l'achèvement, tous font moins bien que « comme l'an passé » (4,54 à 4,79 points d'erreur contre 4,23). Le modèle simple et explicable est retenu.</li>
<li><b>La faim pour prévoir</b> : elle accompagne le recul (+10 points de population en crise alimentaire vont avec environ −4 points d'achèvement), mais elle monte en même temps, pas avant. Elle explique, la violence alerte.</li>
<li><b>L'achèvement 2025/26</b> : aucun modèle ne bat « comme l'an passé » ; c'est donc la prévision affichée, avec une fourchette tirée des erreurs passées.</li>
</ul>
</section>

<section>
<h2><span class="num">5</span>Résultats pour la rentrée 2026/27</h2>
<table><tr><th>Région (nom 2025)</th><th class="n">Score</th><th class="n">Risque de chute</th><th class="n">Achèvement 24/25</th><th>Priorité</th><th>Sur quoi agir</th><th class="n">Enfants hors CM2</th></tr>
{lignes_resultats}</table>
<p class="note">Enfants hors CM2 : enfants d'environ 11 ans qui n'atteignent pas le CM2, estimés à partir de la population 2024 ; ordre de grandeur.</p>
<ul>
<li><b>Les cinq régions en tête du score sont exactement les cinq en priorité 1.</b> Elles réunissent environ {fr(round(p1_hors, -2))} enfants qui n'atteignent pas le CM2, {round(100 * p1_hors / total_hors)} % du pays.</li>
<li><b>Ce qui change</b> entre le score 2025/26 et la prévision 2026/27 : le risque monte à {hausses}. Yaadga est la région où la violence s'aggrave le plus.</li>
<li><b>Les leviers diffèrent</b> au sein même de la priorité 1 : l'insécurité dans l'Est et la Boucle du Mouhoun, l'accueil des déplacés au Sahel, les grossesses précoces au Centre-Nord, la pauvreté au Nord.</li>
<li><b>Alerte de septembre</b> : Yaadga monte à 61 %, Guiriko passe de 1 % à 20 % : une région qui tient encore mais où le risque monte, à placer en veille.</li>
</ul>
<figure style="width:88%;margin:8pt auto"><img src="{FIG}15_matrice_priorite_2026_27.png"><figcaption>Figure 4. Matrice de priorité 2026/27 : à gauche le retard d'achèvement, en haut le risque de chute.</figcaption></figure>
<figure style="width:88%;margin:8pt auto"><img src="{FIG}16_profil_facteurs.png"><figcaption>Figure 5. Profil des facteurs de fond de chaque région : plus la case est foncée, plus la région est exposée.</figcaption></figure>
</section>

<section>
<h2><span class="num">6</span>L'outil : un tableau de bord qui fonctionne sans réseau</h2>
<p>L'application s'ouvre sur un téléphone comme sur un ordinateur. <b>L'accueil est la carte du score</b> ; un lecteur discret fait défiler les années de 2020/21 à la prévision 2026/27. Toucher une région ouvre sa page : le score et sa décomposition, la courbe du score année par année jusqu'à la prévision (avec les chutes réellement observées), le facteur dominant et son levier, l'achèvement, la violence, et la fiche imprimable.</p>
<div class="ecrans">
<figure><img src="img/app_carte.png"><figcaption>Accueil : la carte du score, barres et couleurs, et le lecteur des années.</figcaption></figure>
<figure><img src="img/app_region_score.png"><figcaption>Page d'une région : le score année par année jusqu'à la prévision.</figcaption></figure>
<figure><img src="img/app_region_action.png"><figcaption>Sur quoi agir : le facteur dominant, son levier, le poids de chaque facteur.</figcaption></figure>
<figure><img src="img/app_hors_ligne.png"><figcaption>Serveur arrêté : l'application s'ouvre et le dit, avec la date des données.</figcaption></figure>
</div>
<h3>Conçu pour les réseaux qui coupent</h3>
<ul>
<li><b>Lire</b> : les données sont gardées sur l'appareil ; sans réseau, l'écran le dit et donne la date des données.</li>
<li><b>Saisir</b> : le nombre d'écoles ouvertes saisi sur le terrain est enregistré sur le téléphone, visible aussitôt, et part au retour du réseau, une seule fois, sans doublon.</li>
<li><b>Imprimer</b> : la fiche régionale d'une page reste disponible hors ligne.</li>
<li><b>Prouvé</b> : deux contrôles automatiques le vérifient à chaque modification, dont un avec le serveur réellement arrêté.</li>
</ul>
<p class="note">Next.js, base PostgreSQL pour la publication des versions et la réception des saisies, stockage local sur l'appareil (IndexedDB) et service worker. Les chiffres affichés viennent d'un seul fichier produit par l'analyse : l'application, les fiches et ce rapport ne peuvent pas se contredire.</p>
</section>

<section>
<div class="deux" style="grid-template-columns: 1.1fr 1fr">
<div>
<h3 style="margin-top:0">La fiche régionale</h3>
<p>Une page par région, pour un directeur régional, dans le même ordre que l'application : le score et son rang, sur quoi agir, le score année par année jusqu'à la prévision, l'achèvement, la violence et les leviers. Le livret des 13 fiches est classé de la région la plus urgente à la moins urgente.</p>
<h2 style="margin-top:16pt"><span class="num">7</span>Limites</h2>
<ul>
<li><b>13 régions, pas 17 ni 47 provinces</b> : c'est le niveau des données du challenge. Une région coupée en 2025 garde un seul score.</li>
<li><b>Peu de cas</b> : 19 fortes baisses pour apprendre, 14 pour tester, concentrées sur trois années. Les gains des alertes de septembre et janvier sont modestes et restent à confirmer.</li>
<li><b>L'essentiel du ciblage vient du retard d'achèvement</b> ; la violence sert surtout à faire monter en veille une région qui tient encore.</li>
<li><b>Les réouvertures ne se prévoient pas</b> : ce sont des décisions de l'État. D'où la saisie des écoles ouvertes.</li>
<li><b>Des taux fragiles</b> là où la population de référence ignore les déplacements.</li>
<li><b>La faim n'est plus publiée</b> pour le Burkina après la soudure 2024 ; les facteurs de fond datent de 2021-2022.</li>
</ul>
<h2 style="margin-top:12pt"><span class="num">8</span>Pour aller plus loin</h2>
<ul>
<li><b>Brancher le nombre d'écoles ouvertes par région</b>, suivi par le ministère, sur l'outil dès octobre : il donnerait les effectifs de l'année, avec une erreur divisée par deux, bien avant l'annuaire.</li>
<li><b>Descendre aux 47 provinces</b> dès que les données le permettent : ACLED et la population sont déjà disponibles à ce niveau.</li>
<li><b>Mesurer l'effet des actions</b> en les déployant par vagues, les régions pas encore couvertes servant de témoins.</li>
<li><b>Passer à l'école, puis à l'élève</b>, quand le Fichier national des élèves sera généralisé.</li>
</ul>
</div>
<figure style="margin-top:0"><img src="../analyse/fiches/fiche_koulse.png" style="border:.6pt solid var(--line)"><figcaption>La fiche régionale de Koulsé (ancien Centre-Nord).</figcaption></figure>
</div>
</section>

<section>
<h2><span class="num">9</span>Reproductibilité et sources</h2>
<p><b>Tout se relance.</b> Le code de chaque étape est dans un cahier Jupyter déjà exécuté (nettoyage, transformation, analyse descriptive, modèles, interprétation). Relancés, les cahiers redonnent exactement les mêmes résultats. Chaque modèle a été testé sur des années non vues, avec une liste de modèles fixée avant de lancer ; les 21 décisions de méthode sont consignées dans un journal, avec ce qu'elles écartent.</p>
<p><b>Aucune donnée personnelle.</b> Seules des données agrégées par région et par année sont utilisées. Les données brutes d'ACLED ne sont pas redistribuées, conformément à leurs conditions ; seul notre agrégat est déposé.</p>
<h3>Sources des données</h3>
<ul class="note" style="font-size:8.6pt">
<li>DGESS, Ministère de l'Éducation nationale : données statistiques du préscolaire et du primaire 2015/16-2024/25 (Data Challenge Burkina 2026).</li>
<li>ACLED : violence politique et attaques contre les civils, Burkina Faso, par province et par mois (via HDX).</li>
<li>IGB, via OCHA : limites administratives v03, au 1er août 2025 (cod-ab-bfa). INSD, via UNFPA : population 2024 par province (cod-ps-bfa).</li>
<li>CILSS / RPCA : Cadre harmonisé, population par phase d'insécurité alimentaire (via HDX).</li>
<li>INSD : EHCVM 2021, Diagnostic de la pauvreté, tableau 3-2. INSD / DHS Program : Enquête démographique et de santé 2021, indicateurs régionaux (via HDX).</li>
<li>CONASUR, via OCHA : situation des personnes déplacées internes au 31 décembre 2022. Insecurity Insight : Education in Danger, 2017-2026 (via HDX).</li>
</ul>
<h3>Références</h3>
<ul class="note" style="font-size:8.6pt">
<li>Adelman M., Haimovich F., Ham A., Vazquez E. (2018). Predicting school dropout with administrative data: new evidence from Guatemala and Honduras. Education Economics.</li>
<li>IIEP-UNESCO (2024). Données d'éducation en situation d'urgence, Burkina Faso.</li>
<li>Kazianga H., Levy D., Linden L., Sloan M. (2013). The effects of girl-friendly schools: evidence from the BRIGHT program in Burkina Faso. AEJ: Applied Economics.</li>
<li>MEBAPLN (2026). 14 chantiers pour l'école burkinabè à l'horizon 2030.</li>
<li>Vazquez E., Haimovich F., Adelman M. (2021). Scalable early warning systems for school dropout prevention. Banque mondiale.</li>
<li>Wisner B., Blaikie P., Cannon T., Davis I. (2004). At Risk. Routledge.</li>
</ul>
</section>
</body></html>"""

(ICI / "rapport_defi1.html").write_text(html, encoding="utf-8")
script = ICI / "imprimer.cjs"
script.write_text(f"""const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://{ICI / "rapport_defi1.html"}', {{ waitUntil: 'networkidle' }});
  await p.pdf({{ path: '{ICI / "rapport_defi1.pdf"}', format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font:7.5pt Inter,sans-serif;color:#7d8799;padding:0 16mm;display:flex;justify-content:space-between"><span>Anticiper le risque de décrochage scolaire · Défi 1</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: {{ top: '15mm', bottom: '16mm', left: '16mm', right: '16mm' }} }});
  await b.close();
}})();
""")
subprocess.run(["node", str(script)], check=True, env={**__import__("os").environ,
               "NODE_PATH": subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()})
from pypdf import PdfReader
print("pages :", len(PdfReader(ICI / "rapport_defi1.pdf").pages))

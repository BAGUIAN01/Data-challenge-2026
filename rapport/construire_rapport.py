"""Build the final report in LaTeX from the dashboard data set and the figures, then compile it with XeLaTeX."""
import json
import subprocess
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
jeu = json.load(open(RACINE / "dashboard/public/data/tableau_de_bord.json", encoding="utf-8"))
R = jeu["regions"]
sg, fd, val = jeu["score_global"], jeu["facteur_dominant"]["par_region"], jeu["validation"]
NOM_ACTION = {"violence": "l'insécurité", "deplaces": "l'accueil des déplacés", "pauvrete": "la pauvreté", "faim": "la faim",
              "meres": "l'instruction des mères", "grossesses": "les grossesses précoces", "prescolaire": "le préscolaire"}


def fr(v, d=0):
    return f"{v:,.{d}f}".replace(",", "\\,").replace(".", "{,}")


ordre = sorted(R, key=lambda r: (r["priorite"], -sg["par_region"][r["cle"]]))
lignes = "\n".join(
    f"{r['nom']} & {r['ancienne']} & {sg['par_region'][r['cle']]} & {r['probabilites']['ref_2026_27']} & "
    f"{fr(r['tap'][-1], 1)} & {r['priorite']} & "
    f"{(NOM_ACTION[fd[r['cle']]['dominant']]) if fd[r['cle']]['dominant'] else '(aucun : consolider)'} & "
    f"{fr(round(r['enfants_hors_cm2'], -2))} \\tabularnewline"
    for r in ordre)
tr = sg["trajectoire"]
mouv = sorted(((r, tr["par_region"][r["cle"]]["score"]) for r in R), key=lambda x: x[1][-1] - x[1][-2], reverse=True)
hausses = ", ".join(f"{r['nom']} ({s[-2]} $\\to$ {s[-1]})" for r, s in mouv if s[-1] - s[-2] >= 3)
total_hors = sum(r["enfants_hors_cm2"] for r in R)
p1_hors = sum(r["enfants_hors_cm2"] for r in R if r["priorite"] == 1)
V = {
    "P1HORS": fr(round(p1_hors, -2)), "P1PCT": str(round(100 * p1_hors / total_hors)),
    "AUCREF": fr(val["auc_reference"], 2), "AUCSEPT": fr(val["auc_septembre"], 2), "AUCJANV": fr(val["auc_janvier"], 2),
    "RANG": fr(val["rang_tap"], 2), "MREG": str(val["matrice_regions_pct"]), "MBAISSES": str(val["matrice_baisses_pct"]),
    "MPERDUS": str(val["matrice_perdus_pct"]), "AUCSCORE": fr(sg["rejoue"]["auc_score"], 2),
    "AUCRISQUE": fr(sg["rejoue"]["auc_risque"], 2), "BSCORE": str(sg["rejoue"]["baisses_score_pct"]),
    "PSCORE": str(sg["rejoue"]["perdus_score_pct"]), "NCERR": fr(jeu["nowcast"]["erreur_pct"], 1),
    "NCPERS": fr(jeu["nowcast"]["erreur_persistance_pct"], 1), "LIGNES": lignes, "HAUSSES": hausses,
}

TEX = (ICI / "rapport_defi1.modele.tex").read_text(encoding="utf-8")
for k, v in V.items():
    TEX = TEX.replace(f"<<{k}>>", v)
assert "<<" not in TEX
(ICI / "rapport_defi1.tex").write_text(TEX, encoding="utf-8")
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "rapport_defi1.tex"], cwd=ICI, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-3000:])
        raise SystemExit(1)
for ext in ("aux", "log", "out"):
    (ICI / f"rapport_defi1.{ext}").unlink(missing_ok=True)
from pypdf import PdfReader
print("pages :", len(PdfReader(ICI / "rapport_defi1.pdf").pages))

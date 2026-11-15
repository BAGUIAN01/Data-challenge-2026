"""Build the final report in LaTeX from the dashboard data set and the figures, then compile it with XeLaTeX."""
import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

import chemins

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
dataset = json.load(open(ROOT / "dashboard/public/data/tableau_de_bord.json", encoding="utf-8"))
R = dataset["regions"]
sg, fd, val = dataset["score_global"], dataset["facteur_dominant"]["par_region"], dataset["validation"]
ACTION_NAME = {"violence": "l'insécurité", "deplaces": "l'accueil des déplacés", "pauvrete": "la pauvreté", "faim": "la faim",
              "meres": "l'instruction des mères", "grossesses": "les grossesses précoces", "prescolaire": "le préscolaire"}


def fr(v, d=0):
    return f"{v:,.{d}f}".replace(",", "\\,").replace(".", "{,}")


order = sorted(R, key=lambda r: (r["priorite"], -sg["par_region"][r["cle"]]))
lines_out = "\n".join(
    f"{r['nom']} & {r['ancienne']} & {sg['par_region'][r['cle']]} & {r['probabilites']['ref_2026_27']} & "
    f"{fr(r['tap'][-1], 1)} & {r['priorite']} & "
    f"{(ACTION_NAME[fd[r['cle']]['dominant']]) if fd[r['cle']]['dominant'] else '(aucun : consolider)'} & "
    f"{fr(round(r['enfants_hors_cm2'], -2))} \\tabularnewline"
    for r in order)
tr = sg["trajectoire"]
moves = sorted(((r, tr["par_region"][r["cle"]]["score"]) for r in R), key=lambda x: x[1][-1] - x[1][-2], reverse=True)
rises = ", ".join(f"{r['nom']} ({s[-2]} $\\to$ {s[-1]})" for r, s in moves if s[-1] - s[-2] >= 3)
total_out_of_cm2 = sum(r["enfants_hors_cm2"] for r in R)
p1_out_of_cm2 = sum(r["enfants_hors_cm2"] for r in R if r["priorite"] == 1)
V = {
    "P1HORS": fr(round(p1_out_of_cm2, -2)), "P1PCT": str(round(100 * p1_out_of_cm2 / total_out_of_cm2)),
    "AUCREF": fr(val["auc_reference"], 2), "AUCSEPT": fr(val["auc_septembre"], 2), "AUCJANV": fr(val["auc_janvier"], 2),
    "RANG": fr(val["rang_tap"], 2), "MREG": str(val["matrice_regions_pct"]), "MBAISSES": str(val["matrice_baisses_pct"]),
    "MPERDUS": str(val["matrice_perdus_pct"]), "AUCSCORE": fr(sg["rejoue"]["auc_score"], 2),
    "AUCRISQUE": fr(sg["rejoue"]["auc_risque"], 2), "BSCORE": str(sg["rejoue"]["baisses_score_pct"]),
    "PSCORE": str(sg["rejoue"]["perdus_score_pct"]), "NCERR": fr(dataset["nowcast"]["erreur_pct"], 1),
    "NCPERS": fr(dataset["nowcast"]["erreur_persistance_pct"], 1), "LIGNES": lines_out, "HAUSSES": rises,
}

TEX = Path(chemins.path("rapport.tex")).read_text(encoding="utf-8")
# Built in a scratch folder: images as JPEG at a print resolution (about 200 dpi at their width on A4),
# so the PDF stays light enough to upload; only the PDF goes back to 05_interpretation/.
BUILD = HERE / ".build_rapport"
LIGHT = BUILD / "images"
LIGHT.mkdir(parents=True, exist_ok=True)
for name in re.findall(r"includegraphics\[[^]]*\]\{([^}]+)\.png\}", TEX):
    im = Image.open(chemins.path(f"{name}.png")).convert("RGB")
    im.thumbnail((1400, 1400))
    im.save(LIGHT / f"{name}.jpg", quality=72, optimize=True, progressive=True)
TEX = re.sub(r"(includegraphics\[[^]]*\]\{[^}]+)\.png\}", r"\1.jpg}", TEX)
TEX = re.sub(r"\\graphicspath\{.*\}", lambda m: r"\graphicspath{{images/}}", TEX, count=1)
for k, v in V.items():
    TEX = TEX.replace(f"<<{k}>>", v)
assert "<<" not in TEX
(BUILD / "rapport.tex").write_text(TEX, encoding="utf-8")
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "rapport.tex"], cwd=BUILD, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-3000:])
        raise SystemExit(1)
shutil.copy2(BUILD / "rapport.pdf", chemins.path("rapport.pdf"))
print(chemins.rel("rapport.pdf"), ":", len(PdfReader(chemins.path("rapport.pdf")).pages), "pages")

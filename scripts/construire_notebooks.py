"""Build and run the notebooks of the project, one per step, from the scripts."""
import ast
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

RACINE = Path(__file__).resolve().parent.parent
TIDY, REF, A = "data/tidy/presco_tidy.csv", "data/ref/regions_13_17.csv", "analyse/"

CAHIERS = {
    "02_nettoyage": ("Étape 2 · Nettoyage", "Lecture du fichier du challenge, contrôles de cohérence, sources externes.", [
        ("parse_presco", "Lecture du fichier du challenge", ["data/raw/Presco.txt", TIDY]),
        ("check_presco", "Contrôles de cohérence", [TIDY]),
        ("prepare_facteurs", "Sources externes : faim, EDS, déplacés", []),
    ]),
    "03_transformation": ("Étape 3 · Transformation", "Référentiel des régions, panel région × année, violence, carte.", [
        ("referentiel_officiel", "Correspondance officielle 13 / 17 régions", ["data/raw/externe/hdx_cod_ab/bfa_admin_boundaries.xlsx", "data/ref/"]),
        ("regions_2025", "Noms des régions de 2025", [REF, TIDY, "data/tidy/presco_tidy_regions2025.csv"]),
        ("analyse_pistes", "Panel région × année et pistes P1 à P7", [TIDY, A]),
        ("regions_2025", "Panel avec les régions de 2025", [REF, "analyse/panel_region_annee.csv", "analyse/panel_region_annee_2025.csv"]),
        ("acled_anticipation", "Violence : agrégat ACLED par région et année scolaire",
         ["data/raw/externe/hdx_acled/acled_political_violence_month_year.xlsx", "analyse/panel_region_annee.csv", A]),
        ("carte_13_regions", "Carte des 13 régions", ["data/raw/externe/hdx_cod_ab/geojson/bfa_admin1.geojson", REF, A]),
    ]),
    "04a_analyse_descriptive": ("Étape 4 · Analyse descriptive", "Ce que disent les données du challenge, et les figures des pistes.", [
        ("analyse_presco", "Analyse descriptive", [TIDY, A]),
        ("figures_pistes", "Figures 01 à 07", [TIDY, A, "analyse/figures/"]),
    ]),
    "04b_modeles": ("Étape 4 · Modèles", "Prévision, alerte, apprentissage automatique, facteurs, formule du risque, score global, facteur dominant.", [
        ("prevision_hypothese", "Prévision 2025/26, alerte d'escalade, test de l'hypothèse", []),
        ("figures_prevision", "Figures de la prévision", []),
        ("machine_learning", "Apprentissage automatique contre règles simples", []),
        ("figures_ml", "Figures de l'apprentissage automatique", []),
        ("approches_prevision", "Écoles ouvertes et filière des cohortes", []),
        ("solution_prevision", "Où, combien, matrice de priorité 2026/27", []),
        ("facteurs_decrochage", "Facteurs autres que l'insécurité", []),
        ("prevision_facteurs", "Les facteurs aident-ils à prévoir ?", []),
        ("anticipation_fine", "Signaux fins de violence et calendrier d'alerte", []),
        ("formule_risque", "Formule du risque", []),
        ("score_global", "Score global", []),
        ("facteur_dominant", "Facteur dominant : sur quoi agir", []),
    ]),
    "05_interpretation": ("Étape 5 · Interprétation", "Figures de la solution, données du tableau de bord, fiches régionales.", [
        ("figures_approches", "Figures 13 à 17", []),
        ("export_tableau_de_bord", "Données du tableau de bord", []),
        ("fiches_regionales", "Fiches régionales", []),
    ]),
}

CHEMINS = """racine = Path.cwd()
while not (racine / "scripts").is_dir() and racine != racine.parent:
    racine = racine.parent
os.chdir(racine)
sys.path.insert(0, "scripts")"""

FIGURES = '''def montrer_figures(depuis, dossiers=("analyse/figures", "analyse", "analyse/fiches"), maxi=8):
    vues = sorted((p for d in dossiers for p in Path(d).glob("*.png") if p.stat().st_mtime >= depuis), key=lambda p: p.name)
    for p in vues[:maxi]:
        print(p)
        display(Image(filename=str(p), width=760))'''

SCRIPTS = {p.stem for p in (RACINE / "scripts").glob("*.py")}


def reglage(n):
    """Import, or a setting that belongs with the imports (matplotlib backend, search path)."""
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        return True
    return isinstance(n, ast.Expr) and ast.unparse(n).startswith(("matplotlib.use(", "sys.path.insert("))


def bloc_imports(noms):
    """One cell with every import of the notebook: standard library, then packages, then the project's scripts."""
    simples, depuis = set(), {}
    base = [ast.parse("import os\nimport sys\nimport time\nfrom pathlib import Path\nfrom IPython.display import Image, display")]
    arbres = base + [ast.parse((RACINE / "scripts" / f"{n}.py").read_text(encoding="utf-8")) for n in noms]
    for t in arbres:
        for n in t.body:
            if isinstance(n, ast.Import):
                for a in n.names:
                    simples.add((a.name, a.asname))
            elif isinstance(n, ast.ImportFrom):
                depuis.setdefault(n.module, set()).update((a.name, a.asname) for a in n.names)
    groupe = lambda m: 2 if m.split(".")[0] in SCRIPTS else 0 if m.split(".")[0] in sys.stdlib_module_names else 1
    lignes = {0: [], 1: [], 2: []}
    for m, a in sorted(simples):
        lignes[groupe(m)].append((m, f"import {m}" + (f" as {a}" if a else "")))
    for m, ns in sorted(depuis.items()):
        noms_m = ", ".join(n + (f" as {a}" if a else "") for n, a in sorted(ns))
        lignes[groupe(m)].append((m, f"from {m} import {noms_m}"))
    paquets = [l for _, l in sorted(lignes[1], key=lambda x: (x[0] != "matplotlib", x[0], x[1].startswith("from")))]
    if any(l == "import matplotlib" for l in paquets):
        paquets.insert(paquets.index("import matplotlib") + 1, 'matplotlib.use("Agg")')
    blocs = ["\n".join(l for _, l in sorted(lignes[0], key=lambda x: (x[1].startswith("from"), x[0]))), "\n".join(paquets), CHEMINS]
    if lignes[2]:
        blocs.append("\n".join(l for _, l in sorted(lignes[2])))
    return "\n\n".join(b for b in blocs if b)


def cellules(nom):
    src = (RACINE / "scripts" / f"{nom}.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    lignes = src.splitlines()
    blocs, courant = [], []
    for n in tree.body:
        if reglage(n):
            continue
        if isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant) and isinstance(n.value.value, str):
            continue
        if isinstance(n, ast.If) and "__name__" in ast.unparse(n.test):
            continue
        texte = "\n".join(lignes[(n.decorator_list[0].lineno if getattr(n, "decorator_list", None) else n.lineno) - 1:n.end_lineno])
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            if courant:
                blocs.append("\n".join(courant)); courant = []
            blocs.append(texte)
        else:
            courant.append(texte)
    if courant:
        blocs.append("\n".join(courant))
    return blocs


def construire(fichier, titre, chapo, etapes):
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.cells.append(nbformat.v4.new_markdown_cell(
        f"# {titre}\n\n{chapo}\n\nÀ lancer dans le projet complet (archive `05-interpretation_D1_scientist_projet-complet_v1.zip`), "
        "avec les données brutes placées comme le dit `data/raw/LISEZ-MOI.md`."))
    nb.cells.append(nbformat.v4.new_code_cell(bloc_imports(list(dict.fromkeys(e[0] for e in etapes)))))
    nb.cells.append(nbformat.v4.new_code_cell(FIGURES))
    vus = set()
    for i, (nom, intitule, args) in enumerate(etapes, 1):
        nb.cells.append(nbformat.v4.new_markdown_cell(f"## {i}. {intitule}\n\n`scripts/{nom}.py`"))
        alias = ""
        if nom not in vus:
            for c in cellules(nom):
                nb.cells.append(nbformat.v4.new_code_cell(c))
            vus.add(nom)
            alias = f"lancer_{nom} = main\n"
        nb.cells.append(nbformat.v4.new_code_cell(
            f"{alias}t0 = time.time()\nsys.argv = {[nom + '.py'] + args!r}\nlancer_{nom}()\nmontrer_figures(t0)"))
    return nb


def main():
    sortie = RACINE / "notebooks"
    sortie.mkdir(exist_ok=True)
    choix = sys.argv[1:] or list(CAHIERS)
    for f in choix:
        nb = construire(f, *CAHIERS[f])
        NotebookClient(nb, timeout=3600, kernel_name="python3", resources={"metadata": {"path": str(RACINE)}}).execute()
        nbformat.write(nb, sortie / f"{f}.ipynb")
        print("cahier :", sortie / f"{f}.ipynb")


if __name__ == "__main__":
    main()
